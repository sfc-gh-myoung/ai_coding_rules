<!-- Generated for Cline rules. See https://docs.cline.bot/features/cline-rules -->

**Keywords:** CREATE SEMANTIC VIEW, FACTS, DIMENSIONS, METRICS, TABLES, RELATIONSHIPS, PRIMARY KEY, validation rules, relationship constraints, granularity rules, mapping syntax, anti-patterns
**TokenBudget:** ~6250
**ContextTier:** High
**Depends:** 100-snowflake-core

# Snowflake Native Semantic Views: Core DDL

## Purpose
Provide authoritative guidance for creating Snowflake Native Semantic Views using the `CREATE SEMANTIC VIEW` DDL syntax. Focuses on DDL structure, component definitions, anti-patterns, and comprehensive validation rules to prevent errors during semantic view creation.

**For querying semantic views and testing strategies, see `106a-snowflake-semantic-views-querying.mdc`.**
**For Cortex Analyst integration and development workflows, see `106b-snowflake-semantic-views-integration.mdc`.**

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake native semantic view DDL creation and validation

## Contract
- **Inputs/Prereqs:**
  - Target DATABASE.SCHEMA with appropriate privileges
  - Warehouse context with `CREATE SEMANTIC VIEW` privilege
  - Physical base tables/views with defined structure
  - Business glossary for naming dimensions, facts, and metrics
- **Allowed Tools:**
  - `CREATE SEMANTIC VIEW` DDL syntax
  - `SHOW SEMANTIC VIEWS`, `SHOW SEMANTIC DIMENSIONS`, `SHOW SEMANTIC METRICS`
  - Snowflake CLI for validation
- **Forbidden Tools:**
  - YAML semantic model uploads (legacy approach - use native views instead)
  - Regular `CREATE VIEW` when semantic view is appropriate
  - CAST, DATE_TRUNC in DIMENSIONS (use simple columns)
- **Required Steps:**
  1. Define TABLES block with physical base table references and PRIMARY KEY
  2. Declare FACTS (numeric measures at row level)
  3. Declare DIMENSIONS (categorical and temporal attributes - simple columns only)
  4. Define METRICS (aggregations over facts/dimensions)
  5. Add WITH SYNONYMS for improved NLQ accuracy
  6. Add COMMENT clauses for documentation (use `=` syntax)
  7. Validate using `SHOW SEMANTIC VIEWS`
- **Output Format:**
  - Minimal, runnable `CREATE SEMANTIC VIEW` DDL statements
  - Clear separation of TABLES, FACTS, DIMENSIONS, METRICS blocks
- **Validation Steps:**
  - DDL compiles without syntax errors
  - `SHOW SEMANTIC VIEWS` confirms object creation
  - `SHOW SEMANTIC DIMENSIONS/METRICS` validates structure
  - Validation rules pass (relationships, granularity, expressions)

## Key Principles
- **Native database objects**: Semantic views are schema-level objects stored in Snowflake's metadata
- **Explicit syntax**: Column mappings use `logical_name AS physical_expression` format
- **Clause ordering**: Must follow TABLES → FACTS → DIMENSIONS → METRICS sequence
- **Simple expressions**: DIMENSIONS use simple columns only (no CAST, DATE_TRUNC)
- **Comment syntax**: Use `COMMENT = 'text'` (with equals sign)
- **Validation first**: Understand validation rules to prevent errors

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Use `CREATE SEMANTIC VIEW` DDL** - Native database objects, not YAML files
- **Correct mapping syntax** - `logical_name AS physical_column` (NOT reversed)
- **Clause order matters** - TABLES → FACTS → DIMENSIONS → METRICS (strict sequence)
- **Simple expressions in DIMENSIONS** - No CAST, DATE_TRUNC, or complex functions
- **COMMENT uses equals sign** - `COMMENT = 'text'` (NOT `COMMENT 'text'`)
- **PRIMARY KEY uses physical columns** - Required for relationships
- **Relationships are many-to-one** - No circular, no self-ref, no multi-path
- **Respect granularity rules** - Aggregate when referencing higher granularity
- **Window function metrics cannot nest** - Cannot use in dimensions, facts, or other metrics

