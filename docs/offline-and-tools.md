# Offline operation, scanner preparation and egress testing

## What runs with no network at all

Everything mandatory works offline:
- Fact detection
- Questions
- Tool recommendation
- Work package, budgeter and redaction
- Built-in checks (secrets, risky patterns, OpenAPI)
- Approved test runs
- Report import
- Verdicts and lessons

Compass makes outbound calls only if you configure Jira or the optional LLM enhancer. Both are off by default.

## Preparing optional scanners (separate, approved step)

Install tools only through your enterprise process (for example, from your internal artifact repository). Then open **Setup > 5**, enter each path and click **Approve**. Compass records the path, version and SHA-256, and refuses to run a binary whose hash changed.

| Tool | Version verified with Compass | How Compass runs it | Network behavior |
|---|---|---|---|
| gitleaks | 8.30.1 | `gitleaks dir . --report-format json --report-path <temp> --redact --no-banner --exit-code 0` | None for directory scans |
| Semgrep CE | 1.181.0 | `semgrep scan --config compass_rules/semgrep-local.yaml --metrics off --disable-version-check --json --quiet .` | Local rules only. `--metrics off` and `SEMGREP_SEND_METRICS=off` are both set. Never `--config auto` or registry rules |
| Spectral | 6.17.0 | `spectral lint <spec> --ruleset compass_rules/spectral-local.yaml --format json --quiet` | The ruleset extends the bundled `spectral:oas`. Do not add URL `extends` for offline use |

These versions were run against the synthetic fixtures while building Compass. The raw outputs are in `tests/fixtures/reports/`, and the adapter tests parse them.

### Optional capabilities (not implemented as adapters)

Trivy, OSV-Scanner, Syft, Checkov, zizmor, MegaLinter, skill-scanner, Repomix, RTK, ast-grep, Ruff, Biome, Stryker, Schemathesis and axe-core are listed in the Tool catalog as inactive. Until an adapter is implemented and verified, Compass reports them as **not checked**. If your team adds one:
- **Trivy:** provision the DB separately and run with `--skip-db-update --offline-scan`. Record the DB date.
- **OSV-Scanner:** use its offline mode with a pre-downloaded local database. Record the DB date.
- **zizmor:** use offline mode; some audits need the GitHub API.
- **Never** fetch database updates during an offline run. Report scope and staleness with every result.

## Egress testing

Configuration flags are not proof of isolation. Compass ships an in-process egress test:
- `tests/test_workflow.py::BlockedNetwork` replaces socket connections so any non-loopback connection raises.
- It then runs a full journey: start, answer, recommend, package and checks.
- It also asserts that an outbound HTTPS call fails.

For an OS-level check on Windows, block outbound traffic for `python.exe` with Windows Defender Firewall (an outbound rule), start Compass, and run the three demos. Do this with your IT team's approval; do not weaken security settings to make a demo pass.

## Data retention

| Data | Where | Retention |
|---|---|---|
| Journeys (goal, answers, facts, evidence) | Memory | Session only, max 8 hours, **Delete this journey now** button |
| Settings (no secrets) | `var/settings.json` | Until you change them |
| Cache (off by default) | `var/cache/<project-hash>/` | Invalidated on any change. Cleared when you turn it off |
| Jira token | Environment variable or typed per session | Never written to disk or logs |
| Access audit | `var/access-audit.log` | Role, path, status only |
