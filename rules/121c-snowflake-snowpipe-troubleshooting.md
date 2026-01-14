# Snowflake Snowpipe Troubleshooting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** snowpipe troubleshooting, debugging, error resolution, pipe errors, streaming errors, connection failures, schema errors, offset tracking, latency issues, duplicate data, authentication errors, channel errors
**TokenBudget:** ~5050
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
  ```python
  # Verify private key format
  with open('snowflake_key.pem', 'rb') as f:
      key_content = f.read()
      print(f"Key length: {len(key_content)} bytes")
      # Should start with "-----BEGIN PRIVATE KEY-----"
  
  # Test JWT generation
  import jwt
  from cryptography.hazmat.primitives import serialization
  from cryptography.hazmat.backends import default_backend
  from datetime import datetime, timedelta
  
  with open('snowflake_key.pem', 'rb') as pem_file:
      private_key = serialization.load_pem_private_key(
          pem_file.read(),
          password=None,
          backend=default_backend()
      )
  
  payload = {
      'iss': 'ORGNAME-ACCOUNTNAME.USERNAME.SHA256_FINGERPRINT',
      'sub': 'ORGNAME-ACCOUNTNAME.USERNAME',
      'iat': datetime.utcnow(),
      'exp': datetime.utcnow() + timedelta(minutes=59)
  }
  
  token = jwt.encode(payload, private_key, algorithm='RS256')
  print(f"JWT token generated: {token[:50]}...")
  
  # Verify account identifier format
  # Should be: ORGNAME-ACCOUNTNAME (not account URL)
  ```
  - **Fix:** Verify private key file exists and is readable
  - **Fix:** Ensure private key format is correct (PEM format)
  - **Fix:** Verify public key registered in Snowflake user
  - **Fix:** Check account identifier format (ORGNAME-ACCOUNTNAME)
  - **Fix:** Verify user has appropriate privileges (INSERT, CREATE TABLE)

