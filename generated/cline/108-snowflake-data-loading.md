<!-- Generated for Cline rules. See https://docs.cline.bot/features/cline-rules -->

**Keywords:** Data loading, COPY INTO, file formats, stages, Parquet, JSON, CSV, bulk loading, ON_ERROR, FILE_FORMAT
**TokenBudget:** ~950
**ContextTier:** High
**Depends:** 100-snowflake-core

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

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Stage files first:** CREATE STAGE before loading data
- **Use COPY INTO for bulk loads** - scheduled/one-time batch loading
- **Target 100-250MB compressed file sizes** - optimal performance and cost
- **Be explicit about error handling:** `ON_ERROR = CONTINUE | SKIP_FILE | ABORT_STATEMENT`
- **Specify file format:** `FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 ...)`
- **For continuous ingestion, use Snowpipe** - see 121-snowflake-snowpipe.md
- **Don't use COPY INTO for real-time streaming** - use Snowpipe instead

**Quick Checklist:**
- [ ] CREATE STAGE (internal or external)
- [ ] Prepare files: 100-250MB compressed, consistent schema
- [ ] Create FILE_FORMAT with explicit options
- [ ] COPY INTO with FILE_FORMAT and ON_ERROR specified
- [ ] Verify loaded row count matches expected
- [ ] Check COPY_HISTORY for errors
- [ ] If continuous ingestion needed, use Snowpipe (121)

> **Investigation Required**  
> When applying this rule:
> 1. Read existing STAGE definitions BEFORE making recommendations
> 2. Verify file format (CSV, JSON, Parquet) matches actual data
> 3. Never speculate about file structure - check sample files
> 4. Review COPY_HISTORY for actual load patterns and errors
> 5. Make grounded recommendations based on investigated stage and file metadata

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
