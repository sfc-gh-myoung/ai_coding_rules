---
schema_version: v4.0
rule_version: v3.0.0
description: "Measured pandas memory/query optimization with range-safe dtypes, cardinality-correct joins and complete chunk reconciliation."
last_updated: 2026-10-07
keywords:
  - kw:pandas dtype optimization
  - kw:categorical data memory
  - kw:groupby aggregation efficiency
  - kw:merge validation indicator
  - kw:eval query expressions
  - kw:chunked file processing
  - kw:pandas
token_budget: ~1050
context_tier: Medium
depends:
  required:
    - 252-python-pandas-core.md  # Core Pandas patterns
  optional:
    - 252b-python-pandas-io-integration.md  # Streamlit, Plotly, file I/O
    - 251-python-datetime-core.md  # Datetime handling
---
# Pandas Performance and Memory Optimization

## Scope

**What This Rule Covers:**
Dtype/category/sparse tradeoffs, aggregation/join semantics, trusted expressions, bounded chunks and concurrency ownership.

**When to Load This Rule:**
When measured pandas resource bottlenecks require improvement; read IO/datetime companions where needed.

## Contract

### Inputs and Prerequisites

- Actual frame memory/dtypes/cardinality/key distributions, operation timings, installed engine/version and intended invariant.
- Permitted benchmark scope, memory target, precision/range/NULL rules and chunk/error policy.

### Mandatory

- Profile memory_usage(deep=True), peak allocations and actual bottleneck before optimizing. No compulsory dtype rewrite at 100000 rows or guaranteed savings from category/sparse.
- Validate min/max and future/domain range before integer narrowing; int8 is -128..127 and ordinary numeric casts can wrap instead of raise. Status codes such as 200 don't fit. Nullable integers/missing and unsigned negatives need explicit checks.
- float32 can lose precision; retain actual financial/statistical tolerances. Downcast only with independent value/round-trip checks; errors=coerce needs reject accounting, not silent recovery.
- Categories help repeated values under actual cardinality/access patterns; handle unseen values, category unions/order and groupby observed defaults. A universal <50% string ratio isn't proof of net benefit.
- Sparse data needs deliberate fill value and downstream operation support; verify serialization/densification cost. Memory savings examples aren't estimates for unseen frames.
- Prefilter only if transformation semantics permit: row predicate before aggregation isn't equivalent to HAVING/group total after. Combine/reuse aggregations when useful, define NULL/dropna/observed/sort and count versus size; no guarantee .agg is one physical scan.
- Merges specify actual key/type/cardinality and validate=1:1/1:m/m:1 as appropriate, indicator and independent rows/totals. m:m validate doesn't prevent fanout; pandas can match null keys unlike typical SQL joins. Prevent unnoticed duplicate/null join expansion.
- Indexing repeated joins may help but isn't universally faster or required. Preserve index/key/order semantics and measure real workload, not categorical ban on nonindexed merges.
- query/eval expressions are trusted static code, not safe sandbox for user input. Actual supported engine/Numexpr/dtypes decide benefits; no mandatory eval on large data or unreviewed expression injection.
- Chunk reads retain global group/key/dedup/order state needed for correctness; totals/means require valid reduction/weights. Don't skip failed chunks then publish a complete total; fail or explicitly report partial with original identities/reject counts.
- Bound chunks, aggregate/error/unique/cache state and final output; no collecting whole frames in results to claim streaming memory-flat. Test count/type/key/totals across boundaries and last partial chunk.
- Concurrent mutation isn't safe by default; .copy can still share nested Python objects and copy itself can race. Use synchronized ownership/independent data or justified processes, accounting for serialization and global aggregation. No multiprocessing change without measured need.

### Execution Steps

1. Profile actual resource/current semantics and choose smallest justified optimization.
2. Implement range/precision-safe dtypes, correct joins/agg or bounded chunks with explicit failure accounting.
3. Verify independent expected outputs and boundary/null/duplicate/chunk/concurrency cases.
4. Benchmark controlled before/after and run project checks; report partial/unverified scope.

### Validation

- Range/NULL/precision/category/sparse changes preserve expected values and future contract.
- Aggregation/filter/merge grain correct and totals reconcile without fanout or null surprises.
- Chunks/concurrency bounded and complete or truthfully partial; no hidden errors.
- Performance actually measured, not inferred from syntax/library choice.

## References

- [Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [Merge cardinality/null behavior](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)
- [GroupBy](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Categorical data](https://pandas.pydata.org/docs/user_guide/categorical.html)
- [Scaling/chunks](https://pandas.pydata.org/docs/user_guide/scale.html)
