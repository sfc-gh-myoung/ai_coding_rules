# Snowflake Snowpipe Streaming

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** snowpipe streaming, streaming SDK, high-performance streaming, classic streaming, channel management, row-level ingestion, low-latency ingestion, offset tracking, schema evolution, streaming API, Java SDK, Python SDK, .NET SDK, sub-second latency, real-time ingestion, streaming channels
**TokenBudget:** ~6000
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 108-snowflake-data-loading.md

## Scope

**What This Rule Covers:**
SDK-based continuous data ingestion using Snowpipe Streaming for low-latency, row-level writes directly to Snowflake tables. Covers architecture selection (high-performance vs classic), SDK usage (Java, Python, .NET), channel management, offset tracking, schema evolution, monitoring, and troubleshooting for sub-second latency requirements. This is a **separate, complementary approach** to file-based Snowpipe (121), not an extension of it.

**When to Load This Rule:**
- Implementing low-latency streaming ingestion with Snowpipe Streaming SDK (<1 sec latency)
- Integrating direct row-level writes from streaming sources (Kafka, Kinesis, custom apps)
- Configuring channel-based offset tracking for exactly-once semantics
- Implementing schema evolution for streaming data
- Troubleshooting Snowpipe Streaming SDK issues or performance
- Choosing between high-performance and classic streaming architectures

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
from snowflake.ingest import SnowflakeStreamingIngestClient

client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Insert rows without offset tokens
for row in data_stream:
    channel.insert_row(row)  # No offset token!
    # If application crashes and restarts, rows are duplicated!

channel.close()
```
**Problem:** Duplicate data on restarts; no exactly-once semantics; data quality issues; difficult troubleshooting; unprofessional

**Correct Pattern:**
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
**Benefits:** Exactly-once semantics; no duplicates; safe restarts; data quality; professional; audit trail; idempotent

**Anti-Pattern 2: Using Streaming for Bulk Historical Loads**
```python
# Bad: Using Snowpipe Streaming for bulk historical load
from snowflake.ingest import SnowflakeStreamingIngestClient

client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Load 10 million historical rows row-by-row
for row in historical_data_10M_rows:
    channel.insert_row(row, offset_token=f'offset_{row["id"]}')
    # Extremely slow! High latency! Expensive! Wrong tool!

channel.close()
# Takes hours, costs 10x more than COPY INTO!
```
**Problem:** Extremely slow; high costs; high latency; inefficient; wrong tool; unprofessional; wasted resources

**Correct Pattern:**
```python
# Good: Use COPY INTO for bulk historical loads
# Step 1: Stage files (use file-based Snowpipe or COPY INTO)
# See 121-snowflake-snowpipe.md for file-based ingestion

# Step 2: Use Snowpipe Streaming only for ongoing real-time data
from snowflake.ingest import SnowflakeStreamingIngestClient

client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

# Stream only new real-time data
for row in real_time_stream:  # Ongoing stream, not bulk load
    response = channel.insert_row(row, offset_token=f'offset_{row["timestamp"]}')
    if response.has_errors():
        handle_error(response.insert_errors)

channel.close()
# Fast, cost-effective, right tool for the job!
```
**Benefits:** Fast bulk load; cost-effective; right tool selection; professional; efficient; scalable

**Anti-Pattern 3: Ignoring Schema Evolution Settings**
```python
# Bad: No schema evolution configuration, silent data loss
from snowflake.ingest import SnowflakeStreamingIngestClient

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
**Problem:** Silent data loss; unpredictable behavior; schema mismatches; debugging nightmares; data quality issues; unprofessional

**Correct Pattern:**
```python
# Good: Explicit schema evolution configuration
from snowflake.ingest import SnowflakeStreamingIngestClient
from snowflake.ingest.utils.constants import OnErrorOption

client = SnowflakeStreamingIngestClient(...)

# Open channel with explicit schema evolution mode
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='TABLE',
    channel_name='CHANNEL',
    on_error=OnErrorOption.CONTINUE  # Or ABORT, SKIP_FILE
)

# For production: Use explicit schema management
# Option 1: Fail on unknown columns (strict)
# Option 2: Add columns automatically (flexible)
# Option 3: Ignore unknown columns (defensive)

# Insert row with validation
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
response = channel.insert_row(row, 'offset_1')

if response.has_errors():
    for error in response.insert_errors:
        print(f"Schema error: {error}")
        # Handle: retry, alert, skip, or fail
```
**Benefits:** Predictable behavior; explicit schema control; no silent data loss; easy debugging; data quality; professional

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

