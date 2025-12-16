# Snowflake Dynamic Tables Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** automatic pipelines, DOWNSTREAM, FULL, warehouse sizing, data freshness, create dynamic table, dynamic table lag, refresh frequency, dynamic table error, materialized view alternative, pipeline automation, lag configuration, refresh strategies
**TokenBudget:** ~5200
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/104-snowflake-streams-tasks.md, rules/119-snowflake-warehouse-management.md

## Purpose
Establish comprehensive best practices for Snowflake Dynamic Tables to ensure efficient, maintainable, and cost-effective materialized query results that automatically refresh based on changes to base tables, following Snowflake's recommended patterns for refresh modes, lag configuration, and pipeline architecture.

## Rule Scope

Snowflake Dynamic Tables for automated materialized views, incremental refresh patterns, and data pipeline orchestration

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Declare refresh mode explicitly** - FULL or AUTO (with DOWNSTREAM preferred)
- **Set appropriate lag** - Balance freshness vs compute costs
- **Never use SELECT *** - Explicit column selection required
- **Size warehouse appropriately** - Based on data volume and frequency
- **Monitor refresh operations** - Track costs, duration, failures
- **Use for incremental patterns** - Perfect for aggregations, joins
- **Don't use for real-time** - Streaming or Snowpipe for <1min latency

**Quick Checklist:**
- [ ] Refresh mode declared (FULL/AUTO)
- [ ] Target lag configured
- [ ] Explicit column selection
- [ ] Warehouse sized and assigned
- [ ] Base table dependencies understood
- [ ] Monitoring queries configured
- [ ] Cost baseline established

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~500 tokens (always load for dynamic table tasks)
- + Core Patterns (sections 1-2): ~1200 tokens (load for creation)
- + Advanced Config & Troubleshooting (sections 3-4): ~2000 tokens (load for issues)
- + Complete Reference: ~2500 tokens (full dynamic table guide)

**Recommended Loading Strategy:**
- **Understanding dynamic tables**: Quick Start only
- **Creating tables**: + Core Patterns
- **Lag/refresh issues**: + Advanced Config & Troubleshooting
- **Production deployment**: Full reference

## Contract

<contract>
<inputs_prereqs>
Target database/schema; base tables; warehouse configuration; refresh requirements; data freshness SLAs
</inputs_prereqs>

<mandatory>
SQL DDL for Dynamic Tables; Query Profile; INFORMATION_SCHEMA queries; Snowsight monitoring
</mandatory>

<forbidden>
Using Dynamic Tables without explicit refresh mode declaration; SELECT * in Dynamic Table definitions; unmonitored refresh operations
</forbidden>

<steps>
1. Explicitly set `REFRESH_MODE` (INCREMENTAL or FULL) for all production Dynamic Tables
2. Configure `TARGET_LAG` appropriately (time-based or DOWNSTREAM)
3. Assign dedicated warehouses for refresh operations
4. Chain Dynamic Tables into modular pipelines rather than creating monolithic definitions
5. Validate incremental refresh eligibility using Query Profile
6. Monitor refresh history and performance using INFORMATION_SCHEMA views
</steps>

<output_format>
Complete Dynamic Table DDL with all required parameters; monitoring queries
</output_format>

<validation>
- Verify refresh mode explicitly declared
- Confirm TARGET_LAG aligns with data freshness requirements
- Check Query Profile shows incremental refresh when expected
- Validate warehouse assignment and sizing
- Review refresh history for errors and performance
</validation>

<design_principles>
- **Explicit Configuration:** Always declare `REFRESH_MODE` and `TARGET_LAG` explicitly to ensure predictable behavior across Snowflake releases
- **Modular Pipelines:** Chain smaller, focused Dynamic Tables together rather than creating large, complex monolithic definitions
- **Cost Optimization:** Use transient Dynamic Tables where fail-safe isn't needed; assign dedicated warehouses for monitoring and cost control
- **Incremental First:** Design queries to support incremental refresh when possible; understand limitations and fallback to full refresh
- **Downstream Dependencies:** Use `TARGET_LAG = 'DOWNSTREAM'` to refresh only when dependent objects need updates
- **Security and Access:** Grant MONITOR privilege for metadata access without modification capability; use OWNERSHIP for administrative control
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Omitting Explicit Refresh Mode**
```sql
-- Missing REFRESH_MODE declaration
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_SALES
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
AS
SELECT ...
```
**Problem:** Snowflake's default behavior may change across releases, causing unexpected refresh behavior changes in production.

