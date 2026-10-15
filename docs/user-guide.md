# User guide

## Engineers

1. **Sign in.** Choose *Engineer* and pick a persona. In production, single sign-on takes you straight in.
2. **Read your next best actions.** Each card has four parts:
   - **Observation:** what your recent signals show, with numbers and the practice guideline
   - **Suggested action:** a concrete step, tailored to your stack, role and project complexity, with the tool to use
   - **Why:** the practice and the evidence behind it
   - **Outcome to watch:** the signal to watch over the next two weeks and a realistic target
3. **Check the evidence.** *Evidence, sources and agent-kit files* shows the exact records used, the sources, and the Copilot, Claude Code or Devin files that apply the practice.
4. **Preview the effect.** *Show before and after* plots your actual signals and a clearly labeled simulation of the practice.
5. **Stay in control.** *I tried this*, *Useful*, *Not useful* or *Dismiss* (with a reason). This is private and only changes your own ordering. *My data* shows everything stored about your coaching and lets you delete it.
6. **Prompt coach.** Paste a story, or import a Jira CSV export (Jira: *Export > CSV*). Compass:
   - names the task type and which parts of a good brief are present
   - warns about secrets or personal data in the text
   - recommends a tool and explains why (or says no AI is needed)
   - asks up to three questions
   - writes a prompt in the right shape for the chosen tool

   Copy it into Copilot, Claude Code or Devin.

## Managers

- *Team insights* shows tool adoption, team medians, weekly trends and the gaps shared by at least 5 engineers, each with an enablement opportunity and files to roll out.
- Patterns affecting fewer than 5 engineers are hidden. Teams under 5 show nothing.
- There is no way to see individuals. The "Request an engineer's private coaching" button demonstrates that the server refuses.

## Leaders

- *Portfolio insights* shows portfolio patterns, teams (alphabetical, not ranked), and practices discovered in the data with their association statistics.

## AI enablement team

- *Enablement* shows the quality evaluation, compliance checks and the access audit (role, endpoint and status only).
- *Practices* is the catalog. Each practice links to its agent-kit files.

## Using the agent kit in your repo

See [agent-kit/README.md](../agent-kit/README.md). In short, run `agent-kit\install-kit.bat <your repo>`. Then:
- **Copilot Chat:** type `/pr-readiness`, `/test-plan`, `/write-tests` or `/jira-to-plan`.
- **Claude Code:** skills load automatically by description.
- **Devin:** paste the playbooks into *Settings > Playbooks* and attach them with `!macro`.

## Workflow coach (engineers)

1. **Goal:** pick the project folder, then paste the story or defect, fetch it from Jira, or click a demo. Choose the workflow or let Compass detect it.
2. **Project facts:** what Compass found, each with a clickable `file:line` source. *Inferred* facts are conventions you should confirm. *Unknown* means Compass will not guess.
3. **Questions:** at most three at a time, each with the reason it matters. Answer or skip.
4. **Tool:** say what data is involved and how complex the task is. Compass applies approval and data rules first, then fit. You can pick another allowed tool.
5. **Work package:** choose Lean, Balanced or Deep. Review the included and excluded files, the redactions and any untrusted-text warnings. Remove or add files. Tick the review box, then copy or download. Nothing is sent anywhere.
6. **Evidence:** run local checks (static, never runs your code), optionally run your tests with explicit approval, import reports (JUnit XML, unittest output, gitleaks, Semgrep, Spectral, diffs), or verify a defect fix on temporary copies.
7. **Result and lesson:** each acceptance criterion is passed, failed or not checked, with evidence. You also get the next action, one lesson and a short exercise. Delete the journey when you're done.

For tasks outside the three workflows (documents, emails, SQL, refactors), use **Quick prompt**. Copilot and Claude Code are approved for office work.
