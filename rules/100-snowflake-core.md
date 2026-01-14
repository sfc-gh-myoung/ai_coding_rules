# Snowflake Core Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Snowflake patterns. Load for Snowflake tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** SQL, CTE, performance, cost optimization, query profile, warehouse, security, governance, stages, COPY INTO, streams, tasks, warehouse creation
**TokenBudget:** ~4600
**ContextTier:** High
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Comprehensive foundational practices for all Snowflake development work, ensuring cost-effective, performant, and secure solutions through proper SQL authoring, object naming, security policies, and architectural patterns.

**When to Load This Rule:**
- Writing or modifying Snowflake SQL queries
- Creating or modifying Snowflake database objects (tables, views, stages, pipes, tasks)
- Performance tuning Snowflake queries
- Implementing Snowflake security policies (masking, row access)
- Designing incremental data pipelines with Streams and Tasks
- Optimizing Snowflake costs and warehouse usage
- Loading data into Snowflake (COPY INTO, Snowpipe)
- Working with VARIANT/semi-structured data

### Quantification Standards

**Data Volume Thresholds:**
- **Large table:** >10M rows OR >5GB uncompressed OR >1M rows with >1000 updates/hour OR >10% rows modified per day (context: incremental patterns with Streams + Tasks)
- **Minimal data movement:** <10% of source data copied or transformed (context: validation of efficient query design)

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Recommended:**
- **103-snowflake-performance-tuning.md** - Detailed query profiling and optimization
- **105-snowflake-cost-governance.md** - Cost monitoring and resource management
- **119-snowflake-warehouse-management.md** - Warehouse sizing, types, and configuration

**Related:**
- **101-snowflake-streamlit-core.md** - Streamlit UI development on Snowflake
- **102-snowflake-sql-core.md** - General SQL file patterns
- **104-snowflake-streams-tasks.md** - Incremental pipelines with Streams + Tasks
- **106-snowflake-semantic-views-core.md** - View layering and naming conventions
- **107-snowflake-security-governance.md** - Security policies and governance
- **108-snowflake-data-loading.md** - Data loading patterns (COPY INTO)
- **121-snowflake-snowpipe.md** - Continuous ingestion with Snowpipe
- **123-snowflake-object-tagging.md** - Object tagging for governance

### External Documentation

