---
description: 'Convert an approved spec into an ordered, test-first task list grouped by user story (spec-kit style), with parallelizable tasks marked.'
argument-hint: 'path to spec file, for example docs/specs/2025-01-01-feature.md'
agent: 'agent'
---
<!-- practice: P4 plan-then-implement -->

Read the spec at `${input:spec:docs/specs/<file>.md}` and any linked plan. Produce `docs/plans/<same-name>-tasks.md`. Do not implement.

Rules:
- Every functional requirement and acceptance scenario maps to at least one task. List any requirement you could not map.
- Group by user story in priority order (P1 first). Each story must be independently testable and shippable.
- Within a story: tests first (they must fail), then implementation, then integration.
- Format each task: `- [ ] T### [P?] [US#] <action> in <exact file path>` where `[P]` means it can run in parallel (different files, no dependency).
- Put setup and shared foundation tasks in Phase 1/2 before stories.
- Each task is one reviewable commit. Each phase ends with a checkpoint: how to verify.
- Note `[NEEDS CLARIFICATION]` items from the spec as blockers; do not invent answers.

Output: the tasks file content, then a coverage table `Requirement -> Task IDs`, then blockers.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
