# Snowflake Data Quality: Operations & Monitoring

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:dmf-operations, kw:quality-monitoring
**Keywords:** remediation, RBAC, privilege requirements, automated monitoring, quality alerts, schedule DMF, quality event tables, quality alerting, DMF results, quality workflows, DMF RBAC, quality notifications, remediation workflows
**TokenBudget:** ~4400
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 124-snowflake-data-quality-core.md, 111-snowflake-observability-core.md

## Scope

**What This Rule Covers:**
Operational patterns for Data Quality Monitoring including DMF scheduling, event table analysis, alerting, remediation workflows, and RBAC configuration. Covers automated monitoring, quality event tables, alerting strategies, remediation patterns, and privilege requirements.

**When to Load This Rule:**
- Scheduling DMF evaluations with Snowflake Tasks
- Monitoring DMF results and quality trends
- Configuring alerts and notifications for quality issues
- Defining remediation workflows (automated or manual)
- Setting up RBAC for DMF operations
- Troubleshooting DMF execution or alerting issues

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **124-snowflake-data-quality-core.md** - Data Quality fundamentals
- **111-snowflake-observability-core.md** - Event tables and monitoring patterns

**Related:**
- **124a-snowflake-data-quality-custom.md** - Custom DMF creation
- **104-snowflake-streams-tasks.md** - Task scheduling patterns

### External Documentation

- [DMF Scheduling](https://docs.snowflake.com/en/user-guide/data-quality-schedule) - Scheduling quality evaluations
- [Data Quality Event Tables](https://docs.snowflake.com/en/user-guide/data-quality-events) - Monitoring DMF results
- [Task Management](https://docs.snowflake.com/en/sql-reference/sql/create-task) - Creating scheduled tasks

## Contract

### Inputs and Prerequisites

- DMFs configured from 124-snowflake-data-quality-core or 124a-snowflake-data-quality-custom
- Expectations set with thresholds
- Event tables available for monitoring
- EXECUTE DATA METRIC FUNCTION privilege

### Mandatory

- Schedule DMF evaluations with Tasks
- Configure event tables for results
- Set up alerts for quality violations
- Define remediation workflows
- Configure RBAC with least privilege

### Forbidden

- Scheduling DMF evaluations too frequently (causing compute waste)
- Ignoring event table analysis for quality trends

### Execution Steps

1. Schedule DMF evaluations with Snowflake Tasks
2. Configure event tables to capture DMF results
3. Set up alerts and notifications for violations
4. Define remediation workflows (automated or manual)
5. Configure RBAC with least privilege access

### Output Format

Operational configurations produce:
- Task schedules for DMF evaluations
- Event table queries for monitoring
- Alert configurations
- Remediation workflow definitions
- RBAC grant statements

### Validation

**Pre-Task-Completion Checks:**
- Tasks created and scheduled
- Event tables configured
- Alert thresholds defined

**Success Criteria:**
- Tasks run successfully on schedule
- Alerts trigger correctly on violations
- RBAC enforced with least privilege
- Remediation workflows executed

**Negative Tests:**
- Alerts should not trigger on valid data
- RBAC should deny unauthorized access

### Design Principles

- **Automation:** Schedule DMF evaluations with Tasks
- **Observability:** Monitor event tables for quality trends
- **Proactive alerts:** Configure alerts for critical quality issues
- **Clear remediation:** Define explicit remediation workflows
- **Least privilege:** Enforce RBAC for DMF operations

### Post-Execution Checklist

- [ ] Data profiling completed before implementing DMFs
- [ ] System or custom DMFs selected based on quality requirements
- [ ] Table owner has EXECUTE DATA METRIC FUNCTION privilege (account-level)
- [ ] Table owner is account-scoped custom role (not database role)
- [ ] DMFs associated with tables using ALTER TABLE commands
- [ ] Expectations defined with explicit pass/fail criteria
- [ ] Schedules configured (balance frequency vs cost)
- [ ] Event table configured to capture results
- [ ] Alerts configured for expectation failures
- [ ] Remediation workflow documented with SLAs
- [ ] Cost monitoring via DATA_QUALITY_MONITORING_USAGE_HISTORY established
- [ ] Account limit of 10,000 DMF-object associations tracked

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

**Anti-Pattern 3: No Remediation Workflow**
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

## Scheduling DMF Evaluations

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

## Event Tables and Results

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

Navigate to Catalog > Database Explorer > [table] > Data Quality > Quality Checks for UI-based monitoring. For programmatic access, use the event table queries above.

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

**Failure Rate by Table:**
```sql
SELECT
  record_value:table_name::STRING AS table_name,
  COUNT(*) AS total_checks,
  SUM(CASE WHEN record_value:expectation_passed::BOOLEAN = FALSE THEN 1 ELSE 0 END) AS failures,
  ROUND(SUM(CASE WHEN record_value:expectation_passed::BOOLEAN = FALSE THEN 1 ELSE 0 END)::FLOAT
    / COUNT(*) * 100, 2) AS failure_rate_pct
FROM <database>.INFORMATION_SCHEMA.EVENT_TABLE_HISTORY
WHERE record_type = 'DATA_METRIC_FUNCTION_RESULT'
  AND record_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY failure_rate_pct DESC;
```

## Alerts and Remediation

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
    -- Requires: CREATE NOTIFICATION INTEGRATION dq_email_int TYPE = EMAIL ENABLED = TRUE;
    CALL SYSTEM$SEND_EMAIL(
      'dq_email_int',
      'data-quality-team@company.com',
      'Data Quality Alert: NULL Count Violation',
      'The email column in CUSTOMERS table has exceeded acceptable NULL threshold.'
    );
```

### Remediation Workflow

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
-- Investigate specific failure (use Find Failing Expectations query above for details)
-- Then query the problematic data directly:
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

## Privilege Requirements

Understand and configure privileges correctly for DMF operations.

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

## Supported Objects

**DMFs can be set on:** Tables, Views, Dynamic Tables, External Tables, Apache Iceberg Tables, Materialized Views, Event Tables.

**Not supported:** Shared tables/views (data sharing consumers), reader accounts, object tags.

## Billing and Cost Management

DMFs use serverless compute and consume credits from your Snowflake account.

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

### Cost Optimization

1. **Right-size schedules:** Balance frequency with budget
2. **Business hours only:** Use CRON for weekday/business hours schedules
3. **Progressive monitoring:** Start with critical tables, expand gradually
4. **Consolidate checks:** Combine related metrics in custom DMFs

### Limits and Quotas

- **10,000 total DMF-object associations** per account (plan capacity for large deployments)
- Cannot grant privileges on DMFs to shares or set DMFs on shared tables (consumer side)
- Cannot set DMFs on object tags or in reader accounts
- Data Quality feature not supported in trial accounts
- DMFs replicate within database replication; monitor primary and secondary independently
