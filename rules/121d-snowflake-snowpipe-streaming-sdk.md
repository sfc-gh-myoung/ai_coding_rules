# Snowflake Snowpipe Streaming: SDK Implementation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-streaming-sdk
**Keywords:** snowpipe streaming SDK, Java SDK, Python SDK, streaming client, channel management, offset tracking, schema evolution, streaming ingestion code, SnowflakeStreamingIngestClient
**TokenBudget:** ~3850
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 121a-snowflake-snowpipe-streaming.md

## Scope

**What This Rule Covers:**
SDK implementation patterns for Snowpipe Streaming: Java SDK setup and ingestion, Python SDK setup and ingestion, production-ready error handling, channel lifecycle management, offset token best practices, and schema evolution configuration.

**When to Load This Rule:**
- Writing Snowpipe Streaming ingestion code (Java or Python)
- Implementing channel management and offset tracking
- Configuring schema evolution for streaming tables
- Building production-ready streaming producers with error handling

**For architecture selection, overview, and anti-patterns, see `121a-snowflake-snowpipe-streaming.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **121a-snowflake-snowpipe-streaming.md** - Streaming architecture, overview, and anti-patterns

**Related:**
- **121-snowflake-snowpipe.md** - File-based Snowpipe for comparison
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring and cost tracking
- **121c-snowflake-snowpipe-troubleshooting.md** - Troubleshooting and debugging

### External Documentation

- [Snowpipe Streaming Java SDK](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-java) - Java SDK reference and examples
- [Snowpipe Streaming Python SDK](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-python) - Python SDK reference and examples

## Contract

### Inputs and Prerequisites

Snowpipe Streaming architecture selected (high-performance or classic), target tables created, private key authentication configured

### Mandatory

SDK client initialization, channel management, offset token tracking, error handling

### Forbidden

Using streaming for bulk historical loads (use COPY INTO), skipping offset tracking, ignoring schema evolution settings

### Execution Steps

1. Install SDK (Java Maven dependency or Python pip install)
2. Configure private key authentication
3. Initialize streaming client
4. Open channel with descriptive name and error handling mode
5. Insert rows with monotonically increasing offset tokens
6. Implement error handling and retry logic
7. Configure schema evolution mode at table level
8. Close channel and client gracefully

### Output Format

SDK client initialization code, channel management patterns, row insertion logic with offset tracking, schema evolution configuration

### Validation

**Pre-Task-Completion Checks:**
- SDK installed and importable
- Private key authentication tested
- Channel opens successfully
- Offset tracking implemented
- Error handling covers insert failures

**Success Criteria:**
- Rows loading via SDK with offset tracking
- Channel status accessible via monitoring queries
- Schema evolution working as configured
- Error rate acceptable (<1% of rows)

**Negative Tests:**
- Invalid authentication rejected
- Duplicate offset tokens handled correctly
- Schema mismatches caught based on evolution mode
- Channel reopens resume from last offset

### Design Principles

- Use descriptive channel names that identify data source and partition
- Implement monotonically increasing offset tokens for exactly-once semantics
- Configure explicit schema evolution mode (never rely on defaults in production)
- Build production-ready error handling with retry logic and dead-letter queues

### Post-Execution Checklist

- [ ] SDK installed and configured (Java or Python)
- [ ] Private key authentication working
- [ ] Channel management implemented with descriptive names
- [ ] Offset token tracking implemented
- [ ] Error handling and retry logic in place
- [ ] Schema evolution mode configured explicitly
- [ ] Channel close/reopen tested for recovery

## Java SDK Implementation

### Setup

```xml
<!-- Maven dependency -->
<dependency>
    <groupId>net.snowflake</groupId>
    <artifactId>snowflake-ingest-sdk</artifactId>
    <version>2.0.0</version>
