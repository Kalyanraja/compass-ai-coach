---
description: 'Brainstorm a feature into a short written spec through focused questions before any code: goals, non-goals, acceptance criteria, constraints.'
argument-hint: 'one-line idea or ticket'
agent: 'ask'
---
<!-- practice: P4 plan-then-implement -->

Idea: ${input:idea:describe the feature or change}

Do not write code. Run a short design conversation, then write a spec.

1. Ask one question at a time (max 5 total), most important first: who uses it and why, what success looks like, what must not happen, constraints, what exists today. Offer a concrete guess the human can correct.
2. Look at the codebase (#codebase) for related code and say what you found.
3. Propose 2-3 approaches with trade-offs and a recommendation.
4. After the human answers, write the spec:

```markdown
# Spec: <title>
Status: Draft | Date: <YYYY-MM-DD>
## Intent and why
## Goals / Non-goals / Anti-goals
## User scenarios (P1, P2, ...) with Given/When/Then acceptance criteria
## Edge cases
## Functional requirements (FR-001 ... use MUST/SHOULD)
## Constraints (tech, security, data, performance)
## Success criteria (measurable)
## Open questions [NEEDS CLARIFICATION: ...]
## Decisions made by the agent (for human review)
```
Save to `docs/specs/<YYYY-MM-DD>-<topic>.md` only after the human approves.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