**Official Documentation:**
- [Snowflake Documentation](https://docs.snowflake.com/) - Complete platform documentation
- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) - SQL command reference and syntax
- [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/best-practices) - Performance and cost optimization
- [Snowflake Security Guide](https://docs.snowflake.com/en/user-guide/security) - Security features and implementation

## Contract

### Inputs and Prerequisites

- Target database/schema identified
- Warehouse context available
- Table/view inventory known
- Access roles configured
- Understanding of data model and business requirements

### Mandatory

- **SQL Authoring:** Write explicit, well-structured SQL with clear CTEs
- **Object Qualification:** Fully qualify all objects (`DATABASE.SCHEMA.TABLE`)
- **Column Selection:** Explicit column lists (never `SELECT *` in production)
- **Performance Profiling:** Use Snowflake UI/CLI Query Profile for optimization
- **Security Policies:** Apply masking/row access policies for sensitive data
- **Incremental Patterns:** Use Streams + Tasks for mutable large tables (>10M rows OR >5GB uncompressed OR >1M rows with >1000 updates/hour OR >10% rows modified per day)

### Forbidden

- **Never** use `SELECT *` in production code
- **Never** use `DISTINCT` as a deduplication band-aid (solve root cause)
- **Never** parse VARIANT fields multiple times (extract once in CTE)
- **Never** use template characters in identifiers (`&`, `<%`, `%>`, `{{`, `}}`)
- **Never** implement full table reloads when incremental processing is viable

### Execution Steps

1. Define explicit columns and joins; add WHERE filters in the first CTE (before JOINs/aggregations) for partition pruning
2. Normalize VARIANT fields once in a dedicated CTE
3. Prefer set-based operations; avoid row-wise loops
4. For mutable large tables (>10M rows OR >5GB OR >1M rows with >1000 updates/hour OR >10% rows modified per day), design Streams + Tasks incremental pattern with idempotency
5. Validate with Query Profile before scaling warehouse
6. Apply security policies (masking/row access) where needed
7. Verify no anti-patterns present (SELECT *, DISTINCT dedupe, repeated VARIANT parsing)

### Output Format

```sql
-- Explicit column selection, early filters, single VARIANT extraction CTE
WITH src AS (
  SELECT v:customer_id::string AS customer_id,
         v:order_ts::timestamp_ntz AS order_ts,
         v:total_amount::number AS total_amount
  FROM RAW_DB.STAGE.ORDERS_JSON
  WHERE v:order_ts::timestamp_ntz >= DATEADD(day, -7, CURRENT_TIMESTAMP())
),
agg AS (
  SELECT customer_id, COUNT(*) AS num_orders, SUM(total_amount) AS total_amount
  FROM src
  GROUP BY customer_id
)
SELECT * FROM agg;
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Code Quality:**
- **CRITICAL:** All queries use explicit column selection (no `SELECT *`)
- **CRITICAL:** WHERE clauses applied early to reduce scan size
- **CRITICAL:** VARIANT fields parsed once in dedicated CTE
- **CRITICAL:** No `DISTINCT` used for deduplication (use `ROW_NUMBER()` with `QUALIFY`)
- **Format Check:** SQL keywords in UPPERCASE for consistency
- **Object Naming:** Follows DDL naming conventions

**Performance:**
- **CRITICAL:** Query Profile reviewed for performance bottlenecks
- **CRITICAL:** Partition pruning and early filtering confirmed
- **CRITICAL:** Minimal data movement verified

**Security and Governance:**
- **CRITICAL:** Row Access Policies or Dynamic Data Masking applied for PII
- **Resource Monitors:** Configured for cost governance
- **Warehouse Config:** Follows `119-snowflake-warehouse-management.md`

**Incremental Processing:**
- **Where Applicable:** Streams and Tasks used for mutable large tables (>10M rows OR >5GB OR >1M rows with >1000 updates/hour OR >10% rows modified per day)
- **Idempotency:** MERGE operations handle late arrivals and duplicates

**Success Criteria:**
- Query Profile shows pruning and minimized data movement
- No `SELECT *` in production code
- Incremental pattern present for mutable facts
- Security policies applied where needed

**Validation Protocol:**
- **Rule:** Run Query Profile after implementation
- **Rule:** Verify explicit columns in all queries
- **Rule:** Confirm early filtering and partition pruning

**Investigation Required:**
1. **Read SQL files and table definitions BEFORE making recommendations**
2. **Verify schema structure and column types against actual metadata**
3. **Never speculate about table structures or data types**
4. **Check Query Profile for actual performance characteristics**
5. **Make grounded recommendations based on investigated schema and data**

**Anti-Pattern Examples:**
- Using `SELECT *` in production queries
- Parsing VARIANT fields multiple times across clauses
- Full table scans when incremental processing is viable
- `DISTINCT` for deduplication instead of `QUALIFY ROW_NUMBER()`

**Correct Pattern:**
- "Let me check your table structure first."
- [reads table definitions, examines Query Profile]
- "I see you're working with semi-structured data. Here's how to optimize VARIANT parsing..."
- [implements CTE-based extraction, validates with Query Profile]

### Design Principles

- **Cost-First Mindset:** Always consider cost implications of query patterns
- **Explicit Object Qualification:** Fully qualify objects (`DATABASE.SCHEMA.TABLE`)
- **Set-Based Operations:** Prefer declarative SQL over procedural loops
- **CTE Usage:** Use CTEs for logical segmentation and readability
- **Early Filtering:** Push WHERE filters in the first CTE (before JOINs/aggregations) for partition pruning
- **VARIANT Optimization:** Parse semi-structured data once at edge, normalize critical fields
- **Incremental Processing:** Use Streams + Tasks for mutable large tables (>10M rows OR >5GB OR >1M rows with >1000 updates/hour OR >10% rows modified per day)
- **Security by Design:** Enforce governance with masking policies, row access, and tagging
- **Query Profiling:** Always use Query Profile to validate performance assumptions

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Target database/schema identified
- [ ] Warehouse context available
- [ ] Understanding of table structures and data model

**After Completion:**
- [ ] **CRITICAL:** All queries use explicit column selection (no `SELECT *`)
- [ ] **CRITICAL:** WHERE clauses applied early to reduce scan size
- [ ] **CRITICAL:** VARIANT fields parsed once in dedicated CTE
- [ ] **CRITICAL:** Query Profile reviewed for performance bottlenecks
- [ ] Warehouse configuration follows `119-snowflake-warehouse-management.md`
- [ ] Row Access Policies or Dynamic Data Masking applied for PII
- [ ] Resource monitors configured for cost governance
- [ ] Streams and Tasks used for incremental processing where applicable
- [ ] SQL keywords in UPPERCASE for consistency
- [ ] Object names follow DDL naming conventions
- [ ] No `DISTINCT` used for deduplication (use `ROW_NUMBER()` instead)
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in identifiers

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using SELECT * Instead of Explicit Columns

```sql
-- Bad: SELECT * wastes I/O and parsing
SELECT *
FROM large_table
WHERE order_date >= '2024-01-01';
-- Scans all 50 columns, even if you need only 3!
```

**Problem:** Excessive I/O; wasted credits; slow queries; partition pruning disabled; unnecessary data transfer; poor performance; high costs

**Correct Pattern:**
```sql
-- Good: Explicit column selection
SELECT
  order_id,
  customer_id,
  order_date,
  total_amount
FROM large_table
WHERE order_date >= '2024-01-01';
-- Scans only required columns, much faster and cheaper
```

**Benefits:** Minimal I/O; faster queries; lower credits; efficient pruning; reduced data transfer; better performance; cost-effective

### Anti-Pattern 2: Parsing VARIANT Fields Multiple Times

```sql
-- Bad: Parse VARIANT in every clause
SELECT
  raw_json:customer:id::string AS customer_id,
  raw_json:customer:name::string AS customer_name,
  SUM(raw_json:amount::number) AS total_amount
FROM events
WHERE raw_json:event_type::string = 'purchase'
  AND raw_json:timestamp::timestamp_ntz >= '2024-01-01'
GROUP BY raw_json:customer:id::string, raw_json:customer:name::string;
-- Parses raw_json 7 times! Extremely expensive!
```

**Problem:** Repeated parsing overhead; high CPU usage; slow queries; wasted credits; inefficient; poor performance; violates Snowflake best practices

**Correct Pattern:**
```sql
-- Good: Parse VARIANT once in CTE
WITH parsed AS (
  SELECT
    raw_json:customer:id::string AS customer_id,
    raw_json:customer:name::string AS customer_name,
    raw_json:amount::number AS amount,
    raw_json:event_type::string AS event_type,
    raw_json:timestamp::timestamp_ntz AS event_timestamp
  FROM events
  WHERE raw_json:timestamp::timestamp_ntz >= '2024-01-01'
)
SELECT
  customer_id,
  customer_name,
  SUM(amount) AS total_amount
FROM parsed
WHERE event_type = 'purchase'
GROUP BY customer_id, customer_name;
-- Parses each field once, reuses parsed values, much faster!
```

**Benefits:** Parse once; reuse values; lower CPU; faster queries; fewer credits; efficient; better performance; professional

### Anti-Pattern 3: Not Using Streams and Tasks for Incremental Processing

```sql
-- Bad: Full table scan every hour
CREATE TASK hourly_aggregation
WAREHOUSE = compute_wh
SCHEDULE = '60 MINUTE'
AS
DELETE FROM summary_table;  -- Drop all data!

INSERT INTO summary_table
SELECT
  customer_id,
  DATE_TRUNC('hour', order_timestamp) AS hour,
  SUM(amount) AS total_amount
FROM orders  -- Full scan of millions of rows every hour!
GROUP BY customer_id, hour;
-- Scans entire table, deletes and recreates everything, very expensive!
```

**Problem:** Full table scans; unnecessary processing; high credits; slow updates; DELETE/INSERT overhead; not scalable; violates Snowflake best practices; high cost

**Correct Pattern:**
```sql
-- Good: Incremental processing with Streams and Tasks
-- Step 1: Create Stream to capture changes (with error handling)
CREATE STREAM IF NOT EXISTS orders_stream ON TABLE orders;

-- Error handling for Stream creation:
-- If orders table doesn't exist:
--   1. Verify table name: SELECT * FROM information_schema.tables WHERE table_name = 'ORDERS';
--   2. If found, check permissions: SHOW GRANTS ON TABLE orders;
--   3. If not found, report error: "Table orders does not exist. Verify table name and database/schema."

-- Step 2: Create Task for incremental aggregation
CREATE TASK incremental_aggregation
WAREHOUSE = compute_wh
SCHEDULE = '60 MINUTE'
WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')  -- Only runs if new data
AS
MERGE INTO summary_table tgt
USING (
  SELECT
    customer_id,
    DATE_TRUNC('hour', order_timestamp) AS hour,
    SUM(amount) AS total_amount
  FROM orders_stream  -- Only new/changed rows!
  WHERE METADATA$ACTION = 'INSERT'
  GROUP BY customer_id, hour
) src
ON tgt.customer_id = src.customer_id AND tgt.hour = src.hour
WHEN MATCHED THEN UPDATE SET total_amount = tgt.total_amount + src.total_amount
WHEN NOT MATCHED THEN INSERT (customer_id, hour, total_amount)
  VALUES (src.customer_id, src.hour, src.total_amount);

ALTER TASK incremental_aggregation RESUME;
-- Processes only new rows, MERGE updates incrementally, extremely efficient!

-- Error handling for Task failures:
-- If MERGE fails with timeout: Increase warehouse size (ALTER WAREHOUSE compute_wh SET WAREHOUSE_SIZE = 'MEDIUM') OR reduce batch window
-- If MERGE fails with constraint violation: Add data validation CTE before MERGE to filter invalid rows
-- If warehouse suspended: Check resource monitor settings (SHOW RESOURCE MONITORS) and credit limits
-- If repeated failures: Add error notification via SYSTEM$SEND_EMAIL or external integration
-- Monitor with: SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY()) WHERE NAME = 'incremental_aggregation' ORDER BY SCHEDULED_TIME DESC LIMIT 10;
```

**Benefits:** Incremental processing; minimal scans; low credits; fast updates; scalable; efficient MERGE; professional; cost-effective

### Anti-Pattern 4: Using DISTINCT for Deduplication Instead of QUALIFY

```sql
-- Bad: DISTINCT for deduplication
SELECT DISTINCT
  customer_id,
  order_id,
  order_timestamp,
  amount
