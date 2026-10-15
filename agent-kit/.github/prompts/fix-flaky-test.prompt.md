---
description: 'Diagnose and fix a flaky test by measuring failure rate, finding the nondeterminism source, and proving the fix with repeated runs.'
argument-hint: 'test name/file and CI failure link or log excerpt (no secrets)'
agent: 'agent'
---
<!-- practice: P8 flaky-test-hardening -->

Fix the flaky test `${input:test:test file and name}`. Evidence: ${input:evidence:paste failure message or log excerpt, redacted}

Do not add retries, increase timeouts, add sleeps, use `force: true`, or skip/quarantine the test as the fix.

Steps:
1. Baseline: run the test ${input:runs:20} times in isolation (for example `--repeat-each`, a loop, or `pytest --count`). Record fail count. Also run it with the full file/suite to check order dependence.
2. Classify the cause (check each): fixed sleeps or timing, missing wait for async condition, shared state or order dependence, test data collisions, time/date/timezone, randomness, unawaited promise or async void, external service, resource leaks, environment differences (CI vs local, parallelism).
3. State one hypothesis: "Fails when X because Y". Show the line(s).
4. Make the smallest fix at the source: wait for a condition, isolate data, inject clock/seed, await properly, reset state.
5. Prove it: rerun the same N times (use about 3x the original failure interval) and the full suite.

Output:
```
Baseline: <fails>/<runs> (<command>)
Root cause: <category> - <one sentence> (<file:line>)
Fix: <what changed and why it removes the nondeterminism>
After: <fails>/<runs> (<command>), full suite: <summary>
Similar risks elsewhere: <files with the same pattern>
```
Stop and ask if the root cause is in production code or shared infrastructure.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
