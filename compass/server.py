"""HTTP API and web host (Python standard library only).

Access boundaries (enforced server-side, not just hidden in the UI):
  engineer   -> only /api/me/* for their own id (taken from the signed session, never from a parameter)
  manager    -> only aggregated insights for their own team
  leader     -> aggregated org and team insights
  enablement -> practice catalog, discovery, eval, compliance and the access audit
No role can read another engineer's recommendations, feedback or history.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import __version__, aggregate, compliance, config, db, engine, llm, prompt_coach
from .practices import PRACTICES, SIGNAL_META

ROUTES: dict[tuple[str, str], tuple] = {}
_audit_lock = threading.Lock()


def route(method: str, path: str, roles: tuple | None = None):
    def deco(fn):
        ROUTES[(method, path)] = (fn, roles)
        return fn
    return deco


# --------------------------------------------------------------------------- sessions

def sign(payload: dict) -> str:
    raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(config.SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{raw}.{sig}"


def verify(token: str) -> dict | None:
    try:
        raw, sig = token.split(".", 1)
        good = hmac.new(config.SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(sig, good):
            return None
        payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:  # noqa: BLE001
        return None


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def audit(role: str, method: str, path: str, status: int):
    """Access audit: role, endpoint and status only. No subject ids, no content."""
    line = json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "role": role,
                       "method": method, "path": path, "status": status})
    with _audit_lock:
        config.AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(config.AUDIT_LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


# --------------------------------------------------------------------------- helpers

def _engineer(eid: str) -> dict:
    conn = db.signals_conn()
    try:
        rows = db.rows(conn, "SELECT e.*, t.name AS team_name, t.domain AS team_domain FROM engineers e "
                             "JOIN teams t USING(team_id) WHERE engineer_id=?", (eid,))
        if not rows:
            raise ApiError(404, "unknown engineer")
        u = db.rows(conn, "SELECT * FROM usage_weekly WHERE engineer_id=? ORDER BY week", (eid,))
        d = db.rows(conn, "SELECT * FROM delivery_weekly WHERE engineer_id=? ORDER BY week", (eid,))
        return {"profile": rows[0], "usage": u, "delivery": d}
    finally:
        conn.close()


def _my_feedback(eid: str) -> dict:
    p = db.private_conn()
    try:
        latest = {}
        for r in db.rows(p, "SELECT rec_key, action FROM feedback WHERE engineer_id=? ORDER BY id", (eid,)):
            latest[r["rec_key"]] = None if r["action"] == "restored" else r["action"]
        return {k: v for k, v in latest.items() if v}
    finally:
        p.close()


# --------------------------------------------------------------------------- routes: public

@route("GET", "/api/health")
def health(ctx, q, body):
    return {"status": "ok", "version": __version__, "k_anon": config.K_ANON, "llm_enhancer": llm.enabled()}


@route("GET", "/api/demo/personas")
def personas(ctx, q, body):
    """Demo sign-in only. In production this is replaced by enterprise SSO; the
    picker exposes profile context only, never recommendations or signals."""
    conn = db.signals_conn()
    try:
        engs = db.rows(conn, "SELECT e.engineer_id, e.codename, e.role, e.seniority, e.stack_label, e.project_complexity, "
                             "t.name AS team_name, e.team_id FROM engineers e JOIN teams t USING(team_id) ORDER BY t.name, e.engineer_id")
        teams = db.rows(conn, "SELECT team_id, name, domain FROM teams ORDER BY name")
        featured = ["E-ATL-01", "E-BOR-01", "E-CIR-01", "E-ECH-05", "E-ATL-05", "E-ATL-04"]
        return {"engineers": engs, "teams": teams, "featured": featured}
    finally:
        conn.close()


@route("POST", "/api/session")
def session(ctx, q, body):
    role = body.get("role")
    subject = body.get("subject")
    if role not in ("engineer", "manager", "leader", "enablement"):
        raise ApiError(400, "invalid role")
    conn = db.signals_conn()
    try:
        if role == "engineer":
            r = db.rows(conn, "SELECT codename FROM engineers WHERE engineer_id=?", (subject,))
            if not r:
                raise ApiError(400, "unknown engineer")
            display = r[0]["codename"]
        elif role == "manager":
            r = db.rows(conn, "SELECT name FROM teams WHERE team_id=?", (subject,))
            if not r:
                raise ApiError(400, "unknown team")
            display = f"Manager, {r[0]['name']}"
        else:
            subject = "org"
            display = {"leader": "Engineering leader", "enablement": "AI enablement team"}[role]
    finally:
        conn.close()
    payload = {"role": role, "sub": subject, "display": display, "exp": time.time() + 8 * 3600}
    return {"token": sign(payload), "role": role, "display": display}


@route("GET", "/api/practices")
def practices(ctx, q, body):
    out = []
    for pid, p in PRACTICES.items():
        out.append({"id": pid, **{k: v for k, v in p.items() if k != "simulation"},
                    "signal_labels": [SIGNAL_META[s][0] for s in p["signals"]],
                    "simulation_assumptions": {SIGNAL_META[s][0]: list(e) for s, e in p["simulation"].items()}})
    return {"practices": out}


@route("GET", "/api/kit")
def kit_file(ctx, q, body):
    rel = (q.get("path") or [""])[0]
    base = config.ROOT.resolve()
    target = (base / rel).resolve()
    if not str(target).startswith(str((base / "agent-kit").resolve())) or not target.is_file():
        raise ApiError(404, "not an agent-kit file")
    return {"path": rel, "content": target.read_text(encoding="utf-8")[:60000]}


# --------------------------------------------------------------------------- routes: engineer (private)

@route("GET", "/api/me", roles=("engineer",))
def me(ctx, q, body):
    data = _engineer(ctx["sub"])
    return {"profile": data["profile"]}


@route("GET", "/api/me/coaching", roles=("engineer",))
def my_coaching(ctx, q, body):
    eid = ctx["sub"]
    data = _engineer(eid)
    result = engine.recommend(data["profile"], data["usage"], data["delivery"], _my_feedback(eid))
    p = db.private_conn()
    try:
        p.executemany("INSERT INTO coaching_history (engineer_id, rec_key) VALUES (?, ?)",
                      [(eid, r["rec_key"]) for r in result["recommendations"]])
        p.commit()
    finally:
        p.close()
    result["profile"] = data["profile"]
    result["privacy"] = "Only you can see this page. Managers and leaders see team-level patterns only."
    return result


@route("POST", "/api/me/feedback", roles=("engineer",))
def my_feedback(ctx, q, body):
    action = body.get("action")
    reason = body.get("reason")
    rec_key = str(body.get("rec_key", ""))[:40]
    if action not in ("useful", "not_useful", "dismissed", "restored", "tried"):
        raise ApiError(400, "invalid action")
    if reason not in (None, "not_relevant", "already_doing", "not_now", "too_generic", "wrong_context", "other"):
        raise ApiError(400, "invalid reason")
    if rec_key not in engine.RULES_BY_ID and rec_key != "R-GROWTH":
        raise ApiError(400, "invalid recommendation")
    p = db.private_conn()
    try:
        p.execute("INSERT INTO feedback (engineer_id, rec_key, action, reason) VALUES (?,?,?,?)",
                  (ctx["sub"], rec_key, action, reason))
        p.commit()
    finally:
        p.close()
    return {"saved": True, "visibility": "private to you"}


@route("GET", "/api/me/history", roles=("engineer",))
def my_history(ctx, q, body):
    p = db.private_conn()
    try:
        fb = db.rows(p, "SELECT rec_key, action, reason, created_at FROM feedback WHERE engineer_id=? ORDER BY id DESC LIMIT 50",
                     (ctx["sub"],))
        shown = db.rows(p, "SELECT rec_key, COUNT(*) AS times_shown, MAX(shown_at) AS last_shown FROM coaching_history "
                           "WHERE engineer_id=? GROUP BY rec_key", (ctx["sub"],))
        return {"feedback": fb, "shown": shown}
    finally:
        p.close()


@route("POST", "/api/me/forget", roles=("engineer",))
def my_forget(ctx, q, body):
    p = db.private_conn()
    try:
        p.execute("DELETE FROM feedback WHERE engineer_id=?", (ctx["sub"],))
        p.execute("DELETE FROM coaching_history WHERE engineer_id=?", (ctx["sub"],))
        p.commit()
    finally:
        p.close()
    return {"deleted": True}


@route("GET", "/api/me/simulate", roles=("engineer",))
def my_simulate(ctx, q, body):
    pid = (q.get("practice") or [""])[0]
    if pid not in PRACTICES:
        raise ApiError(400, "unknown practice")
    data = _engineer(ctx["sub"])
    return engine.simulate(data["profile"], data["usage"], data["delivery"], pid)


@route("GET", "/api/me/trend", roles=("engineer",))
def my_trend(ctx, q, body):
    data = _engineer(ctx["sub"])
    merged = engine.merged_rows(data["usage"], data["delivery"])
    keys = ["pr_size_loc_median", "review_rounds_avg", "ci_first_pass_rate", "tests_added_per_pr",
            "flaky_test_rate", "chat_turns_avg"]
    return {"series": {k: {"label": SIGNAL_META[k][0], "direction": SIGNAL_META[k][2],
                           "points": [{"week": r["week"], "value": r[k]} for r in merged]} for k in keys}}


# --------------------------------------------------------------------------- routes: aggregated

@route("GET", "/api/team/insights", roles=("manager", "leader"))
def team(ctx, q, body):
    team_id = ctx["sub"] if ctx["role"] == "manager" else (q.get("team") or [""])[0]
    return aggregate.team_insights(team_id)


@route("GET", "/api/org/insights", roles=("leader", "enablement"))
def org(ctx, q, body):
    return aggregate.org_insights()


@route("GET", "/api/practices/discovery", roles=("leader", "enablement", "manager"))
def discovery(ctx, q, body):
    return {"practices": aggregate.practice_discovery(),
            "note": "Org-level associations in synthetic data. Correlation is not causation."}


# --------------------------------------------------------------------------- routes: prompt coach

def _coach_ctx(ctx):
    if ctx and ctx.get("role") == "engineer":
        prof = _engineer(ctx["sub"])["profile"]
        return prof["project_complexity"], prof["stack"]
    return "medium", None


@route("POST", "/api/coach/analyze", roles=("engineer", "manager", "leader", "enablement"))
def coach_analyze(ctx, q, body):
    text = str(body.get("text", ""))[:20000]
    if not text.strip():
        raise ApiError(400, "paste a story or describe the task")
    complexity, _ = _coach_ctx(ctx)
    return prompt_coach.analyze(text, body.get("complexity") or complexity, body.get("task_type"))


@route("POST", "/api/coach/build", roles=("engineer", "manager", "leader", "enablement"))
def coach_build(ctx, q, body):
    text = str(body.get("text", ""))[:20000]
    complexity, stack = _coach_ctx(ctx)
    out = prompt_coach.build(text, body.get("answers") or {}, body.get("tool"), body.get("complexity") or complexity,
                             body.get("task_type"), body.get("stack") or stack)
    if body.get("polish") and llm.enabled():
        polished = llm.polish(out["prompt"])
        if polished:
            out["prompt_polished"] = polished
    return out


@route("POST", "/api/coach/jira-csv", roles=("engineer", "manager", "leader", "enablement"))
def coach_jira(ctx, q, body):
    return {"issues": prompt_coach.parse_jira_csv(str(body.get("csv", ""))[:500000])}


@route("GET", "/api/coach/sample-jira", roles=("engineer", "manager", "leader", "enablement"))
def coach_sample(ctx, q, body):
    return {"issues": prompt_coach.parse_jira_csv(config.SAMPLE_JIRA_CSV.read_text(encoding="utf-8"))}


# --------------------------------------------------------------------------- routes: trust

@route("GET", "/api/trust/compliance")
def trust_compliance(ctx, q, body):
    return compliance.run([p for (_, p) in ROUTES])


@route("GET", "/api/trust/eval")
def trust_eval(ctx, q, body):
    path = config.ROOT / "reports" / "eval-report.json"
    if not path.exists():
        from . import evaluation
        evaluation.run(write=True)
    return json.loads(path.read_text(encoding="utf-8"))


@route("GET", "/api/trust/boundaries")
def trust_boundaries(ctx, q, body):
    """Live demonstration of the privacy boundary."""
    teams = []
    conn = db.signals_conn()
    try:
        for t in db.rows(conn, "SELECT team_id, name FROM teams ORDER BY name"):
            s = aggregate.team_insights(t["team_id"])
            teams.append({"team": t["name"], "suppressed": s["suppressed"], "group_size": s["group_size"],
                          "patterns_shown": len(s.get("workflow_gaps", [])),
                          "patterns_below_threshold": s.get("patterns_below_threshold")})
    finally:
        conn.close()
    matrix = []
    for (method, path), (_, roles) in sorted(ROUTES.items(), key=lambda kv: kv[0][1]):
        matrix.append({"endpoint": f"{method} {path}", "roles": list(roles) if roles else ["public"]})
    return {"k": config.K_ANON, "teams": teams, "access_matrix": matrix,
            "private_store_readers": ["/api/me/coaching", "/api/me/feedback", "/api/me/history", "/api/me/forget"],
            "aggregation_reads": "signals.db (read-only). Never private.db."}


@route("GET", "/api/audit", roles=("enablement",))
def audit_log(ctx, q, body):
    if not config.AUDIT_LOG.exists():
        return {"entries": []}
    lines = config.AUDIT_LOG.read_text(encoding="utf-8").splitlines()[-200:]
    return {"entries": [json.loads(x) for x in reversed(lines)],
            "note": "Role, endpoint and status only. No user ids and no content are logged."}


# --------------------------------------------------------------------------- handler

class Handler(BaseHTTPRequestHandler):
    server_version = "Compass/" + __version__

    def log_message(self, fmt, *args):  # quiet console; audit log is separate
        pass

    def _send(self, status, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'")
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self, method):
        url = urlparse(self.path)
        path = url.path
        if not path.startswith("/api/"):
            return self._static(path)
        ctx = None
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            ctx = verify(auth[7:])
        role = ctx["role"] if ctx else "anonymous"
        entry = ROUTES.get((method, path))
        status = 200
        try:
            if not entry:
                raise ApiError(404, "not found")
            fn, roles = entry
            if roles is not None:
                if not ctx:
                    raise ApiError(401, "sign in required")
                if ctx["role"] not in roles:
                    raise ApiError(403, f"the {ctx['role']} role cannot access this endpoint")
            self._check_origin(method)
            body = {}
            if method == "POST":
                if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
                    raise ApiError(415, "send JSON (Content-Type: application/json)")
                n = int(self.headers.get("Content-Length") or 0)
                if n > 4_000_000:
                    raise ApiError(413, "request too large")
                body = json.loads(self.rfile.read(n) or b"{}") if n else {}
            result = fn(ctx, parse_qs(url.query), body)
            self._send(200, result)
        except ApiError as e:
            status = e.status
            self._send(e.status, {"error": e.message})
        except json.JSONDecodeError:
            status = 400
            self._send(400, {"error": "invalid JSON"})
        except Exception as e:  # noqa: BLE001
            status = 500
            self._send(500, {"error": "internal error", "detail": type(e).__name__})
        finally:
            audit(role, method, path, status)

    def _check_origin(self, method):
        """Block DNS-rebinding and cross-site requests to the local API."""
        host = (self.headers.get("Host") or "").lower()
        port = self.server.server_address[1]
        allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"}
        bound = self.server.server_address[0]
        if bound in ("127.0.0.1", "localhost", "::1") and host not in allowed_hosts:
            raise ApiError(403, "unexpected Host header")
        origin = self.headers.get("Origin")
        if origin and origin.lower() not in {f"http://{h}" for h in allowed_hosts}:
            raise ApiError(403, "cross-origin requests are not allowed")
        if method == "POST" and (self.headers.get("Sec-Fetch-Site") or "same-origin") not in ("same-origin", "none"):
            raise ApiError(403, "cross-site requests are not allowed")

    def _static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        target = (config.WEB_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(config.WEB_DIR.resolve())) or not target.is_file():
            target = config.WEB_DIR / "index.html"
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")


def serve(host: str = config.HOST, port: int = config.PORT, open_browser: bool = False, deep_link: str = ""):
    db.init()
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/" + deep_link
    print(f"Compass is running at {url}  (Ctrl+C to stop)")
    print(f"Privacy threshold k = {config.K_ANON}. Data: synthetic. LLM enhancer: {'on' if llm.enabled() else 'off'}.")
    if open_browser:
        import webbrowser
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


# Workflow-coach routes register themselves into ROUTES.
from . import api_workflow  # noqa: E402,F401
