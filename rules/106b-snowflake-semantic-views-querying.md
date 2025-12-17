# Snowflake Semantic Views: Querying and Testing

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** window functions, dimension compatibility, testing, validation, TPC-DS, performance optimization, aliases, granularity, query semantic view, semantic view results, query patterns, result processing, SEMANTIC_VIEW function, query errors, dimension filters
**TokenBudget:** ~5750
**ContextTier:** High
**Depends:** rules/106-snowflake-semantic-views-core.md

## Purpose
Provide comprehensive guidance for querying Snowflake Semantic Views using the `SEMANTIC_VIEW()` function and validating semantic view implementations through systematic testing. Covers query syntax, dimension compatibility, window function metrics, WHERE clause usage, and performance optimization.

## Rule Scope

Querying semantic views after creation, testing patterns, validation strategies

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use SEMANTIC_VIEW() function** - `SELECT * FROM SEMANTIC_VIEW(view_name DIMENSIONS ... METRICS ...)`
- **Specify at least one clause** - DIMENSIONS, METRICS, or FACTS (one minimum required)
- **Cannot mix FACTS and METRICS** - Choose one or the other, can combine either with DIMENSIONS
- **Check dimension compatibility** - Use `SHOW SEMANTIC DIMENSIONS FOR METRIC metric_name`
- **Window function metrics** - Must return all PARTITION BY and ORDER BY dimensions
- **WHERE filters returned columns only** - Cannot filter on columns not in SELECT
- **Validate with base tables** - Compare semantic view results to direct table queries
- **Optimize base tables** - Semantic views are metadata, performance depends on underlying tables

**Quick Checklist:**
- [ ] Used SEMANTIC_VIEW() function (not direct SELECT)
- [ ] Specified at least one of: DIMENSIONS, METRICS, FACTS
- [ ] Did NOT combine FACTS and METRICS
- [ ] Checked dimension/metric compatibility with SHOW commands
- [ ] WHERE clause filters only returned columns
- [ ] Window function metrics include required dimensions
- [ ] Validated results against base table calculations
- [ ] Reviewed Query Profile for performance

## Contract

<contract>
<inputs_prereqs>
- Semantic view exists in DATABASE.SCHEMA (created via `CREATE SEMANTIC VIEW`)
- Understanding of DIMENSIONS, METRICS, and FACTS defined in semantic view
- Query privileges on semantic view and underlying base tables
</inputs_prereqs>

<mandatory>
- `SELECT * FROM SEMANTIC_VIEW(...)` query syntax
- `SHOW SEMANTIC DIMENSIONS/METRICS/FACTS` for structure inspection
- `SHOW SEMANTIC DIMENSIONS FOR METRIC` for compatibility checks
- Query Profile for performance analysis
- SnowCLI cortex analyst commands
</mandatory>

<forbidden>
- Direct SELECT from semantic view without SEMANTIC_VIEW() function
- Mixing FACTS and METRICS in same query
- Querying without specifying at least one of DIMENSIONS, METRICS, or FACTS
</forbidden>

<steps>
1. Inspect semantic view structure with SHOW commands
2. Identify dimensions compatible with metrics
3. Construct SEMANTIC_VIEW() query with proper clause combination
4. Apply WHERE filters on returned columns only
5. Validate results against base table queries
6. Review Query Profile for performance
</steps>

<output_format>
- Valid SEMANTIC_VIEW() SELECT statements
- Test queries comparing semantic vs direct table results
</output_format>

<validation>
- Query executes without errors
- Results match expected business logic
- Performance acceptable (check Query Profile)
- Dimension compatibility validated via SHOW commands
</validation>

<design_principles>
- **Function-based querying**: Use `SEMANTIC_VIEW()` function, not direct SELECT
- **Clause requirements**: Must specify at least ONE of DIMENSIONS, METRICS, or FACTS
- **Mutually exclusive**: Cannot combine FACTS and METRICS in same query
- **Dimension compatibility**: Not all dimensions work with all metrics - check granularity
- **Window function metrics**: Require returning PARTITION BY and ORDER BY dimensions
- **WHERE clause restrictions**: Can only filter on columns returned in query
- **Performance depends on base tables**: Semantic views are metadata - optimize underlying tables
- **Testing is mandatory**: Validate metrics match direct table calculations
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Combining FACTS and METRICS in Same Query**
```sql
-- Problem: Attempting to combine FACTS and METRICS
SELECT * FROM SEMANTIC_VIEW(my_view
  DIMENSIONS(orders.order_date),
  FACTS(orders.order_amount),
  METRICS(orders.total_revenue)
);
```
**Problem:** FACTS and METRICS are mutually exclusive - query fails with error "Cannot combine FACTS and METRICS".

