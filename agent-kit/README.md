# Compass agent kit

A drop-in folder of instructions, prompts, skills, agents and playbooks that makes **GitHub Copilot**, **Claude Code** and **Devin** follow the same strong engineering workflows in any repository.

- **No MCP servers. No API keys. No extensions to install.** Everything is plain Markdown and JSON that the tools already read from the repo (or that you paste into Devin's web app once).
- **Generic.** Every project-specific value is a `{{PLACEHOLDER}}`.
- **Safety built in.** Every instruction and skill says: no secrets, PII or production data in prompts; run tests and show evidence; a human reviews before merge.

## Install in 2 minutes

Bash (Linux, macOS, Git Bash, WSL):
```bash
git clone <this-repo-url> compass && cd compass/agent-kit
./install-kit.sh /path/to/your-repo              # add --dry-run to preview, --with-vendor for third-party originals
```

Windows (cmd or PowerShell):
```bat
cd compass\agent-kit
install-kit.bat C:\path\to\your-repo           & rem add --dry-run to preview, --with-vendor for originals
```

The installer **never overwrites** an existing file. It skips it and lists it so you can merge by hand.

Then:
1. Fill the placeholders in `AGENTS.md` (commands, stack, PR size). Fastest: run `/create-agents-md` in Copilot Chat or Claude Code; it fills them from verified repo facts.
2. VS Code: turn on `chat.useAgentsMdFile` so Copilot also reads `AGENTS.md` (Copilot already reads `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`, `.github/agents/` and `.claude/skills/`).
3. Devin: follow [`devin/README.md`](devin/README.md) to create 7 Playbooks and 3 Knowledge entries (about 15 minutes, once per org).
4. Commit on a branch and open a PR. Instruction files are code; review them like code.

What lands in your repo:
```
AGENTS.md  CLAUDE.md
.github/copilot-instructions.md  .github/instructions/  .github/prompts/  .github/agents/
.claude/skills/  .claude/commands/  .claude/agents/
.agent-kit/            # reference only, not auto-loaded: this README, tool-routing-guide.md, devin/, prompt-library/, vendor/ (optional)
```

## Which tool reads which file

| File / folder | Copilot (VS Code) | Copilot (GitHub.com: code review, cloud agent) | Claude Code | Devin (web) |
|---|---|---|---|---|
| `AGENTS.md` | yes, with `chat.useAgentsMdFile` | yes | yes, via `@AGENTS.md` import in `CLAUDE.md` | not documented for web agent; playbooks read it explicitly (Devin CLI reads it) |
| `CLAUDE.md` | not documented on VS Code page | yes (root, as agent instructions) | yes | Devin CLI only |
| `.github/copilot-instructions.md` | yes (always on) | yes | no | no |
| `.github/instructions/*.instructions.md` | yes (`applyTo` globs) | yes (code review and cloud agent) | no | no |
| `.github/prompts/*.prompt.md` | yes (`/name`) | no | no | no |
| `.github/agents/*.agent.md` | yes (agent picker) | not verified here (VS Code docs mention a `github-copilot` target) | no | no |
| `.claude/skills/*/SKILL.md` | **yes** (auto or `/name`) | code review reads `.github/skills` only | **yes** (auto or `/name`) | **yes** (auto or `@skills:name`) |
| `.claude/commands/*.md` | no | no | yes (`/name`) | no |
| `.claude/agents/*.md` | yes (Claude format) | no | yes (subagents) | no |
| `devin/playbooks`, `devin/knowledge` | no | no | no | yes, after pasting into the web app |

Sources and exact field lists: [`tool-routing-guide.md`](tool-routing-guide.md) section 3. Items marked "not documented" are listed under "Not verified".

## How the kit maps to the eight practices

| ID | Practice | Copilot | Claude Code | Devin | Shared skill |
|---|---|---|---|---|---|
| P1 | `pr-slicing` | `/slice-pr`, `pull-requests.instructions.md` | `/slice-pr` | jira-ticket-to-pr, modernization playbooks | `pr-slicing` |
| P2 | `pr-readiness-selfcheck` | `/pr-readiness`, `/self-review`, `/pr-description`, PR Reviewer agent | `/pr-readiness`, `code-reviewer` subagent | `!pr-readiness`, definition-of-done knowledge | `pr-readiness-selfcheck`, `requesting-code-review`, `finishing-a-branch` |
| P3 | `test-first-acceptance` | `/test-plan`, `/write-tests`, Test Engineer agent, `tests.instructions.md` | `/write-tests`, `test-writer` subagent | `!test-backfill`, testing-standards knowledge | `test-driven-development`, `test-creation` |
| P4 | `plan-then-implement` | `/write-spec`, `/jira-to-plan`, `/spec-to-tasks`, Planner agent | `/jira-to-plan`, `/spec-to-tasks`, plan mode | `!ticket-to-pr` (plan approval gate) | `brainstorming`, `writing-plans`, `executing-plans`, `ticket-to-plan` |
| P5 | `context-pack` | `copilot-instructions.md`, `/create-agents-md`, `/explain-code` | `CLAUDE.md` + `@AGENTS.md`, `/create-agents-md` | repo-conventions knowledge | `context-pack`, `writing-agent-instructions` |
| P6 | `verify-before-done` | `/debug-investigation`, `/root-cause`, Debugger agent | `/debug-investigation`, `/root-cause` | `!bug-investigate`, definition-of-done | `verification-before-completion`, `systematic-debugging`, `receiving-code-review` |
| P7 | `right-tool-for-task` | prompt library `route-task-to-tool` | same | same | `right-tool-for-task`, `tool-routing-guide.md` |
| P8 | `flaky-test-hardening` | `/fix-flaky-test`, `playwright.instructions.md` | `/fix-flaky-test` | `!flaky-fix` | `flaky-test-hardening` |

Every file is tagged with its practice: `metadata.practice` in skill frontmatter, or a `<!-- practice: ... -->` comment right after the frontmatter elsewhere.

## Inventory

| Path | Count | What |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md` | 2 | Cross-agent conventions template; Claude entry point that imports it |
| `.github/copilot-instructions.md` | 1 | Short always-on Copilot rules (under 4,000 chars) |
| `.github/instructions/` | 10 | tests, pull-requests, security, java, csharp, python, typescript, sql, playwright, docs (`applyTo` globs) |
| `.github/prompts/` | 20 | pr-readiness, pr-description, self-review, slice-pr, test-plan, write-tests, fix-flaky-test, jira-to-plan, spec-to-tasks, debug-investigation, root-cause, refactor-safely, dependency-upgrade, security-check, create-agents-md, explain-code, write-spec, address-review-feedback, sql-review, commit-message |
| `.github/agents/` | 4 | Planner (read-only), PR Reviewer (read-only), Test Engineer, Debugger |
| `.claude/skills/` | 17 | brainstorming, writing-plans, executing-plans, test-driven-development, systematic-debugging (+3 technique files), verification-before-completion, requesting-code-review, receiving-code-review, pr-readiness-selfcheck, pr-slicing, test-creation, ticket-to-plan, context-pack, flaky-test-hardening, right-tool-for-task, finishing-a-branch, writing-agent-instructions |
| `.claude/commands/` | 17 | Slash commands mirroring the prompt files |
| `.claude/agents/` | 2 | code-reviewer (read-only), test-writer |
| `devin/` | 7 + 3 | Playbooks and Knowledge entries, plus loading guide |
| `prompt-library/` | 54 + 27 | Prompt templates and anti-patterns (JSON + Markdown) |
| `tool-routing-guide.md` | 1 | When to use which tool; documented facts vs recommendations |
| `vendor/` | 4 sets | Unmodified originals with licenses (optional install) |

Naming note: skills that would collide with a prompt or command of the same `/name` use a distinct name. The requested `pr-readiness` skill is `pr-readiness-selfcheck`, and the `jira-to-plan` skill is `ticket-to-plan` (it works for Jira, Azure Boards and GitHub issues). The prompt files and commands keep the short names.

## Customizing
- Edit `AGENTS.md` first; everything else points to it.
- Change globs in `.github/instructions/*.instructions.md` to match your layout. Delete language files you do not use.
- Add team workflows as new skills (see the `writing-agent-instructions` skill). Keep `name` equal to the folder name.
- Keep always-on files short; move detail into scoped instructions and skills.

## Vendored originals (optional)
`--with-vendor` copies these, unmodified, into `.agent-kit/vendor/` for teams that want the full sources. They are not auto-loaded.
- `vendor/superpowers/` - obra/superpowers skills (MIT)
- `vendor/awesome-copilot-selected/` - selected instructions, skills and agents from github/awesome-copilot (MIT)
- `vendor/spec-kit-templates/` - spec, plan, tasks, checklist, constitution templates from github/spec-kit (MIT)
- `vendor/ai-engineering-coach-rules/` - anti-pattern rule definitions from microsoft/AI-Engineering-Coach (MIT)

To use a vendored skill, copy its folder into `.claude/skills/` and review it first. Some reference subagents, MCP tools or scripts that may not be allowed in your environment.

See `NOTICE.md` at the root of the Compass repository for sources, licenses, and what was vendored vs adapted.
