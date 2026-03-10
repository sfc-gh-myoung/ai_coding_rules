# Snowflake Data Quality: Custom DMFs & Expectations

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:custom-quality-check
**Keywords:** quality assertions, custom metrics, validation functions, create custom DMF, custom quality checks, business rule validation, custom expectations, quality functions, UDF for quality, validation logic, custom quality metrics, quality rules, custom validation
**TokenBudget:** ~3600
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 124-snowflake-data-quality-core.md

## Scope

**What This Rule Covers:**
Patterns for creating custom Data Metric Functions (DMFs) and expectations to implement business-specific quality rules and validation logic beyond system DMFs. Covers custom DMF creation, business rule validation, expectation thresholds, testing strategies, and documentation requirements.

**When to Load This Rule:**
- Creating custom DMFs for business-specific quality checks
- Implementing business rule validation beyond system DMFs
- Defining custom expectations with specific thresholds
- Troubleshooting custom DMF execution issues

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **124-snowflake-data-quality-core.md** - Data Quality fundamentals

**Related:**
- **124b-snowflake-data-quality-operations.md** - Operational patterns and scheduling

### External Documentation

- [Custom DMFs](https://docs.snowflake.com/en/user-guide/data-quality-custom) - Creating custom quality metrics

## Contract

### Inputs and Prerequisites

- Understanding of DMF fundamentals from 124-snowflake-data-quality-core
- Business rules and quality requirements defined
- EXECUTE DATA METRIC FUNCTION privilege

### Mandatory

- CREATE FUNCTION for custom DMFs
- FLOAT return type for DMF compatibility
- Expectation definitions with thresholds
- Testing with representative data

### Forbidden

- Creating custom DMFs without clear business justification
- Custom DMFs that don't return FLOAT type

### Execution Steps

1. Define custom metric and business rule
2. Create DMF function returning FLOAT
3. Set expectations with appropriate thresholds
4. Test validation with representative and edge case data
5. Document metric semantics and business rationale

### Output Format

Custom DMF implementations produce:
- DMF function definitions (CREATE FUNCTION)
- Expectation configurations
- Test validation queries
- Documentation of metric semantics

### Validation

**Pre-Task-Completion Checks:**
- Custom DMF returns FLOAT type
- Business rule clearly documented
- Expectations defined with thresholds

**Success Criteria:**
- DMF executes successfully and returns expected metrics
- Expectations trigger correctly on threshold violations
- Custom validation tested with edge cases

**Negative Tests:**
- DMF should fail gracefully with invalid inputs
- Expectations should not trigger on valid data
- Custom DMF with wrong return type should fail at creation time

**Integration Tests:**
- Create custom DMF with SQL UDF and verify it executes successfully
- Test custom DMF with edge cases (empty tables, null values, extreme thresholds)
- Verify custom validation logic correctly identifies data quality issues
- Compare custom DMF results with standard DMF functions for accuracy
- Test Python UDF DMFs if using complex validation logic
- Schedule custom DMF and check execution history
- Validate integration with alerting and monitoring systems

### Design Principles

- **Business-specific rules:** Custom DMFs extend system DMFs for domain-specific validation
- **Expectation-driven:** Define explicit thresholds and trigger actions
- **Documentation:** Document metric semantics for maintainability
- **Testing:** Test custom validations with representative data

### Post-Execution Checklist

- [ ] Custom DMF created with clear naming convention (DMF_CUSTOM_ prefix)
- [ ] DMF returns FLOAT type for compatibility
- [ ] SQL UDF or Python UDF defined with appropriate input/output types
- [ ] Custom validation logic tested with sample data and edge cases
- [ ] Edge cases handled (empty tables, null values, division by zero)
- [ ] Expectation set with appropriate threshold based on business requirements
- [ ] DMF scheduled to run at appropriate frequency
- [ ] Execution history monitored for failures or anomalies
- [ ] Documentation includes business logic and threshold rationale
- [ ] Custom DMF performance tested (execution time < 5 minutes for large tables)
- [ ] Access controls configured for custom functions and DMFs

### Custom DMF Requirements
**Must return FLOAT:**
- Custom DMFs must return FLOAT data type for compatibility with expectations
- Use CAST() to convert other types to FLOAT
**Function Signature:**
```sql
CREATE DATA METRIC FUNCTION [IF NOT EXISTS] <schema>.<function_name>()
RETURNS FLOAT
AS ...
```
### Custom DMF Examples
**Example 1: Revenue Validation**
```sql
-- Custom DMF: Validate revenue within expected range
CREATE DATA METRIC FUNCTION ANALYTICS.REVENUE_RANGE_CHECK()
RETURNS FLOAT
AS
$$
SELECT
CASE
WHEN SUM(revenue) BETWEEN 1000000 AND 10000000 THEN 1.0
ELSE 0.0
END::FLOAT
FROM SALES_FACT
WHERE order_date = CURRENT_DATE()
$$;
-- Associate with table
ALTER TABLE SALES_FACT
ADD DATA METRIC FUNCTION ANALYTICS.REVENUE_RANGE_CHECK ON ();
-- Set expectation: Should pass (return 1.0)
ALTER TABLE SALES_FACT
MODIFY DATA METRIC SCHEDULE '1 HOUR'
EXPECT (ANALYTICS.REVENUE_RANGE_CHECK ON ()) = 1.0;
```
**Example 2: Business Rule Validation**
```sql
-- Custom DMF: Validate business rule (order total = sum of line items)
CREATE DATA METRIC FUNCTION ANALYTICS.ORDER_TOTAL_INTEGRITY()
RETURNS FLOAT
AS
$$
SELECT COUNT(*)::FLOAT
FROM ORDERS o
LEFT JOIN (
SELECT order_id, SUM(line_total) AS calculated_total
FROM ORDER_LINES
GROUP BY order_id
) ol ON o.order_id = ol.order_id
WHERE ABS(o.order_total - COALESCE(ol.calculated_total, 0)) > 0.01
$$;
-- Associate and expect zero violations
ALTER TABLE ORDERS
ADD DATA METRIC FUNCTION ANALYTICS.ORDER_TOTAL_INTEGRITY ON ();
ALTER TABLE ORDERS
MODIFY DATA METRIC SCHEDULE '30 MINUTES'
EXPECT (ANALYTICS.ORDER_TOTAL_INTEGRITY ON ()) = 0;
```
**Example 3: Referential Integrity Check**
```sql
-- Custom DMF: Check orphaned foreign keys
CREATE DATA METRIC FUNCTION ANALYTICS.ORPHANED_ORDERS()
RETURNS FLOAT
AS
$$
SELECT COUNT(*)::FLOAT
FROM ORDERS o
LEFT JOIN CUSTOMERS c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
$$;
-- Expect zero orphaned orders
ALTER TABLE ORDERS
ADD DATA METRIC FUNCTION ANALYTICS.ORPHANED_ORDERS ON ();
ALTER TABLE ORDERS
MODIFY DATA METRIC SCHEDULE '1 HOUR'
EXPECT (ANALYTICS.ORPHANED_ORDERS ON ()) = 0;
```

**Example 4: Python UDF DMF (Complex Validation)**
```sql
-- Python UDF DMF for regex-based validation (e.g., phone number format)
CREATE OR REPLACE DATA METRIC FUNCTION DMF_INVALID_PHONE_FORMAT(
  ARG_T TABLE(phone STRING)
)
RETURNS FLOAT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
AS
$$
import re

def main(df):
    """Count phone numbers not matching E.164 or US format."""
    pattern = re.compile(r'^\+?1?\d{10,15}$')
    invalid = df[~df['PHONE'].apply(
        lambda x: bool(pattern.match(str(x).replace('-','').replace(' ','')))
        if x is not None else True  # NULLs handled by NULL_COUNT DMF
    )]
    return float(len(invalid))
$$;

-- Associate and set expectation:
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION DMF_INVALID_PHONE_FORMAT ON (phone);
ALTER TABLE CUSTOMERS
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
    EXPECT (DMF_INVALID_PHONE_FORMAT ON phone) < 50;
```

> **When to use Python UDF DMFs:** Use when validation requires regex, statistical
> analysis, or logic too complex for SQL. SQL DMFs are faster and cheaper — prefer
> SQL unless Python capabilities are specifically needed.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Custom DMF Doesn't Return FLOAT Type**
```sql
-- Bad: Returns BOOLEAN instead of FLOAT
CREATE DATA METRIC FUNCTION validate_revenue()
RETURNS BOOLEAN
AS $$
  SELECT SUM(revenue) > 1000000
  FROM sales_fact
$$;
-- Error: DMF must return FLOAT, not BOOLEAN
```
**Problem:** Type mismatch error; DMF creation fails; can't use with expectations; Snowflake requires FLOAT return type for all DMFs; blocks deployment

**Correct Pattern:**
```sql
-- Good: Convert BOOLEAN to FLOAT
CREATE DATA METRIC FUNCTION validate_revenue()
RETURNS FLOAT
AS $$
  SELECT (SUM(revenue) > 1000000)::FLOAT
  FROM sales_fact
$$;
-- Returns 1.0 (true) or 0.0 (false) as FLOAT
```
**Benefits:** Type-safe DMF; works with expectations; follows Snowflake DMF contract; deployment succeeds; can use EXPECT = 1.0 for validation

**Anti-Pattern 2: Not Handling Edge Cases in Custom DMF Logic**
```sql
-- Bad: Division by zero on empty table
CREATE DATA METRIC FUNCTION completion_rate()
RETURNS FLOAT
AS $$
  SELECT
    COUNT_IF(status = 'complete')::FLOAT / COUNT(*)::FLOAT
  FROM orders
$$;
-- Returns NULL or error when orders table is empty!
```
**Problem:** NULL results break expectations; division by zero errors; empty table handling missing; DMF failures on edge cases; unreliable monitoring

**Correct Pattern:**
```sql
-- Good: Handle edge cases explicitly
CREATE DATA METRIC FUNCTION completion_rate()
RETURNS FLOAT
AS $$
  SELECT
    CASE
      WHEN COUNT(*) = 0 THEN 0.0  -- Empty table = 0% completion
      ELSE COUNT_IF(status = 'complete')::FLOAT / COUNT(*)::FLOAT
    END
  FROM orders
$$;
```
**Benefits:** Robust DMF logic; handles empty tables; no NULL results; predictable behavior; reliable expectations; production-ready validation

**Anti-Pattern 3: Overly Complex Custom DMF Logic**
```sql
-- Bad: 50-line SQL with 5 CTEs and multiple joins in DMF
CREATE DATA METRIC FUNCTION complex_validation()
RETURNS FLOAT
AS $$
  WITH cte1 AS (...),
       cte2 AS (...),
       cte3 AS (...),
       cte4 AS (...),
       cte5 AS (...)
  SELECT [complex 30-line calculation]
  FROM cte5
  JOIN cte4 ON ...
  -- [Additional complexity]
$$;
```
**Problem:** Slow DMF execution; high serverless costs; difficult to debug; unclear validation logic; maintenance nightmare; performance bottleneck

**Correct Pattern:**
```sql
-- Good: Simple, focused DMF; complex logic in materialized view
-- Step 1: Create materialized view with complex logic
CREATE MATERIALIZED VIEW validation_metrics AS
WITH cte1 AS (...),
     cte2 AS (...)
SELECT
  metric_name,
  metric_value
FROM cte2;

-- Step 2: Simple DMF reads from materialized view
CREATE DATA METRIC FUNCTION check_threshold()
RETURNS FLOAT
AS $$
  SELECT metric_value
  FROM validation_metrics
  WHERE metric_name = 'completion_rate'
$$;
```
**Benefits:** Fast DMF execution; lower serverless costs; clear separation; debuggable logic; reusable metrics view; better performance; maintainable validation

**Anti-Pattern 4: Not Testing Custom DMF Before Production Deployment**
```sql
-- Bad: Deploy custom DMF directly to production without testing
CREATE DATA METRIC FUNCTION untested_validation()
RETURNS FLOAT
AS $$
  SELECT [complex logic]
  FROM production_table
$$;

ALTER TABLE critical_prod_table
  ADD DATA METRIC FUNCTION untested_validation ON ();
-- Discover bugs in production when DMF runs!
```
**Problem:** Production bugs discovered post-deployment; incorrect expectations trigger false alerts; alert fatigue; lost credibility; emergency fixes required; user impact

**Correct Pattern:**
```sql
-- Good: Test custom DMF in dev before production
-- Step 1: Create DMF in dev environment
CREATE DATA METRIC FUNCTION test_validation()
RETURNS FLOAT
AS $$
  SELECT [complex logic]
  FROM dev_table
$$;

-- Step 2: Test with sample data
SELECT test_validation();
-- Verify: Returns expected FLOAT value

-- Step 3: Test with edge cases
-- Empty table, NULL values, boundary conditions

-- Step 4: Only after validation, deploy to production
CREATE DATA METRIC FUNCTION prod_validation()
RETURNS FLOAT
AS $$
  SELECT [tested logic]
  FROM production_table
$$;
```
**Benefits:** Bugs caught in dev; validated logic; confidence in production; realistic expectations; no false alerts; professional deployment; reduced risk

> **Investigation Required**
> When applying this rule:
> 1. Read existing data quality patterns and validation logic BEFORE creating custom DMFs
> 2. Verify custom validation logic through testing with actual data samples
> 3. Never speculate about data patterns without analyzing actual data distribution
> 4. Check execution time and performance impact of custom DMFs on large tables
> 5. Make grounded recommendations based on investigated data characteristics and validation requirements

## Expectations

Define expectations for every DMF to establish pass/fail criteria and enable automated alerting.

### Expectation Syntax

**Basic Expectation:**
```sql
ALTER TABLE <table_name>
  MODIFY DATA METRIC SCHEDULE '<interval>'
    EXPECT (<dmf_name> ON <column>) <comparison> <threshold>;
```

**Supported Comparisons:**
- `=` (equals)
- `!=` (not equals)
- `<` (less than)
- `<=` (less than or equal)
- `>` (greater than)
- `>=` (greater than or equal)

### Expectation Patterns

**Absolute Threshold:**
```sql
-- NULL count must be less than 100
EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON email) < 100
```

**Percentage-Based Threshold:**
```sql
-- NULLs must be < 5% of total rows
EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON email) < (
  SELECT COUNT(*) * 0.05 FROM CUSTOMERS
)
```

**Range-Based Threshold:**
```sql
-- Row count should be between 10K and 100K (use two comparisons)
EXPECT (SNOWFLAKE.CORE.ROW_COUNT ON ()) >= 10000
EXPECT (SNOWFLAKE.CORE.ROW_COUNT ON ()) <= 100000
```

**Zero Tolerance:**
```sql
-- Absolutely zero duplicates allowed
EXPECT (SNOWFLAKE.CORE.DUPLICATE_COUNT ON order_id) = 0
```

## Parameterized Column References

Create reusable DMFs that work on any table by using the `ARG_T TABLE(...)` parameter:

```sql
-- Reusable DMF: NULL rate for any STRING column
CREATE OR REPLACE DATA METRIC FUNCTION DMF_NULL_RATE(
  ARG_T TABLE(col STRING)
)
RETURNS FLOAT
COMMENT = 'Returns NULL rate (0.0-1.0) for any string column'
AS
$$
  SELECT
    CASE WHEN COUNT(*) = 0 THEN 0.0
         ELSE COUNT_IF(col IS NULL)::FLOAT / COUNT(*)::FLOAT
    END
  FROM ARG_T
$$;

-- Apply to different tables and columns:
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION DMF_NULL_RATE ON (email);
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION DMF_NULL_RATE ON (phone);
ALTER TABLE ORDERS
  ADD DATA METRIC FUNCTION DMF_NULL_RATE ON (shipping_address);

-- Multi-column parameterized DMF:
CREATE OR REPLACE DATA METRIC FUNCTION DMF_DATE_RANGE_CHECK(
  ARG_T TABLE(date_col TIMESTAMP_NTZ)
)
RETURNS FLOAT
COMMENT = 'Returns count of dates outside 2020-2030 range'
AS
$$
  SELECT COUNT_IF(
    date_col < '2020-01-01'::TIMESTAMP_NTZ
    OR date_col > '2030-12-31'::TIMESTAMP_NTZ
  )::FLOAT
  FROM ARG_T
$$;
```
