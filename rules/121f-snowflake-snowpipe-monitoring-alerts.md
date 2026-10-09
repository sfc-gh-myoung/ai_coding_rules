---
schema_version: v4.0
rule_version: v3.0.0
description: "Actionable Snowpipe alerts with truthful metric sources, owner-scoped execution, safe notifications, and measured cost optimization."
last_updated: 2026-10-07
keywords:
  - kw:snowpipe alert configuration
  - kw:channel stall detection
  - kw:system send email
  - kw:baseline threshold derivation
  - kw:pipe cost per GB
  - kw:file size 100-250MB
  - kw:snowpipe
token_budget: ~1450
context_tier: Medium
depends:
  required:
    - 121-snowflake-snowpipe.md  # File-based Snowpipe core concepts
  optional:
    - 121b-snowflake-snowpipe-monitoring.md  # Core monitoring queries and cost tracking
    - 105-snowflake-cost-governance.md  # Resource monitors and cost optimization
---
# Snowpipe Monitoring Alerts and Cost Optimization

## Scope

**What This Rule Covers:**
Error/stall/freshness/spend alert design, deduplicated monitoring, approved delivery, and correctness-preserving file/streaming optimization.

**When to Load This Rule:**
When designing Snowpipe alerts, scheduled checks, or cost improvements. Read `121b-snowflake-snowpipe-monitoring.md` for actual metric schemas and `105-snowflake-cost-governance.md` for consumption/control analysis.

## Contract

### Inputs and Prerequisites

- Existing monitoring, exact pipeline/architecture, source arrival expectations, measured baseline, SLA/error tolerance, and alert owner/escalation policy.
- Approved recipients/integration and notification content; condition/action role privileges and current alert/task API.
- Defined compute/cadence/window, deduplication/watermark, retention, and approved creation/resume/send scope.

### Mandatory

- Start with actionable failures, source backlog/no-data, sustained SLA breach, and cost anomalies; prioritize by operational consequence, not an arbitrary two/three-alert count. Use workload baselines and agreed policy; cold-start provisional alerts are better than waiting weeks to detect outages.
- Derive thresholds from relevant latency/error metrics and business SLO, not universally 1.3x p95, 5% files, 1% rows, or fifteen-minute stalls. Enforce minimum sample counts and separate NULL/no-data from zero-error success.
- File errors come from supported COPY_HISTORY/pipe validation/status, streaming errors/progress from documented channel status/event telemetry. PIPE_USAGE_HISTORY lacks row-error/latency fields; COPY_HISTORY start/end fields must not be invented. Time since last commit is recency, not measured load latency.
- Alert on stalled progress only with expected source arrivals/backlog and source freshness. Ignore intentional idle periods and authorized maintenance; distinguish stale monitoring collection from stalled ingestion.
- Choose scheduled versus supported new-data alerts and inspect constraints; new-data mode isn't generic polling of any view and cannot be manually executed with EXECUTE ALERT. Inspect available streaming templates before using them; template availability/settings are account-specific.
- Alerts can use supported serverless compute or an appropriately sized warehouse; a dedicated warehouse can isolate heavy checks but is not universally required. Verify CREATE ALERT, execution privileges, parent/source/action access, and serverless privilege when applicable.
- Conditions/actions run with the alert owner's role, not a worksheet caller's permissions. Verify effective role and source filters, least privilege, integration access, and data boundaries; diagnosis does not authorize broad grants or new integrations.
- Newly created alerts are suspended. Review condition/action/cadence and notification authority before approved resume; inspect actual status/history afterward. Creating an object or returning no error is not proof delivery works.
- If using SYSTEM$SEND_EMAIL, use an existing approved notification integration, allowed/verified recipients, and confidential-content policy. Do not send test email, raw records, filenames, or account errors externally without authorization. Track condition, action, and delivery outcome separately.
- Persist processed failures with a stable pipeline/file/event identity and a durable last-success watermark. Overlapping windows and repeated polls must not insert the same history rows or send the same outage notification on every run. Late history arrival needs deliberate lookback and keyed deduplication.
- Use supported alert/task schedule syntax and real fully qualified identities; inspect templates/SQL before execution. Schedules, tasks, views/log tables, alert activation and automated remediation are mutations needing scoped approval.
- Optimize measured file sizes/cadence/event filtering and streaming batching/channel reuse/mappings without violating latency or source replay. 100-250MB is guidance, not a hard gate. Avoid waiting for a full batch indefinitely or closing active channels just to reduce cost.
- Compare actual service billing/bytes and row integrity before/after. Current file Snowpipe billing is per GB, not universal per-file/per-second savings. Cost improvements must not discard rows, relax schema, drop business transformations, or claim guaranteed reductions.
- Budgets/alerts do not guarantee stopping serverless ingestion. Do not automatically pause pipes, suspend monitoring, reset channels, delete files, or disable integrity checks in response to spend.

### Execution Steps

1. Review actual source metrics/freshness, arrival expectations, incident history, baseline, and alert ownership/permissions.
2. Design scoped condition/action/window/watermark, severity/deduplication, compute/cadence, and approved recipients/content.
3. Validate fixtures for failure, normal load, intentional idle, late data, NULL/zero denominators, and repeated polls.
4. Create/resume/test only approved objects/messages; inspect evaluation/action/delivery history and effective role behavior.
5. Benchmark approved optimizations against latency, row/reject integrity and billed usage; document owners, results, and gaps.

### Validation

- Supported sources and threshold/denominator/window semantics detect real errors without treating idle/missing telemetry as healthy.
- Alert owner can execute actual condition/action; serverless/warehouse cost and schedule limitations are explicit.
- Repeated/late events do not duplicate logs/notifications; normal and maintenance cases do not generate preventable noise.
- Approved notification delivery is observed or explicitly unverified; no unauthorized external data or destructive action.
- Output includes alert/task design, justified policy, owners, optimization evidence and outstanding runtime checks; no guaranteed savings or zero-false-positive claim.

## References

- [Alert types, compute, privileges, lifecycle, and history](https://docs.snowflake.com/en/user-guide/alerts)
- [Streaming metrics and alert templates](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-event-table-telemetry)
- [Snowpipe costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing)
- [Email notification integration](https://docs.snowflake.com/en/user-guide/notifications/email-notifications)
- `121b-snowflake-snowpipe-monitoring.md` for source-specific metric definitions.
