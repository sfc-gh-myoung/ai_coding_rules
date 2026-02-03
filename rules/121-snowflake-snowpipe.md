# Snowflake Snowpipe (File-Based Ingestion)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:snowpipe, kw:streaming
**Keywords:** snowpipe, auto-ingest, REST API, file-based ingestion, event notifications, COPY INTO, pipe management, serverless ingestion
**TokenBudget:** ~2600
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 108-snowflake-data-loading.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for continuous file-based data ingestion using Snowflake Snowpipe. Covers auto-ingest vs REST API, file sizing optimization, cloud event configuration, security, monitoring, and troubleshooting.

**When to Load This Rule:**
- Setting up continuous file-based data ingestion
- Configuring auto-ingest with cloud event notifications (SNS, Event Grid, Pub/Sub)
- Implementing REST API-based pipe triggering
- Troubleshooting Snowpipe load failures or high costs

**For SDK-based streaming (sub-second latency), see `121a-snowflake-snowpipe-streaming.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **108-snowflake-data-loading.md** - Stages and bulk loading

**Related:**
- **121a-snowflake-snowpipe-streaming.md** - SDK-based streaming ingestion
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring and cost tracking
- **104-snowflake-streams-tasks.md** - Incremental pipelines and CDC

### Related Examples

- **examples/121-snowpipe-auto-ingest-example.md** - Complete AWS S3 auto-ingest setup with SNS

### External Documentation

- [Snowpipe Introduction](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro)
- [Snowpipe Auto-Ingest](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto)
- [Snowpipe REST API](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-overview)

## Contract

### Inputs and Prerequisites

- Snowflake account with pipe creation privileges (`CREATE PIPE`)
- Configured stages (internal or external)
- Target tables with appropriate schema
- Cloud event notifications configured (for auto-ingest)

### Mandatory

- Snowflake DDL for CREATE PIPE statements
- Cloud storage event configuration (for auto-ingest)
- Explicit FILE_FORMAT specifications
- Monitoring queries for load history and error tracking

### Forbidden

- Using Snowpipe for bulk historical loads (use COPY INTO instead)
- Mixing bulk COPY and Snowpipe on same files (causes duplicates)
- Undersized files (<1MB) for file-based Snowpipe (poor cost efficiency)
- Omitting FILE_FORMAT specifications
- Generic PATTERN matching (.*) without proper file filtering

### Execution Steps

1. Determine ingestion pattern: auto-ingest or REST API
2. Configure cloud storage and create stages
3. Optimize file sizing: 100-250MB compressed
4. Create and test file format specifications
5. Validate COPY statement manually before creating pipe
6. Create pipe with validated COPY statement
7. Configure cloud event notifications (auto-ingest) or REST API auth
8. Set up monitoring queries and error notifications

### Output Format

- Complete pipe DDL with comments
- Cloud event configuration
- Monitoring queries for load history and errors

### Validation

**Success Criteria:**
- Pipe shows in SHOW PIPES
- Files loading automatically (auto-ingest) or via REST API
- Load history accessible via INFORMATION_SCHEMA.PIPE_USAGE_HISTORY
- Latency within requirements (<2 min for file-based)
- No duplicate data; error rate <5%

### Design Principles

- **Auto-Ingest First:** Prefer auto-ingest for simplicity and automation
- **File Sizing:** 100-250MB compressed, stage once per minute
- **Serverless Compute:** Snowpipe uses Snowflake-managed compute
- **Idempotency:** Snowpipe tracks loaded files to prevent duplicates
- **Latency:** Expect 1-2 minutes for properly sized files

### Post-Execution Checklist

- [ ] Ingestion method selected (auto-ingest or REST API)
- [ ] File sizes optimized (100-250MB compressed)
- [ ] Cloud event notifications configured (for auto-ingest)
- [ ] File format specifications explicit and tested
- [ ] COPY statement validated before pipe creation
- [ ] ON_ERROR setting appropriate (CONTINUE/SKIP_FILE/ABORT)
- [ ] Monitoring queries configured
- [ ] Error notifications enabled

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Not Using AUTO_INGEST

```sql
-- BAD: Manual REST API calls for continuous loading
CREATE PIPE manual_pipe AS COPY INTO target FROM @stage;
-- Requires constant API calls, manual tracking!
```

**Problem:** High operational overhead, manual file tracking, error-prone.

**Correct Pattern:**
```sql
CREATE PIPE auto_pipe AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123:my-topic'
AS COPY INTO target FROM @stage FILE_FORMAT = (TYPE = CSV) ON_ERROR = CONTINUE;
```

### Anti-Pattern 2: Missing FILE_FORMAT

```sql
-- BAD: No file format, relies on defaults
CREATE PIPE vague_pipe AUTO_INGEST = TRUE AS COPY INTO target FROM @stage;
```

**Problem:** Data parsing errors, incorrect types, debugging nightmares.

**Correct Pattern:**
```sql
CREATE FILE FORMAT csv_format TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1
  NULL_IF = ('NULL', '') DATE_FORMAT = 'YYYY-MM-DD' COMPRESSION = GZIP;

CREATE PIPE explicit_pipe AUTO_INGEST = TRUE
AS COPY INTO target FROM @stage FILE_FORMAT = (FORMAT_NAME = csv_format);
```

### Anti-Pattern 3: Not Monitoring COPY_HISTORY

```sql
-- BAD: Create pipe and never check for errors
CREATE PIPE silent_pipe AUTO_INGEST = TRUE ON_ERROR = CONTINUE AS ...;
-- Files fail silently!
```

**Problem:** Silent data loss, undetected failures.

**Correct Pattern:**
```sql
SELECT pipe_name, file_name, status, first_error_message, error_count
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET', START_TIME => DATEADD(HOUR, -1, CURRENT_TIMESTAMP())
)) WHERE status = 'LOAD_FAILED' OR error_count > 0;
```

### Anti-Pattern 4: Greedy File Pattern

```sql
-- BAD: Matches everything including test files
CREATE PIPE greedy_pipe AS COPY INTO target FROM @stage PATTERN = '.*';
```

**Problem:** Loads test data, backups, old files, wasted credits.

**Correct Pattern:**
```sql
CREATE PIPE specific_pipe AS COPY INTO target FROM @stage
  PATTERN = 'production/sales/.*sales_data_[0-9]{8}\\.csv\\.gz';
