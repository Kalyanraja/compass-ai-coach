---
description: 'Documentation rules for Markdown docs, READMEs, ADRs, specs and plans.'
applyTo: '**/*.md,docs/**'
---
<!-- practice: P4 plan-then-implement -->

# Documentation rules
- Write for a new teammate: purpose first, then how to run, then details.
- Use headings, short paragraphs, numbered steps for procedures, tables for options.
- Every command shown must be copy-paste runnable and verified in this repo.
- Keep docs next to the code they describe; update docs in the same PR as the behavior change.
- Specs go in `docs/specs/YYYY-MM-DD-<topic>.md`; plans in `docs/plans/YYYY-MM-DD-<topic>.md`.
- Mark unknowns explicitly as `[NEEDS CLARIFICATION: ...]` instead of guessing.
- Use placeholders like `{{SERVICE_URL}}` instead of real hostnames, account IDs or names. No secrets or personal data.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
