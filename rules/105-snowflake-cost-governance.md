---
schema_version: v4.0
rule_version: v5.0.0
description: Measured Snowflake cost attribution, resource controls, warehouse optimization, and recovery-aware storage governance.
last_updated: 2026-10-07
keywords:
  - kw:resource monitor
  - kw:credit quota
  - kw:warehouse metering history
  - kw:cost attribution tagging
  - kw:serverless task credits
  - kw:suspend trigger
  - kw:credit-quota-monitoring
token_budget: ~1250
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
    - 100-snowflake-core.md  # Snowflake SQL patterns and best practices
---
# Snowflake Cost Governance

## Scope

**What This Rule Covers:**
Credit and storage baselines, warehouse/resource controls, serverless monitoring, attribution, anomaly response, and approved cost optimization.

**When to Load This Rule:**
When reviewing Snowflake spending, planning resource monitors/budgets, or proposing cost-governance changes.

## Contract

### Inputs and Prerequisites

- Approved budget, interval/currency/contract rates, workload SLA, cost-center taxonomy, resource inventory, and baseline period.
- Authorized usage-view access and object-specific management privileges. Resource monitor creation requires account-administrator authority; delegated MONITOR/MODIFY can cover existing monitors. Do not require ACCOUNTADMIN for all analysis or invent a schema USAGE grant as sufficient access.

### Mandatory

- Treat cost as a design constraint alongside latency, reliability, and recovery. Record credit estimates separately from currency estimates; use actual account/region/edition/service pricing rather than fixed universal rates.
- Inventory warehouse compute, cloud services, serverless features, storage, and applicable transfer costs separately. WAREHOUSE_METERING_HISTORY is not total account spend; inspect appropriate service histories and billing/usage views with their latency and scope caveats.
- Define monitored warehouse/account coverage, quota interval/reset, notification recipients, and agreed notify/suspend thresholds. The old 75/90/100 thresholds are policy choices, not product requirements. Document shared-monitor impact and any approved coverage exception.
- Resource monitors do not cap serverless spend or provide precise hard credit ceilings. Suspension can lag the threshold, and cloud-services usage can continue. Include headroom and separately monitor serverless tasks, Snowpipe, clustering, and materialized views; budgets/alerts are not guaranteed stop mechanisms.
- Distinguish SUSPEND from SUSPEND_IMMEDIATE and assess running-query/business impact. Configure actual notification delivery/preferences and verify recipients, not merely trigger syntax. Do not bypass a reached monitor by removing it or increasing quotas without approval.
- Apply organization-approved attribution tags, including cost center, workload, environment, and owner where policy requires. Do not invent mandatory tag names or category values. Check tag privileges and allowed values.
- Attribute by stable object identity and appropriate time grain. Current-name/current-tag joins can misattribute historical usage, renamed/recreated resources, or duplicate tag matches; document attribution limits and reconcile totals before chargeback.
- Right-size warehouse size/type and concurrency from measured history/profile evidence. Use workload-appropriate auto-suspend/resume for standard warehouses; avoid universal timeout/concurrency thresholds and respect other warehouse types' lifecycle controls.
- Assess clustering benefit against maintenance cost; inspect actual table metadata rather than unsupported SHOW CLUSTERING KEYS. Do not deploy clustering or larger compute merely to satisfy a checklist.
- Review active, Time Travel, Fail-safe, and stage storage using applicable storage views. Retention reduction or transient-table conversion requires recovery/compliance review and approval; no blanket zero-retention staging policy.
- Distinguish metered cloud-services credits from billed credits after daily adjustments; use applicable billing views/current billing documentation rather than treating warehouse metering sums as an invoice.
- All monitor/tag/warehouse/retention/grant mutations and notification integrations require approved scope, ownership, and downstream impact review. Diagnosis does not authorize changing budgets, suspending workloads, or externally sending account data.

### Execution Steps

1. Read existing resource policies/configuration and permitted usage evidence; establish time zone, reporting period, freshness, and exclusions.
2. Reconcile compute/service/storage totals, attribution coverage, idle/queue/spill patterns, and anomalies against workload needs.
3. Propose monitor/budget coverage, notification thresholds, warehouse settings, tags, and storage changes with savings assumptions, SLA impact, and recovery requirements.
4. Apply only authorized changes after dependency/ownership review; verify effective configuration and delivery in approved scope without inducing an outage to test suspension.
5. Compare subsequent actual usage and SLA against the baseline; retain uncertain outcomes and escalate anomalies through approved channels.

### Validation

- Report reconciled usage, cost assumptions, data latency, service exclusions, and historical-attribution limitations.
- Approved resources have intended quota/trigger/recipient coverage; serverless and storage monitoring remain separate and hard-ceiling limitations explicit.
- Effective warehouse lifecycle, tags, and configuration match policy; workload performance/recovery requirements remain satisfied.
- Cost reductions are measured or labeled estimates, never inferred solely from smaller warehouse size or shorter retention.
- Output includes scoped recommendations/configuration, owner/cadence for review, anomaly response, and remaining verification gaps. Unexecuted SQL and unavailable account evidence remain unverified.

## References

- [Cost management](https://docs.snowflake.com/en/guides-overview-cost)
- [Resource monitor behavior and privileges](https://docs.snowflake.com/en/user-guide/resource-monitors)
- [Budgets](https://docs.snowflake.com/en/user-guide/budgets)
- [WAREHOUSE_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [TABLE_STORAGE_METRICS](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics)
- `103-snowflake-performance-tuning.md` for evidence-based tuning.
- `119-snowflake-warehouse-management.md` and `123-snowflake-object-tagging.md` for warehouse and attribution details.
