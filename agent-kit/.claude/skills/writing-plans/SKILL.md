---
name: writing-plans
description: Use when you have an approved spec, ticket or requirements for a multi-step change, before touching code. Produces a test-first implementation plan with exact files, interfaces, failing tests, verification commands and PR slicing that another engineer or agent can execute without guessing.
metadata:
  practice: P4 plan-then-implement
  source: adapted from obra/superpowers writing-plans (MIT) and github/spec-kit tasks template (MIT)
---

# Writing Plans

Write the plan for an engineer who knows the language but has never seen this codebase or this conversation. Record the decisions they cannot make alone.

Announce: "Using writing-plans to create the implementation plan."
Save to: `docs/plans/YYYY-MM-DD-<feature>.md` (team preference overrides).

## Steps
1. Read the spec/ticket fully. If it covers several independent subsystems, propose one plan per subsystem.
2. Map files first: which files are created or modified and what each is responsible for. Follow existing patterns.
3. Break work into tasks. A task is the smallest unit with its own test cycle that a reviewer could accept or reject on its own. Fold setup and docs into the task that needs them.
4. For each task write steps that are one action with a checkable result.
5. Self-review (below), fix gaps inline, then hand off.

## Plan header
```markdown
# <Feature> Implementation Plan
Goal: <one sentence>
Spec: <path or ticket>
Architecture: <2-3 sentences>
Global constraints: <versions, dependency limits, naming rules; copied exactly from spec>
Review focus: <up to 5 inputs or failure modes the spec implies but no test covers yet, each mapped to the task that adds its test>
PR slicing: <which tasks ship together; each PR under {{MAX_PR_LINES}} lines>
```

## Task format
```markdown
### Task N: <component>
Files: Create `path` / Modify `path:lines` / Test `path`
Interfaces: Consumes <exact signatures from earlier tasks> / Produces <exact signatures later tasks use>
- [ ] Step 1: Write failing test `<test name>` asserting <literal expected values>
- [ ] Step 2: Run `<single test command>` - expect FAIL with "<reason>"
- [ ] Step 3: Implement `<signature>` in `<file>` (one line on approach if the test leaves a choice)
- [ ] Step 4: Run `<single test command>` then `{{TEST_CMD}}` - expect PASS
- [ ] Step 5: Commit `<type>: <message>`
```

## What a step contains
- Test step: test name and assertions with the spec's exact values.
- Code step: exact signature, file, and pinned values. No full bodies unless the algorithm is not determined by the test.
- Verification step: command and the output that means pass.
- Never write "TBD", "handle edge cases", "add validation", or "write tests for the above". Those decide nothing.

## Self-review checklist
- [ ] Every spec requirement maps to a task (list gaps and add tasks)
- [ ] Every step lets the implementer write exactly one reasonable thing
- [ ] Names and types are consistent across tasks
- [ ] Review focus items each have a test in an owning task
- [ ] Plan is shorter than the code it describes (signatures, not transcripts)

## Handoff
Link the plan and ask the human to review it and choose: implement in this session (`executing-plans`) or task by task with review gates. Do not start implementing until they approve.

## Stop and ask when
- The spec has unresolved `[NEEDS CLARIFICATION]` items that change design.
- The plan requires schema changes, new dependencies, or security-sensitive changes not in the spec.

## Safety
- No secrets, PII or production data in plans or example values; use synthetic values and `{{PLACEHOLDERS}}`.
- Every task ends with a verification command; a human reviews before merge.
