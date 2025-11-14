**Keywords:** Semantic views, CREATE SEMANTIC VIEW, Cortex Analyst, FACTS, DIMENSIONS, METRICS, data modeling, Generator workflow, iterative development, TPC-DS, natural language query, business logic layer
**TokenBudget:** ~8100
**ContextTier:** High
**Depends:** 100-snowflake-core

# Snowflake Native Semantic Views (Cortex Analyst)

## Purpose
Provide authoritative guidance for creating and managing native Snowflake Semantic Views using the `CREATE SEMANTIC VIEW` DDL syntax. These database-native objects enable Cortex Analyst and Cortex Agent to perform natural language querying directly against the database without external YAML files. This rule emphasizes the modern native approach over legacy YAML semantic models.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake native semantic view creation, governance, and integration with Cortex Analyst/Agent

## Contract
- **Inputs/Prereqs:**
  - Target DATABASE.SCHEMA with appropriate privileges
  - Warehouse context with `CREATE SEMANTIC VIEW` privilege
  - Physical base tables/views with defined structure
  - Business glossary for naming dimensions, facts, and metrics
- **Allowed Tools:**
  - `CREATE SEMANTIC VIEW` DDL syntax
  - `SHOW SEMANTIC VIEWS`, `SHOW SEMANTIC DIMENSIONS`, `SHOW SEMANTIC METRICS`
  - Cortex Analyst REST API with `semantic_view` parameter
  - Snowflake CLI for validation
- **Forbidden Tools:**
  - YAML semantic model uploads (legacy approach - use native views instead)
  - Regular `CREATE VIEW` when semantic view is appropriate
  - Ambiguous `SELECT *` references in dimensional projections
- **Required Steps:**
  1. Define TABLES block with physical base table references and PRIMARY KEY
  2. Declare FACTS (numeric measures at row level)
  3. Declare DIMENSIONS (categorical and temporal attributes)
  4. Define METRICS (aggregations over facts/dimensions)
  5. Add WITH SYNONYMS for improved NLQ accuracy
  6. Add COMMENT clauses for documentation (use `=` syntax)
  7. Validate using `SHOW SEMANTIC VIEWS` and test with Cortex Analyst
  8. Apply security policies (masking, row access) on base tables
- **Output Format:**
  - Minimal, runnable `CREATE SEMANTIC VIEW` DDL statements
  - Clear separation of TABLES, FACTS, DIMENSIONS, METRICS blocks
- **Validation Steps:**
  - DDL compiles without syntax errors
  - `SHOW SEMANTIC VIEWS` confirms object creation
  - `SHOW SEMANTIC DIMENSIONS/METRICS` validates structure
  - Cortex Analyst REST API accepts `semantic_view` parameter
  - Query performance validated on base tables (semantic views are metadata only)

## Key Principles
- **Native database objects**: Semantic views are schema-level objects stored in Snowflake's metadata, not external files
- **No YAML required**: Unlike legacy semantic models, native semantic views don't require YAML file uploads
- **Metadata only**: Semantic views store logical structure, not data - performance depends on base tables
- **Cortex Analyst ready**: Use `semantic_view` parameter in REST API instead of `semantic_model`
- **Explicit syntax**: Column mappings use `logical_name AS physical_expression` format
- **Clause ordering**: Must follow TABLES → FACTS → DIMENSIONS → METRICS sequence
- **Simple expressions**: DIMENSIONS and FACTS support simple columns, limited functions like DATEDIFF
- **Comment syntax**: Use `COMMENT = 'text'` (with equals sign)
- **Governance via RBAC**: Standard Snowflake privileges apply (no special semantic model permissions)

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Use `CREATE SEMANTIC VIEW` DDL** - Native database objects, not YAML files
- **Correct mapping syntax** - `logical_name AS physical_column` (NOT reversed)
- **Clause order matters** - TABLES → FACTS → DIMENSIONS → METRICS (strict sequence)
- **Simple expressions in DIMENSIONS** - No CAST, DATE_TRUNC, or complex functions
- **COMMENT uses equals sign** - `COMMENT = 'text'` (NOT `COMMENT 'text'`)
- **Add WITH SYNONYMS** - Improves natural language query matching
- **Never reverse mappings** - `physical AS logical` causes "invalid identifier" errors

**Quick Checklist:**
- [ ] Clause order: TABLES → FACTS → DIMENSIONS → METRICS
- [ ] PRIMARY KEY defined in TABLES block
- [ ] Mappings use correct syntax: `logical_name AS physical_column`
- [ ] All COMMENT clauses have equals sign
- [ ] DIMENSIONS use simple columns only (no functions)
- [ ] WITH SYNONYMS added for key business terms
- [ ] Validated with `SHOW SEMANTIC VIEWS`

## 1) Native Semantic View Syntax

### Complete DDL Structure

```sql
CREATE [OR REPLACE] SEMANTIC VIEW <database>.<schema>.<view_name>
  TABLES (
    <table_alias> AS <database>.<schema>.<physical_table>
      PRIMARY KEY (<column1>[, <column2>, ...])
      [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
      [COMMENT = '<table_description>']
  )
  FACTS (
    <table_alias>.<logical_name> AS <physical_column_or_expression>
      [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
      [COMMENT = '<fact_description>'],
    ...
  )
  DIMENSIONS (
    <table_alias>.<logical_name> AS <physical_column>
      [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
      [COMMENT = '<dimension_description>'],
    ...
  )
  METRICS (
    <table_alias>.<metric_name> AS <aggregate_function>(<expression>)
      [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
      [COMMENT = '<metric_description>'],
    ...
  )
  [COMMENT = '<overall_view_description>'];
```

### Minimal Working Example

```sql
-- Filename: create_semantic_view_minimal.sql
-- Description: Minimal semantic view for asset inventory

CREATE OR REPLACE SEMANTIC VIEW PROD.GRID_DATA.SEM_ASSET_INVENTORY
  TABLES (
    asset AS PROD.GRID_DATA.GRID_ASSETS
      PRIMARY KEY (asset_id)
  )
  FACTS (
    asset.rated_capacity AS rated_capacity
  )
  DIMENSIONS (
    asset.asset_id AS asset_id,
    asset.asset_type AS asset_type,
    asset.asset_name AS asset_name
  )
  METRICS (
    asset.asset_count AS COUNT(DISTINCT asset_id)
  );
```

### Production Example with Synonyms and Comments

