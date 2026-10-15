# Five-minute demo script

**Before you start**
1. Run `python -m compass --reset` (clean private store).
2. Open Setup, tick "allow test execution", and Save.
3. Sign in as engineer **Falcon**.
4. Keep a backup screen recording ready.

All demo projects are synthetic.

| Time | Show | Say |
|---|---|---|
| 0:00-0:30 | Title / sign-in page | "We all have Copilot, Claude Code and Devin, but usage doesn't tell us whether work got better. People give agents half a story, pick whichever tool is open, and accept output nobody checked. Compass coaches the workflow, locally, with no API keys." |
| 0:30-1:45 | **Workflow coach > Catch a missing API requirement > Start** | *Facts*: Java/Maven from `pom.xml:10`; the team standard at `standards/api-standard.md:10` requires `X-Correlation-Id`; auth is unknown. *Questions*: who may call it, which errors, the header. "The story said none of this." *Tool*: approval and data rules first, then fit; I can override within policy. *Work package*: spec and standard included in full, size and bytes shown, nothing sent anywhere. *Evidence > Run local checks*: missing header at `openapi.yaml:11`, no 400, no auth. *Result*: **Not accepted yet**, next action, one lesson. |
| 1:45-2:45 | **Reject a fix without reproduction evidence** | Defect LOGIN-7 has no repro steps, so Compass asks for expected vs actual and steps. *Evidence > Fix without a test > Verify*: tests run on temporary copies. **Not accepted: no reproduction evidence**, and it names the existing test that does reproduce it. Then *Fix with a regression test*: fails before, passes after, full suite green: **Accepted with evidence**. "My files were never touched." |
| 2:45-3:30 | **A test that catches a seeded defect** | *Evidence*, tick "run the project's tests" (explicit approval). `test_wrong_password_same_length_is_rejected` detects the planted defect at `auth.py:35`, while the smoke tests pass on broken code and are flagged weak. Security candidates: a synthetic credential at `settings.ini:7` and `shell=True` at `admin.py:8`, both labeled candidates. |
| 3:30-4:05 | **My coaching** | Private next-best actions from usage and delivery signals, with the 4 elements and evidence records. "Only I see this." |
| 4:05-4:35 | Switch role > **Manager, Team Echo** > *Request an engineer's private coaching* | Team patterns only, with k ≥ 5. The button tries to read an individual's coaching and the server refuses with 403. Team Delta (3 people) shows nothing. |
| 4:35-5:00 | **Tool catalog** and **How it works** | "37 reviewed open-source tools, all inactive until approved; real gitleaks, Semgrep and Spectral adapters; everything runs offline. Enablement, not evaluation." |

## Likely questions

- **Is this live AI?** The coach is deterministic on purpose: explainable, testable, offline, zero tokens. It makes the AI tools you already have work better by giving them complete, reviewed work packages and by checking what comes back. An approved-LLM hook exists (`COMPASS_LLM_URL`) and is off by default.
- **Can it read any folder?** No. Only folders you allow in Setup. It refuses path traversal, symlinks and credential files.
- **Does it send code to anyone?** No. You preview and copy the package yourself. Secrets are redacted and listed before export.
- **Can it run arbitrary commands?** No. It only runs named templates with validated arguments and no shell. Test runs need the Setup switch and per-run approval. Scanners must be approved and hash-matched.
- **What if a scanner isn't installed?** It shows as "not checked", never "passed".
- **Jira?** Off by default. Paste the story or import a CSV export, or enable a read-only fetch with your own token from an environment variable.
- **Why k = 5?** It matches common people-analytics practice (Microsoft Viva Insights minimum 5), and it is configurable upward.
