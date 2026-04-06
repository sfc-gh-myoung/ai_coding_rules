# Snowflake Semantic Views: Querying and Testing

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:semantic-query, kw:analyst
**Keywords:** window functions, dimension compatibility, testing, validation, TPC-DS, SEMANTIC_VIEW function, query patterns
**TokenBudget:** ~2550
**ContextTier:** High
**Depends:** 106-snowflake-semantic-views-core.md

## Scope

**What This Rule Covers:**
Comprehensive guidance for querying Snowflake Semantic Views using `SEMANTIC_VIEW()` function and validating implementations through systematic testing. Covers query syntax, dimension compatibility, window function metrics, WHERE clause usage, and performance optimization.

**When to Load This Rule:**
- Querying semantic views with SEMANTIC_VIEW() function
- Testing and validating semantic view implementations
- Debugging semantic view query errors
- Understanding dimension compatibility rules

## References

### Dependencies

**Must Load First:**
- **106-snowflake-semantic-views-core.md** - Semantic Views DDL fundamentals

### External Documentation

- [Querying Semantic Views](https://docs.snowflake.com/en/user-guide/views-semantic/querying)
- [SEMANTIC_VIEW() Function](https://docs.snowflake.com/en/sql-reference/functions/semantic_view)
- [Window Function Metrics](https://docs.snowflake.com/en/user-guide/views-semantic/querying#window-function-metrics)

## Contract

### Inputs and Prerequisites

- Semantic view exists (created via `CREATE SEMANTIC VIEW`)
- Role with SELECT privilege on the semantic view and USAGE on its schema
- Understanding of DIMENSIONS, METRICS, and FACTS defined in semantic view
- Query privileges on underlying base tables

### Mandatory

- `SELECT * FROM SEMANTIC_VIEW(...)` query syntax
- `SHOW SEMANTIC DIMENSIONS/METRICS/FACTS` for structure inspection
- `SHOW SEMANTIC DIMENSIONS FOR METRIC` for compatibility checks

### Forbidden

- Direct SELECT from semantic view without SEMANTIC_VIEW() function
- Mixing FACTS and METRICS in same query
- Querying without specifying at least one of DIMENSIONS, METRICS, or FACTS

### Execution Steps

1. Inspect semantic view structure with SHOW commands
2. Identify dimensions compatible with metrics
3. Construct SEMANTIC_VIEW() query with proper clause combination
4. Apply WHERE filters on returned columns only
5. Validate results against base table queries
6. Review Query Profile for performance

### Output Format

- Valid SEMANTIC_VIEW() SELECT statements
- Test queries comparing semantic vs direct table results

### Validation

- Query executes without errors
- Results match expected business logic
- Dimension compatibility validated via SHOW commands

### Design Principles

- **Function-based querying**: Use `SEMANTIC_VIEW()` function, not direct SELECT
- **Clause requirements**: Must specify at least ONE of DIMENSIONS, METRICS, or FACTS
- **Mutually exclusive**: Cannot combine FACTS and METRICS in same query
- **Dimension compatibility**: Not all dimensions work with all metrics - check granularity
- **Window function metrics**: Require returning PARTITION BY and ORDER BY dimensions
- **WHERE clause restrictions**: Can only filter on columns returned in query

### Post-Execution Checklist

- [ ] Used SEMANTIC_VIEW() function (not direct SELECT)
- [ ] Specified at least one of: DIMENSIONS, METRICS, FACTS
- [ ] Did NOT combine FACTS and METRICS
- [ ] Checked dimension/metric compatibility with SHOW commands
- [ ] WHERE clause filters only returned columns
- [ ] Window function metrics include required dimensions
- [ ] Validated results against base table calculations

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Combining FACTS and METRICS

```sql
SELECT * FROM SEMANTIC_VIEW(my_view
  DIMENSIONS(orders.order_date), FACTS(orders.amount), METRICS(orders.total_revenue)
);
```

**Problem:** FACTS and METRICS are mutually exclusive - query fails.

**Correct Pattern:**
```sql
-- Use FACTS only OR METRICS only
SELECT * FROM SEMANTIC_VIEW(my_view DIMENSIONS(orders.order_date) FACTS(orders.amount));
SELECT * FROM SEMANTIC_VIEW(my_view DIMENSIONS(orders.order_date) METRICS(orders.total_revenue));
```

### Anti-Pattern 2: Missing All Required Clauses

```sql
SELECT * FROM SEMANTIC_VIEW(my_view);  -- Error: no clauses specified
```

**Problem:** At least ONE of DIMENSIONS, METRICS, or FACTS required.

**Correct Pattern:**
```sql
SELECT * FROM SEMANTIC_VIEW(my_view DIMENSIONS(orders.order_date, orders.customer_id));
```

## SEMANTIC_VIEW() Query Syntax

### Key Terminology

- **FACTS**: Raw numeric values at row level (e.g., `amount`, `quantity`). Not aggregated.
- **METRICS**: Aggregated calculations (e.g., `SUM(amount)`, `COUNT(*)`). Pre-defined in DDL.
- **DIMENSIONS**: Categorical or temporal attributes for grouping (e.g., `region`, `order_date`).

FACTS and METRICS are **mutually exclusive** in a single query. Use FACTS for row-level detail; use METRICS for aggregated results.

### NULL Handling in Queries

- NULLs in DIMENSIONS appear as NULL grouping values (standard SQL GROUP BY behavior)
- METRICS like `SUM()`, `AVG()`, `COUNT(col)` ignore NULLs; `COUNT(*)` includes them
- Use `WHERE dimension IS NOT NULL` to filter NULLs from results
- `COALESCE` can be applied to returned columns in the outer SELECT

**Basic Syntax:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  <semantic_view_name>
  [DIMENSIONS <dimension_list>]
  [METRICS <metric_list>]
  [FACTS <fact_list>]
) [WHERE <filter>] [ORDER BY <cols>] [LIMIT <n>];
```

**Rules:**
- Must specify at least ONE of: DIMENSIONS, METRICS, FACTS
- Cannot combine FACTS and METRICS
- Can combine DIMENSIONS with either METRICS or FACTS
- Clause order controls output column order

**Allowed Combinations:**
```sql
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1, d2);              -- OK
SELECT * FROM SEMANTIC_VIEW(view METRICS m1, m2);                 -- OK
SELECT * FROM SEMANTIC_VIEW(view FACTS f1, f2);                   -- OK
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1 METRICS m1);       -- OK
SELECT * FROM SEMANTIC_VIEW(view DIMENSIONS d1 FACTS f1);         -- OK
SELECT * FROM SEMANTIC_VIEW(view FACTS f1 METRICS m1);            -- FORBIDDEN
```

## Dimension Compatibility

**Not all dimensions work with all metrics.** Use SHOW to find compatible dimensions:

```sql
SHOW SEMANTIC DIMENSIONS FOR METRIC avg_7_days_sales
  IN sv_window_example;

