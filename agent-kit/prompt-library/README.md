# Compass prompt library

54 reusable prompt templates and 27 prompt anti-patterns, tool-agnostic, no MCP or API needed. Copy a template, replace each `{{PLACEHOLDER}}`, paste into the tool in the **Best tool** column.

Files:
- `prompts.json` - templates. Fields: `id`, `title`, `workflow`, `task_type`, `practice_id`, `best_tool`, `alt_tools`, `when_to_use`, `template`, `placeholders`, `tags`, `source`.
- `anti-patterns.json` / `anti-patterns.md` - what to avoid and how to fix it.

Every template ends with the same guardrail: no secrets, PII or production data; show commands and results; a human reviews before merge.

Tool keys: `copilot_inline` = Copilot inline, `copilot_chat` = Copilot Chat (ask), `copilot_agent` = Copilot agent mode, `claude_code` = Claude Code, `devin` = Devin, `m365_copilot` = General assistant (e.g. M365 Copilot), `no_ai` = No AI (deterministic tool).

Practices: P1 `pr-slicing`, P2 `pr-readiness-selfcheck`, P3 `test-first-acceptance`, P4 `plan-then-implement`, P5 `context-pack`, P6 `verify-before-done`, P7 `right-tool-for-task`, P8 `flaky-test-hardening`.

## pr_readiness

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `pr-readiness-check` | PR readiness self-check | `pr-readiness-selfcheck` | Copilot agent mode | Claude Code, Devin | Before opening or updating a PR. |
| `pr-description-draft` | Draft PR description from diff | `pr-readiness-selfcheck` | Copilot Chat (ask) | Claude Code, Devin | When opening a PR and the description is empty or vague. |
| `pr-slice-plan` | Slice a large change into small PRs | `pr-slicing` | Claude Code | Copilot agent mode | When a branch exceeds the PR size target or mixes refactor and behavior. |
| `commit-message-conventional` | Conventional commit message | `pr-readiness-selfcheck` | Copilot Chat (ask) | Claude Code | When committing staged changes. |

## planning

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `pr-plan-slices-upfront` | Plan PR slices before coding | `pr-slicing` | Copilot Chat (ask) | Claude Code | When starting a feature you expect to exceed one small PR. |
| `brainstorm-to-spec` | Brainstorm an idea into a spec | `plan-then-implement` | Copilot Chat (ask) | Claude Code | A new feature or behavior where intent is not fully specified. |
| `ticket-to-plan` | Ticket to clarified plan | `plan-then-implement` | Copilot Chat (ask) | Claude Code, Devin | When picking up a Jira/Azure Boards/GitHub ticket. |
| `clarify-spec` | Find ambiguities in a spec | `plan-then-implement` | Copilot Chat (ask) | Claude Code | A spec exists but has not been stress-tested. |
| `implementation-plan` | Write a test-first implementation plan | `plan-then-implement` | Claude Code | Copilot agent mode | An approved spec needs to become executable tasks. |
| `spec-to-tasks` | Spec to user-story task list | `plan-then-implement` | Copilot agent mode | Claude Code | Turning a spec into a tracked, parallelizable task list. |
| `execute-plan-task` | Execute one plan task with ledger | `plan-then-implement` | Claude Code | Copilot agent mode, Devin | Implementing an approved plan task by task. |
| `task-brief` | Write a task brief before a big agent task | `context-pack` | Copilot Chat (ask) | Claude Code, Devin | Before handing a multi-step task to any agent. |
| `what-context-needed` | Ask the agent what context it needs | `context-pack` | Copilot Chat (ask) | Claude Code | Before asking a question about code you have not shared. |

## review

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `self-review-strict` | Strict self-review before requesting review | `pr-readiness-selfcheck` | Copilot Chat (ask) | Claude Code | Right before asking a teammate to review. |
| `review-against-plan` | Review a git range against its plan | `pr-readiness-selfcheck` | Claude Code | Copilot agent mode | After finishing a plan task or feature, before merging. |
| `address-review-comments` | Process review comments with rigor | `verify-before-done` | Claude Code | Copilot agent mode | When you receive PR review comments. |
| `route-task-to-tool` | Pick the right tool for a task | `right-tool-for-task` | Copilot Chat (ask) | Claude Code | Unsure whether to use inline, chat, agent mode, Claude Code, Devin, a general assistant, or no AI. |

