---
description: 'Write a Conventional Commits message from the staged diff.'
argument-hint: 'optional ticket ID'
agent: 'ask'
---
<!-- practice: P2 pr-readiness-selfcheck -->

Write a commit message for the staged changes (#changes). Ticket: ${input:ticket:none}.

Format (Conventional Commits):
```
<type>(<scope>): <imperative summary, max 72 chars>

<why the change was needed, what it does; wrap at 72>

Refs: <ticket>
```
Types: feat, fix, refactor, test, docs, build, ci, chore, perf. Use `!` and a `BREAKING CHANGE:` footer for breaking changes.
If the staged diff mixes unrelated concerns, say so and suggest how to split the commit instead.
Describe only what the diff shows. No secrets or personal data.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
