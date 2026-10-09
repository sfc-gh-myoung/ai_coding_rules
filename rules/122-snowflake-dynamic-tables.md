---
schema_version: v4.0
rule_version: v5.1.0
description: "Dynamic table refresh/lag design, supported query grounding, safe pipeline evolution, measured freshness, and cost diagnosis."
last_updated: 2026-10-08
keywords:
  - kw:dynamic table
  - kw:refresh mode
  - kw:target lag
  - kw:incremental refresh
  - kw:downstream dependencies
  - kw:modular pipeline chaining
token_budget: ~1650
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 104-snowflake-streams-tasks.md  # Incremental pipelines and CDC
  optional:
    - 105-snowflake-cost-governance.md  # Cost optimization
    - 103-snowflake-performance-tuning.md  # Query optimization
---
# Snowflake Dynamic Tables Best Practices

## Scope

**What This Rule Covers:**
Declarative materialization versus alternative pipelines, refresh/query compatibility, root-relative lag, DAG scheduling, evolution/recovery, monitoring, and costs.

**When to Load This Rule:**
When creating/changing dynamic tables, evaluating materialization or troubleshooting refreshes. Read `103-snowflake-performance-tuning.md` for profiling and `105-snowflake-cost-governance.md` for cost review.

## Contract

### Inputs and Prerequisites

- Actual source schemas/query grain/keys, base-table change pattern, existing dynamic-table graph/settings/grants, freshness/latency requirements, and cost baseline.
- Creation/source SELECT/warehouse and owner-role refresh privileges; current account feature/query support and authorized DDL/refresh/testing scope.
- Approved definition/target lag/mode/initialization/warehouse choice, retention/recovery requirements, and existing consumer dependencies.

### Mandatory

- Compare dynamic tables with views/materialized views, CTAS, and Streams/Tasks from workload requirements. Declarative supported transformations fit; strict sub-minute freshness or fixed refresh timing needs another justified mechanism, not a blanket Streams/Tasks guarantee.
- Inspect current supported-query matrix before choosing mode. CTEs, DISTINCT, many windows, joins, UNION and current-time filters have supported incremental cases; do not claim all force FULL or complex CTEs inherently prevent incremental refresh. Preserve keys, NULLs, cardinality and aggregate grain.
- Declare production refresh mode explicitly as a policy for predictable intent. Current docs describe INCREMENTAL, FULL, AUTO, ADAPTIVE and specialized CUSTOM_INCREMENTAL; verify account support. ADAPTIVE refresh is not an Adaptive warehouse requirement.
- AUTO resolves to INCREMENTAL or FULL at creation, not each refresh, and later incompatibility can fail. Explicit INCREMENTAL/ADAPTIVE requires eligible definitions. ADAPTIVE can reinitialize on expensive change sets and then resume incremental; a five-percent change guideline is not a automatic mode-fallback threshold.
- Favor incremental-compatible/ADAPTIVE where justified, FULL for unsupported/high-churn cases, and custom incrementalization only with an explicit change/correctness contract. A full-refresh upstream can feed incremental downstream only under documented unique-key/frozen-region constraints; inspect actual graph/support.
- TARGET_LAG is desired root-relative staleness, not a fixed interval or guaranteed SLA. Minimum duration is 60 seconds. Monitor actual data timestamp/lag and duration; do not parse arbitrary duration strings as minutes or use last refresh wall time as equivalent data freshness.
- Use DOWNSTREAM on intermediate nodes driven by an actual scheduled downstream dynamic table; a terminal DOWNSTREAM node has no automatic schedule. SQL SELECT consumers do not drive refresh; soft refresh-boundary dependencies don't count for scheduling. Ensure the final node has an explicit duration or deliberate manual controller.
- Use explicit columns/types and modular nodes where they improve observability/reuse/performance; do not split mechanically or assume added tables always lower cost. Understand coordinated snapshot/dependency behavior and refresh boundaries.
- Choose refresh/initialization warehouses from observed profiles/change rates/lag and isolation needs; dedicated compute is optional, not a universal requirement. Assess initialization and reinitialization full-data cost separately.
- Before authorized DDL/manual refresh, use supported EXPLAIN CHANGES to inspect target-specific next action/failure/reinitialization effects. Prediction reflects current state and not every downstream table; it neither applies the change nor guarantees future outcome. If unavailable/unapproved, disclose the gap, not silently mutate.
- Changing definitions/modes or replacing sources can reinitialize/cascade and affect grants/consumers. Inspect exact ALTER versus CREATE OR ALTER/REPLACE capabilities and capture approved rollback/settings; REFRESH_MODE cannot be changed by a guessed ALTER SET clause.
- Diagnose actual scheduling/refresh action/error/reason from supported SHOW/Information Schema functions and refresh history. UPSTREAM_FAILED is a refresh outcome, not automatically a scheduling-state column. Inspect failed upstream before approved correction; no universal automatically recovered downstream promise.
- Resolve configured mode and actual refresh actions separately; Query Profile helps cost/bottlenecks but metadata/history establishes refresh behavior. Use correct dynamic-table graph/history APIs, not invented SYSTEM$DYNAMIC_TABLE_REFRESH_HISTORY or history credit columns.
- Monitor warehouse compute, cloud services, storage, and retention costs using actual metering plus query/refresh correlation without double attribution. Shorter lag can raise costs but actual scheduling/change patterns matter; no per-table exact credits from an unsupported refresh-history column.
- Time Travel follows supported table retention/history semantics; do not invent DATA_TIMESTAMP_OUTPUT_EXPRESSION as a freshness or Time Travel control. Transient conversion/retention changes need recovery/compliance approval. Cloning a schema does not prove every dependency is remapped or refreshed.
- Suspend/resume, manual refresh, scheduler changes, grants/ownership, replacement and drop require approved scope/impact. Inspect uncertain outcomes before retries and verify data/consumer integrity after changes; no broad teardown for repair.

