# CLAUDE.md

@AGENTS.md

<!-- The line above imports AGENTS.md (Claude Code @path import). Without it, Claude Code reads only CLAUDE.md when both exist. Keep this file short; shared rules belong in AGENTS.md. -->
<!-- practice: P5 context-pack -->

## Claude Code specifics
- Skills live in `.claude/skills/`. Use them by name or let Claude load them:
  - New feature or behavior change: `brainstorming` then `writing-plans` then `executing-plans`
  - Any code change: `test-driven-development`
  - Any bug or failing test: `systematic-debugging`
  - Before saying done, committing or opening a PR: `verification-before-completion`, then `pr-readiness-selfcheck`
- Slash commands live in `.claude/commands/` (for example `/pr-readiness`, `/slice-pr`, `/write-tests`, `/root-cause`).
- Subagents live in `.claude/agents/`: `code-reviewer` (read-only review) and `test-writer`.
- Use plan mode for multi-file work. Ask before running destructive commands (`rm -rf`, `git push --force`, `DROP`, `TRUNCATE`, migrations).
- Do not auto-approve all tools. Keep permission prompts on for shell commands that change state.
- Start a fresh session when switching task type (feature, bug, docs). Keep sessions focused.

## Safety
- No secrets, PII or production data in prompts, files or command output you paste.
- Run tests and show the command and result before claiming success.
- A human reviews and merges. Never merge or deploy.
