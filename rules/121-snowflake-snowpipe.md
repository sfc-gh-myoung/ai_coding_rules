# Snowflake Snowpipe and Snowpipe Streaming

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** streaming data, micro-batching, file-based ingestion, SDK, event notifications, COPY INTO, create pipe, auto ingest, data ingestion, streaming load, pipe errors, pipe management, ingestion monitoring
**TokenBudget:** ~6900
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/108-snowflake-data-loading.md, rules/104-snowflake-streams-tasks.md

## Purpose
Establish comprehensive best practices for continuous data ingestion using Snowflake Snowpipe (serverless, file-based) and Snowpipe Streaming (SDK-based, low-latency) including architecture selection, configuration, security, monitoring, and cost optimization.

## Rule Scope

Snowpipe serverless (auto-ingest and REST API) and Snowpipe Streaming (high-performance and classic architectures) for continuous data loading

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Choose ingestion method** - Auto-ingest for event-driven, REST for programmatic, Streaming for low-latency
- **Optimize file sizes** - 100-250MB compressed for Snowpipe
- **Configure cloud events** - SNS/Event Grid/Pub/Sub for auto-ingest
- **Validate COPY statements** - Test before pipe creation
- **Monitor load history** - Track latency, errors, costs
- **Set up error notifications** - Alert on ingestion failures
- **Never use for bulk loads** - Use COPY INTO for historical data

**Quick Checklist:**
- [ ] Ingestion pattern determined
- [ ] File sizes optimized (100-250MB)
- [ ] Cloud storage configured
- [ ] Stages created with permissions
- [ ] COPY statement validated
- [ ] Pipe created and tested
- [ ] Monitoring queries configured

## Contract

<contract>
<inputs_prereqs>
Snowflake account with pipe creation privileges (`CREATE PIPE`); configured stages (internal or external); target tables with appropriate schema; cloud storage with event notifications (for auto-ingest); Snowpipe Streaming SDK setup (for streaming)
</inputs_prereqs>

<mandatory>
Snowflake DDL for pipes; cloud storage event configuration (SNS, Azure Event Grid, GCS Pub/Sub); Snowpipe REST API; Snowpipe Streaming SDK (Java, Python, .NET); monitoring queries
</mandatory>

<forbidden>
Using Snowpipe for bulk historical loads; mixing bulk COPY and Snowpipe on same files; undersized files (<1MB); Snowpipe without proper file sizing
</forbidden>

<steps>
1. Determine ingestion pattern (auto-ingest vs REST API vs Streaming)
2. Configure cloud storage and stages with appropriate permissions
3. Optimize file sizing (100-250MB compressed for Snowpipe)
4. Create pipes with validated COPY statements
5. Configure security and access controls
6. Set up monitoring and alerting
7. Test latency and throughput under expected load
8. Document cost baseline and optimize
</steps>

<output_format>
Complete pipe DDL with comments; cloud event configuration; Snowpipe Streaming code examples; monitoring queries; cost tracking patterns
</output_format>

<validation>
Pipe created successfully; files loading automatically (auto-ingest) or via API; load history accessible; latency within requirements; error notifications working; cost tracking functional
</validation>

<design_principles>
- **File-Based vs Streaming:** Use Snowpipe for micro-batch file ingestion; use Snowpipe Streaming for low-latency, row-level ingestion
- **Auto-Ingest First:** Prefer auto-ingest with cloud event notifications over REST API for simplicity and automation
- **File Sizing:** Stage files of 100-250MB compressed, ideally once per minute for optimal cost/performance
- **Serverless Compute:** Snowpipe uses Snowflake-managed compute (not user warehouses); billed per-second of compute used
- **Load History:** Snowpipe metadata retained for 14 days (vs 64 days for bulk loads); query via REST API or SQL
- **Idempotency:** Snowpipe tracks loaded files to prevent duplicates; do not mix bulk and Snowpipe on same files
- **Latency Management:** Expect variable latency based on file size, format, transformations; test to establish baseline
- **High-Performance Streaming:** Use for sub-second latency requirements with direct SDK integration
</design_principles>

