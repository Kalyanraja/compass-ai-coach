---
name: context-pack
description: Use when starting work in an unfamiliar repo, when agents keep getting commands or conventions wrong, when AGENTS.md/CLAUDE.md/copilot-instructions.md are missing or stale, or before a large task. Builds or refreshes a verified, lean context pack (AGENTS.md plus a task brief) from real repo facts and checks it for bloat and staleness.
metadata:
  practice: P5 context-pack
  source: original Compass content; checks informed by microsoft/AI-Engineering-Coach context-health and instruction-bloat rules (MIT), agents.md format (MIT), github/awesome-copilot create-agentsmd and context-engineering (MIT)
---

# Context Pack

Agents do their best work when the right facts are written down once, verified, and short.

## Part A - Repo context pack (AGENTS.md)
1. Inspect build files, CI workflows, README, linters, test folders and 2-3 representative source files.
2. Verify commands by running the cheap ones (lint, one unit test). Mark unverified ones.
3. Fill AGENTS.md sections: overview, commands table, key directories, code/test/git conventions (cite one example file each), security rules, where workflows live.
4. Keep shared rules in AGENTS.md. Keep `CLAUDE.md` as `@AGENTS.md` plus Claude-only notes. Keep `.github/copilot-instructions.md` short and pointing to AGENTS.md.
5. Move language- or folder-specific rules into `.github/instructions/*.instructions.md` with `applyTo` globs (and optionally `.claude/rules/`), not the always-on file.

## Part B - Task brief (per task)
Before a large task, give the agent a brief instead of a vague one-liner:
```
Goal: <one sentence, user-visible outcome>
Context: <files to read first, related ticket/spec, pattern to copy: path>
Constraints: <must / must not, versions, no new deps, performance>
Acceptance: <Given/When/Then or checklist>
Verify with: <commands>
Output: <what to return: diff, plan, table>
Out of scope: <list>
```
Reference files by path (`#file`, `@path`) instead of pasting large blobs. Attach the 3-5 most relevant files, not the whole tree.

## Health checks (fix any that fail)
| Check | Target |
|---|---|
| Always-on files exist | AGENTS.md, CLAUDE.md (importing it), .github/copilot-instructions.md |
| Size | copilot-instructions.md under ~4,000 chars; CLAUDE.md/AGENTS.md under ~200 lines |
| Structure | starts with a heading; `##` sections; imperative bullets ("Use", "Never"); flat rules, few nested if/then chains; code fences closed |
| Freshness | commands still run; paths still exist; reviewed in the last {{REVIEW_INTERVAL:90 days}} |
| Scoped rules | at least 2 `.instructions.md` with `applyTo`; skills and prompts present |
| Consistency | no contradictions between AGENTS.md, CLAUDE.md, instructions files |
| Placeholders | no unresolved `{{...}}` that agents would copy literally |

## Output
```
Files changed: <list>
Verified facts: | Item | Value | How verified |
Health: | Check | Pass/Fail | Note |
Remaining placeholders / unknowns: <list>
```

## Safety
- Never write secrets, internal hostnames, account IDs, personal names or customer data into context files. Use `{{PLACEHOLDERS}}`.
- Context files are code: they go through PR review like any change.
