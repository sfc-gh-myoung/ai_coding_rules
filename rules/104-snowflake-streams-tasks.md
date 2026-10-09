---
schema_version: v4.0
rule_version: v5.0.0
description: Reliable Snowflake change-data capture, task orchestration, transaction boundaries, and pipeline recovery.
last_updated: 2026-10-07
keywords:
  - kw:change data capture
  - kw:stream consumption
  - kw:task dag
  - kw:merge patterns
  - kw:task history monitoring
  - kw:stream staleness
  - kw:cdc
token_budget: ~1300
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
    - 100-snowflake-core.md  # Snowflake SQL patterns and best practices
---
# Snowflake Streams and Tasks

## Scope

**What This Rule Covers:**
Incremental pipelines, stream change semantics, task compute/scheduling, deterministic application, observability, and data-preserving recovery.

**When to Load This Rule:**
When implementing or troubleshooting Snowflake CDC, streams, scheduled/triggered tasks, or task graphs.

## Contract

### Inputs and Prerequisites

- Source/target schemas, business keys, initial-load strategy, supported change types, arrival ordering, latency SLA, and recovery requirements.
- Authorized object scope, current stream/task state, source retention, and task owner privileges. Check CREATE STREAM/TASK and source access; task execution needs appropriate object privileges and EXECUTE TASK, plus EXECUTE MANAGED TASK for serverless compute or warehouse USAGE for user-managed compute.

### Mandatory

- Select a stream type compatible with the source and changes. Standard streams capture inserts/deletes and update pairs; append-only streams do not represent updates/deletes. Define whether initial rows are needed and how bootstrap and subsequent changes avoid gaps or duplicates.
- Streams expose changes from an offset, not an immutable event log. Plain SELECT does not advance the offset. Successful committed stream-consuming DML advances it; rollback leaves it unchanged. Explicit transactions permit multiple statements to read the same stream snapshot.
- Filtering rows out of consuming DML does not preserve those excluded changes for later consumption. Define the complete consumption boundary; use separate streams for independent consumers rather than sharing one offset accidentally.
- Normalize METADATA$ACTION and METADATA$ISUPDATE according to source semantics before application. Do not blindly treat an update's DELETE record as a business deletion. Resolve duplicate source keys and late/out-of-order records deterministically before MERGE.
- Choose INSERT, UPDATE, DELETE, MERGE, or a procedure to match the transformation; MERGE alone is not proof of idempotency. Preserve transaction atomicity for related writes and offset advancement, with explicit replay/deduplication policy for retries and external effects.
- Select user-managed warehouse or serverless compute explicitly; WAREHOUSE is omitted for serverless tasks. Use supported scheduled/triggered execution or AFTER graph dependencies; reject cycles and unintended source-feedback loops.
- Use SYSTEM$STREAM_HAS_DATA in suitable task WHEN conditions, not as a guarantee of rows. It can return false positives, especially for view streams; the consuming path must handle empty results without an endless unnecessary-run loop.
- Task dependencies impose orchestration, not one transaction across a graph. Define per-task commit boundaries, overlap policy, timeouts, failure suspension/retry, and partial-graph recovery.
- Creating/replacing streams can discard pending change history; replacing tasks can affect state/dependencies. Inspect existing objects, grants, consumers, and running executions before approved deployment. Never use blanket replacement as an idempotency guarantee.
- New tasks start suspended. RESUME, EXECUTE TASK, grants, retention changes, and test-data writes require separate execution authority; SHOW/inspection is not activation.
- Monitor task history/errors, end-to-end data lag, row reconciliation, credit usage, and SHOW STREAMS stale/STALE_AFTER metadata. Choose warning lead time from recovery needs, not a universal fixed interval.
- SYSTEM$STREAM_HAS_DATA helps prevent staleness only when the stream is empty and the function returns FALSE. Consumption must keep pace with retention. For stale streams, stop and establish an approved backfill/reconciliation plan before recreating; do not silently lose pending changes.

### Execution Steps

1. Inspect authorized source/target, stream/task definitions, retention, ownership, and dependencies; establish bootstrap and change-application semantics.
2. Design complete consumption transactions, deterministic keyed application, compute, triggers/schedule, graph order, and failure/replay handling.
3. Prepare data-preserving deployment and recovery steps; leave tasks suspended until activation is approved.
4. In an approved test scope, cover insert/update/delete, duplicate keys, late arrivals, empty/false-positive checks, rollback, and retry scenarios.
5. Activate only approved tasks after checks; observe history, freshness, offset consumption, target reconciliation, and costs. Inspect uncertain outcomes before replay.

### Validation

- Correct final state and expected changes, no skipped filtered records, update-pair misapplication, duplicate amplification, or bootstrap gaps.
- Committed consumption and rollback behavior verified, independent consumers isolated, replay behavior documented.
- Task compute/privileges, graph dependencies, lifecycle, overlap/failure policies, and retention monitoring match the actual environment.
- Output includes reviewed DDL/DML design, dependency/transaction diagram or description, monitoring, activation approval, and recovery runbook.
- Report actual test/query/task outcomes; design-only SQL, unrun activation, unavailable history, and untested recovery are not passes.

## References

- [Streams introduction and transactions](https://docs.snowflake.com/en/user-guide/streams-intro)
- [Stream management and staleness](https://docs.snowflake.com/en/user-guide/streams-manage)
- [Tasks and compute models](https://docs.snowflake.com/en/user-guide/tasks-intro)
- [Task graphs](https://docs.snowflake.com/en/user-guide/tasks-graphs)
- [SYSTEM$STREAM_HAS_DATA](https://docs.snowflake.com/en/sql-reference/functions/system_stream_has_data)
- [MERGE semantics](https://docs.snowflake.com/en/sql-reference/sql/merge)
- `119-snowflake-warehouse-management.md` for user-managed warehouse planning.
