# Snowflake SQL: Demo Engineering and Learning

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** teardown, customer_load.sql, inline documentation, progress indicators, rerunnable demos, Snowflake SQL, CREATE OR REPLACE, educational SQL, demo patterns, demo data, setup scripts, demo automation, learning examples
**TokenBudget:** ~4850
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Guide SQL file creation for Snowflake demos and customer learning environments. Prioritizes ease of use, readability, and educational value over automation complexity. Optimized for pre-sales engineers, field teams, and customers learning Snowflake capabilities.

## Rule Scope

Demo SQL files, workshop materials, customer learning environments, quickstart guides

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use `<schema>_<operation>.sql` naming** - e.g., `grid_setup.sql`, `customer_load.sql` (self-documenting)
- **Per-schema isolation** - setup/teardown files affect only their target schema, never the database
- **Idempotent patterns** - `CREATE OR REPLACE TABLE`, `CREATE SCHEMA IF NOT EXISTS`, `DROP SCHEMA IF EXISTS CASCADE`
- **Progress indicators** - Include `SELECT '[PASS] Step complete' AS progress;` after each major operation
- **Inline education** - Comments explain "why" and define acronyms (e.g., "SCADA = Supervisory Control And Data Acquisition")
- **Fully qualified names** - Always use `DATABASE.SCHEMA.OBJECT` format
- **Never use `ON_ERROR` inside `FILE_FORMAT`** - It's a COPY INTO parameter, not FILE_FORMAT parameter

**Quick Checklist:**
- [ ] Filename follows `<schema>_<operation>.sql` pattern
- [ ] File header lists prerequisites and what gets created
- [ ] Progress SELECT statements after each major step
- [ ] All object names fully qualified (DB.SCHEMA.OBJECT)
- [ ] Script is rerunnable (idempotent patterns)
- [ ] Comments teach concepts, not just describe syntax

## Contract

<contract>
<inputs_prereqs>
Demo environment, Snowflake CLI access, CSV data files, database already created
</inputs_prereqs>

<mandatory>
Snowflake CLI (`snow sql`), Taskfile, SnowSQL, Snowsight
</mandatory>

<forbidden>
Production deployment tools, automated schedulers
</forbidden>

<steps>
1. Create per-schema setup files with inline documentation
2. Add progress indicators after each major step
3. Use idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)
4. Create independent teardown files per schema
5. Test rerunability (scripts should work multiple times)
</steps>

<output_format>
SQL files with .sql extension, UTF-8 encoding, Unix line endings
</output_format>

<validation>
Run setup, then verify objects created, then run teardown, then verify cleanup, then rerun setup (idempotency test)
</validation>

<design_principles>
- **Readability First**: Simple, self-documenting filenames and patterns
- **Per-Schema Operations**: Independent setup/load/teardown per schema
- **Educational Value**: Inline documentation that teaches concepts
- **Rerunnable Demos**: Idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)
- **Audience-Aware**: Comments explain "why" for learning, not just "what"
- **Demo-Safe**: Patterns suitable for ephemeral environments, not production databases
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Dropping Database or Shared Resources in Demo Files**
```sql
-- Bad: Demo file drops entire database!
DROP DATABASE IF EXISTS DEMO_DB;
CREATE DATABASE DEMO_DB;

-- Cleanup section:
DROP DATABASE DEMO_DB;  -- Destroys ALL schemas, not just demo schema!
-- Accidentally drops production data if run in wrong environment!
```
**Problem:** Catastrophic data loss; affects other demos; production risk; not isolated; unprofessional; emergency recovery; reputation damage

**Correct Pattern:**
```sql
-- Good: Drop only target schema, never database
-- Setup section
CREATE SCHEMA IF NOT EXISTS DEMO_DB.CUSTOMER_ANALYTICS;
USE SCHEMA DEMO_DB.CUSTOMER_ANALYTICS;

-- Demo code here...

-- Cleanup section (at end of file)
/*
-- To clean up this demo:
DROP SCHEMA IF EXISTS DEMO_DB.CUSTOMER_ANALYTICS CASCADE;
*/
-- Affects only this schema, other schemas untouched, safe!
```
**Benefits:** Schema isolation; no data loss; other demos unaffected; production-safe; professional; selective cleanup; reliable


**Anti-Pattern 2: Not Making Demo Files Idempotent**
```sql
-- Bad: Fails on second run
CREATE SCHEMA customer_analytics;
CREATE TABLE customers (id INT, name STRING);
INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob');

-- Second run: ERROR - Schema already exists!
-- Third run: ERROR - Table already exists!
-- Fourth run: Duplicate data inserted!
```
**Problem:** Not rerunnable; manual cleanup required; breaks demos; unprofessional; frustration; wasted time; poor user experience

