<!-- Suggested macro: !modernize-slice | practice: P1 pr-slicing; P4 plan-then-implement; P6 verify-before-done -->
# Modernization / Migration Slice

## Overview
Migrate one bounded slice of a codebase (for example one module from Java 8 to 17, one service from .NET Framework to .NET 8, one package from JavaScript to TypeScript, one framework API to its replacement) with behavior pinned by tests, delivered as a small draft PR.

## What's Needed From User
- Repository, base branch, and the exact slice (module, folder or file list)
- Source and target (language/framework/library versions) and the team's migration guide if any
- Definition of "behavior unchanged" (tests that must keep passing, contracts)
- Approval of the slice plan before implementation

## Procedure
1. Read `AGENTS.md`, the language instructions, and any migration guide provided.
2. Inventory the slice: files, public APIs, dependencies, tests, and usages from outside the slice.
3. Write a slice plan: steps, characterization tests needed, risks, PR size estimate (under {{MAX_PR_LINES}} lines or split further). Wait for approval.
4. Create branch `modernize/<slice-name>`.
5. Add characterization tests for untested behavior; confirm they pass on the old code; commit.
6. Migrate in small mechanical steps (for example tooling/config, then syntax, then API replacements); build and test after each; commit each step.
7. Run full build, tests and lint; compare with the baseline.
8. Open a draft PR: slice scope, steps, test evidence before/after, remaining work for the next slice.

## Specifications
- Public behavior and contracts unchanged; characterization tests and existing tests pass.
- Only files in the approved slice changed (plus required build config).
- PR includes baseline vs after results and the next-slice recommendation.

## Advice and Pointers
- Expand before contract: keep old and new paths working together until consumers move.
- Prefer official migration tools and codemods for mechanical changes; review their output.
- Keep commits mechanical and reviewable; do not mix refactors with migration steps.

## Forbidden Actions
- Do not migrate outside the approved slice or change behavior intentionally.
- Do not delete tests or lower coverage to pass.
- Do not change CI, deployment, or infrastructure without approval.
- Do not merge or deploy; no secrets or production data anywhere.
