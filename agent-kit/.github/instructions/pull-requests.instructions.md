---
description: 'Pull request conventions: small single-concern PRs, required description sections, readiness self-check and review priorities.'
applyTo: '**'
excludeAgent: 'cloud-agent'
---
<!-- practice: P1 pr-slicing; P2 pr-readiness-selfcheck -->

# Pull request rules

## Size and scope
- One concern per PR. Target under {{MAX_PR_LINES}} changed lines (excluding generated files and lockfiles).
- Separate mechanical changes (renames, formatting, moves) from behavior changes.
- Ship in order: refactor (no behavior change) > new behavior behind tests > cleanup.

## Description must include
1. What changed and why (link {{TICKET_SYSTEM}} ticket).
2. How it was tested: exact commands and results; manual steps if any.
3. Risk and rollback: what could break, how to revert, feature flag if used.
4. Screenshots or recordings for UI changes.
5. Follow-ups intentionally left out.

## Before requesting review
- Re-read the full diff. Remove debug code, commented-out code, stray TODOs and unrelated changes.
- Tests added or updated for every behavior change; full suite and linters pass.
- No secrets, PII or production data anywhere in the diff.

## When reviewing
- Critical (block): security, correctness, data loss, breaking API changes.
- Important (discuss): missing tests, performance, design deviations.
- Suggestion (non-blocking): naming, readability.
- Cite file:line, explain impact, propose a fix. Acknowledge what is done well.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