**Correct Pattern:**
```sql
-- Explicit refresh mode ensures consistency
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_SALES
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL  -- Explicit declaration
AS
SELECT ...
```
**Benefits:** Predictable behavior across Snowflake versions; explicit documentation of design intent.

**Anti-Pattern 2: Using SELECT * in Dynamic Table Definitions**
```sql
-- SELECT * reduces maintainability and performance
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_CUSTOMERS
  TARGET_LAG = '30 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT * FROM raw.customers;  -- Bad: implicit columns
```
**Problem:** Schema changes to base table automatically propagate; no explicit column control; increased storage and compute costs.

**Correct Pattern:**
```sql
-- Explicit column selection
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_CUSTOMERS
  TARGET_LAG = '30 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  customer_id,
  customer_name,
  customer_email,
  created_date,
  last_updated_date
FROM raw.customers;
```
**Benefits:** Explicit schema control; reduced storage costs; clearer data lineage; protection from upstream schema changes.

**Anti-Pattern 3: Monolithic Dynamic Tables with Complex Nesting**
```sql
-- Single massive Dynamic Table with nested logic
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_EVERYTHING
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = FULL  -- Forced by complexity
AS
WITH step1 AS (SELECT ...),
     step2 AS (SELECT ... FROM step1 ...),
     step3 AS (SELECT ... FROM step2 ...),
     step4 AS (SELECT ... FROM step3 ...)
SELECT * FROM step4;
```
**Problem:** Forces full refresh; difficult to debug; no intermediate reusability; poor incremental performance.

**Correct Pattern:**
```sql
-- Chain of focused Dynamic Tables
CREATE OR REPLACE DYNAMIC TABLE staging.DT_STEP1
  TARGET_LAG = '30 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...;

CREATE OR REPLACE DYNAMIC TABLE staging.DT_STEP2
  TARGET_LAG = 'DOWNSTREAM'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ... FROM staging.DT_STEP1;

-- Continue chaining...
```
**Benefits:** Modular design; better incremental refresh; easier debugging; intermediate reusability.

**Anti-Pattern 4: Unmonitored Refresh Operations**
```sql
-- Create Dynamic Table and forget it
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_SALES
  TARGET_LAG = '15 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...;

-- No monitoring, alerting, or validation
```
**Problem:** Silent refresh failures; cost overruns; data staleness issues; no visibility into performance degradation.

**Correct Pattern:**
```sql
-- Create Dynamic Table with monitoring
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_SALES
  TARGET_LAG = '15 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...;

-- Establish monitoring queries
CREATE OR REPLACE VIEW monitoring.VW_DYNAMIC_TABLE_HEALTH AS
SELECT
  table_name,
  target_lag,
  scheduling_state,
  last_refresh_duration_ms,
  CASE
    WHEN scheduling_state = 'FAILED' THEN 'CRITICAL'
    WHEN last_refresh_duration_ms > 300000 THEN 'WARNING'  -- >5 min
    ELSE 'OK'
  END AS health_status
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES;
```
**Benefits:** Proactive issue detection; cost visibility; performance tracking; automated alerting capability.

**Anti-Pattern 5: Using Dynamic Tables for Real-Time Requirements**
```sql
-- Dynamic Table with unrealistic lag expectation
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_REALTIME_DASHBOARD
  TARGET_LAG = '30 seconds'  -- Too aggressive
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...;
```
**Problem:** Dynamic Tables have scheduling overhead (minimum ~1 minute practical lag); excessive refresh frequency causes high costs; may not meet true real-time SLAs.

**Correct Pattern:**
```sql
-- Use appropriate technology for requirements
-- For true real-time (<1 minute): Use Streams + Tasks or query base tables directly
-- For near-real-time (1-15 minutes): Use Dynamic Tables

CREATE OR REPLACE DYNAMIC TABLE analytics.DT_NEAR_REALTIME_DASHBOARD
  TARGET_LAG = '5 minutes'  -- Realistic for Dynamic Tables
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...;
```
**Benefits:** Appropriate technology choice; realistic expectations; cost-effective refresh cadence.

## Post-Execution Checklist

