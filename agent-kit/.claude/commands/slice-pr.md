---
description: "Split a large branch or change into small, independently reviewable PRs"
argument-hint: "[base-branch] [max-lines]"
---
<!-- practice: P1 pr-slicing -->

Use the `pr-slicing` skill. Arguments: $ARGUMENTS (defaults: base `{{DEFAULT_BRANCH}}`, max {{MAX_PR_LINES}} lines).

Produce the slicing table (title, type, files, lines, depends on, tests), suggested git commands for the human, and requirement coverage. Do not rewrite history or push.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
