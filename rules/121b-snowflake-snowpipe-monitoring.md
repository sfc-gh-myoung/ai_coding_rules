# Snowflake Snowpipe Monitoring and Cost Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-monitoring, kw:pipe-costs
**Keywords:** snowpipe monitoring, cost management, load history, pipe usage, streaming monitoring, channel status, credits tracking, performance metrics, cost optimization, observability, metering history, monitoring queries
**TokenBudget:** ~4000
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 121-snowflake-snowpipe.md, 121a-snowflake-snowpipe-streaming.md

## Scope

**What This Rule Covers:**
Monitoring, cost tracking, and performance analysis for both file-based Snowpipe and Snowpipe Streaming. Covers load history queries, channel status monitoring, credit usage tracking, cost optimization strategies, and alerting patterns for production Snowpipe deployments.

**When to Load This Rule:**
- Setting up monitoring for Snowpipe or Snowpipe Streaming
- Tracking Snowpipe costs and credit usage
- Analyzing load performance and latency
- Creating alerts for pipe failures or high costs
- Optimizing Snowpipe cost efficiency
- Debugging performance issues with existing pipes

**For core Snowpipe setup, see `121-snowflake-snowpipe.md` and `121a-snowflake-snowpipe-streaming.md`**
**For troubleshooting, see `121c-snowflake-snowpipe-troubleshooting.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **121-snowflake-snowpipe.md** - File-based Snowpipe core concepts
- **121a-snowflake-snowpipe-streaming.md** - Streaming Snowpipe core concepts

**Related:**
- **121f-snowflake-snowpipe-monitoring-alerts.md** - Alert configuration and cost optimization
- **121c-snowflake-snowpipe-troubleshooting.md** - Troubleshooting and debugging patterns
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization
- **111-snowflake-observability-core.md** - Logging, tracing, and monitoring patterns

### External Documentation

- [Snowpipe Costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing) - Billing model and cost optimization
- [PIPE_USAGE_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/pipe_usage_history) - Pipe usage monitoring function
- [COPY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/copy_history) - Copy operation history
- [LOAD_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/load_history) - Streaming load history

## Contract

### Inputs and Prerequisites

- Existing Snowpipe or Snowpipe Streaming deployment
- Access to ACCOUNT_USAGE schema for monitoring queries
- Snowflake warehouse for running monitoring queries
- Understanding of Snowpipe billing model
- Alert configuration system (optional, for automated monitoring)

### Mandatory

- PIPE_USAGE_HISTORY queries for file-based Snowpipe monitoring
- LOAD_HISTORY queries for Snowpipe Streaming monitoring
- COPY_HISTORY queries for detailed load analysis
- Cost tracking queries using ACCOUNT_USAGE.METERING_HISTORY
- Error monitoring queries to detect failures
- Performance metrics tracking (latency, throughput, error rates)

### Forbidden

- Monitoring without establishing baseline performance metrics first
- Setting alert thresholds without analyzing historical patterns
- Ignoring cost per GB/file/row metrics
- Monitoring only when issues occur (reactive instead of proactive)
- Using production warehouses for heavy monitoring queries

### Execution Steps

1. Establish baseline metrics by running monitoring queries for 1-2 weeks
2. Implement load history queries for file-based Snowpipe or Snowpipe Streaming
3. Set up cost tracking queries to monitor credit usage per pipe/channel
4. Create error monitoring views to detect load failures
5. Configure performance dashboards with key metrics (latency, throughput, error rates)
6. Set realistic alert thresholds based on baseline analysis
7. Implement automated monitoring tasks (optional, for continuous monitoring)
8. Review cost optimization opportunities based on cost per GB metrics

### Output Format

- SQL queries returning load history, error counts, and performance metrics
- Cost tracking reports showing credits per GB/file/row
- Dashboard queries for real-time pipe/channel health monitoring
- Alert configurations with appropriate thresholds
- Monitoring views for automated error detection

### Validation

**Pre-Task-Completion Checks:**
- [ ] Monitoring queries configured for all pipes/channels
- [ ] Cost tracking queries implemented
- [ ] Alert thresholds defined and configured
- [ ] Dashboard queries tested and validated
- [ ] Error monitoring views created
- [ ] Scheduled tasks for automated monitoring (if applicable)

**Success Criteria:**
- Load history accessible and accurate
- Cost metrics available and tracking correctly
- Alerts triggering appropriately for error conditions
- Performance metrics within expected ranges
- Dashboard queries returning useful insights
- Error rates within acceptable thresholds

### Post-Execution Checklist

- [ ] Baseline performance metrics established (1-2 weeks of data)
- [ ] Load history queries tested and returning accurate data
- [ ] Cost tracking queries implemented for all pipes/channels
- [ ] Error monitoring views created and validated
- [ ] Performance dashboard queries configured
- [ ] Alert thresholds set based on baseline analysis
- [ ] Automated monitoring tasks scheduled (if applicable)
- [ ] Cost optimization opportunities identified and documented
- [ ] Monitoring documentation updated with query patterns

## INFORMATION_SCHEMA vs ACCOUNT_USAGE

**CRITICAL:** Choose the right monitoring source based on your use case:

- **INFORMATION_SCHEMA** (e.g., `TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(...))`)
  - Real-time data, no latency
  - Retention: 14 days
  - Scope: current database only
  - Best for: live debugging, operational monitoring, short-term analysis

- **ACCOUNT_USAGE** (e.g., `SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY`)
  - Up to 45-minute latency
  - Retention: 365 days
  - Scope: entire account (all databases)
  - Best for: trend analysis, cross-database reporting, cost tracking, compliance

**Rule of thumb:** Use INFORMATION_SCHEMA for real-time operational queries. Use ACCOUNT_USAGE for historical analysis and dashboards.

**Time Range Convention:** Adjust `DATEADD` lookback period based on monitoring frequency: `-1 hour` for real-time operational checks, `-7 days` for weekly review, `-30 days` for trend analysis and cost reporting. Examples below use representative defaults.

## File-Based Snowpipe Monitoring

### Load History Queries

**View Recent Loads:**
```sql
-- Get load history for a specific pipe (last 14 days)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP()),
  DATE_RANGE_END => CURRENT_TIMESTAMP(),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
