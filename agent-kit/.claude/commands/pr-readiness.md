---
description: "Run the PR readiness self-check on this branch and report READY/NOT READY with evidence"
argument-hint: "[base-branch] [ticket-id]"
---
<!-- practice: P2 pr-readiness-selfcheck -->

Use the `pr-readiness-selfcheck` skill on the current branch.
Arguments: $ARGUMENTS (base branch defaults to `{{DEFAULT_BRANCH}}`).

1. Show the diff stat and commit list for the range.
2. Run build, full tests and lint; quote each summary line.
3. Walk the 10-item readiness checklist with PASS/FAIL/N-A and file:line reasons.
4. If too large or mixed, propose slices (`pr-slicing`).
5. Output the readiness report and a draft PR description. Do not push or open the PR unless asked.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
