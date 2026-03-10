# Data Governance & Quality Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Data governance, data quality, lineage, metadata management, compliance, data catalog, Great Expectations, schema evolution, data observability, incident response
**TokenBudget:** ~4300
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Comprehensive directives for ensuring data quality, governance, and operational reliability throughout the data lifecycle. Covers code-based validation, schema evolution management, automated quality gates, data lineage, and incident response.

**When to Load This Rule:**
- Implementing data quality validation frameworks
- Managing schema evolution and migrations
- Setting up automated quality gates in pipelines
- Establishing data governance policies
- Monitoring data drift and observability
- Defining incident response procedures for data issues

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **100-snowflake-core.md** - Snowflake SQL patterns
- **124-snowflake-data-quality-core.md** - Snowflake-specific data quality patterns
- **132-snowflake-demo-modeling.md** - Data modeling standards

### External Documentation

- [Great Expectations Documentation](https://docs.greatexpectations.io/) - Data quality validation framework
- [Snowflake Data Governance](https://docs.snowflake.com/en/user-guide/governance) - Governance features and best practices

## Contract

### Inputs and Prerequisites

- Data quality validation framework (Great Expectations, Snowflake DMFs)
- Version control system (Git) for expectation suites
- Data catalog or metadata management system
- CI/CD pipeline for automated quality gates
- Schema evolution strategy defined

### Mandatory

- MUST implement data quality as code (version expectation suites in Git)
- MUST profile data distributions before creating expectations
- MUST use non-destructive schema evolution (add columns first, avoid destructive changes)
- MUST maintain a single source of truth for metric definitions

  **Implementation Pattern — Metric Definitions File:**
  ```yaml
  # metrics/metric_definitions.yml (version-controlled)
  metrics:
    monthly_recurring_revenue:
      display_name: "Monthly Recurring Revenue (MRR)"
      formula: "SUM(subscription_amount) WHERE status = 'active' AND date = last_day_of_month"
      owner: "Finance Team"
      update_frequency: "Daily at 00:00 UTC"
      data_source: "DB.ANALYTICS.SUBSCRIPTIONS"
      lineage:
        - "RAW.STRIPE.INVOICES"
        - "STAGING.STG_SUBSCRIPTIONS"
      quality_checks:
        - "not_null"
        - "positive_value"
      last_reviewed: "2026-03-01"

    customer_churn_rate:
      display_name: "Customer Churn Rate (%)"
      formula: "(COUNT(churned_customers) / COUNT(total_customers_start)) * 100"
      owner: "Customer Success"
      update_frequency: "Monthly"
      data_source: "DB.ANALYTICS.CUSTOMER_LIFECYCLE"
      lineage:
        - "RAW.CRM.ACCOUNTS"
        - "STAGING.STG_CUSTOMER_STATUS"
      quality_checks:
        - "between_0_and_100"
        - "not_null"
      last_reviewed: "2026-02-15"
  ```

  **dbt Alternative — Semantic Models:**
  ```yaml
  # models/staging/schema.yml
  semantic_models:
    - name: revenue_metrics
      description: "Single source of truth for revenue calculations"
      model: ref('fct_revenue')
      entities:
        - name: transaction_id
          type: primary
      measures:
        - name: total_revenue
          agg: sum
          expr: amount
          description: "Total revenue from all sources"
        - name: order_count
          agg: count
          expr: order_id
  ```

  Every metric MUST have: name, formula, owner, update_frequency, data_source, and lineage. Store in version control alongside expectation suites.
- MUST automate quality gates in ETL/ELT pipelines
- MUST implement data drift monitoring with thresholds
- MUST use secrets management (no hard-coded credentials)

### Forbidden

- Hard-coded credentials in code or configuration files
- Destructive schema changes without backward compatibility
- Unversioned expectation suites or quality rules
- Manual quality checks without automation
- Undocumented metric definitions

### Execution Steps

1. Profile data to discover initial quality checks and distributions
2. Create expectation suites based on profiling results
3. Version expectation suites in Git
4. Integrate quality gates into ETL/ELT pipelines
5. Document metric definitions in data catalog
6. Set up data drift monitoring with thresholds
7. Define incident response plan for data quality issues
8. Implement schema evolution strategy (add columns, avoid destructive changes)
9. Validate quality gates in CI/CD
10. Monitor and iterate on quality expectations

### Output Format

- Expectation suites versioned in Git
- Data quality reports with pass/fail status
- Schema evolution documentation
- Metric definitions in data catalog
- Incident response runbooks
- Data drift monitoring dashboards

### Validation

**Pre-Task-Completion Checks:**
- Expectation suites in version control
- Data profiling completed
- Schema changes non-destructive
- Metrics documented in catalog
- Quality gates integrated in CI/CD
- Drift monitoring configured (>10% distribution shift threshold)
- Incident response plan documented

**During-Execution Monitoring:**
- Quality gate pass/fail rates tracked per pipeline run
- Data drift metrics collected at each checkpoint
- Schema validation runs before and after migrations
- Alert channels (Slack, PagerDuty) receiving notifications

**Success Criteria:**
- All expectation suites pass validation
- Schema changes backward compatible
- Quality gates automated in pipelines
- Metrics have single source of truth
- Data drift alerts configured
- Incident response plan tested

**Negative Tests:**
- Hard-coded credentials should trigger security scan failure
- Destructive schema changes should fail review
- Unversioned expectations should fail compliance check
- Manual quality checks should trigger automation requirement

### Design Principles

- **Data Quality as Code:** Version all quality rules and expectations
- **Profile First:** Use data profiling to discover initial checks
- **Non-Destructive Evolution:** Add columns, avoid breaking changes
- **Single Source of Truth:** One canonical definition per metric
- **Automate Everything:** Quality gates in CI/CD, not manual checks
- **Monitor Drift:** Track distribution changes with thresholds
- **Secure by Default:** Use secrets management, never hard-code credentials

### Post-Execution Checklist

- [ ] Expectation suites versioned in Git
- [ ] Data profiling completed and documented
- [ ] Schema changes non-destructive and backward compatible
- [ ] All metrics documented in data catalog with single source of truth
- [ ] Quality gates integrated into CI/CD pipelines
- [ ] Data drift monitoring configured with thresholds
- [ ] Incident response plan documented and tested
- [ ] Secrets management implemented (no hard-coded credentials)
- [ ] Quality validation automated (no manual checks)
- [ ] Schema evolution strategy documented

### Investigation Required

Before implementing data governance changes, investigate the following:

1. **Inventory existing quality checks:** Identify all ad-hoc queries, manual processes, and existing automated checks. Document what is currently validated and what gaps exist.
2. **Map data lineage for critical tables:** Trace upstream sources and downstream consumers for each table targeted by governance policies. Use `SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY` to discover actual access patterns.
3. **Identify current metric definitions and their locations:** Find all places where metrics are defined (dashboards, notebooks, SQL scripts, dbt models). Flag duplicates and conflicts.
4. **Review schema change history for breaking patterns:** Query `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` for ALTER TABLE statements in the past 90 days. Identify tables with frequent schema changes.
5. **Check existing monitoring and alerting infrastructure:** Determine what monitoring tools are in place (Snowflake Alerts, Tasks, external tools). Identify coverage gaps for freshness, volume, and schema drift.

```
⚠️ Investigation Required: Complete items 1-5 above before proceeding with governance implementation. Results inform which quality gates, monitoring thresholds, and incident response procedures to configure.
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hard-Coded Thresholds Without Profiling

**Problem:**
Creating expectation suites with arbitrary thresholds (e.g., "column must be >0") without first profiling actual data distributions.

**Why It Fails:**
Thresholds that don't reflect real data patterns generate false positives (noise) or miss real anomalies. Teams disable noisy checks, defeating the purpose.

**Correct Pattern:**
```python
# WRONG: Arbitrary threshold
expectation_suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "price", "min_value": 0, "max_value": 1000}
    )
)