**Correct Pattern:**
```sql
-- Query with FACTS only
SELECT * FROM SEMANTIC_VIEW(my_view
  DIMENSIONS(orders.order_date),
  FACTS(orders.order_amount)
);

-- Or query with METRICS only
SELECT * FROM SEMANTIC_VIEW(my_view
  DIMENSIONS(orders.order_date),
  METRICS(orders.total_revenue)
);
```
**Benefits:** Valid queries that execute successfully - choose FACTS for row-level data, METRICS for aggregated results.


**Anti-Pattern 2: Missing All Required Clauses**
```sql
-- Problem: Query without DIMENSIONS, METRICS, or FACTS
SELECT * FROM SEMANTIC_VIEW(my_view);
```
**Problem:** At least ONE of DIMENSIONS, METRICS, or FACTS required - query fails with error.

**Correct Pattern:**
```sql
-- Specify at least one clause
SELECT * FROM SEMANTIC_VIEW(my_view
  DIMENSIONS(orders.order_date, orders.customer_id)
);
```
**Benefits:** Valid query that returns dimension data.

## Post-Execution Checklist

**Querying:**
- [ ] Use SEMANTIC_VIEW() function with at least one of: DIMENSIONS, METRICS, or FACTS
- [ ] Cannot combine FACTS and METRICS in same query
- [ ] Check dimension compatibility with SHOW SEMANTIC DIMENSIONS FOR METRIC
- [ ] WHERE clause filters only columns returned in query
- [ ] Window function metrics include all required dimensions (PARTITION BY, ORDER BY)
- [ ] Aliases used for cleaner output column names
- [ ] Performance validated via Query Profile

**Testing:**
- [ ] Structure validated with SHOW commands
- [ ] Test queries executed successfully
- [ ] Results compared against direct base table queries
- [ ] Accuracy validation shows matching totals (semantic vs direct)
- [ ] Natural language queries tested with Cortex Analyst
- [ ] Query Profile reviewed for performance issues
- [ ] Base tables optimized (clustering, partitioning) if needed

## Validation
- **Success Checks:**
  - SEMANTIC_VIEW() queries execute without errors
  - Dimension/metric combinations are compatible (verified with SHOW commands)
  - WHERE filters only reference returned columns
  - Window function metrics include required dimensions
  - Results match direct base table calculations
  - Query Profile shows efficient execution (partition pruning, filter pushdown)
  - Cortex Analyst accepts queries and returns valid responses
- **Negative Tests:**
  - Combining FACTS and METRICS causes error
  - Omitting all clauses (no DIMENSIONS, METRICS, FACTS) causes error
  - Incompatible dimension/metric combinations cause error
  - Missing required dimensions for window metrics causes error
  - Filtering on non-returned columns causes error
  - Results diverge from base table calculations (indicates definition error)

## Output Format Examples

```sql
-- Query semantic view: <view_name>
-- Business question: <question being answered>
-- Expected result: <what output represents>

-- Step 1: Verify available dimensions and metrics
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW <database>.<schema>.<view_name>;
SHOW SEMANTIC METRICS FOR SEMANTIC VIEW <view_name>;

-- Step 2: Check dimension compatibility for target metric
SHOW SEMANTIC DIMENSIONS FOR METRIC <database>.<schema>.<view_name>.<metric_name>;

-- Step 3: Query with compatible dimensions and metrics
SELECT
  <dimension_1>,
  <dimension_2>,
  <metric_1>,
  <metric_2>
FROM SEMANTIC_VIEW(<database>.<schema>.<view_name>)
WHERE <filter_condition>  -- Optional: filters on returned columns only
ORDER BY <dimension_1>;

-- Step 4: Validate results against base tables (testing)
-- Compare aggregated results from semantic view vs. direct base table query
```

