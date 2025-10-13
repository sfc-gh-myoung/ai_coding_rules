**Description:** Advanced SQL authoring patterns for Snowflake, focusing on CTEs, VARIANT extraction, cardinality control, and correct syntax patterns.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** SQL best practices, CTEs, VARIANT extraction, JOIN patterns, QUALIFY, window functions, set operations, UNION vs UNION ALL
**Version:** 1.6
**LastUpdated:** 2025-10-13

**TokenBudget:** ~1200
**ContextTier:** High

# Snowflake SQL Best Practices

## Purpose
Establish advanced SQL authoring patterns specifically for Snowflake, focusing on CTEs, VARIANT data extraction, cardinality control, and query optimization techniques for maintainable and performant data processing.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Advanced Snowflake SQL authoring patterns, CTEs, VARIANT handling, and query optimization

## Key Principles
- Use CTEs to segment logic; control join cardinality; prefer QUALIFY over nested subqueries for window filters.
- Extract/flatten VARIANT once in an early CTE; avoid repeated casts.
- Use APPROX_* functions where exact precision isn't required for performance at scale.
- Always use fully qualified object names (DATABASE.SCHEMA.OBJECT) in production and automation; USE statements don't persist across CLI sessions.
- Place COMMENT before AS in CREATE VIEW; keep ON_ERROR outside FILE_FORMAT in COPY INTO.
- Link to Snowflake docs for syntax; keep queries readable and maintainable.
- Document objects with COMMENT wherever supported; verify comment syntax per object type.

## 1. Advanced SQL Authoring
- **Requirement:** Use CTEs to modularize complex queries. Avoid excessive nesting (cap ~6 levels).
- **Requirement:** Control join cardinality by ensuring distinct keys or using semi-joins.
- **Requirement:** Use `QUALIFY` to filter window function results instead of subqueries.

## 2. Semi-Structured Data
- **Requirement:** Extract and flatten semi-structured `VARIANT` data in an early CTE.
- **Requirement:** Avoid repeated casting or navigation of `VARIANT` columns; perform extraction once.
- **Consider:** For high-cardinality operations, use `APPROX_COUNT_DISTINCT` instead of `COUNT(DISTINCT ...)` when exact precision is not required.

## 3. Common SQL Syntax Patterns

### COPY INTO Parameter Placement
- **Critical:** `ON_ERROR` is a COPY INTO parameter, not a FILE_FORMAT parameter
- **Rule:** Place `ON_ERROR` outside and after the FILE_FORMAT clause, or omit it (default is ABORT_STATEMENT)

**Incorrect:**
```sql
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    ON_ERROR = 'ABORT_STATEMENT'  -- ❌ Invalid - not a FILE_FORMAT parameter
);
```

**Correct:**
```sql
-- Option 1: Omit ON_ERROR (uses default ABORT_STATEMENT)
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
);

-- Option 2: Place ON_ERROR outside FILE_FORMAT
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (TYPE = 'CSV')
ON_ERROR = 'CONTINUE';
```

### CREATE VIEW Comment Syntax
- **Critical:** `COMMENT` must be placed before `AS` in CREATE VIEW statements
- **Rule:** Use `CREATE [OR REPLACE] VIEW name COMMENT = 'text' AS SELECT ...`

**Incorrect:**
```sql
CREATE OR REPLACE VIEW my_view AS
SELECT col1, col2
FROM my_table
COMMENT = 'My view description';  -- ❌ Syntax error - COMMENT after query
```

**Correct:**
```sql
CREATE OR REPLACE VIEW my_view
COMMENT = 'My view description'
AS
SELECT col1, col2
FROM my_table;
```

### CREATE TABLE Comment Syntax
- **Rule:** For tables, `COMMENT` can be placed after column definitions or as a table option

**Correct patterns:**
```sql
-- Pattern 1: Table-level comment
CREATE OR REPLACE TABLE my_table (
    col1 VARCHAR,
    col2 NUMBER
)
COMMENT = 'My table description';

-- Pattern 2: Column-level comments
CREATE OR REPLACE TABLE my_table (
    col1 VARCHAR COMMENT 'First column',
    col2 NUMBER COMMENT 'Second column'
);
```

### Commenting Other Object Types
- **Requirement:** Add descriptive `COMMENT` for objects whenever supported (e.g., databases, schemas, stages, file formats, tasks, pipes, streams, sequences, functions/procedures, views, tables, and columns).
- **Critical:** Comment syntax and placement vary by object type. Always verify the exact DDL syntax in Snowflake documentation for the specific object before use.

General patterns (verify per object type):