```sql
-- Filename: create_semantic_view_transformer_health.sql
-- Description: Semantic view for transformer health monitoring with NLQ synonyms

CREATE OR REPLACE SEMANTIC VIEW PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH
  TABLES (
    tfm AS PROD.GRID_DATA.TRANSFORMER_DATA
      PRIMARY KEY (equipment_id, timestamp)
      WITH SYNONYMS ('transformers', 'equipment')
      COMMENT = 'Transformer telemetry and health metrics'
  )
  FACTS (
    tfm.load_kw AS load_kw
      WITH SYNONYMS ('power draw', 'load'),
    tfm.ambient_temp_c AS ambient_temp_c
      WITH SYNONYMS ('temperature', 'temp'),
    tfm.failure_imminent AS failure_imminent
      WITH SYNONYMS ('at risk', 'failing')
  )
  DIMENSIONS (
    tfm.transformer_id AS equipment_id
      WITH SYNONYMS ('equipment ID', 'transformer ID')
      COMMENT = 'Unique transformer identifier',
    tfm.substation AS substation_id
      WITH SYNONYMS ('substation', 'location'),
    tfm.event_timestamp AS timestamp
      WITH SYNONYMS ('time', 'date', 'reading time')
      COMMENT = 'Telemetry reading timestamp'
  )
  METRICS (
    tfm.avg_load AS AVG(load_kw)
      WITH SYNONYMS ('average load', 'mean power'),
    tfm.max_load AS MAX(load_kw)
      WITH SYNONYMS ('peak load', 'maximum power'),
    tfm.reading_count AS COUNT(*)
      WITH SYNONYMS ('total readings', 'observation count')
  )
  COMMENT = 'Transformer health and performance metrics for Cortex Analyst NLQ';
```

## 2) Semantic View Components

### TABLES Block

**Purpose:** Defines the physical base tables and their aliases for the semantic view.

**Syntax:**
```sql
TABLES (
  <alias> AS <database>.<schema>.<table>
    PRIMARY KEY (<column>[, <column>, ...])  -- Required for relationships
    [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
    [COMMENT = '<description>']
)
```

**Rules:**
- Each semantic view has exactly ONE TABLES block (no joins - relationships are defined separately)
- `PRIMARY KEY` is required if this semantic view will be used in relationships with other semantic views
- Composite primary keys are supported: `PRIMARY KEY (col1, col2, col3)`
- Synonyms improve NLQ matching (e.g., "equipment" for "transformer", "units" for "assets")
- Only one base table per semantic view - use relationships to connect multiple semantic views

**Multi-Table Semantic Views:**

When creating semantic views that reference multiple tables, define relationships between them:

```sql
-- Example: Multi-table semantic view with relationships
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  TABLES (
    CUSTOMER PRIMARY KEY (C_CUSTOMER_SK),
    DATE AS DATE_DIM PRIMARY KEY (D_DATE_SK),
    DEMO AS CUSTOMER_DEMOGRAPHICS PRIMARY KEY (CD_DEMO_SK),
    ITEM PRIMARY KEY (I_ITEM_SK),
    STORE PRIMARY KEY (S_STORE_SK),
    STORESALES AS STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_CDEMO_SK, SS_ITEM_SK, SS_STORE_SK, SS_CUSTOMER_SK)
  )
  RELATIONSHIPS (
    SALESTOCUSTOMER AS STORESALES(SS_CUSTOMER_SK) REFERENCES CUSTOMER(C_CUSTOMER_SK),
    SALESTODATE AS STORESALES(SS_SOLD_DATE_SK) REFERENCES DATE(D_DATE_SK),
    SALESTODEMO AS STORESALES(SS_CDEMO_SK) REFERENCES DEMO(CD_DEMO_SK),
    SALESTOITEM AS STORESALES(SS_ITEM_SK) REFERENCES ITEM(I_ITEM_SK),
    SALETOSTORE AS STORESALES(SS_STORE_SK) REFERENCES STORE(S_STORE_SK)
  )
  FACTS (
    ITEM.COST AS i_wholesale_cost,
    ITEM.PRICE AS i_current_price,
    STORE.TAX_RATE AS S_TAX_PRECENTAGE
  )
  DIMENSIONS (
    CUSTOMER.BIRTHYEAR AS C_BIRTH_YEAR,
    CUSTOMER.COUNTRY AS C_BIRTH_COUNTRY,
    DATE.DATE AS D_DATE,
    DATE.MONTH AS D_MOY,
    DATE.YEAR AS D_YEAR,
    ITEM.BRAND AS I_BRAND_NAME,
    ITEM.CATEGORY AS I_CATEGORY,
    STORE.STATE AS S_STATE
  )
  METRICS (
    STORESALES.TotalSalesQuantity AS SUM(SS_QUANTITY)
  );
```

**RELATIONSHIPS Block:**

**Purpose:** Define foreign key relationships between tables in multi-table semantic views.

**Syntax:**
```sql
RELATIONSHIPS (
  <relationship_name> AS <child_table>(<fk_column>) REFERENCES <parent_table>(<pk_column>),
  ...
)
```

**Rules:**
- Relationship names must be unique within the semantic view
- Foreign key column must exist in child table
- Referenced primary key must match PRIMARY KEY definition in TABLES block
- Enables Cortex Analyst to perform automatic joins across tables
- Required for multi-table semantic views to function correctly

**Time-Based Filtering Pattern:**

For semantic views with temporal dimensions, optimize for time-range queries:

```sql
-- Example: Semantic view optimized for time-range filtering
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.SALES_BY_TIME
  TABLES (
    sales AS ANALYTICS.CORE.SALES_FACT
      PRIMARY KEY (sale_id)
      WITH SYNONYMS ('sales transactions', 'orders')
  )
  FACTS (
    sales.amount AS amount,
    sales.quantity AS quantity
  )
  DIMENSIONS (
    sales.sale_date AS sale_date
      WITH SYNONYMS ('date', 'transaction date', 'order date')
      COMMENT = 'Date of sale - use for time-range filtering',
    sales.sale_year AS YEAR(sale_date)
      WITH SYNONYMS ('year', 'fiscal year')
      COMMENT = 'Extracted year for annual analysis',
    sales.sale_month AS MONTH(sale_date)
      WITH SYNONYMS ('month', 'month number')
      COMMENT = 'Extracted month (1-12)',
    sales.product_id AS product_id,
    sales.region AS region
  )
  METRICS (
    sales.total_revenue AS SUM(amount),
    sales.daily_avg_revenue AS AVG(amount)
      WITH SYNONYMS ('average daily sales', 'mean revenue per day')
  )
  COMMENT = 'Sales semantic view with temporal dimensions for time-series analysis';
```