- [ ] `REFRESH_MODE` explicitly declared (INCREMENTAL or FULL) for all production Dynamic Tables
- [ ] `TARGET_LAG` configured appropriately (time-based or DOWNSTREAM)
- [ ] Dedicated warehouse assigned for refresh operations with appropriate sizing
- [ ] Dynamic Table pipeline uses modular chaining instead of monolithic definitions
- [ ] Explicit column selection (no SELECT *) in Dynamic Table definitions
- [ ] Query Profile reviewed to confirm incremental refresh eligibility
- [ ] Transient Dynamic Tables used where fail-safe isn't required
- [ ] MONITOR privilege granted for appropriate roles
- [ ] Refresh history monitoring queries established
- [ ] Alert mechanisms configured for refresh failures
- [ ] Compound grouping keys materialized in separate Dynamic Tables where applicable
- [ ] Data locality optimized (filtered to recent windows, appropriate clustering)
- [ ] Pipeline cloning strategy documented (clone all dependencies together)
- [ ] Controller Dynamic Table pattern considered for complex pipeline networks
- [ ] Cost tracking enabled via warehouse isolation and tagging

## Validation

- **Success Checks:**
  - Query `INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY` shows successful refreshes
  - Query Profile confirms incremental refresh when REFRESH_MODE = INCREMENTAL
  - Actual lag stays within target lag threshold
  - Refresh duration is acceptable for business requirements
  - Warehouse usage isolated and monitored
  - No SELECT * patterns in production Dynamic Tables

- **Negative Tests:**
  - Dynamic Table without explicit REFRESH_MODE should trigger review
  - Incremental refresh on unsupported operations should fall back to full refresh

> **Investigation Required**
> When applying this rule:
> 1. **Read existing Dynamic Tables BEFORE creating new ones** - Check refresh modes, lag settings, patterns
> 2. **Verify base table structure** - Understand data volume, change frequency, dependencies
> 3. **Never assume refresh frequency** - Query REFRESH_HISTORY to understand actual patterns
> 4. **Check warehouse assignments** - Review existing warehouse sizing and costs
> 5. **Test refresh performance** - Monitor first few refreshes before production
>
> **Anti-Pattern:**
> "Creating Dynamic Table... (without understanding base table change patterns)"
> "Using SELECT *... (violates explicit column requirement)"
>
> **Correct Pattern:**
> "Let me check your existing Dynamic Tables setup first."
> [reads existing Dynamic Tables, checks refresh patterns, reviews costs]
> "I see you use AUTO mode with 10-minute lag. Creating new table following this pattern..."
  - Refresh failures logged in INFORMATION_SCHEMA with error details
  - Target lag violations detected via monitoring queries
  - Unassigned warehouses (using default) should trigger configuration review

> **Investigation Required**
> When applying this rule:
> 1. **Read referenced base table schemas BEFORE designing Dynamic Table queries**
> 2. **Check Query Profile to verify incremental refresh eligibility**
> 3. **Never assume incremental refresh will work—validate against supported operations list**
> 4. **Review existing warehouse configuration before assigning to Dynamic Table**
> 5. **Query INFORMATION_SCHEMA to understand current Dynamic Table state before modifications**
>
> **Anti-Pattern:**
> "This query should work with incremental refresh..."
> "Typically Dynamic Tables in this schema use..."
>
> **Correct Pattern:**
> "Let me check the Query Profile to confirm incremental refresh support."
> [reviews Query Profile using EXPLAIN or actual execution]
> "After reviewing the query plan, I found [specific operations]. Here's the appropriate refresh mode..."

## Output Format Examples

```sql
-- Filename: DT_example.sql
-- Description: Dynamic Table for [business purpose]
-- Refresh Mode: [INCREMENTAL | FULL] - [reason]
-- Target Lag: [time | DOWNSTREAM] - [reason]
-- Warehouse: [warehouse_name] - [sizing rationale]

CREATE OR REPLACE DYNAMIC TABLE schema.DT_NAME
  TARGET_LAG = 'value'
  WAREHOUSE = warehouse_name
  REFRESH_MODE = mode
  -- Optional: CLUSTER BY (column_list) for query optimization
AS
SELECT
  explicit_column_1,
  explicit_column_2,
  explicit_column_3
FROM base_table
WHERE filter_condition;

-- Monitoring query
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  TABLE_NAME => 'DT_NAME'
))
ORDER BY refresh_start_time DESC
LIMIT 5;
```

## References

