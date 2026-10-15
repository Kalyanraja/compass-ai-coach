---
name: writing-agent-instructions
description: Use when creating or editing agent customization files - SKILL.md skills, .prompt.md prompt files, .instructions.md files, custom agents, AGENTS.md/CLAUDE.md, or Devin playbooks - so they trigger reliably, stay lean, and work across Copilot, Claude Code and Devin.
metadata:
  practice: P5 context-pack
  source: original Compass content; informed by obra/superpowers writing-skills (MIT), anthropics/skills skill-creator (Apache-2.0, paraphrased), microsoft/AI-Engineering-Coach markdown quality checks (MIT), official Copilot, Claude Code and Devin docs
---

# Writing Agent Instructions

Instructions are code for agents. Make them findable, short, testable.

## Pick the right file
| Need | File | Loaded |
|---|---|---|
| Rules for every request | `AGENTS.md` (+ `CLAUDE.md` with `@AGENTS.md`, short `.github/copilot-instructions.md`) | always |
| Rules for certain files | `.github/instructions/<topic>.instructions.md` with `applyTo` | when matching files are in play |
| Repeatable multi-step workflow | `.claude/skills/<name>/SKILL.md` | on demand (description match or `/name`) |
| One-shot template a human triggers | `.github/prompts/<name>.prompt.md`, `.claude/commands/<name>.md` | when invoked |
| Persona with limited tools | `.github/agents/<name>.agent.md`, `.claude/agents/<name>.md` | when selected/delegated |
| Devin unattended procedure | Devin Playbook (web UI) | when attached or via `!macro` |

## Skill rules
- Folder name equals `name`: lowercase, hyphens, max 64 chars. Name must match the directory or VS Code will not load it.
- `description` (max 1024 chars for VS Code): what it does AND when to use it, with trigger words people actually type. Put the key use case first.
- Body: imperative steps, checklists, explicit output format, "stop and ask when", safety. Move long reference material into sibling files and link them.
- Avoid names that collide with prompt files or commands (a skill and a prompt both create `/name`).

## Writing style
- Start with a heading or frontmatter. Use `##` sections.
- Imperative bullets ("Run", "Never", "Use"). Flat rules beat nested if/then chains.
- Concrete commands and exact strings where they matter. Placeholders as `{{NAME}}`.
- Say what done looks like and how to report it.
- Close every code fence.

## Test it
1. Write 3 realistic prompts that should trigger it and 2 that should not.
2. Run them in each tool your team uses. Check it triggered, followed the steps, and produced the output format.
3. Fix the description or steps; rerun. Keep the prompts as a regression set.

## Safety
- No secrets, internal URLs, real names or customer data in instruction files.
- Instruction files go through PR review like code.
