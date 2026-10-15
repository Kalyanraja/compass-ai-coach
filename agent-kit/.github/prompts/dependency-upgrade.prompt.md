---
description: 'Plan and perform a single dependency or framework upgrade safely: read release notes, find breaking changes, update, fix, verify.'
argument-hint: 'package name, current version, target version'
agent: 'agent'
---
<!-- practice: P1 pr-slicing; P6 verify-before-done -->

Upgrade `${input:package:package}` from `${input:from:current}` to `${input:to:target}`.

Rules:
- One dependency (or one tightly coupled group) per PR. No unrelated upgrades or refactors.
- Use only the approved package source ({{PACKAGE_REGISTRY}}). Do not add new packages.
- Do not change lockfiles by hand; use the package manager.

Steps:
1. Baseline: run build and full tests on the current version; record results.
2. Read the changelog/release notes/migration guide between the versions (ask the human to paste them if you cannot access them). List breaking changes and deprecations that affect this repo; search usages (#codebase).
3. Update the version with the package manager. Rebuild.
4. Fix compile errors and deprecations one at a time; run tests after each group.
5. Run full build, tests and linter. Compare with baseline.
6. Note transitive dependency changes and any security advisories resolved.

Output:
```
Baseline: <results>
Breaking changes affecting us: <list with file refs>
Changes made: <list>
After: <build/test/lint results>
Risk: <low/med/high>, rollback: revert this PR
Follow-ups: <deprecations left>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
