# Compass evaluation report

Generated: 2026-10-15T14:39:18+00:00 (deterministic; rerun with `python -m compass eval`)

## Recommendation quality (AC3)

**25 of 25 seeded scenarios passed (100%). Target: 80%. Result: PASS.**

A scenario passes only if every check passes: relevant, complete (4 elements), explainable (cited source and traceable records), actionable (concrete step and measurable outcome) and persona-specific.

| Scenario | Workflow | Expected | Fired | Relevant | Complete | Explainable | Actionable | Persona | Result |
|---|---|---|---|---|---|---|---|---|---|
| S01 Large PRs, senior Java, high complexity | pr_readiness | R-PR-SIZE | R-PR-SIZE | yes | yes | yes | yes | yes | PASS |
| S02 Large PRs, junior .NET | pr_readiness | R-PR-SIZE | R-PR-SIZE | yes | yes | yes | yes | yes | PASS |
| S03 Many review rounds on small PRs, mid TypeScript | pr_readiness | R-REVIEW-ROUNDS | R-REVIEW-ROUNDS | yes | yes | yes | yes | yes | PASS |
| S04 CI failures with heavy agent use, mid Python | pr_readiness | R-CI-FIRST-PASS | R-CI-FIRST-PASS | yes | yes | yes | yes | yes | PASS |
| S05 Few tests per PR, mid Java | test_creation | R-FEW-TESTS | R-FEW-TESTS | yes | yes | yes | yes | yes | PASS |
| S06 Slow manual test writing, senior .NET | test_creation | R-SLOW-TESTS | R-SLOW-TESTS | yes | yes | yes | yes | yes | PASS |
| S07 Flaky AI-generated Playwright tests, SDET | test_creation | R-FLAKY-AI-TESTS | R-FLAKY-AI-TESTS | yes | yes | yes | yes | yes | PASS |
| S08 Long agent sessions, junior Python, high complexity | pr_readiness | R-LONG-SESSIONS | R-LONG-SESSIONS | yes | yes | yes | yes | yes | PASS |
| S09 Long agent sessions, mid TypeScript, medium complexity | pr_readiness | R-LONG-SESSIONS | R-LONG-SESSIONS | yes | yes | yes | yes | yes | PASS |
| S10 No repo instructions with agent mode, lead Java | pr_readiness | R-NO-CONTEXT | R-NO-CONTEXT | yes | yes | yes | yes | yes | PASS |
| S11 Coding agent used for emails, mid .NET | pr_readiness | R-WRONG-TOOL-TEXT | R-WRONG-TOOL-TEXT | yes | yes | yes | yes | yes | PASS |
| S12 Repo-wide migration done in chat, lead Python | pr_readiness | R-WRONG-TOOL-LARGE | R-WRONG-TOOL-LARGE | yes | yes | yes | yes | yes | PASS |
| S13 Low tool adoption, junior Java | pr_readiness | R-LOW-ADOPTION | R-LOW-ADOPTION | yes | yes | yes | yes | yes | PASS |
| S14 Large PRs and few tests, mid Java | pr_readiness | R-PR-SIZE, R-FEW-TESTS | R-PR-SIZE, R-FEW-TESTS | yes | yes | yes | yes | yes | PASS |
| S15 Flaky tests and CI failures, mid TypeScript | test_creation | R-FLAKY-AI-TESTS, R-CI-FIRST-PASS | R-FLAKY-AI-TESTS, R-CI-FIRST-PASS | yes | yes | yes | yes | yes | PASS |
| S16 No context and long sessions, senior Python | pr_readiness | R-NO-CONTEXT, R-LONG-SESSIONS | R-NO-CONTEXT, R-LONG-SESSIONS | yes | yes | yes | yes | yes | PASS |
| S17 Few tests, SDET Playwright | test_creation | R-FEW-TESTS | R-FEW-TESTS | yes | yes | yes | yes | yes | PASS |
| S18 Healthy senior Java: no false alarms | pr_readiness | none | R-GROWTH | yes | yes | yes | yes | yes | PASS |
| S19 Healthy junior TypeScript: no false alarms | test_creation | none | R-GROWTH | yes | yes | yes | yes | yes | PASS |
| S20 Borderline PR size (380 lines) should not trigger | pr_readiness | none | R-GROWTH | yes | yes | yes | yes | yes | PASS |
| S21 Flaky tests but not AI-generated: no AI-test flag | test_creation | none | R-GROWTH | yes | yes | yes | yes | yes | PASS |
| S22 Low CI pass without agent use: not attributed to AI | pr_readiness | none | R-GROWTH | yes | yes | yes | yes | yes | PASS |
| S23 Large PRs, lead TypeScript, high complexity | pr_readiness | R-PR-SIZE | R-PR-SIZE | yes | yes | yes | yes | yes | PASS |
| S24 Slow tests, junior Python | test_creation | R-SLOW-TESTS | R-SLOW-TESTS | yes | yes | yes | yes | yes | PASS |
| S25 Emails in coding agent and low adoption, junior | pr_readiness | R-WRONG-TOOL-TEXT, R-LOW-ADOPTION | R-LOW-ADOPTION, R-WRONG-TOOL-TEXT | yes | yes | yes | yes | yes | PASS |

## Context awareness (AC8)

5 of 5 pairs produced different actions for the same signal and different personas.

| Pair | Rule | Persona A | Persona B | Different action |
|---|---|---|---|---|
| C01 | R-PR-SIZE | senior java high | junior typescript medium | yes |
| C02 | R-FEW-TESTS | mid dotnet medium | sdet playwright medium | yes |
| C03 | R-LONG-SESSIONS | junior python high | mid typescript low | yes |
| C04 | R-FLAKY-AI-TESTS | sdet playwright medium | mid java medium | yes |
| C05 | R-NO-CONTEXT | lead java high | mid python medium | yes |

## Seeded synthetic personas (AC6, AC12)

37 of 37 seeded personas surfaced every seeded pattern (adopters also show a before/after improvement; healthy personas get no gap alerts).

## Prompt coach: task type and tool routing

16 of 16 stories classified and routed as expected, with 3 or fewer questions.

| Story | Expected type | Got | Expected tool | Got | Pass |
|---|---|---|---|---|---|
| J01 | feature_api | feature_api | copilot | copilot | yes |
| J02 | bug_fix | bug_fix | claude | claude | yes |
| J03 | test_creation | test_creation | copilot | copilot | yes |
| J04 | refactor_modernization | refactor_modernization | devin | devin | yes |
| J05 | docs_communication | docs_communication | writing | writing | yes |
| J06 | trivial_deterministic | trivial_deterministic | no_ai | no_ai | yes |
| J07 | test_creation | test_creation | copilot | copilot | yes |
| J08 | exploration | exploration | claude | claude | yes |
| J09 | pr_readiness | pr_readiness | copilot | copilot | yes |
| J10 | data_sql | data_sql | copilot | copilot | yes |
| J11 | bug_fix | bug_fix | claude | claude | yes |
| J12 | refactor_modernization | refactor_modernization | claude | claude | yes |
| J13 | refactor_modernization | refactor_modernization | devin | devin | yes |
| J14 | feature_api | feature_api | copilot | copilot | yes |
| J15 | feature_api | feature_api | claude | claude | yes |
| J16 | docs_communication | docs_communication | writing | writing | yes |

Reusable practices identified: 8 (each cites the workflow signals it improves).
