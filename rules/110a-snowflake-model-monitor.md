---
schema_version: v4.0
rule_version: v5.0.0
description: Schema-grounded model monitoring with correct function/version binding, baseline semantics, and scoped lifecycle recovery.
last_updated: 2026-10-07
keywords:
  - kw:MODEL MONITOR
  - kw:enable_monitoring
  - kw:drift detection
  - kw:baseline scoring schema
  - kw:ml observability
  - kw:monitor refresh interval
token_budget: ~1200
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 110-snowflake-model-registry.md  # Model Registry core patterns
---
# Snowflake MODEL MONITOR: ML Observability

## Scope

**What This Rule Covers:**
Model-version monitoring of stored inference data, drift/performance requirements, schema/privilege binding, refresh diagnostics and safe recovery.

**When to Load This Rule:**
When designing or troubleshooting MODEL MONITOR, scoring/baseline datasets, or model quality monitoring.

## Contract

### Inputs and Prerequisites

- Actual model/version/function/task, supported monitor type, current SDK/SQL capabilities and representative scoring/baseline schema/data.
- Approved monitor/compute scope, refresh/window requirements, expected metrics, labels and owner response policy.
- Verify CREATE MODEL MONITOR on schema, model USAGE, source SELECT, warehouse USAGE and parent access for the chosen workflow; inspect current monitor privileges for lifecycle changes.

### Mandatory

- Inspect registered model/version and actual grants/source before diagnosing not-found/not-authorized errors. Do not claim every failure is missing enable_monitoring or require DROP/re-registration; current SQL documentation does not establish that destructive prerequisite.
- Bind model, version and function explicitly using supported identifiers and literal syntax; version/function names are quoted string values in current CREATE syntax. Fully qualify cross-schema objects; USE session context is not a universal substitute for a correct model FQN.
- Distinguish model-version monitors from gateway monitors and verify feature/task/output support. Do not transfer a VERSION/SOURCE syntax contract to a gateway workflow without its documented GATEWAY/ground-truth requirements.
- Stored source contains relevant input features, predictions, TIMESTAMP_NTZ observation time, and optional actuals/IDs. Column arrays contain string names; verify supported classification/regression types and no conflicting reuse across parameters.
- At least one supported prediction class/score column is needed for a version monitor. Accuracy/performance metrics need appropriate actual labels; absence of ground truth must not become an accuracy pass.
- Baseline is optional but required for drift; it represents a reviewed reference distribution and is snapshotted into the monitor. Align relevant features/types/semantics with source; do not assert every metadata column must universally match exactly or create a guessed unsupported view workaround.
- Validate keys, timestamps, labels, class/score mapping and allowed values, including NULL/NaN/infinite/out-of-range data. Delayed ground truth and late data need explicit reconciliation, not an append-only assertion that prevents updates.
- Choose supported refresh interval and aggregation window based on data/SLA/cost (version-monitor windows use days). Review current feature/segment/monitor limits and account capabilities rather than copy stale universal counts.
- Inspect SHOW/DESCRIBE status/errors and documented model-monitor metric functions for actual refresh/metric evidence. Do not invent INFORMATION_SCHEMA.MODEL_MONITOR_REFRESH_HISTORY or treat DESCRIBE as the metric result itself.
- Missing metrics can reflect no data, timing, source/grant changes, unsupported values or suspended refreshes. Inspect aggregation status/last errors and source progress before approved resume; no automatic warehouse/privilege escalation.
- Basic monitored model/source/baseline configuration is not freely mutable. Adding a missing baseline may require reviewed recreation; preserve dependencies/evidence and require explicit ownership/deletion approval rather than promise ALTER can attach it.
- Monitor warehouse/storage/dashboard costs and privacy. Configure alerts/remediation/retraining as approved workflows; drift indicates distribution change, not guaranteed accuracy degradation or automatic permission to retrain/deploy.
- CREATE/ALTER/SUSPEND/RESUME/DROP, grants and data population are mutations. Separate design, inspection, and approved execution; preserve existing monitors and known-good state on uncertain outcomes.

### Execution Steps

1. Inspect model/version/function, source/baseline schemas/data and current monitor state/privileges.
2. Design supported column/task/time bindings, baseline/label expectations, refresh/window and owner response.
3. Prepare scoped definition and data-quality tests without replacing existing models or creating resources implicitly.
4. Under execution approval, create/update the intended monitor and inspect actual status plus correlated metric results after refresh.
5. Diagnose failures from actual evidence and apply approved scoped recovery; report unavailable accuracy/drift separately.

### Validation

- Actual model/version/function and supported task/schema bindings verified, labels and baseline sufficient for claimed metrics.
- Data types/values/time/IDs align; no fabricated monitoring flag/drop requirement or unknown history function.
- Refresh/status/metrics and cost/access behavior observed where authorized; no empty-result correctness claim.
- Recovery/recreation scope and immutable configuration limits explicit, existing model consumers preserved.
- Deliver definition/data contract/runbook and exact tested/unverified outcomes; no unexecuted cloud checks counted as passes.

## References

- [CREATE MODEL MONITOR](https://docs.snowflake.com/en/sql-reference/sql/create-model-monitor)
- [ML Observability workflow and metric functions](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-observability)
- [ALTER MODEL MONITOR](https://docs.snowflake.com/en/sql-reference/sql/alter-model-monitor)
- `110-snowflake-model-registry.md` for registration and serving contracts.
- `110b-snowflake-model-registry-operations.md` for cost/promotion governance.
