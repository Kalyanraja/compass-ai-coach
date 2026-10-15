<!-- Suggested macro: !flaky-fix | practice: P8 flaky-test-hardening -->
# Flaky Test Fix

## Overview
Measure a flaky test's failure rate, find the nondeterminism source, fix it at the cause, and prove the fix with repeated runs in a draft PR.

## What's Needed From User
- Repository, base branch, and the test identifier (file and name)
- A redacted failure excerpt or CI run link
- How to run the test locally if not in `AGENTS.md`

## Procedure
1. Read `AGENTS.md` and `.claude/skills/flaky-test-hardening/SKILL.md`.
2. Create branch `fix/flaky-<short-test-name>`.
3. Baseline: run the test 20+ times isolated, with its file/suite, and in parallel; record fail counts and commands.
4. Classify the cause with evidence (timing, shared state/order, time zone, randomness, concurrency, external dependency, async misuse, environment, brittle selector).
5. Apply the smallest fix at the source.
6. Rerun with about 3x the runs needed to see one baseline failure, plus the full suite.
7. Search for the same pattern in other tests; list them in the PR (do not fix them in this PR unless trivial and asked).
8. Open a draft PR with baseline, cause, fix, after results.

## Specifications
- PR shows baseline and after fail counts with exact commands.
- The fix removes the nondeterminism; it is not a sleep, retry, timeout increase, force-click, or skip.
- Full suite passes.

## Advice and Pointers
- Playwright: `--repeat-each=20 --retries=0`; replace `waitForTimeout` with web-first assertions or `waitForResponse`.
- Cypress: replace `cy.wait(<ms>)` with aliased intercepts; avoid `{ force: true }`.
- JVM/.NET: inject clocks; isolate DB rows per test; await async work.
- If the race is in production code, write a failing test that exposes it and report before changing production code.

## Forbidden Actions
- Do not add retries, sleeps, longer timeouts, or skip/quarantine annotations as the fix.
- Do not run repeated tests against production or shared environments that send real notifications or move money.
- Do not merge.
- Do not use or expose secrets, credentials, PII or production data.
- Do not skip human review: deliver a draft PR or a report for a person to review and merge.
