---
name: systematic-debugging
description: Use when you hit any bug, failing test, build failure, unexpected behavior or performance problem, before proposing a fix. Four phases - reproduce and gather evidence, compare with working code, test one hypothesis at a time, then fix at the root cause with a regression test. Escalates after 3 failed fixes.
metadata:
  practice: P6 verify-before-done; P8 flaky-test-hardening
  source: adapted from obra/superpowers systematic-debugging (MIT)
---

# Systematic Debugging

No fixes without root cause investigation first. Symptom fixes are failures.

## Phase 1 - Root cause investigation
1. Read the whole error, warning and stack trace. Note files, lines, codes.
2. Reproduce consistently with the smallest command. Write down exact steps and output. Cannot reproduce? Gather more data; do not guess.
3. Check recent changes: `git log`, `git diff`, dependency and config changes, environment differences.
4. Multi-component flows (UI -> API -> service -> DB, CI -> build -> deploy): add temporary logging at each boundary (what enters, what leaves, config seen). Run once. Find the layer where it breaks.
5. Trace the bad value backward to its source (see `root-cause-tracing.md`).

## Phase 2 - Pattern analysis
6. Find similar working code in the repo. Read the reference completely.
7. List every difference between working and broken, however small.

## Phase 3 - Hypothesis
8. Write one hypothesis: "X is the root cause because Y."
9. Test it with the smallest possible change, one variable at a time.
10. Wrong? Form a new hypothesis. Do not stack fixes. Say "I don't understand X" when true.

## Phase 4 - Fix
11. Write a failing test that reproduces the bug (`test-driven-development`).
12. Make one fix at the source. No "while I'm here" changes.
13. Run the test and full suite (`verification-before-completion`). Remove temporary logging.
14. If the fix fails: under 3 attempts, go back to Phase 1 with the new information. At 3 failed attempts, STOP and discuss the design with the human; each fix revealing a new problem elsewhere means the architecture is the issue.

## Supporting techniques (in this folder)
- `root-cause-tracing.md` - follow the call chain back to the original trigger
- `defense-in-depth.md` - after the fix, validate at each layer so the bug becomes impossible
- `condition-based-waiting.md` - replace sleeps with condition polling (flaky tests)

## Red flags (return to Phase 1)
"Quick fix for now", "just try X", several changes at once, "probably X", proposing fixes before tracing, "one more attempt" after 2 failures.

## Output
```
Reproduction: <command> -> <observed>
Evidence: <log lines / boundary where data went wrong>
Root cause: <one sentence> (<file:line>)
Fix: <change>; regression test: <name>
Verification: <commands and results>
```

## Safety
- Redact logs before sharing. Never paste secrets, tokens, PII or production records.
- Do not debug against production or shared data; reproduce locally or in a test environment.
- Do not run destructive commands without human approval.
- A human reviews every change before merge.
