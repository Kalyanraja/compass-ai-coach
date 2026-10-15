---
description: "Explain code for onboarding: purpose, flow, dependencies, risks, where to change"
argument-hint: "<file / symbol>"
---
<!-- practice: P5 context-pack -->

Explain $ARGUMENTS for an engineer new to this codebase. Read-only.

Cover with file:line: purpose (2 sentences), main flow (numbered), inputs/outputs/side effects, callers and dependencies, invariants, risky areas, test coverage, and "to change X start at Y". Mark inferences as (inferred). Under 400 words.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
