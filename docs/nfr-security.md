# NFRs, security and operational model

## NFR checklist

| Area | Status in the prototype | Path to production |
|---|---|---|
| **Scalability** | Single process, SQLite, ThreadingHTTPServer. 37 personas and 296 engineer-weeks per table. Aggregation is O(engineers x weeks) in memory. | Same modules behind an approved app server. Swap SQLite for the enterprise database. Precompute weekly aggregates in a batch job. The engine is stateless per request and scales horizontally. |
| **Performance** | Measured locally (median of 10): coaching request about 6 ms, team insights about 10 ms, org insights about 46 ms. Full eval and the 34 tests each finish in under 1 s. | Cache team aggregates per week (data changes weekly). |
| **Security** | HMAC-signed sessions with 8-hour expiry. Role checks on every endpoint. Engineer identity only from the session. Path-traversal guard on kit files. Request size limit (1 MB). JSON-only API. CSP, nosniff and no-referrer headers. All UI output escaped. Binds to 127.0.0.1. | Enterprise SSO (OIDC/SAML) replaces the demo picker. TLS. Secrets in the enterprise vault. Threat model review. |
| **Privacy** | Separate private store. k = 5 suppression. Below-threshold folding. Differencing protection. No ids in manager output. Prompt text never persisted. Audit without ids or content. Engineer "delete my data". | Data protection impact assessment. Retention policy, for example 90 days for feedback. Works council and HR review where required. |
| **Compliance** | Synthetic data only. Schema allow-list. PII, code and free-text scans. No-ranking API check (`python -m compass compliance`). | Run compliance in CI against every data source. Authorized metadata exports only. |
| **Reliability and resilience** | Deterministic. No external calls. The optional LLM fails closed and silently falls back. Bad input returns 4xx with clear messages. Unexpected errors return a generic 500 without internals. | Health endpoint `/api/health` for probes. Restart policy. Read-only replica for aggregation. |
| **Operational readiness** | Access audit log, eval report, compliance report, reset command. | Ship the audit log to the SIEM. Dashboards for request rate and error rate (no content). Monthly practice review by the enablement team. |
| **Maintainability** | Rules, practices and thresholds are data in single modules. 34 tests. CI on Windows and Linux. | Practice and rule changes go through PR review with the eval gate (at least 80%). |
| **Adoption** | One-click start. Two interactions to a recommendation. Agent kit installs into any repo with one command. | Pilot with 2-3 volunteer teams; see [roadmap.md](roadmap.md). |

## Security considerations

- **Trust boundary:** the browser is untrusted. All authorization happens server-side.
- **Least privilege:** the aggregation module opens `signals.db` with `mode=ro` and has no code path to `private.db` (a test asserts this).
- **No secrets in the repo:** the signing key is random per process unless `COMPASS_SECRET` is set.
- **Input handling:** the prompt-coach text is capped at 20,000 characters and the Jira CSV at 500 KB. Text is never stored or logged. A sensitive-data scan warns about passwords, keys, emails, SSN-like and card-like numbers, connection strings and bearer tokens.
- **Supply chain:** zero third-party runtime dependencies. Vendored agent-kit material is static text with licenses recorded.
- **Demo sign-in:** the persona picker is for the hackathon only and is labeled as such in the UI.

## Operational model

| Role | Responsibility |
|---|---|
| AI enablement team (owner) | Maintains practices, rules, thresholds and the agent kit. Reviews the eval report on each change. Reviews aggregated opportunities monthly. |
| Platform team | Hosts the service and data feeds (authorized metadata only). Manages SSO. |
| Engineering managers | Act on team-level opportunities (sessions, repo files). Never request individual data. |
| Engineers | Own their coaching. Can dismiss, give feedback and delete their data. |
| Privacy / risk | Approves the data sources, k threshold and retention. Reviews the access audit. |

## Performance assumptions

Signals refresh weekly, so recommendations change weekly. Expected load is under one request per engineer per day, which is small.

## Workflow coach security boundaries

| Threat | Control | Test |
|---|---|---|
| Another website calls the local API (CSRF, DNS rebinding) | Host header must be loopback; Origin must match; POST requires `application/json`; `Sec-Fetch-Site` cross-site is refused | `Api.test_cross_origin_and_non_json_refused` |
| Reading outside the project | Allowed roots only; path traversal, symlinks, `.env`, keys and credential folders are refused | `Boundaries.*` |
| Command injection | Named templates, regex-validated arguments, no shell, paths confined, minimal environment | `Boundaries.test_command_injection_rejected`, `test_minimal_environment` |
| Runaway processes | Timeout, process-group kill, CPU and file-size limits (POSIX), output cap, cancel endpoint | `Timeouts.*` |
| Tampered scanner binary | SHA-256 recorded at approval and re-checked before every run | Devin session 2 tamper test |
| Prompt injection in project files | Fenced as untrusted data, flagged, cannot change settings | `UntrustedInput.*` |
| Secret leakage in exports | Redaction before preview with a list of what was redacted; a review checkbox is required before copy | `Redaction.*` |
| Over-claiming | Missing tool = not checked; malformed report = blocked; findings are candidates; "passed" is not a certification | `MissingToolsAndReports.*`, `CombinedSecrets.*` |
| Stale results | The cache is opt-in and its key covers sources, settings, rules and packs; stale entries are deleted | `Cache.*` |
| Jira token exposure | Token from an environment variable or session memory only; never written or logged; https host pinned | `Jira.*` |
