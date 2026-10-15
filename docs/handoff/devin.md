# Devin (web) instructions

Devin works in its own Linux VM with the repository connected. It can reach your approved artifact repository (JFrog Artifactory), so it can install the optional scanners the approved way. There is no MCP; paste these prompts into a new Devin session. Run them in order, one session each, or as one playbook.

> Create a Devin Playbook from this file (Settings > Playbooks) and attach it with its macro, for example `!compass-verify`.

---

## Session 1: independent verification (no installs)

```
## Overview
Independently verify the Compass repository end to end on Linux and report evidence. Do not change application code in this session.

## Procedure
1. Read README.md, AGENTS.md, docs/workflow-coach.md and docs/IMPLEMENTATION-REPORT.md.
2. Check Python: python3 --version (needs 3.9+). Use the standard library only; do not pip install anything for the app.
3. Run and capture full output:
   - python3 -m unittest discover -s tests -t . -v
   - python3 -m compass eval
   - python3 -m compass compliance
   - python3 -m compass doctor
4. Start the server: python3 -m compass --no-browser --reset & then sleep 3.
5. With curl against http://127.0.0.1:8765, exercise the Workflow coach API for the three demos (see tests/test_workflow.py class Demos for the exact calls):
   a. POST /api/session {"role":"engineer","subject":"E-ATL-01"} -> token
   b. POST /api/setup {"allow_test_execution": true}
   c. Demo 1: POST /api/wf/start with goal = contents of examples/java-orders-api/docs/stories/ORD-12.md, project = absolute path of examples/java-orders-api, workflow feature-api; then POST /api/wf/checks; then GET /api/wf/state and record verdict.overall.
   d. Demo 2: start uat-defect on examples/py-login-service; POST /api/wf/verify-fix with diff = fixes/fix-no-repro.diff and approve_tests true; record verdict; repeat with fixes/fix-with-repro.diff.
   e. Demo 3: start test-creation on examples/py-login-service; POST /api/wf/checks with approve_tests true; record the checks tests.detects_defect and tests.weak_suite_flagged.
6. Confirm the project files under examples/ are byte-identical before and after (git status must be clean).
7. Try the negative cases and confirm they are refused: a POST with Content-Type text/plain (415), a request with Origin: http://evil.example (403), GET /api/me/coaching with a manager token (403), POST /api/wf/start with project /etc (400).

## Specifications
- Expected: all tests OK; eval 25/25; compliance all pass.
- Expected verdicts: Demo 1 "Not accepted yet"; Demo 2 no-repro "Not accepted: no reproduction evidence"; Demo 2 with-repro "Accepted with evidence"; Demo 3 detects_defect passed and weak_suite_flagged failed.
- Any difference from the expected results is a finding: report it with the exact command and output.

## Forbidden actions
- Do not push to main. Do not edit tests to make them pass.
- Do not add company names, internal URLs or real data to this public repository.

## Required from user
- Repository connected in Devin.
```

---

## Session 2: install approved scanners from Artifactory and verify the real adapters

```
## Overview
Install gitleaks, Semgrep CE and Spectral from our approved JFrog Artifactory remotes (not from the public internet), approve them in Compass, and verify the real-scanner adapters. This proves the optional security checks work with approved binaries.

## Procedure
1. Use only Artifactory remotes that our organization configured (PyPI remote for semgrep, npm remote for @stoplight/spectral-cli, generic/GitHub-releases remote for the gitleaks binary). Pin these versions, which Compass was verified against: gitleaks 8.30.1, semgrep 1.181.0, @stoplight/spectral-cli 6.17.0. If a pinned version is unavailable, use the closest approved version and note it.
2. Install into a scratch folder outside the repo (for example ~/tools). Do not commit binaries.
3. Start Compass (python3 -m compass --no-browser) and approve each tool through the API, which records path, version and SHA-256:
   POST /api/scanners/approve {"name":"gitleaks","path":"<abs path>"} (repeat for semgrep and spectral).
4. Run checks on both fixtures (feature-api on examples/java-orders-api, test-creation on examples/py-login-service) via POST /api/wf/checks and record scanner.gitleaks, scanner.semgrep and scanner.spectral results.
5. Compare the findings with tests/fixtures/reports/*.json (which were produced by the same versions) and with docs/measurements.md.
6. Tamper test: copy a scanner binary, approve the copy, then modify the copy (append a byte) and confirm Compass refuses it with a SHA-256 mismatch.
7. Write docs/verification/devin-<date>.md with versions, SHA-256 values, commands, outputs and differences. Open a PR with only that file.

## Specifications
- Semgrep must run with the local rules file only and --metrics off (see compass/workflow/runner.py). Never use --config auto.
- Spectral must use compass_rules/spectral-local.yaml (no URL extends).
- Findings stay "candidate"; do not describe them as confirmed vulnerabilities.

## Forbidden actions
- No downloads from the public internet if Artifactory has the package. No curl | sh installers.
- Do not change compass_rules/ or the runner's argument templates.
- Do not commit tool binaries or caches.

## Required from user
- Which Artifactory remotes are approved, and credentials configured in Devin's environment (never in the repo).
```

---

## Session 3 (optional): implement one optional adapter

```
## Overview
Add one optional capability as a real, tested adapter, following the existing pattern. Candidate: OSV-Scanner in offline mode (dependency vulnerability matching) for the security-review stage.

## Procedure
1. Read compass/workflow/runner.py (TEMPLATES, discover, resolve_exe), compass/workflow/evidence.py (check, finding, parse_* functions) and compass/workflow/journey.py (run_checks).
2. Install OSV-Scanner from Artifactory and prepare its offline database in a separate step. Record the database date.
3. Add a template "osv-offline" using the verified offline flags (check the official docs for the installed version), a parser parse_osv() that normalizes results to findings, and a check "scanner.osv" in run_checks that reports the DB date and scope in coverage. It must be "not-checked" when not installed or not approved.
4. Add tests with a recorded JSON output fixture (real output from a synthetic lockfile) and a malformed-report test.
5. Update catalog/tools.json (integration_status runtime-adapter-candidate, still enabled false until approved), docs/offline-and-tools.md and docs/third-party/source-manifest.md (run scripts/build_source_manifest.py).

## Specifications
- All existing tests still pass; new tests pass; never fetch DB updates during a check.

## Forbidden actions
- Do not mark the tool enabled or approved in committed files.
```
