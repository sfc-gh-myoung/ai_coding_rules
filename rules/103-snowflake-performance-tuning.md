# Snowflake Performance Tuning

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-20
**Keywords:** search optimization, pruning, spillage, SQL optimization, Snowflake, partition pruning, QUERY_HISTORY, optimize query, fix slow query, query bottleneck, warehouse performance, micro-partitions, clustering, performance analysis
**TokenBudget:** ~3200
**ContextTier:** High
**Depends:** 100-snowflake-core.md
**LoadTrigger:** kw:performance, kw:optimization, kw:slow

## Scope

**What This Rule Covers:**
Systematic approaches for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage to achieve optimal performance while managing costs effectively.

**When to Load This Rule:**
- Optimizing slow Snowflake queries
- Tuning warehouse performance
- Managing query costs
- Analyzing Query Profile for bottlenecks
- Implementing partition pruning strategies

### Quantification Standards

**Performance Thresholds:**
- **Large table:** >1M rows OR >1GB uncompressed (context: partition pruning)
- **Slow query:** >10s execution time (context: query optimization)
- **Heavy workload:** >50 concurrent queries (context: warehouse sizing)
- **Complex query:** >5 table joins OR >3 CTEs (context: SQL patterns)

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **100-snowflake-core.md** - Snowflake SQL patterns and best practices

