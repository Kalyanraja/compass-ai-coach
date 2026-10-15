---
name: pr-slicing
description: Use when a change or branch is too large or mixes concerns (refactor plus feature, many files, over the PR size target), or when planning work that will exceed one small PR. Splits the work into an ordered stack of small, independently buildable and reviewable PRs with tests per slice.
metadata:
  practice: P1 pr-slicing
  source: original Compass content; ordering informed by github/spec-kit story-based task grouping (MIT)
---

# PR Slicing

Small PRs get reviewed faster and break less. Slice by concern, keep every slice green.

## Signals you need to slice
- Over {{MAX_PR_LINES}} changed lines (excluding generated files and lockfiles), or more than ~15 files.
- The PR description needs the word "also".
- Renames/moves/formatting mixed with behavior changes.
- Schema or API changes shipped together with their consumers.

## Steps
1. List every change in the diff (or planned work) and tag it: `mechanical`, `refactor`, `schema/config`, `behavior`, `tests`, `cleanup`, `docs`.
2. Group by concern. Each group becomes a candidate slice.
3. Order slices so each builds, passes all tests and is safe to merge alone:
   1. Mechanical (rename, move, format) - no behavior change
   2. Refactor/preparatory seams - characterization tests prove no change
   3. Additive schema/config/API (backward compatible: expand before contract)
   4. Behavior, one user story per slice, test-first, behind a feature flag if partially done
   5. Cleanup (remove old paths, flags) after rollout
4. For each slice define tests and how a reviewer verifies it.
5. Verify every requirement lands in some slice.

## Output
```
## Slicing plan: <N> PRs
| # | Title | Type | Files | ~Lines | Depends on | Tests / reviewer check |
Feature flag: <name or none>
Commands for the human (new branches from base, cherry-pick or `git checkout <branch> -- <paths>`; no force-push to shared branches)
Requirements coverage: <req -> slice>
```

## Stop and ask when
- A slice cannot be made backward compatible, or splitting needs a feature flag the team has not approved.

## Safety
- Never rewrite or force-push shared history. Suggest commands; the human runs history-changing ones.
- Each slice still passes the `pr-readiness-selfcheck`.
- Never include secrets, credentials, PII or production data.
