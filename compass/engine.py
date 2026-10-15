"""Private recommendation engine.

Deterministic and explainable: every recommendation is produced by a named rule
with a fixed, practice-based threshold (never a comparison with colleagues), and
cites the exact synthetic records it was derived from.

Each recommendation always contains the four required elements:
observation, suggested action, rationale, outcome to monitor.
"""

from __future__ import annotations

from statistics import mean

from .practices import PRACTICES, SIGNAL_META, fmt

WINDOW = (5, 8)      # recent window (weeks) used for observations
BASELINE = (1, 4)    # earlier window, used to detect progress

STACK_CONTEXT = {
    "java": {"test_fw": "JUnit 5 with Mockito", "test_cmd": "mvn -q verify",
             "slice_hint": "keep API contract (OpenAPI / DTO) changes in a separate PR from service logic",
             "flaky_hint": "replace Thread.sleep with Awaitility and isolate test data per test"},
    "dotnet": {"test_fw": "xUnit with Moq", "test_cmd": "dotnet test",
               "slice_hint": "ship EF Core migrations separately from feature logic",
               "flaky_hint": "avoid shared static state and use IAsyncLifetime fixtures"},
    "typescript": {"test_fw": "Jest with React Testing Library", "test_cmd": "npm test",
                   "slice_hint": "separate component refactors from behavior changes",
                   "flaky_hint": "use findBy* queries instead of fixed timeouts"},
    "python": {"test_fw": "pytest", "test_cmd": "pytest -q",
               "slice_hint": "separate pipeline or schema config from transformation logic",
               "flaky_hint": "freeze time and seed randomness in fixtures"},
    "playwright": {"test_fw": "Playwright Test", "test_cmd": "npx playwright test",
                   "slice_hint": "one user journey per PR, with page objects in their own change",
                   "flaky_hint": "use web-first assertions and role-based locators instead of waitForTimeout"},
}

TOOL_LABEL = {
    "copilot": "GitHub Copilot (VS Code)",
    "claude": "Claude Code (VS Code)",
    "devin": "Devin (web)",
    "writing": "Copilot or Claude Code in Ask mode (office work)",
}


def window_metrics(rows: list[dict], weeks: tuple[int, int]) -> dict:
    sel = [r for r in rows if weeks[0] <= r["week"] <= weeks[1]]
    if not sel:
        return {}
    keys = [k for k in sel[0] if k not in ("record_id", "engineer_id", "week", "source")]
    return {k: round(mean(r[k] for r in sel), 3) for k in keys}


# --------------------------------------------------------------------------- rules
# Each rule: id, practice, trigger(m) -> bool, severity(m) -> 0..1, signals cited.

def _sev(value, threshold, span):
    return max(0.05, min(1.0, (value - threshold) / span)) if span > 0 else 0.5


