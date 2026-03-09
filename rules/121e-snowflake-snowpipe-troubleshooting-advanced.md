# Snowpipe Advanced Troubleshooting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:snowpipe-offset, kw:snowpipe-streaming-debug, kw:snowpipe-checklist
**Keywords:** snowpipe streaming, offset tracking, batch performance, data validation, debugging checklists, channel troubleshooting, exactly-once semantics
**TokenBudget:** ~2700
**ContextTier:** Low
**Depends:** 121c-snowflake-snowpipe-troubleshooting.md, 121a-snowflake-snowpipe-streaming.md

## Scope

**What This Rule Covers:**
Advanced Snowpipe Streaming troubleshooting patterns including offset tracking for exactly-once semantics, batch performance optimization, data validation before insert, and comprehensive debugging checklists for both file-based and streaming Snowpipe.

**When to Load This Rule:**
- Debugging offset tracking or duplicate data in Snowpipe Streaming
- Optimizing streaming batch performance
- Implementing data validation before streaming inserts
- Using debugging checklists for systematic issue resolution

**For common issues and diagnostic decision tree, see `121c-snowflake-snowpipe-troubleshooting.md`**

## References

### Dependencies

**Must Load First:**
- **121c-snowflake-snowpipe-troubleshooting.md** - Core troubleshooting patterns and decision tree
- **121a-snowflake-snowpipe-streaming.md** - Streaming Snowpipe core concepts

**Related:**
- **121b-snowflake-snowpipe-monitoring.md** - Monitoring and alerting
- **121f-snowflake-snowpipe-monitoring-alerts.md** - Alert configuration

## Contract

### Inputs and Prerequisites

- Snowflake account with Snowpipe or Snowpipe Streaming configured
- Knowledge of specific issue symptoms (offset errors, performance, data validation failures)
- Access to Snowpipe monitoring views and channel status
- Core troubleshooting rule 121c loaded for decision tree context

### Mandatory

- Use monotonically increasing offset tokens for exactly-once semantics
- Persist offsets to durable storage after successful inserts
- Validate row data types before streaming insert
- Batch 100-1000 rows per insert cycle for performance
- Follow debugging checklists systematically

### Forbidden

- Using non-unique offset tokens across batches
- Inserting rows one at a time in production (batch instead)
- Skipping data validation before insert
- Skipping checklist steps during debugging

### Execution Steps

1. Identify issue category (offset, performance, errors, auth, config)
2. Follow appropriate debugging checklist
3. Apply targeted fix pattern from this guide
4. Verify resolution with diagnostic queries from 121c

### Output Format

```text
Issue: [offset tracking | batch performance | data validation | auth | config]
Root Cause: [specific cause identified]
Fix Applied: [pattern from this guide]
Verification: [diagnostic query result]
```

### Validation

**Pre-Task-Completion Checks:**
- [ ] Issue category correctly identified
- [ ] Appropriate debugging checklist followed completely
- [ ] Fix pattern applied matches root cause
- [ ] Resolution verified with diagnostic queries

**Success Criteria:**
- Error rate reduced to acceptable level (<1% for data validation)
- Latency within target (<5 seconds for streaming)
- No duplicate or missing data (offset tracking)

**Negative Tests:**
- Verify offsets are unique and monotonic after fix
- Confirm batch sizes are appropriate (100-1000)
- Check data validation catches known bad records

### Post-Execution Checklist

- [ ] Issue category identified
- [ ] Appropriate checklist followed
- [ ] Fix pattern applied and tested
- [ ] Resolution verified with diagnostic queries

## Streaming Offset Tracking

**Problem:** Duplicate data, missing data, or offset errors in Snowpipe Streaming.

**Root causes:** Non-unique offset tokens, offset persistence failures, channel reopens without offset recovery.

```python
# Offset token tracking for exactly-once semantics
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

**Fixes:**
- Use unique, monotonically increasing offset tokens
- Persist offsets to disk/database after successful inserts
- Implement offset recovery logic for channel reopens
- Verify offset uniqueness within channel

## Streaming Batch Performance

**Problem:** Data takes >5 seconds to appear in table.

**Root causes:** Small batch sizes, network latency, classic architecture, channel contention.

```python
# Batch rows for better performance
from snowflake.ingest import SnowflakeStreamingIngestClient

