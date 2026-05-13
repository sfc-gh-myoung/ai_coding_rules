# Snowflake SQL: Demo Engineering and Workshops

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-03-26
**Keywords:** demo SQL, workshop, teardown, progress indicators, rerunnable demos, CREATE OR REPLACE, educational SQL, demo patterns, setup scripts, customer learning, per-schema isolation, inline documentation, dynamic grant, CURRENT_USER, IDENTIFIER
**LoadTrigger:** kw:demo, kw:workshop, kw:quickstart
**TokenBudget:** ~4600
**ContextTier:** High
**Depends:** 102-snowflake-sql-core.md

## Scope

**What This Rule Covers:**
SQL file patterns specifically for Snowflake demos, workshops, and customer learning environments. Covers schema-based file naming (`NN_<schema>_<operation>.sql`), per-schema isolation with independent setup/teardown files, progress indicators (`SELECT '[PASS]'`), inline educational comments, and demo-safe idempotent patterns (`CREATE OR REPLACE TABLE`). Prioritizes ease of use, readability, and educational value over automation complexity.

**When to Load This Rule:**
- Creating demo SQL files for Snowflake workshops
- Building customer learning environments or quickstart guides
- Writing educational SQL with inline documentation
- Setting up rerunnable demo scripts with progress indicators
- Creating per-schema setup/load/teardown files
- Teaching Snowflake concepts through SQL examples
- Building workshop materials for field teams

## References

### Dependencies

**Must Load First:**
- **102-snowflake-sql-core.md** - General SQL file patterns (headers, syntax, qualified names)

**Related:**
- **131-snowflake-demo-creation.md** - Synthetic data generation for demos
- **132-snowflake-demo-modeling.md** - Data modeling patterns for demos
- **102a-snowflake-sql-automation.md** - Production patterns (when demos evolve to production)

### External Documentation

**Snowflake:**
- [SQL Command Reference](https://docs.snowflake.com/en/sql-reference-commands.html) - Complete SQL syntax
- [Snowflake Quickstarts](https://quickstarts.snowflake.com/) - Workshop examples

## Contract

### Inputs and Prerequisites

- Demo environment with Snowflake CLI access
- CSV data files for loading
- Database already created
- Understanding of demo audience

### Mandatory

- `NN_<schema>_<operation>.sql` file naming pattern
- Per-schema isolation (setup/teardown affect only target schema)
- Progress indicators after each major step
- Inline educational comments explaining "why"
- Idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)

### Forbidden

- Dropping database or shared resources in demo files
- Production deployment tools in demo context
- Automated schedulers for demo scripts
- Non-idempotent patterns that fail on rerun

### Execution Steps

1. Create per-schema setup files with inline documentation
2. Add progress indicators after each major step
3. Use demo-safe idempotent patterns (CREATE OR REPLACE TABLE)
4. Create independent teardown files per schema
5. Test rerunability (scripts should work multiple times)

### Output Format

SQL files with .sql extension, UTF-8 encoding, Unix line endings

### Validation

**Test Requirements:**
- Run setup, verify objects created
- Run teardown, verify cleanup
- Rerun setup (idempotency test)

**Success Criteria:**
- Scripts execute without errors on multiple runs
- Progress indicators appear at each step
- Objects created with correct names and structure
- Teardown removes all created objects
- Comments educate readers on concepts

**Negative Tests:**
- Setup without database fails gracefully (clear error message, not cryptic SQL error)
- Load without prior setup shows clear "schema does not exist" error
- Teardown of non-existent schema succeeds (IF EXISTS prevents errors)
- Rerun of setup produces identical results (idempotency verified)

### Design Principles

- **Readability First**: Simple, self-documenting filenames and patterns
- **Per-Schema Operations**: Independent setup/load/teardown per schema
- **Educational Value**: Inline documentation that teaches concepts
- **Rerunnable Demos**: Idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)
- **Audience-Aware**: Comments explain "why" for learning, not just "what"
- **Demo-Safe**: Patterns suitable for ephemeral environments, not production

### Post-Execution Checklist