## test_creation

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `test-plan-from-story` | Test plan from acceptance criteria | `test-first-acceptance` | Copilot Chat (ask) | Claude Code | When a story or ticket is ready and before implementation. |
| `failing-test-first` | Write the failing test first | `test-first-acceptance` | Copilot agent mode | Claude Code | At the start of implementing any behavior or bug fix. |
| `tdd-green-minimal` | Make the failing test pass minimally | `test-first-acceptance` | Copilot agent mode | Claude Code | After a failing test is confirmed. |
| `unit-tests-junit5` | JUnit 5 unit tests | `test-first-acceptance` | Copilot agent mode | Claude Code, Copilot Chat (ask) | Writing or extending Java unit tests. |
| `unit-tests-xunit` | xUnit unit tests | `test-first-acceptance` | Copilot agent mode | Claude Code | Writing or extending C#/.NET unit tests. |
| `unit-tests-pytest` | pytest tests | `test-first-acceptance` | Copilot agent mode | Claude Code | Writing or extending Python tests. |
| `unit-tests-jest` | Jest/Vitest tests | `test-first-acceptance` | Copilot agent mode | Claude Code | Writing or extending JavaScript/TypeScript tests. |
| `playwright-e2e-test` | Playwright UI test for a journey | `test-first-acceptance` | Copilot agent mode | Claude Code, Devin | Adding an end-to-end test for a critical user journey. |
| `characterization-tests` | Characterization tests before changing legacy code | `test-first-acceptance` | Claude Code | Copilot agent mode | Before modifying untested legacy code. |
| `test-gap-audit` | Find missing or weak tests for a change | `test-first-acceptance` | Claude Code | Copilot Chat (ask) | Before a risky merge or when asked 'are the tests enough?'. |
| `mutation-check` | Mutation check of a test suite | `test-first-acceptance` | Copilot Chat (ask) | Claude Code | After writing tests, to check they actually catch bugs. |
| `flaky-test-diagnose` | Diagnose and fix a flaky test | `flaky-test-hardening` | Claude Code | Copilot agent mode, Devin | A test fails intermittently or only in CI. |
| `replace-sleeps` | Replace fixed sleeps with condition waits | `flaky-test-hardening` | Copilot agent mode | Claude Code | Tests contain sleep/waitForTimeout/cy.wait(ms). |
| `playwright-flaky-locators` | Harden flaky Playwright locators and waits | `flaky-test-hardening` | Copilot agent mode | Claude Code, Devin | A Playwright spec fails intermittently with timeouts, strict-mode or detached-element errors. |
| `ci-only-failure` | Test fails only in CI | `flaky-test-hardening` | Claude Code | Copilot agent mode, Devin | A test passes locally but fails in the pipeline. |

## docs

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `context-pack-agents-md` | Generate AGENTS.md from repo facts | `context-pack` | Claude Code | Copilot agent mode, Devin | New repo for agents, or agents keep using wrong commands. |
| `onboard-explain-module` | Explain a module for onboarding | `context-pack` | Copilot Chat (ask) | Claude Code | Joining a codebase or touching an unfamiliar area. |
| `adr-draft` | Architecture decision record | `plan-then-implement` | Copilot Chat (ask) | Claude Code | Recording a technical decision. |
| `readme-runbook` | README or runbook update | `context-pack` | Copilot agent mode | Claude Code | Behavior or setup changed and docs are stale. |
| `status-update-email` | Status update or email (non-coding assistant) | `right-tool-for-task` | General assistant (e.g. M365 Copilot) | Copilot Chat (ask) | Writing a stakeholder update, email or meeting summary. |