RULES = [
    {"id": "R-PR-SIZE", "practice": "pr-slicing",
     "trigger": lambda m: m["pr_size_loc_median"] > 400,
     "severity": lambda m: _sev(m["pr_size_loc_median"], 400, 400),
     "signals": ["pr_size_loc_median", "review_rounds_avg", "pr_cycle_time_hrs"],
     "guide": "Practice guideline: under 400 changed lines, 1-2 review rounds."},
    {"id": "R-REVIEW-ROUNDS", "practice": "pr-readiness-selfcheck",
     "trigger": lambda m: m["review_rounds_avg"] >= 2.5 and m["pr_size_loc_median"] <= 400,
     "severity": lambda m: _sev(m["review_rounds_avg"], 2.5, 2.0),
     "signals": ["review_rounds_avg", "pr_template_used_rate", "ci_first_pass_rate"],
     "guide": "Practice guideline: most reviews should close in 1-2 rounds."},
    {"id": "R-CI-FIRST-PASS", "practice": "verify-before-done",
     "trigger": lambda m: m["ci_first_pass_rate"] < 0.7 and m["agent_mode_share"] >= 0.45,
     "severity": lambda m: _sev(0.7 - m["ci_first_pass_rate"], 0, 0.3),
     "signals": ["ci_first_pass_rate", "agent_mode_share", "review_rounds_avg"],
     "guide": "Practice guideline: 85%+ of pushes pass CI the first time."},
    {"id": "R-FEW-TESTS", "practice": "test-first-acceptance",
     "trigger": lambda m: m["tests_added_per_pr"] < 1.0,
     "severity": lambda m: _sev(1.0 - m["tests_added_per_pr"], 0, 1.0),
     "signals": ["tests_added_per_pr", "test_creation_time_min", "tests_first_rate"],
     "guide": "Practice guideline: every behavior change ships with tests (2+ per PR is typical)."},
    {"id": "R-SLOW-TESTS", "practice": "test-first-acceptance",
     "trigger": lambda m: m["tests_added_per_pr"] >= 1.0 and m["test_creation_time_min"] > 90
     and m["ai_assisted_test_share"] < 0.3,
     "severity": lambda m: _sev(m["test_creation_time_min"], 90, 90),
     "signals": ["test_creation_time_min", "ai_assisted_test_share", "tests_first_rate"],
     "guide": "Practice guideline: draft the test plan with AI, then refine; aim for under 60 minutes per PR."},
    {"id": "R-LONG-SESSIONS", "practice": "plan-then-implement",
     "trigger": lambda m: m["chat_turns_avg"] > 12 or m["abandoned_session_rate"] > 0.3,
     "severity": lambda m: max(_sev(m["chat_turns_avg"], 12, 12), _sev(m["abandoned_session_rate"], 0.3, 0.3)),
     "signals": ["chat_turns_avg", "abandoned_session_rate", "plan_first_rate"],
     "guide": "Practice guideline: well-scoped sessions usually finish in under 10 turns."},
    {"id": "R-NO-CONTEXT", "practice": "context-pack",
     "trigger": lambda m: m["repo_has_instructions"] < 0.5 and m["agent_mode_share"] >= 0.4,
     "severity": lambda m: 0.6,
     "signals": ["repo_has_instructions", "agent_mode_share", "chat_turns_avg"],
     "guide": "Practice guideline: every repo used with agents has a short AGENTS.md or copilot-instructions.md."},
    {"id": "R-WRONG-TOOL-TEXT", "practice": "right-tool-for-task",
     "trigger": lambda m: m["noncode_tasks_in_coding_agent"] >= 3,
     "severity": lambda m: _sev(m["noncode_tasks_in_coding_agent"], 2, 6),
     "signals": ["noncode_tasks_in_coding_agent"],
     "guide": "Practice guideline: documents, emails and summaries belong in a writing assistant."},
    {"id": "R-WRONG-TOOL-LARGE", "practice": "right-tool-for-task",
     "trigger": lambda m: m["large_task_chat_sessions"] >= 3 and m["devin_sessions"] < 1,
     "severity": lambda m: _sev(m["large_task_chat_sessions"], 2, 6),
     "signals": ["large_task_chat_sessions", "devin_sessions"],
     "guide": "Practice guideline: long, well-specified, repo-wide work suits an asynchronous agent with a playbook."},
    {"id": "R-FLAKY-AI-TESTS", "practice": "flaky-test-hardening",
     "trigger": lambda m: m["flaky_test_rate"] > 0.05 and m["ai_assisted_test_share"] >= 0.5,
     "severity": lambda m: _sev(m["flaky_test_rate"], 0.05, 0.08),
     "signals": ["flaky_test_rate", "ai_assisted_test_share", "ci_first_pass_rate"],
     "guide": "Practice guideline: flaky rate under 2%; AI-generated tests reviewed for waits and shared state."},
    {"id": "R-LOW-ADOPTION", "practice": "starter-path",
     "trigger": lambda m: (m["copilot_sessions"] + m["claude_sessions"] + m["devin_sessions"]) < 4,
     "severity": lambda m: 0.5,
     "signals": ["copilot_sessions", "claude_sessions"],
     "guide": "Optional: a short guided path to try the tools you already have on a real ticket."},
]

RULES_BY_ID = {r["id"]: r for r in RULES}


def triggered_rules(m: dict) -> list[dict]:
    return [r for r in RULES if m and r["trigger"](m)]


# --------------------------------------------------------------------------- context

def _tool_for(rule_id: str, profile: dict) -> str:
    c = profile.get("project_complexity", "medium")
    if rule_id == "R-WRONG-TOOL-TEXT":
        return "writing"
    if rule_id == "R-WRONG-TOOL-LARGE":
        return "devin"
    if rule_id in ("R-LONG-SESSIONS", "R-PR-SIZE") and c == "high":
        return "claude"
    if rule_id == "R-NO-CONTEXT":
        return "copilot"
    return "copilot"