> **Investigation Required**
> When applying this rule:
> 1. **Check semantic view definition BEFORE querying** - Use `SHOW SEMANTIC DIMENSIONS/METRICS` to see available columns
> 2. **Verify dimension compatibility** - Use `SHOW SEMANTIC DIMENSIONS FOR METRIC` to check which dimensions work with specific metrics
> 3. **Never assume column names** - Always verify logical names defined in CREATE SEMANTIC VIEW
> 4. **Test queries before recommending** - Run SEMANTIC_VIEW() queries to confirm they execute successfully
> 5. **Validate window function metrics** - Check for required dimensions before using metrics with PARTITION BY
> 6. **Make grounded recommendations based on investigated view structure** - Don't suggest dimensions/metrics that don't exist
>
> **Anti-Pattern:**
> "Just query the semantic view with these standard dimensions..."
> "This metric should work with any dimension..."
>
> **Correct Pattern:**
> "Let me check what dimensions and metrics are available in this semantic view."
> [runs SHOW SEMANTIC DIMENSIONS and SHOW SEMANTIC METRICS]
> "I see the view has these dimensions: [actual list]. For the <metric_name> metric, let me verify compatible dimensions."
> [runs SHOW SEMANTIC DIMENSIONS FOR METRIC]
> "Here's a query using only compatible dimensions..."

## References

