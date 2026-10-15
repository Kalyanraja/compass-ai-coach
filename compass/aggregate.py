"""Manager and leader insights: aggregated, k-anonymous, no path to individuals.

Privacy rules enforced here (AC4, AC5, AC9, AC10):
* Only signals.db is read, opened read-only. This module never receives a
  connection to private.db, so feedback, dismissals and coaching history cannot
  appear in any output.
* A team with fewer than K engineers is fully suppressed.
* A pattern (workflow gap) is shown only when at least K engineers share it.
  Smaller groups are folded into a single "below threshold" count.
* Outputs contain no engineer ids, codenames, or per-person rows. There is no
  ranking or scoring of people, and teams are listed alphabetically, not ranked.
"""

from __future__ import annotations

from statistics import median

from . import config, db
from .engine import RULES_BY_ID, WINDOW, merged_rows, triggered_rules, window_metrics
from .practices import PRACTICES, SIGNAL_META, apply_effect, fmt

TEAM_SIGNALS = [
    "pr_size_loc_median", "review_rounds_avg", "pr_cycle_time_hrs", "ci_first_pass_rate",
    "tests_added_per_pr", "test_creation_time_min", "flaky_test_rate", "chat_turns_avg",
    "abandoned_session_rate", "repo_has_instructions",
]


def _load(conn, team_id: str | None = None):
    if team_id:
        engs = db.rows(conn, "SELECT engineer_id, team_id FROM engineers WHERE team_id=?", (team_id,))
    else:
        engs = db.rows(conn, "SELECT engineer_id, team_id FROM engineers")
    usage = db.rows(conn, "SELECT * FROM usage_weekly")
    delivery = db.rows(conn, "SELECT * FROM delivery_weekly")
    profiles = {e["engineer_id"]: e for e in engs}
    u_by, d_by = {}, {}
    for r in usage:
        if r["engineer_id"] in profiles:
            u_by.setdefault(r["engineer_id"], []).append(r)
    for r in delivery:
        if r["engineer_id"] in profiles:
            d_by.setdefault(r["engineer_id"], []).append(r)
    merged = {eid: merged_rows(u_by.get(eid, []), d_by.get(eid, [])) for eid in profiles}
    return merged


def _k(k):
    return k if k is not None else config.K_ANON


def summarize_group(merged: dict, k: int | None = None) -> dict:
    """Aggregate a group of engineers. `merged` maps an internal id to weekly rows;
    ids are used only for counting and never leave this function."""
    k = _k(k)
    n = len(merged)
    if n < k:
        return {"suppressed": True, "group_size": f"fewer than {k}",
                "reason": f"This group has fewer than {k} engineers, so no patterns are shown to protect individual privacy."}

    windows = {eid: window_metrics(rows, WINDOW) for eid, rows in merged.items()}
    windows = {e: w for e, w in windows.items() if w}

    # Tool adoption: share of engineers who used each tool in the window.
    adoption = {}
    for tool, col in (("GitHub Copilot", "copilot_sessions"), ("Claude Code", "claude_sessions"), ("Devin", "devin_sessions")):
        users = sum(1 for w in windows.values() if w[col] >= 1)
        adoption[tool] = _cell(users, n, k)

    medians = {}
    for s in TEAM_SIGNALS:
        vals = [w[s] for w in windows.values()]
        med = median(vals)
        medians[s] = {"label": SIGNAL_META[s][0], "value": round(med, 3), "display": fmt(s, med, unit=True),
                      "direction": SIGNAL_META[s][2]}

    # Weekly trend of medians; a week is shown only if >= k engineers have data.
    trend = {}
    for s in ("pr_size_loc_median", "review_rounds_avg", "tests_added_per_pr", "flaky_test_rate", "chat_turns_avg"):
        pts = []
        for wk in range(1, config.WEEKS + 1):
            vals = [r[s] for rows in merged.values() for r in rows if r["week"] == wk]
            pts.append({"week": wk, "value": round(median(vals), 3) if len(vals) >= k else None})
        trend[s] = {"label": SIGNAL_META[s][0], "points": pts}

    # Workflow gaps: count engineers per rule; show only if count >= k.
    counts = {}
    for w in windows.values():
        for rule in triggered_rules(w):
            counts[rule["id"]] = counts.get(rule["id"], 0) + 1
    gaps, hidden = [], 0
    for rid, c in sorted(counts.items(), key=lambda kv: kv[0]):
        if c >= k:
            rule = RULES_BY_ID[rid]
            p = PRACTICES[rule["practice"]]
            primary = rule["signals"][0]
            affected = [w for w in windows.values() if rule["trigger"](w)]
            group_med = median(w[primary] for w in affected)
            projected = apply_effect(primary, group_med, p["simulation"][primary]) if primary in p["simulation"] else None
            gaps.append({
                "rule_id": rid,
                "pattern": rule["guide"].replace("Practice guideline: ", "Below guideline: "),
                "engineers_affected": _bucket(c, n),
                "signal": primary, "signal_label": SIGNAL_META[primary][0],
                "group_median": fmt(primary, group_med, unit=True),
                "projected_if_adopted": fmt(primary, projected, unit=True) if projected is not None else None,
                "practice_id": rule["practice"], "practice_code": p["code"], "practice_title": p["title"],
                "enablement_opportunity": _opportunity(rule["practice"]),
                "kit": p["kit"],
            })
        else:
            hidden += 1
    return {
        "suppressed": False,
        "group_size": _bucket(n, n, exact_total=True),
        "k_threshold": k,
        "adoption": adoption,
        "medians": medians,
        "trend": trend,
        "workflow_gaps": gaps,
        "patterns_below_threshold": hidden,
        "privacy_note": (f"Patterns shared by fewer than {k} engineers are not shown. No individual recommendations, "
                         "prompts, coaching history, dismissals or feedback are used in this view."),
    }


