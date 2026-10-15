<!-- Suggested macro: !test-backfill | practice: P3 test-first-acceptance -->
# Test Creation / Backfill

## Overview
Add behavior-focused automated tests for a named module, feature or ticket, following the repo's test conventions, and open a draft PR with run evidence. Production code is not changed.

## What's Needed From User
- Repository, base branch, and the target (path, class, endpoint or feature)
- Behaviors or acceptance criteria to cover (redacted)
- Test levels wanted (unit / integration / UI) if not obvious
- Any test environment details not in `AGENTS.md` (never real credentials; use the team's test secrets mechanism)

## Procedure
1. Create branch `test/{{TICKET_ID}}-<short-name>` from the base branch.
2. Read `AGENTS.md`, `.github/instructions/tests.instructions.md`, the language instructions file, and `.claude/skills/test-creation/SKILL.md`.
3. Read the target code and its existing tests; pick the nearest similar test file as the style reference.
4. Write a case table (test name, given, when, then, level) into the PR description draft.
5. Write the tests; run them, then the full suite; fix test mistakes (not production code).
6. Mutation check: for 2-3 realistic bugs, confirm at least one test would fail (temporarily change the code locally, run, revert; never commit the mutation).
7. Open a draft PR with the case table, commands and results, and remaining gaps.

## Specifications
- New tests pass and the full suite passes; results quoted in the PR.
- Every listed behavior has at least one test or is listed under "Gaps" with a reason.
- No production code changes, no fixed sleeps, no assertions on mocks only.
- Test data is synthetic.

## Advice and Pointers
- Prefer unit tests for logic, integration tests for boundaries, UI tests only for critical journeys.
- Use literal expected values; one behavior per test; behavior-describing names.
- If the code is untestable without a refactor, stop and propose the smallest seam in the PR description.
- If existing behavior looks like a bug, do not encode it in a test; report it.

## Forbidden Actions
- Do not modify production code, CI pipelines or shared test infrastructure.
- Do not use production data, real customer records or real credentials in fixtures.
- Do not merge or approve the PR.
- Do not skip human review: deliver a draft PR or a report for a person to review and merge.
