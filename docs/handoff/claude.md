# Claude Code (VS Code) instructions

Claude Code runs in VS Code with **no MCP servers and no extra skills** installed by default. The repository's `CLAUDE.md` imports `AGENTS.md`, so the conventions load automatically. If you want the review skills, copy them in first:

```
agent-kit\install-kit.bat .      (Windows)   or   ./agent-kit/install-kit.sh .
```

The installer never overwrites existing files. Start each task in **plan mode** and approve the plan before edits.

---

## Task 1: Independent architecture and security review (read-only)

```
Use plan mode. Do not edit files in this task.

Review the Workflow coach against docs/workflow-coach.md, docs/nfr-security.md and the original requirements in docs/IMPLEMENTATION-REPORT.md.
Focus areas, in order:
1. Trust boundaries: compass/workflow/workspace.py (allowed roots, traversal, symlinks, credential files), compass/workflow/runner.py (templates, argument validation, environment, timeouts, approval), compass/server.py (_check_origin, roles, owner-scoped journeys), compass/jira_client.py (host pinning, token handling).
2. Privacy: confirm compass/aggregate.py never reads private.db, and journeys are session-only.
3. Honesty: confirm missing tools are "not-checked", malformed reports are "blocked", a test file existing is never counted as a pass, and findings stay "candidate".
4. Prompt injection: confirm project text is fenced as untrusted and cannot change settings.
For each issue give: file:line, a concrete failing scenario, severity, and the smallest fix. Separate confirmed issues from hypotheses. Then run python -m unittest discover -s tests -t . -v and paste the summary.
```

## Task 2: Fix confirmed issues (one PR per concern)

```
For each confirmed issue from Task 1, in order of severity:
1. Write a failing test first (tests/test_workflow.py or tests/test_acceptance.py) that reproduces it. Run it and show it failing.
2. Make the smallest fix. Run the full suite and python -m compass eval; paste the summary lines.
3. Keep each change under about 400 lines and one concern.
Never weaken a guardrail to make a test pass. Stop and ask me if a fix changes documented behavior.
```

## Task 3 (stretch): Implement the planned "PR review" workflow

```
Goal: turn workflows/packs/pr-review.json from "planned" into a working workflow, following the same pattern as feature-api.

1. Read compass/workflow/coach.py (WORKING, pack, next_questions), journey.py (run_checks, verdict, NEXT) and the three working packs.
2. Design the pack in plan mode first: required facts, at most 3 questions at a time (for example linked story, risk areas, test evidence), staged actions (self-review -> slice if > 400 lines -> evidence), acceptance criteria (description present, tests changed for behavior changes, no secrets in the diff, size under limit) and checks (diff import + secrets_in_diff + tests report).
3. Implement it with tests: a passing PR diff and a failing one (synthetic, add under examples/), plus the API refusing it before you flip status to working.
4. Update WORKING, the UI copy, docs/workflow-coach.md and the deck's workflow slide text.
Constraints: standard library only; no new dependencies; all existing tests pass; eval stays >= 80%.
```

## Task 4: Final pre-submission check

```
Use the verification-before-completion approach:
1. Run: python -m unittest discover -s tests -t . -v ; python -m compass eval ; python -m compass compliance ; python -m compass doctor
2. Start the app and walk docs/demo-script.md end to end. Confirm each verdict matches docs/measurements.md.
3. Search the repository for company names, internal URLs, real emails, tokens or real personal data (git grep -n -i for your company name and domain). Report any hit; the public repo must stay generic.
4. Check docs/acceptance-criteria.md and docs/rubric-mapping.md: every claim must point to a file or test that exists.
5. Output a READY / NOT READY list with evidence for each item.
```
