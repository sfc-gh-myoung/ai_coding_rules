**Description:** Core observability foundations for Snowflake including telemetry configuration, event table management, and foundational concepts.
**Type:** Agent Requested
**AppliesTo:** `**/*.sql`, `**/*.py`, `**/*.scl`
**AutoAttach:** false
**Keywords:** Observability, Snowflake Trail, telemetry configuration, event tables, LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL, SHOW PARAMETERS, OpenTelemetry, System Views vs Telemetry, monitoring, logging, tracing, debug observability, telemetry setup, event table queries, observability patterns, configure telemetry
**TokenBudget:** ~3550
**ContextTier:** High
**Version:** 2.0
**LastUpdated:** 2025-11-19
**Depends:** 100-snowflake-core

# Snowflake Observability Core

## Purpose
Establish foundational observability practices for Snowflake environments through telemetry configuration and event table management, enabling effective monitoring, troubleshooting, and performance optimization.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake observability foundations, telemetry configuration, event table setup, and basic patterns

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~400 tokens (always load for observability tasks)
- + Telemetry Configuration (sections 1-2): ~1000 tokens (load for setup)
- + Event Tables & Queries (sections 3-4): ~1800 tokens (load for querying)
- + Complete Reference: ~2000 tokens (full observability guide)

**Recommended Loading Strategy:**
- **Understanding observability**: Quick Start only
- **Setting up telemetry**: + Telemetry Configuration
- **Querying events**: + Event Tables & Queries
- **Advanced patterns**: + 111a (logging), 111b (tracing), 111c (monitoring)

## Contract

**MANDATORY:**
- **Inputs/Prereqs:** 
  - Active event table (verify with `SHOW PARAMETERS LIKE 'EVENT_TABLE' IN ACCOUNT`)
  - Appropriate telemetry level configuration for environment
  - Warehouse with SELECT privileges on `SNOWFLAKE.ACCOUNT_USAGE` schema

- **Allowed Tools:** 
  - `ALTER ACCOUNT/DATABASE/SCHEMA/FUNCTION` for telemetry level configuration
  - SQL queries on event tables (`SNOWFLAKE.ACCOUNT_USAGE.EVENT_TABLE`)
  - `SHOW PARAMETERS` for investigating current telemetry configuration
  - `SHOW EVENT TABLES` for verifying event table setup

**FORBIDDEN:**
- **Forbidden Tools:** 
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
  4. **Validate:** Query event tables to confirm data collection is working
  5. **Document:** Cross-reference specialized observability rules for logging, tracing, monitoring

- **Output Format:** 
  - SQL DDL statements with explicit telemetry level configuration
  - Monitoring queries with explicit column selection (no `SELECT *`)
  - Fully-qualified object names for production queries
  - Comments explaining telemetry strategy and cost considerations

- **Validation Steps:** 
  - Verify telemetry parameters are set correctly with `SHOW PARAMETERS`
  - Confirm event table is receiving data with row count query
  - Ensure log levels are appropriate for environment (no DEBUG in production)
  - Verify retention policy on event tables aligns with cost budget

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Configure telemetry hierarchically** - Account → Database → Schema → Object
- **Verify event tables first** - Use `SHOW PARAMETERS LIKE 'EVENT_TABLE'`
- **Use appropriate log levels** - WARN+ for production, DEBUG for dev
- **Understand System Views vs Telemetry** - Historical (45+ min lag) vs Real-time
- **Never speculate about config** - Always read with `SHOW PARAMETERS`
- **Consider cost implications** - DEBUG can generate 10-100x more data
- **Load specialized rules as needed** - 111a (logging), 111b (tracing), 111c (monitoring)

**Quick Checklist:**
- [ ] Telemetry levels configured (`SHOW PARAMETERS` to verify)
- [ ] Event tables created and active
- [ ] Cost implications reviewed (DEBUG vs WARN)
- [ ] System Views understood (not for real-time)

