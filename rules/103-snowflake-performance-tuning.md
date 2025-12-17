# Snowflake Performance Tuning

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** search optimization, pruning, spillage, SQL optimization, Snowflake, partition pruning, QUERY_HISTORY, optimize query, fix slow query, query bottleneck, warehouse performance, micro-partitions, clustering, performance analysis
**TokenBudget:** ~2150
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide systematic approaches for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage to achieve optimal performance while managing costs effectively.

## Rule Scope

Snowflake query performance tuning, warehouse optimization, and cost management

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use Query Profile first** - identify bottlenecks (large TableScans, join explosions, spillage)
- **Check partition pruning:** Compare "Partitions Scanned" vs "Partitions Total"
- **Avoid functions in WHERE** - prevents partition pruning (e.g., `DATE(timestamp_col)`)
- **Right-size warehouses:** Follow 119-snowflake-warehouse-management.md sizing guidance
- **Enable AUTO_SUSPEND/RESUME** - prevent idle warehouse costs
- **Don't add clustering keys without evidence** - Query Profile must show poor pruning first

**Quick Checklist:**
- [ ] Open Query Profile for slow query
- [ ] Check "Partitions Scanned" vs "Partitions Total" (want <10% scanned)
- [ ] Identify expensive operations (TableScan, JOIN, Aggregate)
- [ ] Verify no functions in WHERE clause
- [ ] Confirm warehouse size appropriate for workload
- [ ] Only consider clustering if Query Profile shows poor pruning

> **Investigation Required**
> When applying this rule:
> 1. Open Query Profile in Snowsight for the slow query BEFORE making recommendations
> 2. Read actual partition statistics (scanned vs total)
> 3. Never speculate about performance issues - verify in Query Profile
> 4. Check warehouse size and utilization in QUERY_HISTORY
> 5. Make grounded recommendations based on investigated Query Profile data

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
- Use Query Profile to find bottlenecks; maximize pruning; avoid functions in WHERE.
- Right-size warehouses; enable AUTO_SUSPEND/RESUME; consider clustering only with clear justification.
- Reference official docs for profiling, warehouses, and clustering.
> **Investigation Required**
> When optimizing query performance:
> 1. Check Query Profile first - never optimize without profiling: `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_...)`
> 2. Verify partition pruning effectiveness - check "Partitions Scanned" vs "Partitions Total" in Query Profile
> 3. Identify actual bottlenecks - look for large TableScans, join explosions, spillage to remote storage
> 4. Check warehouse size and utilization - query WAREHOUSE_METERING_HISTORY before resizing
> 5. Never add clustering keys without analyzing query patterns first
> 6. Measure impact - compare before/after query execution times with same warehouse
>
> **Anti-Pattern:**
> "Let me add a clustering key to speed this up."
>
> **Correct Pattern:**
> "Let me check the Query Profile first to identify the bottleneck."
> [reviews Query Profile, finds large TableScan]
> "The issue is partition pruning - 1000/1000 partitions scanned. Let me check the WHERE clause..."
</design_principles>

</contract>

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
-- Look for: "Partitions scanned" vs "Partitions total"
-- If scanning >50% of partitions for selective query, clustering may help

-- Step 3: Only add clustering if Query Profile shows poor pruning
-- AND if query pattern is consistent
ALTER TABLE sales_fact CLUSTER BY (region, product_category);

-- Step 4: Measure improvement - re-run query, check Query Profile
-- Validate: Partitions scanned reduced significantly
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

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Output Format Examples

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## References

### External Documentation
- [Query Profile Guide](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query execution analysis and performance diagnostics
- [Virtual Warehouse Management](https://docs.snowflake.com/en/user-guide/warehouses) - Warehouse sizing, scaling, and cost optimization
- [Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys) - Table clustering for query performance optimization

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

## 1. Query Profiling & Optimization
- **Always:** Use the Query Profile to diagnose execution, identify bottlenecks, and pinpoint expensive operations (e.g., large `TableScans`, join explosions).
- **Always:** Compare `Partitions Scanned` vs. `Partitions Total` to find pruning opportunities.
- **Requirement:** Avoid functions in `WHERE` clauses when they prevent pruning.

## 2. Warehouse Sizing & Clustering
- **Always:** Follow comprehensive warehouse sizing guidance in `119-snowflake-warehouse-management.md` including type selection (CPU/GPU/High-Memory), sizing strategy, auto-suspend configuration, and cost governance.
- **Requirement:** Consider clustering keys only with clear justification based on query patterns and Query Profile evidence of poor pruning.

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

## Related Rules

**Closely Related** (consider loading together):
- `119-snowflake-warehouse-management` - For warehouse sizing, type selection (CPU/GPU/High-Memory), auto-suspend config
- `105-snowflake-cost-governance` - For cost monitoring, resource monitors, budget alerts during optimization

**Sometimes Related** (load if specific scenario):
- `100-snowflake-core` - For CTE usage patterns and query structure fundamentals
- `122-snowflake-dynamic-tables` - When optimizing dynamic table refresh performance
- `104-snowflake-streams-tasks` - When optimizing stream/task pipeline performance

**Complementary** (different aspects of same domain):
- `108-snowflake-data-loading` - For optimizing COPY INTO and data loading performance
- `111-snowflake-observability-core` - For query profiling and performance monitoring
