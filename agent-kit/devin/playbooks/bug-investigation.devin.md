<!-- Suggested macro: !bug-investigate | practice: P6 verify-before-done -->
# Bug Investigation

## Overview
Reproduce a reported bug, find the root cause with evidence, and either open a draft PR with a regression test and fix, or deliver an investigation report if the fix needs a human decision.

## What's Needed From User
- Bug description with expected vs actual behavior (redacted)
- Error messages, stack traces or log excerpts with secrets and personal data removed
- Environment where it happens (local, test, staging) and version/commit if known
- Whether Devin may implement the fix or should only investigate

## Procedure
1. Read `AGENTS.md` and `.claude/skills/systematic-debugging/SKILL.md`.
2. Write a reproduction brief: target and commit, environment, expected, actual, minimal steps.
3. Reproduce with the smallest command or test in a local or test environment; run it twice; record outputs.
4. Check recent changes in the suspect area (`git log -p`).
5. For multi-component flows, add temporary boundary logging (no secrets) to find the failing layer; trace the bad value back to its origin.
6. State one hypothesis at a time and test it minimally.
7. If allowed to fix: create branch `fix/{{TICKET_ID}}-<short>`, write a failing regression test, fix at the source, remove temporary logging, run the full suite, open a draft PR.
8. If not allowed, or after 3 failed fixes: post the investigation report and stop.

## Specifications
- Report includes reproduction command and output, root cause with file:line and evidence (or exactly what is still unknown).
- If fixed: regression test fails before and passes after; full suite passes; draft PR opened.

## Advice and Pointers
- A verified reproduction is valuable even without a fix.
- Do not claim a root cause from correlation alone.
- Compare with a similar working path; list differences.

## Forbidden Actions
- Do not reproduce against production systems or modify production data.
- Do not paste unredacted logs, secrets, or customer data into the session or PR.
- Do not merge or deploy; do not attempt a 4th fix without reporting.
- Do not skip human review: deliver a draft PR or a report for a person to review and merge.