### External Documentation
- [Dynamic Tables Introduction](https://docs.snowflake.com/en/user-guide/dynamic-tables-about) - Complete overview of Dynamic Tables concepts and capabilities
- [Dynamic Tables Best Practices](https://docs.snowflake.com/en/user-guide/dynamic-tables-best-practices) - Official Snowflake recommendations and patterns
- [Dynamic Table Performance Guide](https://docs.snowflake.com/en/user-guide/dynamic-table-performance-guide) - Optimization strategies for refresh operations
- [Dynamic Tables Refresh Modes](https://docs.snowflake.com/en/user-guide/dynamic-tables-refresh) - Detailed refresh behavior and configuration
- [Dynamic Tables Tasks Comparison](https://docs.snowflake.com/en/user-guide/dynamic-tables-tasks-create) - When to use Dynamic Tables vs Streams + Tasks
- [DYNAMIC_TABLE_REFRESH_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/dynamic_table_refresh_history) - Monitoring function reference

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Streams and Tasks**: `rules/104-snowflake-streams-tasks.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - Use parallel tool calls to read base table schemas and Query Profile simultaneously
> - Leverage investigation-first protocol: always check INFORMATION_SCHEMA before making recommendations
> - When asked about incremental refresh eligibility, read the actual query definition and validate against supported operations list
> - For complex pipelines, create visualization of dependencies before recommending changes

## Implementation Details

### Common Pitfalls

**Pitfall 1: Not Declaring REFRESH_MODE and TARGET_LAG Explicitly** [WARNING]
- **Trigger words**: "default settings", omitting REFRESH_MODE/TARGET_LAG
- **Why critical**: Defaults may change across Snowflake releases - unpredictable behavior
- **Correct approach**: Always explicitly declare `REFRESH_MODE = AUTO/FULL/INCREMENTAL` and `TARGET_LAG`
- **Detection**: Check DDL for missing REFRESH_MODE or TARGET_LAG clauses

**Pitfall 2: Creating Large Monolithic Dynamic Tables** [WARNING]
- **Trigger words**: "one big table", complex multi-stage transformations in single DT
- **Why critical**: Hard to debug, maintain, optimize; full refresh on any change
- **Correct approach**: Chain smaller Dynamic Tables with focused transformations
- **Detection**: Review query complexity - flag if >200 lines or >5 CTEs

**Pitfall 3: Using Standard Tables When Transient Would Suffice** [WARNING]
- **Trigger words**: "fail-safe not needed", cost optimization opportunities
- **Why critical**: Standard tables incur fail-safe storage costs unnecessarily
- **Correct approach**: Use transient Dynamic Tables when 7-day fail-safe recovery not required
- **Detection**: Review table type - check if fail-safe actually needed for use case

**Pitfall 4: Not Designing for Incremental Refresh** [WARNING]
- **Trigger words**: "full refresh every time", missing incremental support
- **Why critical**: Full refresh wastes compute and increases latency
- **Correct approach**: Design queries to support incremental refresh (append-only, temporal predicates)
- **Detection**: Check if query uses temporal columns or append-only patterns

## 1. Dynamic Table Fundamentals

### What Are Dynamic Tables?

**MANDATORY:**
Dynamic Tables are declarative materialized views that automatically refresh based on changes to upstream data. They simplify data pipeline management by handling refresh orchestration internally.

**Key Characteristics:**
- Declarative query definition (what, not how)
- Automatic dependency tracking and refresh orchestration
- Support for incremental and full refresh modes
- Integration with Snowflake's task scheduling infrastructure
- Time Travel and cloning support

### When to Use Dynamic Tables

**Good Use Cases:**
- Materialized aggregations updated regularly
- Multi-stage data pipelines with clear dependencies
- Incremental refresh patterns (append-only logs, CDC streams)
- Simplifying complex Streams + Tasks orchestration

**Poor Use Cases:**
- One-time data transformations (use CTAS instead)
- Real-time requirements (<1 minute lag)
- Highly complex queries that can't leverage incremental refresh

### Dynamic Table Naming Convention

**MANDATORY:**

All Dynamic Table names must use the `DT_` prefix to clearly distinguish them from views, base tables, and other database objects.

**Pattern:** `DT_<descriptive_name>`

**Examples:**
```sql
-- Good: Clear Dynamic Table naming
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_DAILY_SALES_SUMMARY ...
CREATE OR REPLACE DYNAMIC TABLE staging.DT_CUSTOMER_360 ...
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_RECENT_ORDERS ...
CREATE OR REPLACE DYNAMIC TABLE dimensions.DT_DIM_CUSTOMERS_SCD1 ...

-- Bad: Missing DT_ prefix
CREATE OR REPLACE DYNAMIC TABLE analytics.DAILY_SALES_SUMMARY ...
CREATE OR REPLACE DYNAMIC TABLE staging.CUSTOMER_360 ...
```

**Benefits:**
- **Clear Identification**: Immediately distinguishes Dynamic Tables from views (`VW_*`) and base tables in data lineage tools
- **Consistent Taxonomy**: Aligns with organizational object naming standards (similar to `VW_` for views per `901-data-generation-modeling.md`)
- **Query Clarity**: Makes SQL queries self-documenting when referencing Dynamic Tables
- **Tooling Integration**: Easier to filter and manage Dynamic Tables in monitoring queries and governance tools

**Naming Best Practices:**
- Use descriptive names that indicate the business purpose: `DT_MONTHLY_REVENUE_ROLLUP`
- Include aggregation level when applicable: `DT_DAILY_*`, `DT_HOURLY_*`, `DT_MONTHLY_*`
- Prefix SCD implementations: `DT_DIM_<entity>_SCD1` or `DT_DIM_<entity>_SCD2`
- Use schema prefixes for context: `staging.DT_*`, `analytics.DT_*`, `dimensions.DT_*`

## 2. Refresh Mode Configuration

### Explicit Refresh Mode Declaration

**MANDATORY:**
**CRITICAL:** Always explicitly set `REFRESH_MODE` for production Dynamic Tables to ensure consistent behavior across Snowflake releases.

**Syntax:**
```sql
CREATE OR REPLACE DYNAMIC TABLE schema.DT_name  -- Note: DT_ prefix
  TARGET_LAG = '10 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL  -- or FULL
AS
  SELECT ...
```

### Incremental Refresh Mode

**RECOMMENDED:**
**When to Use:**
- Append-only data sources (logs, events, CDC streams)
- Aggregations where base table changes are <5% between refreshes
- Queries with supported operations (see limitations below)

**Supported Operations:**
- Filters (WHERE clauses)
- Projections (SELECT columns)
- Joins (with limitations on join types)
- Simple aggregations (SUM, COUNT, MIN, MAX)
- UNION ALL (not UNION)

**Not Supported for Incremental:**
- DISTINCT operations
- Window functions (RANK, ROW_NUMBER, LAG, LEAD)
- Non-deterministic functions (RANDOM, UUID_STRING)
- Subqueries in SELECT list
- Complex aggregations (LISTAGG, ARRAY_AGG)

**Example:**
```sql
-- Incremental refresh: append-only event log aggregation
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_DAILY_EVENTS
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  DATE_TRUNC('day', event_timestamp) AS event_date,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM raw.events
WHERE event_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY 1, 2;
```

### Full Refresh Mode

**MANDATORY:**
**When to Use:**
- Queries with operations not supported for incremental refresh
- Small to medium datasets where full refresh is acceptably fast
- When data correctness requires complete recomputation

**Example:**
```sql
-- Full refresh: uses window functions (not incremental-compatible)
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_CUSTOMER_RANKINGS
  TARGET_LAG = '1 day'
  WAREHOUSE = compute_wh
  REFRESH_MODE = FULL
AS
SELECT
  customer_id,
  total_revenue,
  ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM analytics.customer_summary;
```

## 3. Target Lag Configuration

### Time-Based Lag

**RECOMMENDED:**
Specify maximum acceptable data staleness. Snowflake attempts to keep data within this lag threshold.

**Syntax:**
```sql
TARGET_LAG = '5 minutes'   -- Minutes, hours, days
TARGET_LAG = '2 hours'
TARGET_LAG = '1 day'
```

**Considerations:**
- Shorter lag = more frequent refreshes = higher compute cost
- Set lag based on business requirements, not arbitrary values
- Monitor actual lag vs target lag to detect performance issues

### Downstream Lag

**RECOMMENDED:**
**BEST PRACTICE:** Use `TARGET_LAG = 'DOWNSTREAM'` to refresh only when dependent Dynamic Tables or queries require updates.

**Benefits:**
- Reduces unnecessary refresh operations
- Simplifies pipeline management (no manual lag coordination)
- Optimizes compute cost by refreshing only when needed

**Example:**
```sql
-- Base Dynamic Table with explicit lag
CREATE OR REPLACE DYNAMIC TABLE staging.DT_RAW_ORDERS
  TARGET_LAG = '15 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT * FROM raw.orders WHERE order_date >= DATEADD(day, -30, CURRENT_DATE());

-- Dependent Dynamic Table using DOWNSTREAM
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_ORDER_SUMMARY
  TARGET_LAG = 'DOWNSTREAM'  -- Refresh only when needed
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  order_date,
  COUNT(*) AS order_count,
  SUM(order_amount) AS total_amount
FROM staging.DT_RAW_ORDERS
GROUP BY order_date;
```

## 4. Warehouse Assignment and Isolation

**MANDATORY:**
**CRITICAL:** Assign dedicated warehouses to Dynamic Table refreshes for cost monitoring and workload isolation.

**Best Practices:**
- Create dedicated warehouses for Dynamic Table refresh workloads
- Size warehouses based on refresh duration and frequency requirements
- Enable auto-suspend (60-120 seconds) to minimize idle compute costs
- Use multi-cluster warehouses for concurrent refresh operations
- Follow `119-snowflake-warehouse-management.md` for comprehensive warehouse configuration guidance

**Example:**
```sql
-- Create dedicated warehouse for Dynamic Table refreshes
CREATE WAREHOUSE IF NOT EXISTS dynamic_tables_wh
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Dedicated warehouse for Dynamic Table refresh operations';

-- Assign to Dynamic Table
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_SALES_SUMMARY
  TARGET_LAG = '30 minutes'
  WAREHOUSE = dynamic_tables_wh  -- Isolated warehouse
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...
```

## 5. Pipeline Design Patterns

### Modular Pipeline Chaining

**MANDATORY:**
**BEST PRACTICE:** Chain smaller, focused Dynamic Tables together instead of creating large, monolithic definitions.

**Benefits:**
- Easier to debug and maintain
- Better incremental refresh performance
- Improved reusability across pipelines
- Clearer data lineage

**Anti-Pattern:**
```sql
-- Monolithic Dynamic Table with nested complexity
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_CUSTOMER_ANALYTICS_ALL
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = FULL  -- Complex query forces full refresh
AS
WITH raw_events AS (
  SELECT ... FROM raw.events WHERE ...
),
aggregated AS (
  SELECT ... FROM raw_events ...
),
joined_customers AS (
  SELECT ... FROM aggregated JOIN raw.customers ...
),
final_metrics AS (
  SELECT ... FROM joined_customers ...
)
SELECT * FROM final_metrics;
```

**Correct Pattern:**
```sql
-- Step 1: Filter and normalize raw events
CREATE OR REPLACE DYNAMIC TABLE staging.DT_EVENTS_FILTERED
  TARGET_LAG = '15 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  event_id,
  user_id,
  event_timestamp,
  event_type
FROM raw.events
WHERE event_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP());

-- Step 2: Aggregate events
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_EVENT_AGGREGATES
  TARGET_LAG = 'DOWNSTREAM'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  user_id,
  DATE_TRUNC('day', event_timestamp) AS event_date,
  COUNT(*) AS event_count
FROM staging.DT_EVENTS_FILTERED
GROUP BY user_id, event_date;

-- Step 3: Join with customer data
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_CUSTOMER_ANALYTICS
  TARGET_LAG = 'DOWNSTREAM'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  c.customer_id,
  c.customer_name,
  e.event_date,
  e.event_count
FROM analytics.DT_EVENT_AGGREGATES e
JOIN raw.customers c ON e.user_id = c.customer_id;
```

### Controller Dynamic Table Pattern

**RECOMMENDED:**
For complex pipeline networks, create a "controller" Dynamic Table that reads from all leaf nodes to enable centralized management.

**Use Case:** Change lag, trigger manual refreshes, or suspend entire pipeline from single point.

**Example:**
```sql
-- Controller table aggregates all leaf nodes
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_PIPELINE_CONTROLLER
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = FULL
AS
SELECT
  'sales_summary' AS pipeline,
  MAX(refresh_timestamp) AS last_refresh
FROM analytics.DT_SALES_SUMMARY
UNION ALL
SELECT
  'customer_analytics' AS pipeline,
  MAX(refresh_timestamp) AS last_refresh
FROM analytics.DT_CUSTOMER_ANALYTICS;

-- Manage entire pipeline via controller
ALTER DYNAMIC TABLE analytics.DT_PIPELINE_CONTROLLER SET TARGET_LAG = '30 minutes';
ALTER DYNAMIC TABLE analytics.DT_PIPELINE_CONTROLLER SUSPEND;
ALTER DYNAMIC TABLE analytics.DT_PIPELINE_CONTROLLER RESUME;
```

## 6. Slowly Changing Dimensions (SCD) Patterns

### Type 1 SCD (Overwrite)

**RECOMMENDED:**
Use Dynamic Tables to maintain Type 1 SCDs by reading from change streams.

**Example:**
```sql
-- Stream on source table
CREATE OR REPLACE STREAM raw.customers_stream ON TABLE raw.customers;

-- Dynamic Table applies Type 1 changes
CREATE OR REPLACE DYNAMIC TABLE dimensions.DT_DIM_CUSTOMERS_SCD1
  TARGET_LAG = '5 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  customer_id,
  customer_name,
  customer_email,
  CURRENT_TIMESTAMP() AS last_updated
FROM raw.customers_stream
WHERE METADATA$ACTION = 'INSERT' OR METADATA$ACTION = 'UPDATE';
```

### Type 2 SCD (Historical Tracking)

**RECOMMENDED:**
Implement Type 2 SCDs using window functions over change streams ordered by timestamp.

**Example:**
```sql
-- Dynamic Table maintains Type 2 SCD with history
CREATE OR REPLACE DYNAMIC TABLE dimensions.DT_DIM_CUSTOMERS_SCD2
  TARGET_LAG = '10 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = FULL  -- Window functions require full refresh
AS
WITH changes_ordered AS (
  SELECT
    customer_id,
    customer_name,
    customer_email,
    change_timestamp,
    LEAD(change_timestamp) OVER (
      PARTITION BY customer_id ORDER BY change_timestamp
    ) AS next_change_timestamp
  FROM raw.customers_stream
  WHERE METADATA$ACTION IN ('INSERT', 'UPDATE')
)
SELECT
  customer_id,
  customer_name,
  customer_email,
  change_timestamp AS valid_from,
  COALESCE(next_change_timestamp, '9999-12-31'::TIMESTAMP) AS valid_to,
  CASE WHEN next_change_timestamp IS NULL THEN TRUE ELSE FALSE END AS is_current
FROM changes_ordered;
```

## 7. Performance Optimization

### Simplify Compound Grouping Keys

**RECOMMENDED:**
Materialize compound expressions in one Dynamic Table, then group in a dependent table to improve incremental refresh performance.

**Anti-Pattern:**
```sql
-- Grouping on compound expression hinders incremental refresh
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_MONTHLY_SALES
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  DATE_TRUNC('month', order_date) AS order_month,  -- Compound in GROUP BY
  SUM(order_amount) AS total_sales
FROM raw.orders
GROUP BY DATE_TRUNC('month', order_date);
```

**Correct Pattern:**
```sql
-- Step 1: Materialize the compound expression
CREATE OR REPLACE DYNAMIC TABLE staging.DT_ORDERS_WITH_MONTH
  TARGET_LAG = '30 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  order_id,
  order_date,
  DATE_TRUNC('month', order_date) AS order_month,  -- Materialized
  order_amount
FROM raw.orders;

-- Step 2: Group by materialized column
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_MONTHLY_SALES
  TARGET_LAG = 'DOWNSTREAM'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  order_month,  -- Simple column reference
  SUM(order_amount) AS total_sales
FROM staging.DT_ORDERS_WITH_MONTH
GROUP BY order_month;
```

### Optimize Data Locality

**RECOMMENDED:**
Keep changes between refreshes minimal (<5% of dataset) and ensure query keys align with table clustering to maximize incremental refresh efficiency.

**Best Practices:**
- Filter to recent data windows (last 90 days, last year) where appropriate
- Use clustering keys that align with typical query patterns
- Monitor partition pruning in Query Profile

**Example:**
```sql
-- Well-scoped Dynamic Table with good locality
CREATE OR REPLACE DYNAMIC TABLE analytics.DT_RECENT_ORDERS
  TARGET_LAG = '15 minutes'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
  CLUSTER BY (order_date)  -- Aligns with filter and queries
AS
SELECT
  order_id,
  customer_id,
  order_date,
  order_amount
FROM raw.orders
WHERE order_date >= DATEADD(day, -90, CURRENT_DATE());  -- Recent data only
```

## 8. Cost Optimization

### Use Transient Dynamic Tables

**RECOMMENDED:**
**COST OPTIMIZATION:** Use transient Dynamic Tables when fail-safe recovery (7-day period) isn't required to reduce storage costs.

**Syntax:**
```sql
CREATE OR REPLACE TRANSIENT DYNAMIC TABLE analytics.DT_TEMP_AGGREGATIONS
  TARGET_LAG = '1 hour'
  WAREHOUSE = compute_wh
  REFRESH_MODE = INCREMENTAL
AS
SELECT ...
```

**Use Cases:**
- Intermediate staging tables
- Temporary aggregations
- Development/testing environments
- Data that can be easily recreated

### Clone Pipelines Together

**MANDATORY:**
When cloning Dynamic Table pipelines, clone all dependencies together in a single operation to prevent unnecessary reinitializations.

**Best Practice:** Consolidate Dynamic Table pipelines within the same schema or database.

**Example:**
```sql
-- Clone entire pipeline schema at once
CREATE SCHEMA analytics_dev CLONE analytics;

-- This preserves all Dynamic Table dependencies and refresh state
-- Avoids reinitialization overhead
```

## 9. Security and Access Control

### MONITOR Privilege

**RECOMMENDED:**
Grant MONITOR privilege to roles that need visibility into Dynamic Table metadata without modification capability.

**Example:**
```sql
-- Grant metadata access without modification rights
GRANT MONITOR ON DYNAMIC TABLE analytics.DT_SALES_SUMMARY TO ROLE analyst_role;

-- Analysts can query metadata
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  'DT_SALES_SUMMARY'
));
```

### Ownership and Administration

**MANDATORY:**
Use OWNERSHIP role for administrative operations (ALTER, DROP, REFRESH).

**Example:**
```sql
-- Administrative control
GRANT OWNERSHIP ON DYNAMIC TABLE analytics.DT_SALES_SUMMARY
  TO ROLE data_engineer_role;

-- Data engineers can manage the table
ALTER DYNAMIC TABLE analytics.DT_SALES_SUMMARY SET TARGET_LAG = '1 hour';
ALTER DYNAMIC TABLE analytics.DT_SALES_SUMMARY REFRESH;
```

## 10. Monitoring and Observability

### Query Refresh History

**MANDATORY:**
Monitor Dynamic Table refresh operations using INFORMATION_SCHEMA views.

**Example:**
```sql
-- Check recent refresh history
SELECT
  name,
  state,
  refresh_mode,
  refresh_action,
  scheduling_state,
  data_timestamp,
  refresh_start_time,
  refresh_end_time,
  DATEDIFF('second', refresh_start_time, refresh_end_time) AS refresh_duration_seconds
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  TABLE_NAME => 'DT_SALES_SUMMARY'
))
ORDER BY refresh_start_time DESC
LIMIT 10;
```

### Monitor Lag and Performance

**Example:**
```sql
-- Check current lag and configuration
SELECT
  table_catalog,
  table_schema,
  table_name,
  target_lag,
  refresh_mode,
  warehouse_name,
  scheduling_state,
  last_refresh_duration_ms,
  data_timestamp,
  CURRENT_TIMESTAMP() AS current_time
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLES
WHERE table_schema = 'ANALYTICS'
ORDER BY last_refresh_duration_ms DESC;
```

### Alert on Refresh Failures

**Example:**
```sql
-- Identify failed refreshes
SELECT
  name,
  state,
  refresh_action,
  refresh_start_time,
  error_message
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  TABLE_NAME => 'DT_SALES_SUMMARY'
))
WHERE state = 'FAILED'
ORDER BY refresh_start_time DESC;
```

## Related Rules

**Closely Related** (consider loading together):
- `104-snowflake-streams-tasks` - For alternative imperative approach to CDC pipelines
- `119-snowflake-warehouse-management` - For warehouse assignment to dynamic table refreshes

**Sometimes Related** (load if specific scenario):
- `124-snowflake-data-quality-core` - When adding quality checks to dynamic table pipelines
- `103-snowflake-performance-tuning` - When optimizing dynamic table refresh performance
- `111-snowflake-observability-core` - When monitoring dynamic table lag and refresh status

**Complementary** (different aspects of same domain):
- `100-snowflake-core` - For DDL fundamentals and object naming conventions
- `107-snowflake-security-governance` - For access control on dynamic tables
- `105-snowflake-cost-governance` - For monitoring dynamic table refresh costs
