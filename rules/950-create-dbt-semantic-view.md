# Create Semantic Views via dbt-snowflake Native Package

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** dbt, semantic view, Snowflake, dbt_semantic_view, materialization, Cortex Analyst, YAML, semantic model, dbt models, analytics, business intelligence, data modeling
**TokenBudget:** ~3500
**ContextTier:** High
**Depends:** 200-python-core.md

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
- dbt project with base models (materialized as tables or views)
- Snowflake warehouse access
- Understanding of star schema design
- Business requirements for metrics and dimensions
- Primary keys identified for all tables (verify with `DESCRIBE TABLE <table_name>` or `SHOW PRIMARY KEYS IN TABLE <table_name>`)
- Relationships (foreign keys) mapped between tables
- dbt_semantic_view package version identified

### Mandatory
- dbt 1.x+
- Snowflake warehouse
- dbt_semantic_view package installed
- Base models with primary keys defined
- packages.yml file

**Essential Patterns:**
- **Always use dbt:** Create semantic views through dbt using `dbt_semantic_view` package, never direct DDL
- **Use ref() and source():** Reference base models with `{{ ref() }}` and `{{ source() }}` for lineage tracking
- **Add inline comments:** Document with COMMENT clauses (persist_docs not supported)
- **No TIME_DIMENSIONS:** Time columns are regular dimensions, not a separate clause
- **Standard SQL only:** Use CASE statements, no COUNT_IF or RATIO_TO_REPORT functions
- **Test thoroughly:** Query semantic views with SEMANTIC_VIEW() function before deployment

### Forbidden
- Direct DDL creation of semantic views
- TIME_DIMENSIONS clause
- COUNT_IF or RATIO_TO_REPORT functions
- Table qualification in SEMANTIC_VIEW() queries
- Skipping primary key definitions

### Execution Steps
1. Add dbt_semantic_view package to packages.yml and run dbt deps
2. Analyze existing dbt models to identify tables, relationships, dimensions, and metrics
3. Create semantic view model file in models/ directory with semantic_view materialization
4. Define TABLES section with ref() or source() and PRIMARY KEY for each table
5. Define RELATIONSHIPS section for foreign key connections between tables
6. Define DIMENSIONS section with business-friendly column aliases and synonyms
7. Define METRICS section with aggregation expressions and CASE statements for ratios
8. Add COMMENT clauses for all tables, relationships, dimensions, and metrics
9. Build semantic view with dbt run --select model_name
10. Test with SEMANTIC_VIEW() queries in Snowflake
11. Add documentation to schema.yml and integrate into CI/CD pipeline

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

## Output Format Examples

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
  my_db.my_schema.sv_sales_performance
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
SHOW SEMANTIC VIEWS IN SCHEMA my_db.my_schema;
DESCRIBE SEMANTIC VIEW my_db.my_schema.sv_sales_performance;
```

## Setup and Installation

Add `Snowflake-Labs/dbt_semantic_view` to `packages.yml`, run `dbt deps`, then verify with `dbt ls --resource-type materialization`. Before creating a semantic view, identify base models, their primary keys, foreign key relationships, and target dimensions/metrics. See [dbt_semantic_view Package](https://github.com/Snowflake-Labs/dbt_semantic_view) for detailed setup.

## Key Components

- **TABLES:** `<name> AS {{ ref('<model>') }} PRIMARY KEY (<col>) [WITH SYNONYMS = (...)] [COMMENT = '...']`
- **RELATIONSHIPS:** `<name> AS <table1>(<fk>) REFERENCES <table2>(<pk>) [COMMENT = '...']`
- **DIMENSIONS:** `<table>.<col> AS <dim_name> [WITH SYNONYMS = (...)] [COMMENT = '...']` — time columns are regular dimensions
- **METRICS:** `<name> AS <aggregation_expr> [COMMENT = '...']` — use standard SQL (SUM, AVG, COUNT, CASE)

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
- **Synonyms:** Add for abbreviations, plural/singular variants, and business vs technical terms
- **Comments:** Required on all TABLES, RELATIONSHIPS, DIMENSIONS, METRICS, and the semantic view itself
- **Performance:** Materialize base models as tables or incremental; add clustering keys for large datasets
- **Documentation:** Use inline COMMENT clauses (`persist_docs` not supported); add schema.yml entries

## Testing and Deployment

1. Build: `dbt run --select <model>` (with deps: `dbt build --select +<model>`)
2. Verify: `SHOW SEMANTIC VIEWS IN SCHEMA <db>.<schema>` and `DESCRIBE SEMANTIC VIEW <db>.<schema>.<view>`
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
