# Snowflake Native Semantic Views: Core DDL

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Semantic Views patterns. Load for Semantic Views tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** TABLES, RELATIONSHIPS, PRIMARY KEY, validation rules, semantic view error, create semantic view, debug semantic view, SQL, verified queries, VQR, YAML semantic model, NLQ, mapping syntax, granularity rules
**TokenBudget:** ~5550
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide authoritative guidance for creating Snowflake Native Semantic Views using the `CREATE SEMANTIC VIEW` DDL syntax. Focuses on DDL structure, component definitions, anti-patterns, and comprehensive validation rules to prevent errors during semantic view creation.

**For querying semantic views and testing strategies, see `rules/106b-snowflake-semantic-views-querying.md`.**
**For Cortex Analyst integration and development workflows, see `rules/106c-snowflake-semantic-views-integration.md`.**

## Rule Scope

Snowflake native semantic view DDL creation and validation

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~500 tokens (always load for semantic view tasks)
- + Core DDL Patterns (sections 1-3): ~1500 tokens (load for creation)
- + Validation & Troubleshooting (sections 4-5): ~2300 tokens (load for debugging)
- + Complete Reference: ~2800 tokens (full semantic view guide)

**Recommended Loading Strategy:**
- **Understanding semantic views**: Quick Start only
- **Creating views**: + Core DDL Patterns
- **Debugging issues**: + Validation & Troubleshooting
- **Advanced patterns**: + 106a (advanced), 106b (querying)

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use `CREATE SEMANTIC VIEW` DDL** - Native database objects, not YAML files
- **Correct mapping syntax** - `logical_name AS physical_column` (NOT reversed)
- **Clause order matters** - TABLES, then FACTS, then DIMENSIONS, then METRICS (strict sequence)
- **Simple expressions in DIMENSIONS** - No CAST, DATE_TRUNC, or complex functions
- **COMMENT uses equals sign** - `COMMENT = 'text'` (NOT `COMMENT 'text'`)
- **PRIMARY KEY uses physical columns** - Required for relationships
- **Relationships are many-to-one** - No circular, no self-ref, no multi-path
- **Respect granularity rules** - Aggregate when referencing higher granularity
- **Window function metrics cannot nest** - Cannot use in dimensions, facts, or other metrics

**Quick Checklist:**
- [ ] Clause order: TABLES, then FACTS, then DIMENSIONS, then METRICS
- [ ] PRIMARY KEY defined in TABLES block (uses physical columns only)
- [ ] Mappings use correct syntax: `logical_name AS physical_column`
- [ ] All COMMENT clauses have equals sign
- [ ] DIMENSIONS use simple columns only (no CAST, DATE_TRUNC)
- [ ] At least one dimension or metric defined
- [ ] Relationships are many-to-one (no circular, no self-ref)
- [ ] Cross-table references use relationships (not direct column refs)
- [ ] Granularity rules respected (aggregate when referencing higher granularity)
- [ ] No `&` or template characters in SYNONYMS, COMMENT, or identifiers (CLI compatibility)
- [ ] Validated with `SHOW SEMANTIC VIEWS`

## Contract

<contract>
<inputs_prereqs>
- Target DATABASE.SCHEMA with appropriate privileges
- Warehouse context with `CREATE SEMANTIC VIEW` privilege
- Physical base tables/views with defined structure
- Business glossary for naming dimensions, facts, and metrics
</inputs_prereqs>

<mandatory>
- `CREATE SEMANTIC VIEW` DDL syntax
- `SHOW SEMANTIC VIEWS`, `SHOW SEMANTIC DIMENSIONS`, `SHOW SEMANTIC METRICS`
- Snowflake CLI for validation
</mandatory>

<forbidden>
- YAML semantic model uploads (legacy approach - use native views instead)
- Regular `CREATE VIEW` when semantic view is appropriate
- CAST, DATE_TRUNC in DIMENSIONS (use simple columns)
- Verified queries in DDL (must use YAML semantic model files)
</forbidden>

<steps>
1. Define TABLES block with physical base table references and PRIMARY KEY
2. Declare FACTS (numeric measures at row level)
3. Declare DIMENSIONS (categorical and temporal attributes - simple columns only)
4. Define METRICS (aggregations over facts/dimensions)
5. Add WITH SYNONYMS for improved NLQ accuracy
6. Add COMMENT clauses for documentation (use `=` syntax)
7. Validate using `SHOW SEMANTIC VIEWS`
</steps>