def _action(rule_id: str, m: dict, profile: dict) -> str:
    stack = STACK_CONTEXT.get(profile.get("stack"), STACK_CONTEXT["python"])
    sen = profile.get("seniority", "mid")
    lead = sen in ("senior", "lead")
    junior = sen == "junior"
    c = profile.get("project_complexity", "medium")

    if rule_id == "R-PR-SIZE":
        tool = "Claude Code (start in plan mode, skill: pr-slicing)" if c == "high" else "Copilot Chat (/slice-pr)"
        a = (f"On your next ticket, ask {tool} to propose 2-3 slices of under 400 lines before writing code; "
             f"for {profile.get('stack_label', 'your stack')} work, {stack['slice_hint']}.")
        if sen == "lead":
            a += " As a lead, consider adding a PR-size note to the team's AGENTS.md so every agent proposes slices."
        elif sen == "senior":
            a += " Pair it with a short PR-size note in the repo's AGENTS.md so agents propose slices by default."
        if junior:
            a += " Share the proposed slices with your reviewer before you start, so the split is agreed early."
        return a
    if rule_id == "R-REVIEW-ROUNDS":
        return (f"Before requesting review, run /pr-readiness in Copilot Chat (or the pr-readiness-selfcheck skill in Claude Code). "
                f"It checks tests, description, risks and debug leftovers and runs `{stack['test_cmd']}` so reviewers see evidence up front.")
    if rule_id == "R-CI-FIRST-PASS":
        a = (f"Add one line to your agent requests: 'Run `{stack['test_cmd']}` and lint, paste the summary, and do not say done without it.' "
             "The verification-before-completion skill does this automatically in Claude Code and Copilot.")
        if junior:
            a += " Start with one PR this week and compare the CI result."
        return a
    if rule_id == "R-FEW-TESTS":
        a = (f"Paste the story's acceptance criteria into Copilot Chat with /test-plan, review the happy, negative and boundary cases, "
             f"then use /write-tests to generate {stack['test_fw']} tests before or alongside the implementation.")
        if profile.get("stack") == "playwright":
            a = ("Use /test-plan with the story's acceptance criteria to list user journeys and negative paths first, then "
                 "/write-tests to generate Playwright Test specs with web-first assertions.")
        return a
    if rule_id == "R-SLOW-TESTS":
        return (f"Let the agent draft the first version: give Copilot agent mode the acceptance criteria plus one existing "
                f"{stack['test_fw']} test as a style example (/write-tests), then spend your time reviewing assertions instead of typing boilerplate.")
    if rule_id == "R-LONG-SESSIONS":
        if c == "high":
            a = ("Start complex sessions in Claude Code plan mode with the writing-plans skill: get a numbered plan (files, steps, tests, risks), "
                 "approve it, then run one step per session. Restart a session instead of steering past 10 turns.")
        else:
            a = ("Open sessions with /jira-to-plan in Copilot Chat to get a short plan first, approve it, then implement step by step. "
                 "Restart with a fresh brief instead of steering past 10 turns.")
        if junior:
            a += " Ask a teammate to sanity-check the first plan."
        return a
    if rule_id == "R-NO-CONTEXT":
        a = ("Run /create-agents-md in Copilot Chat once to draft an AGENTS.md (build and test commands, conventions, guardrails), "
             "edit it by hand to keep it short, and commit it. Copilot, Claude Code and Devin all read it.")
        if sen == "lead":
            a += " As a lead, this is a 30-minute task that helps everyone on the repo."
        elif sen == "senior":
            a += " It takes about 30 minutes and every teammate's agent sessions benefit."
        return a
    if rule_id == "R-WRONG-TOOL-TEXT":
        return ("Keep office work (status updates, emails, document rewrites) in a separate Copilot Chat or Claude Code conversation "
                "in Ask mode with a short brief (audience, tone, length) instead of mixing it into agent-mode coding sessions, "
                "so code context stays clean. Use the right-tool-for-task skill when unsure.")
    if rule_id == "R-WRONG-TOOL-LARGE":
        return "devin"
    if rule_id in ("R-LONG-SESSIONS", "R-PR-SIZE") and c == "high":
        return "claude"
    if rule_id == "R-NO-CONTEXT":
        return "copilot"
    return "copilot"


