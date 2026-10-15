"""Acceptance tests mapped one-to-one to the hackathon acceptance criteria (AC1-AC14).

Run: python -m unittest discover -s tests -v
"""

import json
import unittest

from tests.helpers import call, login  # noqa: F401  (starts the server)

from compass import aggregate, compliance, config, db, engine, evaluation, prompt_coach
from compass.practices import PRACTICES
from compass.server import ROUTES

ENGINEER = "E-ATL-01"
OTHER = "E-BOR-01"


def flatten(obj) -> str:
    return json.dumps(obj, default=str)


class AC01_PrivateEngineerView(unittest.TestCase):
    def test_engineer_sees_own_recommendations(self):
        s, b = call("GET", "/api/me/coaching", token=login("engineer", ENGINEER))
        self.assertEqual(s, 200)
        self.assertGreaterEqual(len(b["recommendations"]), 1)
        self.assertEqual(b["profile"]["engineer_id"], ENGINEER)

    def test_no_parameter_can_select_another_engineer(self):
        tok = login("engineer", ENGINEER)
        s, b = call("GET", f"/api/me/coaching?engineer_id={OTHER}", token=tok)
        self.assertEqual(b["profile"]["engineer_id"], ENGINEER)

    def test_manager_and_leader_cannot_reach_private_endpoints(self):
        for role, sub in (("manager", "T-ATLAS"), ("leader", None), ("enablement", None)):
            tok = login(role, sub)
            for path in ("/api/me/coaching", "/api/me/history", "/api/me/trend"):
                s, _ = call("GET", path, token=tok)
                self.assertEqual(s, 403, f"{role} reached {path}")

    def test_anonymous_blocked(self):
        s, _ = call("GET", "/api/me/coaching")
        self.assertEqual(s, 401)

    def test_forged_token_rejected(self):
        s, _ = call("GET", "/api/me/coaching", token="eyJyb2xlIjoiZW5naW5lZXIifQ.deadbeef")
        self.assertEqual(s, 401)


class AC02_Completeness(unittest.TestCase):
    def test_every_recommendation_has_four_populated_elements(self):
        conn = db.signals_conn()
        for e in db.rows(conn, "SELECT engineer_id FROM engineers"):
            s, b = call("GET", "/api/me/coaching", token=login("engineer", e["engineer_id"]))
            for r in b["recommendations"]:
                self.assertTrue(r["observation"].strip())
                self.assertTrue(r["suggested_action"].strip())
                self.assertTrue(r["rationale"].strip())
                self.assertTrue(r["outcome_to_monitor"]["text"].strip())
                self.assertRegex(r["observation"], r"\d")  # cites actual numbers, not boilerplate
        conn.close()


class AC03_QualityThreshold(unittest.TestCase):
    def test_at_least_80_percent_of_seeded_scenarios_pass_and_are_recorded(self):
        report = evaluation.run(write=True)
        self.assertGreaterEqual(report["summary"]["pass_rate"], 0.8)
        self.assertTrue((config.ROOT / "reports" / "eval-report.md").exists())
        for sc in report["scenarios"]:
            self.assertIn("passed", sc)


class AC04_AggregatedManagerView(unittest.TestCase):
    def test_manager_sees_only_team_level_data(self):
        s, b = call("GET", "/api/team/insights", token=login("manager", "T-ATLAS"))
        self.assertEqual(s, 200)
        text = flatten(b)
        conn = db.signals_conn()
        for e in db.rows(conn, "SELECT engineer_id, codename FROM engineers"):
            self.assertNotIn(e["engineer_id"], text)
            self.assertNotIn(f'"{e["codename"]}"', text)
        conn.close()
        data_only = flatten({k: v for k, v in b.items() if k != "privacy_note"})
        for banned in ("suggested_action", "observation", "rec_key", "feedback", "dismiss"):
            self.assertNotIn(banned, data_only)

    def test_manager_scoped_to_own_team(self):
        s, b = call("GET", "/api/team/insights?team=T-BOREALIS", token=login("manager", "T-ATLAS"))
        self.assertEqual(b["team"]["team_id"], "T-ATLAS")


