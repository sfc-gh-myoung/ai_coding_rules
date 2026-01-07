# Snowflake Snowpipe (File-Based Ingestion)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** snowpipe, auto-ingest, REST API, file-based ingestion, event notifications, COPY INTO, create pipe, data ingestion, pipe errors, pipe management, micro-batching, serverless ingestion
**TokenBudget:** ~8450
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 108-snowflake-data-loading.md, 104-snowflake-streams-tasks.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for continuous file-based data ingestion using Snowflake Snowpipe (serverless, event-driven). Covers architecture selection (auto-ingest vs REST API), file sizing optimization, cloud event configuration, security, monitoring, cost management, and troubleshooting for file-based ingestion patterns.

**When to Load This Rule:**
- Setting up continuous file-based data ingestion with Snowpipe
- Configuring auto-ingest with cloud event notifications (SNS, Event Grid, Pub/Sub)
- Implementing REST API-based pipe triggering
- Optimizing file sizes and ingestion latency (1-2 min acceptable)
- Troubleshooting Snowpipe load failures or high costs
- Monitoring and managing Snowpipe load history

**For SDK-based streaming ingestion (sub-second latency), see `121a-snowflake-snowpipe-streaming.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **108-snowflake-data-loading.md** - Stages and bulk loading with COPY INTO

**Related:**
- **121a-snowflake-snowpipe-streaming.md** - SDK-based streaming ingestion for sub-second latency
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring, cost tracking, and performance analysis
- **121c-snowflake-snowpipe-troubleshooting.md** - Troubleshooting and debugging patterns
- **104-snowflake-streams-tasks.md** - Incremental pipelines and change data capture
- **119-snowflake-warehouse-management.md** - Warehouse sizing (note: Snowpipe uses serverless compute)
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization
- **107-snowflake-security-governance.md** - Access control and security policies

### External Documentation

- [Snowpipe Introduction](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) - Overview of Snowpipe architecture and capabilities
- [Snowpipe Auto-Ingest](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto) - Configuring automated data loads with cloud messaging
- [Snowpipe REST API](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-overview) - REST endpoint reference for programmatic control
- [Snowpipe Costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing) - Billing model and cost optimization
- [Snowpipe Error Notifications](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors) - Error handling and notification configuration
- [Snowpipe Troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-troubleshooting) - Common issues and solutions

## Contract

### Inputs and Prerequisites

- Snowflake account with pipe creation privileges (`CREATE PIPE`)
- Configured stages (internal or external) with appropriate permissions
- Target tables with appropriate schema
- Cloud storage with event notifications configured (for auto-ingest: SNS, Event Grid, Pub/Sub)
- Understanding of file sizing and ingestion patterns (100-250MB compressed recommended)

### Mandatory

- Snowflake DDL for CREATE PIPE statements
- Cloud storage event configuration (SNS, Azure Event Grid, GCS Pub/Sub for auto-ingest)
- Snowpipe REST API client (for REST API method)
- Monitoring queries for load history and error tracking
- File format specifications (explicit, not defaults)

### Forbidden

- Using Snowpipe for bulk historical loads (use COPY INTO instead)
- Mixing bulk COPY and Snowpipe on same files (causes duplicate data)
- Undersized files (<1MB) for file-based Snowpipe (poor cost efficiency)
- Omitting FILE_FORMAT specifications (causes parse errors)
- Generic PATTERN matching (.*) without proper file filtering

### Execution Steps

1. Determine ingestion pattern: auto-ingest (event-driven), REST API (programmatic), or Streaming (SDK-based)
2. Configure cloud storage and create stages with appropriate permissions and storage integrations
3. Optimize file sizing: 100-250MB compressed for Snowpipe, stage once per minute
4. Create and test file format specifications explicitly
5. Validate COPY statement manually before creating pipe
6. Create pipe with validated COPY statement and appropriate ON_ERROR setting
7. Configure cloud event notifications (for auto-ingest) or REST API authentication (for REST method)
8. Set up monitoring queries for load history and error tracking
9. Configure error notifications and alerting
10. Test latency and throughput under expected load
11. Document cost baseline and establish optimization targets

### Output Format

Pipe deployments produce:
- Complete pipe DDL with comments and configuration
- Cloud event configuration (SNS topics, Event Grid subscriptions, Pub/Sub topics)
- Snowpipe Streaming code examples with channel management
- Monitoring queries for load history, errors, and costs
- Cost tracking patterns and optimization strategies

### Validation

**Pre-Task-Completion Checks:**
- Pipe creation privileges granted (CREATE PIPE, USAGE, SELECT, INSERT)
- Stages configured with proper permissions and storage integrations
- Target tables exist with appropriate schema
- Cloud event notifications configured (for auto-ingest)
- File format specifications explicit and tested
- COPY statement validated manually before pipe creation
- Monitoring queries configured and tested

**Success Criteria:**
- Pipe created successfully and shows in SHOW PIPES
- Files loading automatically (auto-ingest) or via REST API/SDK
- Load history accessible via INFORMATION_SCHEMA.PIPE_USAGE_HISTORY
- Latency within requirements: <2 min for file-based, <1 sec for streaming
- No duplicate data in target tables
- Error rate acceptable (<5% of files)
- Cost per GB within expected range
- Error notifications working and alerts configured

**Negative Tests:**
- Pipe creation should fail without CREATE PIPE privilege
- Files should not load with misconfigured cloud event notifications
- Duplicate loads should not occur (Snowpipe tracks loaded files)
- High latency should be detected with undersized files (<1MB)
- Excessive costs should trigger alerts with micro-batches
- Schema errors should be caught with missing columns or type mismatches
- Offset tracking should prevent duplicate rows in streaming mode

### Design Principles

- **Auto-Ingest First:** Prefer auto-ingest with cloud event notifications over REST API for simplicity, automation, and reliability
- **File Sizing:** Stage files of 100-250MB compressed, ideally once per minute for optimal cost/performance balance
- **Serverless Compute:** Snowpipe uses Snowflake-managed compute (not user warehouses); billed per-second of compute used
- **Load History:** Snowpipe metadata retained for 14 days (vs 64 days for bulk loads); query via REST API or INFORMATION_SCHEMA
- **Idempotency:** Snowpipe tracks loaded files to prevent duplicates; do not mix bulk COPY and Snowpipe on same files
- **Latency Management:** Expect variable latency based on file size, format, transformations; test to establish baseline (typical: 1-2 minutes)

> **Investigation Required**
> When working with Snowpipe:
> 1. **Read existing pipes BEFORE creating new ones** - Check SHOW PIPES, understand patterns, file sizes
> 2. **Verify cloud storage setup** - Check stages, permissions, event notifications configuration
> 3. **Never assume file patterns** - List stage to understand actual file sizes and frequency
> 4. **Check COPY statement** - Test COPY INTO manually before creating pipe
> 5. **Monitor first loads** - Verify latency and error rates after pipe creation
>
> **Anti-Pattern:**
> "Creating Snowpipe... (without testing COPY statement first)"
> "Using Snowpipe for bulk load... (wrong tool for the job)"
>
> **Correct Pattern:**
> "Let me check your existing ingestion setup first."
> [reads existing pipes, checks stages, tests COPY statement]
> "I see you use auto-ingest with 200MB files. Creating new pipe following this pattern..."

### Post-Execution Checklist

- [ ] Ingestion method selected (auto-ingest, REST API, or Streaming)
- [ ] File sizes optimized (100-250MB compressed for file-based Snowpipe)
- [ ] Cloud event notifications configured correctly (for auto-ingest)
- [ ] Stages created with proper permissions and storage integrations
- [ ] Target tables exist with appropriate schema
- [ ] File format specifications explicit and tested
- [ ] COPY statement validated manually before pipe creation
- [ ] Pipes created with validated COPY statements
- [ ] ON_ERROR setting appropriate for workload (CONTINUE/SKIP_FILE/ABORT)
- [ ] Security privileges granted (CREATE PIPE, USAGE, SELECT, INSERT)
- [ ] Monitoring queries configured and tested
- [ ] Load history accessible and reviewed
- [ ] Cost tracking implemented and baseline established
- [ ] Error notifications configured (for production pipes)
- [ ] Documentation updated with pipe details and architecture

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Using AUTO_INGEST for Continuous Loading**
```sql
-- Bad: Manual REST API calls for continuous file loading
CREATE PIPE manual_load_pipe
AS COPY INTO target_table
FROM @my_stage
FILE_FORMAT = (TYPE = CSV);

