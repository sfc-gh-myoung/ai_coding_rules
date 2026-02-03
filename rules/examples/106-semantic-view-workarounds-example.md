# 106 Example: Semantic View Dimension Workarounds

> **EXAMPLE FILE** - Reference implementation for `106-snowflake-semantic-views-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 106-snowflake-semantic-views-core.md
**Demonstrates:** Correct patterns for semantic view dimensions when complex expressions are needed
**Use When:** Creating semantic views that require DATE_TRUNC, CASE, CAST, or other transformations
**Version:** 1.0
**Last Validated:** 2026-01-27

## Prerequisites

- [ ] Base table(s) exist with raw data
- [ ] Understanding of required transformations for analysis
- [ ] Snowflake account with semantic view creation privileges

## Implementation

### Anti-Pattern: Complex Expressions in DIMENSIONS (NOT ALLOWED)

```sql
-- BAD: Complex transformations in DIMENSIONS
-- This will FAIL with syntax errors!
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

### Correct Pattern 1: Simple Column References Only

```sql
-- GOOD: Simple columns from base tables
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_data AS sales
  )
  DIMENSIONS (
    order_date AS sales.order_date
      COMMENT = 'Date of sale'
      SYNONYMS ('sale date', 'order day', 'purchase date'),
    amount AS sales.amount
      COMMENT = 'Sale amount in USD'
      SYNONYMS ('price', 'revenue', 'sale value')
  )
  METRICS (
    monthly_revenue AS SUM(sales.amount)
      COMMENT = 'Revenue by month'
      SYNONYMS ('monthly sales')
  );
```

### Correct Pattern 2: Pre-compute in Base View

```sql
-- Step 1: Create enriched view with pre-computed transformations
CREATE OR REPLACE VIEW sales_enriched AS
SELECT
  -- Original columns
  order_id,
  customer_id,
  order_date,
  amount,
  product_id,
  -- Pre-computed transformations (do complex logic HERE)
  DATE_TRUNC('MONTH', order_date) AS sale_month,
  DATE_TRUNC('QUARTER', order_date) AS sale_quarter,
  CASE 
    WHEN amount > 1000 THEN 'High'
    WHEN amount > 100 THEN 'Medium'
    ELSE 'Low' 
  END AS revenue_category,
  CASE 
    WHEN amount > 0 THEN 'Revenue'
    ELSE 'Refund'
  END AS transaction_type
FROM sales_data;

-- Step 2: Create semantic view using simple column references
CREATE OR REPLACE SEMANTIC VIEW sales_analysis AS
  TABLES (
    sales_enriched AS sales
  )
  DIMENSIONS (
    sale_month AS sales.sale_month  -- Simple column reference
      COMMENT = 'Month of sale (truncated)'
      SYNONYMS ('month', 'sales month', 'order month'),
    sale_quarter AS sales.sale_quarter  -- Simple column reference
      COMMENT = 'Quarter of sale'
      SYNONYMS ('quarter', 'fiscal quarter'),
    revenue_category AS sales.revenue_category  -- Simple column reference
      COMMENT = 'Revenue category (High/Medium/Low)'
      SYNONYMS ('category', 'revenue tier', 'amount tier'),
    transaction_type AS sales.transaction_type  -- Simple column reference
      COMMENT = 'Transaction type (Revenue/Refund)'
      SYNONYMS ('type', 'txn type')
  )
  METRICS (
    total_revenue AS SUM(sales.amount)
      COMMENT = 'Total sales revenue'
      SYNONYMS ('revenue', 'sales', 'total sales'),
    order_count AS COUNT(sales.order_id)
      COMMENT = 'Number of orders'
      SYNONYMS ('orders', 'count', 'transaction count')
  );
```

### Anti-Pattern: Missing Equals Sign in COMMENT

```sql
-- BAD: COMMENT without equals sign
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

### Correct Pattern: COMMENT with Equals Sign

```sql
-- GOOD: COMMENT = 'text' (with equals sign)
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

### Anti-Pattern: Not Validating DDL Before Deployment

```sql
-- BAD: Deploying without testing
CREATE OR REPLACE SEMANTIC VIEW my_view AS ...;
-- Immediately used by Cortex Analyst -> Silent failures!
```

### Correct Pattern: Validate Before Deployment

```sql
-- Step 1: Compile-only check
CREATE OR REPLACE SEMANTIC VIEW my_view AS
  TABLES (
    sales_enriched AS sales
  )
  DIMENSIONS (
    sale_month AS sales.sale_month
      COMMENT = 'Month of sale'
  );

-- Step 2: Verify view was created
SHOW SEMANTIC VIEWS LIKE 'my_view';

-- Step 3: Verify dimensions are correct
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW my_view;

-- Step 4: Test querying the view
SELECT * FROM TABLE(SEMANTIC_VIEW('my_view')) LIMIT 5;

-- Step 5: Test with Cortex Analyst (if applicable)
-- Use semantic_view_optimization skill for testing prompts
```

## Validation

```sql
-- Verify semantic view exists
SHOW SEMANTIC VIEWS LIKE 'sales_analysis';
-- Expected: View listed with correct schema

-- Verify dimensions are all simple column references
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW sales_analysis;
-- Expected: All dimensions show simple column mappings

-- Verify metrics are defined correctly
SHOW SEMANTIC METRICS FOR SEMANTIC VIEW sales_analysis;
-- Expected: Metrics show aggregate functions

-- Test data access
SELECT * FROM TABLE(SEMANTIC_VIEW('sales_analysis')) LIMIT 10;
-- Expected: Data returned without errors
```

**Expected Results:**
- Semantic view creates without syntax errors
- All dimensions use simple column references (no functions)
- All COMMENTs use `=` syntax
- SHOW SEMANTIC DIMENSIONS shows correct mappings
- Queries against the view return data successfully
- Cortex Analyst can parse and use the view for natural language queries
