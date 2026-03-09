# Snowflake Snowpipe Streaming

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-streaming
**Keywords:** snowpipe streaming, high-performance streaming, classic streaming, row-level ingestion, low-latency ingestion, sub-second latency, real-time ingestion, streaming architecture, streaming channels
**TokenBudget:** ~3700
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 108-snowflake-data-loading.md
**Companions:** 121d-snowflake-snowpipe-streaming-sdk.md

## Scope

**What This Rule Covers:**
Architecture selection and core concepts for Snowpipe Streaming: high-performance vs classic architecture, decision matrix for file-based vs streaming ingestion, and anti-patterns. This is a **separate, complementary approach** to file-based Snowpipe (121), not an extension of it.

**When to Load This Rule:**
- Choosing between high-performance and classic streaming architectures
- Deciding between file-based Snowpipe and Snowpipe Streaming
- Understanding streaming concepts (channels, offsets, exactly-once semantics)
- For SDK implementation (Java/Python), channel management, and schema evolution, see **121d-snowflake-snowpipe-streaming-sdk.md**

**For file-based continuous ingestion (1-2 min latency), see `121-snowflake-snowpipe.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **108-snowflake-data-loading.md** - Data loading fundamentals (stages, COPY INTO basics)

**Related:**
- **121-snowflake-snowpipe.md** - File-based Snowpipe for comparison (when to use files vs streaming)
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring, cost tracking, and performance analysis
- **121c-snowflake-snowpipe-troubleshooting.md** - Troubleshooting and debugging patterns
- **104-snowflake-streams-tasks.md** - Incremental pipelines and change data capture
- **111-snowflake-observability-core.md** - Logging, tracing, and monitoring patterns
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization

### External Documentation

- [Snowpipe Streaming Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview) - Introduction to Snowpipe Streaming SDK
- [High-Performance Streaming Architecture](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview) - Optimized streaming for high-volume workloads
- [Classic Streaming Architecture](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-classic-overview) - Standard Snowpipe Streaming architecture
- [Streaming Architecture Comparison](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-comparison) - High-performance vs classic comparison
- [Snowpipe Streaming Java SDK](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-java) - Java SDK reference and examples
- [Snowpipe Streaming Python SDK](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-python) - Python SDK reference and examples

## Contract

### Inputs and Prerequisites

- Snowflake account with appropriate privileges (INSERT, CREATE TABLE)
- Target tables with appropriate schema
- Snowpipe Streaming SDK setup (Java, Python, or .NET)
- Private key authentication configured
- Understanding of streaming source architecture (Kafka, Kinesis, custom)
- Latency requirements defined (<1 sec for streaming)

### Mandatory

- Snowpipe Streaming SDK (Java, Python, .NET)
- Private key authentication (RSA key pair)
- Channel management implementation
- Offset token tracking for exactly-once semantics
- Error handling and retry logic
- Monitoring queries for channel status and load history

### Forbidden

- Using Snowpipe Streaming for batch file loads (use file-based Snowpipe instead)
- Skipping offset token tracking (causes duplicate data)
- Ignoring schema evolution settings (causes silent data loss)
- Omitting error handling (causes data gaps)
- Using streaming for historical bulk loads (use COPY INTO)

### Execution Steps

1. Determine architecture: high-performance (sub-second, high-volume) or classic (standard streaming)
2. Install and configure Snowpipe Streaming SDK (Java, Python, or .NET)
3. Set up private key authentication and generate JWT tokens
4. Create target tables with appropriate schema
5. Implement channel management with descriptive channel names
6. Implement offset token tracking for exactly-once semantics
7. Configure schema evolution mode (ADD_COLUMNS, FAIL_MISSING_COLUMNS, IGNORE_MISSING_COLUMNS)
8. Implement error handling and retry logic
9. Set up monitoring queries for channel status and load history
10. Test latency and throughput under expected load

### Output Format

Snowpipe Streaming implementations produce:
- SDK client initialization code (Java, Python, .NET)
- Channel management patterns with offset tracking
- Row insertion logic with error handling
- Monitoring queries for channel status and load history
- Schema evolution configuration
- Cost tracking patterns and optimization strategies

### Validation

**Pre-Task-Completion Checks:**
- SDK installed and configured correctly
- Private key authentication working
- Target tables exist with appropriate schema
- Channel management implemented with offset tracking
- Error handling and retry logic in place
- Monitoring queries configured and tested

**Success Criteria:**
- Rows loading successfully via SDK
- Latency within requirements: <1 sec for high-performance, 1-2 sec for classic
- Channel status accessible via monitoring queries
- Offset tracking preventing duplicate data
- Schema evolution working as configured
- Error rate acceptable (<1% of rows)
- Cost per GB within expected range

**Negative Tests:**
- SDK should fail with invalid authentication
- Duplicate offset tokens should be rejected
- Schema mismatches should be caught based on evolution mode
- Channel reopens should resume from last offset
- Connection failures should trigger retry logic

### Design Principles

- **Architecture Selection:** Use high-performance for sub-second latency and high-volume; use classic for standard streaming workloads
- **Row-Level Ingestion:** Write rows directly to Snowflake without file staging
- **Channel-Based Tracking:** Use channels for offset tracking and exactly-once semantics
- **Offset Tokens:** Implement unique, monotonically increasing offset tokens for idempotency
- **Schema Evolution:** Configure automatic schema detection and evolution for flexible data models
- **Error Handling:** Implement robust error handling and retry logic for production reliability
- **Monitoring:** Track channel status, load history, and latency metrics continuously

> **Investigation Required**
> When working with Snowpipe Streaming:
> 1. **Read existing streaming implementations BEFORE creating new ones** - Check patterns, channel naming, offset strategies
> 2. **Verify authentication setup** - Check private key configuration, JWT generation
> 3. **Never assume schema** - Verify target table structure and column types
> 4. **Test latency requirements** - Measure actual latency under expected load
> 5. **Monitor first loads** - Verify offset tracking and error rates after implementation
>
> **Anti-Pattern:**
> "Creating Snowpipe Streaming client... (without testing authentication first)"
> "Using streaming for bulk load... (wrong tool for the job)"
>
> **Correct Pattern:**
> "Let me check your existing streaming setup first."
> [reads existing channels, checks authentication, tests connection]
> "I see you use high-performance architecture with Kafka offset tracking. Creating new channel following this pattern..."

### Post-Execution Checklist

- [ ] Architecture selected (high-performance or classic)
- [ ] SDK installed and configured (Java, Python, or .NET)
- [ ] Private key authentication working
- [ ] Target tables exist with appropriate schema
- [ ] Channel management implemented with descriptive names
- [ ] Offset token tracking implemented for exactly-once semantics
- [ ] Schema evolution mode configured appropriately
- [ ] Error handling and retry logic in place
- [ ] Monitoring queries configured and tested
- [ ] Channel status accessible and reviewed
- [ ] Load history accessible and reviewed
- [ ] Latency measured and within requirements
- [ ] Cost tracking implemented and baseline established
- [ ] Documentation updated with channel details and architecture

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Implementing Offset Token Tracking**
```python
# Bad: No offset tracking, causes duplicate data
# (client/channel setup - see "Python SDK Example" section below for full init pattern)
client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Insert rows without offset tokens
for row in data_stream:
    channel.insert_row(row)  # No offset token!
    # If application crashes and restarts, rows are duplicated!

