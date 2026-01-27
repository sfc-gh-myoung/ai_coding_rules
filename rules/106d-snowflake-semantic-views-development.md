# Snowflake Semantic Views: Development Workflows

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:semantic-generator, kw:vqr
**Keywords:** VQR, verified queries, Generator workflow, iterative development, YAML semantic model, semantic model file, onboarding questions, development workflow, verified query repository, semantic view generator
**TokenBudget:** ~3050
**ContextTier:** Medium
**Depends:** 106-snowflake-semantic-views-core.md

## Scope

**What This Rule Covers:**
Development workflows for Semantic Views including the Semantic View Generator tool, Verified Query Repository (VQR) for YAML semantic models, and iterative refinement patterns.

**When to Load This Rule:**
- Using the Semantic View Generator tool
- Creating YAML semantic models with verified queries
- Implementing VQR for improved Cortex Analyst accuracy
- Following iterative development workflows

**For DDL syntax and core patterns, see `106-snowflake-semantic-views-core.md`.**
**For Cortex Analyst integration and governance, see `106c-snowflake-semantic-views-integration.md`.**

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule
- **106-snowflake-semantic-views-core.md** - DDL fundamentals

### External Documentation
- [Semantic View Generator](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-generator) - Automated view creation
- [Verified Query Repository](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/verified-query-repository) - VQR documentation
- [Verified Query Suggestions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/verified-query-suggestions) - AI-suggested queries

### Related Rules
- **106c-snowflake-semantic-views-integration.md** - Cortex Analyst integration, governance

## Contract

### Inputs and Prerequisites

- Base tables exist and are populated
- CREATE SEMANTIC VIEW privilege granted
- For VQR: Stage access for YAML file upload

### Mandatory

- Semantic View Generator (Snowsight UI or API)
- YAML semantic model format for VQR
- Iterative validation workflow

### Forbidden

- Deploying Generator output without validation
- Using physical table names in VQR SQL (must use `__logical_name`)
- Skipping testing phase

### Execution Steps

1. Use Generator for initial structure (if starting from scratch)
2. Validate Generator output against base table schema
3. Add WITH SYNONYMS for business terms
4. Add COMMENT clauses for documentation
5. Test with Cortex Analyst
6. For VQR: Create YAML model, upload to stage, test verified queries

### Output Format

- Validated `CREATE SEMANTIC VIEW` DDL
- YAML semantic model with VQR (when verified queries needed)

### Validation

- Generator output matches base table schema
- VQR SQL uses `__logical_name` syntax
- All verified queries return expected results

### Post-Execution Checklist

- [ ] Generator output validated before execution
- [ ] Column names verified against base table
- [ ] Synonyms added for key business terms
- [ ] VQR tested with Cortex Analyst (if applicable)
- [ ] Development workflow documented

## Verified Query Repository (VQR)

### What is VQR?

VQR is a YAML-only feature providing pre-verified question-SQL pairs. When users ask questions similar to verified queries, Cortex Analyst uses the verified SQL directly.

**Key Benefits:**
- Guaranteed accuracy for high-stakes questions
- Reduced SQL generation errors
- Faster response for common questions
- Onboarding questions for new users

### VQR Syntax Requirements

> **CRITICAL: Table Naming in VQR SQL**
> VQR SQL uses **logical table names** with a **double underscore prefix (`__`)**.
> - Reference tables as `__logical_name` (from `tables.name` in YAML)
> - Do NOT use physical table names (e.g., `DATABASE.SCHEMA.TABLE`)

**VQR YAML Structure:**
```yaml
verified_queries:
  - name: query_identifier
    question: "Natural language question?"
    sql: |
      SELECT column1, SUM(metric)
      FROM __logical_table_name     # CRITICAL: __ prefix + logical name
      WHERE condition
      GROUP BY column1
    verified_at: 1737590400         # Unix timestamp
    verified_by: team_name
    use_as_onboarding_question: true
```

