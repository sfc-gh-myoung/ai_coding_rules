**Keywords:** Observability, logging, tracing, metrics, telemetry, monitoring, query history, ACCOUNT_USAGE, event tables, Snowflake Trail, System Views, Snowsight, Query History, Copy History, Task History, Dynamic Tables, AI Observability
**TokenBudget:** ~7700
**ContextTier:** High
**Depends:** 100-snowflake-core

# Snowflake Observability

## Purpose
Establish comprehensive observability practices for Snowflake environments through proper telemetry configuration, strategic logging, distributed tracing, and metrics collection to ensure effective monitoring, troubleshooting, and performance optimization.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake observability, telemetry configuration, logging, tracing, metrics, and event table management

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Configure telemetry hierarchically** - Account → Database → Schema → Object
- **Use standard logging libraries** - WARN+ for production, DEBUG for dev
- **Implement distributed tracing** - Custom spans for performance analysis
- **Query ACCOUNT_USAGE views** - Historical analysis and patterns
- **Use event tables** - Store and query application logs/traces
- **Monitor with Snowsight** - Built-in visualization and monitoring
- **Never log sensitive data** - PII, credentials must be excluded

**Quick Checklist:**
- [ ] Telemetry levels configured
- [ ] Event tables created
- [ ] Logging library integrated
- [ ] Distributed tracing enabled
- [ ] ACCOUNT_USAGE queries working
- [ ] Snowsight dashboards created
- [ ] Alert thresholds configured

## Key Principles
- Configure telemetry levels hierarchically (Account then Database then Schema then Object) with cost-conscious data volume management.
- Use standard logging libraries with strategic placement; prefer WARN+ for production, DEBUG for development.
- Implement distributed tracing with custom spans for performance analysis and bottleneck identification.
- Enable system metrics collection; organize objects by database/schema for simplified telemetry management.
- Query event tables regularly for analysis; use Snowsight for visualization and monitoring.

## 0. Foundational Concepts

### Snowflake Trail: Comprehensive Observability Suite
- **Always:** Understand that "Snowflake Trail" is Snowflake's umbrella term for its complete observability suite encompassing logs, metrics, traces, events, alerts, and notifications.
- **Rule:** Snowflake Trail provides comprehensive workload monitoring across AI applications, data pipelines, and infrastructure.

### System Views vs Telemetry Data (Critical Distinction)

**System Views (Historical Data):**
- **Purpose:** Historical analysis of completed operations and resource usage patterns.
- **Data Source:** `SNOWFLAKE.ACCOUNT_USAGE` schema with views like `QUERY_HISTORY`, `COPY_HISTORY`, `TASK_HISTORY`.
- **Latency:** Data available with 45 minutes to 3 hours delay (varies by view).
- **Retention:** Typically 365 days of historical data.
- **Use Cases:** Long-term trend analysis, cost attribution, compliance auditing, performance optimization over time.

**Telemetry Data (Event-Driven):**
- **Purpose:** Real-time monitoring of application behavior, errors, and performance from user code.
- **Data Source:** Event tables populated by handler code (functions, procedures, Snowpark).
- **Latency:** Near real-time (seconds to minutes).
- **Retention:** Configurable based on event table settings.
- **Use Cases:** Live debugging, application monitoring, distributed tracing, immediate alerting.

**Critical Rule for AI Agents:**
```xml
> **Investigation Required**  
> When addressing observability questions:
> 1. Determine the data source: System View (historical) vs Event Table (real-time)
> 2. Verify time range requirements match the data source latency
> 3. Check object existence before querying telemetry (use SHOW commands)
> 4. Never speculate about telemetry configuration—read it first with SHOW PARAMETERS
> 5. Understand retention implications before recommending data collection strategies
```

### OpenTelemetry Standard Alignment
- **Always:** Snowflake captures observability data in a structure based on the OpenTelemetry standard.
- **Benefit:** Enables integration with industry-standard observability tools (Grafana, Datadog, Observe).
- **Structure:** Logs, metrics, and traces follow OpenTelemetry semantic conventions for portability.

### Anti-Patterns for AI Agents

**Anti-Pattern: Speculating about telemetry configuration**
```python
# Agent assumes DEBUG logging is enabled
logger.debug("This will only appear if DEBUG is configured")
# Agent doesn't verify actual setting
```

