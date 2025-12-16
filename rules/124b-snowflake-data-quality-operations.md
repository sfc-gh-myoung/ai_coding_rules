# Snowflake Data Quality: Operations & Monitoring

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** remediation, RBAC, privilege requirements, automated monitoring, quality alerts, schedule DMF, quality event tables, quality alerting, DMF results, quality workflows, DMF RBAC, quality notifications, remediation workflows
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/124-snowflake-data-quality-core.md, rules/111-snowflake-observability-core.md

## Purpose
Provide operational patterns for Data Quality Monitoring including DMF scheduling, event table analysis, alerting, remediation workflows, and RBAC configuration.

## Rule Scope
DMF scheduling, event tables, alerts, remediation, RBAC

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.
**MANDATORY:**
**Essential Patterns:**
- **Schedule DMF evaluations** - Automate quality checks with Tasks
- **Monitor event tables** - Track DMF results and violations
- **Configure alerts** - Notify on quality issues
- **Define remediation** - Automated or manual fix workflows
- **Enforce RBAC** - Least-privilege access to DMF operations

**Quick Checklist:**
- [ ] DMF evaluation tasks scheduled
- [ ] Event tables configured for results
- [ ] Alerts set up for quality violations
- [ ] Remediation workflows defined
- [ ] RBAC configured with least privilege

## Contract

<contract>
<inputs_prereqs>
DMFs configured (from 124-core), expectations set (from 124a-custom)
</inputs_prereqs>

<mandatory>
Tasks, event tables, alert configurations, RBAC commands
</mandatory>

<forbidden>
None specific
</forbidden>

<steps>
1) Schedule DMF evaluations 2) Configure event tables 3) Set up alerts 4) Define remediation 5) Configure RBAC
</steps>

<output_format>
Task schedules, event table queries, alert configs, RBAC grants
</output_format>

<validation>
Tasks run successfully; alerts trigger correctly; RBAC enforced
</validation>

<design_principles>
- Automate DMF evaluations with scheduled Tasks
- Monitor event tables for quality trends and violations
- Configure proactive alerts for critical quality issues
- Define clear remediation workflows
- Enforce least-privilege RBAC for DMF operations
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Over-Monitoring Everything**
```sql
-- Setting DMFs on every column of every table at high frequency
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (customer_id);
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (first_name);
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (last_name);
-- ... 50 more columns
-- All scheduled every 5 minutes
ALTER TABLE CUSTOMERS MODIFY DATA METRIC SCHEDULE '5 MINUTES';
```
**Problem:** Excessive monitoring drives up serverless credit costs without proportional value; alert fatigue from too many checks; approaching 10,000 association limit quickly.

**Correct Pattern:**
```sql
-- Focus on critical columns and appropriate frequency
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (customer_id); -- Primary key
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email); -- Required field

-- Schedule based on data update frequency
ALTER TABLE CUSTOMERS MODIFY DATA METRIC SCHEDULE '1 HOUR'; -- Updated hourly

-- Create custom DMF for multiple column checks if needed
CREATE DATA METRIC FUNCTION ANALYTICS.CUSTOMER_COMPLETENESS()
RETURNS FLOAT AS
$$ SELECT COUNT(*)::FLOAT FROM CUSTOMERS
   WHERE first_name IS NULL OR last_name IS NULL OR email IS NULL $$;
```
**Benefits:** Cost-effective monitoring focused on critical quality indicators; sustainable approach within limits; actionable alerts only.

**Anti-Pattern 2: Missing Expectations**
```sql
-- Adding DMFs without expectations
ALTER TABLE ORDERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.DUPLICATE_COUNT ON (order_id);
ALTER TABLE ORDERS MODIFY DATA METRIC SCHEDULE '30 MINUTES';

-- No expectation defined = no pass/fail criteria = no alerts
```
**Problem:** DMFs run and consume credits but provide no actionable insights; no automated alerting; manual review required to detect issues.

