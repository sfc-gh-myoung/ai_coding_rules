**Description:** Rules for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake Performance Tuning

## TL;DR
- Use Query Profile to find bottlenecks; maximize pruning; avoid functions in WHERE.
- Right-size warehouses; enable AUTO_SUSPEND/RESUME; consider clustering only with clear justification.
- Reference official docs for profiling, warehouses, and clustering.

## 1. Query Profiling & Optimization
- **Always:** Use the Query Profile to diagnose execution, identify bottlenecks, and pinpoint expensive operations (e.g., large `TableScans`, join explosions).
- **Always:** Compare `Partitions Scanned` vs. `Partitions Total` to find pruning opportunities.
- **Requirement:** Avoid functions in `WHERE` clauses when they prevent pruning.

## 2. Warehouse Sizing & Clustering
- **Always:** Right-size warehouses: larger for parallel complex queries; smaller for simple, highly concurrent tasks.
- **Always:** Enable `AUTO_SUSPEND` and `AUTO_RESUME` on all warehouses.
- **Requirement:** Consider clustering keys only with clear justification based on query patterns.

## 3. Documentation
- **Always:** Reference official documentation:
  - **Query Profiling**: https://docs.snowflake.com/en/user-guide/ui-query-profile
  - **Warehouse Management**: https://docs.snowflake.com/en/user-guide/warehouses
  - **Clustering**: https://docs.snowflake.com/en/user-guide/tables-clustering-keys