</contract>

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

## Post-Execution Checklist
- [ ] Ingestion method selected (auto-ingest, REST API, or Streaming)
- [ ] File sizes optimized (100-250MB compressed for file-based Snowpipe)
- [ ] Cloud event notifications configured correctly (for auto-ingest)
- [ ] Stages created with proper permissions and storage integrations
- [ ] Target tables exist with appropriate schema
- [ ] Pipes created with validated COPY statements
- [ ] ON_ERROR setting appropriate for workload (CONTINUE/SKIP_FILE/ABORT)
- [ ] Security privileges granted (CREATE PIPE, USAGE, SELECT, INSERT)
- [ ] Monitoring queries configured and tested
- [ ] Load history accessible and reviewed
- [ ] Cost tracking implemented and baseline established
- [ ] Error notifications configured (for production pipes)
- [ ] Documentation updated with pipe details and architecture

## Validation
- **Success Checks:** Pipe created successfully and shows in SHOW PIPES; files loading automatically (auto-ingest) or via REST API/SDK; load history shows successful inserts; latency within requirements (<2 min for file-based, <1 sec for streaming); no duplicate data; error rate acceptable (<5%); cost per GB within expected range
- **Negative Tests:** Pipe creation fails without proper privileges; files not loading due to misconfigured notifications; duplicate loads when mixing bulk and Snowpipe; high latency with undersized files (<1MB); excessive costs with micro-batches; schema errors with missing columns; offset tracking failures in streaming

> **Investigation Required**
> When applying this rule:
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

## References

### External Documentation
- [Snowpipe Introduction](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) - Overview of Snowpipe architecture and capabilities
- [Snowpipe Auto-Ingest](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto) - Configuring automated data loads with cloud messaging
- [Snowpipe REST API](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-overview) - REST endpoint reference for programmatic control
- [Snowpipe Costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing) - Billing model and cost optimization
- [Snowpipe Streaming Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview) - Introduction to Snowpipe Streaming SDK
- [High-Performance Streaming Architecture](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview) - Optimized streaming for high-volume workloads
- [Classic Streaming Architecture](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-classic-overview) - Standard Snowpipe Streaming architecture
- [Streaming Architecture Comparison](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-comparison) - High-performance vs classic comparison
- [Snowpipe Error Notifications](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors) - Error handling and notification configuration
- [Snowpipe Troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-troubleshooting) - Common issues and solutions

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **Data Loading**: `rules/108-snowflake-data-loading.md` - Stages and bulk loading with COPY INTO
- **Streams and Tasks**: `rules/104-snowflake-streams-tasks.md` - Incremental pipelines and change data capture
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md` - Warehouse sizing (note: Snowpipe uses serverless compute)
- **Cost Governance**: `rules/105-snowflake-cost-governance.md` - Resource monitors and cost optimization
- **Security Governance**: `rules/107-snowflake-security-governance.md` - Access control and security policies

## 1. Snowpipe Overview and Architecture

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

## 2. Snowpipe Ingestion Methods

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

## 3. File Sizing Best Practices

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

## 4. Snowpipe DDL and Configuration

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

## 5. Cloud Event Configuration

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

## 6. Snowpipe REST API Usage

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

## 7. Security and Access Control

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

## 8. Monitoring and Load History

### 8.1 Load History Queries

**View Recent Loads:**
```sql
-- Get load history for a specific pipe (last 14 days)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP()),
  DATE_RANGE_END => CURRENT_TIMESTAMP(),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
ORDER BY START_TIME DESC;