class AC05_PrivacySeparation(unittest.TestCase):
    def test_small_team_is_suppressed(self):
        s, b = call("GET", "/api/team/insights", token=login("manager", "T-DELTA"))
        self.assertTrue(b["suppressed"])
        self.assertNotIn("workflow_gaps", b)

    def test_patterns_below_k_are_not_shown(self):
        for t in ("T-ATLAS", "T-BOREALIS", "T-CIRRUS", "T-ECHO"):
            b = aggregate.team_insights(t)
            conn = db.signals_conn()
            # recompute counts independently and confirm nothing under k leaks
            for g in b["workflow_gaps"]:
                rule = engine.RULES_BY_ID[g["rule_id"]]
                n = 0
                for e in db.rows(conn, "SELECT engineer_id FROM engineers WHERE team_id=?", (t,)):
                    u = db.rows(conn, "SELECT * FROM usage_weekly WHERE engineer_id=?", (e["engineer_id"],))
                    d = db.rows(conn, "SELECT * FROM delivery_weekly WHERE engineer_id=?", (e["engineer_id"],))
                    m = engine.window_metrics(engine.merged_rows(u, d), engine.WINDOW)
                    n += 1 if rule["trigger"](m) else 0
                self.assertGreaterEqual(n, config.K_ANON)
            conn.close()

    def test_feedback_never_changes_manager_view(self):
        before = aggregate.team_insights("T-ATLAS")
        tok = login("engineer", ENGINEER)
        for act in ("dismissed", "not_useful", "useful"):
            call("POST", "/api/me/feedback", {"rec_key": "R-PR-SIZE", "action": act}, token=tok)
        after = aggregate.team_insights("T-ATLAS")
        self.assertEqual(flatten(before), flatten(after))
        call("POST", "/api/me/forget", {}, token=tok)

    def test_aggregation_layer_never_opens_private_db(self):
        import inspect
        src = inspect.getsource(aggregate)
        self.assertNotIn("private_conn", src)
        self.assertNotIn("PRIVATE_DB", src)

    def test_org_totals_exclude_suppressed_teams(self):
        org = aggregate.org_insights()
        self.assertEqual(org["teams_excluded_for_privacy"], 1)
        self.assertEqual(org["group_size"], "34 engineers")


class AC06_WorkflowCoverage(unittest.TestCase):
    def test_two_workflows_with_full_cycle(self):
        report = evaluation.run()
        wfs = {s["workflow"] for s in report["scenarios"] if s["passed"] and s["expected"]}
        self.assertIn("pr_readiness", wfs)
        self.assertIn("test_creation", wfs)
        # observation -> recommendation -> outcome: seeded adopters show progress
        adopters = [p for p in report["seeded_personas"]["personas"] if "adopter_pr" in p["patterns"] or "adopter_tests" in p["patterns"]]
        self.assertTrue(adopters and all(p["progress_detected"] for p in adopters))


class AC07_ReusablePractices(unittest.TestCase):
    def test_at_least_three_practices_discovered_with_signals(self):
        found = aggregate.practice_discovery()
        self.assertGreaterEqual(len(found), 3)
        for p in found:
            self.assertEqual(len(p["cites_signals"]), 2)

    def test_catalog_practices_cite_signals_and_kit_files_exist(self):
        for pid, p in PRACTICES.items():
            self.assertTrue(p["signals"], pid)
            for path in p["kit"].values():
                self.assertTrue((config.ROOT / path).exists(), path)


class AC08_ContextAwareness(unittest.TestCase):
    def test_same_signal_different_personas_get_different_actions(self):
        report = evaluation.run()
        self.assertTrue(all(p["passed"] for p in report["context_awareness"]["pairs"]))


class AC09_EngineerControl(unittest.TestCase):
    def test_dismiss_and_restore_are_private(self):
        tok = login("engineer", ENGINEER)
        s, b = call("GET", "/api/me/coaching", token=tok)
        key = b["recommendations"][0]["rec_key"]
        call("POST", "/api/me/feedback", {"rec_key": key, "action": "dismissed", "reason": "not_now"}, token=tok)
        s, b2 = call("GET", "/api/me/coaching", token=tok)
        self.assertNotIn(key, [r["rec_key"] for r in b2["recommendations"]])
        self.assertIn(key, [r["rec_key"] for r in b2["dismissed"]])
        call("POST", "/api/me/feedback", {"rec_key": key, "action": "restored"}, token=tok)
        s, b3 = call("GET", "/api/me/coaching", token=tok)
        self.assertIn(key, [r["rec_key"] for r in b3["recommendations"]])
        # another engineer cannot see it
        s, h = call("GET", "/api/me/history", token=login("engineer", OTHER))
        self.assertEqual(h["feedback"], [])
        call("POST", "/api/me/forget", {}, token=tok)

    def test_invalid_feedback_rejected(self):
        tok = login("engineer", ENGINEER)
        s, _ = call("POST", "/api/me/feedback", {"rec_key": "R-PR-SIZE", "action": "rate_5_stars"}, token=tok)
        self.assertEqual(s, 400)


