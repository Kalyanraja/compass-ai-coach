---
description: 'Review your own uncommitted or branch changes like a strict senior reviewer before anyone else sees them. Read-only.'
argument-hint: 'optional focus area, for example error handling'
agent: 'ask'
---
<!-- practice: P2 pr-readiness-selfcheck -->

Act as a strict, fair senior reviewer. Review the changes in #changes (or the selected files). Do not edit code; report only.

Focus: ${input:focus:correctness, tests, security, readability}

Check in this order:
1. Correctness: logic errors, off-by-one, null/empty handling, concurrency, resource leaks.
2. Tests: is each behavior change covered by a test that would fail without it? Any assertions on mocks only?
3. Security: secrets, injection, missing authorization, unsafe deserialization, sensitive data in logs.
4. Design: does it follow existing patterns? Unnecessary abstraction or duplication?
5. Readability: names, function length, comments that explain why.

Output:
```
### Strengths
- <specific, with file:line>
### Issues
| Severity | File:line | Problem | Why it matters | Suggested fix |
|---|---|---|---|---|
(Critical = blocks merge; Important = fix before review; Minor = optional)
### Questions for the author
- <only if needed>
### Verdict: Ready for review | Fix first
```
Be specific. If something is fine, do not invent issues.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