**Best Practices for Time Dimensions:**
- Include raw timestamp/date column as primary temporal dimension
- Add extracted time parts (year, month, quarter) as separate dimensions for easier filtering
- Use synonyms like "last year", "this month", "recent" to improve NLQ matching
- Ensure base table has clustering or partitioning on date column for performance

### FACTS Block

**Purpose:** Numeric measures at row level (not aggregated).

**Syntax:**
```sql
FACTS (
  <alias>.<logical_name> AS <physical_column_or_expression>
    [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
    [COMMENT = '<description>'],
  ...
)
```

**Rules:**
- Facts are typically numeric: `INTEGER`, `NUMBER`, `FLOAT`, `DECIMAL`
- Simple expressions allowed: `physical_column`, `col1 * col2`, `DATEDIFF('day', col1, col2)`
- Complex functions (CAST, DATE_TRUNC, CASE) may not be supported - test carefully
- Facts are additive by nature - document non-additive facts clearly
- **Mapping format:** `logical_name AS physical_expression` (NOT reversed)

**Examples:**
```sql
FACTS (
  asset.rated_capacity AS rated_capacity,
  tfm.load_kw AS load_kw,
  tfm.days_since_maint AS DATEDIFF('day', last_maint_date, CURRENT_DATE())
)
```

### DIMENSIONS Block

**Purpose:** Categorical and temporal attributes for grouping and filtering.

**Syntax:**
```sql
DIMENSIONS (
  <alias>.<logical_name> AS <physical_column>
    [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
    [COMMENT = '<description>'],
  ...
)
```

**Rules:**
- Dimensions are typically categorical: `VARCHAR`, `STRING`, `DATE`, `TIMESTAMP`
- **Simple columns only** - no CAST, DATE_TRUNC, or complex expressions
- Temporal dimensions: Use raw timestamp/date columns, not derived date parts
- **Mapping format:** `logical_name AS physical_column` (NOT reversed)
- Synonyms are critical for NLQ: `WITH SYNONYMS ('equipment ID', 'transformer ID', 'unit ID')`

**Examples:**
```sql
DIMENSIONS (
  asset.asset_id AS asset_id,
  asset.asset_type AS asset_type,
  tfm.event_timestamp AS timestamp,  -- Simple timestamp
  tfm.substation AS substation_id    -- Simple column
  -- tfm.reading_date AS CAST(timestamp AS DATE)  -- CAST not supported
)
```

### METRICS Block

**Purpose:** Aggregations over facts and/or dimensions.

**Syntax:**
```sql
METRICS (
  <alias>.<metric_name> AS <aggregate_function>(<expression>)
    [WITH SYNONYMS ('<syn1>', '<syn2>', ...)]
    [COMMENT = '<description>'],
  ...
)
```

**Rules:**
- Aggregates: `COUNT(*)`, `COUNT(DISTINCT col)`, `SUM(col)`, `AVG(col)`, `MIN(col)`, `MAX(col)`
- Simple expressions supported: `SUM(col1 * col2)`, `AVG(CASE WHEN ... THEN 1 ELSE 0 END)` (test carefully)
- Complex CASE expressions may fail - use simple metrics first
- Metrics are automatically computed by Cortex Analyst when user asks questions
- **Mapping format:** `metric_name AS aggregate_expression`

**Examples:**
```sql
METRICS (
  asset.asset_count AS COUNT(DISTINCT asset_id),
  tfm.avg_load AS AVG(load_kw),
  tfm.max_load AS MAX(load_kw),
  tfm.total_readings AS COUNT(*),
  ami.total_outages AS SUM(outage_flag)  -- Simple SUM on flag
  -- ami.customers_impacted AS SUM(CASE WHEN outage_flag = 1 THEN 1 ELSE 0 END)  -- May fail
)
```

## 3) Anti-Patterns and Common Mistakes


**Anti-Pattern 1: Reversed Mapping Syntax**
```sql
-- INCORRECT - Backwards mapping (will cause syntax error)
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS total_amount  -- Reversed!
  )
  DIMENSIONS (
    orders.order_id AS order_number      -- Reversed!
  );
```
**Problem:** Syntax error: "invalid identifier 'ORDER_AMOUNT'" - the mapping is backwards.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.total_amount AS order_amount  -- logical_name AS physical_column
  )
  DIMENSIONS (
    orders.order_number AS order_id      -- logical_name AS physical_column
  );
```
**Benefits:** Correct syntax compiles successfully.

---

**Anti-Pattern 2: Complex Expressions in DIMENSIONS**
```sql
-- INCORRECT - Complex functions in DIMENSIONS
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS order_amount
  )
  DIMENSIONS (
    orders.order_id AS order_id,
    orders.reading_date AS CAST(order_timestamp AS DATE),  -- CAST not allowed
    orders.order_hour AS DATE_TRUNC('hour', order_timestamp) -- DATE_TRUNC not allowed
  );
```
**Problem:** Syntax error: "unexpected 'CAST'" or "invalid expression" - dimensions must be simple columns.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS order_amount
  )
  DIMENSIONS (
    orders.order_id AS order_id,
    orders.order_timestamp AS order_timestamp  -- Use raw timestamp
    -- Add derived columns (date parts) to base table/view if needed
  );
```
**Benefits:** Clean dimensions that work with Cortex Analyst's temporal intelligence.

---

**Anti-Pattern 3: Missing Equals Sign in COMMENT**
```sql
-- INCORRECT - COMMENT without equals sign
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT 'Sales orders table'  -- Missing equals sign
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT 'Total order value'   -- Missing equals sign
  );
```
**Problem:** Syntax error: "unexpected 'Sales'" - COMMENT requires equals sign.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT = 'Sales orders table'  -- Equals sign required
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT = 'Total order value'   -- Equals sign required
  );
```
**Benefits:** Proper comment syntax compiles successfully.

---

**Anti-Pattern 4: Wrong Clause Order**
```sql
-- INCORRECT - Wrong clause ordering
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  DIMENSIONS (                        -- DIMENSIONS before FACTS
    orders.order_id AS order_id
  )
  FACTS (                             -- FACTS after DIMENSIONS
    orders.order_amount AS order_amount
  );
```
**Problem:** Syntax error or unexpected behavior - clause order matters.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (                             -- FACTS first
    orders.order_amount AS order_amount
  )
  DIMENSIONS (                        -- DIMENSIONS after FACTS
    orders.order_id AS order_id
  )
  METRICS (                           -- METRICS last
    orders.order_count AS COUNT(*)
  );
```
**Benefits:** Correct clause order: TABLES → FACTS → DIMENSIONS → METRICS.


## 4) Cortex Analyst Integration

### REST API Usage (Native Semantic Views)

