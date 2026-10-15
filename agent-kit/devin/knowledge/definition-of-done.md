# Knowledge: Definition of done

<!-- Paste into Devin: Settings > Knowledge > Create knowledge. Pin to all repos (or each team repo). practice: P6 verify-before-done; P2 pr-readiness-selfcheck -->

**Name:** Definition of done for pull requests
**Trigger description:** Before declaring a task complete, pushing commits, or opening or updating a pull request.
**Pin to:** All repos

**Content:**
A change is done only when all of these are true and shown with evidence from this session:
1. Every acceptance criterion has at least one automated test, and each new test was seen failing before the change.
2. Build, full test suite and linter pass; the summary line of each is quoted in the PR.
3. The PR is one concern and under {{MAX_PR_LINES}} changed lines (excluding lockfiles and generated files), or it is one slice of an approved slicing plan.
4. No secrets, credentials, PII or production data appear in the diff, commits, logs or PR text.
5. No debug output, commented-out code, unrelated formatting or stray TODOs.
6. API, schema, config or dependency changes are called out with migration and rollback steps.
7. Docs and changelog updated when behavior changed.
8. PR description has What / Why / How / Testing / Risk and rollback, links the ticket, and is opened as a draft for human review.
If any item cannot be verified, say "not verified" and why. Never say done, fixed or passing without the evidence.