**Correct Pattern:**
```sql
-- Always define expectations for automated pass/fail
ALTER TABLE ORDERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.DUPLICATE_COUNT ON (order_id);

ALTER TABLE ORDERS
  MODIFY DATA METRIC SCHEDULE '30 MINUTES'
    EXPECT (SNOWFLAKE.CORE.DUPLICATE_COUNT ON order_id) = 0;

-- Configure alert for failures
CREATE ALERT DATA_QUALITY.ALERTS.ORDER_DUPLICATE_ALERT
  WAREHOUSE = ALERT_WH
  SCHEDULE = '30 MINUTES'
  IF (EXISTS (
    SELECT 1 FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
    WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
      AND record_value:table_name = 'ORDERS'
      AND record_value:expectation_passed::BOOLEAN = FALSE
      AND record_timestamp >= DATEADD(minute, -30, CURRENT_TIMESTAMP())
  ))
  THEN CALL SYSTEM$SEND_EMAIL(...);
```
**Benefits:** Automated detection of quality issues; timely alerting enables rapid remediation; clear pass/fail criteria for tracking.

**Anti-Pattern 3: Database Role as Table Owner**
```sql
-- Creating table with database role ownership
USE ROLE ACCOUNTADMIN;
CREATE DATABASE ROLE ANALYTICS.DATA_ENGINEERS;
GRANT OWNERSHIP ON TABLE ANALYTICS.CORE.CUSTOMERS TO DATABASE ROLE ANALYTICS.DATA_ENGINEERS;

-- Attempting to set DMF fails
USE ROLE ACCOUNTADMIN;
GRANT EXECUTE DATA METRIC FUNCTION ON ACCOUNT TO DATABASE ROLE ANALYTICS.DATA_ENGINEERS;
-- Error: Cannot grant global privilege to database role

ALTER TABLE ANALYTICS.CORE.CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email);
-- Error: Table owner lacks required privilege
```
**Problem:** Database roles cannot receive global privileges; DMF operations fail; ownership transfer required.

**Correct Pattern:**
```sql
-- Use account-scoped custom role for table ownership
USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS DATA_QUALITY_ADMIN;
GRANT EXECUTE DATA METRIC FUNCTION ON ACCOUNT TO ROLE DATA_QUALITY_ADMIN;
GRANT USAGE ON DATABASE ANALYTICS TO ROLE DATA_QUALITY_ADMIN;
GRANT USAGE ON SCHEMA ANALYTICS.CORE TO ROLE DATA_QUALITY_ADMIN;
GRANT OWNERSHIP ON TABLE ANALYTICS.CORE.CUSTOMERS TO ROLE DATA_QUALITY_ADMIN;

-- Now DMF operations work
USE ROLE DATA_QUALITY_ADMIN;
ALTER TABLE ANALYTICS.CORE.CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email);
```
**Benefits:** Proper privilege structure enables DMF operations; follows Snowflake security best practices; avoids permission errors.

**Anti-Pattern 4: No Remediation Workflow**
```sql
-- DMFs configured, alerts firing, but no process to fix issues
-- Alerts accumulate, team ignores them (alert fatigue)
-- Quality issues persist without resolution
```
**Problem:** DMFs detect problems but nothing changes; wasted investment in monitoring; data quality does not improve; alert fatigue leads to ignoring all alerts.

**Correct Pattern:**
```sql
-- Establish documented remediation workflow

-- 1. Alert fires and creates incident ticket
CREATE ALERT DATA_QUALITY.ALERTS.QUALITY_INCIDENT
  WAREHOUSE = ALERT_WH
  SCHEDULE = '15 MINUTES'
  IF (EXISTS (SELECT 1 FROM ... WHERE expectation_passed = FALSE))
  THEN CALL CREATE_INCIDENT_TICKET_PROCEDURE(...);

-- 2. On-call engineer investigates using runbook
CREATE OR REPLACE VIEW DATA_QUALITY.MONITORING.VW_RECENT_FAILURES AS
SELECT
  record_timestamp,
  record_value:table_name::STRING AS table_name,
  record_value:metric_name::STRING AS metric_name,
  record_value:expectation::STRING AS expectation,
  'Runbook: https://wiki.company.com/data-quality/' ||
    record_value:table_name::STRING AS runbook_link
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_value:expectation_passed::BOOLEAN = FALSE;

-- 3. SLA tracking table
CREATE TABLE DATA_QUALITY.TRACKING.INCIDENTS (
  incident_id NUMBER,
  table_name STRING,
  metric_name STRING,
  detected_timestamp TIMESTAMP,
  resolved_timestamp TIMESTAMP,
  resolution_time_minutes NUMBER,
  root_cause STRING,
  remediation_action STRING
);

-- 4. Regular review of resolution times
SELECT
  table_name,
  AVG(resolution_time_minutes) AS avg_resolution_time,
  MAX(resolution_time_minutes) AS max_resolution_time
FROM DATA_QUALITY.TRACKING.INCIDENTS
WHERE detected_timestamp >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY table_name;
```
**Benefits:** Structured response to quality issues; accountability and tracking; continuous improvement of data quality; prevents alert fatigue.