- [ ] Filename follows `NN_<schema>_<operation>.sql` pattern
- [ ] File header lists prerequisites and what gets created
- [ ] Progress SELECT statements after each major step
- [ ] All object names fully qualified (DB.SCHEMA.OBJECT)
- [ ] Script is rerunnable (idempotent patterns)
- [ ] Comments teach concepts, not just describe syntax
- [ ] Teardown file created for cleanup
- [ ] Tested multiple executions successfully
- [ ] **FK dependencies mapped** (if multi-file): referenced tables created before referencing tables
- [ ] **CLI orchestration aligned** (if applicable): print menus match execution order

## File Naming for Demos

### Schema-Based Naming Pattern

**Rule:** Use `NN_<schema>_<operation>.sql` format

**Pattern:**
```

For Taskfile patterns, see `820-taskfile-automation.md`. For Makefile patterns, see `821-makefile-automation.md`.text
NN_<lowercase_schema>_<operation>.sql
```

**Examples:**
```text
01_grid_setup.sql        # Create GRID_DATA schema and tables
02_grid_load.sql         # Load grid data from CSV files
99_grid_teardown.sql     # Drop GRID_DATA schema

03_customer_setup.sql    # Create CUSTOMER_DATA schema and tables
04_customer_load.sql     # Load customer data from CSV files
98_customer_teardown.sql # Drop CUSTOMER_DATA schema

00_database_setup.sql    # Create database and RBAC
99_database_teardown.sql # Drop database and role
```

**Benefits:**
- Immediately clear what each file does
- Easy to run per-schema operations
- Self-documenting for demo audiences
- Works well with task commands

### Multi-Step Operations

**Rule:** The two-digit prefix in `NN_<schema>_<operation>.sql` already encodes execution order. For schemas with multiple dependent steps, use sequential numbers:

```text
01_grid_setup.sql
02_grid_load_core.sql
03_grid_load_sensors.sql
04_grid_features.sql
99_grid_teardown.sql
```

**Numbering tips:** Reserve `00` for database-level setup, `99`/`98` for teardown, and `01`-`89` for operational steps

## Per-Schema Setup and Teardown

### Schema Isolation Requirements

**Critical:** Each schema's setup/teardown must be fully independent

**Schema-Specific File Checklist:**
- [ ] Creates/drops only objects in target schema
- [ ] Does NOT drop database or shared resources
- [ ] Does NOT affect other schemas
- [ ] Can run in any order relative to other schemas
- [ ] Handles dependencies within schema only

**Why this matters:** Demo users should be able to explore one schema (e.g., GRID_DATA) without breaking another (e.g., CUSTOMER_DATA).

### Setup File Pattern

**Template: 01_grid_setup.sql**

```sql
-- ============================================================================
-- Filename: 01_grid_setup.sql
-- Description: Create GRID_DATA schema and all related objects
--
-- Prerequisites: Database UTILITY_DEMO_V2 must exist
-- Creates: GRID_DATA schema, 5 tables, 1 stage, 2 views
-- ============================================================================

-- Step 1: Create the schema
-- This organizes all grid-related objects in one namespace
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA
    COMMENT = 'Grid asset and sensor data for predictive maintenance';

SELECT '[PASS] Schema created' AS progress;

-- Step 2: Create core asset table
-- asset_id is PRIMARY KEY to ensure unique assets
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (
    asset_id VARCHAR PRIMARY KEY,      -- Unique identifier (e.g., "TFX001")
    asset_type VARCHAR,                 -- Type: TRANSFORMER, SUBSTATION, etc.
    latitude FLOAT,                     -- Location for mapping
    longitude FLOAT,
    install_date DATE                   -- Age impacts failure probability
) COMMENT = 'Core grid infrastructure assets';

SELECT '[PASS] GRID_ASSETS table created' AS progress;

-- Step 3: Create failure history table
-- This tracks when transformers failed and why
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS (
    failure_id VARCHAR PRIMARY KEY,
    asset_id VARCHAR,                   -- Links to GRID_ASSETS
    failure_time TIMESTAMP_NTZ,
    failure_reason VARCHAR,
    repair_cost NUMBER(10,2)           -- Track financial impact
) COMMENT = 'Historical transformer failure events';

SELECT '[PASS] FAILURE_EVENTS table created' AS progress;

-- Step 4: Create stage for data files
-- Stages are Snowflake's way to reference external files
CREATE OR REPLACE STAGE UTILITY_DEMO_V2.GRID_DATA.DATA_FILES
    COMMENT = 'Stage for grid CSV files';

SELECT '[PASS] Stage created' AS progress;

-- Step 5: Create analysis view
-- Views give business-friendly access to technical data
CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_ASSET_FAILURES
COMMENT = 'Join assets with failure history for analysis'
AS
SELECT
    a.asset_id,
    a.asset_type,
    a.install_date,
    COUNT(f.failure_id) AS failure_count,
    SUM(f.repair_cost) AS total_repair_cost
FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS a
LEFT JOIN UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS f
    ON a.asset_id = f.asset_id
GROUP BY a.asset_id, a.asset_type, a.install_date;

SELECT '[PASS] VW_ASSET_FAILURES view created' AS progress;

SELECT 'GRID_DATA schema setup complete!' AS status;
```

