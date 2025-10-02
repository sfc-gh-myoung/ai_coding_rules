**Description:** Comprehensive observability practices for Snowflake telemetry, logging, tracing, and metrics following best practices.
**AppliesTo:** `**/*.sql`, `**/*.py`, `**/*.scl`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-17

# Snowflake Observability

## Purpose
Establish comprehensive observability practices for Snowflake environments through proper telemetry configuration, strategic logging, distributed tracing, and metrics collection to ensure effective monitoring, troubleshooting, and performance optimization.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake observability, telemetry configuration, logging, tracing, metrics, and event table management

## Key Principles
- Configure telemetry levels hierarchically (Account then Database then Schema then Object) with cost-conscious data volume management.
- Use standard logging libraries with strategic placement; prefer WARN+ for production, DEBUG for development.
- Implement distributed tracing with custom spans for performance analysis and bottleneck identification.
- Enable system metrics collection; organize objects by database/schema for simplified telemetry management.
- Query event tables regularly for analysis; use Snowsight for visualization and monitoring.

## 1. Telemetry Configuration

### Telemetry Level Hierarchy
- **Always:** Understand the telemetry hierarchy: Account then Database then Schema then Object, and Session overrides.
- **Rule:** Set account-level defaults, override at database/schema for specific workloads, and use session overrides for debugging.
- **Always:** Use the most verbose level when both session and object parameters are set.

```sql
-- Account-level baseline configuration
ALTER ACCOUNT SET LOG_LEVEL = WARN;
ALTER ACCOUNT SET TRACE_LEVEL = ON_EVENT;
ALTER ACCOUNT SET METRIC_LEVEL = ALL;

-- Database-specific overrides for development
ALTER DATABASE dev_db SET LOG_LEVEL = INFO;
ALTER DATABASE dev_db SET TRACE_LEVEL = ALWAYS;

-- Function-specific debugging
ALTER FUNCTION critical_udf(varchar) SET LOG_LEVEL = DEBUG;

-- Session-level debugging
ALTER SESSION SET LOG_LEVEL = DEBUG;
ALTER SESSION SET TRACE_LEVEL = ALWAYS;
```

### Privilege Requirements
- **Requirement:** Grant appropriate privileges for telemetry management:

```sql
-- Central logging administrator role
GRANT MODIFY LOG LEVEL ON ACCOUNT TO ROLE central_log_admin;
GRANT MODIFY TRACE LEVEL ON ACCOUNT TO ROLE central_log_admin;
GRANT MODIFY METRIC LEVEL ON ACCOUNT TO ROLE central_log_admin;

-- Developer debugging privileges
GRANT MODIFY SESSION LOG LEVEL TO ROLE developer_debugging;
GRANT MODIFY SESSION TRACE LEVEL TO ROLE developer_debugging;
```

## 2. Event Table Management

### Event Table Setup
- **Always:** Ensure an active event table exists for telemetry data collection.
- **Rule:** Use the default Snowflake event table unless specific requirements demand a custom table.

```sql
-- Verify active event table
SHOW EVENT TABLES;

-- Create custom event table if needed
CREATE EVENT TABLE my_custom_events;
ALTER ACCOUNT SET EVENT_TABLE = my_database.my_schema.my_custom_events;
```

### Event Table Querying
- **Always:** Query event tables regularly for monitoring and analysis.
- **Rule:** Use structured queries to filter by object type, severity, and time ranges.

```sql
-- Query recent errors and warnings
SELECT 
    timestamp,
    resource_attributes:"snow.database.name"::string as database_name,
    resource_attributes:"snow.schema.name"::string as schema_name,
    resource_attributes:"snow.executable.name"::string as object_name,
    severity_text,
    body
FROM snowflake.account_usage.event_table
WHERE timestamp >= current_timestamp() - interval '1 hour'
  AND severity_text IN ('WARN', 'ERROR', 'FATAL')
ORDER BY timestamp DESC;

-- Analyze trace performance patterns
SELECT 
    resource_attributes:"snow.executable.name"::string as function_name,
    span_name,
    AVG(duration_ms) as avg_duration_ms,
    COUNT(*) as execution_count
FROM snowflake.account_usage.event_table
WHERE record_type = 'SPAN'
  AND timestamp >= current_timestamp() - interval '24 hours'
GROUP BY 1, 2
HAVING avg_duration_ms > 1000
ORDER BY avg_duration_ms DESC;
```

