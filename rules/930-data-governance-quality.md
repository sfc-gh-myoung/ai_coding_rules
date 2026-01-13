# Data Governance & Quality Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** Data governance, data quality, lineage, metadata management, compliance, data catalog, Great Expectations, schema evolution, data observability, incident response
**TokenBudget:** ~2050
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

- Data quality as code (version expectation suites in Git)
- Data profiling before creating expectations
- Schema evolution (add columns first, avoid destructive changes)
- Single source of truth for metric definitions
- Automated quality gates in ETL/ELT pipelines
- Data drift monitoring with thresholds
- Secrets management (no hard-coded credentials)

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

## Anti-Patterns and Common Mistakes

### Pattern 1: Hard-Coded Thresholds Without Profiling

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

### Pattern 2: Destructive Schema Changes in Production

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

## Data Quality as Code
- **Requirement:** Treat data quality as code. Version expectation suites and integrate into CI/CD.
- **Requirement:** Layer expectations: start with schema/basic validity, then add business rules.
- **Requirement:** Keep suites lean and focused; avoid noisy or redundant checks.
- **Always:** Use profiling to discover initial expectations, then manually curate and refine before acceptance.
- **Requirement:** Never hard-code credentials or secrets in data quality configurations.
- **Always:** Integrate validation as a gating step in ETL/ELT pipelines.
- **Always:** Monitor for data drift by tracking distribution changes. Threshold: >10% shift in mean, median, or standard deviation triggers alert.
- **Always:** Reference Great Expectations docs: https://docs.greatexpectations.io/

## Data Stewardship and Schema Evolution
- **Requirement:** Every metric must have a Single Source of Truth in a catalog, with formula, lineage, and ownership.
- **Requirement:** Version metrics and schemas immutably when updated.
- **Always:** Add new columns first; avoid destructive in-place changes.
- **Always:** For major changes (>3 columns modified, data type changes, or breaking API contracts), prepare a communication plan with impact and rollback strategy.
- **Requirement:** Use idempotent migration scripts under version control.
- **Requirement:** Validate that downstream consumers are unaffected before production deployment.
- **Always:** Reference Snowflake schema management docs: https://docs.snowflake.com/en/user-guide/database-schemas

## Data Observability
- **Always:** Implement observability to monitor freshness, volume, and schema changes.
- **Always:** Use Snowflake Tasks to automate freshness checks and other metrics.
- **Always:** Create automated alerts for anomalies and quality failures.

## Incident Response and Reliability
- **Always:** Respond with a clear plan; triage severity and assign an incident commander.
- **Requirement:** Avoid uncoordinated fixes; log all actions with timestamps.
- **Requirement:** After stabilization, run a blameless postmortem focusing on systems/processes.
- **Requirement:** Preserve all evidence (logs, query history) until root cause is identified.
- **Requirement:** Make failures visible; avoid silent failures.

## Final Self-Audit Checklist
- **Always:** Ensure all changes comply with these rules.
- **Always:** Confirm the solution addresses the problem with a clear plan.
- **Always:** Verify that the solution promotes data quality, stewardship, and reliability.
