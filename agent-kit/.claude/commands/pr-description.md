---
description: "Draft a PR description from the actual branch diff"
argument-hint: "[ticket-id] [base-branch]"
---
<!-- practice: P2 pr-readiness-selfcheck -->

Draft a PR description for the current branch. Arguments: $ARGUMENTS.

Read `git diff` and `git log` for the range against the base branch. Describe only what the diff shows. If tests were not run in this session write "Not run by agent".

Format: ## What / ## Why (ticket link) / ## How / ## Testing (commands + results) / ## Risk and rollback / ## Out of scope. Under 300 words.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