```

## Snowpipe Overview

**Key Characteristics:**
- **Serverless:** Uses Snowflake-managed compute
- **File-based:** Works with staged files
- **Near real-time:** 1-2 minute latency for properly sized files
- **Event-driven:** Auto-ingest uses cloud storage events
- **Idempotent:** Tracks loaded files to prevent duplicates

**Snowpipe vs Bulk Loading:**
- **Bulk COPY:** Large historical loads, scheduled batches, user warehouse, 64-day history
- **Snowpipe:** Continuous micro-batches, serverless compute, event-driven, 14-day history

**Rule:** Do NOT use Snowpipe for one-time bulk historical loads.

## Ingestion Methods

**Auto-Ingest (Recommended):**
- Files staged, then cloud event notification, then Snowpipe loads automatically
- Fully automated, no application code needed
- Requires external stage + event notifications

**REST API:**
- Application stages files, then calls REST endpoint, then Snowpipe loads
- Programmatic control, works with internal stages
- Requires JWT authentication

## File Sizing Best Practices

**Target:** 100-250MB compressed
**Frequency:** Stage files once per minute

**Why:**
- Too small (<10MB): High overhead, poor cost efficiency
- Optimal (100-250MB): Best balance of throughput/latency/cost
- Too large (>1GB): Increased latency, timeout issues

## Pipe DDL Examples

**Auto-Ingest (AWS S3):**
```sql
CREATE PIPE PIPE_LOAD_EVENTS AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123:snowpipe-events'
AS COPY INTO EVENTS (id, type, ts, payload)
FROM (SELECT $1:id::STRING, $1:type::STRING, $1:ts::TIMESTAMP_NTZ, $1
      FROM @STG_S3_EVENTS)
FILE_FORMAT = FF_JSON_GZIP ON_ERROR = CONTINUE;

-- Get SQS queue ARN for S3 event notifications
DESC PIPE PIPE_LOAD_EVENTS;
```

**Azure Event Grid:**
```sql
CREATE NOTIFICATION INTEGRATION NINT_AZURE TYPE = QUEUE
  NOTIFICATION_PROVIDER = AZURE_STORAGE_QUEUE
  AZURE_STORAGE_QUEUE_PRIMARY_URI = '<queue_uri>' AZURE_TENANT_ID = '<tenant>';

CREATE PIPE PIPE_AZURE AUTO_INGEST = TRUE INTEGRATION = 'NINT_AZURE'
AS COPY INTO target FROM @STG_AZURE FILE_FORMAT = FF_JSON_GZIP;
```

**GCS Pub/Sub:**
```sql
CREATE NOTIFICATION INTEGRATION NINT_GCS TYPE = QUEUE
  NOTIFICATION_PROVIDER = GCP_PUBSUB GCP_PUBSUB_SUBSCRIPTION_NAME = '<sub>';

CREATE PIPE PIPE_GCS AUTO_INGEST = TRUE INTEGRATION = 'NINT_GCS'
AS COPY INTO target FROM @STG_GCS FILE_FORMAT = FF_JSON_GZIP;
```

## REST API Usage

**Key Pair Authentication:**
```bash
openssl genrsa -out snowpipe_key.pem 2048
openssl rsa -in snowpipe_key.pem -pubout -out snowpipe_key.pub
```

```sql
ALTER USER snowpipe_user SET RSA_PUBLIC_KEY='<public_key>';
```

**Insert Files Endpoint:**
```http
POST /v1/data/pipes/<pipe>/insertFiles
Authorization: Bearer <JWT>
{"files": [{"path": "file1.json.gz"}, {"path": "file2.json.gz"}]}
```

## Security and Privileges

```sql
-- Create pipes
GRANT USAGE ON DATABASE, SCHEMA TO ROLE pipe_admin;
GRANT CREATE PIPE ON SCHEMA TO ROLE pipe_admin;
GRANT USAGE ON STAGE TO ROLE pipe_admin;
GRANT SELECT, INSERT ON TABLE TO ROLE pipe_admin;

-- Operate pipes (pause/resume)
GRANT OPERATE ON PIPE TO ROLE pipe_operator;
```

**Pipe Management:**
```sql
ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = TRUE;   -- Pause
ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = FALSE;  -- Resume
ALTER PIPE my_pipe REFRESH;                            -- Force load
ALTER PIPE my_pipe REFRESH PREFIX = 'events/2025/01/'; -- Refresh prefix
```

## Monitoring Quick Reference

```sql
-- Pipe status
SHOW PIPES LIKE 'PIPE_NAME';

-- Recent loads
SELECT * FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  DATE_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP()),
  PIPE_NAME => 'DB.SCHEMA.PIPE_NAME'
)) ORDER BY START_TIME DESC;

-- Errors
SELECT * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'TARGET', START_TIME => DATEADD(DAY, -1, CURRENT_TIMESTAMP())
)) WHERE status = 'LOAD_FAILED' OR error_count > 0;

-- Stage contents
LIST @STAGE_NAME;
```

For comprehensive monitoring and troubleshooting, see `121b-snowflake-snowpipe-monitoring.md` and `121c-snowflake-snowpipe-troubleshooting.md`.
