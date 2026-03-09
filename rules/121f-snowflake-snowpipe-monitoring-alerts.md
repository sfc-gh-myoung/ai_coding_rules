# Snowpipe Monitoring Alerts and Cost Optimization

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-alerts, kw:pipe-alerts, kw:pipe-cost-optimization
**Keywords:** snowpipe alerts, pipe error alerts, channel stall alerts, cost optimization, file size optimization, streaming optimization, alert thresholds, SYSTEM$SEND_EMAIL, monitoring tasks, performance metrics
**TokenBudget:** ~3100
**ContextTier:** Medium
**Depends:** 121b-snowflake-snowpipe-monitoring.md, 121-snowflake-snowpipe.md

## Scope

**What This Rule Covers:**
Alert configuration for Snowpipe and Snowpipe Streaming (error alerts, stall detection, SLA monitoring), cost optimization strategies for both file-based and streaming ingestion, and performance metric tracking guidance.

**When to Load This Rule:**
- Setting up automated alerts for pipe failures or stalled channels
- Optimizing Snowpipe or Snowpipe Streaming costs
- Configuring SYSTEM$SEND_EMAIL notifications for pipe monitoring
- Establishing performance metric thresholds
- Creating scheduled monitoring tasks

### Quantification Standards

**Performance Thresholds:**
- **File-based error rate alert:** >5% of files with errors
- **Streaming error rate alert:** >1% of rows with errors
- **Channel stall threshold:** No commits in 15+ minutes
- **Optimal file size:** 100-250MB compressed for file-based Snowpipe
- **Minimum file size:** Avoid micro-files (<1MB)

> **Investigation Required**
> When configuring alerts:
> 1. **Establish baselines FIRST** - Run monitoring queries for 1-2 weeks before setting thresholds
> 2. **Set realistic thresholds** - Base alerts on actual p95 performance, not assumptions
> 3. **Verify notification integration** - Test SYSTEM$SEND_EMAIL with `pipe_notify_int` before deploying
> 4. **Avoid alert fatigue** - Start with critical alerts only, add more as needed
>
> **Anti-Pattern:**
> "Setting alert threshold to 5 seconds latency based on assumptions..."
>
> **Correct Pattern:**
> "Let me check your baseline p95 latency first."
> [runs percentile query on 14 days of data]
> "Your p95 is 8.3s, so I'll set the alert threshold at 10s to catch anomalies..."

## References

### Dependencies

**Must Load First:**
- **121b-snowflake-snowpipe-monitoring.md** - Core monitoring queries and cost tracking
- **121-snowflake-snowpipe.md** - File-based Snowpipe core concepts

**Related:**
- **121a-snowflake-snowpipe-streaming.md** - Streaming Snowpipe core concepts
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization
- **111-snowflake-observability-core.md** - Logging, tracing, and monitoring patterns

### External Documentation