<output_format>
- Minimal, runnable `CREATE SEMANTIC VIEW` DDL statements
- Clear separation of TABLES, FACTS, DIMENSIONS, METRICS blocks
</output_format>

<validation>
- DDL compiles without syntax errors
- `SHOW SEMANTIC VIEWS` confirms object creation
- `SHOW SEMANTIC DIMENSIONS/METRICS` validates structure
- Validation rules pass (relationships, granularity, expressions)
</validation>

<design_principles>
- **Native database objects**: Semantic views are schema-level objects stored in Snowflake's metadata
- **Explicit syntax**: Column mappings use `logical_name AS physical_expression` format
- **Clause ordering**: Must follow TABLES, then FACTS, then DIMENSIONS, then METRICS sequence
- **Simple expressions**: DIMENSIONS use simple columns only (no CAST, DATE_TRUNC)
- **Comment syntax**: Use `COMMENT = 'text'` (with equals sign)
- **Validation first**: Understand validation rules to prevent errors
> **Investigation Required**
> When working with semantic views:
> 1. Check if semantic view exists first with `SHOW SEMANTIC VIEWS LIKE '%name%';`
> 2. Read the DDL structure before making recommendations - use `GET_DDL('SEMANTIC_VIEW', 'DB.SCHEMA.VIEW')`
> 3. Verify base tables exist and are populated - query them directly first
> 4. Never assume mapping syntax - always verify logical_name AS physical_column order
> 5. Test queries against the semantic view before using in production
> 6. Check for COMMENT syntax (must have equals sign: `COMMENT = 'text'`)
>
> **Anti-Pattern:**
> "Based on typical patterns, this view probably maps customer_id to..."
>
> **Correct Pattern:**
> "Let me read the semantic view DDL first to give accurate guidance."
> [reads DDL using GET_DDL or SHOW commands]
> "After reviewing the DDL, I found the view maps customer_id AS cust_id. Here's my recommendation..."
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Following TABLES, FACTS, DIMENSIONS, METRICS Sequence**
```sql
-- Bad: Wrong clause ordering
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  DIMENSIONS (
    customer_id AS customers.customer_id
  )
  TABLES (
    sales_data AS sales
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
  );
-- Error: Syntax error - clauses out of order!
```
**Problem:** Syntax errors; semantic view creation fails; deployment blocked; unprofessional; confusion; documentation misalignment

**Correct Pattern:**
```sql
-- Good: Correct clause sequence
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales,
    customer_data AS customers
  )
  RELATIONSHIPS (
    sales.customer_id = customers.customer_id
  )
  DIMENSIONS (
    customer_id AS customers.customer_id
      COMMENT 'Unique customer identifier'
      SYNONYMS ('cust id', 'customer number'),
    customer_name AS customers.name
      COMMENT 'Customer full name'
      SYNONYMS ('cust name', 'client name')
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT 'Total sales revenue'
      SYNONYMS ('revenue', 'sales total', 'income'),
    order_count AS COUNT(sales.order_id)
      COMMENT 'Number of orders'
      SYNONYMS ('num orders', 'order total')
  );
```
**Benefits:** Valid DDL; successful deployment; Cortex Analyst compatible; professional; clear structure; maintainable


**Anti-Pattern 2: Using Complex Expressions in DIMENSIONS (CAST, DATE_TRUNC Not Allowed)**
```sql
-- Bad: Complex transformations in DIMENSIONS
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
  )
  DIMENSIONS (
    sale_month AS DATE_TRUNC('MONTH', sales.order_date)  -- NOT ALLOWED!
      COMMENT 'Month of sale',
    revenue_category AS CASE WHEN sales.amount > 1000 THEN 'High' ELSE 'Low' END  -- NOT ALLOWED!
      COMMENT 'Revenue category'
  );
-- Error: DATE_TRUNC and CASE not supported in DIMENSIONS!
```
**Problem:** Syntax errors; deployment failure; Cortex Analyst can't parse; query failures; wasted development time; emergency fixes

