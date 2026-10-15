---
description: 'SQL and stored procedure rules (SQL Server/T-SQL first, portable where possible): safety, performance, migrations.'
applyTo: '**/*.sql'
---
<!-- practice: P2 pr-readiness-selfcheck -->

# SQL rules

## Safety
- Never run or generate destructive statements (`DROP`, `TRUNCATE`, `DELETE`/`UPDATE` without `WHERE`) against shared environments. Destructive migrations need a human-approved rollback script.
- No dynamic SQL built from input. If dynamic SQL is required, use `sp_executesql` with parameters and `QUOTENAME` for identifiers.
- Never include real customer or production data in scripts, seeds or examples. Use synthetic rows.
- Grant least privilege. Do not add `GRANT` statements without approval.

## Style
- Explicit column lists. Never `SELECT *` in production code; never `INSERT` without a column list.
- Schema-qualify objects (`dbo.Orders`). Consistent casing per repo convention ({{SQL_STYLE}}).
- Stored procedures: `SET NOCOUNT ON;`, validate parameters, `TRY...CATCH` with `THROW`, explicit transactions with `XACT_ABORT ON` when modifying multiple tables.
- Comment the purpose, parameters and side effects at the top of each procedure.

## Performance
- Keep predicates sargable: no functions on indexed columns in `WHERE`/`JOIN`, no leading `%` wildcards, matching data types.
- Avoid cursors and row-by-row loops when a set-based statement works.
- Check the execution plan for scans on large tables; propose indexes with reasoning, never add them silently.
- Paginate with keyset or `OFFSET ... FETCH` with a deterministic `ORDER BY`.

## Migrations
- One migration per change, idempotent where possible (`IF NOT EXISTS`). Include a tested rollback.
- Describe data volume impact and locking risk in the PR.
- Never include secrets, credentials, PII or production data.
- A human reviews every change before merge.