**Anti-Pattern 5: Skipping Data Profiling**
```sql
-- Creating DMFs without understanding baseline data characteristics
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (middle_name);

-- Set expectation based on guess
ALTER TABLE CUSTOMERS
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
    EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON middle_name) < 100;

-- Reality: 80% of records don't have middle names (legitimate)
-- Alert fires constantly on false positives
```
**Problem:** Expectations based on assumptions, not reality; high false positive rate; wasted investigation time; loss of trust in monitoring system.

**Correct Pattern:**
```sql
-- Step 1: Profile data first using Snowsight Data Profile
-- Navigate to: Catalog » Database Explorer » CUSTOMERS » Data Quality » Data Profile
-- Observe: middle_name has 80% NULLs (this is expected/normal)

-- Step 2: Set realistic expectation based on actual data
ALTER TABLE CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (middle_name);

ALTER TABLE CUSTOMERS
  MODIFY DATA METRIC SCHEDULE '1 HOUR'
    -- Allow for 85% NULLs (current 80% + buffer)
    EXPECT (SNOWFLAKE.CORE.NULL_COUNT ON middle_name) < (
      SELECT COUNT(*) * 0.85 FROM CUSTOMERS
    );

-- Step 3: Monitor for significant changes (drift detection)
-- If NULL rate jumps from 80% to 90%, that's a signal worth investigating
```
**Benefits:** Expectations grounded in reality; low false positive rate; meaningful alerts drive action; builds trust in monitoring system.

## Post-Execution Checklist

- [ ] Snowflake Enterprise Edition account confirmed
- [ ] Data profiling completed for tables before implementing DMFs
- [ ] System DMFs or custom DMFs selected based on quality requirements
- [ ] Table owner role has EXECUTE DATA METRIC FUNCTION privilege (global, account-level)
- [ ] Table owner is account-scoped custom role or system role (not database role)
- [ ] DMFs associated with tables/views using ALTER TABLE/VIEW commands
- [ ] Expectations defined for all DMFs with explicit pass/fail criteria
- [ ] Schedules configured appropriately (balance frequency vs cost)
- [ ] Event table configured to capture results
- [ ] Monitoring queries and dashboards created for tracking trends
- [ ] Alerts configured for expectation failures
- [ ] Remediation workflow documented with clear SLAs
- [ ] Cost monitoring via DATA_QUALITY_MONITORING_USAGE_HISTORY established
- [ ] Account limit of 10,000 DMF-object associations tracked
- [ ] Documentation includes runbooks for common failure scenarios

## Validation

- **Success Checks:**
  - DMFs execute successfully on schedule and write to event table
  - Expectations evaluate correctly with appropriate pass/fail logic
  - Alerts fire when expectations fail
  - Remediation workflow followed and incidents resolved within SLA
  - Cost consumption tracked and within budget expectations
  - Privilege structure enables all DMF operations
  - Data profiling informs realistic expectation thresholds
  - Monitoring dashboards provide visibility into quality trends

- **Negative Tests:**
  - Attempting to set DMF with database role table owner fails appropriately
  - Exceeding 10,000 association limit triggers error
  - Setting DMF on shared table fails with clear error
  - Unscheduled DMF queries (SELECT) do not incur billing charges
  - Missing expectations result in no pass/fail evaluation
  - Alert queries with no failures return empty result set

