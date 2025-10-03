**Description:** Advanced SQL authoring patterns for Snowflake, focusing on CTEs, VARIANT extraction, cardinality control, and correct syntax patterns.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-30

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] CTEs used for complex query modularization (avoid deep nesting)
- [ ] VARIANT data extracted once in early CTE (no repeated casting)
- [ ] Fully qualified object names used (DATABASE.SCHEMA.OBJECT) in production and automation
- [ ] No USE DATABASE/SCHEMA statements in CLI automation (session context doesn't persist)
- [ ] COPY INTO uses ON_ERROR outside FILE_FORMAT clause (or omits it for default)
- [ ] CREATE VIEW has COMMENT before AS keyword (not after query)
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
  - SQL executes without compilation errors in CLI and Snowsight
- **Negative tests:** 
  - USE DATABASE/SCHEMA in separate CLI commands should fail with "object does not exist"
  - ON_ERROR inside FILE_FORMAT should cause "invalid parameter" error
  - COMMENT after AS in CREATE VIEW should cause "unexpected COMMENT" syntax error
  - Repeated VARIANT casting should impact query performance

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

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
