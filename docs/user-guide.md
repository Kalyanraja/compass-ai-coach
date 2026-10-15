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
