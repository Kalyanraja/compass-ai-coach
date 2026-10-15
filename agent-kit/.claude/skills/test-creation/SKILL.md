---
name: test-creation
description: Use when asked to add, generate or improve tests for existing code (unit, integration, API or UI with JUnit, xUnit, NUnit, pytest, Jest, Vitest or Playwright), or to close test gaps before a change. Picks the right test level, follows repo conventions, writes behavior-focused tests with synthetic data, runs them, and reports evidence and remaining gaps.
metadata:
  practice: P3 test-first-acceptance
  source: original Compass content; framework rules informed by github/awesome-copilot java-junit, csharp-xunit, pytest-coverage, javascript-typescript-jest, playwright-* instructions and test-gap-audit (MIT)
---

# Test Creation

Tests exist to catch specific breaks. Write fewer, sharper tests.

## Steps
1. **Scope**: identify the unit/feature and its public behavior. Read existing tests for it and the nearest similar test file; copy its conventions.
2. **Inventory behaviors**: list inputs, outputs, side effects, error paths, permissions. Check what existing tests already cover.
3. **Pick levels**: unit for logic and edge cases, integration for boundaries (DB, HTTP, queue), UI/E2E only for critical journeys.
4. **Write the case table** (show it; wait for "go" if more than 8 cases):
   `| Test name | Given | When | Then | Level |`
5. **Write tests** using the framework rules below.
6. **Run** the new tests, then the full suite. If testing existing code, temporarily break the behavior (or reason through the mutation) to confirm at least one test fails.
7. **Report** evidence and gaps.

## Framework quick rules
| Framework | Rules |
|---|---|
| JUnit 5 | `assertEquals(expected, actual)`, `assertAll`, `assertThrows` + message check, `@ParameterizedTest`, no JUnit 4 imports |
| xUnit | `[Fact]`/`[Theory]` + `[InlineData]`, constructor setup, `IAsyncLifetime`, `Assert.ThrowsAsync<T>` |
| NUnit/MSTest | `[TestCase]`/`[DataRow]`, `Assert.That` constraint model (NUnit) |
| pytest | fixtures, `parametrize`, `pytest.raises(match=)`, `tmp_path`, `monkeypatch` |
| Jest/Vitest | `describe`/`it('should ... when ...')`, fake timers, mock at module boundary, reset in `afterEach` |
| Playwright | role-based locators, web-first `expect`, no `waitForTimeout`, isolated state per test |

## Quality bar
- Each test names the break it catches; expected values are literals.
- Assert outcomes, not mock calls (unless the call is the contract, then assert arguments too).
- No fixed sleeps, no order dependence, no shared mutable state.
- Coverage is a hint, not a goal. Do not write tests that only execute lines.

## Output
```
Added: <file>: <test names>
Run: `<cmd>` -> <passed/failed>; full suite: <summary>
Mutation check: <bug -> catching test>
Gaps: <untested behaviors and why>
```

## Stop and ask when
- Code is untestable without a design change (propose the smallest seam, do not refactor silently).
- Expected behavior is unclear or existing behavior looks like a bug (report it; do not encode the bug in a test without asking).

## Safety
- Synthetic data and fake credentials only. Never copy production data or real customer records into fixtures.
- Do not change production code unless asked; a human reviews all tests.
- Never include secrets, credentials, PII or production data.
