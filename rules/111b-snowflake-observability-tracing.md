# Snowflake Observability: Distributed Tracing and Metrics

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** span attributes, trace_id, performance analysis, metrics collection, cpu_usage, memory_usage, telemetry.create_span, OpenTelemetry, nested spans, tracing patterns, span creation, trace analysis, distributed traces
**TokenBudget:** ~4600
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 111-snowflake-observability-core.md

## Scope

**What This Rule Covers:**
Distributed tracing and metrics collection patterns for Snowflake handlers using `snowflake-telemetry-python` package. Covers span creation, nested tracing hierarchies, performance analysis, bottleneck identification, resource monitoring, and trace event limits (128 events/span maximum).

**When to Load This Rule:**
- Implementing distributed tracing in Snowflake Python handlers
- Performance analysis and bottleneck identification
- Adding custom spans and metrics to handlers
- Debugging slow operations with trace data
- Configuring TRACE_LEVEL and METRIC_LEVEL

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **111-snowflake-observability-core.md** - Telemetry configuration and event tables

**Related:**
- **111a-snowflake-observability-logging.md** - Logging best practices
- **111c-snowflake-observability-monitoring.md** - Monitoring, Snowsight interfaces, analysis
- **103-snowflake-performance-tuning.md** - Performance optimization using trace data

### External Documentation

