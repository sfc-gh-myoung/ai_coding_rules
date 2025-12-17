# Snowflake SQL: Production Automation and CI/CD

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** idempotent, MERGE, operations, multi-environment, infrastructure as code, Snowflake variables, production-safe, upsert, SQL automation, deployment scripts, SQL pipeline, config management, environment variables
**TokenBudget:** ~4050
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/102-snowflake-sql-demo-engineering.md

## Purpose
Guide creation of parameterized SQL templates for automated Snowflake deployments in production environments. Supports CI/CD pipelines, multi-environment workflows, and infrastructure-as-code patterns. Optimized for DevOps engineers, data engineers, and automated deployment systems.

## Rule Scope

Production SQL templates, CI/CD pipelines, multi-environment deployments, automated workflows

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use `<%VARIABLE%>` for parameterization** - All environment values as variables: `<%DATABASE%>`, `<%SCHEMA%>`, `<%STAGE%>`
- **NEVER use `CREATE OR REPLACE TABLE` in production** - Data loss risk! Use `CREATE TABLE IF NOT EXISTS` instead
- **Use MERGE for idempotent upserts** - Updates existing, inserts new, safe to rerun
- **Document parameters in header** - List all variables with descriptions and concrete examples
- **Test across dev/test before production** - Same SQL, different variables per environment
- **Never hardcode database/schema names** - Breaks environment portability

**Quick Checklist:**
- [ ] All environment values parameterized (`<%VARIABLE%>`)
- [ ] Header documents parameters with usage examples
- [ ] Uses `CREATE TABLE IF NOT EXISTS` (never `CREATE OR REPLACE TABLE`)
- [ ] Data updates use MERGE or `INSERT WHERE NOT EXISTS`
- [ ] Tested in dev/test environments
- [ ] CI/CD pipeline configured with environment secrets

## Contract

<contract>
<inputs_prereqs>
Production Snowflake account, CI/CD pipeline, SQL templates with variables, environment-specific secrets
</inputs_prereqs>

<mandatory>
Snowflake CLI, Task automation, GitHub Actions, Terraform
</mandatory>

<forbidden>
Manual UI operations, hardcoded credentials, CREATE OR REPLACE for tables with data
</forbidden>

<steps>
1. Create parameterized SQL templates with variables
2. Use idempotent patterns (MERGE, IF NOT EXISTS)
3. Never use CREATE OR REPLACE for tables (data loss risk)
4. Add validation scripts for pre/post deployment
5. Integrate with CI/CD pipeline
6. Test across dev/test environments before production
</steps>

<output_format>
SQL template files (.sql), Taskfile.yml tasks, CI/CD workflow files
</output_format>

<validation>
Template validation, then dev deployment, then test verification, then production deployment, then post-deploy checks
</validation>

<design_principles>
- **Parameterization**: All environment-specific values as variables
- **Idempotency**: Safe to run multiple times (MERGE, WHERE NOT EXISTS)
- **Environment Agnostic**: Works across dev/test/prod with different parameters
- **Automation Ready**: Integrates with Taskfile, GitHub Actions
- **Audit Trail**: Clear tracking of what was executed and when
- **Data Preservation**: Never use CREATE OR REPLACE for tables with data
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using CREATE OR REPLACE for Tables in Automation**
```sql
-- Bad: Drops and recreates table, loses all data!
CREATE OR REPLACE TABLE <%DATABASE%>.<%SCHEMA%>.customers AS
SELECT * FROM raw_customers WHERE is_active = TRUE;
-- Next run: All data lost, recreated from scratch!
```
**Problem:** Data loss on every run; not incremental; breaks downstream dependencies; table permissions reset; emergency data recovery; production outage

**Correct Pattern:**
```sql
-- Good: Use CREATE TABLE IF NOT EXISTS + MERGE for incremental updates
CREATE TABLE IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.customers (
  customer_id NUMBER PRIMARY KEY,
  name STRING,
  email STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

MERGE INTO <%DATABASE%>.<%SCHEMA%>.customers tgt
USING (SELECT * FROM raw_customers WHERE is_active = TRUE) src
ON tgt.customer_id = src.customer_id
WHEN MATCHED THEN
  UPDATE SET
    name = src.name,
    email = src.email,
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, email, created_at, updated_at)
  VALUES (src.customer_id, src.name, src.email, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
```
**Benefits:** No data loss; incremental updates; idempotent; preserves permissions; production-safe; no outages; reliable automation