client = SnowflakeStreamingIngestClient(...)
channel = client.open_channel(...)

batch = []
batch_size = 1000
global_offset = 0

for row in data_stream:
    batch.append(row)
    
    if len(batch) >= batch_size:
        # Insert batch with globally unique offset tokens
        for row_item in batch:
            channel.insert_row(row_item, offset_token=f'offset_{global_offset}')
            global_offset += 1
        batch = []

# Insert remaining rows
if batch:
    for row_item in batch:
        channel.insert_row(row_item, offset_token=f'offset_{global_offset}')
        global_offset += 1

channel.close()
```

**Fixes:**
- Increase batch size (100-1000 rows per batch)
- Use high-performance architecture for high-volume
- Reduce network hops (deploy closer to Snowflake region)
- Use multiple channels for parallel ingestion

## Streaming Data Validation

**Problem:** >1% of rows failing to insert.

**Root causes:** Schema mismatches, data type errors, constraint violations, malformed data.

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

**Fixes:**
- Validate data before insert
- Implement schema validation
- Check constraints (PK, FK, NOT NULL)
- Add data quality checks

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Inserting Rows One at a Time in Production**

**Problem:** Calling `insert_row()` in a tight loop with no batching sends each row as an individual network round-trip. This creates massive per-row overhead, saturates control-plane calls, and results in ingestion latencies of 10-100x compared to batched inserts. It also makes offset tracking fragile since each row is a separate commit boundary.

**Correct Pattern:** Accumulate rows into batches of 100-1000 before inserting. Use `insert_rows()` (plural) when available, or loop through the batch in a single logical unit. This amortizes network and commit overhead across many rows.

```python
# Wrong: one row at a time
for row in data_stream:
    channel.insert_row(row, offset_token=f'offset_{idx}')
    idx += 1
    # Each row = separate network round-trip

# Correct: batch rows before inserting
batch = []
for row in data_stream:
    batch.append(row)
    if len(batch) >= 1000:
        for row_item in batch:
            channel.insert_row(row_item, offset_token=f'offset_{idx}')
            idx += 1
        batch = []
```

**Anti-Pattern 2: Skipping Offset Persistence and Relying on In-Memory State**

**Problem:** Keeping the last committed offset only in application memory means any crash, restart, or deployment loses track of ingestion progress. On restart, the application either re-ingests from the beginning (causing duplicates) or starts from an arbitrary point (causing data loss). This completely defeats the exactly-once semantics that offset tracking provides.

**Correct Pattern:** Persist the last successfully committed offset to durable storage (database, file, or external state store) after each successful batch insert. On startup, read the persisted offset and resume from that position.

```python
# Wrong: offset only in memory
offset = 0
for row in data_stream:
    channel.insert_row(row, offset_token=f'offset_{offset}')
    offset += 1  # Lost on crash!

# Correct: persist offset to durable storage
offset = load_last_offset_from_storage()  # Recover on restart
for row in data_stream:
    offset += 1
    channel.insert_row(row, offset_token=f'offset_{offset}')
    if offset % 1000 == 0:
        save_offset_to_storage(offset)  # Durable checkpoint
```

**Anti-Pattern 3: Reusing the Same Channel Name Across Concurrent Processes**

**Problem:** Running multiple application instances that open channels with the same name causes channel ownership conflicts. When a second process opens a channel already held by the first, the first process's channel becomes invalidated. Both processes then fight over the channel, causing intermittent insert failures, lost data, and offset corruption.

**Correct Pattern:** Include a unique process identifier (hostname, PID, or partition ID) in channel names. Each concurrent process must use a distinct channel name targeting the same table.

```python
# Wrong: same channel name in all instances
channel = client.open_channel(
    channel_name='orders_channel',  # Collides across instances!
    ...
)

# Correct: unique channel name per process
import socket, os
channel = client.open_channel(
    channel_name=f'orders_{socket.gethostname()}_{os.getpid()}',
    ...
)
```

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
- [ ] No constraint violations (PK, FK, NOT NULL)

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
