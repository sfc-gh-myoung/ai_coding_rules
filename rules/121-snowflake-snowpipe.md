---
schema_version: v4.0
rule_version: v5.1.0
description: "Continuous file ingestion with explicit formats, cloud event boundaries, load reconciliation, and duplicate-safe Snowpipe recovery."
last_updated: 2026-10-08
keywords:
  - kw:snowpipe auto-ingest
  - kw:file-based ingestion
  - kw:cloud event notifications
  - kw:pipe DDL
  - kw:serverless compute
  - kw:file sizing optimization
token_budget: ~1550
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 108-snowflake-data-loading.md  # Stages and bulk loading
  optional:
    - 121a-snowflake-snowpipe-streaming.md  # SDK-based streaming ingestion
    - 121b-snowflake-snowpipe-monitoring.md  # Monitoring and cost tracking
    - 104-snowflake-streams-tasks.md  # Incremental pipelines and CDC
---
# Snowflake Snowpipe (File-Based Ingestion)

## Scope

**What This Rule Covers:**
Auto-ingest versus file REST submission, stage/format/pipe configuration, event filtering, monitored load outcomes, costs, and safe lifecycle recovery.

**When to Load This Rule:**
When designing continuous file ingestion or diagnosing Snowpipe setup/loads. Read `121a-snowflake-snowpipe-streaming.md` for direct row ingestion, `121b-snowflake-snowpipe-monitoring.md` for monitoring, and `121c-snowflake-snowpipe-troubleshooting.md` for failure diagnosis.

## Contract

### Inputs and Prerequisites

- Existing target/stage/format/pipe, immutable file manifest, actual source format, cloud provider/region, event infrastructure, and latency/reject expectations.
- CREATE PIPE and parent access plus stage-type-specific USAGE (external) or READ (internal), target SELECT/INSERT, and integration permissions where applicable.
- Approved cloud/storage/notification/pipe mutation and paid-load scope. REST file submission uses documented key-pair JWT authentication, not inference API auth assumptions.

### Mandatory

- Read existing configuration before creating or replacing resources. Choose cloud auto-ingest for suitable continuous external-stage events; REST submission provides explicit filename queueing, including supported internal-stage workflows. Bulk COPY is usually appropriate for historical batches; REST can load historic files, so do not state a blanket Snowpipe prohibition.
- Use explicit reviewed file format/mappings and approved ON_ERROR behavior. Validate a compatible COPY plan with isolated/manifest-separated files; a production COPY test on the same files later sent to Snowpipe risks duplicates.
- Tune file size and staging cadence to measured latency/throughput. Documented roughly 100-250 MB compressed guidance is not a mandatory minimum or universal two-minute SLA; small event files can be justified. No fixed 5% acceptable data-loss threshold.
- Configure supported S3/SNS/SQS, Azure Event Grid/Storage Queue, or GCS Pub/Sub integration paths using actual provider instructions and approved identities. Filter source events/prefixes/suffixes and pipe selection to exclude test/backup files; overlapping pipe paths can duplicate loads.
- Inspect notification channel values and cloud delivery/permissions, not just AUTO_INGEST=true. Keep cloud keys out of DDL; use approved storage/notification integrations and least privilege. Creating resources or changing ownership/grants requires authorization.
- Snowpipe is serverless and uses managed ingestion compute, not a user warehouse kept running. Current per-GB billing distinguishes uncompressed text from observed binary size; use current service rates and billed-byte evidence, not obsolete per-file charges or fixed savings claims.
- File metadata deduplicates by path/name within bounded pipe history, not by business key or changed eTag. Preserve immutable filenames/content and external manifests; renaming/recreating pipes, aged history, or mixing COPY/Snowpipe can duplicate data.
- Load order is not guaranteed. Snowpipe can combine/split loads across transactions; row/CDC order, reconciliation, and downstream keyed processing must be designed explicitly. Inserted event records are not automatic UPDATE/DELETE application.
- Monitor SYSTEM$PIPE_STATUS, event receipt/queue progress, COPY_HISTORY per-file rows/errors, and PIPE_USAGE_HISTORY consumption separately. Usage history is not file error history. Statement/REST queue success does not prove every row became queryable.
- Reconcile source files, parsed/loaded/rejected rows, keys, timestamps, business totals, and approved tolerance. Quarantine/remediate errors without reloading already accepted rows; inspect actual committed state after timeouts or partial loads.
- Pause/resume only within approval and verify effective state. ALTER PIPE REFRESH queues supported recent files (previous seven days), not arbitrary historical replay or force reload. Review exact prefix/manifests/load history before queueing.
- Recreating a pipe drops its file history and may require cloud notification reconfiguration. Follow documented pause/state/drain/recreate/pause/review/resume steps with ownership/grant/queue evidence; retain beforeimages and explicit duplicate-safe recovery. Never blindly replace a pipe to fix an error.
- Long pauses can outlive event retention (default 14 days). A force-resume override acknowledges risk, not recovery of missing events; reconcile source history and plan authorized backfill. No automatic override or cost-triggered outage.
- Pipe PURGE is unsupported. Delete staged files only after verified reconciliation and retention/deletion approval; cloud lifecycle settings are separate mutations. Configure error notifications through approved integrations/recipients, without exposing file payloads externally.

### Execution Steps

1. Inspect source/target/pipe state and ownership, file identity, format, event path, permissions, and required outcomes.
2. Select auto-ingest/REST/bulk boundaries; prepare explicit format/COPY design and filtered events with duplicate-safe testing/backfill.
3. Under approval, configure resources, queue/load bounded test files, and inspect event/status plus actual COPY outcomes.
4. Reconcile row/file integrity, latency, rejects, and credits/billed bytes; configure approved monitoring/notifications.
5. For changes/recovery, capture current state and manifests, apply documented scoped lifecycle actions, and verify no missing or repeated data.

### Validation

- Intended files, parsing/mapping, integration paths, cloud filters, and effective privileges are established.
- Real file outcomes and source-target checks satisfy specified tolerance/SLA; queue acceptance and usage history are not substituted.
- Bulk/pipe overlap, changed filenames, partial loads, recreation/history expiry, and stale notifications have safe documented recovery.
- Costs use applicable billing evidence; notifications and deletion have approved boundaries.
- Report pipe/event design, file/query evidence, row/reject counts, monitoring and unresolved account/runtime checks. Unexecuted cloud/SQL/load tests remain unverified.

## References

- [Snowpipe behavior, security, history, and order](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro)
- [Cloud auto-ingest](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto)
- [File REST endpoints](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-overview)
- [Managing pipes, refresh, recreation, and staleness](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-manage)
- [Snowpipe costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing)
- [Error notifications](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors)