**Quick Checklist:**
- [ ] Clause order: TABLES → FACTS → DIMENSIONS → METRICS
- [ ] PRIMARY KEY defined in TABLES block (uses physical columns only)
- [ ] Mappings use correct syntax: `logical_name AS physical_column`
- [ ] All COMMENT clauses have equals sign
- [ ] DIMENSIONS use simple columns only (no CAST, DATE_TRUNC)
- [ ] At least one dimension or metric defined
- [ ] Relationships are many-to-one (no circular, no self-ref)
- [ ] Cross-table references use relationships (not direct column refs)
- [ ] Granularity rules respected (aggregate when referencing higher granularity)
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
    [COMMENT = '<dimension_description>'],
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


## 4) Validation Rules

### 4.1 General Validation Rules

**Purpose:** Understand Snowflake's validation rules to prevent errors during semantic view creation.

**Required Elements:**
```sql
-- CORRECT: Must have at least one dimension or metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders
      PRIMARY KEY (order_id)
  )
  DIMENSIONS (
    orders.order_id AS order_id
  );

-- ERROR: No dimensions or metrics defined
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders
      PRIMARY KEY (order_id)
  );
-- Error: A semantic view must define at least one dimension or metric
```

**Primary and Foreign Keys:**
```sql
-- CORRECT: Use physical base table columns in keys
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey),      -- Physical column
    orders AS db.schema.orders
      PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
    -- Both o_custkey and c_custkey are physical columns
  )
  DIMENSIONS (
    customer.name AS c_name
  );
```

**Table Alias References:**
```sql
-- CORRECT: Use defined aliases in expressions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders_table  -- Alias is 'orders'
      PRIMARY KEY (o_orderkey)
  )
  DIMENSIONS (
    orders.order_id AS o_orderkey     -- Use 'orders' alias, not 'orders_table'
  );

-- ERROR: Using physical table name instead of alias
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders_table
      PRIMARY KEY (o_orderkey)
  )
  DIMENSIONS (
    orders_table.order_id AS o_orderkey  -- Wrong: should use 'orders'
  );
-- Error: Invalid table reference 'orders_table'
```

### 4.2 Relationship Validation Rules

**Many-to-One Relationships:**
```sql
-- CORRECT: Many orders to one customer
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey),
    orders AS db.schema.orders
      PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
    -- Many orders can belong to one customer (c_custkey must be PRIMARY KEY)
  )
  DIMENSIONS (
    customer.name AS c_name,
    orders.order_date AS o_orderdate
  );
```

**Transitive Relationships:**
```sql
-- Snowflake automatically derives indirect relationships
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey),
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey)
    -- Snowflake automatically understands line_items relates to customer
  )
  DIMENSIONS (
    customer.name AS c_name,
    line_items.quantity AS l_quantity
    -- Can reference customer from line_items via transitive relationship
  );
```

**Circular Relationships (FORBIDDEN):**
```sql
-- ERROR: Circular relationship
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey),
    customer_to_orders AS customer(c_recent_order) REFERENCES orders(o_orderkey)
    -- Creates circular relationship between customer and orders
  );
-- Error: Circular relationships are not allowed
```

**Self-References (NOT SUPPORTED):**
```sql
-- ERROR: Self-referencing relationship
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    employee AS db.schema.employee PRIMARY KEY (emp_id)
  )
  RELATIONSHIPS (
    employee_manager AS employee(manager_id) REFERENCES employee(emp_id)
    -- Self-reference for employee-manager hierarchy not supported
  );
-- Error: A table cannot reference itself
```

**Multi-Path Relationship Restrictions:**
```sql
-- LIMITATION: Multiple paths between tables have restrictions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders_key AS line_items(l_orderkey) REFERENCES orders(o_orderkey),
    lineitem_to_orders_alt AS line_items(l_alt_key) REFERENCES orders(o_alt_key)
    -- Multiple paths: these tables cannot refer to each other's semantic expressions
  );

-- SOLUTION: Define separate logical tables for different paths
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    orders_alt AS db.schema.orders PRIMARY KEY (o_alt_key),  -- Separate logical table
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey),
    lineitem_to_orders_alt AS line_items(l_alt_key) REFERENCES orders_alt(o_alt_key)
  );
```

