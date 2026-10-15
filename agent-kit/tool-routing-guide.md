# Tool routing guide: which assistant for which task

<!-- practice: P7 right-tool-for-task -->

Pick the cheapest tool that can do the task well, and keep a human in the loop. This guide separates **documented facts** (with sources) from **Compass recommendations** (judgment, adjust to your team).

Environment assumed: GitHub Copilot in VS Code (no MCP servers), Claude Code in VS Code (no MCP), Devin web app (no MCP, no API), an org-approved general assistant for documents and email (for example Microsoft 365 Copilot), and the usual deterministic tools (formatters, linters, IDE refactorings, codemods).

## 1. Quick decision tree (recommendation)

1. Can a rule do it exactly? (format, sort imports, rename a symbol, apply a known API migration) -> **No AI**: formatter, linter auto-fix, IDE refactor, codemod (OpenRewrite, Roslyn code fix, jscodeshift/ts-morph, ruff). Use AI only to help write the codemod.
2. Is it a question with no edits? (what does this do, what does this error mean, how do I...) -> **Copilot Chat in ask mode** (or Claude Code without edits). Lightweight model is usually enough.
3. Is it a small edit where you are already typing? -> **Copilot inline suggestions / next edit**.
4. Is it a multi-file change you want to watch and steer, with tests run locally? -> **Copilot agent mode** or **Claude Code**. Prefer Claude Code for long plan-driven work, terminal-heavy work, or when you want subagent reviews; prefer Copilot agent mode when you want to stay inside the editor's chat and inline diff flow.
5. Is it a well-specified, self-contained task that can run unattended and end in a PR? (dependency bump, test backfill, flaky test fix, migration slice) -> **Devin** with a playbook.
6. Is it prose for people? (status update, email, meeting summary, document rewrite) -> **General assistant** approved for that data.
7. Does it need secrets, production data, or a decision only a person can make? -> **Human**. Use AI only on redacted or synthetic inputs.

## 2. Decision matrix (recommendation)

| Task shape | Example | Best | Also OK | Avoid |
|---|---|---|---|---|
| Deterministic transform | rename across 80 files, reformat, import order | No AI (IDE refactor, formatter, codemod) | AI to draft the codemod | Agent editing files one by one |
| Lookup / explain | "what does this regex do?", explain stack trace | Copilot Chat (ask) | Claude Code (no edits) | Agent mode, premium reasoning model |
| Local edit | finish a function, add a guard clause | Copilot inline | Copilot Chat edit | Devin |
| Multi-file feature, interactive | implement a ticket with tests | Claude Code or Copilot agent mode | Devin (if well specified) | Inline only |
| Plan / spec | ticket to plan, spec to tasks | Copilot Chat with Planner agent, or Claude Code plan mode | General assistant for non-code parts | Starting in agent mode without a plan |
| Code review assist | self-review before PR | Copilot PR Reviewer agent or Copilot code review, Claude `code-reviewer` subagent | Devin PR readiness playbook | Merging on AI approval alone |
| Debugging, reproducible locally | failing test, exception | Claude Code or Copilot agent mode with `systematic-debugging` | Devin bug investigation playbook | Guess-and-check fixes |
| Flaky test | intermittent CI failure | Claude Code / Copilot agent (measure locally) | Devin `!flaky-fix` | Adding retries or sleeps |
| Unattended chore ending in PR | dependency upgrade, test backfill, migration slice | Devin with playbook | Claude Code | Large unsliced PRs |
| Prose for people | release email, status report | General assistant | Copilot Chat | Pasting confidential data into unapproved tools |
| Needs production data or secrets | investigate a customer record | Human | AI on redacted/synthetic copy | Any AI with real data |

Escape hatches (recommendation, informed by microsoft/AI-Engineering-Coach rules on runaway loops, session drift and repeated prompts):
- Agent repeats similar tool calls or 3 fixes failed -> stop, summarize, start a fresh session with a better brief.
- Session spans several task types or 25+ messages -> new session per task.
- Same prompt sent 3 times -> change the prompt (context, constraints, example) or save a working one as a prompt file/skill.

## 3. Documented facts: what each tool reads (no MCP needed)

Verified against official docs in October 2026. Behavior can change; recheck the links.

