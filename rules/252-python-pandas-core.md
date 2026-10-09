---
schema_version: v4.0
rule_version: v5.0.0
description: "Correct pandas indexing/alignment/NULL semantics, scoped transformations and measured vectorization."
last_updated: 2026-10-07
keywords:
  - kw:pandas vectorization
  - kw:SettingWithCopyWarning
  - kw:.loc .iloc indexing
  - kw:pandas method chaining
  - kw:np.where np.select conditional
  - kw:iterrows apply anti-patterns
  - kw:pandas
token_budget: ~1000
context_tier: High
depends:
  required:
    - 200-python-core.md  # Modern Python tooling and practices
  optional:
    - 251-python-datetime-core.md  # Datetime handling for Pandas
    - 252a-python-pandas-performance.md  # Memory optimization, groupby, merge, eval/query
    - 252b-python-pandas-io-integration.md  # Streamlit, Plotly, file I/O integration
---
# Pandas Core Best Practices

## Scope

**What This Rule Covers:**
Existing frame/schema investigation, label/position alignment, safe assignment, vectorization/conditions and independent transformation checks.

**When to Load This Rule:**
When transforming pandas frames/Series; read datetime/performance/IO companions for those tasks.

## Contract

### Inputs and Prerequisites

- Actual data shape/schema/dtypes/index, installed pandas/NumPy and Copy-on-Write behavior.
- Intended output grain/order/NULL/type/precision and authorized data/operation scope.

### Mandatory

- Read current operations and actual dtypes/index before optimization; don't assume shape, types or CoW defaults across versions. Diagnose exact warning/error; suppressing SettingWithCopy warnings isn't a fix.
- Use .loc for labeled selection/assignment and .iloc for positions; masks/Series align by index. Duplicate labels, reordered RHS and mismatched indices can silently change results; explicit positional conversion only when contract warrants.
- Modify original frame with one assignment, not chained df[mask][column]. For independent subset use intentional copy under actual CoW semantics. Changes to iterrows row objects aren't reliable frame writes.
- Prefer native vectorized arithmetic/string/datetime/agg where correct and measured; apply/itertuples can suit distinct unsupported operations. No guaranteed 10x/100x or categorical prohibition on every loop; external per-row calls require separate approval/bounds.
- np.where/np.select can coerce dtypes/evaluate both branches; nullable Boolean pd.NA may need explicit mask policy. Series.where/mask or guarded arithmetic can preserve nullable/index semantics; no dividing by zero in a supposedly inactive vector branch.
- Use .str operations with deliberate regex/literal/NA handling and actual string types. Input query/eval expression must be trusted/static; never interpolate arbitrary user strings as executable pandas expressions.
- Preserve NULL/missing/zero distinctions, integer/Decimal/floating precision and business tolerances. sum/count/size/mean/groupby dropna defaults differ and all-missing sums can become zero; define intended population.
- Readable assign/pipe/chains suit transformations but intermediate named stages are valid for clarity. Don't automatically remove outliers, drop duplicates/NULLs or fill values as a generic cleanup; these change data meaning and need requirement/authority.
- df.append removed in pandas2; collect/concat intentionally rather than loop-concat quadratic memory. inplace isn't itself universally deprecated/unsafe, but assignment is clearer under actual version/CoW ownership.
- Inspect resulting rows/keys/index/dtypes/order and reconcile independent counts/totals. Test empty/all-null/duplicate index/mask/type boundaries before claimed correctness; performance measurement separate.

### Execution Steps

1. Inspect frame/version/current transformation and define output invariants.
2. Implement minimal index/NULL/type-correct operation with suitable vectorization.
3. Test independent expected values/rows/dtypes, empty and alignment edge cases.
4. Run project checks and approved benchmarks; report semantic/performance gaps.

### Validation

- Index/label/position/mask ownership correct, no chained assignment or silently lost changes.
- NULL/type/precision/grain/order preserve intended values; no unapproved cleanup/drop.
- Actual before/after correctness and measured performance separate; checks pass.

## References

- [Pandas indexing](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Copy-on-Write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
- [Missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Pandas performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
