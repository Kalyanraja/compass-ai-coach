---
name: requesting-code-review
description: Use after completing a task or feature and before merging, to get a focused review of the change against its plan or requirements. Packages exactly the context a reviewer needs (what was built, requirements, git range), dispatches a read-only reviewer or runs a fresh-eyes self-review, and triages findings by severity.
metadata:
  practice: P2 pr-readiness-selfcheck
  source: adapted from obra/superpowers requesting-code-review (MIT)
---

# Requesting Code Review

Review early, review often. Give the reviewer crafted context, never your whole session history.

## When
- After each plan task (for larger work), after a major feature, and always before opening a PR.
- When stuck, before a big refactor, or after fixing a complex bug.

## Steps
1. Get the range: `BASE=$(git merge-base origin/{{DEFAULT_BRANCH}} HEAD)`, `HEAD=$(git rev-parse HEAD)`.
2. Fill the review brief:
```
What was implemented: <2-3 sentences>
Requirements / plan: <path or ticket>
Range: <BASE>..<HEAD>   (git diff --stat BASE..HEAD)
Focus: <risky areas>
```
3. Choose the reviewer:
   - Claude Code: delegate to the `code-reviewer` subagent with the brief.
   - Copilot: switch to the `PR Reviewer` custom agent, or run `/self-review`.
   - Devin or no subagent support: review it yourself in a fresh pass using the checklist below, reading only the diff and the requirements.
4. Triage the findings:
   - Critical -> fix now (with a failing test first).
   - Important -> fix before continuing.
   - Minor -> note in PR or ledger.
   - Wrong -> push back with evidence (see `receiving-code-review`).

## Reviewer checklist
- Plan alignment: everything planned is present; deviations are justified.
- Correctness and edge cases; error handling.
- Tests: real behavior, would fail without the change, cover edge cases, all passing.
- Security: secrets, injection, authorization, sensitive logging.
- Production readiness: migrations, backward compatibility, docs.
- Reviewer stays read-only: no edits, no branch changes.

## Reviewer output
```
Strengths: <file:line specifics>
Issues: Critical / Important / Minor, each with file:line, problem, fix
Set aside: <behaviors considered out of scope, with reason>
Assessment: Ready | Ready with fixes | Not ready - <reason>
```

## Safety
- The brief must not include secrets, PII or production data.
- Agent review supplements human review; it never replaces approval by a person.