**Correct Pattern: Investigate configuration first**
```sql
-- First, check current telemetry configuration
SHOW PARAMETERS LIKE '%LOG_LEVEL%' IN ACCOUNT;
SHOW PARAMETERS LIKE '%TRACE_LEVEL%' IN ACCOUNT;
SHOW PARAMETERS LIKE '%METRIC_LEVEL%' IN ACCOUNT;

-- Then provide guidance based on actual settings
```

**Anti-Pattern: Using System Views for real-time monitoring**
```sql
-- This won't show recent data (45+ min latency)
SELECT * 
FROM snowflake.account_usage.query_history
WHERE start_time >= current_timestamp() - INTERVAL '5 minutes';
```

**Correct Pattern: Use appropriate data source for time sensitivity**
```sql
-- For real-time: Use event tables from telemetry
SELECT timestamp, body, severity_text
FROM snowflake.account_usage.event_table
WHERE timestamp >= current_timestamp() - INTERVAL '5 minutes'
  AND record_type = 'LOG';

-- For historical: Use System Views
SELECT start_time, query_text, execution_status
FROM snowflake.account_usage.query_history
WHERE start_time >= current_timestamp() - INTERVAL '24 hours';
```

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

### Default Event Table (Enabled by Default)
- **Always:** Snowflake accounts have a default event table automatically enabled in the `SNOWFLAKE.TELEMETRY` schema.
- **Rule:** The default event table (`SNOWFLAKE.TELEMETRY.DEFAULT_EVENT_TABLE`) is active by default and requires no setup for basic telemetry collection.
- **Benefit:** Immediate telemetry collection without configuration overhead.

### Event Table Setup and Verification

**Step 1: Verify Active Event Table**
```sql
-- Check if an event table is active at account level
SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT;

-- List all available event tables
SHOW EVENT TABLES;

-- View event table details
DESC EVENT TABLE snowflake.telemetry.default_event_table;
```

**Step 2: Create Custom Event Table (Optional)**
```sql
-- Create custom event table for specific requirements
CREATE DATABASE IF NOT EXISTS observability_db;
CREATE SCHEMA IF NOT EXISTS observability_db.telemetry;

CREATE EVENT TABLE observability_db.telemetry.custom_event_table
  CLUSTER BY (timestamp)
  DATA_RETENTION_TIME_IN_DAYS = 30;

-- Set as active event table at account level
ALTER ACCOUNT SET EVENT_TABLE = observability_db.telemetry.custom_event_table;

-- Or set at database level for scoped collection
ALTER DATABASE analytics_db SET EVENT_TABLE = observability_db.telemetry.custom_event_table;
```

**Step 3: Configure via Snowsight UI (Alternative Method)**
- **Navigation:** Admin → Monitoring → Event Tables
- **Actions:** View active event table, create new event table, set as account default
- **Benefit:** Visual interface for event table management without SQL

### Event Table Schema Understanding
- **Always:** Understand key columns in event tables for effective querying:
  - `TIMESTAMP`: When the event occurred (real-time)
  - `RECORD_TYPE`: Type of record (LOG, SPAN, METRIC)
  - `SEVERITY_TEXT`: Log level (DEBUG, INFO, WARN, ERROR, FATAL)
  - `BODY`: Log message content or event details
  - `TRACE_ID`: Unique identifier linking related events
  - `SPAN_NAME`: Name of the trace span
  - `DURATION_MS`: Span execution duration in milliseconds
  - `RESOURCE_ATTRIBUTES`: JSON object with context (database, schema, function name)

```sql
-- Query to understand event table structure
SELECT 
    record_type,
    COUNT(*) as event_count,
    MIN(timestamp) as earliest_event,
    MAX(timestamp) as latest_event
FROM snowflake.account_usage.event_table
GROUP BY record_type
ORDER BY event_count DESC;
```

### Anti-Patterns for Event Tables

**Anti-Pattern: Creating event tables without considering retention costs**
```sql
-- Retains data forever, accumulating storage costs
CREATE EVENT TABLE long_term_events
  DATA_RETENTION_TIME_IN_DAYS = 365;  -- May be excessive
```

**Correct Pattern: Balance retention with cost and analysis needs**
```sql
-- Development: shorter retention for cost efficiency
CREATE EVENT TABLE dev_events
  DATA_RETENTION_TIME_IN_DAYS = 7;

-- Production: longer retention for compliance/analysis
CREATE EVENT TABLE prod_events
  CLUSTER BY (timestamp)  -- Improve query performance
  DATA_RETENTION_TIME_IN_DAYS = 90;
```

