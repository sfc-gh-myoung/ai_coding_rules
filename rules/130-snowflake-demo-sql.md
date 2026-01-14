# Snowflake SQL: Demo Engineering and Workshops

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** demo SQL, workshop, teardown, progress indicators, rerunnable demos, CREATE OR REPLACE, educational SQL, demo patterns, setup scripts, customer learning, per-schema isolation, inline documentation
**TokenBudget:** ~3900
**ContextTier:** High
**Depends:** 102-snowflake-sql-core.md

## Scope

**What This Rule Covers:**
SQL file patterns specifically for Snowflake demos, workshops, and customer learning environments. Covers schema-based file naming (`<schema>_<operation>.sql`), per-schema isolation with independent setup/teardown files, progress indicators (`SELECT '[PASS]'`), inline educational comments, and demo-safe idempotent patterns (`CREATE OR REPLACE TABLE`). Prioritizes ease of use, readability, and educational value over automation complexity.

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

- `<schema>_<operation>.sql` file naming pattern
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

### Design Principles

- **Readability First**: Simple, self-documenting filenames and patterns
- **Per-Schema Operations**: Independent setup/load/teardown per schema
- **Educational Value**: Inline documentation that teaches concepts
- **Rerunnable Demos**: Idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)
- **Audience-Aware**: Comments explain "why" for learning, not just "what"
- **Demo-Safe**: Patterns suitable for ephemeral environments, not production

### Post-Execution Checklist

- [ ] Filename follows `<schema>_<operation>.sql` pattern
- [ ] File header lists prerequisites and what gets created
- [ ] Progress SELECT statements after each major step
- [ ] All object names fully qualified (DB.SCHEMA.OBJECT)
- [ ] Script is rerunnable (idempotent patterns)
- [ ] Comments teach concepts, not just describe syntax
- [ ] Teardown file created for cleanup
- [ ] Tested multiple executions successfully

## File Naming for Demos

### Schema-Based Naming Pattern

**Rule:** Use `<schema>_<operation>.sql` format

**Pattern:**
```text
<lowercase_schema>_<operation>.sql
```

**Examples:**
```text
grid_setup.sql           # Create GRID_DATA schema and tables
grid_load.sql            # Load grid data from CSV files
grid_teardown.sql        # Drop GRID_DATA schema

customer_setup.sql       # Create CUSTOMER_DATA schema and tables
customer_load.sql        # Load customer data from CSV files
customer_teardown.sql    # Drop CUSTOMER_DATA schema

database_setup.sql       # Create database and RBAC
database_teardown.sql    # Drop database and role
```

**Benefits:**
- Immediately clear what each file does
- Easy to run per-schema operations
- Self-documenting for demo audiences
- Works well with task commands

### Multi-Step Operations

**Rule:** Add numeric prefix when order matters within a schema

**Use when:** A schema has dependencies between setup steps

```text
grid_01_setup.sql
grid_02_load_core.sql
grid_03_load_sensors.sql
grid_04_features.sql
grid_teardown.sql
```

**When NOT to use:** If steps can run in any order, omit numbers

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

**Template: grid_setup.sql**

```sql
-- ============================================================================
-- Filename: grid_setup.sql
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

**Template: grid_teardown.sql**

```sql
-- ============================================================================
-- Filename: grid_teardown.sql
-- Description: Remove GRID_DATA schema and all objects
--
-- WARNING: This will delete all grid data!
-- Does NOT affect: CUSTOMER_DATA schema, database, or roles
-- ============================================================================

-- Drop schema with CASCADE to remove all child objects
-- CASCADE ensures tables, views, stages are all removed
DROP SCHEMA IF EXISTS UTILITY_DEMO_V2.GRID_DATA CASCADE;

SELECT '[PASS] GRID_DATA schema removed' AS status;
```

### Load File Pattern

**Template: grid_load.sql**

```sql
-- ============================================================================
-- Filename: grid_load.sql
-- Description: Load all grid data from CSV files into GRID_DATA tables
--
-- Prerequisites:
--   - GRID_DATA schema exists (run grid_setup.sql first)
--   - CSV files uploaded to stage
-- ============================================================================

-- Load grid assets
-- SKIP_HEADER=1 skips the CSV header row
COPY INTO UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
FROM @UTILITY_DEMO_V2.GRID_DATA.DATA_FILES
PATTERN = '.*grid_assets.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

SELECT '[PASS] Grid assets loaded' AS progress;

-- Load SCADA sensor data
-- SCADA = Supervisory Control And Data Acquisition (grid sensors)
COPY INTO UTILITY_DEMO_V2.GRID_DATA.SCADA_DATA
FROM @UTILITY_DEMO_V2.GRID_DATA.DATA_FILES
PATTERN = '.*scada.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

SELECT '[PASS] SCADA data loaded' AS progress;

SELECT 'Grid data load complete!' AS status;
```

## Progress Indicators

### Rule

**Include SELECT statements to show progress after each major operation**

**Pattern:**
```sql
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;
SELECT '[PASS] Schema created' AS progress;

CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);
SELECT '[PASS] GRID_ASSETS table created' AS progress;

CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_SUMMARY AS ...;
SELECT '[PASS] VW_SUMMARY view created' AS progress;

SELECT 'Setup complete!' AS status;
```

**Benefits:**
- Users see immediate feedback
- Easy to spot where errors occur
- Confirms each step succeeded
- Professional demo experience

## Inline Educational Comments

### Rule

**SQL files for demos should teach as they execute**

**Pattern:**
- Explain concepts in comments
- Use "Step 1, Step 2" structure
- Inline comments for column purposes
- Explain acronyms and domain terms

**Example:**
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

### Rule

**Make demos rerunnable without errors**

**Demo-Safe Patterns:**
```sql
-- Schema: IF NOT EXISTS (won't error if exists)
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;

-- Tables: CREATE OR REPLACE (drops and recreates - OK for demos)
-- WARNING: This deletes data - only safe for demo/dev environments
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);

-- Views: CREATE OR REPLACE (always safe - no data loss)
CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_SUMMARY AS ...;

-- Stages: CREATE OR REPLACE (safe - files remain in cloud storage)
CREATE OR REPLACE STAGE UTILITY_DEMO_V2.GRID_DATA.DATA_FILES;
```

**Why `CREATE OR REPLACE TABLE` is OK for demos:**
- Demo data is ephemeral and regenerable
- Users expect to reset demo state
- Simplifies rerunning without manual cleanup

**NOT production-safe:** For production, use `102a-snowflake-sql-automation.md` patterns (CREATE TABLE IF NOT EXISTS + MERGE).

## Demo Project Structure

### Recommended Directory Structure

**Pattern:**

Directory structure for `sql/`:
- **setup/** - Initial setup scripts
  - `database_setup.sql` - Create database and RBAC
  - `grid_setup.sql` - Create GRID_DATA schema
  - `customer_setup.sql` - Create CUSTOMER_DATA schema
- **features/** - Feature-specific scripts
  - `grid_load.sql` - Load grid data
  - `customer_load.sql` - Load customer data
  - `semantic_views.sql` - Optional: Create semantic models
- **teardown/** - Cleanup scripts
  - `grid_teardown.sql` - Drop GRID_DATA schema
  - `customer_teardown.sql` - Drop CUSTOMER_DATA schema
  - `database_teardown.sql` - Drop entire database

### Task Commands Pattern

**Recommended:** Define Taskfile.yml commands for common operations

**Example Taskfile.yml:**
```yaml
tasks:
  setup:grid:
    desc: Create GRID_DATA schema and tables
    cmds:
      - snow sql -f sql/setup/grid_setup.sql

  load:grid:
    desc: Load grid data from CSV files
    cmds:
      - snow sql -f sql/features/grid_load.sql

  teardown:grid:
    desc: Remove GRID_DATA schema
    cmds:
      - snow sql -f sql/teardown/grid_teardown.sql

  demo:full:
    desc: Full demo setup (all schemas)
    cmds:
      - task: setup:grid
      - task: setup:customer
      - task: load:grid
      - task: load:customer
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

**Problem:**
```sql
CREATE SCHEMA IF NOT EXISTS my_schema;
CREATE OR REPLACE TABLE table1 (...);
CREATE OR REPLACE TABLE table2 (...);
CREATE OR REPLACE TABLE table3 (...);
```

**Why It Fails:** User sees no feedback during long setup. Hard to spot where errors occur.

**Correct Pattern:**
```sql
CREATE SCHEMA IF NOT EXISTS my_schema;
SELECT '[PASS] Schema created' AS progress;

CREATE OR REPLACE TABLE table1 (...);
SELECT '[PASS] table1 created' AS progress;

CREATE OR REPLACE TABLE table2 (...);
SELECT '[PASS] table2 created' AS progress;
```

### Anti-Pattern 4: No Educational Comments

**Problem:**
```sql
CREATE TABLE AMI_DATA (
    meter_id VARCHAR,
    reading_time TIMESTAMP_NTZ,
    consumption_kwh NUMBER(10,3)
);
```

**Why It Fails:** Demo audiences don't learn concepts. Acronyms like "AMI" are unexplained. No teaching value.

**Correct Pattern:**
```sql
-- AMI = Advanced Metering Infrastructure (smart meters)
-- Records electricity consumption every 15 minutes
CREATE TABLE AMI_DATA (
    meter_id VARCHAR,                    -- Unique meter identifier
    reading_time TIMESTAMP_NTZ,          -- When reading was taken
    consumption_kwh NUMBER(10,3)         -- Kilowatt-hours consumed
) COMMENT = 'Smart meter readings (15-minute intervals)';
```

## When to Use Production Patterns

**If user requests:**
- "production ready"
- "production quality"
- "for automation"
- "CI/CD pipeline"
- "parameterized templates"
- "multi-environment deployment"

**Then use:** `102a-snowflake-sql-automation.md` for:
- SQL templates with variables (`<%DATABASE%>`, `<%SCHEMA%>`)
- Production idempotency (MERGE, WHERE NOT EXISTS)
- CREATE TABLE IF NOT EXISTS (never CREATE OR REPLACE TABLE)
- Environment-agnostic patterns
- CI/CD integration
