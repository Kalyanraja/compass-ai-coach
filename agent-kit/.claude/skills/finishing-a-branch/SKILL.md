---
name: finishing-a-branch
description: Use when implementation on a branch is complete and you need to decide how to integrate it (open a PR, keep the branch, or discard on explicit request). Verifies tests first, runs the PR readiness self-check, then presents exact options and executes only what the human chooses. Never merges to shared branches on its own.
metadata:
  practice: P2 pr-readiness-selfcheck; P6 verify-before-done
  source: adapted from obra/superpowers finishing-a-development-branch (MIT)
---

# Finishing a Branch

Verify, present options, execute the human's choice, clean up.

## Steps
1. **Verify**: run the full test suite. If anything fails, report the failures and stop. The options come only after a green suite.
2. **Readiness**: run `pr-readiness-selfcheck`. Fix blocking items or report them.
3. **Confirm base branch**: "This branch split from `<base>`, correct?" if not already known.
4. **Present exactly these options** and wait:
```
Implementation complete and verified.
1. Push branch and open a pull request against <base>
2. Keep the branch as-is (I'll handle it later)
Which option?
```
5. **Execute**:
   - Option 1: `git push -u origin <branch>`, then open the PR with the team's template (forge CLI or the URL printed by push), using the drafted description. Report the PR link.
   - Option 2: report branch name and location.
6. **Discard only on explicit request**: list the branch and commits that will be lost and require the human to type `discard`. Then delete.

## Never
- Merge into `main`/`release` branches, force-push shared branches, or delete work without explicit confirmation.
- Use `--force` to remove a worktree that has uncommitted files; show the files and ask.

## Safety
- Final check that no secrets or production data are in the commits before pushing.
- A human reviews and merges the PR.
