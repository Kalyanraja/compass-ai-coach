---
description: 'Playwright UI test rules (TypeScript, Python, .NET): role-based locators, web-first assertions, no fixed waits, isolated state.'
applyTo: '**/*.spec.ts,**/*.spec.js,**/e2e/**,**/playwright/**,**/ui-tests/**,**/playwright.config.*,**/test_*_ui.py,**/*UiTests.cs'
---
<!-- practice: P8 flaky-test-hardening; P3 test-first-acceptance -->

# Playwright rules

## Locators
- Prefer user-facing locators: `getByRole`, `getByLabel`, `getByText`, `getByTestId` (in that order). Python: `get_by_role`; .NET: `GetByRole`.
- Never use brittle CSS/XPath chains, nth-child indexes or generated class names unless there is no alternative, and comment why.
- Avoid strict-mode violations: make locators specific (`{ name: 'Submit' }`, `exact: true`).

## Waiting and assertions
- Never use `page.waitForTimeout`, `sleep` or fixed delays.
- Use auto-retrying web-first assertions: `await expect(locator).toHaveText(...)`, `toHaveURL`, `toHaveCount`, `toBeEnabled`.
- Wait for the specific network response or UI state you depend on (`page.waitForResponse`, assertion on a result element), not `networkidle` by default.
- Do not raise global timeouts to hide slowness. Do not use `{ force: true }` without explaining the overlay or state it bypasses.

## Structure and state
- One feature or page per spec file. `test.describe` per feature, `test.step` for readable phases.
- Each test sets up its own state (API seeding or fixtures) and does not depend on order. Use `storageState` for login reuse.
- Use synthetic test accounts and data only. Never real customer data or production credentials; read secrets from CI variables.
- Page objects only for repeated flows; keep assertions in tests.

## Running and evidence
- Run: `{{E2E_CMD}}` (for example `npx playwright test --project=chromium`).
- For a suspected flaky test: run it repeatedly (`--repeat-each=20` or `--retries=0` loop) and report pass/fail counts before and after the fix.
- Attach trace (`--trace on`) for failures you report.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
