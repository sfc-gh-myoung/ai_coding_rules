# Snowflake Snowpipe Troubleshooting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-troubleshooting, kw:pipe-errors
**Keywords:** snowpipe troubleshooting, debugging, error resolution, pipe errors, streaming errors, connection failures, schema errors, offset tracking, latency issues, duplicate data, authentication errors, channel errors
**TokenBudget:** ~4150
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 121-snowflake-snowpipe.md, 121a-snowflake-snowpipe-streaming.md

## Scope

**What This Rule Covers:**
Troubleshooting and debugging patterns for both file-based Snowpipe and Snowpipe Streaming. Covers common issues, error resolution strategies, debugging checklists, and diagnostic queries for production Snowpipe deployments.

**When to Load This Rule:**
- Debugging Snowpipe or Snowpipe Streaming failures
- Resolving authentication or connection errors
- Fixing schema mismatches or data type errors
- Addressing high latency or performance issues
- Resolving duplicate data or offset tracking problems
- Investigating pipe/channel errors in production

**For core Snowpipe setup, see `121-snowflake-snowpipe.md` and `121a-snowflake-snowpipe-streaming.md`**
**For monitoring, see `121b-snowflake-snowpipe-monitoring.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **121-snowflake-snowpipe.md** - File-based Snowpipe core concepts
- **121a-snowflake-snowpipe-streaming.md** - Streaming Snowpipe core concepts

**Related:**
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring and cost management
- **121e-snowflake-snowpipe-troubleshooting-advanced.md** - Advanced streaming patterns and debugging checklists
- **111-snowflake-observability-core.md** - Logging, tracing, and monitoring patterns

### External Documentation

- [Snowpipe Troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-troubleshooting) - Official troubleshooting guide
- [Snowpipe Error Notifications](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors) - Error handling and notification configuration

## Contract

### Inputs and Prerequisites

- Failing Snowpipe or Snowpipe Streaming deployment
- Access to ACCOUNT_USAGE schema for diagnostic queries
- Snowflake warehouse for running diagnostic queries
- Error messages or symptoms from monitoring systems
- Understanding of expected behavior and SLAs

### Mandatory

- Systematic debugging approach using checklists
- Diagnostic queries to gather evidence before making changes
- Root cause analysis to identify underlying issues
- Test fixes before declaring resolution
- Documentation of issue and resolution for future reference
- Monitoring configuration to prevent recurrence

### Forbidden

- Making changes without gathering evidence first
- Changing multiple things simultaneously
- Skipping checklist steps
- Declaring success without verification
- Ignoring root cause and only addressing symptoms
- Failing to document resolution

### Execution Steps

1. Gather evidence by running diagnostic queries and reviewing error messages
2. Identify symptoms and classify issue type (authentication, configuration, data, performance)
3. Follow appropriate debugging checklist systematically
4. Form hypothesis about root cause based on evidence
5. Test hypothesis with targeted queries or configuration checks
6. Implement fix for identified root cause
7. Verify resolution by testing data loading and checking error rates
8. Configure monitoring to detect similar issues early
9. Document issue, root cause, and resolution for future reference

### Output Format

- Diagnostic query results showing issue evidence
- Root cause analysis documenting underlying problem
- Fix implementation (SQL, Python code, or configuration changes)
- Verification results confirming resolution
- Monitoring configuration to prevent recurrence
- Documentation of issue and resolution

### Validation

**Pre-Task-Completion Checks:**
- [ ] Issue identified and root cause determined
- [ ] Diagnostic queries executed and results analyzed
- [ ] Fix implemented and tested
- [ ] Monitoring configured to prevent recurrence
- [ ] Documentation updated with resolution

**Success Criteria:**
- Issue resolved and data loading successfully
- Error rates within acceptable thresholds
- Latency within requirements
- No duplicate data
- Monitoring alerts configured appropriately

### Post-Execution Checklist

- [ ] Evidence gathered using diagnostic queries
- [ ] Issue type classified (authentication, configuration, data, performance)
- [ ] Debugging checklist followed systematically
- [ ] Root cause identified and documented
- [ ] Fix implemented and tested
- [ ] Data loading verified successful
- [ ] Error rates within acceptable thresholds (<5% for Snowpipe, <1% for Streaming)
- [ ] Latency within requirements
- [ ] No duplicate data detected
- [ ] Monitoring configured to prevent recurrence
- [ ] Issue and resolution documented for future reference

## File-Based Snowpipe Troubleshooting

### Common Issues

**Files not loading:**
- **Symptom:** Files staged but not appearing in target table
- **Causes:** Pipe paused, cloud event notifications misconfigured, stage permissions, file pattern mismatch
- **Solutions:**
  ```sql
  -- Check pipe status
  SHOW PIPES LIKE 'PIPE_NAME';
  -- Look for PIPE_EXECUTION_PAUSED = TRUE
  
  -- Resume pipe if paused
  ALTER PIPE PIPE_NAME SET PIPE_EXECUTION_PAUSED = FALSE;
  
  -- Verify cloud event notifications (check SQS queue ARN)
  DESC PIPE PIPE_NAME;
  
  -- Check load history for errors
  SELECT *
  FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
    DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
    PIPE_NAME => 'DB.SCHEMA.PIPE_NAME'
  ))
  ORDER BY START_TIME DESC;
  
  -- Verify stage permissions
  LIST @STAGE_NAME;
  
  -- Test file pattern matching
  LIST @STAGE_NAME PATTERN = 'your_pattern_here';
  ```

**High latency:**
- **Symptom:** Files taking >5 minutes to load
- **Causes:** Undersized files (<1MB), complex transformations, concurrent load contention
- **Solutions:**
  ```sql
  -- Check file sizes
  SELECT
    AVG(file_size) AS avg_file_size_bytes,
    MIN(file_size) AS min_file_size,
    MAX(file_size) AS max_file_size,
    COUNT(*) AS file_count
  FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
  WHERE pipe_name = 'PIPE_NAME'
    AND last_load_time >= DATEADD(day, -1, CURRENT_TIMESTAMP());
  
  -- Check load latency
  SELECT
    file_name,
    file_size,
    row_count,
    DATEDIFF(second, last_load_time, CURRENT_TIMESTAMP()) AS seconds_since_load
  FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
  WHERE pipe_name = 'PIPE_NAME'
    AND last_load_time >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
  ORDER BY last_load_time DESC;
  ```
  - **Fix:** Increase file sizes to 100-250MB compressed
  - **Fix:** Simplify COPY statement transformations
  - **Fix:** Verify ON_ERROR setting (CONTINUE vs SKIP_FILE vs ABORT)

**Duplicate data:**
- **Symptom:** Same data appearing multiple times in target table
- **Causes:** Mixing bulk COPY and Snowpipe on same files, file renamed/modified (different eTag)
- **Solutions:**
  - **Never mix bulk COPY and Snowpipe** on the same files
  - Snowpipe tracks loaded files automatically via eTag
  - If file is renamed or modified, Snowpipe treats it as new file
  - Use separate stages for bulk loads vs Snowpipe

**High costs:**
- **Symptom:** Snowpipe credits exceeding budget
- **Causes:** Micro-files (<1MB), continuous staging, excessive transformations
- **Solutions:**
  ```sql
  -- Analyze cost per file
  SELECT
    pipe_name,
    COUNT(*) AS load_count,
    SUM(files_inserted) AS total_files,
    SUM(credits_used) AS total_credits,
    ROUND(SUM(credits_used) / NULLIF(SUM(files_inserted), 0), 6) AS credits_per_file,
    AVG(bytes_inserted / NULLIF(files_inserted, 0)) AS avg_file_size_bytes
  FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
  WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  GROUP BY pipe_name
  ORDER BY total_credits DESC;
  ```
  - **Fix:** Optimize file sizes (100-250MB compressed)
  - **Fix:** Stage files once per minute, not continuously
  - **Fix:** Minimize transformations in COPY statement
  - **Fix:** Use pattern matching to filter files at pipe level

## Snowpipe Streaming Troubleshooting

### Common Issues

**Connection failures:**
- **Symptom:** SDK fails to connect to Snowflake
- **Causes:** Invalid authentication (key pair, JWT), network connectivity, firewall rules, incorrect account identifier
- **Solutions:**
  See **121a-snowflake-snowpipe-streaming.md** for client initialization patterns.
  - **Fix:** Verify private key file exists, is readable, and in PEM format
  - **Fix:** Ensure public key is registered in Snowflake user (`ALTER USER ... SET RSA_PUBLIC_KEY`)
  - **Fix:** Check account identifier format (ORGNAME-ACCOUNTNAME, not account URL)
  - **Fix:** Verify user has appropriate privileges (INSERT, CREATE TABLE)
  - **Fix:** Test network connectivity to Snowflake endpoint

**Schema errors:**
- **Symptom:** Insert failures with schema mismatch errors
- **Causes:** Table doesn't exist, column type mismatch, schema evolution disabled, missing columns
- **Solutions:**
  ```sql
  -- Verify table exists
  SHOW TABLES LIKE 'TABLE_NAME' IN SCHEMA DB.SCHEMA;
  
  -- Check table schema
  DESC TABLE DB.SCHEMA.TABLE_NAME;
  
  -- Check for recent schema changes via INFORMATION_SCHEMA
  SELECT column_name, data_type, ordinal_position, is_nullable
  FROM DB.INFORMATION_SCHEMA.COLUMNS
  WHERE table_name = 'TABLE_NAME'
    AND table_schema = 'SCHEMA'
  ORDER BY ordinal_position;
  ```
  ```python
  # Configure schema evolution mode
  from snowflake.ingest import SnowflakeStreamingIngestClient
  from snowflake.ingest.utils.constants import OnErrorOption
  
  client = SnowflakeStreamingIngestClient(...)
  
  # Strict mode: Fail on unknown columns
  channel = client.open_channel(
      database='DB',
      schema='SCHEMA',
      table='TABLE',
      channel_name='CHANNEL',
      on_error=OnErrorOption.ABORT  # Or CONTINUE, SKIP_FILE
  )
  
  # Validate row data types before insert
  row = {'id': 1, 'name': 'Alice'}
  response = channel.insert_row(row, 'offset_1')
  
  if response.has_errors():
      for error in response.insert_errors:
          print(f"Schema error: {error}")
  ```
  - **Fix:** Verify table exists in specified database and schema
  - **Fix:** Check column types match row data types
  - **Fix:** Configure schema evolution mode appropriately
  - **Fix:** Validate row data before insertion

**Offset tracking issues:**
- **Symptom:** Duplicate data, missing data, offset errors
- **Causes:** Non-unique offset tokens, offset persistence failures, channel reopens without offset
- **Fix:** Use unique, monotonically increasing offset tokens. Persist offsets to durable storage after successful inserts. Implement offset recovery for channel reopens.
- See **121e-snowflake-snowpipe-troubleshooting-advanced.md** for full Python offset tracking pattern.

**High latency:**
- **Symptom:** Data takes >5 seconds to appear in table
- **Causes:** Small batch sizes, network latency, classic architecture, channel contention
- **Fix:** Batch 100-1000 rows per insert cycle. Use multiple channels for parallel ingestion. Deploy closer to Snowflake region.
- See **121e-snowflake-snowpipe-troubleshooting-advanced.md** for batch performance pattern.

**High error rates:**
- **Symptom:** >1% of rows failing to insert
- **Causes:** Schema mismatches, data type errors, constraint violations, malformed data
- **Fix:** Validate data types and required fields before insert. Implement schema validation. Check constraints (PK, FK, NOT NULL).
- See **121e-snowflake-snowpipe-troubleshooting-advanced.md** for data validation pattern.

## Diagnostic Decision Tree

**Start here: What is the symptom?**

1. **Data not loading (file-based Snowpipe)**
   - Check: `SHOW PIPES LIKE 'PIPE_NAME'` - is pipe paused?
     - Yes: `ALTER PIPE PIPE_NAME SET PIPE_EXECUTION_PAUSED = FALSE`
   - Check: `LIST @STAGE_NAME PATTERN = '...'` - do files exist?
     - No: Verify cloud event notifications (SNS/Event Grid/Pub/Sub)
   - Check: COPY_HISTORY for errors - any LOAD_FAILED?
     - Yes: Read FIRST_ERROR_MESSAGE, fix file format or schema

2. **Duplicate data**
   - File-based: Are you mixing bulk COPY and Snowpipe on same files?
     - Yes: Use separate stages for bulk vs Snowpipe
   - Streaming: Are offset tokens globally unique across batches?
     - No: Use monotonically increasing global offset counter

3. **Schema mismatch errors**
   - Check: `DESC TABLE DB.SCHEMA.TABLE` - do columns match data?
   - Check: Column types (STRING vs NUMBER vs TIMESTAMP)
   - Streaming: Configure `on_error` mode and validate rows before insert

4. **High latency / slow performance**
   - File-based: Check file sizes - are they <1MB?
     - Yes: Consolidate to 100-250MB compressed files
   - Streaming: Check batch size - are you inserting one row at a time?
     - Yes: Batch 100-1000 rows per insert cycle

5. **Permission / authentication errors**
   - File-based: Verify CREATE PIPE, USAGE ON STAGE, INSERT ON TABLE
   - Streaming: Verify private key registered, account identifier format

## Debugging Checklists

For comprehensive debugging checklists (authentication, configuration, channel, data, and performance checks for both file-based and streaming Snowpipe), see **121e-snowflake-snowpipe-troubleshooting-advanced.md**.

**Quick reference - top items to check first:**
- File-based: Pipe not paused, event notifications configured, files exist in stage, file sizes 100-250MB
- Streaming: Private key readable and registered, account identifier correct (ORGNAME-ACCOUNTNAME), target table exists, batch size 100-1000

## Diagnostic Queries

### File-Based Snowpipe Diagnostics

Pipe status, load history, error, and stage queries are covered inline in the **Common Issues** section above. For ongoing monitoring queries, see **121b-snowflake-snowpipe-monitoring.md**.

**Additional diagnostic: Test COPY statement without loading data:**
```sql
COPY INTO TARGET_TABLE
FROM @STAGE_NAME/sample_file.csv.gz
FILE_FORMAT = (FORMAT_NAME = FILE_FORMAT_NAME)
VALIDATION_MODE = RETURN_ERRORS;
```

### Snowpipe Streaming Diagnostics

```sql
-- Check channel status (use SHOW CHANNELS, not ACCOUNT_USAGE)
SHOW CHANNELS IN TABLE DB.SCHEMA.TABLE;

