---
description: "Measure, root-cause and fix a flaky test; prove it with repeated runs"
argument-hint: "<test id> [failure excerpt]"
---
<!-- practice: P8 flaky-test-hardening -->

Use the `flaky-test-hardening` skill for: $ARGUMENTS

Baseline fail rate first (isolated, suite, parallel). Classify the nondeterminism with evidence. Fix at the source. Never add sleeps, retries, longer timeouts, force-clicks or skips as the fix. Rerun about 3x the baseline failure interval and report before/after counts.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