**Complete VQR Example:**
```yaml
name: sales_semantic_model
description: Sales analytics with verified queries

tables:
  - name: sales_data                # Logical name becomes __sales_data in VQR
    base_table:
      database: ANALYTICS
      schema: CORE
      table: SALES_FACT             # Physical table (NOT used in VQR SQL)
    
    dimensions:
      - name: sale_date
        expr: order_date
        data_type: DATE
      - name: region
        expr: sales_region
        data_type: VARCHAR

    metrics:
      - name: total_revenue
        expr: SUM(amount)
      - name: order_count
        expr: COUNT(*)

verified_queries:
  - name: revenue_by_region
    question: "What is the total revenue by region?"
    sql: |
      SELECT region, SUM(total_revenue) AS revenue
      FROM __sales_data
      GROUP BY region
      ORDER BY revenue DESC
    verified_at: 1737590400
    verified_by: analytics_team
    use_as_onboarding_question: true

  - name: monthly_trend
    question: "Show me the monthly revenue trend"
    sql: |
      SELECT DATE_TRUNC('MONTH', sale_date) AS month, SUM(total_revenue) AS revenue
      FROM __sales_data
      GROUP BY month
      ORDER BY month
    verified_at: 1737590400
    verified_by: analytics_team
```

### Common VQR Mistakes

```yaml
# WRONG - Physical table name:
sql: SELECT * FROM ANALYTICS.CORE.SALES_FACT

# WRONG - Single underscore:
sql: SELECT * FROM _sales_data

# CORRECT - Double underscore + logical name:
sql: SELECT * FROM __sales_data
```

### VQR Deployment Workflow

**Step 1: Create YAML with verified queries**
```yaml
# sales_model.yaml
name: sales_analysis
tables:
  - name: sales_data
    base_table:
      database: PROD
      schema: ANALYTICS  
      table: SALES_FACT
    dimensions:
      - name: sale_date
        expr: order_date
        data_type: DATE
    metrics:
      - name: total_revenue
        expr: SUM(amount)

verified_queries:
  - name: monthly_revenue
    question: "What is total revenue by month?"
    sql: |
      SELECT DATE_TRUNC('MONTH', sale_date) AS month, SUM(total_revenue)
      FROM __sales_data
      GROUP BY month
    verified_at: 1737590400
    verified_by: data_team
```

**Step 2: Upload to stage**
```sql
CREATE STAGE IF NOT EXISTS PROD.ANALYTICS.SEMANTIC_MODELS;
PUT file:///path/to/sales_model.yaml @PROD.ANALYTICS.SEMANTIC_MODELS/;
LIST @PROD.ANALYTICS.SEMANTIC_MODELS/;
```

**Step 3: Test with Cortex Analyst**
```python
payload = {
    "semantic_model_file": "@PROD.ANALYTICS.SEMANTIC_MODELS/sales_model.yaml",
    "messages": [{"role": "user", "content": "What is total revenue by month?"}]
}
```

### Suggested Queries (Preview)

Snowflake provides AI-generated VQR suggestions:

**Snowsight Access:**
1. Navigate to AI & ML, then Cortex Analyst
2. Select semantic model, then Verified Queries tab
3. Click Review Suggestions

**API Access:**
```python
url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/suggestions"
payload = {
    "semantic_model_file": "@ANALYTICS.MODELS/model.yaml",
    "mode": "ca_requests_based",  # or "query_history_based"
    "limit": 10
}
```

### VQR Best Practices

**When to Add Verified Queries:**
- High-stakes business questions (revenue, KPIs)
- Frequently asked questions with poor accuracy
- Complex queries with specific business logic

**Design Guidelines:**
1. Use natural language questions matching user phrasing
2. Test SQL independently before adding to VQR
3. Include question variations
4. Set onboarding questions for new users
5. Update timestamps when data changes

## Semantic View Generator

### When to Use Generator

- Starting new semantic view from scratch
- Exploring unfamiliar database schemas
- Creating baseline views for refinement
- Rapid prototyping

### Generator Workflow

```sql
-- Step 1: Verify Generator availability
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Step 2: Use Generator via Snowsight or API
-- Generator analyzes table structure and suggests DDL

-- Step 3: Review generated DDL before execution
-- Generator produces CREATE SEMANTIC VIEW with:
-- - Inferred PRIMARY KEY from constraints
-- - Numeric columns as FACTS
-- - String/date columns as DIMENSIONS
-- - Common aggregations as METRICS

-- Step 4: Execute and validate
CREATE OR REPLACE SEMANTIC VIEW ...;
SHOW SEMANTIC VIEWS IN SCHEMA ...;
```

### Generator Limitations

- Cannot infer complex business logic
- May misclassify columns (review FACTS vs DIMENSIONS)
- Does not add synonyms automatically
- Cannot create relationships between views

### Post-Generation Refinement

