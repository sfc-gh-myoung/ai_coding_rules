**Description:** Best practices for loading data into Snowflake using Stages, COPY INTO, and Snowpipe.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

# Snowflake Data Loading

## Purpose
Provide comprehensive best practices for efficiently loading data into Snowflake using Stages, COPY INTO, and Snowpipe, optimizing for performance, reliability, and cost-effectiveness in both batch and streaming scenarios.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake data loading with Stages, COPY INTO, and Snowpipe for bulk and streaming ingestion


## Key Principles
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
- [COPY INTO Command](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) - Bulk data loading syntax and options                                                                                           
- [Snowpipe Introduction](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) - Continuous data ingestion and automation                                                                                 
- [Data Loading Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Internal and external stage management

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Streams and Tasks**: `104-snowflake-streams-tasks.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