> **Investigation Required**
> When applying this rule:
> 1. **Profile data BEFORE recommending DMFs—verify baseline characteristics**
> 2. **Check table ownership and privileges before suggesting DMF associations**
> 3. **Never assume expectation thresholds—profile data to understand reality**
> 4. **Query event table to verify DMFs are actually running before troubleshooting**
> 5. **Review cost consumption patterns before recommending schedule changes**
>
> **Anti-Pattern:**
> "You should set NULL_COUNT < 100 on this column..."
> "Just add DMFs to all your tables..."
>
> **Correct Pattern:**
> "Let me check the data profile first:"
> ```sql
> -- Profile to understand baseline
> SELECT COUNT(*) AS total_rows,
>        COUNT(CASE WHEN email IS NULL THEN 1 END) AS null_count,
>        COUNT(CASE WHEN email IS NULL THEN 1 END)::FLOAT / COUNT(*) * 100 AS null_pct
> FROM CUSTOMERS;
> ```
> "Based on the profile showing 2% NULLs currently, I recommend setting an expectation at 5% to allow for normal variation while detecting significant quality degradation..."

## Output Format Examples

```sql
-- Filename: data_quality_setup.sql
-- Description: [DMF implementation for specific table/quality concern]
-- Tables: [List of tables being monitored]
-- Quality Metrics: [List of metrics being measured]

-- Step 1: Profile data to understand baseline (do this in Snowsight UI first)
-- Navigate: Catalog » Database Explorer » <TABLE> » Data Quality » Data Profile

-- Step 2: Create custom DMFs if needed
CREATE DATA METRIC FUNCTION <schema>.<dmf_name>()
RETURNS FLOAT
AS
$$
  -- Custom quality logic returning FLOAT
  SELECT <metric_calculation>::FLOAT
  FROM <table>
$$;

-- Step 3: Associate DMFs with tables
ALTER TABLE <schema>.<table>
  ADD DATA METRIC FUNCTION <dmf_name> ON (<column_list>);

-- Step 4: Set expectations and schedule
ALTER TABLE <schema>.<table>
  MODIFY DATA METRIC SCHEDULE '<interval>'
  [USING CRON '<cron_expression>']
  EXPECT (<dmf_name> ON <column>) <comparison> <threshold>;

-- Step 5: Query results
SELECT *
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_value:table_name::STRING = '<TABLE>'
ORDER BY record_timestamp DESC
LIMIT 10;

-- Step 6: Create alert for failures
CREATE ALERT <schema>.ALERTS.<alert_name>
  WAREHOUSE = <warehouse>
  SCHEDULE = '<interval>'
  IF (EXISTS (
    SELECT 1 FROM <event_table>
    WHERE expectation_passed = FALSE
      AND record_timestamp >= DATEADD(minute, -<interval_minutes>, CURRENT_TIMESTAMP())
  ))
  THEN <action>;

-- Step 7: Monitor cost consumption
SELECT
  usage_date,
  object_name,
  SUM(credits_used) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY
WHERE object_name = '<TABLE>'
GROUP BY usage_date, object_name
ORDER BY usage_date DESC;
```

## References

