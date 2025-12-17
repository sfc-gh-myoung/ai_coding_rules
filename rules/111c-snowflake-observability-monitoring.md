# Snowflake Observability: Monitoring and Analysis

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Copy History, Task History, Dynamic Tables, cost management, AI observability, Cortex AI, token tracking, troubleshooting, performance analysis, monitor queries, monitoring dashboard, observability UI, query monitoring, telemetry volume, SQL
**TokenBudget:** ~4300
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/111-snowflake-observability-core.md

## Purpose
Provide comprehensive monitoring, analysis, and cost management strategies for Snowflake observability, covering Snowsight monitoring interfaces, AI observability patterns, and troubleshooting workflows.

## Rule Scope

Monitoring queries, Snowsight navigation, cost management, AI observability, troubleshooting patterns

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **System Views (historical)** - 45+ min latency, use for trends/audits
- **Event Tables (real-time)** - Seconds latency, use for live debugging
- **Snowsight Monitoring > Traces & Logs** - Real-time telemetry UI
- **Snowsight Monitoring > Query History** - Historical SQL analysis
- **Always use timestamp filters** - Prevent full table scans
- **Monitor telemetry volume** - DEBUG generates 10-100x more data
- **AI observability** - Track Cortex AI token usage and costs

**Quick Checklist:**
- [ ] Data source identified (System View vs Event Table)
- [ ] Monitoring queries have timestamp filters
- [ ] Snowsight interfaces accessible
- [ ] Cost implications reviewed (especially for DEBUG level)

## Contract

<contract>
<inputs_prereqs>
- Active event table configured (see `111-snowflake-observability-core.md`)
- Access to ACCOUNT_USAGE schema for System Views
- Snowsight UI access for monitoring dashboards
- Understanding of System Views vs Telemetry distinction (see core rule)
</inputs_prereqs>

<mandatory>
- SQL queries on `SNOWFLAKE.ACCOUNT_USAGE` schema views
- Snowsight monitoring interfaces (Traces & Logs, Query History, Copy History, Task History)
- Monitoring views and stored procedures
- Alert and notification mechanisms
</mandatory>

<forbidden>
- Using System Views (QUERY_HISTORY) for real-time monitoring (45+ min latency)
- Querying event tables with `SELECT *` (always use explicit columns)
- Creating monitoring queries without timestamp filters (full table scan)
</forbidden>

<steps>
1. **Identify:** Determine data source (System View historical vs Event Table real-time)
2. **Query:** Create monitoring queries with explicit columns and timestamp filters
3. **Visualize:** Use Snowsight interfaces for operational dashboards
4. **Alert:** Set up proactive alerting for critical error patterns
5. **Optimize:** Review cost implications and optimize telemetry volume
</steps>

<output_format>
- SQL queries with explicit column selection (no `SELECT *`)
- Monitoring views with aggregated metrics
- Snowsight navigation paths for UI access
- Cost analysis queries with estimated storage impact
</output_format>

<validation>
- Verify monitoring queries return expected data
- Confirm Snowsight dashboards accessible
- Validate timestamp filters prevent full table scans
- Check cost implications of telemetry volume
</validation>

<design_principles>
- Use System Views (ACCOUNT_USAGE) for historical analysis and trends (45+ min latency).
- Use Event Tables for real-time monitoring and live debugging (seconds latency).
- Always include timestamp filters in monitoring queries to prevent full table scans.
- Create reusable monitoring views for common observability queries.
- Monitor telemetry data volume and cost implications (DEBUG can generate 10-100x more data).
- Use Snowsight monitoring interfaces for operational dashboards and troubleshooting.
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using SELECT * in Monitoring Queries**
```sql
-- Bad: SELECT * on large system views
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP());
-- Returns 100+ columns, most unused, slow and expensive!
```
**Problem:** Returns unnecessary columns; slow queries; high compute costs; wide result sets; query timeout risk; inefficient data transfer; wasted resources

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
**Benefits:** Fast queries; low costs; minimal data transfer; focused results; query performance; production-scalable monitoring; efficient dashboards