-- Summary of files loaded per day
SELECT
  DATE_TRUNC('day', START_TIME) AS load_date,
  COUNT(*) AS num_loads,
  SUM(FILES_INSERTED) AS total_files,
  SUM(ROWS_INSERTED) AS total_rows,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb,
  AVG(BYTES_INSERTED / NULLIF(FILES_INSERTED, 0)) AS avg_file_size_bytes
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -30, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY load_date DESC;
```

**Check for Errors:**
```sql
-- Find loads with errors
SELECT
  START_TIME,
  FILES_INSERTED,
  ROWS_INSERTED,
  ERROR_COUNT,
  ERROR_LIMIT,
  FIRST_ERROR_MESSAGE,
  FIRST_ERROR_LINE_NUMBER,
  FIRST_ERROR_CHARACTER_POS,
  FIRST_ERROR_COLUMN_NAME
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'MY_DB.MY_SCHEMA.PIPE_LOAD_RAW_EVENTS'
))
WHERE ERROR_COUNT > 0
ORDER BY START_TIME DESC;
```

### 8.2 Copy History for Snowpipe

```sql
-- Query COPY_HISTORY for Snowpipe loads
SELECT
  TABLE_NAME,
  STAGE_LOCATION,
  FILE_NAME,
  FILE_SIZE,
  ROW_COUNT,
  ROW_PARSED,
  FIRST_ERROR_MESSAGE,
  FIRST_ERROR_LINE_NUMBER,
  LAST_LOAD_TIME,
  STATUS
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE TABLE_NAME = 'RAW_EVENTS'
  AND PIPE_NAME = 'PIPE_LOAD_RAW_EVENTS'
  AND LAST_LOAD_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY LAST_LOAD_TIME DESC;
```

### 8.3 Monitoring Best Practices

**Set up alerts for:**
- Pipes in error state or paused unexpectedly
- High error rates (>5% of rows)
- Load latency exceeding SLAs
- Significant changes in file counts or sizes
- Pipes consuming excessive compute credits

## 9. Cost Management

### 9.1 Snowpipe Billing Model

**How Snowpipe is billed:**
- Billed based on **compute resources used** in the Snowpipe warehouse
- Charged per-second with a 1-minute minimum per compute cluster
- Separate from user warehouse credits
- Costs appear in `SNOWPIPE` usage type in `ACCOUNT_USAGE.METERING_HISTORY`

**Cost Monitoring Query:**
```sql
-- Daily Snowpipe costs (last 30 days)
SELECT
  DATE_TRUNC('day', START_TIME) AS usage_date,
  SUM(CREDITS_USED) AS snowpipe_credits,
  COUNT(DISTINCT PIPE_NAME) AS num_pipes,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb_loaded
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY usage_date DESC;

-- Cost per pipe
SELECT
  PIPE_NAME,
  SUM(CREDITS_USED) AS total_credits,
  SUM(FILES_INSERTED) AS total_files,
  SUM(ROWS_INSERTED) AS total_rows,
  SUM(BYTES_INSERTED) / POWER(1024, 3) AS total_gb,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(FILES_INSERTED), 0), 6) AS credits_per_file,
  ROUND(SUM(CREDITS_USED) / NULLIF(SUM(BYTES_INSERTED) / POWER(1024, 3), 0), 4) AS credits_per_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY PIPE_NAME
