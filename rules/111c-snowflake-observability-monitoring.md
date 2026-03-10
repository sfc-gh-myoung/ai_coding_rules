# Snowflake Observability: Monitoring and Analysis

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:monitoring, kw:metrics
**Keywords:** Copy History, Task History, Dynamic Tables, cost management, troubleshooting, performance analysis, monitor queries, monitoring dashboard, telemetry volume, SQL
**TokenBudget:** ~4100
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 111-snowflake-observability-core.md
**Companions:** 111d-snowflake-observability-snowsight.md

## Scope

**What This Rule Covers:**
Monitoring, analysis, and cost management for Snowflake observability. Covers monitoring query patterns, troubleshooting workflows, System Views vs Event Tables selection, and telemetry cost optimization.

**When to Load This Rule:**
- Creating monitoring queries and dashboards
- Troubleshooting performance or errors
- Setting up proactive alerts
- Optimizing telemetry volume and costs

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **111-snowflake-observability-core.md** - Telemetry configuration and event tables

**Related:**
- **111a-snowflake-observability-logging.md** - Logging best practices
- **111b-snowflake-observability-tracing.md** - Distributed tracing and metrics

### External Documentation

**Monitoring Documentation:**
- [Snowflake Query History](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) - QUERY_HISTORY view reference
- [Snowsight Monitoring](https://docs.snowflake.com/en/user-guide/ui-snowsight-activity) - Snowsight monitoring interfaces
- [Cortex AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-observability) - AI token tracking

## Contract

### Inputs and Prerequisites

- Active event table configured (see `111-snowflake-observability-core.md`)
- Access to ACCOUNT_USAGE schema for System Views
- Snowsight UI access for monitoring dashboards
- Understanding of System Views vs Telemetry distinction (see core rule)

### Mandatory

- SQL queries on `SNOWFLAKE.ACCOUNT_USAGE` schema views
- Snowsight monitoring interfaces (Traces & Logs, Query History, Copy History, Task History)
- Monitoring views and stored procedures
- Alert and notification mechanisms

### Forbidden

- Using System Views (QUERY_HISTORY) for real-time monitoring (45+ min latency)
- Querying event tables with `SELECT *` (always use explicit columns)
- Creating monitoring queries without timestamp filters (full table scan)

### Execution Steps

1. Determine data source (System View historical vs Event Table real-time)
2. Create monitoring queries with explicit columns and timestamp filters
3. Use Snowsight interfaces for operational dashboards
4. Set up proactive alerting for critical error patterns
5. Review cost implications and optimize telemetry volume

### Output Format

- SQL queries with explicit column selection (no `SELECT *`)
- Monitoring views with aggregated metrics
- Snowsight navigation paths for UI access
- Cost analysis queries with estimated storage impact

### Validation

**Pre-Task-Completion Checks:**
- Monitoring queries return expected data
- Snowsight dashboards accessible
- Timestamp filters prevent full table scans
- Cost implications reviewed

**Success Criteria:**
- Queries execute within performance targets
- Dashboards display real-time/historical data correctly
- Alerts trigger on error conditions
- Telemetry volume within budget

### Design Principles

- Use System Views (ACCOUNT_USAGE) for historical analysis and trends (45+ min latency)
- Use Event Tables for real-time monitoring and live debugging (seconds latency)
- Include timestamp filters in monitoring queries to prevent full table scans
- Create reusable monitoring views for common observability queries
- Monitor telemetry data volume and cost implications (DEBUG can generate 10-100x more data)
- Use Snowsight monitoring interfaces for operational dashboards and troubleshooting

### Post-Execution Checklist

- [ ] Data source identified (System View vs Event Table)
- [ ] Monitoring queries created with explicit columns
- [ ] Timestamp filters applied to all queries
- [ ] Snowsight interfaces verified accessible
- [ ] Cost implications reviewed (especially for DEBUG level)
- [ ] Alerts configured for critical patterns
- [ ] Telemetry volume monitored

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using SELECT * in Monitoring Queries**
```sql
-- Bad: SELECT * on large system views
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP());
-- Returns 100+ columns, most unused, slow and expensive!
```
**Problem:** Returns unnecessary columns; slow queries; high compute costs

**Correct Pattern:**
```sql
-- Good: Select only needed columns
SELECT
  query_id,
  query_text,
  user_name,
  warehouse_name,
  execution_status,
  execution_time_ms,
  start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND execution_status = 'FAILED';  -- Additional filters
```
**Benefits:** Fast queries; low costs; focused results

**Anti-Pattern 2: Monitoring Queries Without Timestamp Filters**
```sql
-- Bad: No time filter on large historical table
SELECT warehouse_name, SUM(credits_used)
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
GROUP BY warehouse_name;
-- Scans years of data! Very expensive query!
```
**Problem:** Full table scan; extremely slow; high costs; query timeout

**Correct Pattern:**
```sql
-- Good: Always include timestamp filter for recent data
SELECT
  warehouse_name,
  SUM(credits_used) as total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;
-- Scans only last 30 days, fast and cost-effective
```
**Benefits:** Fast queries; bounded costs; relevant recent data

**Anti-Pattern 3: Using ACCOUNT_USAGE for Real-Time Alerting**
```sql
-- Bad: Real-time alert query on ACCOUNT_USAGE (45 min latency!)
SELECT COUNT(*) as failed_queries
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('minute', -5, CURRENT_TIMESTAMP())
  AND execution_status = 'FAILED';
-- Returns stale data, misses recent failures!
```
**Problem:** 45-minute data latency; stale alerts; missed incidents

**Correct Pattern:**
```sql
-- Good: Use Event Tables for real-time monitoring (<1 min latency)
SELECT COUNT(*) as failed_queries
FROM my_event_table
WHERE timestamp > DATEADD('minute', -5, CURRENT_TIMESTAMP())
  AND record['execution_status']::STRING = 'FAILED';

-- Use ACCOUNT_USAGE for historical analysis only (>45 min old)
SELECT DATE_TRUNC('hour', start_time) as hour,
       COUNT(*) as failed_queries
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time BETWEEN DATEADD('day', -7, CURRENT_DATE())
                     AND DATEADD('hour', -1, CURRENT_TIMESTAMP())
  AND execution_status = 'FAILED'
GROUP BY hour;
```
**Benefits:** Real-time alerting (<1 min); timely incident detection; proper data source selection

**Anti-Pattern 4: Not Monitoring Telemetry Volume and Costs**
```python
# Bad: Enable verbose logging without monitoring costs
import logging
logging.basicConfig(level=logging.DEBUG)  # In production!
# Never check: How much data? What's the cost?
# Costs spiral out of control, surprise bills!
```
**Problem:** Unbounded telemetry costs; surprise budget overruns; no cost visibility

**Correct Pattern:**
```sql
-- Good: Monitor telemetry data volume and costs regularly
-- Check event table size growth
SELECT
  DATE_TRUNC('day', timestamp) as day,
  COUNT(*) as event_count,
  SUM(LENGTH(record::STRING)) as total_bytes
FROM my_event_table
WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY day
ORDER BY day DESC;

-- Monitor serverless credit usage for logging/tracing
SELECT
  service_type,
  DATE_TRUNC('day', start_time) as day,
  SUM(credits_used) as credits
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE service_type IN ('LOGGING', 'DATA_QUALITY_MONITORING')
  AND start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY service_type, day
ORDER BY day DESC;

-- Set alerts when costs exceed thresholds
```
**Benefits:** Cost visibility; budget control; early warning on spending

### Proactive Alerting

- **Rule:** Use `CREATE ALERT` to automate incident detection based on event table conditions.

```sql
-- Alert when error count exceeds threshold in 5-minute window
CREATE OR REPLACE ALERT error_spike_alert
  WAREHOUSE = admin_wh
  SCHEDULE = '5 MINUTE'
  IF (EXISTS (
    SELECT 1 FROM snowflake.account_usage.event_table
    WHERE record_type = 'LOG'
      AND severity_text IN ('ERROR', 'FATAL')
      AND timestamp > DATEADD('minute', -5, CURRENT_TIMESTAMP())
    HAVING COUNT(*) > 10
  ))
  THEN
    CALL SYSTEM$SEND_EMAIL(
      'ops_alerts', 'oncall@example.com',
      'Error Spike Detected', 'More than 10 errors in last 5 minutes.'
    );

ALTER ALERT error_spike_alert RESUME;
```

## Output Format Examples
```sql
-- Monitoring Setup Template

-- Step 1: Create error monitoring view
CREATE OR REPLACE VIEW production_error_monitoring AS
SELECT
    DATE_TRUNC('hour', timestamp) as error_hour,
    resource_attributes:"snow.database.name"::string as database_name,
    resource_attributes:"snow.executable.name"::string as function_name,
    severity_text,
    COUNT(*) as error_count,
    ARRAY_AGG(DISTINCT body LIMIT 10) as sample_error_messages
FROM snowflake.account_usage.event_table
WHERE record_type = 'LOG'
  AND severity_text IN ('ERROR', 'FATAL')
  AND timestamp >= current_timestamp() - INTERVAL '7 days'
GROUP BY 1, 2, 3, 4
ORDER BY error_hour DESC, error_count DESC;

-- Step 2: Create performance monitoring view
CREATE OR REPLACE VIEW function_performance_monitoring AS
SELECT
    resource_attributes:"snow.executable.name"::string as function_name,
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as execution_count,
    AVG(duration_ms) as avg_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms,
    MAX(duration_ms) as max_duration_ms
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND timestamp >= current_timestamp() - INTERVAL '24 hours'
GROUP BY 1, 2
ORDER BY hour DESC, avg_duration_ms DESC;

-- Step 3: Monitor AI costs
-- Note: `resource_attributes:"cortex.function"` is populated only for Cortex AI function calls.
-- Expected values for cortex.function: COMPLETE, EXTRACT, SUMMARIZE, TRANSLATE, SENTIMENT, EMBED, etc.
-- `cortex.tokens` tracks input+output token counts for cost attribution.
CREATE OR REPLACE VIEW ai_cost_monitoring AS
SELECT
    DATE_TRUNC('day', timestamp) as usage_day,
    resource_attributes:"cortex.function"::string as ai_function,
    resource_attributes:"cortex.model"::string as model_name,
    COUNT(*) as invocations,
    SUM(resource_attributes:"cortex.tokens"::number) as total_tokens,
    AVG(duration_ms) as avg_latency_ms
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND resource_attributes:"cortex.function" IS NOT NULL
  AND timestamp >= current_timestamp() - INTERVAL '30 days'
GROUP BY 1, 2, 3
ORDER BY usage_day DESC, total_tokens DESC;

-- Step 4: Estimate telemetry costs
SELECT
    record_type,
    COUNT(*) as record_count,
    COUNT(*) * 1024 / (1024*1024*1024) as estimated_gb,
    DATEDIFF(day, MIN(timestamp), MAX(timestamp)) as retention_days
FROM snowflake.account_usage.event_table
GROUP BY record_type
ORDER BY estimated_gb DESC;
```

## Cost and Volume Management

### Data Volume Control
- **Rule:** Implement strategies to control telemetry data volume and associated storage costs.
- **Always:** Use WARN or higher in production; use DEBUG only in development or targeted debugging sessions.

> For the `log_with_sampling()` helper function and sampling strategies, see `111a-snowflake-observability-logging.md` (Sampling Strategies section).

### Organizational Strategy
- **Rule:** Group production objects under specific databases or schemas for simplified telemetry management.
- **Always:** Set telemetry levels at database/schema level rather than individual objects when possible.

```sql
-- Organize by environment and set appropriate levels
CREATE DATABASE prod_analytics;
CREATE DATABASE dev_analytics;

-- Production: Conservative logging, essential tracing
ALTER DATABASE prod_analytics SET LOG_LEVEL = WARN;
ALTER DATABASE prod_analytics SET TRACE_LEVEL = ON_EVENT;
ALTER DATABASE prod_analytics SET METRIC_LEVEL = ALL;

-- Development: Verbose logging for debugging
ALTER DATABASE dev_analytics SET LOG_LEVEL = DEBUG;
ALTER DATABASE dev_analytics SET TRACE_LEVEL = ALWAYS;
ALTER DATABASE dev_analytics SET METRIC_LEVEL = ALL;
```

### Cost Estimation

See the telemetry cost estimation query in Output Format Examples above (Step 4). Key considerations:
- Event table storage scales with volume and retention period
- Use the estimation query weekly to track growth trends
- Set alerts when estimated_gb exceeds thresholds

## Monitoring and Analysis

### Regular Monitoring Queries
- **Always:** Implement regular monitoring queries to identify issues and performance trends.
- **Rule:** Create views or stored procedures for common observability queries.
- **Templates:** See Output Format Examples above for production-ready error monitoring (`production_error_monitoring`), performance monitoring (`function_performance_monitoring`), AI cost monitoring (`ai_cost_monitoring`), and telemetry cost estimation views.

### Snowsight Dashboard Queries
- **Always:** Use Snowsight to visualize telemetry data and create dashboards for operational monitoring.
- **Rule:** Set up alerts for critical error patterns and performance degradation.

```sql
-- Query for Snowsight dashboard: Error rate by hour
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(CASE WHEN severity_text IN ('ERROR', 'FATAL') THEN 1 END) as errors,
    COUNT(*) as total_logs,
    ROUND(errors / NULLIF(total_logs, 0) * 100, 2) as error_rate_percent
FROM snowflake.account_usage.event_table
WHERE record_type = 'LOG'
  AND timestamp >= current_timestamp() - interval '24 hours'
GROUP BY hour
ORDER BY hour;
```

## Security and Governance Integration

### Telemetry Data Protection
- **Rule:** Grant SELECT on event_table to TELEMETRY_ANALYST role; restrict TELEMETRY_ADMIN for unmasked access.
- **Always:** Consider data masking for sensitive information in log messages.

```sql
-- Create role for telemetry analysis
CREATE ROLE telemetry_analyst;
GRANT SELECT ON snowflake.account_usage.event_table TO ROLE telemetry_analyst;

-- Restrict access to sensitive telemetry data
CREATE OR REPLACE MASKING POLICY log_message_mask AS (val string) RETURNS string ->
  CASE
    WHEN CURRENT_ROLE() IN ('TELEMETRY_ADMIN', 'SYSADMIN') THEN val
    ELSE REGEXP_REPLACE(val, '[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}', 'XXXX-XXXX-XXXX-XXXX')
  END;

-- Apply masking to event table body column (if using custom event table)
ALTER TABLE custom_event_table MODIFY COLUMN body SET MASKING POLICY log_message_mask;
```

## Troubleshooting and Optimization

### Performance Analysis
- **Always:** Use trace data to identify performance bottlenecks and optimize critical paths.
- **Rule:** Correlate telemetry data with query profiles for comprehensive performance analysis.

> For the complete trace-log correlation query and trace analysis patterns, see `111b-snowflake-observability-tracing.md` (Querying Trace Data section).

## Snowsight Monitoring Interfaces

> **See companion rule:** `111d-snowflake-observability-snowsight.md` for Snowsight UI navigation paths (Traces & Logs, Query History, Copy History, Task History, Dynamic Tables), unified monitoring strategy, and AI Agent guidance for each interface.

## AI Observability

> **See companion rule:** `111d-snowflake-observability-snowsight.md` for Cortex AI function monitoring, cost attribution queries, LLM evaluation capabilities, and generative AI application tracing patterns.

## Limitations and Considerations

### Event Table Retention
- **Default:** Retention controlled by `DATA_RETENTION_TIME_IN_DAYS` on event table.
- **Cost Impact:** Longer retention increases storage costs.
- **Rule:** Set retention to 30 days for standard monitoring; extend to 90 days only when compliance regulations (SOX, HIPAA) require it.

### Cost Implications of Verbose Logging
- **DEBUG Level:** Can generate 10-100x more log entries than WARN level.
- **Storage:** Event tables consume storage based on volume and retention.
- **Compute:** Querying large event tables requires warehouse credits.
- **Rule:** Set log level to INFO or WARN in production environments; use DEBUG only for targeted debugging sessions.

### Performance Impact of TRACE_LEVEL = ALWAYS
- **ALWAYS:** Generates trace spans for every function/procedure invocation regardless of errors.
- **Performance:** Minimal overhead (<5% typically); monitor total span count and switch to ON_EVENT if exceeding 1M spans/day.
- **Rule:** Use `ON_EVENT` for production (traces only on errors), `ALWAYS` for debugging.

```sql
-- Production: Trace only on errors
ALTER ACCOUNT SET TRACE_LEVEL = ON_EVENT;

-- Development/Debugging: Trace all executions
ALTER SESSION SET TRACE_LEVEL = ALWAYS;
```

### System View Latency Considerations
- **Query History:** 45 minutes latency
- **Copy History:** 2 hours latency
- **Task History:** 45 minutes latency
- **Metering History:** 2-3 hours latency
- **Implication:** Not suitable for real-time monitoring; use event tables for real-time needs.
