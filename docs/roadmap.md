# Roadmap

## Phase 1: Hackathon MVP (done)
- Private engineer coaching for two workflows (PR readiness, AI-assisted test creation) with four-element recommendations
- Prompt coach with Jira CSV import and tool routing
- Aggregated manager and leader views with k-anonymity and differencing protection
- Practice discovery with non-causal statistics
- Drop-in agent kit for Copilot, Claude Code and Devin
- Evaluation, compliance and acceptance tests, plus CI

## Phase 2: Pilot (4-6 weeks, 2-3 volunteer teams)
1. Privacy and risk review of data sources, the k threshold (consider 10 for production) and retention.
2. Replace synthetic data with **authorized metadata exports only**: PR and CI metadata from the SCM, and tool usage counts from the vendors' admin metrics. No code, no prompt text.
3. Enterprise SSO in place of the demo picker.
4. Install the agent kit in pilot repos. Track team-level before and after on the same services.
5. Run a short perceptual survey (SPACE recommends at least one), aggregated only.
6. Success criteria: at least 60% of engineers find recommendations useful (private feedback, aggregated), and the pilot teams' median review rounds and CI first-pass rate move in the right direction. Report as association, not causation.

## Phase 3: Scale
- A VS Code extension shell so coaching and the prompt coach live in the editor. It can use the Copilot Language Model API where approved, with no separate API keys.
- More workflows: code review, documentation, modernization and remediation.
- Practice catalog contributions through PRs with the eval gate.
- An org-wide `.github` repository to distribute the agent kit centrally.
- Jira integration through approved connectors when available (CSV import keeps working without them).

## Future enhancements
- Held-out evaluation set from real, authorized pilot data
- Regression analysis with confidence intervals when sample sizes allow
- Localized practice content per language and stack
- Opt-in "share my practice" so engineers can contribute a working prompt to the library, reviewed before publishing
