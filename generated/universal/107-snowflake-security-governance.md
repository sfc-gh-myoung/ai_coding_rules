**Keywords:** Masking policies, row access policies, column masking, data governance, tagging, RBAC, roles, grants, secure views
**Depends:** 100-snowflake-core

**TokenBudget:** ~250
**ContextTier:** High

# Snowflake Security Governance

## Purpose
Establish comprehensive data security and access control practices using Snowflake's governance features, including RBAC, data masking, row-level security, and object tagging for enterprise-grade data protection.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake security governance, RBAC, data masking, access control policies, and data quality monitoring best practices


## Key Principles
- Enforce least-privilege RBAC; use role hierarchies; map roles to business responsibilities.
- Protect data with masking policies, row access policies, and object tagging.
- Reference official docs for RBAC, masking, row access, and tagging.
- Integrate data quality monitoring using Data Metric Functions (DMFs) with clear expectations and alerts.
- Apply least privilege for DMF execution (EXECUTE DATA METRIC FUNCTION) and ownership.
- Use data profiling to baseline and discover issues; do not substitute for security policies.

## 1. Access Control
- **Requirement:** Implement Role-Based Access Control (RBAC) following least privilege.
- **Requirement:** Use role hierarchies to simplify permission management and inherit privileges.
- **Always:** Define functional roles that map directly to business responsibilities.

## 2. Data Protection Policies
- **Always:** Use masking policies to dynamically mask or tokenize sensitive data in columns.
- **Always:** Use row access policies to enforce row-level security based on a user's role or other session context.
- **Always:** Apply object tagging to classify data for governance purposes (e.g., PII, `SENSITIVITY_LEVEL`). See `123-snowflake-object-tagging.md` for comprehensive tagging patterns including tag-based masking policies.

## 3. Data Quality Monitoring (DMFs)
- **Always:** Use Data Metric Functions (DMFs) to measure and monitor quality metrics (e.g., NULL counts, duplicates, freshness). System DMFs are available in `SNOWFLAKE.CORE`; create custom DMFs for domain-specific checks.
- **Requirement:** Associate DMFs to supported objects (tables, views, dynamic tables, external tables, Iceberg tables, materialized views, event tables) and schedule evaluations; results are recorded in the dedicated event table for DMFs.
- **Always:** Define expectations for each DMF association to determine pass/fail thresholds. Use alerts to notify owners on failures to drive remediation.
- **Rule:** Enterprise Edition is required. DMFs use serverless compute; billing appears under "Data Quality Monitoring". Unscheduled ad-hoc SELECTs of DMFs are not billed.
- **Rule:** Monitor consumption and performance via `DATA_QUALITY_MONITORING_USAGE_HISTORY` and Snowsight monitoring pages.
- **Requirement:** Enforce least privilege for DMFs. The table/view owner role must have the global `EXECUTE DATA METRIC FUNCTION` privilege. Database roles cannot receive global privileges; transfer ownership to an account-scoped role if needed.
- **Requirement:** Document and operate within limitations: maximum 10,000 DMF-object associations per account; cannot set DMFs on shared objects or in reader accounts; cannot set DMFs on object tags.
- **Rule:** Establish a remediation workflow: investigate failures, triage severity, correct data/process, and track resolution SLAs.
- **Avoid:** Relying on DMFs alone for protection. Combine DMFs with masking, row access, and tags for comprehensive governance.
- **Note:** For comprehensive Data Quality Monitoring guidance including system/custom DMFs, data profiling, expectations, scheduling, and cost management, see `124-snowflake-data-quality.md`.

## 4. Data Profiling
- **Always:** Use Snowflake Data Profile to baseline datasets (distributions, distinct counts, NULLs) and to inform policy design and DMF selection.
- **Rule:** Profile sensitive datasets in segregated roles/warehouses to minimize blast radius and ensure least privilege during exploration.
- **Rule:** Use profiling insights to refine masking policies, row access rules, and to prioritize DMFs for high-risk columns.
- **Avoid:** Treating profiling as a one-time activity; re-profile after schema or source changes.

## 5. Operational Monitoring & Cost
- **Always:** Track DMF schedules, results, and alerts in Snowsight; review event table outputs for trends and recurrence of failures.
- **Rule:** Monitor serverless credits under the “Data Quality Monitoring” category and the logging service (“Logging”). Right-size schedules and scopes to control cost.
- **Rule:** Version and review DMF definitions alongside application code; maintain owners, runbooks, and SLAs.
- **Requirement:** Separate duties: creators of DMFs and operators of alerts should be distinct from data producers when feasible.

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
- [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) - RBAC, roles, and privilege management                                                                          
- [Column-Level Security](https://docs.snowflake.com/en/user-guide/security-column-intro) - Dynamic data masking and column-level policies                                                                              
- [Row-Level Security](https://docs.snowflake.com/en/user-guide/security-row-intro) - Row access policies and conditional data access                                                                                   
- [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) - Metadata tagging for governance and classification
- [Introduction to data quality and DMFs](https://docs.snowflake.com/en/user-guide/data-quality-intro) - Data metric functions, expectations, scheduling, billing
- [Data Profile](https://docs.snowflake.com/en/user-guide/data-quality-profile) - Profiling datasets to baseline and discover issues
- [Working with data quality](https://docs.snowflake.com/en/user-guide/data-quality-working) - Associate, schedule, monitor, and manage DMFs

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Object Tagging**: `123-snowflake-object-tagging.md`
- **Data Quality Monitoring**: `124-snowflake-data-quality.md`
- **Data Governance**: `600-data-governance-quality.md`