**Anti-Pattern 2: Hardcoding Database/Schema Names Instead of Variables**
```sql
-- Bad: Hardcoded names, can't reuse across environments
CREATE TABLE PROD_DB.PUBLIC.sales_summary AS
SELECT
  DATE_TRUNC('day', order_date) as day,
  SUM(amount) as total_sales
FROM PROD_DB.PUBLIC.orders
GROUP BY day;
-- Can't deploy to DEV or TEST! Manual find/replace required!
```
**Problem:** Not portable across environments; manual modifications required; error-prone deployment; can't test in dev; production-only scripts; breaks CI/CD

**Correct Pattern:**
```sql
-- Good: Use Snowflake variables for portability
/*!
Parameters:
  DATABASE: Target database (e.g., PROD_DB, DEV_DB, TEST_DB)
  SCHEMA: Target schema (e.g., PUBLIC, ANALYTICS)

Usage:
  snowsql -D DATABASE=DEV_DB -D SCHEMA=PUBLIC -f sales_summary.sql
*/

CREATE TABLE IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.sales_summary (
  day DATE,
  total_sales NUMBER(38,2)
);

INSERT INTO <%DATABASE%>.<%SCHEMA%>.sales_summary
SELECT
  DATE_TRUNC('day', order_date) as day,
  SUM(amount) as total_sales
FROM <%DATABASE%>.<%SCHEMA%>.orders
WHERE DATE_TRUNC('day', order_date) NOT IN (SELECT day FROM <%DATABASE%>.<%SCHEMA%>.sales_summary)
GROUP BY day;
```
**Benefits:** Environment-portable; testable in dev; CI/CD-friendly; no manual edits; reliable deployment; professional automation; multi-environment support


**Anti-Pattern 3: Missing Documentation Header in SQL Templates**
```sql
-- Bad: No header, unclear purpose and usage
SELECT * FROM customers WHERE region = '<%REGION%>';
-- What is REGION? What are valid values? How to run this?
```
**Problem:** Unclear purpose; unknown parameters; no usage examples; difficult maintenance; knowledge silos; onboarding friction; support burden

**Correct Pattern:**
```sql
-- Good: Comprehensive header documentation
/*!
Script: regional_customer_report.sql
Purpose: Generate customer report filtered by region for monthly analysis
Author: data-engineering-team
Created: 2024-11-15
Last Modified: 2024-11-20

Parameters:
  REGION: Geographic region code (required)
    Valid values: 'NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL'
    Example: REGION=WEST

Usage:
  Development:
    snowsql -D REGION=WEST -f regional_customer_report.sql

  Production (CI/CD):
    snow sql -f regional_customer_report.sql --variable REGION=EAST

Dependencies:
  - Source table: RAW_DB.PUBLIC.CUSTOMERS must exist
  - Requires SELECT on RAW_DB.PUBLIC.CUSTOMERS

Idempotency:
  - Safe to run multiple times
  - Uses CREATE TABLE IF NOT EXISTS
  - Incremental MERGE prevents duplicates
*/

SELECT * FROM customers WHERE region = '<%REGION%>';
```
**Benefits:** Clear purpose; documented parameters; usage examples; easy maintenance; self-documenting; onboarding-friendly; reduced support; professional


**Anti-Pattern 4: Not Making SQL Scripts Idempotent**
```sql
-- Bad: Fails on second run
CREATE TABLE analytics_summary AS
SELECT * FROM raw_data;

INSERT INTO metrics
SELECT COUNT(*) FROM analytics_summary;
-- Second run: ERROR - Table already exists!
```
**Problem:** Not repeatable; fails on re-run; manual cleanup required; breaks automation; CI/CD failures; deployment fragility; unprofessional

**Correct Pattern:**
```sql
-- Good: Idempotent operations
CREATE TABLE IF NOT EXISTS analytics_summary (
  -- schema definition
);

-- Clear existing data for this run's date range
DELETE FROM analytics_summary
WHERE report_date = CURRENT_DATE();

-- Insert today's data
INSERT INTO analytics_summary
SELECT * FROM raw_data WHERE DATE(created_at) = CURRENT_DATE();

-- Upsert metrics (idempotent)
MERGE INTO metrics m
USING (SELECT COUNT(*) as cnt FROM analytics_summary WHERE report_date = CURRENT_DATE()) s
ON m.report_date = CURRENT_DATE()
WHEN MATCHED THEN UPDATE SET row_count = s.cnt
WHEN NOT MATCHED THEN INSERT (report_date, row_count) VALUES (CURRENT_DATE(), s.cnt);
```
**Benefits:** Repeatable execution; safe re-runs; no manual cleanup; automation-friendly; CI/CD reliable; production-ready; professional deployment

