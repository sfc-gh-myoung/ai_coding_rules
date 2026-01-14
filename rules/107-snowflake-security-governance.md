# Snowflake Security Governance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** roles, grants, secure views, security policies, access control, data security, policy troubleshooting, grant management, Data Metric Functions, DMF, least privilege, create masking policy, tagging, SQL
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Comprehensive data security and access control practices using Snowflake's governance features, including RBAC, data masking, row-level security, and object tagging for enterprise-grade data protection.

**When to Load This Rule:**
- Implementing role-based access control (RBAC)
- Creating data masking and row access policies
- Setting up security governance frameworks
- Managing object tagging for compliance
- Troubleshooting access control issues

### Quantification Standards

**Security and Governance Thresholds:**
- **Over-privileged role:** >5 direct privilege grants OR direct ACCOUNTADMIN inheritance
- **Excessive comment length:** >500 characters per comment (aim for 50-200 characters)
- **Role assignment limit:** User with >3 role assignments requires review
- **Privilege audit trigger:** Role with ALL privileges on schema (use specific grants instead)

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
**Closely Related** (consider loading together):
- **100-snowflake-core.md** - fundamental DDL patterns and object creation
- **105-snowflake-cost-governance.md** - RBAC on resource monitors and cost controls

**Sometimes Related** (load if specific scenario):
- **106-snowflake-semantic-views-core.md** - applying masking policies and row access to semantic views
- **119-snowflake-warehouse-management.md** - configuring warehouse access control and RBAC
- **115b-snowflake-cortex-agents-operations.md** - implementing agent RBAC and security

**Complementary** (different aspects of same domain):
- **111-snowflake-observability-core.md** - security event monitoring and audit logs
- **108-snowflake-data-loading.md** - stage encryption and secure data loading

## Contract

### Inputs and Prerequisites

- Snowflake account with SECURITYADMIN or ACCOUNTADMIN privileges
- Data classification completed (PII, PHI, confidential, public)
- Compliance requirements identified (GDPR, HIPAA, SOC 2, etc.)
- Business role definitions and responsibilities documented
- Understanding of data access patterns and user personas
- Existing schema and table inventory

### Mandatory

- RBAC implementation: CREATE ROLE, GRANT commands
- Role hierarchy design: Functional roles -> Access roles -> User assignments
- Masking policies: CREATE MASKING POLICY for PII/PHI columns
- Row access policies: CREATE ROW ACCESS POLICY for multi-tenant data
- Object tagging: CREATE TAG, ALTER ... SET TAG for governance metadata
- Data Metric Functions (DMFs): CREATE DATA METRIC FUNCTION for quality monitoring
- GRANT EXECUTE DATA METRIC FUNCTION with least privilege
- Secure views: CREATE SECURE VIEW for controlled data access
- Future grants: GRANT ... ON FUTURE TABLES for automated inheritance

### Forbidden

- Direct SELECT grants on raw PII tables without masking
- Over-privileged roles (>5 direct privilege grants OR granting ACCOUNTADMIN for application use)
- Hardcoding passwords or credentials in SQL scripts
- Exposing raw PII in views, UDFs, or stored procedures
- Granting ownership without role hierarchy justification
- Creating DMFs without clear expectations and alert thresholds
- Skipping data profiling before implementing quality checks

### Execution Steps

1. Design role hierarchy: Map business functions to Snowflake roles
2. Create functional roles (e.g., DATA_ENGINEER, ANALYST, BI_DEVELOPER)
3. Create access roles (e.g., READ_ONLY_SALES, WRITE_MARKETING)
4. Grant object privileges to access roles (SELECT, INSERT, UPDATE)
5. Grant access roles to functional roles (role hierarchy)
6. Create masking policies for PII columns (SSN, email, credit card, phone)
7. Apply masking policies: ALTER TABLE ... ALTER COLUMN ... SET MASKING POLICY
8. Create row access policies for multi-tenant or region-restricted data
9. Apply row access policies: ALTER TABLE ... ADD ROW ACCESS POLICY
10. Create and apply tags for cost attribution, data classification, compliance
11. Create Data Metric Functions for critical quality checks (NULL detection, freshness)
12. Schedule DMFs with appropriate warehouses and notification targets
13. Verify with test queries from different roles to confirm policy enforcement

### Output Format

- Role hierarchy diagram showing functional -> access -> user assignments
- DDL scripts: CREATE ROLE, GRANT, masking policies, row access policies
- Masking policy definitions with exemption roles (for data stewards)
- Row access policy logic with clear filtering conditions
- Tag taxonomy: Tag names, allowed values, application strategy
- DMF definitions: Expectations, schedules, alert thresholds
- Documentation: Access control matrix, compliance mappings, runbook

### Validation

