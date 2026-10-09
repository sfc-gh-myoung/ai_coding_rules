---
schema_version: v4.0
rule_version: v5.0.0
description: Schema-grounded monitoring sources, complete outcome accounting, governed alerting and actual telemetry cost analysis.
last_updated: 2026-10-07
keywords:
  - kw:ACCOUNT_USAGE views
  - kw:telemetry cost optimization
  - kw:query history monitoring
  - kw:real-time vs historical latency
  - kw:Snowsight operational dashboards
  - kw:cortex token tracking
token_budget: ~1200
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 111-snowflake-observability-core.md  # Telemetry configuration and event tables
  optional:
    - 111a-snowflake-observability-logging.md  # Logging best practices
    - 111b-snowflake-observability-tracing.md  # Distributed tracing and metrics
---
# Snowflake Observability: Monitoring and Analysis

## Scope

**What This Rule Covers:**
Monitoring-query source selection, history/telemetry completeness, errors/performance/freshness, alert semantics, cost and privacy.

**When to Load This Rule:**
When designing dashboards, operational analysis, incident checks or telemetry-volume/cost controls.

## Contract

### Inputs and Prerequisites

- Actual workload/incident, expected outcomes, monitored object scope, time zone/window, SLA and permitted sources.
- View/event schema and privileges, current destination/levels, observed/documented latency, retention, alert ownership and notification approval.

### Mandatory

- Select data by purpose and freshness, not a universal historical-versus-real-time dichotomy. Account Usage latency/retention varies per view; information-schema history can be more current with different limits. UI Query History is not necessarily the same delayed Account Usage view.
- Event tables contain emitted/supported telemetry, not complete replacement query history. No invented ACCOUNT_USAGE.EVENT_TABLE or execution_status attribute presumed on every event.
- Inspect actual column names/types/status enums before queries. QUERY_HISTORY execution_time is in documented units, not an invented execution_time_ms; distinguish failed/canceled/running results with actual schema semantics.
- Use bounded time/object/type filters and needed projection; limits/pagination may truncate source evidence. Report earliest/latest timestamps, source delay and exclusions before declaring no errors or complete activity.
- Correlate query/task/load/event identities without fanout; preserve event versus operation grain. Summarize failures, successes, pending/blocked/unavailable results separately and protect division by zero/NULLs in rates.
- Use actual RECORD severity, VALUE messages and TRACE/timestamp span fields. Do not invent flat BODY/severity/duration columns or ARRAY_AGG LIMIT syntax; bounded safe examples need supported SQL.
- Profile slow/error/queue patterns and correlate traces to query execution, not generic fixed thresholds. A timestamp filter may help pruning but does not guarantee no full scan.
- Alert conditions define approved thresholds, windows, late arrivals, deduplication/cooldown and escalation. Creating/resuming alerts, integrations and email/webhook sends requires separate authorization and verified recipients/host scope.
- Test alert positive/negative/late/empty-source cases in approved scope; source delay can mask incidents. Empty delayed data is not a pass or proof there was no failure.
- Measure actual telemetry/storage/service usage with applicable metering views. Character lengths and assumed 1KB/record are not compressed physical storage or invoice evidence; Time Travel retention is not active-row TTL.
- Choose scoped collection/sampling/retention strategies from workload, privacy, signal and budget; no universal 10x DEBUG cost, million-span cutoff or accountwide logging changes.
- Cortex observability differs by product. Use actual feature-specific usage views for tokens/credits and supported trace schemas; built-in AI functions do not universally emit cortex.tokens span attributes.
- Restrict telemetry access and sensitive projection using supported views/policies; prevent sensitive emission first. Do not apply guessed policy syntax to invented body columns or grant broad admin exemptions.
- New monitoring views/procedures, configuration changes, grants and lifecycle/export operations are mutations. Prepare read-only diagnostics first and retain uncertain/failure evidence before approved remediation.

### Execution Steps

1. Inspect sources/schema/config and establish time/freshness/completeness/role boundaries for the requested analysis.
2. Prepare bounded correctly grained monitoring queries and source-specific error/performance/freshness definitions.
3. Validate expected/edge cases locally where possible; execute account diagnostics only under approved scope.
4. Design/test alerts and cost controls separately with explicit mutation/notification authority.
5. Report actual evidence, gaps and owners; preserve failed/late outcomes rather than masking them with success summaries.

### Validation

- Actual sources/fields/units and freshness documented, no assumed event-table history completeness.
- Grain/correlation/time filters and NULL-safe rates correct; no pending/missing events counted as passes.
- Alerts tested and authorized, recipient/export scope verified without arbitrary external data transmission.
- Cost/volume/retention claims measured or explicitly estimates, privacy and least privilege maintained.
- Deliver queries/dashboards/design with exact results and missing verification; no unexecuted runtime/alert pass.

## References

- [QUERY_HISTORY fields/latency](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [Event-table columns](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-columns)
- [Telemetry collection costs](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-billing)
- [AI observability sources and billing](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- `111d-snowflake-observability-snowsight.md` for UI/AI-specific guidance.
