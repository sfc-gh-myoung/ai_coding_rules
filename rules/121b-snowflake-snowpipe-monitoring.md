---
schema_version: v4.0
rule_version: v5.0.0
description: "Source-specific Snowpipe file/streaming progress, row integrity, telemetry, latency, and billing monitoring."
last_updated: 2026-10-07
keywords:
  - kw:PIPE_USAGE_HISTORY
  - kw:Snowpipe credit tracking
  - kw:channel status monitoring
  - kw:COPY_HISTORY Snowpipe
  - kw:cost per GB optimization
  - kw:baseline performance metrics
  - kw:snowpipe
token_budget: ~1600
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 121-snowflake-snowpipe.md  # File-based Snowpipe core concepts
  optional:
    - 121f-snowflake-snowpipe-monitoring-alerts.md  # Alert configuration and cost optimization
    - 121c-snowflake-snowpipe-troubleshooting.md  # Troubleshooting and debugging patterns
    - 105-snowflake-cost-governance.md  # Resource monitors and cost optimization
---
# Snowflake Snowpipe Monitoring and Cost Management

## Scope

**What This Rule Covers:**
File/streaming health and integrity evidence, correctly scoped history sources, progress/latency metrics, billing reconciliation, and baseline-driven alerts.

**When to Load This Rule:**
When monitoring or analyzing Snowpipe costs/performance. Read `121a-snowflake-snowpipe-streaming.md` for channel semantics, `121f-snowflake-snowpipe-monitoring-alerts.md` for alerts, and `121c-snowflake-snowpipe-troubleshooting.md` for diagnosis.

## Contract

### Inputs and Prerequisites

- Exact pipeline identities and architecture, source manifests/checkpoints, expected arrival schedule, workload SLA, reporting window/time zone, and cost policy.
- Authorized history/telemetry access and query compute; verify current view/function schemas, retention, scope, and latency separately.
- Existing dashboards/alert owners, collection destination/settings, and approved monitoring/notification mutation scope.

### Mandatory

- Monitor proactively without waiting for a perfect baseline before detecting failures. Establish representative historical patterns including bursts/idle periods; a fixed one/two-week window is not mandatory. Mark cold-start thresholds provisional.
- For files separate SYSTEM$PIPE_STATUS/event delivery/queue state, COPY_HISTORY per-file load outcomes, and PIPE_USAGE_HISTORY aggregated usage. PIPE_USAGE_HISTORY has bytes/files/credits, not invented row/error/latency columns. COUNT(history buckets) is not files loaded.
- Prefer the current Account Usage PIPE_USAGE_HISTORY view for complete longer-term usage; its Information Schema function is generally deprecated, account-wide, bounded to recent history, and privilege-filtered. Do not assume every Information Schema function is database-only or latency-free.
- Inspect each source's current latency/retention and privileges. COPY_HISTORY function's recent window differs from the account view; missing records can mean latency, inaccessible objects, filters, or old history, not no ingestion. LOAD_HISTORY is not a universal Snowpipe Streaming history table.
- For high-performance streaming use documented SDK channel status/committed tokens, SNOWPIPE_STREAMING_CHANNEL_HISTORY, and event-table telemetry as appropriate. Do not invent ACCOUNT_USAGE.STREAMING_CHANNELS or streaming load_type columns in LOAD_HISTORY.
- Find the active event destination and effective LOG_EVENT_LEVEL; an event table alone does not enable collection. INFO captures progress/latency/lifecycle and errors, ERROR only error events, OFF none. Changes require approval and do not backfill old ingestion.
- Filter streaming telemetry by SCOPE name snow.snowpipe.streaming, RECORD_TYPE=EVENT, actual object attributes, and time. RECORD holds event identity/severity, VALUE event fields. Preserve unknown/missing object attribution for separate investigation rather than silently discarding it.
- Use commit-event row_count/rows_parsed/error_count for accepted/parsed/rejected totals; individual row_error events are not exhaustive totals. Define error-rate denominator and NULL/no-data behavior. Best-effort telemetry is not exact source-to-target reconciliation or a checkpoint authority.
- Use actual latency-event total_latency_ms for server receive-to-commit processing when recorded. It excludes source buffering/network before arrival and can restart on retry. Time since last load/commit measures recency, not ingestion latency or end-to-end visibility.
- Judge stalled channels against expected arrivals and committed/source backlog; inactivity on an idle producer is not a failure. Offset tokens are opaque application markers; latest telemetry timestamp is not maximum source position.
- Reconcile source manifests/checkpoints, target keys/counts/business totals, partial/rejected rows, and visibility independently. Uncompressed_bytes may repeat across channel events for one request; do not sum it as exact bytes/billing.
- Reconcile service-specific consumption and documented billed-byte basis/current rates; distinguish file Snowpipe, high-performance streaming, classic streaming, and monitoring/telemetry costs. Per-file/per-row ratios are analytical measures, not universal billing formulas. Zero loaded bytes with credits may be maintenance, not corruption.
- Guard rate/cost ratios against zero denominators, account for reporting grain and historical identities, and avoid fanout when combining per-file/interval usage. Retain missing usage as unknown, not zero cost.
- Set alerts from agreed SLA/error tolerance and actual baseline, with minimum sample volume, deduplication, cooldowns, severity/owner, and separate no-data detection. No fixed 5%/1% or 15-minute threshold and no automatic warehouse resizing or pipe pause.
- Bound query time/object scope and monitoring cost; isolate heavy monitoring where justified rather than categorically banning all production compute. Scheduled tasks, telemetry changes, alert creation, and external notifications require approval and scoped confidential content.

### Execution Steps

1. Inventory exact pipelines, expected source progress, installed SDK/architecture, accessible histories/telemetry, and source freshness.
2. Select supported progress, row/error, latency, throughput, and billing metrics with explicit grains/units/windows/denominators.
3. Reconcile representative records against sources/targets and measure baseline/collection gaps before claiming dashboard correctness.
4. Configure approved dashboards/alerts and safe notification tests; verify both positive/error and idle/missing-data cases.
5. Report metric definitions, actual data latency, costs, alert owners, and unverified coverage; review thresholds after workload changes.

### Validation

- Queries use documented columns/sources and exact object scope; usage/file/streaming histories are not conflated.
- Recency, server-processing latency, end-to-end visibility, and source backlog are separately defined.
- Row/reject/billing totals reconcile at compatible grains with NULL/zero/fanout handling and telemetry caveats.
- Idle/no-data/throttled/error cases yield appropriate health/alerts without fabricated success or destructive auto-remediation.
- Output includes monitoring design/queries, cost assumptions, baselines, freshness, and gaps. Unexecuted SQL/alerts remain unverified.

## References

- [Snowpipe billing](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing)
- [PIPE_USAGE_HISTORY view](https://docs.snowflake.com/en/sql-reference/account-usage/pipe_usage_history)
- [PIPE_USAGE_HISTORY function scope and columns](https://docs.snowflake.com/en/sql-reference/functions/pipe_usage_history)
- [COPY_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/copy_history)
- [Streaming event/client telemetry](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-event-table-telemetry)
- [Streaming channel history](https://docs.snowflake.com/en/sql-reference/account-usage/snowpipe_streaming_channel_history)
