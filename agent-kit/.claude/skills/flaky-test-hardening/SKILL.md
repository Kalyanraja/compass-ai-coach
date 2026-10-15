---
name: flaky-test-hardening
description: Use when a test passes and fails intermittently, fails only in CI or in parallel, depends on run order, or contains sleeps, fixed waits, retries or force-clicks (Playwright, Cypress, Selenium, JUnit, xUnit, pytest, Jest). Measures the failure rate, classifies the nondeterminism source, fixes it at the cause, and proves the fix with repeated runs.
metadata:
  practice: P8 flaky-test-hardening
  source: original Compass content; informed by obra/superpowers condition-based-waiting (MIT) and github/awesome-copilot cypress-flake-fixer and playwright instructions (MIT)
---

# Flaky Test Hardening

A flaky test is a real bug in the test or the code. Retries hide it; measurement and root cause fix it.

## Never as the fix
Adding sleeps, raising timeouts, adding retries, `{ force: true }`, skipping or quarantining (quarantine is a temporary, ticketed, human decision, not a fix).

## Steps
1. **Baseline**: run the test N times in isolation and with its full file/suite.
   - Playwright: `npx playwright test <file> --repeat-each=20 --retries=0 --workers=4`
   - pytest: loop `for i in $(seq 20); do pytest <test> -p no:randomly || echo FAIL $i; done` (or `pytest-repeat`)
   - Jest/Vitest: loop the single test; also run with `--runInBand` to test parallelism effects
   - JUnit/xUnit: `@RepeatedTest(20)` locally, or a shell loop with the single-test filter
   Record `fails/runs` for isolated, suite, and parallel.
2. **Classify** (pick the evidence-backed category):
   | Category | Signs | Fix |
   |---|---|---|
   | Timing / missing wait | sleeps, `waitForTimeout`, asserting before async completes | wait for condition, web-first assertions, await the promise |
   | Order dependence / shared state | fails only with other tests, static/global state, shared DB rows | isolate data per test, reset state, unique IDs |
   | Time and timezone | dates, midnight, DST, `now()` | inject clock, fixed timezone |
   | Randomness | random data, unordered collections | seed, sort before compare |
   | Concurrency | parallel workers collide | unique resources per worker, locks in code under test |
   | External dependency | network, real services | stub at the boundary, contract test separately |
   | Async misuse | unawaited promise, `async void`, fire-and-forget | await properly |
   | Environment | CI-only, resource limits, viewport, locale | pin config, make test explicit about env |
   | Selector brittleness (UI) | nth-child, generated classes, detached DOM | role/label/test-id locators, re-query after navigation |
3. **Prove the hypothesis**: make it fail on purpose (for example run in parallel, shift clock) when possible.
4. **Fix at the source** with the smallest change. If the race is in production code, write a failing test and treat it as a bug (`systematic-debugging`).
5. **Verify**: rerun about 3x the runs needed to see one failure at baseline (for example baseline 1/10 -> 30 clean runs), plus the full suite.
6. **Sweep**: search for the same pattern elsewhere and list the files.

## Output
```
Test: <id>
Baseline: isolated <f>/<n>, suite <f>/<n>, parallel <f>/<n>
Category: <category>; evidence: <file:line / log>
Fix: <change>
After: <f>/<n> (<command>); full suite: <summary>
Same pattern elsewhere: <files>
```

## Stop and ask when
- The fix needs production code changes, shared test infrastructure changes, or a quarantine decision.

## Safety
- Use synthetic test accounts and data. Never point repeated runs at production or shared environments that send real notifications or charge money.
- Never include secrets, credentials, PII or production data.
- A human reviews every change before merge.