**Anti-Pattern 2: Monitoring Queries Without Timestamp Filters**
```sql
-- Bad: No time filter on large historical table
SELECT warehouse_name, SUM(credits_used)
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
GROUP BY warehouse_name;
-- Scans years of data! Very expensive query!
```
**Problem:** Full table scan; extremely slow; high costs; query timeout; unnecessary historical data; dashboard latency; user frustration

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
**Benefits:** Fast queries; bounded costs; relevant recent data; quick dashboard refresh; production-ready monitoring; user-friendly performance


**Anti-Pattern 3: Using ACCOUNT_USAGE for Real-Time Alerting**
```sql
-- Bad: Real-time alert query on ACCOUNT_USAGE (45 min latency!)
SELECT COUNT(*) as failed_queries
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('minute', -5, CURRENT_TIMESTAMP())
  AND execution_status = 'FAILED';
-- Returns stale data, misses recent failures!
```
**Problem:** 45-minute data latency; stale alerts; missed incidents; false negatives; delayed response; poor real-time visibility; SLA violations

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
**Benefits:** Real-time alerting (<1 min); timely incident detection; accurate monitoring; proper data source selection; SLA compliance; operational excellence


**Anti-Pattern 4: Not Monitoring Telemetry Volume and Costs**
```python
# Bad: Enable verbose logging without monitoring costs
import logging
logging.basicConfig(level=logging.DEBUG)  # In production!
# Never check: How much data? What's the cost?
# Costs spiral out of control, surprise bills!
```
**Problem:** Unbounded telemetry costs; surprise budget overruns; no cost visibility; runaway spending; lack of accountability; emergency cost-cutting required

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
**Benefits:** Cost visibility; budget control; early warning; informed decisions; predictable spending; resource optimization; financial accountability

## Post-Execution Checklist
- [ ] Data source identified (System View for historical, Event Table for real-time)
- [ ] Monitoring queries include timestamp filters (prevent full table scans)
- [ ] Explicit column selection used (no `SELECT *`)
- [ ] Snowsight access verified for monitoring dashboards
- [ ] Cost implications reviewed (DEBUG generates 10-100x more data)
- [ ] Telemetry volume monitored regularly
- [ ] AI observability enabled for Cortex AI functions
- [ ] Token tracking configured for cost attribution
- [ ] Cross-references noted (114-aisql for AI costs, 122-dynamic-tables for DT monitoring)

## Validation
- **Success Checks:**
  - Monitoring queries return expected data within latency constraints
  - Snowsight dashboards accessible and show current telemetry
  - Event table queries execute efficiently with timestamp filters
  - Cost analysis shows telemetry volume within budget
  - System View queries account for latency (no real-time expectations)
  - AI observability captures token usage and costs

- **Negative Tests:**
  - `SELECT *` on event tables should be discouraged
  - System Views queried for real-time data (< 45 min) should show no recent results
  - Event table queries without timestamp filters should be flagged
  - DEBUG level in production should trigger cost review

> **Investigation Required**
> When applying this rule:
> 1. **Identify data source** - System View (historical) vs Event Table (real-time)
> 2. **Check Snowsight access** - Verify users can access monitoring dashboards
> 3. **Review monitoring patterns** - Understand existing queries and dashboards
> 4. **Verify cost implications** - Check telemetry volume and retention settings
> 5. **Test navigation paths** - Ensure Snowsight interfaces accessible
>
> **Anti-Pattern:**
> "Querying Query History for real-time data... (45+ min latency)"
> "Using SELECT * on event tables... (inefficient)"
>
> **Correct Pattern:**
> "Let me check which data source is appropriate for your time range first."
> [checks time requirements, selects Event Table for real-time or System View for historical]
> "For real-time monitoring, use Monitoring > Traces & Logs. For historical analysis, use Query History..."

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

## References

