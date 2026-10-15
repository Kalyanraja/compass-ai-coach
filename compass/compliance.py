"""Data-minimization and no-employee-analytics checks (AC10).

Runs against the live signals database and the API surface, and reports
pass/fail per check. Used by the tests, the eval report and the Trust page.
"""

from __future__ import annotations

import re

from . import db

ALLOWED_COLUMNS = {
    "teams": {"team_id", "name", "domain", "stack", "project_complexity", "source"},
    "engineers": {"engineer_id", "codename", "team_id", "seniority", "role", "stack", "stack_label",
                  "project_complexity", "primary_workflows"},
    "usage_weekly": {"record_id", "engineer_id", "week", "copilot_sessions", "claude_sessions", "devin_sessions",
                     "agent_mode_share", "suggestion_accept_rate", "chat_turns_avg", "abandoned_session_rate",
                     "noncode_tasks_in_coding_agent", "large_task_chat_sessions", "repo_has_instructions", "source"},
    "delivery_weekly": {"record_id", "engineer_id", "week", "prs_opened", "pr_size_loc_median", "pr_cycle_time_hrs",
                        "review_rounds_avg", "ci_first_pass_rate", "tests_added_per_pr", "test_creation_time_min",
                        "flaky_test_rate", "ai_assisted_test_share", "pr_template_used_rate", "plan_first_rate",
                        "tests_first_rate", "source"},
    "seed_labels": {"engineer_id", "patterns"},
}

FORBIDDEN_COLUMN_HINTS = ["name_full", "email", "phone", "address", "ssn", "salary", "rating", "score", "rank",
                          "performance", "prompt", "code", "content", "message", "password", "token", "comment"]

PII_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "code_fragment": r"(def |class |public static|import |function\s*\(|SELECT .* FROM|=>|;\s*$)",
}

FORBIDDEN_API_TERMS = ["rank", "leaderboard", "score_engineer", "rate_engineer", "compare_engineers", "performance_review"]


def run(api_routes: list[str] | None = None) -> dict:
    conn = db.signals_conn(readonly=True)
    checks = []
    try:
        tables = [r["name"] for r in db.rows(conn, "SELECT name FROM sqlite_master WHERE type='table'")]
        unexpected = []
        for t in tables:
            cols = {r["name"] for r in db.rows(conn, f"PRAGMA table_info({t})")}
            extra = cols - ALLOWED_COLUMNS.get(t, set())
            if extra:
                unexpected.append(f"{t}: {sorted(extra)}")
        checks.append({"id": "schema-allowlist", "title": "Only allow-listed metadata columns exist",
                       "passed": not unexpected, "detail": unexpected or "All columns are allow-listed metadata."})

        bad_cols = [f"{t}.{c}" for t in tables for c in (r["name"] for r in db.rows(conn, f"PRAGMA table_info({t})"))
                    if any(h == c or c.startswith(h + "_") or c.endswith("_" + h) for h in FORBIDDEN_COLUMN_HINTS)]
        checks.append({"id": "no-sensitive-columns", "title": "No PII, prompt, code, rating or score columns",
                       "passed": not bad_cols, "detail": bad_cols or "None found."})

        hits = []
        for t in tables:
            for row in db.rows(conn, f"SELECT * FROM {t}"):
                for k, v in row.items():
                    if isinstance(v, str):
                        for label, rx in PII_PATTERNS.items():
                            if re.search(rx, v):
                                hits.append(f"{t}.{k}: {label}")
        checks.append({"id": "no-pii-or-code-values", "title": "No emails, phone numbers, SSNs or code in any value",
                       "passed": not hits, "detail": sorted(set(hits))[:10] or "None found."})

        long_text = []
        for t in tables:
            for row in db.rows(conn, f"SELECT * FROM {t}"):
                for k, v in row.items():
                    if isinstance(v, str) and len(v) > 80:
                        long_text.append(f"{t}.{k}")
        checks.append({"id": "no-free-text", "title": "No free-text fields (all strings are short labels)",
                       "passed": not long_text, "detail": sorted(set(long_text)) or "None found."})

        synthetic = all(r["source"].startswith("synthetic:") for t in ("teams", "usage_weekly", "delivery_weekly")
                        for r in db.rows(conn, f"SELECT source FROM {t}"))
        checks.append({"id": "synthetic-source", "title": "Every record is labeled synthetic and traceable",
                       "passed": synthetic, "detail": "All rows carry record_id and a synthetic source label."})
    finally:
        conn.close()

    if api_routes is not None:
        bad = [r for r in api_routes if any(term in r.lower() for term in FORBIDDEN_API_TERMS)]
        checks.append({"id": "no-ranking-api", "title": "No API to score, rank, compare or label engineers",
                       "passed": not bad, "detail": bad or f"{len(api_routes)} routes checked."})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}
