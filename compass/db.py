"""SQLite storage.

signals.db  - synthetic org, usage and delivery metadata (no free text, no PII).
private.db  - engineer-owned data: feedback, dismissals, coaching history.

The aggregation layer opens signals.db read-only and never receives a handle to
private.db. That separation is the core privacy boundary and is covered by tests.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path

from . import config, synth

SIGNALS_SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
  team_id TEXT PRIMARY KEY, name TEXT, domain TEXT, stack TEXT, project_complexity TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS engineers (
  engineer_id TEXT PRIMARY KEY, codename TEXT, team_id TEXT, seniority TEXT, role TEXT,
  stack TEXT, stack_label TEXT, project_complexity TEXT, primary_workflows TEXT);
CREATE TABLE IF NOT EXISTS usage_weekly (
  record_id TEXT PRIMARY KEY, engineer_id TEXT, week INTEGER,
  copilot_sessions INTEGER, claude_sessions INTEGER, devin_sessions INTEGER,
  agent_mode_share REAL, suggestion_accept_rate REAL, chat_turns_avg REAL,
  abandoned_session_rate REAL, noncode_tasks_in_coding_agent INTEGER,
  large_task_chat_sessions INTEGER, repo_has_instructions INTEGER, source TEXT);
CREATE TABLE IF NOT EXISTS delivery_weekly (
  record_id TEXT PRIMARY KEY, engineer_id TEXT, week INTEGER,
  prs_opened INTEGER, pr_size_loc_median INTEGER, pr_cycle_time_hrs REAL,
  review_rounds_avg REAL, ci_first_pass_rate REAL, tests_added_per_pr REAL,
  test_creation_time_min INTEGER, flaky_test_rate REAL, ai_assisted_test_share REAL,
  pr_template_used_rate REAL, plan_first_rate REAL, tests_first_rate REAL, source TEXT);
-- Ground-truth seed labels used only by the evaluation harness, never by the engine.
CREATE TABLE IF NOT EXISTS seed_labels (engineer_id TEXT PRIMARY KEY, patterns TEXT);
"""

PRIVATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT, engineer_id TEXT NOT NULL, rec_key TEXT NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('useful','not_useful','dismissed','restored','tried')),
  reason TEXT CHECK (reason IS NULL OR reason IN
    ('not_relevant','already_doing','not_now','too_generic','wrong_context','other')),
  created_at TEXT DEFAULT (datetime('now')));
CREATE TABLE IF NOT EXISTS coaching_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT, engineer_id TEXT NOT NULL, rec_key TEXT NOT NULL,
  shown_at TEXT DEFAULT (datetime('now')));
"""


def _connect(path: Path, readonly: bool = False) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if readonly:
        conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, check_same_thread=False)
    else:
        conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def signals_conn(readonly: bool = True) -> sqlite3.Connection:
    return _connect(config.SIGNALS_DB, readonly=readonly)


def private_conn() -> sqlite3.Connection:
    return _connect(config.PRIVATE_DB)


def init(reset: bool = False) -> None:
    """Create both databases and load the synthetic dataset if empty."""
    if reset:
        for p in (config.SIGNALS_DB, config.PRIVATE_DB):
            if p.exists():
                p.unlink()
    conn = _connect(config.SIGNALS_DB)
    conn.executescript(SIGNALS_SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM engineers").fetchone()[0] == 0:
        teams, engineers, usage, delivery = synth.generate()
        conn.executemany("INSERT INTO teams VALUES (:team_id,:name,:domain,:stack,:project_complexity,:source)", teams)
        for e in engineers:
            row = asdict(e)
            patterns = row.pop("patterns")
            conn.execute("INSERT INTO engineers VALUES (:engineer_id,:codename,:team_id,:seniority,:role,"
                         ":stack,:stack_label,:project_complexity,:primary_workflows)", row)
            conn.execute("INSERT INTO seed_labels VALUES (?,?)", (e.engineer_id, "|".join(patterns)))
        cols = ",".join(synth.USAGE_FIELDS)
        conn.executemany(f"INSERT INTO usage_weekly ({cols}) VALUES ({','.join(':'+c for c in synth.USAGE_FIELDS)})", usage)
        cols = ",".join(synth.DELIVERY_FIELDS)
        conn.executemany(f"INSERT INTO delivery_weekly ({cols}) VALUES ({','.join(':'+c for c in synth.DELIVERY_FIELDS)})", delivery)
        conn.commit()
    conn.close()
    pconn = private_conn()
    pconn.executescript(PRIVATE_SCHEMA)
    pconn.commit()
    pconn.close()


def rows(conn: sqlite3.Connection, sql: str, params=()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]