### Snowsight UI and System Views
- [Snowflake Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query performance analysis and optimization using Query Profile
- [Query History](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) - QUERY_HISTORY System View reference
- [Copy History](https://docs.snowflake.com/en/sql-reference/account-usage/copy_history) - COPY_HISTORY System View for data loading monitoring
- [Task History](https://docs.snowflake.com/en/sql-reference/account-usage/task_history) - TASK_HISTORY System View for pipeline monitoring
- [Dynamic Table Refresh History](https://docs.snowflake.com/en/sql-reference/account-usage/dynamic_table_refresh_history) - Monitoring Dynamic Table refresh operations

### AI Observability
- [Snowflake AI Observability (Cortex)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate and trace generative AI applications with evaluations, comparisons, and tracing features

### Related Rules
- **Observability Core**: `rules/111-snowflake-observability-core.md` - Telemetry configuration and event tables
- **Observability Logging**: `rules/111a-snowflake-observability-logging.md` - Logging best practices
- **Observability Tracing**: `rules/111b-snowflake-observability-tracing.md` - Distributed tracing patterns
- **Cost Governance**: `rules/105-snowflake-cost-governance.md` - Cost optimization strategies for telemetry data
- **Cortex AISQL**: `rules/114-snowflake-cortex-aisql.md` - AI function cost governance and observability patterns
- **Dynamic Tables**: `rules/122-snowflake-dynamic-tables.md` - Dynamic Table monitoring and optimization

## 1. Cost and Volume Management

### Data Volume Control
- **Rule:** Implement strategies to control telemetry data volume and associated storage costs.
- **Always:** Use appropriate log levels and conditional logging to prevent data overflow.

```python
import random

# Volume-conscious logging strategy
def log_with_sampling(logger, level, message, sample_rate=0.1):
    """Log messages with sampling to control volume."""
    if random.random() < sample_rate:
        logger.log(level, f"[SAMPLED {sample_rate*100}%] {message}")

# Use for high-frequency operations
for record in large_dataset:
    result = process_record(record)

    # Only log a sample of successful operations
    if result.success:
        log_with_sampling(logger, logging.INFO, f"Processed record {record.id}", sample_rate=0.01)
    else:
        # Always log failures
        logger.warn(f"Failed to process record {record.id}: {result.error}")
```

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
```sql
-- Estimate event table storage and volume
SELECT
    record_type,
    COUNT(*) as record_count,
    COUNT(*) * 1024 / (1024*1024*1024) as estimated_gb,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest,
    DATEDIFF(day, earliest, latest) as retention_days
FROM snowflake.account_usage.event_table
GROUP BY record_type
ORDER BY estimated_gb DESC;
```

## 2. Monitoring and Analysis

### Regular Monitoring Queries
- **Always:** Implement regular monitoring queries to identify issues and performance trends.
- **Rule:** Create views or stored procedures for common observability queries.

```sql
-- Create monitoring view for error analysis
CREATE OR REPLACE VIEW system_errors AS
SELECT
    DATE_TRUNC('hour', timestamp) as error_hour,
    resource_attributes:"snow.database.name"::string as database_name,
    resource_attributes:"snow.executable.name"::string as object_name,
    severity_text,
    COUNT(*) as error_count,
    ARRAY_AGG(DISTINCT body) as sample_messages
FROM snowflake.account_usage.event_table
WHERE record_type = 'LOG'
  AND severity_text IN ('ERROR', 'FATAL')
  AND timestamp >= current_timestamp() - interval '7 days'
GROUP BY 1, 2, 3, 4
ORDER BY error_hour DESC, error_count DESC;

-- Create performance monitoring view
CREATE OR REPLACE VIEW function_performance AS
SELECT
    resource_attributes:"snow.executable.name"::string as function_name,
    DATE_TRUNC('hour', timestamp) as performance_hour,
    AVG(duration_ms) as avg_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms,
    COUNT(*) as execution_count
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND timestamp >= current_timestamp() - interval '24 hours'
GROUP BY 1, 2
ORDER BY performance_hour DESC, avg_duration_ms DESC;
```

### Snowsight Dashboard Queries
- **Always:** Use Snowsight to visualize telemetry data and create dashboards for operational monitoring.
- **Rule:** Set up alerts for critical error patterns and performance degradation.

```sql
-- Query for Snowsight dashboard: Error rate by hour
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(CASE WHEN severity_text IN ('ERROR', 'FATAL') THEN 1 END) as errors,
    COUNT(*) as total_logs,
    (errors / total_logs * 100) as error_rate_percent
FROM snowflake.account_usage.event_table
WHERE record_type = 'LOG'
  AND timestamp >= current_timestamp() - interval '24 hours'
GROUP BY hour
ORDER BY hour;
```

## 3. Security and Governance Integration

### Telemetry Data Protection
- **Rule:** Apply appropriate access controls to event tables and telemetry data.
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

## 4. Troubleshooting and Optimization

### Performance Analysis
- **Always:** Use trace data to identify performance bottlenecks and optimize critical paths.
- **Rule:** Correlate telemetry data with query profiles for comprehensive performance analysis.

```sql
-- Identify slow function executions
SELECT
    resource_attributes:"snow.executable.name"::string as function_name,
    span_name,
    duration_ms,
    timestamp,
    trace_id
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND duration_ms > 5000  -- Functions taking more than 5 seconds
  AND timestamp >= current_timestamp() - interval '1 hour'
ORDER BY duration_ms DESC;

-- Correlate with error logs
SELECT
    t.function_name,
    t.duration_ms,
    l.severity_text,
    l.body as error_message
FROM (
    SELECT
        resource_attributes:"snow.executable.name"::string as function_name,
        duration_ms,
        trace_id,
        timestamp
    FROM snowflake.account_usage.event_table
    WHERE record_type = 'SPAN' AND duration_ms > 5000
) t
JOIN (
    SELECT
        trace_id,
        severity_text,
        body,
        timestamp
    FROM snowflake.account_usage.event_table
    WHERE record_type = 'LOG' AND severity_text IN ('ERROR', 'WARN')
) l ON t.trace_id = l.trace_id
WHERE ABS(DATEDIFF(second, t.timestamp, l.timestamp)) < 10;
```

## 5. Snowsight Monitoring Interfaces

### Traces & Logs Monitoring Page
- **Navigation:** Monitoring > Traces & Logs
- **Purpose:** Unified interface for real-time monitoring of application telemetry from event tables.
- **Features:**
  - Filter by time range, log level, trace ID
  - Search log message content
  - View trace spans with execution timeline
  - Drill into individual trace details with nested spans

**Usage for AI Agents:**
> **Investigation Required**
> When recommending Snowsight monitoring:
> 1. Verify user has access to Monitoring > Traces & Logs
> 2. Confirm event table is active and receiving data
> 3. Guide user to specific filters (severity, time range) relevant to their issue
> 4. Reference trace IDs for end-to-end debugging workflows

**Correct Pattern:**
"Navigate to Monitoring > Traces & Logs, filter by Severity = ERROR, Time Range = Last Hour"

**Anti-Pattern:**
Telling users to "check logs" without specific navigation path

### Query History Interface
- **Navigation:** Monitoring > Query History
- **Purpose:** Historical analysis of all SQL queries executed in the account (System View based).
- **Latency:** 45 minutes to 3 hours for data availability.
- **Key Use Cases:**
  - SQL performance optimization
  - Identifying expensive queries
  - Analyzing query patterns and trends
  - Troubleshooting failed queries

**Programmatic Access:**
```sql
-- Query History System View (historical data)
SELECT
    query_id,
    query_text,
    user_name,
    warehouse_name,
    execution_status,
    total_elapsed_time / 1000 as duration_seconds,
    rows_produced,
    bytes_scanned
FROM snowflake.account_usage.query_history
WHERE start_time >= current_timestamp() - INTERVAL '24 hours'
  AND execution_status = 'FAIL'
ORDER BY start_time DESC
LIMIT 100;
```

### Copy History (Data Loading Monitoring)
- **Navigation:** Monitoring > Copy History
- **Purpose:** Track all data loading operations via COPY INTO commands (System View based).
- **Monitors:** Snowpipe, bulk COPY INTO, continuous data ingestion.
- **Key Metrics:** Rows loaded, bytes transferred, file count, errors.

**Programmatic Access:**
```sql
-- Copy History System View
SELECT
    file_name,
    table_name,
    last_load_time,
    status,
    row_count,
    row_parsed,
    file_size,
    error_count,
    error_limit
FROM snowflake.account_usage.copy_history
WHERE last_load_time >= current_timestamp() - INTERVAL '24 hours'
  AND status != 'LOADED'  -- Show problems
ORDER BY last_load_time DESC;
```

**AI Agent Guidance:**
- Use for diagnosing data pipeline loading issues
- Correlate with Task History for scheduled load jobs
- Check for parse errors, schema mismatches, file format issues

### Task History (Pipeline Monitoring)
- **Navigation:** Monitoring > Task History
- **Purpose:** Monitor execution of scheduled tasks (System View based).
- **Tracks:** Task runs, execution status, duration, error messages.
- **Critical for:** Pipeline orchestration, scheduled data transformations, incremental processing.

**Programmatic Access:**
```sql
-- Task History System View
SELECT
    name as task_name,
    database_name,
    schema_name,
    state,
    scheduled_time,
    completed_time,
    DATEDIFF(second, scheduled_time, completed_time) as duration_seconds,
    error_code,
    error_message
FROM snowflake.account_usage.task_history
WHERE scheduled_time >= current_timestamp() - INTERVAL '24 hours'
  AND state IN ('FAILED', 'CANCELLED')  -- Show problems
ORDER BY scheduled_time DESC;
```

**AI Agent Usage:**
- Diagnose task failures and scheduling issues
- Analyze task execution patterns and dependencies
- Recommend optimizations for task DAGs

### Dynamic Tables Monitoring
- **Navigation:** Data > Databases > [Select Table] > Refresh History
- **Purpose:** Monitor automatic refresh operations for Dynamic Tables (System View based).
- **Tracks:** Refresh timestamps, lag, data freshness, refresh mode (INCREMENTAL vs FULL).

**Programmatic Access:**
```sql
-- Dynamic Tables Refresh History
SELECT
    name as dynamic_table_name,
    database_name,
    schema_name,
    refresh_action,
    refresh_trigger,
    state,
    completion_target,
    data_timestamp,
    refresh_start_time,
    refresh_end_time
FROM snowflake.account_usage.dynamic_table_refresh_history
WHERE refresh_start_time >= current_timestamp() - INTERVAL '24 hours'
ORDER BY refresh_start_time DESC;
```

**AI Agent Guidance:**
- Use to verify Dynamic Table refresh patterns
- Diagnose lag issues and staleness
- Correlate with target lag configuration
- Reference `122-snowflake-dynamic-tables.md` for optimization patterns

### Unified Monitoring Strategy

**System Views (Historical) for:**
- Long-term performance trends
- Cost analysis and attribution
- Compliance and auditing
- Batch job retrospectives

**Event Tables (Real-Time) for:**
- Live application debugging
- Real-time alerting
- User code telemetry
- Distributed tracing

**Anti-Pattern:**
Using Query History (System View) to debug real-time application issues. Instead, use Traces & Logs (Event Tables) for real-time, Query History for historical analysis

## 6. AI Observability

### Cortex AI Function Monitoring
- **Purpose:** Track usage, cost, and performance of Snowflake Cortex AI functions (COMPLETE, CLASSIFY, EXTRACT, SENTIMENT, etc.).
- **Integration:** AI observability data flows into same event tables as other telemetry.
- **Key Metrics:** Token consumption, model latency, error rates, cost per operation.

**Cost Tracking Query:**
```sql
-- Monitor Cortex AI token usage and costs
SELECT
    DATE_TRUNC('day', timestamp) as usage_day,
    resource_attributes:"cortex.function"::string as ai_function,
    resource_attributes:"cortex.model"::string as model_name,
    SUM(resource_attributes:"cortex.tokens"::number) as total_tokens,
    COUNT(*) as invocation_count,
    AVG(duration_ms) as avg_latency_ms
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND resource_attributes:"cortex.function" IS NOT NULL
  AND timestamp >= current_timestamp() - INTERVAL '7 days'
GROUP BY usage_day, ai_function, model_name
ORDER BY usage_day DESC, total_tokens DESC;
```

### Evaluations and Comparisons
- **Feature:** Snowflake AI Observability provides built-in evaluation capabilities for generative AI applications.
- **Use Cases:**
  - Compare responses across different LLM models
  - Measure output quality with evaluation metrics
  - A/B testing for prompt engineering
  - Track model performance over time

**Reference Documentation:**
- [Snowflake AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- Cross-reference with `114-snowflake-cortex-aisql.md` for cost optimization patterns

### Tracing Generative AI Applications
- **Always:** Use distributed tracing to monitor end-to-end AI application workflows.
- **Pattern:** Create spans for prompt preparation, model invocation, response processing.

```python
from snowflake import telemetry
import logging

logger = logging.getLogger(__name__)

def generate_insights(session, user_query):
    """Generate AI insights with comprehensive tracing."""

    with telemetry.create_span("ai_insight_generation") as span:
        span.set_attribute("user_query_length", len(user_query))
        span.set_attribute("model", "mistral-large2")

        # Prompt preparation span
        with telemetry.create_span("prompt_preparation") as prep_span:
            prompt = f"Analyze this query: {user_query}"
            prep_span.set_attribute("prompt_length", len(prompt))

        # AI model invocation span
        with telemetry.create_span("cortex_complete") as ai_span:
            result = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large2',
                    '{prompt}'
                )
            """).collect()

            response = result[0][0]
            ai_span.set_attribute("response_length", len(response))
            ai_span.set_attribute("success", True)

        logger.info(f"AI insight generated: {len(response)} chars")
        span.set_attribute("total_processing_complete", True)
        return response
```

### Cost Monitoring for AI Workloads
- **Rule:** Track token consumption and costs for Cortex AI functions to manage budget.
- **Integration:** Combine cost data from `ACCOUNT_USAGE.METERING_HISTORY` with telemetry for comprehensive cost attribution.

```sql
-- AI Cost Attribution by Application
SELECT
    t.resource_attributes:"snow.executable.name"::string as application_name,
    t.resource_attributes:"cortex.function"::string as ai_function,
    COUNT(*) as invocations,
    SUM(t.resource_attributes:"cortex.tokens"::number) as total_tokens,
    -- Estimated cost (adjust multiplier based on actual pricing)
    total_tokens * 0.0001 as estimated_cost_usd
FROM snowflake.account_usage.event_table t
WHERE t.record_type = 'SPAN'
  AND t.resource_attributes:"cortex.function" IS NOT NULL
  AND t.timestamp >= current_timestamp() - INTERVAL '30 days'
GROUP BY application_name, ai_function
ORDER BY estimated_cost_usd DESC;
```

**Cross-Reference:** See `114-snowflake-cortex-aisql.md` for detailed AISQL cost governance patterns.

## 7. Limitations and Considerations

### Event Table Retention
- **Default:** Retention controlled by `DATA_RETENTION_TIME_IN_DAYS` on event table.
- **Cost Impact:** Longer retention increases storage costs.
- **Recommendation:** Balance compliance needs with cost efficiency (7-90 days typical).

### Cost Implications of Verbose Logging
- **DEBUG Level:** Can generate 10-100x more log entries than WARN level.
- **Storage:** Event tables consume storage based on volume and retention.
- **Compute:** Querying large event tables requires warehouse credits.
- **Best Practice:** Use INFO/WARN in production, DEBUG only for targeted debugging.

### Performance Impact of TRACE_LEVEL = ALWAYS
- **ALWAYS:** Generates trace spans for every function/procedure invocation regardless of errors.
- **Performance:** Minimal overhead (<5% typically), but consider cumulative impact at scale.
- **Recommendation:** Use `ON_EVENT` for production (traces only on errors), `ALWAYS` for debugging.

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