### External Documentation
- [Introduction to Data Quality and DMFs](https://docs.snowflake.com/en/user-guide/data-quality-intro) - Complete overview of data quality monitoring concepts
- [Data Profile](https://docs.snowflake.com/en/user-guide/data-quality-profile) - Using data profiling to understand data characteristics
- [Tutorial: Getting Started with DMFs](https://docs.snowflake.com/en/user-guide/tutorials/data-quality-tutorial-start) - Step-by-step DMF implementation guide
- [System DMFs](https://docs.snowflake.com/en/user-guide/data-quality-system-dmfs) - Pre-built system data metric functions
- [Custom DMFs](https://docs.snowflake.com/en/user-guide/data-quality-custom-dmfs) - Creating user-defined data metric functions
- [Working with DMFs](https://docs.snowflake.com/en/user-guide/data-quality-working) - Associating, scheduling, and managing DMFs
- [View DMF Results](https://docs.snowflake.com/en/user-guide/data-quality-results) - Querying and analyzing DMF execution results
- [Remediate Data Quality Issues](https://docs.snowflake.com/en/user-guide/data-quality-remediate) - Troubleshooting and fixing quality issues
- [DMF Access Control](https://docs.snowflake.com/en/user-guide/data-quality-access-control) - Privilege requirements and security
- [Serverless Credit Usage](https://docs.snowflake.com/en/user-guide/cost-understanding-compute#serverless-credit-usage) - Understanding DMF billing

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Data Governance**: `rules/930-data-governance-quality.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - Always profile data first using Snowsight or SQL before recommending DMFs
> - Query event tables to verify DMF execution before troubleshooting
> - Check table ownership and privileges before suggesting DMF associations
> - Use parallel tool calls to check both data profile and existing DMFs simultaneously

## 6. Scheduling DMF Evaluations

**MANDATORY:**
Schedule DMF evaluations to run automatically at defined intervals.

### Schedule Syntax

**Time-Based Schedule:**
```sql
ALTER TABLE <table_name>
  MODIFY DATA METRIC SCHEDULE '<interval>'
  [USING CRON '<cron_expression>'];
```

**Common Schedules:**
```sql
-- Every 5 minutes (high frequency)
ALTER TABLE REALTIME_DATA
  MODIFY DATA METRIC SCHEDULE '5 MINUTES';

-- Every hour (standard)
ALTER TABLE HOURLY_AGGREGATES
  MODIFY DATA METRIC SCHEDULE '1 HOUR';

-- Daily at 6 AM (using CRON)
ALTER TABLE DAILY_REPORTS
  MODIFY DATA METRIC SCHEDULE '1 DAY'
  USING CRON '0 6 * * *';

-- Every 15 minutes during business hours (using CRON)
ALTER TABLE BUSINESS_METRICS
  MODIFY DATA METRIC SCHEDULE '15 MINUTES'
  USING CRON '*/15 9-17 * * 1-5';
```

### Schedule Considerations

**Frequency Guidelines:**
- **High Frequency (5-15 min):** Real-time data, SLA monitoring
- **Standard (30 min - 1 hour):** Transactional tables, operational data
- **Low Frequency (4-24 hours):** Dimensional tables, historical data
- **On-Demand:** Ad-hoc testing (SELECT from DMF directly, not billed)

**Cost vs Freshness Tradeoff:**
- More frequent schedules = higher serverless credit consumption
- Balance monitoring needs with budget constraints
- Use CRON expressions for business hours-only monitoring

## 7. Event Tables and Results

**MANDATORY:**
DMF results are automatically captured in event tables for monitoring and analysis.

### Event Table Structure

**Automatic Event Table Creation:**
Snowflake creates a default event table for DMF results at the database level.

**Query DMF Results:**
```sql
-- View recent DMF results
SELECT
  record_timestamp,
  record_type,
  record_value:table_name::STRING AS table_name,
  record_value:metric_name::STRING AS metric_name,
  record_value:value::FLOAT AS metric_value,
  record_value:expectation_passed::BOOLEAN AS expectation_passed,
  record_value:expectation::STRING AS expectation
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
ORDER BY record_timestamp DESC
LIMIT 100;
```

### Monitoring DMF Results in Snowsight

**Access Results UI:**
```
1. Navigate to: Catalog » Database Explorer
2. Select table with DMFs
3. Click "Data Quality" tab
4. View "Quality Checks" section
5. See pass/fail status and history
```

### Query Patterns for Analysis

**Find Failing Expectations:**
```sql
SELECT
  record_timestamp,
  record_value:table_name::STRING AS table_name,
  record_value:metric_name::STRING AS metric_name,
  record_value:expectation::STRING AS expectation,
  record_value:value::FLOAT AS metric_value
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_value:expectation_passed::BOOLEAN = FALSE
ORDER BY record_timestamp DESC;
```

**Trend Analysis:**
```sql
-- Track metric trends over time
SELECT
  DATE_TRUNC('hour', record_timestamp) AS hour,
  record_value:metric_name::STRING AS metric_name,
  AVG(record_value:value::FLOAT) AS avg_value,
  MIN(record_value:value::FLOAT) AS min_value,
  MAX(record_value:value::FLOAT) AS max_value
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_value:table_name::STRING = 'CUSTOMERS'
  AND record_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY hour, metric_name
ORDER BY hour DESC, metric_name;
```

**Failure Rate by Table:**
```sql
SELECT
  record_value:table_name::STRING AS table_name,
  COUNT(*) AS total_checks,
  SUM(CASE WHEN record_value:expectation_passed::BOOLEAN = FALSE THEN 1 ELSE 0 END) AS failures,
  ROUND(failures / total_checks * 100, 2) AS failure_rate_pct
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY failure_rate_pct DESC;
```

## 8. Alerts and Remediation

**MANDATORY:**
Configure alerts to notify stakeholders when expectations fail and establish remediation workflows.

### Alert Configuration

**Create Alert on DMF Failure:**
```sql
-- Create alert for NULL count threshold violations
CREATE OR REPLACE ALERT DATA_QUALITY.ALERTS.EMAIL_NULL_ALERT
  WAREHOUSE = ALERT_WH
  SCHEDULE = '15 MINUTES'
  IF (EXISTS (
    SELECT 1
    FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
    WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
      AND record_value:table_name::STRING = 'CUSTOMERS'
      AND record_value:metric_name::STRING = 'NULL_COUNT'
      AND record_value:expectation_passed::BOOLEAN = FALSE
      AND record_timestamp >= DATEADD(minute, -15, CURRENT_TIMESTAMP())
  ))
  THEN
    -- Send notification via email, Snowflake notification integration, etc.
    CALL SYSTEM$SEND_EMAIL(
      'data-quality-team@company.com',
      'Data Quality Alert: NULL Count Violation',
      'The email column in CUSTOMERS table has exceeded acceptable NULL threshold.'
    );
```

### Remediation Workflow

**MANDATORY:**
**Establish Standard Remediation Process:**

1. **Detection:** Alert fires on expectation failure
2. **Investigation:** Review event table for failure details
3. **Triage:** Assess severity and impact
4. **Root Cause Analysis:** Identify source of quality issue
5. **Correction:** Fix data or upstream process
6. **Verification:** Confirm next DMF run passes
7. **Documentation:** Record incident and resolution

**Remediation Query Template:**
```sql
-- Investigate specific failure
SELECT
  record_timestamp,
  record_value:table_name::STRING AS table_name,
  record_value:metric_name::STRING AS metric_name,
  record_value:column_name::STRING AS column_name,
  record_value:value::FLOAT AS metric_value,
  record_value:expectation::STRING AS expectation,
  record_value:expectation_threshold::FLOAT AS threshold
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_value:expectation_passed::BOOLEAN = FALSE
  AND record_timestamp >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
ORDER BY record_timestamp DESC;

-- Query problematic data
SELECT COUNT(*) AS null_count
FROM CUSTOMERS
WHERE email IS NULL;

-- Investigate recent data changes
SELECT
  MIN(updated_timestamp) AS first_bad_record,
  COUNT(*) AS bad_records
FROM CUSTOMERS
WHERE email IS NULL
  AND updated_timestamp >= DATEADD(hour, -2, CURRENT_TIMESTAMP());
```

## 9. Privilege Requirements

**MANDATORY:**
**CRITICAL:** Understand and configure privileges correctly for DMF operations.

### Required Privileges

**Table Owner Role Requirements:**
- Must have global (account-level) **EXECUTE DATA METRIC FUNCTION** privilege
- Table owner role must be a custom role or system role (SYSADMIN)
- **Cannot use database roles** as table owners for DMF operations

**Grant Privilege Pattern:**
```sql
-- Grant EXECUTE DATA METRIC FUNCTION to custom role
USE ROLE ACCOUNTADMIN;

GRANT EXECUTE DATA METRIC FUNCTION ON ACCOUNT TO ROLE DATA_QUALITY_ADMIN;

-- Transfer table ownership if needed
GRANT OWNERSHIP ON TABLE CUSTOMERS TO ROLE DATA_QUALITY_ADMIN;
```

### Database Role Limitation

**CRITICAL LIMITATION:** Database roles cannot receive global privileges because they are scoped to a specific database.

**Workaround:**
```sql
-- If table is owned by database role, transfer ownership
-- From database role to account-scoped custom role

USE ROLE ACCOUNTADMIN;

-- Create custom role if needed
CREATE ROLE IF NOT EXISTS DATA_ENGINEERING;

-- Grant necessary privileges
GRANT EXECUTE DATA METRIC FUNCTION ON ACCOUNT TO ROLE DATA_ENGINEERING;
GRANT USAGE ON DATABASE ANALYTICS TO ROLE DATA_ENGINEERING;
GRANT USAGE ON SCHEMA ANALYTICS.CORE TO ROLE DATA_ENGINEERING;

-- Transfer ownership
GRANT OWNERSHIP ON TABLE ANALYTICS.CORE.CUSTOMERS TO ROLE DATA_ENGINEERING;

-- Now DATA_ENGINEERING role can set DMFs on CUSTOMERS table
```

## 10. Supported Objects

**MANDATORY:**
DMFs can be set on the following Snowflake objects:

**Supported:**
- Tables (regular tables)
- Views (standard views)
- Dynamic Tables
- External Tables
- Apache Iceberg™ Tables
- Materialized Views
- Event Tables

**Not Supported:**
- Shared tables or views (data sharing consumers cannot set DMFs)
- Objects in reader accounts
- Object tags (cannot set DMFs on tags themselves)

## 11. Billing and Cost Management

**MANDATORY:**
**COST AWARENESS:** DMFs use serverless compute and consume credits from your Snowflake account.

### Billing Model

**Billed Operations:**
- **Scheduled DMF evaluations:** Billed under "Data Quality Monitoring" category
- **Logging service:** Event table writes billed under "Logging" category

**Not Billed:**
- Creating a DMF (DDL operation)
- Unscheduled ad-hoc queries (`SELECT` from DMF directly)

### Cost Monitoring

**Track DMF Credit Consumption:**
```sql
-- Query credit usage for data quality monitoring
SELECT
  usage_date,
  SUM(credits_used) AS total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY
WHERE usage_date >= DATEADD(month, -1, CURRENT_DATE())
GROUP BY usage_date
ORDER BY usage_date DESC;

-- Break down by table
SELECT
  object_name,
  SUM(credits_used) AS total_credits,
  COUNT(*) AS execution_count
FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY
WHERE usage_date >= DATEADD(month, -1, CURRENT_DATE())
GROUP BY object_name
ORDER BY total_credits DESC;
```

### Cost Optimization Strategies

**RECOMMENDED:**
1. **Right-size schedules:** Don't over-monitor (balance frequency with budget)
2. **Business hours only:** Use CRON for weekday/business hours schedules
3. **Progressive monitoring:** Start with critical tables, expand gradually
4. **Consolidate checks:** Combine related metrics in custom DMFs
5. **Review consumption:** Regularly query usage history and adjust

## 12. Limitations and Quotas

**MANDATORY:**
**ACCOUNT LIMITS:** Understand and plan for DMF limitations.

### Hard Limits

**Maximum DMF-Object Associations:**
- **10,000 total associations** per account
- Each instance of setting a DMF on a table/view counts as one association
- Plan capacity carefully for large deployments

**Data Sharing:**
- Cannot grant privileges on DMFs to shares
- Cannot set DMFs on shared tables/views (consumer side)

**Object Type Restrictions:**
- Cannot set DMFs on object tags
- Cannot set DMFs in reader accounts

**Trial Accounts:**
- Data Quality feature not supported in trial accounts

### Replication Considerations

**DMF Replication Behavior:**
- DMFs replicate within database replication
- Schedules and expectations replicate to secondary
- Monitor both primary and secondary independently