**One-to-One Relationship Restrictions:**
```sql
-- LIMITATION: One-to-one relationships have usage restrictions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    order_summary AS db.schema.order_summary
  )
  RELATIONSHIPS (
    orders_to_summary AS orders(o_orderkey) REFERENCES order_summary(summary_id)
    -- o_orderkey has unique values (one-to-one)
  )
  DIMENSIONS (
    orders.order_id AS o_orderkey
  )
  METRICS (
    orders.total AS SUM(order_summary.amount)  -- orders can refer to order_summary
    -- order_summary CANNOT refer to orders semantic expressions
  );
```

### 4.3 Expression Validation Rules

**Expression Types:**
```sql
-- Dimensions and facts are row-level (unaggregated)
DIMENSIONS (
  customer.customer_name AS c_name        -- Row-level
)
FACTS (
  orders.order_amount AS o_totalprice     -- Row-level
)

-- Metrics are aggregate-level (aggregated)
METRICS (
  orders.order_average AS AVG(o_totalprice)  -- Aggregate-level
)
```

**Table Association (MANDATORY):**
```sql
-- CORRECT: Every expression associated with table
DIMENSIONS (
  customer.customer_name AS c_name,       -- Associated with 'customer' table
  orders.order_date AS o_orderdate        -- Associated with 'orders' table
)

-- ERROR: Expression without table association
DIMENSIONS (
  customer_name AS c_name                 -- Missing table prefix
);
-- Error: Expression must be associated with a table
```

**Same-Table References:**
```sql
-- Both qualified and unqualified references allowed within same table
DIMENSIONS (
  orders.shipping_month AS MONTH(o_shipdate),           -- Unqualified column
  orders.shipping_year AS YEAR(orders.o_shipdate)       -- Qualified column
  -- Both work because referencing same table's column
)
```

**Cross-Table Limitations:**
```sql
-- ERROR: Direct reference to unrelated table column
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  -- No relationship defined
  DIMENSIONS (
    customer.order_count AS COUNT(orders.o_orderkey)  -- Cannot reference orders
  );
-- Error: Expression cannot refer to columns from unrelated tables

-- CORRECT: Use relationships and facts
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  FACTS (
    orders.order_key AS o_orderkey           -- Define fact on source table
  )
  DIMENSIONS (
    customer.order_count AS COUNT(orders.order_key)  -- Reference via relationship
  );
```

**Name Resolution:**
```sql
-- If semantic expression and column have same name, expression takes precedence
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey)
  )
  DIMENSIONS (
    customer.region AS UPPER(c_region),      -- Define 'region' dimension
    customer.regional_id AS CONCAT(region, c_custkey)
    -- 'region' resolves to dimension, not column
  );

-- Exception: Self-referential definition
DIMENSIONS (
  customer.c_name AS customer.c_name       -- 'c_name' resolves to column, not itself
)
```

**Expression Reference Cycles (FORBIDDEN):**
```sql
-- ERROR: Circular expression references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    customer.total_value AS SUM(orders.customer_value),
    orders.customer_value AS AVG(customer.total_value)  -- Circular reference
  );
-- Error: Circular references between expressions not allowed
```

**Table Reference Cycles (FORBIDDEN):**
```sql
-- ERROR: Circular table references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  DIMENSIONS (
    customer.total_value AS SUM(orders.customer_value),
    orders.customer_count AS COUNT(customer.c_custkey)  -- Circular table refs
  );
-- Error: Circular references between logical tables not allowed
```

