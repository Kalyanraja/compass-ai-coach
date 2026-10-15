---
description: "Upgrade one dependency safely with baseline, release-note review and verification"
argument-hint: "<package> <from> <to>"
---
<!-- practice: P1 pr-slicing -->

Upgrade $ARGUMENTS.

1. Baseline build + tests.
2. Read release notes / migration guide between versions (ask the human to paste them if unreachable); list breaking changes that affect this repo with file refs.
3. Update via the package manager only, from the approved registry.
4. Fix breakages in small groups, testing after each.
5. Compare final results with baseline. One dependency per PR.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
