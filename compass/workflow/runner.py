"""Safe execution of approved local tools.

* Only named command templates can run. Arguments are validated against strict
  patterns and paths must stay inside the project (or a Compass temp folder).
* Never uses a shell, so there is no interpolation.
* Scanners run only from a path the user approved in Settings, and only if the
  binary's SHA-256 still matches what was recorded at approval time.
* Minimal environment (no ambient secrets), stdin closed, timeout, output caps,
  CPU limit on POSIX, and cancellation.
* Running a project's tests executes the project's code. That requires explicit
  approval per run. Compass does not provide an OS sandbox; it says so, and
  security review of untrusted code stays static-only.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

from .. import settings

OUTPUT_CAP = 400_000
SAFE_PATH_ARG = re.compile(r"^[A-Za-z0-9_./\\: ~()-]{1,260}$")

TEMPLATES = {
    "python-unittest": {"exe": "python", "args": ["-m", "unittest", "discover", "-s", "{tests_dir}", "-t", ".", "-v"],
                        "params": {"tests_dir": SAFE_PATH_ARG}, "kind": "tests", "executes_project_code": True, "timeout": 120},
    "maven-test": {"exe": "mvn", "args": ["-q", "-o", "test"], "params": {}, "kind": "tests", "executes_project_code": True, "timeout": 600},
    "npm-test": {"exe": "npm", "args": ["test", "--silent"], "params": {}, "kind": "tests", "executes_project_code": True, "timeout": 600},
    "dotnet-test": {"exe": "dotnet", "args": ["test", "--nologo"], "params": {}, "kind": "tests", "executes_project_code": True, "timeout": 600},
    "gitleaks-dir": {"exe": "gitleaks", "args": ["dir", "{target}", "--report-format", "json", "--report-path", "{report}",
                                                  "--redact", "--no-banner", "--exit-code", "0"],
                     "params": {"target": SAFE_PATH_ARG, "report": SAFE_PATH_ARG}, "kind": "scan", "executes_project_code": False, "timeout": 120},
    "semgrep-local": {"exe": "semgrep", "args": ["scan", "--config", "{rules}", "--metrics", "off", "--disable-version-check",
                                                  "--json", "--quiet", "{target}"],
                      "params": {"rules": SAFE_PATH_ARG, "target": SAFE_PATH_ARG}, "kind": "scan", "executes_project_code": False, "timeout": 300},
    "spectral-lint": {"exe": "spectral", "args": ["lint", "{spec}", "--ruleset", "{ruleset}", "--format", "json", "--quiet"],
                      "params": {"spec": SAFE_PATH_ARG, "ruleset": SAFE_PATH_ARG}, "kind": "scan", "executes_project_code": False, "timeout": 120},
}
SCANNERS = ("gitleaks", "semgrep", "spectral")
BUILD_TOOLS = ("mvn", "npm", "dotnet")

_running: dict[str, subprocess.Popen] = {}
_lock = threading.Lock()


class RunError(Exception):
    pass


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def discover(name: str, path: str | None = None) -> dict:
    """Find a scanner candidate for the Settings page (does not approve it)."""
    if name not in SCANNERS:
        raise RunError("unknown scanner")
    cand = path or shutil.which(name)
    if not cand or not Path(cand).is_file():
        return {"name": name, "found": False}
    version = ""
    try:
        args = [cand, "version"] if name == "gitleaks" else [cand, "--version"]
        r = subprocess.run(args, capture_output=True, text=True, timeout=30, env=_env(), stdin=subprocess.DEVNULL)
        text = (r.stdout or "").strip() or (r.stderr or "").strip()
        version = text.splitlines()[-1][:60] if text else ""
    except (OSError, subprocess.TimeoutExpired):
        pass
    return {"name": name, "found": True, "path": str(Path(cand).resolve()), "version": version, "sha256": sha256_file(cand)}


def resolve_exe(name: str) -> tuple[str | None, str]:
    """Return (path, state). state: ok | not-installed | not-approved | hash-mismatch."""
    if name == "python":
        return sys.executable, "ok"
    if name in SCANNERS:
        rec = settings.load().get("scanners", {}).get(name)
        if not rec or not rec.get("path"):
            return None, "not-installed"
        if not rec.get("approved"):
            return None, "not-approved"
        if not Path(rec["path"]).is_file():
            return None, "not-installed"
        if sha256_file(rec["path"]) != rec.get("sha256"):
            return None, "hash-mismatch"
        return rec["path"], "ok"
    if name in BUILD_TOOLS:
        p = shutil.which(name)
        return (p, "ok") if p else (None, "not-installed")
    return None, "not-installed"


def _env() -> dict:
    keep = ("PATH", "SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC", "TEMP", "TMP", "HOME", "USERPROFILE", "LANG", "LC_ALL",
            "JAVA_HOME", "PATHEXT")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "SEMGREP_SEND_METRICS": "off", "NO_COLOR": "1", "CI": "true"})
    return env


def _limits():  # pragma: no cover - POSIX only
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
        resource.setrlimit(resource.RLIMIT_FSIZE, (200 * 1024 * 1024, 200 * 1024 * 1024))
    except Exception:
        pass
    os.setsid()


def run(template_id: str, params: dict, cwd: str, approved: bool, timeout: float | None = None,
        allowed_dirs: list[str] | None = None) -> dict:
    t = TEMPLATES.get(template_id)
    if not t:
        raise RunError("unknown command template")
    if t["executes_project_code"] and not approved:
        return {"status": "blocked", "reason": "Running tests executes the project's own code. Approve this run explicitly.",
                "template": template_id}
    exe, state = resolve_exe(t["exe"])
    if not exe:
        return {"status": "not-installed" if state == "not-installed" else "blocked", "reason": {
            "not-installed": f"{t['exe']} is not installed or not configured",
            "not-approved": f"{t['exe']} is installed but not approved in Settings",
            "hash-mismatch": f"{t['exe']} changed since it was approved (SHA-256 mismatch); re-approve it in Settings"}[state],
            "template": template_id}
    roots = [Path(cwd).resolve()] + [Path(d).resolve() for d in (allowed_dirs or [])]
    argv = [exe]
    for a in t["args"]:
        m = re.fullmatch(r"\{(\w+)\}", a)
        if not m:
            argv.append(a)
            continue
        name = m.group(1)
        val = str(params.get(name, ""))
        rx = t["params"].get(name)
        if not rx or not rx.fullmatch(val) or val.startswith("-") or ".." in Path(val).parts:
            raise RunError(f"invalid value for {name}")
        full = (Path(cwd) / val).resolve() if not Path(val).is_absolute() else Path(val).resolve()
        if not any(full == r or r in full.parents for r in roots):
            raise RunError(f"{name} must stay inside the project or the Compass temp folder")
        argv.append(val)
    run_id = uuid.uuid4().hex[:12]
    started = time.time()
    kwargs = dict(cwd=str(Path(cwd).resolve()), env=_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE, text=True, shell=False)
    if os.name == "posix":
        kwargs["preexec_fn"] = _limits
    else:  # pragma: no cover
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        proc = subprocess.Popen(argv, **kwargs)
    except OSError as e:
        return {"status": "blocked", "reason": f"could not start: {type(e).__name__}", "template": template_id}
    with _lock:
        _running[run_id] = proc
    try:
        out, err = proc.communicate(timeout=timeout or t["timeout"])
        status = "cancelled" if proc.returncode in (-9, -15) and run_id not in _running else "completed"
    except subprocess.TimeoutExpired:
        _kill(proc)
        out, err = proc.communicate()
        status = "timeout"
    finally:
        with _lock:
            _running.pop(run_id, None)
    return {"status": status, "run_id": run_id, "template": template_id, "exit_code": proc.returncode,
            "argv": [Path(argv[0]).name] + argv[1:], "stdout": (out or "")[:OUTPUT_CAP], "stderr": (err or "")[:OUTPUT_CAP],
            "duration_s": round(time.time() - started, 2), "executes_project_code": t["executes_project_code"],
            "sandbox": "none (no OS-enforced sandbox; run only code you trust)" if t["executes_project_code"] else "not needed (static scan)"}


def _kill(proc):
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:  # pragma: no cover
            proc.kill()
    except (OSError, ProcessLookupError):
        proc.kill()


def cancel(run_id: str) -> bool:
    with _lock:
        proc = _running.pop(run_id, None)
    if proc:
        _kill(proc)
        return True
    return False


def temp_copy(ws, files: list[str]) -> str:
    """Copy selected readable project files into a fresh temp folder (never the original)."""
    d = tempfile.mkdtemp(prefix="compass-run-")
    for rel in files:
        src = ws.safe_path(rel)
        dst = Path(d) / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return d