**Correct Pattern:**
```sql
-- Good: Idempotent operations
CREATE SCHEMA IF NOT EXISTS customer_analytics;
USE SCHEMA customer_analytics;

CREATE TABLE IF NOT EXISTS customers (
  id INT PRIMARY KEY,
  name STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Idempotent insert: only insert if not exists
MERGE INTO customers tgt
USING (SELECT 1 AS id, 'Alice' AS name UNION ALL
       SELECT 2, 'Bob') src
ON tgt.id = src.id
WHEN NOT MATCHED THEN INSERT (id, name) VALUES (src.id, src.name);

-- Can run multiple times without errors!
```
**Benefits:** Rerunnable; no manual cleanup; demo-friendly; professional; reliable; good UX; frustration-free


**Anti-Pattern 3: Missing Environment Variables for Portability**
```sql
-- Bad: Hardcoded database and schema names
USE DATABASE PROD_DB;  -- Hardcoded!
USE SCHEMA PUBLIC;

CREATE TABLE PROD_DB.PUBLIC.demo_customers AS  -- Hardcoded!
SELECT * FROM PROD_DB.PUBLIC.source_data;

-- Can't run in DEV or TEST without manual edits!
```
**Problem:** Not portable; can't test in dev; manual edits required; error-prone; production risk; not CI/CD friendly; unprofessional

**Correct Pattern:**
```sql
-- Good: Use Snowflake variables for environment portability
/*!
File: customer_analytics_demo.sql
Purpose: Customer analytics demo showcasing aggregations and joins

Environment Variables:
  DATABASE: Target database (e.g., DEV_DB, TEST_DB, PROD_DB)
  SCHEMA: Target schema (e.g., DEMO_CUSTOMER_ANALYTICS)

Usage:
  snowsql -D DATABASE=DEV_DB -D SCHEMA=DEMO_CUSTOMER_ANALYTICS -f customer_analytics_demo.sql
*/

-- Create schema using variables
CREATE SCHEMA IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>;
USE SCHEMA <%DATABASE%>.<%SCHEMA%>;

-- Create tables using variables
CREATE TABLE IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.demo_customers AS
SELECT * FROM <%DATABASE%>.PUBLIC.source_data;

-- Works in DEV, TEST, PROD without code changes!
```
**Benefits:** Environment portable; testable in dev; no manual edits; error-free; production-safe; CI/CD friendly; professional


**Anti-Pattern 4: No Sample Output or Expected Results Documentation**
```sql
-- Bad: No sample output, users don't know what to expect
SELECT
  customer_id,
  COUNT(*) AS order_count,
  SUM(amount) AS total_amount
FROM orders
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 10;

-- Output: ???
-- User: "Is this correct? What should I see?"
```
**Problem:** No validation; unclear expectations; users unsure if demo works; hard to debug; poor documentation; unprofessional; confusion

**Correct Pattern:**
```sql
-- Good: Document expected output
-- Query: Top 10 customers by total spend
SELECT
  customer_id,
  COUNT(*) AS order_count,
  SUM(amount) AS total_amount
FROM orders
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 10;

/*
Expected Output (sample):
+-------------+-------------+--------------+
| CUSTOMER_ID | ORDER_COUNT | TOTAL_AMOUNT |
+-------------+-------------+--------------+
| C001        |          15 |      5234.50 |
| C042        |           8 |      4890.25 |
| C103        |          12 |      4567.80 |
| ...         |         ... |          ... |
+-------------+-------------+--------------+

Validation:
- Should return exactly 10 rows
- TOTAL_AMOUNT should be in descending order
- ORDER_COUNT should be positive integers
- No NULL values in any column

If you see errors or different output:
1. Verify orders table has data: SELECT COUNT(*) FROM orders;
2. Check for NULL amounts: SELECT COUNT(*) FROM orders WHERE amount IS NULL;
3. Review Query Profile for performance issues
*/
```
**Benefits:** Clear expectations; easy validation; debuggable; documented; professional; good UX; confidence-building

## Post-Execution Checklist

**File Naming:**
- [ ] Filename uses schema_operation.sql pattern (grid_setup.sql, customer_load.sql)
- [ ] Clear what schema and operation from filename alone
- [ ] No numeric prefixes unless order dependencies exist

**Schema Isolation:**
- [ ] File can run independently without affecting other schemas
- [ ] Does NOT drop database or shared resources
- [ ] Teardown only affects target schema

