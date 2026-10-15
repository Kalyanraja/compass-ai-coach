---
description: 'Draft a reviewer-friendly PR description from the branch diff: what, why, how tested, risk, rollback.'
argument-hint: 'ticket ID and base branch'
agent: 'agent'
---
<!-- practice: P2 pr-readiness-selfcheck -->

Draft a pull request description for the current branch against `${input:base:main}` for ticket `${input:ticket:TICKET-ID}`.

Rules:
- Read the actual diff (`git diff ${input:base:main}...HEAD`) and commit messages. Describe only what the diff shows.
- If you did not run tests in this session, write "Not run by agent" under Testing. Never invent results.
- No secrets, internal hostnames, personal data or customer data.
- Keep it under 300 words. Reviewers skim.

Output exactly:
```markdown
## What
<1-3 bullets of user-visible or system-visible change>

## Why
<problem or ticket goal, link: {{TICKET_URL_PREFIX}}${input:ticket:TICKET-ID}>

## How
<key design choices, files a reviewer should start with>

## Testing
- Automated: <commands and results>
- Manual: <steps, or "none">

## Risk and rollback
- Risk: <low/medium/high + why>
- Rollback: <revert commit / disable flag / migration down>

## Out of scope / follow-ups
- <items>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
