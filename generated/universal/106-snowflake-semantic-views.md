**Keywords:** Semantic models, semantic views, Cortex Analyst, data modeling, business logic layer, metrics layer
**Depends:** 100-snowflake-core

**TokenBudget:** ~800
**ContextTier:** High

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
  tfm.event_timestamp AS timestamp,  -- ✅ Simple timestamp
  tfm.substation AS substation_id    -- ✅ Simple column
  -- tfm.reading_date AS CAST(timestamp AS DATE)  -- ❌ CAST not supported
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
  ami.total_outages AS SUM(outage_flag)  -- ✅ Simple SUM on flag
  -- ami.customers_impacted AS SUM(CASE WHEN outage_flag = 1 THEN 1 ELSE 0 END)  -- ⚠️ May fail
)
```

## 3) Anti-Patterns and Common Mistakes


**❌ Anti-Pattern 1: Reversed Mapping Syntax**
```sql
-- INCORRECT - Backwards mapping (will cause syntax error)
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS total_amount  -- ❌ Reversed!
  )
  DIMENSIONS (
    orders.order_id AS order_number      -- ❌ Reversed!
  );
```
**Problem:** Syntax error: "invalid identifier 'ORDER_AMOUNT'" - the mapping is backwards.

**✅ Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.total_amount AS order_amount  -- ✅ logical_name AS physical_column
  )
  DIMENSIONS (
    orders.order_number AS order_id      -- ✅ logical_name AS physical_column
  );
```
**Benefits:** Correct syntax compiles successfully.

---

**❌ Anti-Pattern 2: Complex Expressions in DIMENSIONS**
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
    orders.reading_date AS CAST(order_timestamp AS DATE),  -- ❌ CAST not allowed
    orders.order_hour AS DATE_TRUNC('hour', order_timestamp) -- ❌ DATE_TRUNC not allowed
  );
```
**Problem:** Syntax error: "unexpected 'CAST'" or "invalid expression" - dimensions must be simple columns.

**✅ Correct Pattern:**
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
    orders.order_timestamp AS order_timestamp  -- ✅ Use raw timestamp
    -- Add derived columns (date parts) to base table/view if needed
  );
```
**Benefits:** Clean dimensions that work with Cortex Analyst's temporal intelligence.

---

**❌ Anti-Pattern 3: Missing Equals Sign in COMMENT**
```sql
-- INCORRECT - COMMENT without equals sign
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT 'Sales orders table'  -- ❌ Missing equals sign
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT 'Total order value'   -- ❌ Missing equals sign
  );
```
**Problem:** Syntax error: "unexpected 'Sales'" - COMMENT requires equals sign.

**✅ Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT = 'Sales orders table'  -- ✅ Equals sign required
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT = 'Total order value'   -- ✅ Equals sign required
  );
```
**Benefits:** Proper comment syntax compiles successfully.

---

**❌ Anti-Pattern 4: Wrong Clause Order**
```sql
-- INCORRECT - Wrong clause ordering
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  DIMENSIONS (                        -- ❌ DIMENSIONS before FACTS
    orders.order_id AS order_id
  )
  FACTS (                             -- ❌ FACTS after DIMENSIONS
    orders.order_amount AS order_amount
  );
```
**Problem:** Syntax error or unexpected behavior - clause order matters.

**✅ Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (                             -- ✅ FACTS first
    orders.order_amount AS order_amount
  )
  DIMENSIONS (                        -- ✅ DIMENSIONS after FACTS
    orders.order_id AS order_id
  )
  METRICS (                           -- ✅ METRICS last
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
- ✅ **Native views:** Use `"semantic_view": "DB.SCHEMA.VIEW_NAME"`
- ❌ **Legacy YAML:** Used `"semantic_model": "@stage/model.yaml"`
- ✅ **No staging:** No need to upload files to internal stages
- ✅ **Version control:** DDL changes tracked via SQL migrations

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

### Verification Commands

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

### Testing with Cortex Analyst

```bash
# Test NLQ query via SnowCLI
snow cortex analyst query \
  --semantic-view "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH" \
  --question "What is the average load for transformers in the last 24 hours?"
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
- ✅ No YAML files to maintain
- ✅ No stage uploads required
- ✅ Standard SQL version control
- ✅ Integrated with database governance
- ✅ Simpler deployment pipeline

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

## Response Template
```markdown
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
- [Semantic Views SQL Examples](https://docs.snowflake.com/en/user-guide/views-semantic/sql#label-semantic-views-create) - Working DDL examples
- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Integration with Cortex Analyst
- [Cortex Agent Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Grounding agents on semantic views

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Demo Engineering**: `102-snowflake-sql-demo-engineering.md`
- **Security Governance**: `107-snowflake-security-governance.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Cortex AISQL**: `114-snowflake-cortex-aisql.md`
- **Cortex Agents**: `114a-snowflake-cortex-agents.md`
- **Cortex Analyst**: `114c-snowflake-cortex-analyst.md`
