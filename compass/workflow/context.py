"""Explicit context budgeter.

Starts from a small project map and local search, then includes only relevant
files. Decisive files (for example the API spec and the project standard) are
always included in full; if they do not fit, the result reports an overflow and
asks the user to expand the budget instead of silently dropping them.

Token counts are ESTIMATES (about 4 characters per token); exact UTF-8 bytes are
always reported too. These numbers are not Copilot, Claude or Devin billing.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .workspace import Workspace, WorkspaceError

BUDGETS = {"lean": 4000, "balanced": 8000, "deep": 16000}
COUNT_METHOD = "estimate: ceil(characters / 4); exact UTF-8 bytes also reported; not a model tokenizer and not billing"
STOP = set("this that with from have when then they will must should into your their there what which while where about "
           "users user story order orders given able also only need needs some more each other than test tests".split())
WINDOW = 12
MIN_SCORE = 4
MAX_OPTIONAL = 5


def est_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def keywords(*texts: str) -> list[str]:
    words = []
    for t in texts:
        for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", t or ""):
            lw = w.lower()
            if lw not in STOP and lw not in words:
                words.append(lw)
    return words[:40]


def _lang(path: str) -> str:
    return {".py": "python", ".java": "java", ".ts": "ts", ".js": "js", ".cs": "csharp", ".yaml": "yaml", ".yml": "yaml",
            ".json": "json", ".xml": "xml", ".md": "markdown", ".sql": "sql", ".ini": "ini", ".toml": "toml"}.get(
        Path(path).suffix.lower(), "")


def _score(ws: Workspace, rel: str, kws: list[str]) -> tuple[int, list[int]]:
    try:
        lines = ws.lines(rel)
    except WorkspaceError:
        return 0, []
    s = 0
    hits = []
    low_path = rel.lower()
    for k in kws:
        if k in low_path:
            s += 3
    for i, ln in enumerate(lines, start=1):
        ll = ln.lower()
        n = sum(1 for k in kws if k in ll)
        if n:
            s += n
            hits.append(i)
    return s, hits


def decisive_files(ws: Workspace, facts: dict, pack: dict, kws: list[str]) -> list[dict]:
    out = []
    files = ws.files()
    for d in pack.get("decisive_context", []):
        if d in ("api_spec", "api_standard"):
            f = facts.get(d)
            if f and f.get("value"):
                out.append({"path": f["value"], "reason": f"decisive: {f['label']}"})
        elif d == "suspect_source":
            src = [f for f in files if Path(f).suffix in (".py", ".java", ".ts", ".js", ".cs")
                   and not re.search(r"(^|/)(tests?|src/test)/|Test\.|_test\.|\.spec\.", f) and not f.endswith("__init__.py")]
            scored = sorted(((s, f) for f in src for s in [_score(ws, f, kws)[0]] if s > 0), reverse=True)[:2]
            out += [{"path": f, "reason": "decisive: most relevant source for this task"} for _, f in scored]
        elif d == "existing_tests":
            tests = facts.get("existing_tests", {}).get("value") or []
            scored = sorted(((_score(ws, f, kws)[0], f) for f in tests), reverse=True)[:2]
            out += [{"path": f, "reason": "decisive: related existing test"} for _, f in scored]
    seen, uniq = set(), []
    for o in out:
        if o["path"] not in seen:
            seen.add(o["path"])
            uniq.append(o)
    return uniq


def build_context(ws: Workspace, facts: dict, pack: dict, goal: str, answers: dict, budget: str = "balanced",
                  skeleton_tokens: int = 0, include: list | None = None, exclude: list | None = None) -> dict:
    limit = BUDGETS.get(budget, BUDGETS["balanced"])
    room = max(0, int(limit * 0.93) - skeleton_tokens)  # margin for headings and fences
    kws = keywords(goal, " ".join(str(v) for v in answers.values())) + [k for k in pack.get("context_keywords", [])]
    exclude = set(exclude or [])
    required = [d for d in decisive_files(ws, facts, pack, kws) if d["path"] not in exclude]
    req_paths = {d["path"] for d in required}
    files_set = set(ws.files())
    for m in re.findall(r"[\w./-]+\.(?:py|java|ts|tsx|js|cs|ya?ml|json|md|sql|xml|kt)\b", goal or ""):
        m = m.strip("./")
        if m in files_set and m not in req_paths and m not in exclude:
            required.append({"path": m, "reason": "named in the task"})
            req_paths.add(m)
    for p in include or []:
        ws.safe_path(p)  # validates
        if p not in req_paths:
            required.append({"path": p, "reason": "selected by you"})
            req_paths.add(p)

    items, used = [], 0
    overflow = None
    for d in required:
        text = ws.read(d["path"])
        t = est_tokens(text)
        items.append({"path": d["path"], "reason": d["reason"], "mode": "full", "lines": f"1-{len(text.splitlines())}",
                      "tokens": t, "bytes": len(text.encode()), "content": text, "required": True})
        used += t
    if used > room:
        overflow = {"required_tokens": used, "budget_tokens": room,
                    "message": (f"Decisive context needs about {used:,} tokens but the {budget} budget leaves about {room:,}. "
                                "Choose a larger budget or deselect a file explicitly. Compass will not silently drop decisive code or standards.")}

    excluded = []
    candidates = []
    docs = set((facts.get("documents") or {}).get("value") or [])
    for rel in ws.files():
        if rel in req_paths or rel in exclude:
            if rel in exclude:
                excluded.append({"path": rel, "reason": "excluded by you"})
            continue
        if rel in docs or rel.startswith("recorded/"):
            excluded.append({"path": rel, "reason": "already in the goal or a recorded artifact"})
            continue
        if rel.endswith((".diff", ".patch")) or rel in ("compass-fixture.json",):
            excluded.append({"path": rel, "reason": "patches and fixture metadata are never sent as context"})
            continue
        s, hits = _score(ws, rel, kws)
        if s >= MIN_SCORE:
            candidates.append((s, rel, hits))
        elif s > 0:
            excluded.append({"path": rel, "reason": f"low relevance ({s})"})
    candidates.sort(reverse=True)
    for extra in candidates[MAX_OPTIONAL:]:
        excluded.append({"path": extra[1], "reason": f"lower relevance ({extra[0]}); ask to expand"})
    for s, rel, hits in candidates[:MAX_OPTIONAL]:
        text = ws.read(rel)
        t = est_tokens(text)
        if overflow is None and used + t <= room:
            items.append({"path": rel, "reason": f"relevance {s}", "mode": "full", "lines": f"1-{len(text.splitlines())}",
                          "tokens": t, "bytes": len(text.encode()), "content": text, "required": False})
            used += t
            continue
        lines = text.splitlines()
        ranges = []
        for h in hits[:6]:
            a, b = max(1, h - WINDOW), min(len(lines), h + WINDOW)
            if ranges and a <= ranges[-1][1] + 1:
                ranges[-1][1] = max(ranges[-1][1], b)
            else:
                ranges.append([a, b])
        excerpt = "\n".join(f"// lines {a}-{b}\n" + "\n".join(lines[a - 1:b]) for a, b in ranges)
        et = est_tokens(excerpt)
        if overflow is None and ranges and used + et <= room:
            items.append({"path": rel, "reason": f"relevance {s}", "mode": "excerpt",
                          "lines": ", ".join(f"{a}-{b}" for a, b in ranges) + f" of {len(lines)}",
                          "tokens": et, "bytes": len(excerpt.encode()), "content": excerpt, "required": False,
                          "truncated": True})
            used += et
        else:
            excluded.append({"path": rel, "reason": "outside budget" if overflow is None else "budget exceeded by decisive files",
                             "tokens": t})
    return {"budget": budget, "budget_tokens": limit, "keywords": kws[:15], "items": items, "excluded": excluded,
            "used_tokens": used, "overflow": overflow, "count_method": COUNT_METHOD}


def naive_full_dump_size(ws: Workspace) -> dict:
    """What pasting every readable project file would cost, for an honest comparison."""
    total_chars = total_bytes = 0
    for rel in ws.files():
        try:
            t = ws.read(rel)
        except WorkspaceError:
            continue
        total_chars += len(t)
        total_bytes += len(t.encode())
    return {"files": len(ws.files()), "tokens": math.ceil(total_chars / 4), "bytes": total_bytes, "count_method": COUNT_METHOD}
