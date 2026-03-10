# Snowflake Observability: Snowsight Interfaces & AI Observability

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowsight-monitoring, kw:ai-observability
**Keywords:** Snowsight monitoring, Traces and Logs, Query History UI, Copy History, Task History, Dynamic Tables monitoring, AI observability, Cortex AI monitoring, token tracking, AI cost attribution, LLM evaluation, generative AI tracing
**TokenBudget:** ~3900
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 111-snowflake-observability-core.md, 111c-snowflake-observability-monitoring.md

## Scope

**What This Rule Covers:**
Snowsight monitoring interfaces (Traces & Logs, Query History, Copy History, Task History, Dynamic Tables) and AI observability patterns for Cortex AI function monitoring, cost attribution, LLM evaluation, and generative AI application tracing.

**When to Load This Rule:**
- Using Snowsight UI for operational monitoring and troubleshooting
- Monitoring Cortex AI function usage, costs, and performance
- Tracing generative AI application workflows
- Evaluating and comparing LLM model responses
- Attributing AI costs by application or function

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **111-snowflake-observability-core.md** - Telemetry configuration and event tables
- **111c-snowflake-observability-monitoring.md** - Monitoring queries and analysis

**Related:**
- **114-snowflake-cortex-aisql.md** - Cortex AI SQL function patterns and cost governance

### External Documentation

