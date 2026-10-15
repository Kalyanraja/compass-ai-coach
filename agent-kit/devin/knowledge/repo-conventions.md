# Knowledge: {{REPO_NAME}} conventions

<!-- Paste into Devin: Settings > Knowledge > Create knowledge. Pin to repo {{REPO_NAME}}. practice: P5 context-pack -->

**Name:** {{REPO_NAME}} conventions
**Trigger description:** When working in the {{REPO_NAME}} repository: building, testing, naming, branching or opening pull requests.
**Pin to:** {{REPO_NAME}} (specific repo)

**Content:**
- Read `AGENTS.md` at the repo root first; it is the source of truth for commands and conventions. Skills in `.claude/skills/` (also discovered by Devin) describe workflows step by step.
- Commands: install `{{INSTALL_CMD}}`, build `{{BUILD_CMD}}`, test `{{TEST_CMD}}`, single test `{{SINGLE_TEST_CMD}}`, lint `{{LINT_CMD}}`.
- Stack: {{LANGUAGES_AND_FRAMEWORKS}}. Production code in `{{SRC_DIR}}`, tests in `{{TEST_DIR}}`.
- Branches: `{{BRANCH_PATTERN}}`. Commits: {{COMMIT_STYLE}}. PRs: draft, under {{MAX_PR_LINES}} changed lines, one concern, template sections What / Why / How / Testing / Risk and rollback.
- Follow the nearest existing pattern and name the file you copied from in the PR.
- Never merge, approve, force-push or deploy. Never use secrets, PII or production data in code, tests, logs or PRs.
- A human reviews every change before merge.