channel.close()
```
**Problem:** Duplicate data on restarts; no exactly-once semantics

**Correct Pattern:**
```python
# Good: Offset token tracking for exactly-once semantics
# (client/channel setup - see "Python SDK Example" section below for full init pattern)
client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Track last committed offset (persist to disk/database)
last_offset = load_last_offset_from_storage()

# Insert rows with monotonically increasing offset tokens
for idx, row in enumerate(data_stream, start=last_offset + 1):
    response = channel.insert_row(row, offset_token=f'offset_{idx}')
    
    if response.has_errors():
        print(f"Insert errors: {response.insert_errors}")
    else:
        save_offset_to_storage(idx)

channel.close()
# On restart, resume from last_offset + 1, no duplicates!
```
**Benefits:** Exactly-once semantics; no duplicates on restart; safe recovery

**Anti-Pattern 2: Using Streaming for Bulk Historical Loads**
```python
# Bad: Using Snowpipe Streaming for bulk historical load
client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Load 10 million historical rows row-by-row
for row in historical_data_10M_rows:
    channel.insert_row(row, offset_token=f'offset_{row["id"]}')
    # Extremely slow! High latency! Expensive! Wrong tool!

channel.close()
# Takes hours, costs 10x more than COPY INTO!
```
**Problem:** Extremely slow for bulk loads; costs 10x more than COPY INTO

**Correct Pattern:**
```python
# Good: Use COPY INTO for bulk historical loads
# Step 1: Stage files (use file-based Snowpipe or COPY INTO)
# See 121-snowflake-snowpipe.md for file-based ingestion

# Step 2: Use Snowpipe Streaming only for ongoing real-time data
client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Stream only new real-time data
for row in real_time_stream:  # Ongoing stream, not bulk load
    response = channel.insert_row(row, offset_token=f'offset_{row["timestamp"]}')
    if response.has_errors():
        handle_error(response.insert_errors)

channel.close()
```
**Benefits:** Right tool for the job; fast bulk load via COPY INTO; streaming for real-time only

**Anti-Pattern 3: Ignoring Schema Evolution Settings**
```python
# Bad: No schema evolution configuration, silent data loss
client = SnowflakeStreamingIngestClient(...)

# Open channel without specifying schema evolution mode
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='TABLE',
    channel_name='CHANNEL'
    # No on_error or schema evolution config!
)