```python
import requests
import json

# Cortex Analyst with NATIVE semantic view (no YAML needed)
url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"

headers = {
    "Authorization": f"Bearer {snowflake_token}",
    "Content-Type": "application/json"
}

payload = {
    "semantic_view": "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",  # Native semantic view
    "messages": [
        {
            "role": "user",
            "content": "Which transformers have the highest average load this month?"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result["message"]["content"])  # Natural language response
```

**Key Differences from YAML Approach:**
- **Native views:** Use `"semantic_view": "DB.SCHEMA.VIEW_NAME"`
- **Legacy YAML:** Used `"semantic_model": "@stage/model.yaml"`
- **No staging:** No need to upload files to internal stages
- **Version control:** DDL changes tracked via SQL migrations

### Cortex Agent Integration

```python
from snowflake.core import Root
from snowflake.core.cortex import Agent

# Initialize Snowflake connection
root = Root(session)

# Create agent grounded on native semantic views
agent = root.databases["PROD"].schemas["GRID_DATA"].cortex_agents.create(
    Agent(
        name="grid_ops_assistant",
        grounding_sources=[
            "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",
            "PROD.GRID_DATA.SEM_ASSET_INVENTORY",
            "PROD.GRID_DATA.SEM_CUSTOMER_OUTAGE_IMPACT"
        ],
        instructions="You are a grid operations expert. Answer questions about transformer health, asset inventory, and customer impact.",
        model="mistral-large2"
    )
)

# Query the agent
response = agent.invoke("Show me transformers at risk of failure")
print(response["content"])
```

## 5) Governance and Security

### Access Control

**Semantic views inherit RBAC from base tables:**
```sql
-- Grant SELECT on base table (semantic view inherits)
GRANT SELECT ON TABLE PROD.GRID_DATA.GRID_ASSETS TO ROLE BI_ANALYST;

-- Grant USAGE on semantic view schema
GRANT USAGE ON SCHEMA PROD.GRID_DATA TO ROLE BI_ANALYST;

-- No special semantic view privilege needed - standard Snowflake RBAC
```

### Data Masking

**Apply masking to base tables (semantic views reflect masked data):**
```sql
-- Create masking policy
CREATE OR REPLACE MASKING POLICY PROD.GOVERNANCE.MASK_PII AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
    ELSE '***MASKED***'
  END;

-- Apply to base table (semantic view automatically uses masked data)
ALTER TABLE PROD.CUSTOMER_DATA.CUSTOMERS
  MODIFY COLUMN customer_email SET MASKING POLICY PROD.GOVERNANCE.MASK_PII;
```

### Row Access Policies

**Apply row-level security to base tables:**
```sql
CREATE OR REPLACE ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION AS (region STRING) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'ADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'ANALYST_WEST' AND region = 'WEST' THEN TRUE
    ELSE FALSE
  END;

ALTER TABLE PROD.GRID_DATA.GRID_ASSETS
  ADD ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION ON (region);
```

## 6) Validation and Testing

### 6.1 Verification Commands

```sql
-- List all semantic views in schema
SHOW SEMANTIC VIEWS IN SCHEMA PROD.GRID_DATA;

-- Show dimensions for a semantic view
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH;

-- Show metrics for a semantic view
SHOW SEMANTIC METRICS IN SEMANTIC VIEW PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH;

-- Show facts for a semantic view
SHOW SEMANTIC FACTS IN SEMANTIC VIEW PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH;

-- Query metadata
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.SEMANTIC_VIEWS
WHERE semantic_view_name = 'SEM_TRANSFORMER_HEALTH'
  AND semantic_view_schema = 'GRID_DATA';
```

### 6.2 Semantic View Generator Validation

**Validate Generator Output Before Execution:**

```sql
-- Step 1: Use Generator to create DDL (via Snowsight UI or API)
-- Generator produces CREATE SEMANTIC VIEW statement

-- Step 2: Review generated DDL for quality
-- Check these elements BEFORE executing:

-- Checklist for Generated DDL:
-- [ ] PRIMARY KEY matches actual table primary key or business grain
-- [ ] FACTS contain only numeric columns (INTEGER, NUMBER, FLOAT, DECIMAL)
-- [ ] DIMENSIONS contain categorical/temporal columns (VARCHAR, DATE, TIMESTAMP)
-- [ ] METRICS use appropriate aggregation functions (SUM, AVG, COUNT, MIN, MAX)
-- [ ] Table references are fully qualified (DATABASE.SCHEMA.TABLE)
-- [ ] No ambiguous column names in multi-table views

-- Step 3: Execute with verification
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  TABLES (
    customer AS SAMPLE_DATA.TPCDS_SF10TCL.CUSTOMER
      PRIMARY KEY (C_CUSTOMER_SK)
  )
  FACTS (
    customer.C_BIRTH_YEAR AS c_birth_year  -- VALIDATE: Should this be DIMENSION?
  )
  DIMENSIONS (
    customer.C_CUSTOMER_SK AS c_customer_sk,
    customer.C_CUSTOMER_ID AS c_customer_id,
    customer.C_BIRTH_COUNTRY AS c_birth_country
  )
  METRICS (
    customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
  );

-- Step 4: Verify creation
SHOW SEMANTIC VIEWS LIKE 'SEM_CUSTOMER' IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;

-- Step 5: Test structure
DESCRIBE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER;

-- Step 6: Validate with test query
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  METRICS customer_count
  DIMENSIONS c_birth_country
) LIMIT 10;
```

**Common Generator Issues and Corrections:**

```sql
-- ISSUE 1: Year classified as FACT instead of DIMENSION
-- Generated (incorrect):
FACTS (
  customer.C_BIRTH_YEAR AS c_birth_year  -- Year should be DIMENSION
)

-- Corrected:
DIMENSIONS (
  customer.C_BIRTH_YEAR AS c_birth_year  -- Temporal dimension for filtering
    WITH SYNONYMS ('birth year', 'year of birth')
)

-- ISSUE 2: Missing synonyms for natural language queries
-- Generated (incomplete):
DIMENSIONS (
  customer.C_BIRTH_COUNTRY AS c_birth_country
)

-- Corrected:
DIMENSIONS (
  customer.C_BIRTH_COUNTRY AS c_birth_country
    WITH SYNONYMS ('country', 'birth country', 'nationality', 'nation')
    COMMENT = 'Country where customer was born'
)

-- ISSUE 3: Missing business-relevant metrics
-- Generated (minimal):
METRICS (
  customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
)

-- Enhanced:
METRICS (
  customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
    WITH SYNONYMS ('total customers', 'number of customers', 'customer count'),
  customer.unique_countries AS COUNT(DISTINCT C_BIRTH_COUNTRY)
    WITH SYNONYMS ('countries represented', 'country count'),
  customer.avg_birth_year AS AVG(C_BIRTH_YEAR)
    WITH SYNONYMS ('average birth year', 'mean age indicator')
)
```

