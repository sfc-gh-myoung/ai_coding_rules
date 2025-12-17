# Snowflake Core Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Snowflake patterns. Load for Snowflake tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** SQL, CTE, performance, cost optimization, query profile, warehouse, security, governance, stages, COPY INTO, streams, tasks, warehouse creation
**TokenBudget:** ~2850
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose
Establish comprehensive foundational practices for all Snowflake development work, ensuring cost-effective, performant, and secure solutions through proper SQL authoring, object naming, security policies, and architectural patterns.

## Rule Scope

Foundational Snowflake development practices across all SQL, data modeling, and platform features

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Fully qualify all objects** - `DATABASE.SCHEMA.TABLE` in all SQL
- **Push filters early** - WHERE clauses before JOINs for partition pruning
- **Parse VARIANT once** - Extract all fields in single CTE, reference downstream
- **Use Streams + Tasks** - Incremental processing, not full reloads
- **Never use SELECT *** in production - explicit columns only
- **Avoid template characters in identifiers** - No `&`, `<%`, `%>`, `{{`, `}}` in names, synonyms, or comments (Snowflake CLI interprets these as template variables)

## Contract

<contract>
<inputs_prereqs>
Target database/schema; warehouse context; table/view inventory; access roles
</inputs_prereqs>

<mandatory>
SQL authoring; Snowflake UI/CLI profiling; read-only inspection of schemas
</mandatory>

<forbidden>
`SELECT *` in production; `DISTINCT` as a dedupe band-aid; repeated VARIANT extraction
</forbidden>

<steps>
1. Define explicit columns and joins; add early filters
2. Normalize VARIANT once in a dedicated CTE
3. Prefer set-based ops; avoid row-wise loops
4. For mutable large tables, design Streams + Tasks incremental pattern with idempotency
5. Validate with Query Profile before scaling warehouse
</steps>

<output_format>
SQL snippets or task definitions only; no narrative unless requested
</output_format>

<validation>
- Query Profile shows pruning and minimized data movement
- No `SELECT *`; columns are explicit
- Incremental pattern present for mutable facts
- Security policies (masking/row access) applied where needed
</validation>

<design_principles>
- Cost-first; fully qualify objects; prefer set-based SQL with clear CTEs and explicit joins.
- Push filters early, minimize data movement; parse VARIANT at the edge.
- Enforce security policies; never use SELECT *; avoid deep view nesting and DISTINCT as a band-aid.
- Use Streams + Tasks for incremental pipelines; avoid unnecessary full reloads.
- Validate with the provided checklist before shipping.
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using SELECT * Instead of Explicit Columns**
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


**Anti-Pattern 2: Parsing VARIANT Fields Multiple Times**
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
**Problem:** Repeated parsing overhead; high CPU usage; slow queries; wasted credits; inefficient; poor performance; unprofessional

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


**Anti-Pattern 3: Not Using Streams and Tasks for Incremental Processing**
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
**Problem:** Full table scans; unnecessary processing; high credits; slow updates; DELETE/INSERT overhead; not scalable; unprofessional; expensive

**Correct Pattern:**
```sql
-- Good: Incremental processing with Streams and Tasks
-- Step 1: Create Stream to capture changes
CREATE STREAM orders_stream ON TABLE orders;

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
```
**Benefits:** Incremental processing; minimal scans; low credits; fast updates; scalable; efficient MERGE; professional; cost-effective


**Anti-Pattern 4: Using DISTINCT for Deduplication Instead of QUALIFY**
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
**Problem:** Unnecessary DISTINCT; extra sorting; wasted memory; inefficient; unclear intent; poor performance; unprofessional

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

## Post-Execution Checklist
- [ ] All queries use explicit column selection (no SELECT *)
- [ ] WHERE clauses applied early to reduce scan size
- [ ] VARIANT fields parsed once in dedicated CTE
- [ ] Warehouse configuration follows `119-snowflake-warehouse-management.md` (type, size, auto-suspend, tags, resource monitor)
- [ ] Query Profile reviewed for performance bottlenecks
- [ ] Row Access Policies or Dynamic Data Masking applied for PII
- [ ] Resource monitors configured for cost governance
- [ ] Streams and Tasks used for incremental processing where applicable
- [ ] SQL keywords in UPPERCASE for consistency
- [ ] Object names follow DDL naming conventions (see section 8)
- [ ] No DISTINCT used for deduplication (use ROW_NUMBER() instead)
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in identifiers, synonyms, or comments