FROM (
  SELECT
    customer_id,
    order_id,
    order_timestamp,
    amount,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
  FROM orders_with_duplicates
)
WHERE rn = 1;
-- DISTINCT on entire result set, inefficient, extra processing!
```

**Problem:** Unnecessary DISTINCT; extra sorting; wasted memory; inefficient; unclear intent; poor performance; violates Snowflake best practices

**Correct Pattern:**
```sql
-- Good: Use QUALIFY for window function filtering
SELECT
  customer_id,
  order_id,
  order_timestamp,
  amount
FROM orders_with_duplicates
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1;
-- Single pass, efficient filtering, clear intent, optimal performance!
```

**Benefits:** Single pass; no extra sorting; minimal memory; efficient; clear deduplication; better performance; professional; Snowflake-native

## General Principles

- **Always:** Apply a "cost-first" mindset
- **Rule:** Always fully qualify objects (`DATABASE.SCHEMA.OBJECT`) in shared code
- **Rule:** Prefer declarative set-based operations over procedural row loops
- **Rule:** Use CTEs for logical segmentation
- **Rule:** Avoid accidental cross joins by using explicit join predicates and aliases

## Optimization and Performance

- **Always:** Push WHERE filters in the first CTE (before JOINs/aggregations) for partition pruning
- **Rule:** Minimize data movement by avoiding unnecessary re-materialization
- **Always:** Use semi-structured data types (VARIANT) only at the ingestion edge; normalize critical fields
- **Always:** Use Snowflake's Query Profile to diagnose performance issues and propose optimizations

## Security and Governance

- **Rule:** Enforce governance with masking policies, row access policies, and tagging, especially for sensitive data
- **Rule:** Never use `SELECT *` in production code. Explicitly project required columns
- **Always:** Use Time Travel and Cloning for safe development, testing, and dev/test isolation

## Anti-Patterns Summary

- **Rule:** Avoid deep view nesting (>5 layers)
- **Rule:** Do not use `DISTINCT` to fix duplicates; solve the root cause upstream
- **Rule:** Avoid repeated casting of `VARIANT` fields; parse them once in a CTE
- **Rule:** Avoid recomputing large fact tables from scratch daily unless >70% of rows change per batch OR source system requires full snapshots

## Incremental Patterns

- **Always:** Use **Streams** and **Tasks** for incremental data pipelines instead of full reloads
- **Always:** Implement idempotency with MERGE operations to handle late arrivals

## Common Tasks and Checklists

**Before any action, verify:**
- Are objects fully qualified?
- Are joins explicit?
- Is `SELECT *` removed?
- Is an incremental pattern used for mutable, large tables (>10M rows OR >5GB OR >1M rows with >1000 updates/hour OR >10% rows modified per day)?
- Are security policies or masks applied where needed?
- Are anti-patterns absent?

## Object Naming Conventions (DDL)

**General Rule:** Use the pattern `[OBJECT_TYPE]_[DESCRIPTOR]`. Prefer `VW_MY_VIEW` over `MY_VIEW_VW` so objects group by type in explorers. Above all, be consistent.

### Databases, Schemas, and Warehouses

**Databases:** Prefix with environment: `DEV_`, `QA_`, `PROD_`
- Examples: `DEV_RAW`, `PROD_ANALYTICS`

**Schemas:** Name by function or source system
- Examples: `SALESFORCE`, `MARKETING`, `STG` (staging), `ODS` (operational data store)

**Warehouses:** See `119-snowflake-warehouse-management.md` for comprehensive guidance

### Tables and Views

**Tables:** Prefer no prefix within well-named schemas. If explicit, use `TBL_`
- Examples: `CUSTOMERS` or `TBL_CUSTOMERS`

**Dynamic Tables:** Prefix with `DT_`
- Example: `DT_REALTIME_SALES_AGG`

**Views:** Prefix standard views with `VW_`
- Example: `VW_ACTIVE_USERS`

**Materialized Views:** Prefix with `MV_`
- Example: `MV_HOURLY_SALES_SUMMARY`

**Semantic Views/Models:** Use `SEM_` or `MODEL_` for BI/business semantics
- Example: `SEM_CUSTOMER_LIFETIME_VALUE`

### Data Loading and Integration Objects

**Stages:** Prefix with `STG_`; include source system and data type
- Examples: `STG_S3_SALESFORCE_JSON`, `STG_INTERNAL_USER_AVATARS`

**File Formats:** Prefix with `FF_`
- Examples: `FF_CSV_WITH_HEADER`, `FF_PARQUET_SNAPPY`

**Pipes:** Prefix with `PIPE_`
- Example: `PIPE_LOAD_S3_SALESFORCE_JSON`

**Integrations:** Prefix by type: `SINT_` (Storage), `NINT_` (Notification), `APIINT_` (API)
- Examples: `SINT_S3_PROD_BUCKET`, `NINT_AWS_SNS_PIPE_ALERTS`

### Reserved Characters (CLI Compatibility)

**Rule:** Avoid characters that Snowflake CLI or SnowSQL interpret as template variables in object names, synonyms, comments, and string literals.

**Forbidden Characters:**
- `&` - Snowflake CLI (`snow sql`) template variable prefix
- `<%` and `%>` - SnowSQL variable delimiters
- `{{` and `}}` - Common templating syntax (Jinja2, dbt)

**Examples:**
- **Bad:** `'R&D Department'`, `'Sales & Marketing'`, `'<%ENV%>_TABLE'`
- **Good:** `'R and D Department'`, `'Research and Development'`, `'Sales and Marketing'`

**Why:** These characters cause deployment failures with cryptic error messages when SQL files are executed via CLI tools.
