# Create Semantic Views via dbt-snowflake Native Package

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**Keywords:** dbt, semantic view, Snowflake, dbt_semantic_view, materialization, Cortex Analyst, YAML, semantic model, dbt models, analytics, business intelligence, data modeling
**TokenBudget:** ~5100
**ContextTier:** High
**Depends:** 950-dbt-core.md, 200-python-core.md

## Purpose

Guide creation of Snowflake semantic views using the dbt-snowflake native integration through the `dbt_semantic_view` package to materialize semantic views as native dbt models with version control, CI/CD integration, and lineage tracking.

## Scope

Creating Snowflake semantic views through dbt using the `dbt_semantic_view` package for analytics and Cortex Agent integration

## References

### Related Rules
- `200-python-core.md` - Python development standards for dbt projects
- `100-snowflake-core.md` - Snowflake SQL best practices
- `106-snowflake-semantic-views-core.md` - Semantic view query patterns

### External Documentation
- [dbt_semantic_view Package](https://github.com/Snowflake-Labs/dbt_semantic_view) - Official package documentation
- [Snowflake Semantic Views](https://docs.snowflake.com/en/user-guide/semantic-views) - Snowflake documentation
- [dbt Materializations](https://docs.getdbt.com/docs/build/materializations) - dbt materialization concepts
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Integration with semantic views

## Contract

### Inputs and Prerequisites
- Snowflake account with semantic view support
- dbt 1.x+ installed with Snowflake adapter
- Snowflake warehouse available for dbt execution
- dbt_semantic_view package installed (via packages.yml)
- Base dbt models exist for all tables to include
- Primary keys identified for all tables (verify with `DESCRIBE TABLE <table_name>` or `SHOW PRIMARY KEYS IN TABLE <table_name>`)
- Relationships (foreign keys) mapped between tables
- dbt_semantic_view package version identified

### Mandatory
- MUST create semantic views through dbt using `dbt_semantic_view` package, never direct DDL
- MUST reference base models with `{{ ref() }}` and `{{ source() }}` for lineage tracking
- MUST add inline comments with COMMENT clauses (persist_docs not supported)
- MUST define primary keys for all tables in the semantic view
- MUST use standard SQL only (CASE statements, no COUNT_IF or RATIO_TO_REPORT)
- MUST test semantic views with SEMANTIC_VIEW() function before deployment
- Time columns are regular dimensions, not a separate TIME_DIMENSIONS clause

### Forbidden
- Direct DDL creation of semantic views
- TIME_DIMENSIONS clause
- COUNT_IF or RATIO_TO_REPORT functions
- Table qualification in SEMANTIC_VIEW() queries
- Skipping primary key definitions

### Execution Steps
1. **[~2 min]** Add dbt_semantic_view package to packages.yml and run `dbt deps`
2. **[~10 min]** Analyze existing dbt models to identify tables, relationships, dimensions, and metrics
3. **[~5 min]** Create semantic view model file in models/ directory with `semantic_view` materialization
4. **[~5 min]** Define TABLES section with `ref()` or `source()` and PRIMARY KEY for each table
5. **[~5 min]** Define RELATIONSHIPS section for foreign key connections between tables
6. **[~10 min]** Define DIMENSIONS section with business-friendly column aliases and synonyms
7. **[~10 min]** Define METRICS section with aggregation expressions and CASE statements for ratios
8. **[~5 min]** Add COMMENT clauses for all tables, relationships, dimensions, and metrics
9. **[~2 min]** Build semantic view with `dbt run --select model_name`
10. **[~5 min]** Test with `SEMANTIC_VIEW()` queries in Snowflake
11. **[~10 min]** Add documentation to schema.yml and integrate into CI/CD pipeline

**Total estimated time:** ~70 minutes for a new semantic view (less for simple single-table views)

### Output Format
dbt model SQL file with semantic_view materialization; SHOW SEMANTIC VIEWS output; test query results; schema.yml documentation

### Validation

**Success Checks:**
- `dbt run --select <model_name>` completes without errors
- `SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>` shows the created view
- `DESCRIBE SEMANTIC VIEW <database>.<schema>.<view_name>` returns structure
- Test query returns expected results: `SELECT * FROM SEMANTIC_VIEW(<view_name> DIMENSIONS <dim> METRICS <metric>) LIMIT 10`
- Downstream models can reference with `{{ ref('<model_name>') }}`

**Negative Tests:**
- Using TIME_DIMENSIONS clause should fail with syntax error
- Using COUNT_IF or RATIO_TO_REPORT should fail with syntax error
- Missing PRIMARY KEY should fail with validation error
- Table-qualified dimensions in queries should fail with syntax error

### Post-Execution Checklist
- [ ] dbt_semantic_view package added to packages.yml
- [ ] Package installed via dbt deps
- [ ] Semantic view model created in models/ directory
- [ ] TABLES section defined with PRIMARY KEY for each table
- [ ] RELATIONSHIPS section defined for foreign keys (if multi-table)
- [ ] DIMENSIONS section defined with business-friendly names
- [ ] METRICS section defined with aggregation expressions
- [ ] COMMENT clauses added for all components
- [ ] Model built successfully with dbt run
- [ ] Semantic view exists in Snowflake (verified with SHOW SEMANTIC VIEWS)
- [ ] Test queries executed successfully with SEMANTIC_VIEW() function
- [ ] Documentation added to schema.yml
- [ ] Downstream models can reference semantic view (if applicable)
- [ ] CI/CD pipeline updated to build semantic views

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Direct DDL Instead of dbt**
```sql
-- Bad: Creating semantic view with direct DDL
CREATE OR REPLACE SEMANTIC VIEW my_view AS ...
```
**Problem:** No version control, no lineage tracking, no CI/CD integration, manual deployment.

**Correct Pattern:**
```sql
-- Good: dbt model with semantic_view materialization
{{
  config(
    materialized='semantic_view',
    tags=['semantic_view']
  )
}}

TABLES (
  sales AS {{ ref('fct_sales') }}
    PRIMARY KEY (sale_id)
)
...
```
**Benefits:** Version control, dbt lineage, CI/CD integration, reproducible builds.

**Anti-Pattern 2: Using TIME_DIMENSIONS Clause**
```sql
-- Bad: TIME_DIMENSIONS clause does not exist
TIME_DIMENSIONS (
  created_date,
  updated_date
)
```
**Problem:** Syntax error, TIME_DIMENSIONS is not a valid clause in semantic view DDL.

**Correct Pattern:**
```sql
-- Good: Time columns as regular dimensions
DIMENSIONS (
  sales.created_date AS created_date
    COMMENT = 'Date when record was created',
  sales.updated_date AS updated_date
    COMMENT = 'Last update timestamp'
)
```
**Benefits:** Valid syntax, time columns accessible for filtering and grouping.

**Anti-Pattern 3: Using Non-Standard SQL Functions**
```sql
-- Bad: COUNT_IF and RATIO_TO_REPORT do not exist
METRICS (
  won_leads AS COUNT_IF(status = 'Won'),
  win_rate AS RATIO_TO_REPORT(won_leads)
)
```
**Problem:** Syntax error, these functions are not supported in semantic view metrics.

**Correct Pattern:**
```sql
-- Good: Standard SQL with CASE statements
METRICS (
  won_leads AS SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END)
    COMMENT = 'Number of won leads',
  
  win_rate AS CASE 
    WHEN SUM(total_leads) > 0 
    THEN (SUM(won_leads)::FLOAT / SUM(total_leads)) * 100
    ELSE 0 
  END
    COMMENT = 'Win rate as percentage'
)
```
**Benefits:** Valid syntax, handles division by zero, clear business logic.

**Anti-Pattern 4: Table Qualification in Queries**
```sql
-- Bad: Using table prefix in SEMANTIC_VIEW() query
SELECT * FROM SEMANTIC_VIEW(
  my_semantic_view
  DIMENSIONS salesforce_leads.region
  METRICS salesforce_leads.total_leads
)
```
**Problem:** Syntax error, dimensions and metrics should not be table-qualified in queries.

**Correct Pattern:**
```sql
-- Good: No table qualification in query
SELECT * FROM SEMANTIC_VIEW(
  my_semantic_view
  DIMENSIONS region
  METRICS total_leads
)
```
**Benefits:** Valid syntax, cleaner query interface, matches semantic view design.

## Examples

**dbt Model File (models/sv_sales_performance.sql):**
```sql
{{
  config(
    materialized='semantic_view',
    tags=['semantic_view', 'sales']
  )
}}

TABLES (
  sales AS {{ ref('fct_sales_performance') }}
    PRIMARY KEY (performance_key)
    WITH SYNONYMS = ('revenue', 'transactions')
    COMMENT = 'Sales performance fact table'
)

DIMENSIONS (
  sales.product_category AS product_category
    WITH SYNONYMS = ('product_line', 'category')
    COMMENT = 'Product category classification',
  
  sales.region AS region
    WITH SYNONYMS = ('territory', 'geographic_region')
    COMMENT = 'Sales region',
  
  sales.sales_date AS sales_date
    WITH SYNONYMS = ('transaction_date', 'order_date')
    COMMENT = 'Date of sales activity'
)

METRICS (
  total_revenue AS SUM(sales.total_notion_revenue)
    COMMENT = 'Total revenue from all sources',
  
  total_orders AS SUM(sales.total_notion_orders)
    COMMENT = 'Total number of orders',
  
  average_order_value AS AVG(sales.avg_order_value)
    COMMENT = 'Average order value'
)

COMMENT = 'Sales performance analytics combining Notion and Salesforce data'
```

**Test Query:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  <database>.<schema>.sv_sales_performance
  DIMENSIONS product_category, region
  METRICS total_revenue, total_orders
)
WHERE region IS NOT NULL
ORDER BY total_revenue DESC
LIMIT 10;
```

**Verification Commands:**
```bash
# Build semantic view
dbt run --select sv_sales_performance

# Verify in Snowflake
SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>;
DESCRIBE SEMANTIC VIEW <database>.<schema>.sv_sales_performance;
```

## Setup and Installation

Add `Snowflake-Labs/dbt_semantic_view` to `packages.yml`, run `dbt deps`, then verify with `dbt ls --resource-type materialization`. Before creating a semantic view, identify base models, their primary keys, foreign key relationships, and target dimensions/metrics. See [dbt_semantic_view Package](https://github.com/Snowflake-Labs/dbt_semantic_view) for detailed setup.

## Key Components

- **TABLES** — Syntax: `<name> AS {{ ref('<model>') }} PRIMARY KEY (<col>)`. Required: `PRIMARY KEY`. Optional: `WITH SYNONYMS`, `COMMENT`. One entry per table.
- **RELATIONSHIPS** — Syntax: `<name> AS <table1>(<fk>) REFERENCES <table2>(<pk>)`. Required: FK and PK columns. Optional: `COMMENT`. Only for multi-table views.
- **DIMENSIONS** — Syntax: `<table>.<col> AS <dim_name>`. Required: Table-qualified column. Optional: `WITH SYNONYMS`, `COMMENT`. Time columns are regular dimensions.
- **METRICS** — Syntax: `<name> AS <aggregation_expr>`. Required: Aggregation expression. Optional: `COMMENT`. Use standard SQL: SUM, AVG, COUNT, CASE.

## Common Patterns

### Star Schema (Fact + Dimensions)
```sql
{{
  config(materialized='semantic_view')
}}

TABLES (
  facts AS {{ ref('fct_orders') }}
    PRIMARY KEY (order_id)
    COMMENT = 'Orders fact table',
  customers AS {{ ref('dim_customers') }}
    PRIMARY KEY (customer_id)
    COMMENT = 'Customer dimension'
)

RELATIONSHIPS (
  order_customer AS facts(customer_id) REFERENCES customers(customer_id)
    COMMENT = 'Link orders to customers'
)

DIMENSIONS (
  customers.customer_name AS customer_name
    COMMENT = 'Customer full name',
  facts.order_date AS order_date
    COMMENT = 'Date order was placed'
)

METRICS (
  total_sales AS SUM(facts.order_amount)
    COMMENT = 'Total sales revenue',
  order_count AS COUNT(facts.order_id)
    COMMENT = 'Number of orders'
)
```

### Multi-Table Pattern (3+ Tables)
```sql
{{
  config(materialized='semantic_view', tags=['semantic_view', 'sales'])
}}

TABLES (
  orders AS {{ ref('fct_orders') }}
    PRIMARY KEY (order_id)
    COMMENT = 'Orders fact table',
  customers AS {{ ref('dim_customers') }}
    PRIMARY KEY (customer_id)
    COMMENT = 'Customer dimension',
  products AS {{ ref('dim_products') }}
    PRIMARY KEY (product_id)
    COMMENT = 'Product dimension',
  regions AS {{ ref('dim_regions') }}
    PRIMARY KEY (region_id)
    COMMENT = 'Geographic region dimension'
)

RELATIONSHIPS (
  order_customer AS orders(customer_id) REFERENCES customers(customer_id)
    COMMENT = 'Link orders to customers',
  order_product AS orders(product_id) REFERENCES products(product_id)
    COMMENT = 'Link orders to products',
  customer_region AS customers(region_id) REFERENCES regions(region_id)
    COMMENT = 'Link customers to regions (chained relationship)'
)

DIMENSIONS (
  customers.customer_name AS customer_name
    WITH SYNONYMS = ('buyer', 'client')
    COMMENT = 'Customer full name',
  products.product_name AS product_name
    WITH SYNONYMS = ('item', 'sku_name')
    COMMENT = 'Product display name',
  products.category AS product_category
    WITH SYNONYMS = ('product_line', 'department')
    COMMENT = 'Product category',
  regions.region_name AS region
    WITH SYNONYMS = ('territory', 'geographic_area')
    COMMENT = 'Sales region name',
  orders.order_date AS order_date
    WITH SYNONYMS = ('purchase_date', 'transaction_date')
    COMMENT = 'Date order was placed'
)

METRICS (
  total_revenue AS SUM(orders.order_amount)
    COMMENT = 'Total revenue from orders',
  order_count AS COUNT(orders.order_id)
    COMMENT = 'Number of orders',
  avg_order_value AS AVG(orders.order_amount)
    COMMENT = 'Average order value',
  unique_customers AS COUNT(DISTINCT orders.customer_id)
    COMMENT = 'Number of unique customers'
)

COMMENT = 'Multi-table sales analytics with customer, product, and region dimensions'
```

**Test Query (3+ tables):**
```sql
SELECT * FROM SEMANTIC_VIEW(
  <database>.<schema>.sv_sales_multi
  DIMENSIONS customer_name, product_category, region
  METRICS total_revenue, order_count
)
WHERE region IS NOT NULL
ORDER BY total_revenue DESC
LIMIT 20;
```

### Complex Metrics with CASE
```sql
METRICS (
  win_rate_pct AS 
    CASE 
      WHEN SUM(total_opportunities) > 0 
      THEN (SUM(won_opportunities)::FLOAT / SUM(total_opportunities)) * 100
      ELSE 0 
    END
    COMMENT = 'Win rate as percentage',
  conditional_count AS SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END)
    COMMENT = 'Count of active records'
)
```

## Design Principles

- **Naming:** Model files as `sv_<domain>_<subject>.sql`; use business-friendly names for tables, dimensions, metrics

> **Note:** dbt model files follow dbt ecosystem conventions (`sv_<domain>_<subject>.sql`) and are exempt from the `NN_<schema>_<operation>.sql` deployment script naming convention defined in `102a` and `130`.
- **Synonyms:** Add for abbreviations, plural/singular variants, and business vs technical terms
- **Comments:** Required on all TABLES, RELATIONSHIPS, DIMENSIONS, METRICS, and the semantic view itself
- **Performance:** Materialize base models as tables or incremental; add clustering keys for large datasets
- **Documentation:** Use inline COMMENT clauses (`persist_docs` not supported); add schema.yml entries

## Performance Considerations

### Base Model Materialization

For semantic views over large datasets (>1M rows), base model materialization directly impacts query performance:

- **<100K rows** — Recommended: `view`. Acceptable latency for small datasets.
- **100K–1M rows** — Recommended: `table`. Materialized for consistent performance.
- **>1M rows** — Recommended: `incremental`. Avoids full-table rebuild on each run.
- **>10M rows** — Recommended: `incremental` + clustering. Add `cluster_by` for frequently filtered columns.

```sql
-- Base model optimized for large semantic views
{{
  config(
    materialized='incremental',
    unique_key='order_id',
    cluster_by=['region', 'order_date'],
    on_schema_change='append_new_columns'
  )
}}

SELECT
    order_id,
    customer_id,
    region,
    order_date,
    order_amount
FROM {{ source('raw', 'orders') }}
{% if is_incremental() %}
WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
```

### Query Optimization

- Use `APPROX_COUNT_DISTINCT` instead of `COUNT(DISTINCT ...)` for metrics on large tables (>10M rows)
- Avoid metrics that require full-table scans without filters (add date range constraints)
- Test query performance with `EXPLAIN` before deploying:
  ```sql
  EXPLAIN
  SELECT * FROM SEMANTIC_VIEW(
    <database>.<schema>.<view_name>
    DIMENSIONS region, order_date
    METRICS total_revenue, order_count
  )
  WHERE order_date >= '2025-01-01';
  ```

### Monitoring Performance

```sql
-- Check query duration for semantic view queries
SELECT query_id, query_text, total_elapsed_time / 1000 AS duration_seconds,
       bytes_scanned / (1024*1024*1024) AS gb_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_text ILIKE '%SEMANTIC_VIEW%'
  AND start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY total_elapsed_time DESC
LIMIT 10;
```

**Performance Targets:**
- Simple queries (1-2 dimensions, 1-2 metrics): <2 seconds
- Complex queries (3+ dimensions, 3+ metrics): <10 seconds
- Full-scan queries (no filters): <30 seconds for tables up to 10M rows

## Testing and Deployment

1. Build: `dbt run --select <model>` (with deps: `dbt build --select +<model>`)
2. Verify: `SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>` and `DESCRIBE SEMANTIC VIEW <database>.<schema>.<view_name>`
3. Test query: `SELECT * FROM SEMANTIC_VIEW(<view> DIMENSIONS <dim> METRICS <metric>) LIMIT 10`
4. Document in `schema.yml` with description and `meta.type: semantic_view`
5. Note: `persist_docs` not supported; use inline COMMENT clauses in SQL

## Troubleshooting

### Error: "materialization not found"
**Cause:** Package not installed or not loaded
**Fix:**
```bash
dbt deps
dbt clean
dbt compile --select <model>
```

### Error: "PRIMARY KEY constraint failed"
**Cause:** Base table has duplicate values in primary key column
**Fix:**
- Add DISTINCT or GROUP BY to base model
- Use dbt tests to enforce uniqueness:
  ```yaml
  - name: fct_sales
    columns:
      - name: sale_id
        tests:
          - unique
          - not_null
  ```

### Error: "REFERENCES column not found"
**Cause:** Foreign key column doesn't exist or is misspelled
**Fix:** Check column names in base models with `DESCRIBE TABLE`

### Semantic view created but queries return unexpected results
**Cause:** Base model data quality issues
**Fix:**
- Add dbt tests to base models (not_null, relationships, accepted_values)
- Check for NULL values in key columns
- Validate data types match expectations

### Rollback Procedure

If a semantic view deployment fails or produces incorrect results, follow this rollback procedure:

**Step 1: Identify the failure scope**
```sql
-- Check if the semantic view exists in a broken state
SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>;
DESCRIBE SEMANTIC VIEW <database>.<schema>.<view_name>;
```

**Step 2: Drop the broken semantic view**
```sql
-- Remove the failed semantic view
DROP SEMANTIC VIEW IF EXISTS <database>.<schema>.<view_name>;

-- Verify removal
SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>;
```

**Step 3: Restore the previous version via dbt**
```bash
# Revert to the last known-good commit
git log --oneline models/sv_*.sql  # Find last good commit
git checkout <last-good-commit> -- models/<model_name>.sql

# Rebuild from the known-good version
dbt run --select <model_name>

# Verify restoration
# In Snowflake:
# SHOW SEMANTIC VIEWS IN SCHEMA <database>.<schema>;
# SELECT * FROM SEMANTIC_VIEW(<view_name> DIMENSIONS <dim> METRICS <metric>) LIMIT 5;
```

**Step 4: If no previous version exists (first deployment)**
```sql
-- Simply drop the semantic view and investigate
DROP SEMANTIC VIEW IF EXISTS <database>.<schema>.<view_name>;

-- Check base model data quality before retrying
SELECT COUNT(*), COUNT(DISTINCT <primary_key>) FROM <base_table>;
-- If counts differ, fix duplicates in base model first
```

**Step 5: Document the failure**
- Record what failed and why in the PR or issue tracker
- Add a dbt test to prevent recurrence if the failure was data-related
- Update the model if the failure was schema-related

## Integration with Cortex Agent

Once your semantic view is deployed, connect it to a Cortex Agent:

```sql
CREATE OR REPLACE AGENT <database>.agents.<agent_name>
  COMMENT = '<agent description>'
  FROM SPECIFICATION $$
  {
    "models": {"orchestration": "claude-4-sonnet"},
    "instructions": {
      "response": "Provide clear analytics insights",
      "orchestration": "Use the semantic view to answer questions"
    },
    "tools": [{
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "analytics_tool",
        "description": "Query semantic view for insights"
      }
    }],
    "tool_resources": {
      "analytics_tool": {
        "semantic_view": "<database>.<schema>.<semantic_view_name>",
        "execution_environment": {"type": "warehouse"}
      }
    }
  }
  $$;
```
