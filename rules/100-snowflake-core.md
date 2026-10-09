---
schema_version: v4.0
rule_version: v5.0.0
description: "Foundational Snowflake practices: SQL authoring, object naming, cost control, security policies, and performance patterns."
last_updated: 2026-10-06
keywords:
  - kw:CTE extraction
  - kw:VARIANT parsing optimization
  - kw:Streams Tasks incremental
  - kw:partition pruning early filtering
  - kw:QUALIFY ROW_NUMBER deduplication
  - kw:Query Profile validation
  - ext:.sql
token_budget: ~1600
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - 119-snowflake-warehouse-management.md  # Warehouse config referenced throughout core patterns
    - 103-snowflake-performance-tuning.md  # Query profiling and optimization
    - 105-snowflake-cost-governance.md  # Cost monitoring and resource management
---
# Snowflake Core Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Foundational Snowflake practices. Load for any Snowflake development task.

## Scope

**What This Rule Covers:**
Comprehensive foundational practices for all Snowflake development: SQL authoring, object naming, security policies, incremental pipelines, and performance patterns.

**When to Load This Rule:**
- Writing or modifying Snowflake SQL queries or database objects (tables, views, stages, pipes, tasks)
- Performance tuning, cost optimization, or security policy implementation
- Designing incremental data pipelines with Streams and Tasks
- Loading data (COPY INTO, Snowpipe) or working with VARIANT/semi-structured data

**Sizing:** Use observed volume, change rate, latency and cost to choose an incremental design; no universal row-count threshold applies.

## Contract

### Inputs and Prerequisites

- Target database/schema and warehouse identified; table/view inventory and data model understood
- Access role and target scope verified; obtaining privileges is a separate authorized action
- Snowflake CLI (`snow`) >= 3.0 or SnowSQL >= 1.3 for CLI execution; Python Connector >= 3.0 for programmatic access

### Mandatory

**SQL authoring:**
- Never use `SELECT *` in production; always list explicit columns
- Fully qualify all objects: `DATABASE.SCHEMA.TABLE`
- Filter early where semantics permit; confirm pruning in Query Profile rather than assuming CTE placement guarantees it
- Parse VARIANT/semi-structured fields exactly once in a dedicated normalization CTE; never re-parse the same path in downstream CTEs or clauses
- Deduplicate with `QUALIFY ROW_NUMBER() OVER (...) = 1`; do not use `DISTINCT` as a deduplication mechanism
- Use TIMESTAMP_NTZ for event timestamps (UTC-normalized); TIMESTAMP_LTZ for user-facing display

**Object naming (DDL):**
- Databases: environment prefix `DEV_`, `QA_`, `PROD_`; schemas named by function or source system
- Views: `VW_`; Materialized Views: `MV_`; Dynamic Tables: `DT_`; Semantic Views: `SEM_` or `MODEL_`
- Stages: `STG_<source>_<format>`; File Formats: `FF_`; Pipes: `PIPE_`
- Integrations: `SINT_` (Storage), `NINT_` (Notification), `APIINT_` (API)
- Avoid `&`, `<%`, `%>`, `{{`, `}}` in identifiers and comments (CLI template variable characters); for SQL data values that legitimately contain `&`, use `--enable-templating NONE` at the CLI layer — never replace `&` with `and` in data

**Performance and cost:**
- Review Query Profile (bytes scanned, partitions pruned) before scaling warehouse size
- Consider Streams + Tasks for incremental processing when change rate, latency, retention and cost justify it; see `119-snowflake-warehouse-management.md` for warehouse sizing

**Security:**
- Identify sensitive columns and applicable masking/row-access requirements; apply policy or change grants only with authorization
- Wrap multi-statement DML operations in explicit transactions (`BEGIN ... COMMIT`) with `ROLLBACK` on failure

### Execution Steps

1. Define explicit columns and semantically safe early filters; check actual pruning in Query Profile when execution is authorized
2. Extract all VARIANT paths in a single normalization CTE; reference the typed aliases in downstream CTEs
3. Use `QUALIFY ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...) = 1` for deduplication
4. If incremental processing is justified and creation is authorized, design a Stream/Task workflow with measured retention and idempotent MERGE behavior
5. Run Query Profile before scaling warehouse; investigate bytes spilled to remote storage and low partition pruning ratios
6. Check sensitive-data policies and role-scoped grants; propose changes without applying them absent authorization

**Example — VARIANT extraction with early filter:**
```sql
WITH src AS (
  SELECT v:customer_id::string       AS customer_id,
         v:order_ts::timestamp_ntz   AS order_ts,
         v:total_amount::number      AS total_amount
  FROM RAW_DB.STAGE.ORDERS_JSON
  WHERE v:order_ts::timestamp_ntz >= DATEADD(day, -7, CURRENT_TIMESTAMP())
),
agg AS (
  SELECT customer_id, COUNT(*) AS num_orders, SUM(total_amount) AS total_spend
  FROM src
  GROUP BY customer_id
)
SELECT customer_id, num_orders, total_spend FROM agg;
```

**Example — QUALIFY deduplication:**
```sql
SELECT customer_id, order_id, order_timestamp, amount
FROM MY_DB.MY_SCHEMA.orders_with_duplicates
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1;
```

### Validation

- [ ] No `SELECT *` in any production query
- [ ] All objects fully qualified (DATABASE.SCHEMA.TABLE)
- [ ] Filters preserve query semantics; any claimed pruning is supported by Query Profile evidence
- [ ] VARIANT fields extracted exactly once; no repeated parsing of same path
- [ ] Deduplication uses QUALIFY ROW_NUMBER(), not DISTINCT
- [ ] Query Profile reviewed; bytes scanned and partition pruning confirmed
- [ ] Security policies applied to columns tagged PII/CONFIDENTIAL/financial
- [ ] Incremental design justified by workload evidence; no universal size threshold assumed
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in identifiers or comments

**Negative tests — must never appear in reviewed code:**
- `SELECT *` in production queries
- `DISTINCT` used as the sole deduplication mechanism
- Same VARIANT path re-parsed in multiple CTEs or clauses
- Unjustified full reload when an authorized, correct incremental approach is preferable

## References

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) — SQL command reference and syntax
- [Best Practices](https://docs.snowflake.com/en/user-guide/best-practices) — Performance and cost optimization
- [Dynamic Data Masking](https://docs.snowflake.com/en/user-guide/security-column-ddm) — Column-level security
- [Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row-access-policies) — Row-level security
- [Streams](https://docs.snowflake.com/en/user-guide/streams-intro) — Change data capture
- [Tasks](https://docs.snowflake.com/en/user-guide/tasks-intro) — Scheduled SQL execution
- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) — Execution analysis
