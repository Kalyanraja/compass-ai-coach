# Hand-off: finishing and verifying Compass with Devin, Copilot and Claude Code

All three assistants work **without MCP servers and without API keys**. Everything they need is in this repository: code, tests, docs, fixtures and the agent kit.

## Order of work

| Step | Who | Where | Goal | Instructions |
|---|---|---|---|---|
| 1 | **Devin** (web) | Devin's VM, repository connected | Independent verification on Linux, plus real scanners installed from your approved artifact repository (JFrog Artifactory) | [devin.md](devin.md) |
| 2 | **GitHub Copilot** (VS Code, office laptop) | Your Windows laptop | Windows run-through, organizer sample-data mapping, office work (deck, submission text, demo recording plan) | [copilot.md](copilot.md) |
| 3 | **Claude Code** (VS Code) | Your laptop | Independent code and security review, stretch workflow, final pre-submission check | [claude.md](claude.md) |

## Ground rules for every assistant

1. **Two repositories.** The public GitHub repository stays generic: no company names, no internal URLs, no organizer documents, no real data. Anything specific to your organization (the organizers' sample data, team names, internal Jira URL) goes **only** into the designated internal hackathon repository.
2. **Synthetic data only** for the demo. Never paste production data, customer data, credentials or real employee information into any assistant.
3. **Evidence over claims.** Every "done" needs the exact command and its output. Use `python -m unittest discover -s tests -t . -v`, `python -m compass eval` and `python -m compass compliance`.
4. **Don't weaken the guardrails.** Leave these alone:
   - k-anonymity (`COMPASS_K_ANON`, minimum 5)
   - the Host/Origin checks
   - the scanner hash check
   - the "no shell" runner
   - the prohibition on ranking people
5. **Human review before merge.** Assistants open PRs or produce diffs; a person merges.
6. **Keep the pass rate honest.** If a change drops the eval below 80% or any test fails, fix it or report it. Never edit a test to make it pass without explaining why the test was wrong.

## What "end to end" means for the hackathon submission

| Deliverable | Where it is | Who finalizes |
|---|---|---|
| Working source code | this repo | all |
| Architecture diagram | `docs/architecture.md`, in-app "How it works", deck slide | Copilot updates the deck if anything changes |
| Test results | `reports/eval-report.md`, test output, `docs/measurements.md` | Devin re-runs and attaches output |
| Five-minute demo recording | follow `docs/demo-script.md` | you, with Copilot's script help |
| Setup instructions | `docs/setup.md`, README | Copilot verifies on Windows |
| Presentation | `docs/presentation/Compass-Hackathon.pptx` | Copilot adds team names and final screenshots in the internal copy |
