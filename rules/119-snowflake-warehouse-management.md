---
schema_version: v4.0
rule_version: v5.0.0
description: Evidence-based warehouse type, generation, sizing, lifecycle, attribution, cost controls, and safe conversion decisions.
last_updated: 2026-10-07
keywords:
- kw:virtual warehouse creation
- kw:warehouse sizing strategy
- kw:auto-suspend configuration
- kw:warehouse type selection
- kw:GEN 2 warehouse
- kw:adaptive warehouse tuning
- kw:warehouse
token_budget: ~1650
context_tier: High
depends:
  required:
  - 103-snowflake-performance-tuning.md
  - 105-snowflake-cost-governance.md
---
# Snowflake Warehouse Management

## Scope

**What This Rule Covers:**
Workload-based warehouse selection, Gen2/Adaptive tradeoffs, sizing/concurrency, lifecycle configuration, tags/monitors, and safe retirement.

**When to Load This Rule:**
When creating/configuring warehouses, evaluating compute fit, converting warehouse types, or reviewing sizing, costs, and lifecycle governance.

## Contract

### Inputs and Prerequisites

- Existing configuration, authorized history/profile evidence, workload mix/SLA, concurrency, memory needs, pricing baseline, and organization naming/tag/monitor policy.
- Exact account edition/region and current feature constraints. Warehouse generation is not account edition; live capability remains unverified without account evidence.
- Object-specific creation/modification/usage/monitor/tag permissions and approved scope. Analysis does not authorize creation, resizing, suspension, conversion, grants, or dropping resources.

### Mandatory

- Inspect current warehouse settings, tags, resource monitors, query/load/metering history, and representative Query Profiles before changes. Separate queueing, provisioning, execution, spill, and idle time; preserve workload isolation and chargeback requirements.
- Choose standard Gen2 for supported general analytical workloads when measured fit favors it, Adaptive for eligible analytical/loading/mixed workloads needing automatic tuning, interactive for eligible low-latency needs, and Snowpark-optimized for supported high-memory single-node work. Do not treat Adaptive as mandatory merely because available.
- Snowpark-optimized warehouses provide CPU/memory resource choices, not GPU warehouses. GPU execution requires a supported GPU compute service, not labeling WAREHOUSE_TYPE='SNOWPARK-OPTIMIZED' as GPU. MEMORY_* constraints belong to the supported Snowpark-optimized type, not a fictitious standard high-memory type.
- For standard warehouses use documented GENERATION='1'/'2' or compatible STANDARD_GEN_* constraints; do not specify conflicting values. Verify current region/size/type support. Gen2 supports through X4LARGE, not X5LARGE/X6LARGE; GENERATION does not apply to Snowpark-optimized memory constraints.
- Select size from measured latency/spill and cost; begin with a justified small candidate, then test representative workloads. Optimize SQL/intermediate results before buying memory. No universal 30-second/80-percent/concurrency cutoff or guaranteed savings applies.
- Scale up to improve an individual query when evidence supports it; scale out with eligible multi-cluster standard warehouses for concurrency. Choose STANDARD/ECONOMY policy and cluster bounds from queue/SLA/spend targets, not fixed five/30-second defaults.
- Set standard warehouse auto-suspend/resume and initially-suspended behavior from workload arrival, cache reuse, cold starts, and billing constraints. Zero/NULL disables automatic suspension; any deliberate always-on exception needs justification. A 30-second setting is not a promise of exact suspension time or billing granularity.
- Adaptive uses automatic per-query allocation and shared account-dedicated compute. MAX_QUERY_PERFORMANCE_LEVEL bounds per-query performance and QUERY_THROUGHPUT_MULTIPLIER bounds aggregate work relative to a computed baseline, not an exact concurrent-query count. Zero allows unbounded throughput; assess spend risk.
- Adaptive has distinct enable/disable controls; standard size/cluster/scaling/QAS/suspend settings do not apply. Current docs describe GA in selected AWS/Azure/GCP regions with Enterprise+; verify account eligibility and limitations, not a stale AWS-only preview list.
- Inspect conversion eligibility and existing settings before ALTER; unsupported Snowpark-optimized/interactive/large-size paths are not automatic fallbacks. During supported online conversion old queries finish on old resources while new work routes to the new type, creating temporary dual-resource cost. Capture previous settings and an approved rollback.
- For bulk updates, inspect the documented function signature/filter semantics and run only an authorized dry-run first. Review exact selected identities and per-resource failures before approved activation. A dry-run or partial success never authorizes widening scope or blindly repeating mutations.
- Preserve organization attribution policy: cost center, workload, environment, owner, and any classification/lifecycle requirements. Verify existing tag identities/allowed values and privileges; do not create GOVERNANCE.TAGS or impose example names without approval. Current tags/names are not necessarily historical attribution.
- Associate production warehouses with policy-required monitors; record coverage exceptions and agreed quotas/notification/suspension effects. Monitors/budgets are not precise hard caps. Do not remove monitors to bypass reached quotas; use current type-specific metering and actual contract/service rates, not static credit tables.
- Prefer scoped ALTER over CREATE OR REPLACE on existing warehouses; review grants/dependents and uncertain outcomes before retries. Document name/purpose, size/type rationale, cost/SLA, owner, and operational review cadence.
- Retirement requires owner approval, consumer inventory, scheduled/infrequent workload review, and sufficient history. Mark lifecycle and disable auto-resume only when approved; zero queries for seven days alone does not authorize DROP.

### Execution Steps

1. Read configuration/policy and permitted usage evidence; establish workload targets, pricing, feature eligibility, identity, and authority.
2. Compare type/generation, size versus concurrency, lifecycle, tags, and monitor choices with measured tradeoffs and rollback scope.
3. Propose exact scoped settings/DDL and impact; apply only authorized changes, keeping unrelated warehouses and grants intact.
4. Inspect effective settings with supported metadata; run representative benchmarks only under execution approval and compare latency, queue/spill, throughput, cost, and correctness.
5. Review subsequent usage, billing/attribution coverage, notification delivery, and lifecycle behavior; retain partial/failed outcomes and report unresolved limits.

### Validation

- Configuration reflects supported type/generation/resource combinations and actual account capability; GPU/edition/preview claims are not inferred.
- Sizing/scaling/lifecycle meet specified workload goals under controlled evidence; estimates and unexecuted benchmarks stay labeled.
- Approved tags/monitor/owner coverage is effective, attribution reconciles, and cost-cap limitations remain explicit.
- Conversions preserve identity/consumer access and have tested or explicitly unverified rollback; bulk selection/failures reviewed individually.
- Output includes scoped configuration, rationale, before/after metrics, costs, monitoring cadence, and permission/runtime gaps. No retirement or mutation occurred outside approval.

## References

- [Warehouse overview](https://docs.snowflake.com/en/user-guide/warehouses-overview)
- [CREATE WAREHOUSE properties and resource constraints](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse)
- [ALTER WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse)
- [Gen2 availability](https://docs.snowflake.com/en/user-guide/warehouses-gen2)
- [Adaptive workload fit, controls, conversion, and metering](https://docs.snowflake.com/en/user-guide/warehouses-adaptive)
- [Snowpark-optimized CPU and memory choices](https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized)
- [Warehouse considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
- [Resource monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
- `123-snowflake-object-tagging.md` for tag policy/permissions; `111-snowflake-observability-core.md` for monitoring when those tasks apply.