def _action(rule_id: str, m: dict, profile: dict) -> str:
    stack = STACK_CONTEXT.get(profile.get("stack"), STACK_CONTEXT["python"])
    sen = profile.get("seniority", "mid")
    lead = sen in ("senior", "lead")
    junior = sen == "junior"
    c = profile.get("project_complexity", "medium")

    if rule_id == "R-PR-SIZE":
        tool = "Claude Code (start in plan mode, skill: pr-slicing)" if c == "high" else "Copilot Chat (/slice-pr)"
        a = (f"On your next ticket, ask {tool} to propose 2-3 slices of under 400 lines before writing code; "
             f"for {profile.get('stack_label', 'your stack')} work, {stack['slice_hint']}.")
        if sen == "lead":
            a += " As a lead, consider adding a PR-size note to the team's AGENTS.md so every agent proposes slices."
        elif sen == "senior":
            a += " Pair it with a short PR-size note in the repo's AGENTS.md so agents propose slices by default."
        if junior:
            a += " Share the proposed slices with your reviewer before you start, so the split is agreed early."
        return a
    if rule_id == "R-REVIEW-ROUNDS":
        return (f"Before requesting review, run /pr-readiness in Copilot Chat (or the pr-readiness-selfcheck skill in Claude Code). "
                f"It checks tests, description, risks and debug leftovers and runs `{stack['test_cmd']}` so reviewers see evidence up front.")
    if rule_id == "R-CI-FIRST-PASS":
        a = (f"Add one line to your agent requests: 'Run `{stack['test_cmd']}` and lint, paste the summary, and do not say done without it.' "
             "The verification-before-completion skill does this automatically in Claude Code and Copilot.")
        if junior:
            a += " Start with one PR this week and compare the CI result."
        return a
    if rule_id == "R-FEW-TESTS":
        a = (f"Paste the story's acceptance criteria into Copilot Chat with /test-plan, review the happy, negative and boundary cases, "
             f"then use /write-tests to generate {stack['test_fw']} tests before or alongside the implementation.")
        if profile.get("stack") == "playwright":
            a = ("Use /test-plan with the story's acceptance criteria to list user journeys and negative paths first, then "
                 "/write-tests to generate Playwright Test specs with web-first assertions.")
        return a
    if rule_id == "R-SLOW-TESTS":
        return (f"Let the agent draft the first version: give Copilot agent mode the acceptance criteria plus one existing "
                f"{stack['test_fw']} test as a style example (/write-tests), then spend your time reviewing assertions instead of typing boilerplate.")
    if rule_id == "R-LONG-SESSIONS":
        if c == "high":
            a = ("Start complex sessions in Claude Code plan mode with the writing-plans skill: get a numbered plan (files, steps, tests, risks), "
                 "approve it, then run one step per session. Restart a session instead of steering past 10 turns.")
        else:
            a = ("Open sessions with /jira-to-plan in Copilot Chat to get a short plan first, approve it, then implement step by step. "
                 "Restart with a fresh brief instead of steering past 10 turns.")
        if junior:
            a += " Ask a teammate to sanity-check the first plan."
        return a
    if rule_id == "R-NO-CONTEXT":
        a = ("Run /create-agents-md in Copilot Chat once to draft an AGENTS.md (build and test commands, conventions, guardrails), "
             "edit it by hand to keep it short, and commit it. Copilot, Claude Code and Devin all read it.")
        if sen == "lead":
            a += " As a lead, this is a 30-minute task that helps everyone on the repo."
        elif sen == "senior":
            a += " It takes about 30 minutes and every teammate's agent sessions benefit."
        return a
    if rule_id == "R-WRONG-TOOL-TEXT":
        return ("Move status updates, emails and document rewrites to your approved writing assistant (for example Microsoft 365 Copilot where enabled) "
                "and keep the coding agents for code. Use the right-tool-for-task skill when unsure.")
    if rule_id == "R-WRONG-TOOL-LARGE":
        return ("For repo-wide, well-specified work (upgrades, migrations, repetitive fixes), hand it to Devin with the "
                "modernization-migration or dependency-upgrade playbook and review the PR, instead of driving it turn by turn in chat.")
    if rule_id == "R-FLAKY-AI-TESTS":
        return (f"Before merging AI-generated tests, run /fix-flaky-test or the flaky-test-hardening skill: {stack['flaky_hint']}, "
                "and run the suite 3 times locally to confirm stability.")
    if rule_id == "R-LOW-ADOPTION":
        return ("Try the 30-minute starter path on a real ticket: (1) add a context pack, (2) ask for a plan first, "
                "(3) run the readiness self-check before review. Entirely optional.")
    return "Review the linked practice."


