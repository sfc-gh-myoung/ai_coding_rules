# Snowflake Data Quality Monitoring Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Data Quality patterns. Load for data quality tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** data profiling, expectations, quality checks, data validation, NULL detection, uniqueness validation, freshness monitoring, anomaly detection, automated monitoring, event tables, create DMF, quality monitoring, data expectations, quality rules
**TokenBudget:** ~4550
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 105-snowflake-cost-governance.md, 107-snowflake-security-governance.md, 930-data-governance-quality.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for Snowflake Data Quality Monitoring using Data Metric Functions (DMFs), data profiling, expectations, and automated quality checks. Covers system DMFs, custom DMF creation, data profiling workflows, expectation definitions, scheduling strategies, event table monitoring, alerting, remediation workflows, and cost optimization to ensure data reliability, integrity, and compliance throughout the data lifecycle.

**When to Load This Rule:**
- Implementing Snowflake Data Quality Monitoring with DMFs
- Creating or configuring Data Metric Functions (system or custom)
- Setting up data profiling and baseline quality metrics
- Defining quality expectations and pass/fail criteria
- Troubleshooting DMF execution or expectation failures
- Monitoring data quality trends and violations
- Establishing automated quality monitoring schedules

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization
- **107-snowflake-security-governance.md** - Access control and security policies
- **930-data-governance-quality.md** - Data governance framework

**Related:**
- **124a-snowflake-data-quality-custom.md** - Custom DMF creation patterns
- **124b-snowflake-data-quality-operations.md** - Operational patterns and remediation

### External Documentation