**Anti-Pattern: Not verifying event table is receiving data**
```python
# Emit log without checking if collection is active
logger.info("Processing started")
# No verification that telemetry is captured
```

**Correct Pattern: Verify telemetry collection after setup**
```sql
-- After configuring telemetry, verify data collection
SELECT 
    resource_attributes:"snow.executable.name"::string as function_name,
    COUNT(*) as log_count
FROM snowflake.account_usage.event_table
WHERE timestamp >= current_timestamp() - INTERVAL '1 hour'
  AND record_type = 'LOG'
GROUP BY function_name
ORDER BY log_count DESC;
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

### Anti-Patterns in Logging

**Anti-Pattern: Logging in tight loops without sampling**
```python
def process_large_dataset(records):
    """Process with excessive logging."""
    for record in records:  # Could be millions of records
        logger.debug(f"Processing record {record.id}")  # Generates huge log volume
        process_record(record)
```
**Problem:** Generates millions of log entries, overwhelming event tables and increasing storage costs.

**Correct Pattern: Use sampling or conditional logging**
```python
def process_large_dataset(records):
    """Process with intelligent logging."""
    total = len(records)
    for i, record in enumerate(records):
        # Log progress at intervals
        if i % 10000 == 0:
            logger.info(f"Progress: {i}/{total} records ({i/total*100:.1f}%)")
        
        try:
            process_record(record)
        except Exception as e:
            # Always log failures
            logger.error(f"Failed processing record {record.id}: {e}")
```

**Anti-Pattern: Using DEBUG level in production environments**
```sql
-- Setting DEBUG for all production workloads
ALTER DATABASE prod_db SET LOG_LEVEL = DEBUG;
```
**Problem:** Generates excessive log volume, increases costs, and may expose sensitive information.

**Correct Pattern: Environment-appropriate log levels**
```sql
-- Production: Conservative logging
ALTER DATABASE prod_db SET LOG_LEVEL = WARN;

-- Development: Verbose logging for debugging
ALTER DATABASE dev_db SET LOG_LEVEL = DEBUG;

-- Critical functions: Targeted debugging
ALTER FUNCTION prod_db.schema.critical_udf(varchar) SET LOG_LEVEL = INFO;
```

**Anti-Pattern: Not using standard logging libraries**
```python
def my_function():
    # Using print statements instead of logging
    print("Starting processing")  # Does NOT route to event tables
    print(f"Error occurred: {error}")  # Not captured in telemetry
```

**Correct Pattern: Use standard logging libraries**
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    # Automatically routes to event tables
    logger.info("Starting processing")
    try:
        # Processing logic
        pass
    except Exception as e:
        logger.error(f"Error occurred: {e}")  # Captured in telemetry
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

## 10. Snowsight Monitoring Interfaces

### Traces & Logs Monitoring Page
- **Navigation:** Monitoring → Traces & Logs
- **Purpose:** Unified interface for real-time monitoring of application telemetry from event tables.
- **Features:**
  - Filter by time range, log level, trace ID
  - Search log message content
  - View trace spans with execution timeline
  - Drill into individual trace details with nested spans

**Usage for AI Agents:**
```xml
> **Investigation Required**  
> When recommending Snowsight monitoring:
> 1. Verify user has access to Monitoring → Traces & Logs
> 2. Confirm event table is active and receiving data
> 3. Guide user to specific filters (severity, time range) relevant to their issue
> 4. Reference trace IDs for end-to-end debugging workflows
```

**Anti-Pattern:**
- Telling users to "check logs" without specific navigation path
- "Navigate to Monitoring → Traces & Logs, filter by Severity = ERROR, Time Range = Last Hour"

### Query History Interface
- **Navigation:** Monitoring → Query History
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
- **Navigation:** Monitoring → Copy History  
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
- **Navigation:** Monitoring → Task History
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
- **Navigation:** Data → Databases → [Select Table] → Refresh History
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
- Using Query History (System View) to debug real-time application issues
- Use Traces & Logs (Event Tables) for real-time, Query History for historical analysis

## 11. AI Observability

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

## 12. Limitations and Considerations

### Trace Event Limits
- **Critical Constraint:** Maximum 128 trace events per span.
- **Implication:** In high-frequency operations, not all events may be captured if limit exceeded.
- **Mitigation:** Use strategic span creation for key operations rather than exhaustive logging.

```python
# Anti-Pattern: Creating too many events per span
with telemetry.create_span("process_batch") as span:
    for i in range(10000):  # Too many iterations
        telemetry.add_event(f"Processing item {i}")  # Will hit 128 limit