def _rationale(rule: dict, m: dict, profile: dict) -> str:
    p = PRACTICES[rule["practice"]]
    ev = p["evidence"][0]
    who = {"junior": "while you build habits", "mid": "", "senior": "", "lead": "for you and the repo",
           "sdet": "for test automation work"}.get(profile.get("seniority"), "")
    ctx = f"{profile.get('stack_label', '')} work on a {profile.get('project_complexity', 'medium')}-complexity project"
    return (f"{p['title']} targets {' and '.join(SIGNAL_META[s][0] for s in rule['signals'][:2])}. "
            f"Evidence: {ev['claim']} ({ev['source']}). Tailored for {ctx}{(' ' + who) if who else ''}.")


def _observation(rule: dict, m: dict) -> str:
    parts = [f"{SIGNAL_META[s][0]}: {fmt(s, m[s], unit=True)}" for s in rule["signals"] if s in m]
    return f"Over the last 4 weeks: {'; '.join(parts)}. {rule['guide']}"


def _outcome(rule: dict, m: dict) -> dict:
    p = PRACTICES[rule["practice"]]
    primary = rule["signals"][0]
    from .practices import apply_effect
    eff = p["simulation"].get(primary)
    target = apply_effect(primary, m[primary], eff) if eff else None
    label, unit, better = SIGNAL_META[primary]
    return {
        "signal": primary,
        "label": label,
        "baseline": m[primary],
        "baseline_display": fmt(primary, m[primary]),
        "target": target,
        "target_display": fmt(primary, target) if target is not None else "trend " + better,
        "direction": better,
        "review_after_weeks": 2,
        "text": f"Watch {label} over your next 2 weeks of work: from {fmt(primary, m[primary], unit=True)} toward "
                f"{fmt(primary, target, unit=True) if target is not None else 'a ' + better + ' value'}. Only you see this.",
    }


def build_recommendation(rule: dict, m: dict, profile: dict, evidence: list[dict]) -> dict:
    p = PRACTICES[rule["practice"]]
    tool = _tool_for(rule["id"], profile)
    return {
        "rec_key": rule["id"],
        "rule_id": rule["id"],
        "practice_id": rule["practice"],
        "practice_code": p["code"],
        "practice_title": p["title"],
        "action_type": p["type"],
        "workflow": p["workflow"],
        "severity": round(rule["severity"](m), 2),
        "observation": _observation(rule, m),
        "suggested_action": _action(rule["id"], m, profile),
        "rationale": _rationale(rule, m, profile),
        "outcome_to_monitor": _outcome(rule, m),
        "recommended_tool": {"id": tool, "label": TOOL_LABEL[tool]},
        "kit": p["kit"],
        "prompt_id": p["prompt_id"],
        "evidence_records": evidence,
        "sources": p["evidence"],
        "framing": "Optional coaching. Not a rating. Visible only to you.",
    }


