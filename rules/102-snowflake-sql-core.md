# Snowflake SQL: Core File Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential SQL file authoring patterns for Snowflake.
> Load for any SQL file creation. Demo and production rules extend this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** SQL files, file headers, COPY INTO, FILE_FORMAT, CREATE VIEW, fully qualified names, idempotent, reserved characters, CLI compatibility, ON_ERROR
**TokenBudget:** ~3000
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Essential SQL file authoring patterns for Snowflake: file headers, COPY INTO syntax, CREATE VIEW syntax, fully qualified object names, reserved character handling for CLI compatibility, and idempotent pattern foundations. This rule provides general patterns that apply to both demo and production SQL files.

**When to Load This Rule:**
- Writing any Snowflake SQL files (.sql)
- Using COPY INTO for data loading
- Creating views with documentation
- Ensuring CLI compatibility (snow sql, snowsql)
- Setting up SQL file standards for a project

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake fundamentals

**Related:**
- **130-snowflake-demo-sql.md** - Demo/workshop SQL patterns (extends this rule)
- **102a-snowflake-sql-automation.md** - Production CI/CD patterns (extends this rule)
- **112-snowflake-snowcli.md** - Snowflake CLI usage

### External Documentation

**Snowflake:**
- [SQL Command Reference](https://docs.snowflake.com/en/sql-reference-commands.html) - Complete SQL syntax
- [COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html) - Data loading reference
- [CREATE TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-table.html) - Table creation syntax
- [CREATE VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-view.html) - View creation syntax
- [FILE FORMAT](https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html) - File format options

## Contract

### Inputs and Prerequisites

- Target database/schema identified
- Snowflake CLI or Snowsight access
- Understanding of target environment (demo vs production)

### Mandatory

- File headers with filename, description, prerequisites
- Fully qualified object names (DATABASE.SCHEMA.OBJECT)
- Correct COPY INTO syntax (ON_ERROR outside FILE_FORMAT)
- Correct CREATE VIEW syntax (COMMENT before AS)
- No reserved characters in identifiers/comments

### Forbidden

- `ON_ERROR` inside `FILE_FORMAT` (syntax error)
- Reserved template characters in SQL: `&`, `<%`, `%>`, `{{`, `}}`
- Unqualified object names in reusable SQL files
- `COMMENT` after `AS` in CREATE VIEW

### Execution Steps

1. Create file with standard header (filename, description, prerequisites)
2. Use fully qualified names for all objects
3. Apply correct syntax for COPY INTO and CREATE VIEW
4. Avoid reserved characters for CLI compatibility
5. Choose idempotent pattern based on environment (demo vs production)

### Output Format

SQL files with .sql extension, UTF-8 encoding, Unix line endings

### Validation

**Test Requirements:**
- SQL compiles without syntax errors
- Executes successfully via CLI (snow sql, snowsql)
- No template variable expansion errors

**Success Criteria:**
- File header present and complete
- All objects fully qualified
- No reserved character issues
- Correct syntax for all statements

### Design Principles

- **Clarity First**: Self-documenting headers and structure
- **CLI Compatible**: Works with snow sql, snowsql, CI/CD pipelines
- **Environment Agnostic**: Patterns apply to demo and production
- **Explicit Qualification**: DATABASE.SCHEMA.OBJECT always

### Post-Execution Checklist

- [ ] File header includes filename, description, prerequisites
- [ ] All object names fully qualified (DB.SCHEMA.OBJECT)
- [ ] No reserved characters (`&`, `<%`, `%>`, `{{`, `}}`)
- [ ] COPY INTO uses ON_ERROR outside FILE_FORMAT
- [ ] CREATE VIEW places COMMENT before AS
- [ ] SQL executes without errors via CLI

## File Header Standard

### Required Header Format

**Rule:** All SQL files must include a documentation header

**Template:**
```sql
-- ============================================================================
-- Filename: <filename>.sql
-- Description: <Brief one-line description>
--
-- Prerequisites: <What must exist before running>
-- Creates: <What this script creates or modifies>
-- ============================================================================
```

**Example:**
```sql
-- ============================================================================
-- Filename: customer_analytics_setup.sql
-- Description: Create customer analytics schema and core tables
--
-- Prerequisites: Database ANALYTICS_DB must exist
-- Creates: CUSTOMER_ANALYTICS schema, 3 tables, 2 views
-- ============================================================================
```

### Extended Header (Production Templates)

**Use when:** SQL files have parameterized variables

```sql
-- ============================================================================
-- Filename: <filename>.sql
-- Description: <Brief description>
--
-- Parameters:
--   DATABASE - Target database (e.g., DEV_DB, PROD_DB)
--   SCHEMA   - Target schema (e.g., ANALYTICS)
--
-- Usage:
--   snow sql -D DATABASE=DEV -D SCHEMA=ANALYTICS -f <filename>.sql
--
-- Example:
--   snow sql -D DATABASE=PROD -D SCHEMA=CUSTOMER -f <filename>.sql
--
-- Prerequisites: <Dependencies>
-- Creates: <Objects created>
-- Idempotency: <Explain why safe to rerun>
-- ============================================================================
```

## COPY INTO Syntax

### Basic Pattern

**Rule:** COPY INTO loads files from stages into tables

```sql
COPY INTO <database>.<schema>.<table>
FROM @<database>.<schema>.<stage>
PATTERN = '.*filename_pattern.*\\.csv'
FILE_FORMAT = (
    TYPE = 'CSV',
    SKIP_HEADER = 1,
    FIELD_DELIMITER = ',',
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
);
```

### Critical: ON_ERROR Placement

**Rule:** `ON_ERROR` is a COPY INTO parameter, NOT a FILE_FORMAT parameter

**Correct:**
```sql
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';
```

**Incorrect:**
```sql
-- CAUSES SYNTAX ERROR
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (
    TYPE = 'CSV',
    ON_ERROR = 'CONTINUE'  -- WRONG: ON_ERROR is not a FILE_FORMAT option
);
```

### Common FILE_FORMAT Options

```sql
FILE_FORMAT = (
    TYPE = 'CSV',
    SKIP_HEADER = 1,
    FIELD_DELIMITER = ',',
    FIELD_OPTIONALLY_ENCLOSED_BY = '"',
    NULL_IF = ('NULL', 'null', ''),
    EMPTY_FIELD_AS_NULL = TRUE,
    TRIM_SPACE = TRUE
)
```

### Common COPY INTO Options

```sql
COPY INTO target_table
FROM @source_stage
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1)
PATTERN = '.*data.*\\.csv'
ON_ERROR = 'CONTINUE'           -- Skip bad rows
FORCE = TRUE                    -- Reload already-loaded files
PURGE = TRUE;                   -- Delete files after load
```

## CREATE VIEW Syntax

### COMMENT Placement

**Rule:** COMMENT must appear BEFORE the AS keyword

**Correct:**
```sql
CREATE OR REPLACE VIEW my_db.my_schema.my_view
COMMENT = 'Business-friendly view for dashboards'
AS
SELECT
    customer_id,
    order_count,
    total_spend
FROM my_db.my_schema.customer_orders;
```

**Incorrect:**
```sql
-- CAUSES SYNTAX ERROR
CREATE OR REPLACE VIEW my_db.my_schema.my_view AS
SELECT customer_id, order_count
FROM customer_orders
COMMENT = 'My view';  -- WRONG: COMMENT must be before AS
```

## Fully Qualified Object Names

### Rule

**Always use DATABASE.SCHEMA.OBJECT format in SQL files**

**Why:** Ensures scripts work regardless of session context

**Correct:**
```sql
CREATE TABLE ANALYTICS_DB.CUSTOMER_DATA.CUSTOMERS (...);

COPY INTO ANALYTICS_DB.CUSTOMER_DATA.ORDERS
FROM @ANALYTICS_DB.CUSTOMER_DATA.DATA_STAGE/orders.csv
FILE_FORMAT = (TYPE = 'CSV');

SELECT * FROM ANALYTICS_DB.CUSTOMER_DATA.VW_CUSTOMER_SUMMARY;
```

**Incorrect:**
```sql
-- Relies on session context - fragile
USE DATABASE ANALYTICS_DB;
USE SCHEMA CUSTOMER_DATA;
CREATE TABLE CUSTOMERS (...);  -- May fail in CLI automation
```

### When USE Is Acceptable

- Interactive sessions in Snowsight
- Single-file scripts executed as one unit
- Development/exploration only

## Reserved Characters (CLI Compatibility)

### Rule

**Avoid characters that CLI tools interpret as template variables**

**Why:** SQL files executed via `snow sql` or `snowsql` may fail with cryptic errors when reserved characters are present.

### Forbidden Characters

**Reserved characters to avoid in SQL files:**
- **`&`** - snow sql interprets as template variable prefix
- **`<%` `%>`** - snowsql interprets as variable delimiters
- **`{{` `}}`** - Jinja2, dbt interpret as template syntax

### Incorrect Examples

```sql
-- & in comments or strings causes CLI errors
CREATE TABLE departments (
    dept_name VARCHAR COMMENT 'R&D or Sales & Marketing'  -- FAILS in CLI
);

-- Template syntax in comments
-- Deploy to <%ENV%> environment  -- snowsql tries to expand this

CREATE SEMANTIC VIEW my_view AS
  DIMENSIONS (
    dept AS departments.dept_name
      SYNONYMS ('R&D', 'Sales & Marketing')  -- FAILS: & character
  );
```

### Correct Examples

```sql
-- Use 'and' instead of '&'
CREATE TABLE departments (
    dept_name VARCHAR COMMENT 'R and D or Sales and Marketing'
);

-- Plain text comments
-- Deploy to DEV or PROD environment

CREATE SEMANTIC VIEW my_view AS
  DIMENSIONS (
    dept AS departments.dept_name
      SYNONYMS ('R and D', 'Research and Development', 'Sales and Marketing')
  );
```

### Common Substitutions

**Replace reserved characters with alternatives:**
- **`R&D`** - Use `R and D` or `Research and Development`
- **`Sales & Marketing`** - Use `Sales and Marketing`
- **`P&L`** - Use `P and L` or `Profit and Loss`
- **`<%VAR%>`** - Use Snowflake CLI `--variable` flag instead

## Idempotent Patterns Overview

### Demo vs Production

SQL files should be rerunnable without errors. The specific patterns differ by environment:

**Demo environment (130-snowflake-demo-sql.md):**
- Tables: `CREATE OR REPLACE TABLE`
- Schemas: `CREATE SCHEMA IF NOT EXISTS`
- Views: `CREATE OR REPLACE VIEW`
- Data: Direct INSERT/COPY

**Production environment (102a-snowflake-sql-automation.md):**
- Tables: `CREATE TABLE IF NOT EXISTS` + `MERGE`
- Schemas: `CREATE SCHEMA IF NOT EXISTS`
- Views: `CREATE OR REPLACE VIEW`
- Data: MERGE for idempotent upserts

### Schema Creation (Both Environments)

```sql
CREATE SCHEMA IF NOT EXISTS my_db.my_schema
    COMMENT = 'Schema description';
```

### View Creation (Both Environments)

```sql
CREATE OR REPLACE VIEW my_db.my_schema.my_view
COMMENT = 'View description'
AS
SELECT ...;
```

**Views are always safe for CREATE OR REPLACE** - they store no data.

### Table Creation

**Demo environment:**
```sql
-- OK for demos - drops and recreates (data loss acceptable)
CREATE OR REPLACE TABLE my_db.my_schema.my_table (...);
```

**Production environment:**
```sql
-- Production-safe - preserves existing data
CREATE TABLE IF NOT EXISTS my_db.my_schema.my_table (...);

-- Use MERGE for updates
MERGE INTO my_db.my_schema.my_table AS target
USING source_data AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: ON_ERROR Inside FILE_FORMAT

**Problem:**
```sql
COPY INTO my_table FROM @my_stage
FILE_FORMAT = (TYPE = 'CSV', ON_ERROR = 'CONTINUE');
```

**Why It Fails:** ON_ERROR is a COPY INTO parameter, not a FILE_FORMAT option. Placing it inside FILE_FORMAT causes a syntax error.

**Correct Pattern:**
```sql
COPY INTO my_table FROM @my_stage
FILE_FORMAT = (TYPE = 'CSV')
ON_ERROR = 'CONTINUE';
```

### Anti-Pattern 2: COMMENT After AS in Views

**Problem:**
```sql
CREATE VIEW my_view AS SELECT * FROM t COMMENT = 'desc';
```

**Why It Fails:** COMMENT must appear before the AS keyword in CREATE VIEW syntax.

**Correct Pattern:**
```sql
CREATE VIEW my_view COMMENT = 'desc' AS SELECT * FROM t;
```

### Anti-Pattern 3: Unqualified Names in Reusable SQL

**Problem:**
```sql
CREATE TABLE customers (...);
SELECT * FROM orders;
```

**Why It Fails:** Relies on session context. Fails when executed via CLI or in different database/schema contexts.

**Correct Pattern:**
```sql
CREATE TABLE my_db.my_schema.customers (...);
SELECT * FROM my_db.my_schema.orders;
```

### Anti-Pattern 4: Reserved Characters in SQL Files

**Problem:**
```sql
COMMENT = 'Sales & Marketing data'
```

**Why It Fails:** The `&` character is interpreted as a template variable prefix by snow sql CLI, causing cryptic errors.

**Correct Pattern:**
```sql
COMMENT = 'Sales and Marketing data'
```
