**Description:** Rules for enforcing data security and access control using Snowflake's governance features.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

# Snowflake Security Governance

## Purpose
Establish comprehensive data security and access control practices using Snowflake's governance features, including RBAC, data masking, row-level security, and object tagging for enterprise-grade data protection.

## Key Principles
- Enforce least-privilege RBAC; use role hierarchies; map roles to business responsibilities.
- Protect data with masking policies, row access policies, and object tagging.
- Reference official docs for RBAC, masking, row access, and tagging.

## 1. Access Control
- **Requirement:** Implement Role-Based Access Control (RBAC) following least privilege.
- **Requirement:** Use role hierarchies to simplify permission management and inherit privileges.
- **Always:** Define functional roles that map directly to business responsibilities.

## 2. Data Protection Policies
- **Always:** Use masking policies to dynamically mask or tokenize sensitive data in columns.
- **Always:** Use row access policies to enforce row-level security based on a user's role or other session context.
- **Always:** Apply object tagging to classify data for governance purposes (e.g., PII, `SENSITIVITY_LEVEL`).

## References

### External Documentation
- [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) - RBAC, roles, and privilege management
- [Column-Level Security](https://docs.snowflake.com/en/user-guide/security-column-intro) - Dynamic data masking and column-level policies
- [Row-Level Security](https://docs.snowflake.com/en/user-guide/security-row-intro) - Row access policies and conditional data access
- [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) - Metadata tagging for governance and classification
