---
description: 'Trace a bad value or wrong behavior backward through the call chain to its original trigger and propose a fix at the source plus defense-in-depth.'
argument-hint: 'where the bad value or error appears'
agent: 'ask'
---
<!-- practice: P6 verify-before-done -->

The problem shows up at: ${input:symptom:file:line, error, or bad value}

Trace backward, do not patch the symptom.

1. Immediate cause: which line produces the error or bad value?
2. Ask "what called this, with what value?" Follow callers up the stack (#usages, #codebase). Show the chain as `A -> B -> C` with file:line.
3. Keep going until you reach the original trigger (input, config, test setup, data, race).
4. Explain why the bad value was allowed through each layer.
5. Propose: (a) the fix at the source, (b) validation at the layers that should have rejected it, (c) a regression test.

Output:
```
Call chain: <trigger file:line> -> ... -> <symptom file:line>
Original trigger: <one sentence>
Fix at source: <change>
Defense-in-depth: <validations per layer>
Regression test: <name and assertion>
Confidence: high | medium | low (what would raise it)
```
If you cannot trace further, say exactly where the trail ends and what logging would reveal the next step.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
