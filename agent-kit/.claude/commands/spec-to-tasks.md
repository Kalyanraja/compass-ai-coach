---
description: "Convert an approved spec into an ordered, test-first task list"
argument-hint: "<spec path>"
---
<!-- practice: P4 plan-then-implement -->

Read the spec at $ARGUMENTS. Produce `docs/plans/<name>-tasks.md` with tasks formatted `- [ ] T### [P?] [US#] <action> in <path>`, grouped by user story in priority order, tests before implementation, a checkpoint per phase, and a coverage table requirement -> tasks. List unmapped requirements and `[NEEDS CLARIFICATION]` blockers. Do not implement.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
