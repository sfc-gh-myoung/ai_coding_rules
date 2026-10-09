---
schema_version: v4.0
rule_version: v5.0.0
description: Evidence-based Snowflake query profiling, pruning, warehouse sizing, and cost-aware optimization.
last_updated: 2026-10-07
keywords:
- kw:Query Profile analysis
- kw:partition pruning optimization
- kw:spillage detection
- kw:clustering key justification
- kw:cluster-key-tuning
- kw:slow query investigation
- kw:snowsight
token_budget: ~1000
context_tier: High
depends:
  required:
  - 000-global-core.md
  - 100-snowflake-core.md
---
# Snowflake Performance Tuning

## Scope

**What This Rule Covers:**
Measured query diagnosis, correctness-preserving SQL improvements, pruning, spillage, concurrency, warehouse sizing, and clustering tradeoffs.

**When to Load This Rule:**
When investigating slow Snowflake queries or proposing performance and warehouse-cost changes.

## Contract

### Inputs and Prerequisites

- Query text/ID, intended result grain, workload SLA, data volumes, warehouse configuration, and representative parameters.
- Authorized access to relevant history/profile evidence and explicit approval for benchmarks or configuration changes. Verify object-specific privileges; do not require ACCOUNTADMIN for all diagnosis.

### Mandatory

- Inspect the existing Query Profile before selecting a fix. Query History supplies timing and workload context, not the operator-level profile itself. If the profile is unavailable, label conclusions provisional and request the missing evidence rather than claim a diagnosis.
- Separate compilation, execution, queueing, provisioning, and result-transfer costs. Inspect expensive operators, input/output row counts, scanned/total partitions, bytes scanned, local/remote spill, and external-call latency where present.
- Evaluate pruning against filter selectivity and table organization; full scans can be appropriate. DATE/CAST expressions do not universally disable pruning. Verify actual behavior and preserve timestamp type/time-zone semantics when rewriting ranges.
- Preserve join keys, cardinality, NULL semantics, duplicate handling, and output grain. Select needed columns; remove DISTINCT or replace UNION with UNION ALL only when result semantics permit.
- Investigate exploding joins, skew, and unnecessary intermediate data before increasing compute. Batching, prefiltering, or aggregation must preserve results; salting is not a default remedy.
- Right-size from measured execution/spill and concurrency evidence. Distinguish scaling up for a query from scaling out for concurrency; multi-cluster availability depends on account capabilities. No fixed queries-per-cluster or universal concurrency threshold.
- Recommend clustering only for repeated selective workloads with poor pruning and an assessed maintenance/storage cost. Do not apply speculative keys or automatic clustering changes without authorization.
- Match benchmark data, parameters, warehouse size/type, cache conditions, and competing load; disclose differences. Compare repeated representative runs and cost as well as latency, not a single favorable run.
- Treat resizing, clustering, scheduling, and auto-suspend/resume changes as mutations. Inspect current state and ownership, assess downstream effects, and obtain approval; a diagnostic checklist is not execution permission.

### Execution Steps

1. Capture query identity, required results, workload targets, current configuration, and available evidence without exposing confidential query data externally.
2. Locate profile bottlenecks and history patterns; inspect table/warehouse metadata through permitted reads only.
3. Propose the smallest targeted SQL or configuration change with expected benefit, correctness checks, cost, and recovery plan.
4. Under execution approval, benchmark baseline and candidate in a controlled scope; record query IDs, cache/load conditions, elapsed/execution/queue times, pruning, and spill.
5. Check result equivalence, repeatability, SLA, and cost; retain failed attempts and revert only owned approved changes when warranted.

### Validation

- Actual before/after evidence supports the stated bottleneck and improvement; no guaranteed speedup, universal scanned-partition ratio, or invented SLA.
- Result rows, values, grain, duplicates, and NULL behavior remain correct for representative and boundary cases.
- Pruning/spill changes are reported where relevant, not mandatory improvements for unrelated bottlenecks.
- Warehouse sizing, scaling, and suspension settings meet the workload's measured latency/cost and recovery needs.
- Report SQL recommendations, profile metrics/query IDs, configuration proposals, and unresolved risks. Unexecuted benchmarks and unavailable profiles remain explicitly unverified.

## References

- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile)
- [Micro-partitions and pruning](https://docs.snowflake.com/en/user-guide/tables-micro-partitions)
- [Clustering keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- [Warehouse considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
- `119-snowflake-warehouse-management.md` for warehouse-specific planning.
