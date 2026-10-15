# Implementation report: Workflow coach extension

This report follows the requested format: files changed, working flows, checks executed, disabled or blocked items, upstream revisions and licenses, measured context changes, and the run/package command.

## Files added or changed

| Area | Files |
|---|---|
| Workflow engine | `compass/workflow/__init__.py`, `workspace.py` (safe reader + facts), `coach.py` (packs, questions, tool policy), `context.py` (budgeter), `package.py` (work package, redaction, untrusted fencing), `evidence.py` (model, readers, built-in checks, diff apply, verdict inputs), `runner.py` (safe command templates), `cache.py`, `journey.py` |
| Settings, Jira, doctor | `compass/settings.py`, `compass/jira_client.py`, `compass/doctor.py` |
| API | `compass/api_workflow.py` (new routes), `compass/server.py` (Host/Origin/Content-Type checks, deep link, route registration), `compass/__main__.py` (`--project`, `--jira`, `doctor`) |
| Existing behavior adjusted | `compass/prompt_coach.py`, `compass/engine.py`, `compass/practices.py`, `eval/scenarios.json`: office work now routes to Copilot / Claude Code, which are approved for it |
| Data | `workflows/packs/*.json` (3 working, 1 shared stage, 3 planned), `catalog/capabilities.json`, `catalog/tools.json` (37 records), `catalog/schema/tool-registry.schema.json`, `compass_rules/semgrep-local.yaml`, `compass_rules/spectral-local.yaml` |
| UI | `web/workflow.js` (Workflow coach, Setup, Tool catalog), `web/app.js` (router with query, nav, setup banner, deep links), `web/styles.css`, `web/index.html` |
| Fixtures | `examples/java-orders-api`, `examples/py-login-service` (+ `compass-fixture.json`), `examples/legacy-batch-unknown`, `examples/TESTER-NOTES.md`, `tests/fixtures/reports/*` (real gitleaks/Semgrep/Spectral output + hand-written JUnit), `tests/fixtures/scan-targets/*` |
| Tests | `tests/test_workflow.py` (40 tests) |
| Docs | `docs/workflow-coach.md`, `docs/offline-and-tools.md`, `docs/jira.md`, `docs/measurements.md`, `docs/third-party/source-manifest.md`, `docs/handoff/*`, this report, plus updates to README and the existing docs |
| Launchers and agents | `Start-Coach.bat` (folder and Jira arguments, drag-and-drop), root `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (for developing Compass itself), `scripts/build_source_manifest.py` |

## Working flows

1. **Feature / API:** Facts come from the pom, spec and standard, each with file:line. Questions cover auth, errors and header. The tool comes from policy. The package keeps the spec and standard in full. Checks run: OpenAPI header, 400 and auth (built-in or Spectral), test report import, secrets. Verdict: **Not accepted yet**, with three failing spec criteria and a failing recorded test.
2. **UAT defect:** Questions cover expected vs actual, repro and what changed. `verify-fix` runs tests on temp copies, first with test changes only and then with the full fix.
   - Fix without a test: **Not accepted: no reproduction evidence**. AC-DEF-1 fails, and the coach names the existing test that already reproduces the defect.
   - Fix with a regression test: **Accepted with evidence**.
   - Importing only an "after" report with no before evidence: **Not accepted: no reproduction evidence**.
3. **Test creation:** an approved run of the fixture's tests shows `test_wrong_password_same_length_is_rejected` detecting the seeded defect SD-1 (`auth.py:35`), flags `tests.test_login_smoke` as passing on broken code, and reports the security candidates (synthetic credential at `config/settings.ini:7`, `shell=True` at `login_service/admin.py:8`).
4. **Security review (shared stage):** built-in secret and pattern checks always run. gitleaks, Semgrep and Spectral run only when approved. Findings are candidates.
5. **Setup:** eight questions saved to `var/settings.json`, with no secrets. Scanner approval records path, version and SHA-256.
6. **Jira:** off by default; read-only GET to one configured https host; token from env or per session. CSV import and paste remain available.
7. **Automated start:** `Start-Coach.bat <folder> [JIRA-KEY]` opens the Workflow coach on that project and adds the folder to allowed roots. `python -m compass doctor` checks the setup.

## Checks executed (exact)

- `python -m unittest discover -s tests -t . -v`: 74 tests, OK.
- `python -m compass eval`: 25/25 scenarios, 16/16 prompt routing, 5/5 context pairs, 37/37 seeded personas.
- `python -m compass compliance`: all checks pass.
- Playwright walkthrough of all three demos plus Setup and Tool catalog pages: no console errors; verdicts as listed above.
- Real scanners: gitleaks 8.30.1, Semgrep 1.181.0 and Spectral 6.17.0 were discovered, approved (hash recorded) and run through `run_checks` on both fixtures; see [measurements.md](measurements.md).

## Disabled or blocked, with reasons

| Item | State | Reason |
|---|---|---|
| PR review, documentation/onboarding, release/config workflows | Planned (disabled in UI, refused by API) | Not implemented; registered as extensions only |
| Trivy, OSV-Scanner, Syft, Checkov, zizmor, MegaLinter, skill-scanner, Repomix, RTK, ast-grep, Ruff, Biome, Stryker, Schemathesis, axe-core, promptfoo, llama.cpp, WebLLM, LLMLingua | Inactive optional capabilities | No adapter implemented or verified yet; never reported as passing |
| ripgrep adapter | Not implemented | Python search is used; listed as a candidate |
| OS-enforced sandbox | Not available | Test runs need explicit approval and are labeled "no sandbox"; security review of untrusted code stays static |
| Maven / npm / dotnet test templates | Available only if the tool is on PATH and the run is approved | Not executed in the build sandbox |
| LLM enhancer | Off | Optional; `COMPASS_LLM_URL` to an approved endpoint |
| Copilot / Claude / Devin integration | Copy/export only | No MCP and no API by design; nothing is sent automatically |
| `Start-Coach.bat`, `install-kit.bat` | Not executed here | No Windows in the build sandbox; CI runs Python tests on `windows-latest` |

## Selected upstream revisions and licenses

See [third-party/source-manifest.md](third-party/source-manifest.md) for all 37. The ones actually used at runtime or as adapted content:

| Upstream | Reviewed commit | License |
|---|---|---|
| gitleaks | `b58d3f102cf3` (v8.30.1) | MIT |
| semgrep | `51602ad27f09` (v1.181.0) | LGPL-2.1 (engine); registry rules not used |
| spectral | `95ab37eeea1f` (v6.17.0) | Apache-2.0 |
| obra/superpowers | `bb92a7774141` | MIT |
| github/awesome-copilot | `36e95dfda721` | MIT |
| github/spec-kit | `6e7348de375f` | MIT |
| microsoft/AI-Engineering-Coach | `8c78e96316a8` | MIT |
| OWASP/ASVS | cited only (5.0.0) | CC-BY-SA-4.0 |

## Measured context

See [measurements.md](measurements.md). Example: in a 386-file repository, a Deep package used about 15,145 estimated tokens (60,579 bytes) against about 454,230 (1,819,098 bytes) for a whole-repository paste. Lean and Balanced reported an overflow instead of dropping the two named files.

```python
# reproduce (from the repo root)
import os; os.environ["COMPASS_DATA_DIR"] = "/tmp/compass-measure"
from compass import settings; from compass.workflow import journey
settings.save({"allowed_roots": [os.getcwd()]})
j = journey.start("m:1", "Add an optional 'reason' field to POST /api/me/feedback in compass/server.py. Add tests in tests/test_acceptance.py.", os.getcwd(), "feature-api")
p = journey.build_package(j["id"], "m:1", "deep"); print(p["size"], p["comparison"]["whole_project_paste"])
```

## Run and package

```
Start-Coach.bat                         (Windows)
python -m compass                       (any OS)
python -m compass --project <folder> --jira ABC-123
python -m unittest discover -s tests -t . -v
git archive --format=zip -o compass-ai-coach.zip HEAD    (package for hand-off)
```