-- Then in application:
-- POST /v1/data/pipes/manual_load_pipe/insertFiles
-- Requires constant API calls, manual tracking, complex orchestration!
```
**Problem:** High operational overhead; manual file tracking; complex code; API rate limits; delayed loading; error-prone; expensive maintenance

**Correct Pattern:**
```sql
-- Good: AUTO_INGEST for continuous automated loading
CREATE PIPE auto_load_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'  -- For AWS
-- OR INTEGRATION = 'AZURE_EVENT_GRID_INT'  -- For Azure
-- OR INTEGRATION = 'GCS_PUBSUB_INT'  -- For GCS
AS COPY INTO target_table
FROM @my_stage
FILE_FORMAT = (TYPE = CSV)
ON_ERROR = CONTINUE;

-- Cloud storage sends notifications automatically
-- Snowpipe loads files within minutes, no code needed!
```
**Benefits:** Fully automated; no API calls; near real-time loading (5-10 min); cloud-native; simple setup; reliable; low maintenance; cost-effective

**Anti-Pattern 2: Missing FILE_FORMAT Specifications**
```sql
-- Bad: No file format, relies on defaults
CREATE PIPE vague_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'
AS COPY INTO target_table
FROM @my_stage;
-- What delimiter? Date format? Compression? NULL handling?
-- Fails on first complex file!
```
**Problem:** Data parsing errors; incorrect data types; NULL mishandling; silent failures; data quality issues; debugging nightmares; production incidents

**Correct Pattern:**
```sql
-- Good: Explicit file format with all details
CREATE OR REPLACE FILE FORMAT csv_pipe_format
TYPE = CSV
FIELD_DELIMITER = ','
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
NULL_IF = ('NULL', 'null', '')
DATE_FORMAT = 'YYYY-MM-DD'
TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
COMPRESSION = GZIP
ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
TRIM_SPACE = TRUE;

