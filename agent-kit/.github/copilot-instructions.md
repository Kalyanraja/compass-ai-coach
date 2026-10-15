# Copilot instructions for {{PROJECT_NAME}}

<!-- Always-on for Copilot Chat, cloud agent and code review. Keep under ~4,000 characters: it is sent with every request. Details live in AGENTS.md and .github/instructions/. -->
<!-- practice: P5 context-pack -->

Read `AGENTS.md` at the repo root for commands, conventions and the working agreement.

## Always
- Make the smallest change that solves the stated problem. Preserve existing style and structure.
- Follow the nearest existing pattern. Name the file you copied the pattern from.
- For multi-file or behavior changes: propose a plan (goal, files, tests, risks) and wait for approval.
- Write or update a test that fails before the fix and passes after it.
- Run `{{TEST_CMD}}` (and `{{LINT_CMD}}`) and quote the result before saying a task is done.
- State assumptions explicitly. Ask instead of guessing when requirements are unclear.

## Never
- Never include secrets, credentials, tokens, PII, customer or production data in code, tests, logs, prompts or commits.
- Never add a dependency, change a public API, or touch auth, security or schema without flagging it.
- Never use fixed sleeps in tests. Never weaken or delete a test to make it pass.
- Never claim success without evidence. Never merge, force-push or deploy.

## Code review (Copilot code review reads this)
- Order findings: Critical (security, correctness, data loss) > Important (tests, performance, design) > Suggestion.
- Cite file and line. Explain impact. Propose a concrete fix.
- Check: tests cover the change, errors are handled, no secrets, input is validated, PR is one concern.

## Workflows available
- Prompt files: type `/` in Copilot Chat (`/pr-readiness`, `/write-tests`, `/debug-investigation`, `/slice-pr`, `/jira-to-plan`).
- Skills in `.claude/skills/` load automatically when relevant.
- Custom agents in `.github/agents/`: Planner (read-only), PR Reviewer (read-only), Test Engineer, Debugger.