class AC10_DataMinimization(unittest.TestCase):
    def test_compliance_checks_pass(self):
        r = compliance.run([p for (_, p) in ROUTES])
        self.assertTrue(r["passed"], r)

    def test_audit_log_has_no_ids_or_content(self):
        call("POST", "/api/coach/analyze", {"text": "Build an API for orders with password=abc"}, token=login("engineer", ENGINEER))
        text = config.AUDIT_LOG.read_text()
        self.assertNotIn(ENGINEER, text)
        self.assertNotIn("password", text)

    def test_prompt_text_is_not_persisted(self):
        marker = "UNIQUE-MARKER-7731"
        call("POST", "/api/coach/build", {"text": f"Fix bug {marker} in the API"}, token=login("engineer", ENGINEER))
        for p in (config.SIGNALS_DB, config.PRIVATE_DB, config.AUDIT_LOG):
            self.assertNotIn(marker.encode(), p.read_bytes())


class AC11_Usability(unittest.TestCase):
    def test_engineer_reaches_recommendation_in_three_interactions(self):
        # 1) choose persona (session) 2) coaching view loads with recommendations
        tok = login("engineer", "E-CIR-01")
        s, b = call("GET", "/api/me/coaching", token=tok)
        self.assertTrue(b["recommendations"])

    def test_prompt_coach_three_steps(self):
        tok = login("engineer", ENGINEER)
        s, a = call("POST", "/api/coach/analyze", {"text": "Create Playwright tests for the login page"}, token=tok)
        self.assertLessEqual(len(a["questions"]), 3)
        s, b = call("POST", "/api/coach/build", {"text": "Create Playwright tests for the login page",
                                                  "answers": {"negative": "wrong password, locked account"}}, token=tok)
        self.assertIn("wrong password", b["prompt"])

    def test_manager_finds_opportunity_without_individual_path(self):
        s, b = call("GET", "/api/team/insights", token=login("manager", "T-ECHO"))
        self.assertTrue(b["workflow_gaps"])
        self.assertTrue(b["workflow_gaps"][0]["enablement_opportunity"])


class AC12_BeforeAfter(unittest.TestCase):
    def test_simulation_shows_before_and_after(self):
        s, b = call("GET", "/api/me/simulate?practice=pr-slicing", token=login("engineer", ENGINEER))
        ser = b["series"]["pr_size_loc_median"]
        self.assertGreater(ser["before"], ser["after"])
        self.assertIn("Simulated", b["label"])


class AC13_FeedbackLoop(unittest.TestCase):
    def test_feedback_reorders_privately(self):
        tok = login("engineer", "E-ECH-04")
        s, b = call("GET", "/api/me/coaching", token=tok)
        keys = [r["rec_key"] for r in b["recommendations"]]
        self.assertGreaterEqual(len(keys), 2)
        call("POST", "/api/me/feedback", {"rec_key": keys[0], "action": "not_useful"}, token=tok)
        call("POST", "/api/me/feedback", {"rec_key": keys[-1], "action": "useful"}, token=tok)
        s, b2 = call("GET", "/api/me/coaching", token=tok)
        self.assertNotEqual(keys, [r["rec_key"] for r in b2["recommendations"]])
        call("POST", "/api/me/forget", {}, token=tok)


class AC14_Statistics(unittest.TestCase):
    def test_correlations_labeled_non_causal(self):
        for p in aggregate.practice_discovery():
            self.assertIn("not causation", p["label"])
            self.assertIsNotNone(p["pearson_r"])


class PromptCoach(unittest.TestCase):
    def test_sensitive_data_warning(self):
        a = prompt_coach.analyze("Fix login, password=hunter2, contact jane@example.com")
        self.assertIn("password or secret", a["sensitive_data_warnings"])

    def test_routing(self):
        self.assertEqual(prompt_coach.analyze("Fix formatting in utils")["recommendation"]["tool"], "no_ai")
        self.assertEqual(prompt_coach.analyze("Upgrade all services to Java 21 across all services")["recommendation"]["tool"], "devin")

    def test_jira_csv(self):
        issues = prompt_coach.parse_jira_csv(config.SAMPLE_JIRA_CSV.read_text())
        self.assertGreaterEqual(len(issues), 5)


class Security(unittest.TestCase):
    def test_kit_endpoint_blocks_path_traversal(self):
        s, _ = call("GET", "/api/kit?path=../compass/config.py")
        self.assertEqual(s, 404)
        s, _ = call("GET", "/api/kit?path=agent-kit/../var/private.db")
        self.assertEqual(s, 404)

    def test_audit_only_for_enablement(self):
        s, _ = call("GET", "/api/audit", token=login("manager", "T-ATLAS"))
        self.assertEqual(s, 403)


if __name__ == "__main__":
    unittest.main()
