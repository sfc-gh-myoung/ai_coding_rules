**Description:** Best practices for loading data into Snowflake using Stages, COPY INTO, and Snowpipe.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake Data Loading

## TL;DR
- Stage files first; use dedicated stages per source; manage with PUT/GET for internal stages.
- Use COPY INTO for bulk loads; Snowpipe for continuous ingestion; be explicit about ON_ERROR and file formats.
- Target 100–250MB compressed files; prepare semi-structured data for subcolumnarization.

## 1. Stages
- **Requirement:** Stage data files in an internal or external stage before loading.
- **Requirement:** Use a separate, dedicated stage for each external data source for organization and security.
- **Always:** Use `PUT` and `GET` to manage files in internal stages.

## 2. Data Ingestion
- **Requirement:** Use `COPY INTO` for bulk, one-time loads.
- **Requirement:** Use Snowpipe for continuous, near-real-time ingestion.
- **Requirement:** With `COPY INTO`, be explicit about error handling (`ON_ERROR = CONTINUE`) and file formats.

## 3. File Preparation and Optimization
- **Requirement:** Aim for compressed file sizes between 100–250 MB for performance and cost.
- **Requirement:** For semi-structured data, ensure consistent data types within elements to enable subcolumnarization.

## 4. Documentation
- **Always:** Reference official documentation:
  - **COPY INTO**: https://docs.snowflake.com/en/sql-reference/sql/copy-into-table
  - **Snowpipe**: https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro
  - **Stages**: https://docs.snowflake.com/en/user-guide/data-load-stages-intro
