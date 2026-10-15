---
name: pr-readiness-selfcheck
description: Use before opening or updating a pull request, or when asked "is this ready for review?". Runs build, tests and lint, inspects the full diff against a readiness checklist (size, tests, secrets, hygiene, docs, risk), and outputs a READY / NOT READY report with evidence plus a draft PR description.
metadata:
  practice: P2 pr-readiness-selfcheck
  source: original Compass content; checklist informed by github/awesome-copilot code-review-generic (MIT) and obra/superpowers finishing-a-development-branch (MIT)
---

# PR Readiness Self-Check

Catch what a reviewer would catch, before they see it.

## Steps
1. Identify base: `git merge-base origin/{{DEFAULT_BRANCH}} HEAD`. Show `git diff --stat` and `git log --oneline` for the range.
2. Run and quote: `{{BUILD_CMD}}`, `{{TEST_CMD}}`, `{{LINT_CMD}}` (and `{{E2E_CMD}}` if UI changed). Use `verification-before-completion` rules.
3. Read the entire diff, file by file. Fill the checklist with PASS / FAIL / N/A and a file:line reason.
4. If size or scope fails, run `pr-slicing`.
5. Draft the PR description.
6. Report. Do not push, open, or merge unless the human asks; never merge.

## Checklist
| # | Check |
|---|---|
| 1 | One concern; under {{MAX_PR_LINES}} changed lines (excluding generated/lockfiles) |
| 2 | Every behavior change has a test that fails without it |
| 3 | Build, tests and lint pass now (output quoted) |
| 4 | No secrets, tokens, connection strings, PII or production data |
| 5 | No debug output, commented-out code, stray TODOs, unrelated formatting |
| 6 | New code paths validate input and handle errors |
| 7 | API, schema, config or dependency changes are flagged, compatible, with migration/rollback |
| 8 | Docs, README, changelog updated if behavior changed |
| 9 | Commit messages follow {{COMMIT_STYLE}} and reference {{TICKET_ID}} |
| 10 | UI changes have screenshots; risky changes have a flag or rollback plan |

## Output
```
## PR Readiness: READY | NOT READY
Range: <base>..<head>, <files> files, +<a>/-<d>
Evidence:
- build: `<cmd>` -> <result>
- tests: `<cmd>` -> <passed/failed/skipped>
- lint: `<cmd>` -> <result>
Checklist: | # | Result | Reason |
Blocking: <numbered fixes or none>
Draft PR description: What / Why / How / Testing / Risk and rollback / Follow-ups
```

## Stop and ask when
- A check fails for a reason that needs a product, security or architecture decision.
- Tests cannot run locally (missing services or credentials): report NOT VERIFIED, never READY.

## Safety
- If the diff contains something that looks like a secret, stop, report the location (first 4 chars only), and do not commit or push.
- A human reviews and merges every PR.