def _evidence(rule: dict, rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if WINDOW[0] <= r["week"] <= WINDOW[1]:
            vals = {s: r[s] for s in rule["signals"] if s in r}
            out.append({"record_id": r["record_id"], "week": r["week"], "source": r["source"], "values": vals})
    return out


def recommend(profile: dict, usage_rows: list[dict], delivery_rows: list[dict],
              feedback: dict | None = None) -> dict:
    """Return the private recommendation set for one engineer.

    feedback maps rec_key -> latest action ('useful','not_useful','dismissed','restored','tried').
    It is private data owned by the engineer and only affects their own ordering.
    """
    feedback = feedback or {}
    merged = _merge(usage_rows, delivery_rows)
    m = window_metrics(merged, WINDOW)
    base = window_metrics(merged, BASELINE)
    recs = []
    for rule in triggered_rules(m):
        evidence = _evidence(rule, merged)
        recs.append(build_recommendation(rule, m, profile, evidence))

    # Growth suggestion when nothing is flagged, so the view is never empty.
    if not recs and m:
        rule = {"id": "R-GROWTH", "practice": "right-tool-for-task",
                "severity": lambda _m: 0.1,
                "signals": ["devin_sessions", "large_task_chat_sessions"],
                "guide": "No workflow gaps detected. Optional growth idea below."}
        rec = build_recommendation(rule, m, profile, _evidence(rule, merged))
        rec["suggested_action"] = ("Pick one backlog chore (dependency bump, lint cleanup, test gap) and try it with Devin using a "
                                   "playbook from the agent kit, then compare the effort with doing it in chat.")
        rec["rec_key"] = "R-GROWTH"
        recs.append(rec)

    # Private feedback loop (AC13): affects only this engineer's ordering.
    weight = {"useful": 1.25, "not_useful": 0.5, "tried": 0.9}
    active, dismissed = [], []
    for r in recs:
        act = feedback.get(r["rec_key"])
        r["my_feedback"] = act
        r["rank_score"] = round(r["severity"] * weight.get(act, 1.0), 3)
        (dismissed if act == "dismissed" else active).append(r)
    active.sort(key=lambda r: r["rank_score"], reverse=True)

    # Progress: rules that fired in the baseline window but no longer fire.
    progress = []
    if base:
        now_ids = {r["id"] for r in triggered_rules(m)}
        for rule in triggered_rules(base):
            if rule["id"] not in now_ids:
                s = rule["signals"][0]
                progress.append({
                    "rule_id": rule["id"], "practice_id": rule["practice"],
                    "practice_title": PRACTICES[rule["practice"]]["title"],
                    "signal": s, "label": SIGNAL_META[s][0],
                    "before": base[s], "after": m[s],
                    "before_display": fmt(s, base[s]), "after_display": fmt(s, m[s]),
                    "text": f"{SIGNAL_META[s][0]} moved from {fmt(s, base[s])} (weeks 1-4) to {fmt(s, m[s])} (weeks 5-8).",
                })
    return {"window_weeks": list(WINDOW), "metrics": m, "baseline_metrics": base,
            "recommendations": active, "dismissed": dismissed, "progress": progress}


def _merge(usage_rows, delivery_rows):
    by_week = {}
    for r in usage_rows:
        by_week.setdefault(r["week"], {}).update({k: v for k, v in r.items()})
        by_week[r["week"]]["usage_record_id"] = r["record_id"]
    for r in delivery_rows:
        by_week.setdefault(r["week"], {}).update({k: v for k, v in r.items() if k not in ("record_id", "source")})
        by_week[r["week"]]["delivery_record_id"] = r["record_id"]
    out = []
    for w in sorted(by_week):
        row = by_week[w]
        row["record_id"] = f"{row.get('usage_record_id', '')}+{row.get('delivery_record_id', '')}"
        row["source"] = "synthetic:genai_usage_metadata + synthetic:scm_ci_metadata"
        row.pop("usage_record_id", None)
        row.pop("delivery_record_id", None)
        out.append(row)
    return out


def merged_rows(usage_rows, delivery_rows):
    return _merge(usage_rows, delivery_rows)


def simulate(profile: dict, usage_rows, delivery_rows, practice_id: str) -> dict:
    """Before/after projection (AC12). Applies the practice's documented, conservative
    simulation assumption to the engineer's recent weekly signals."""
    from .practices import apply_effect
    p = PRACTICES[practice_id]
    merged = _merge(usage_rows, delivery_rows)
    m = window_metrics(merged, WINDOW)
    series = {}
    for s, eff in p["simulation"].items():
        actual = [{"week": r["week"], "value": r[s]} for r in merged]
        projected = [{"week": 8 + i, "value": apply_effect(s, m[s], eff)} for i in range(1, 5)]
        series[s] = {
            "label": SIGNAL_META[s][0], "direction": SIGNAL_META[s][2],
            "before": m[s], "after": apply_effect(s, m[s], eff),
            "before_display": fmt(s, m[s]), "after_display": fmt(s, apply_effect(s, m[s], eff)),
            "actual": actual, "projected": projected, "assumption": list(eff),
        }
    return {"practice_id": practice_id, "practice_title": p["title"], "series": series,
            "label": "Simulated projection on synthetic data. Assumptions are documented in compass/practices.py; not a prediction about any person."}
