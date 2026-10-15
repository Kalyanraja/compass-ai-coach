"""Recommendation-quality evaluation (AC2, AC3, AC6, AC8) and prompt-coach routing eval.

Every scenario is graded on five deterministic checks:
  relevant        - the expected rule(s) fire and no forbidden rule fires
  complete        - all four elements (observation, action, rationale, outcome) are populated
  explainable     - rationale cites a source and every evidence record id exists in the input
  actionable      - action names a concrete step/tool/kit file and the outcome has a signal and target
  persona_specific- the recommendation reflects role, stack or complexity (not boilerplate)

A scenario passes only if all checks pass. Results are written to reports/.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from . import config, db, engine, prompt_coach
from .practices import PRACTICES

HEALTHY = {
    "copilot_sessions": 14, "claude_sessions": 5, "devin_sessions": 1, "agent_mode_share": 0.35,
    "suggestion_accept_rate": 0.32, "chat_turns_avg": 6.5, "abandoned_session_rate": 0.12,
    "noncode_tasks_in_coding_agent": 0, "large_task_chat_sessions": 0, "repo_has_instructions": 1,
    "prs_opened": 4, "pr_size_loc_median": 210, "pr_cycle_time_hrs": 26, "review_rounds_avg": 1.6,
    "ci_first_pass_rate": 0.86, "tests_added_per_pr": 2.6, "test_creation_time_min": 45,
    "flaky_test_rate": 0.02, "ai_assisted_test_share": 0.45, "pr_template_used_rate": 0.8,
    "plan_first_rate": 0.6, "tests_first_rate": 0.5,
}
USAGE_KEYS = ["copilot_sessions", "claude_sessions", "devin_sessions", "agent_mode_share", "suggestion_accept_rate",
              "chat_turns_avg", "abandoned_session_rate", "noncode_tasks_in_coding_agent", "large_task_chat_sessions",
              "repo_has_instructions"]
STACK_LABEL = {"java": "Java / Spring Boot", "dotnet": ".NET / C#", "typescript": "TypeScript / React",
               "python": "Python", "playwright": "Playwright (TypeScript) test automation"}
ACTION_HINTS = r"(/[a-z-]+|skill|playbook|AGENTS\.md|plan mode|Copilot|Claude Code|Devin|writing assistant|run `|starter path)"


def _rows(sid: str, signals: dict):
    vals = {**HEALTHY, **signals}
    usage, delivery = [], []
    for w in range(1, 9):
        u = {"record_id": f"U-{sid}-W{w:02d}", "engineer_id": sid, "week": w, "source": "synthetic:eval_scenario"}
        d = {"record_id": f"D-{sid}-W{w:02d}", "engineer_id": sid, "week": w, "source": "synthetic:eval_scenario"}
        for k, v in vals.items():
            (u if k in USAGE_KEYS else d)[k] = v
        usage.append(u)
        delivery.append(d)
    return usage, delivery


def _profile(p: dict) -> dict:
    return {**p, "stack_label": STACK_LABEL[p["stack"]], "role": p["seniority"]}


def grade_rec(rec: dict, profile: dict, valid_ids: set) -> dict:
    four = all([rec.get("observation"), rec.get("suggested_action"), rec.get("rationale"),
                rec.get("outcome_to_monitor", {}).get("text")])
    explain = ("Evidence:" in rec["rationale"] and bool(rec["sources"]) and bool(rec["evidence_records"])
               and all(part in valid_ids for e in rec["evidence_records"] for part in e["record_id"].split("+")))
    actionable = (len(rec["suggested_action"].split()) >= 15 and re.search(ACTION_HINTS, rec["suggested_action"]) is not None
                  and rec["outcome_to_monitor"].get("signal") is not None
                  and rec["outcome_to_monitor"].get("target") is not None)
    stack_ctx = engine.STACK_CONTEXT.get(profile["stack"], {})
    tokens = [profile["stack_label"]] + [v for v in stack_ctx.values() if isinstance(v, str)]
    persona = (profile["stack_label"] in rec["rationale"] and profile["project_complexity"] in rec["rationale"])
    return {"complete": bool(four), "explainable": bool(explain), "actionable": bool(actionable),
            "persona_specific": bool(persona),
            "stack_specific_action": any(t.split(" ")[0] in rec["suggested_action"] for t in tokens if t)}


def run_scenarios(spec: dict) -> list[dict]:
    results = []
    for s in spec["scenarios"]:
        prof = _profile(s["profile"])
        usage, delivery = _rows(s["id"], s["signals"])
        valid = {r["record_id"] for r in usage + delivery}
        out = engine.recommend(prof, usage, delivery)
        recs = out["recommendations"]
        fired = [r["rule_id"] for r in recs]
        relevant = all(e in fired for e in s["expected_rules"]) and not any(f in fired for f in s["forbidden_rules"])
        if s["expected_rules"]:
            relevant = relevant and fired[0] in s["expected_rules"] or (relevant and len(s["expected_rules"]) > 1)
        grades = [grade_rec(r, prof, valid) for r in recs]
        checks = {
            "relevant": relevant,
            "complete": all(g["complete"] for g in grades),
            "explainable": all(g["explainable"] for g in grades),
            "actionable": all(g["actionable"] for g in grades),
            "persona_specific": all(g["persona_specific"] for g in grades),
        }
        results.append({
            "id": s["id"], "title": s["title"], "workflow": s["workflow"],
            "expected": s["expected_rules"], "fired": fired, "checks": checks, "passed": all(checks.values()),
            "top_recommendation": {k: recs[0][k] for k in ("practice_title", "observation", "suggested_action")} if recs else None,
        })
    return results


def run_context_pairs(spec: dict) -> list[dict]:
    out = []
    for c in spec["context_pairs"]:
        acts = []
        for side in ("a", "b"):
            prof = _profile(c[side])
            u, d = _rows(c["id"] + side, c["signals"])
            recs = [r for r in engine.recommend(prof, u, d)["recommendations"] if r["rule_id"] == c["rule"]]
            acts.append(recs[0]["suggested_action"] if recs else "")
        passed = bool(acts[0]) and bool(acts[1]) and acts[0] != acts[1]
        out.append({"id": c["id"], "rule": c["rule"], "persona_a": c["a"], "persona_b": c["b"],
                    "action_a": acts[0], "action_b": acts[1], "passed": passed})
    return out


def run_seeded_personas() -> list[dict]:
    """Check the 37 seeded synthetic personas: every seeded pattern should surface."""
    expected = {"large_prs": "R-PR-SIZE", "few_tests": "R-FEW-TESTS", "long_sessions": "R-LONG-SESSIONS",
                "no_context": "R-NO-CONTEXT", "wrong_tool": "R-WRONG-TOOL-TEXT", "flaky_ai_tests": "R-FLAKY-AI-TESTS",
                "low_adoption": "R-LOW-ADOPTION", "modernization_in_chat": "R-WRONG-TOOL-LARGE", "low_ci_pass": "R-CI-FIRST-PASS"}
    conn = db.signals_conn()
    res = []
    try:
        for e in db.rows(conn, "SELECT * FROM engineers"):
            labels = db.rows(conn, "SELECT patterns FROM seed_labels WHERE engineer_id=?", (e["engineer_id"],))[0]["patterns"].split("|")
            u = db.rows(conn, "SELECT * FROM usage_weekly WHERE engineer_id=?", (e["engineer_id"],))
            d = db.rows(conn, "SELECT * FROM delivery_weekly WHERE engineer_id=?", (e["engineer_id"],))
            out = engine.recommend(e, u, d)
            fired = {r["rule_id"] for r in out["recommendations"]}
            exp = {expected[p] for p in labels if p in expected}
            ok = exp <= fired
            if "adopter_pr" in labels or "adopter_tests" in labels:
                ok = ok and bool(out["progress"])
            if labels == ["healthy"]:
                ok = fired == {"R-GROWTH"}
            res.append({"persona": f"seeded-{len(res) + 1:02d}", "patterns": labels, "expected": sorted(exp),
                        "fired": sorted(fired), "progress_detected": bool(out["progress"]), "passed": ok})
    finally:
        conn.close()
    return res


def run_prompt_coach(spec: dict) -> list[dict]:
    out = []
    for s in spec["prompt_coach_stories"]:
        a = prompt_coach.analyze(s["text"])
        ok_type = a["task_type"] == s["expected_type"]
        ok_tool = a["recommendation"]["tool"] == s["expected_tool"]
        out.append({"id": s["id"], "expected_type": s["expected_type"], "got_type": a["task_type"],
                    "expected_tool": s["expected_tool"], "got_tool": a["recommendation"]["tool"],
                    "questions": len(a["questions"]), "passed": ok_type and ok_tool and len(a["questions"]) <= 3})
    return out


def _summary(rows, target=None):
    total = len(rows)
    passed = sum(1 for r in rows if r["passed"])
    s = {"total": total, "passed": passed, "pass_rate": round(passed / total, 3) if total else 0}
    if target is not None:
        s["target"] = target
        s["meets_target"] = s["pass_rate"] >= target
    return s


def run(write: bool = False) -> dict:
    spec = json.loads((config.ROOT / "eval" / "scenarios.json").read_text(encoding="utf-8"))
    db.init()
    scen = run_scenarios(spec)
    pairs = run_context_pairs(spec)
    seeded = run_seeded_personas()
    coach = run_prompt_coach(spec)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": _summary(scen, spec["target_pass_rate"]),
        "by_workflow": {wf: _summary([r for r in scen if r["workflow"] == wf]) for wf in ("pr_readiness", "test_creation")},
        "scenarios": scen,
        "context_awareness": {"summary": _summary(pairs), "pairs": pairs},
        "seeded_personas": {"summary": _summary(seeded), "personas": seeded},
        "prompt_coach": {"summary": _summary(coach), "stories": coach},
        "practices_identified": len([p for p in PRACTICES.values() if p["type"] != "learning"]),
    }
    if write:
        out = config.ROOT / "reports"
        out.mkdir(exist_ok=True)
        (out / "eval-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (out / "eval-report.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(r: dict) -> str:
    s = r["summary"]
    lines = [
        "# Compass evaluation report", "",
        f"Generated: {r['generated_at']} (deterministic; rerun with `python -m compass eval`)", "",
        "## Recommendation quality (AC3)", "",
        f"**{s['passed']} of {s['total']} seeded scenarios passed ({s['pass_rate']:.0%}). Target: {s['target']:.0%}. "
        f"Result: {'PASS' if s['meets_target'] else 'FAIL'}.**", "",
        "A scenario passes only if every check passes: relevant, complete (4 elements), explainable (cited source and traceable records), "
        "actionable (concrete step and measurable outcome) and persona-specific.", "",
        "| Scenario | Workflow | Expected | Fired | Relevant | Complete | Explainable | Actionable | Persona | Result |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    yn = lambda b: "yes" if b else "NO"
    for x in r["scenarios"]:
        c = x["checks"]
        lines.append(f"| {x['id']} {x['title']} | {x['workflow']} | {', '.join(x['expected']) or 'none'} | {', '.join(x['fired'])} | "
                     f"{yn(c['relevant'])} | {yn(c['complete'])} | {yn(c['explainable'])} | {yn(c['actionable'])} | "
                     f"{yn(c['persona_specific'])} | {'PASS' if x['passed'] else 'FAIL'} |")
    ca = r["context_awareness"]
    lines += ["", "## Context awareness (AC8)", "",
              f"{ca['summary']['passed']} of {ca['summary']['total']} pairs produced different actions for the same signal and different personas.", "",
              "| Pair | Rule | Persona A | Persona B | Different action |", "|---|---|---|---|---|"]
    for p in ca["pairs"]:
        pa, pb = p["persona_a"], p["persona_b"]
        lines.append(f"| {p['id']} | {p['rule']} | {pa['seniority']} {pa['stack']} {pa['project_complexity']} | "
                     f"{pb['seniority']} {pb['stack']} {pb['project_complexity']} | {yn(p['passed'])} |")
    sp = r["seeded_personas"]
    lines += ["", "## Seeded synthetic personas (AC6, AC12)", "",
              f"{sp['summary']['passed']} of {sp['summary']['total']} seeded personas surfaced every seeded pattern "
              "(adopters also show a before/after improvement; healthy personas get no gap alerts).", ""]
    pc = r["prompt_coach"]
    lines += ["## Prompt coach: task type and tool routing", "",
              f"{pc['summary']['passed']} of {pc['summary']['total']} stories classified and routed as expected, with 3 or fewer questions.", "",
              "| Story | Expected type | Got | Expected tool | Got | Pass |", "|---|---|---|---|---|---|"]
    for x in pc["stories"]:
        lines.append(f"| {x['id']} | {x['expected_type']} | {x['got_type']} | {x['expected_tool']} | {x['got_tool']} | {yn(x['passed'])} |")
    lines += ["", f"Reusable practices identified: {r['practices_identified']} (each cites the workflow signals it improves).", ""]
    return "\n".join(lines)
