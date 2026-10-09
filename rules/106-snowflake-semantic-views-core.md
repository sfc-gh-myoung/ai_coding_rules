---
schema_version: v4.0
rule_version: v5.0.0
description: 'Creating and safely evolving Snowflake Native Semantic Views: logical tables, expressions, relationships, and validation.'
last_updated: 2026-10-07
keywords:
- kw:CREATE SEMANTIC VIEW
- kw:TABLES PRIMARY KEY
- kw:FACTS DIMENSIONS METRICS
- kw:RELATIONSHIPS clause
- kw:mapping syntax alias.physical_column
- kw:SHOW SEMANTIC DIMENSIONS
- kw:semantic view
token_budget: ~1150
context_tier: High
depends:
  required:
  - 100-snowflake-core.md
---
# Snowflake Native Semantic Views: Core DDL

## Scope

**What This Rule Covers:**
Native semantic-view definitions, physical/logical mappings, relationships, business expressions, metadata, and safe deployment.

**When to Load This Rule:**
When creating, reviewing, or debugging CREATE SEMANTIC VIEW definitions and their evolution.

## Contract

### Inputs and Prerequisites

- Actual source schemas, business glossary, table grain/keys, relationship cardinality, metric units/NULL policy, and approved target.
- Read existing semantic definitions and exact physical columns through available metadata. Creation needs CREATE SEMANTIC VIEW on the schema and SELECT on referenced tables/views, with applicable parent privileges; changing existing definitions needs appropriate ownership.
- Separate design from account execution. Missing source data blocks result validation, not necessarily definition authoring; do not invent columns or claim data checks passed.

### Mandatory

- Use current documented SQL or YAML creation workflows according to project requirements. SQL now supports AI_VERIFIED_QUERIES; do not claim verified queries are YAML-only or assume YAML/service payloads are interchangeable.
- Follow clause order: TABLES, optional RELATIONSHIPS, FACTS, DIMENSIONS, METRICS, then supported view properties. A definition needs at least one dimension or metric, not all optional blocks.
- Map logical names to expressions: alias.logical_name AS sql_expression. TABLES maps a logical alias to a qualified physical source. Preserve exact physical identifier case; never reverse the expression mapping because a trigger keyword uses older terminology.
- Facts and dimensions are row-level expressions; metrics are aggregate-level calculations. Dimensions support scalar expressions, not merely direct columns. Validate each expression against documented granularity/function restrictions; use a base view when it genuinely simplifies the model.
- Declare keys that reflect actual grain, including composite keys where needed. Verify uniqueness/non-NULL values and relationship coverage; a key declaration is not proof of data integrity. Respect documented allowed key expressions and relationship target constraints.
- Define supported many-to-one/one-to-one relationships and aliases; reject self/circular paths. Review fanout, ambiguous paths, and cross-table expression rules before publishing metrics.
- Define aggregation, derived ratios, units, date/time zones, and NULL behavior explicitly. Avoid unintended double aggregation and denominator-zero errors; substitution of NULLs must match business meaning.
- Add distinct synonyms and explanatory comments without confidential/regulated metadata. COMMENT uses equals syntax. Template characters are a client-renderer concern, not a universal semantic-view ban; inspect configured substitution/escaping before execution.
- Inspect existing grants, consumers, and materializations before evolution. ALTER does not support arbitrary ADD/DROP DIMENSIONS/METRICS; use supported CREATE OR ALTER or reviewed replacement. CREATE OR ALTER can unset omitted properties; replacement can drop materializations and explicit grants without COPY GRANTS.
- No CREATE OR REPLACE against an assumed disposable production target. Define ownership-scoped deployment, compatibility checks, and recovery; changing a view definition is a mutation requiring authorization.

### Execution Steps

1. Inspect sources and existing semantic views, resolve glossary/grain/keys/units, and identify deployment scope and unresolved inputs.
2. Define logical tables and valid relationships, then logical expressions/metrics, synonyms/comments, and any approved verified queries.
3. Review syntax, expression dependencies, cardinality, aggregation, security, and client rendering against current primary documentation.
4. Only with execution approval, deploy in the intended scope and inspect DESCRIBE/SHOW SEMANTIC VIEWS, DIMENSIONS, FACTS, METRICS, and GET_DDL evidence as supported.
5. Compare representative semantic results with independently derived physical-table calculations; test consumers/NLQ only when authorized and configured.

### Validation

- Physical names/mapping direction, clause order, required expression presence, keys, relationships, and metric semantics verified.
- Actual key/NULL/coverage tests distinguish data quality from syntactic validity; empty data is not evidence of correct business totals.
- Effective definition, grants, consumers, and materializations meet approved deployment expectations.
- Deliver reviewed definition, business meanings, prerequisites, deployment/recovery steps, and exact validation outcomes. Compile/deploy/NLQ checks not run remain unverified; a successful Analyst response is not sufficient correctness proof.

## References

- [CREATE SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [ALTER SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/alter-semantic-view)
- [Semantic-view validation](https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules)
- [SQL creation and management](https://docs.snowflake.com/en/user-guide/views-semantic/sql)
- `106a-snowflake-semantic-views-advanced.md` for expression/cardinality validation.
- `106b-snowflake-semantic-views-querying.md` and `106c-snowflake-semantic-views-integration.md` for consumers.