**Function Usage:**
```sql
-- ALLOWED: Scalar functions in dimensions
DIMENSIONS (
  orders.order_year AS YEAR(o_orderdate),
  orders.order_month AS MONTH(o_orderdate),
  orders.order_quarter AS QUARTER(o_orderdate),
  orders.order_week AS WEEK(o_orderdate),
  orders.order_day AS DAY(o_orderdate)
)

-- FORBIDDEN: Table functions not allowed
DIMENSIONS (
  orders.flattened AS FLATTEN(o_json_column)  -- Table function not supported
);
-- Error: Table functions are not allowed in dimensions
```

### 4.4 Row-Level Expression Rules (Dimensions and Facts)

**Same-Table References:**
```sql
-- Row-level expression can directly refer to own table columns
DIMENSIONS (
  customer.customer_name AS c_name,           -- Direct column reference
  customer.full_name AS CONCAT(c_firstname, ' ', c_lastname)
)
```

**Equal or Lower Granularity:**
```sql
-- Can reference row-level expressions at same or lower granularity
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  DIMENSIONS (
    customer.name AS c_name,
    orders.customer_name AS customer.name  -- Lower granularity: OK
    -- One customer has many orders, so customer is lower granularity
  );
```

**Higher Granularity References (Requires Aggregation):**
```sql
-- Must use aggregation when referencing higher granularity
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  FACTS (
    orders.order_key AS o_orderkey
  )
  DIMENSIONS (
    customer.total_orders AS COUNT(orders.order_key)  -- Must aggregate
    -- Orders is higher granularity than customer (one customer = many orders)
  );
```

**Aggregate References (Restrictions):**
```sql
-- FORBIDDEN: Dimension cannot refer to metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  METRICS (
    orders.avg_value AS AVG(o_totalprice)
  )
  DIMENSIONS (
    orders.order_type AS CASE 
      WHEN orders.avg_value > 1000 THEN 'Large'  -- Cannot reference metric
      ELSE 'Small'
    END
  );
-- Error: Dimensions cannot refer to metrics

-- ALLOWED: Lower granularity dimension can refer to higher granularity metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    orders.avg_value AS AVG(o_totalprice)
  )
  DIMENSIONS (
    customer.segment AS CASE
      WHEN orders.avg_value > 1000 THEN 'Premium'  -- OK: customer lower granularity
      ELSE 'Standard'
    END
  );
```

### 4.5 Aggregate-Level Expression Rules (Metrics)

**Basic Aggregation (MANDATORY):**
```sql
-- CORRECT: Metric uses aggregate function
METRICS (
  orders.order_average AS AVG(o_totalprice),
  orders.order_total AS SUM(o_totalprice),
  orders.order_count AS COUNT(*)
)

-- ERROR: Metric without aggregation
METRICS (
  orders.order_amount AS o_totalprice  -- Missing aggregation
);
-- Error: Metrics must use aggregate functions
```

**Equal or Lower Granularity (Single Aggregate):**
```sql
-- Use single aggregate for equal or lower granularity references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey)
  )
  FACTS (
    line_items.discounted_price AS l_extendedprice * (1 - l_discount)
  )
  METRICS (
    orders.total_value AS SUM(line_items.discounted_price)  -- Single aggregate
    -- line_items is lower granularity than orders (many line items per order)
  );
```

**Higher Granularity References (Nested Aggregation):**
```sql
-- Must use nested aggregation for higher granularity references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    customer.avg_order_value AS AVG(SUM(orders.o_totalprice))  -- Nested agg
    -- orders is higher granularity than customer (one customer = many orders)
    -- Inner SUM aggregates by order, outer AVG aggregates across orders
  );
```

**Metric-to-Metric References:**
```sql
-- Can reference other metrics at equal or lower granularity without aggregation
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  METRICS (
    orders.total_revenue AS SUM(o_totalprice),
    orders.total_cost AS SUM(o_cost),
    orders.profit_margin AS orders.total_revenue / orders.total_cost  -- No extra agg
    -- Both metrics at same granularity (orders level)
  );

-- Requires aggregation when referencing higher granularity metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    orders.total_value AS SUM(o_totalprice),
    customer.avg_order_value AS AVG(orders.total_value)  -- Aggregation required
    -- orders is higher granularity than customer
  );
```

### 4.6 Window Function Metric Restrictions