# CORRECT: Profile first, then set thresholds
profile_result = profiler.profile(batch)
stats = profile_result.columns["price"]
expectation_suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "price",
            "min_value": stats["min"] * 0.9,  # 10% buffer
            "max_value": stats["max"] * 1.1
        }
    )
)
```

### Anti-Pattern 2: Destructive Schema Changes in Production

**Problem:**
Dropping or renaming columns, changing data types, or deleting tables without backward compatibility period.

**Why It Fails:**
Downstream consumers (dashboards, ETL jobs, APIs) break immediately. No rollback path if issues discovered post-deployment.

**Correct Pattern:**
```sql
-- WRONG: Destructive change
ALTER TABLE orders DROP COLUMN legacy_status;
ALTER TABLE orders RENAME COLUMN status TO order_status;

-- CORRECT: Non-destructive evolution
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN order_status VARCHAR;

-- Step 2: Populate new column
UPDATE orders SET order_status = status;

-- Step 3: Mark old column deprecated (comment + docs)
COMMENT ON COLUMN orders.status IS 'DEPRECATED: Use order_status. Removal date: 2026-04-01';

-- Step 4: After 90-day deprecation period, drop old column
-- ALTER TABLE orders DROP COLUMN status;
```

### Anti-Pattern 3: Manual Quality Checks Without Automation

**Problem:**
Running ad-hoc SQL queries to verify data quality instead of using automated validation frameworks.

**Why It Fails:**
Manual checks are inconsistent, not repeatable, and don't scale. They rely on individual knowledge, get skipped under time pressure, and leave no audit trail.

**Correct Pattern:**
```python
# BAD: Manual SQL queries for quality checks
# A developer runs this ad-hoc before each release:
# SELECT COUNT(*) FROM orders WHERE amount < 0;
# SELECT COUNT(DISTINCT customer_id) FROM orders;