</dependency>
```

### Basic Ingestion

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

## Python SDK Implementation

### Setup

```bash
pip install snowflake-ingest
```

### Basic Ingestion

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
# (See "Python SDK Implementation" section for full client init pattern)
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

**Important:** Schema evolution modes and `on_error` are separate concerns:
- **Schema evolution modes** (ADD_COLUMNS, FAIL_MISSING_COLUMNS, IGNORE_MISSING_COLUMNS) control how the table handles unknown columns. Configured via table properties or channel open parameters.
- **on_error** (ABORT, CONTINUE, SKIP_FILE) controls what happens when any insert error occurs (type mismatches, constraint violations, etc.).

```python
client = SnowflakeStreamingIngestClient(...)

# Production: Strict error handling + strict schema
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='CRITICAL_TABLE',
    channel_name='CHANNEL',
    on_error='ABORT'  # Fail on any insert error
    # Schema evolution mode: set FAIL_MISSING_COLUMNS at table level
)

# Development: Lenient error handling + flexible schema
channel = client.open_channel(
    database='DB',
    schema='SCHEMA',
    table='EXPLORATORY_TABLE',
    channel_name='CHANNEL',
    on_error='CONTINUE'  # Skip bad rows, continue ingestion
    # Schema evolution mode: set ADD_COLUMNS at table level
)
```

**Rule:** Use schema evolution cautiously in production. Prefer explicit schema management for critical tables.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Creating a New Channel Per Batch**

**Problem:** Opening a new channel for every batch of rows (e.g., inside a loop or per API request) causes excessive metadata overhead, prevents offset continuity, and can hit channel limits. Each channel open is a control-plane operation that adds latency and creates orphaned channels that consume resources.

**Correct Pattern:** Open a channel once during application startup, reuse it across batches, and close it only during graceful shutdown. Use a single long-lived channel per logical data source partition.

```python
# Wrong: new channel per batch
for batch in data_stream:
    channel = client.open_channel(...)  # Expensive!
    for row in batch:
        channel.insert_row(row, offset_token=...)
    channel.close()

# Correct: reuse channel across batches
channel = client.open_channel(...)
for batch in data_stream:
    for row in batch:
        channel.insert_row(row, offset_token=...)
channel.close()
```

**Anti-Pattern 2: Using Random UUIDs as Offset Tokens**

**Problem:** Random UUIDs are not monotonically increasing, which breaks exactly-once semantics. When a channel is reopened after a crash, the SDK cannot determine the last committed position because UUIDs have no ordering. This leads to duplicate or missing data on recovery.

**Correct Pattern:** Use monotonically increasing offset tokens derived from source system positions (Kafka offsets, database sequence IDs, or sequential counters). Persist the last committed offset to durable storage so recovery can resume from the correct position.

```python
# Wrong: random UUIDs
offset_token = str(uuid.uuid4())

# Correct: monotonic counter persisted to storage
offset_counter += 1
offset_token = f"offset_{offset_counter}"
channel.insert_row(row, offset_token=offset_token)
save_offset_to_storage(offset_counter)
```

**Anti-Pattern 3: Using ADD_COLUMNS Schema Evolution in Production**

**Problem:** Leaving schema evolution set to `ADD_COLUMNS` on production tables allows any upstream data change to silently alter your table schema. A typo in a field name (e.g., `emial` instead of `email`) creates a new column rather than failing, leading to data silently landing in the wrong column and NULL values in the intended column.

**Correct Pattern:** Use `FAIL_MISSING_COLUMNS` for production tables to enforce strict schema contracts. Manage schema changes through explicit DDL migrations. Reserve `ADD_COLUMNS` for development or exploratory environments only.

```sql
-- Production: strict schema enforcement
ALTER TABLE PROD_DB.CORE.ORDERS SET
  ENABLE_SCHEMA_EVOLUTION = FALSE;

-- Development: flexible schema discovery
ALTER TABLE DEV_DB.SANDBOX.EVENTS SET
  ENABLE_SCHEMA_EVOLUTION = TRUE;
```

## Monitoring and Troubleshooting Quick Reference

**For comprehensive monitoring, cost tracking, and performance analysis, see `121b-snowflake-snowpipe-monitoring.md`**
**For comprehensive troubleshooting and debugging patterns, see `121c-snowflake-snowpipe-troubleshooting.md`**

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

-- Check table schema
DESC TABLE DB.SCHEMA.TABLE;

-- Check user privileges
SHOW GRANTS TO USER USERNAME;
```
