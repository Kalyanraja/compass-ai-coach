"""Local user settings, captured by the first-run setup questions.

Stored in var/settings.json. Never stores secrets (Jira tokens come from an
environment variable or are kept in memory for the session only). Workspace
content can never change these settings: only the local Settings page writes them.
"""

from __future__ import annotations

import copy
import json
import threading
from pathlib import Path

from . import config

_lock = threading.Lock()
SETTINGS_FILE = config.DATA_DIR / "settings.json"

DEFAULTS = {
    "setup_complete": False,
    "approved_tools": {"copilot": True, "claude": True, "devin": True, "writing": False, "no_ai": True},
    "tools_see_internal_code": {"copilot": True, "claude": True, "devin": True, "writing": True},
    "allowed_roots": [str((config.ROOT / "examples").resolve())],
    "default_project": str((config.ROOT / "examples" / "java-orders-api").resolve()),
    "default_data_class": "internal",
    "context_budget": "balanced",
    "cache_enabled": False,
    "allow_test_execution": False,
    "scanners": {},  # name -> {"path", "version", "sha256", "approved": bool}
    "jira": {
        "mode": "off",  # off | cloud | datacenter
        "base_url": "",
        "email": "",
        "token_env": "COMPASS_JIRA_TOKEN",
        "acceptance_field": "",
        "default_jql": "assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC",
        "approved": False,
    },
}

ALLOWED_KEYS = set(DEFAULTS)


def _path() -> Path:
    return config.DATA_DIR / "settings.json"


def load() -> dict:
    with _lock:
        p = _path()
        data = copy.deepcopy(DEFAULTS)
        if p.exists():
            try:
                saved = json.loads(p.read_text(encoding="utf-8"))
                for k, v in saved.items():
                    if k in ALLOWED_KEYS:
                        if isinstance(v, dict) and isinstance(data.get(k), dict):
                            data[k].update(v)
                        else:
                            data[k] = v
            except (OSError, ValueError):
                pass
        return data


def save(update: dict) -> dict:
    """Merge a validated update into the settings file."""
    current = load()
    for k, v in update.items():
        if k not in ALLOWED_KEYS:
            raise ValueError(f"unknown setting: {k}")
        if k == "allowed_roots":
            roots = []
            for r in v:
                rp = Path(str(r)).expanduser()
                if not rp.is_absolute() or not rp.is_dir():
                    raise ValueError(f"not an existing absolute folder: {r}")
                if rp.resolve() == Path(rp.anchor) or rp.resolve() == Path.home().resolve():
                    raise ValueError("choose a project folder, not a whole drive or your home folder")
                roots.append(str(rp.resolve()))
            v = roots
        if k == "jira":
            j = dict(current["jira"])
            for jk, jv in v.items():
                if jk not in j:
                    raise ValueError(f"unknown jira setting: {jk}")
                if jk == "base_url" and jv and not str(jv).startswith("https://"):
                    raise ValueError("Jira base URL must start with https://")
                j[jk] = jv
            v = j
        if isinstance(v, dict) and isinstance(current.get(k), dict) and k != "scanners":
            merged = dict(current[k])
            merged.update(v)
            v = merged
        current[k] = v
    with _lock:
        p = _path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return current


def public_view(s: dict | None = None) -> dict:
    s = s or load()
    out = copy.deepcopy(s)
    import os
    out["jira"]["token_present"] = bool(os.environ.get(s["jira"].get("token_env") or "COMPASS_JIRA_TOKEN"))
    return out
