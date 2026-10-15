# NOTICE

Compass: AI Engineering Enablement Coach includes, adapts, or was informed by the third-party works below. This notice covers the `agent-kit/` folder. Snapshots were taken on 2026-10-15.

Terms used:
- **Vendored**: copied unmodified, with the original license file, under `agent-kit/vendor/`.
- **Adapted**: rewritten in Compass's own words and structure, keeping ideas and some short phrases from the source; each adapted file names its source in frontmatter `metadata.source` or in a header line.
- **Informed by**: ideas only, paraphrased; no text copied.

## Sources

| Source | URL | Commit | License | Vendored | Adapted / informed |
|---|---|---|---|---|---|
| obra/superpowers | https://github.com/obra/superpowers | bb92a77 | MIT (Copyright (c) 2025 Jesse Vincent) | Full `skills/` folder in `agent-kit/vendor/superpowers/` with `LICENSE` | Adapted: skills `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging` (+ `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`), `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `finishing-a-branch`; Claude subagent `code-reviewer`. Informed: `pr-readiness-selfcheck`, `flaky-test-hardening`, `writing-agent-instructions`, several prompts and anti-patterns |
| github/awesome-copilot | https://github.com/github/awesome-copilot | 36e95df | MIT (Copyright GitHub, Inc.) | Selected files in `agent-kit/vendor/awesome-copilot-selected/` with `LICENSE`: 20 instructions (code-review-generic, security-and-owasp, playwright-typescript/python/dotnet, java-junit5-assertions, csharp, qa-engineering-best-practices, spec-driven-workflow-v1, taming-copilot, context-engineering, sql-sp-generation, ms-sql-dba, nodejs-javascript-vitest, springboot, dotnet-architecture-good-practices, self-explanatory-code-commenting, agent-safety, exclude-prompt-data, update-docs-on-code-change), 19 skills (bug-reproduction-brief, create-agentsmd, csharp-xunit, java-junit, pytest-coverage, javascript-typescript-jest, sql-code-review, sql-optimization, test-gap-audit, refactor, conventional-commit, create-implementation-plan, create-specification, breakdown-test, what-context-needed, tiny-stepping, cypress-flake-fixer, playwright-generate-test, review-and-refactor), 9 agents (debug, planner, plan, tdd-red, tdd-green, tdd-refactor, playwright-tester, critical-thinking, devils-advocate) | Informed: `.github/instructions/*` (tests, security, playwright, java, csharp, sql), prompts (`pr-readiness`, `self-review`, `security-check`, `sql-review`, `commit-message`, `create-agents-md`), skills `test-creation`, `flaky-test-hardening`, `context-pack`, custom agents, many prompt-library templates |
| github/spec-kit | https://github.com/github/spec-kit | 3238fa9 | MIT (Copyright GitHub, Inc.) | `templates/` spec, plan, tasks, checklist, constitution templates in `agent-kit/vendor/spec-kit-templates/` with `LICENSE` | Informed: `/spec-to-tasks` and `/write-spec` prompts, `ticket-to-plan` clarification taxonomy, `writing-plans` task format, `pr-slicing` story ordering |
| microsoft/AI-Engineering-Coach | https://github.com/microsoft/AI-Engineering-Coach | 8c78e96 | MIT (Copyright (c) Microsoft Corporation) | 45 rule definitions from `src/core/rules/` in `agent-kit/vendor/ai-engineering-coach-rules/` with `LICENSE` | Informed: `prompt-library/anti-patterns.json` (detection hints paraphrased from rules such as lazy-prompting, no-file-context, low-constraint-usage, vibe-coding, copy-paste-blindness, speed-accept, session-drift, instruction-bloat, yolo-mode), `context-pack` health checks (size, structure and imperative-phrasing checks), `tool-routing-guide.md` escape hatches |
| anthropics/skills | https://github.com/anthropics/skills | dbd4588 | Apache-2.0 for open-source skills (for example `skill-creator`, `webapp-testing`); document skills (docx, pdf, pptx, xlsx) are source-available, not open source | Nothing | Informed only (paraphrased): skill authoring conventions in `writing-agent-instructions` (description states what and when, progressive disclosure, test prompts) |
| agentsmd/agents.md | https://github.com/agentsmd/agents.md | d001185 | MIT (Copyright (c) 2025 OpenAI) | Nothing | Informed: `AGENTS.md` section layout (overview, commands, testing, PR instructions) |
| PatrickJS/awesome-cursorrules | https://github.com/PatrickJS/awesome-cursorrules | b044f95 | CC0-1.0 | Nothing | Reviewed for coverage; no content used |
| wshobson/agents | https://github.com/wshobson/agents | 7257c27 | MIT | Nothing | Reviewed for coverage; no content used |
| hesreallyhim/awesome-claude-code | https://github.com/hesreallyhim/awesome-claude-code | eb40c09 | CC BY-NC-ND 4.0 (not permissive) | Nothing | Reviewed as a link index only; no content copied or adapted |

## Official documentation consulted (facts only, no text copied)
- GitHub Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Copilot code review: https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review
- VS Code: custom instructions, prompt files, custom agents, agent skills: https://code.visualstudio.com/docs/copilot/customization/
- Claude Code: memory (CLAUDE.md, AGENTS.md, imports), skills, subagents: https://code.claude.com/docs/en/
- Devin: playbooks, skills, knowledge, CLI rules: https://docs.devin.ai/

## License texts
Full license texts for vendored material are in each `agent-kit/vendor/*/LICENSE` file. Each vendored folder also has a `SOURCE.txt` with the exact commit.

### MIT License (applies to obra/superpowers, github/awesome-copilot, github/spec-kit, microsoft/AI-Engineering-Coach material)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Notes
- The vendored `awesome-copilot-selected/skills/bug-reproduction-brief` states it was itself adapted from the MIT-licensed https://github.com/skyestrela/ai-agent-skill-preview.
- Vendored files are kept unmodified, including their references to tools, MCP servers or scripts that may not be available in restricted environments. Review before enabling them.
- Product names (GitHub Copilot, Visual Studio Code, Claude Code, Devin, Microsoft 365 Copilot) are trademarks of their owners and are used only to describe compatibility.
