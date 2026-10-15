---
description: "Turn a story or spec into a test plan mapped to test levels"
argument-hint: "<story text or spec path>"
---
<!-- practice: P3 test-first-acceptance -->

Create a test plan for: $ARGUMENTS

Restate acceptance criteria as Given/When/Then, choose the cheapest test level for each, add edge cases (empty, null, boundaries, invalid, permissions, dependency failures), list synthetic data needs, and output a table: ID | Scenario | Level | Test name | File | Data. List open questions. No code yet.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