**Test Requirements:**
- Roles created: SHOW ROLES, verify hierarchy with SHOW GRANTS
- Masking policies active: Query as non-privileged role, verify masked data
- Row access policies enforced: Query as different users, verify filtered results
- Tags applied: SELECT SYSTEM$GET_TAG() for tagged objects
- DMFs scheduled: SHOW DATA METRIC FUNCTIONS, check Task History for execution
- No direct PII access for analyst roles
- Least privilege verified: Attempt unauthorized operations, confirm denial

**Success Criteria:**
- Role hierarchy follows least privilege principle
- PII columns masked for unauthorized roles
- Row access policies enforce tenant/region isolation
- Tags enable cost attribution and compliance reporting
- DMFs detect quality issues and trigger alerts
- Secure views prevent data exfiltration
- Future grants automate access control for new objects
- Compliance requirements met (GDPR right to be forgotten, HIPAA audit trails)

### Design Principles

- Enforce least-privilege RBAC; use role hierarchies; map roles to business responsibilities.
- Protect data with masking policies, row access policies, and object tagging.
- Reference official docs for RBAC, masking, row access, and tagging.
- Integrate data quality monitoring using Data Metric Functions (DMFs) with clear expectations and alerts.
- Apply least privilege for DMF execution (EXECUTE DATA METRIC FUNCTION) and ownership.
- Use data profiling to baseline and discover issues; do not substitute for security policies.

### Post-Execution Checklist

- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Granting SELECT on Raw PII Tables Without Masking**
```sql
-- Bad: Direct SELECT grants expose sensitive data
GRANT SELECT ON TABLE customers TO ROLE analyst_role;
-- Analysts now see raw SSN, credit card numbers, email addresses
```
**Problem:** Violates least privilege; exposes PII to unauthorized users; compliance violations (GDPR, HIPAA); no audit trail of sensitive data access; security breach risk

**Correct Pattern:**
```sql
-- Good: Create masking policy and apply to PII columns
CREATE OR REPLACE MASKING POLICY ssn_mask AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('COMPLIANCE_ADMIN') THEN val
    ELSE '***-**-' || SUBSTRING(val, 8, 4)  -- Show last 4 digits only
  END;

ALTER TABLE customers MODIFY COLUMN ssn
  SET MASKING POLICY ssn_mask;

-- Now grant SELECT - analysts see masked data
GRANT SELECT ON TABLE customers TO ROLE analyst_role;
```
**Benefits:** Least privilege enforcement; PII protected; role-based unmasking; compliance-ready; audit trail via POLICY_REFERENCES

**Anti-Pattern 2: Not Using Role Hierarchies for Permission Management**
```sql
-- Bad: Granting same permissions to many roles individually
GRANT SELECT ON DATABASE prod_db TO ROLE analyst1;
GRANT SELECT ON DATABASE prod_db TO ROLE analyst2;
GRANT SELECT ON DATABASE prod_db TO ROLE analyst3;
-- [Repeat for 50 analysts...]
```
**Problem:** Maintenance nightmare; permission drift across users; inconsistent access; manual revocation on offboarding; can't bulk update permissions; audit complexity

**Correct Pattern:**
```sql
-- Good: Role hierarchy with inherited permissions
CREATE ROLE analyst_base;
GRANT SELECT ON DATABASE prod_db TO ROLE analyst_base;

-- Create child roles that inherit from base
CREATE ROLE analyst1;
CREATE ROLE analyst2;
CREATE ROLE analyst3;

GRANT ROLE analyst_base TO ROLE analyst1;
GRANT ROLE analyst_base TO ROLE analyst2;
GRANT ROLE analyst_base TO ROLE analyst3;

-- Single permission change affects all analysts
REVOKE SELECT ON SCHEMA prod_db.sensitive FROM ROLE analyst_base;
```
**Benefits:** Centralized permission management; consistent access patterns; easy bulk updates; role inheritance reduces grants; simplified audit; efficient onboarding/offboarding

**Anti-Pattern 3: Missing Row Access Policies for Multi-Tenant Data**
```sql
-- Bad: All users see all tenant data
CREATE TABLE customer_orders (
  order_id NUMBER,
  customer_id NUMBER,
  tenant_id NUMBER,
  order_total NUMBER
);

GRANT SELECT ON TABLE customer_orders TO ROLE analyst_role;
-- Analysts from Tenant A can see Tenant B's data!
```
**Problem:** Data leakage across tenants; compliance violations; security breach; no tenant isolation; trust erosion; manual WHERE clause filtering unreliable

**Correct Pattern:**
```sql
-- Good: Row Access Policy enforces tenant isolation
CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation AS (tenant_id NUMBER) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'SYSADMIN' THEN TRUE
    ELSE tenant_id = CURRENT_ACCOUNT()  -- Or lookup user's tenant_id from mapping table
  END;

ALTER TABLE customer_orders
  ADD ROW ACCESS POLICY tenant_isolation ON (tenant_id);

-- Now SELECT automatically filters to user's tenant
GRANT SELECT ON TABLE customer_orders TO ROLE analyst_role;
```
**Benefits:** Automatic tenant isolation; no manual filtering; centralized security logic; compliance-ready; prevents accidental data leakage; auditable policy

