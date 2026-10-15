---
description: "Systematic bug investigation: reproduce, evidence, one hypothesis at a time"
argument-hint: "<symptom / error / failing test>"
---
<!-- practice: P6 verify-before-done -->

Use the `systematic-debugging` skill for: $ARGUMENTS

No fix until the root cause is shown with evidence. Report: reproduction command and output, evidence, root cause (file:line), fix with regression test, verification results. Stop after 3 failed fix attempts and discuss the design.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
