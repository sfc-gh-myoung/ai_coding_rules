---
schema_version: v4.0
rule_version: v5.0.0
description: "Data quality and governance as code: profiled checks, versioned metric definitions, non-destructive schema evolution, approved monitoring and governed incident response."
last_updated: 2026-10-07
keywords:
  - kw:expectation suites
  - kw:schema evolution
  - kw:metric definitions catalog
  - kw:data drift monitoring
  - kw:quality gates automation
  - kw:incident response procedures
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 100-snowflake-core.md  # Snowflake SQL patterns
    - 124-snowflake-data-quality-core.md  # Snowflake-specific data quality patterns
    - 132-snowflake-demo-modeling.md  # Data modeling standards
---
# Data Governance and Quality

## Scope

**What This Rule Covers:**
Tool-agnostic data quality and governance practice: profiled checks (DMFs, dbt tests, Great Expectations), pipeline quality gates, canonical metric definitions, schema evolution and deprecation, freshness/volume/drift monitoring, governed agent access and incident response.

**When to Load This Rule:**
When designing quality checks, metric catalogs, schema changes, monitoring or data incident processes; load `124-snowflake-data-quality-core.md` for Snowflake DMF specifics.

## Contract

### Inputs and Prerequisites

- Existing checks, frameworks and versions (DMFs, dbt, Great Expectations), metric definitions, lineage, consumers and SLAs.
- Approved roles, warehouses, notification integrations, catalog/tagging conventions and authority for any object, task, alert or schema change.

### Mandatory

- Inventory existing checks, metric definitions and monitoring before adding new ones; extend the established framework rather than introducing a parallel one.
- Keep quality rules, metric definitions and migrations as reviewed code in version control, executed by automated pipeline or CI gates where available; record ad-hoc checks only as investigation evidence.
- Derive thresholds from profiling and business rules (valid domains, uniqueness, referential integrity, freshness SLAs), not arbitrary percentage buffers; document severity and whether a failure blocks or warns.
- Use the installed framework's current API (for example dbt `data_tests` or semantic models/MetricFlow, Great Expectations 1.x expectation classes, Snowflake DMFs with expectations) rather than deprecated forms.
- Maintain one canonical definition per metric with name, business definition, calculation, grain, filters, owner, refresh cadence, source and lineage; reconcile duplicates found elsewhere with their owners before replacing them.
- Schema evolution is backward compatible by default: add, backfill, migrate consumers, deprecate with date and owner, then remove after verified consumer migration. Destructive DDL, `CREATE OR REPLACE`, large backfills and drops require explicit approval, impact analysis and rollback (Time Travel/clone or reversible migration).
- Write idempotent migrations and test them on non-production data before production.
- Monitor freshness, volume, schema changes and distribution drift with thresholds tied to SLAs and observed variance. Creating tasks, alerts, DMF schedules or notifications are mutations needing approval; new tasks are created suspended and must be resumed deliberately.
- Account Usage views have latency and retention limits; do not use them for real-time detection, and query them with appropriate privileges.
- Agents and services use least-privilege governed roles and inherit masking and row access policies; never switch to broader roles or bypass policies, and do not log sensitive query text or results without approved retention.
- Never hard-code credentials; use approved secret management and integrations.
- Incident response: triage severity, assign an owner, communicate impact, preserve evidence (query history, logs, snapshots), avoid uncoordinated fixes, make failures visible and run a blameless postmortem with follow-up actions.
- Validate gates and monitors by triggering known failures in a safe environment; do not claim coverage or alerting from configuration alone.

### Execution Steps

1. Inventory current checks, metrics, lineage, consumers and monitoring; profile the data with bounded read-only queries.
2. Implement or update versioned checks, metric definitions and migrations within approved scope.
3. Run framework tests and validate gates, monitors and migrations against non-production or known-failure data.
4. Report checks, thresholds rationale, changed objects, approvals, evidence and remaining gaps.

### Validation

- Checks versioned, profiled and wired into automated gates with documented severity.
- Metrics canonical with owner, calculation and lineage; duplicates reconciled.
- Schema changes backward compatible or explicitly approved with rollback.
- Monitors and alerts approved, resumed deliberately and tested; governed roles and secrets respected.

## References

- [Snowflake data quality and DMFs](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [DMF expectations](https://docs.snowflake.com/en/sql-reference/functions/data_metric_function_expectations)
- [Snowflake governance](https://docs.snowflake.com/en/guides-overview-govern)
- [dbt data tests](https://docs.getdbt.com/docs/build/data-tests)
- [Great Expectations](https://docs.greatexpectations.io/)
- [Snowflake alerts](https://docs.snowflake.com/en/user-guide/alerts)