**Correct Pattern:**
```sql
-- Good: Simple column references only in DIMENSIONS
-- Option 1: Use simple columns from base tables
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
  )
  DIMENSIONS (
    order_date AS sales.order_date
      COMMENT 'Date of sale'
      SYNONYMS ('sale date', 'order day', 'purchase date'),
    amount AS sales.amount
      COMMENT 'Sale amount in USD'
      SYNONYMS ('price', 'revenue', 'sale value')
  )
  METRICS (
    monthly_revenue AS SUM(sales.amount)
      COMMENT 'Revenue by month'
      SYNONYMS ('monthly sales')
  );

-- Option 2: Pre-compute transformations in base tables or views
CREATE OR REPLACE VIEW sales_enriched AS
SELECT
  *,
  DATE_TRUNC('MONTH', order_date) AS sale_month,
  CASE WHEN amount > 1000 THEN 'High' ELSE 'Low' END AS revenue_category
FROM sales_data;

-- Then use simple columns in semantic view
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_enriched AS sales
  )
  DIMENSIONS (
    sale_month AS sales.sale_month  -- Simple column reference
      COMMENT 'Month of sale',
    revenue_category AS sales.revenue_category  -- Simple column reference
      COMMENT 'Revenue category'
  );
```
**Benefits:** Valid syntax; deployment succeeds; Cortex Analyst compatible; query reliability; maintainable; professional; separation of concerns


**Anti-Pattern 3: Missing Equals Sign in COMMENT Syntax**
```sql
-- Bad: COMMENT without equals sign
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
  )
  DIMENSIONS (
    customer_id AS sales.customer_id
      COMMENT 'Customer identifier'  -- Missing "="!
      SYNONYMS ('cust id')
  );
-- Error: Syntax error near 'Customer identifier'
```
**Problem:** Syntax error; deployment fails; confusing error message; delayed deployments; frustration; unprofessional

**Correct Pattern:**
```sql
-- Good: COMMENT = 'text' (with equals sign)
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
  )
  DIMENSIONS (
    customer_id AS sales.customer_id
      COMMENT = 'Customer identifier'  -- Correct syntax with "="
      SYNONYMS ('cust id', 'customer number'),
    product_id AS sales.product_id
      COMMENT = 'Product identifier'
      SYNONYMS ('prod id', 'item id')
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Total sales revenue'
      SYNONYMS ('revenue', 'sales')
  );
```
**Benefits:** Valid syntax; successful deployment; clear documentation; Cortex Analyst compatible; professional; no deployment delays


**Anti-Pattern 4: Not Validating Semantic View DDL Before Deployment**
```sql
-- Bad: Deploy semantic view without testing
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales,
    customer_data AS customers
  )
  RELATIONSHIPS (
    sales.cust_id = customers.customer_id  -- Typo! Should be customer_id
  )
  DIMENSIONS (
    customer_name AS customers.name
      COMMENT = 'Customer name'
      SYNONYMS ('cust name')
  );
-- Deploy to production... Error: Column 'cust_id' not found!
-- Production outage, users can't query!
```
**Problem:** Production deployment failures; user impact; emergency rollback; untested DDL; wasted time; unprofessional; reputation damage

**Correct Pattern:**
```sql
-- Good: Validate before deploying

-- Step 1: Verify base tables exist and check column names
SHOW TABLES LIKE 'sales_data';
SHOW TABLES LIKE 'customer_data';

DESC TABLE sales_data;
DESC TABLE customer_data;

-- Step 2: Test join logic in standard SQL first
SELECT
  s.*,
  c.name
FROM sales_data s
JOIN customer_data c ON s.customer_id = c.customer_id  -- Verified column names!
LIMIT 10;

-- Step 3: Create semantic view in DEV first
CREATE OR REPLACE SEMANTIC VIEW dev_db.analytics.sales_analysis AS
  TABLES (
    sales_data AS sales,
    customer_data AS customers
  )
  RELATIONSHIPS (
    sales.customer_id = customers.customer_id  -- Correct column name
  )
  DIMENSIONS (
    customer_name AS customers.name
      COMMENT = 'Customer name'
      SYNONYMS ('cust name', 'client name')
  );

-- Step 4: Test semantic view with Cortex Analyst
-- Use Snowsight or Python SDK to test natural language queries
-- Example: "What is the total revenue by customer name?"

-- Step 5: Verify results
SELECT * FROM dev_db.analytics.sales_analysis LIMIT 10;

-- Step 6: Only deploy to production after successful validation
CREATE OR REPLACE SEMANTIC VIEW prod_db.analytics.sales_analysis AS
  -- Copy validated DDL here
  ...;
```
**Benefits:** No production failures; validated before deployment; user confidence; professional; tested thoroughly; reliable; no emergency fixes