ORDER BY START_TIME DESC;

-- Summary of files loaded per day
SELECT
  DATE_TRUNC('day', START_TIME) AS load_date,
  COUNT(*) AS num_loads,
  SUM(FILES_INSERTED) AS total_files,
  SUM(ROWS_INSERTED) AS total_rows,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb,
  AVG(BYTES_INSERTED / NULLIF(FILES_INSERTED, 0)) AS avg_file_size_bytes
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -30, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY load_date DESC;
```

**Check for Errors:**
```sql
-- Find loads with errors
SELECT
  START_TIME,
  FILES_INSERTED,
  ROWS_INSERTED,
  ERROR_COUNT,
  ERROR_LIMIT,
  FIRST_ERROR_MESSAGE,
  FIRST_ERROR_LINE_NUMBER,
  FIRST_ERROR_CHARACTER_POS,
  FIRST_ERROR_COLUMN_NAME
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
WHERE ERROR_COUNT > 0
ORDER BY START_TIME DESC;
```

### Copy History for Snowpipe

```sql
-- Query COPY_HISTORY for Snowpipe loads
SELECT
  TABLE_NAME,
  STAGE_LOCATION,
  FILE_NAME,
  FILE_SIZE,
  ROW_COUNT,
  ROW_PARSED,
  FIRST_ERROR_MESSAGE,
  FIRST_ERROR_LINE_NUMBER,
  LAST_LOAD_TIME,
  STATUS
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE TABLE_NAME = 'RAW_EVENTS'
  AND PIPE_NAME = 'PIPE_LOAD_RAW_EVENTS'
  AND LAST_LOAD_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY LAST_LOAD_TIME DESC;