```

```python
# Correct: Sample events strategically
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
- **Constraint:** Limited number of custom attributes per span (typically 128).
- **Best Practice:** Use attributes judiciously for high-cardinality data.
- **Rule:** Prefer logging detailed messages over excessive span attributes.

### Event Table Retention
- **Default:** Retention controlled by `DATA_RETENTION_TIME_IN_DAYS` on event table.
- **Cost Impact:** Longer retention increases storage costs.
- **Recommendation:** Balance compliance needs with cost efficiency (7-90 days typical).

### Cost Implications of Verbose Logging
- **DEBUG Level:** Can generate 10-100x more log entries than WARN level.
- **Storage:** Event tables consume storage based on volume and retention.
- **Compute:** Querying large event tables requires warehouse credits.
- **Best Practice:** Use INFO/WARN in production, DEBUG only for targeted debugging.

**Cost Estimation:**
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

## 13. Contract

**MANDATORY:**
- **Inputs/Prereqs:** 
  - Active event table (verify with `SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT`)
  - Appropriate telemetry level configuration for environment
  - Warehouse with SELECT privileges on `SNOWFLAKE.ACCOUNT_USAGE` schema
  - For Python handlers: `snowflake-telemetry-python` package dependency
  - For Java/Scala: SLF4J logging framework configured

- **Allowed Tools:** 
  - `ALTER ACCOUNT/DATABASE/SCHEMA/FUNCTION` for telemetry level configuration
  - Standard logging libraries (Python `logging`, Java `slf4j`, JavaScript `console`)
  - `snowflake-telemetry-python` package for custom spans and attributes
  - SQL queries on event tables (`SNOWFLAKE.ACCOUNT_USAGE.EVENT_TABLE`)
  - SQL queries on System Views (`QUERY_HISTORY`, `COPY_HISTORY`, `TASK_HISTORY`, etc.)
  - Snowsight UI for Traces & Logs visualization
  - `SHOW PARAMETERS` for investigating current telemetry configuration

**FORBIDDEN:**
- **Forbidden Tools:** 
  - Excessive DEBUG logging in production environments without cost analysis
  - Modifying telemetry configuration without understanding retention and cost implications
  - Using System Views (ACCOUNT_USAGE) for real-time monitoring (45+ min latency)
  - Querying event tables with `SELECT *` (always use explicit column projection)
  - Creating event tables without specifying retention policy
  - Speculating about telemetry configuration without reading actual parameter values

**MANDATORY:**
- **Required Steps:**
  1. **Investigate:** Check current telemetry configuration using `SHOW PARAMETERS LIKE '%LOG_LEVEL%'`, `SHOW PARAMETERS LIKE '%TRACE_LEVEL%'`, `SHOW PARAMETERS LIKE '%METRIC_LEVEL%'`
  2. **Verify:** Confirm active event table exists with `SHOW EVENT TABLES` and `SHOW PARAMETERS LIKE 'EVENT_TABLE'`
  3. **Configure:** Set appropriate telemetry levels based on environment (WARN+ for prod, DEBUG for dev)
  4. **Implement:** Add logging/tracing in handler code using standard libraries and telemetry package
  5. **Validate:** Query event tables to confirm data collection is working
  6. **Monitor:** Create monitoring views/queries for ongoing analysis
  7. **Visualize:** Set up Snowsight dashboards and alerts for operational monitoring

- **Output Format:** 
  - SQL DDL statements with explicit telemetry level configuration
  - Python/Java/JavaScript code with proper logging import statements and usage
  - Monitoring queries with explicit column selection (no `SELECT *`)
  - Fully-qualified object names for production queries
  - Comments explaining telemetry strategy and cost considerations

- **Validation Steps:** 
  - Verify telemetry parameters are set correctly with `SHOW PARAMETERS`
  - Confirm event table is receiving data with row count query
  - Validate monitoring queries return expected results without errors
  - Check Snowsight UI displays telemetry data in Traces & Logs interface
  - Ensure log levels are appropriate for environment (no DEBUG in production)
  - Verify retention policy on event tables aligns with cost budget

