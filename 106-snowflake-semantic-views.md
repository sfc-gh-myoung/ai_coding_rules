**Description:** Rules for creating a structured and maintainable data model using a layered view strategy.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake Semantic Views

## Purpose
Establish a structured and maintainable data modeling approach using layered view strategies to separate concerns, promote reusability, and create purpose-built semantic interfaces for downstream consumption.

## Key Principles
- Use layered modeling: staging → core → semantic views; avoid recomputing across layers.
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

## 3. Documentation
- **Always:** Reference official documentation:
  - **Semantic View SQL Reference**: https://docs.snowflake.com/en/sql-reference/constructs/semantic_view
  - ** Semantic View Documentation**: https://docs.snowflake.com/en/user-guide/views-semantic/overview