## Post-Execution Checklist

**Template Requirements:**
- [ ] Uses Snowflake variables (`<%DATABASE%>`, `<%SCHEMA%>`)
- [ ] Header documents all parameters with examples
- [ ] Usage section shows concrete example
- [ ] Idempotency explained in header

**Production Safety:**
- [ ] Uses CREATE TABLE IF NOT EXISTS (never CREATE OR REPLACE for tables)
- [ ] Data updates use MERGE or INSERT WHERE NOT EXISTS
- [ ] Views can use CREATE OR REPLACE (safe)
- [ ] No hardcoded database or schema names

**File Organization:**
- [ ] Located in sql/operations/ directory structure
- [ ] Grouped by domain and operation type
- [ ] Testable independently
- [ ] Reusable across environments

**Automation Integration:**
- [ ] Taskfile defines reusable tasks
- [ ] CI/CD workflow defined
- [ ] Environment variables externalized
- [ ] Validation scripts included

**Idempotency:**
- [ ] Safe to run multiple times
- [ ] MERGE used for data upserts
- [ ] IF NOT EXISTS for object creation
- [ ] No data loss risk from reruns

## Validation
- **Success Checks:**
  - Templates execute successfully across dev/test/prod
  - Same SQL works with different variables
  - Reruns don't cause errors or data loss
  - MERGE operations handle duplicates correctly
  - CI/CD pipeline deploys changes automatically
  - Validation scripts catch issues before production
- **Negative Tests:**
  - Missing variable causes clear error
  - Invalid database name fails gracefully
  - CREATE OR REPLACE on tables is flagged in code review
  - Duplicate key in MERGE handled correctly
  - Failed deployment rolls back cleanly

> **Investigation Required**
> When applying this rule:
> 1. **Read existing CI/CD files BEFORE making recommendations** - Check for GitHub Actions or other automation
> 2. **Verify current Taskfile.yml structure** - Understand existing task patterns and variable usage
> 3. **Never speculate about deployment environments** - Ask user about dev/test/prod setup if unclear
> 4. **Check existing SQL templates for patterns** - Match parameterization style with current codebase
> 5. **Make grounded recommendations based on investigated automation setup** - Don't recommend CI/CD platforms without checking what's in use
>
> **Anti-Pattern:**
> "Most projects use GitHub Actions for CI/CD, so let's set that up..."
> "Based on typical patterns, you probably have a .github/workflows/ directory..."
>
> **Correct Pattern:**
> "Let me check your current automation setup first."
> [reads Taskfile.yml, .github/workflows/]
> "I see you're using GitHub Actions with Taskfile integration. Here's how to add SQL template deployment to your existing workflow..."

## Output Format Examples
```sql
-- ============================================================================
-- Filename: merge_grid_assets.sql
-- Description: Upsert grid assets from stage (production-safe)
--
-- Parameters:
--   DATABASE - Database name (e.g., UTILITY_DEMO_V2)
--   SCHEMA   - Schema name (e.g., GRID_DATA)
--   STAGE    - Stage name (e.g., @UTILITY_DEMO_V2.GRID_DATA.FILES)
--
-- Usage:
--   snow sql -D DATABASE=DB -D SCHEMA=SCH -D STAGE=STG -f merge_grid_assets.sql
--
-- Example:
--   snow sql -D DATABASE=PROD -D SCHEMA=GRID_DATA -D STAGE=@PROD.GRID_DATA.FILES -f merge_grid_assets.sql
--
-- Dependencies: GRID_ASSETS table must exist, stage must have CSV files
-- Idempotency: MERGE ensures safe reruns (updates/inserts)
-- ============================================================================

-- Load into temp table
CREATE TEMP TABLE GRID_ASSETS_STAGE LIKE <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS;

COPY INTO GRID_ASSETS_STAGE
FROM @<%STAGE%>
PATTERN = '.*grid_assets.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

-- Merge into production
MERGE INTO <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS AS target
USING GRID_ASSETS_STAGE AS source
    ON target.asset_id = source.asset_id
WHEN MATCHED THEN UPDATE SET /* ... */
WHEN NOT MATCHED THEN INSERT /* ... */;
```

## References

### External Documentation