## 3. Logging Best Practices

### Standard Library Integration
- **Always:** Use standard logging libraries (Python `logging`, Java `slf4j`) that automatically route to event tables.
- **Rule:** Structure log messages with context and avoid excessive logging in tight loops.

```python
import logging

# Configure logging in Python handlers
logger = logging.getLogger(__name__)

def process_data(session, df):
    """Process DataFrame with comprehensive logging."""
    logger.info(f"Starting data processing for {len(df)} rows")
    
    try:
        # Processing logic
        result = df.filter(df.amount > 0)
        logger.info(f"Filtered to {len(result)} valid records")
        
        if len(result) == 0:
            logger.warn("No valid records found after filtering")
            return None
            
        # Additional processing
        transformed = result.withColumn("processed_at", current_timestamp())
        logger.info("Data transformation completed successfully")
        
        return transformed
        
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        raise
```

### Log Level Strategy
- **Production:** Use WARN or ERROR to capture significant events without excessive verbosity.
- **Development:** Use INFO or DEBUG for detailed troubleshooting.
- **Critical Systems:** Use ERROR or FATAL for mission-critical components.

```sql
-- Production environment logging
ALTER DATABASE prod_db SET LOG_LEVEL = WARN;

-- Development environment logging  
ALTER DATABASE dev_db SET LOG_LEVEL = INFO;

-- Critical UDF debugging
ALTER FUNCTION critical_calculation(number, number) SET LOG_LEVEL = DEBUG;
```

### Conditional Logging
- **Rule:** Use conditional statements to log only meaningful scenarios and control data volume.

```python
def validate_input(data):
    """Validate input with conditional logging."""
    if not data:
        logger.error("Input data is empty or null")
        return False
        
    if len(data) > 10000:
        logger.warn(f"Large dataset detected: {len(data)} records")
        
    # Only log validation details for problematic cases
    invalid_count = sum(1 for row in data if not is_valid(row))
    if invalid_count > 0:
        logger.warn(f"Found {invalid_count} invalid records out of {len(data)}")
        
    return invalid_count == 0
```

## 4. Distributed Tracing

### Python Telemetry Package
- **Always:** Use the `snowflake-telemetry-python` package for Python handlers to emit trace events.
- **Rule:** Import telemetry at the module level and create spans for significant processing segments.

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

### Custom Spans for Performance Analysis
- **Always:** Add custom spans around expensive operations, external calls, and critical business logic.
- **Rule:** Include relevant attributes in spans to aid in performance analysis and troubleshooting.

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

## 5. Metrics Collection

### System Metrics
- **Always:** Enable system metrics collection to monitor CPU and memory usage automatically.
- **Rule:** Use metrics data to identify resource bottlenecks and optimize warehouse sizing.

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
- **Rule:** Emit custom metrics for business-relevant measurements and performance indicators.

```python
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

## 6. Cost and Volume Management

### Data Volume Control
- **Rule:** Implement strategies to control telemetry data volume and associated storage costs.
- **Always:** Use appropriate log levels and conditional logging to prevent data overflow.

```python
# Volume-conscious logging strategy
def log_with_sampling(logger, level, message, sample_rate=0.1):
    """Log messages with sampling to control volume."""
    if random.random() < sample_rate:
        logger.log(level, f"[SAMPLED] {message}")

# Use for high-frequency operations
for record in large_dataset:
    result = process_record(record)
    
    # Only log a sample of successful operations
    if result.success:
        log_with_sampling(logger, logging.INFO, f"Processed record {record.id}")
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

## 7. Monitoring and Analysis

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

### Snowsight Integration
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

## 8. Security and Governance Integration

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

## 9. Troubleshooting and Optimization

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Snowflake Telemetry Levels](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels) - Complete guide to configuring telemetry levels and hierarchy
- [Snowflake Logging, Tracing, and Metrics Overview](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-overview) - Comprehensive overview of observability features
- [Snowflake Python Tracing](https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python) - Python-specific tracing implementation guide
- [Snowflake Builders Observability](https://docs.snowflake.com/en/developer-guide/builders/observability) - Best practices for building observable applications
- [Snowflake Event Tables](https://docs.snowflake.com/en/sql-reference/sql/create-event-table) - Event table creation and management
- [Snowflake Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query performance analysis and optimization
 - [Snowflake AI Observability (Cortex)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate and trace generative AI applications with evaluations, comparisons, and tracing features
