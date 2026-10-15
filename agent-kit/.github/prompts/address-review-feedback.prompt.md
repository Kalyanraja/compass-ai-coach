---
description: 'Process code review comments with technical rigor: verify each one against the codebase, push back with evidence when wrong, fix one at a time with tests.'
argument-hint: 'paste review comments'
agent: 'agent'
---
<!-- practice: P6 verify-before-done -->

Review comments: ${input:comments:paste the reviewer comments}

Rules:
- No performative agreement ("Great point!", "You're absolutely right"). State the technical requirement or just fix it.
- If any comment is unclear, ask about it before implementing anything; comments may be related.
- Verify each suggestion against this codebase before changing code. If it would break behavior, conflicts with an earlier decision, or is unused (YAGNI), reply with evidence.
- Implement in order: blocking (bugs, security) > simple > complex. Test after each.

Output:
```
| # | Comment (short) | Verdict: accept / push back / clarify | Evidence | Change made | Test |
|---|---|---|---|---|---|
Draft replies (one per comment, factual, no thanks or apologies):
Verification: <full suite result>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