def _bucket(c: int, n: int, exact_total=False) -> str:
    if exact_total:
        return f"{n} engineers"
    pct = round(100 * c / n / 10) * 10
    return f"about {pct}% of the group"


def _cell(count: int, n: int, k: int) -> dict:
    if count < k and count != 0:
        return {"display": f"hidden (fewer than {k})", "suppressed": True}
    return {"display": f"about {round(100 * count / n / 10) * 10}%", "suppressed": False, "share": round(count / n, 2)}


OPPORTUNITIES = {
    "pr-slicing": "Run a 30-minute team session on slicing work with the /slice-pr prompt; add a PR-size note to the repo's AGENTS.md.",
    "pr-readiness-selfcheck": "Add the pr-readiness prompt and skill to the team's repos and make the self-check part of the PR template.",
    "test-first-acceptance": "Pair the team's story template with acceptance criteria and roll out /test-plan and /write-tests from the agent kit.",
    "plan-then-implement": "Share the plan-then-implement pattern; add the writing-plans skill and /jira-to-plan prompt to the team's repos.",
    "context-pack": "Commit a short AGENTS.md and copilot-instructions.md to each team repo (30 minutes per repo, one owner).",
    "verify-before-done": "Add the verification-before-completion skill to the repos so agents always show test evidence.",
    "right-tool-for-task": "Share the tool-routing guide; set up Devin playbooks for recurring repo-wide tasks.",
    "flaky-test-hardening": "Adopt the flaky-test-hardening skill and the Playwright instructions file; add a 3x local rerun step for new AI-generated tests.",
    "starter-path": "Offer an optional hands-on starter session using the agent kit.",
}


def _opportunity(practice_id: str) -> str:
    return OPPORTUNITIES.get(practice_id, "Share the practice and the matching agent-kit files.")


def team_insights(team_id: str, k: int | None = None) -> dict:
    conn = db.signals_conn(readonly=True)
    try:
        team = db.rows(conn, "SELECT team_id, name, domain, stack, project_complexity FROM teams WHERE team_id=?", (team_id,))
        if not team:
            return {"error": "unknown team"}
        out = summarize_group(_load(conn, team_id), k)
        out["team"] = team[0]
        return out
    finally:
        conn.close()


def org_insights(k: int | None = None) -> dict:
    conn = db.signals_conn(readonly=True)
    try:
        teams = db.rows(conn, "SELECT team_id, name, domain, stack, project_complexity FROM teams ORDER BY name")
        per_team, org_members, excluded = [], {}, 0
        for t in teams:  # alphabetical, never ranked
            members = _load(conn, t["team_id"])
            s = summarize_group(members, k)
            if s["suppressed"]:
                # Excluded from org totals too, so "org minus visible teams" cannot
                # reveal anything about a small team (differencing protection).
                excluded += 1
            else:
                org_members.update(members)
            per_team.append({"team": t, "suppressed": s["suppressed"],
                             "group_size": s["group_size"],
                             "top_opportunities": [g["practice_title"] for g in s.get("workflow_gaps", [])][:3]})
        org = summarize_group(org_members, k)
        org["teams"] = per_team
        org["teams_excluded_for_privacy"] = excluded
        org["practice_discovery"] = practice_discovery(conn)
        return org
    finally:
        conn.close()


# --------------------------------------------------------------------------- discovery

DISCOVERY = [
    # practice, adoption flag (column, threshold), outcome signal
    ("pr-readiness-selfcheck", ("pr_template_used_rate", 0.6), "review_rounds_avg"),
    ("plan-then-implement", ("plan_first_rate", 0.4), "chat_turns_avg"),
    ("test-first-acceptance", ("tests_first_rate", 0.4), "tests_added_per_pr"),
    ("context-pack", ("repo_has_instructions", 0.5), "chat_turns_avg"),
    ("pr-slicing", ("pr_size_loc_median", -400), "review_rounds_avg"),
]


def practice_discovery(conn=None, k: int | None = None) -> list[dict]:
    """Find reusable practices from the synthetic data (AC7) with non-causal
    association statistics (AC14). Unit of analysis is the engineer-week; results
    are org-level only."""
    from .stats import pearson
    own = conn is None
    conn = conn or db.signals_conn(readonly=True)
    try:
        merged = _load(conn)
        weeks = [r for rows in merged.values() for r in rows]
        out = []
        for practice, (col, thr), outcome in DISCOVERY:
            if thr < 0:
                adopted = [r for r in weeks if r[col] <= -thr]
                not_adopted = [r for r in weeks if r[col] > -thr]
            else:
                adopted = [r for r in weeks if r[col] >= thr]
                not_adopted = [r for r in weeks if r[col] < thr]
            if len(adopted) < _k(k) or len(not_adopted) < _k(k):
                continue
            a = median(r[outcome] for r in adopted)
            b = median(r[outcome] for r in not_adopted)
            r_val = pearson([r[col] for r in weeks], [r[outcome] for r in weeks])
            p = PRACTICES[practice]
            out.append({
                "practice_id": practice, "practice_code": p["code"], "practice_title": p["title"],
                "adoption_signal": SIGNAL_META[col][0], "outcome_signal": SIGNAL_META[outcome][0],
                "cites_signals": [col, outcome],
                "median_with_practice": fmt(outcome, a), "median_without_practice": fmt(outcome, b),
                "pearson_r": r_val, "n_engineer_weeks": len(weeks),
                "label": "Association in synthetic data, not causation.",
            })
        return out
    finally:
        if own:
            conn.close()
