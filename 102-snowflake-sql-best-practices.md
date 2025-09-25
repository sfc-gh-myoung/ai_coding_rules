**Description:** Advanced SQL authoring patterns for Snowflake, focusing on CTEs, VARIANT extraction, and cardinality control.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

# Snowflake SQL Best Practices

## Purpose
Establish advanced SQL authoring patterns specifically for Snowflake, focusing on CTEs, VARIANT data extraction, cardinality control, and query optimization techniques for maintainable and performant data processing.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Advanced Snowflake SQL authoring patterns, CTEs, VARIANT handling, and query optimization

## Key Principles
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

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference) - Complete SQL command reference and syntax guide
- [Querying Semi-Structured Data](https://docs.snowflake.com/en/sql-reference/data-types-semistructured) - VARIANT, OBJECT, and ARRAY data type handling

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
