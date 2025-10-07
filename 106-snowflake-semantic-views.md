**Description:** Rules for building Snowflake Semantic Models (Cortex Analyst) and Snowflake Semantic Views (not plain views).
**AppliesTo:** `**/*.sql`, `**/*.yaml`, `**/*.yml`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-22

# Snowflake Semantic Models and Semantic Views

## Purpose
Provide authoritative guidance for designing and maintaining Snowflake Semantic Models (Cortex Analyst) and Snowflake Semantic Views. Focus on logical tables, dimensions, time dimensions, facts, metrics, filters, and relationships, plus creation and governance of semantic views used for natural language querying and governed analytics. This rule is not about plain SQL views.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Cortex Analyst semantic model specification and Snowflake Semantic Views authoring, validation, and governance

## Contract
- **Inputs/Prereqs:**
  - Target DATABASE.SCHEMA
  - Warehouse context and roles with appropriate privileges (see `119-snowflake-warehouse-management.md`)
  - Source physical tables/views inventory
  - Naming conventions and business glossary (for synonyms and metrics)
- **Allowed Tools:**
  - SQL authoring for semantic views
  - YAML authoring for semantic models
  - Snowflake UI/CLI to validate objects and query profiles
- **Forbidden Tools:**
  - Plain view guidance where semantic views or semantic models are required
  - Ambiguous `SELECT *` in production semantic views or verified queries
- **Required Steps:**
  1. Define logical tables mapping to physical base tables with primary keys.
  2. Declare dimensions, time dimensions, facts, filters, and metrics with explicit expressions and data types.
  3. Model relationships with correct `relationship_type`, `join_type`, and key columns.
  4. Provide synonyms and descriptions to align with business language.
  5. Create semantic views that surface curated metrics and dimensions with explicit columns and comments.
  6. Validate allowed references and relationship traversal against the spec.
  7. Apply governance: security policies, role-based access, comments, versioning.
- **Output Format:**
  - Minimal, runnable YAML fragments for semantic models
  - Minimal, runnable SQL for semantic views (`CREATE SEMANTIC VIEW ... AS SELECT ...`)
- **Validation Steps:**
  - YAML validates against the semantic model spec (logical objects and fields present, allowed refs only)
  - Semantic views select explicit columns and compile successfully
  - Relationships resolve without Cartesian products; keys are present on joined tables
  - Security and comments are applied where required

## Key Principles
- Prefer semantic models and semantic views specifically; do not rely on plain views for this layer.
- Use explicit names and business-aligned synonyms; avoid abbreviations that hinder NLQ.
- Define primary keys for any logical table participating in relationships.
- Keep metrics additive where possible; document non-additive metrics and compute at base grain.
- Follow allowed-references rules: expressions may reference physical columns of own base table; logical columns from own or other logical tables in the model (not physical columns of other physical tables).
- Use explicit column projection; avoid `SELECT *`.
- Add `COMMENT` metadata to semantic views and key logical objects.
- Enforce security: masking, row access policies, and least-privilege roles.

## 1) Cortex Analyst Semantic Models

- Logical tables map to physical base tables or views via fully-qualified names and include a `primary_key` when used in relationships.
- Column types:
  - Dimensions (categorical)
  - Time dimensions (temporal)
  - Facts (row-level numeric)
  - Filters (logical predicates)
  - Metrics (aggregations over facts and/or logical columns)
- Synonyms increase NLQ accuracy; keep unique across the model.
- Relationships must specify `left_table`, `right_table`, `relationship_columns`, `join_type` (`left_outer` or `inner`), and `relationship_type` (`many_to_one` or `one_to_one`). Place the many side as `left_table` for performance.
- Verified queries and custom instructions can further constrain and guide NLQ behavior.

