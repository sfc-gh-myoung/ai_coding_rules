---
schema_version: v4.0
rule_version: v5.0.0
description: Advanced semantic-view relationship, expression, data-quality, and deployment validation.
last_updated: 2026-10-07
keywords:
  - kw:semantic view anti-patterns
  - kw:relationship granularity
  - kw:physical column verification
  - kw:expression reference cycles
  - kw:template character restrictions
  - kw:semantic view quality checks
token_budget: ~1150
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake SQL patterns
    - 106-snowflake-semantic-views-core.md  # Semantic Views DDL fundamentals
  optional:
    - 106b-snowflake-semantic-views-querying.md  # Query patterns, SEMANTIC_VIEW() function
    - 106c-snowflake-semantic-views-integration.md  # Cortex Analyst/Agent integration
---
# Snowflake Semantic Views: Advanced Patterns and Validation

## Scope

**What This Rule Covers:**
Schema grounding, relationship paths/granularity, expression dependencies, window metrics, data integrity, and evidence-based quality review.

**When to Load This Rule:**
When reviewing complex semantic models, diagnosing definition/query errors, or designing semantic-view quality gates.

## Contract

### Inputs and Prerequisites

- Core rule loaded, actual source metadata and semantic definition, relationship/key evidence, and expected business calculations.
- Authorized inspection/test scope and relevant role privileges; CREATE SEMANTIC VIEW and source SELECT for creation, not a nonexistent table USAGE requirement.

### Mandatory

- Verify exact physical columns with DESCRIBE TABLE/view or equivalent current schema evidence before DDL. Compare case-sensitive identifiers accurately; uppercasing every name can hide quoted-name mismatches.
- Use alias.logical_name AS expression, with physical columns on the expression side. Require at least one dimension or metric; preserve TABLES/RELATIONSHIPS/FACTS/DIMENSIONS/METRICS order when present.
- Keys use supported physical columns or direct-column expressions; referenced keys must meet documented primary/unique-key constraints for the chosen relationship. Test actual uniqueness, NULLs, orphan keys, and composite-key completeness.
- Review many-to-one and one-to-one relationships, transitive paths, and multipath restrictions. Reject cycles and self-references; do not assume two tables with matching column names are related.
- Bind semantic expressions to their logical table and refer across tables through connected semantic expressions, not arbitrary remote physical columns. Check name resolution when physical and semantic names overlap.
- Facts/dimensions permit row-level scalar expressions; table functions are not allowed in dimensions. Do not ban CAST/DATE_TRUNC categorically or confuse table alias qualification with a function-name prefix.
- Follow documented same/equal/lower/higher-granularity expression rules, including required aggregation or nested aggregation. Reject semantic-expression and table-reference cycles; review derived metrics for correct aggregation level rather than assuming every metric contains SUM.
- One-to-one relationships have equal-grain rules distinct from many-to-one: row-level references are direct and metrics reference row-level values through a single aggregate, or other equal-grain metrics directly.
- Window-function metrics cannot feed row-level facts/dimensions or other metric definitions. Validate partition/order/frame meanings and required query dimensions independently.
- Inspect the actual CLI/renderer before handling template characters in synonyms/comments. Correct escaping or disable unwanted substitution according to approved tooling; do not change business labels solely to satisfy an invented universal character ban.
- Separate structural validation from business/data correctness. Compilation or SHOW output does not prove cardinality, measure totals, access policy, performance, or NLQ quality.
- Preserve current grants/consumers/materializations and authorization through deployment/recovery. Keep source data and sensitive metadata out of external validators and test prompts unless explicitly authorized.

### Execution Steps

1. Inspect existing DDL/schema and document logical-to-physical mappings, keys, grain, units, and dependencies.
2. Trace relationship/expression graphs and review names, cardinality, aggregation, windows, renderer behavior, and privileges.
3. Prepare expected-result tests for key/NULL/orphan/duplicate cases, fanout, empty sets, and representative metric combinations.
4. Execute only approved definition/data tests; inspect effective DDL and SHOW/DESCRIBE output after authorized deployment.
5. Compare semantic and independent physical results at the same grain/filter scope; report failures and unresolved verification separately from optional Analyst checks.

### Validation

- Each physical reference grounded; relationships and expressions meet current documented restrictions without circular/self references.
- Key quality and result cardinality/totals verified with actual data; quoted identifiers and NULL cases handled accurately.
- Window/derived metrics and renderer behavior tested where applicable, with no unsupported character/function prohibition.
- Review output records definition/data/security findings, supporting evidence, corrected guidance, and remaining gaps. No unrun SQL or inferred compliance pass.

## References

- [Semantic-view validation rules](https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules)
- [CREATE SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [Querying semantic views](https://docs.snowflake.com/en/user-guide/views-semantic/querying)
- `106-snowflake-semantic-views-core.md` for deployment and mapping fundamentals.
- `106b-snowflake-semantic-views-querying.md` for metric/dimension compatibility tests.