# GOOD: Automated Great Expectations or dbt tests
# great_expectations/expectations/orders_suite.json (version-controlled)
expectation_suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "amount", "min_value": 0}
    )
)
# Runs automatically in CI/CD pipeline on every deployment
context.run_checkpoint(checkpoint_name="orders_quality_gate")
```

### Anti-Pattern 4: Unversioned Expectation Suites

**Problem:**
Defining quality rules ad-hoc in scripts or notebooks without version control, making them impossible to audit, review, or roll back.

**Why It Fails:**
Without version control, there is no history of rule changes, no peer review, and no way to correlate a quality regression with a specific rule modification. Teams lose track of what is validated and why.

**Correct Pattern:**
```yaml
# BAD: Ad-hoc quality rules in a notebook or one-off script
# Cell 1: check nulls... Cell 2: check ranges... (no history, no review)

# GOOD: Version-controlled expectation files in Git
# great_expectations/expectations/orders_suite.json
# - Committed to Git with meaningful commit messages
# - Changes go through pull request review
# - CI validates expectation suite syntax on every push

# dbt alternative: version-controlled schema tests
# models/staging/schema.yml
version: 2
models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
```

## Data Stewardship and Schema Evolution
- **Requirement:** Every metric must have a Single Source of Truth in a catalog, with formula, lineage, and ownership.
- **Requirement:** Version metrics and schemas immutably when updated.
- **Always:** Add new columns first; avoid destructive in-place changes.
- **Always:** For major changes (>3 columns modified, data type changes, or breaking API contracts), prepare a communication plan with impact and rollback strategy.
- **Requirement:** Use idempotent migration scripts under version control.
- **Requirement:** Validate that downstream consumers are unaffected before production deployment.
- **Always:** Reference Snowflake schema management docs: https://docs.snowflake.com/en/user-guide/database-schemas

**Deprecation Pattern:**
```sql
-- Mark column as deprecated with removal date
COMMENT ON COLUMN orders.legacy_status IS
  'DEPRECATED: Use order_status instead. Removal date: 2026-06-01. Migration: UPDATE orders SET order_status = legacy_status;';

-- Track deprecations in a governance table
INSERT INTO governance.column_deprecations (table_name, column_name, replacement, deprecation_date, removal_date, migration_sql)
VALUES ('orders', 'legacy_status', 'order_status', '2026-03-09', '2026-06-01',
        'UPDATE orders SET order_status = legacy_status');
```

## Data Observability
- **Always:** Implement observability to monitor freshness, volume, and schema changes.
- **Always:** Use Snowflake Tasks to automate freshness checks and other metrics.
- **Always:** Create automated alerts for anomalies and quality failures.

**Freshness Check Task:**
```sql
-- Automated freshness monitoring with Snowflake Tasks
CREATE OR REPLACE TASK governance.check_data_freshness
  WAREHOUSE = 'GOVERNANCE_WH'
  SCHEDULE = 'USING CRON 0 * * * * America/New_York'
AS
  INSERT INTO governance.freshness_log (table_name, last_updated, check_time, is_stale)
  SELECT 'ANALYTICS.SALES_FACT',
         MAX(updated_at),
         CURRENT_TIMESTAMP(),
         CASE WHEN DATEDIFF('hour', MAX(updated_at), CURRENT_TIMESTAMP()) > 4
              THEN TRUE ELSE FALSE END
  FROM analytics.sales_fact;