**Educational Value:**
- [ ] Inline comments explain concepts for learning
- [ ] Acronyms and domain terms defined
- [ ] "Why" explained, not just "what"

**Demo-Safe Patterns:**
- [ ] Uses CREATE OR REPLACE and IF NOT EXISTS for rerunnable demos
- [ ] Includes progress indicators (SELECT statements)
- [ ] Final success message confirms completion

**File Structure:**
- [ ] Header includes prerequisites and what gets created
- [ ] Fully qualified object names used (DATABASE.SCHEMA.OBJECT)
- [ ] COPY INTO syntax correct (ON_ERROR outside FILE_FORMAT)
- [ ] CREATE VIEW has COMMENT before AS
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in comments, synonyms, or strings

**Demo Experience:**
- [ ] Scripts provide immediate feedback
- [ ] Safe to rerun multiple times
- [ ] Clear error messages if prerequisites missing
- [ ] SQL files execute successfully via CLI (`snow sql -f file.sql`)

## Validation
- **Success Checks:**
  - SQL files execute without errors in Snowsight and CLI
  - Progress indicators display after each step
  - Scripts can be rerun without errors (idempotent)
  - Per-schema teardown removes only target schema
  - Comments are educational and explain concepts
  - Fully qualified names work regardless of session context
- **Negative Tests:**
  - Teardown does NOT drop other schemas
  - Teardown does NOT drop database
  - Missing prerequisites cause clear error messages
  - ON_ERROR inside FILE_FORMAT causes syntax error
  - COMMENT after AS in CREATE VIEW causes syntax error
  - Non-qualified names may fail in CLI without session context

> **Investigation Required**
> When applying this rule:
> 1. **Read existing SQL files BEFORE making recommendations** - Never assume demo structure or naming patterns
> 2. **Verify actual object names and schemas** - Check what database/schema names are being used in the project
> 3. **Never speculate about file organization** - List directory contents to understand current structure
> 4. **Check for existing Taskfile.yml** - Read it to understand automation patterns before suggesting changes
> 5. **Make grounded recommendations based on investigated project structure** - Don't recommend patterns that conflict with existing setup
>
> **Anti-Pattern:**
> "Based on typical demo patterns, you probably have a setup/ directory..."
> "Usually demos use DATABASE_DEMO as the database name..."
>
> **Correct Pattern:**
> "Let me check your current SQL file organization first."
> [reads sql/ directory and existing files]
> "I see you're using UTILITY_DEMO_V2 as the database and have grid_setup.sql. Here's how to add customer_setup.sql following the same pattern..."

## Output Format Examples
```sql
-- ============================================================================
-- Filename: grid_setup.sql
-- Description: Create GRID_DATA schema and all related objects
--
-- Prerequisites: Database UTILITY_DEMO_V2 must exist
-- Creates: GRID_DATA schema, 5 tables, 1 stage, 2 views
-- ============================================================================

-- Step 1: Create schema
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA
    COMMENT = 'Grid asset and sensor data for predictive maintenance';

SELECT '[PASS] Schema created' AS progress;

-- Step 2: Create tables with inline documentation
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (
    asset_id VARCHAR PRIMARY KEY,      -- Unique identifier
    asset_type VARCHAR,                 -- TRANSFORMER, SUBSTATION, etc.
    install_date DATE                   -- Age impacts failure risk
) COMMENT = 'Core grid infrastructure assets';

SELECT '[PASS] Tables created' AS progress;

SELECT 'GRID_DATA schema setup complete!' AS status;
```

## References