**Cannot Use in Row-Level Calculations:**
```sql
-- FORBIDDEN: Window function metric in dimension
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    sales AS db.schema.sales PRIMARY KEY (sale_id)
  )
  METRICS (
    sales.running_total AS SUM(SUM(amount)) OVER (ORDER BY sale_date)
  )
  DIMENSIONS (
    sales.is_high_sale AS CASE
      WHEN sales.running_total > 1000 THEN 'Yes'  -- Cannot use window metric
      ELSE 'No'
    END
  );
-- Error: Window function metrics cannot be used in dimensions

-- FORBIDDEN: Window function metric in fact
FACTS (
  sales.daily_rank AS RANK() OVER (PARTITION BY sale_date ORDER BY amount)
  -- Cannot use window functions in facts
);
```

**Cannot Use in Other Metrics:**
```sql
-- FORBIDDEN: Window function metric in another metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    sales AS db.schema.sales PRIMARY KEY (sale_id)
  )
  METRICS (
    sales.running_total AS SUM(SUM(amount)) OVER (ORDER BY sale_date),
    sales.pct_of_running AS amount / sales.running_total  -- Cannot reference
  );
-- Error: Window function metrics cannot be used in other metric definitions
```

### 4.7 Validation Best Practices

**Pre-Creation Checklist:**
```sql
-- Before creating semantic view, verify:
-- [ ] At least one dimension or metric defined
-- [ ] PRIMARY KEY uses physical columns only
-- [ ] All relationships are many-to-one (no circular, no self-ref)
-- [ ] Table aliases used consistently in expressions
-- [ ] No circular expression or table references
-- [ ] Row-level expressions respect granularity rules
-- [ ] Metrics use proper aggregation (nested when needed)
-- [ ] Window function metrics not used in other expressions
-- [ ] Only scalar functions in dimensions (no table functions)

-- Validate after creation:
SHOW SEMANTIC VIEWS IN SCHEMA my_schema;
DESCRIBE SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW my_schema.my_view;
```

## See Also

**Related Semantic View Rules:**
- **106a-snowflake-semantic-views-querying.mdc** - Query patterns, testing, SEMANTIC_VIEW() function, dimension compatibility, window function metrics, WHERE clause usage, performance optimization
- **106b-snowflake-semantic-views-integration.mdc** - Cortex Analyst/Agent integration, REST API usage, governance (RBAC, masking, row access), Generator workflow, iterative development, synonym design

## Quick Compliance Checklist

**DDL Creation:**
- [ ] Use `CREATE SEMANTIC VIEW` (not `CREATE VIEW`)
- [ ] Clause order: TABLES → FACTS → DIMENSIONS → METRICS
- [ ] Mapping syntax: `logical_name AS physical_column` (NOT reversed)
- [ ] PRIMARY KEY defined in TABLES block (uses physical columns only)
- [ ] COMMENT clauses use equals sign: `COMMENT = 'text'`
- [ ] DIMENSIONS use simple columns (no CAST, DATE_TRUNC)
- [ ] At least one dimension or metric defined
- [ ] Verified with `SHOW SEMANTIC VIEWS`

**Validation Rules:**
- [ ] Relationships are many-to-one (no circular, no self-ref, no multi-path)
- [ ] Table aliases used consistently in expressions
- [ ] No circular expression or table reference cycles
- [ ] Cross-table references use relationships (not direct column refs)
- [ ] Row-level expressions respect granularity rules (aggregate for higher granularity)
- [ ] Metrics use proper aggregation (nested when referencing higher granularity)
- [ ] Window function metrics not used in dimensions, facts, or other metrics
- [ ] Only scalar functions in dimensions (no table functions)

## Validation
- **Success Checks:**
  - DDL compiles without syntax errors
  - `SHOW SEMANTIC VIEWS` confirms object creation
  - `SHOW SEMANTIC DIMENSIONS/METRICS` returns expected structure
  - Validation rules pass (relationships, granularity, expressions)
  - Correct mapping syntax used (logical_name AS physical_expression)
  - Clause order correct (TABLES → FACTS → DIMENSIONS → METRICS)
  - COMMENT syntax correct (uses equals sign)
  - PRIMARY KEY uses physical columns only