```sql
-- CREATE with table-like options (many objects support COMMENT as an option)
CREATE OR REPLACE <OBJECT_TYPE> <fully_qualified_name>
  [ ... object-specific options ... ]
  COMMENT = 'Purpose/ownership/lineage';

-- ALTER to add or update a comment (common pattern)
ALTER <OBJECT_TYPE> <fully_qualified_name>
  SET COMMENT = 'Updated description';
```

Examples (illustrative only; confirm syntax for your object type):

```sql
-- Schema
CREATE OR REPLACE SCHEMA my_db.my_schema COMMENT = 'Business entities for analytics';
ALTER SCHEMA my_db.my_schema SET COMMENT = 'Primary analytics schema';

-- Stage
CREATE OR REPLACE STAGE my_db.ingest.ext_stage COMMENT = 'External files landing';
ALTER STAGE my_db.ingest.ext_stage SET COMMENT = 'Raw file landing zone';

-- File format
CREATE OR REPLACE FILE FORMAT my_db.util.csv_fmt
  TYPE = CSV
  SKIP_HEADER = 1
  COMMENT = 'Standard CSV imports';
ALTER FILE FORMAT my_db.util.csv_fmt SET COMMENT = 'CSV with header row';

-- Task (syntax varies across versions/options)
CREATE OR REPLACE TASK my_db.ops.load_task
  WAREHOUSE = wh_xsmall
  SCHEDULE = '5 MINUTE'
  COMMENT = 'Loads incrementals into raw layer'
AS
  CALL my_db.ops.load_proc();
```

### Internal Named Stage Privileges
- **Critical:** Internal named stages do NOT support `USAGE` grants. Grant `READ` and/or `WRITE` instead.
- **Rule:** Use `GRANT READ, WRITE ON STAGE <DB>.<SCHEMA>.<STAGE> TO ROLE <role>` as needed.
- **Note:** Access still requires appropriate `USAGE` on the parent database and schema; always reference the stage with a fully qualified name in CLI workflows.

**Incorrect:**
```sql
-- ❌ USAGE is not valid on internal named stages
GRANT USAGE ON STAGE my_db.my_schema.my_stage TO ROLE app_role;
```

**Correct:**
```sql
-- ✓ Grant appropriate privileges on internal named stage
GRANT READ, WRITE ON STAGE my_db.my_schema.my_stage TO ROLE app_role;

-- ✓ Fully qualified PUT/GET paths in CLI automation
PUT 'file://local/path/file.csv' @my_db.my_schema.my_stage AUTO_COMPRESS=FALSE;
GET @my_db.my_schema.my_stage file://local/downloads/;
```

### Fully Qualified Object Names
- **Critical:** Always use fully qualified object names (DATABASE.SCHEMA.OBJECT) in production code and automation
- **Critical:** In CLI automation, each command runs in a separate session - USE DATABASE/SCHEMA don't persist
- **Rule:** Prefer `DATABASE.SCHEMA.TABLE` over `USE DATABASE; USE SCHEMA; TABLE`

**Problem - Session Context Doesn't Persist:**
```bash
# ❌ Incorrect - Each command is a separate session
uvx snow sql -q "USE DATABASE my_db"     # Session 1
uvx snow sql -q "USE SCHEMA my_schema"   # Session 2 - doesn't know about my_db
uvx snow sql -q "SELECT * FROM my_table" # Session 3 - no context
```

**Solution - Fully Qualified Names:**
```bash
# ✓ Correct - No session dependency
uvx snow sql -q "SELECT * FROM my_db.my_schema.my_table"
uvx snow sql -q "PUT 'file://data.csv' @my_db.my_schema.my_stage"
uvx snow sql -q "COPY INTO my_db.my_schema.my_table FROM @my_db.my_schema.my_stage/file.csv ..."
```

**Benefits:**
- Works in CLI automation (no session dependency)
- Explicit and unambiguous
- Follows Snowflake best practices for production code
- Prevents "object does not exist" errors in multi-command workflows

**When USE is acceptable:**
- Interactive sessions in Snowsight/SnowSQL
- Single-file SQL scripts executed as a unit
- Development/exploration (not production)

**Best Practice:**
```sql
-- ✓ Production code - fully qualified
INSERT INTO prod_db.analytics.customer_summary
SELECT ...
FROM prod_db.raw.customers c
JOIN prod_db.raw.orders o ON c.customer_id = o.customer_id;

-- ✓ Stage references - fully qualified
PUT file://data.csv @prod_db.staging.my_stage;
COPY INTO prod_db.raw.my_table FROM @prod_db.staging.my_stage/data.csv;
```

## 4. SQL File Header and Section Standards