### External Documentation
- [Query Profile Guide](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query execution analysis and performance diagnostics
- [Virtual Warehouse Management](https://docs.snowflake.com/en/user-guide/warehouses) - Warehouse sizing, scaling, and cost optimization
- [Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys) - Table clustering for query performance optimization

### Related Rules

**Closely Related** (consider loading together):
- **119-snowflake-warehouse-management.md** - Warehouse sizing, type selection (CPU/GPU/High-Memory), auto-suspend config
- **105-snowflake-cost-governance.md** - Cost monitoring, resource monitors, budget alerts during optimization

**Sometimes Related** (load if specific scenario):
- **100-snowflake-core.md** - CTE usage patterns and query structure fundamentals
- **102-snowflake-sql-core.md** - General SQL file patterns
- **122-snowflake-dynamic-tables.md** - Optimizing dynamic table refresh performance
- **104-snowflake-streams-tasks.md** - Optimizing stream/task pipeline performance

**Complementary** (different aspects of same domain):
- **108-snowflake-data-loading.md** - Optimizing COPY INTO and data loading performance
- **111-snowflake-observability-core.md** - Query profiling and performance monitoring

## Contract

### Inputs and Prerequisites

- Snowflake account with SYSADMIN or equivalent role (for warehouse resizing) or USAGE privilege on the warehouse
- Access to QUERY_HISTORY view (requires ACCOUNTADMIN or MONITOR privilege on the account)
- Access to Query Profile in Snowsight or via INFORMATION_SCHEMA.QUERY_HISTORY
- Warehouse context for query execution (X-SMALL minimum; sizing depends on workload)
- Slow query identified (>10s execution time or user complaint)
- Understanding of table structures and data volumes

### Mandatory

- Query Profile analysis before optimization (CRITICAL)
- SHOW WAREHOUSES, SHOW TABLES for context
- QUERY_HISTORY queries for execution patterns
- Partition pruning verification (Partitions Scanned vs Total)
- Spillage detection (remote vs local disk)
- Warehouse sizing appropriate for workload (see 119-snowflake-warehouse-management.md)

### Forbidden

- Optimizing queries without reviewing Query Profile
- Adding clustering keys without evidence of poor pruning
- Using functions in WHERE clause that prevent partition pruning (DATE(), CAST())
- Oversizing warehouses without measuring impact
- Speculating about performance issues without profiling data

### Execution Steps

1. Identify slow query (execution time, user report, monitoring alert)
2. Open Query Profile in Snowsight or query QUERY_HISTORY
3. Analyze partition pruning: Compare "Partitions Scanned" vs "Partitions Total" (target <10%)
4. Identify bottlenecks: Large TableScans (>1M rows scanned per query), join explosions, spillage to remote storage
5. Check WHERE clause for functions that prevent pruning
6. Verify warehouse size appropriate for data volume
7. Apply optimization: Rewrite query, adjust warehouse, consider clustering only if justified
8. Measure impact: Compare before/after execution times with same warehouse

### Output Format

- Optimized SQL query with explicit column selection
- Query Profile screenshots or statistics (before/after)
- Performance metrics: Execution time reduction, Partitions Scanned reduction
- Warehouse sizing recommendations with justification
- Clustering key recommendations (only if Query Profile shows poor pruning)

### Validation

**Test Requirements:**
- Query executes successfully
- Execution time reduced by ≥30% (or meets performance target)
- Partition pruning improved (lower scanned:total ratio)
- No spillage to remote storage (or significantly reduced)
- Warehouse auto-suspend/resume enabled

**Success Criteria:**
- Query Profile shows pruning improvement
- Execution time meets SLA (<2s for interactive, <30s for analytical)
- No anti-patterns present (functions in WHERE, unnecessary DISTINCT)
- Warehouse appropriately sized for workload

### Design Principles

- Use Query Profile to find bottlenecks; maximize pruning; avoid functions in WHERE.
- Right-size warehouses; enable AUTO_SUSPEND/RESUME; consider clustering only with clear justification.
- Reference official docs for profiling, warehouses, and clustering.

> **Investigation Required**
> Always check Query Profile before optimizing (see Mandatory requirements above).
>
> **Anti-Pattern:**
> "Let me add a clustering key to speed this up."
>
> **Correct Pattern:**
> "Let me check the Query Profile first to identify the bottleneck."
> [reviews Query Profile, finds large TableScan]
> "The issue is partition pruning - 1000/1000 Partitions Scanned. Let me check the WHERE clause..."

### Post-Execution Checklist

- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Functions in WHERE Clause That Prevent Pruning**
```sql
-- Bad: Function on column prevents partition pruning
SELECT *
FROM large_fact_table
WHERE DATE(order_timestamp) = '2024-01-15';
-- DATE() function scans ALL partitions, extremely slow!
```
**Problem:** Partition pruning disabled; scans all micro-partitions; 100x slower queries; massive compute costs; query timeouts; poor performance

**Correct Pattern:**
```sql
-- Good: Filter on raw column for partition pruning
SELECT *
FROM large_fact_table
WHERE order_timestamp >= '2024-01-15'
  AND order_timestamp < '2024-01-16';
-- Prunes to relevant partitions only, 100x faster!
```
**Benefits:** Partition pruning enabled; scans minimal partitions; 100x faster; low costs; production-ready; excellent performance

**Anti-Pattern 2: Adding Clustering Keys Without Query Profile Evidence**
```sql
-- Bad: Add clustering arbitrarily without analysis
ALTER TABLE sales_fact CLUSTER BY (region, product_category);
-- No Query Profile analysis! May not help, costs money to maintain!
```
**Problem:** Unnecessary clustering costs; no proven benefit; maintenance overhead; wasted resources; assumption-driven; not data-driven

**Correct Pattern:**
```sql
-- Good: Analyze Query Profile FIRST
-- Step 1: Run slow query, get query_id
SELECT * FROM sales_fact WHERE region = 'WEST' AND product_category = 'Electronics';
-- Get query_id from result

-- Step 2: Check Query Profile for pruning statistics
-- In Snowsight: Query History > Click query > Query Profile
-- Look for: "Partitions Scanned" vs "Partitions Total"
-- If scanning >50% of partitions for selective query, clustering may help

-- Step 3: Only add clustering if Query Profile shows poor pruning
-- AND if query pattern is consistent
ALTER TABLE sales_fact CLUSTER BY (region, product_category);

-- Step 4: Measure improvement - re-run query, check Query Profile
-- Validate: Partitions Scanned reduced significantly
```
**Benefits:** Data-driven clustering decisions; proven performance gains; cost-justified; Query Profile validated; measurable improvements; production evidence-based

**Anti-Pattern 3: Using SELECT * Instead of Specific Columns**
```sql
-- Bad: SELECT * returns unnecessary columns
SELECT *
FROM wide_dimension_table t1
JOIN fact_table t2 ON t1.id = t2.dim_id;
-- Returns 150 columns, only need 5!
```
**Problem:** Transfers unnecessary data; slower queries; higher network costs; wider result sets; memory pressure; inefficient

**Correct Pattern:**
```sql
-- Good: Select only needed columns
SELECT
  t1.customer_name,
  t1.region,
  t2.order_date,
  t2.order_amount,
  t2.status
FROM wide_dimension_table t1
JOIN fact_table t2 ON t1.id = t2.dim_id;
-- Returns only 5 needed columns, much faster
```
**Benefits:** Minimal data transfer; faster queries; lower costs; focused results; memory efficient; production-optimized

**Anti-Pattern 4: Not Using Query Profile to Diagnose Slow Queries**
```python
# Bad: Guess at performance issues
# "Query is slow, maybe warehouse is too small?"
# ALTER WAREHOUSE my_wh SET WAREHOUSE_SIZE = 'XXLARGE';  # Expensive guess!
```
**Problem:** Assumption-driven fixes; expensive trial-and-error; may not solve root cause; wastes money; no evidence; ineffective optimization

**Correct Pattern:**
```sql
-- Good: Use Query Profile for root cause analysis
-- Step 1: Run slow query, capture query_id
SET query_id = (SELECT LAST_QUERY_ID());

-- Step 2: Analyze in Snowsight Query Profile
-- Check for:
-- - Partition pruning: Are most partitions scanned? If yes, add clustering or fix WHERE
-- - Spillage: Is data spilling to remote storage? If yes, increase warehouse size
-- - Join explosion: Are joins creating massive intermediate results? If yes, optimize join order
-- - External function latency: Are UDFs/external APIs slow? If yes, optimize or cache

-- Step 3: Apply targeted fix based on Query Profile evidence
-- Example: If 90% partitions scanned for selective query:
ALTER TABLE my_table CLUSTER BY (date_column);

-- Step 4: Re-run query, verify improvement in Query Profile
```
**Benefits:** Evidence-based optimization; targeted fixes; cost-effective; root cause resolution; measurable results; professional performance tuning

## Output Format Examples

```sql
-- Query Optimization Workflow

-- Step 1: Capture baseline metrics for the slow query
SELECT query_id, execution_time, partitions_scanned, partitions_total,
       bytes_spilled_to_local_storage, bytes_spilled_to_remote_storage
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_id = '<slow_query_id>';

-- Step 2: Apply optimization (example: rewrite WHERE for pruning)
-- BEFORE: WHERE DATE(order_timestamp) = '2024-01-15'
-- AFTER:
SELECT order_id, customer_id, order_amount
FROM my_db.my_schema.orders
WHERE order_timestamp >= '2024-01-15'
  AND order_timestamp < '2024-01-16';

-- Step 3: Compare before/after metrics
-- Document: execution_time reduced from Xs to Ys
-- Document: Partitions Scanned reduced from X to Y (of Z total)
-- Document: spillage eliminated (or reduced from X bytes to Y bytes)
```

## Query Profiling & Optimization
- **Always:** Use the Query Profile to diagnose execution, identify bottlenecks, and pinpoint expensive operations (e.g., large `TableScans`, join explosions).
- **Always:** Compare `Partitions Scanned` vs. `Partitions Total` to find pruning opportunities.
- **Requirement:** Avoid functions in `WHERE` clauses when they prevent pruning.

## Warehouse Sizing & Clustering
- **Always:** Follow comprehensive warehouse sizing guidance in `119-snowflake-warehouse-management.md` including type selection (CPU/GPU/High-Memory), sizing strategy, auto-suspend configuration, and cost governance.
- **Requirement:** Consider clustering keys only with clear justification based on query patterns and Query Profile evidence of poor pruning.

## Data Skew and Concurrency

### Data Skew
- **Detection:** In Query Profile, look for uneven partition sizes or operators where one thread processes significantly more data than others. Skewed joins produce one or two partitions with disproportionate row counts.
- **Mitigation:** Add a secondary clustering key on the skewed column; pre-filter the larger table in a CTE before joining; or use a salting technique (append a modulo-based suffix to the join key) for extreme skew.

### High-Concurrency Workloads
- For workloads exceeding 50 concurrent queries, use multi-cluster warehouses with `MIN_CLUSTER_COUNT = 1` and `MAX_CLUSTER_COUNT` set based on peak concurrency (each cluster handles ~8-10 concurrent queries).
- Use `SCALING_POLICY = 'STANDARD'` for consistent workloads (scales out when queries queue for 20s) or `'ECONOMY'` for cost-sensitive workloads (scales out after 6 minutes of queueing).
- Monitor `QUERY_HISTORY` for `QUEUED_OVERLOAD_TIME > 0` to detect when scaling is insufficient.

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~600 tokens (always load for performance tasks)
- + Query Profiling (section 1): ~1200 tokens (load for slow queries)
- + Warehouse & Clustering (section 2): ~1800 tokens (load for sizing/clustering)
- + Complete Reference: ~2500 tokens (full performance guide)

**Recommended Loading Strategy:**
- **Initial diagnosis**: Quick Start only
- **Slow query investigation**: + Query Profiling
- **Warehouse optimization**: + Warehouse & Clustering + 119 (warehouse management)
- **Complete tuning**: Full reference
