"""Optional per-project cache. Off by default; enabled only with explicit permission
in Settings. Isolated per project and invalidated whenever the source snapshot,
settings, tool versions or rules change. Stale entries are deleted, never reused."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .. import config, settings

RULES_DIR = config.ROOT / "compass_rules"
PACK_DIR = config.ROOT / "workflows" / "packs"


def _dir(project_root: str) -> Path:
    return config.DATA_DIR / "cache" / hashlib.sha256(project_root.encode()).hexdigest()[:16]


def key_material(snapshot: str) -> str:
    s = settings.load()
    h = hashlib.sha256()
    h.update(snapshot.encode())
    h.update(json.dumps({k: s[k] for k in ("scanners", "approved_tools", "context_budget")}, sort_keys=True).encode())
    for d in (RULES_DIR, PACK_DIR):
        for p in sorted(d.glob("*")):
            h.update(p.name.encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def get(project_root: str, kind: str, key: str):
    if not settings.load().get("cache_enabled"):
        return None
    p = _dir(project_root) / f"{kind}.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        p.unlink(missing_ok=True)
        return None
    if data.get("key") != key:
        p.unlink(missing_ok=True)  # invalidated: never reuse stale results
        return None
    return data["value"]


def put(project_root: str, kind: str, key: str, value) -> bool:
    if not settings.load().get("cache_enabled"):
        return False
    d = _dir(project_root)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{kind}.json").write_text(json.dumps({"key": key, "value": value}), encoding="utf-8")
    return True


def clear() -> int:
    root = config.DATA_DIR / "cache"
    n = 0
    if root.exists():
        for p in root.rglob("*.json"):
            p.unlink()
            n += 1
    return n