### 4.0 Universal Header Format (ALL SQL Files)

- **Critical:** ALL SQL files must use consistent header format regardless of project complexity
- **Rule:** Use equals-sign box format with standardized sections
- **Applies to:** setup.sql, teardown.sql, DDL files, templates, all .sql files

**Standard Header Template:**
```sql
-- ============================================================================
-- Filename: <filename>.sql
-- Description: <Brief one-line description>
-- [Optional: Additional context lines]
--
-- Parameters: (if using Snowflake variables)
--   PARAM1 - Description (e.g., DATABASE - Database name)
--   PARAM2 - Description (e.g., SCHEMA - Schema name)
--
-- Usage:
--   snow sql -D PARAM1=value -D PARAM2=value -f <filename>.sql
--
-- [Optional sections:]
-- Dependencies: <What must exist before running>
-- Returns: <What the script outputs or creates>
-- Note: <Important warnings or context>
-- ============================================================================
```

**Standard Section Divider (when sections are present):**
```sql
-- ===========================================================================
-- SECTION NAME: CONTEXT
-- ===========================================================================
```

**Examples:**

Simple DDL file:
```sql
-- ============================================================================
-- Filename: 001_ddl-grid_data.sql
-- Description: Create GRID_DATA schema and tables
--
-- Usage:
--   snow sql -f 001_ddl-grid_data.sql
--
-- Dependencies: Database UTILITY_DEMO_V2 must exist
-- ============================================================================

-- ===========================================================================
-- SCHEMA SETUP
-- ===========================================================================
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;

-- ===========================================================================
-- TABLE DEFINITIONS
-- ===========================================================================
CREATE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);
```

Template file with variables:
```sql
-- ============================================================================
-- Filename: copy_ami_data.sql
-- Description: Load AMI data from stage into table using COPY INTO
-- Note: This operation may take 2-3 minutes due to data volume
-- 
-- Parameters:
--   DATABASE - Database name (e.g., UTILITY_DEMO_V2)
--   SCHEMA   - Schema name (e.g., GRID_DATA)
--   STAGE    - Stage name (e.g., UTILITY_DEMO_V2.GRID_DATA.STAGE)
--
-- Usage:
--   snow sql -D DATABASE=DB -D SCHEMA=SCH -D STAGE=STG -f copy_ami_data.sql
-- ============================================================================

COPY INTO <%DATABASE%>.<%SCHEMA%>.AMI_DATA 
FROM @<%STAGE%> 
PATTERN='.*synthetic_ami_data_.*\\.csv' 
FILE_FORMAT=(...);
```

Multi-step file with sections:
```sql
-- ============================================================================
-- Filename: merge_all_tables.sql
-- Description: Upsert all grid data tables (prevents duplicates)
-- Executes CREATE TEMP + COPY + MERGE for each table sequentially
--
-- Parameters:
--   DATABASE - Database name
--   SCHEMA   - Schema name
--   STAGE    - Stage name
--
-- Usage:
--   snow sql -D DATABASE=DB -D SCHEMA=SCH -D STAGE=STG -f merge_all_tables.sql
--
-- Note: This file contains multiple SQL statements executed sequentially
-- ============================================================================

-- ===========================================================================
-- TABLE 1/5: GRID_ASSETS
-- ===========================================================================
CREATE TEMP TABLE GRID_ASSETS_STAGE LIKE <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS;
COPY INTO GRID_ASSETS_STAGE FROM @<%STAGE%> ...;
MERGE INTO <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS ...;

-- ===========================================================================
-- TABLE 2/5: TRANSFORMER_DATA
-- ===========================================================================
CREATE TEMP TABLE TRANSFORMER_DATA_STAGE ...;
```

### 4.1 SQL Template Files for Automation

**When to Use Templates:**
- When project expands beyond simple setup.sql/teardown.sql
- For reusable operations (upload, load, merge, verify)
- When integrating with automation (Taskfiles, CI/CD)
- For parameterized operations across environments

**Template File Organization:**
```
sql/operations/
├── domain/              # Group by schema/domain (grid, customer, etc.)
│   ├── operation/       # Group by operation type (upload, load, etc.)
│   │   └── file.sql     # Template with Snowflake variables
```

**Snowflake Variable Syntax:**
- Use `<%VARIABLE%>` for parameter substitution
- Pass via CLI: `snow sql -D VARIABLE=value -f template.sql`
- Variables work in all SQL contexts (object names, paths, values)
- **Note:** The old `&{VARIABLE}` syntax is deprecated and will no longer be supported