### Teardown File Pattern

**Template: 99_grid_teardown.sql**

```sql
-- ============================================================================
-- Filename: 99_grid_teardown.sql
-- WARNING: This will delete all grid data!
-- Does NOT affect: CUSTOMER_DATA schema, database, or roles
-- ============================================================================

DROP SCHEMA IF EXISTS UTILITY_DEMO_V2.GRID_DATA CASCADE;
SELECT '[PASS] GRID_DATA schema removed' AS status;
```

### Load File Pattern

**Template: 02_grid_load.sql**

```sql
-- ============================================================================
-- Filename: 02_grid_load.sql
-- Prerequisites: GRID_DATA schema exists (run 01_grid_setup.sql first)
--                CSV files uploaded to stage
-- ============================================================================

-- Load grid assets
-- SKIP_HEADER=1 skips the CSV header row
COPY INTO UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
FROM @UTILITY_DEMO_V2.GRID_DATA.DATA_FILES
PATTERN = '.*grid_assets.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';  -- Skip bad rows in demo context

SELECT '[PASS] Grid assets loaded' AS progress;

-- Repeat COPY INTO pattern for each table (SCADA_DATA, etc.)

SELECT 'Grid data load complete!' AS status;
```

## Progress Indicators

Add `SELECT '[PASS] ...' AS progress;` after each major operation (CREATE SCHEMA, CREATE TABLE, COPY INTO, etc.). End each file with `SELECT '... complete!' AS status;`. This gives users immediate feedback, makes errors easy to locate, and creates a professional demo experience. See the setup template above for a complete example.

## Inline Educational Comments

Demo SQL should teach as it executes. Explain concepts in comments, use "Step N" structure, add inline comments for column purposes, and explain acronyms/domain terms.

```sql
-- Step 3: Create AMI data table
-- AMI = Advanced Metering Infrastructure (smart meters)
-- Records electricity consumption every 15 minutes
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.AMI_DATA (
    meter_id VARCHAR,                    -- Unique meter identifier
    reading_time TIMESTAMP_NTZ,          -- When reading was taken
    consumption_kwh NUMBER(10,3),        -- Kilowatt-hours consumed
    voltage_v NUMBER(6,2)                -- Voltage in volts
) COMMENT = 'Smart meter readings (15-minute intervals)';
```

## Demo-Safe Idempotent Patterns

Make demos rerunnable without errors:

```sql
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;       -- Won't error if exists
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);  -- Drops & recreates
CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_SUMMARY AS ...;   -- Always safe
CREATE OR REPLACE STAGE UTILITY_DEMO_V2.GRID_DATA.DATA_FILES;         -- Files remain in cloud
```

`CREATE OR REPLACE TABLE` is OK for demos (data is ephemeral/regenerable). **NOT production-safe** — for production use `102a-snowflake-sql-automation.md` patterns (CREATE TABLE IF NOT EXISTS + MERGE).

## Demo Project Structure and Orchestration