### 6.3 TPC-DS Test Examples

**Complete TPC-DS Semantic View Test Suite:**

```sql
-- Test 1: Basic structure validation
SHOW SEMANTIC VIEWS IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;

-- Expected: List of semantic views including TPCDS_SEMANTIC_VIEW_SM

-- Test 2: Multi-table relationship validation
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM;

-- Expected: Dimensions from CUSTOMER, DATE, ITEM, STORE tables

-- Test 3: Simple aggregation query
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  METRICS StoreSales.TotalSalesQuantity
  DIMENSIONS Item.Category
)
ORDER BY TotalSalesQuantity DESC
LIMIT 10;

-- Expected: Top 10 categories by sales quantity

-- Test 4: Multi-dimensional analysis
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS 
    Item.Brand,
    Item.Category,
    Store.State
  METRICS 
    StoreSales.TotalSalesQuantity
)
WHERE Category = 'Electronics'
  AND State IN ('CA', 'TX', 'NY')
ORDER BY TotalSalesQuantity DESC
LIMIT 20;

-- Expected: Top 20 electronic brands by state (CA, TX, NY)

-- Test 5: Temporal filtering with relationships
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS 
    Date.Year,
    Date.Month,
    Item.Brand
  METRICS 
    StoreSales.TotalSalesQuantity
)
WHERE Year = '2002'
  AND Month BETWEEN '10' AND '12'  -- Q4 2002
ORDER BY TotalSalesQuantity DESC
LIMIT 15;

-- Expected: Top 15 brands in Q4 2002 by sales quantity

-- Test 6: Cross-dimensional analysis (customer + product + time)
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS 
    Customer.C_BIRTH_COUNTRY,
    Item.Category,
    Date.Year
  METRICS 
    StoreSales.TotalSalesQuantity
)
WHERE Year = '2002'
  AND C_BIRTH_COUNTRY IN ('UNITED STATES', 'CANADA', 'MEXICO')
ORDER BY TotalSalesQuantity DESC
LIMIT 25;

-- Expected: Sales by country, category, and year (North America only)

-- Test 7: Performance validation with Query Profile
-- Run this query and check Query Profile for:
-- - Partition pruning on date columns
-- - Join elimination if dimensions not used
-- - Efficient aggregation patterns

SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS 
    Date.Year,
    Date.Month,
    Store.State
  METRICS 
    StoreSales.TotalSalesQuantity
)
WHERE Year = '2002'
  AND Month = '12'
  AND State = 'TX'
ORDER BY TotalSalesQuantity DESC;

-- Review Query Profile:
-- [ ] Date filters pushed down to STORE_SALES table
-- [ ] Partition pruning applied (check "Partitions scanned")
-- [ ] No unnecessary table scans
-- [ ] Join order optimized by Snowflake optimizer
```

**Accuracy Validation Pattern:**

```sql
-- Validate semantic view metrics match direct table queries

-- Semantic view query
WITH semantic_result AS (
  SELECT 
    SUM(TotalSalesQuantity) AS semantic_total
  FROM SEMANTIC_VIEW (
    SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
    METRICS StoreSales.TotalSalesQuantity
  )
  WHERE Date.Year = '2002'
),
-- Direct table query
direct_result AS (
  SELECT 
    SUM(SS_QUANTITY) AS direct_total
  FROM SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES s
  JOIN SAMPLE_DATA.TPCDS_SF10TCL.DATE_DIM d ON s.SS_SOLD_DATE_SK = d.D_DATE_SK
  WHERE d.D_YEAR = 2002
)
SELECT 
  s.semantic_total,
  d.direct_total,
  s.semantic_total - d.direct_total AS difference,
  CASE 
    WHEN s.semantic_total = d.direct_total THEN 'PASS'
    ELSE 'FAIL'
  END AS validation_status
FROM semantic_result s, direct_result d;

-- Expected: difference = 0, validation_status = 'PASS'
```

### 6.4 Testing with Cortex Analyst

**SnowCLI Testing:**

```bash
# Test NLQ query via SnowCLI
snow cortex analyst query \
  --semantic-view "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH" \
  --question "What is the average load for transformers in the last 24 hours?"

# Test with TPC-DS semantic view
snow cortex analyst query \
  --semantic-view "SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM" \
  --question "What are the top 5 selling brands in Texas during December 2002?"

# Test synonym effectiveness
snow cortex analyst query \
  --semantic-view "SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM" \
  --question "Show me revenue by product category for last year"
```

**Python REST API Testing:**

```python
import requests
import json

def test_semantic_view_nlq(account, token, semantic_view, test_queries):
    """Test semantic view with multiple natural language queries"""
    
    url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = []
    for query in test_queries:
        payload = {
            "semantic_view": semantic_view,
            "messages": [{"role": "user", "content": query}]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        result = {
            "query": query,
            "status": response.status_code,
            "response": response.json() if response.ok else response.text
        }
        results.append(result)
        
        print(f"Query: {query}")
        print(f"Status: {result['status']}")
        print(f"Response: {json.dumps(result['response'], indent=2)}\n")
    
    return results

# TPC-DS test queries
tpcds_queries = [
    "What are the top 10 selling brands?",
    "Show me sales by state for books in December 2002",
    "Which product categories have the highest revenue?",
    "Compare sales in California vs Texas",
    "What is the average quantity sold per transaction?"
]

results = test_semantic_view_nlq(
    account="your_account",
    token="your_token",
    semantic_view="SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM",
    test_queries=tpcds_queries
)
```

### 6.5 Performance Validation

**Check Base Table Optimization:**

```sql
-- Semantic views are metadata only - performance depends on base tables

-- Step 1: Verify clustering on base table
SHOW CLUSTERING KEYS IN TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- Step 2: Check table statistics
SELECT 
  TABLE_NAME,
  ROW_COUNT,
  BYTES,
  CLUSTERING_KEY
FROM SAMPLE_DATA.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'TPCDS_SF10TCL'
  AND TABLE_NAME = 'STORE_SALES';

-- Step 3: Test query with Query Profile analysis
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  METRICS StoreSales.TotalSalesQuantity
  DIMENSIONS Date.Year, Date.Month
)
WHERE Year = '2002' AND Month = '12';

-- Step 4: Review Query Profile for:
-- [ ] Partitions scanned vs total partitions
-- [ ] Bytes scanned vs bytes spilled
-- [ ] Join order and elimination
-- [ ] Aggregation pushdown
-- [ ] Filter pushdown to base tables

-- Step 5: If performance issues, optimize base table
-- (Semantic view optimization happens via base table tuning)
ALTER TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES 
  CLUSTER BY (SS_SOLD_DATE_SK);
```