```

### Error Monitoring

```sql
-- Find loads with errors (real-time, last 1 hour)
SELECT
  pipe_name, file_name, last_load_time, status,
  row_count, row_parsed, first_error_message, error_count
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET_TABLE',
  START_TIME => DATEADD(HOUR, -1, CURRENT_TIMESTAMP())
))
WHERE status = 'LOAD_FAILED' OR error_count > 0
ORDER BY last_load_time DESC;
```

For scheduled error monitoring tasks and ALERT objects, see **121f-snowflake-snowpipe-monitoring-alerts.md**.

## Snowpipe Streaming Monitoring

### Channel Status

```sql
-- Query channel status
SELECT
  channel_name,
  table_name,
  offset_token,
  row_count,
  start_time,
  last_commit_time
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'MY_DB'
  AND schema_name = 'MY_SCHEMA'
ORDER BY last_commit_time DESC;
```

### Streaming Load History

```sql
-- Query streaming load history
SELECT
  table_name,
  channel_name,
  row_count,
  bytes_received,
  start_time,
  end_time,
  DATEDIFF(second, start_time, end_time) AS latency_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE table_name = 'MY_TABLE'
  AND start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

### Channel Health Check

```sql
-- Channel health check
SELECT
  channel_name,
  table_name,
  last_commit_time,
  DATEDIFF(minute, last_commit_time, CURRENT_TIMESTAMP()) AS minutes_since_last_commit,
  row_count,
  CASE
    WHEN DATEDIFF(minute, last_commit_time, CURRENT_TIMESTAMP()) > 10 THEN 'STALLED'
    WHEN DATEDIFF(minute, last_commit_time, CURRENT_TIMESTAMP()) > 5 THEN 'WARNING'
    ELSE 'HEALTHY'
  END AS channel_status
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'MY_DB'
  AND schema_name = 'MY_SCHEMA'
ORDER BY minutes_since_last_commit DESC;
```

## Cost Management

### File-Based Snowpipe Billing

**How Snowpipe is billed:**
- Billed based on **compute resources used** in the Snowpipe warehouse
- Charged per-second with a 1-minute minimum per compute cluster
- Separate from user warehouse credits
- Costs appear in `SNOWPIPE` usage type in `ACCOUNT_USAGE.METERING_HISTORY`

**Cost Monitoring Query:**
```sql
-- Daily Snowpipe costs (last 30 days)
SELECT
  DATE_TRUNC('day', START_TIME) AS usage_date,
  SUM(CREDITS_USED) AS snowpipe_credits,
  COUNT(DISTINCT PIPE_NAME) AS num_pipes,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb_loaded
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY usage_date DESC;

-- Cost per pipe
SELECT
  PIPE_NAME,
  SUM(CREDITS_USED) AS total_credits,
  SUM(FILES_INSERTED) AS total_files,
  SUM(ROWS_INSERTED) AS total_rows,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(FILES_INSERTED), 0), 6) AS credits_per_file,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(BYTES_INSERTED) / POWER(1024, 3), 0), 4) AS credits_per_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY PIPE_NAME
ORDER BY total_credits DESC;
```

### Snowpipe Streaming Billing

**How Snowpipe Streaming is billed:**
- Billed based on **compute resources used** for ingestion
- Charged per-second with a 1-minute minimum per compute cluster
- Separate from user warehouse credits
- Costs appear in `SNOWPIPE_STREAMING` usage type in `ACCOUNT_USAGE.METERING_HISTORY`

**Cost Monitoring Query:**
```sql
-- Daily Snowpipe Streaming costs (last 30 days)
SELECT
  DATE_TRUNC('day', START_TIME) AS usage_date,
  SUM(CREDITS_USED) AS streaming_credits,
  COUNT(DISTINCT CHANNEL_NAME) AS num_channels,
  SUM(BYTES_RECEIVED) / POWER(1024, 3) AS total_gb_loaded
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND LOAD_TYPE = 'SNOWPIPE_STREAMING'
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY usage_date DESC;

-- Cost per channel
SELECT
  CHANNEL_NAME,
  SUM(CREDITS_USED) AS total_credits,
  SUM(ROW_COUNT) AS total_rows,
  SUM(BYTES_RECEIVED) / POWER(1024, 3) AS total_gb,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(ROW_COUNT), 0) * 1000000, 6) AS credits_per_million_rows,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(BYTES_RECEIVED) / POWER(1024, 3), 0), 4) AS credits_per_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND LOAD_TYPE = 'SNOWPIPE_STREAMING'
GROUP BY CHANNEL_NAME
ORDER BY total_credits DESC;
```