### GitHub Copilot (VS Code and GitHub.com)
| Fact | Source |
|---|---|
| Repository-wide instructions: `.github/copilot-instructions.md`, applied to all chat requests in the workspace (VS Code setting `github.copilot.chat.codeGeneration.useInstructionFiles`). | [VS Code custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) |
| Path-specific instructions: `.github/instructions/*.instructions.md` with `applyTo` glob frontmatter (comma-separated patterns; `**` for all) and `description`. Applied when creating or modifying matching files. | VS Code custom instructions; [GitHub repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) |
| `excludeAgent: "code-review"` or `"cloud-agent"` in an instructions file excludes that surface. | GitHub repository instructions |
| `AGENTS.md` (nearest in tree wins) or a root `CLAUDE.md` / `GEMINI.md` are agent instructions for Copilot on GitHub. VS Code reads a root `AGENTS.md` when `chat.useAgentsMdFile` is enabled. | GitHub repository instructions; VS Code custom instructions |
| Prompt files: `.github/prompts/*.prompt.md`; frontmatter `description`, `name`, `argument-hint`, `agent` (`ask`, `edit`, `agent`, or a custom agent name), `model`, `tools`; invoked with `/name`; variables `${input:name:placeholder}`, `${selection}`, `${file}`, `${workspaceFolder}`. Unavailable tools are ignored. | [VS Code prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files) |
| Custom agents: `.github/agents/*.agent.md` (any `.md` in that folder is detected); frontmatter `description`, `name`, `argument-hint`, `tools`, `agents`, `model`, `user-invocable`, `disable-model-invocation`, `target`, `handoffs` (`label`, `agent`, `prompt`, `send`). VS Code also reads `.claude/agents/*.md` in Claude format (`name`, `description`, `tools`, `disallowedTools`). | [VS Code custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents) |
| Agent skills: VS Code reads `.github/skills/`, `.claude/skills/` and `.agents/skills/` (plus `~/.copilot/skills`, `~/.claude/skills`, `~/.agents/skills`). `SKILL.md` needs `name` (lowercase, hyphens, max 64 chars, must match the folder name or it is not loaded) and `description` (max 1024 chars, what + when). Skills load automatically by description match or via `/name`. | [VS Code agent skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| Copilot code review uses repository custom instructions and `AGENTS.md`, and agent skills in `.github/skills`; instructions come from the PR head branch. | [Copilot code review](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review); GitHub repository instructions |

### Claude Code
| Fact | Source |
|---|---|
| Project instructions: `./CLAUDE.md` or `./.claude/CLAUDE.md`; `CLAUDE.local.md` for personal notes. Files above the working directory load at launch; subdirectory files load on demand. Target under 200 lines. | [Claude Code memory](https://code.claude.com/docs/en/memory) |
| `@path` imports expand at launch (relative to the importing file, max four hops). | Claude Code memory |
| Claude Code reads `AGENTS.md` only when no `CLAUDE.md`/`CLAUDE.local.md` exists in the working directory or above, unless `CLAUDE.md` imports it with `@AGENTS.md` (recommended pattern; never read twice). | Claude Code memory |
| `.claude/rules/*.md` with `paths:` frontmatter for path-scoped rules. | Claude Code memory |
| Skills: `.claude/skills/<name>/SKILL.md`; all frontmatter optional, `description` recommended; `description` + `when_to_use` truncated at 1,536 chars in the listing; fields include `name`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `context: fork`, `paths`, `metadata`. Unknown fields are ignored. `$ARGUMENTS`, `$0`... substitution. | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Custom commands merged into skills: `.claude/commands/<name>.md` still works and creates `/name`; a skill wins on a name collision. | Claude Code skills |
| Subagents: `.claude/agents/*.md`; required `name`, `description`; optional `tools`, `disallowedTools`, `model`, `permissionMode`, `skills`, and more. Invoked automatically by description, by natural language, or `@"name (agent)"`. | [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) |

### Devin (web app)
| Fact | Source |
|---|---|
| Playbooks are reusable prompts created in Settings > Playbooks; recommended sections: Overview, Procedure, Specifications, Advice and Pointers, What's Needed From User, Forbidden Actions. A macro (`!name`, letters/numbers/underscores/hyphens, unique in org) attaches a playbook from the prompt box. Saves are versioned. | [Devin creating playbooks](https://docs.devin.ai/product-guides/creating-playbooks) |
| Skills: Devin scans `.agents/skills/`, `.devin/skills/`, `.github/skills/`, `.claude/skills/`, `.cognition/skills/`, `.windsurf/skills/` in every repo; `SKILL.md` with `name`, `description`, optional `allowed-tools`, `argument-hint`, `triggers`; invoked automatically or with `@skills:name`; one skill active at a time. | [Devin skills](https://docs.devin.ai/product-guides/skills) |
| Knowledge: tips Devin recalls by trigger description; created in Settings > Knowledge; can be pinned to a repo or all repos; being migrated to Skills. | [Devin knowledge](https://docs.devin.ai/product-guides/knowledge) |
| Devin CLI reads `AGENTS.md`, `CLAUDE.md`, `.windsurfrules`, `.devin/rules/`, `.cursor/rules/`, `.claude/` automatically. | [Devin CLI rules](https://docs.devin.ai/cli/extensibility/rules) |

### Consequences for this kit (derived from the facts above)
- One skill folder, `.claude/skills/`, is read by Claude Code, Copilot in VS Code and Devin. That is why the kit puts all workflows there.
- `CLAUDE.md` contains `@AGENTS.md` so Claude Code reads the shared rules even though a `CLAUDE.md` exists.
- Skill names differ from prompt/command names (for example skill `pr-readiness-selfcheck` vs prompt `/pr-readiness`) to avoid two `/name` entries colliding.

## 4. Not verified (treat as open questions)
- Whether the Devin **web/cloud** agent automatically reads `AGENTS.md` (documented only for the Devin CLI). The kit's Devin playbooks tell Devin to read it explicitly.
- Whether VS Code Copilot reads a root `CLAUDE.md` as instructions (documented for Copilot on GitHub, not on the VS Code page checked).
- Whether Copilot code review truncates instruction files after ~4,000 characters. This limit is asserted by microsoft/AI-Engineering-Coach but not stated on the GitHub page checked; the kit keeps `copilot-instructions.md` under that size anyway.
- Exact built-in tool names for `tools:` in `.agent.md` vary by VS Code version (for example `search` vs `search/codebase`). The kit lists common names; unavailable names are ignored, but check the tool picker after install.

## 5. Safety rules for every tool (recommendation)
- Use only tools approved by your organization for the data you are handling.
- Never put secrets, credentials, PII, customer or production data into any prompt, instruction file, playbook or knowledge entry.
- Keep approvals on for state-changing terminal commands; do not auto-approve everything.
- Require evidence (command plus output) for every "done", and a human review before merge.