## 7) Migration from YAML Semantic Models

### Legacy Approach (YAML + Stage Upload)
```yaml
# config/semantic_model_grid.yaml
tables:
  - name: transformer_health
    base_table:
      database: PROD
      schema: GRID_DATA
      table: TRANSFORMER_DATA
    dimensions:
      - name: equipment_id
        expr: equipment_id
    facts:
      - name: load_kw
        expr: load_kw
    metrics:
      - name: avg_load
        expr: AVG(load_kw)
```

**Upload script:**
```sql
PUT file://config/semantic_model_grid.yaml @PROD.GRID_DATA.SEMANTIC_MODEL_STAGE;
```

### Modern Approach (Native Semantic View)
```sql
CREATE OR REPLACE SEMANTIC VIEW PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH
  TABLES (
    tfm AS PROD.GRID_DATA.TRANSFORMER_DATA
      PRIMARY KEY (equipment_id, timestamp)
  )
  FACTS (
    tfm.load_kw AS load_kw
  )
  DIMENSIONS (
    tfm.equipment_id AS equipment_id
  )
  METRICS (
    tfm.avg_load AS AVG(load_kw)
  );
```

**Benefits:**
- No YAML files to maintain
- No stage uploads required
- Standard SQL version control
- Integrated with database governance
- Simpler deployment pipeline

## 8) Development Best Practices

### 8.1 Semantic View Generator Tool

**Purpose:** Automate initial semantic view creation from existing tables to accelerate development.

**When to Use:**
- Starting new semantic view from scratch
- Exploring unfamiliar database schemas
- Creating baseline views for iterative refinement
- Rapid prototyping for Cortex Analyst testing

**Generator Workflow:**

```sql
-- Step 1: Verify Generator availability (requires ACCOUNTADMIN or appropriate role)
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Step 2: Use Generator to create semantic view from base table
-- The Generator analyzes table structure and suggests semantic view DDL
-- (Generator UI available in Snowsight or via API)

-- Step 3: Review generated DDL before execution
-- Generator produces CREATE SEMANTIC VIEW statement with:
-- - Inferred PRIMARY KEY from table constraints
-- - Numeric columns as FACTS
-- - String/date columns as DIMENSIONS
-- - Common aggregations as METRICS

-- Step 4: Execute generated DDL
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  TABLES (
    customer AS SAMPLE_DATA.TPCDS_SF10TCL.CUSTOMER
      PRIMARY KEY (C_CUSTOMER_SK)
  )
  FACTS (
    customer.C_BIRTH_YEAR AS c_birth_year
  )
  DIMENSIONS (
    customer.C_CUSTOMER_SK AS c_customer_sk,
    customer.C_CUSTOMER_ID AS c_customer_id,
    customer.C_FIRST_NAME AS c_first_name,
    customer.C_LAST_NAME AS c_last_name,
    customer.C_BIRTH_COUNTRY AS c_birth_country
  )
  METRICS (
    customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
  );

-- Step 5: Validate creation
SHOW SEMANTIC VIEWS IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;
```

**Generator Limitations:**
- Cannot infer complex business logic (e.g., calculated facts)
- May misclassify columns (review FACTS vs DIMENSIONS)
- Does not add synonyms or comments automatically
- Cannot create relationships between semantic views

**Post-Generation Refinement Checklist:**
- [ ] Verify PRIMARY KEY is correct for business grain
- [ ] Review FACTS classification (should be numeric measures)
- [ ] Review DIMENSIONS classification (should be categorical/temporal)
- [ ] Add WITH SYNONYMS for natural language query matching
- [ ] Add COMMENT clauses for business definitions
- [ ] Test with sample Cortex Analyst queries

### 8.2 Iterative Development Workflow

**MANDATORY:**
**Follow this workflow for production-ready semantic views:**

**Phase 1: Generate and Validate Base Structure**
```sql
-- 1. Read base table structure BEFORE generating
DESCRIBE TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- 2. Generate or write minimal semantic view
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE,
    sales.quantity AS SS_QUANTITY
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK,
    sales.customer_sk AS SS_CUSTOMER_SK,
    sales.sold_date_sk AS SS_SOLD_DATE_SK
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE),
    sales.total_quantity AS SUM(SS_QUANTITY)
  );

-- 3. Verify structure
SHOW SEMANTIC VIEWS LIKE 'SEM_STORE_SALES' IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;

-- 4. Test basic query
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  METRICS total_sales, total_quantity
  DIMENSIONS SS_ITEM_SK
) LIMIT 10;
```

**Phase 2: Add Business Context**
```sql
-- 5. Add synonyms for natural language querying
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
      WITH SYNONYMS ('store sales', 'retail transactions', 'sales data')
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE
      WITH SYNONYMS ('price', 'revenue', 'amount'),
    sales.quantity AS SS_QUANTITY
      WITH SYNONYMS ('qty', 'units sold', 'volume')
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK
      WITH SYNONYMS ('item', 'product', 'SKU'),
    sales.customer_sk AS SS_CUSTOMER_SK
      WITH SYNONYMS ('customer', 'buyer'),
    sales.sold_date_sk AS SS_SOLD_DATE_SK
      WITH SYNONYMS ('date', 'transaction date', 'sale date')
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE)
      WITH SYNONYMS ('total revenue', 'gross sales'),
    sales.total_quantity AS SUM(SS_QUANTITY)
      WITH SYNONYMS ('total units', 'total volume')
  );

-- 6. Add comments for business definitions
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
      WITH SYNONYMS ('store sales', 'retail transactions')
      COMMENT = 'Retail store sales transactions from TPC-DS dataset'
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE
      WITH SYNONYMS ('price', 'revenue', 'amount')
      COMMENT = 'Sales price per item (excludes tax)',
    sales.quantity AS SS_QUANTITY
      WITH SYNONYMS ('qty', 'units sold')
      COMMENT = 'Quantity of items sold'
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK
      WITH SYNONYMS ('item', 'product')
      COMMENT = 'Surrogate key for item dimension',
    sales.customer_sk AS SS_CUSTOMER_SK
      WITH SYNONYMS ('customer', 'buyer')
      COMMENT = 'Surrogate key for customer dimension',
    sales.sold_date_sk AS SS_SOLD_DATE_SK
      WITH SYNONYMS ('date', 'transaction date')
      COMMENT = 'Surrogate key for date dimension'
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE)
      WITH SYNONYMS ('total revenue', 'gross sales')
      COMMENT = 'Sum of all sales prices',
    sales.total_quantity AS SUM(SS_QUANTITY)
      WITH SYNONYMS ('total units')
      COMMENT = 'Sum of quantities sold'
  )
  COMMENT = 'Store sales semantic view for Cortex Analyst natural language queries';
```