## debugging

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `debug-systematic` | Systematic debugging session | `verify-before-done` | Claude Code | Copilot agent mode | Any bug, failing test, or unexpected behavior. |
| `bug-repro-brief` | Minimal reproduction brief | `verify-before-done` | Copilot agent mode | Claude Code, Devin | A vague or intermittent bug report. |
| `root-cause-trace` | Trace a bad value to its origin | `verify-before-done` | Copilot Chat (ask) | Claude Code | An error appears deep in the call stack. |
| `explain-stack-trace` | Explain an error or stack trace | `right-tool-for-task` | Copilot Chat (ask) | Claude Code | You need to understand an error quickly (lookup-style). |
| `restart-stuck-session` | Reset a stuck agent session | `right-tool-for-task` | Claude Code | Copilot agent mode | An agent is looping, repeating fixes, or the session covers too many topics. |

## refactoring

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `refactor-no-behavior-change` | Safe refactor with characterization tests | `pr-slicing` | Copilot agent mode | Claude Code | Improving structure without changing behavior. |
| `reduce-complexity` | Reduce method complexity | `pr-slicing` | Copilot inline | Copilot agent mode | A method is long or deeply nested. |

## modernization

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `dependency-upgrade` | Upgrade one dependency safely | `pr-slicing` | Devin | Claude Code, Copilot agent mode | Bumping a library or framework version. |
| `language-version-migration` | Migrate a module to a newer language/runtime | `plan-then-implement` | Devin | Claude Code | Java 8->17/21, .NET Framework->.NET 8, JS->TS, Python 3.x upgrades, one slice at a time. |
| `codemod-instead-of-ai` | Use a codemod or IDE refactor instead of AI | `right-tool-for-task` | No AI (deterministic tool) | Copilot Chat (ask) | A rename, API replacement or format change across many files that a rule can describe. |

## security

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `security-review-diff` | Security review of a diff | `pr-readiness-selfcheck` | Copilot Chat (ask) | Claude Code | Before merging changes that touch input handling, auth, data or config. |
| `secret-leak-check` | Check a diff for leaked secrets | `pr-readiness-selfcheck` | No AI (deterministic tool) | Copilot Chat (ask) | Before every push; use the secret scanner first, AI second. |
| `threat-model-lite` | Lightweight threat model for a feature | `plan-then-implement` | Copilot Chat (ask) | Claude Code | Designing a feature that handles sensitive data or new entry points. |

## data_sql

| ID | Title | Practice | Best tool | Also works in | When to use |
|---|---|---|---|---|---|
| `sql-review` | Review SQL or stored procedure | `pr-readiness-selfcheck` | Copilot Chat (ask) | Claude Code | Changing queries, procedures or migrations. |
| `sql-optimize-query` | Optimize a slow query | `verify-before-done` | Copilot Chat (ask) | Claude Code | A query is slow and you have its plan or timings. |
| `sql-proc-with-tests` | Stored procedure with tests | `test-first-acceptance` | Copilot agent mode | Claude Code | Creating or changing a stored procedure. |
| `migration-safety` | Database migration safety review | `pr-slicing` | Copilot Chat (ask) | Claude Code | Any schema change. |

## Equivalent file-based workflows

Many templates also exist as ready-to-run files installed by the kit:

| Template | Copilot prompt file | Claude Code | Devin |
|---|---|---|---|
| pr-readiness-check | `/pr-readiness` | `/pr-readiness`, skill `pr-readiness-selfcheck` | `!pr-readiness` |
| pr-slice-plan | `/slice-pr` | `/slice-pr`, skill `pr-slicing` | part of `!ticket-to-pr` |
| ticket-to-plan | `/jira-to-plan` | `/jira-to-plan`, skill `ticket-to-plan` | `!ticket-to-pr` |
| flaky-test-diagnose | `/fix-flaky-test` | `/fix-flaky-test`, skill `flaky-test-hardening` | `!flaky-fix` |
| debug-systematic | `/debug-investigation` | `/debug-investigation`, skill `systematic-debugging` | `!bug-investigate` |
| dependency-upgrade | `/dependency-upgrade` | `/dependency-upgrade` | `!dep-upgrade` |
| context-pack-agents-md | `/create-agents-md` | `/create-agents-md`, skill `context-pack` | Knowledge `repo-conventions` |
