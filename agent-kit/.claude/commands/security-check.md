---
description: "Read-only security review of changes or files (OWASP-style)"
argument-hint: "[files or scope]"
---
<!-- practice: P2 pr-readiness-selfcheck -->

Review $ARGUMENTS (default: current branch diff) for security issues. Do not edit.

Trace sources (HTTP, messages, files, DB) to sinks (SQL, shell, paths, HTML, logs, outbound calls). Check secrets, injection, authZ/IDOR, validation/encoding, sensitive data exposure, crypto/TLS, dependencies, error leakage.
Output table: Severity | Category | File:line | Source -> sink | Issue | Fix. Never print a found secret; show location and first 4 chars only. This complements, not replaces, the team's security tools and review.

Safety: no secrets, PII or production data in prompts, files or output. Run the relevant tests and quote results before claiming success. A human reviews before merge; never merge, force-push or deploy.