-- Check recent data arrival (compare row counts over time)
SELECT COUNT(*) AS current_row_count FROM DB.SCHEMA.TABLE;

-- Check table schema
DESC TABLE DB.SCHEMA.TABLE;

-- Check user privileges
SHOW GRANTS TO USER USERNAME;
SHOW GRANTS ON TABLE DB.SCHEMA.TABLE;
```

## Design Principles

- **Systematic Debugging:** Follow checklist methodically, don't skip steps
- **Root Cause Analysis:** Identify underlying cause, not just symptoms
- **Test Fixes:** Verify fix resolves issue before declaring success
- **Prevent Recurrence:** Configure monitoring to catch similar issues early
- **Document Resolutions:** Record issue and fix for future reference

> **Investigation Required**
> When troubleshooting:
> 1. **Gather evidence FIRST** - Run diagnostic queries before making changes
> 2. **Check recent changes** - Review recent deployments or configuration changes
> 3. **Test hypotheses** - Verify assumptions with queries or tests
> 4. **Fix one thing at a time** - Avoid changing multiple things simultaneously
> 5. **Verify resolution** - Confirm issue is resolved before closing investigation

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Jumping to Solutions Without Root Cause Analysis

**Problem:** Immediately applying fixes (restart pipe, refresh stage, resize warehouse) when errors occur, without systematically investigating the underlying cause.

**Why It Fails:** Fixes symptoms temporarily but root cause persists, same issues recur repeatedly, wastes time on repeated firefighting, and prevents implementing preventive measures. Band-aid solutions don't solve systemic problems.

**Correct Pattern:**
```sql
-- BAD: Immediate fix without investigation
-- Error: "Snowpipe not loading files"
ALTER PIPE my_pipe REFRESH;  -- Restart without understanding why

