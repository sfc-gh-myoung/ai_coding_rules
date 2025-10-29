**Description:** Best practices for loading data into Snowflake using Stages and COPY INTO for bulk loading. For continuous ingestion, see 121-snowflake-snowpipe.md.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Data loading, stages, COPY INTO, CSV load, JSON load, Parquet, file formats, bulk loading, stage management
**Version:** 1.3
**LastUpdated:** 2025-10-13
**Depends:** 100-snowflake-core

**TokenBudget:** ~200
**ContextTier:** Medium

# Snowflake Data Loading

## Purpose
Provide comprehensive best practices for efficiently staging and bulk loading data into Snowflake using Stages and COPY INTO commands, optimizing for performance, reliability, and cost-effectiveness in batch loading scenarios.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake data staging and bulk loading with Stages and COPY INTO commands (for continuous ingestion with Snowpipe, see `121-snowflake-snowpipe.md`)


## Key Principles
- Stage files first; use dedicated stages per source; manage with PUT/GET for internal stages.
- Use COPY INTO for bulk, scheduled, and one-time loads; target 100–250MB compressed files.
- For continuous near-real-time ingestion, use Snowpipe (see `121-snowflake-snowpipe.md`).
- Prepare semi-structured data for subcolumnarization; be explicit about ON_ERROR and file formats.

## 1. Stages
- **Requirement:** Stage data files in an internal or external stage before loading.
- **Requirement:** Use a separate, dedicated stage for each external data source for organization and security.
- **Always:** Use `PUT` and `GET` to manage files in internal stages.

## 2. Bulk Data Loading with COPY INTO
- **Requirement:** Use `COPY INTO` for bulk, one-time, and scheduled batch loads.
- **Always:** For continuous, near-real-time ingestion, use Snowpipe instead (see `121-snowflake-snowpipe.md`).
- **Requirement:** Be explicit about error handling (`ON_ERROR = CONTINUE`, `SKIP_FILE`, or `ABORT_STATEMENT`).
- **Requirement:** Specify file formats explicitly with `FILE_FORMAT` parameter.

## 3. File Preparation and Optimization
- **Requirement:** Aim for compressed file sizes between 100–250 MB for optimal performance and cost.
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
- [Data Loading Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Internal and external stage management
- [Data Loading Best Practices](https://docs.snowflake.com/en/user-guide/data-load-considerations) - File sizing and optimization guidance

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowpipe and Snowpipe Streaming**: `121-snowflake-snowpipe.md` - Continuous near-real-time ingestion
- **Streams and Tasks**: `104-snowflake-streams-tasks.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