**Anti-Pattern 5: Attempting to Define Verified Queries in DDL**
```sql
-- Bad: Trying to add verified queries in CREATE SEMANTIC VIEW DDL
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
      PRIMARY KEY (sale_id)
  )
  DIMENSIONS (
    sale_date AS sales.order_date
      COMMENT = 'Date of sale'
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Total sales revenue'
  )
  -- VERIFIED_QUERIES (  -- NOT SUPPORTED!
  --   'Monthly Revenue' AS
  --     QUESTION 'What is the total revenue by month?'
  --     SQL 'SELECT ...'
  -- );
-- Error: VERIFIED_QUERIES clause does not exist in DDL syntax!
```
**Problem:** DDL syntax limitation; verified queries unsupported in CREATE SEMANTIC VIEW; Cortex Analyst features blocked; workarounds needed; confusion; incomplete semantic model; reduced query accuracy

**Correct Pattern:**
```yaml
# File: sales_semantic_model.yaml
# Upload to Snowflake stage: @analytics.models/sales_semantic_model.yaml

name: sales_analysis
description: Sales analysis semantic model with verified queries

tables:
  - name: sales_data
    base_table:
      database: PROD
      schema: SALES
      table: SALES_FACT

    dimensions:
      - name: sale_date
        expr: order_date
        data_type: DATE
        description: Date of sale
        synonyms:
          - "order date"
          - "purchase date"

    metrics:
      - name: total_revenue
        expr: SUM(amount)
        description: Total sales revenue
        synonyms:
          - "revenue"
          - "sales total"

# Verified queries - ONLY supported in YAML format
verified_queries:
  - name: monthly_revenue
    question: What is the total revenue by month?
    sql: |
      SELECT
        DATE_TRUNC('MONTH', sale_date) AS month,
        SUM(total_revenue) AS revenue
      FROM sales_analysis
      GROUP BY month
      ORDER BY month DESC
    verified_at: 1701734400
    verified_by: analytics_team
    use_as_onboarding_question: true

  - name: top_products
    question: What are the top 10 products by revenue?
    sql: |
      SELECT
        product_name,
        SUM(total_revenue) AS revenue
      FROM sales_analysis
      GROUP BY product_name
      ORDER BY revenue DESC
      LIMIT 10
    verified_at: 1701734400
    verified_by: analytics_team
```

```sql
-- Then use CREATE SEMANTIC VIEW for DDL structure (without verified queries)
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
      PRIMARY KEY (sale_id)
  )
  DIMENSIONS (
    sale_date AS sales.order_date
      COMMENT = 'Date of sale'
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Total sales revenue'
  );

-- Verified queries remain in YAML file uploaded to stage
-- Cortex Analyst references YAML file for verified queries
-- See 106c-snowflake-semantic-views-integration for integration patterns
```
**Benefits:** Proper separation of concerns; verified queries supported; Cortex Analyst fully functional; improved query accuracy; maintainable; follows Snowflake architecture; clear documentation

**Reference:**
- See [Snowflake Semantic Model Specification](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec) for complete YAML format
- See `106c-snowflake-semantic-views-integration` for using verified queries with Cortex Analyst
- See `106c-snowflake-semantic-views-integration` for integration patterns


**Anti-Pattern 6: Using Template Characters in SYNONYMS or COMMENT**
```sql
-- Bad: & and other template characters in SYNONYMS
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
      PRIMARY KEY (sale_id)
  )
  DIMENSIONS (
    department AS sales.department
      COMMENT = 'Sales & Marketing department'  -- & causes CLI issues!
      SYNONYMS ('R&D', 'Sales & Marketing', 'S&M')  -- & interpreted as template variable!
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Revenue for <%REGION%>'  -- <% %> are SnowSQL variables!
  );
-- Snowflake CLI error: "undefined variable 'D'" or similar cryptic message
-- Deployment fails with confusing error, hard to debug!
```
**Problem:** Snowflake CLI (`snow sql`) interprets `&` as template variable prefix; SnowSQL interprets `<%` and `%>` as variable delimiters; deployment fails with cryptic errors; hard to debug; wasted time; blocks CI/CD pipelines

**Correct Pattern:**
```sql
-- Good: Avoid template characters, use alternatives
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
      PRIMARY KEY (sale_id)
  )
  DIMENSIONS (
    department AS sales.department
      COMMENT = 'Sales and Marketing department'  -- Use 'and' instead of '&'
      SYNONYMS ('R and D', 'Research and Development', 'Sales and Marketing')
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Revenue by region'  -- Plain text, no template syntax
  );
-- Deploys successfully via CLI, Snowsight, and CI/CD pipelines!
```
**Benefits:** CLI compatible; no deployment errors; CI/CD friendly; clear error-free execution; professional; maintainable