**Schema errors:**
- **Symptom:** Insert failures with schema mismatch errors
- **Causes:** Table doesn't exist, column type mismatch, schema evolution disabled, missing columns
- **Solutions:**
  ```sql
  -- Verify table exists
  SHOW TABLES LIKE 'TABLE_NAME' IN SCHEMA DB.SCHEMA;
  
  -- Check table schema
  DESC TABLE DB.SCHEMA.TABLE_NAME;
  
  -- Check for recent schema changes
  SELECT *
  FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMNS
  WHERE table_name = 'TABLE_NAME'
    AND table_schema = 'SCHEMA'
    AND table_catalog = 'DB'
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
- **Solutions:**
  ```python
  # Good: Offset token tracking for exactly-once semantics
  from snowflake.ingest import SnowflakeStreamingIngestClient
  import time
  
  client = SnowflakeStreamingIngestClient(...)
  channel = client.open_channel(...)
  
  # Track last committed offset (persist to disk/database)
  last_offset = load_last_offset_from_storage()
  
  # Insert rows with monotonically increasing offset tokens
  for idx, row in enumerate(data_stream, start=last_offset + 1):
      response = channel.insert_row(row, offset_token=f'offset_{idx}')
      
      if response.has_errors():
          print(f"Insert errors: {response.insert_errors}")
          # Handle errors, retry, or skip
      else:
          # Persist offset after successful insert
          save_offset_to_storage(idx)
  
  channel.close()
  # On restart, resume from last_offset + 1, no duplicates!
  ```
  - **Fix:** Use unique, monotonically increasing offset tokens
  - **Fix:** Persist offsets to disk/database after successful inserts
  - **Fix:** Implement offset recovery logic for channel reopens
  - **Fix:** Verify offset uniqueness within channel

**High latency:**
- **Symptom:** Data takes >5 seconds to appear in table
- **Causes:** Small batch sizes, network latency, classic architecture, channel contention
- **Solutions:**
  ```python
  # Batch rows for better performance
  from snowflake.ingest import SnowflakeStreamingIngestClient
  
  client = SnowflakeStreamingIngestClient(...)
  channel = client.open_channel(...)
  
  batch = []
  batch_size = 1000
  
  for row in data_stream:
      batch.append(row)
      
      if len(batch) >= batch_size:
          # Insert batch
          for idx, row in enumerate(batch):
              channel.insert_row(row, offset_token=f'offset_{idx}')
          batch = []
  
  # Insert remaining rows
  if batch:
      for idx, row in enumerate(batch):
          channel.insert_row(row, offset_token=f'offset_{idx}')
  
  channel.close()
  ```
  - **Fix:** Increase batch size (100-1000 rows per batch)
  - **Fix:** Use high-performance architecture for high-volume
  - **Fix:** Reduce network hops (deploy closer to Snowflake region)
  - **Fix:** Use multiple channels for parallel ingestion

**High error rates:**
- **Symptom:** >1% of rows failing to insert
- **Causes:** Schema mismatches, data type errors, constraint violations, malformed data
- **Solutions:**
  ```python
  # Implement data validation before insert
  from snowflake.ingest import SnowflakeStreamingIngestClient
  
  client = SnowflakeStreamingIngestClient(...)
  channel = client.open_channel(...)
  
  def validate_row(row):
      """Validate row data before insertion"""
      # Check required fields
      if 'id' not in row or 'name' not in row:
          return False, "Missing required fields"
      
      # Check data types
      if not isinstance(row['id'], int):
          return False, "id must be integer"
      
      if not isinstance(row['name'], str):
          return False, "name must be string"
      
      return True, None
  
  for idx, row in enumerate(data_stream):
      valid, error = validate_row(row)
      
      if not valid:
          print(f"Validation error at offset {idx}: {error}")
          continue  # Skip invalid row
      
      response = channel.insert_row(row, offset_token=f'offset_{idx}')
      
      if response.has_errors():
          print(f"Insert error at offset {idx}: {response.insert_errors}")
  
  channel.close()
  ```
  - **Fix:** Validate data before insert
  - **Fix:** Implement schema validation
  - **Fix:** Check constraints (PK, FK, CHECK)
  - **Fix:** Add data quality checks

## Debugging Checklists

### File-Based Snowpipe Checklist

**Authentication Issues:**
- [ ] Pipe creation privileges granted (CREATE PIPE, USAGE, SELECT, INSERT)
- [ ] Stage permissions configured correctly
- [ ] Storage integration configured (for external stages)
- [ ] Cloud event notifications configured (SNS, Event Grid, Pub/Sub)

**Configuration Issues:**
- [ ] Pipe status is not paused (PIPE_EXECUTION_PAUSED = FALSE)
- [ ] Cloud event notifications configured correctly (SQS queue ARN)
- [ ] File format specifications explicit and tested
- [ ] COPY statement validated manually before pipe creation
- [ ] Pattern matching configured correctly

**Data Issues:**
- [ ] Files exist in stage and match pattern
- [ ] File sizes appropriate (100-250MB compressed)
- [ ] No schema mismatches or data type errors
- [ ] No constraint violations (PK, FK, CHECK)

### Snowpipe Streaming Checklist

**Authentication Issues:**
- [ ] Private key file exists and is readable
- [ ] Private key format is correct (PEM format)
- [ ] Public key registered in Snowflake user
- [ ] Account identifier is correct (ORGNAME-ACCOUNTNAME)
- [ ] User has appropriate privileges (INSERT, CREATE TABLE)

**Channel Issues:**
- [ ] Target table exists in specified database and schema
- [ ] Channel name is unique and descriptive
- [ ] On-error mode configured appropriately
- [ ] Channel not already open in another process

**Data Issues:**
- [ ] Row data types match table schema
- [ ] Offset tokens are unique and monotonic
- [ ] No NULL values in NOT NULL columns
- [ ] No constraint violations (PK, FK, CHECK)

**Performance Issues:**
- [ ] Using high-performance architecture for high-volume
- [ ] Batch size appropriate (100-1000 rows per batch)
- [ ] Network latency acceptable (<50ms)
- [ ] Multiple channels for parallel ingestion

## Diagnostic Queries

### File-Based Snowpipe Diagnostics

```sql
-- Check pipe status and configuration
SHOW PIPES LIKE 'PIPE_NAME';
DESC PIPE PIPE_NAME;

-- Check recent load history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'DB.SCHEMA.PIPE_NAME'
))
ORDER BY START_TIME DESC;

-- Check for errors in COPY_HISTORY
SELECT
  file_name,
  status,
  row_count,
  error_count,
  first_error_message,
  first_error_line_number
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE pipe_name = 'PIPE_NAME'
  AND last_load_time >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
  AND (status = 'LOAD_FAILED' OR error_count > 0)
ORDER BY last_load_time DESC;

-- Check stage contents
LIST @STAGE_NAME;

-- Test file pattern matching
LIST @STAGE_NAME PATTERN = 'your_pattern_here';

-- Manually test COPY statement
COPY INTO TARGET_TABLE
FROM @STAGE_NAME/sample_file.csv.gz
FILE_FORMAT = (FORMAT_NAME = FILE_FORMAT_NAME)
VALIDATION_MODE = RETURN_ERRORS;
```

### Snowpipe Streaming Diagnostics

```sql
-- Check channel status
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'DB'
  AND schema_name = 'SCHEMA'
  AND table_name = 'TABLE'
ORDER BY last_commit_time DESC;

-- Check recent load history
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE table_name = 'TABLE'
  AND load_type = 'SNOWPIPE_STREAMING'
  AND start_time >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

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
