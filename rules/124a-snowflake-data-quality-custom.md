---
schema_version: v4.0
rule_version: v5.0.0
description: "Deterministic SQL custom DMFs with TABLE arguments, NUMBER results, tested metric semantics and valid named expectations."
last_updated: 2026-10-07
keywords:
  - kw:custom DMF creation
  - kw:business rule validation
  - kw:expectation thresholds
  - kw:FLOAT return type
  - kw:parameterized ARG_T
  - kw:Python UDF DMF
  - kw:dmf
token_budget: ~1400
context_tier: Medium
depends:
  required:
    - 124-snowflake-data-quality-core.md  # Data Quality fundamentals
  optional:
    - 124b-snowflake-data-quality-operations.md  # Operational patterns and scheduling
---
# Snowflake Data Quality: Custom DMFs and Expectations

## Scope

**What This Rule Covers:**
Business-specific scalar SQL metrics, reusable typed table arguments, NULL/empty/cardinality behavior, expectations, testing and safe function evolution.

**When to Load This Rule:**
When system metrics cannot express a required business check or a custom metric/expectation needs diagnosis. Read `124b-snowflake-data-quality-operations.md` for execution/results/scheduling.

## Contract

### Inputs and Prerequisites

- Existing metric/association definitions, actual business formula/units/tolerance, target schema/keys and input population, and system-metric alternatives.
- Approved CREATE DATA METRIC FUNCTION on schema, function/object/result privileges and isolated testing scope.
- Current SQL DMF specification, expected edge-case outputs, execution/association owner and cost/cadence budget.

### Mandatory

- Read existing data-quality conventions/data distribution before custom design. Create one focused metric per distinct requirement; no arbitrary complexity/line/five-minute ban, duplicate system metric, or forced custom function.
- Use CREATE DATA METRIC FUNCTION, not generic CREATE FUNCTION. Custom DMFs support deterministic scalar SQL only and RETURNS NUMBER; FLOAT and LANGUAGE PYTHON DMF examples are invalid. Do not work around this with an ordinary Python UDF-dependent object that the DMF specification disallows.
- Declare one or more TABLE arguments with typed column arguments and map association columns in matching order. Use argument tables for reusable checks instead of silently hardcoding a production object or a zero-argument custom signature.
- Match a precise count/rate/amount/Boolean-coded numeric meaning, units and scale to NUMBER behavior. Choose supported precision for ratios; do not cast Boolean to FLOAT and assume the DMF accepts it. Document 0/1 meaning when used.
- Expression must return one deterministic scalar. Current-time/nondeterministic functions and objects depending on UDF/UDTF violate documented restrictions; use supported system freshness or explicitly supplied deterministic data for time-based checks.
- Handle empty tables, all NULLs, zero denominators, unknown values, future/extreme values and threshold inclusivity explicitly. COUNT_IF can be NULL for no matching records; COUNT(*) on filtered rows can express an unambiguous zero. Empty data is not universally zero quality or a passing check.
- For cross-table integrity define source/reference keys, source NULL policy, duplicate reference behavior and orphan population. Use NULL-safe semantics; NOT IN with reference NULL can suppress orphans, and one-to-many joins can inflate counts.
- For order-versus-lines totals aggregate lines to unique order grain before comparison; define missing-line/NULL/currency/rounding tolerance. Thresholds belong to the actual business rule, not a copied million-dollar range/0.01 default.
- Regex/format checks implement a stated accepted format, not proof an email/phone exists or is deliverable. Keep optional NULL handling separate from format failures; use documented SQL functions and actual escaping.
- Named EXPECTATION evaluates returned VALUE using supported Boolean/comparison operators. It cannot query another table/view or UDF. Compute a rate/denominator in the metric, not compare NULL_COUNT to a guessed absolute count labeled percentage or embed a subquery in EXPECTATION.
- Test functions by supplying a query projection matching TABLE argument signatures; multi-table arguments use documented call syntax. Test expectation behavior using supported evaluation, not an assumed zero-argument SELECT metric().
- Test valid/invalid/boundary/empty/NULL/skewed/duplicate populations against independent expected values before approved production association. Inspect runtime/cost on representative sizes, not just compiling DDL; retain unexecuted cases as gaps.
- More complex validation can use an appropriately supported precomputed view/table/pipeline when needed; do not prescribe joins/CTEs in an unsupported materialized view. Review freshness/security and total maintenance cost before moving logic.
- Inspect existing associations/grants before replacement; CREATE OR ALTER has limited supported changes and does not arbitrarily change the function body/signature. Version definitions and migrate bindings under approved scope with rollback; no blind OR REPLACE.
- Document name, signature/population, formula/units, empty/NULL/reject behavior, threshold rationale, tests, owner and schedule. Keep confidential values out of function comments or test artifacts transmitted externally.

### Execution Steps

1. Inspect actual business/data contract and existing checks; select custom versus system metric and expected edge behavior.
2. Define deterministic SQL TABLE-argument metric returning NUMBER and named expectation, with scoped privilege/deployment/recovery requirements.
3. Test query-projected inputs and expectation boundaries in approved isolated scope; compare independent results and resource cost.
4. Apply approved version/binding/schedule changes; inspect dedicated evaluation/violation results and access.
5. Report semantics, tests, associations, threshold rationale, owner and unresolved runtime checks.

### Validation

- Signature/language/return type are valid DMF constructs, not generic SQL/Python UDF syntax.
- Metric grain/units/scale and NULL/empty/zero/reference-duplicate behavior match the documented business rule.
- Named expectations evaluate real VALUE with valid operators and no table/UDF subqueries; positive and boundary tests agree.
- Representative performance and actual associations/result visibility are checked separately from syntax; production changes scoped and reversible.
- Output includes definition, business rationale, expected/observed values, schedule/owner and gaps; no invented execution success.

## References

- [DMF SQL language, TABLE signature, NUMBER type, and restrictions](https://docs.snowflake.com/en/sql-reference/sql/create-data-metric-function)
- [Custom metrics](https://docs.snowflake.com/en/user-guide/data-quality-custom-dmfs)
- [Direct calls and associations](https://docs.snowflake.com/en/user-guide/data-quality-working)
- [Named expectations](https://docs.snowflake.com/en/user-guide/data-quality-expectations)
- [Privilege and execution context](https://docs.snowflake.com/en/user-guide/data-quality-access-control)