**Characters to Avoid:**
- `&` - Snowflake CLI template variable prefix
- `<%` and `%>` - SnowSQL variable delimiters
- `{{` and `}}` - Common templating syntax (Jinja2, dbt)

**Alternatives:**
- **`R&D`** - Use `R and D` or `Research and Development` instead
- **`Sales & Marketing`** - Use `Sales and Marketing` instead
- **`P&L`** - Use `P and L` or `Profit and Loss` instead
- **`M&A`** - Use `M and A` or `Mergers and Acquisitions` instead

## Post-Execution Checklist

- [ ] All semantic view blocks present: TABLES, RELATIONSHIPS, DIMENSIONS, METRICS
- [ ] TABLES block declares all base tables with unique aliases
- [ ] RELATIONSHIPS block declares all join paths between tables
- [ ] DIMENSIONS block uses correct mapping: `logical_name AS physical_column`
- [ ] No CAST or transformation functions in DIMENSIONS block
- [ ] METRICS block uses simple aggregates (COUNT, SUM, AVG, MIN, MAX)
- [ ] All dimensions and metrics have synonyms for natural language querying
- [ ] Comments provided for all dimensions and metrics explaining business meaning
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in SYNONYMS or COMMENT values
- [ ] Semantic view tested with Cortex Analyst natural language questions
- [ ] Base tables follow 100-snowflake-core naming conventions
- [ ] Related semantic views follow consistent naming: SEM_ prefix or MODEL_ prefix

## Validation

- Create semantic view with all blocks (TABLES, RELATIONSHIPS, DIMENSIONS, METRICS) and verify it compiles
- Test natural language questions with Cortex Analyst against the semantic view
- Verify DIMENSIONS block uses correct mapping format: `logical_name AS physical_column`
- Confirm RELATIONSHIPS block uses correct syntax with `identifier` and `references` keywords
- Validate synonyms are comprehensive for all dimensions and metrics (3-5 per entity)
- Check that METRICS use simple aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- Ensure no CAST, DATE_TRUNC, or transformation functions in DIMENSIONS block

## Output Format Examples

```sql
-- Semantic view definition with all required blocks
CREATE OR REPLACE SEMANTIC VIEW SEM_ASSET_PERFORMANCE
  AS
    SEMANTIC CATEGORY = 'Energy Grid Analytics'
    COMMENT = 'Semantic view for asset performance analysis including failure rates, maintenance costs, and asset metadata'
    TABLES (
      assets (ALIAS = asset) (COMMENT = 'Grid assets including transformers, substations, and distribution lines'),
      failure_events (ALIAS = failure) (COMMENT = 'Asset failure events with timestamps and costs'),
      maintenance_logs (ALIAS = maint) (COMMENT = 'Preventive and corrective maintenance records')
    )
    RELATIONSHIPS (
      asset.asset_id = failure.asset_id identifier = 'asset_failure_rel',
      asset.asset_id = maint.asset_id identifier = 'asset_maintenance_rel'
    )
    DIMENSIONS (
      asset.asset_id AS asset_id
        WITH SYNONYMS ('equipment ID', 'transformer ID', 'asset number')
        COMMENT = 'Unique identifier for grid assets',
      asset.asset_type AS asset_type
        WITH SYNONYMS ('equipment type', 'asset category')
        COMMENT = 'Type of asset: TRANSFORMER, SUBSTATION, DISTRIBUTION_LINE',
      asset.install_date AS install_date
        WITH SYNONYMS ('installation date', 'commissioned date')
        COMMENT = 'Date the asset was installed',
      failure.failure_time AS failure_timestamp
        WITH SYNONYMS ('failure date', 'breakdown time', 'outage time')
        COMMENT = 'Timestamp when failure occurred'
    )
    METRICS (
      asset.asset_count AS COUNT(DISTINCT asset_id)
        WITH SYNONYMS ('number of assets', 'total assets', 'equipment count')
        COMMENT = 'Total number of unique assets',
      failure.failure_count AS COUNT(*)
        WITH SYNONYMS ('number of failures', 'total failures', 'breakdown count')
        COMMENT = 'Total number of failure events',
      failure.avg_repair_cost AS AVG(repair_cost)
        WITH SYNONYMS ('average repair cost', 'mean repair cost')
        COMMENT = 'Average cost to repair asset failures',
      maint.total_maintenance_cost AS SUM(maintenance_cost)
        WITH SYNONYMS ('total maintenance spend', 'maintenance expenses')
        COMMENT = 'Sum of all maintenance costs'
    );

-- Test the semantic view with Cortex Analyst
SELECT *
FROM TABLE(ANALYST_SEMANTIC_VIEW_QUERY(
  'SEM_ASSET_PERFORMANCE',
  'What is the average repair cost by asset type?'
));
```

