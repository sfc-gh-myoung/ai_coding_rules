---
schema_version: v4.0
rule_version: v5.0.0
description: "Scoped DMF schedules, dedicated result access, violation alerting, idempotent remediation, and reconciled serverless costs."
last_updated: 2026-10-07
keywords:
  - kw:DMF scheduling
  - kw:quality event tables
  - kw:expectation failures
  - kw:remediation workflows
  - kw:EXECUTE DATA METRIC FUNCTION
  - kw:quality alerting
  - kw:dmf
token_budget: ~1450
context_tier: High
depends:
  optional:
    - 124a-snowflake-data-quality-custom.md  # Custom DMF creation
    - 104-snowflake-streams-tasks.md  # Task scheduling patterns
---
# Snowflake Data Quality: Operations and Monitoring

## Scope

**What This Rule Covers:**
Native DMF scheduling/execution access, dedicated result/expectation monitoring, alerts/incidents, scoped remediation, and cost management.

**When to Load This Rule:**
When operating scheduled quality checks or diagnosing results/violations/access. Read `124-snowflake-data-quality-core.md` for metric/association semantics, `124a-snowflake-data-quality-custom.md` for custom checks and `104-snowflake-streams-tasks.md` for separate automation tasks.

## Contract

### Inputs and Prerequisites

- Actual DMF associations/signatures, named expectations, table schedule/execution role, baseline, business SLA and supported object kind.
- Authorized result/function access, monitoring compute, scoped configuration/remediation approval, and confidential incident destinations.
- Current result/usage schemas, defined measurement window/time zone, incident owner/severity, watermark/deduplication and rollback policy.

### Mandatory

- Inspect existing checks and effective execution identity before changing schedules/roles. Native DATA_METRIC_SCHEDULE drives scheduled serverless DMFs; Snowflake Tasks are not mandatory DMF evaluators and task success is not scheduled DMF success.
- Set documented minute/cron/eligible TRIGGER_ON_CHANGES schedule through object SET DATA_METRIC_SCHEDULE, not invented MODIFY DATA METRIC SCHEDULE syntax. All associated metrics share the object schedule; suspension/resume and effective-change delay need explicit review.
- Match criticality, arrival pattern, detection SLA and total cost. Business-hour scheduling is a policy option, not permission to stop critical monitoring overnight. No universal five-minute/hour/day interval or blanket over-monitoring rule.
- Association execution defaults to owner or documented EXECUTE AS ROLE. Verify account EXECUTE DATA METRIC FUNCTION, function USAGE, appropriate object SELECT/ownership and policy effects. Non-owner execution is supported under its contract; database-role global privilege limits do not authorize automatic ownership transfer.
- Query dedicated SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS_RAW, flattened results/expectation-status views or supported functions. There is no generic database INFORMATION_SCHEMA.EVENT_TABLE_HISTORY quality feed; do not create/repoint the account event table for DMF results.
- Verify admin/viewer/lookup application-role and function-specific access. Function access can also require object/function privileges and active execution role. Broad raw-results access is not the default solution to a permission error.
- Use actual measurement_time as evaluation evidence and retain scheduled_time separately. Filter exact object/metric/association/expectation identities and time; historical names alone cannot establish current coverage after replacement.
- Distinguish computed metric, expectation violation, execution error, suspended association and missing/stale result. Raw evaluation versus expectation rows differ; expectation raw Boolean true means violated, not passed. Do not invert it or count each expectation as a distinct metric run.
- Define denominators/NULL/empty behavior and freshness before computing pass/failure rates. Multi-expectation joins can fan out metrics; reconcile association/run grain independently. A last passing old measurement is not current health.
- Alerts/tasks use actual owner-role privileges, supported warehouse/serverless models, and approved actions/recipients. Creation is not activation; verify resumed status, evaluation/action history and delivery separately. Named expectation alone does not automatically send email.
- Deduplicate incident events and monitoring inserts with stable association/measurement identity and last-success windows; allow late results without recurring duplicate notifications or quarantine rows.
- Remediation follows detection, evidence/triage, root cause, scoped correction, verification and documentation with severity/owner/SLA. Automatic quarantine/circuit-breakers require an explicit idempotent action contract, transaction/data retention, protected-source scope and recovery.
- A quality violation is not authorization to delete/overwrite rows, relax expectations/masks, self-grant, transfer ownership, or externally send payloads. Recheck the latest source state before correction; broad task scans must not repeatedly copy the entire failing population.
- Scheduled quality compute uses serverless metering plus separate logging/storage/query overhead. Manual metric calls are not scheduled-DMF billing but their SQL query can still use compute. DATA_QUALITY_MONITORING_USAGE_HISTORY uses START_TIME/END_TIME, CREDITS_USED and table/database/schema identities, not invented usage_date/object_name/execution_count columns.
- Track current association capacity (50000/account in current docs), unsupported shared/reader/trial cases, replication/effective schedule/result access, and changed-object bindings. No guarantee that replica checks or results operate identically without verification.

### Execution Steps

1. Inventory associations/expectations/schedules, role/policies and dedicated results; profile gaps and expected detection window.
2. Design minimal cadence/access/alert policy with measurement grain, deduplication, owners and cost limits.
3. Apply only approved settings/automation and exercise representative good/bad/empty/stale/denied cases.
4. Inspect actual fresh values/violations/execution/delivery and billed usage; reconcile independent source checks.
5. Implement approved scoped remediation, re-evaluate corrected data and record incident/rollback evidence and unresolved gaps.

### Validation

- Native schedules and actual execution permissions are effective; Tasks/results/expectations are not conflated.
- Dedicated results/violation semantics, timestamps and denominator/grain are verified, including missing data and multiple expectations.
- Allow/deny, repeated/late events, action/delivery and remediation rollback are checked without unauthorized data exposure.
- Costs/capacity/replication assumptions match actual evidence; monitoring remains within business detection requirements.
- Output includes configuration, access, measurements/incidents, costs and verification gaps, not fabricated live success.

## References

- [Native schedules and suspension](https://docs.snowflake.com/en/user-guide/data-quality-working)
- [Dedicated expectation results](https://docs.snowflake.com/en/user-guide/data-quality-expectations)
- [Execution/result access](https://docs.snowflake.com/en/user-guide/data-quality-access-control)
- [Supported kinds, limits and billing](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [Usage columns and latency](https://docs.snowflake.com/en/sql-reference/account-usage/data_quality_monitoring_usage_history)
- [Alerts](https://docs.snowflake.com/en/user-guide/alerts)
