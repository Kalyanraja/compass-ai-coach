"""The coaching journey for one task, held in memory for the current session only.

Goal -> confirmed project facts -> missing questions -> approved tool -> work package
-> local checks / imported evidence -> next action and lesson.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import threading
import time
import uuid
from pathlib import Path

from .. import config, settings
from . import cache, coach, evidence as E, package, runner
from .workspace import Workspace, WorkspaceError, detect_facts, project_map

TTL = 8 * 3600
_store: dict[str, dict] = {}
_lock = threading.Lock()


class JourneyError(Exception):
    pass


def _ws(j) -> Workspace:
    return Workspace(j["project"], settings.load()["allowed_roots"])


def _get(jid: str, owner: str) -> dict:
    with _lock:
        j = _store.get(jid)
    if not j or j["owner"] != owner or time.time() - j["created"] > TTL:
        raise JourneyError("journey not found (it lives only in this session)")
    return j


def _facts(ws: Workspace) -> dict:
    snap = ws.snapshot_hash()
    key = cache.key_material(snap)
    cached = cache.get(str(ws.root), "facts", key)
    if cached:
        cached["cache"] = "hit"
        return cached
    d = detect_facts(ws)
    d["snapshot"] = snap
    cache.put(str(ws.root), "facts", key, d)
    d["cache"] = "miss" if settings.load().get("cache_enabled") else "off"
    return d


def start(owner: str, goal: str, project: str, workflow: str | None = None, source: str = "manual") -> dict:
    goal = (goal or "").strip()[:20000]
    if not goal:
        raise JourneyError("describe the goal, or fetch a Jira issue")
    ws = Workspace(project, settings.load()["allowed_roots"])
    candidates = coach.classify(goal)
    wf = workflow or candidates[0]["id"]
    coach.pack(wf)
    d = _facts(ws)
    j = {"id": uuid.uuid4().hex[:16], "owner": owner, "created": time.time(), "goal": goal, "source": source,
         "project": str(ws.root), "project_name": ws.root.name, "workflow": wf, "candidates": candidates,
         "detected": d, "facts": json.loads(json.dumps(d["facts"])), "answers": {}, "skipped": [],
         "data_class": settings.load()["default_data_class"], "complexity": "medium", "large_scope": False,
         "tool": None, "budget": settings.load()["context_budget"], "include": [], "exclude": [],
         "checks": {}, "reports": {}, "defect": None, "package": None}
    with _lock:
        _store[j["id"]] = j
    return view(j)


def view(j: dict) -> dict:
    p = coach.pack(j["workflow"])
    q = coach.next_questions(j["workflow"], j["goal"], j["facts"], j["answers"], j["skipped"])
    j["open_questions"] = [x["text"] for x in q["questions"]] + ([] if not q["remaining"] else [f"{q['remaining']} more question(s) not shown"])
    facts = list(j["facts"].values())
    return {
        "id": j["id"], "goal": j["goal"], "source": j["source"], "project": j["project"], "project_name": j["project_name"],
        "workflow": {"id": p["id"], "version": p["version"], "title": p["title"], "summary": p["summary"]},
        "candidates": j["candidates"], "stack": j["detected"]["stack"], "supported_stack": j["detected"]["supported_stack"],
        "file_count": j["detected"]["file_count"], "cache": j["detected"].get("cache"),
        "facts": {"detected": [f for f in facts if f["status"] in ("detected", "inferred")],
                  "confirmed": [f for f in facts if f["status"] == "confirmed"],
                  "unknown": [f for f in facts if f["status"] == "unknown"]},
        "questions": q, "answers": j["answers"], "tool": j["tool"], "data_class": j["data_class"],
        "complexity": j["complexity"], "large_scope": j["large_scope"], "budget": j["budget"],
        "checks": list(j["checks"].values()), "verdict": verdict(j),
    }


def state(jid, owner):
    return view(_get(jid, owner))


def confirm_fact(jid, owner, fid, value):
    j = _get(jid, owner)
    f = j["facts"].get(fid)
    if not f:
        raise JourneyError("unknown fact")
    value = str(value).strip()[:500] if value is not None else f.get("value")
    f.update({"value": value, "status": "confirmed", "confirmed_by": "you"})
    return view(j)


def answer(jid, owner, answers: dict, skip: list | None = None):
    j = _get(jid, owner)
    p = coach.pack(j["workflow"])
    qmap = {q["id"]: q for q in p["questions"]}
    for k, v in (answers or {}).items():
        if k in qmap and str(v).strip():
            j["answers"][k] = str(v).strip()[:2000]
            fills = qmap[k].get("fills")
            if fills == "test_command":
                j["facts"]["test_command"] = {"id": "test_command", "label": "Test command", "value": j["answers"][k],
                                              "status": "confirmed", "confirmed_by": "you"}
    for s in skip or []:
        if s in qmap and s not in j["skipped"]:
            j["skipped"].append(s)
    return view(j)


def set_workflow(jid, owner, wf):
    j = _get(jid, owner)
    coach.pack(wf)
    j["workflow"] = wf
    return view(j)


def recommend(jid, owner, data_class=None, complexity=None, large_scope=None, deterministic=False, choose=None):
    j = _get(jid, owner)
    if data_class:
        if data_class not in ("synthetic", "internal", "restricted"):
            raise JourneyError("invalid data class")
        j["data_class"] = data_class
    if complexity in ("low", "medium", "high"):
        j["complexity"] = complexity
    if large_scope is not None:
        j["large_scope"] = bool(large_scope)
    rec = coach.recommend_tool(j["workflow"], j["data_class"], j["complexity"], j["large_scope"], deterministic)
    if choose:
        allowed = {o["id"]: o for o in rec["options"] if o["allowed"]}
        if choose not in allowed:
            raise JourneyError("that tool is not allowed by your approval and data rules")
        j["tool"] = choose
        rec["chosen"] = choose
        rec["override"] = choose != rec["tool"]
    else:
        j["tool"] = rec["tool"]
        rec["chosen"] = rec["tool"]
    return rec


def build_package(jid, owner, budget=None, include=None, exclude=None):
    j = _get(jid, owner)
    if budget:
        j["budget"] = budget
    if include is not None:
        j["include"] = include
    if exclude is not None:
        j["exclude"] = exclude
    if not j["tool"]:
        recommend(jid, owner)
    ws = _ws(j)
    view(j)  # refresh open questions
    pkg = package.build(ws, j, coach.pack(j["workflow"]), j["tool"] or "copilot", j["budget"])
    naive = __import__("compass.workflow.context", fromlist=["naive_full_dump_size"]).naive_full_dump_size(ws)
    pkg["comparison"] = {"whole_project_paste": naive, "this_package": pkg["size"],
                         "note": "Both are estimates with the same counting method. Not billing, not total conversation usage."}
    j["package"] = {"size": pkg["size"], "budget": j["budget"]}
    return pkg


# ---------------------------------------------------------------------- evidence

def _relevant_files(j, ws):
    files = ws.files()
    return [f for f in files if not f.startswith("recorded/")][:400]


def run_checks(jid, owner, approve_tests=False):
    j = _get(jid, owner)
    ws = _ws(j)
    files = _relevant_files(j, ws)
    s = settings.load()
    j["checks"]["security.secrets"] = E.secrets_lite(ws, files)
    j["checks"]["security.patterns"] = E.patterns_lite(ws, files)
    spec = (j["facts"].get("api_spec") or {}).get("value")
    if spec:
        for c in E.openapi_lite(ws, spec, j["facts"]):
            j["checks"][c["check_id"]] = c
    # Optional real scanners, only when approved in Settings.
    tmp = tempfile.mkdtemp(prefix="compass-scan-")
    try:
        g = runner.run("gitleaks-dir", {"target": ".", "report": str(Path(tmp) / "gitleaks.json")}, str(ws.root), True,
                       allowed_dirs=[tmp])
        if g["status"] == "completed":
            try:
                fnd = E.parse_gitleaks((Path(tmp) / "gitleaks.json").read_text())
                j["checks"]["scanner.gitleaks"] = E.check("scanner.gitleaks", "Secret scan (gitleaks)", "gitleaks",
                                                         s["scanners"].get("gitleaks", {}).get("version", ""),
                                                         E.FAILED if fnd else E.PASSED, ["."], fnd, snapshot=ws.snapshot_hash(files),
                                                         coverage="gitleaks default rules over readable files; --redact on.")
            except (E.ReportError, OSError) as e:
                j["checks"]["scanner.gitleaks"] = E.check("scanner.gitleaks", "Secret scan (gitleaks)", "gitleaks", "", E.BLOCKED,
                                                         detail=str(e), completed=False)
        else:
            j["checks"]["scanner.gitleaks"] = E.check("scanner.gitleaks", "Secret scan (gitleaks)", "gitleaks", "", E.NOT_CHECKED,
                                                     detail=g.get("reason", g["status"]), completed=False)
        rules = str(config.ROOT / "compass_rules" / "semgrep-local.yaml")
        sg = runner.run("semgrep-local", {"rules": rules, "target": "."}, str(ws.root), True, allowed_dirs=[str(config.ROOT / "compass_rules")])
        if sg["status"] == "completed":
            try:
                fnd, ver = E.parse_semgrep(sg["stdout"])
                j["checks"]["scanner.semgrep"] = E.check("scanner.semgrep", "Pattern scan (Semgrep, local rules, metrics off)", "semgrep",
                                                        ver, E.FAILED if fnd else E.PASSED, ["."], fnd,
                                                        coverage="Pinned local rules in compass_rules/semgrep-local.yaml only.")
            except E.ReportError as e:
                j["checks"]["scanner.semgrep"] = E.check("scanner.semgrep", "Pattern scan (Semgrep)", "semgrep", "", E.BLOCKED, detail=str(e), completed=False)
        else:
            j["checks"]["scanner.semgrep"] = E.check("scanner.semgrep", "Pattern scan (Semgrep)", "semgrep", "", E.NOT_CHECKED,
                                                    detail=sg.get("reason", sg["status"]), completed=False)
        if spec:
            ruleset = str(config.ROOT / "compass_rules" / "spectral-local.yaml")
            sp = runner.run("spectral-lint", {"spec": spec, "ruleset": ruleset}, str(ws.root), True,
                            allowed_dirs=[str(config.ROOT / "compass_rules")])
            if sp["status"] == "completed":
                try:
                    fnd = E.parse_spectral(sp["stdout"] or "[]", str(ws.root))
                    j["checks"]["scanner.spectral"] = E.check("scanner.spectral", "API spec lint (Spectral, local ruleset)", "spectral",
                                                             s["scanners"].get("spectral", {}).get("version", ""),
                                                             E.FAILED if fnd else E.PASSED, [spec], fnd)
                except E.ReportError as e:
                    j["checks"]["scanner.spectral"] = E.check("scanner.spectral", "API spec lint (Spectral)", "spectral", "", E.BLOCKED, detail=str(e), completed=False)
            else:
                j["checks"]["scanner.spectral"] = E.check("scanner.spectral", "API spec lint (Spectral)", "spectral", "", E.NOT_CHECKED,
                                                         detail=sp.get("reason", sp["status"]), completed=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # Tests: run only with explicit approval for this run.
    cmd = (j["facts"].get("test_command") or {}).get("value")
    if approve_tests and cmd:
        r = E.run_tests(ws, cmd, True)
        if r.get("report"):
            j["reports"]["tests"] = {"report": r["report"], "label": "run by Compass (this session)", "run": E._strip(r)}
        else:
            j["checks"]["tests.run"] = E.check("tests.run", "Run tests", "compass", "", E.BLOCKED if r["status"] != "completed" else E.NOT_CHECKED,
                                              detail=r.get("reason") or r.get("report_error") or r["status"], completed=False)
    elif not j["reports"].get("tests"):
        j["checks"]["tests.run"] = E.check("tests.run", "Run tests", "compass", "", E.NOT_CHECKED,
                                          detail="Tests not run: approve test execution for this run, or import a report.", completed=False)
    _derive_test_checks(j, ws)
    return view(j)


def _fixture(ws):
    try:
        return json.loads(ws.read("compass-fixture.json"))
    except (WorkspaceError, ValueError):
        return None


def _derive_test_checks(j, ws):
    rep = (j["reports"].get("tests") or {}).get("report")
    if rep:
        j["checks"].pop("tests.run", None)
    if j["workflow"] == "test-creation":
        for c in E.evaluate_tests_detect_defect(rep, _fixture(ws)):
            j["checks"][c["check_id"]] = c
    else:
        j["checks"]["tests.ran_and_passed"] = E.evaluate_report_for_feature(rep, (j["reports"].get("tests") or {}).get("label", ""))


def import_report(jid, owner, kind, text, label="imported"):
    j = _get(jid, owner)
    ws = _ws(j)
    text = (text or "")[:3_000_000]
    try:
        if kind in ("junit", "unittest"):
            rep = E.parse_junit(text) if kind == "junit" else E.parse_unittest(text)
            if label in ("before", "after"):
                j["reports"][label] = rep
            else:
                j["reports"]["tests"] = {"report": rep, "label": f"imported {kind} report"}
        elif kind == "gitleaks":
            fnd = E.parse_gitleaks(text)
            j["checks"]["scanner.gitleaks"] = E.check("scanner.gitleaks", "Secret scan (gitleaks, imported)", "gitleaks", "imported",
                                                     E.FAILED if fnd else E.PASSED, findings=fnd)
        elif kind == "semgrep":
            fnd, ver = E.parse_semgrep(text)
            j["checks"]["scanner.semgrep"] = E.check("scanner.semgrep", "Pattern scan (Semgrep, imported)", "semgrep", ver,
                                                    E.FAILED if fnd else E.PASSED, findings=fnd)
        elif kind == "spectral":
            fnd = E.parse_spectral(text)
            j["checks"]["scanner.spectral"] = E.check("scanner.spectral", "API spec lint (Spectral, imported)", "spectral", "imported",
                                                     E.FAILED if fnd else E.PASSED, findings=fnd)
        elif kind == "diff":
            j["reports"]["diff"] = text
            E.parse_diff(text)
        else:
            raise JourneyError("unsupported report type")
    except E.ReportError as e:
        j["checks"][f"import.{kind}"] = E.check(f"import.{kind}", f"Imported {kind} report", kind, "", E.BLOCKED,
                                               detail=f"Could not read the report: {e}", completed=False)
        return view(j)
    j["checks"].pop(f"import.{kind}", None)
    if j["workflow"] == "uat-defect" and (j["reports"].get("diff") or j["reports"].get("after")):
        files = E.parse_diff(j["reports"]["diff"]) if j["reports"].get("diff") else []
        res = E.evaluate_defect(files, {"report": j["reports"].get("before")} if j["reports"].get("before") else
                                {"reason": "No before-fix test run was provided, so there is no reproduction evidence."},
                                {"report": j["reports"].get("after")} if j["reports"].get("after") else None)
        j["defect"] = res
        for c in res["checks"]:
            j["checks"][c["check_id"]] = c
    _derive_test_checks(j, ws)
    return view(j)


def verify_fix(jid, owner, diff_text, approve_tests):
    j = _get(jid, owner)
    ws = _ws(j)
    cmd = (j["facts"].get("test_command") or {}).get("value")
    if not cmd:
        raise JourneyError("confirm the test command first")
    try:
        res = E.verify_defect_fix(ws, diff_text, cmd, bool(approve_tests))
    except E.ReportError as e:
        j["checks"]["import.diff"] = E.check("import.diff", "Fix diff", "diff", "", E.BLOCKED, detail=str(e), completed=False)
        return view(j)
    j["reports"]["diff"] = diff_text
    j["defect"] = res
    for c in res["checks"]:
        j["checks"][c["check_id"]] = c
    return view(j) | {"defect": res}


NEXT = {
    "openapi.header": "Add the required X-Correlation-Id header parameter to every operation in the spec, then re-run checks.",
    "openapi.error400": "Document a 400 response with the error schema on each POST/PUT.",
    "openapi.security": "Declare securitySchemes and require authentication on the operations.",
    "tests.ran_and_passed": "Run the tests (approve the run) or import the JUnit XML report, and fix failures.",
    "security.secrets": "Move the flagged credential out of source (secret store or environment) and rotate it if it was real.",
    "defect.repro_test_in_change": "Add a regression test that reproduces the defect to the change (or name the existing test that does).",
    "defect.fails_before": "Show the regression test failing on the unfixed code. Without it the fix is a guess.",
    "defect.passes_after": "Make the full suite pass after the fix.",
    "tests.ran": "Run the tests or import a report.",
    "tests.detects_defect": "Add an assertion on behavior (for example: a wrong password must be rejected) so a test fails on the defect.",
    "tests.weak_suite_flagged": "Replace existence/type checks with behavior assertions, or keep them as smoke tests alongside real ones.",
}


def verdict(j: dict) -> dict:
    p = coach.pack(j["workflow"])
    ac_rows = []
    for ac in p["acceptance"]:
        cond = ac.get("when")
        if cond and "fact_present" in cond and not j["facts"].get(cond["fact_present"]):
            continue
        cid = ac["check"]
        c = j["checks"].get(cid)
        if cid == "security.secrets":
            # Combine every secret check that ran: any failure fails; a pass needs at least one completed check.
            sec = [x for k, x in j["checks"].items() if k in ("security.secrets", "scanner.gitleaks") and x["status"] in (E.PASSED, E.FAILED)]
            if sec:
                bad = [x for x in sec if x["status"] == E.FAILED]
                c = dict(bad[0] if bad else sec[0])
                c["detail"] = "; ".join(f"{x['tool']}: {x['status']} ({len(x['findings'])} finding(s))" for x in sec)
        if c is None:
            status, ev = E.NOT_CHECKED, "No evidence yet."
        else:
            status, ev = c["status"], c.get("detail") or f"{len(c.get('findings', []))} finding(s) from {c['tool']}"
            if status == E.BLOCKED:
                status = E.NOT_CHECKED
        ac_rows.append({"id": ac["id"], "text": ac["text"], "status": status, "evidence": ev, "check": cid,
                        "next_action": NEXT.get(cid) if status != E.PASSED else None})
    failed = [r for r in ac_rows if r["status"] == E.FAILED]
    unchecked = [r for r in ac_rows if r["status"] == E.NOT_CHECKED]
    if not j["checks"]:
        overall = "No evidence yet"
    elif failed:
        overall = "Not accepted yet"
        if j["workflow"] == "uat-defect" and any(r["check"].startswith("defect.") for r in failed + unchecked):
            overall = "Not accepted: no reproduction evidence" if any(r["check"] in ("defect.fails_before", "defect.repro_test_in_change")
                                                                       for r in failed + unchecked) else overall
    elif unchecked:
        overall = "Partially verified"
        if j["workflow"] == "uat-defect" and any(r["check"] == "defect.fails_before" for r in unchecked):
            overall = "Not accepted: no reproduction evidence"
    else:
        overall = "Accepted with evidence"
    nxt = (failed or unchecked or [None])[0]
    return {"overall": overall, "acceptance": ac_rows,
            "counts": {s: sum(1 for r in ac_rows if r["status"] == s) for s in (E.PASSED, E.FAILED, E.NOT_CHECKED)},
            "next_action": nxt["next_action"] if nxt else "Share the evidence with your reviewer and merge through your normal process.",
            "lesson": p["teaching_tip"], "exercise": p.get("exercise"),
            "honesty": "Passed means the listed check ran and found nothing. It is not a security or compliance certification."}


def delete(jid, owner):
    with _lock:
        j = _store.get(jid)
        if j and j["owner"] == owner:
            del _store[jid]
            return True
    return False


def read_file(jid, owner, rel):
    j = _get(jid, owner)
    ws = _ws(j)
    text = ws.read(rel)
    return {"path": rel, "lines": text.splitlines()[:2000]}


def projects(allowed_roots):
    out = []
    for r in allowed_roots:
        rp = Path(r)
        if not rp.is_dir():
            continue
        out.append({"path": str(rp), "name": rp.name})
        for c in sorted(rp.iterdir()):
            if c.is_dir() and not c.is_symlink() and not c.name.startswith("."):
                out.append({"path": str(c.resolve()), "name": f"{rp.name}/{c.name}"})
    return out[:200]
