# 121 Example: Snowpipe Auto-Ingest (AWS S3)

> **EXAMPLE FILE** - Reference implementation for `121-snowflake-snowpipe.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 121-snowflake-snowpipe.md
**Demonstrates:** Complete end-to-end Snowpipe auto-ingest setup with AWS S3, SNS notifications, and monitoring
**Use When:** Setting up continuous file-based data ingestion from AWS S3 with automatic loading
**Version:** 1.0
**Last Validated:** 2026-01-27

## Prerequisites

- [ ] AWS S3 bucket with data files (JSON/GZIP format)
- [ ] AWS IAM role with trust policy for Snowflake
- [ ] AWS SNS topic for event notifications
- [ ] Snowflake account with ACCOUNTADMIN or CREATE INTEGRATION privilege
- [ ] Target database and schema exist

## Implementation

```sql
-- Step 1: Create storage integration (AWS S3)
-- This establishes trust between Snowflake and your AWS account
CREATE STORAGE INTEGRATION SINT_S3_RAW_DATA
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-s3-access'
  STORAGE_ALLOWED_LOCATIONS = ('s3://my-bucket/raw-data/');

-- Get the AWS IAM user ARN and external ID for trust policy
DESC INTEGRATION SINT_S3_RAW_DATA;
-- Copy STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID
-- Use these to update your AWS IAM role trust policy

-- Step 2: Create file format with explicit settings
-- NEVER rely on defaults - always specify format options
CREATE FILE FORMAT FF_JSON_GZIP
  TYPE = JSON
  COMPRESSION = GZIP
  STRIP_OUTER_ARRAY = TRUE
  ENABLE_OCTAL = FALSE
  ALLOW_DUPLICATE = FALSE;

-- Step 3: Create external stage using storage integration
CREATE STAGE STG_S3_RAW_DATA
  URL = 's3://my-bucket/raw-data/'
  STORAGE_INTEGRATION = SINT_S3_RAW_DATA
  FILE_FORMAT = FF_JSON_GZIP;

-- Verify stage is accessible
LIST @STG_S3_RAW_DATA;

-- Step 4: Create target table with metadata columns
CREATE TABLE RAW_DATA (
  record_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP_NTZ,
  payload VARIANT,
  -- Metadata columns for auditing
  loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  source_file STRING DEFAULT METADATA$FILENAME
);

-- Step 5: Test COPY statement BEFORE creating pipe
-- CRITICAL: Always validate the COPY works manually first
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
ON_ERROR = CONTINUE
VALIDATION_MODE = RETURN_ALL_ERRORS;  -- Check for errors without loading

-- Step 6: Create pipe with auto-ingest
CREATE PIPE PIPE_LOAD_RAW_DATA
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-notifications'
  COMMENT = 'Auto-ingest pipe for raw JSON data from S3'
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

-- Step 7: Get SQS queue ARN for S3 bucket event configuration
SHOW PIPES LIKE 'PIPE_LOAD_RAW_DATA';
DESC PIPE PIPE_LOAD_RAW_DATA;
-- Copy the "notification_channel" value (SQS ARN)
-- Configure S3 bucket to send events to this SQS queue via SNS
```

## AWS Configuration (After Snowflake Setup)

```bash
# Configure S3 bucket event notifications to SNS topic
# This triggers Snowpipe when new files arrive

aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration '{
    "TopicConfigurations": [{
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:snowpipe-notifications",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [{
            "Name": "prefix",
            "Value": "raw-data/"
          }]
        }
      }
    }]
  }'
```

## Monitoring

```sql
-- Monitor pipe load history (last hour)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'PIPE_LOAD_RAW_DATA'
))
ORDER BY START_TIME DESC;

-- Check for load errors
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'RAW_DATA',
  START_TIME => DATEADD(hour, -24, CURRENT_TIMESTAMP())
))
WHERE STATUS = 'LOAD_FAILED'
ORDER BY LAST_LOAD_TIME DESC;

-- Verify data is loading
SELECT 
  DATE_TRUNC('hour', loaded_at) AS load_hour,
  COUNT(*) AS records_loaded
FROM RAW_DATA
WHERE loaded_at > DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY 1
ORDER BY 1 DESC;
```

## Validation

```sql
-- Verify pipe exists and is running
SHOW PIPES LIKE 'PIPE_LOAD_RAW_DATA';
-- Expected: PIPE_LOAD_RAW_DATA with AUTO_INGEST = TRUE

-- Verify pipe status
SELECT SYSTEM$PIPE_STATUS('PIPE_LOAD_RAW_DATA');
-- Expected: {"executionState":"RUNNING",...}

-- Verify data loaded successfully
SELECT COUNT(*) FROM RAW_DATA;
-- Expected: Non-zero count after files processed

-- Check for any pending files
SELECT SYSTEM$PIPE_STATUS('PIPE_LOAD_RAW_DATA');
-- Check "pendingFileCount" - should be 0 or low
```

**Expected Results:**
- Storage integration shows valid IAM user ARN
- Stage lists files from S3 bucket
- Pipe shows AUTO_INGEST = TRUE and RUNNING status
- Data appears in RAW_DATA table within 1-2 minutes of file arrival
- Monitoring queries show successful loads