> **Investigation Required**
> When applying this rule:
> 1. Read SQL files and table definitions BEFORE making recommendations
> 2. Verify schema structure and column types against actual metadata
> 3. Never speculate about table structures or data types
> 4. Check Query Profile for actual performance characteristics
> 5. Make grounded recommendations based on investigated schema and data

## Validation
- Run and inspect Query Profile for each critical query; ensure early filters and pruning.
- Verify no `SELECT *` and no `DISTINCT`-based deduplication.
- Confirm VARIANT fields are parsed once in a CTE.
- For pipelines, demonstrate Streams + Tasks with idempotency and late-arrival handling.

## Output Format Examples
```sql
-- Explicit column selection, early filters, and single VARIANT extraction CTE
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

## References

### External Documentation
- [Snowflake Documentation](https://docs.snowflake.com/) - Complete Snowflake platform documentation
- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) - Complete SQL command reference and syntax guide
- [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/best-practices) - Official performance and cost optimization guidelines
- [Snowflake Security Guide](https://docs.snowflake.com/en/user-guide/security) - Comprehensive security features and implementation guide

### Related Rules
- **Connection Error Handling**: `rules/100f-snowflake-connection-errors.md` - Error classification (network policy vs auth vs connection)
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **SQL Automation**: `rules/102a-snowflake-sql-automation.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`
- **Object Tagging**: `rules/123-snowflake-object-tagging.md`
- **Data Loading**: `rules/108-snowflake-data-loading.md`
- **Snowpipe**: `rules/121-snowflake-snowpipe.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

## 1. General Principles
- **Always:** Apply a "cost-first" mindset.
- **Rule:** Always fully qualify objects (DATABASE.SCHEMA.OBJECT) in shared code.
- **Rule:** Prefer declarative set-based operations over procedural row loops.
- **Rule:** Use CTEs for logical segmentation.
- **Rule:** Avoid accidental cross joins by using explicit join predicates and aliases.

## 2. Optimization and Performance
- **Always:** Push filtering and partition pruning as early as possible in queries.
- **Rule:** Minimize data movement by avoiding unnecessary re-materialization.
- **Always:** Use semi-structured data types (VARIANT) only at the ingestion edge; normalize critical fields.
- **Always:** Use Snowflake's query profile to diagnose performance issues and propose optimizations.
- **Always:** Reference Snowflake performance documentation for query tuning guidance: https://docs.snowflake.com/en/user-guide/performance-overview

## 3. Security and Governance
- **Rule:** Enforce governance with masking policies, row access policies, and tagging, especially for sensitive data. See `123-snowflake-object-tagging.md` for comprehensive tagging patterns.
- **Rule:** Never use `SELECT *` in production code. Explicitly project required columns.
- **Always:** Use Time Travel and Cloning for safe development, testing, and dev/test isolation.
- **Always:** Reference Snowflake security and governance documentation for best practices: https://docs.snowflake.com/en/user-guide/data-governance-intro

## 4. Anti-Patterns
- **Rule:** Avoid deep view nesting (>5 layers).
- **Rule:** Do not use `DISTINCT` to fix duplicates; solve the root cause upstream.
- **Rule:** Avoid repeated casting of `VARIANT` fields; parse them once in a CTE.
- **Rule:** Avoid recomputing large fact tables from scratch daily unless a high change rate is necessary.

## 5. Incremental Patterns
- **Always:** Use **Streams** and **Tasks** for incremental data pipelines instead of full reloads or ad-hoc MERGE loops.
- **Always:** Reference Snowflake Streams and Tasks documentation for implementation details: https://docs.snowflake.com/en/sql-reference-commands

## 6. Common Tasks & Checklists
- **Always:** Before any action, apply the following checks:
  - Are objects fully qualified?
  - Are joins explicit?
  - Is `SELECT *` removed?
  - Is an incremental pattern used for mutable, large tables?
  - Are security policies or masks applied where needed?
  - Are anti-patterns absent?

## 7. Related Specialized Rules
- **Rule:** For deeper guidance, reference the following specialized rules:
  - `101-snowflake-streamlit-core.md`: Modern, performant, and maintainable Streamlit UIs
  - `102-snowflake-sql-demo-engineering.md`: SQL patterns for demos and learning environments.
  - `103-snowflake-performance-tuning.md`: Profiling, pruning, clustering justification.
  - `119-snowflake-warehouse-management.md`: Comprehensive warehouse creation, type selection (CPU/GPU/High-Memory), sizing, tagging, and cost governance.
  - `104-snowflake-streams-tasks.md`: Incremental pipelines with Streams + Tasks, idempotency, monitoring.
  - `105-snowflake-cost-governance.md`: Workload isolation, resource monitors, right-sizing, anomaly detection.
  - `106-snowflake-semantic-views-core.md`: Layering (staging/core/semantic), naming conventions, and slim views.
  - `107-snowflake-security-governance.md`: Masking policies, row access, tagging, and role strategies.
  - `123-snowflake-object-tagging.md`: Object tagging for governance, cost attribution, and policy automation.
  - `108-snowflake-data-loading.md`: Stages and `COPY INTO` for bulk loading.
  - `121-snowflake-snowpipe.md`: Snowpipe and Snowpipe Streaming for continuous near-real-time ingestion.
  - `109-snowflake-notebooks.md`: Jupyter Notebooks in Snowflake best practices.