### External Documentation
- [Querying Semantic Views](https://docs.snowflake.com/en/user-guide/views-semantic/querying) - Official query syntax reference
- [SEMANTIC_VIEW() Function](https://docs.snowflake.com/en/sql-reference/functions/semantic_view) - Function documentation
- [Window Function Metrics](https://docs.snowflake.com/en/user-guide/views-semantic/querying#window-function-metrics) - Window function patterns
- [Cortex Analyst REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst#rest-api) - Natural language query testing
- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Performance analysis tool

### Related Rules
- **Semantic Views Core**: `rules/106-snowflake-semantic-views-core.md` - DDL creation, validation rules, components
- **Semantic Views Integration**: `rules/106c-snowflake-semantic-views-integration.md` - Cortex Analyst, governance, workflows
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md` - Query optimization strategies
- **Cortex Analyst Integration**: `rules/106c-snowflake-semantic-views-integration.md` - Natural language query patterns

## 1) Validation and Testing

### 1.1 Verification Commands

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

### 1.2 Semantic View Generator Validation

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

### 1.3 TPC-DS Test Examples

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

### 1.4 Testing with Cortex Analyst

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

### 1.5 Performance Validation

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

## 2) Querying Semantic Views

### 2.1 SEMANTIC_VIEW() Query Syntax

**Purpose:** Query semantic views using the `SEMANTIC_VIEW()` function with DIMENSIONS, METRICS, or FACTS clauses.

**Basic Syntax:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  <semantic_view_name>
  [DIMENSIONS <dimension_list>]
  [METRICS <metric_list>]
  [FACTS <fact_list>]
)
[WHERE <filter_conditions>]
[ORDER BY <columns>]
[LIMIT <n>];
```

**Rules:**
- **Must specify at least ONE of:** DIMENSIONS, METRICS, or FACTS
- **Cannot combine:** FACTS and METRICS in the same query
- **Can combine:** DIMENSIONS with either METRICS or FACTS
- **Clause order matters:** Specify clauses in the order you want columns to appear in results

**Minimal Query Example:**
```sql
-- Query with metrics only
SELECT * FROM SEMANTIC_VIEW(
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  METRICS StoreSales.TotalSalesQuantity
);

-- Query with dimensions and metrics
SELECT * FROM SEMANTIC_VIEW(
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS Item.Category
  METRICS StoreSales.TotalSalesQuantity
)
ORDER BY TotalSalesQuantity DESC
LIMIT 10;
```

### 2.2 Choosing Dimensions for Metrics

**Rule:** Not all dimensions can be used with every metric. Dimensions must have compatible granularity with the metric's logical table.

**Use SHOW SEMANTIC DIMENSIONS FOR METRIC to find compatible dimensions:**

```sql
-- Find which dimensions work with a specific metric
SHOW SEMANTIC DIMENSIONS FOR METRIC avg_7_days_sales_quantity
  IN sv_window_function_example;

-- Output includes 'required' column indicating mandatory dimensions
+------------+-----------+--------------+----------+----------+---------+
| table_name | name      | data_type    | required | synonyms | comment |
|------------+-----------+--------------+----------+----------+---------|
| DATE       | DATE      | DATE         | true     | NULL     | NULL    |
| DATE       | D_DATE_SK | NUMBER(38,0) | false    | NULL     | NULL    |
| DATE       | YEAR      | NUMBER(38,0) | true     | NULL     | NULL    |
+------------+-----------+--------------+----------+----------+---------+
```

**Granularity Rules:**
- **Higher granularity dimensions** (more detailed) can be used with **lower granularity metrics** (aggregated)
- **Lower granularity dimensions** cannot be used with **higher granularity metrics** (would require aggregation)
- **Example:** Daily sales metrics can be grouped by month, but monthly metrics cannot be grouped by day

**Compatible Dimension Query:**
```sql
-- Correct: Using compatible dimension (Customer) with metric
SELECT * FROM SEMANTIC_VIEW(
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS Customer.C_BIRTH_COUNTRY
  METRICS StoreSales.TotalSalesQuantity
)
ORDER BY TotalSalesQuantity DESC
LIMIT 10;
```

**Incompatible Dimension Error:**
```sql
-- Error: Dimension not compatible with metric's logical table
SELECT * FROM SEMANTIC_VIEW(
  my_semantic_view
  DIMENSIONS incompatible_table.dimension
  METRICS my_metric
);
-- Error: Dimension 'INCOMPATIBLE_TABLE.DIMENSION' cannot be used with metric 'MY_METRIC'
```

### 2.3 Using Aliases in Queries

**Rule:** Define aliases for dimensions and metrics to customize output column names.

**Syntax:**
```sql
DIMENSIONS <table>.<dimension> [AS] <alias>
METRICS <table>.<metric> [AS] <alias>
```

**Example with Aliases:**
```sql
-- Use aliases for cleaner column names
SELECT * FROM SEMANTIC_VIEW(
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS
    Customer.C_BIRTH_COUNTRY AS country,
    Item.Category AS product_category
  METRICS
    StoreSales.TotalSalesQuantity AS total_quantity
)
WHERE country IN ('UNITED STATES', 'CANADA')
ORDER BY total_quantity DESC;

-- Output columns: COUNTRY, PRODUCT_CATEGORY, TOTAL_QUANTITY
```

**Clause Order Controls Output Order:**
```sql
-- Metrics first in output
SELECT * FROM SEMANTIC_VIEW(
  my_view
  METRICS sales.total_revenue
  DIMENSIONS sales.region
);
-- Output: TOTAL_REVENUE, REGION

-- Dimensions first in output
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS sales.region
  METRICS sales.total_revenue
);
-- Output: REGION, TOTAL_REVENUE
```

### 2.4 WHERE Clause Usage

**Rule:** WHERE clauses filter results based on dimensions, facts, or metrics returned in the query.

**Filtering on Dimensions:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
  DIMENSIONS
    Date.Year,
    Store.State,
    Item.Category
  METRICS StoreSales.TotalSalesQuantity
)
WHERE Year = '2002'
  AND State IN ('CA', 'TX', 'NY')
  AND Category = 'Electronics'
ORDER BY TotalSalesQuantity DESC;
```

**Filtering on Facts:**
```sql
-- Filter on fact values (row-level data)
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS customer.customer_name
  FACTS customer.c_customer_order_count
)
WHERE c_customer_order_count > 10
ORDER BY c_customer_order_count DESC;
```

**Important Restrictions:**
- **Cannot filter on metrics** that aren't returned in the query
- **Facts and dimensions in WHERE must be in query select list**
- **All facts and dimensions in query must be from same logical table** when combining FACTS and DIMENSIONS

### 2.5 Combining FACTS, DIMENSIONS, and METRICS

**Critical Rules:**

**FORBIDDEN:**
- **Cannot use FACTS and METRICS in same query**
- **Cannot omit all three clauses** (must specify at least one)

**ALLOWED:**
```sql
-- ✓ Dimensions only
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1, d2);

-- ✓ Metrics only
SELECT * FROM SEMANTIC_VIEW(view METRICS m1, m2);

-- ✓ Facts only
SELECT * FROM SEMANTIC_VIEW(view FACTS f1, f2);

-- ✓ Dimensions + Metrics
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1 METRICS m1);

