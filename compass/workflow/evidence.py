"""Evidence model, report readers, built-in lite checks, diff handling and verdicts.

Statuses for checks: passed | failed | not-checked | blocked.
Claim states for findings: candidate | needs-validation | confirmed | rejected.
A pattern match is a candidate, never a proven vulnerability. A test file that
exists is not proof that it ran. Missing tools are "not checked", never passing.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from . import runner
from .package import SECRET_PATTERNS
from .workspace import Workspace, WorkspaceError

PASSED, FAILED, NOT_CHECKED, BLOCKED = "passed", "failed", "not-checked", "blocked"


class ReportError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check(check_id, title, tool, version, status, scope=None, findings=None, detail="", snapshot=None, completed=True, coverage=""):
    return {"check_id": check_id, "title": title, "tool": tool, "tool_version": version, "status": status,
            "scan_completed": completed, "scope": scope or [], "source_snapshot": snapshot, "timestamp": now(),
            "findings": findings or [], "detail": detail, "coverage": coverage}


def finding(tool, rule, path, line, severity, evidence, next_action, claim="candidate"):
    return {"tool": tool, "rule": rule, "location": {"path": path, "line": line}, "reported_severity": severity,
            "evidence": (evidence or "")[:240], "claim_state": claim, "next_action": next_action}


# ---------------------------------------------------------------------- report readers

def _safe_xml(text: str):
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        raise ReportError("XML with DOCTYPE/ENTITY declarations is not accepted")
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        raise ReportError(f"malformed XML: {e}")


def parse_junit(text: str) -> dict:
    root = _safe_xml(text)
    cases = root.iter("testcase")
    tests = []
    for c in cases:
        status = "passed"
        msg = ""
        for tag, st in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
            el = c.find(tag)
            if el is not None:
                status = st
                msg = (el.get("message") or (el.text or "")).strip()[:300]
                break
        tests.append({"name": c.get("name", ""), "classname": c.get("classname", ""), "status": status, "message": msg})
    if not tests:
        raise ReportError("no <testcase> elements found")
    return _summarize(tests, "junit-xml")


UT_LINE = re.compile(r"^(\w+) \((.+?)\)(?:\n.*?)? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$", re.M)


def parse_unittest(text: str) -> dict:
    tests = []
    for m in UT_LINE.finditer(text):
        name, cls, res = m.groups()
        st = {"ok": "passed", "FAIL": "failed", "ERROR": "error"}.get(res, "skipped" if res.startswith("skipped") else "passed")
        cls = re.sub(r"\.%s$" % re.escape(name), "", cls)
        tests.append({"name": name, "classname": cls, "status": st, "message": ""})
    ran = re.search(r"^Ran (\d+) tests? in", text, re.M)
    if not tests and not ran:
        raise ReportError("not recognizable unittest output (run with -v)")
    for m in re.finditer(r"^(?:FAIL|ERROR): (\w+) \((.+?)\)\n-+\n([\s\S]*?)(?=\n={10,}|\n-{10,}\nRan )", text, re.M):
        for t in tests:
            if t["name"] == m.group(1):
                lines = [ln for ln in m.group(3).strip().splitlines() if ln.strip()]
                t["message"] = lines[-1][:300] if lines else ""
    s = _summarize(tests, "unittest-text")
    if ran:
        s["ran_reported"] = int(ran.group(1))
    return s


def _summarize(tests, fmt):
    c = {k: sum(1 for t in tests if t["status"] == k) for k in ("passed", "failed", "error", "skipped")}
    return {"format": fmt, "tests": tests, "counts": c, "ran": c["passed"] + c["failed"] + c["error"]}


def parse_gitleaks(text: str) -> list[dict]:
    try:
        data = json.loads(text or "[]")
    except ValueError as e:
        raise ReportError(f"malformed gitleaks JSON: {e}")
    if not isinstance(data, list):
        raise ReportError("gitleaks report must be a JSON array")
    return [finding("gitleaks", d.get("RuleID", "?"), d.get("File", "?"), d.get("StartLine"), "secret",
                    "match redacted by gitleaks" if d.get("Secret") in ("REDACTED", "") else "secret value present (redact before sharing)",
                    "Confirm whether this is a real credential; if so rotate it and move it to a secret store.") for d in data]


def parse_semgrep(text: str) -> tuple[list[dict], str]:
    try:
        data = json.loads(text)
    except ValueError as e:
        raise ReportError(f"malformed semgrep JSON: {e}")
    if "results" not in data:
        raise ReportError("semgrep JSON has no 'results'")
    out = []
    for r in data["results"]:
        ex = r.get("extra", {})
        out.append(finding("semgrep", str(r.get("check_id", "?")).split(".")[-1], r.get("path"), r.get("start", {}).get("line"),
                           ex.get("severity", "?"), ex.get("message", ""), "Review the flagged code; confirm or reject the candidate."))
    return out, data.get("version", "")


def parse_spectral(text: str, root: str | None = None) -> list[dict]:
    try:
        data = json.loads(text)
    except ValueError as e:
        raise ReportError(f"malformed spectral JSON: {e}")
    if not isinstance(data, list):
        raise ReportError("spectral JSON must be an array")
    sev = {0: "error", 1: "warn", 2: "info", 3: "hint"}
    def rel(p):
        if root and p and str(p).startswith(str(root)):
            return str(Path(p).resolve().relative_to(Path(root).resolve())).replace("\\", "/")
        return p
    return [finding("spectral", d.get("code", "?"), rel(d.get("source")), (d.get("range", {}).get("start", {}).get("line", -1) + 1),
                    sev.get(d.get("severity"), "?"), d.get("message", ""), "Update the API spec to satisfy the rule.") for d in data]


# ---------------------------------------------------------------------- built-in lite checks

LITE_PATTERNS = [
    ("compass-lite.eval", r"\beval\s*\(", "Dynamic evaluation of input"),
    ("compass-lite.shell-true", r"shell\s*=\s*True", "Subprocess with shell=True"),
    ("compass-lite.pickle", r"pickle\.loads?\(", "Unpickling untrusted data"),
    ("compass-lite.yaml-load", r"yaml\.load\((?![^)]*SafeLoader)", "yaml.load without SafeLoader"),
    ("compass-lite.runtime-exec", r"Runtime\.getRuntime\(\)\.exec", "Java Runtime.exec"),
    ("compass-lite.fixed-sleep", r"\b(time\.sleep|Thread\.sleep|waitForTimeout)\s*\(", "Fixed sleep (flaky test risk)"),
]


def secrets_lite(ws: Workspace, files: list[str]) -> dict:
    fnd = []
    for rel in files:
        try:
            lines = ws.lines(rel)
        except WorkspaceError:
            continue
        for i, ln in enumerate(lines, start=1):
            m = SECRET_PATTERNS[1][1].search(ln)
            if m and not re.search(r"\{\{|\$\{|<[A-Z_]+>|REDACTED|example|changeme|placeholder", m.group(4), re.I):
                fnd.append(finding("compass-secrets-lite", "credential-assignment", rel, i, "secret",
                                   ln[:m.start(4)].strip() + " [REDACTED]", "Confirm and move secrets out of source files."))
            elif SECRET_PATTERNS[4][1].search(ln) or "PRIVATE KEY-----" in ln:
                fnd.append(finding("compass-secrets-lite", "key-material", rel, i, "secret", "[REDACTED]",
                                   "Confirm and rotate if real."))
    return check("security.secrets", "Secret-pattern scan", "compass-secrets-lite", "built-in 1.0",
                 FAILED if fnd else PASSED, files, fnd, snapshot=ws.snapshot_hash(files),
                 coverage="Built-in regex for credential assignments and key material. Limited: it will miss secrets with "
                          "unusual formats. Use gitleaks for broader coverage.")


def secrets_in_diff(files: list[dict]) -> dict:
    """Secret-pattern scan of the lines a diff adds (the changed content)."""
    fnd = []
    for f in files:
        n = 0
        for h in f["hunks"]:
            for ln in h["lines"]:
                if not ln.startswith("+"):
                    continue
                n += 1
                m = SECRET_PATTERNS[1][1].search(ln[1:])
                if m and not re.search(r"\{\{|\$\{|<[A-Z_]+>|REDACTED|example|changeme|placeholder", m.group(4), re.I):
                    fnd.append(finding("compass-secrets-lite", "credential-assignment", f["path"], None, "secret",
                                       ln[1:m.start(4) + 1].strip() + " [REDACTED]", "Remove the credential from the change."))
    return check("security.secrets", "Secret-pattern scan of the change", "compass-secrets-lite", "built-in 1.0",
                 FAILED if fnd else PASSED, [f["path"] for f in files], fnd,
                 coverage="Added lines of the diff only, built-in regex. Use gitleaks for broader coverage.")


def patterns_lite(ws: Workspace, files: list[str]) -> dict:
    fnd = []
    for rel in files:
        if Path(rel).suffix.lower() not in (".py", ".java", ".ts", ".js", ".cs", ".kt"):
            continue
        for i, ln in enumerate(ws.lines(rel), start=1):
            for rid, rx, label in LITE_PATTERNS:
                if re.search(rx, ln):
                    fnd.append(finding("compass-patterns-lite", rid, rel, i, "warning", ln.strip()[:160],
                                       f"{label}: confirm whether untrusted input can reach this line."))
    return check("security.patterns", "Risky code patterns", "compass-patterns-lite", "built-in 1.0",
                 FAILED if fnd else PASSED, files, fnd, snapshot=ws.snapshot_hash(files),
                 coverage="A handful of line-based patterns. Candidates only; no data-flow analysis. Use Semgrep with local rules for more.")


def _yaml_ops(lines):
    """Line-based OpenAPI YAML walker: yields (path, method, start_line, block_lines)."""
    ops = []
    in_paths = False
    cur_path = None
    for i, ln in enumerate(lines, start=1):
        if re.match(r"^paths:\s*$", ln):
            in_paths = True
            continue
        if in_paths and re.match(r"^\S", ln):
            in_paths = False
        if not in_paths:
            continue
        m = re.match(r"^  (['\"]?/[^:]*['\"]?):\s*$", ln)
        if m:
            cur_path = m.group(1).strip("'\"")
            continue
        m = re.match(r"^    (get|post|put|patch|delete):\s*$", ln)
        if m and cur_path:
            ops.append([cur_path, m.group(1), i, []])
            continue
        if ops and (ln.startswith("      ") or not ln.strip()):
            ops[-1][3].append((i, ln))
        elif ops and re.match(r"^ {0,4}\S", ln):
            pass
    return ops


def openapi_lite(ws: Workspace, spec: str, facts: dict) -> list[dict]:
    text = ws.read(spec)
    lines = text.splitlines()
    results = []
    if spec.endswith(".json"):
        try:
            doc = json.loads(text)
        except ValueError as e:
            return [check("openapi.lite", "OpenAPI checks", "compass-openapi-lite", "built-in 1.0", BLOCKED, [spec],
                          detail=f"Could not parse JSON spec: {e}", completed=False)]
        ops = [(p, m, None, json.dumps(op)) for p, item in doc.get("paths", {}).items() for m, op in item.items()
               if m in ("get", "post", "put", "patch", "delete")]
        global_sec = bool(doc.get("security")) and bool(doc.get("components", {}).get("securitySchemes"))
        op_rows = [(p, m, ln, blob) for p, m, ln, blob in ops]
    else:
        ops = _yaml_ops(lines)
        global_sec = any(re.match(r"^security:", ln) for ln in lines) and "securitySchemes" in text
        op_rows = [(p, m, ln, "\n".join(x for _, x in block)) for p, m, ln, block in ops]
    if not op_rows:
        return [check("openapi.lite", "OpenAPI checks", "compass-openapi-lite", "built-in 1.0", BLOCKED, [spec],
                      detail="No operations found (unsupported spec layout).", completed=False)]
    params_block = text.split("parameters:", 1)[1] if "components:" in text and "parameters:" in text else ""
    snap = ws.snapshot_hash([spec])
    if facts.get("standard_header_rule"):
        miss = []
        for p, m, ln, blob in op_rows:
            ok = "X-Correlation-Id" in blob or ("$ref" in blob and "X-Correlation-Id" in params_block and "orrelation" in blob)
            if not ok:
                miss.append(finding("compass-openapi-lite", "STD-API-1 header", spec, ln, "error",
                                    f"{m.upper()} {p} has no X-Correlation-Id header parameter", "Add the required header parameter."))
        results.append(check("openapi.header", "Required header on every operation", "compass-openapi-lite", "built-in 1.0",
                             FAILED if miss else PASSED, [spec], miss, snapshot=snap))
    miss = []
    for p, m, ln, blob in op_rows:
        if m in ("post", "put") and not re.search(r"['\"]?400['\"]?\s*:", blob):
            miss.append(finding("compass-openapi-lite", "STD-API-2 error-400", spec, ln, "error",
                                f"{m.upper()} {p} documents no 400 response", "Document a 400 response with the error schema."))
    results.append(check("openapi.error400", "400 response on POST/PUT", "compass-openapi-lite", "built-in 1.0",
                         FAILED if miss else PASSED, [spec], miss, snapshot=snap))
    miss = []
    if not global_sec:
        for p, m, ln, blob in op_rows:
            if "security:" not in blob and '"security"' not in blob:
                miss.append(finding("compass-openapi-lite", "STD-API-3 auth", spec, ln, "error",
                                    f"{m.upper()} {p} has no security requirement", "Declare securitySchemes and require auth."))
    results.append(check("openapi.security", "Authentication declared", "compass-openapi-lite", "built-in 1.0",
                         FAILED if miss else PASSED, [spec], miss, snapshot=snap))
    for r in results:
        r["coverage"] = "Line-based OpenAPI 3 checks for the synthetic training standard. Not a full validator; use Spectral with your ruleset for complete linting."
    return results


# ---------------------------------------------------------------------- diffs

def parse_diff(text: str) -> list[dict]:
    files = []
    cur = None
    prev_old = None
    for ln in (text or "").splitlines():
        if ln.startswith("+++ "):
            path = ln[4:].split("\t")[0].strip()
            path = path[2:] if path.startswith(("a/", "b/")) else path
            cur = {"path": path, "added": 0, "removed": 0, "hunks": [], "new_file": prev_old == "/dev/null"}
            files.append(cur)
        elif ln.startswith("--- "):
            prev_old = ln[4:].split("\t")[0].strip()
        elif ln.startswith("@@") and cur is not None:
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
            if not m:
                raise ReportError("malformed hunk header")
            cur["hunks"].append({"old_start": int(m.group(1)), "lines": []})
        elif cur is not None and cur["hunks"] and ln[:1] in (" ", "+", "-", "\\"):
            if ln.startswith("\\"):
                continue
            cur["hunks"][-1]["lines"].append(ln)
            if ln.startswith("+"):
                cur["added"] += 1
            elif ln.startswith("-"):
                cur["removed"] += 1
    for f in files:
        if ".." in Path(f["path"]).parts or Path(f["path"]).is_absolute():
            raise ReportError("diff paths must be relative and inside the project")
        f["is_test"] = bool(re.search(r"(^|/)(tests?|src/test|__tests__)/|(Test|_test|\.test|\.spec)\.\w+$", f["path"]))
    if not files:
        raise ReportError("no file changes found in the diff")
    return files


def apply_diff(root: str, files: list[dict], only_tests: bool = False) -> None:
    for f in files:
        if only_tests and not f["is_test"]:
            continue
        target = Path(root) / f["path"]
        old = [] if f["new_file"] or not target.exists() else target.read_text(encoding="utf-8").splitlines()
        new, pos = [], 0
        for h in f["hunks"]:
            start = h["old_start"] - 1 if old else 0
            new.extend(old[pos:start])
            pos = start
            for ln in h["lines"]:
                tag, body = ln[0], ln[1:]
                if tag == " ":
                    if pos >= len(old) or old[pos] != body:
                        raise ReportError(f"diff does not apply cleanly to {f['path']}")
                    new.append(body)
                    pos += 1
                elif tag == "-":
                    if pos >= len(old) or old[pos] != body:
                        raise ReportError(f"diff does not apply cleanly to {f['path']}")
                    pos += 1
                else:
                    new.append(body)
        new.extend(old[pos:])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(new) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- test runs

def run_tests(ws: Workspace, test_command: str, approved: bool, root_override: str | None = None, files_for_copy=None) -> dict:
    """Run the project's tests via an approved template. Only python unittest is executable
    out of the box; other stacks need their build tool installed and approval."""
    cmd = (test_command or "").strip()
    if re.match(r"^python3? -m unittest", cmd):
        tid, params = "python-unittest", {"tests_dir": (re.search(r"-s\s+(\S+)", cmd) or [None, "tests"])[1]}
    elif cmd.startswith("mvn"):
        tid, params = "maven-test", {}
    elif cmd.startswith("npm"):
        tid, params = "npm-test", {}
    elif cmd.startswith("dotnet"):
        tid, params = "dotnet-test", {}
    else:
        return {"status": "blocked", "reason": "No approved command template matches this test command. Import a report instead."}
    res = runner.run(tid, params, root_override or str(ws.root), approved)
    if res.get("status") == "completed" and tid == "python-unittest":
        try:
            res["report"] = parse_unittest(res["stderr"] + "\n" + res["stdout"])
        except ReportError as e:
            res["report_error"] = str(e)
    return res


def _key(t):
    return f"{t['classname']}::{t['name']}"


def verify_defect_fix(ws: Workspace, diff_text: str, test_command: str, approved: bool) -> dict:
    """Run tests on temporary copies: (A) tests-only from the diff applied, (B) full diff applied."""
    files = parse_diff(diff_text)
    copy_files = ws.files()
    runs = {}
    for label, only_tests in (("before", True), ("after", False)):
        d = runner.temp_copy(ws, copy_files)
        try:
            apply_diff(d, files, only_tests=only_tests)
            r = run_tests(ws, test_command, approved, root_override=d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        runs[label] = r
    return evaluate_defect(files, runs.get("before"), runs.get("after"))


def evaluate_defect(files, before, after) -> list[dict] | dict:
    test_files = [f["path"] for f in files if f["is_test"]]
    b = (before or {}).get("report")
    a = (after or {}).get("report")
    results = []
    flipped = []
    if b and a:
        bstat = {_key(t): t["status"] for t in b["tests"]}
        flipped = [t for t in a["tests"] if t["status"] == "passed" and bstat.get(_key(t)) in ("failed", "error")]
    in_change = [t for t in flipped if any(t["classname"].startswith(Path(p).with_suffix("").as_posix().replace("/", "."))
                                            for p in test_files)]
    if not test_files:
        hint = (" An existing test (" + ", ".join(t["name"] for t in flipped) + ") fails before and passes after: name it as the "
                "reproduction or add a dedicated regression test.") if flipped else ""
        results.append(check("defect.repro_test_in_change", "Regression test in the change", "compass", "1.0", FAILED,
                             detail="The fix changes no test file, so nothing in the change reproduces the defect." + hint))
    else:
        results.append(check("defect.repro_test_in_change", "Regression test in the change", "compass", "1.0",
                             PASSED if in_change else FAILED,
                             detail=("Regression test(s) in the change: " + ", ".join(t["name"] for t in in_change)) if in_change
                             else "Test files changed, but none of their tests fails before the fix."))
    if not b:
        results.append(check("defect.fails_before", "Reproduction fails before the fix", "compass", "1.0", NOT_CHECKED,
                             detail=(before or {}).get("reason") or "No before-fix test evidence. A fix without reproduction evidence is not accepted."))
    else:
        results.append(check("defect.fails_before", "Reproduction fails before the fix", "compass", "1.0",
                             PASSED if flipped else FAILED,
                             detail=f"Before: {b['counts']['failed']} failed, {b['counts']['passed']} passed. "
                                    + ("Failing before and passing after: " + ", ".join(t["name"] for t in flipped) if flipped
                                       else "No test failed before the fix, so the defect was not reproduced.")))
    if not a:
        results.append(check("defect.passes_after", "Passes after the fix (full suite)", "compass", "1.0", NOT_CHECKED,
                             detail=(after or {}).get("reason") or "No after-fix test evidence."))
    else:
        ok = a["counts"]["failed"] == 0 and a["counts"]["error"] == 0 and a["ran"] > 0
        results.append(check("defect.passes_after", "Passes after the fix (full suite)", "compass", "1.0", PASSED if ok else FAILED,
                             detail=f"After: {a['counts']['passed']} passed, {a['counts']['failed']} failed, {a['counts']['error']} errors."))
    results.append(secrets_in_diff(files))
    return {"checks": results, "runs": {"before": _strip(before), "after": _strip(after)}, "diff_files": [
        {k: f[k] for k in ("path", "added", "removed", "is_test", "new_file")} for f in files]}


def _strip(r):
    if not r:
        return None
    return {k: v for k, v in r.items() if k not in ("stdout", "stderr")} | {"output_tail": (r.get("stderr", "") + r.get("stdout", ""))[-1500:]}


def evaluate_tests_detect_defect(report: dict, fixture: dict | None) -> list[dict]:
    """For a run against code with a KNOWN (declared, synthetic) defect."""
    out = []
    if not report:
        return [check("tests.ran", "Tests ran", "compass", "1.0", NOT_CHECKED, detail="No test run or report yet.")]
    out.append(check("tests.ran", "Tests ran", "compass", "1.0", PASSED if report["ran"] > 0 else FAILED,
                     detail=f"{report['ran']} tests ran ({report['counts']['passed']} passed, {report['counts']['failed']} failed, "
                            f"{report['counts']['error']} errors)."))
    if not fixture or not fixture.get("seeded_defects"):
        out.append(check("tests.detects_defect", "Tests detect a known defect", "compass", "1.0", NOT_CHECKED,
                         detail="No known defect declared for this project. Mutation testing (for example Stryker for JS/TS) is an optional capability, not enabled."))
        return out
    failing = [t for t in report["tests"] if t["status"] == "failed"]
    sd = fixture["seeded_defects"][0]
    out.append(check("tests.detects_defect", "Tests detect the known defect", "compass", "1.0", PASSED if failing else FAILED,
                     detail=(f"Known synthetic defect {sd['id']} at {sd['file']}:{sd['line']}. " +
                             ("Detected by: " + ", ".join(t["name"] for t in failing) if failing
                              else "The whole suite passes on broken code, so these tests do not verify the behavior."))))
    by_file = {}
    for t in report["tests"]:
        by_file.setdefault(t["classname"].rsplit(".", 1)[0], []).append(t)
    weak = [m for m, ts in by_file.items() if ts and all(t["status"] == "passed" for t in ts)]
    out.append(check("tests.weak_suite_flagged", "Tests that pass on broken code", "compass", "1.0", FAILED if weak else PASSED,
                     detail=("These test modules pass even though the known defect is present, so they check existence or type, "
                             "not behavior: " + ", ".join(weak)) if weak else "Every test module has at least one test that fails on the defect."))
    return out


def evaluate_report_for_feature(report: dict | None, label: str) -> dict:
    if not report:
        return check("tests.ran_and_passed", "Tests ran and passed", "compass", "1.0", NOT_CHECKED,
                     detail="No test report imported or run. A test file that exists is not proof that it ran.")
    ok = report["ran"] > 0 and report["counts"]["failed"] == 0 and report["counts"]["error"] == 0
    failing = [t for t in report["tests"] if t["status"] in ("failed", "error")]
    return check("tests.ran_and_passed", "Tests ran and passed", report["format"], "", PASSED if ok else FAILED,
                 findings=[finding(report["format"], "test-failure", t["classname"], None, "failure", t["message"] or t["name"],
                                   "Fix the code or the test, then re-run.", claim="confirmed") for t in failing],
                 detail=f"{label}: {report['ran']} ran, {report['counts']['failed']} failed, {report['counts']['skipped']} skipped.")
