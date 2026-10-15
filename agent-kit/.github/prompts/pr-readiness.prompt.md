---
description: 'Run the PR readiness self-check on the current branch and produce a pass/fail report with evidence before requesting review.'
argument-hint: 'base branch (default main) and ticket ID'
agent: 'agent'
---
<!-- practice: P2 pr-readiness-selfcheck -->

You are preparing this branch for human code review. Do not open, merge or push anything.

Inputs: base branch `${input:base:main}`, ticket `${input:ticket:TICKET-ID}`.

Steps:
1. Run `git diff --stat ${input:base:main}...HEAD` and `git log --oneline ${input:base:main}..HEAD`. Summarize the change in 2 sentences.
2. Size check: count changed lines excluding lockfiles and generated files. If over {{MAX_PR_LINES}} or more than one concern, recommend a split (use `/slice-pr`).
3. Run the full test suite (`{{TEST_CMD}}`), the linter (`{{LINT_CMD}}`) and the build (`{{BUILD_CMD}}`). Quote the summary line of each. Do not claim a pass you did not see.
4. Read the full diff and check each item below. Mark PASS, FAIL or N/A with a file:line reason.
5. Stop and ask if any FAIL needs a product or security decision.

Checklist:
- [ ] Every behavior change has a test that would fail without it
- [ ] Tests, lint and build pass (evidence quoted)
- [ ] No secrets, tokens, PII or production data in the diff
- [ ] No debug prints, commented-out code, stray TODOs, unrelated edits
- [ ] Error handling and input validation on new paths
- [ ] Public API, schema or config changes are flagged and backward compatible (or migration noted)
- [ ] New dependencies justified
- [ ] Docs/README/changelog updated if behavior changed
- [ ] PR is one concern and under the size target

Output format:
```
## PR Readiness: READY | NOT READY
Summary: <2 sentences>
Size: <files> files, +<adds>/-<dels> (target {{MAX_PR_LINES}})
Evidence:
- tests: <command> -> <summary line>
- lint: <command> -> <summary line>
- build: <command> -> <summary line>
Checklist: <table: item | PASS/FAIL/N-A | reason>
Blocking fixes: <numbered list or "none">
Suggested PR description: <use /pr-description format>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
