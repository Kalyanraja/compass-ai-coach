---
description: 'Test-writing rules: test-first acceptance, one behavior per test, no fixed sleeps, synthetic data. Applies to test files in any language.'
applyTo: '**/test/**,**/tests/**,**/__tests__/**,**/*Test.java,**/*Tests.java,**/*IT.java,**/*Tests.cs,**/*Test.cs,**/test_*.py,**/*_test.py,**/*.test.ts,**/*.test.tsx,**/*.test.js,**/*.spec.ts,**/*.spec.js'
---
<!-- practice: P3 test-first-acceptance; P8 flaky-test-hardening -->

# Test rules

## Write tests that prove behavior
- Start from the acceptance criterion. Write the test first, run it, and confirm it fails for the expected reason before implementing.
- Name the break the test catches. If you cannot name a production change that would make it fail, redesign the test.
- One behavior per test. Name tests `should_<result>_when_<condition>` or Given/When/Then.
- Arrange-Act-Assert. Keep setup short; extract helpers into test utilities, never into production classes.
- Use literal expected values. Never compute the expected value with the code under test.
- Assert real behavior and outputs. Do not assert on mocks; mock only slow or external boundaries.
- Cover: happy path, boundaries (0, 1, max, empty, null), invalid input, error paths, authorization failures.

## Keep tests deterministic
- No fixed sleeps (`Thread.sleep`, `Task.Delay`, `time.sleep`, `setTimeout`, `waitForTimeout`). Wait for a condition with a timeout.
- Control time, randomness and IDs (inject clocks, seed generators).
- Tests must pass in any order and in parallel. No shared mutable state between tests.
- Clean up data each test creates.
- Never add retries or longer timeouts to hide a race. Find the race.

## Data and safety
- Use synthetic fixtures only. No production data, customer data, PII or real credentials.
- Never delete, skip or weaken an assertion to make a test pass without a human's explicit approval.

## Done means
- The new test failed before the change and passes after it.
- The full suite passes: run `{{TEST_CMD}}` and include the summary line (passed/failed counts) in your reply.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
