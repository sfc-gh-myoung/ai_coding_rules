---
schema_version: v4.0
rule_version: v3.0.0
description: 'Snowflake SQL file patterns: file headers, COPY INTO and CREATE VIEW syntax, qualified names, and CLI-safe idempotent DDL.'
last_updated: 2026-10-06
keywords:
  - kw:SQL file headers
  - kw:COPY INTO ON_ERROR placement
  - kw:CREATE VIEW COMMENT syntax
  - kw:fully qualified object names
  - kw:CLI templating reserved characters
  - kw:idempotent DDL patterns
  - ext:.sql
token_budget: ~1800
context_tier: High
depends:
  required:
    - 100-snowflake-core.md
  optional:
    - 130-snowflake-demo-sql.md
    - 102a-snowflake-sql-automation.md
    - 112-snowflake-snowcli.md
---
# Snowflake SQL: Core File Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Essential SQL file authoring patterns for Snowflake. Load for any SQL file creation.

## Scope

**What This Rule Covers:**
Essential patterns for Snowflake SQL files: standard headers, COPY INTO syntax, CREATE VIEW syntax, fully qualified object names, CLI reserved character handling, idempotent DDL, CTE naming, and JOIN column qualification. Applies to both demo and production SQL; environment-specific idempotent patterns are extended in `130-snowflake-demo-sql.md` (demo) and `102a-snowflake-sql-automation.md` (production).

**When to Load This Rule:**
- Writing or reviewing Snowflake SQL files (.sql)
- Using COPY INTO for data loading or CREATE VIEW for views
- Ensuring CLI compatibility (snow sql, snowsql)
- Setting up SQL file standards for a project

## Contract

### Inputs and Prerequisites

- Snowflake account with SYSADMIN or equivalent role, running warehouse, target database/schema created
- USAGE on target database and schema; CREATE TABLE/VIEW privileges on schema
- COPY INTO: USAGE on stage; for external stages, storage integration configured and IAM/SAS trust policy verified
- Snowflake CLI (`snow sql`) or Snowsight for execution

### Mandatory

- **File header:** Every SQL file must begin with the standard header block (filename, description, prerequisites, creates); add parameters and usage block when the file uses templated variables
- **Fully qualified names:** Use `DATABASE.SCHEMA.OBJECT` for all objects in reusable SQL files; unqualified names depend on session context and break in CLI/automation
- **COPY INTO syntax:** `ON_ERROR` is a COPY INTO option, not a FILE_FORMAT option; placing it inside `FILE_FORMAT = (...)` causes a syntax error
- **CREATE VIEW syntax:** `COMMENT` must appear before `AS`; placing it after AS causes a syntax error
- **Reserved characters:** SQL executed via CLI that contains `&`, `<%`, `%>`, `{{`, or `}}` must use `snow sql --enable-templating NONE`; never replace `&` with `and` in data values — fix at the CLI layer
- **Rerunnable DDL:** `CREATE TABLE IF NOT EXISTS` preserves an existing table but does not reconcile its definition. `CREATE OR REPLACE TABLE` replaces an existing table; use only where that loss is authorized. Replacing a view can affect grants and dependent objects: inspect those effects and obtain authorization first. Use `EXPLAIN` only for applicable query statements; it does not establish that DDL is safe to execute.
- **JOIN column qualification:** Qualify all SELECT-clause columns with table aliases in JOINs; shared column names (`STATUS`, `ID`, `CREATED_AT`, `UPDATED_AT`) cause `ambiguous column name` compile errors
- **CTE naming:** Use descriptive names reflecting purpose (`filtered_orders`, `daily_revenue`); never use generic placeholders (`cte1`, `temp`, `data`)
- **Dynamic identifiers:** DDL requires literal identifier tokens; use `SET var = expr; ... IDENTIFIER($var)` for dynamic values (e.g., `GRANT ROLE r TO USER IDENTIFIER($MY_USER)`)

### Execution Steps

1. Begin every SQL file with the standard header; add parameters/usage block for templated files
2. Use fully qualified `DATABASE.SCHEMA.OBJECT` names throughout
3. Place `ON_ERROR` outside `FILE_FORMAT = (...)` in all COPY INTO statements
4. Place `COMMENT = '...'` before `AS` in all CREATE VIEW statements
5. Execute via CLI with `--enable-templating NONE` when the file contains reserved characters
6. Choose idempotent pattern: `IF NOT EXISTS` for production tables; `OR REPLACE` for views and demo/staging tables only
7. Qualify all SELECT-clause columns with table aliases in any JOIN

**Example — standard SQL file header:**
```sql
-- ============================================================================
-- Filename: 01_customer_analytics_setup.sql
-- Description: Create customer analytics schema and core tables
--
-- Prerequisites: Database ANALYTICS_DB must exist
-- Creates: CUSTOMER_ANALYTICS schema, 3 tables, 2 views
-- ============================================================================
```

**Example — COPY INTO with ON_ERROR correctly placed:**
```sql
COPY INTO ANALYTICS_DB.SALES.ORDERS
FROM @ANALYTICS_DB.SALES.DATA_STAGE
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '"')
ON_ERROR = 'CONTINUE';
```

**Example — qualify all columns in JOINs:**
```sql
SELECT l.CUSTOMER_ID, l.TOTAL_QUERIES, l.ERROR_COUNT
FROM MY_DB.MY_SCHEMA.latest_metrics l
LEFT JOIN MY_DB.MY_SCHEMA.worker_heartbeats h
  ON h.RUN_ID = l.RUN_ID AND h.WORKER_ID = l.WORKER_ID;
```

### Validation

- [ ] Every SQL file has a complete standard header
- [ ] All objects fully qualified (DATABASE.SCHEMA.OBJECT)
- [ ] `ON_ERROR` is outside `FILE_FORMAT = (...)` in all COPY INTO statements
- [ ] `COMMENT` appears before `AS` in all CREATE VIEW statements
- [ ] No unescaped reserved characters (`&`, `<%`, `%>`, `{{`, `}}`) in CLI-executed SQL, or `--enable-templating NONE` is used
- [ ] `CREATE OR REPLACE TABLE` is absent from production files (data loss risk); `IF NOT EXISTS` used instead
- [ ] All SELECT-clause columns qualified with table aliases in JOINs
- [ ] CTE names are descriptive; no `cte1`, `temp`, `data`
- [ ] Any constraint claims are checked against current product documentation; data integrity is verified independently of declared constraints
- [ ] Record whether SQL was compiled, executed, or neither; never report an unperformed check as passed

**Negative tests — must never appear in reviewed SQL files:**
- `ON_ERROR` inside `FILE_FORMAT = (...)` block
- `COMMENT = '...'` placed after `AS` in CREATE VIEW
- Unqualified object names in reusable SQL files
- `&` in CLI-executed SQL without `--enable-templating NONE`

## References

- [COPY INTO (Table)](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) — Data loading reference; `ON_ERROR` is listed under COPY INTO options, not FILE_FORMAT
- [CREATE VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-view) — Syntax showing COMMENT placement before AS
- [CREATE TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-table) — Table creation including IF NOT EXISTS and OR REPLACE semantics
- [CREATE FILE FORMAT](https://docs.snowflake.com/en/sql-reference/sql/create-file-format) — FILE_FORMAT options (ON_ERROR is absent here, confirming placement)
- [snow sql CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/sql/sql-command) — `--enable-templating NONE` flag reference
- [IDENTIFIER function](https://docs.snowflake.com/en/sql-reference/identifier-fn) — Dynamic identifier pattern for DDL
