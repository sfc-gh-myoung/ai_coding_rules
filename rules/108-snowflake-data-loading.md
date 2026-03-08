# Snowflake Data Loading

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-20
**LoadTrigger:** kw:data-loading, kw:copy-into, kw:import
**Keywords:** bulk loading, ON_ERROR, FILE_FORMAT, load data, external stage, internal stage, data ingestion, file upload, COPY error, loading patterns, stage files, PUT command, GET command
**TokenBudget:** ~3750
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

- Role with USAGE on stage and warehouse; INSERT on target table
- CREATE STAGE privilege (for new stages) or USAGE on existing stage
- For external stages: storage integration configured with appropriate cloud credentials
- Source data files in supported format (CSV, JSON, Parquet, Avro, ORC, XML)
- Target table schema defined and created
- File format definition (delimiter, compression, encoding, null handling)
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

- [ ] Stage created with appropriate encryption and access controls
- [ ] FILE_FORMAT defined with explicit delimiter, compression, NULL_IF, encoding
- [ ] VALIDATION_MODE tested before production load
- [ ] ON_ERROR strategy defined (CONTINUE, SKIP_FILE, or ABORT_STATEMENT)
- [ ] Files sized 100-250MB compressed (small files batched)
- [ ] COPY_HISTORY checked for errors after load
- [ ] Row counts verified (source vs target)
- [ ] Semi-structured data parsed correctly (VARIANT fields accessible)

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
-- Data Load Workflow

-- Step 1: Create stage and file format
CREATE STAGE IF NOT EXISTS db.schema.load_stage
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE FILE FORMAT IF NOT EXISTS db.schema.csv_format
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  NULL_IF = ('', 'NULL', 'null')
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  COMPRESSION = GZIP
  ENCODING = 'UTF-8';

-- Step 2: Upload and verify
PUT file:///data/sales_*.csv.gz @db.schema.load_stage/sales/;
LIST @db.schema.load_stage/sales/;

-- Step 3: Validate before loading
COPY INTO db.schema.sales_target
FROM @db.schema.load_stage/sales/
FILE_FORMAT = db.schema.csv_format
VALIDATION_MODE = 'RETURN_ERRORS';

-- Step 4: Execute load
COPY INTO db.schema.sales_target
FROM @db.schema.load_stage/sales/
FILE_FORMAT = db.schema.csv_format
ON_ERROR = CONTINUE
PATTERN = '.*\.csv\.gz';

-- Step 5: Verify results
SELECT COUNT(*) FROM db.schema.sales_target WHERE _metadata_file_last_modified > DATEADD(hour, -1, CURRENT_TIMESTAMP());
SELECT * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'db.schema.sales_target', START_TIME => DATEADD(hour, -1, CURRENT_TIMESTAMP())));
```

### Parallel COPY INTO Guidance

**Optimal file sizes:** 100-250MB compressed per file for maximum throughput.

**File count vs warehouse size:**
- **XS warehouse:** 4-8 files loading in parallel
- **S warehouse:** 8-16 files
- **M warehouse:** 16-32 files
- **L warehouse:** 32-64 files
- **XL+:** 64+ files

**Best practice:** Split large files to match warehouse parallelism. A 2GB file on an XS warehouse loads slower than 8x 250MB files.

### Encoding and BOM Handling

```sql
-- Specify encoding explicitly for non-UTF-8 files
CREATE FILE FORMAT latin1_format
  TYPE = CSV
  ENCODING = 'ISO-8859-1'
  SKIP_HEADER = 1;

-- Handle UTF-8 BOM (Byte Order Mark) from Excel exports
-- Snowflake auto-detects BOM in UTF-8 files
-- For explicit handling, use ENCODING = 'UTF-8' (handles BOM automatically)

-- Common encoding issues:
-- Windows exports: Often WINDOWS-1252, not UTF-8
-- Excel CSV: May include BOM (EF BB BF prefix)
-- If garbled characters appear, check source file encoding with: file -I data.csv
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

### Data Files vs Application Files: Compression Distinction

Compression behavior differs depending on what you are staging:

- **Data files** (CSV, JSON, Parquet): Compression **ON** (default, recommended) — `AUTO_COMPRESS=TRUE` (default) / `--auto-compress` (default)
- **Application files** (.py, .yml): Compression **OFF** (mandatory) — `AUTO_COMPRESS=FALSE` / `--no-auto-compress`

- **Data loading (this rule):** Compression is desirable. GZIP reduces transfer time and storage.
  The default `AUTO_COMPRESS=TRUE` is correct for data files staged via PUT/COPY INTO.
- **Application deployment (see `109b-snowflake-app-deployment-core.md`):** Compression MUST be
  disabled. Python's import system cannot read `.py.gz` files, and Streamlit in Snowflake (SiS)
  will fail with `TypeError: bad argument type for built-in operation` if `.py` files are compressed.

> **Do not apply data loading compression defaults to application deployment.**
> When writing Python wrappers that call `PUT` or `snow stage copy`, use `AUTO_COMPRESS=FALSE` /
> `--no-auto-compress` for application files. See `109b-snowflake-app-deployment-core.md` for
> the correct pattern.