**Tracing Documentation:**
- [Snowflake Python Tracing](https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python) - Python-specific tracing implementation guide
- [OpenTelemetry Tracing](https://opentelemetry.io/docs/concepts/signals/traces/) - OpenTelemetry standard for distributed tracing
- [Snowflake Telemetry Levels](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels) - TRACE_LEVEL configuration guide

## Contract

### Inputs and Prerequisites

- `snowflake-telemetry-python` package installed for Python handlers
- TRACE_LEVEL configured (see `111-snowflake-observability-core.md`)
- METRIC_LEVEL configured for system metrics
- Active event table receiving data

### Mandatory

- `snowflake.telemetry.create_span()` for Python handlers
- `telemetry.set_attribute()` for span attributes
- `telemetry.add_event()` for span events
- `telemetry.emit_metric()` for custom metrics

### Forbidden

- Creating >128 trace events per span (hard limit)
- Creating >128 custom attributes per span (hard limit)
- Using TRACE_LEVEL = ALWAYS in production without performance analysis

### Execution Steps

1. Import `snowflake.telemetry` at module level
2. Use `create_span()` context manager for operations
3. Add relevant attributes to spans (`set_attribute()`)
4. Create nested spans for sub-operations
5. Query event tables to verify trace data collection

### Output Format

- Python code with `snowflake.telemetry` import
- Spans with meaningful names describing operations
- Attributes providing context (input size, processing time, success status)
- Nested spans showing operation hierarchy

### Validation

**Pre-Task-Completion Checks:**
- Spans appear in event tables with `record_type = 'SPAN'`
- Trace IDs link related events
- Span attributes provide meaningful context
- Duration metrics are reasonable

**Success Criteria:**
- Spans visible in Snowsight Traces UI
- Nested spans show correct hierarchy
- System metrics captured when METRIC_LEVEL = ALL
- No spans exceed 128 events or 128 attributes

**Negative Tests:**
- Spans with >128 events trigger sampling strategy
- Spans with >128 attributes trigger reduction
- TRACE_LEVEL = ALWAYS in production triggers performance review

### Design Principles

- Use `snowflake-telemetry-python` package for custom spans in Python handlers
- Create spans around expensive operations (>100ms), external calls, critical business logic
- Add relevant attributes to spans for performance analysis and troubleshooting
- Use nested spans to show operation hierarchy and identify bottlenecks
- Respect span limits (128 events per span, 128 attributes per span)
- Use TRACE_LEVEL = ON_EVENT for production (traces only on errors), ALWAYS for debugging

### Post-Execution Checklist

- [ ] `snowflake.telemetry` imported for Python handlers
- [ ] Spans created around expensive operations (>100ms)
- [ ] Span attributes added for context (input_size, success, error)
- [ ] Nested spans used to show operation hierarchy
- [ ] Event limit respected (<128 events per span)
- [ ] Attribute limit respected (<128 attributes per span)
- [ ] TRACE_LEVEL = ON_EVENT for production
- [ ] System metrics enabled (METRIC_LEVEL = ALL)
- [ ] Trace data verified in event tables

## Anti-Patterns and Common Mistakes
```python
# Bad: Span for every small operation
def process_order(order):
    with telemetry.create_span("process_order"):  # Span 1
        with telemetry.create_span("validate"):  # Span 2 - 5ms
            validate(order)
        with telemetry.create_span("transform"):  # Span 3 - 3ms
            transform(order)
        with telemetry.create_span("save"):  # Span 4 - 10ms
            save(order)
# 4 spans for 18ms total operation - excessive overhead!
```
**Problem:** Span overhead exceeds actual work time; massive trace volume; high costs; performance degradation; signal-to-noise destroyed; unusable traces

**Correct Pattern:**
```python
# Good: Single span for operation, use events for milestones
def process_order(order):
    with telemetry.create_span("process_order") as span:
        span.add_attribute("order_id", order.id)
        validate(order)  # No span, <10ms
        transform(order)  # No span, <10ms
        span.add_event("validation_complete")
        save(order)  # Only span expensive ops (>100ms)
        span.add_attribute("success", True)
```
**Benefits:** Minimal overhead; manageable trace volume; cost-effective; performance maintained; clear operation boundaries; actionable traces

**Anti-Pattern 2: Exceeding 128 Events Per Span Limit**
```python
# Bad: Add event for every loop iteration
with telemetry.create_span("process_batch") as span:
    for i in range(10000):  # 10,000 iterations
        span.add_event(f"Processing item {i}")
# Hits 128 event limit, remaining 9,872 events silently dropped!
```
**Problem:** 128 event limit silently drops events; incomplete traces; missing critical events; debugging impossible; no error raised; data loss

**Correct Pattern:**
```python
# Good: Sample events strategically
with telemetry.create_span("process_batch") as span:
    batch_size = 10000
    for i in range(batch_size):
        if i % 1000 == 0:  # Sample every 1000th
            span.add_event(f"Progress: {i}/{batch_size}")
    span.add_attribute("total_processed", batch_size)
# 10 events total, well under 128 limit
```
**Benefits:** Stays under 128 limit; all events captured; complete traces; effective debugging; efficient sampling; production-scalable

**Anti-Pattern 3: Using TRACE_LEVEL = ALWAYS in Production**
```sql
-- Bad: Trace every execution in production
ALTER SESSION SET TRACE_LEVEL = ALWAYS;
-- OR
ALTER ACCOUNT SET TRACE_LEVEL = ALWAYS;
-- Generates massive trace volume, high costs!
```
**Problem:** Traces every execution; 100x data volume; massive serverless costs; performance impact; event table bloat; production noise; unusable for debugging

**Correct Pattern:**
```sql
-- Good: Production uses ON_EVENT (only when telemetry APIs called)
ALTER ACCOUNT SET TRACE_LEVEL = ON_EVENT;

-- Development can use ALWAYS temporarily for debugging
-- (In dev/test environments only!)
ALTER SESSION SET TRACE_LEVEL = ALWAYS;
```
**Benefits:** Production cost-effective; traces only instrumented code; manageable volume; performance maintained; development flexibility; targeted debugging

**Anti-Pattern 4: Not Adding Context Attributes to Spans**
```python
# Bad: Span without context - can't filter or analyze
with telemetry.create_span("process_data"):
    result = process(data)
# Which data? What size? Success? No context!
```
**Problem:** Can't filter traces by criteria; no debugging context; unclear operation details; can't identify patterns; unusable for root cause analysis; poor observability

**Correct Pattern:**
```python
# Good: Add meaningful attributes for filtering and analysis
with telemetry.create_span("process_data") as span:
    span.add_attribute("input_size", len(data))
    span.add_attribute("data_source", data.source)
    span.add_attribute("user_id", user.id)

    result = process(data)

    span.add_attribute("success", result.success)
    span.add_attribute("output_size", len(result.data))
    if not result.success:
        span.add_attribute("error_code", result.error_code)
```
**Benefits:** Filterable traces; rich debugging context; pattern identification; root cause analysis; production debugging; operational insights; actionable observability

## Output Format Examples
```python
# Distributed Tracing Template

from snowflake import telemetry
import logging
import time

logger = logging.getLogger(__name__)

def my_handler(session, input_data):
    """Handler with distributed tracing."""

    # Create span for overall operation
    with telemetry.create_span("my_handler_execution") as span:
        span.set_attribute("input_size", len(input_data))

        logger.info(f"Starting processing for {len(input_data)} records")

        try:
            # Nested span for validation
            with telemetry.create_span("data_validation") as validation_span:
                valid_records = validate_data(input_data)
                validation_span.set_attribute("valid_count", len(valid_records))

            # Nested span for processing
            with telemetry.create_span("data_processing") as process_span:
                results = []
                for i, record in enumerate(valid_records):
                    # Sample progress events (every 1000 records)
                    if i % 1000 == 0 and i > 0:
                        telemetry.add_event(f"Progress: {i}/{len(valid_records)}")

                    try:
                        result = process_record(record)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed processing record {record.id}: {e}")

                process_span.set_attribute("success_count", len(results))
                process_span.set_attribute("error_count", len(valid_records) - len(results))

            logger.info(f"Processing complete: {len(results)} successful")
            span.set_attribute("total_success", True)
            return results

        except Exception as e:
            logger.error(f"Handler failed: {str(e)}")
            span.set_attribute("error", str(e))
            span.set_attribute("total_success", False)
            raise
```

## Python Telemetry Package

### Basic Span Creation

- Use `snowflake-telemetry-python` package for Python handlers to emit trace events
- Import telemetry at module level and create spans for significant processing segments

```python
from snowflake import telemetry

def complex_calculation(session, input_data):
    """Complex calculation with distributed tracing."""

    # Create custom span for the entire calculation
    with telemetry.create_span("complex_calculation") as span:
        span.set_attribute("input_size", len(input_data))

        # Nested span for data validation
        with telemetry.create_span("data_validation") as validation_span:
            validation_span.set_attribute("validation_type", "business_rules")
            valid_data = validate_business_rules(input_data)
            validation_span.set_attribute("valid_records", len(valid_data))

        # Nested span for computation
        with telemetry.create_span("computation") as compute_span:
            compute_span.set_attribute("algorithm", "weighted_average")
            result = perform_calculation(valid_data)
            compute_span.set_attribute("result_count", len(result))

        span.set_attribute("processing_complete", True)
        return result
```

### Span Context and Attributes

- Add relevant attributes to spans to aid performance analysis and troubleshooting
- Include attributes: input size, processing time, success status, error details

**Common Span Attributes:**
- `input_size`: Number of records/rows being processed
- `output_size`: Number of results produced
- `success`: Boolean indicating operation success
- `error`: Error message if operation failed
- `algorithm`: Name of algorithm or processing method
- `stage`: Pipeline stage name
- `duration_ms`: Processing duration (automatically captured)

```python
def data_pipeline_stage(session, stage_name, data):
    """Pipeline stage with performance tracing."""

    with telemetry.create_span(f"pipeline_stage_{stage_name}") as span:
        span.set_attribute("stage", stage_name)
        span.set_attribute("input_rows", len(data))
        span.set_attribute("pipeline_id", session.get_current_database())

        start_time = time.time()

        try:
            # Stage processing logic
            processed_data = transform_data(data, stage_name)

            span.set_attribute("output_rows", len(processed_data))
            span.set_attribute("processing_time_ms", (time.time() - start_time) * 1000)
            span.set_attribute("success", True)

            return processed_data

        except Exception as e:
            span.set_attribute("error", str(e))
            span.set_attribute("success", False)
            raise
```

## Custom Spans for Performance Analysis

### Spans Around Expensive Operations

- Add custom spans around expensive operations, external calls, critical business logic
- Create spans for operations taking >100ms or critical for performance analysis

```python
import time
from snowflake import telemetry

def process_with_performance_tracking(session, data):
    """Track performance of expensive operations."""

    with telemetry.create_span("full_processing") as main_span:
        main_span.set_attribute("total_records", len(data))

        # Span for expensive database query
        with telemetry.create_span("database_query") as db_span:
            db_span.set_attribute("query_type", "JOIN")
            enriched_data = session.sql("""
                SELECT a.*, b.metadata
                FROM input_table a
                JOIN lookup_table b ON a.id = b.id
            """).collect()
            db_span.set_attribute("rows_returned", len(enriched_data))

        # Span for complex transformation
        with telemetry.create_span("transformation") as transform_span:
            transform_span.set_attribute("transform_type", "aggregation")
            result = perform_aggregation(enriched_data)
            transform_span.set_attribute("result_size", len(result))

        main_span.set_attribute("total_duration_ms", (time.time() - main_span.start_time) * 1000)
        return result
```

### Nested Spans for Operation Hierarchy

- Use nested spans to show operation hierarchy and identify bottlenecks
- Visualize end-to-end operation flow and pinpoint slow sub-operations

```python
def multi_stage_pipeline(session, input_data):
    """Multi-stage pipeline with nested tracing."""

    with telemetry.create_span("full_pipeline") as pipeline_span:
        pipeline_span.set_attribute("stages", 3)
        pipeline_span.set_attribute("input_size", len(input_data))

        # Stage 1: Ingestion
        with telemetry.create_span("stage_1_ingestion") as stage1:
            stage1.set_attribute("source", "external_api")
            data_stage1 = ingest_data(input_data)
            stage1.set_attribute("records_ingested", len(data_stage1))

        # Stage 2: Validation
        with telemetry.create_span("stage_2_validation") as stage2:
            stage2.set_attribute("validation_rules", 5)
            data_stage2 = validate_data(data_stage1)
            stage2.set_attribute("valid_records", len(data_stage2))
            stage2.set_attribute("invalid_records", len(data_stage1) - len(data_stage2))

        # Stage 3: Transformation
        with telemetry.create_span("stage_3_transformation") as stage3:
            stage3.set_attribute("transform_type", "normalization")
            final_data = transform_data(data_stage2)
            stage3.set_attribute("output_records", len(final_data))

        pipeline_span.set_attribute("total_output", len(final_data))
        pipeline_span.set_attribute("success", True)

        return final_data
```

## Trace Events and Limitations

### Trace Event Limits (Critical)

- **Maximum:** 128 trace events per span
- **Implication:** High-frequency operations may not capture all events if limit exceeded
- **Mitigation:** Use strategic span creation for key operations, not exhaustive logging

**Anti-Pattern: Creating too many events per span**
```python
# Anti-Pattern: Too many events
with telemetry.create_span("process_batch") as span:
    for i in range(10000):  # Too many iterations
        telemetry.add_event(f"Processing item {i}")  # Will hit 128 limit
```

**Correct: Sample events strategically**
```python
# Correct: Strategic sampling
with telemetry.create_span("process_batch") as span:
    batch_size = 10000
    span.set_attribute("batch_size", batch_size)

    for i in range(batch_size):
        process_item(i)
        # Only log milestones
        if i % 1000 == 0:
            telemetry.add_event(f"Progress: {i}/{batch_size}")
```

### Span Attribute Limits

- **Constraint:** Limited number of custom attributes per span (typically 128)
- **Best Practice:** Use attributes judiciously for high-cardinality data
- Prefer logging detailed messages over excessive span attributes

```python
# Good: Essential attributes only
with telemetry.create_span("operation") as span:
    span.set_attribute("input_size", len(data))
    span.set_attribute("operation_type", "transformation")
    span.set_attribute("success", True)

# Anti-Pattern: Too many attributes
with telemetry.create_span("operation") as span:
    for i, record in enumerate(data):  # Don't create attribute per record
        span.set_attribute(f"record_{i}_status", record.status)  # BAD
```

## Querying Trace Data

### Trace Analysis Queries
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

-- Correlate traces with error logs
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

## System Metrics Collection

### Enabling Metrics

- Enable system metrics collection to monitor CPU and memory usage automatically
- Use metrics data to identify resource bottlenecks and optimize warehouse sizing

```sql
-- Enable metrics collection at account level
ALTER ACCOUNT SET METRIC_LEVEL = ALL;

-- Query system metrics for performance analysis
SELECT
    timestamp,
    resource_attributes:"snow.executable.name"::string as function_name,
    metric_name,
    value
FROM snowflake.account_usage.event_table
WHERE record_type = 'METRIC'
  AND metric_name IN ('cpu_usage_percent', 'memory_usage_bytes')
  AND timestamp >= current_timestamp() - interval '1 hour'
ORDER BY timestamp DESC;
```

### Custom Metrics in Code

Emit custom metrics for business-relevant measurements and performance indicators:

```python
from snowflake import telemetry

def process_batch(session, batch_data):
    """Process batch with custom metrics."""

    with telemetry.create_span("batch_processing") as span:
        # Emit custom metrics
        telemetry.emit_metric("batch_size", len(batch_data))
        telemetry.emit_metric("processing_start", time.time())

        # Processing logic
        results = []
        error_count = 0

        for record in batch_data:
            try:
                processed = process_record(record)
                results.append(processed)
            except Exception as e:
                error_count += 1
                logger.warn(f"Record processing failed: {e}")

        # Emit completion metrics
        telemetry.emit_metric("records_processed", len(results))
        telemetry.emit_metric("processing_errors", error_count)
        telemetry.emit_metric("success_rate", len(results) / len(batch_data))

        return results
```

## TRACE_LEVEL Configuration

### Performance Impact

- **ALWAYS:** Generates trace spans for every function/procedure invocation regardless of errors
- **Performance:** Minimal overhead (<5% typically), but consider cumulative impact at scale
- **Recommendation:** Use ON_EVENT for production (traces only on errors), ALWAYS for debugging

```sql
-- Production: Trace only on errors
ALTER ACCOUNT SET TRACE_LEVEL = ON_EVENT;

-- Development/Debugging: Trace all executions
ALTER SESSION SET TRACE_LEVEL = ALWAYS;
```