CREATE PIPE explicit_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'
AS COPY INTO target_table
FROM @my_stage
FILE_FORMAT = (FORMAT_NAME = csv_pipe_format)
ON_ERROR = CONTINUE;

-- Test file format before creating pipe
COPY INTO target_table
FROM @my_stage/sample_file.csv.gz
FILE_FORMAT = (FORMAT_NAME = csv_pipe_format)
VALIDATION_MODE = RETURN_ERRORS;
```
**Benefits:** Predictable parsing; data quality; explicit expectations; easy debugging; documented format; testable; reliable production

**Anti-Pattern 3: Not Monitoring COPY_HISTORY for Load Errors**
```sql
-- Bad: Create pipe and never check for errors
CREATE PIPE silent_failure_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'
AS COPY INTO target_table
FROM @my_stage
FILE_FORMAT = (TYPE = CSV)
ON_ERROR = CONTINUE;  -- Continues on errors but never alerts!

-- Files fail silently, data gaps go unnoticed for weeks!
```
**Problem:** Silent data loss; undetected failures; data quality degradation; missing rows; business impact; late discovery; customer complaints; audit gaps

**Correct Pattern:**
```sql
-- Good: Monitor COPY_HISTORY for errors and alerts

-- Step 1: Create monitoring query
CREATE OR REPLACE VIEW pipe_error_monitoring AS
SELECT
  pipe_name,
  file_name,
  last_load_time,
  status,
  row_count,
  row_parsed,
  first_error_message,
  first_error_line_number,
  error_count,
  error_limit
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET_TABLE',
  START_TIME => DATEADD(HOUR, -1, CURRENT_TIMESTAMP())
))
WHERE status = 'LOAD_FAILED' OR error_count > 0
ORDER BY last_load_time DESC;

-- Step 2: Set up scheduled task to check for errors
CREATE OR REPLACE TASK monitor_pipe_errors
WAREHOUSE = monitoring_wh
SCHEDULE = '5 MINUTE'
AS
INSERT INTO pipe_error_log
SELECT * FROM pipe_error_monitoring
WHERE last_load_time > DATEADD(MINUTE, -10, CURRENT_TIMESTAMP());

ALTER TASK monitor_pipe_errors RESUME;

-- Step 3: Create alerts (using Snowflake Alerts or external system)
-- Query pipe_error_log and send notifications when errors detected

-- Step 4: Regular manual checks
SELECT
  COUNT(*) as total_files,
  SUM(CASE WHEN status = 'LOADED' THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN status = 'LOAD_FAILED' THEN 1 ELSE 0 END) as failed,
  SUM(row_count) as total_rows,
  SUM(error_count) as total_errors
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET_TABLE',
  START_TIME => DATEADD(DAY, -7, CURRENT_TIMESTAMP())
));
```
**Benefits:** Early error detection; data quality assurance; proactive alerts; no silent failures; audit trail; business continuity; professional operations

**Anti-Pattern 4: Not Handling File Naming Patterns Correctly**
```sql
-- Bad: Generic pattern loads all files repeatedly
CREATE PIPE greedy_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'
AS COPY INTO target_table
FROM @my_stage
PATTERN = '.*';  -- Matches everything! Test files, backups, old files!
-- Loads test_file.csv, backup_old.csv, debug_data.csv, all repeated!
```
**Problem:** Loads unwanted files; duplicates; test data in production; slow performance; wasted credits; data contamination; difficult troubleshooting

**Correct Pattern:**
```sql
-- Good: Specific file patterns with proper organization