- [Snowflake SQL Variables](https://docs.snowflake.com/en/user-guide/snowsql-use#using-variables) - Variable syntax and usage
- [MERGE Statement](https://docs.snowflake.com/en/sql-reference/sql/merge) - Idempotent upsert patterns
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/index) - CLI automation
- [GitHub Actions for Snowflake](https://github.com/Snowflake-Labs/snowflake-cli-action) - CI/CD integration

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md` - Demo and learning SQL patterns
- **Taskfile Automation**: `rules/820-taskfile-automation.md` - Task automation patterns
- **Git Workflow**: `rules/803-project-git-workflow.md` - Branching and PR strategies

## 1. SQL Template Patterns

### 1.1 Snowflake Variable Syntax

**Rule:** Use `<%VARIABLE%>` for parameter substitution

**CLI Usage:**
```bash
snow sql -D DATABASE=PROD -D SCHEMA=GRID -f template.sql
```

**Why:** Variables make SQL reusable across environments without code duplication

### 1.2 Template File Structure

**Standard Template:**
```sql
-- ============================================================================
-- Filename: copy_grid_assets.sql
-- Description: Load grid assets from stage (parameterized template)
--
-- Parameters:
--   DATABASE - Database name (e.g., UTILITY_DEMO_V2)
--   SCHEMA   - Schema name (e.g., GRID_DATA)
--   STAGE    - Fully qualified stage name
--
-- Usage:
--   snow sql -D DATABASE=DB -D SCHEMA=SCH -D STAGE=@DB.SCH.STG -f copy_grid_assets.sql
--
-- Example:
--   snow sql -D DATABASE=PROD -D SCHEMA=GRID -D STAGE=@PROD.GRID.FILES -f copy_grid_assets.sql
-- ============================================================================

COPY INTO <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS
FROM <%STAGE%>
PATTERN = '.*grid_assets.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';
```

**Required Sections:**
- **Parameters**: List all variables with descriptions
- **Usage**: Generic usage pattern
- **Example**: Concrete example with real values

### 1.3 Variable Naming Conventions

**Rule:** Use UPPERCASE for variable names

**Standard Variables:**
```text
<%DATABASE%>           # Database name
<%SCHEMA%>             # Schema name
<%TABLE%>              # Table name
<%STAGE%>              # Stage name (fully qualified)
<%WAREHOUSE%>          # Warehouse name
<%ENVIRONMENT%>        # Environment (DEV, TEST, PROD)
<%ROLE%>               # Role name for grants
```

## 2. Directory Structure for Operations

### 2.1 Operations Directory Pattern

**Structure:**

Directory structure for `sql/operations/`:
- **grid/** - Domain/schema grouping
  - **setup/** - `create_schema.sql`, `create_tables.sql`
  - **load/** - `copy_assets.sql`, `copy_scada.sql`
  - **merge/** - `upsert_assets.sql`, `upsert_events.sql`
  - **teardown/** - `drop_schema.sql`
- **customer/** - Customer domain
  - **setup/**, **load/**, **merge/**, **teardown/**
- **shared/** - Cross-domain scripts
  - `create_database.sql`, `create_roles.sql`, `drop_database.sql`

**Benefits:**
- Clear domain separation
- Operation types grouped together
- Testable in isolation
- Reusable across projects

### 2.2 Template Naming Convention

**Pattern:** `<operation>_<object>.sql`

**Examples:**
```text
create_schema.sql
create_table_assets.sql
copy_assets.sql
merge_assets.sql
grant_read_access.sql
drop_schema.sql
```

**No numeric prefixes:** Execution order controlled by automation, not filenames

## 3. Idempotent Production Patterns

### 3.1 Schema and Database Creation

**Rule:** Use IF NOT EXISTS for creation

**Pattern:**
```sql
-- Idempotent schema creation
CREATE SCHEMA IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>
    COMMENT = 'Grid data for <%ENVIRONMENT%> environment';

-- Idempotent database creation
CREATE DATABASE IF NOT EXISTS <%DATABASE%>
    COMMENT = 'Utility demo database - <%ENVIRONMENT%>';
```

**Why:** Safe to run in CI/CD repeatedly

### 3.2 Table Creation (Production)

**Rule:** Use CREATE TABLE IF NOT EXISTS, never CREATE OR REPLACE

**Critical:** CREATE OR REPLACE deletes data - unacceptable in production

**Pattern:**
```sql
-- ✓ Production-safe table creation
CREATE TABLE IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS (
    asset_id VARCHAR PRIMARY KEY,
    asset_type VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    install_date DATE
);

-- Add columns if schema evolves
ALTER TABLE <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS
ADD COLUMN IF NOT EXISTS region VARCHAR;
```

**Never do this in production:**
```sql
-- Destroys all data - production disaster
CREATE OR REPLACE TABLE <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS (...);
```

### 3.3 Data Loading with MERGE

**Rule:** Use MERGE for idempotent upserts

**Pattern:**
```sql
-- ============================================================================
-- Filename: merge_assets.sql
-- Description: Upsert grid assets (insert new, update existing)
--
-- Parameters:
--   DATABASE - Database name
--   SCHEMA   - Schema name
--   STAGE    - Stage name
-- ============================================================================

-- Step 1: Load into temp table
CREATE TEMP TABLE GRID_ASSETS_STAGE (
    asset_id VARCHAR,
    asset_type VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    install_date DATE
);

COPY INTO GRID_ASSETS_STAGE
FROM @<%STAGE%>
PATTERN = '.*grid_assets.*\\.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

-- Step 2: MERGE into production table
MERGE INTO <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS AS target
USING GRID_ASSETS_STAGE AS source
    ON target.asset_id = source.asset_id
WHEN MATCHED THEN
    UPDATE SET
        asset_type = source.asset_type,
        latitude = source.latitude,
        longitude = source.longitude,
        install_date = source.install_date
WHEN NOT MATCHED THEN
    INSERT (asset_id, asset_type, latitude, longitude, install_date)
    VALUES (source.asset_id, source.asset_type, source.latitude,
            source.longitude, source.install_date);

-- Step 3: Report results
SELECT 'Rows merged' AS operation, COUNT(*) AS row_count
FROM <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS;
```

**Why MERGE:**
- Idempotent (safe to rerun)
- Updates existing records
- Inserts new records
- Single atomic operation

### 3.4 View Updates

**Rule:** CREATE OR REPLACE is safe for views (no data loss)

**Pattern:**
```sql
-- Safe: Views don't store data
CREATE OR REPLACE VIEW <%DATABASE%>.<%SCHEMA%>.VW_ASSET_SUMMARY
COMMENT = 'Asset summary view for <%ENVIRONMENT%>'
AS
SELECT
    asset_type,
    COUNT(*) AS asset_count,
    AVG(DATEDIFF(YEAR, install_date, CURRENT_DATE())) AS avg_age_years
FROM <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS
GROUP BY asset_type;
```

## 4. CI/CD Integration

### 4.1 Taskfile Integration

**Pattern:**
```yaml
version: '3'

vars:
  DATABASE: UTILITY_DEMO_V2
  SCHEMA: GRID_DATA
  STAGE: '@{{.DATABASE}}.{{.SCHEMA}}.DATA_FILES'

tasks:
  sql:exec:
    desc: Execute SQL template with variables
    silent: true
    internal: true
    cmds:
      - >
        snow sql
        -D DATABASE={{.DATABASE}}
        -D SCHEMA={{.SCHEMA}}
        -D STAGE={{.STAGE}}
        -f {{.SQL_FILE}}

  operations:create-schema:
    desc: Create GRID_DATA schema
    cmds:
      - task: sql:exec
        vars:
          SQL_FILE: sql/operations/grid/setup/create_schema.sql

  operations:load-assets:
    desc: Load grid assets from stage
    cmds:
      - task: sql:exec
        vars:
          SQL_FILE: sql/operations/grid/load/copy_assets.sql

  operations:merge-assets:
    desc: Upsert grid assets (production-safe)
    cmds:
      - task: sql:exec
        vars:
          SQL_FILE: sql/operations/grid/merge/merge_assets.sql
```

**Benefits:**
- Environment variables centralized
- Reusable task patterns
- Easy to test locally
- CI/CD can call same commands

### 4.2 GitHub Actions Integration

**Pattern:**
```yaml
name: Deploy SQL Changes

on:
  push:
    branches: [main]
    paths:
      - 'sql/operations/**/*.sql'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Snowflake CLI
        run: pip install snowflake-cli-labs

      - name: Configure Snowflake Connection
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
        run: |
          snow connection add prod \
            --account $SNOWFLAKE_ACCOUNT \
            --user $SNOWFLAKE_USER \
            --password $SNOWFLAKE_PASSWORD

      - name: Deploy Schema Changes
        run: |
          snow sql \
            -D DATABASE=PROD \
            -D SCHEMA=GRID_DATA \
            -f sql/operations/grid/setup/create_schema.sql

      - name: Deploy Table Changes
        run: |
          snow sql \
            -D DATABASE=PROD \
            -D SCHEMA=GRID_DATA \
            -f sql/operations/grid/setup/create_tables.sql
```

### 4.3 Environment-Specific Variables

**Pattern:**
```bash
# Development
snow sql -D DATABASE=DEV -D SCHEMA=GRID -f template.sql

# Test
snow sql -D DATABASE=TEST -D SCHEMA=GRID -f template.sql

# Production
snow sql -D DATABASE=PROD -D SCHEMA=GRID -f template.sql
```

**Store in CI/CD secrets:**
- `SNOWFLAKE_ACCOUNT_DEV`
- `SNOWFLAKE_ACCOUNT_TEST`
- `SNOWFLAKE_ACCOUNT_PROD`

## 5. Production SQL File Headers

### 5.1 Template Header Format

**Required Sections:**
```sql
-- ============================================================================
-- Filename: <filename>.sql
-- Description: <What this template does>
--
-- Parameters:
--   PARAM1 - Description and example
--   PARAM2 - Description and example
--
-- Usage:
--   snow sql -D PARAM1=value -D PARAM2=value -f <filename>.sql
--
-- Example:
--   snow sql -D DATABASE=PROD -D SCHEMA=GRID -f <filename>.sql
--
-- Dependencies: <What must exist before running>
-- Returns: <What gets created or modified>
-- Idempotency: <Explain why safe to rerun>
-- ============================================================================
```

### 5.2 Header Example

```sql
-- ============================================================================
-- Filename: merge_scada_data.sql
-- Description: Upsert SCADA sensor data from stage (production-safe)
--
-- Parameters:
--   DATABASE - Database name (e.g., UTILITY_DEMO_V2)
--   SCHEMA   - Schema name (e.g., GRID_DATA)
--   STAGE    - Stage name (e.g., @UTILITY_DEMO_V2.GRID_DATA.FILES)
--
-- Usage:
--   snow sql -D DATABASE=DB -D SCHEMA=SCH -D STAGE=STG -f merge_scada_data.sql
--
-- Example:
--   snow sql -D DATABASE=PROD -D SCHEMA=GRID_DATA -D STAGE=@PROD.GRID_DATA.FILES -f merge_scada_data.sql
--
-- Dependencies:
--   - SCADA_DATA table must exist
--   - Stage must contain scada_*.csv files
--   - Warehouse must be active
--
-- Returns: Row count of merged records
-- Idempotency: MERGE ensures safe reruns (updates existing, inserts new)
-- ============================================================================
```

## 6. Validation and Testing

### 6.1 Pre-Deployment Validation

**Create validation template:**
```sql
-- ============================================================================
-- Filename: validate_schema.sql
-- Description: Validate schema exists and has required objects
-- ============================================================================

-- Check schema exists
SELECT
    'Schema exists' AS check_name,
    CASE
        WHEN COUNT(*) > 0 THEN '✓ PASS'
        ELSE '✗ FAIL'
    END AS status
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE CATALOG_NAME = '<%DATABASE%>'
  AND SCHEMA_NAME = '<%SCHEMA%>';

-- Check required tables exist
SELECT
    'Required tables exist' AS check_name,
    CASE
        WHEN COUNT(*) = 5 THEN '✓ PASS'
        ELSE '✗ FAIL - Found ' || COUNT(*) || ' of 5 tables'
    END AS status
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = '<%DATABASE%>'
  AND TABLE_SCHEMA = '<%SCHEMA%>'
  AND TABLE_NAME IN ('GRID_ASSETS', 'SCADA_DATA', 'FAILURE_EVENTS',
                     'AMI_DATA', 'TRANSFORMER_DATA');
```

### 6.2 Post-Deployment Verification

**Pattern:**
```sql
-- Row count verification
SELECT
    'GRID_ASSETS' AS table_name,
    COUNT(*) AS row_count,
    MAX(METADATA$ROW_ID) AS max_row_id
FROM <%DATABASE%>.<%SCHEMA%>.GRID_ASSETS

UNION ALL

SELECT
    'SCADA_DATA' AS table_name,
    COUNT(*) AS row_count,
    MAX(METADATA$ROW_ID) AS max_row_id
FROM <%DATABASE%>.<%SCHEMA%>.SCADA_DATA;
```
