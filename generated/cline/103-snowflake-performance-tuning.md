<!-- Generated for Cline rules. See https://docs.cline.bot/features/cline-rules -->

**Keywords:** Query profile, slow queries, performance tuning, warehouse sizing, clustering keys, search optimization, pruning, spillage, SQL optimization, Snowflake, partition pruning, QUERY_HISTORY
**TokenBudget:** ~800
**ContextTier:** High
**Depends:** 100-snowflake-core

# Snowflake Performance Tuning

## Purpose
Provide systematic approaches for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage to achieve optimal performance while managing costs effectively.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake query performance tuning, warehouse optimization, and cost management

## Key Principles
- Use Query Profile to find bottlenecks; maximize pruning; avoid functions in WHERE.
- Right-size warehouses; enable AUTO_SUSPEND/RESUME; consider clustering only with clear justification.
- Reference official docs for profiling, warehouses, and clustering.

## Quick Start TL;DR (Read First - 30 Seconds)

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

## 1. Query Profiling & Optimization
- **Always:** Use the Query Profile to diagnose execution, identify bottlenecks, and pinpoint expensive operations (e.g., large `TableScans`, join explosions).
- **Always:** Compare `Partitions Scanned` vs. `Partitions Total` to find pruning opportunities.
- **Requirement:** Avoid functions in `WHERE` clauses when they prevent pruning.

## 2. Warehouse Sizing & Clustering
- **Always:** Follow comprehensive warehouse sizing guidance in `119-snowflake-warehouse-management.md` including type selection (CPU/GPU/High-Memory), sizing strategy, auto-suspend configuration, and cost governance.
- **Requirement:** Consider clustering keys only with clear justification based on query patterns and Query Profile evidence of poor pruning.

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
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Demo Engineering**: `102-snowflake-sql-demo-engineering.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
