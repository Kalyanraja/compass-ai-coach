# GitHub Copilot (VS Code) instructions

Copilot runs in VS Code on your office laptop with **no MCP servers**. Open the repository folder, then use Copilot Chat in **Agent mode**. The repository's `.github/copilot-instructions.md` and `AGENTS.md` load automatically. Copilot is also approved for office work, so it can help with the deck and the written submission.

Paste one prompt at a time. Ask Copilot to show its plan first and to paste command output as evidence.

---

## Task 1: Windows run-through and fixes

```
Goal: confirm Compass runs on this Windows laptop exactly as documented, and fix only real Windows-specific problems.

Steps (show me a plan first, then do them one by one, pasting the output of each command):
1. In a terminal at the repo root run: py -3 --version  (or python --version)
2. Run: py -3 -m unittest discover -s tests -t . -v   and   py -3 -m compass eval   and   py -3 -m compass doctor
3. Double-click Start-Coach.bat (or run it from the terminal). Confirm the browser opens http://127.0.0.1:8765/.
4. In the app: open Setup, keep the defaults, tick "allow test execution", Save. Then Workflow coach > run the three demo buttons end to end. Write down each final verdict.
5. Run: Start-Coach.bat "<full path to>\examples\py-login-service"   and confirm the Workflow coach opens with that project selected.
6. If anything fails, find the root cause (paths with spaces, backslashes, encoding, firewall prompt, py launcher) and propose the smallest fix with a test. Do not change behavior on Linux.

Constraints: standard library only; do not weaken any security check (Host/Origin check, runner argument validation, scanner hash check); do not edit tests just to make them pass.
Done when: all tests pass on Windows, the three demos give the verdicts in docs/measurements.md, and you list any fixes with evidence.
```

## Task 2: Map the organizers' sample data (internal repository only)

```
Goal: make Compass load the organizers' "Sample Usecase Data" instead of only the built-in synthetic generator, without breaking the existing synthetic data.

Context: compass/synth.py generates the synthetic dataset; compass/db.py loads it; compass/compliance.py enforces the column allowlist (no PII, no free text, no prompt content).
Steps:
1. Open the organizers' sample file. Save each relevant sheet as CSV (File > Save As > CSV) into data/organizer/ IN THE INTERNAL REPOSITORY ONLY. Never commit it to the public repo.
2. Show me the column headers and propose a mapping to the fields in docs/data-dictionary.md (usage_weekly, delivery_weekly, engineers, teams). Columns that don't map stay out.
3. After I approve the mapping, add compass/importers/organizer_csv.py that reads those CSVs with the csv module and writes the same tables, and a command: python -m compass import-organizer data/organizer
4. Extend compass/compliance.py's ALLOWED_COLUMNS only for the mapped metadata columns. Never allow names, emails or free text.
5. Add held-out evaluation scenarios built from the organizer data to eval/scenarios.json BEFORE looking at the engine's output, then run python -m compass eval and report the honest pass rate.
6. Add tests for the importer (good file, missing column, malformed row).

Constraints: standard library only; keep k = 5 or higher; no individual scoring or ranking anywhere.
```

## Task 3: Office work for the submission

```
Goal: prepare the submission materials from the repository content. You are approved for office work.

1. Open docs/presentation/Compass-Hackathon.pptx. In the INTERNAL copy only, add our team name and members on the title slide, and replace screenshots with fresh ones from the app if anything changed (screenshots live in docs/screenshots/). Keep the structure and claims; do not add numbers that are not in docs/measurements.md or reports/eval-report.md.
2. Draft the submission form answers (problem, solution, business value, architecture, guardrails, test results, how to run) from README.md, docs/business-case.md, docs/rubric-mapping.md and docs/measurements.md. Keep sourced facts and our assumptions clearly separated.
3. Turn docs/demo-script.md into a speaker script with exact clicks and timings for a 5-minute recording, and a backup plan if the live demo fails.
4. List anything in the deck or form that you could not verify from the repository.
```