-- Step 1: Organize files in stage with clear prefixes/folders
-- Stage structure:
--   @my_stage/production/sales/2024-11-22/sales_data_*.csv.gz
--   @my_stage/test/test_*.csv
--   @my_stage/archive/old_*.csv

-- Step 2: Use specific PATTERN for production data only
CREATE PIPE specific_pattern_pipe
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789:my-topic'
AS COPY INTO target_table
FROM @my_stage
PATTERN = 'production/sales/.*sales_data_[0-9]{8}_[0-9]{6}\\.csv\\.gz'
FILE_FORMAT = (FORMAT_NAME = csv_pipe_format)
ON_ERROR = CONTINUE;

-- Step 3: Verify pattern matches expected files
LIST @my_stage PATTERN = 'production/sales/.*sales_data_[0-9]{8}_[0-9]{6}\\.csv\\.gz';

-- Step 4: Check loaded files
SELECT DISTINCT file_name
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET_TABLE',
  START_TIME => DATEADD(DAY, -1, CURRENT_TIMESTAMP())
))
ORDER BY file_name;

-- Note: Snowpipe automatically tracks loaded files to prevent duplicates
-- But correct PATTERN prevents unnecessary processing
```
**Benefits:** Loads correct files only; no test data leakage; predictable behavior; fast processing; optimized credits; clean production data; easy debugging

## Output Format Examples
```sql
-- Complete Snowpipe auto-ingest example

-- 1. Create storage integration (AWS S3)
CREATE STORAGE INTEGRATION SINT_S3_RAW_DATA
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-s3-access'
  STORAGE_ALLOWED_LOCATIONS = ('s3://my-bucket/raw-data/');

-- 2. Create file format
CREATE FILE FORMAT FF_JSON_GZIP
  TYPE = JSON
  COMPRESSION = GZIP
  STRIP_OUTER_ARRAY = TRUE;

-- 3. Create external stage
CREATE STAGE STG_S3_RAW_DATA
  URL = 's3://my-bucket/raw-data/'
  STORAGE_INTEGRATION = SINT_S3_RAW_DATA
  FILE_FORMAT = FF_JSON_GZIP;

