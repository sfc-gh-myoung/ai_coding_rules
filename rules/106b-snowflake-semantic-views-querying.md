---
schema_version: v4.0
rule_version: v5.0.0
description: Snowflake semantic SQL query forms, grain/filter compatibility, window metrics, and result validation.
last_updated: 2026-10-07
keywords:
  - kw:SEMANTIC_VIEW function
  - kw:dimension compatibility
  - kw:FACTS METRICS mutual exclusion
  - kw:window function metrics
  - kw:semantic view testing
  - kw:WHERE clause restrictions
token_budget: ~1150
context_tier: High
depends:
  required:
    - 106-snowflake-semantic-views-core.md  # Semantic Views DDL fundamentals
---
# Snowflake Semantic Views: Querying and Testing

## Scope

**What This Rule Covers:**
Semantic-query forms, logical expressions, compatible dimensions/metrics, filter timing, window requirements, and independent correctness/performance tests.

**When to Load This Rule:**
When querying semantic views, comparing semantic results, or diagnosing semantic SQL errors.

## Contract

### Inputs and Prerequisites

- Actual semantic view definition, logical calculations, relationship/grain metadata, business question, and approved query scope.
- SELECT on the semantic view with applicable parent/warehouse access. Query consumers do not inherently need SELECT on underlying tables; independent physical-table comparisons need separately authorized source access.

### Mandatory

- Inspect SHOW SEMANTIC DIMENSIONS/METRICS/FACTS and DESCRIBE/GET_DDL through permitted reads. Use exact defined logical names; do not invent columns or assume a physical column is exposed.
- Choose a supported query form: SEMANTIC_VIEW(view ...), or direct FROM semantic_view with documented AGG(metric)/GROUP BY semantics. Direct SELECT is not categorically prohibited; SELECT * is not mandatory.
- In SEMANTIC_VIEW specify at least one DIMENSIONS, FACTS, or METRICS clause. FACTS and METRICS are mutually exclusive there; dimensions can accompany either subject to compatibility.
- For FACTS plus DIMENSIONS, dimensions must uniquely determine facts and all facts/dimensions, including filters, must belong to the same logical table. Otherwise results can be nondeterministic; row detail requires an adequate grain.
- For metrics, choose dimensions reachable through valid relationships at supported equal/lower granularity. Use SHOW SEMANTIC DIMENSIONS FOR METRIC to inspect compatibility and required dimensions, not a blanket day/month rule.
- Include dimensions required by window metric partition/order expressions. Verify frame boundaries, sparse dates, tie ordering, and filter effects; window metric validity does not guarantee business-period correctness.
- Distinguish WHERE inside semantic computation from an outer filter on returned results. Apply row-level dimension/fact conditions before aggregation and metric-result conditions after aggregation; do not assume filters must always be returned columns or can aggregate inside semantic WHERE.
- For direct FROM queries, select defined metrics through AGG, group selected dimensions appropriately, use dimensions/facts in WHERE and metric expressions in HAVING as documented. Qualify ambiguous calculation names by logical table.
- Preserve aliases, grain, units, NULL/duplicate semantics, join paths, and filter scope. NULL grouping and aggregate behavior differ for COUNT(*), COUNT(column), SUM, and AVG; empty results and zero denominators need explicit expectations.
- Compare semantic results with independently authored base calculations at matching grain and filters. Do not sum already-aggregated non-additive metrics or filter a missing returned alias in the comparison.
- Use Query Profile for actual bottlenecks and inspect base-table organization; do not run unsupported SHOW CLUSTERING KEYS or automatically ALTER tables. Materializations may affect performance and freshness; inspect actual configuration before asserting metadata-only behavior.
- Analyst/CLI/API testing is optional and separately authorized. Verify installed command/payload syntax and permissions first; never send source data or credentials to an arbitrary endpoint or call a generated answer a correctness certificate.

### Execution Steps

1. Inspect logical model and compatibility, resolve expected result grain/time/filter semantics, and note access limitations.
2. Construct the chosen documented query form with exact names/aliases and necessary window dimensions.
3. Review filter/aggregation order, fanout, NULL behavior, determinism, and security before approved execution.
4. Execute representative and boundary cases only in authorized scope; compare independent expected results and inspect performance evidence.
5. Report actual query IDs/results, equivalence differences, timing/freshness conditions, and unexecuted checks without modifying the model to conceal a failure.

### Validation

- Valid clause combination, defined calculations, compatible dimensions, and required window dimensions.
- Matching grain/filter/unit/NULL semantics and totals across independent comparisons; non-additive metrics not double-aggregated.
- Correct pre/post-aggregation filters and direct FROM AGG/GROUP BY behavior where used.
- Performance findings supported by actual profiles and materialization freshness/configuration.
- Output includes reviewed queries, expected-result tests, evidence, and limitations; no SQL/cloud execution solely to satisfy this checklist.

## References

- [Query forms, privileges, filters, and compatibility](https://docs.snowflake.com/en/user-guide/views-semantic/querying)
- [SHOW SEMANTIC DIMENSIONS FOR METRIC](https://docs.snowflake.com/en/sql-reference/sql/show-semantic-dimensions-for-metric)
- [AGG](https://docs.snowflake.com/en/sql-reference/functions/agg)
- [Semantic-view materializations](https://docs.snowflake.com/en/user-guide/views-semantic/materializations)
- `106-snowflake-semantic-views-core.md` for model definitions.
- `103-snowflake-performance-tuning.md` for evidence-based performance diagnosis.
