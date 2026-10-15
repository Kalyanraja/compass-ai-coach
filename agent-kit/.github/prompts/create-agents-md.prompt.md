---
description: 'Build a context pack for this repo: fill AGENTS.md placeholders from real repo facts (commands, structure, conventions) so every agent starts with correct context.'
argument-hint: 'optional: areas to emphasize'
agent: 'agent'
---
<!-- practice: P5 context-pack -->

Create or update `AGENTS.md` at the repo root (and keep `.github/copilot-instructions.md` consistent) using only facts you can verify in this repository.

Steps:
1. Inspect: build files (`pom.xml`, `build.gradle`, `*.csproj`, `package.json`, `pyproject.toml`), CI workflows, README, existing docs, test folders, linter configs.
2. Extract and verify commands: install, build, full test, single test, lint, E2E. Run the cheap ones (lint, a single test) to confirm they work; note any you could not verify.
3. Describe structure: key directories and what lives there (5-10 lines).
4. Infer conventions from code (naming, error handling, logging, test style). Cite one example file for each.
5. Fill `{{PLACEHOLDERS}}` in AGENTS.md. Leave `{{...}}` in place and list it if you cannot verify a value. Do not invent.
6. Keep AGENTS.md under 200 lines and copilot-instructions.md under 4,000 characters. Move long detail to docs and link it.

Never include secrets, internal URLs, personal names or customer data. Use placeholders.

Output: the updated files, then a table `Item | Value | Verified how`, then remaining placeholders.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
