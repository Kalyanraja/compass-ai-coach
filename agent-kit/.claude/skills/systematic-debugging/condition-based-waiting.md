# Condition-based waiting

Adapted from obra/superpowers (MIT). Flaky tests often guess at timing. Wait for the condition you care about, not for a duration.

## Replace
| Instead of | Use |
|---|---|
| `Thread.sleep(500)` (Java) | Awaitility `await().atMost(5, SECONDS).until(() -> repo.count() == 1)` |
| `await Task.Delay(500)` (C#) | poll helper with timeout, or await the task/event directly |
| `time.sleep(1)` (Python) | poll loop with deadline, or `pytest` fixture that waits on the event |
| `setTimeout`/`sleep` (JS) | `await waitFor(() => expect(x).toBe(y))`, fake timers |
| `page.waitForTimeout(1000)` (Playwright) | `await expect(locator).toHaveText(...)`, `page.waitForResponse(...)` |
| `cy.wait(1000)` (Cypress) | `cy.intercept(...).as('x'); cy.wait('@x')`, retrying assertions |

## Generic poll helper (shape)
```
waitFor(condition, description, timeoutMs = 5000):
  start = now()
  loop:
    if condition(): return
    if now() - start > timeoutMs: fail("Timed out waiting for " + description)
    sleep(10..50 ms)
```
Rules: always a timeout with a descriptive error; read fresh state inside the loop; poll at a sensible interval.

## When a fixed delay is correct
Only when testing timing itself (debounce, throttle, TTL). First wait for the triggering condition, then wait the known interval, and comment why.

## Safety
- Never include secrets, credentials, PII or production data.
- A human reviews every change before merge.
