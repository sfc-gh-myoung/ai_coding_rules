**Description:** Advanced SQL authoring patterns for Snowflake, focusing on CTEs, VARIANT extraction, and cardinality control.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake SQL Best Practices

## TL;DR
- Use CTEs to segment logic; control join cardinality; prefer QUALIFY over nested subqueries for window filters.
- Extract/flatten VARIANT once in an early CTE; avoid repeated casts.
- Use APPROX_* functions where exact precision isn’t required for performance at scale.
- Link to Snowflake docs for syntax; keep queries readable and maintainable.

## 1. Advanced SQL Authoring
- **Requirement:** Use CTEs to modularize complex queries. Avoid excessive nesting (cap ~6 levels).
- **Requirement:** Control join cardinality by ensuring distinct keys or using semi-joins.
- **Requirement:** Use `QUALIFY` to filter window function results instead of subqueries.

## 2. Semi-Structured Data
- **Requirement:** Extract and flatten semi-structured `VARIANT` data in an early CTE.
- **Requirement:** Avoid repeated casting or navigation of `VARIANT` columns; perform extraction once.
- **Consider:** For high-cardinality operations, use `APPROX_COUNT_DISTINCT` instead of `COUNT(DISTINCT ...)` when exact precision is not required.

## 3. Documentation
- **Always:** Reference the official Snowflake documentation:
  - **SQL Reference**: https://docs.snowflake.com/en/sql-reference
  - **Querying Semi-Structured Data**: https://docs.snowflake.com/en/sql-reference/data-types-semistructured
