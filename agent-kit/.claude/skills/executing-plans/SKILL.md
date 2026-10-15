---
name: executing-plans
description: Use when implementing an approved implementation plan yourself, task by task, in the current session. Works through tasks in order with red-green tests, keeps a progress ledger that survives context loss, records deviations as explicit rulings, and ends with a whole-branch review before integration.
metadata:
  practice: P4 plan-then-implement; P6 verify-before-done
  source: adapted from obra/superpowers executing-plans (MIT)
---

# Executing Plans

The plan did the thinking. Execute it exactly, prove each step, and leave a record.

## Setup
1. Confirm you are on a feature branch (never implement on `main`/`master` without explicit consent).
2. Read the plan and its spec completely. List any step that is impossible or contradicts the spec before starting.
3. Create a ledger file next to the plan: `docs/plans/<plan-name>.ledger.md`.

## Per task
1. Mark the task in progress in the ledger with the current commit SHA.
2. Do the steps in order: write failing test, run it and read the failure, implement, run it, run the full suite.
3. If a step's output does not match the plan's "expected":
   - Plan is wrong -> record a ruling and continue.
   - Code is wrong -> use `systematic-debugging`.
4. Commit as the plan says. Mark the task done in the ledger with the test result line.

Ledger entry format:
```
## Task N - <name> - DONE @ <sha>
Tests: <command> -> <summary>
Ruling: <what you decided> - <why> - <cost if wrong>   (only when you deviated)
```

## Keep going, except for these four stops
Do not ask "should I continue?" between tasks. Stop and ask only for:
1. An irreversible or destructive operation (data deletion, migrations on shared DBs, force-push).
2. A security-sensitive action (auth, secrets, permissions).
3. A side effect outside the branch (merge, push to shared branch, deploy, publish, ticket changes).
4. A plan so broken that every path forward is a guess.

## Finish
1. Run full build, tests and linter; quote results.
2. Do a whole-branch review: use `requesting-code-review` (a subagent if your tool supports it, otherwise a fresh-eyes self-review with the same checklist).
3. Fix Critical and Important findings, each with a red-green test. Log Minor ones.
4. Run `pr-readiness-selfcheck`, then hand off to the human. Never merge yourself.

## Safety
- No secrets, PII or production data in code, tests, ledger or commits.
- Never claim a task is done without the test output in the ledger.
