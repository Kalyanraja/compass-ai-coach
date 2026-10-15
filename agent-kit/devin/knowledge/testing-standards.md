# Knowledge: Testing standards

<!-- Paste into Devin: Settings > Knowledge > Create knowledge. Pin to all repos (or each team repo). practice: P3 test-first-acceptance; P8 flaky-test-hardening -->

**Name:** Testing standards
**Trigger description:** When writing, changing, debugging or reviewing automated tests (unit, integration, API, Playwright or other UI tests), or when a test is flaky.
**Pin to:** All repos

**Content:**
- Test first for new behavior: write the failing test from the acceptance criterion, run it, confirm the failure reason, then implement.
- One behavior per test; names like `should_<result>_when_<condition>`; literal expected values; assert real behavior, not mocks.
- Frameworks here: {{TEST_FRAMEWORKS}}. Follow the nearest existing test file's style.
- No fixed sleeps or waits (`Thread.sleep`, `Task.Delay`, `time.sleep`, `waitForTimeout`, `cy.wait(ms)`); wait for a condition or use web-first assertions.
- Tests must pass in any order and in parallel; each test creates and cleans its own data.
- Playwright: role/label/test-id locators, `await expect(...)` assertions, `--repeat-each` to measure flakiness.
- Flaky test fixes must show before/after fail counts from repeated runs. Retries, longer timeouts, skips and force-clicks are not fixes.
- Synthetic data only; never production data or real credentials in fixtures.
- Never include secrets, credentials, PII or production data.