- [Data Quality Introduction](https://docs.snowflake.com/en/user-guide/data-quality-intro) - Overview and concepts
- [Data Metric Functions](https://docs.snowflake.com/en/user-guide/data-metric-functions) - DMF creation and usage
- [System DMFs](https://docs.snowflake.com/en/sql-reference/data-metric-functions) - Built-in quality metrics
- [Data Quality Monitoring](https://docs.snowflake.com/en/user-guide/ui-snowsight-data-quality-monitoring) - Snowsight monitoring

### Related Rules

**Closely Related** (consider loading together):
- **124a-snowflake-data-quality-custom.md** - creating custom DMFs with SQL or Python UDFs
- **124b-snowflake-data-quality-operations.md** - scheduling, monitoring, and alerting on DMF results

**Sometimes Related** (load if specific scenario):
- **122-snowflake-dynamic-tables.md** - adding quality checks to dynamic table pipelines
- **104-snowflake-streams-tasks.md** - triggering tasks based on data quality events
- **111-snowflake-observability-core.md** - logging data quality metrics to event tables

**Complementary** (different aspects of same domain):
- **107-snowflake-security-governance.md** - access control on DMFs and quality monitoring
- **100-snowflake-core.md** - DDL fundamentals and object creation patterns

## Contract

### Inputs and Prerequisites

- Snowflake Enterprise Edition account
- Tables/views requiring quality monitoring
- Defined quality expectations and pass/fail criteria
- EXECUTE DATA METRIC FUNCTION privilege
- Event table for capturing results

### Mandatory

- System DMFs in SNOWFLAKE.CORE schema
- Custom DMF creation (when system DMFs insufficient)
- ALTER TABLE/VIEW for DMF associations
- Snowsight Data Quality tab for monitoring
- INFORMATION_SCHEMA and ACCOUNT_USAGE views for analysis

### Forbidden

- Exceeding 10,000 DMF-object associations per account
- Setting DMFs on shared objects or reader accounts
- Setting DMFs on object tags
- Using database roles as table owners for DMF operations

### Execution Steps

1. Profile data using Snowsight Data Profile to understand baseline characteristics
2. Select appropriate system DMFs or create custom DMFs for specific quality checks
3. Associate DMFs with tables/views using ALTER TABLE/VIEW statements
4. Define expectations for pass/fail criteria with appropriate thresholds
5. Schedule DMF evaluations at appropriate intervals based on data refresh frequency
6. Configure event table to capture results and enable alerts for failures
7. Monitor DMF execution via Snowsight Data Quality tab and query event tables for trends
8. Establish remediation workflows for failures with clear SLAs and ownership
9. Track cost consumption via DATA_QUALITY_MONITORING_USAGE_HISTORY view
10. Continuously refine expectations based on historical performance

### Output Format

Data quality implementations produce:
- DMF DDL for custom metric functions
- ALTER TABLE/VIEW statements for DMF associations
- Expectation definitions with pass/fail thresholds
- Monitoring queries for event table analysis
- Alert configurations for proactive notifications
- Remediation workflow documentation

### Validation

**Pre-Task-Completion Checks:**
- Enterprise Edition enabled for account
- EXECUTE DATA METRIC FUNCTION privilege granted to table owner role
- Event table configured and accessible
- DMFs created successfully (system or custom)
- Expectations defined for all critical quality checks

**Success Criteria:**
- DMFs execute successfully and write results to event table
- Expectations evaluate correctly (pass/fail logic functioning)
- Alerts trigger appropriately for expectation failures
- Cost consumption within expected ranges for monitoring frequency
- Remediation workflows documented and followed
- Quality trends visible in Snowsight Data Quality tab

**Negative Tests:**
- DMF execution should fail without EXECUTE DATA METRIC FUNCTION privilege
- Invalid DMF associations should be rejected at ALTER TABLE/VIEW time
- Exceeding 10,000 DMF associations should produce clear error
- Expectations with invalid syntax should fail validation

### Design Principles

- **Enterprise Edition Required:** Data Quality and DMFs require Snowflake Enterprise Edition
- **Serverless Compute:** DMFs use serverless compute billed under "Data Quality Monitoring" category
- **Proactive Monitoring:** Scheduled DMF evaluations provide continuous quality assurance
- **Expectations-Driven:** Define explicit pass/fail criteria using expectations for all quality checks
- **Automated Alerting:** Configure alerts on expectation failures to drive timely remediation
- **Cost Awareness:** Monitor serverless credit consumption and right-size schedules
- **Least Privilege:** Table owner role must have global EXECUTE DATA METRIC FUNCTION privilege

> **Investigation Required**
> When working with Data Quality:
> 1. **Check existing DMFs BEFORE creating new ones** - Use SHOW DATA METRIC FUNCTIONS to understand current setup
> 2. **Verify Enterprise Edition** - Data Quality features require Enterprise Edition
> 3. **Profile data first** - Use Snowsight Data Profile to understand baseline before setting expectations
> 4. **Review event table** - Check DMF_EVALUATION_HISTORY for execution patterns and failures
> 5. **Monitor costs** - Query DATA_QUALITY_MONITORING_USAGE_HISTORY for credit consumption
>
> **Anti-Pattern:**
> "Creating DMF... (without profiling data first)"
> "Setting expectations... (without understanding baseline)"
>
> **Correct Pattern:**
> "Let me check your existing data quality setup first."
> [reads SHOW DATA METRIC FUNCTIONS, checks event table, profiles data]
> "I see you have NULL rate monitoring with 5% threshold. Creating new DMF following this pattern..."

### Post-Execution Checklist

- [ ] Enterprise Edition verified for account
- [ ] Data profiling completed to understand baselines
- [ ] System DMFs evaluated for applicability
- [ ] Custom DMFs created where system DMFs insufficient
- [ ] DMFs associated with critical tables/views
- [ ] Expectations defined with appropriate thresholds
- [ ] Monitoring schedule configured based on data refresh frequency
- [ ] Event table configured and accessible
- [ ] Alerts configured for expectation failures
- [ ] Remediation workflows documented with SLAs
- [ ] Cost monitoring queries established
- [ ] Snowsight Data Quality tab reviewed
- [ ] EXECUTE DATA METRIC FUNCTION privilege granted appropriately

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using DMFs Without Defining Expectations**
```sql
-- Bad: DMF created but no expectations set
CREATE DATA METRIC FUNCTION check_nulls()
RETURNS FLOAT
AS $$
  SELECT COUNT_IF(important_column IS NULL)::FLOAT / COUNT(*)::FLOAT
  FROM critical_table
$$;

ALTER TABLE critical_table ADD DATA METRIC FUNCTION check_nulls ON ();
-- No expectation defined! DMF runs but never alerts on high null rates
```
**Problem:** No pass/fail criteria; metrics collected but not acted upon; silent quality degradation; no alerting; manual result checking required; defeats automation purpose

**Correct Pattern:**
```sql
-- Good: DMF with clear expectation threshold
CREATE DATA METRIC FUNCTION check_nulls()
RETURNS FLOAT
AS $$
  SELECT COUNT_IF(important_column IS NULL)::FLOAT / COUNT(*)::FLOAT
  FROM critical_table
$$;

ALTER TABLE critical_table
  ADD DATA METRIC FUNCTION check_nulls ON ()
  EXPECT (check_nulls ON ()) < 0.05;  -- Alert if >5% nulls

-- Set up alerting on expectation failures via event table
```
**Benefits:** Automated pass/fail evaluation; proactive alerting; clear quality thresholds; actionable results; enables quality gates; compliance-ready

**Anti-Pattern 2: Not Profiling Data Before Setting Thresholds**
```sql
-- Bad: Arbitrary expectation thresholds without baseline understanding
ALTER TABLE sales_data
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
  EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON (discount_pct)) = 0;
-- Expectation fails immediately because discount_pct is NULL for 30% of rows naturally!
```
**Problem:** False positive alerts; arbitrary thresholds; alert fatigue; lost trust in monitoring; production noise; unrealistic expectations; wasted investigation time

**Correct Pattern:**
```sql
-- Good: Profile data first to understand baseline
-- Step 1: Profile using Snowsight Data Profile or SQL
SELECT
  COUNT(*) as total_rows,
  COUNT_IF(discount_pct IS NULL) as null_count,
  COUNT_IF(discount_pct IS NULL)::FLOAT / COUNT(*)::FLOAT as null_rate
FROM sales_data;
-- Result: null_rate = 0.32 (32% naturally NULL for non-discounted sales)

-- Step 2: Set realistic expectation based on baseline
ALTER TABLE sales_data
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
  EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON (discount_pct)) < 0.40;
-- Alert only if null rate exceeds normal 32% by significant margin
```
**Benefits:** Realistic thresholds; fewer false positives; actionable alerts; baseline understanding; trust in monitoring; effective quality gates

**Anti-Pattern 3: Exceeding 10,000 DMF-Object Association Limit**
```sql
-- Bad: Associating same DMF to every table without prioritization
-- [Loop through 15,000 tables and add same DMF to each]
-- Hits 10,000 association limit and fails
```
**Problem:** Account-wide 10,000 association limit; deployment failures; unmonitored critical tables; wasted associations on low-value tables; serverless cost bloat; monitoring gaps

**Correct Pattern:**
```sql
-- Good: Prioritize DMF associations for critical tables only
-- Step 1: Identify critical tables with tagging
ALTER TABLE critical_customer_data SET TAG criticality = 'HIGH';
ALTER TABLE critical_financial_data SET TAG criticality = 'HIGH';
-- [Tag 200 critical tables]

-- Step 2: Apply DMFs only to high-criticality tables
SELECT
  table_catalog,
  table_schema,
  table_name
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_name = 'CRITICALITY' AND tag_value = 'HIGH';

-- Associate DMFs to ~200 critical tables, well under 10,000 limit
-- Use system DMFs efficiently: FRESHNESS, NULL_COUNT, ROW_COUNT
```
**Benefits:** Stays under 10,000 limit; focuses on high-value tables; cost-effective monitoring; complete critical coverage; scalable approach; prioritized quality

**Anti-Pattern 4: Using Database Roles as DMF Table Owners**
```sql
-- Bad: Table owned by database role, can't execute DMFs
CREATE DATABASE ROLE db_owner;
GRANT OWNERSHIP ON TABLE customers TO DATABASE ROLE db_owner;

-- Try to add DMF - FAILS
ALTER TABLE customers ADD DATA METRIC FUNCTION check_freshness ON ();
-- Error: Database roles cannot have global EXECUTE DATA METRIC FUNCTION privilege
```
**Problem:** Database roles can't hold global privileges; DMF execution fails; requires ownership transfer; deployment complications; cross-database DMF limitations

**Correct Pattern:**
```sql
-- Good: Use account-scoped role as table owner for DMF operations
CREATE ROLE data_quality_owner;  -- Account role, not database role
GRANT EXECUTE DATA METRIC FUNCTION TO ROLE data_quality_owner;

-- Transfer ownership to account role
GRANT OWNERSHIP ON TABLE customers TO ROLE data_quality_owner;

-- Now DMF operations succeed
ALTER TABLE customers ADD DATA METRIC FUNCTION check_freshness ON ();
```
**Benefits:** DMF operations work; proper privilege model; account-scoped role inheritance; cross-database DMF support; clean ownership model; no deployment issues

## Output Format Examples

```sql
-- Complete Data Metric Function definition with multiple measurement types
CREATE OR REPLACE DATA METRIC FUNCTION DMF_CUSTOMER_DATA_QUALITY()
  COMMENT = 'Comprehensive data quality monitoring for customer dimension table'
  RETURNS NUMBER
  SCHEDULE = '60 MINUTE'  -- Run every hour
  AS
  $$
    DECLARE
        freshness_hours NUMBER;
        null_count_email NUMBER;
        null_count_phone NUMBER;
        duplicate_count NUMBER;
        invalid_email_count NUMBER;
        total_rows NUMBER;
    BEGIN
        -- 1. Freshness: Data should be updated within last 24 hours
        SELECT DATEDIFF(HOUR, MAX(last_updated_ts), CURRENT_TIMESTAMP())
        INTO freshness_hours
        FROM PROD_DB.DIM.CUSTOMERS;

        -- 2. Null checks: Critical fields should have minimal nulls
        SELECT
            SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN phone IS NULL THEN 1 ELSE 0 END),
            COUNT(*)
        INTO null_count_email, null_count_phone, total_rows
        FROM PROD_DB.DIM.CUSTOMERS;

        -- 3. Uniqueness: Customer IDs must be unique
        SELECT COUNT(*) - COUNT(DISTINCT customer_id)
        INTO duplicate_count
        FROM PROD_DB.DIM.CUSTOMERS;

        -- 4. Custom validation: Email format check
        SELECT COUNT(*)
        INTO invalid_email_count
        FROM PROD_DB.DIM.CUSTOMERS
        WHERE email IS NOT NULL
        AND email NOT REGEXP '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}';

        -- Define quality expectations
        EXPECT (freshness_hours) < 24;  -- Data updated within 24 hours
        EXPECT (null_count_email) < (total_rows * 0.05);  -- <5% null emails
        EXPECT (null_count_phone) < (total_rows * 0.10);  -- <10% null phones
        EXPECT (duplicate_count) = 0;  -- No duplicate customer IDs
        EXPECT (invalid_email_count) < (total_rows * 0.01);  -- <1% invalid emails

        -- Return overall quality score (percentage of passing checks)
        RETURN 1.0;  -- DMF framework handles pass/fail internally
    END;
  $$;

-- Execute DMF and check results
CALL DMF_CUSTOMER_DATA_QUALITY();

-- Query execution history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DATA_METRIC_FUNCTION_RESULTS(
  REF('DMF_CUSTOMER_DATA_QUALITY')))
ORDER BY measurement_time DESC
LIMIT 10;
```

## Data Quality Fundamentals

### What are Data Metric Functions (DMFs)?

**MANDATORY:**
**CRITICAL:** Data Metric Functions (DMFs) are specialized functions that measure data quality metrics such as freshness, NULL counts, duplicates, and custom business rules.

**Key Characteristics:**
- DMFs run on serverless compute (no warehouse required)
- Results stored in dedicated event tables
- Scheduled evaluations for continuous monitoring
- System-provided and user-defined DMF types
- Enterprise Edition feature only

**DMF Types:**

1. **System DMFs (SNOWFLAKE.CORE):**
   - Pre-built functions for common metrics
   - No need to create, just use directly
   - Examples: NULL_COUNT, DUPLICATE_COUNT, FRESHNESS, ROW_COUNT

2. **Custom DMFs:**
   - User-defined functions for specific business rules
   - Created in user schemas
   - Must return FLOAT for compatibility with expectations

### Enterprise Edition Requirement

**REQUIREMENT:** Data Quality and DMFs require Snowflake Enterprise Edition. Trial accounts do not support this feature.

## Data Profiling

**RECOMMENDED:**
**BEST PRACTICE:** Always start with data profiling to understand baseline characteristics before implementing DMFs.

### Using Data Profile in Snowsight

**Access Data Profile:**
```
1. Sign in to Snowsight
2. Navigate to: Catalog » Database Explorer
3. Select table or view
4. Click "Data Quality" tab
5. Click "Data Profile"
```

**Profile Statistics Provided:**
- Number of rows in table
- Last update timestamp
- NULL value counts per column
- Minimum and maximum values per column
- Most common values per column
- Data type distributions

### Warehouse Considerations for Profiling

**Recommendation:** Use X-Small warehouse for data profiling queries (default behavior).

```sql
-- Data profiling runs background queries
-- Default: Uses user's default warehouse
-- Override: Select different warehouse in Snowsight dropdown

-- For heavy workloads, consider larger warehouse
-- Tradeoff: Faster profiling vs higher credit consumption
```

### Profiling-to-DMF Workflow

**RECOMMENDED:**
```sql
-- Step 1: Profile data to discover issues
-- Use Snowsight Data Profile UI

-- Step 2: Identify quality concerns from profile
-- Example: Column X has 15% NULLs (unexpected)

-- Step 3: Create expectation-based DMF
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email);

-- Step 4: Set expectation
ALTER TABLE CUSTOMERS
  MODIFY DATA METRIC SCHEDULE
    '5 MINUTES'
    USING CRON '*/5 * * * *'
    SET REFERENCE = 'email_quality_check'
    EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON email) < 100;
```

## System DMFs

**MANDATORY:**
System DMFs are pre-built functions in the SNOWFLAKE.CORE schema for common quality metrics.

### Available System DMFs

**System Data Metric Functions:**
- **NULL_COUNT** - Count NULL values in column (returns FLOAT) - Monitor unexpected NULLs in required fields
- **DUPLICATE_COUNT** - Count duplicate values in column(s) (returns FLOAT) - Detect duplicate keys in dimensional tables
- **UNIQUE_COUNT** - Count distinct values (returns FLOAT) - Monitor cardinality of categorical columns
- **ROW_COUNT** - Count total rows in table (returns FLOAT) - Track table growth over time
- **FRESHNESS** - Measure data staleness in minutes since last update (returns FLOAT) - SLA monitoring for data pipelines

### System DMF Usage Patterns

**NULL_COUNT Example:**
```sql
-- Associate NULL_COUNT DMF with column
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email);

-- Set expectation: email column should have < 5% NULLs
ALTER TABLE CUSTOMERS
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
    EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON email) < (SELECT COUNT(*) * 0.05 FROM CUSTOMERS);
```

**DUPLICATE_COUNT Example:**
```sql
-- Detect duplicates in primary key
ALTER TABLE ORDERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.DUPLICATE_COUNT ON (order_id);

-- Expectation: Zero duplicates allowed
ALTER TABLE ORDERS
  MODIFY DATA METRIC SCHEDULE '30 MINUTES'
    EXPECT (SNOWFLAKE.CORE.DUPLICATE_COUNT ON order_id) = 0;
```

**FRESHNESS Example:**
```sql
-- Monitor data freshness
ALTER TABLE SALES_FACT
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (updated_timestamp);

-- Expectation: Data should be < 60 minutes old
ALTER TABLE SALES_FACT
  MODIFY DATA METRIC SCHEDULE '15 MINUTES'
    EXPECT (SNOWFLAKE.CORE.FRESHNESS ON updated_timestamp) < 60;
```

**ROW_COUNT Example:**
```sql
-- Track table growth
ALTER TABLE TRANSACTIONS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.ROW_COUNT ON ();

-- Expectation: Table should have > 1000 rows minimum
ALTER TABLE TRANSACTIONS
  MODIFY DATA METRIC SCHEDULE '1 DAY'
    EXPECT (SNOWFLAKE.CORE.ROW_COUNT ON ()) > 1000;
```

## Custom DMFs