ORDER BY total_credits DESC;
```

### 9.2 Cost Optimization Strategies

**Best Practices:**
1. **Optimize file sizes:** 100-250MB compressed files minimize overhead
2. **Stage files once per minute:** Avoid micro-files (<1MB)
3. **Use pattern matching:** Filter files at pipe level to reduce processing
4. **Minimize transformations:** Complex SELECT logic increases compute time
5. **Batch notifications:** Configure cloud event filtering to reduce noise
6. **Monitor and right-size:** Review cost per GB and optimize accordingly

**Snowflake Documentation Reference:** [Snowpipe Costs](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing)

## 10. Snowpipe Streaming Overview

### 10.1 What is Snowpipe Streaming?

**Snowpipe Streaming** provides a direct, low-latency alternative to file-based Snowpipe by using the Snowpipe Streaming SDK to write rows directly to Snowflake tables.

**Key Characteristics:**
- **Row-level ingestion:** No file staging required
- **Sub-second latency:** Typically <1 second for data availability
- **SDK-based:** Java, Python, .NET SDKs available
- **Channel-based:** Uses channels for offset tracking and exactly-once semantics
- **Schema evolution:** Automatic schema detection and evolution supported

### 10.2 High-Performance vs Classic Architecture

**High-Performance Architecture:**
- Latency: Sub-second (optimized)
- Throughput: Higher (optimized for large volumes)
- Overhead: Lower (direct write path)
- Complexity: Slightly more complex setup
- Use Case: High-volume, low-latency streaming
- Availability: AWS, Azure, GCP

**Classic Architecture:**
- Latency: 1-2 seconds
- Throughput: Moderate
- Overhead: Higher (metadata operations)
- Complexity: Simpler setup
- Use Case: Standard streaming workloads
- Availability: AWS, Azure, GCP

**Rule:** Prefer **High-Performance Architecture** for production workloads with strict latency and throughput requirements.

**Snowflake Documentation References:**
- [High-Performance Architecture Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview)
- [Classic Architecture Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-classic-overview)
- [Architecture Comparison](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-comparison)

### 10.3 When to Use Snowpipe Streaming

**Use Snowpipe Streaming when:**
- Sub-second latency is required
- Data arrives row-by-row or in small micro-batches
- Direct integration from streaming sources (Kafka, Kinesis, custom apps)
- Need exactly-once semantics with offset tracking
- Schema evolution is important

**Use regular Snowpipe (file-based) when:**
- Data is already in files (S3, GCS, Azure Blob)
- 1-2 minute latency is acceptable
- Simpler setup preferred
- File-based event notifications available

## 11. Snowpipe Streaming SDK Usage

### 11.1 Java SDK Example

**Setup:**
```xml
<!-- Maven dependency -->
<dependency>
    <groupId>net.snowflake</groupId>
    <artifactId>snowflake-ingest-sdk</artifactId>
    <version>2.0.0</version>
</dependency>
```

**Basic Ingestion:**
```java
import net.snowflake.ingest.streaming.*;
import java.util.*;

public class SnowpipeStreamingExample {
    public static void main(String[] args) throws Exception {
        // Create client
        Properties props = new Properties();
        props.put("user", "USERNAME");
        props.put("private_key", "PRIVATE_KEY_CONTENT");
        props.put("account", "ACCOUNT_IDENTIFIER");
        props.put("role", "ROLE_NAME");
        props.put("warehouse", "WAREHOUSE_NAME");  // Optional for high-perf
        props.put("database", "DATABASE_NAME");
        props.put("schema", "SCHEMA_NAME");

        SnowflakeStreamingIngestClient client =
            SnowflakeStreamingIngestClientFactory.builder("CLIENT_NAME")
                .setProperties(props)
                .build();

        // Open channel
        OpenChannelRequest channelRequest = OpenChannelRequest.builder("CHANNEL_NAME")
            .setDBName("DATABASE_NAME")
            .setSchemaName("SCHEMA_NAME")
            .setTableName("TABLE_NAME")
            .setOnErrorOption(OpenChannelRequest.OnErrorOption.CONTINUE)
            .build();

        SnowflakeStreamingIngestChannel channel = client.openChannel(channelRequest);

        // Insert rows
        Map<String, Object> row = new HashMap<>();
        row.put("id", 1);
        row.put("name", "Alice");
        row.put("timestamp", System.currentTimeMillis());

        InsertValidationResponse response = channel.insertRow(row, "offset_1");

        if (response.hasErrors()) {
            System.err.println("Insert errors: " + response.getInsertErrors());
        }

        // Close channel and client
        channel.close().get();
        client.close();
    }
}
```

### 11.2 Python SDK Example

**Setup:**
```bash
pip install snowflake-ingest
```

**Basic Ingestion:**
```python
from snowflake.ingest import SnowflakeStreamingIngestClient
from snowflake.ingest import StreamingIngestChannel
from snowflake.ingest.utils.crypto import load_private_key
import time

# Load private key
with open('snowflake_key.pem', 'rb') as f:
    private_key = load_private_key(f.read(), None)

# Create client
client = SnowflakeStreamingIngestClient(
    account='ACCOUNT_IDENTIFIER',
    user='USERNAME',
    private_key=private_key,
    role='ROLE_NAME',
    warehouse='WAREHOUSE_NAME',  # Optional for high-perf
)