### Minimal YAML skeleton
```yaml
tables:
  - name: orders
    description: Sales orders entity at header level.
    base_table:
      database: PROD
      schema: SALES
      table: ORDERS
    primary_key:
      columns: [order_id]

    dimensions:
      - name: order_status
        expr: orders.status
        data_type: STRING
        synonyms: ["status"]

    time_dimensions:
      - name: order_date
        expr: orders.order_date
        data_type: DATE

    facts:
      - name: order_amount
        expr: orders.amount
        data_type: NUMBER

    filters:
      - name: us_only
        expr: customers.country = 'United States'

    metrics:
      - name: total_revenue
        expr: SUM(orders.amount)

relationships:
  - name: orders_to_customers
    left_table: orders
    right_table: customers
    relationship_columns:
      - left_column: customer_id
        right_column: customer_id
    join_type: left_outer
    relationship_type: many_to_one
```

## 2) Snowflake Semantic Views

- Create semantic views to present curated, governed projections aligned with the semantic model and business consumption.
- Use explicit columns, add `COMMENT`, and fully-qualify dependencies.
- Avoid deep nesting; semantic views should be slim and purpose-built.

### Minimal SQL example
```sql
CREATE OR REPLACE SEMANTIC VIEW PROD.SALES.V_ORDERS_SUMMARY
COMMENT = 'Curated orders summary for BI and NLQ'
AS
SELECT
  o.order_id,
  o.order_date,
  o.order_status,
  c.customer_name,
  o.order_amount,
  SUM(o.order_amount) OVER (PARTITION BY c.customer_id) AS customer_lifetime_value
FROM PROD.SALES.ORDERS AS o
JOIN PROD.SALES.CUSTOMERS AS c
  ON o.customer_id = c.customer_id;
```

## 3) Governance and Versioning
- Store semantic model YAML in version control with review policies.
- Version semantic views alongside model changes; include migration notes in PRs.
- Apply role-based access; restrict write/admin privileges.

## 4) Performance, Cost, and Pitfalls
- Push filters early and avoid unnecessary joins in semantic views.
- Ensure relationship keys exist and are selective to prevent large joins.
- Document non-additive metrics and compute directly from base grain.
- Avoid ambiguous synonyms or overlapping names across logical objects.

## Quick Compliance Checklist
- [ ] Primary keys defined for all related logical tables
- [ ] Dimensions, time dimensions, facts, filters, and metrics have explicit expressions and types
- [ ] Relationships configured with correct join and relationship types
- [ ] Synonyms are unique and business-aligned
- [ ] Semantic views project explicit columns and include comments
- [ ] Security policies and least-privilege roles applied

## Validation
- Success: YAML validates per spec; semantic views compile and return accurate results.
- Success: Query profile shows no accidental Cartesian joins; selective filters applied.
- Negative: Metrics referencing physical columns from other base tables (outside allowed references) should be rejected and refactored.

## Response Template
```yaml
# Filename: semantic_model.yaml
# Description: Minimal semantic model definition
tables:
  - name: <logical_table>
    base_table: { database: <DB>, schema: <SCHEMA>, table: <TABLE> }
    primary_key: { columns: [<pk_col>] }
    dimensions: [{ name: <dim>, expr: <expr>, data_type: STRING }]
    time_dimensions: [{ name: <tdim>, expr: <expr>, data_type: DATE }]
    facts: [{ name: <fact>, expr: <expr>, data_type: NUMBER }]
    metrics: [{ name: <metric>, expr: SUM(<fact>) }]
relationships:
  - name: <rel_name>
    left_table: <many_side>
    right_table: <one_side>
    relationship_columns: [{ left_column: <col>, right_column: <col> }]
    join_type: left_outer
    relationship_type: many_to_one
```

```sql
-- Filename: create_semantic_view.sql
-- Description: Minimal semantic view
CREATE OR REPLACE SEMANTIC VIEW <DB>.<SCHEMA>.<VIEW_NAME>
COMMENT = 'Purpose-built semantic view'
AS
SELECT <explicit_columns>
FROM <DB>.<SCHEMA>.<SOURCE>
WHERE <optional_filter>;
```

## References

### External Documentation
- [Cortex Analyst semantic model specification](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec)
- [Snowflake Semantic Views overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview)
- [Snowflake Semantic Views SQL](https://docs.snowflake.com/en/user-guide/views-semantic/sql)

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Data Governance**: `600-data-governance-quality.md`