## 8. Object Naming Conventions (DDL)

- **Rule:** Use the pattern `[OBJECT_TYPE]_[DESCRIPTOR]`. Prefer `VW_MY_VIEW` over `MY_VIEW_VW` so objects group by type in explorers (e.g., Snowsight). Above all, be consistent.

### Databases, Schemas, and Warehouses
- **Rule (Databases):** Prefix with environment: `DEV_`, `QA_`, `PROD_`.
  - Examples: `DEV_RAW`, `PROD_ANALYTICS`.
- **Rule (Schemas):** Name by function or source system.
  - Examples: `SALESFORCE`, `MARKETING`, `STG` (staging), `ODS` (operational data store).
- **Rule (Warehouses):** See `119-snowflake-warehouse-management.md` for comprehensive warehouse naming, sizing, type selection, and management guidance.

### Tables and Views
- **Rule (Tables):** Prefer no prefix within well-named schemas (e.g., `STG`, `RAW`, `PROD`). If explicit, use `TBL_`.
  - Examples: `CUSTOMERS` or `TBL_CUSTOMERS`.
- **Rule (Dynamic Tables):** Prefix with `DT_`.
  - Example: `DT_REALTIME_SALES_AGG`.
- **Rule (Views):** Prefix standard views with `VW_`.
  - Example: `VW_ACTIVE_USERS`.
- **Rule (Materialized Views):** Prefix with `MV_`.
  - Example: `MV_HOURLY_SALES_SUMMARY`.
- **Consider (Semantic Views/Models):** Use `SEM_` or `MODEL_` when you must distinguish for BI/business semantics.
  - Example: `SEM_CUSTOMER_LIFETIME_VALUE`.

### Data Loading and Integration Objects
- **Rule (Stages):** Prefix with `STG_`; include source system and data type when useful.
  - Examples: `STG_S3_SALESFORCE_JSON`, `STG_INTERNAL_USER_AVATARS`.
- **Rule (File Formats):** Prefix with `FF_`.
  - Examples: `FF_CSV_WITH_HEADER`, `FF_PARQUET_SNAPPY`.
- **Rule (Pipes):** Prefix with `PIPE_`.
  - Example: `PIPE_LOAD_S3_SALESFORCE_JSON`.
- **Rule (Integrations):** Prefix by type: `SINT_` (Storage), `NINT_` (Notification), `APIINT_` (API).
  - Examples: `SINT_S3_PROD_BUCKET`, `NINT_AWS_SNS_PIPE_ALERTS`.

### Reserved Characters (CLI Compatibility)
- **Rule:** Avoid characters that Snowflake CLI or SnowSQL interpret as template variables in object names, synonyms, comments, and string literals.
- **Forbidden Characters:**
  - `&` - Snowflake CLI (`snow sql`) template variable prefix
  - `<%` and `%>` - SnowSQL variable delimiters
  - `{{` and `}}` - Common templating syntax (Jinja2, dbt)
- **Examples:**
  - Bad: `'R&D Department'`, `'Sales & Marketing'`, `'<%ENV%>_TABLE'`
  - Good: `'R and D Department'`, `'Research and Development'`, `'Sales and Marketing'`
- **Why:** These characters cause deployment failures with cryptic error messages when SQL files are executed via CLI tools.

## Related Rules

**Closely Related** (consider loading together):
- `103-snowflake-performance-tuning` - For query optimization patterns (CTEs, query structure)
- `119-snowflake-warehouse-management` - For comprehensive warehouse creation and management

**Sometimes Related** (load if specific scenario):
- `107-snowflake-security-governance` - When implementing RBAC, masking policies, row access
- `108-snowflake-data-loading` - When loading data with COPY INTO and stages
- `104-snowflake-streams-tasks` - When setting up CDC pipelines with streams and tasks

**Complementary** (different aspects of same domain):
- `105-snowflake-cost-governance` - For tagging standards (COST_CENTER, WORKLOAD_TYPE)
- `111-snowflake-observability-core` - For monitoring Snowflake workloads and queries