-- Output shows 'required' column for mandatory dimensions
```

**Granularity Rules:**
- Higher granularity dimensions (more detailed) can be used with lower granularity metrics (aggregated)
- Example: Daily sales metrics can be grouped by month, but monthly metrics cannot be grouped by day

## WHERE Clause Usage

**Filter on dimensions, facts, or metrics returned in query:**
```sql
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS Date.Year, Store.State, Item.Category
  METRICS StoreSales.TotalSalesQuantity
)
WHERE Year = '2002'
  AND State IN ('CA', 'TX', 'NY')
  AND Category = 'Electronics';
```

**Important:** Cannot filter on columns not returned in query.

## Using Aliases

```sql
SELECT * FROM SEMANTIC_VIEW(
  my_view
  DIMENSIONS Customer.C_BIRTH_COUNTRY AS country
  METRICS StoreSales.TotalSalesQuantity AS total_qty
)
WHERE country IN ('UNITED STATES', 'CANADA');
```

## Window Function Metrics

**Definition:**
```sql
METRICS (
  store_sales.avg_7_days AS AVG(total_sales_quantity)
    OVER (PARTITION BY EXCLUDING date.date ORDER BY date.date
      RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW)
)
```

**Critical Rule:** When querying window function metrics, MUST return dimensions from PARTITION BY and ORDER BY:

```sql
-- Find required dimensions
SHOW SEMANTIC DIMENSIONS FOR METRIC avg_7_days
  IN sv_window_example;

-- Must include required dimensions (required=true)
SELECT * FROM SEMANTIC_VIEW(
  sv_window_example
  DIMENSIONS date.date, date.year  -- Required dimensions
  METRICS store_sales.avg_7_days
);
```

**Error if missing required dimensions:**
```
Invalid semantic view query: Dimension 'DATE.DATE' used in a window function metric must be requested in the query.
```

## Verification Commands

```sql
SHOW SEMANTIC VIEWS IN SCHEMA my_schema;
SHOW SEMANTIC DIMENSIONS IN my_view;
SHOW SEMANTIC METRICS IN my_view;
SHOW SEMANTIC FACTS IN my_view;
SHOW SEMANTIC DIMENSIONS FOR METRIC my_metric IN my_view;
DESCRIBE SEMANTIC VIEW my_view;
```

## Accuracy Validation Pattern

```sql
-- Compare semantic view vs direct table query
WITH semantic_result AS (
  SELECT SUM(TotalSalesQuantity) AS semantic_total
  FROM SEMANTIC_VIEW(my_view METRICS StoreSales.TotalSalesQuantity)
  WHERE Date.Year = '2002'
),
direct_result AS (
  SELECT SUM(SS_QUANTITY) AS direct_total
  FROM STORE_SALES s JOIN DATE_DIM d ON s.SS_SOLD_DATE_SK = d.D_DATE_SK
  WHERE d.D_YEAR = 2002
)
SELECT s.semantic_total, d.direct_total,
       CASE WHEN s.semantic_total = d.direct_total THEN 'PASS' ELSE 'FAIL' END
FROM semantic_result s, direct_result d;
```

## Testing with Cortex Analyst

**SnowCLI:**
```bash
snow cortex analyst query \
  --semantic-view "PROD.SCHEMA.MY_VIEW" \
  --question "What are the top 5 selling brands?"
```

**Python REST API:**
```python
payload = {
    "semantic_view": "DATABASE.SCHEMA.MY_VIEW",
    "messages": [{"role": "user", "content": "What are top brands?"}]
}
response = requests.post(f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message",
                        headers={"Authorization": f"Bearer {token}"}, json=payload)
```

## Performance Optimization

**Semantic views are metadata only - performance depends on base tables.**

```sql
-- Check clustering on base table
SHOW CLUSTERING KEYS IN TABLE my_base_table;

-- Review Query Profile for:
-- [ ] Partitions scanned vs total
-- [ ] Filter pushdown to base tables
-- [ ] Join elimination when dimensions not used

-- Optimize base table if needed
ALTER TABLE my_base_table CLUSTER BY (date_column);
```

## Generator Validation Checklist

When reviewing generated DDL:
- [ ] PRIMARY KEY matches actual table grain
- [ ] FACTS contain only numeric columns
- [ ] DIMENSIONS contain categorical/temporal columns
- [ ] METRICS use appropriate aggregations (SUM, AVG, COUNT)
- [ ] Table references are fully qualified
- [ ] Synonyms added for natural language queries
