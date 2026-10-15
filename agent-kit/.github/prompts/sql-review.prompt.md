---
description: 'Review SQL or stored procedures for injection, correctness, performance and migration safety. Read-only.'
argument-hint: 'SQL file, procedure, or selection'
agent: 'ask'
---
<!-- practice: P2 pr-readiness-selfcheck -->

Review ${input:target:the selected SQL (#selection) or file} for {{DB_ENGINE}}. Report only.

Check:
1. Injection: dynamic SQL from parameters without `sp_executesql` parameters / `QUOTENAME`.
2. Correctness: NULL handling, join cardinality (duplicates), implicit conversions, transaction boundaries, error handling (`TRY/CATCH`, `XACT_ABORT`).
3. Performance: non-sargable predicates, `SELECT *`, cursors/loops, missing or redundant indexes (suggest, with reasoning), parameter sniffing risk, unbounded result sets.
4. Safety: destructive statements, `DELETE`/`UPDATE` without `WHERE`, missing rollback for migrations, locking on large tables.
5. Style: schema-qualified names, explicit columns, header comment.

Output:
```
| Severity | Line | Issue | Why | Suggested rewrite |
|---|---|---|---|---|
Execution plan to check: <what to look for, which query>
Test to add: <data setup and expected result, synthetic data only>
```

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