### Execution Steps

1. Read source/query/graph/settings and workload targets; establish actual permissions, support, correctness grain and refresh economics.
2. Select explicit mode, root-relative lag/controller, modular boundaries, initialization/refresh compute and monitoring.
3. Predict authorized changes with EXPLAIN CHANGES where supported; review scope/reinitialization/grant/rollback effects before approved DDL.
4. Inspect actual mode/actions/history and benchmark permitted refreshes; reconcile materialized results with source snapshot and lag/cost targets.
5. Investigate failed/slow upstream nodes first; apply only scoped approved correction and verify downstream/consumer outcomes.

### Validation

- Supported query/refresh mode and source/grant/warehouse compatibility are verified; no blanket window/DISTINCT bans or guessed account capabilities.
- DAG has a real scheduling driver, valid >=60-second durations, and actual freshness meets stated goals or gaps are reported.
- Before/after prediction/history/reinitialization and correctness evidence are distinct; actual row/grain/NULL/aggregate results reconcile.
- Costs, retention/cloning, consumer access and rollback are assessed without unauthorized resource changes.
- Output includes scoped DDL/design, graph/lag/mode rationale, monitoring/refresh IDs and unresolved runtime checks. Static schema success is not live refresh correctness.

## References

- [Dynamic tables](https://docs.snowflake.com/en/user-guide/dynamic-tables/overview)
- [Supported queries](https://docs.snowflake.com/en/user-guide/dynamic-tables/supported-queries)
- [Refresh modes](https://docs.snowflake.com/en/user-guide/dynamic-tables/refresh-modes)
- [Target lag and DOWNSTREAM](https://docs.snowflake.com/en/user-guide/dynamic-tables/target-lag)
- [Predict refresh effects](https://docs.snowflake.com/en/user-guide/dynamic-tables/predict-refresh)
- [Monitoring](https://docs.snowflake.com/en/user-guide/dynamic-tables/monitoring)
- [Modify dynamic tables](https://docs.snowflake.com/en/user-guide/dynamic-tables/modify)
- [Costs](https://docs.snowflake.com/en/user-guide/dynamic-tables/cost)