## 14. Quick Compliance Checklist
- [ ] Event table verified as active before emitting telemetry (`SHOW PARAMETERS LIKE 'EVENT_TABLE'`)
- [ ] Telemetry levels appropriate for environment (WARN+ for prod, DEBUG for dev only)
- [ ] Logging uses standard libraries (Python `logging`, not `print` statements)
- [ ] Trace spans have meaningful names and relevant attributes
- [ ] Monitoring queries use explicit column selection (no `SELECT *`)
- [ ] Cost implications reviewed for verbose logging levels (DEBUG can be 10-100x more data)
- [ ] System Views used for historical analysis (>45 min old), Event Tables for real-time
- [ ] Investigation-first protocol followed (read config with `SHOW PARAMETERS` before recommending changes)
- [ ] Anti-patterns avoided (no tight-loop logging, no DEBUG in prod, no System View for real-time)
- [ ] OpenTelemetry structure understood (logs, metrics, traces with standard conventions)
- [ ] Retention policy set on custom event tables (7-90 days typical)
- [ ] Cross-references checked (`114-snowflake-cortex-aisql.md` for AI costs, `122-snowflake-dynamic-tables.md` for DT monitoring)

## Validation
- **Success Checks:** 
  - Telemetry parameters show expected levels: `SHOW PARAMETERS LIKE '%_LEVEL%' IN ACCOUNT` returns correct LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL
  - Event table receives data: `SELECT COUNT(*) FROM snowflake.account_usage.event_table WHERE timestamp >= current_timestamp() - INTERVAL '1 hour'` returns > 0
  - Logging from handler code appears in event table within minutes
  - Trace spans visible in Snowsight Monitoring → Traces & Logs interface
  - Monitoring queries execute without errors and return expected data types
  - System View queries account for latency (no real-time expectations)
  - Cost analysis confirms telemetry volume is within budget

- **Negative Tests:** 
  - `SELECT * FROM snowflake.account_usage.event_table` should be rejected (use explicit columns)
  - DEBUG level in production should trigger cost review (not automatically allowed)

> **Investigation Required**  
> When applying this rule:
> 1. **Read existing telemetry configuration BEFORE making changes** - Check current LOG_LEVEL, TRACE_LEVEL settings
> 2. **Verify event table setup** - Check if event tables exist and are receiving data
> 3. **Never assume monitoring patterns** - Review existing ACCOUNT_USAGE queries to understand patterns
> 4. **Check Snowsight access** - Verify users can access monitoring dashboards
> 5. **Test telemetry changes** - Validate logs/traces appear after configuration changes
>
> **Anti-Pattern:**
> "Enabling DEBUG logging... (without checking cost impact)"
> "Querying event table with SELECT *... (inefficient, violates best practice)"
>
> **Correct Pattern:**
> "Let me check your current observability setup first."
> [reads telemetry parameters, checks event tables, reviews queries]
> "I see you use WARN level with daily ACCOUNT_USAGE queries. Adding new monitoring following this pattern..."
  - Querying System Views for real-time data (< 45 min) should show no recent results
  - Event table queries without timestamp filters should be discouraged (full table scan)
  - Logging without standard libraries (`print` statements) should not appear in event tables
  - Telemetry configuration changes without `SHOW PARAMETERS` investigation should be caught
  - Creating event tables without retention policy should prompt for cost consideration