- **Negative Tests:**
  - Reversed mappings cause syntax error ("invalid identifier")
  - CAST/DATE_TRUNC in DIMENSIONS causes syntax error
  - Wrong COMMENT syntax (missing equals) causes syntax error
  - Wrong clause order causes syntax error or unexpected behavior
  - Missing PRIMARY KEY prevents relationships
  - Circular relationships cause error
  - Self-referencing relationships cause error
  - Direct cross-table references without relationships cause error
  - Dimension referencing metric (same granularity) causes error
  - Window function metric in dimension/fact/other metric causes error

## Response Template

```sql
-- Semantic View: <logical_name>
-- Purpose: <business purpose>
-- Base Tables: <list tables>
-- Key Metrics: <primary metrics>

CREATE OR REPLACE SEMANTIC VIEW <database>.<schema>.<view_name>
COMMENT = 'Business-friendly description'
AS
  TABLES (
    <table_alias> AS <database>.<schema>.<table_name> (
      PRIMARY KEY (<physical_column>)
    ),
    <related_table_alias> AS <database>.<schema>.<related_table> (
      PRIMARY KEY (<physical_column>),
      FOREIGN KEY (<fk_column>) REFERENCES <table_alias>(<pk_column>)
    )
  )
  FACTS (
    <logical_fact> AS <table_alias>.<physical_column>
      COMMENT = 'Row-level measure description'
  )
  DIMENSIONS (
    <logical_dimension> AS <table_alias>.<physical_column>
      COMMENT = 'Grouping attribute description'
  )
  METRICS (
    <logical_metric> AS AGG_FUNCTION(<table_alias>.<physical_column>)
      COMMENT = 'Aggregated business metric description'
  );

-- Validation checks
SHOW SEMANTIC VIEWS LIKE '<view_name>';
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW <view_name>;
SHOW SEMANTIC METRICS FOR SEMANTIC VIEW <view_name>;
```

> **Investigation Required**  
> When applying this rule:
> 1. **Read existing semantic views BEFORE creating new ones** - Check for naming patterns, standards, and conventions
> 2. **Verify base table schemas** - Use `DESCRIBE TABLE` to confirm physical column names and types
> 3. **Never assume table structures** - Always query `INFORMATION_SCHEMA.COLUMNS` or use `SHOW COLUMNS`
> 4. **Check existing relationships** - Verify foreign key relationships between tables before defining semantic relationships
> 5. **Validate granularity assumptions** - Confirm whether tables are fact tables (many rows per entity) or dimension tables (one row per entity)
> 6. **Make grounded recommendations based on investigated schema** - Don't create mappings for columns that don't exist
>
> **Anti-Pattern:**
> "Based on typical data models, you probably have a customer_id column..."
> "Let me create a semantic view with standard dimension names..."
>
> **Correct Pattern:**
> "Let me check your table schema first."
> [runs DESCRIBE TABLE or queries INFORMATION_SCHEMA]
> "I see your table has these columns: [actual columns]. Here's a semantic view definition using your actual schema..."

## References

### External Documentation
- [CREATE SEMANTIC VIEW DDL](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view) - Official DDL syntax reference
- [Semantic Views Overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview) - Conceptual overview and use cases
- [Using SQL to create and manage views](https://docs.snowflake.com/en/user-guide/views-semantic/sql) - SQL workflow and examples
- [Validation Rules for Semantic Views](https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules) - Complete validation rule reference

### Related Rules
- **Querying Semantic Views**: `106a-snowflake-semantic-views-querying.md` - SEMANTIC_VIEW() query patterns and testing
- **Integration & Development**: `106b-snowflake-semantic-views-integration.md` - Cortex Analyst, governance, workflows
- **Snowflake Core**: `100-snowflake-core.md` - Foundational Snowflake practices
- **Cortex Analyst**: `114c-snowflake-cortex-analyst.md` - Natural language query patterns