**Benefits:**
- **Reusability:** Same template for dev/test/prod
- **Testability:** Execute standalone with `snow sql`
- **Maintainability:** SQL separate from orchestration logic
- **Version Control:** SQL changes tracked independently

**Integration with Taskfiles:**
```yaml
sql:template:
  desc: Execute SQL template with Snowflake variables
  silent: true
  internal: true
  cmds:
    - >
      snow sql
      -D DATABASE={{.DATABASE}}
      -D SCHEMA={{.SCHEMA}}
      -f {{.SQL_FILE}}
```

## 5. SQL File Naming Conventions

- **Scope:** Applies to `**/*.sql` files in demos, automation, and CI/CD.
- **Goal:** Human clarity for simple demos and deterministic ordering for complex/automated flows.

### 4.1 Demo-friendly conventions (simple/quickstarts)
- Use `setup.sql` to create required objects and `teardown.sql` (or `cleanup.sql`) to remove them.
- For multi-step demos, prefix with numbers to enforce order (optionally reserve a high number for teardown):

```text
setup.sql
teardown.sql

01_setup_infra.sql
02_create_objects.sql
03_load_data.sql
99_teardown.sql

projectname_setup.sql
projectname_teardown.sql
```

### 4.2 Strict, ordered convention (recommended for complex demos and CI/CD)
- **Pattern:** `NNN-<mode>-<schema-or-object>[-<short-desc>].sql`
  - `NNN`: 3-digit, zero-padded numeric sequence starting at `001`; strictly increasing; unique within repository (or per module/directory if documented).
  - `<mode>`: one of `ddl`, `dml`, `grant`, `ops`.
  - `<schema-or-object>`: lowercase kebab-case; characters `[a-z0-9-]+`; no spaces, underscores, or dots. Use hyphens as word separators (e.g., `grid-data`, `customer-data`).
  - Optional `-<short-desc>`: brief, hyphenated descriptor (e.g., `-add-indexes`).
  - **Critical:** Use kebab-case (lowercase-with-hyphens) for ALL filename components.
  - **Critical:** Use hyphens as separators between all components (not underscores).

**Correct Examples (kebab-case):**

```text
001-ddl-analytics-customer-orders.sql
002-dml-analytics-customer-orders.sql
003-grant-analytics.sql
004-ops-util-csv-format.sql
005-ddl-raw-customer-events-add-indexes.sql
100-ddl-snowflake-intelligence.sql
200-ops-mlops-monitoring.sql
```

**Incorrect Examples:**
```text
001_ddl-analytics.customer_orders.sql  ❌ Uses underscores and dots
002_dml_analytics.sql                  ❌ Uses underscores
003-DDL-Analytics.sql                  ❌ Uses uppercase
004-ops-util.csv.format.sql            ❌ Uses dots
```

**Validation regex for strict convention:**

```text
^[0-9]{3}-(ddl|dml|grant|ops)-[a-z0-9-]+\.sql$
```

**Rationale:**
- Zero-padded prefixes ensure lexical sort equals execution order, aligning with widely adopted migration tooling patterns (e.g., Flyway, Liquibase).
- Kebab-case provides visual consistency with modern naming conventions and URL-friendly identifiers.
- Hyphens as separators improve readability and are standard in web/CLI contexts.
- Mode and target in the filename improve reviewability and change auditing.

**Modular Organization for Complex Projects:**

For projects with many SQL files, organize into subdirectories by purpose:

```text
sql/
├── setup/          # Core foundation (001-099)
│   ├── 001-ddl-database-and-rbac.sql
│   ├── 002-ddl-grid-data-core.sql
│   └── 003-ddl-customer-data-core.sql
├── features/       # Optional/modular features (100-899)
│   ├── 100-ddl-snowflake-intelligence.sql
│   ├── 101-ddl-semantic-views-grid.sql
│   ├── 200-ops-mlops-monitoring.sql
│   └── 300-ops-performance-optimizations.sql
├── teardown/       # Cleanup scripts (900-999)
│   ├── 998-ops-grid-data-teardown.sql
│   └── 999-ops-customer-data-teardown.sql
└── operations/     # Parameterized templates (no numbering)
    └── [domain/operation/template.sql]
```

**Benefits of modular organization:**
- Clear separation of concerns (core vs optional features)
- Easier to test features independently
- Simpler CI/CD integration (run setup, selected features, teardown)
- Better discoverability and maintainability

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist

**SQL File Standards:**
- [ ] All SQL files use equals-sign box header format with mandatory sections (Filename, Description, Usage)
- [ ] Parameters documented when using Snowflake variables (`<%VARIABLE%>`)
- [ ] Section dividers use equals-sign format for multi-step files
- [ ] Template files organized in domain-first directory structure (sql/operations/domain/operation/)

