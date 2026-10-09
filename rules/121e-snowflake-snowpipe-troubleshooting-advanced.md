---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced streaming recovery: durable committed checkpoints, writer coordination, bounded throughput, and reject reconciliation."
last_updated: 2026-10-07
keywords:
  - kw:snowpipe streaming offset
  - kw:exactly-once semantics
  - kw:streaming batch optimization
  - kw:channel ownership conflicts
  - kw:pre-insert validation
  - kw:snowpipe debugging checklist
  - kw:snowpipe
token_budget: ~1300
context_tier: Low
depends:
  optional:
    - 121c-snowflake-snowpipe-troubleshooting.md  # Core troubleshooting patterns and decision tree
---
# Snowpipe Advanced Troubleshooting

## Scope

**What This Rule Covers:**
Source-offset replay, channel ownership, producer buffering, schema validation/quarantine, and evidence-based file/streaming checks.

**When to Load This Rule:**
When resolving streaming duplicates/gaps, writer conflicts, producer backpressure, or row validation. Read `121c-snowflake-snowpipe-troubleshooting.md` for the core diagnostic branch and `121d-snowflake-snowpipe-streaming-sdk.md` for actual SDK APIs.

## Contract

### Inputs and Prerequisites

- Exact source partition/channel/pipe/table and SDK architecture/version, retained input, current committed token, checkpoint store, and error evidence.
- Expected arrival/reject/latency policy, current producer ownership, and approved read/test/recovery scope.
- Actual schema/type/mapping constraints, durable quarantine destination, and existing buffering/checkpoint implementation.

### Mandatory

- Gather status/source/checkpoint evidence before edits or reopen. Treat synchronous append acceptance, server durable progress, processing success, and query visibility as distinct states; a plausible code patch is not verified recovery.
- Named Channel recovery must compare original retained source positions to server committed progress. Never persist progress merely after append/insert returned without error. Preserve source records until committed checkpoint confirms them.
- Offset tokens identify application progress per channel, not a global counter or automatically sorted/deduplicated Snowflake key. Document token decoding/comparison and row association; no guessed restart at zero or unique timestamp substitute.
- If persisted checkpoint is ahead of confirmed progress, stop source acknowledgement and reconcile retained rows before replay. If source retention cannot recover missing records, report the data gap rather than fabricate exactly-once success.
- Coordinate a single active producer per Named Channel/source partition using actual assignment/lease ownership. A second open can invalidate the first. Fix coordination and resume the stable identity; random PID/hostname channel names can abandon recovery history and are not a general fix.
- Independent source partitions use independent stable channels. Concurrent Elastic producers use its supported delivery contract and durable acknowledgements; ambiguous retries can duplicate rows and need retained-event/downstream reconciliation.
- Let supported SDKs append asynchronously and batch internally. Bound retained bytes/outstanding rows and checkpoints; do not force every sparse stream to wait for 1000 rows or incorrectly claim each append is a network round trip/commit.
- Diagnose throughput from source arrival, buffer/backpressure, network, server processing, and commit/visibility measurements. Use multi-row APIs when source batches already exist; keep time/size flushing bounded and preserve Named order.
- Validate fields, true numeric/boolean distinctions, required/NULL values, precision/time zones, and schema mappings using the actual contract. PK/FK declarations on ordinary tables are not automatically enforced ingestion uniqueness.
- Preserve invalid/rejected rows with original partition/offset and sanitized errors in authorized durable quarantine. Skipping silently or advancing beyond unhandled errors can cause permanent gaps; apply explicit reject/checkpoint policy and source-target reconciliation.
- Handle immediate and asynchronous errors separately; retry only classified recoverable outcomes with bounded backoff and committed-state inspection. No row-error logging that exposes confidential payloads or secrets.
- For file pipelines check actual pipe status, stage/format/path, event forwarding and COPY_HISTORY under current access/history limits; apply duplicate-safe REFRESH/recreation rules. For streaming check auth/network/role/pipe/schema, writer status, committed offsets, async errors and backpressure.
- Recovery mutations, credential/grant changes, test ingestion, and retention/quarantine infrastructure need approval. Change one justified variable, preserve failed attempts/current bytes, and verify integrity before removing evidence or old resources.

### Execution Steps

1. Read source/client/checkpoint and current ownership/status; identify exact symptom and retained records affected.
2. Reconcile source positions, durable commits, rejects and target rows; test writer/schema/buffer hypotheses without mutation.
3. Implement approved smallest fix with stable channel coordination, commit-gated checkpoints, retained replay, and explicit quarantine policy.
4. Test crash/reopen/concurrent-writer/schema/backpressure cases locally and authorized bounded recovery live; verify no missing/repeated data.
5. Report issue, evidence, cause/hypotheses, scoped fix, verification, and unresolved source/runtime gaps.

### Validation

- Checkpoints reflect server committed progress; stable channel identity/source ownership and replay retention survive restart.
- Duplicate/gap claims use actual source-target evidence; irrecoverable or unverified ranges remain explicit.
- Buffering and retries are bounded, order preserved, asynchronous errors inspected, and invalid rows quarantined under agreed policy.
- Auth/schema/data/progress/performance checks match the actual architecture and expected arrivals; no arbitrary 1%/five-second/50ms gate.
- Output preserves incident/attempt evidence and scope; no unsafe channel reset, replay, or credential/DDL change.

## References

- [Channel delivery and recovery](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-choosing-channel-type)
- [Batching, errors, and committed progress](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-best-practices)
- [Actual Named SDK lifecycle](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-getting-started)
- [Streaming telemetry](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-event-table-telemetry)
- [File Snowpipe troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-ts)
