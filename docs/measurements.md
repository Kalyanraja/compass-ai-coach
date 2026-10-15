# Measurements (honest numbers)

All numbers on this page were produced in the build sandbox on 2026-10-15 from this repository. **Token counts are estimates (characters / 4)**. They come from no model tokenizer and are **not** Copilot, Claude or Devin billing or total conversation usage. Exact UTF-8 bytes are given alongside.

## Context size: work package vs pasting the whole project

| Project | Budget | Package (est. tokens) | Package bytes | Whole project (est. tokens) | Whole project bytes | Files in project | Files in package | Overflow |
|---|---|---|---|---|---|---|---|---|
| ORD-12 story, `examples/java-orders-api` | any | 3,716 | 14,862 | 2,977 | 11,907 | 12 | 7 | no |
| LOGIN-7 defect, `examples/py-login-service` | any | 2,210 | 8,839 | 2,190 | 8,757 | 16 | 9 | no |
| Compass repository itself (feature task naming 2 files) | Lean | 9,703 | 38,812 | 454,230 | 1,819,098 | 386 | 2 | **yes** |
| Compass repository itself | Balanced | 9,703 | 38,812 | 454,230 | 1,819,098 | 386 | 2 | **yes** |
| Compass repository itself | Deep | 15,145 | 60,579 | 454,230 | 1,819,098 | 386 | 7 | no |

How to read it:
- **Small projects:** for the tiny fixtures the package is slightly *larger* than the whole project, because it adds structure: goal, confirmed facts, standards, questions, staged actions, acceptance criteria and evidence requirements. On small projects the value is completeness, not compression.
- **Large repositories:** a Deep package for a task in the 386-file Compass repo is about 3.3% of a whole-repository paste, and it keeps both named files in full.
- **Overflow:** Lean and Balanced report an overflow for that task instead of silently dropping decisive code. The user picks Deep or removes a file explicitly.
- **Quality:** budgets are product defaults to evaluate, not proven optimums. Quality is checked by the acceptance tests: decisive files are always present and patches are never sent.

Reproduce with the snippet in `docs/IMPLEMENTATION-REPORT.md` (section "Measured context").

## Checks executed

| Check | Command | Result |
|---|---|---|
| Acceptance and workflow tests | `python -m unittest discover -s tests -t . -v` | 74 tests, all pass (Python 3.13, Linux) |
| Recommendation quality eval | `python -m compass eval` | 25/25 scenarios, 5/5 context pairs, 37/37 personas, 16/16 routing stories |
| Data-minimization checks | `python -m compass compliance` | all pass |
| Browser walkthrough of the 3 demos | Playwright script against a live server | no console errors. Verdicts: API "Not accepted yet"; fix without test "Not accepted: no reproduction evidence"; fix with regression test "Accepted with evidence"; test-creation "Not accepted yet" (defect detected, weak suite flagged, secret found) |
| Real scanners through the approval flow | gitleaks 8.30.1, Semgrep 1.181.0, Spectral 6.17.0 on the fixtures | gitleaks: 0 findings on the fixtures (its default rules did not flag the synthetic `admin_password`; the built-in check did, and the verdict combines both). Semgrep: `subprocess shell=True` at `login_service/admin.py:8`. Spectral: correlation-id, 400-response and security rule violations on `openapi.yaml` |
| In-process egress block | `tests/test_workflow.py::BlockedNetwork` | full journey passes with non-loopback connections blocked |
| Windows | CI matrix `windows-latest` (Python 3.9, 3.12) | runs on push. `Start-Coach.bat` and `install-kit.bat` were not executed in the build sandbox |
