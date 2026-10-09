---
schema_version: v4.0
rule_version: v5.1.0
description: Agent-specific traces/usage, truthful health and output evaluation, bounded costs and evidence-based recovery.
last_updated: 2026-10-08
keywords:
  - kw:cortex agent observability
  - kw:agent cost attribution
  - kw:AI Observability tracing
  - kw:agent health checks
  - kw:agent troubleshooting runbook
  - kw:dedicated agent warehouse
token_budget: ~1150
context_tier: Low
depends:
  required:
    - 115-snowflake-cortex-agents-core.md  # Core agent creation
  optional:
    - 105-snowflake-cost-governance.md  # Cost monitoring and governance
---
# Snowflake Cortex Agents: Observability and Cost Management

## Scope

**What This Rule Covers:**
Agent request/tool traces, usage attribution, quality/health evaluation, budgets and scoped error diagnostics.

**When to Load This Rule:**
When monitoring Agent costs/latency/quality, preparing health checks or investigating failures.

## Contract

### Inputs and Prerequisites

- Actual agent/spec/model/tool versions, request identities, expected behavior, execution context and permitted trace/usage sources.
- Approved MONITOR/usage access, latency/cost/quality targets, privacy policy and separate call/configuration/alert authority.

### Mandatory

- Use current Agent observability sources and supported retrieval functions/schema. Shared AI traces use SNOWFLAKE.LOCAL.AI_OBSERVABILITY_EVENTS, not assumed handler DEFAULT_EVENT_TABLE fields; inspect actual records/role access.
- Agent MONITOR controls trace/thread visibility as documented; SELECT/USAGE alone does not grant all monitoring. Keep sensitive prompts/results redacted and avoid unapproved trace export.
- Correlate request/thread/turn/tool IDs with actual versions and role context. Do not invent CORTEX_AGENT_HISTORY or use query-text filtering as complete Agent history.
- Use CORTEX_AGENT_USAGE_HISTORY and relevant tool/warehouse/service usage for costs; best-effort traces can undercount consumption. Distinguish tokens/credits/currency, grain and source delay before attributing totals.
- Dedicated warehouses can isolate applicable SQL compute when justified, but are not mandatory per agent or complete inference-cost attribution. Size/lifecycle/generation choices require actual workload/capability evidence.
- Configure supported orchestration token/time budgets and input/result limits deliberately; character counts are not tokens, and resource monitors do not provide universal per-request credit caps.
- Health checks separate reachability, tool execution, answer correctness, permission safety and cost. Nonempty response is not golden-answer correctness; source/time/model changes need explicit expectation review.
- New scheduled golden-question calls spend credits and can run tools. Require approved dataset/tools/cadence/cost scope and notification recipients rather than create/resume a task by default.
- Retain each evaluation identity/outcome and independently review actual outputs. Denied unauthorized calls remain failures, absent/unpaired/interrupted evidence is not success, and no benchmark retries/substitution.
- Calculate success rates over all applicable attempts including failures/interruptions; latency percentiles need declared sample/population and handle no successful timings without indexing errors. No fixed 95%/5-second/2x baseline policy assumed.
- Diagnose empty/missing/permission/tool-routing outputs from actual spec/resource/default role/warehouse, filters/source/schema/availability and inaccessible-tool warnings. Do not weaken filters/grants or infer one root cause from an error alone.
- Verify supported semantic query/service contracts in component diagnostics; no fake builtin function grants, outdated model calls or VIEW versus SEMANTIC VIEW confusion.
- Approved flagging comes from business policy/data definitions; presentation/routing defects require tested instruction fixes, not universal removal of semantic flags.
- Changes to models/budgets, warehouses/grants, tracing, tasks, alerts or agent versions are authorized mutations. Inspect uncertain current state before recovery and preserve consumers/known-good versions.

### Execution Steps

1. Inspect agent/request/tool identities and current trace/usage schemas, visibility and freshness.
2. Prepare bounded correlated quality/performance/cost summaries with explicit missing/failed outcomes.
3. Define health/evaluation expectations and budgeted runtime scope; exercise calls only when separately authorized.
4. Investigate demonstrated failures with source/tool/default-context evidence and propose minimal scoped remediation.
5. Verify approved fixes and report exact outcomes, unknown costs/trace gaps and recovery/monitoring ownership.

### Validation

- Correct Agent-specific schema/identity and usage attribution, no trace-as-invoice or invented history fields.
- Health/output/permission tests distinct, all applicable outcomes accounted and latency populations honest.
- Budget/control claims supported, dedicated compute justified and scheduled calls/notifications separately approved.
- Diagnoses grounded and scoped recovery preserves grants/resources/versions; uncalled/unobserved runtime remains unverified.
- Deliver monitoring/evaluation/runbook changes and actual evidence/limitations.

## References

- [AI observability sources/billing](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- [Agent monitoring](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-monitor)
- [Agent usage history](https://docs.snowflake.com/en/sql-reference/account-usage/cortex_agent_usage_history)
- [Default-role and monitoring privileges](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup)
- `115c-snowflake-cortex-agents-testing.md` for frozen evaluation/RBAC.