## Response Template
```sql
-- Observability Setup Template

-- Step 1: Investigate current configuration
SHOW PARAMETERS LIKE '%LOG_LEVEL%' IN ACCOUNT;
SHOW PARAMETERS LIKE '%TRACE_LEVEL%' IN ACCOUNT;
SHOW PARAMETERS LIKE '%METRIC_LEVEL%' IN ACCOUNT;
SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT;
SHOW EVENT TABLES;

-- Step 2: Configure telemetry levels
ALTER ACCOUNT SET LOG_LEVEL = WARN;      -- Production default
ALTER ACCOUNT SET TRACE_LEVEL = ON_EVENT; -- Trace on errors only
ALTER ACCOUNT SET METRIC_LEVEL = ALL;     -- Enable system metrics

-- Override for development database
ALTER DATABASE dev_db SET LOG_LEVEL = DEBUG;
ALTER DATABASE dev_db SET TRACE_LEVEL = ALWAYS;

-- Step 3: Verify event table is receiving data
SELECT 
    record_type,
    COUNT(*) as event_count,
    MAX(timestamp) as latest_event
FROM snowflake.account_usage.event_table
WHERE timestamp >= current_timestamp() - INTERVAL '1 hour'
GROUP BY record_type;

-- Step 4: Create monitoring view
CREATE OR REPLACE VIEW error_monitoring AS
SELECT 
    timestamp,
    resource_attributes:"snow.database.name"::string as database_name,
    resource_attributes:"snow.executable.name"::string as function_name,
    severity_text,
    body as error_message
FROM snowflake.account_usage.event_table
WHERE record_type = 'LOG'
  AND severity_text IN ('ERROR', 'FATAL')
  AND timestamp >= current_timestamp() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

```python
# Python Handler Logging Template
import logging
from snowflake import telemetry

# Configure logger at module level
logger = logging.getLogger(__name__)

def my_handler(session, input_data):
    """Handler with comprehensive observability."""
    
    # Create span for overall operation
    with telemetry.create_span("my_handler_execution") as span:
        span.set_attribute("input_size", len(input_data))
        
        logger.info(f"Starting processing for {len(input_data)} records")
        
        try:
            # Nested span for specific operation
            with telemetry.create_span("data_validation") as validation_span:
                valid_records = validate_data(input_data)
                validation_span.set_attribute("valid_count", len(valid_records))
            
            # Processing with conditional logging
            results = []
            for i, record in enumerate(valid_records):
                if i % 1000 == 0:  # Progress logging
                    logger.info(f"Progress: {i}/{len(valid_records)}")
                
                try:
                    result = process_record(record)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed processing record {record.id}: {e}")
            
            logger.info(f"Processing complete: {len(results)} successful")
            span.set_attribute("success_count", len(results))
            return results
            
        except Exception as e:
            logger.error(f"Handler failed: {str(e)}")
            span.set_attribute("error", str(e))
            raise
```

## References

### Core Observability Documentation
- [Snowflake Trail Observability Quickstart](https://quickstarts.snowflake.com/guide/getting-started-with-snowflake-trail-for-observability/) - Comprehensive quickstart for getting started with Snowflake Trail observability features
- [Snowflake Logging, Tracing, and Metrics Overview](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-overview) - Comprehensive overview of observability features and OpenTelemetry alignment
- [Event Table Setup Guide](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up) - Step-by-step guide for setting up and managing event tables
- [Snowflake Telemetry Levels](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels) - Complete guide to configuring telemetry levels and hierarchy
- [Snowflake Builders Observability](https://docs.snowflake.com/en/developer-guide/builders/observability) - Best practices for building observable applications

### Logging, Tracing, and Metrics
- [Logging Guide](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging) - Comprehensive guide to logging messages from functions and procedures
- [Snowflake Python Tracing](https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python) - Python-specific tracing implementation guide with telemetry package usage
- [Snowflake Event Tables](https://docs.snowflake.com/en/sql-reference/sql/create-event-table) - Event table DDL syntax, schema, and management

### Snowsight UI and System Views
- [Snowflake Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query performance analysis and optimization using Query Profile
- [Query History](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) - QUERY_HISTORY System View reference
- [Copy History](https://docs.snowflake.com/en/sql-reference/account-usage/copy_history) - COPY_HISTORY System View for data loading monitoring
- [Task History](https://docs.snowflake.com/en/sql-reference/account-usage/task_history) - TASK_HISTORY System View for pipeline monitoring
- [Dynamic Table Refresh History](https://docs.snowflake.com/en/sql-reference/account-usage/dynamic_table_refresh_history) - Monitoring Dynamic Table refresh operations

### AI Observability
 - [Snowflake AI Observability (Cortex)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate and trace generative AI applications with evaluations, comparisons, and tracing features

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md` - Foundation Snowflake practices
- **Cost Governance**: `105-snowflake-cost-governance.md` - Cost optimization strategies applicable to telemetry data
- **Cortex AISQL**: `114-snowflake-cortex-aisql.md` - AI function cost governance and observability patterns
- **Dynamic Tables**: `122-snowflake-dynamic-tables.md` - Dynamic Table monitoring and optimization