# Insert row with new column not in table
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}  # 'email' column doesn't exist!
channel.insert_row(row, 'offset_1')
# What happens? Depends on default! Data loss? Error? Unknown!
```
**Problem:** Silent data loss; unpredictable behavior with unknown columns

**Correct Pattern:**
```python
# Good: Explicit schema evolution configuration
from snowflake.ingest.utils.constants import OnErrorOption

client = SnowflakeStreamingIngestClient(...)

# Open channel with explicit error handling mode
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='TABLE',
    channel_name='CHANNEL',
    on_error=OnErrorOption.CONTINUE  # Or ABORT, SKIP_FILE
)

# Note: on_error controls error behavior, NOT schema evolution.
# Schema evolution (ADD_COLUMNS, FAIL_MISSING_COLUMNS, IGNORE_MISSING_COLUMNS)
# is configured at the table level. See "Schema Evolution" section below.

# Insert row with validation
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
response = channel.insert_row(row, 'offset_1')

if response.has_errors():
    for error in response.insert_errors:
        print(f"Schema error: {error}")
```
**Benefits:** Predictable behavior; explicit error control; no silent data loss

## Snowpipe Streaming Overview

### What is Snowpipe Streaming?

**Snowpipe Streaming** provides a direct, low-latency alternative to file-based Snowpipe by using the Snowpipe Streaming SDK to write rows directly to Snowflake tables.

**Key Characteristics:**
- **Row-level ingestion:** No file staging required
- **Sub-second latency:** Typically <1 second for data availability
- **SDK-based:** Java, Python, .NET SDKs available
- **Channel-based:** Uses channels for offset tracking and exactly-once semantics
- **Schema evolution:** Automatic schema detection and evolution supported

### File-Based Snowpipe vs Snowpipe Streaming

**File-Based Snowpipe (see 121-snowflake-snowpipe.md):**
- Use Case: Micro-batch file ingestion from cloud storage
- Latency: 1-2 minutes (typical)
- Data Format: Files (CSV, JSON, Parquet, Avro, ORC)
- Triggering: Event-driven (SNS, Event Grid, Pub/Sub) or REST API
- Setup: Stage configuration, cloud event notifications
- Best For: File-based sources, event-driven architectures, 1-2 min latency acceptable

**Snowpipe Streaming:**
- Use Case: Low-latency, row-level ingestion from streaming sources
- Latency: <1 second (high-performance), 1-2 seconds (classic)
- Data Format: Rows (direct SDK writes)
- Triggering: Application-driven (SDK calls)
- Setup: SDK integration, channel management, offset tracking
- Best For: Kafka, Kinesis, custom apps, sub-second latency required

**Decision Matrix:**

**Use File-Based Snowpipe when:**
- Data is already in files (S3, GCS, Azure Blob)
- 1-2 minute latency is acceptable
- Simpler setup preferred
- File-based event notifications available
- Batch processing patterns

**Use Snowpipe Streaming when:**
- Sub-second latency is required
- Data arrives row-by-row or in small micro-batches
- Direct integration from streaming sources (Kafka, Kinesis, custom apps)
- Need exactly-once semantics with offset tracking
- Schema evolution is important

## High-Performance vs Classic Architecture

### Architecture Comparison

**High-Performance Architecture:**
- **Latency:** Sub-second (optimized)
- **Throughput:** Higher (optimized for large volumes)
- **Overhead:** Lower (direct write path)
- **Complexity:** Slightly more complex setup
- **Use Case:** High-volume, low-latency streaming
- **Availability:** AWS, Azure, GCP
- **Cost:** Lower per-row overhead

**Classic Architecture:**
- **Latency:** 1-2 seconds
- **Throughput:** Moderate
- **Overhead:** Higher (metadata operations)
- **Complexity:** Simpler setup
- **Use Case:** Standard streaming workloads
- **Availability:** AWS, Azure, GCP
- **Cost:** Higher per-row overhead

**Rule:** Prefer **High-Performance Architecture** for production workloads with strict latency and throughput requirements.

**Snowflake Documentation References:**
- [High-Performance Architecture Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview)
- [Classic Architecture Overview](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-classic-overview)
- [Architecture Comparison](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-comparison)

### When to Use Each Architecture

**High-Performance Architecture:**
- Throughput requirements: >10,000 rows/sec
- Latency requirements: <500ms
- Large-scale streaming applications
- Production workloads with strict SLAs
- Cost-sensitive high-volume ingestion

**Classic Architecture:**
- Throughput requirements: <10,000 rows/sec
- Latency requirements: 1-2 seconds acceptable
- Standard streaming workloads
- Development and testing environments
- Simpler operational requirements

## SDK Implementation, Channel Management, and Schema Evolution

> **See companion rule for all SDK implementation details:**
> - **121d-snowflake-snowpipe-streaming-sdk.md** — Java SDK setup and ingestion, Python SDK setup and ingestion, production-ready error handling class, channel lifecycle management, channel naming best practices, offset token patterns, schema evolution modes and configuration, monitoring and troubleshooting quick references