- [Snowpipe Costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing) - Billing model and cost optimization
- [Snowflake Alerts](https://docs.snowflake.com/en/user-guide/alerts) - Alert object creation and management

## Contract

### Inputs and Prerequisites

- Existing Snowpipe monitoring setup (per 121b)
- Notification integration configured (SYSTEM$SEND_EMAIL)
- Baseline performance data (1-2 weeks minimum)
- Monitoring warehouse (separate from production)

### Mandatory

- Alerts based on baseline analysis, not arbitrary thresholds
- SYSTEM$SEND_EMAIL with configured notification integration
- Scheduled monitoring tasks on dedicated monitoring warehouse

### Forbidden

- Setting alert thresholds without baseline analysis
- Using production warehouses for monitoring tasks
- Ignoring alert fatigue (too many low-value alerts)

### Execution Steps

1. Establish baseline metrics (run monitoring queries for 1-2 weeks)
2. Calculate p95 thresholds from baseline data
3. Create notification integration for email alerts
4. Deploy ALERT objects for pipe errors and channel stalls
5. Configure scheduled monitoring tasks
6. Review cost optimization opportunities based on cost per GB metrics
7. Implement file size and batching optimizations

### Output Format

SQL ALERT object definitions, scheduled TASK definitions, and cost optimization recommendations.

### Validation

**Pre-Task-Completion Checks:**
- Baseline data collected (minimum 1 week)
- Alert thresholds derived from baseline percentiles
- Notification integration tested
- Monitoring warehouse configured

**Success Criteria:**
- Alerts trigger on genuine issues (no false positives in first week)
- Cost per GB trending downward after optimizations
- No alert fatigue reported by operations team

**Negative Tests:**
- Alerts do not fire during normal load patterns
- Missing notification integration raises clear error
- Invalid thresholds caught during ALERT creation

### Post-Execution Checklist

- [ ] Baseline metrics established from 1-2 weeks of data
      Verify: Run percentile queries on PIPE_USAGE_HISTORY -- confirm p95 values available
- [ ] Alert thresholds set above p95 baseline values
      Verify: Compare alert threshold to baseline p95 -- threshold should be 1.2-1.5x p95
- [ ] Notification integration tested with SYSTEM$SEND_EMAIL
      Verify: Send test email -- confirm delivery
- [ ] Pipe error alert deployed and resumed
      Verify: `SHOW ALERTS IN SCHEMA MONITORING.ALERTS;` -- status is 'started'
- [ ] Channel stall alert deployed and resumed (if using Streaming)
      Verify: `SHOW ALERTS IN SCHEMA MONITORING.ALERTS;` -- status is 'started'
- [ ] Cost optimization strategies implemented
      Verify: Check file sizes are 100-250MB compressed -- review cost per GB trend

## Alert Configuration

**Set up alerts for:**
- Pipes in error state or paused unexpectedly
- Channels in error state or stalled
- High error rates (>5% of files for Snowpipe, >1% of rows for Streaming)
- Load latency exceeding SLAs
- Significant changes in file counts, row counts, or sizes
- Pipes/channels consuming excessive compute credits

### Pipe Error Alert

```sql
-- Alert on pipe load errors (INFORMATION_SCHEMA for real-time)
CREATE OR REPLACE ALERT MONITORING.ALERTS.PIPE_ERROR_ALERT
  WAREHOUSE = MONITORING_WH
  SCHEDULE = '5 MINUTES'
  IF (EXISTS (
    SELECT 1 FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
      TABLE_NAME => 'TARGET_TABLE',
      START_TIME => DATEADD(MINUTE, -10, CURRENT_TIMESTAMP())
    )) WHERE STATUS = 'LOAD_FAILED'
  ))
  THEN CALL SYSTEM$SEND_EMAIL(
    'pipe_notify_int', 'data-eng@company.com',
    'Snowpipe Load Failure', 'Pipe load failures detected in last 10 minutes.'
  );

ALTER ALERT MONITORING.ALERTS.PIPE_ERROR_ALERT RESUME;
```

### Channel Stall Alert

```sql
-- Alert on stalled streaming channels (ACCOUNT_USAGE for cross-database)
CREATE OR REPLACE ALERT MONITORING.ALERTS.CHANNEL_STALL_ALERT
  WAREHOUSE = MONITORING_WH
  SCHEDULE = '15 MINUTES'
  IF (EXISTS (
    SELECT 1 FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
    WHERE DATEDIFF(MINUTE, LAST_COMMIT_TIME, CURRENT_TIMESTAMP()) > 15
      AND DATABASE_NAME = 'MY_DB'
  ))
  THEN CALL SYSTEM$SEND_EMAIL(
    'pipe_notify_int', 'data-eng@company.com',
    'Streaming Channel Stalled', 'One or more channels have not committed in 15+ minutes.'
  );

ALTER ALERT MONITORING.ALERTS.CHANNEL_STALL_ALERT RESUME;
```

### Scheduled Error Monitoring Task

```sql
-- Create monitoring view for pipe errors
CREATE OR REPLACE VIEW pipe_error_monitoring AS
SELECT
  pipe_name, file_name, last_load_time, status,
  row_count, row_parsed, first_error_message,
  first_error_line_number, error_count, error_limit
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET_TABLE',
  START_TIME => DATEADD(HOUR, -1, CURRENT_TIMESTAMP())
))
WHERE status = 'LOAD_FAILED' OR error_count > 0
ORDER BY last_load_time DESC;

-- Scheduled task to log errors
CREATE OR REPLACE TASK monitor_pipe_errors
WAREHOUSE = monitoring_wh
SCHEDULE = '5 MINUTE'
AS
INSERT INTO pipe_error_log
SELECT * FROM pipe_error_monitoring
WHERE last_load_time > DATEADD(MINUTE, -10, CURRENT_TIMESTAMP());

ALTER TASK monitor_pipe_errors RESUME;
```

## Cost Optimization Strategies

### File-Based Snowpipe Optimization

**Best Practices:**
1. **Optimize file sizes:** 100-250MB compressed files minimize overhead
2. **Stage files once per minute:** Avoid micro-files (<1MB)
3. **Use pattern matching:** Filter files at pipe level to reduce processing
4. **Minimize transformations:** Complex SELECT logic increases compute time
5. **Batch notifications:** Configure cloud event filtering to reduce noise
6. **Monitor and right-size:** Review cost per GB and optimize accordingly

### Snowpipe Streaming Optimization

**Best Practices:**
1. **Use high-performance architecture:** Lower per-row overhead for high-volume workloads
2. **Batch rows when possible:** Reduce per-row metadata overhead
3. **Monitor channel efficiency:** Review cost per GB and optimize accordingly
4. **Close unused channels:** Avoid idle channel overhead
5. **Use appropriate schema evolution:** Minimize schema change overhead
6. **Implement error handling:** Avoid retry storms and duplicate processing

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Setting Alert Thresholds Without Baseline Data**

**Problem:** Picking arbitrary alert thresholds (e.g., "alert if latency > 5 seconds") without measuring actual baseline performance leads to either constant false alarms or missed real incidents. A threshold set too low for your workload causes alert fatigue and trains the team to ignore alerts. A threshold set too high means genuine degradation goes undetected until it causes downstream failures.

**Correct Pattern:** Collect 1-2 weeks of baseline monitoring data before configuring alerts. Calculate p95 values from the baseline and set thresholds at 1.2-1.5x the p95 value to catch genuine anomalies while avoiding noise.

```sql
-- Step 1: Establish baseline p95 latency over 14 days
SELECT APPROX_PERCENTILE(
  DATEDIFF(SECOND, start_time, end_time), 0.95
) AS p95_latency_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE pipe_name = 'MY_DB.MY_SCHEMA.MY_PIPE'
  AND start_time >= DATEADD(DAY, -14, CURRENT_TIMESTAMP());

-- Step 2: Set alert threshold at 1.3x baseline p95
-- If p95 = 8s, threshold = ~10s
CREATE OR REPLACE ALERT MONITORING.ALERTS.LATENCY_ALERT
  WAREHOUSE = MONITORING_WH
  SCHEDULE = '5 MINUTES'
  IF (EXISTS (
    SELECT 1 FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(...))
    WHERE DATEDIFF(SECOND, start_time, end_time) > 10  -- 1.3x of p95
  ))
  THEN CALL SYSTEM$SEND_EMAIL(...);
```

**Anti-Pattern 2: Running Monitoring Tasks on Production Warehouses**

**Problem:** Scheduling monitoring queries (COPY_HISTORY scans, ACCOUNT_USAGE aggregations, alert evaluations) on the same warehouse that handles production ingestion or queries creates resource contention. During peak load, monitoring tasks compete for compute, which can slow down both production workloads and the monitoring itself -- the exact time when monitoring matters most.

**Correct Pattern:** Use a dedicated, small monitoring warehouse (e.g., X-Small) for all alert evaluations and monitoring tasks. This isolates monitoring cost, ensures alerts fire reliably during production load spikes, and makes monitoring costs visible and predictable.

```sql
-- Wrong: monitoring on production warehouse
CREATE OR REPLACE ALERT MONITORING.ALERTS.PIPE_ERROR_ALERT
  WAREHOUSE = PRODUCTION_WH  -- Competes with production!
  SCHEDULE = '5 MINUTES'
  ...

-- Correct: dedicated monitoring warehouse
CREATE WAREHOUSE IF NOT EXISTS MONITORING_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

CREATE OR REPLACE ALERT MONITORING.ALERTS.PIPE_ERROR_ALERT
  WAREHOUSE = MONITORING_WH  -- Isolated from production
  SCHEDULE = '5 MINUTES'
  ...
```

**Anti-Pattern 3: Creating Too Many Fine-Grained Alerts Without Prioritization**

**Problem:** Alerting on every possible metric (per-pipe error counts, per-channel latency, per-file size deviations, cost fluctuations) creates dozens of alerts that fire frequently. Operations teams quickly learn to ignore or bulk-dismiss alerts, which means critical alerts for genuine outages get lost in the noise. This is "alert fatigue" and is one of the most common reasons monitoring systems fail in practice.

**Correct Pattern:** Start with 2-3 critical alerts only (pipe failures, channel stalls, error rate spikes). Add more alerts incrementally only when a real incident reveals a gap. Group related conditions into a single alert where possible, and use severity levels to distinguish actionable alerts from informational ones.

```sql
-- Wrong: separate alert for every pipe and every metric
-- Results in 50+ alerts that nobody reads

-- Correct: one consolidated error alert across all pipes
CREATE OR REPLACE ALERT MONITORING.ALERTS.PIPE_ERROR_ALERT
  WAREHOUSE = MONITORING_WH
  SCHEDULE = '5 MINUTES'
  IF (EXISTS (
    SELECT 1 FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
    WHERE start_time >= DATEADD(MINUTE, -10, CURRENT_TIMESTAMP())
      AND status = 'LOAD_FAILED'
      -- Alert only when error rate exceeds threshold across ALL pipes
    HAVING COUNT_IF(status = 'LOAD_FAILED') > 0.05 * COUNT(*)
  ))
  THEN CALL SYSTEM$SEND_EMAIL(
    'pipe_notify_int', 'data-eng@company.com',
    'CRITICAL: Pipe Error Rate Exceeded 5%',
    'Error rate across pipes exceeded 5% in last 10 minutes. Check COPY_HISTORY for details.'
  );
```

## Performance Metrics

**Key metrics to track:** Files loaded per hour/day, average file size, load latency, error rate (>5% for file-based, >1% for streaming), credits per GB loaded, credits per file/million rows. Use the monitoring queries in **121b-snowflake-snowpipe-monitoring.md** for each metric.
