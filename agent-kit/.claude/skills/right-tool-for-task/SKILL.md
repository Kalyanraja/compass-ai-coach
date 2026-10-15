---
name: right-tool-for-task
description: Use when deciding which assistant or tool should handle a task - Copilot inline/chat/agent mode, Claude Code, Devin, a general assistant for docs and email, or no AI at all (formatter, linter, codemod, script) - or when a session is going in circles. Classifies the task shape and recommends the cheapest tool that can do it well, with a ready-to-use prompt.
metadata:
  practice: P7 right-tool-for-task
  source: original Compass content; anti-patterns informed by microsoft/AI-Engineering-Coach rules (agent-mode-for-asks, premium-for-lookup-questions, runaway-agent-loops, session-drift) (MIT)
---

# Right Tool for the Task

Match the tool to the task shape. Deterministic tools beat AI for deterministic jobs.

## Step 1 - Classify the task
Answer each:
1. Is the output fully determined by a rule? (format, rename symbol, sort imports, upgrade by codemod) -> **No AI**.
2. Is it a lookup or explanation question with no edits? -> **Chat (ask mode)**, lightweight model.
3. Is it a small edit inside the file you are in (< ~20 lines)? -> **Copilot inline / next edit**.
4. Is it a multi-file change in a repo you have open, needing to run tests, where you want to watch and steer? -> **Copilot agent mode or Claude Code** (pick the one your team set up; Claude Code for long, plan-heavy or terminal-heavy work).
5. Is it a well-specified, self-contained ticket that can run unattended (dependency bump, test backfill, migration slice) and produce a PR? -> **Devin with a playbook**.
6. Is it prose for people (email, status update, meeting notes, doc summary) with no code? -> **General assistant** (for example M365 Copilot or the org-approved chat tool).
7. Does it need production data, secrets, or a decision only a human can make? -> **Human**, with AI only on redacted or synthetic inputs.

## Step 2 - Check the escape hatches
- Agent looping (many tool calls, same error, 3+ failed fixes) -> stop, start a fresh session with a better brief, or switch to `systematic-debugging`.
- Session covering several task types -> start a new focused session.
- Repeating the same prompt -> rewrite it with context and constraints, or save it as a prompt file/skill.

## Step 3 - Output
```
Task shape: <deterministic | lookup | local edit | multi-file interactive | unattended ticket | prose | human-only>
Recommended: <tool + mode> because <one reason>
Alternative: <tool> if <condition>
Not recommended: <tool> because <reason>
Starter prompt: <brief using the context-pack task brief format>
Guardrails: <what the human must review/verify>
```
See `.agent-kit/tool-routing-guide.md` (installed by the Compass kit) for the full matrix and documented facts.

## Safety
- Use only tools approved by your organization for the data involved. Never paste secrets, PII or production data into any assistant.
- Whatever the tool, a human reviews the output before it ships.
