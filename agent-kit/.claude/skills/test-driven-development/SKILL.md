---
name: test-driven-development
description: Use when implementing any feature, bug fix, or behavior change, before writing implementation code. Enforces red-green-refactor - write one failing test from the acceptance criterion, watch it fail for the right reason, write the minimum code to pass, then refactor while green.
metadata:
  practice: P3 test-first-acceptance
  source: adapted from obra/superpowers test-driven-development and writing-good-tests (MIT)
---

# Test-Driven Development

If you did not watch the test fail, you do not know that it tests the right thing.

## The rule
No production code without a failing test first. Exceptions only with the human's explicit OK (throwaway spikes, generated code, pure config).
If you wrote code before the test: set it aside, write the test, watch it fail, then reimplement.

## Cycle
1. **RED** - Write one minimal test for one behavior from the acceptance criterion. Clear name (`should_<result>_when_<condition>`), literal expected value, real code (mock only slow or external boundaries).
2. **Verify RED** - Run it. Confirm it fails (not errors) and the failure message is the one you expect because the feature is missing. Passes immediately? You are testing existing behavior; fix the test.
3. **GREEN** - Write the simplest code that passes. No extra options, no refactoring elsewhere.
4. **Verify GREEN** - Run the test, then the whole project suite (`{{TEST_CMD}}`), not just your file. Report any failure by name, even ones you did not cause.
5. **REFACTOR** - Clean names and duplication while staying green. No new behavior.
6. Repeat for the next behavior.

## Writing good tests
- Name the break: before writing the body, name the production change that would make this test fail. If you cannot, redesign the test.
- Derive expected values by hand. Never compute them with the code under test.
- Assert behavior, not mock existence. Mock responses mirror the full real structure.
- Test your contract at the boundary, not the framework's internals.
- Test-only helpers live in test utilities, never in production classes.
- Mutation check before finishing: for wrong constant, wrong branch, missing side effect, empty return, missing validation, at least one test fails.

## Bug fixes
Reproduce the bug as a failing test first. The test proves the fix and prevents regression.

## Red flags (start over)
"Too simple to test", "I'll test after", "I already tested manually", test passes on first run, cannot explain the failure, mocks everywhere.

## Output when done
```
Behavior: <criterion>
RED: <command> -> <failure message>
GREEN: <command> -> <pass count>; full suite: <summary>
Refactor: <what changed, still green>
```

## Stop and ask when
- The acceptance criterion is ambiguous, or passing requires changing an existing test's expectation.

## Safety
- Synthetic test data only. No secrets, PII or production data in tests or fixtures.
- Never delete or weaken a test to get green without human approval.
- A human reviews every change before merge.
