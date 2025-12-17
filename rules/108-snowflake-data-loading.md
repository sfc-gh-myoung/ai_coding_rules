# Snowflake Data Loading

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** bulk loading, ON_ERROR, FILE_FORMAT, load data, external stage, internal stage, data ingestion, file upload, COPY error, loading patterns, stage files, PUT command, GET command
**TokenBudget:** ~1900
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide comprehensive best practices for efficiently staging and bulk loading data into Snowflake using Stages and COPY INTO commands, optimizing for performance, reliability, and cost-effectiveness in batch loading scenarios.

## Rule Scope

Snowflake data staging and bulk loading with Stages and COPY INTO commands (for continuous ingestion with Snowpipe, see `121-snowflake-snowpipe.md`)

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

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

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
- Stage files first; use dedicated stages per source; manage with PUT/GET for internal stages.
- Use COPY INTO for bulk, scheduled, and one-time loads; target 100–250MB compressed files.
- For continuous near-real-time ingestion, use Snowpipe (see `121-snowflake-snowpipe.md`).
- Prepare semi-structured data for subcolumnarization; be explicit about ON_ERROR and file formats.
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Loading Many Small Files Instead of Larger Batches**
```sql
-- Bad: 10,000 files of 1MB each
COPY INTO target_table
FROM @my_stage/
FILES = ('file0001.csv', 'file0002.csv', ..., 'file10000.csv');
-- Takes hours, high metadata overhead, poor performance
```
**Problem:** Metadata overhead dominates; slow load performance; increased costs; table metadata bloat; compaction needed immediately; inefficient resource usage

**Correct Pattern:**
```bash
# Good: Concatenate small files into 100-250MB batches before loading
# Outside Snowflake: Combine files
cat file*.csv > batch_001.csv  # Create 150MB batches
cat file*.csv > batch_002.csv

# Then load larger files
COPY INTO target_table
FROM @my_stage/
PATTERN = 'batch_.*\.csv'
FILE_FORMAT = (TYPE=CSV);
```
**Benefits:** Optimal 100-250MB file size; faster loading; lower metadata overhead; better compression; efficient resource usage; no immediate compaction needed


**Anti-Pattern 2: Not Specifying FILE_FORMAT for Semi-Structured Data**
```sql
-- Bad: Let Snowflake infer format, inconsistent parsing
COPY INTO json_table
FROM @my_stage/data.json;
-- May misparse nested structures, wrong type inference
```
**Problem:** Inconsistent parsing; type inference errors; nested structure issues; poor subcolumnarization; query performance degradation; data quality issues

**Correct Pattern:**
```sql
-- Good: Explicit FILE_FORMAT with STRIP_OUTER_ARRAY for JSON arrays
CREATE FILE FORMAT my_json_format
  TYPE = JSON
  STRIP_OUTER_ARRAY = TRUE
  COMPRESSION = GZIP;

COPY INTO json_table
FROM @my_stage/data.json.gz
FILE_FORMAT = my_json_format;

-- For consistent types, enable subcolumnarization
ALTER TABLE json_table
  SET ENABLE_SCHEMA_EVOLUTION = TRUE;
```
**Benefits:** Consistent parsing; correct type handling; subcolumnarization enabled; better query performance; data quality assured; predictable loading behavior


**Anti-Pattern 3: Using INSERT INTO for Bulk Data Loading**
```sql
-- Bad: Row-by-row INSERT in loop (Python/stored proc)
FOR row IN (SELECT * FROM source_data) LOOP
  INSERT INTO target_table VALUES (row.col1, row.col2, ...);
END LOOP;
-- Extremely slow, thousands of micro-partitions, table bloat
```
**Problem:** Glacially slow (1000x slower than COPY); creates micro-partitions per INSERT; metadata bloat; compaction required; high costs; table performance degrades

**Correct Pattern:**
```sql
-- Good: Use COPY INTO for bulk loading, INSERT SELECT for internal data
-- External data: Use COPY INTO
COPY INTO target_table
FROM @my_stage/data.csv
FILE_FORMAT = (TYPE=CSV);

-- Internal data: Use INSERT SELECT for batch
INSERT INTO target_table
SELECT col1, col2, col3
FROM source_table
WHERE load_date = CURRENT_DATE();
-- Creates optimal partitions, fast bulk operation
```
**Benefits:** 1000x faster than row-by-row; optimal partition sizes; no metadata bloat; efficient resource usage; production-grade performance; no compaction needed


**Anti-Pattern 4: Not Using VALIDATION_MODE to Test Before Loading**
```sql
-- Bad: Load directly to production table without validation
COPY INTO prod_critical_table
FROM @my_stage/untested_data.csv;
-- Discover format errors after partial load, data corruption!
```
**Problem:** Format errors discovered mid-load; partial data loaded; data corruption; rollback required; production downtime; emergency recovery; user impact

**Correct Pattern:**
```sql
-- Good: Test with VALIDATION_MODE first
-- Step 1: Validate file format without loading
COPY INTO prod_critical_table
FROM @my_stage/untested_data.csv
VALIDATION_MODE = 'RETURN_ERRORS';
-- Returns: Row errors, parsing issues, format mismatches

-- Step 2: Check row count
COPY INTO prod_critical_table
FROM @my_stage/untested_data.csv
VALIDATION_MODE = 'RETURN_N_ROWS'
  (N => 10);
-- Preview first 10 rows

-- Step 3: Only after validation, load to production
COPY INTO prod_critical_table
FROM @my_stage/untested_data.csv
FILE_FORMAT = (TYPE=CSV);
```
**Benefits:** Errors caught before loading; no partial loads; no data corruption; production safety; confidence in load; zero downtime; professional deployment

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

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

## References

### External Documentation
- [COPY INTO Command](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) - Bulk data loading syntax and options
- [Data Loading Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Internal and external stage management
- [Data Loading Best Practices](https://docs.snowflake.com/en/user-guide/data-load-considerations) - File sizing and optimization guidance

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Snowpipe and Snowpipe Streaming**: `rules/121-snowflake-snowpipe.md` - Continuous near-real-time ingestion
- **Streams and Tasks**: `rules/104-snowflake-streams-tasks.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

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

## Related Rules

**Closely Related** (consider loading together):
- `100-snowflake-core` - For stage creation, COPY INTO fundamentals, and object naming
- `103-snowflake-performance-tuning` - For optimizing COPY INTO performance and file sizing

**Sometimes Related** (load if specific scenario):
- `104-snowflake-streams-tasks` - When setting up automated loading pipelines with tasks
- `116-snowflake-cortex-search` - When loading documents for indexing and search
- `119-snowflake-warehouse-management` - For warehouse sizing for data loading workloads

**Complementary** (different aspects of same domain):
- `107-snowflake-security-governance` - For encryption, masking during loading, stage access
- `111-snowflake-observability-core` - For monitoring COPY INTO performance and errors