-- GOOD: Systematic root cause analysis
-- Step 1: Check pipe status
SHOW PIPES LIKE 'my_pipe';

-- Step 2: Check recent load history
SELECT status, COUNT(*), error_message
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE pipe_name = 'MY_PIPE'
  AND start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY status, error_message;

-- Step 3: Identify root cause (e.g., schema mismatch)
-- Step 4: Fix root cause (update table schema or file format)
-- Step 5: THEN refresh pipe
ALTER PIPE my_pipe REFRESH;
```

### Anti-Pattern 2: Ignoring File Size and Batch Patterns in Performance Issues

**Problem:** Troubleshooting slow Snowpipe performance by only checking warehouse size and query execution, without analyzing file sizes, arrival patterns, and batching behavior.

**Why It Fails:** Small files (<1MB) cause excessive overhead regardless of warehouse size, bursty arrival patterns create latency spikes, and batching issues waste compute. Warehouse resizing doesn't fix file-level inefficiencies.

**Correct Pattern:**
```sql
-- BAD: Only check warehouse
SHOW WAREHOUSES LIKE 'SNOWPIPE_WH';  -- Check size, assume that's the issue

-- GOOD: Analyze file patterns first
SELECT 
  pipe_name,
  AVG(file_size_bytes) / POWER(1024, 2) as avg_file_size_mb,
  MIN(file_size_bytes) / POWER(1024, 2) as min_file_size_mb,
  COUNT(*) as file_count,
  COUNT(*) / NULLIF(DATEDIFF(hour, MIN(start_time), MAX(start_time)), 0) as files_per_hour,
  CASE 
    WHEN AVG(file_size_bytes) < 1048576 THEN 'ISSUE: Small files causing overhead'
    WHEN COUNT(*) / NULLIF(DATEDIFF(hour, MIN(start_time), MAX(start_time)), 0) > 1000 THEN 'ISSUE: High frequency causing batching problems'
    ELSE 'File patterns OK'
  END as diagnosis
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
GROUP BY pipe_name;
```
