---
schema_version: v4.0
rule_version: v5.0.0
description: "Snowpipe Streaming architecture and delivery contracts: channel ownership, committed offsets, schema handling, and bounded recovery."
last_updated: 2026-10-07
keywords:
  - kw:snowpipe streaming
  - kw:high-performance streaming architecture
  - kw:streaming channel management
  - kw:offset token tracking
  - kw:sub-second latency ingestion
  - kw:row-level SDK ingestion
  - kw:snowpipe
token_budget: ~1600
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 108-snowflake-data-loading.md  # Data loading fundamentals (stages, COPY INTO basics)
  optional:
    - 121-snowflake-snowpipe.md  # File-based Snowpipe for comparison (when to use files vs streaming)
    - 121b-snowflake-snowpipe-monitoring.md  # Monitoring, cost tracking, and performance analysis
    - 121c-snowflake-snowpipe-troubleshooting.md  # Troubleshooting and debugging patterns
---
# Snowflake Snowpipe Streaming

## Scope

**What This Rule Covers:**
File versus direct-row ingestion, high-performance versus existing classic compatibility, delivery/channel choice, checkpoints, schema validation, and replay safety.

**When to Load This Rule:**
When choosing or designing Snowpipe Streaming. Read `121d-snowflake-snowpipe-streaming-sdk.md` for SDK implementations, `121b-snowflake-snowpipe-monitoring.md` for metrics, and `121c-snowflake-snowpipe-troubleshooting.md` for diagnosis.

## Contract

### Inputs and Prerequisites

- Existing producer/SDK version, source ordering/retention, target schema, pipe/channel identity, architecture, and measured ingestion/visibility requirements.
- Documented SDK or REST interface, supported auth/runtime/table/region, required privileges, and approved installation/creation/paid-ingestion scope.
- Explicit delivery/reject policy, durable source or replay store, checkpoint authority, and schema-change authorization.

### Mandatory

- Read existing ingestion/channel/checkpoint code before changes. Select current high-performance architecture for suitable new workloads; inspect existing classic compatibility before migration. Do not mix classic methods/configuration with high-performance APIs or assume Java/Python/.NET feature parity.
- Compare file Snowpipe, direct streaming, and bulk COPY by source format, desired latency, throughput, replay, cost, and operational fit. Streaming is not categorically forbidden for historical data; define backfill/live boundaries without invented ten-thousand-row thresholds or guaranteed sub-second visibility.
- High-performance streams process rows through a PIPE object, including supported transformations/column mapping. Verify default versus custom pipe behavior and actual schema; do not treat direct rows as file COPY or assume target INSERT alone supplies every streaming privilege.
- Choose Named Channels for per-channel ordering/source-offset recovery and exactly-once delivery when the application implements that contract. Choose supported Elastic Channels only when at-least-once/no ordering is acceptable. Channel mode is distinct from classic/high-performance architecture.
- For Named Channels use deterministic source-partition identities and coordinated single-writer ownership; keep channels long-lived. Submit serially in source order and scale across independent channels. Ordering is not global across channels, and reopening the same identity can invalidate another writer.
- Offset tokens are application-managed progress markers, not automatic business-key deduplication or universally numerically validated sequences. Bind tokens to retained source records and a defined comparison/replay policy; do not use wall-clock timestamps as guaranteed unique source positions.
- Advance source/application checkpoints only after the server committed offset confirms the relevant records, not after a synchronous append accepted/buffered them. Retain uncommitted records durably; neither channel mode makes memory-only producer data crash-durable.
- On uncertain outcome/channel invalidation, inspect last committed progress, reopen with verified ownership, and replay only retained records after that point in order. Do not repeatedly append the same token expecting automatic rejection/deduplication. Elastic ambiguous acknowledgements can duplicate rows and need downstream reconciliation.
- Let the supported SDK buffer/batch while bounding outstanding rows/bytes and backpressure. Direct REST batching/compression/payload limits are interface-specific; preserve documented retry request identity for the same rowset without treating request IDs as blanket exactly-once guarantees.
- Validate data types, precision/time zones, NULLs, mappings, and table support. Carry source partition/offset metadata when required for gap/error reconciliation; gaps may be legitimate source behavior, so do not declare every nonconsecutive offset missing data.
- Table schema evolution uses documented ENABLE_SCHEMA_EVOLUTION and privileges/mappings where supported; inspect current architecture/version restrictions. No invented ADD_COLUMNS/FAIL_MISSING_COLUMNS table modes or SKIP_FILE row-SDK option. Evolution can be asynchronous and may drop NOT NULL constraints; permission and downstream impact require review.
- Handle immediate validation/serialization/client/backpressure errors and asynchronous row/channel errors separately. Successful durable progress does not alone prove all rows passed processing or are query-visible. Record/reconcile rejects rather than silently dropping data.
- Use bounded classified retries/backoff for documented transient errors; invalid schema/auth requires correction, not an infinite retry. Ensure checkpoint/producers recover after crashes and close/flush behavior is understood before termination.
- Streaming is insert-only; CDC updates/deletes require downstream state application with business keys/order/tombstones. Monitor progress, reject/gap counts, visibility latency, throughput, and actual usage/cost with source-specific histories; no universal 1% error allowance or classic/high-performance cost promise.

### Execution Steps

1. Inspect producer, SDK/architecture, source retention/order, target/pipe schema, and delivery/authority requirements.
2. Select ingestion/channel mode and define ownership, durable retention, committed checkpoint, reject handling, and schema contract.
3. Implement the documented interface with bounded buffering/retries, cleanup, progress/error telemetry, and explicit downstream CDC behavior.
4. Test local crash/replay/invalidation/schema fixtures; run authorized bounded ingestion to verify committed progress, row integrity, visibility, latency, and cost.
5. Report channel/pipe identities, checkpoint/recovery design, measured outcomes, and unresolved capability/live checks.

### Validation

- Actual architecture/SDK/auth/target/pipe support is verified, not inferred from generic snippets.
- Source checkpoints never advance ahead of committed progress; retained replay and writer coordination survive failure without hidden data gaps.
- Named/Elastic delivery limitations are explicit; no global ordering or token-based automatic deduplication claim.
- Synchronous/asynchronous rejects, schema evolution, partial outcomes, buffering/backpressure, and clean shutdown are tested.
- Source-target rows/keys/offsets and specified latency/throughput/cost targets reconcile; unexecuted ingestion remains unverified.

## References

- [Streaming introduction](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview)
- [High-performance concepts](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview)
- [Channel type and delivery comparison](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-choosing-channel-type)
- [Committed checkpoints and error recovery](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-best-practices)
- [Table/schema support](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-table-support)
- [Streaming access control](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-access-control)