-- 4. Create target table
CREATE TABLE RAW_DATA (
  record_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP_NTZ,
  payload VARIANT,
  loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 5. Create pipe with auto-ingest
CREATE PIPE PIPE_LOAD_RAW_DATA
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-notifications'
  COMMENT = 'Auto-ingest pipe for raw data from S3'
AS
  COPY INTO RAW_DATA (record_id, event_type, event_timestamp, payload)
  FROM (
    SELECT
      $1:id::STRING,
      $1:type::STRING,
      $1:timestamp::TIMESTAMP_NTZ,
      $1
    FROM @STG_S3_RAW_DATA
  )
  FILE_FORMAT = FF_JSON_GZIP
  ON_ERROR = CONTINUE;

-- 6. Get SQS queue ARN for S3 event notifications
SHOW PIPES LIKE 'PIPE_LOAD_RAW_DATA';
DESC PIPE PIPE_LOAD_RAW_DATA;
-- Copy the "notification_channel" value (SQS ARN) for S3 bucket configuration

-- 7. Monitor pipe
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'PIPE_LOAD_RAW_DATA'
))
ORDER BY START_TIME DESC;
```

## Snowpipe Overview and Architecture

### 1.1 What is Snowpipe?

**Snowpipe** enables continuous, automated loading of data from files as soon as they're available in a stage. Instead of manually executing COPY statements on a schedule, Snowpipe loads files in micro-batches within minutes of arrival.

**Key Characteristics:**
- **Serverless:** Uses Snowflake-managed compute resources (not user warehouses)
- **File-based:** Works with staged files (internal or external stages)
- **Near real-time:** Typical latency of 1-2 minutes for properly sized files
- **Event-driven:** Auto-ingest mode uses cloud storage event notifications
- **Idempotent:** Tracks loaded files to prevent duplicate data

### 1.2 Snowpipe vs Bulk Loading

**Bulk Loading (COPY INTO):**
- Use Case: Large historical loads, scheduled batches
- Compute: User-specified warehouse
- Triggering: Manual or scheduled execution
- Transactions: Single transaction per COPY
- Load History: 64 days in table metadata
- Authentication: User session (any method)
- Cost Model: Warehouse time (per-second billing)
- Best For: Initial loads, large batches, scheduled ETL

**Snowpipe:**
- Use Case: Continuous, near-real-time micro-batches
- Compute: Snowflake-managed serverless compute
- Triggering: Automated (event-driven or REST API)
- Transactions: Multiple transactions based on file size/count
- Load History: 14 days in pipe metadata
- Authentication: JWT with key pairs (REST API)
- Cost Model: Snowpipe compute (per-second billing)
- Best For: Streaming sources, event-driven, continuous feeds

**Rule:** Do NOT use Snowpipe for one-time bulk historical loads. Use COPY INTO with appropriately sized warehouses instead.

## Snowpipe Ingestion Methods

### 2.1 Auto-Ingest (Recommended)

**How it works:**
1. Files are staged in cloud storage (S3, GCS, Azure Blob)
2. Cloud storage sends event notification to queue (SNS, Pub/Sub, Event Grid)
3. Snowpipe polls event queue and discovers new files
4. Files are loaded automatically based on pipe's COPY statement

**Benefits:**
- Fully automated; no application code needed
- Scalable and reliable
- Simplest architecture for continuous loads

**Requirements:**
- External stage with cloud storage
- Event notification configuration (SNS topic, Pub/Sub subscription, Event Grid)
- Proper IAM/permissions for Snowflake to access storage and notifications

**When to use:**
- Continuous file arrival from external systems
- Event-driven architectures
- Minimal custom logic required

### 2.2 REST API

**How it works:**
1. Application stages files in cloud storage or internal stage
2. Application calls Snowpipe REST endpoint with pipe name and file list
3. Snowpipe queues files for loading
4. Files are loaded based on pipe's COPY statement

**Benefits:**
- Programmatic control over when files are loaded
- Works with internal stages
- Integration with custom workflows

**Requirements:**
- Key pair authentication (JWT)
- REST API client implementation
- Application manages file staging and API calls

**When to use:**
- Internal stage usage required
- Custom orchestration or complex workflows
- Need explicit control over load timing

### 2.3 Comparison Matrix

**Auto-Ingest:**
- Stage Type: External only
- Automation: Fully automated
- Event Source: Cloud storage events
- Setup Complexity: Moderate (cloud config)
- Authentication: IAM/service principal
- Best For: Continuous external feeds

**REST API:**
- Stage Type: Internal or external
- Automation: Manual/programmatic
- Event Source: Application-initiated
- Setup Complexity: Low (API calls)
- Authentication: JWT key pair
- Best For: Custom workflows, internal stages

## File Sizing Best Practices

### 3.1 Recommended File Sizes

**Rule:** Target **100-250 MB compressed** files for optimal Snowpipe performance and cost efficiency.

**Staging Frequency:** Ideally stage files **once per minute** to balance cost (queue management overhead) and latency.

**Why this matters:**
- **Too small (<10MB):** High overhead from queue management; poor cost efficiency
- **Optimal (100-250MB):** Best balance of throughput, latency, and cost
- **Too large (>1GB):** Increased latency; potential timeout issues; harder to parallelize

### 3.2 File Format Best Practices

**Supported formats:** CSV, JSON, Avro, ORC, Parquet, XML

**Recommendations:**
- **Compressed formats:** Use GZIP, Brotli, or Zstandard compression
- **Parquet/ORC:** Best for large datasets; native columnar support
- **JSON/Avro:** Good for semi-structured data with schema evolution
- **CSV:** Simple but less efficient; use for small datasets or compatibility

**Rule:** Always compress files before staging. Uncompressed files waste storage and bandwidth.

## Snowpipe DDL and Configuration

### 4.1 Creating Pipes

**Basic Pipe Syntax:**
```sql
CREATE OR REPLACE PIPE <database>.<schema>.<pipe_name>
  AUTO_INGEST = TRUE  -- For auto-ingest; FALSE for REST API
  AWS_SNS_TOPIC = '<arn>'  -- For AWS S3 auto-ingest
  -- INTEGRATION = '<notification_integration_name>'  -- Alternative for Azure/GCS
  COMMENT = '<description>'
AS
  COPY INTO <target_table>
  FROM @<stage_name>
  FILE_FORMAT = (TYPE = '<format>' <options>)
  ON_ERROR = CONTINUE  -- Or SKIP_FILE, ABORT_STATEMENT
  -- Optional: pattern matching, transformations
