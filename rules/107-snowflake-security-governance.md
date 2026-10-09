---
schema_version: v4.0
rule_version: v5.0.0
description: Least-privilege Snowflake roles, masking, tenant isolation, tagging, and governed data-quality monitoring.
last_updated: 2026-10-07
keywords:
  - kw:RBAC role hierarchy
  - kw:masking policy attachment
  - kw:row access policy enforcement
  - kw:object tagging governance
  - kw:data metric function scheduling
  - kw:least privilege grant design
token_budget: ~1300
context_tier: High
depends:
  required:
    - 100-snowflake-core.md
---
# Snowflake Security Governance

## Scope

**What This Rule Covers:**
Access matrices and role inheritance, sensitive-data masking, tenant/region row isolation, classification tags, audit evidence, and quality-monitoring governance.

**When to Load This Rule:**
When designing or reviewing Snowflake RBAC, policies, tagging, data-quality controls, or access failures.

## Contract

### Inputs and Prerequisites

- Approved data classification, business identities/entitlements, access matrix, compliance/recovery requirements, current grants/policies, and ownership.
- Verify operation-specific privileges and edition/object support. Delegated roles can manage authorized controls; SECURITYADMIN/ACCOUNTADMIN are not universal prerequisites. Distinguish creation, policy APPLY, object ownership, grant administration, and read/test permissions.

### Mandatory

- Implement least privilege from actual responsibilities, not arbitrary grant/role-count limits. Keep application/service roles out of account-administration roles; review broad ALL/future grants and ownership transfers against explicit need.
- Model access roles granted to functional roles, then users, with documented inheritance. Granting a role to a parent conveys the child's privileges upward; ownership of a role alone does not inherit its privileges.
- Inspect primary/secondary role context and indirect access. Creation authorization comes from the primary role; test active-role combinations and prevent hidden secondary-role grants from invalidating a denial test.
- Grant object-appropriate privileges: SELECT belongs on supported tables/views, not databases/schemas. Parent access, managed-access schema grant authority, database-role limits, and future grants require explicit review; future grants do not cover existing objects automatically.
- Sensitive access must follow approved classification/entitlements. Mask or otherwise protect unauthorized sensitive fields; do not expose raw values through alternate views, functions, procedures, exports, or logs. Credentials remain in approved secret/auth systems.
- Masking policy signatures and every branch must preserve compatible data types. Partial masks can still reveal information; exemptions require explicit entitlement approval, not a generic ADMIN/service-role shortcut.
- Row-access policies must resolve trusted user/role-to-tenant/region entitlements and deny missing/ambiguous mappings. CURRENT_ACCOUNT is not user tenant identity, and user-set session values are not trusted authorization evidence.
- Apply policies at supported tables/views/columns using verified syntax and privilege requirements. Inspect existing attachments/dependents before changes; use supported policy-body alteration or reviewed versioned migration, not blind replacement of an attached policy.
- Tags classify metadata but do not themselves enforce access; tag-based masking requires configured supported policy bindings. Use approved taxonomy/allowed values and inspect effective attachments/coverage.
- Test allowed and denied identities through actual consumer paths, joins, aggregates, source/derived views, and role hierarchies. Secure views can limit definition/optimizer exposure but do not categorically prevent exfiltration or certify compliance.
- Data quality complements security; it does not replace masking/RBAC. Profile through least-privilege contexts, use system DMFs where suitable and custom DMFs only for distinct checks, and define expectations/owners/remediation SLAs.
- Scheduled DMFs use serverless compute and logging, not a mandatory task warehouse. Verify current supported objects, edition, association limits, execution grants, result access, schedules, and costs; inspect dedicated quality results/usage rather than assuming Task History contains them.
- Version/review policies and quality checks, maintain audit evidence and separation of duties, and re-profile/retest after relevant schema or source changes. No guaranteed GDPR/HIPAA/SOC2 compliance from a checklist.
- Grants, role assignment, policy attachment/removal, tagging, and quality scheduling are authorized mutations. Never self-grant setup privileges or remove protection to complete a test; recovery must preserve protection and affect only approved owned changes.

### Execution Steps

1. Inspect current identity/grant/policy/tag/quality state and document required access, classification, supported features, and ownership.
2. Design least-privilege hierarchy and type-correct masking/row policies, with trusted entitlement mappings and fail-closed behavior.
3. Prepare scoped deployment/recovery, attribution/classification coverage, and quality expectations/schedules/alerts.
4. Under explicit approval, implement controls and test allow/deny cases in isolated scope without leaking real sensitive values.
5. Verify effective grants/attachments and consumer behavior, inspect quality results/usage and notifications, and record exceptions and remediation owners.

### Validation

- Access matrix matches effective primary/secondary/inherited privileges; no application administration access or unsupported database SELECT grants.
- Unauthorized sensitive values and cross-tenant rows remain protected through actual consumer paths; approved access works with compatible policy types.
- Tags/policies, future-grant scope, ownership, and managed-schema authority verified with actual evidence.
- Quality expectations, schedules, result visibility, notifications, cost and remediation tested where configured; no custom DMF or new infrastructure required merely by this rule.
- Deliver access matrix/hierarchy, reviewed definitions, role test results, taxonomy, quality runbook, and compliance gaps. Unexecuted tests and unavailable evidence are explicitly unverified.

## References

- [Access-control framework and role inheritance](https://docs.snowflake.com/en/user-guide/security-access-control-overview)
- [Dynamic data masking](https://docs.snowflake.com/en/user-guide/security-column-ddm-intro)
- [Row access policies](https://docs.snowflake.com/en/user-guide/security-row-intro)
- [Object tagging](https://docs.snowflake.com/en/user-guide/object-tagging/introduction)
- [Data quality checks and serverless billing](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- `123-snowflake-object-tagging.md` and `124-snowflake-data-quality-core.md` for implementation details.
- Network/authentication controls are separate; use their primary product guidance when in scope.