# Open channel
channel = client.open_channel(
    database='DATABASE_NAME',
    schema='SCHEMA_NAME',
    table='TABLE_NAME',
    channel_name='CHANNEL_NAME',
    on_error='CONTINUE'
)

# Insert rows
rows = [
    {'id': 1, 'name': 'Alice', 'timestamp': int(time.time())},
    {'id': 2, 'name': 'Bob', 'timestamp': int(time.time())},
]

for idx, row in enumerate(rows):
    response = channel.insert_row(row, offset_token=f'offset_{idx}')
    if response.has_errors():
        print(f"Insert errors: {response.insert_errors}")

# Close channel and client
channel.close()
client.close()
```

### 11.3 Channel Management

**Channels** provide:
- **Offset tracking:** Exactly-once semantics with offset tokens
- **Isolation:** Separate channels for different data sources
- **Monitoring:** Per-channel metrics and status

**Best Practices:**
- Use descriptive channel names (e.g., `kafka_topic1_partition0`)
- One channel per logical data stream or partition
- Monitor channel lag and throughput
- Close channels gracefully on application shutdown

## 12. Schema Evolution

**Snowpipe Streaming supports automatic schema evolution:**

```python
# Initial table schema: id, name
# Insert row with new column
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
channel.insert_row(row, 'offset_1')

# Snowflake automatically adds 'email' column to table
```

**Schema Evolution Modes:**
- **ADD_COLUMNS:** Automatically add missing columns (default)
- **FAIL_MISSING_COLUMNS:** Reject rows with unknown columns
- **IGNORE_MISSING_COLUMNS:** Insert only known columns

**Rule:** Use schema evolution cautiously in production. Prefer explicit schema management for critical tables.

## 13. Snowpipe Streaming Monitoring

### 13.1 Channel Status

```sql
-- Query channel status
SELECT
  channel_name,
  table_name,
  offset_token,
  row_count,
  start_time,
  last_commit_time
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'MY_DB'
  AND schema_name = 'MY_SCHEMA'
ORDER BY last_commit_time DESC;
```

### 13.2 Streaming Load History

```sql
-- Query streaming load history
SELECT
  table_name,
  channel_name,
  row_count,
  bytes_received,
  start_time,
  end_time,
  DATEDIFF(second, start_time, end_time) AS latency_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE table_name = 'MY_TABLE'
  AND start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

## 14. Troubleshooting

### 14.1 Common Snowpipe Issues

**Files not loading:**
- Check pipe status: `SHOW PIPES;` - ensure not paused
- Verify cloud event notifications are configured correctly
- Check load history for errors: `INFORMATION_SCHEMA.PIPE_USAGE_HISTORY`
- Verify stage permissions and file accessibility

**High latency:**
- Check file sizes (optimize to 100-250MB compressed)
- Review COPY statement complexity (minimize transformations)
- Check for concurrent loads and resource contention
- Verify ON_ERROR setting (CONTINUE vs SKIP_FILE vs ABORT)

**Duplicate data:**
- Never mix bulk COPY and Snowpipe on same files
- Snowpipe tracks loaded files automatically
- Check if files were renamed/modified (different eTag)

**High costs:**
- Optimize file sizes (avoid micro-files <1MB)
- Stage files once per minute, not continuously
- Minimize transformations in COPY statement
- Use pattern matching to filter files at pipe level

### 14.2 Common Snowpipe Streaming Issues

**Connection failures:**
- Verify authentication (key pair, JWT generation)
- Check network connectivity and firewall rules
- Ensure warehouse is available (if using classic architecture)

**Schema errors:**
- Verify table exists and columns match
- Check schema evolution settings
- Ensure INSERT privileges on target table

**Offset tracking issues:**
- Use unique, monotonically increasing offset tokens
- Handle channel reopens gracefully
- Implement idempotency in application logic

**Snowflake Documentation Reference:** [Snowpipe Troubleshooting](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-troubleshooting)