;
```

**Complete Auto-Ingest Example (AWS S3):**
```sql
-- Create external stage
CREATE OR REPLACE STAGE STG_S3_RAW_EVENTS
  URL = 's3://my-bucket/events/'
  STORAGE_INTEGRATION = SINT_S3_PROD
  FILE_FORMAT = FF_JSON_GZIP;

-- Create target table
CREATE OR REPLACE TABLE RAW_EVENTS (
  event_id STRING,
  event_type STRING,
  event_ts TIMESTAMP_NTZ,
  payload VARIANT,
  _metadata VARIANT DEFAULT NULL,
  loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create pipe with auto-ingest
CREATE OR REPLACE PIPE PIPE_LOAD_RAW_EVENTS
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-events'
  COMMENT = 'Auto-ingest pipe for raw events from S3 - loads JSON files as they arrive'
AS
  COPY INTO RAW_EVENTS (event_id, event_type, event_ts, payload)
  FROM (
    SELECT
      $1:event_id::STRING,
      $1:event_type::STRING,
      $1:event_timestamp::TIMESTAMP_NTZ,
      $1:payload::VARIANT
    FROM @STG_S3_RAW_EVENTS
  )
  FILE_FORMAT = FF_JSON_GZIP
  ON_ERROR = CONTINUE;  -- Continue loading other files on error

-- Show pipe details including SQS queue ARN for S3 event notifications
SHOW PIPES LIKE 'PIPE_LOAD_RAW_EVENTS';
DESC PIPE PIPE_LOAD_RAW_EVENTS;
```

**REST API Pipe Example:**
```sql
-- Create pipe for REST API triggering (no AUTO_INGEST)
CREATE OR REPLACE PIPE PIPE_MANUAL_ORDERS
  AUTO_INGEST = FALSE
  COMMENT = 'REST API-triggered pipe for order files from internal stage'
AS
  COPY INTO ORDERS
  FROM @STG_INTERNAL_ORDERS
  FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"')
  ON_ERROR = SKIP_FILE
  PATTERN = '.*orders_[0-9]{8}\\.csv\\.gz';
```

### 4.2 Pattern Matching and Transformations

**File Pattern Filtering:**
```sql
CREATE OR REPLACE PIPE PIPE_FILTERED_LOGS
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:logs-topic'
AS
  COPY INTO APP_LOGS
  FROM @STG_S3_LOGS
  FILE_FORMAT = FF_JSON_GZIP
  PATTERN = '.*application/prod/.*\\.json\\.gz'  -- Only load files matching pattern
  ON_ERROR = CONTINUE;
```

**Data Transformations During Load:**
```sql
CREATE OR REPLACE PIPE PIPE_TRANSFORM_SALES
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:sales-topic'
AS
  COPY INTO SALES_FACT (sale_id, customer_id, sale_date, amount, region)
  FROM (
    SELECT
      $1:id::STRING,
      $1:customer_id::NUMBER,
      TO_TIMESTAMP($1:sale_timestamp::STRING),
      $1:amount::NUMBER(10,2),
      UPPER($1:region::STRING)  -- Transform during load
    FROM @STG_S3_SALES
  )
  FILE_FORMAT = FF_PARQUET
  ON_ERROR = CONTINUE;
```

## Cloud Event Configuration

### 5.1 AWS S3 Event Notifications

**Step 1: Create SNS Topic and Subscribe SQS Queue**
```bash
# AWS CLI commands (run once during setup)
# 1. Get the SQS queue ARN from SHOW PIPES output
SHOW PIPES LIKE 'PIPE_LOAD_RAW_EVENTS';
# Copy the "notification_channel" value (SQS ARN)

# 2. Configure S3 bucket to send events to SNS topic
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration '{
    "TopicConfigurations": [{
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:snowpipe-events",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [{
            "Name": "prefix",
            "Value": "events/"
          }]
        }
      }
    }]
  }'
```

**Step 2: Subscribe Snowflake SQS Queue to SNS Topic**
```bash
# Subscribe the Snowflake SQS queue to your SNS topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:snowpipe-events \
  --protocol sqs \
  --notification-endpoint <SNOWFLAKE_SQS_ARN_FROM_SHOW_PIPES>
```

**Snowflake Documentation Reference:** [Automating Snowpipe using Amazon SNS](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto-s3)

### 5.2 Azure Event Grid Configuration

**Create Notification Integration:**
```sql
CREATE NOTIFICATION INTEGRATION NINT_AZURE_EVENTS
  ENABLED = TRUE
  TYPE = QUEUE
  NOTIFICATION_PROVIDER = AZURE_STORAGE_QUEUE
  AZURE_STORAGE_QUEUE_PRIMARY_URI = '<queue_uri>'
  AZURE_TENANT_ID = '<tenant_id>';
