---
description: 'Investigate a bug or failing test systematically: reproduce, gather evidence, form one hypothesis at a time. No fix until root cause is shown.'
argument-hint: 'symptom, error message or failing test (redacted)'
agent: 'agent'
---
<!-- practice: P6 verify-before-done -->

Symptom: ${input:symptom:error message, stack trace, failing test, or unexpected behavior}

Iron rule: no fix until the root cause is identified and shown with evidence.

Phase 1 - Reproduce and observe
1. Read the full error and stack trace. Note file, line, error code.
2. Reproduce with the smallest command or test. Record the exact command and output. If you cannot reproduce, say so and list what data you need.
3. Check recent changes: `git log -p --since="{{LOOKBACK:7 days}}" -- <suspect paths>`.
4. For multi-component flows, add temporary diagnostic logging at each boundary (no secrets) to find where data goes wrong.

Phase 2 - Compare
5. Find a similar working path in the codebase. List every difference.

Phase 3 - Hypothesis
6. State one hypothesis: "Root cause is X because evidence Y." Test it with the smallest change or probe. If wrong, form a new one; do not stack fixes.

Phase 4 - Fix (only after confirmation)
7. Write a failing test that reproduces the bug. Fix at the source. Run the test and full suite.
8. If 3 fixes fail, stop and report: the design may be wrong.

Output:
```
Reproduction: <command> -> <observed>
Evidence: <logs/lines>
Root cause: <one sentence> (<file:line>) | Not yet found: <what is missing>
Fix: <change> | Regression test: <name>
Verification: <commands and results>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
