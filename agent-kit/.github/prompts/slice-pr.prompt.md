---
description: 'Split a large change or branch into a sequence of small, independently reviewable PRs with a dependency order.'
argument-hint: 'base branch and max lines per PR'
agent: 'agent'
---
<!-- practice: P1 pr-slicing -->

Plan how to split the work on this branch (base `${input:base:main}`) into small PRs of at most ${input:maxLines:400} changed lines each. Do not rewrite history or push. Produce a plan only.

Steps:
1. Run `git diff --stat ${input:base:main}...HEAD` and read the diff. Group changes by concern.
2. Classify each group: mechanical (rename/move/format), refactor (no behavior change), new behavior, tests, config/migration, cleanup.
3. Order slices so each one builds, passes tests and is safe to merge alone. Typical order: mechanical > refactor > schema/config (backward compatible) > behavior behind tests (feature flag if needed) > cleanup.
4. For each slice, list files, estimated size, tests that prove it, and how a reviewer verifies it.
5. Flag any slice that cannot stand alone and say why.

Output:
```
## Slicing plan (<N> PRs)
| # | Title | Type | Files | ~Lines | Depends on | Tests / verification |
|---|---|---|---|---|---|---|
### Commands to create slices (for the human to run)
<git commands using new branches and cherry-pick or path checkout; no force-push to shared branches>
### Risks
- <cross-slice risks, flags needed>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