**Query Best Practices:**
- [ ] CTEs used for complex query modularization (avoid deep nesting)
- [ ] VARIANT data extracted once in early CTE (no repeated casting)
- [ ] Fully qualified object names used (DATABASE.SCHEMA.OBJECT) in production and automation
- [ ] No USE DATABASE/SCHEMA statements in CLI automation (session context doesn't persist)
- [ ] COPY INTO uses ON_ERROR outside FILE_FORMAT clause (or omits it for default)
- [ ] CREATE VIEW has COMMENT before AS keyword (not after query)
- [ ] Comments added to supported objects (tables, views, schemas, stages, etc.)
- [ ] Comment syntax verified per object type against Snowflake documentation

**File Organization:**
- [ ] SQL filenames follow approved convention: demo (`setup.sql`/`teardown.sql`) or strict `NNN-<mode>-<schema-or-object>[-<short-desc>].sql`
- [ ] Strict convention uses 3-digit zero-padded unique, sequential prefixes starting at `001`
- [ ] Filenames use kebab-case (lowercase-with-hyphens); only `[a-z0-9-]` used; modes limited to `ddl|dml|grant|ops`
- [ ] Complex projects organized into setup/, features/, teardown/ subdirectories

**Performance & Optimization:**
- [ ] Join cardinality controlled with distinct keys or semi-joins
- [ ] QUALIFY used for window function filters (instead of subqueries)
- [ ] SQL syntax validated against Snowflake documentation
- [ ] Internal named stages use READ/WRITE grants (not USAGE); fully qualified stage references in CLI

## Validation
- **Success checks:** 
  - CTEs segment logic clearly; no excessive nesting
  - VARIANT extraction happens once in dedicated CTE
  - Objects fully qualified (DATABASE.SCHEMA.OBJECT) in production code
  - No USE statements in CLI automation scripts
  - COPY INTO statements have correct parameter placement
  - CREATE VIEW statements have COMMENT before AS
  - Objects have descriptive comments where supported (DDL uses correct syntax per object)
  - Comment DDL verified against Snowflake docs for targeted object types
  - SQL filenames match the selected convention:
    - Demo: `setup.sql`/`teardown.sql` (and optional numeric-prefixed steps)
    - Strict: matches `^[0-9]{3}-(ddl|dml|grant|ops)-[a-z0-9-]+\.sql$` (kebab-case)
  - SQL executes without compilation errors in CLI and Snowsight
- **Negative tests:** 
  - USE DATABASE/SCHEMA in separate CLI commands should fail with "object does not exist"
  - ON_ERROR inside FILE_FORMAT should cause "invalid parameter" error
  - COMMENT after AS in CREATE VIEW should cause "unexpected COMMENT" syntax error
  - Incorrect COMMENT placement for a specific object type should raise a syntax error
  - Repeated VARIANT casting should impact query performance
  - Strict naming violations: missing/short numeric prefix, invalid mode, uppercase letters, spaces, underscores, dots in names, duplicate sequence numbers

## Response Template
```sql
-- CTE pattern with fully qualified names
WITH extracted_variant AS (
  SELECT 
    raw_data:id::STRING AS id,
    raw_data:timestamp::TIMESTAMP AS ts
  FROM my_db.raw.raw_table
),
aggregated AS (
  SELECT id, COUNT(*) AS cnt
  FROM extracted_variant
  GROUP BY id
)
SELECT * FROM aggregated;

-- COPY INTO pattern with fully qualified names
COPY INTO my_db.analytics.target_table
FROM @my_db.staging.my_stage/data.csv
FILE_FORMAT = (
    TYPE = 'CSV',
    SKIP_HEADER = 1
);

-- CREATE VIEW pattern with COMMENT before AS
CREATE OR REPLACE VIEW my_db.analytics.my_view
COMMENT = 'Purpose-built view for analytics'
AS
SELECT 
    explicit_columns,
    calculated_field
FROM my_db.raw.source_table;
```

## References

### External Documentation

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) - Complete SQL command reference and syntax guide
- [Querying Semi-Structured Data](https://docs.snowflake.com/en/sql-reference/data-types-semistructured) - VARIANT, OBJECT, and ARRAY data type handling
- [Flyway Migrations - Naming](https://documentation.red-gate.com/fd/concepts/migrations#Migrations-Typesofmigrations) - Versioned migration naming and ordering principles
- [Liquibase Changelogs](https://docs.liquibase.com/concepts/changelogs/changelogs.html) - Organizing changes and deterministic execution ordering

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
