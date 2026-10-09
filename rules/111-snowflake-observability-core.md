---
schema_version: v4.0
rule_version: v5.0.0
description: Grounded Snowflake telemetry configuration, event-table schemas, freshness, collection costs and controlled retention.
last_updated: 2026-10-07
keywords:
  - kw:event table setup
  - kw:telemetry level hierarchy
  - kw:system views latency
  - kw:DEBUG cost implications
  - kw:SHOW PARAMETERS investigation
  - kw:OpenTelemetry alignment
  - kw:snowpark
token_budget: ~1150
context_tier: High
depends:
  required:
    - 100-snowflake-core.md
---
# Snowflake Observability Core

## Scope

**What This Rule Covers:**
Telemetry destination/level inspection, logs/events/metrics/traces, event schemas, collection verification, freshness, privacy and cost/retention controls.

**When to Load This Rule:**
When configuring or troubleshooting Snowflake observability, event tables, telemetry levels or monitoring-source selection.

## Contract

### Inputs and Prerequisites

- Actual workload/handler, expected telemetry type, time/freshness requirements, permitted evidence sources, and current configuration/schema.
- Authorized destination/view access, warehouse/query scope, relevant telemetry-level privileges, privacy/cost/recovery policy and mutation approval.

### Mandatory

- Inspect effective EVENT_TABLE and logging/tracing/metric parameters before recommending changes, including database/object/session overrides. Do not infer missing collection from account parameter alone.
- Verify actual active/default/custom table and access. Current default is SNOWFLAKE.TELEMETRY.EVENTS with EVENTS_VIEW; do not query invented ACCOUNT_USAGE.EVENT_TABLE or assume DEFAULT_EVENT_TABLE is the universal object name.
- Event destination precedence and telemetry level precedence differ. Check account/database destination and session Account/User/Session versus object Account/Database/Schema/Object levels; most verbose effective level wins between the latter hierarchies as documented.
- Distinguish LOG_LEVEL log messages, LOG_EVENT_LEVEL system/log events, TRACE_LEVEL and METRIC_LEVEL; supported scopes differ. Verify function/procedure signatures and privileges rather than apply ALTER to unsupported Streamlit objects.
- Configure minimal useful collection for workload needs. Temporary scoped verbose debugging can be appropriate with approval, time bound and restoration; no universal WARN-only production ban or invented 10x cost multiplier.
- Select source by purpose and documented/observed freshness: account usage and information-schema functions differ per object/view in latency/retention; event tables are not guaranteed sub-minute complete query histories.
- Inspect actual predefined columns and record-type structure. Severity/span name are in RECORD, IDs in TRACE, message/value in VALUE, and context in RESOURCE_ATTRIBUTES/RECORD_ATTRIBUTES as applicable; do not invent flat SEVERITY_TEXT/TRACE_ID/DURATION_MS columns.
- Use explicit needed projections and bounded time/object/type filters. Derive span duration from supported timestamps with correct units and semantics; distinguish missing attributes from actual zero values.
- Verify emission, threshold, destination, access, and ingestion delay using authorized representative events. A table row count does not prove a particular handler's logs arrived, and successful emission does not guarantee complete collection.
- Collection, logging and storage costs depend on actual service/volume settings. Monitor real usage and signal/noise; no fixed dollar-per-TB or blanket latency/volume guarantees.
- DATA_RETENTION_TIME_IN_DAYS is Time Travel retention, not automatic deletion of active event rows by age. Plan separate approved lifecycle/purge/archive controls with legal/recovery requirements; do not claim it bounds active storage automatically.
- Never expose secrets, personal data, model prompts or sensitive SQL through logs/trace attributes. Enabling SQL text capture or exporting telemetry requires explicit privacy/host authorization; accountwide debug is not a default diagnostic action.
- Preserve existing destinations/levels and unrelated telemetry. New table creation, routing changes, grants, retention/deletion, alerts and external integrations require approved ownership/scope and restoration plan.

### Execution Steps

1. Inspect actual source/destination schemas and effective telemetry settings/privileges using authorized reads.
2. Match monitoring needs to data type/freshness and propose minimal scoped collection/querying with privacy/cost/lifecycle controls.
3. Validate configuration/query syntax locally where possible without account mutation; disclose missing object evidence.
4. Under execution/configuration approval, apply scoped changes and exercise representative emissions, then verify correlated collection after appropriate delay.
5. Record configuration/event/query outcomes, costs/gaps and approved restoration; do not clear unrelated evidence to resolve a failure.

### Validation

- Active destination and effective thresholds verified, record schema/type filters correct and actual events correlated to workload.
- Freshness/retention caveats explicit; no invented account view or real-time guarantee.
- Privacy, least privilege and cost reviewed; Time Travel not mistaken for active-row TTL.
- Scoped debugging restored according to approval and failures/missing data retained honestly.
- Deliver configuration/query design and actual evidence; unexecuted emission/collection/runtime checks remain unverified.

## References

- [Event table setup/default destination](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up)
- [Telemetry levels and hierarchy](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels)
- [Event table columns](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-columns)
- [Collection costs](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-billing)
- `111a-snowflake-observability-logging.md`, `111b-snowflake-observability-tracing.md` and `111c-snowflake-observability-monitoring.md` for focused workflows.