-- ✓ Dimensions + Facts
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1 FACTS f1);
```

**FORBIDDEN:**
```sql
-- ✗ Facts and Metrics together
SELECT * FROM SEMANTIC_VIEW(view FACTS f1 METRICS m1);
-- Error: Cannot specify both FACTS and METRICS

-- ✗ No clauses specified
SELECT * FROM SEMANTIC_VIEW(view);
-- Error: Must specify at least one of DIMENSIONS, METRICS, or FACTS
```

**Combining FACTS and DIMENSIONS:**
```sql
-- When using FACTS with DIMENSIONS, all must be from same logical table
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS customer.customer_name
  FACTS customer.c_customer_order_count  -- Same table as dimension
)
WHERE c_customer_order_count > 5
ORDER BY customer_name;
```

**Important Note:**
- Query groups results by dimensions specified
- If facts don't depend on dimensions, results may be non-deterministic
- Only combine FACTS and DIMENSIONS when dimensions uniquely determine facts

### 2.6 Using Dimensions in Expressions

**Rule:** DIMENSIONS clause can reference facts, and FACTS clause can reference dimensions for grouping purposes.

**Dimension Expression with Fact:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS my_table.my_fact  -- Fact used as dimension for grouping
);
```

**Fact Expression with Dimension:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  my_view
  FACTS my_table.my_dimension  -- Dimension used as row-level value
);
```

**Key Difference:**
- **DIMENSIONS clause:** Results are grouped by specified expressions
- **FACTS clause:** Row-level values returned without grouping

### 2.7 Handling Duplicate Column Names

**Problem:** Multiple tables in semantic view may have columns with same name.

**Solution:** Use table aliases to disambiguate in query results.

**Example:**
```sql
-- Create semantic view with duplicate column names
CREATE OR REPLACE SEMANTIC VIEW duplicate_names
  TABLES (
    nation AS SAMPLE_DATA.TPCDS_SF10TCL.NATION
      PRIMARY KEY (n_nationkey),
    region AS SAMPLE_DATA.TPCDS_SF10TCL.REGION
      PRIMARY KEY (r_regionkey)
  )
  DIMENSIONS (
    nation.name AS n_name,    -- Both tables have 'name' column
    region.name AS r_name
  );

-- Query with table alias to assign different column names
SELECT * FROM SEMANTIC_VIEW(
  duplicate_names
  DIMENSIONS nation.name, region.name
) AS table_alias(nation_name, region_name);

-- Output columns: NATION_NAME, REGION_NAME
```

### 2.8 Window Function Metrics

**Purpose:** Define metrics that call window functions and pass aggregated values.

**What is a Window Function Metric:**
```sql
-- Window function metric: SUM of another metric with window function
METRICS (
  table_1.metric_1 AS SUM(table_1.metric_3) OVER(
    PARTITION BY dimension_1
    ORDER BY dimension_2
  )
)

-- Another example: Window function on aggregate
METRICS (
  table_1.metric_2 AS SUM(SUM(table_1.column_1)) OVER(
    PARTITION BY dimension_1
    ORDER BY dimension_2
  )
)
```

**NOT a Window Function Metric:**
```sql
-- This passes row-level expression to window function
METRICS (
  table_1.metric_1 AS SUM(
    SUM(table_1.column_1) OVER(...)  -- Window function on column, not metric
  )
)
```

**Defining Window Function Metrics:**

**Parameters:**
```sql
<window_function>(<expression>) OVER (
  [PARTITION BY [EXCLUDING] <dimension>[, ...]]
  [ORDER BY <dimension>[, ...]]
  [RANGE BETWEEN <start> AND <end>]
)
```

**Example with TPC-DS:**
```sql
CREATE OR REPLACE SEMANTIC VIEW sv_window_function_example
  TABLES (
    store_sales AS SNOWFLAKE_SAMPLE_DATA.TPCDS_SF10TCL.store_sales,
    date AS SNOWFLAKE_SAMPLE_DATA.TPCDS_SF10TCL.date_dim PRIMARY KEY (d_date_sk)
  )
  RELATIONSHIPS (
    sales_to_date AS store_sales(ss_sold_date_sk) REFERENCES date(d_date_sk)
  )
  DIMENSIONS (
    date.date AS d_date,
    date.year AS d_year
  )
  METRICS (
    store_sales.total_sales_quantity AS SUM(ss_quantity)
      WITH SYNONYMS = ('Total sales quantity'),

    -- Window function metric: 7-day running average
    store_sales.avg_7_days_sales_quantity AS AVG(total_sales_quantity)
      OVER (PARTITION BY EXCLUDING date.date, date.year ORDER BY date.date
        RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW)
      WITH SYNONYMS = ('Running 7-day average'),

    -- Window function metric: LAG to get value 30 days ago
    store_sales.total_sales_quantity_30_days_ago AS LAG(total_sales_quantity, 30)
      OVER (PARTITION BY EXCLUDING date.date, date.year ORDER BY date.date)
      WITH SYNONYMS = ('Sales quantity 30 days ago')
  );
