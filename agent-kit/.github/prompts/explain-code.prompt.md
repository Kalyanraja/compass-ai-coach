---
description: 'Explain selected code or a module for onboarding: purpose, flow, dependencies, risks, and where to change it safely. Read-only.'
argument-hint: 'file, class, or selection'
agent: 'ask'
---
<!-- practice: P5 context-pack -->

Explain ${input:target:the selected code (#selection) or file}. Audience: an engineer new to this codebase. Do not modify anything.

Cover, citing file:line:
1. Purpose in 2 sentences.
2. Main flow as numbered steps (entry point to output/side effects).
3. Inputs, outputs, side effects (DB, network, files, events).
4. Dependencies and who calls it (#usages).
5. Invariants and assumptions the code relies on.
6. Risky areas: error handling gaps, concurrency, performance, security-sensitive lines.
7. Where tests live and what they cover; what is untested.
8. "If you need to change X, start at Y" for the 2-3 most likely changes.

Mark anything you inferred rather than read as "(inferred)". Keep it under 400 words unless asked.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
