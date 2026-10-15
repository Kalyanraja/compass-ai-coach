"""Deterministic synthetic dataset generator.

Everything here is invented. There are no real people, no source code, no prompt
text and no free-text fields. Engineers are identified by a pseudonymous id and a
codename. Each weekly row carries a record_id and a `source` label so every
recommendation can cite exactly which rows it was derived from (traceability).

Seeded patterns create the coaching scenarios used in the demo and the eval.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import config

TEAMS = [
    # team_id, name, domain, stack, complexity, size, dominant patterns
    ("T-ATLAS", "Team Atlas", "Core services API", "java", "high", 10),
    ("T-BOREALIS", "Team Borealis", "Partner portal", "dotnet", "medium", 9),
    ("T-CIRRUS", "Team Cirrus", "Customer web app", "typescript", "medium", 8),
    ("T-ECHO", "Team Echo", "Data platform", "python", "high", 7),
    ("T-DELTA", "Team Delta", "Internal tooling", "python", "low", 3),
]

STACK_LABEL = {
    "java": "Java / Spring Boot",
    "dotnet": ".NET / C#",
    "typescript": "TypeScript / React",
    "python": "Python",
    "playwright": "Playwright (TypeScript) test automation",
}

CODENAMES = [
    "Falcon", "Otter", "Juniper", "Comet", "Harbor", "Maple", "Quartz", "Nimbus",
    "Cedar", "Pixel", "Atlas-7", "Lynx", "Sparrow", "Topaz", "Willow", "Orbit",
    "Basil", "Echo-3", "Kestrel", "Saffron", "Tundra", "Indigo", "Marlin", "Sage",
    "Vector", "Aspen", "Cobalt", "Fable", "Zephyr", "Granite", "Heron", "Onyx",
    "Raven", "Ember", "Delta-9", "Lumen", "Pebble",
]

ROLES = {
    "junior": "Associate Software Engineer",
    "mid": "Software Engineer",
    "senior": "Senior Software Engineer",
    "lead": "Lead Engineer",
    "sdet": "Software Development Engineer in Test",
}

# Pattern assignments per team (index -> patterns). Chosen so that each team has
# at least one gap shared by >= K_ANON engineers (visible to the manager) and
# several individual-only gaps (visible only privately).
TEAM_PATTERNS = {
    "T-ATLAS": [
        ("senior", ["large_prs", "no_context"]), ("mid", ["large_prs"]), ("mid", ["large_prs", "low_ci_pass"]),
        ("junior", ["large_prs", "low_adoption"]), ("lead", ["adopter_pr"]), ("mid", ["large_prs", "wrong_tool"]),
        ("senior", ["large_prs"]), ("mid", ["healthy"]), ("junior", ["few_tests"]), ("sdet", ["flaky_ai_tests"]),
    ],
    "T-BOREALIS": [
        ("mid", ["few_tests"]), ("senior", ["few_tests", "large_prs"]), ("junior", ["few_tests", "long_sessions"]),
        ("mid", ["few_tests"]), ("lead", ["adopter_tests"]), ("mid", ["few_tests", "wrong_tool"]),
        ("senior", ["healthy"]), ("sdet", ["flaky_ai_tests"]), ("junior", ["low_ci_pass"]),
    ],
    "T-CIRRUS": [
        ("sdet", ["flaky_ai_tests"]), ("sdet", ["flaky_ai_tests", "few_tests"]), ("mid", ["flaky_ai_tests"]),
        ("senior", ["flaky_ai_tests", "no_context"]), ("mid", ["flaky_ai_tests", "low_ci_pass"]),
        ("junior", ["long_sessions"]), ("lead", ["healthy"]), ("mid", ["wrong_tool"]),
    ],
    "T-ECHO": [
        ("senior", ["long_sessions", "no_context"]), ("mid", ["long_sessions", "no_context"]),
        ("mid", ["long_sessions", "no_context"]), ("junior", ["long_sessions", "no_context", "few_tests"]),
        ("lead", ["long_sessions", "no_context", "modernization_in_chat"]), ("mid", ["low_ci_pass"]),
        ("senior", ["modernization_in_chat"]),
    ],
    "T-DELTA": [
        ("mid", ["large_prs"]), ("senior", ["wrong_tool"]), ("junior", ["low_adoption"]),
    ],
}

USAGE_FIELDS = [
    "record_id", "engineer_id", "week", "copilot_sessions", "claude_sessions", "devin_sessions",
    "agent_mode_share", "suggestion_accept_rate", "chat_turns_avg", "abandoned_session_rate",
    "noncode_tasks_in_coding_agent", "large_task_chat_sessions", "repo_has_instructions", "source",
]
DELIVERY_FIELDS = [
    "record_id", "engineer_id", "week", "prs_opened", "pr_size_loc_median", "pr_cycle_time_hrs",
    "review_rounds_avg", "ci_first_pass_rate", "tests_added_per_pr", "test_creation_time_min",
    "flaky_test_rate", "ai_assisted_test_share", "pr_template_used_rate", "plan_first_rate",
    "tests_first_rate", "source",
]


@dataclass
class Engineer:
    engineer_id: str
    codename: str
    team_id: str
    seniority: str
    role: str
    stack: str
    stack_label: str
    project_complexity: str
    primary_workflows: str
    patterns: list = field(default_factory=list)


def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def _week_rows(rng: random.Random, eng: Engineer, week: int):
    """Return (usage_row, delivery_row) for one engineer-week."""
    p = set(eng.patterns)
    # Adopters show the problem in weeks 1-4 and the improved practice in weeks 5-8.
    if "adopter_pr" in p:
        p = p | ({"large_prs", "low_ci_pass"} if week <= 4 else {"adopted_pr"})
    if "adopter_tests" in p:
        p = p | ({"few_tests"} if week <= 4 else {"adopted_tests"})

    n = rng.gauss
    u = {
        "copilot_sessions": max(0, round(n(14, 3))),
        "claude_sessions": max(0, round(n(5, 2))),
        "devin_sessions": max(0, round(n(1, 0.8))),
        "agent_mode_share": round(_clip(n(0.35, 0.08), 0, 1), 2),
        "suggestion_accept_rate": round(_clip(n(0.32, 0.05), 0, 1), 2),
        "chat_turns_avg": round(_clip(n(6.5, 1.2), 1, 40), 1),
        "abandoned_session_rate": round(_clip(n(0.12, 0.04), 0, 1), 2),
        "noncode_tasks_in_coding_agent": max(0, round(n(0.6, 0.6))),
        "large_task_chat_sessions": max(0, round(n(0.4, 0.4))),
        "repo_has_instructions": 1,
    }
    d = {
        "prs_opened": max(1, round(n(4, 1))),
        "pr_size_loc_median": max(20, round(n(210, 45))),
        "pr_cycle_time_hrs": round(_clip(n(26, 6), 2, 400), 1),
        "review_rounds_avg": round(_clip(n(1.6, 0.25), 1, 10), 1),
        "ci_first_pass_rate": round(_clip(n(0.86, 0.05), 0, 1), 2),
        "tests_added_per_pr": round(_clip(n(2.6, 0.5), 0, 20), 1),
        "test_creation_time_min": round(_clip(n(45, 10), 5, 600)),
        "flaky_test_rate": round(_clip(n(0.02, 0.008), 0, 1), 3),
        "ai_assisted_test_share": round(_clip(n(0.45, 0.1), 0, 1), 2),
        "pr_template_used_rate": round(_clip(n(0.8, 0.1), 0, 1), 2),
        "plan_first_rate": round(_clip(n(0.6, 0.12), 0, 1), 2),
        "tests_first_rate": round(_clip(n(0.5, 0.12), 0, 1), 2),
    }

    if "large_prs" in p:
        d["pr_size_loc_median"] = round(n(640, 90))
        d["review_rounds_avg"] = round(_clip(n(3.3, 0.35), 1, 10), 1)
        d["pr_cycle_time_hrs"] = round(_clip(n(68, 10), 2, 400), 1)
        d["pr_template_used_rate"] = round(_clip(n(0.3, 0.1), 0, 1), 2)
        d["prs_opened"] = max(1, round(n(2, 0.6)))
    if "low_ci_pass" in p:
        d["ci_first_pass_rate"] = round(_clip(n(0.56, 0.06), 0, 1), 2)
        u["agent_mode_share"] = round(_clip(n(0.6, 0.06), 0, 1), 2)
        d["review_rounds_avg"] = round(max(d["review_rounds_avg"], _clip(n(2.6, 0.3), 1, 10)), 1)
    if "long_sessions" in p:
        u["chat_turns_avg"] = round(_clip(n(17, 2.5), 1, 40), 1)
        u["abandoned_session_rate"] = round(_clip(n(0.38, 0.06), 0, 1), 2)
        d["plan_first_rate"] = round(_clip(n(0.15, 0.06), 0, 1), 2)
    if "few_tests" in p:
        d["tests_added_per_pr"] = round(_clip(n(0.5, 0.2), 0, 20), 1)
        d["test_creation_time_min"] = round(_clip(n(118, 15), 5, 600))
        d["ai_assisted_test_share"] = round(_clip(n(0.12, 0.05), 0, 1), 2)
        d["tests_first_rate"] = round(_clip(n(0.08, 0.05), 0, 1), 2)
    if "no_context" in p:
        u["repo_has_instructions"] = 0
        u["agent_mode_share"] = round(_clip(n(0.55, 0.06), 0, 1), 2)
    if "wrong_tool" in p:
        u["noncode_tasks_in_coding_agent"] = max(3, round(n(5, 1)))
    if "flaky_ai_tests" in p:
        d["flaky_test_rate"] = round(_clip(n(0.09, 0.015), 0, 1), 3)
        d["ai_assisted_test_share"] = round(_clip(n(0.72, 0.06), 0, 1), 2)
    if "low_adoption" in p:
        u["copilot_sessions"] = max(0, round(n(1.5, 0.8)))
        u["claude_sessions"] = 0
        u["devin_sessions"] = 0
    if "modernization_in_chat" in p:
        u["large_task_chat_sessions"] = max(3, round(n(4, 1)))
        u["devin_sessions"] = 0
    if "adopted_pr" in p:
        d["pr_size_loc_median"] = round(n(260, 40))
        d["review_rounds_avg"] = round(_clip(n(1.7, 0.2), 1, 10), 1)
        d["pr_cycle_time_hrs"] = round(_clip(n(30, 5), 2, 400), 1)
        d["pr_template_used_rate"] = round(_clip(n(0.9, 0.05), 0, 1), 2)
        d["ci_first_pass_rate"] = round(_clip(n(0.85, 0.04), 0, 1), 2)
        d["prs_opened"] = max(1, round(n(4.5, 0.8)))
    if "adopted_tests" in p:
        d["tests_added_per_pr"] = round(_clip(n(2.9, 0.4), 0, 20), 1)
        d["test_creation_time_min"] = round(_clip(n(52, 8), 5, 600))
        d["ai_assisted_test_share"] = round(_clip(n(0.55, 0.06), 0, 1), 2)
        d["tests_first_rate"] = round(_clip(n(0.7, 0.08), 0, 1), 2)

    rid = f"{eng.engineer_id}-W{week:02d}"
    usage = {"record_id": f"U-{rid}", "engineer_id": eng.engineer_id, "week": week, **u,
             "source": "synthetic:genai_usage_metadata"}
    delivery = {"record_id": f"D-{rid}", "engineer_id": eng.engineer_id, "week": week, **d,
                "source": "synthetic:scm_ci_metadata"}
    return usage, delivery


def generate(seed: int = config.RANDOM_SEED, weeks: int = config.WEEKS):
    rng = random.Random(seed)
    teams, engineers, usage, delivery = [], [], [], []
    name_iter = iter(CODENAMES)
    for team_id, name, domain, stack, complexity, size in TEAMS:
        teams.append({"team_id": team_id, "name": name, "domain": domain, "stack": stack,
                      "project_complexity": complexity, "source": "synthetic:org_metadata"})
        for i, (seniority, patterns) in enumerate(TEAM_PATTERNS[team_id][:size], start=1):
            eng_stack = "playwright" if seniority == "sdet" else stack
            workflows = "test_creation" if seniority == "sdet" else "pr_readiness,test_creation"
            e = Engineer(
                engineer_id=f"E-{team_id[2:5]}-{i:02d}",
                codename=next(name_iter),
                team_id=team_id,
                seniority=seniority,
                role=ROLES[seniority],
                stack=eng_stack,
                stack_label=STACK_LABEL[eng_stack],
                project_complexity=complexity,
                primary_workflows=workflows,
                patterns=patterns,
            )
            engineers.append(e)
            for w in range(1, weeks + 1):
                ur, dr = _week_rows(rng, e, w)
                usage.append(ur)
                delivery.append(dr)
    return teams, engineers, usage, delivery


def export_csv(out_dir: Path):
    """Write the synthetic dataset as CSV files for inspection."""
    teams, engineers, usage, delivery = generate()
    out_dir.mkdir(parents=True, exist_ok=True)

    def write(name, rows, fields):
        with open(out_dir / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in fields})

    eng_rows = [asdict(e) | {"patterns": "|".join(e.patterns)} for e in engineers]
    write("teams.csv", teams, list(teams[0].keys()))
    write("engineers.csv", eng_rows, [k for k in eng_rows[0].keys()])
    write("genai_usage_weekly.csv", usage, USAGE_FIELDS)
    write("delivery_signals_weekly.csv", delivery, DELIVERY_FIELDS)
    return out_dir
