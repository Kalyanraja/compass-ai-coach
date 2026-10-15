---
name: verification-before-completion
description: Use whenever you are about to say work is done, fixed, passing or ready, and before committing, opening a PR, or moving to the next task. Requires running the command that proves the claim in this session and quoting its output. Evidence before assertions, always.
metadata:
  practice: P6 verify-before-done
  source: adapted from obra/superpowers verification-before-completion (MIT)
---

# Verification Before Completion

No completion claims without fresh verification evidence.

## Gate (run before any success statement)
1. **Identify** the command that proves the claim.
2. **Run** it fully, now (not an earlier run, not a partial run).
3. **Read** the whole output: exit code, failure and skip counts, warnings.
4. **Compare**: does the output prove the claim?
   - No -> state the actual status with the evidence.
   - Yes -> state the claim with the evidence.

## What proves what
| Claim | Requires | Not enough |
|---|---|---|
| Tests pass | test command output with 0 failures | earlier run, "should pass" |
| Build succeeds | build exit code 0 | linter passing |
| Lint clean | linter output 0 errors | partial run |
| Bug fixed | original reproduction now passes | code changed |
| Regression test works | fails without fix, passes with fix | passes once |
| Requirements met | checklist against spec, item by item | tests green |
| Agent/subagent finished | you inspected the diff | its success report |

## Red flags
"Should work now", "looks correct", "probably", "Done!" or "Perfect!" before running anything, trusting another agent's report, being tired.

## Report format
```
Claim: <what is true>
Evidence:
- `<command>` -> <exit code / summary line>
Not verified: <anything you could not run, and why>
```

## Stop and ask when
- You cannot run the verification (missing env, credentials, services). Say so; do not imply success.

## Safety
- Do not paste secrets or personal data from command output; redact.
- Verification supports human review; it never replaces it.