**Anti-Pattern 4: Not Applying Object Tags for Data Classification**
```sql
-- Bad: No metadata about data sensitivity
CREATE TABLE sensitive_data (
  ssn STRING,
  credit_card STRING,
  salary NUMBER
);
-- Can't identify PII tables automatically; no governance automation
```
**Problem:** Can't discover PII tables programmatically; no automated policy application; manual governance doesn't scale; audit gaps; compliance risk; no data catalog

**Correct Pattern:**
```sql
-- Good: Tag-based data classification for automated governance
CREATE TAG sensitivity_level;
CREATE TAG data_classification;

ALTER TABLE sensitive_data SET TAG
  sensitivity_level = 'HIGH',
  data_classification = 'PII';

-- Query all PII tables programmatically:
SELECT
  tag_database,
  tag_schema,
  tag_name,
  tag_value,
  object_name
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_name = 'DATA_CLASSIFICATION'
  AND tag_value = 'PII';

-- Apply masking policies automatically to all PII-tagged columns
```
**Benefits:** Automated PII discovery; tag-based policy application; scalable governance; compliance automation; data catalog integration; consistent classification

## Output Format Examples

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## Access Control
- **Requirement:** Implement Role-Based Access Control (RBAC) following least privilege.
- **Requirement:** Use role hierarchies to simplify permission management and inherit privileges.
- **Always:** Define functional roles that map directly to business responsibilities.

## Data Protection Policies
- **Always:** Use masking policies to dynamically mask or tokenize sensitive data in columns.
- **Always:** Use row access policies to enforce row-level security based on a user's role or other session context.
- **Always:** Apply object tagging to classify data for governance purposes (e.g., PII, `SENSITIVITY_LEVEL`). See `123-snowflake-object-tagging.md` for comprehensive tagging patterns including tag-based masking policies.

## Data Quality Monitoring (DMFs)
- **Always:** Use Data Metric Functions (DMFs) to measure and monitor quality metrics (e.g., NULL counts, duplicates, freshness). System DMFs are available in `SNOWFLAKE.CORE`; create custom DMFs for domain-specific checks.
- **Requirement:** Associate DMFs to supported objects (tables, views, dynamic tables, external tables, Iceberg tables, materialized views, event tables) and schedule evaluations; results are recorded in the dedicated event table for DMFs.
- **Always:** Define expectations for each DMF association to determine pass/fail thresholds. Use alerts to notify owners on failures to drive remediation.
- **Rule:** Enterprise Edition is required. DMFs use serverless compute; billing appears under "Data Quality Monitoring". Unscheduled ad-hoc SELECTs of DMFs are not billed.
- **Rule:** Monitor consumption and performance via `DATA_QUALITY_MONITORING_USAGE_HISTORY` and Snowsight monitoring pages.
- **Requirement:** Enforce least privilege for DMFs. The table/view owner role must have the global `EXECUTE DATA METRIC FUNCTION` privilege. Database roles cannot receive global privileges; transfer ownership to an account-scoped role if needed.
- **Requirement:** Document and operate within limitations: maximum 10,000 DMF-object associations per account; cannot set DMFs on shared objects or in reader accounts; cannot set DMFs on object tags.
- **Rule:** Establish a remediation workflow: investigate failures, triage severity, correct data/process, and track resolution SLAs.
- **Avoid:** Relying on DMFs alone for protection. Combine DMFs with masking, row access, and tags for comprehensive governance.
- **Note:** For comprehensive Data Quality Monitoring guidance including system/custom DMFs, data profiling, expectations, scheduling, and cost management, see `124-snowflake-data-quality-core.md`.

## Data Profiling
- **Always:** Use Snowflake Data Profile to baseline datasets (distributions, distinct counts, NULLs) and to inform policy design and DMF selection.
- **Rule:** Profile sensitive datasets in segregated roles/warehouses to minimize blast radius and ensure least privilege during exploration.
- **Rule:** Use profiling insights to refine masking policies, row access rules, and to prioritize DMFs for high-risk columns.
- **Avoid:** Treating profiling as a one-time activity; re-profile after schema or source changes.

## Operational Monitoring & Cost
- **Always:** Track DMF schedules, results, and alerts in Snowsight; review event table outputs for trends and recurrence of failures.
- **Rule:** Monitor serverless credits under the “Data Quality Monitoring” category and the logging service (“Logging”). Right-size schedules and scopes to control cost.
- **Rule:** Version and review DMF definitions alongside application code; maintain owners, runbooks, and SLAs.
- **Requirement:** Separate duties: creators of DMFs and operators of alerts should be distinct from data producers when feasible.