-- Alert on stale data
CREATE OR REPLACE ALERT governance.stale_data_alert
  WAREHOUSE = 'GOVERNANCE_WH'
  SCHEDULE = 'USING CRON 0 * * * * America/New_York'
  IF (EXISTS (SELECT 1 FROM governance.freshness_log WHERE is_stale = TRUE AND check_time > DATEADD('hour', -1, CURRENT_TIMESTAMP())))
  THEN CALL SYSTEM$SEND_EMAIL('ops-alerts', 'Data Freshness Alert', 'Stale data detected. Check governance.freshness_log.');
```

## Incident Response and Reliability
- **Always:** Respond with a clear plan; triage severity and assign an incident commander.
- **Requirement:** Avoid uncoordinated fixes; log all actions with timestamps.
- **Requirement:** After stabilization, run a blameless postmortem focusing on systems/processes.
- **Requirement:** Preserve all evidence (logs, query history) until root cause is identified.
- **Requirement:** Make failures visible; avoid silent failures.

**Incident Log Schema:**
```sql
CREATE TABLE IF NOT EXISTS governance.incident_log (
    incident_id VARCHAR DEFAULT UUID_STRING(),
    severity VARCHAR NOT NULL,          -- P1, P2, P3, P4
    title VARCHAR NOT NULL,
    affected_tables ARRAY,
    incident_commander VARCHAR,
    opened_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    resolved_at TIMESTAMP_NTZ,
    root_cause VARCHAR,
    actions_taken ARRAY,
    postmortem_url VARCHAR,
    status VARCHAR DEFAULT 'OPEN'       -- OPEN, INVESTIGATING, MITIGATED, RESOLVED
);

-- Log an action during incident response
INSERT INTO governance.incident_log (severity, title, affected_tables, incident_commander)
VALUES ('P2', 'Revenue metrics showing NULL for APAC region',
        ARRAY_CONSTRUCT('ANALYTICS.SALES_FACT', 'STAGING.STG_ORDERS'),
        'data-eng-oncall@company.com');
```

## AI Agent Integration

- Agents MUST respect data governance policies (masking, row-level security) when querying data
- Agents SHOULD use the data catalog as the authoritative source for metric definitions
- Agent-generated queries MUST go through the same quality gates as human-authored queries
- Log agent data access for audit trail compliance
- Expose governance metadata (sensitivity labels, ownership) to agents via structured APIs

**Governance-Aware Agent Query Pattern:**
```python
from snowflake.snowpark import Session
from datetime import datetime
import logging

logger = logging.getLogger("agent_governance")

def governance_aware_query(
    session: Session,
    query: str,
    agent_id: str,
    purpose: str
) -> list:
    """Execute a query with governance checks and audit logging."""
    # 1. Log agent access for audit trail
    session.sql(f"""
        INSERT INTO governance.agent_access_log
            (agent_id, query_text, purpose, executed_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP())
    """, params=[agent_id, query, purpose]).collect()

    # 2. Validate query goes through quality gates
    # Agent queries use the same governed role as human queries
    session.sql("USE ROLE DATA_READER").collect()

    # 3. Execute with row-level security and masking active
    results = session.sql(query).collect()

    logger.info(f"Agent {agent_id} executed query for '{purpose}', "
                f"returned {len(results)} rows")
    return results


def get_metric_definition(session: Session, metric_name: str) -> dict:
    """Look up metric from the single source of truth (data catalog)."""
    result = session.sql(f"""
        SELECT metric_name, formula, owner, update_frequency, data_source
        FROM governance.metric_catalog
        WHERE metric_name = ?
    """, params=[metric_name]).collect()

    if not result:
        return {"error": f"Unknown metric: {metric_name}. "
                "Check governance.metric_catalog for available metrics."}
    row = result[0]
    return {
        "metric_name": row["METRIC_NAME"],
        "formula": row["FORMULA"],
        "owner": row["OWNER"],
        "update_frequency": row["UPDATE_FREQUENCY"],
        "data_source": row["DATA_SOURCE"]
    }
```

**Agent Access Log Table:**
```sql
CREATE TABLE IF NOT EXISTS governance.agent_access_log (
    log_id VARCHAR DEFAULT UUID_STRING(),
    agent_id VARCHAR NOT NULL,
    query_text VARCHAR NOT NULL,
    purpose VARCHAR,
    executed_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    row_count INTEGER,
    status VARCHAR DEFAULT 'SUCCESS'
);
```

## Data Catalog CLI Reference

Use Snowflake CLI for quick metadata inspection:

```bash
# Describe a table's schema and metadata
snow object describe table DB.SCHEMA.TABLE_NAME

# Run ad-hoc governance queries
snow sql -q "SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY LIMIT 10"
```

See also: `snow object list`, `snow sql` for interactive exploration.
