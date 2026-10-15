---
description: 'Refactor selected code without changing behavior: pin behavior with characterization tests, change in small steps, verify after each step.'
argument-hint: 'target code and refactoring goal'
agent: 'agent'
---
<!-- practice: P1 pr-slicing; P6 verify-before-done -->

Refactor `${input:target:selected code}` to ${input:goal:goal, for example extract method, reduce complexity, remove duplication}.

Rules:
- Behavior must not change. No new features, no bug fixes mixed in (list bugs you notice separately).
- Keep public signatures unless asked. Keep the diff reviewable (under {{MAX_PR_LINES}} lines).

Steps:
1. Check test coverage of the target. If behavior is not pinned, write characterization tests first and run them (they must pass on the current code).
2. Plan the refactor as a sequence of small mechanical steps (rename, extract, inline, move). Show the list.
3. Apply one step at a time; run the relevant tests after each step.
4. Run the full suite and linter at the end.

Output:
```
Characterization tests: <added or existing, names>
Steps applied: <numbered>
Evidence: <commands and results after final step>
Behavior changes: none (or STOP and explain)
Bugs noticed (not fixed): <list>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
