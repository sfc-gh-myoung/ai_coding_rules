---
appliesTo:
  - "**/*.sql"
  - "**/*.py"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Data quality, custom DMFs, expectations, business rules, data validation, quality assertions, custom metrics, validation functions, create custom DMF, custom quality checks, business rule validation, custom expectations, quality functions, UDF for quality, validation logic, custom quality metrics, quality rules, custom validation
**TokenBudget:** ~1800
**ContextTier:** Standard
**Depends:** 100-snowflake-core, 124-snowflake-data-quality-core

# Snowflake Data Quality: Custom DMFs & Expectations

## Purpose
Provide patterns for creating custom Data Metric Functions (DMFs) and expectations to implement business-specific quality rules and validation logic.

## Rule Type and Scope
- **Type:** Agent Requested
- **Scope:** Custom DMFs, expectations, business rule validation

## Contract
- **Inputs/Prereqs:** Understanding of DMF fundamentals (from 124-core), business rules defined
- **Allowed Tools:** CREATE FUNCTION, SET, expectations patterns
- **Forbidden Tools:** None specific
- **Required Steps:** 1) Define custom metric 2) Create DMF function 3) Set expectations 4) Test validation
- **Output Format:** Custom DMF functions, expectation configurations
- **Validation Steps:** DMF returns expected metrics; expectations trigger correctly

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.
**MANDATORY:**
**Essential Patterns:**
- **Create custom DMFs for business rules** - Extend system DMFs with domain logic
- **Set expectations on metrics** - Define thresholds and actions
- **Test custom validations** - Verify business rules work correctly
- **Document metric definitions** - Clear semantics for each custom metric

**Quick Checklist:**
- [ ] Custom DMF created with clear business rule
- [ ] Expectation set with appropriate threshold
- [ ] Validation tested with sample data
- [ ] Metric semantics documented

## Key Principles
- Custom DMFs extend system DMFs for business-specific rules
- Expectations define thresholds and trigger actions
- Document metric semantics for maintainability
- Test custom validations with representative data


**RECOMMENDED:**
Create custom DMFs for business-specific quality rules not covered by system DMFs.

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

## 5. Expectations

**MANDATORY:**
**CRITICAL:** Define expectations for every DMF to establish pass/fail criteria and enable automated alerting.

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
-- Row count should be between 10K and 100K
EXPECT (SNOWFLAKE.CORE.ROW_COUNT ON ()) BETWEEN 10000 AND 100000
```

**Zero Tolerance:**
```sql
-- Absolutely zero duplicates allowed
EXPECT (SNOWFLAKE.CORE.DUPLICATE_COUNT ON order_id) = 0
```

## Validation

- Create custom DMF with SQL UDF and verify it executes successfully
- Test custom DMF with edge cases (empty tables, null values, extreme thresholds)
- Verify custom validation logic correctly identifies data quality issues
- Compare custom DMF results with standard DMF functions for accuracy
- Test Python UDF DMFs if using complex validation logic
- Schedule custom DMF and check execution history
- Validate integration with alerting and monitoring systems

## Quick Compliance Checklist

- [ ] Custom DMF created with clear naming convention (DMF_CUSTOM_ prefix)
- [ ] SQL UDF or Python UDF defined with appropriate input/output types
- [ ] Custom validation logic tested with sample data
- [ ] Edge cases handled (empty tables, null values, division by zero)
- [ ] EXPECT statements use custom function results
- [ ] Thresholds based on business requirements (not arbitrary)
- [ ] DMF scheduled to run at appropriate frequency
- [ ] Execution history monitored for failures or anomalies
- [ ] Documentation includes business logic and threshold rationale
- [ ] Custom DMF performance tested (execution time < 5 minutes for large tables)
- [ ] Access controls configured for custom functions and DMFs

> **Investigation Required**  
> When applying this rule:
> 1. Read existing data quality patterns and validation logic BEFORE creating custom DMFs
> 2. Verify custom validation logic through testing with actual data samples
> 3. Never speculate about data patterns without analyzing actual data distribution
> 4. Check execution time and performance impact of custom DMFs on large tables
> 5. Make grounded recommendations based on investigated data characteristics and validation requirements

## Response Template

```sql
-- Custom Data Metric Function with SQL UDF for complex business logic
-- Example: Validate referential integrity across multiple tables

-- Step 1: Create custom UDF for validation
CREATE OR REPLACE FUNCTION UDF_CHECK_REFERENTIAL_INTEGRITY(
  fact_table STRING,
  dim_table STRING,
  fk_column STRING,
  pk_column STRING
)
RETURNS NUMBER
AS
$$
  SELECT COUNT(*)
  FROM IDENTIFIER(:fact_table) f
  WHERE NOT EXISTS (
    SELECT 1
    FROM IDENTIFIER(:dim_table) d
    WHERE f.fk_column = d.pk_column
  )
$$;

-- Step 2: Create DMF using custom UDF
CREATE OR REPLACE DATA METRIC FUNCTION DMF_CUSTOM_REFERENTIAL_INTEGRITY()
  COMMENT = 'Validate referential integrity between fact and dimension tables'
  RETURNS NUMBER
  SCHEDULE = '120 MINUTE'  -- Run every 2 hours
  AS
  $$
    DECLARE
        orphan_orders NUMBER;
        orphan_line_items NUMBER;
        invalid_products NUMBER;
    BEGIN
        -- Check 1: Orders without valid customers
        SELECT UDF_CHECK_REFERENTIAL_INTEGRITY(
          'PROD_DB.FACT.ORDERS',
          'PROD_DB.DIM.CUSTOMERS',
          'customer_id',
          'customer_id'
        )
        INTO orphan_orders;
        
        -- Check 2: Line items without valid orders
        SELECT UDF_CHECK_REFERENTIAL_INTEGRITY(
          'PROD_DB.FACT.LINE_ITEMS',
          'PROD_DB.FACT.ORDERS',
          'order_id',
          'order_id'
        )
        INTO orphan_line_items;
        
        -- Check 3: Line items with invalid product IDs
        SELECT UDF_CHECK_REFERENTIAL_INTEGRITY(
          'PROD_DB.FACT.LINE_ITEMS',
          'PROD_DB.DIM.PRODUCTS',
          'product_id',
          'product_id'
        )
        INTO invalid_products;
        
        -- Define expectations: Zero orphaned records allowed
        EXPECT (orphan_orders) = 0;
        EXPECT (orphan_line_items) = 0;
        EXPECT (invalid_products) = 0;
        
        RETURN 1.0;
    END;
  $$;

-- Execute and verify
CALL DMF_CUSTOM_REFERENTIAL_INTEGRITY();

-- Check results
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DATA_METRIC_FUNCTION_RESULTS(
  REF('DMF_CUSTOM_REFERENTIAL_INTEGRITY')))
ORDER BY measurement_time DESC
LIMIT 5;
```

## References

### Internal Documentation
- **124-snowflake-data-quality-core:** Standard DMF patterns and built-in functions
- **124b-snowflake-data-quality-operations:** Scheduling, monitoring, alerting
- **100-snowflake-core:** UDF creation patterns and SQL best practices
- **111-snowflake-observability-core:** Logging custom metrics to event tables

### External Documentation
- [Custom Data Metric Functions](https://docs.snowflake.com/en/user-guide/data-quality-custom) - Creating custom DMFs with UDFs
- [SQL UDF Reference](https://docs.snowflake.com/en/developer-guide/udf/sql/udf-sql) - SQL user-defined function syntax
- [Python UDF Reference](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python) - Python UDF for complex validation logic