### External Documentation

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) - Complete SQL command reference
- [COPY INTO Documentation](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) - Loading data from stages
- [CREATE VIEW Documentation](https://docs.snowflake.com/en/sql-reference/sql/create-view) - View syntax and options
- [Stages Overview](https://docs.snowflake.com/en/user-guide/data-load-overview) - Understanding Snowflake stages

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **SQL Automation**: `rules/102a-snowflake-sql-automation.md` - Production SQL templates and CI/CD patterns
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md` - Query optimization
- **Data Loading**: `rules/108-snowflake-data-loading.md` - Comprehensive data loading patterns

## 1. File Naming for Demos

### 1.1 Schema-Based Naming Pattern

**Rule:** Use `<schema>_<operation>.sql` format for maximum clarity

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
- No need to remember numeric sequences

### 1.2 Multi-Step Operations

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

## 2. Per-Schema Setup and Teardown

### 2.1 Schema Isolation Requirements

**Critical:** Each schema's setup/teardown must be fully independent

**Schema-Specific File Checklist:**
- [ ] Creates/drops only objects in target schema
- [ ] Does NOT drop database or shared resources
- [ ] Does NOT affect other schemas
- [ ] Can run in any order relative to other schemas
- [ ] Handles dependencies within schema only

**Why this matters:** Demo users should be able to explore one schema (e.g., GRID_DATA) without breaking another (e.g., CUSTOMER_DATA).

### 2.2 Setup File Pattern

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

**Key Features:**
- Step-by-step structure with explanations
- Progress indicators after each step
- Inline comments explain "why" (educational)
- Idempotent (safe to rerun)
- Final success message

### 2.3 Teardown File Pattern

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

**Key Features:**
- Clear warning about data loss
- Explicit about what's NOT affected
- CASCADE removes all child objects
- Single command (simplicity)

### 2.4 Load File Pattern

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

-- Load failure events
COPY INTO UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS
FROM @UTILITY_DEMO_V2.GRID_DATA.DATA_FILES
PATTERN = '.*failure_events.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

SELECT '[PASS] Failure events loaded' AS progress;

SELECT 'Grid data load complete!' AS status;
```

**Key Features:**
- Clear prerequisites listed
- Educational comments (explain acronyms)
- Pattern matching for flexible file names
- Progress after each table load

## 3. Demo-Specific Best Practices

### 3.1 Inline Documentation

**Rule:** SQL files for demos should teach as they execute

**Pattern:**
- Explain concepts in comments
- Use "Step 1, Step 2" structure
- Inline comments for column purposes
- Reference documentation where helpful
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

### 3.2 Progress Indicators

**Rule:** Include SELECT statements to show progress

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

### 3.3 Idempotent Patterns for Demos

**Rule:** Make demos rerunnable without errors

**Demo-Safe Patterns:**
```sql
-- Schema: IF NOT EXISTS (won't error if exists)
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;

-- Tables: CREATE OR REPLACE (drops and recreates - OK for demos)
-- This deletes data - only safe for demo/dev environments
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);

-- Views: CREATE OR REPLACE (always safe - no data loss)
CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_SUMMARY AS ...;

-- Stages: CREATE OR REPLACE (safe - files remain)
CREATE OR REPLACE STAGE UTILITY_DEMO_V2.GRID_DATA.DATA_FILES;
```

**Why this matters:** Demo users may run scripts multiple times. These patterns prevent errors and make demos smooth.

**NOT production-safe:** CREATE OR REPLACE TABLE deletes data. For production, use `102a-snowflake-sql-automation.md`.

## 4. Common SQL Syntax Patterns

### 4.1 COPY INTO Syntax

**Rule:** COPY INTO loads CSV/JSON/Parquet files from stages into tables

**Basic Pattern:**
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

**Critical:** `ON_ERROR` is a COPY INTO parameter, not a FILE_FORMAT parameter

**Correct:**
```sql
-- Place ON_ERROR outside FILE_FORMAT
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';

-- Or omit ON_ERROR (defaults to ABORT_STATEMENT)
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);
```

**Incorrect:**
```sql
-- ON_ERROR inside FILE_FORMAT causes syntax error
COPY INTO my_table
FROM @my_stage/file.csv
FILE_FORMAT = (
    TYPE = 'CSV',
    ON_ERROR = 'CONTINUE'  -- Invalid placement
);
```

### 4.2 CREATE VIEW with Comments

**Rule:** COMMENT must be placed before AS in CREATE VIEW

**Correct:**
```sql
CREATE OR REPLACE VIEW my_db.my_schema.my_view
COMMENT = 'Business-friendly view for dashboard'
AS
SELECT
    asset_id,
    failure_count,
    total_cost
FROM my_db.my_schema.base_table;
```

**Incorrect:**
```sql
-- COMMENT after query causes syntax error
CREATE OR REPLACE VIEW my_db.my_schema.my_view AS
SELECT asset_id, failure_count
FROM base_table
COMMENT = 'My view';  -- Wrong position
```

### 4.3 Fully Qualified Object Names

**Rule:** Always use DATABASE.SCHEMA.OBJECT format in SQL files

**Why:** Ensures scripts work regardless of current session context

**Correct:**
```sql
-- [PASS] Fully qualified - always works
CREATE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);

COPY INTO UTILITY_DEMO_V2.GRID_DATA.SCADA_DATA
FROM @UTILITY_DEMO_V2.GRID_DATA.DATA_FILES/scada.csv
FILE_FORMAT = (TYPE = 'CSV');

SELECT * FROM UTILITY_DEMO_V2.GRID_DATA.VW_ASSET_FAILURES;
```

**Incorrect:**
```sql
-- Assumes session context - fragile
USE DATABASE UTILITY_DEMO_V2;
USE SCHEMA GRID_DATA;
CREATE TABLE GRID_ASSETS (...);  -- May fail in CLI automation
```

**When USE is acceptable:**
- Interactive sessions in Snowsight
- Single-file scripts executed as one unit
- Development/exploration

### 4.4 Reserved Characters (CLI Compatibility)

**Rule:** Avoid characters that Snowflake CLI or SnowSQL interpret as template variables in SQL files.

**Why:** Demo SQL files are often executed via CLI tools (`snow sql`, `snowsql`) or CI/CD pipelines. Template characters cause cryptic errors that are hard to debug.

**Forbidden Characters:**
- **`&`** - Snowflake CLI (`snow sql`) interprets as template variable prefix
- **`<%` and `%>`** - SnowSQL interprets as variable delimiters
- **`{{` and `}}`** - Jinja2, dbt interpret as template syntax

**Incorrect:**
```sql
-- Bad: & in comments, synonyms, or string literals
CREATE TABLE departments (
    dept_name VARCHAR COMMENT 'R&D or Sales & Marketing'  -- & causes CLI error!
);

-- Bad: Template syntax in comments
-- Deploy to <%ENV%> environment  -- SnowSQL tries to expand this!

CREATE SEMANTIC VIEW my_view AS
  DIMENSIONS (
    dept AS departments.dept_name
      SYNONYMS ('R&D', 'Sales & Marketing')  -- & causes CLI error!
  );
```

**Correct:**
```sql
-- Good: Use 'and' instead of '&'
CREATE TABLE departments (
    dept_name VARCHAR COMMENT 'R and D or Sales and Marketing'
);

-- Good: Plain text comments
-- Deploy to DEV/PROD environment

CREATE SEMANTIC VIEW my_view AS
  DIMENSIONS (
    dept AS departments.dept_name
      SYNONYMS ('R and D', 'Research and Development', 'Sales and Marketing')
  );
```

**Common Substitutions:**
- **`R&D`** - Use `R and D` or `Research and Development` instead
- **`Sales & Marketing`** - Use `Sales and Marketing` instead
- **`P&L`** - Use `P and L` or `Profit and Loss` instead
- **`<%VAR%>`** - Use Snowflake CLI `--variable` flag instead

## 5. File Headers for Demos

### 5.1 Standard Header Format

**Rule:** All SQL files must use consistent header format

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
-- Filename: grid_setup.sql
-- Description: Create GRID_DATA schema and all related objects
--
-- Prerequisites: Database UTILITY_DEMO_V2 must exist
-- Creates: GRID_DATA schema, 5 tables, 1 stage, 2 views
-- ============================================================================
```

### 5.2 Section Dividers (Optional)

**Use when:** Script has distinct phases or multiple operations

**Pattern:**
```sql
-- ===========================================================================
-- SECTION NAME: BRIEF DESCRIPTION
-- ===========================================================================
```

**Example:**
```sql
-- ============================================================================
-- Filename: grid_setup.sql
-- Description: Create GRID_DATA schema and all related objects
-- ============================================================================

-- ===========================================================================
-- SCHEMA SETUP
-- ===========================================================================
CREATE SCHEMA IF NOT EXISTS UTILITY_DEMO_V2.GRID_DATA;

-- ===========================================================================
-- TABLE DEFINITIONS
-- ===========================================================================
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (...);
CREATE OR REPLACE TABLE UTILITY_DEMO_V2.GRID_DATA.SCADA_DATA (...);

-- ===========================================================================
-- VIEWS AND ANALYSIS OBJECTS
-- ===========================================================================
CREATE OR REPLACE VIEW UTILITY_DEMO_V2.GRID_DATA.VW_SUMMARY AS ...;
```

## 6. Demo Project Structure

### 6.1 Recommended Directory Structure

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

**Benefits:**
- Clear organization by purpose
- Easy to run specific parts of demo
- Setup/teardown clearly separated
- Features can be run selectively

### 6.2 Task Commands Pattern

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

## When to Use Production Patterns

**If user requests:**
- "production ready"
- "production quality"
- "for automation"
- "CI/CD pipeline"
- "parameterized templates"
- "multi-environment deployment"

**Then reference:** `102a-snowflake-sql-automation.md` for:
- SQL templates with variables (`<%DATABASE%>`, `<%SCHEMA%>`)
- Production idempotency (MERGE, WHERE NOT EXISTS)
- Environment-agnostic patterns
- CI/CD integration
- Audit trail requirements
