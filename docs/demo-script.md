# Five-minute demo script

Before you start: run `python -m compass --reset` so the private store is empty, open <http://127.0.0.1:8765/>, and keep a backup screen recording ready.

| Time | Show | Say |
|---|---|---|
| 0:00-0:35 | Title page | "We all have Copilot, Claude Code and Devin. Usage dashboards tell us who logged in, not whether work got better. DORA found delivery stability drops as AI adoption rises unless teams keep good habits. Compass coaches the habits, privately." |
| 0:35-1:50 | **Engineer** > persona **Falcon** (senior, Java, high complexity) | Point at the privacy banner. Walk through the first card: **Observation** (median PR 716 lines, 3.2 review rounds), **Suggested action** (Claude Code plan mode, slice into PRs under 400 lines, separate API contract changes), **Why** (SmartBear/Cisco review evidence), **Outcome to watch**. Open *Evidence* to show record ids, which give traceability. Click **Show before and after**: synthetic actuals vs. the simulated projection, clearly labeled. |
| 1:50-2:15 | Same card: **Dismiss** (reason "Not now"), then *Dismissed* > **Restore** | "The engineer stays in control. This is stored privately. Watch: the manager view will not change." |
| 2:15-3:05 | **Prompt coach** > Load sample Jira stories > **DEMO-101** | It detects a feature/API task, shows 5 of 8 brief elements present, and asks about auth, constraints and verification. Type an answer for auth. It recommends Claude Code for this high-complexity persona and explains why. **Write my prompt**, then **Copy**. Then click DEMO-106 (formatting): "No AI needed, use the formatter." Then DEMO-104: "Repo-wide upgrade goes to Devin with a playbook." |
| 3:05-3:50 | Switch role > **Manager, Team Echo** | k stamp. Gaps shared by 5 or more engineers: plan-then-implement and context pack, each with a team-level enablement opportunity and kit files. "4 other patterns are hidden." No list of people, no drill-down. Click **Request an engineer's private coaching**: the server refuses with 403. This is the memorable moment. |
| 3:50-4:10 | Switch role > **Manager, Team Delta** | "Three engineers is below the threshold, so nothing is shown. The leader view also excludes Delta from totals, so nobody can work it out by subtraction." |
| 4:10-4:40 | Switch role > **AI enablement** > *Enablement* | 25/25 scenarios (target 80%), context pairs, compliance checks all PASS. The access audit shows the 403 from the manager's attempt, logged without any user id. |
| 4:40-5:00 | **How it works** diagram | "Python standard library, runs offline with no API keys, and a drop-in agent kit for any repo. Enablement, not evaluation." |

## Likely questions

- **Is this live AI?** The coaching core is deterministic by design: explainable, testable, zero token cost, offline. The agent kit and generated prompts are what make Copilot, Claude Code and Devin better. An optional approved-LLM hook exists (`COMPASS_LLM_URL`).
- **Real data?** No. Synthetic only, per the brief. The schema is metadata-only, and the compliance checks prove it. Real data would come from authorized metadata exports; see [roadmap.md](roadmap.md).
- **Why k = 5?** It matches common people-analytics practice (Microsoft Viva Insights requires a minimum of 5). It is configurable through `COMPASS_K_ANON`.
- **Can a manager game it?** There is no endpoint that returns individual data, and engineer identity comes from the signed session. Tests prove both.