**Phase 3: Test with Cortex Analyst**
```python
# 7. Test natural language queries
import requests

url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test queries demonstrating synonyms
test_queries = [
    "What are the top 10 items by revenue?",  # Tests 'revenue' synonym
    "Show me total units sold by customer",    # Tests 'units' synonym
    "Which products have the highest volume?", # Tests 'product' and 'volume' synonyms
]

for query in test_queries:
    payload = {
        "semantic_view": "SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES",
        "messages": [{"role": "user", "content": query}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Query: {query}")
    print(f"Response: {response.json()}\n")
```

**Phase 4: Performance Validation**
```sql
-- 8. Verify base table performance (semantic views are metadata only)
-- Check clustering and partitioning on base table
SHOW CLUSTERING KEYS IN TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- Test query performance with filters
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  METRICS total_sales
  DIMENSIONS SS_SOLD_DATE_SK
)
WHERE SS_SOLD_DATE_SK >= 2451545  -- Date filter for partition pruning
  AND SS_SOLD_DATE_SK <= 2451910
ORDER BY total_sales DESC
LIMIT 100;

-- Review Query Profile for pruning efficiency
-- (Use Snowsight Query History → Query Profile)
```

### 8.3 Testing Methodology

**Component Testing Pattern:**

```sql
-- Test 1: Structure validation
SHOW SEMANTIC VIEWS IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;
SHOW SEMANTIC FACTS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;

-- Test 2: Basic data retrieval
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  METRICS total_sales, total_quantity
  DIMENSIONS SS_ITEM_SK
) LIMIT 5;

-- Expected: 5 rows with aggregated metrics per item

-- Test 3: Metric calculation accuracy
-- Compare semantic view metric with direct table query
WITH semantic_result AS (
  SELECT 
    SUM(total_sales) AS semantic_total
  FROM SEMANTIC_VIEW (
    SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
    METRICS total_sales
  )
),
direct_result AS (
  SELECT 
    SUM(SS_SALES_PRICE) AS direct_total
  FROM SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
)
SELECT 
  s.semantic_total,
  d.direct_total,
  s.semantic_total - d.direct_total AS difference
FROM semantic_result s, direct_result d;

-- Expected: difference = 0 (exact match)

-- Test 4: Synonym effectiveness (via Cortex Analyst)
-- Test that synonyms map correctly to underlying columns
-- (Use Cortex Analyst REST API or Snowsight UI)
```

**Integration Testing with TPC-DS Examples:**

```sql
-- Complete TPC-DS semantic view test
-- Demonstrates multi-table relationships and complex queries

-- Example: Top selling brands by category
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS 
    Item.Brand,
    Item.Category,
    Date.Year,
    Date.Month,
    Store.State
  METRICS 
    StoreSales.TotalSalesQuantity
)
WHERE Year = '2002' 
  AND Month = '12' 
  AND State = 'TX' 
  AND Category = 'Books'
ORDER BY TotalSalesQuantity DESC 
LIMIT 10;

-- Expected: Ranked list of book brands sold in Texas, December 2002
```

### 8.4 Common Development Patterns

**Pattern 1: Time-Based Analysis Views**

```sql
-- Optimized for temporal queries with date dimension
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.SALES_TEMPORAL
  TABLES (
    sales AS ANALYTICS.CORE.DAILY_SALES
      PRIMARY KEY (sale_date, product_id)
      WITH SYNONYMS ('sales', 'transactions')
  )
  FACTS (
    sales.revenue AS revenue,
    sales.cost AS cost,
    sales.profit AS profit  -- Pre-calculated: revenue - cost
  )
  DIMENSIONS (
    sales.sale_date AS sale_date
      WITH SYNONYMS ('date', 'transaction date', 'day')
      COMMENT = 'Date of sale transaction',
    sales.product_id AS product_id
      WITH SYNONYMS ('product', 'item', 'SKU'),
    sales.region AS region
      WITH SYNONYMS ('location', 'territory')
  )
  METRICS (
    sales.total_revenue AS SUM(revenue)
      WITH SYNONYMS ('total sales', 'gross revenue'),
    sales.total_profit AS SUM(profit)
      WITH SYNONYMS ('net profit', 'earnings'),
    sales.avg_revenue AS AVG(revenue)
      WITH SYNONYMS ('average sale', 'mean revenue')
  )
  COMMENT = 'Daily sales semantic view optimized for temporal analysis';
```

**Pattern 2: Aggregated Fact Views**

```sql
-- Pre-aggregated facts for performance
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.MONTHLY_SALES
  TABLES (
    monthly AS ANALYTICS.AGGREGATE.MONTHLY_SALES_AGG  -- Pre-aggregated base
      PRIMARY KEY (year_month, product_category)
  )
  FACTS (
    monthly.sales_amount AS sales_amount,
    monthly.units_sold AS units_sold,
    monthly.customer_count AS customer_count  -- Already aggregated
  )
  DIMENSIONS (
    monthly.year_month AS year_month
      WITH SYNONYMS ('month', 'period', 'year-month')
      COMMENT = 'Year-month in YYYY-MM format',
    monthly.product_category AS product_category
      WITH SYNONYMS ('category', 'product type')
  )
  METRICS (
    monthly.total_sales AS SUM(sales_amount),
    monthly.total_units AS SUM(units_sold),
    monthly.avg_monthly_sales AS AVG(sales_amount)
      WITH SYNONYMS ('average monthly revenue')
  )
  COMMENT = 'Monthly aggregated sales for trend analysis';
```

**Pattern 3: Multi-Dimensional Views**

```sql
-- Complex dimensional analysis
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.SALES_CUBE
  TABLES (
    sales AS ANALYTICS.CORE.SALES_FACT
      PRIMARY KEY (sale_id)
  )
  FACTS (
    sales.amount AS amount,
    sales.quantity AS quantity,
    sales.discount AS discount
  )
  DIMENSIONS (
    sales.product_id AS product_id
      WITH SYNONYMS ('product', 'item'),
    sales.customer_id AS customer_id
      WITH SYNONYMS ('customer', 'buyer'),
    sales.store_id AS store_id
      WITH SYNONYMS ('store', 'location'),
    sales.sale_date AS sale_date
      WITH SYNONYMS ('date', 'transaction date'),
    sales.channel AS channel
      WITH SYNONYMS ('sales channel', 'channel type')
      COMMENT = 'Online, In-Store, Mobile'
  )
  METRICS (
    sales.revenue AS SUM(amount),
    sales.total_quantity AS SUM(quantity),
    sales.avg_discount AS AVG(discount)
      WITH SYNONYMS ('average discount rate'),
    sales.transaction_count AS COUNT(*)
      WITH SYNONYMS ('number of sales', 'sale count')
  )
  COMMENT = 'Multi-dimensional sales cube for slice-and-dice analysis';
```

