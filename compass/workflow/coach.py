"""Workflow packs, the missing-question engine and approved-tool recommendation."""

from __future__ import annotations

import json
import re
from functools import lru_cache

from .. import config, settings

PACK_DIR = config.ROOT / "workflows" / "packs"
CAPABILITIES = config.ROOT / "catalog" / "capabilities.json"
WORKING = ("feature-api", "uat-defect", "test-creation")
MAX_QUESTIONS = 3


@lru_cache(maxsize=1)
def packs() -> dict:
    out = {}
    for p in sorted(PACK_DIR.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for k in ("id", "version", "status", "title"):
            if k not in data:
                raise ValueError(f"pack {p.name} missing {k}")
        out[data["id"]] = data
    return out


def pack(pid: str) -> dict:
    p = packs().get(pid)
    if not p or p.get("status") != "working" or pid not in WORKING:
        raise KeyError(f"workflow '{pid}' is not available")
    return p


def pack_list() -> list[dict]:
    return [{"id": p["id"], "version": p["version"], "status": p["status"], "title": p["title"],
             "summary": p.get("summary", ""), "kind": p.get("kind", "workflow")} for p in packs().values()]


def classify(text: str) -> list[dict]:
    t = (text or "").lower()
    title = next((ln for ln in t.splitlines() if ln.strip()), "")
    scores = []
    for pid in WORKING:
        p = packs()[pid]
        hits = sum(1 for k in p["detect_keywords"] if k in t)
        hits += 2 * sum(1 for k in p["detect_keywords"] if k in title)  # the title says what the task is
        if pid == "test-creation" and re.search(r"\b(create|write|add|automate|improve)\b.*\btests?\b", title):
            hits += 4
        if pid == "uat-defect" and re.search(r"\b(defect|bug|fails?|broken|wrong|cannot|can't)\b", title):
            hits += 4
        scores.append({"id": pid, "title": p["title"], "score": hits})
    scores.sort(key=lambda s: -s["score"])
    return scores


# ---------------------------------------------------------------------- questions

def _cond(cond: dict, text: str, facts: dict, answers: dict) -> bool:
    if "any" in cond:
        return any(_cond(c, text, facts, answers) for c in cond["any"])
    if "all" in cond:
        return all(_cond(c, text, facts, answers) for c in cond["all"])
    if "text_lacks" in cond:
        return not re.search(cond["text_lacks"], text or "", re.I)
    if "fact_unknown" in cond:
        f = facts.get(cond["fact_unknown"])
        return not f or f["status"] == "unknown"
    if "fact_present" in cond:
        f = facts.get(cond["fact_present"])
        return bool(f) and f["status"] in ("detected", "confirmed", "inferred")
    if "fact_not_confirmed" in cond:
        f = facts.get(cond["fact_not_confirmed"])
        return not f or f["status"] in ("unknown", "inferred")
    return True


def next_questions(pid: str, text: str, facts: dict, answers: dict, skipped: list | None = None) -> dict:
    """Return at most three unanswered, relevant questions in priority order."""
    p = pack(pid)
    skipped = set(skipped or [])
    pending = []
    for q in sorted(p["questions"], key=lambda q: q["priority"]):
        if q["id"] in answers or q["id"] in skipped:
            continue
        if _cond(q.get("ask_if", {}), text, facts, answers):
            item = {k: q[k] for k in ("id", "text", "why", "priority")}
            if q["id"] == "test_command" and facts.get("test_command", {}).get("value"):
                item["suggested"] = facts["test_command"]["value"]
            if q["id"] == "header" and facts.get("standard_header_rule"):
                item["source"] = facts["standard_header_rule"].get("source")
            pending.append(item)
    return {"questions": pending[:MAX_QUESTIONS], "remaining": max(0, len(pending) - MAX_QUESTIONS),
            "total_open": len(pending)}


# ---------------------------------------------------------------------- tools

def catalog() -> dict:
    data = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    s = settings.load()
    for t in data["tools"]:
        if t["id"] in s["approved_tools"]:
            t["approved"] = bool(s["approved_tools"][t["id"]])
        if t["id"] in s.get("tools_see_internal_code", {}) and not s["tools_see_internal_code"][t["id"]]:
            t["allowed_data"] = [d for d in t["allowed_data"] if d != "internal"]
    return data


def recommend_tool(pid: str, data_class: str, complexity: str = "medium", large_scope: bool = False,
                   deterministic: bool = False) -> dict:
    """Policy first (approval, data class), then capability and task fit."""
    cat = catalog()
    tools = {t["id"]: t for t in cat["tools"]}
    options = []
    for t in cat["tools"]:
        reasons_blocked = []
        if not t["approved"]:
            reasons_blocked.append("not approved in your settings")
        if data_class not in t["allowed_data"]:
            reasons_blocked.append(f"not approved for {data_class} data")
        options.append({"id": t["id"], "label": t["label"], "allowed": not reasons_blocked,
                        "blocked_reason": "; ".join(reasons_blocked), "handoff": t["handoff"], "limits": t["limits"]})
    allowed = {o["id"] for o in options if o["allowed"]}
    reasons = []
    if data_class == "restricted":
        choice = "no_ai" if "no_ai" in allowed else None
        reasons.append("The task involves customer, personal or secret data. Remove or replace it with synthetic data before using any AI tool.")
    elif deterministic and "no_ai" in allowed:
        choice = "no_ai"
        reasons.append("This is deterministic work; the project's formatter, linter or test runner is faster, free and exact.")
    else:
        fit = cat["workflow_fit"].get(pid, {})
        choice = fit.get("large_scope") if large_scope and fit.get("large_scope") in allowed else None
        if choice:
            reasons.append("Repo-wide, well-specified work suits an asynchronous agent you review as a PR (repository must be connected in Devin).")
        else:
            pref = fit.get("prefer_by_complexity", {}).get(complexity)
            order = [pref, "copilot", "claude", "devin"]
            choice = next((c for c in order if c and c in allowed), None)
            needs = set(fit.get("needs", []))
            if choice:
                caps = set(tools[choice]["capabilities"])
                matched = sorted(caps & needs)
                reasons.append(f"Approved for {data_class} data and available to you.")
                if matched:
                    reasons.append("Fits this workflow: " + ", ".join(m.replace("-", " ") for m in matched) + ".")
                if choice == "claude":
                    reasons.append("Plan mode gives you a reviewable plan before any edit.")
                if choice == "copilot":
                    reasons.append("Fastest loop for a scoped change in files you have open.")
    if not choice:
        reasons.append("No approved tool fits this task under your settings. Ask your AI enablement team or work without AI.")
    return {"tool": choice, "label": tools[choice]["label"] if choice else None, "reasons": reasons,
            "handoff": tools[choice]["handoff"] if choice else None, "options": options,
            "policy_order": "approval and data rules first, then capability and task fit; you may override within policy"}