- [Snowsight Monitoring](https://docs.snowflake.com/en/user-guide/ui-snowsight-activity) - Snowsight monitoring interfaces
- [Cortex AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-observability) - AI token tracking
- [Snowflake AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - AI evaluation capabilities

## Contract

### Inputs and Prerequisites

- Snowsight UI access for monitoring dashboards
- Active event table configured (see 111-snowflake-observability-core.md)
- Access to ACCOUNT_USAGE schema for System Views
- Cortex AI functions in use (for AI observability)

### Mandatory

- Use specific Snowsight navigation paths when guiding users to monitoring interfaces
- Track token consumption and costs for Cortex AI functions
- Use distributed tracing for end-to-end AI application workflows

### Forbidden

- Telling users to "check logs" without providing specific Snowsight navigation paths
- Using Query History (System Views) to debug real-time application issues
- Running AI workloads without cost monitoring

### Execution Steps

1. Navigate to appropriate Snowsight monitoring interface
2. Apply filters (severity, time range, trace ID) relevant to the issue
3. For AI workloads, set up cost attribution queries
4. Implement distributed tracing for AI application workflows
5. Configure evaluation workflows for LLM comparison

### Output Format

- Snowsight navigation paths for UI access
- SQL queries for AI cost monitoring and attribution
- Python code for traced AI application workflows

### Validation

- Snowsight dashboards accessible and displaying data
- AI cost queries returning expected metrics
- Trace spans appearing in event tables for AI workflows

### Design Principles

- Always provide specific Snowsight navigation paths, not vague "check logs" guidance
- Use System Views for historical analysis, Event Tables for real-time monitoring
- Track AI costs proactively to prevent budget overruns
- Trace AI application workflows end-to-end for debugging and optimization

### Post-Execution Checklist

- [ ] Snowsight interfaces verified accessible
- [ ] AI cost monitoring views created
- [ ] Distributed tracing implemented for AI workflows
- [ ] LLM evaluation workflow configured (if applicable)

## Snowsight Monitoring Interfaces

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
- **Purpose:** Historical analysis of all SQL queries executed in the account (System Views based).
- **Latency:** 45 minutes to 3 hours for data availability.
- **Key Use Cases:**
  - SQL performance optimization
  - Identifying expensive queries
  - Analyzing query patterns and trends
  - Troubleshooting failed queries

**Programmatic Access:**
```sql
-- Query History System Views (historical data)
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
- **Purpose:** Track all data loading operations via COPY INTO commands (System Views based).
- **Monitors:** Snowpipe, bulk COPY INTO, continuous data ingestion.
- **Key Metrics:** Rows loaded, bytes transferred, file count, errors.

**Programmatic Access:**
```sql
-- Copy History System Views
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
- **Purpose:** Monitor execution of scheduled tasks (System Views based).
- **Tracks:** Task runs, execution status, duration, error messages.
- **Critical for:** Pipeline orchestration, scheduled data transformations, incremental processing.

**Programmatic Access:**
```sql
-- Task History System Views
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
- **Purpose:** Monitor automatic refresh operations for Dynamic Tables (System Views based).
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
Using Query History (System Views) to debug real-time application issues. Instead, use Traces & Logs (Event Tables) for real-time, Query History for historical analysis.

### Alerts Interface
- **Navigation:** Monitoring > Alerts
- **Purpose:** View, create, and manage Snowflake Alerts for proactive monitoring.
- **Key Use Cases:** Error spike detection, cost threshold alerts, pipeline failure notifications.

> See `111c-snowflake-observability-monitoring.md` (Proactive Alerting section) for `CREATE ALERT` SQL syntax and examples.

## AI Observability

### Cortex AI Function Monitoring
- **Purpose:** Track usage, cost, and performance of Snowflake Cortex AI functions (COMPLETE, CLASSIFY, EXTRACT, SENTIMENT, etc.).
- **Integration:** AI observability data flows into same event tables as other telemetry.
- **Key Metrics:** Token consumption, model latency, error rates, cost per operation.

**Cost Tracking:** See the `ai_cost_monitoring` view in `111c-snowflake-observability-monitoring.md` Output Format Examples (Step 3) for a production-ready AI cost attribution query.

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

> For the base AI cost attribution query, see the `ai_cost_monitoring` view in `111c-snowflake-observability-monitoring.md` (Output Format Examples, Step 3). The query below extends it with `estimated_cost_usd`:

```sql
-- AI Cost Attribution with estimated cost (extends 111c's ai_cost_monitoring view)
-- Pricing as of 2026-Q1. Verify current rates at docs.snowflake.com/en/user-guide/cost-understanding-overall
SELECT
    resource_attributes:"snow.executable.name"::string as application_name,
    resource_attributes:"cortex.function"::string as ai_function,
    COUNT(*) as invocations,
    SUM(resource_attributes:"cortex.tokens"::number) as total_tokens,
    total_tokens * 0.0001 as estimated_cost_usd
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND resource_attributes:"cortex.function" IS NOT NULL
  AND timestamp >= current_timestamp() - INTERVAL '30 days'
GROUP BY application_name, ai_function
ORDER BY estimated_cost_usd DESC;
```

**Cross-Reference:** See `114-snowflake-cortex-aisql.md` for detailed AISQL cost governance patterns.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Query History for Real-Time Debugging**

**Problem:** Developers query `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` to debug live application issues, then are confused when recent queries don't appear. System Views have 45-minute to 3-hour latency, making them useless for real-time troubleshooting. This leads to wasted time, false negatives ("no errors found"), and delayed incident response.

**Correct Pattern:** Use Monitoring > Traces & Logs (Event Tables) for real-time application debugging. Reserve Query History (System Views) for historical trend analysis, cost attribution, and post-incident review. If you need query-level data in near-real-time, use `INFORMATION_SCHEMA.QUERY_HISTORY()` table functions which have lower latency than Account Usage views.

```sql
-- Wrong: Using Account Usage for real-time debugging (45min-3hr latency)
SELECT query_id, error_message
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('minute', -5, CURRENT_TIMESTAMP())
  AND execution_status = 'FAIL';
-- Returns nothing — data hasn't arrived yet!

-- Correct: Use Event Tables for real-time application debugging
SELECT timestamp, record_attributes, resource_attributes
FROM my_db.my_schema.my_event_table
WHERE timestamp >= DATEADD('minute', -5, CURRENT_TIMESTAMP())
  AND record_type = 'LOG'
  AND severity_text = 'ERROR'
ORDER BY timestamp DESC;

-- Correct: Use INFORMATION_SCHEMA for near-real-time query data
SELECT query_id, error_message, start_time
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(
    DATEADD('minute', -10, CURRENT_TIMESTAMP()),
    CURRENT_TIMESTAMP(),
    RESULT_LIMIT => 50
))
WHERE execution_status = 'FAIL';
```

**Anti-Pattern 2: AI Cost Monitoring Without Attribution Dimensions**

**Problem:** Tracking total Cortex AI token consumption as a single aggregate number without breaking down by application, function type, or model. When costs spike, there is no way to identify which application, prompt, or model is responsible. Teams end up investigating blindly or throttling all AI workloads instead of the offending one.

**Correct Pattern:** Always include attribution dimensions in AI cost queries: `resource_attributes:"snow.executable.name"` for application name, `resource_attributes:"cortex.function"` for function type, and model name. Use dedicated warehouses per agent to enable warehouse-level cost attribution via `WAREHOUSE_METERING_HISTORY`. Set up alerts on per-application cost thresholds, not just account-wide totals.

```sql
-- Wrong: Aggregate-only cost tracking — no way to find the culprit
SELECT SUM(tokens_used) AS total_tokens
FROM my_ai_usage_table
WHERE usage_date >= CURRENT_DATE() - 30;

-- Correct: Cost attribution with application, function, and model dimensions
SELECT
    resource_attributes:"snow.executable.name"::STRING AS app_name,
    resource_attributes:"cortex.function"::STRING AS ai_function,
    resource_attributes:"cortex.model"::STRING AS model_name,
    COUNT(*) AS invocations,
    SUM(resource_attributes:"cortex.tokens"::NUMBER) AS total_tokens
FROM my_db.my_schema.my_event_table
WHERE record_type = 'SPAN'
  AND resource_attributes:"cortex.function" IS NOT NULL
  AND timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY app_name, ai_function, model_name
ORDER BY total_tokens DESC;
```

**Anti-Pattern 3: Tracing AI Workflows Without Span Hierarchy**

**Problem:** Developers add a single flat span around an entire AI workflow (prompt preparation + model invocation + post-processing) instead of creating nested child spans. When latency issues arise, they can only see total duration and cannot determine whether the bottleneck is in data retrieval, prompt construction, model inference, or response parsing.

**Correct Pattern:** Create a parent span for the overall workflow and nested child spans for each distinct phase: prompt preparation, model invocation, and response processing. Set meaningful attributes on each span (e.g., `prompt_length`, `model`, `response_length`, `success`). This enables precise latency attribution and makes it possible to optimize the actual bottleneck rather than guessing.

```python
from snowflake import telemetry

# Wrong: Single flat span — no visibility into which phase is slow
def generate_response_flat(session, query):
    with telemetry.create_span("ai_workflow") as span:
        prompt = build_prompt(query)
        # SECURITY: f-string shown as anti-pattern — use parameterized query instead
        result = session.sql(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{prompt}')").collect()
        parsed = parse_response(result[0][0])
        return parsed

# Correct: Nested spans for each phase — pinpoint the bottleneck
def generate_response_traced(session, query):
    with telemetry.create_span("ai_workflow") as parent:
        parent.set_attribute("model", "mistral-large2")

        with telemetry.create_span("prompt_preparation") as prep:
            prompt = build_prompt(query)
            prep.set_attribute("prompt_length", len(prompt))

        with telemetry.create_span("model_invocation") as invoke:
            result = session.sql(
                f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{prompt}')"
            ).collect()
            invoke.set_attribute("success", True)

        with telemetry.create_span("response_parsing") as parse_span:
            parsed = parse_response(result[0][0])
            parse_span.set_attribute("response_length", len(parsed))

        return parsed
```
