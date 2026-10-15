---
description: 'Turn a story, ticket or spec into a test plan: acceptance criteria mapped to unit, integration and UI tests with edge cases.'
argument-hint: 'paste acceptance criteria or point to the spec file'
agent: 'ask'
---
<!-- practice: P3 test-first-acceptance -->

Create a test plan for: ${input:story:paste the story and acceptance criteria}

Use the existing test layout and frameworks in this repo ({{TEST_FRAMEWORKS}}). Do not write code yet.

Steps:
1. Restate each acceptance criterion as a Given/When/Then scenario. Mark vague criteria `[NEEDS CLARIFICATION: ...]`.
2. For each scenario choose the cheapest test level that proves it (unit > integration > UI/E2E).
3. Add edge cases: empty, null, boundaries, invalid input, permissions, concurrency, failure of each dependency.
4. List test data needs (synthetic only) and any test doubles at external boundaries.
5. Identify which existing tests must change.

Output:
```
| ID | Scenario (Given/When/Then) | Level | Test name | File | Data / doubles |
|---|---|---|---|---|---|
Open questions: <list>
Out of scope: <list>
Order to implement (failing test first): <list of IDs>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
