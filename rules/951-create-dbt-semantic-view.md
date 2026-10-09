---
schema_version: v4.0
rule_version: v5.0.0
description: "Snowflake semantic views as dbt models via dbt_semantic_view: correct CREATE SEMANTIC VIEW clause syntax, lineage refs, documented keys and verified SEMANTIC_VIEW queries."
last_updated: 2026-10-07
keywords:
  - kw:dbt_semantic_view package
  - kw:semantic_view materialization
  - kw:cortex analyst integration
  - kw:semantic view function
  - kw:primary key constraints
  - kw:dimensions metrics relationships
token_budget: ~1000
context_tier: High
depends:
  required:
    - 950-dbt-core.md
---
# Semantic Views with dbt

## Scope

**What This Rule Covers:**
Authoring Snowflake semantic views as dbt models with the `dbt_semantic_view` package's `semantic_view` materialization: logical tables, keys, relationships, facts, dimensions, metrics, comments, deployment, querying with `SEMANTIC_VIEW()` and handoff to Cortex Analyst/Agents.

**When to Load This Rule:**
When creating, migrating or troubleshooting dbt-managed semantic views; load `950-dbt-core.md` for running dbt inside Snowflake.

## Contract

### Inputs and Prerequisites

- dbt project and adapter version, installed `dbt_semantic_view` package version, base models/sources with grain, keys and relationships.
- Business metric definitions and owners, existing semantic views or YAML models, target database/schema, role and authority to build objects.

### Mandatory

- In a dbt-managed project, create and change semantic views through `semantic_view` models so lineage, review and CI apply; hand-run DDL is for investigation in development only, and existing hand-authored views are migrated deliberately.
- Reference base objects with `{{ ref() }}`/`{{ source() }}` in TABLES, using a logical table alias for each.
- Follow current CREATE SEMANTIC VIEW syntax, which the package passes through: clause order TABLES, RELATIONSHIPS, FACTS, DIMENSIONS, METRICS; facts, dimensions and metrics are written `<table_alias>.<name> AS <sql_expr>`, with the defined name on the left and the expression on the right.
- Declare PRIMARY KEY or UNIQUE on logical tables that are referenced by relationships and confirm the key is actually unique in the data; relationships reference the target table's key columns.
- Time columns are ordinary dimensions; there is no TIME_DIMENSIONS clause.
- Metrics aggregate facts or columns of the same logical table or follow documented derived/window metric forms; guard ratios against division by zero and match the canonical business definition.
- Add COMMENT and meaningful synonyms to tables, dimensions, facts and metrics in the definition; do not rely on `persist_docs` unless verified for this materialization.
- Building, replacing or dropping semantic views and running test queries are Snowflake mutations or compute use requiring approval; never drop a production view as a rollback without approval and an available rebuild path.
- Query with `SEMANTIC_VIEW(...)` using bare names, or entity-qualified names where ambiguous; verify results reconcile to equivalent queries on base models.
- Validate with `DESCRIBE SEMANTIC VIEW`, `SHOW SEMANTIC DIMENSIONS/METRICS` and representative queries; do not claim correctness from a successful build alone.
- For Cortex Analyst or Agent use, keep names business-friendly, add verified queries where supported, and configure agents per current agent documentation without hard-coding model names.

### Execution Steps

1. Read package version, base models, grain, keys and metric definitions; check uniqueness and relationship cardinality read-only.
2. Author the `semantic_view` model with correct clause order, alias-qualified definitions, keys, relationships and comments.
3. With approval, build in development, describe the view and reconcile `SEMANTIC_VIEW()` results to base-model queries.
4. Report the model, metrics, verification evidence, deployment status and remaining gaps.

### Validation

- Clause order and `<alias>.<name> AS <expr>` forms match current syntax; no TIME_DIMENSIONS.
- Keys unique in data and relationships consistent with grain.
- Metrics match canonical definitions and reconcile to base queries.
- Comments and synonyms present; builds and queries verified in the target environment.

## References

- [CREATE SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [Querying semantic views](https://docs.snowflake.com/en/user-guide/views-semantic/querying)
- [dbt_semantic_view package](https://github.com/Snowflake-Labs/dbt_semantic_view)
- [Semantic views overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview)
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