```

**Querying Window Function Metrics:**

**Critical Rule:** When querying a window function metric, you MUST also return the dimensions specified in:
- PARTITION BY `dimension`
- PARTITION BY EXCLUDING `dimension`
- ORDER BY `dimension`

**Find Required Dimensions:**
```sql
-- Use SHOW SEMANTIC DIMENSIONS FOR METRIC to find required dimensions
SHOW SEMANTIC DIMENSIONS IN sv_window_function_example
  FOR METRIC avg_7_days_sales_quantity;

-- Output shows 'required' column for mandatory dimensions
+------------+-----------+--------------+----------+
| table_name | name      | data_type    | required |
|------------+-----------+--------------+----------|
| DATE       | DATE      | DATE         | true     |  -- Required
| DATE       | D_DATE_SK | NUMBER(38,0) | false    |  -- Optional
| DATE       | YEAR      | NUMBER(38,0) | true     |  -- Required
+------------+-----------+--------------+----------+
```

**Correct Query with Required Dimensions:**
```sql
-- Must include date.date and date.year (required dimensions)
SELECT * FROM SEMANTIC_VIEW (
  sv_window_function_example
  DIMENSIONS date.date, date.year
  METRICS store_sales.avg_7_days_sales_quantity
);
```

**Incorrect Query (Missing Required Dimensions):**
```sql
-- Error: Missing required dimension 'DATE.DATE'
SELECT * FROM SEMANTIC_VIEW (
  sv_window_function_example
  METRICS store_sales.avg_7_days_sales_quantity
);

-- Error message:
-- Invalid semantic view query: Dimension 'DATE.DATE' used in a
-- window function metric must be requested in the query.
```

**Additional Window Function Examples:**
```sql
-- Query with multiple window function metrics
SELECT * FROM SEMANTIC_VIEW (
  sv_window_function_example
  DIMENSIONS date.date, date.year
  METRICS
    store_sales.total_sales_quantity_30_days_ago,
    store_sales.avg_7_days_sales_quantity_30_days_ago
);

-- Use other metrics from same logical table in window function
METRICS (
  orders.m3 AS SUM(m2) OVER (PARTITION BY m1 ORDER BY m2),
  orders.m4 AS ((SUM(m2) OVER (...)) / m1) + 1
)
```

**Restrictions:**
- **Cannot use window function metrics in facts or dimensions**
- **Cannot use window function metrics in definitions of other metrics**
- Required dimensions must be returned in query select list

### 2.9 Query Performance Optimization

**Remember:** Semantic views are metadata only - performance depends on base tables.

**Optimization Checklist:**
```sql
-- 1. Verify clustering on base table
SHOW CLUSTERING KEYS IN TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- 2. Check partition pruning in Query Profile
SELECT * FROM SEMANTIC_VIEW (
  my_view
  METRICS total_sales
  DIMENSIONS sale_date
)
WHERE sale_date >= '2002-01-01'  -- Filter enables partition pruning
  AND sale_date < '2003-01-01';

-- 3. Review Query Profile for:
-- [ ] Partitions scanned vs total partitions
-- [ ] Filter pushdown to base tables
-- [ ] Join elimination when dimensions not used
-- [ ] Aggregation pushdown
```

**Optimize Base Table if Needed:**
```sql
-- Add clustering to improve query performance
ALTER TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
  CLUSTER BY (SS_SOLD_DATE_SK);
```
