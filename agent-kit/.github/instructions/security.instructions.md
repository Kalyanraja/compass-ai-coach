---
description: 'Secure-coding rules (OWASP-aligned) for application code, config and SQL: secrets, injection, authZ, input validation, logging, dependencies.'
applyTo: '**/*.java,**/*.kt,**/*.cs,**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.jsx,**/*.sql,**/*.go,**/*.yml,**/*.yaml,**/*.json,**/*.config,**/*.properties,**/*.env*'
---
<!-- practice: P2 pr-readiness-selfcheck -->

# Security rules

## Secrets and data
- Never hardcode secrets, keys, tokens, passwords or connection strings. Read them from the approved secret store or environment ({{SECRET_STORE}}).
- Never log secrets, tokens, full card or account numbers, or personal data. Mask identifiers.
- Never place production or customer data in code, tests, fixtures, prompts or commits.
- If you see something that looks like a secret in code or a diff, stop and flag it.

## Injection and input
- Use parameterized queries or the ORM's parameter binding. Never build SQL, shell commands, LDAP or XPath by string concatenation with input.
- Validate input at trust boundaries (type, length, range, allow-list). Reject, do not "fix", bad input.
- Encode output for its context (HTML, URL, JSON). Avoid `eval`, dynamic code execution and unsafe deserialization.
- Do not pass user input to file paths without canonicalizing and checking against an allowed base directory.

## Authentication and authorization
- Check authorization on every request server-side, per resource. Deny by default.
- Do not roll your own crypto, tokens or password hashing. Use the platform's vetted libraries.
- Keep TLS verification on. Never disable certificate checks, even in tests that hit real endpoints.

## Errors and dependencies
- Return generic errors to clients; log details server-side without sensitive data.
- Do not add dependencies without approval. Prefer maintained, widely used packages; pin versions.

## Escalate to a human
- Any change to authentication, authorization, crypto, secrets handling, data retention or deletion, or public API contracts.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
