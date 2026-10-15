# Loading the Compass kit into Devin (web app, no MCP, no API)

Devin picks up three kinds of kit content. Two need clicks in the web app; one comes for free from the repo.

| Kit content | How Devin gets it | Effort |
|---|---|---|
| `.claude/skills/*/SKILL.md` committed to the repo | Devin scans `.agents/skills/`, `.devin/skills/`, `.github/skills/`, `.claude/skills/`, `.cognition/skills/` and `.windsurf/skills/` in every repo ([Devin Skills docs](https://docs.devin.ai/product-guides/skills)) | none after install |
| `devin/playbooks/*.devin.md` | Create a Playbook in the web app and give it a macro | ~2 min each |
| `devin/knowledge/*.md` | Create a Knowledge entry in the web app | ~1 min each |

## 1. Commit the kit to the repo
Run the installer (see the kit README) and merge the PR. After that, Devin sessions in this repo can use the skills automatically or by mention, for example `@skills:pr-readiness-selfcheck`. Devin can have one skill active at a time.

## 2. Create Playbooks (Settings > Playbooks)
For each file in `devin/playbooks/`:
1. Fill the `{{PLACEHOLDERS}}` (or leave them for the user to fill per session).
2. Open **Settings > Playbooks**, click **Create playbook** on the Organization tab.
3. Title: the `#` heading. Body: paste the file content (the HTML comment line can be removed).
4. Macro: use the suggested macro in the first line (for example `!pr-readiness`). Macros may contain letters, numbers, underscores and hyphens and must be unique in your org.
5. Save. Each save creates a version you can revert.

Suggested macros:
| Playbook | Macro | Practice |
|---|---|---|
| pr-readiness | `!pr-readiness` | P2, P6 |
| test-creation | `!test-backfill` | P3 |
| jira-ticket-to-pr | `!ticket-to-pr` | P4, P3, P1, P6 |
| dependency-upgrade | `!dep-upgrade` | P1, P6 |
| flaky-test-fix | `!flaky-fix` | P8 |
| bug-investigation | `!bug-investigate` | P6 |
| modernization-migration | `!modernize-slice` | P1, P4, P6 |

## 3. Create Knowledge entries (Settings > Knowledge)
For each file in `devin/knowledge/`: click **Create knowledge**, copy the **Name**, **Trigger description** and **Content**, and pin it as the file says (specific repo or all repos). Keep each entry focused; Devin reads the whole entry when the trigger matches. Note: Devin's docs say Knowledge is being migrated to Skills, so repo skills are the long-term home; Knowledge is still useful for org-wide rules today.

## 4. Use it in a session
- Type the macro in the session prompt (for example `!ticket-to-pr`) and paste the inputs listed under "What's Needed From User".
- Or attach the playbook from the playbook picker before starting.
- Run two sessions in parallel with the same playbook when trying a new playbook; fold any fix you had to give Devin back into the playbook.

## Playbook format used here
Sections follow Devin's guidance: Overview, What's Needed From User, Procedure (one imperative step per line, including setup and delivery), Specifications (postconditions), Advice and Pointers, Forbidden Actions ([Creating Playbooks](https://docs.devin.ai/product-guides/creating-playbooks)).

## Safety
- Never put secrets, tokens, PII or production data in playbooks, knowledge, or session prompts. Use your organization's approved secrets mechanism for anything Devin needs.
- Every playbook ends in a draft PR or a report for human review. None merges or deploys.

## Not verified
- Whether the Devin cloud agent reads `AGENTS.md` automatically: the Devin CLI does ([CLI rules docs](https://docs.devin.ai/cli/extensibility/rules)), but the web-agent docs do not say. The playbooks therefore tell Devin to read `AGENTS.md` explicitly, and the `repo-conventions` Knowledge entry repeats the essentials.
