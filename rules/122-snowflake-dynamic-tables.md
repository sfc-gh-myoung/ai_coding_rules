# Snowflake Dynamic Tables Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:dynamic-table, kw:incremental
**Keywords:** automatic pipelines, DOWNSTREAM, FULL, warehouse sizing, data freshness, dynamic table lag, refresh frequency, pipeline automation
**TokenBudget:** ~3050
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 104-snowflake-streams-tasks.md, 119-snowflake-warehouse-management.md

## Scope

**What This Rule Covers:**
Dynamic Tables best practices: refresh modes, lag configuration, warehouse sizing, modular pipelines, monitoring, cost optimization.

**When to Load:**
- Creating/configuring Dynamic Tables
- Troubleshooting refresh issues
- Designing modular data pipelines
- Choosing between Dynamic Tables, materialized views, and Streams/Tasks

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **104-snowflake-streams-tasks.md** - Incremental pipelines and CDC
- **119-snowflake-warehouse-management.md** - Warehouse sizing

**Related:**
- **105-snowflake-cost-governance.md** - Cost optimization
- **103-snowflake-performance-tuning.md** - Query optimization

### External Documentation
- [Dynamic Tables Introduction](https://docs.snowflake.com/en/user-guide/dynamic-tables-intro)
- [Dynamic Tables Refresh](https://docs.snowflake.com/en/user-guide/dynamic-tables-refresh)

## Contract

### Inputs and Prerequisites
- Target database/schema with permissions
- Base tables with data
- Warehouse for refresh operations
- Refresh requirements and data freshness SLAs

### Mandatory
- SQL DDL with explicit REFRESH_MODE
- Query Profile analysis for incremental validation
- Explicit column selection (no SELECT *)

### Forbidden
- Dynamic Tables without explicit REFRESH_MODE
- SELECT * in definitions
- Unmonitored refresh operations
- Monolithic definitions without modular design

### Execution Steps
1. Set REFRESH_MODE explicitly (INCREMENTAL or FULL)
2. Configure TARGET_LAG (time-based or DOWNSTREAM)
3. Assign dedicated warehouses
4. Use explicit column selection
5. Chain Dynamic Tables into modular pipelines
6. Validate incremental refresh via Query Profile
7. Monitor using INFORMATION_SCHEMA views

### Output Format
Complete DDL with REFRESH_MODE, TARGET_LAG, WAREHOUSE; monitoring queries; pipeline documentation

### Validation
**Pre-Task-Completion Checks:** REFRESH_MODE declared, TARGET_LAG configured, no SELECT *, warehouse assigned

**Success Criteria:** Dynamic Table created, refreshes within TARGET_LAG, Query Profile shows incremental (if applicable)

### Design Principles
- **Explicit Configuration:** Always declare REFRESH_MODE and TARGET_LAG
- **Modular Pipelines:** Chain smaller Dynamic Tables vs monolithic definitions
- **Incremental First:** Design for incremental refresh when possible
- **Downstream Dependencies:** Use `TARGET_LAG = 'DOWNSTREAM'` when appropriate

### Post-Execution Checklist
- [ ] REFRESH_MODE explicitly declared
- [ ] TARGET_LAG configured
- [ ] Explicit column selection (no SELECT *)
- [ ] Warehouse assigned and sized appropriately
- [ ] Query Profile validates incremental refresh (if applicable)
- [ ] Monitoring queries configured

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Omitting Explicit Refresh Mode
```sql
-- WRONG: Missing REFRESH_MODE
CREATE DYNAMIC TABLE analytics.DT_SALES TARGET_LAG = '1 hour' WAREHOUSE = wh AS SELECT ...
```
**Problem:** Defaults may change across releases.

**Correct Pattern:**
```sql
CREATE DYNAMIC TABLE analytics.DT_SALES
  TARGET_LAG = '1 hour'
  WAREHOUSE = wh
  REFRESH_MODE = INCREMENTAL  -- Explicit
AS SELECT ...
```

### Anti-Pattern 2: Using SELECT *
```sql
-- WRONG
AS SELECT * FROM raw.customers;
```
**Problem:** Schema changes propagate; no explicit column control; higher costs.

**Correct Pattern:**
```sql
AS SELECT customer_id, customer_name, customer_email FROM raw.customers;
```

### Anti-Pattern 3: Monolithic Dynamic Tables
```sql
-- WRONG: Complex nested CTEs
WITH step1 AS (...), step2 AS (...), step3 AS (...) SELECT * FROM step3;
```
**Problem:** Forces full refresh; hard to debug; no intermediate reusability.

**Correct Pattern:** Chain focused Dynamic Tables with DOWNSTREAM lag.

### Anti-Pattern 4: Unmonitored Operations
**Problem:** Silent failures; cost overruns; data staleness.

**Correct Pattern:**
```sql
SELECT name, state, scheduling_state, last_refresh_duration_ms
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES WHERE table_schema = 'ANALYTICS';
```

### Anti-Pattern 5: Using for Real-Time (<1 min)
```sql
-- WRONG
TARGET_LAG = '30 seconds'  -- Too aggressive
```
**Problem:** DT scheduling overhead; minimum ~1 minute practical lag.

**Correct Pattern:** Use Streams + Tasks for <1 minute requirements; DT for 1-15+ minutes.

### UPSTREAM_FAILED Recovery

When a Dynamic Table shows `scheduling_state = 'UPSTREAM_FAILED'`:

1. Identify the failed upstream: `SELECT name, state FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES WHERE table_schema = '<schema>';`
2. Fix the root cause in the upstream table (schema change, permission, or query error)
3. Run `ALTER DYNAMIC TABLE <upstream> REFRESH` to force a refresh of the upstream table
4. Downstream tables recover automatically once the upstream succeeds

**Target Lag Decision Guide:**
- 1-5 minutes: Real-time dashboards, operational reports
- 15-60 minutes: Hourly aggregations, standard analytics
- DOWNSTREAM: Intermediate pipeline stages (refreshes only when consumed by downstream)

## Implementation Details

### When to Use Dynamic Tables

**Good Use Cases:**
- Materialized aggregations updated regularly
- Multi-stage pipelines with clear dependencies
- Incremental refresh patterns (append-only, CDC)

**Poor Use Cases:**
- One-time transformations (use CTAS)
- Real-time requirements (<1 min lag)
- Complex queries that can't leverage incremental

### Naming Convention
**Pattern:** `DT_<descriptive_name>`
```sql
CREATE DYNAMIC TABLE analytics.DT_DAILY_SALES_SUMMARY ...
CREATE DYNAMIC TABLE dimensions.DT_DIM_CUSTOMERS_SCD1 ...
```

### Refresh Mode Configuration

**INCREMENTAL (Recommended when possible):**
- Append-only data, CDC streams
- <5% data change between refreshes
- Supported: Filters, projections, joins, simple aggregations, UNION ALL
- Not supported: DISTINCT, window functions, non-deterministic functions, subqueries

```sql
CREATE DYNAMIC TABLE analytics.DT_DAILY_EVENTS
  TARGET_LAG = '1 hour'
  WAREHOUSE = wh
  REFRESH_MODE = INCREMENTAL
AS SELECT DATE_TRUNC('day', event_timestamp) AS event_date, COUNT(*) AS count
FROM raw.events WHERE event_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY 1;
```

**FULL (When INCREMENTAL not possible):**
```sql
CREATE DYNAMIC TABLE analytics.DT_CUSTOMER_RANKINGS
  TARGET_LAG = '1 day'
  WAREHOUSE = wh
  REFRESH_MODE = FULL  -- Window functions require FULL
AS SELECT customer_id, ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank FROM summary;
```

### Target Lag Configuration

**Time-Based:**
```sql
TARGET_LAG = '5 minutes'
TARGET_LAG = '2 hours'
TARGET_LAG = '1 day'
```

**DOWNSTREAM (Recommended for dependent tables):**
```sql
-- Base table with explicit lag
CREATE DYNAMIC TABLE staging.DT_RAW_ORDERS TARGET_LAG = '15 minutes' ...

-- Dependent table refreshes only when needed
CREATE DYNAMIC TABLE analytics.DT_ORDER_SUMMARY
  TARGET_LAG = 'DOWNSTREAM'  -- Refresh only when needed
  WAREHOUSE = wh
  REFRESH_MODE = INCREMENTAL
AS SELECT order_date, COUNT(*) FROM staging.DT_RAW_ORDERS GROUP BY 1;
```

### Modular Pipeline Chaining
```sql
-- Step 1: Filter/normalize
CREATE DYNAMIC TABLE staging.DT_EVENTS_FILTERED
  TARGET_LAG = '15 minutes' WAREHOUSE = wh REFRESH_MODE = INCREMENTAL
AS SELECT event_id, user_id, event_timestamp FROM raw.events WHERE event_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP());

-- Step 2: Aggregate (DOWNSTREAM)
CREATE DYNAMIC TABLE analytics.DT_EVENT_AGGREGATES
  TARGET_LAG = 'DOWNSTREAM' WAREHOUSE = wh REFRESH_MODE = INCREMENTAL
AS SELECT user_id, DATE_TRUNC('day', event_timestamp) AS event_date, COUNT(*) AS count
FROM staging.DT_EVENTS_FILTERED GROUP BY 1, 2;

-- Step 3: Join (DOWNSTREAM)
CREATE DYNAMIC TABLE analytics.DT_CUSTOMER_ANALYTICS
  TARGET_LAG = 'DOWNSTREAM' WAREHOUSE = wh REFRESH_MODE = INCREMENTAL
AS SELECT c.customer_id, c.name, e.event_date, e.count
FROM analytics.DT_EVENT_AGGREGATES e JOIN raw.customers c ON e.user_id = c.customer_id;
```

### Warehouse Assignment
```sql
CREATE WAREHOUSE IF NOT EXISTS dynamic_tables_wh
  WAREHOUSE_SIZE = 'MEDIUM' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

CREATE DYNAMIC TABLE analytics.DT_SALES TARGET_LAG = '30 minutes'
  WAREHOUSE = dynamic_tables_wh  -- Dedicated for cost isolation
  REFRESH_MODE = INCREMENTAL AS ...
```

### Cost Optimization

**Transient Tables (when fail-safe not needed):**
```sql
CREATE TRANSIENT DYNAMIC TABLE analytics.DT_TEMP TARGET_LAG = '1 hour' ...
```

**Clone Pipelines Together:**
```sql
CREATE SCHEMA analytics_dev CLONE analytics;  -- Preserves dependencies
```

## Monitoring

### Refresh History
```sql
SELECT name, state, refresh_mode, refresh_action, refresh_start_time,
  DATEDIFF('second', refresh_start_time, refresh_end_time) AS duration_sec
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(TABLE_NAME => 'DT_SALES'))
ORDER BY refresh_start_time DESC LIMIT 10;
```

### Lag and Performance
```sql
SELECT table_name, target_lag, refresh_mode, scheduling_state, last_refresh_duration_ms
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES
WHERE table_schema = 'ANALYTICS' ORDER BY last_refresh_duration_ms DESC;
```

### Failed Refreshes
```sql
SELECT name, state, refresh_start_time, error_message
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(TABLE_NAME => 'DT_SALES'))
WHERE state = 'FAILED' ORDER BY refresh_start_time DESC;
```

### Security
```sql
GRANT MONITOR ON DYNAMIC TABLE analytics.DT_SALES TO ROLE analyst_role;  -- Metadata access
GRANT OWNERSHIP ON DYNAMIC TABLE analytics.DT_SALES TO ROLE data_engineer_role;  -- Admin
```

## Troubleshooting

### Common Issues and Diagnostics

**UPSTREAM_FAILED Status:**
```sql
-- Identify which upstream table caused the failure
SELECT name, state, error_message, refresh_start_time
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(TABLE_NAME => 'DT_SALES'))
WHERE state = 'UPSTREAM_FAILED' ORDER BY refresh_start_time DESC LIMIT 5;

-- Check upstream dynamic table health
SELECT name, scheduling_state, last_completed_refresh_action
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES
WHERE table_schema = 'ANALYTICS' AND scheduling_state != 'ACTIVE';
```

**Incremental Refresh Falling Back to Full:**
```sql
-- Check refresh actions to detect unexpected FULL refreshes
SELECT name, refresh_action, refresh_start_time,
  DATEDIFF('second', refresh_start_time, refresh_end_time) AS duration_sec
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(TABLE_NAME => 'DT_SALES'))
WHERE refresh_action = 'FULL' ORDER BY refresh_start_time DESC LIMIT 10;
-- If seeing FULL when expecting INCREMENTAL, check for unsupported operators
-- (DISTINCT, window functions, non-deterministic functions, subqueries)
```

**Target Lag Not Met:**
```sql
-- Compare actual lag vs target
SELECT name, target_lag, scheduling_state, last_refresh_duration_ms,
  DATEDIFF('minute', last_completed_refresh_time, CURRENT_TIMESTAMP()) AS actual_lag_minutes
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES
WHERE table_schema = 'ANALYTICS'
  AND DATEDIFF('minute', last_completed_refresh_time, CURRENT_TIMESTAMP()) > 
      SPLIT_PART(target_lag, ' ', 1)::INT;
```

## Lifecycle Management

```sql
-- Modify target lag
ALTER DYNAMIC TABLE analytics.DT_SALES SET TARGET_LAG = '30 minutes';

-- Suspend refresh (maintenance window)
ALTER DYNAMIC TABLE analytics.DT_SALES SUSPEND;

-- Resume refresh
ALTER DYNAMIC TABLE analytics.DT_SALES RESUME;

-- Change warehouse
ALTER DYNAMIC TABLE analytics.DT_SALES SET WAREHOUSE = new_wh;

-- Drop dynamic table
DROP DYNAMIC TABLE IF EXISTS analytics.DT_OLD_SUMMARY;
```

## Cost Optimization

**Target Lag vs Credit Consumption:**
- Shorter lag = more frequent refreshes = higher credit usage
- Use `DOWNSTREAM` for intermediate tables to avoid unnecessary refreshes
- Monitor credit consumption per dynamic table:

```sql
-- Credit consumption by dynamic table
SELECT name, SUM(credits_used) AS total_credits,
  COUNT(*) AS refresh_count, AVG(credits_used) AS avg_credits_per_refresh
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME_PREFIX => 'MY_DB.MY_SCHEMA.'
))
WHERE refresh_start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY name ORDER BY total_credits DESC;
```
