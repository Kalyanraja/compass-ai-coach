---
description: 'Security review of the selected code or branch diff against OWASP-style risks. Read-only; reports findings with severity and fixes.'
argument-hint: 'files, diff, or feature to review'
agent: 'ask'
---
<!-- practice: P2 pr-readiness-selfcheck -->

Review ${input:scope:the current changes (#changes) or selected files} for security issues. Report only; do not edit. This does not replace the team's security tooling or review process.

Trace data from each entry point (HTTP, message, file, CLI, DB read) to each sink (SQL, shell, file path, HTML, logs, outbound calls).

Check:
- Secrets: hardcoded keys, tokens, passwords, connection strings; secrets in logs or error messages.
- Injection: SQL, command, LDAP, XPath, template, path traversal, deserialization.
- AuthN/AuthZ: missing or client-side-only checks, IDOR (access by ID without ownership check), privilege escalation.
- Input validation and output encoding; XSS.
- Sensitive data exposure: PII in logs, responses, URLs; missing masking.
- Crypto: home-grown crypto, weak algorithms, disabled TLS verification.
- Dependencies: new or outdated packages with known issues.
- Error handling that leaks internals.

Output:
```
| Severity | Category | File:line | Data flow (source -> sink) | Issue | Fix |
|---|---|---|---|---|---|
Severity: Critical | High | Medium | Low
Not checked / needs human or tool review: <list>
```
Never print a discovered secret in full; show only the first 4 characters and the location.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
