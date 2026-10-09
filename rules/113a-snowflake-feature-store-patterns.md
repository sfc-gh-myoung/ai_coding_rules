---
schema_version: v4.0
rule_version: v5.0.0
description: Feature-store temporal leakage, reproducibility, version safety, and measured refresh-cost review.
last_updated: 2026-10-07
keywords:
  - kw:ASOF JOIN
  - kw:feature view versioning
  - kw:deterministic transformations
  - kw:dynamic table refresh costs
  - kw:training data leakage
  - kw:train serve skew
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 113-snowflake-feature-store.md  # Feature Store core patterns
---
# Snowflake Feature Store: Correctness and Operational Review

## Scope

**What This Rule Covers:**
Temporal leakage and join correctness, deterministic/reproducible feature definitions, version compatibility, refresh costs and governance gaps.

**When to Load This Rule:**
When auditing feature datasets/views, train-serve skew, feature changes or refresh costs.

## Contract

### Inputs and Prerequisites

- Existing registered entities/view versions, transformation/source data, spine/labels, serving consumers and actual APIs.
- Time/availability/grain rules, expected values, refresh/compute cost evidence and approved review/remediation scope.

### Mandatory

- Trace feature values to inputs available at observation time. Current/latest keyed joins are unsafe for changing historical features, but static correct keyed joins need not always use ASOF.
- Use supported temporal retrieval/ASOF semantics where required and test key grouping, latest-before boundary, equal-time ties, missing matches and late/retroactive data. ASOF does not repair features themselves computed from future information.
- Pin registered feature versions and dataset/model identities; new logic/columns requires a new reviewed version. No same-version overwrite of consumers or undocumented @fv/decorator/generate_training_set recipes.
- Preserve deterministic business calculations from fixed inputs/time context. Relative-time features use explicit observation/cutoff semantics; current-time ingestion metadata can be valid but must not silently change training feature meaning.
- Randomness must have a justified purpose, reproducible configuration and train/serve semantics. Do not promise a seed makes every distributed operation deterministic or categorically ban timestamps needed for observability.
- Check feature order/types/units, preprocessing, NULL/default behavior and point-in-time coverage between training and inference. Offline/online timestamp/session context can differ and requires specific validation.
- Inspect actual refresh mode, query support, source cadence and lag versus SLA. Aggressive refresh can cost more, but no universal hour/default warehouse or guaranteed dollar-per-day assertion.
- Use documented refresh/history fields and separate applicable metering for cost attribution; do not invent credits_used on every dynamic-table history function or equate target lag with an exact schedule.
- Changes to warehouse/frequency/tracking/materialization/alerts need approved scope and measured tradeoffs. No automatic shrink, clustering or scheduled account task merely because a checklist names cost monitoring.
- Apply approved governance metadata/access and verify actual consumer policies; registration/lineage alone does not prove security or temporal correctness.
- Preserve existing feature versions/source objects and failures. Propose scoped fixes/new versions, test independently, and inspect uncertain state before recovery rather than deleting/replacing shared resources.

### Execution Steps

1. Inspect registered definitions and trace source/time/key contracts to actual training/serving consumption.
2. Review leakage, duplicate/tie/NULL behavior, deterministic transformation and version changes with expected-result tests.
3. Compare actual refresh/lag/cost evidence to workload requirements and document attribution limits.
4. Prepare minimal corrected definitions or new versions and test locally/synthetically first.
5. Execute account remediation only when authorized; verify actual values/consumers/security and retain failed outcomes.

### Validation

- Time-available features, grain/tie/key coverage and train/serve contracts verified; no ASOF-as-universal-guarantee.
- Versions/data/config reproducible, metadata honest and no unsupported API snippets.
- Refresh/cost recommendations grounded in actual fields/usage and approved SLA, not fixed thresholds.
- Existing consumers and ownership protected, local tests separate from unexecuted account checks.
- Deliver findings, scoped changes, expected-result evidence and unresolved temporal/cost/security gaps.

## References

- [Feature Store](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview)
- [Feature-view lifecycle](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/feature-views)
- [ASOF JOIN](https://docs.snowflake.com/en/sql-reference/constructs/asof-join)
- `113-snowflake-feature-store.md` for entity/API foundations.
- `105-snowflake-cost-governance.md` for attribution/control limits.
