<!-- Suggested macro: !dep-upgrade | practice: P1 pr-slicing; P6 verify-before-done -->
# Dependency Upgrade

## Overview
Upgrade one dependency (or one tightly coupled group) to a target version, fix breakages, and open a draft PR with baseline and after results.

## What's Needed From User
- Repository and base branch
- Package name, current version, target version
- Release notes or migration guide text if Devin cannot reach them
- The approved package registry or mirror (`{{PACKAGE_REGISTRY}}`)

## Procedure
1. Create branch `deps/<package>-<target-version>`.
2. Run build and full tests on the base; record results as the baseline.
3. Read the changelog/migration notes between versions; list breaking changes; search the codebase for affected usages.
4. Update the version using the package manager (never edit lockfiles by hand).
5. Build; fix compile errors and deprecations in small commits, running tests after each group.
6. Run full build, tests and lint; compare with baseline.
7. Open a draft PR: versions, breaking changes and how each was handled, baseline vs after results, transitive changes, risk and rollback.

## Specifications
- Only the requested dependency (and its required companions) changed.
- Build, tests and lint pass, or the PR clearly lists what still fails and why.
- Lockfile updated by the package manager.

## Advice and Pointers
- Major versions: check for removed APIs, changed defaults and configuration keys.
- Prefer the official migration guide's recommended replacements.
- If the upgrade forces other major upgrades, stop and report the chain.

## Forbidden Actions
- Do not upgrade unrelated packages or reformat unrelated code.
- Do not pull packages from unapproved sources or add new packages.
- Do not disable tests, lint rules or security checks to get green.
- Do not merge or deploy.
- Do not use or expose secrets, credentials, PII or production data.
- Do not skip human review: deliver a draft PR or a report for a person to review and merge.
