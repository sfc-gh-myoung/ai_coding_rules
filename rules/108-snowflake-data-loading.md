# Snowflake Data Loading

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** bulk loading, ON_ERROR, FILE_FORMAT, load data, external stage, internal stage, data ingestion, file upload, COPY error, loading patterns, stage files, PUT command, GET command
**TokenBudget:** ~2900
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for efficiently staging and bulk loading data into Snowflake using Stages and COPY INTO commands, optimizing for performance, reliability, and cost-effectiveness in batch loading scenarios.

**When to Load This Rule:**
- Staging files for bulk data loading
- Using COPY INTO for batch data ingestion
- Configuring file formats and error handling
- Optimizing bulk load performance
- Troubleshooting COPY INTO errors

### Quantification Standards

**File Sizing Thresholds:**
- **Optimal file size:** 100-250MB compressed per file (context: COPY INTO performance)
- **Small files threshold:** <10MB compressed (context: avoid without batching, causes metadata overhead)
- **Excessive file count:** >100K files (context: metadata overhead degradation)
- **Large load monitoring:** >10GB total data OR >100 files OR >10M rows (context: monitor COPY_HISTORY during execution)
- **Batching requirement:** Concatenate files <10MB into 100-250MB batches before loading

**For continuous ingestion with Snowpipe, see `121-snowflake-snowpipe.md`**

## References

### External Documentation
- [COPY INTO Command](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) - Bulk data loading syntax and options
- [Data Loading Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Internal and external stage management
- [Data Loading Best Practices](https://docs.snowflake.com/en/user-guide/data-load-considerations) - File sizing and optimization guidance

### Related Rules
**Closely Related** (consider loading together):
- **100-snowflake-core.md** - stage creation, COPY INTO fundamentals, and object naming
- **103-snowflake-performance-tuning.md** - optimizing COPY INTO performance and file sizing

**Sometimes Related** (load if specific scenario):
- **104-snowflake-streams-tasks.md** - setting up automated loading pipelines with tasks
- **116-snowflake-cortex-search.md** - loading documents for indexing and search
- **119-snowflake-warehouse-management.md** - warehouse sizing for data loading workloads

**Complementary** (different aspects of same domain):
- **107-snowflake-security-governance.md** - encryption, masking during loading, stage access
- **111-snowflake-observability-core.md** - monitoring COPY INTO performance and errors

## Contract

### Inputs and Prerequisites

- Source data files in supported format (CSV, JSON, Parquet, Avro, ORC, XML)
- Snowflake stage (internal or external) configured and accessible
- Target table schema defined and created
- Warehouse for COPY execution
- File format definition (delimiter, compression, encoding, null handling)
- Understanding of data volume and load frequency requirements
- Error handling strategy defined (ON_ERROR behavior)

### Mandatory

- Stage files: CREATE STAGE or configure external stage (S3, Azure, GCS)
- File format: CREATE FILE FORMAT with explicit configuration
- COPY INTO command with error handling (ON_ERROR = CONTINUE | SKIP_FILE | ABORT)
- VALIDATION_MODE for testing before full load
- COPY_HISTORY monitoring for load tracking
- File size optimization: Target 100-250MB compressed per file
- Semi-structured data: MATCH_BY_COLUMN_NAME for parquet, explicit VARIANT handling for JSON
- LIST @stage to verify files before loading

### Forbidden

- Loading many small files (<10MB) without batching
- Missing error handling (no ON_ERROR clause)
- Skipping VALIDATION_MODE for first-time loads
- Loading without FILE_FORMAT definition (implicit parsing unreliable)
- Using SELECT * in COPY INTO (specify columns explicitly)
- Loading duplicate data without deduplication strategy
- Ignoring COPY_HISTORY errors (silent data quality issues)

### Execution Steps

1. Analyze source files: Size, format, structure, data types
2. CREATE STAGE (internal) or configure external stage with storage integration
3. Upload files to stage: PUT for internal, cloud provider tools for external
4. LIST @stage to verify files present and accessible
5. CREATE FILE_FORMAT with explicit configuration (delimiter, compression, NULL_IF, etc.)
6. CREATE target table if not exists (match file schema)
7. Test with VALIDATION_MODE: COPY INTO ... VALIDATION_MODE = RETURN_ERRORS
8. Review validation errors, adjust FILE_FORMAT or file content
9. Execute load: COPY INTO target_table FROM @stage FILE_FORMAT = (...) ON_ERROR = CONTINUE
10. Monitor progress for large loads (>10GB total OR >100 files OR >10M rows): Query COPY_HISTORY while running
11. Verify load: Check row counts, query COPY_HISTORY for errors
12. Handle errors: Review rejected rows, fix and reload

### Output Format

- Stage DDL: CREATE STAGE with URL, credentials (via storage integration)
- File format DDL: CREATE FILE_FORMAT with all parsing rules
- COPY INTO statement: With error handling and file pattern matching
- Load statistics: Rows loaded, errors, execution time, warehouse credits
- Error report: COPY_HISTORY query showing file-level and row-level errors
- Validation results from VALIDATION_MODE execution

### Validation

**Test Requirements:**
- Stage accessible: LIST @stage returns files
- File format parses correctly: VALIDATION_MODE returns 0 errors (or acceptable error rate)
- COPY INTO executes successfully
- Row count matches expected (source file rows vs loaded rows)
- Error rate acceptable (<1% for production loads)
- Data types correct (no truncation, no precision loss)
- NULL handling correct (empty strings vs NULL values)

**Success Criteria:**
- All files loaded from stage: COPY_HISTORY shows status = 'LOADED'
- Error rate within SLA: <1% rows rejected for data quality, 0% for schema mismatch
- Load performance acceptable: ≥50MB/s per warehouse size (XS: 50MB/s, L: 400MB/s)
- Target table row count matches source (accounting for deduplication)
- Semi-structured columns properly parsed (VARIANT fields accessible)
- No excessive metadata overhead (file count reasonable, not 100k+ small files)

### Design Principles

- Stage files first; use dedicated stages per source; manage with PUT/GET for internal stages.
- Use COPY INTO for bulk, scheduled, and one-time loads; target 100–250MB compressed files.
- For continuous near-real-time ingestion, use Snowpipe (see `121-snowflake-snowpipe.md`).
- Prepare semi-structured data for subcolumnarization; be explicit about ON_ERROR and file formats.

### Post-Execution Checklist

- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

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

## Stages
- **Requirement:** Stage data files in an internal or external stage before loading.
- **Requirement:** Use a separate, dedicated stage for each external data source for organization and security.
- **Always:** Use `PUT` and `GET` to manage files in internal stages.

## Bulk Data Loading with COPY INTO
- **Requirement:** Use `COPY INTO` for bulk, one-time, and scheduled batch loads.
- **Always:** For continuous, near-real-time ingestion, use Snowpipe instead (see `121-snowflake-snowpipe.md`).
- **Requirement:** Be explicit about error handling (`ON_ERROR = CONTINUE`, `SKIP_FILE`, or `ABORT_STATEMENT`).
- **Requirement:** Specify file formats explicitly with `FILE_FORMAT` parameter.

## File Preparation and Optimization
- **Requirement:** Aim for compressed file sizes between 100–250 MB for optimal performance and cost.
- **Requirement:** For semi-structured data, ensure consistent data types within elements to enable subcolumnarization.
