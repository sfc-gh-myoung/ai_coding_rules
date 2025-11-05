**Keywords:** Data governance, data quality, lineage, metadata management, compliance, data catalog
**Depends:** None

**TokenBudget:** ~250
**ContextTier:** Medium

# Data Governance & Quality Directives

## Purpose
Establish comprehensive directives for ensuring data quality, governance, and operational reliability throughout the data lifecycle, using code-based validation, schema evolution management, and automated quality gates.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Data quality, governance, and operational reliability throughout the data lifecycle


## 1. Data Quality as Code
- **Requirement:** Treat data quality as code. Version expectation suites and integrate into CI/CD.
- **Requirement:** Layer expectations: start with schema/basic validity, then add business rules.
- **Requirement:** Keep suites lean and focused; avoid noisy or redundant checks.
- **Always:** Use profiling to discover initial expectations, then manually curate and refine before acceptance.
- **Requirement:** Never hard-code credentials or secrets in data quality configurations.
- **Always:** Integrate validation as a gating step in ETL/ELT pipelines.
- **Always:** Monitor for data drift by tracking distribution changes with thresholds.
- **Always:** Reference Great Expectations docs: https://docs.greatexpectations.io/

## 2. Data Stewardship & Schema Evolution
- **Requirement:** Every metric must have a Single Source of Truth in a catalog, with formula, lineage, and ownership.
- **Requirement:** Version metrics and schemas immutably when updated.
- **Always:** Add new columns first; avoid destructive in-place changes.
- **Always:** For major changes, prepare a communication plan with impact and rollback strategy.
- **Requirement:** Use idempotent migration scripts under version control.
- **Requirement:** Validate that downstream consumers are unaffected before production deployment.
- **Always:** Reference Snowflake schema management docs: https://docs.snowflake.com/en/user-guide/database-schemas

## 3. Data Observability
- **Always:** Implement observability to monitor freshness, volume, and schema changes.
- **Always:** Use Snowflake Tasks to automate freshness checks and other metrics.
- **Always:** Create automated alerts for anomalies and quality failures.

## 4. Incident Response & Reliability
- **Always:** Respond with a clear plan; triage severity and assign an incident commander.
- **Requirement:** Avoid uncoordinated fixes; log all actions with timestamps.
- **Requirement:** After stabilization, run a blameless postmortem focusing on systems/processes.
- **Requirement:** Preserve all evidence (logs, query history) until root cause is identified.
- **Requirement:** Make failures visible; avoid silent failures.

## Final Self-Audit Checklist
- **Always:** Ensure all changes comply with these rules.
- **Always:** Confirm the solution addresses the problem with a clear plan.
- **Always:** Verify that the solution promotes data quality, stewardship, and reliability.

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Data Management Body of Knowledge (DMBOK)](https://www.dama.org/cpages/body-of-knowledge) - Comprehensive data management framework                                                                                  
- [Data Quality Assessment](https://www.dataversity.net/data-quality-assessment/) - Data quality evaluation methodologies                                                                                               
- [Incident Response Best Practices](https://www.sans.org/white-papers/incident-response/) - SANS incident response guidelines

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Security**: `107-snowflake-security-governance.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
