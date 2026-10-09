---
schema_version: v4.0
rule_version: v5.0.0
description: "Evidence-first Snowpipe diagnosis, source-specific error classification, and scoped duplicate-safe recovery."
last_updated: 2026-10-07
keywords:
  - kw:snowpipe debugging
  - kw:pipe execution failures
  - kw:streaming channel errors
  - kw:schema mismatch resolution
  - kw:latency diagnosis
  - kw:diagnostic queries
  - kw:snowpipe
token_budget: ~1550
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 121-snowflake-snowpipe.md  # File-based Snowpipe core concepts
  optional:
    - 121a-snowflake-snowpipe-streaming.md  # Streaming Snowpipe core concepts
    - 121b-snowflake-snowpipe-monitoring.md  # Monitoring and cost management
    - 121e-snowflake-snowpipe-troubleshooting-advanced.md  # Advanced streaming patterns and debugging checklists
---
# Snowflake Snowpipe Troubleshooting

## Scope

**What This Rule Covers:**
File/streaming auth, configuration, data, progress, duplicate, performance, and cost diagnosis with verified recovery and prevention.

**When to Load This Rule:**
When investigating failed or incorrect Snowpipe ingestion. Read `121a-snowflake-snowpipe-streaming.md` for streaming delivery, `121b-snowflake-snowpipe-monitoring.md` for sources, and `121e-snowflake-snowpipe-troubleshooting-advanced.md` for detailed producer recovery.

## Contract

### Inputs and Prerequisites

- Exact pipeline/table/channel/architecture, error/time window, expected source records, SLA, recent changes, and current owner/permissions.
- Permitted status/history/source reads and retained manifests/checkpoint evidence; live loads/mutations are separately authorized.
- Actual SDK/API revision and cloud event/credential configuration, with secrets/raw records excluded from public logs.

### Mandatory

- Gather current status/error/history and recent deployment/configuration evidence before proposing a cause. Classify authentication, network, privileges, events, parsing/schema, channel ownership, backlog, or cost; symptom thresholds alone do not establish root cause.
- For files inspect SYSTEM$PIPE_STATUS execution state and received/forwarded message timestamps, actual stage/path/pattern, cloud event subscription/permissions, and target COPY_HISTORY outcomes. Received events may not match the pipe path; LIST proves file presence, not valid delivery/loading.
- Check applicable object-create event types, including multipart upload/flush-close behavior when relevant, and actual stage/provider/region restrictions. Do not recreate cloud queues/integrations or broaden event filters automatically.
- If files are absent from COPY_HISTORY, check earlier windows, source access/freshness, duplicate history, pattern matching, and queue state before declaring missing data. Usage history is not an error log. Inspect first errors and supported VALIDATE_PIPE_LOAD or compatible validation-only COPY for full details.
- Verify actual file formats, field/NULL/type/time mappings, schema changes, and partial-load behavior. VALIDATION_MODE restrictions apply; a diagnostic request does not authorize a production COPY load or relaxing ON_ERROR/schema enforcement.
- File deduplication uses pipe path/name metadata, not changed eTag. Failed filenames can also be registered. Inspect bulk/pipe overlap, overlapping pipes, renames/recreation, bounded history, and accepted rows before repair; FORCE, TRUNCATE, renaming, or refresh can worsen duplicates.
- Reconcile source-to-target business keys/totals and retained manifests before backfill. REFRESH is recent-file queueing, not a restart or unconditional reprocessing. Recreate only under the parent's pause/drain/history-loss/cloud-reconfiguration safeguards and explicit approval.
- Diagnose file latency from arrival/event/queue/processing evidence, not CURRENT_TIMESTAMP minus last_load_time. Analyze file sizes/cadence and COPY complexity against SLA; serverless Snowpipe isn't fixed by resizing a user warehouse. Consider current per-GB billing before attributing spend to obsolete file overhead.
- For streaming read actual SDK errors/channel status and server processing errors; verify account URL/identifier format, supported auth, network/clock, role/pipe/table access, and library version. No blanket CREATE TABLE requirement for an existing consumer target or universal error-code mapping.
- Separate immediate append validation from asynchronous row errors/commit state. Verify real types/precision/required fields, approved evolution settings, and actual constraints; ordinary Snowflake PK/FK declarations are not universally enforced row checks.
- For Named Channel duplicate/gap problems inspect committed token, source retention, checkpoint durability, channel identity/writer invalidation, and restart logic. Advance checkpoints only after server commit; recover per channel/source partition, not a global counter guessed across independent sources.
- For Elastic Channels ambiguous acknowledgements permit duplicates; verify retained events and downstream reconciliation. Never claim a matching token or successful append eliminates all duplicate/lost records.
- For streaming latency/backpressure measure source-to-visibility stages, SDK buffers/network, async commit and server backlog. Let supported SDKs batch; no mandatory 100-1000-row buffer that delays sparse streams or wait-per-row pattern.
- Change one evidence-supported variable at a time, with approved scope/rollback; preserve uncertain outcomes and failed attempts. Do not automatically resume paused/stale pipes, rotate/register keys, grant access, recreate tables, reset channels, or pause workloads for cost spikes.
- Verify root-cause fix through authorized representative loading plus row/error/latency reconciliation. Document evidence, cause or remaining hypotheses, affected scope, recovery, and monitoring to prevent recurrence; no universal 5%/1% acceptable loss.

### Execution Steps

1. Capture exact symptoms, identities, architecture, error/state, source expectations, and recent changes using permitted reads.
2. Follow the relevant file/event or streaming/channel branch; test hypotheses with bounded non-mutating evidence.
3. Propose minimal correction with duplicate/gap impact, retained-state recovery, permissions, and rollback.
4. Apply only approved correction and safe bounded test loads; reconcile actual committed/visible outcomes before declaring resolution.
5. Record incident evidence, rejected hypotheses, fix verification, remaining gaps, and approved preventive monitoring.

### Validation

- Root-cause claims are supported by exact status/errors and source-specific evidence, or labeled provisional.
- File event/path/schema/load state or streaming auth/channel/commit state is independently checked.
- Partial loads, stale history, source gaps, and duplicates are reconciled; no broad unapproved replay/DDL/grant/teardown.
- Actual row/error/latency/cost outcomes satisfy agreed criteria; recency/usage counts are not false latency/integrity proof.
- Output includes diagnosis, scoped fix/recovery and verification evidence. Unexecuted loads/runtime tests remain open.

## References

- [Snowpipe troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-ts)
- [Safe pipe management](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-manage)
- [Pipe status](https://docs.snowflake.com/en/sql-reference/functions/system_pipe_status)
- [Validate pipe loads](https://docs.snowflake.com/en/sql-reference/functions/validate_pipe_load)
- [Streaming progress/errors](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-event-table-telemetry)
- [Streaming retry/commit guidance](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-best-practices)
