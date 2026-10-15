---
description: "Build or refresh the repo context pack (AGENTS.md) from verified repo facts"
argument-hint: "[areas to emphasize]"
---
<!-- practice: P5 context-pack -->

Use the `context-pack` skill (Part A). Emphasis: $ARGUMENTS.

Inspect build/CI/test/lint config, verify commands by running cheap ones, fill AGENTS.md placeholders with verified facts only, keep CLAUDE.md as `@AGENTS.md` plus Claude notes, keep copilot-instructions.md short. Output: changed files, verified-facts table, health check table, remaining placeholders.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
