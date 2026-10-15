---
description: "Strict read-only review of your own changes before anyone else sees them"
argument-hint: "[focus area]"
---
<!-- practice: P2 pr-readiness-selfcheck -->

Review the uncommitted and branch changes as a strict senior reviewer. Focus: $ARGUMENTS. Do not edit files.

Order: correctness > tests (would they fail without the change?) > security > design > readability.
Output: Strengths (file:line) / Issues table (Severity, File:line, Problem, Why, Fix) / Verdict. Do not invent issues. For a deeper independent review, delegate to the `code-reviewer` subagent.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