**Recommended directory layout for `sql/`:**
- **setup/** - `00_database_setup.sql`, `01_grid_setup.sql`, `03_customer_setup.sql`
- **features/** - `02_grid_load.sql`, `04_customer_load.sql`, `05_shared_semantic_views.sql`
- **teardown/** - `98_customer_teardown.sql`, `99_grid_teardown.sql`, `99_database_teardown.sql`

**Orchestrate with project automation** (for example, Taskfile or Makefile wrapping `snow sql -f` commands):
Taskfile example:
```yaml
tasks:
  setup:grid:
    cmds: [snow sql -f sql/setup/01_grid_setup.sql]
  teardown:grid:
    cmds: [snow sql -f sql/teardown/99_grid_teardown.sql]
  demo:full:
    cmds: [task: setup:grid, task: setup:customer, task: load:grid, task: load:customer]
```

## Multi-File Dependencies

### Foreign Key Dependency Ordering

**Rule:** When SQL files contain foreign key constraints, the referenced table must be created BEFORE the referencing table. Snowflake enforces FK constraints at creation time.

**Dependency analysis:** Before implementing multi-file CLI orchestration:
```bash
# Find all FK references across SQL files
grep -n "FOREIGN KEY\|REFERENCES" sql/*.sql
```
For each FK: note which file creates the referencing table and which creates the referenced table. Referenced file must execute first. Document dependencies in file headers:
```sql
-- Prerequisites: 09_grid_dedup_fastpath.sql (creates UNIQUE_DESCRIPTIONS table)
```

**Execution order = dependency order, NOT file number order.** See Anti-Pattern 5 for a concrete example. Ensure CLI print menus match actual execution order.

> **Investigation Required**
> Before creating demo SQL files:
> 1. **Confirm demo audience level** (beginner, intermediate, advanced) to calibrate comment verbosity
> 2. **Verify target database exists** and you have CREATE SCHEMA privileges
> 3. **Review existing demo files** in the project to follow established naming patterns
> 4. **Confirm schema isolation strategy** (one schema per domain vs shared schema)
> 5. **Map FK dependencies** across files if multi-file demo (run `grep -n "REFERENCES" sql/*.sql`)

## Quick Reference: Minimal Setup/Teardown Pair

**`01_analytics_setup.sql`** (copy and adapt):
```sql
-- ============================================================================
-- Filename: 01_analytics_setup.sql
-- Prerequisites: Database DEMO_DB must exist
-- Creates: ANALYTICS schema, 2 tables, 1 view
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS DEMO_DB.ANALYTICS
    COMMENT = 'Customer analytics for demo';
SELECT '[PASS] Schema created' AS progress;

CREATE OR REPLACE TABLE DEMO_DB.ANALYTICS.CUSTOMERS (
    customer_id INT PRIMARY KEY,
    name STRING,
    segment STRING       -- e.g., 'enterprise', 'smb', 'consumer'
) COMMENT = 'Customer master data';
SELECT '[PASS] CUSTOMERS created' AS progress;

CREATE OR REPLACE TABLE DEMO_DB.ANALYTICS.ORDERS (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES DEMO_DB.ANALYTICS.CUSTOMERS(customer_id),
    order_date DATE,
    amount NUMBER(10,2)
) COMMENT = 'Order transactions';
SELECT '[PASS] ORDERS created' AS progress;

CREATE OR REPLACE VIEW DEMO_DB.ANALYTICS.VW_CUSTOMER_SUMMARY AS
SELECT c.customer_id, c.name, c.segment,
    COUNT(o.order_id) AS order_count, SUM(o.amount) AS total_spend
FROM DEMO_DB.ANALYTICS.CUSTOMERS c
LEFT JOIN DEMO_DB.ANALYTICS.ORDERS o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.segment;
SELECT '[PASS] VW_CUSTOMER_SUMMARY created' AS progress;

SELECT 'ANALYTICS setup complete!' AS status;
```

**`99_analytics_teardown.sql`** (matching pair):
```sql
-- ============================================================================
-- Filename: 99_analytics_teardown.sql
-- WARNING: Deletes all analytics data!
-- Does NOT affect: other schemas, database, or roles
-- ============================================================================
DROP SCHEMA IF EXISTS DEMO_DB.ANALYTICS CASCADE;
SELECT '[PASS] ANALYTICS schema removed' AS status;
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Dropping Database in Demo Files

**Problem:**
```sql
DROP DATABASE IF EXISTS DEMO_DB;
CREATE DATABASE DEMO_DB;
```

**Why It Fails:** Destroys ALL schemas in the database, not just the demo schema. Can accidentally delete production data if run in wrong environment.

**Correct Pattern:**
```sql
DROP SCHEMA IF EXISTS DEMO_DB.CUSTOMER_ANALYTICS CASCADE;
```

### Anti-Pattern 2: Non-Idempotent Demos

**Problem:**
```sql
CREATE SCHEMA customer_analytics;
CREATE TABLE customers (id INT, name STRING);
```

**Why It Fails:** Second run fails with "Schema already exists" error. Demo users often rerun scripts multiple times.

**Correct Pattern:**
```sql
CREATE SCHEMA IF NOT EXISTS customer_analytics;
CREATE OR REPLACE TABLE customers (id INT, name STRING);
```

### Anti-Pattern 3: Missing Progress Indicators

Running multiple DDL statements with no `SELECT '[PASS]...'` between them gives users no feedback and makes errors hard to locate. Always add progress indicators after each major step (see Progress Indicators section above).

### Anti-Pattern 4: No Educational Comments

Demo SQL without concept explanations and column-level comments has no teaching value. Acronyms go unexplained. Always explain "why" in comments (see Inline Educational Comments section above).

### Anti-Pattern 5: FK Reference Before Table Exists

```python
# Bad: CLI runs files in numeric order without considering dependencies
def setup():
    run_sql("06_grid_traceability.sql")   # Has FK to UNIQUE_DESCRIPTIONS
    run_sql("09_grid_dedup.sql")          # Creates UNIQUE_DESCRIPTIONS — too late!
```

**Error:** `Table 'UNIQUE_DESCRIPTIONS' does not exist or not authorized.`

```python
# Correct: respect FK dependencies, not file numbers
def setup():
    run_sql("09_grid_dedup.sql")          # Creates UNIQUE_DESCRIPTIONS FIRST
    run_sql("06_grid_traceability.sql")   # Now FK constraint succeeds
```

**Prevention:** Run `grep -n "FOREIGN KEY\|REFERENCES" sql/*.sql` before implementing CLI orchestration.

### Anti-Pattern 6: Direct CURRENT_USER() in GRANT ROLE

**Problem:**
```sql
-- WRONG: Causes syntax error
GRANT ROLE demo_user TO USER CURRENT_USER();
```

**Why It Fails:** `GRANT ROLE ... TO USER` requires a literal identifier. The parser does not accept function calls in the `TO USER` position.

**Correct Pattern:**
```sql
SET MY_USER = CURRENT_USER();
GRANT ROLE demo_user TO USER IDENTIFIER($MY_USER);
```

## Demo User RBAC

Create a demo-specific role with minimal required grants:

```sql
CREATE ROLE IF NOT EXISTS demo_user;
GRANT USAGE ON DATABASE DEMO_DB TO ROLE demo_user;
GRANT USAGE ON ALL SCHEMAS IN DATABASE DEMO_DB TO ROLE demo_user;
GRANT SELECT ON ALL TABLES IN DATABASE DEMO_DB TO ROLE demo_user;
GRANT SELECT ON ALL VIEWS IN DATABASE DEMO_DB TO ROLE demo_user;
-- For hands-on workshops: add write access
GRANT CREATE TABLE ON ALL SCHEMAS IN DATABASE DEMO_DB TO ROLE demo_user;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN DATABASE DEMO_DB TO ROLE demo_user;
GRANT USAGE ON WAREHOUSE DEMO_WH TO ROLE demo_user;

-- Grant demo role to the user running the script (dynamic)
SET DEMO_USER = CURRENT_USER();
GRANT ROLE demo_user TO USER IDENTIFIER($DEMO_USER);
```

## When to Use Production Patterns

If the user requests "production ready", "CI/CD pipeline", "parameterized templates", or "multi-environment deployment", use `102a-snowflake-sql-automation.md` instead (CREATE TABLE IF NOT EXISTS + MERGE, SQL templates with variables, environment-agnostic patterns).
