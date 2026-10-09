---
schema_version: v4.0
rule_version: v5.0.0
description: Current Snowsight monitoring navigation and feature-specific Cortex tracing, evaluations, and usage attribution.
last_updated: 2026-10-07
keywords:
  - kw:snowsight monitoring interfaces
  - kw:cortex ai cost attribution
  - kw:traces and logs ui
  - kw:llm evaluation workflows
  - kw:distributed tracing ai applications
  - kw:query history latency
token_budget: ~1150
context_tier: Low
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
  optional:
    - 111c-snowflake-observability-monitoring.md  # Monitoring queries and analysis
---
# Snowflake Observability: Snowsight and AI Observability

## Scope

**What This Rule Covers:**
UI evidence/navigation, query/load/task/refresh diagnostics, Cortex feature-specific trace/usage sources, evaluations and safe attribution.

**When to Load This Rule:**
When guiding Snowsight monitoring or reviewing Cortex request traces, evaluations and costs.

## Contract

### Inputs and Prerequisites

- Actual UI/surface/product, account role/capabilities, monitored object/request, time window and desired diagnosis/evaluation.
- Authorized trace/usage access, privacy constraints, current schema/docs, and separate approval for new calls/evaluations/configuration.

### Mandatory

- Provide concrete current navigation and relevant filters/object/request identifiers rather than vague check logs. Verify paths in current UI/docs and disclose inaccessible/unverified UI; menu labels and privileges evolve.
- Common monitoring surfaces include Traces & Logs, Query History/Profile, Copy/Task History and dynamic-table Refresh History. Match interface to emitted events versus actual operation history; do not equate UI Query History with delayed Account Usage automatically.
- Explain source-specific freshness/retention and role visibility. No fixed universal 45-minute UI delay or guaranteed sub-minute telemetry; empty/inaccessible dashboards do not prove no activity.
- Choose Cortex sources per feature: Agents/shared AI traces, direct Analyst-specific request logs, Search enabled request logging, built-in AI function and REST usage histories. They do not all write identical records to one handler event table.
- Current shared AI trace storage is SNOWFLAKE.LOCAL.AI_OBSERVABILITY_EVENTS; direct Analyst uses CORTEX_ANALYST_REQUESTS_RAW. Inspect supported functions/roles and account availability before queries; do not presume handler TRACE schema is interchangeable.
- Base spend reports on feature-specific usage views, not best-effort trace delivery. Built-in AI functions/REST do not universally write event traces; missing trace tokens must not become zero spend.
- Attribute using actual request/model/feature/application IDs and supported usage fields. Deduplicate joins at correct grain and reconcile totals; dedicated warehouses do not capture every Cortex service cost.
- Use current model/account pricing and credit/currency units; no universal token * 0.0001 USD formula or dated unsupported rate table. Label estimates and unavailable costs explicitly.
- Trace custom AI applications through supported current instrumentation (such as configured TruLens) when in scope; inspect exact APIs. Do not invent telemetry.create_span or interpolate user prompts into SQL; bind approved values separately from identifiers.
- Preserve safe phase/context attributes and actual success/error outcomes without logging confidential prompt/result bodies by default. External agents/trace ingestion and cross-region routing need explicit data-handling authorization.
- Evaluation requires reviewed synthetic/authorized datasets, expected answers/rubric, exact model/prompt/tool versions, and output/safety review. Automatic traces or an LLM judge score alone do not prove correctness.
- Retain each attempt, failure, interruption and unpaired/unavailable outcome; never relabel failed requests as passes or silently retry/substitute benchmark identities. Distinguish evaluation from production request monitoring.
- Configure budgets/alerts/integrations and new workloads only with explicit authorization; observation does not authorize grants, logging changes, paid calls, external notifications or runtime deployment.

### Execution Steps

1. Identify actual product/interface/request and permitted data sources, roles, time and privacy boundaries.
2. Give verified navigation/filters and prepare source-specific schema-grounded diagnostics/attribution.
3. Inspect authorized existing UI/query evidence and reconcile trace/activity/usage completeness without generating new workloads.
4. If evaluations/instrumentation are requested and approved, run the supported version-bound workflow and review outputs independently.
5. Report exact evidence, costs/quality limits, unavailable interfaces and scoped next actions without implicit configuration changes.

### Validation

- Current navigation/access and correct feature-specific source identified; no generalized event-table or UI latency claim.
- Tokens/credits/currency and attribution grounded in usage evidence, trace gaps disclosed rather than counted zero.
- Instrumentation/API/SQL bindings supported, sensitive content protected and evaluation failures retained.
- Actual output/quality evidence distinguished from trace success; paid calls/configurations separately approved.
- Deliver paths/filters/queries or evaluation design with precise tested/unverified outcomes.

## References

- [AI observability by feature](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- [Traces and telemetry levels](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels)
- [QUERY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [Cortex AI function usage](https://docs.snowflake.com/en/sql-reference/account-usage/cortex_ai_functions_usage_history)
- `111c-snowflake-observability-monitoring.md` for bounded monitoring/alert queries.
