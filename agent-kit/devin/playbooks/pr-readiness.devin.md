<!-- Suggested macro: !pr-readiness | practice: P2 pr-readiness-selfcheck; P6 verify-before-done -->
# PR Readiness Check

## Overview
Bring an existing branch to review-ready state and report READY / NOT READY with evidence. Devin fixes only mechanical readiness issues (lint, formatting, missing test for a clear behavior, debug leftovers) and reports everything else.

## What's Needed From User
- Repository and branch name: `{{REPO}}` / `{{BRANCH}}`
- Base branch (default `{{DEFAULT_BRANCH}}`)
- Ticket ID or link and the acceptance criteria (redacted)
- Confirmation of whether Devin may push commits to the branch

## Procedure
1. Check out `{{BRANCH}}` and fetch `{{DEFAULT_BRANCH}}`; compute the merge base.
2. Read `AGENTS.md` and any `.claude/skills/pr-readiness-selfcheck/SKILL.md` in the repo and follow their commands.
3. Run build, full tests and lint (`{{BUILD_CMD}}`, `{{TEST_CMD}}`, `{{LINT_CMD}}`); save the summary lines.
4. Read the full diff and fill the readiness checklist (size, tests per behavior change, secrets, debug leftovers, error handling, API/schema/config changes, docs, commit messages).
5. Fix only mechanical issues in separate small commits; rerun the checks after each.
6. Draft the PR description (What / Why / How / Testing / Risk and rollback / Follow-ups).
7. Push to `{{BRANCH}}` only if the user allowed it; open or update the PR as a draft; post the readiness report as a PR comment or in the session.

## Specifications
- A readiness report exists with each checklist item marked PASS / FAIL / N/A and a file:line reason.
- Test, lint and build results are quoted from runs in this session.
- The PR (if opened) is a draft, uses the repo template, and links the ticket.
- No commit contains secrets, PII or production data.

## Advice and Pointers
- Count changed lines excluding lockfiles and generated files; over {{MAX_PR_LINES}} lines means recommend slicing (see the PR slicing playbook) instead of fixing.
- If tests need services that are unavailable, report NOT VERIFIED rather than READY.
- Prefer the repo's own scripts from `AGENTS.md` over guessing commands.

## Forbidden Actions
- Do not merge, approve, force-push, rebase shared branches, or change branch protections.
- Do not delete, skip or weaken tests to get green.
- Do not change behavior beyond mechanical fixes without asking.
- Do not paste secrets, tokens, customer data or production data into the session, code, commits or PR.