```

**Create Pipe with Integration:**
```sql
CREATE OR REPLACE PIPE PIPE_AZURE_EVENTS
  AUTO_INGEST = TRUE
  INTEGRATION = 'NINT_AZURE_EVENTS'
AS
  COPY INTO EVENTS_TABLE
  FROM @STG_AZURE_BLOB
  FILE_FORMAT = FF_JSON_GZIP;
```

**Snowflake Documentation Reference:** [Automating Snowpipe using Azure Event Grid](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto-azure)

### 5.3 GCS Pub/Sub Configuration

**Create Notification Integration:**
```sql
CREATE NOTIFICATION INTEGRATION NINT_GCS_PUBSUB
  ENABLED = TRUE
  TYPE = QUEUE
  NOTIFICATION_PROVIDER = GCP_PUBSUB
  GCP_PUBSUB_SUBSCRIPTION_NAME = '<subscription_name>';
```

**Create Pipe with Integration:**
```sql
CREATE OR REPLACE PIPE PIPE_GCS_EVENTS
  AUTO_INGEST = TRUE
  INTEGRATION = 'NINT_GCS_PUBSUB'
AS
  COPY INTO EVENTS_TABLE
  FROM @STG_GCS_BUCKET
  FILE_FORMAT = FF_JSON_GZIP;
```

**Snowflake Documentation Reference:** [Automating Snowpipe using GCS Pub/Sub](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto-gcs)

## Snowpipe REST API Usage

### 6.1 Authentication Setup

**Generate Key Pair:**
```bash
# Generate private key
openssl genrsa -out snowpipe_key.pem 2048

# Generate public key
openssl rsa -in snowpipe_key.pem -pubout -out snowpipe_key.pub

# Get public key fingerprint for Snowflake
openssl rsa -pubin -in snowpipe_key.pub -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
```

**Assign Public Key to Snowflake User:**
```sql
ALTER USER snowpipe_user SET RSA_PUBLIC_KEY='<public_key_contents>';
```

### 6.2 REST API Endpoints

**Insert Files Endpoint:**
```http
POST /v1/data/pipes/<pipe_name>/insertFiles
Host: <account>.snowflakecomputing.com
Authorization: Bearer <JWT_token>
Content-Type: application/json

{
  "files": [
    {"path": "path/to/file1.json.gz"},
    {"path": "path/to/file2.json.gz"}
  ]
}
```

**Python Example:**
```python
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

# Load private key
with open('snowpipe_key.pem', 'rb') as pem_file:
    private_key = serialization.load_pem_private_key(
        pem_file.read(),
        password=None,
        backend=default_backend()
    )

# Generate JWT token
account_identifier = 'ORGNAME-ACCOUNTNAME'
user = 'SNOWPIPE_USER'
public_key_fingerprint = 'SHA256:FINGERPRINT_HERE'

payload = {
    'iss': f'{account_identifier}.{user}.{public_key_fingerprint}',
    'sub': f'{account_identifier}.{user}',
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(minutes=59)
}

token = jwt.encode(payload, private_key, algorithm='RS256')

