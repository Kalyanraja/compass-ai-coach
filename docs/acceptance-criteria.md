# Acceptance criteria traceability

Every criterion maps to code and to an automated test in `tests/test_acceptance.py` (run with `python -m unittest discover -s tests -t . -v`).

| AC | Criterion | Where it is implemented | Test class |
|---|---|---|---|
| AC1 | Private engineer coaching view; no manager/leader access path | `server.py` `/api/me/*` (role `engineer`, id from the signed session only) | `AC01_PrivateEngineerView` (own data, no id parameter, manager/leader/enablement get 403, anonymous 401, forged token 401) |
| AC2 | Recommendation completeness: observation, action, rationale, outcome; persona-specific | `engine.build_recommendation` | `AC02_Completeness` (all 37 personas; observation cites numbers) |
| AC3 | At least 80% of seeded scenarios relevant, explainable, actionable; pass/fail recorded | `evaluation.py`, `eval/scenarios.json`, `reports/eval-report.md` | `AC03_QualityThreshold` |
| AC4 | Aggregated manager/leader view; nothing individual exposed or derivable | `aggregate.py`, `/api/team/insights`, `/api/org/insights` | `AC04_AggregatedManagerView` (no ids or codenames, no recommendation fields; manager scoped to own team) |
| AC5 | Privacy separation: thresholds/suppression; feedback never exposed | `aggregate.summarize_group` (k = 5), team suppression, below-threshold folding, portfolio differencing protection; separate `private.db` | `AC05_PrivacySeparation` (small team suppressed; every shown gap independently verified at k or more; feedback leaves manager output byte-identical; aggregator source never references the private store; org totals exclude suppressed team) |
| AC6 | One or two workflows end to end, with a seeded observation to recommendation to outcome cycle | PR readiness and AI-assisted test creation; adopter personas show progress | `AC06_WorkflowCoverage` |
| AC7 | At least three reusable practices, each citing the signals it improves | `practices.py` (8 practices); `aggregate.practice_discovery` finds 5 in data | `AC07_ReusablePractices` (also checks every agent-kit file exists) |
| AC8 | Context awareness: different role, complexity or stack gives a different suggested action | `engine._action`, `engine._tool_for`, `STACK_CONTEXT` | `AC08_ContextAwareness` (5 pairs) |
| AC9 | Engineer control: dismiss/feedback recorded privately | `/api/me/feedback`, `/api/me/history`, `/api/me/forget` | `AC09_EngineerControl` (dismiss, restore, isolation from other engineers, invalid input rejected) |
| AC10 | Data minimization; no scoring/ranking functionality | `compliance.py`; schema has no free text, PII, prompt or score columns; audit logs role/path/status only; prompt text never persisted | `AC10_DataMinimization` |
| AC11 | Engineer reaches a useful recommendation within three interactions; manager finds an opportunity with no path to individuals | UI: choose role, pick persona, recommendations shown. Prompt coach: paste, answer, copy | `AC11_Usability` |
| AC12 | Before/after signal comparison for a seeded scenario | `engine.simulate` (labeled simulation) and seeded adopters (actual weeks 1-4 vs 5-8) | `AC12_BeforeAfter` |
| AC13 (stretch) | Private usefulness feedback informs future ranking, invisible to managers | `engine.recommend` feedback weights | `AC13_FeedbackLoop` (plus the AC5 byte-identical manager check) |
| AC14 (stretch) | Correlation/regression, labeled non-causal | `stats.pearson`, `aggregate.practice_discovery` | `AC14_Statistics` |

Additional tests cover prompt-coach routing, sensitive-data warnings, Jira CSV import, path-traversal protection and audit access control.

## Usability walkthrough (AC11)

**Engineer: two interactions**
1. Click **Engineer** and pick a persona. In production, SSO lands directly on step 2.
2. The coaching view opens with the top recommendation and all four elements visible.

**Prompt coach: three interactions**
1. Paste a story, or pick one from the Jira CSV import, and choose **Check my task**.
2. Answer up to three questions (optional) and choose **Write my prompt**.
3. Choose **Copy prompt**.

**Manager: one interaction after sign-in**
1. Open **Team insights**. Gaps and enablement opportunities are on the first screen. There are no links to people.

## Workflow coach requirements traceability

| Requirement | Implemented in | Test |
|---|---|---|
| Goal, facts, questions, tool, package, evidence, lesson journey | `compass/workflow/journey.py`, `web/workflow.js` | `Demos.*`, Playwright walkthrough |
| Three complete workflows plus a shared security stage; planned extensions not presented as working | `workflows/packs/*.json`, `coach.WORKING` | `Api.test_planned_workflows_not_startable` |
| At most 3 questions; detected / inferred / confirmed / unknown facts with file:line | `coach.next_questions`, `workspace.detect_facts` | `Questions.*`, `Provenance.*` |
| Approved-capability catalog; policy before fit; override within policy; "no AI needed" | `catalog/capabilities.json`, `coach.recommend_tool` | `Routing.*` |
| Work package with excerpts, unresolved questions, staged actions, acceptance criteria and an exact preview | `workflow/package.py` | `Budgets.*`, `Redaction.*` |
| Context budgeter (Lean / Balanced / Deep), overflow instead of silent drops, bytes plus labeled estimates | `workflow/context.py` | `Budgets.test_required_context_never_dropped_and_overflow_reported` |
| Evidence model; gitleaks / Semgrep / Spectral / JUnit / unittest adapters; missing = not checked; malformed = blocked | `workflow/evidence.py`, `workflow/runner.py` | `MissingToolsAndReports.*` |
| Safe execution: templates, no shell, validation, minimal env, timeout, approval | `workflow/runner.py` | `Boundaries.*`, `Timeouts.*` |
| Workspace boundaries: allowed roots, traversal, symlinks, credential files | `workflow/workspace.py` | `Boundaries.test_traversal_symlink_and_credential_files` |
| Untrusted input stays data | `package.injection_warnings` | `UntrustedInput.*` |
| Cache only with permission, invalidated on change | `workflow/cache.py` | `Cache.*` |
| Blocked-network smoke test | in-process egress guard | `BlockedNetwork.*` |
| Jira automation (read-only, host-pinned, token never stored) | `compass/jira_client.py` | `Jira.*` |
| Local API protected from other websites | `server._check_origin` | `Api.test_cross_origin_and_non_json_refused` |