### 8.5 Development Checklist for AI Agents

**MANDATORY:**
**Before creating semantic view, verify:**
- [ ] Read base table structure with DESCRIBE TABLE
- [ ] Understand business grain and primary key
- [ ] Identify numeric columns for FACTS
- [ ] Identify categorical/temporal columns for DIMENSIONS
- [ ] Document intended metrics and aggregations

**During semantic view creation:**
- [ ] Use correct mapping syntax: `logical_name AS physical_column`
- [ ] Follow clause order: TABLES → FACTS → DIMENSIONS → METRICS
- [ ] Add WITH SYNONYMS for all business-critical fields
- [ ] Include COMMENT clauses with business definitions
- [ ] Use equals sign in COMMENT syntax: `COMMENT = 'text'`

**After semantic view creation:**
- [ ] Verify with SHOW SEMANTIC VIEWS
- [ ] Test basic query with SEMANTIC_VIEW()
- [ ] Validate metric calculations against base table
- [ ] Test Cortex Analyst natural language queries
- [ ] Review Query Profile for performance
- [ ] Document view purpose and usage examples

## Quick Compliance Checklist
- [ ] Use `CREATE SEMANTIC VIEW` (not `CREATE VIEW`)
- [ ] Clause order: TABLES → FACTS → DIMENSIONS → METRICS
- [ ] Mapping syntax: `logical_name AS physical_expression`
- [ ] PRIMARY KEY defined for relationships
- [ ] COMMENT clauses use equals sign: `COMMENT = 'text'`
- [ ] DIMENSIONS use simple columns (no CAST, DATE_TRUNC)
- [ ] WITH SYNONYMS provided for key business terms
- [ ] Security policies applied to base tables (not semantic views directly)
- [ ] Verified with `SHOW SEMANTIC VIEWS`
- [ ] Tested with Cortex Analyst REST API using `semantic_view` parameter

## Validation
- **Success Checks:** DDL compiles without errors; `SHOW SEMANTIC VIEWS` confirms object exists; `SHOW SEMANTIC DIMENSIONS/METRICS` returns expected structure; Cortex Analyst API accepts semantic view and returns valid responses; base table governance policies (masking, row access) apply correctly
- **Negative Tests:** Invalid clause order causes syntax error; reversed mappings fail with "invalid identifier"; CAST in DIMENSIONS fails; missing PRIMARY KEY prevents relationships; wrong COMMENT syntax causes compilation error

> **Investigation Required**  
> When applying this rule:
> 1. **Read base table schema BEFORE creating semantic view** - Use `DESCRIBE TABLE` or `SHOW COLUMNS` to verify column names and types
> 2. **Verify PRIMARY KEY columns exist** - Check actual table structure before defining PRIMARY KEY
> 3. **Never speculate about column names** - Read the physical table to confirm exact column names and types
> 4. **Check for existing semantic views** - Use `SHOW SEMANTIC VIEWS IN SCHEMA` to understand current semantic layer
> 5. **Make grounded recommendations based on investigated table structure** - Don't guess column names or create mappings without verification
>
> **Anti-Pattern:**
> "Based on typical patterns, the table probably has columns like order_id, order_date..."
> "Usually semantic views for this domain include these dimensions..."
>
> **Correct Pattern:**
> "Let me check the base table structure first."
> [runs `DESCRIBE TABLE DB.SCHEMA.TABLE` or reads table DDL]
> "I see the table has columns: asset_id (VARCHAR), asset_type (VARCHAR), rated_capacity (NUMBER). Here's the semantic view DDL based on these actual columns..."

## Response Template

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT 
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```
## Native Semantic View Implementation

**Semantic View:** `<DB>.<SCHEMA>.<VIEW_NAME>`
**Base Table:** `<DB>.<SCHEMA>.<TABLE>`
**Purpose:** <Business description>

**DDL:**
```sql
CREATE OR REPLACE SEMANTIC VIEW <DB>.<SCHEMA>.<VIEW_NAME>
  TABLES (
    <alias> AS <DB>.<SCHEMA>.<TABLE>
      PRIMARY KEY (<key_columns>)
  )
  FACTS (
    <alias>.<fact_name> AS <physical_column>
  )
  DIMENSIONS (
    <alias>.<dim_name> AS <physical_column>
  )
  METRICS (
    <alias>.<metric_name> AS <aggregate_function>(<expression>)
  );
```

**Verification:**
```bash
snow sql -q "SHOW SEMANTIC VIEWS IN SCHEMA <DB>.<SCHEMA>;"
```

**Cortex Analyst Usage:**
```python
payload = {
    "semantic_view": "<DB>.<SCHEMA>.<VIEW_NAME>",
    "messages": [{"role": "user", "content": "<NLQ_QUESTION>"}]
}
```
```

## References

### External Documentation
- [CREATE SEMANTIC VIEW DDL](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view) - Official DDL syntax reference
- [Semantic Views Overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview) - Conceptual overview and use cases
- [Semantic Views Best Practices - Development](https://docs.snowflake.com/en/user-guide/views-semantic/best-practices-dev) - Development workflow, Generator usage, testing patterns
- [Semantic Views SQL Examples](https://docs.snowflake.com/en/user-guide/views-semantic/sql#label-semantic-views-create) - Working DDL examples
- [Getting Started with Snowflake Semantic View](https://medium.com/snowflake/getting-started-with-snowflake-semantic-view-7eced29abe6f) - Tutorial with TPC-DS examples and iterative development workflow
- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Integration with Cortex Analyst
- [Cortex Agent Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Grounding agents on semantic views
- [Using the Cortex Analyst Semantic View Generator](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-generator) - Automated semantic view creation tool

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Demo Engineering**: `102-snowflake-sql-demo-engineering.md`
- **Security Governance**: `107-snowflake-security-governance.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Cortex AISQL**: `114-snowflake-cortex-aisql.md`
- **Cortex Agents**: `114a-snowflake-cortex-agents.md`
- **Cortex Analyst**: `114c-snowflake-cortex-analyst.md`
