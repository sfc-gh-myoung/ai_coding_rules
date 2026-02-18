# Snowflake SQL: Core File Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential SQL file authoring patterns for Snowflake.
> Load for any SQL file creation. Demo and production rules extend this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-02-18
**Keywords:** SQL files, file headers, COPY INTO, FILE_FORMAT, CREATE VIEW, fully qualified names, idempotent, reserved characters, CLI compatibility, ON_ERROR, JOIN, ambiguous column, table alias
**TokenBudget:** ~3400
**ContextTier:** High
**Depends:** 100-snowflake-core.md
**LoadTrigger:** ext:.sql, kw:sql

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
- Reserved template characters in SQL without `--enable-templating NONE`: `&`, `<%`, `%>`, `{{`, `}}`
- Unqualified object names in reusable SQL files
- `COMMENT` after `AS` in CREATE VIEW

### Execution Steps

1. Create file with standard header (filename, description, prerequisites)
2. Use fully qualified names for all objects
3. Apply correct syntax for COPY INTO and CREATE VIEW
4. Use `--enable-templating NONE` when executing SQL with reserved characters via CLI
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
- [ ] JOINs use table aliases and qualify all columns
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

**Disable client-side template expansion when SQL contains reserved characters**

**Why:** `snow sql` (LEGACY mode, the default) interprets `&` as a template variable prefix. The correct fix is `--enable-templating NONE`, NOT substituting characters in data.

### Reserved Characters

**Characters that CLI tools interpret as template syntax:**
- **`&`** - `snow sql` LEGACY mode interprets as template variable prefix
- **`<%` `%>`** - `snowsql` interprets as variable delimiters
- **`{{` `}}`** - Jinja2, dbt interpret as template syntax

### Error Message Pattern

When `&` is present and templating is not disabled, `snow sql` produces these errors:
```
Warning: &{ ... } syntax is deprecated and will no longer be supported. Use <% ... %> syntax instead.
SQL template rendering error: 'W' is undefined
SQL template rendering error: 'Ms' is undefined
```

The text after `&` is treated as a variable name (e.g., `A&W` → variable `W`, `M&Ms` → variable `Ms`).

### The Fix: `--enable-templating NONE`

**Do NOT replace `&` with `and` in data.** That corrupts real brand names, product descriptions, and other data that legitimately contains `&`.

The correct fix is to disable client-side template expansion at the CLI layer:

```bash
# Correct: disable templating so & is passed through to Snowflake
snow sql --enable-templating NONE -c my_connection -f sql/03_seed_data.sql

# In Python wrappers, add the flag to the command builder:
cmd = [*get_snow_command(), "sql", "--enable-templating", "NONE", "-c", connection]
```

`--enable-templating NONE` should be the default for all non-templated SQL execution. Only use LEGACY or other modes when you actually need client-side variable expansion.

### Incorrect Approach (Data Substitution)

```sql
-- WRONG: Do NOT corrupt data to work around CLI templating
INSERT INTO products (name, brand) VALUES
('M and Ms Milk Chocolate 1.69oz', 'M and Ms'),  -- WRONG: corrupts brand name
('A and W Root Beer 20oz', 'A and W'),             -- WRONG: corrupts brand name
('PB and J Sandwich on White', 'Fresh');           -- WRONG: corrupts product name
```

### Correct Approach (Disable Templating)

```sql
-- CORRECT: Keep real brand names with &, execute with --enable-templating NONE
INSERT INTO products (name, brand) VALUES
('M&Ms Milk Chocolate 1.69oz', 'M&Ms'),
('A&W Root Beer 20oz', 'A&W'),
('PB&J Sandwich on White', 'Fresh');
```

### When Templating Cannot Be Disabled

For `<%` `%>` in `snowsql` or `{{` `}}` in dbt/Jinja contexts where you cannot disable templating, avoid these characters in SQL comments and string literals. Use the `--variable` flag or dbt `var()` for actual variable substitution instead of embedding template syntax in SQL.

### SQL Single-Quote Escaping

Brand names with apostrophes (e.g., Frank's RedHot) must use doubled single quotes inside SQL string literals:

```sql
-- Correct: apostrophe escaped as '' inside SQL string
INSERT INTO products (name, brand) VALUES
('Frank''s RedHot Original Cayenne Pepper Sauce 5oz', 'Frank''s RedHot');
```

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

-- Also common in seed data INSERT statements:
INSERT INTO items (name, brand) VALUES
('M&Ms Milk Chocolate 1.69oz', 'M&Ms'),
('A&W Root Beer 20oz', 'Keurig Dr Pepper');
```

**Why It Fails:** The `&` character is interpreted as a template variable prefix by snow sql CLI. The CLI attempts to expand `&W`, `&Ms`, etc. as variables, producing `SQL template rendering error: 'X' is undefined`. This is especially common in demo seed data containing brand names like M&Ms, A&W, PB&J.

**Correct Pattern:**
```sql
COMMENT = 'Sales and Marketing data'

INSERT INTO items (name, brand) VALUES
('M and Ms Milk Chocolate 1.69oz', 'M and Ms'),
('A and W Root Beer 20oz', 'Keurig Dr Pepper');
```

### Anti-Pattern 5: Unqualified Columns in JOINs

**Problem:**
```sql
-- Both tables have ERROR_COUNT column - ambiguous
SELECT
    SUM(TOTAL_QUERIES) AS TOTAL_OPS,
    SUM(ERROR_COUNT) AS ERROR_COUNT
FROM latest_metrics l
LEFT JOIN worker_heartbeats h
  ON h.RUN_ID = l.RUN_ID AND h.WORKER_ID = l.WORKER_ID;
```

**Why It Fails:** When joining tables that share column names, Snowflake throws `SQL compilation error: ambiguous column name`. Common offenders: `ERROR_COUNT`, `STATUS`, `TIMESTAMP`, `ID`, `NAME`, `CREATED_AT`, `UPDATED_AT`.

**Correct Pattern:**
```sql
-- Always qualify columns with table alias in JOINs
SELECT
    SUM(l.TOTAL_QUERIES) AS TOTAL_OPS,
    SUM(l.ERROR_COUNT) AS ERROR_COUNT
FROM latest_metrics l
LEFT JOIN worker_heartbeats h
  ON h.RUN_ID = l.RUN_ID AND h.WORKER_ID = l.WORKER_ID;
```

**Rule:** When writing JOINs, qualify ALL columns in the SELECT clause with table aliases, even if currently unambiguous. This prevents future breakage when columns are added to joined tables.
