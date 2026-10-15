---
description: "Refactor without changing behavior: pin with tests, small steps, verify each"
argument-hint: "<target> <goal>"
---
<!-- practice: P1 pr-slicing -->

Refactor: $ARGUMENTS

1. Ensure behavior is pinned (add characterization tests if needed; they must pass on current code).
2. List small mechanical steps.
3. Apply one step at a time; run tests after each.
4. Full suite + lint at the end.
No behavior changes, no bug fixes mixed in (list bugs separately). Keep the diff under {{MAX_PR_LINES}} lines.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
