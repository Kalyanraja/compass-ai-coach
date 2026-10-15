---
description: 'Write focused tests for the selected code or behavior, run them, and report evidence. Tests first for new behavior.'
argument-hint: 'target file/class/function and behavior to cover'
agent: 'agent'
---
<!-- practice: P3 test-first-acceptance -->

Write tests for `${input:target:selected code}` covering: ${input:behavior:the behaviors and edge cases to cover}.

Rules:
- Follow the test conventions in this repo and `.github/instructions/tests.instructions.md`. Copy the style of the nearest existing test file and name it.
- One behavior per test; behavior-describing names; literal expected values; no fixed sleeps.
- Mock only external boundaries. Never assert on a mock's existence.
- Synthetic data only.
- If this is new behavior that does not exist yet: write the test, run it, and show it failing for the expected reason before any implementation.
- Do not change production code unless asked. If the code is hard to test, say why and propose the smallest seam.

Steps:
1. List the test cases you will write (table: name, scenario, expected) and wait for "go" if more than 8.
2. Write the tests.
3. Run them with `{{SINGLE_TEST_CMD}}` then the full suite `{{TEST_CMD}}`.
4. Report.

Output:
```
Tests added: <file: test names>
Evidence: <command> -> <pass/fail counts>
Mutation check: <for 2-3 realistic bugs, which test would catch it>
Gaps not covered: <list>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
