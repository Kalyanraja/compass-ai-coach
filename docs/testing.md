# Testing

| Suite | Command | What it proves |
|---|---|---|
| Acceptance tests | `python -m unittest discover -s tests -t . -v` | AC1-AC14 plus security tests: 34 tests against a live server on a random port with an isolated data directory |
| Quality evaluation | `python -m compass eval` | 25 seeded scenarios, 5 context pairs, 37 seeded personas, 16 prompt-routing stories. Writes `reports/eval-report.md` and `.json`. Exits non-zero below 80%. |
| Compliance | `python -m compass compliance` | Schema allow-list, no PII or code, no free text, synthetic labels, no ranking API |
| CI | `.github/workflows/ci.yml` | All of the above on Windows and Linux, Python 3.9 and 3.12 |

## How a scenario is graded

A scenario passes only if all five checks pass:

1. **Relevant:** the expected rule fires (and is the top recommendation when only one is expected), and no forbidden rule fires. Healthy and borderline scenarios check for false alarms.
2. **Complete:** observation, action, rationale and outcome are all populated.
3. **Explainable:** the rationale cites a source and every evidence record id exists in the input.
4. **Actionable:** the action has at least 15 words, names a concrete prompt, skill, playbook, tool or command, and the outcome has a signal and a target.
5. **Persona-specific:** the rationale reflects the persona's stack and project complexity.

## Honest limits

- The team wrote the scenarios and tuned the rules on them, so the 100% result is a regression baseline, not a held-out accuracy estimate.
- To get a held-out estimate, add scenarios built from the organizers' sample data to `eval/scenarios.json` **before** looking at the engine's output, then run `python -m compass eval`.
- The prompt-coach classifier uses keywords. Unusual phrasing can misclassify a task. The UI shows the top candidates, and the API accepts an explicit `task_type` override.
