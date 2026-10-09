---
schema_version: v4.0
rule_version: v5.0.0
description: Observation-time feature windows, grain-safe aggregates, missing-data policy, ratios and train-serve consistency.
last_updated: 2026-10-07
keywords:
  - kw:feature engineering
  - kw:windowed aggregations
  - kw:RFM features
  - kw:velocity features
  - kw:NULLIF division protection
  - kw:deterministic transformations
token_budget: ~1050
context_tier: Low
depends:
  required:
    - 113-snowflake-feature-store.md  # Feature Store core patterns
---
# Snowflake Feature Store: Feature Engineering Patterns

## Scope

**What This Rule Covers:**
Behavioral/time-window aggregates, recency/frequency/monetary features, safe ratios, deterministic time context and value/refresh tests.

**When to Load This Rule:**
When authoring or reviewing Feature Store transformation logic and ML feature correctness.

## Contract

### Inputs and Prerequisites

- Actual entity/event grain/keys, source fields/types, observation/availability timestamps, units, label horizon and expected feature meanings.
- Registered-view/API support, business-selected windows, NULL/default policy, train/serve contract and approved computation scope.

### Mandatory

- Define output grain and key/time uniqueness before aggregates; deduplicate source events by approved keys, not arbitrary DISTINCT to hide fanout.
- Anchor historical features to explicit observation/cutoff time and data availability. Relative CURRENT_DATE snapshots do not reconstruct historical features automatically; ingestion time is not always the correct prediction cutoff.
- Use deliberate bounded intervals (including upper cutoff) and correct time-zone/type semantics. Test exact boundaries, future events, sparse/no history, late arrivals and ties to prevent leakage.
- Distinct windows need distinct conditional filters/ranges; identical COUNT/SUM expressions over one 30-day WHERE clause do not create 7-day features. Multi-window features are optional evidence-driven signals, not a universal 7/30/90 requirement.
- Recency is time since last eligible past event; frequency counts intended events, monetary aggregates defined currency/precision. Preserve zero-event entities through suitable spine joins and declare missing recency explicitly.
- Ratios protect zero denominators with NULLIF or another supported explicit guard. Decide NULL versus zero/default from business meaning; COALESCE is not automatically correct for missing evidence.
- Velocity ratios across unequal/overlapping windows are fractions of activity, not necessarily acceleration. Define comparable rate baselines and duration normalization before naming trends/acceleration.
- Lag/rolling/cyclical features need ordered unique time semantics and correct window frames. Training-fitted normalization/imputation must not use holdout/future data; no universal scale >100x rule.
- Preserve deterministic fixed-input/time-context outputs and train/serve versions/order/types. Observability timestamps/randomness require explicit purpose and reproducibility; do not ban all timestamp fields or promise distributed seed determinism.
- Verify supported dynamic-table/feature-view transformations and refresh mode; expensive windows/full refresh need actual profile/cost review. Freshness and history quality are separate from syntactic correctness.
- Validate key coverage, counts, ranges, types, NULL rates, units and independent expected values, including empty/negative/zero cases. Nonempty feature views are not proof of valid training inputs.
- Refresh failures require actual history/error/upstream evidence and scoped ownership-approved fixes. Unexpected NULLs can arise from temporal coverage or policy/context, not automatically source freshness.
- Register new reviewed feature versions for logic changes; data computation, registration, refresh changes and alerts require execution authority. Preserve existing consumers and uncertain-state evidence.

### Execution Steps

1. Inspect sources/entity/time contracts and define supported business feature meanings/windows/defaults.
2. Implement correct grain/time-bounded aggregations, ratios and temporal features with fixed observation context.
3. Test synthetic boundary/duplicate/missing/future cases and independent expected values.
4. Under execution approval, compute/register intended versions and inspect actual values/refresh/access/cost evidence.
5. Report feature definitions, exact versions, test outcomes and unresolved leakage/coverage or serving differences.

### Validation

- Correct keys/grain and distinct time windows; no future/holdout leakage or lost zero-history entities.
- Ratio/default/type/unit and trend meanings explicit, independent expected values match edge cases.
- Fixed-input/time outputs and train/serve contract reproducible, actual refresh support/freshness verified where authorized.
- Mutation/version scope preserves consumers; unexecuted account checks remain unverified.
- Deliver reviewed transformation/data contract with verification evidence and limitations.

## References

- [Advanced feature engineering](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/advanced-feature-engineering)
- [Feature-view lifecycle](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/feature-views)
- [NULLIF](https://docs.snowflake.com/en/sql-reference/functions/nullif)
- `113-snowflake-feature-store.md` for entity/time foundations.
- `113a-snowflake-feature-store-patterns.md` for leakage/version review.
