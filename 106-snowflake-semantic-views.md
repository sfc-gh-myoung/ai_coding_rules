**Description:** Rules for creating a structured and maintainable data model using a layered view strategy.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

# Snowflake Semantic Views

## Purpose
Establish a structured and maintainable data modeling approach using layered view strategies to separate concerns, promote reusability, and create purpose-built semantic interfaces for downstream consumption.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake semantic layer design with layered view architecture and data modeling patterns


## Key Principles
- Use layered modeling: staging then core then semantic views; avoid recomputing across layers.
- Consistent naming; avoid deep nesting; ensure views have COMMENT metadata.
- Reference Snowflake view docs; keep semantic views slim and purpose-built.

## 1. Layered Data Modeling
- **Requirement:** Structure data models using logical layers to separate concerns.
- **Requirement:** Create a staging layer for raw transformations and cleansing.
- **Requirement:** Create a core layer for standardized business logic and conformed dimensions/facts.
- **Requirement:** Create a semantic layer of slim, purpose-built views for downstream applications and reporting.
- **Requirement:** Avoid duplicating logic across layers; reference prior-layer views rather than recomputing.

## 2. Naming and Readability
- **Requirement:** Use a consistent naming convention for all database objects.
- **Requirement:** Avoid deep view nesting to prevent performance issues and complexity.
- **Requirement:** Add `COMMENT` metadata to all views to describe their purpose.

## References

### External Documentation
- [Views and Materialized Views](https://docs.snowflake.com/en/user-guide/views-introduction) - View creation, management, and best practices                                                                           
- [Database and Schema Design](https://docs.snowflake.com/en/user-guide/database-schemas) - Layered data modeling strategies

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Data Governance**: `600-data-governance-quality.md`