## Cost Optimization and Alerting

For cost optimization strategies (file sizing, batching, channel efficiency) and alert configuration (ALERT objects, SYSTEM$SEND_EMAIL, scheduled monitoring tasks), see **121f-snowflake-snowpipe-monitoring-alerts.md**.

**Quick Reference:**
- Optimal file size: 100-250MB compressed (avoid micro-files <1MB)
- Alert on error rates: >5% for file-based Snowpipe, >1% for Streaming
- Alert on stalled channels: no commits in 15+ minutes

## Design Principles

- **Proactive Monitoring:** Monitor continuously, not reactively
- **Cost Awareness:** Track costs per GB/file/row to identify optimization opportunities
- **Error Detection:** Catch errors early with automated monitoring
- **Performance Tracking:** Measure latency and throughput continuously
- **Alert Fatigue:** Set appropriate thresholds to avoid alert noise
- **Historical Analysis:** Retain monitoring data for trend analysis

> **Investigation Required**
> When setting up monitoring:
> 1. **Establish baselines FIRST** - Run queries for 1-2 weeks to understand normal patterns
> 2. **Set realistic thresholds** - Base alerts on actual performance, not assumptions
> 3. **Monitor cost trends** - Track cost per GB over time to detect inefficiencies
> 4. **Review error patterns** - Analyze error types to identify systemic issues
> 5. **Test alerts** - Verify alert logic triggers correctly before production deployment

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Setting Static Alert Thresholds Without Baseline Analysis

**Problem:** Configuring alert thresholds (e.g., "alert if latency >5 seconds") based on assumptions or arbitrary values instead of analyzing actual performance patterns over time.

**Why It Fails:** Causes alert fatigue with false positives when normal patterns exceed arbitrary thresholds, misses real issues when thresholds are too high, and wastes time investigating non-issues. Static thresholds don't account for workload variations or growth.

**Correct Pattern:**
```sql
-- BAD: Arbitrary threshold without baseline
CREATE ALERT snowpipe_latency_alert IF (SELECT AVG(latency_seconds) FROM METRICS) > 5;

-- GOOD: Baseline-driven threshold with percentile analysis
-- Step 1: Establish baseline (run for 1-2 weeks)
SELECT 
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_seconds) as p95_latency
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE start_time >= DATEADD(day, -14, CURRENT_TIMESTAMP());
-- Results: p95=8.3s

-- Step 2: Set threshold above p95 to catch anomalies
CREATE ALERT snowpipe_latency_alert IF (SELECT AVG(latency_seconds) FROM METRICS) > 10;
```

### Anti-Pattern 2: Monitoring Only Load Success Without Cost Tracking

**Problem:** Tracking file ingestion counts and success rates but ignoring credit consumption, cost per GB, and warehouse utilization patterns.

**Why It Fails:** Snowpipe costs can spiral uncontrollably without cost monitoring, inefficient file sizes waste credits, and lack of cost visibility prevents optimization opportunities. Success metrics alone don't indicate cost efficiency.

**Correct Pattern:**
```sql
-- BAD: Only success monitoring
SELECT pipe_name, COUNT(*) as files_loaded
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
GROUP BY pipe_name;

-- GOOD: Combined success and cost monitoring
SELECT 
  pipe_name,
  COUNT(*) as files_loaded,
  SUM(bytes_loaded) / POWER(1024, 3) as gb_loaded,
  SUM(credits_used) as total_credits,
  SUM(credits_used) / NULLIF(SUM(bytes_loaded) / POWER(1024, 3), 0) as cost_per_gb,
  CASE 
    WHEN SUM(credits_used) / NULLIF(SUM(bytes_loaded) / POWER(1024, 3), 0) > 0.5 
    THEN 'WARNING: High cost per GB'
    ELSE 'OK'
  END as efficiency_flag
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
GROUP BY pipe_name
ORDER BY total_credits DESC;
```
