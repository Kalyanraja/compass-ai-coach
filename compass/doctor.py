"""`python -m compass doctor`: checks the local setup without changing anything."""

from __future__ import annotations

import json
import platform
import sys

from . import config, jira_client, settings
from .workflow import runner


def report() -> dict:
    s = settings.load()
    scanners = {}
    for name in runner.SCANNERS:
        path, state = runner.resolve_exe(name)
        scanners[name] = {"state": state, "path": path, "version": s["scanners"].get(name, {}).get("version")}
    build = {t: bool(runner.resolve_exe(t)[0]) for t in runner.BUILD_TOOLS}
    return {
        "python": sys.version.split()[0], "python_ok": sys.version_info >= (3, 9), "platform": platform.platform(),
        "data_dir": str(config.DATA_DIR), "setup_complete": s["setup_complete"], "allowed_roots": s["allowed_roots"],
        "approved_tools": s["approved_tools"], "scanners": scanners, "build_tools_on_path": build,
        "jira": jira_client.status(), "test_execution_allowed": s["allow_test_execution"], "cache_enabled": s["cache_enabled"],
        "llm_enhancer": bool(config.LLM_URL), "network": "Compass makes no outbound calls unless Jira or the optional LLM enhancer is configured.",
    }


def main():
    r = report()
    print(json.dumps(r, indent=2))
    ok = r["python_ok"]
    print("\nResult:", "ready" if ok else "Python 3.9+ required")
    return 0 if ok else 1
