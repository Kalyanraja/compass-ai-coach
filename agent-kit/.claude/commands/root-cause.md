---
description: "Trace a bad value or error backward to its original trigger"
argument-hint: "<where the symptom appears>"
---
<!-- practice: P6 verify-before-done -->

Trace $ARGUMENTS backward using `.claude/skills/systematic-debugging/root-cause-tracing.md`.

Output: call chain (origin -> ... -> symptom with file:line), original trigger, fix at source, defense-in-depth checks per layer, regression test, confidence. If the trail ends, say where and what logging would reveal the next step.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