# Call insertFiles API
url = f'https://{account_identifier}.snowflakecomputing.com/v1/data/pipes/MY_DB.MY_SCHEMA.PIPE_NAME/insertFiles'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
data = {
    'files': [
        {'path': 'path/to/file1.json.gz'},
        {'path': 'path/to/file2.json.gz'}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

**Snowflake Documentation Reference:** [Snowpipe REST API](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-gs)

## Security and Access Control

### 7.1 Privileges Required

**Creating Pipes:**
```sql
-- Grant privileges to create and manage pipes
GRANT USAGE ON DATABASE MY_DB TO ROLE PIPE_ADMIN;
GRANT USAGE, CREATE PIPE ON SCHEMA MY_DB.MY_SCHEMA TO ROLE PIPE_ADMIN;
GRANT USAGE ON STAGE MY_DB.MY_SCHEMA.STG_S3_RAW TO ROLE PIPE_ADMIN;
GRANT SELECT, INSERT ON TABLE MY_DB.MY_SCHEMA.TARGET_TABLE TO ROLE PIPE_ADMIN;
```

**Owning Pipes (Minimum Privileges):**
```sql
-- Pipe owner needs these privileges
GRANT USAGE ON DATABASE MY_DB TO ROLE PIPE_OWNER;
GRANT USAGE ON SCHEMA MY_DB.MY_SCHEMA TO ROLE PIPE_OWNER;
GRANT OWNERSHIP ON PIPE MY_DB.MY_SCHEMA.PIPE_NAME TO ROLE PIPE_OWNER;
GRANT USAGE ON STAGE MY_DB.MY_SCHEMA.STG_S3_RAW TO ROLE PIPE_OWNER;  -- External
GRANT READ ON STAGE MY_DB.MY_SCHEMA.STG_INTERNAL TO ROLE PIPE_OWNER;  -- Internal
GRANT SELECT, INSERT ON TABLE MY_DB.MY_SCHEMA.TARGET_TABLE TO ROLE PIPE_OWNER;
```

**Operating Pipes (Pause/Resume):**
```sql
-- Grant OPERATE privilege to pause/resume pipes
GRANT USAGE ON DATABASE MY_DB TO ROLE PIPE_OPERATOR;
GRANT USAGE ON SCHEMA MY_DB.MY_SCHEMA TO ROLE PIPE_OPERATOR;
GRANT OPERATE ON PIPE MY_DB.MY_SCHEMA.PIPE_NAME TO ROLE PIPE_OPERATOR;
GRANT USAGE ON STAGE MY_DB.MY_SCHEMA.STG_S3_RAW TO ROLE PIPE_OPERATOR;
GRANT SELECT, INSERT ON TABLE MY_DB.MY_SCHEMA.TARGET_TABLE TO ROLE PIPE_OPERATOR;
```

### 7.2 Pipe Management Commands

**Pause and Resume:**
```sql
-- Pause pipe (stop processing new files)
ALTER PIPE PIPE_LOAD_RAW_EVENTS SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume pipe
ALTER PIPE PIPE_LOAD_RAW_EVENTS SET PIPE_EXECUTION_PAUSED = FALSE;

-- Check pipe status
SHOW PIPES LIKE 'PIPE_LOAD_RAW_EVENTS';
```

**Refresh Pipe (Force Load):**
```sql
-- Manually refresh pipe to load files (useful for testing)
ALTER PIPE PIPE_LOAD_RAW_EVENTS REFRESH;

-- Refresh with specific file prefix
ALTER PIPE PIPE_LOAD_RAW_EVENTS REFRESH PREFIX = 'events/2025/01/';
```

## Monitoring and Cost Management

**For comprehensive monitoring, cost tracking, and performance analysis, see `121b-snowflake-snowpipe-monitoring.md`**

Key monitoring areas:
- Load history queries and error tracking
- Cost monitoring and credit usage analysis
- Performance metrics and latency tracking
- Alert configuration and dashboard queries

**Quick Reference - Check Pipe Status:**
```sql
-- Check pipe status
SHOW PIPES LIKE 'PIPE_NAME';

-- Check recent loads
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'DB.SCHEMA.PIPE_NAME'
))
ORDER BY START_TIME DESC;
```

## File-Based vs SDK-Based Ingestion

**This rule covers file-based Snowpipe only.** For SDK-based streaming ingestion with sub-second latency, see `121a-snowflake-snowpipe-streaming.md`.

**Decision Matrix:**

**Use File-Based Snowpipe (this rule) when:**
- Data is already in files (S3, GCS, Azure Blob)
- 1-2 minute latency is acceptable
- Simpler setup preferred
- File-based event notifications available
- Batch processing patterns

**Use Snowpipe Streaming (121a) when:**
- Sub-second latency is required
- Data arrives row-by-row or in small micro-batches
- Direct integration from streaming sources (Kafka, Kinesis, custom apps)
- Need exactly-once semantics with offset tracking
- Schema evolution is important

## Troubleshooting

**For comprehensive troubleshooting and debugging patterns, see `121c-snowflake-snowpipe-troubleshooting.md`**

Common issues covered:
- Files not loading (pipe paused, event notifications, permissions)
- High latency (file sizes, transformations, concurrency)
- Duplicate data (mixing bulk COPY and Snowpipe)
- High costs (micro-files, staging frequency, transformations)
- Schema errors and data type mismatches
- Authentication and connection failures

**Quick Reference - Basic Diagnostics:**
```sql
-- Check pipe status
SHOW PIPES LIKE 'PIPE_NAME';

-- Check for errors
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'DB.SCHEMA.PIPE_NAME'
))
WHERE ERROR_COUNT > 0
ORDER BY START_TIME DESC;

-- Verify stage contents
LIST @STAGE_NAME;
```