## References

### Internal Documentation
- **106a-snowflake-semantic-views-advanced:** Anti-patterns, validation rules, quality checks
- **106b-snowflake-semantic-views-querying:** Query patterns using SEMANTIC_VIEW() function
- **106c-snowflake-semantic-views-integration:** Integration with Cortex Analyst and Agents
- **100-snowflake-core:** DDL fundamentals and naming conventions
- **107-snowflake-security-governance:** Masking and row access policies

### External Documentation
- [Snowflake Semantic Views Documentation](https://docs.snowflake.com/en/user-guide/semantic-views) - Official semantic view syntax and examples
- [Cortex Analyst with Semantic Views](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Using semantic views for natural language queries
- [Semantic View Best Practices](https://docs.snowflake.com/en/user-guide/semantic-views-best-practices) - Guidelines for building effective semantic models

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

## Prerequisites Validation

Before creating semantic views, verify your environment meets requirements.

### Prerequisites Checklist

- [ ] Snowflake account has Cortex Analyst capability enabled (for NLQ usage)
- [ ] Base tables/views for semantic layer exist and are populated
- [ ] Required permissions granted (CREATE SEMANTIC VIEW, SELECT on source tables)
- [ ] Understanding of business metrics and grain for semantic modeling
- [ ] Warehouse available for query execution

### Verification Commands

**Check Cortex Availability:**
```sql
-- Verify Cortex features available (for Cortex Analyst integration)
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;
```

**Check Semantic View Generator Availability:**
```sql
-- Check account capabilities for Generator
SELECT SYSTEM$GET_ACCOUNT_CAPABILITIES() AS capabilities;

-- Alternative: Check via Snowsight UI
-- Navigate to: Data, then Databases, then [Your Database], then [Schema]
-- Look for "Generate Semantic View" button on table context menu
```

**Verify Base Tables:**
```sql
-- Check source tables exist and have data
SELECT
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    ROW_COUNT
FROM {DATABASE}.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = '{SCHEMA}'
  AND TABLE_TYPE = 'BASE TABLE';

-- Check table structure for semantic view candidates
DESCRIBE TABLE {DATABASE}.{SCHEMA}.{TABLE};

-- Identify columns for FACTS vs DIMENSIONS
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COMMENT
FROM {DATABASE}.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '{SCHEMA}'
  AND TABLE_NAME = '{TABLE}'
ORDER BY ORDINAL_POSITION;
```

**Verify Semantic View Creation Permissions:**
```sql
-- Check you can create semantic views in target schema
SHOW GRANTS ON SCHEMA {DATABASE}.{SCHEMA};

-- Required grants:
-- - CREATE SEMANTIC VIEW on schema
-- - SELECT on source tables
-- - USAGE on database and schema

-- Verify role has necessary privileges
SELECT
    CURRENT_ROLE() AS current_role,
    CURRENT_DATABASE() AS current_database,
    CURRENT_SCHEMA() AS current_schema;
```

## Related Rules

**Closely Related** (consider loading together):
- `106a-snowflake-semantic-views-advanced` - Anti-patterns, validation rules, quality checks, compliance requirements
- `106b-snowflake-semantic-views-querying` - Query patterns using SEMANTIC_VIEW() function, result processing
- `106c-snowflake-semantic-views-integration` - Integration with Cortex Analyst, Cortex Agents, and troubleshooting

**Sometimes Related** (load if specific scenario):
- `115-snowflake-cortex-agents-core` - When configuring semantic views as tools for Cortex Agents
- `103-snowflake-performance-tuning` - When optimizing base tables that semantic views reference

**Complementary** (different aspects of same domain):
- `100-snowflake-core` - For DDL fundamentals and object naming conventions
- `107-snowflake-security-governance` - For masking policies and row access policies on semantic views