## Snowpipe Streaming SDK Usage

### Java SDK Example

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

        // Insert rows with offset tracking
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

### Python SDK Example

**Setup:**
```bash
pip install snowflake-ingest
```

**Basic Ingestion:**
```python
from snowflake.ingest import SnowflakeStreamingIngestClient
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

# Insert rows with offset tracking
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

### Production-Ready Example with Error Handling

```python
from snowflake.ingest import SnowflakeStreamingIngestClient
from snowflake.ingest.utils.crypto import load_private_key
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowpipeStreamingProducer:
    def __init__(self, account, user, private_key_path, role, database, schema, table):
        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key = load_private_key(f.read(), None)
        
        # Create client
        self.client = SnowflakeStreamingIngestClient(
            account=account,
            user=user,
            private_key=private_key,
            role=role,
        )
        
        # Open channel
        self.channel = self.client.open_channel(
            database=database,
            schema=schema,
            table=table,
            channel_name=f'{table}_channel_{int(time.time())}',
            on_error='CONTINUE'
        )
        
        self.offset = 0
        logger.info(f"Channel opened: {self.channel.name}")
    
    def insert_rows(self, rows):
        """Insert rows with offset tracking and error handling"""
        for row in rows:
            self.offset += 1
            offset_token = f'offset_{self.offset}'
            
            response = self.channel.insert_row(row, offset_token=offset_token)
            
            if response.has_errors():
                logger.error(f"Insert failed at offset {offset_token}: {response.insert_errors}")
                # Implement retry logic or dead-letter queue
            else:
                logger.debug(f"Inserted row at offset {offset_token}")
        
        logger.info(f"Batch inserted: {len(rows)} rows, current offset: {self.offset}")
    
    def close(self):
        """Close channel and client gracefully"""
        logger.info(f"Closing channel at offset {self.offset}")
        self.channel.close()
        self.client.close()
        logger.info("Channel and client closed")

# Usage
producer = SnowpipeStreamingProducer(
    account='ACCOUNT_IDENTIFIER',
    user='USERNAME',
    private_key_path='snowflake_key.pem',
    role='ROLE_NAME',
    database='DB',
    schema='SCHEMA',
    table='TABLE'
)

# Stream data
try:
    for batch in data_stream:
        producer.insert_rows(batch)
except Exception as e:
    logger.error(f"Streaming error: {e}")
finally:
    producer.close()
```

## Channel Management

### Channel Concepts

**Channels** provide:
- **Offset tracking:** Exactly-once semantics with offset tokens
- **Isolation:** Separate channels for different data sources
- **Monitoring:** Per-channel metrics and status
- **Parallelism:** Multiple channels for high-throughput ingestion

### Channel Naming Best Practices

**Pattern:** `{source}_{partition}_{identifier}`

**Examples:**
- `kafka_topic1_partition0`
- `kinesis_stream_shard1`
- `app_events_us_east_1`
- `iot_sensors_device_group_a`

**Guidelines:**
- Use descriptive names that identify the data source
- Include partition or shard information for parallel ingestion
- Use consistent naming conventions across channels
- Avoid generic names like `channel1`, `test_channel`

### Channel Lifecycle

```python
from snowflake.ingest import SnowflakeStreamingIngestClient

client = SnowflakeStreamingIngestClient(...)

# Open channel
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='TABLE',
    channel_name='kafka_orders_partition0',
    on_error='CONTINUE'
)

# Use channel for ingestion
for row in data_stream:
    channel.insert_row(row, offset_token=f'offset_{row["id"]}')

# Close channel gracefully
channel.close()

