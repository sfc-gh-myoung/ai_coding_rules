**Description:** Rules for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~200
**ContextTier:** Medium

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
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Query Profile Guide](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query execution analysis and performance diagnostics
- [Virtual Warehouse Management](https://docs.snowflake.com/en/user-guide/warehouses) - Warehouse sizing, scaling, and cost optimization
- [Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys) - Table clustering for query performance optimization

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