## Key Principles
- Configure telemetry levels hierarchically (Account then Database then Schema then Object) with cost-conscious data volume management.
- Distinguish between System Views (historical, 45+ min latency) and Event Tables (real-time, seconds latency).
- Always investigate current configuration before making changes (`SHOW PARAMETERS` is mandatory).
- Set event table retention policies based on cost budget and analysis needs (7-90 days typical).
- Use specialized rules for specific observability tasks: logging (111a), tracing (111b), monitoring (111c).

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
> **Investigation Required**  
> When addressing observability questions:
> 1. Determine the data source: System View (historical) vs Event Table (real-time)
> 2. Verify time range requirements match the data source latency
> 3. Check object existence before querying telemetry (use SHOW commands)
> 4. Never speculate about telemetry configuration—read it first with SHOW PARAMETERS
> 5. Understand retention implications before recommending data collection strategies

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

## Quick Compliance Checklist
- [ ] Event table verified as active before emitting telemetry (`SHOW PARAMETERS LIKE 'EVENT_TABLE'`)
- [ ] Telemetry levels appropriate for environment (WARN+ for prod, DEBUG for dev only)
- [ ] Cost implications reviewed for verbose logging levels (DEBUG can be 10-100x more data)
- [ ] System Views used for historical analysis (>45 min old), Event Tables for real-time
- [ ] Investigation-first protocol followed (read config with `SHOW PARAMETERS` before recommending changes)
- [ ] Retention policy set on custom event tables (7-90 days typical)
- [ ] Cross-references noted: 111a (logging), 111b (tracing), 111c (monitoring)

## Validation
- **Success Checks:** 
  - Telemetry parameters show expected levels: `SHOW PARAMETERS LIKE '%_LEVEL%' IN ACCOUNT` returns correct LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL
  - Event table receives data: `SELECT COUNT(*) FROM snowflake.account_usage.event_table WHERE timestamp >= current_timestamp() - INTERVAL '1 hour'` returns > 0
  - System View queries account for latency (no real-time expectations)
  - Cost analysis confirms telemetry volume is within budget

- **Negative Tests:** 
  - `SELECT * FROM snowflake.account_usage.event_table` should be rejected (use explicit columns)
  - DEBUG level in production should trigger cost review (not automatically allowed)
  - Querying System Views for real-time data (< 45 min) should show no recent results
  - Telemetry configuration changes without `SHOW PARAMETERS` investigation should be caught
  - Creating event tables without retention policy should prompt for cost consideration

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

## Response Template
```sql
-- Observability Core Setup Template

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
```

## References

### Core Observability Documentation
- [Snowflake Trail Observability Quickstart](https://quickstarts.snowflake.com/guide/getting-started-with-snowflake-trail-for-observability/) - Comprehensive quickstart for getting started with Snowflake Trail observability features
- [Snowflake Logging, Tracing, and Metrics Overview](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-overview) - Comprehensive overview of observability features and OpenTelemetry alignment
- [Event Table Setup Guide](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up) - Step-by-step guide for setting up and managing event tables
- [Snowflake Telemetry Levels](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels) - Complete guide to configuring telemetry levels and hierarchy
- [Snowflake Builders Observability](https://docs.snowflake.com/en/developer-guide/builders/observability) - Best practices for building observable applications

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md` - Foundation Snowflake practices
- **Observability Logging**: `111a-snowflake-observability-logging.md` - Logging best practices and patterns
- **Observability Tracing**: `111b-snowflake-observability-tracing.md` - Distributed tracing and metrics collection
- **Observability Monitoring**: `111c-snowflake-observability-monitoring.md` - Monitoring, analysis, Snowsight interfaces, AI observability
- **Cost Governance**: `105-snowflake-cost-governance.md` - Cost optimization strategies applicable to telemetry data

## Related Rules

**Closely Related** (consider loading together):
- `111a-snowflake-observability-logging` - For logging best practices and standard library integration
- `111b-snowflake-observability-tracing` - For distributed tracing patterns with custom spans
- `111c-snowflake-observability-monitoring` - For monitoring queries and Snowsight interfaces

**Sometimes Related** (load if specific scenario):
- `103-snowflake-performance-tuning` - When using telemetry data for performance optimization
- `115b-snowflake-cortex-agents-operations` - When implementing agent observability and evaluation
- `109-snowflake-notebooks` - When adding telemetry to notebook executions

**Complementary** (different aspects of same domain):
- `105-snowflake-cost-governance` - For monitoring costs using telemetry data
- `107-snowflake-security-governance` - For security event monitoring and audit logs