# Reopen channel (resumes from last offset)
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='TABLE',
    channel_name='kafka_orders_partition0',  # Same name
    on_error='CONTINUE'
)
# Channel resumes from last committed offset automatically
```

### Offset Token Best Practices

**Requirements:**
- Unique within channel
- Monotonically increasing (recommended)
- Persistent across restarts
- Idempotent (same offset = same row)

**Good Offset Patterns:**
```python
# Pattern 1: Sequential integers
offset_token = f'offset_{counter}'

# Pattern 2: Kafka offsets
offset_token = f'kafka_{topic}_{partition}_{offset}'

# Pattern 3: Timestamps + sequence
offset_token = f'{timestamp_ms}_{sequence}'

# Pattern 4: Source system IDs
offset_token = f'event_{event_id}'
```

**Bad Offset Patterns:**
```python
# Bad: Random UUIDs (not monotonic)
offset_token = str(uuid.uuid4())

# Bad: Non-unique timestamps
offset_token = str(int(time.time()))

# Bad: No offset tracking
channel.insert_row(row)  # Missing offset_token!
```

## Schema Evolution

**Snowpipe Streaming supports automatic schema evolution:**

```python
# Initial table schema: id, name
# Insert row with new column
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
channel.insert_row(row, 'offset_1')

# Snowflake automatically adds 'email' column to table (if enabled)
```

### Schema Evolution Modes

**ADD_COLUMNS (Default):**
- Automatically add missing columns to table
- Flexible schema evolution
- Use for: Development, exploratory data, schema discovery

**FAIL_MISSING_COLUMNS:**
- Reject rows with unknown columns
- Strict schema enforcement
- Use for: Production, critical tables, compliance requirements

**IGNORE_MISSING_COLUMNS:**
- Insert only known columns, ignore extras
- Defensive schema handling
- Use for: Partial schema mapping, data filtering

### Schema Evolution Configuration

```python
from snowflake.ingest import SnowflakeStreamingIngestClient
from snowflake.ingest.utils.constants import OnErrorOption

client = SnowflakeStreamingIngestClient(...)

# Strict mode: Fail on unknown columns
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='CRITICAL_TABLE',
    channel_name='CHANNEL',
    on_error=OnErrorOption.ABORT  # Fail on any error
)

# Flexible mode: Add columns automatically
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='EXPLORATORY_TABLE',
    channel_name='CHANNEL',
    on_error=OnErrorOption.CONTINUE  # Continue on errors
)
```

**Rule:** Use schema evolution cautiously in production. Prefer explicit schema management for critical tables.

## Monitoring and Cost Management

**For comprehensive monitoring, cost tracking, and performance analysis, see `121b-snowflake-snowpipe-monitoring.md`**

Key monitoring areas:
- Channel status queries and health checks
- Streaming load history and latency tracking
- Cost monitoring and credit usage analysis
- Performance metrics and throughput tracking
- Alert configuration and dashboard queries

**Quick Reference - Check Channel Status:**
```sql
-- Check channel status
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'DB'
  AND schema_name = 'SCHEMA'
ORDER BY last_commit_time DESC;

-- Check recent loads
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY
WHERE table_name = 'TABLE'
  AND load_type = 'SNOWPIPE_STREAMING'
  AND start_time >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

## Troubleshooting

**For comprehensive troubleshooting and debugging patterns, see `121c-snowflake-snowpipe-troubleshooting.md`**

Common issues covered:
- Connection failures (authentication, JWT, network)
- Schema errors (table doesn't exist, type mismatches)
- Offset tracking issues (duplicates, missing data)
- High latency (batch sizes, architecture, network)
- High error rates (validation, constraints, data quality)
- Authentication and privilege issues

**Quick Reference - Basic Diagnostics:**
```sql
-- Check channel status
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMING_CHANNELS
WHERE database_name = 'DB'
  AND schema_name = 'SCHEMA'
  AND table_name = 'TABLE'
ORDER BY last_commit_time DESC;

-- Check table schema
DESC TABLE DB.SCHEMA.TABLE;

-- Check user privileges
SHOW GRANTS TO USER USERNAME;
```