- [ ] Verify PRIMARY KEY matches business grain
- [ ] Review FACTS classification (numeric measures)
- [ ] Review DIMENSIONS classification (categorical/temporal)
- [ ] Add WITH SYNONYMS for NLQ matching
- [ ] Add COMMENT clauses for documentation
- [ ] Test with Cortex Analyst queries

## Iterative Development Workflow

### Phase 1: Generate and Validate

```sql
-- Read base table structure
DESCRIBE TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- Create minimal semantic view
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
    sales.sold_date_sk AS SS_SOLD_DATE_SK
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE)
  );

-- Verify structure
SHOW SEMANTIC VIEWS LIKE 'SEM_STORE_SALES';
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW ...;
```

### Phase 2: Add Business Context

```sql
-- Add synonyms and comments
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
      WITH SYNONYMS ('store sales', 'retail transactions')
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE
      WITH SYNONYMS ('price', 'revenue', 'amount')
      COMMENT = 'Sales price per item'
  )
  ...
```

### Phase 3: Test with Cortex Analyst

```python
test_queries = [
    "What are the top 10 items by revenue?",
    "Show me total units sold by customer",
]

for query in test_queries:
    payload = {
        "semantic_view": "SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES",
        "messages": [{"role": "user", "content": query}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Query: {query}\nResponse: {response.json()}\n")
```

### Development Checklist

**Before creating:**
- [ ] Read base table with DESCRIBE TABLE
- [ ] Understand business grain and primary key
- [ ] Identify numeric columns for FACTS
- [ ] Identify categorical columns for DIMENSIONS

**During creation:**
- [ ] Use correct mapping: `logical_name AS physical_column`
- [ ] Follow clause order: TABLES, FACTS, DIMENSIONS, METRICS
- [ ] Add WITH SYNONYMS for business terms
- [ ] Use COMMENT = 'text' syntax

**After creation:**
- [ ] Verify with SHOW SEMANTIC VIEWS
- [ ] Test basic query with SEMANTIC_VIEW()
- [ ] Test Cortex Analyst NLQ queries
- [ ] Document view purpose

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Physical Table Names in VQR SQL

**Problem:** Writing VQR SQL with fully qualified physical table names instead of logical names.

**Why It Fails:** Cortex Analyst expects `__logical_name` syntax in VQR SQL. Physical table names cause query resolution failures and "table not found" errors.

**Correct Pattern:**
```yaml
# WRONG: Physical table name
verified_queries:
  - name: revenue_query
    sql: SELECT * FROM ANALYTICS.CORE.SALES_FACT

# CORRECT: Logical name with __ prefix
verified_queries:
  - name: revenue_query
    sql: SELECT * FROM __sales_data  # matches tables.name in YAML
```

### Anti-Pattern 2: Deploying Generator Output Without Validation

**Problem:** Executing Generator-produced DDL directly without reviewing column classifications.

**Why It Fails:** Generator may misclassify columns (e.g., numeric IDs as FACTS instead of DIMENSIONS). Incorrect classifications cause wrong aggregations and misleading query results.

**Correct Pattern:**
```sql
-- WRONG: Execute Generator output blindly
CREATE SEMANTIC VIEW SEM_ORDERS ...;  -- Generator output, unreviewed

-- CORRECT: Review and validate before execution
-- Step 1: Check FACTS are actual measures (not IDs)
-- Step 2: Check DIMENSIONS are categorical/temporal
-- Step 3: Verify PRIMARY KEY matches business grain
-- Step 4: Add synonyms and comments
-- Step 5: Execute validated DDL
```

## Output Format Examples

```yaml
# Complete YAML semantic model with VQR
name: grid_operations
description: Grid operations semantic model

tables:
  - name: transformer_health
    base_table:
      database: PROD
      schema: GRID_DATA
      table: TRANSFORMER_TELEMETRY
    
    dimensions:
      - name: equipment_id
        expr: transformer_id
        data_type: VARCHAR
        synonyms: ["transformer ID", "unit ID"]
      - name: reading_time
        expr: timestamp
        data_type: TIMESTAMP

    metrics:
      - name: avg_load
        expr: AVG(load_kw)
        synonyms: ["average load", "mean power"]

verified_queries:
  - name: high_load_transformers
    question: "Which transformers have high load?"
    sql: |
      SELECT equipment_id, AVG(load_kw) AS avg_load
      FROM __transformer_health
      GROUP BY equipment_id
      HAVING AVG(load_kw) > 80
      ORDER BY avg_load DESC
    verified_at: 1737590400
    verified_by: grid_ops_team
    use_as_onboarding_question: true
```
