# Snowflake Streams and Tasks

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-20
**LoadTrigger:** kw:stream, kw:task, kw:cdc
**Keywords:** scheduled tasks, pipeline automation, MERGE patterns, SQL, Snowflake, task DAG, AFTER dependencies, Task History, create stream, create task, debug stream, task troubleshooting, stream consumption, task execution error, stream lag
**TokenBudget:** ~3100
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Patterns for building robust, incremental data pipelines using Snowflake Streams and Tasks, covering change data capture, scheduling, idempotency, and monitoring for reliable data processing workflows.

**When to Load This Rule:**
- Building incremental data pipelines with Streams and Tasks
- Implementing change data capture (CDC) patterns
- Scheduling automated data workflows
- Monitoring task execution and stream lag
- Troubleshooting stream/task pipeline issues

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **100-snowflake-core.md** - Snowflake SQL patterns and best practices

### External Documentation
- [Streams Management](https://docs.snowflake.com/en/user-guide/streams-manage) - Change data capture with streams for incremental processing
- [Tasks Introduction](https://docs.snowflake.com/en/user-guide/tasks-intro) - Scheduled task execution and workflow automation
- [Idempotent DDL](https://docs.snowflake.com/en/sql-reference/sql-ddl-idempotent) - CREATE OR REPLACE patterns for reliable automation

### Related Rules

**Closely Related** (consider loading together):
- **122-snowflake-dynamic-tables.md** - Alternative declarative approach to CDC pipelines
- **119-snowflake-warehouse-management.md** - Warehouse sizing and configuration for task execution

**Sometimes Related** (load if specific scenario):
- **103-snowflake-performance-tuning.md** - Optimizing task SQL statements
- **124-snowflake-data-quality-core.md** - Triggering tasks based on data quality events
- **111-snowflake-observability-core.md** - Monitoring task execution and stream consumption

**Complementary** (different aspects of same domain):
- **100-snowflake-core.md** - Naming conventions and DDL fundamentals
- **102-snowflake-sql-core.md** - General SQL file patterns
- **107-snowflake-security-governance.md** - RBAC on tasks and streams
- **105-snowflake-cost-governance.md** - Monitoring task compute costs
- **108-snowflake-data-loading.md** - Data loading patterns

## Contract

### Inputs and Prerequisites

- Role with CREATE STREAM and CREATE TASK privileges on target schema (typically SYSADMIN or a custom role with these grants)
- USAGE privilege on the warehouse assigned to tasks
- EXECUTE TASK privilege (account-level, granted by ACCOUNTADMIN) for the role that owns the task
- Source table(s) must exist before stream creation
- Target table(s) for incremental updates
- Understanding of data update patterns (frequency, volume, latency requirements)

### Mandatory

- CREATE STREAM on source table to capture changes
- CREATE TASK with MERGE statement for idempotent processing
- WAREHOUSE assignment for task execution
- SCHEDULE or AFTER dependencies for task orchestration
- CREATE OR REPLACE pattern for idempotent DDL
- SYSTEM$STREAM_HAS_DATA() check in task WHEN clause
- Task History monitoring in Snowsight
- ALTER TASK ... RESUME to activate tasks

### Forbidden

- Consuming stream mid-transaction (breaks offset advancement)
- Tasks without MERGE (non-idempotent INSERT/UPDATE/DELETE)
- Hardcoded schedules without SYSTEM$STREAM_HAS_DATA() check
- Tasks without warehouse assignment
- Circular task dependencies
- Tasks that modify source tables (creates infinite loops)

### Execution Steps

1. Analyze source table change patterns and target table requirements
2. CREATE STREAM on source table (STANDARD for updates/deletes, APPEND_ONLY for inserts)
3. Design MERGE statement with proper join conditions and WHEN clauses
4. CREATE TASK with MERGE logic, WHEN clause checks SYSTEM$STREAM_HAS_DATA()
5. Assign appropriate warehouse to task (see 119-snowflake-warehouse-management.md)
6. Set SCHEDULE (time-based) or AFTER dependencies (DAG-based)
7. Test stream consumption: Verify offset advances after MERGE completes
8. ALTER TASK ... RESUME to activate task
9. Monitor in Snowsight Task History for execution status and errors

### Output Format

- Stream DDL: CREATE STREAM statements with appropriate type
- Task DDL: CREATE TASK with MERGE logic and scheduling
- MERGE statement: Idempotent logic handling INSERT/UPDATE/DELETE
- Monitoring queries: Task History, stream offset, row counts
- Documentation: Pipeline description, dependencies, SLA

### Validation

**Test Requirements:**
- Stream created successfully: SHOW STREAMS
- Task created and resumed: SHOW TASKS, status = 'started'
- Test data inserted into source triggers stream
- Task executes successfully (check Task History)
- Stream offset advances after task completion
- Target table updated correctly (compare source + stream to target)
- Idempotency verified: Re-running task with same data produces same result

**Success Criteria:**
- Stream captures all changes (INSERT, UPDATE, DELETE as needed)
- Task executes on schedule or when data available
- MERGE handles duplicates, late arrivals, out-of-order data
- No failed task executions in Task History
- Stream offset advances consistently
- Target table matches source table (accounting for stream lag)

### Design Principles

- Capture changes with STREAM; apply with TASK-driven MERGE; chain tasks for DAGs.
- Ensure idempotency; consume stream at end of transaction; monitor with Task History.
- Follow official docs for implementation details and idempotent DDL.

### Post-Execution Checklist

- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Consuming Stream Mid-Transaction**
```sql
-- Bad: Stream consumed before transaction completes
BEGIN TRANSACTION;
  INSERT INTO target_table SELECT * FROM source_stream;
  -- More operations here
  UPDATE other_table SET status = 'processed';
  -- Stream offset advances here, not at COMMIT
COMMIT;
```
**Problem:** Stream offset advances at first consumption; subsequent transaction failure leaves data inconsistent; lost change data; breaks incremental processing guarantee

**Correct Pattern:**
```sql
-- Good: Single atomic MERGE consumes stream at transaction end
BEGIN TRANSACTION;
  MERGE INTO target_table t
  USING source_stream s
    ON t.id = s.id
  WHEN MATCHED AND s.METADATA$ACTION = 'DELETE' THEN DELETE
  WHEN MATCHED THEN UPDATE SET t.value = s.value
  WHEN NOT MATCHED THEN INSERT (id, value) VALUES (s.id, s.value);
  -- Stream offset advances only at COMMIT
COMMIT;
```
**Benefits:** Atomic stream consumption; transactional consistency; automatic rollback on failure; idempotent processing

**Anti-Pattern 2: Not Using CREATE OR REPLACE for Task DDL**
```sql
-- Bad: CREATE fails if task exists, requires manual DROP
CREATE TASK load_incremental_data
  WAREHOUSE = 'ETL_WH'
  SCHEDULE = '5 MINUTE'
AS
  CALL process_stream_data();
```
**Problem:** Deployment fails if task exists; requires manual intervention; not idempotent; complicates CI/CD pipelines; error-prone updates

**Correct Pattern:**
```sql
-- Good: Idempotent DDL with CREATE OR REPLACE
CREATE OR REPLACE TASK load_incremental_data
  WAREHOUSE = 'ETL_WH'
  SCHEDULE = '5 MINUTE'
AS
  CALL process_stream_data();
```
**Benefits:** Idempotent deployments; CI/CD friendly; updates task definition safely; no manual cleanup needed; repeatable automation

**Anti-Pattern 3: Missing Task Dependencies in DAGs**
```sql
-- Bad: Tasks run in parallel, wrong order
CREATE TASK extract_data WAREHOUSE = 'ETL_WH' SCHEDULE = '1 HOUR' AS CALL extract();
CREATE TASK transform_data WAREHOUSE = 'ETL_WH' SCHEDULE = '1 HOUR' AS CALL transform();
CREATE TASK load_data WAREHOUSE = 'ETL_WH' SCHEDULE = '1 HOUR' AS CALL load();
-- All run simultaneously at top of hour, not sequentially!
```
**Problem:** Tasks run in parallel instead of sequence; transform runs before extract completes; load runs on stale data; race conditions; data corruption

**Correct Pattern:**
```sql
-- Good: Explicit AFTER dependencies create DAG
CREATE OR REPLACE TASK extract_data
  WAREHOUSE = 'ETL_WH'
  SCHEDULE = '1 HOUR'
AS CALL extract();

CREATE OR REPLACE TASK transform_data
  WAREHOUSE = 'ETL_WH'
  AFTER extract_data  -- Runs only after extract_data succeeds
AS CALL transform();

CREATE OR REPLACE TASK load_data
  WAREHOUSE = 'ETL_WH'
  AFTER transform_data  -- Runs only after transform_data succeeds
AS CALL load();
```
**Benefits:** Correct execution order; automatic dependency resolution; Snowflake manages scheduling; no race conditions; transactional DAG execution

**Anti-Pattern 4: Not Monitoring Task Execution Status**
```sql
-- Bad: Create tasks but never check if they're working
CREATE OR REPLACE TASK my_task ... ;
ALTER TASK my_task RESUME;
-- [Never checks Task History, assumes it works]
```
**Problem:** Silent failures go unnoticed; tasks may suspend on errors; no visibility into execution patterns; credit waste if tasks loop; missed SLAs

**Correct Pattern:**
```sql
-- Good: Monitor task execution in Snowsight Task History
-- Check execution history programmatically:
SELECT
  name,
  state,
  completed_time,
  scheduled_time,
  error_code,
  error_message
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE name = 'MY_TASK'
ORDER BY scheduled_time DESC
LIMIT 10;

-- Set up alerts for task failures:
-- Use SYSTEM$SEND_EMAIL or webhook on error_code IS NOT NULL
```
**Benefits:** Proactive error detection; execution pattern visibility; SLA monitoring; credit usage tracking; automated alerting on failures

## Output Format Examples

```sql
-- Pipeline Setup Workflow

-- Step 1: Create stream on source table
CREATE OR REPLACE STREAM my_db.my_schema.orders_stream
  ON TABLE my_db.my_schema.orders
  SHOW_INITIAL_ROWS = FALSE;

-- Step 2: Create target table
CREATE TABLE IF NOT EXISTS my_db.my_schema.orders_processed (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER,
    amount NUMBER(12,2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Step 3: Create task with MERGE and WHEN clause
CREATE OR REPLACE TASK my_db.my_schema.process_orders
  WAREHOUSE = 'ETL_WH'
  SCHEDULE = '5 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('MY_DB.MY_SCHEMA.ORDERS_STREAM')
AS
  MERGE INTO my_db.my_schema.orders_processed t
  USING my_db.my_schema.orders_stream s
    ON t.order_id = s.order_id
  WHEN MATCHED AND s.METADATA$ACTION = 'DELETE' THEN DELETE
  WHEN MATCHED THEN UPDATE SET t.amount = s.amount, t.processed_at = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN INSERT (order_id, customer_id, amount)
    VALUES (s.order_id, s.customer_id, s.amount);

-- Step 4: Resume the task
ALTER TASK my_db.my_schema.process_orders RESUME;

-- Step 5: Verify setup
SHOW STREAMS LIKE 'ORDERS_STREAM' IN SCHEMA my_db.my_schema;
SHOW TASKS LIKE 'PROCESS_ORDERS' IN SCHEMA my_db.my_schema;
```

## Incremental Pipeline Design
- **Requirement:** Use a `STREAM` to capture change data (`INSERT`, `UPDATE`, `DELETE`) on a source table.
- **Requirement:** Use a `TASK` to schedule a `MERGE` that consumes the stream and applies changes to the target.
- **Requirement:** Build task graphs (DAGs) for multi-step pipelines with explicit dependencies.
- **Always:** Assign tasks to appropriate warehouses following `119-snowflake-warehouse-management.md` sizing and configuration guidance.

## Idempotency and Monitoring
- **Requirement:** Tasks and DML must be idempotent. Use `CREATE OR REPLACE` for DDL and ensure re-runs do not duplicate data.
- **Always:** Consume the `STREAM` at the end of the transaction so its offset advances correctly.
- **Always:** Monitor task execution and status using Snowsight's Task History.

## Stream Staleness Monitoring

A stream becomes **stale** when its offset falls behind the data retention period of the source table. Once stale, the stream cannot be consumed and must be recreated, losing unprocessed changes.

### Prevention and Detection

```sql
-- Check stream staleness status
SELECT stream_name, stale, stale_after
FROM TABLE(INFORMATION_SCHEMA.STREAMS())
WHERE stream_schema = 'MY_SCHEMA';

-- Use SYSTEM$STREAM_HAS_DATA() to check for pending changes
SELECT SYSTEM$STREAM_HAS_DATA('MY_DB.MY_SCHEMA.MY_STREAM');
```

**Key strategies:**
- **Monitor `STALE_AFTER`:** This column shows when the stream will become stale. Set alerts when `STALE_AFTER` is within 24 hours of the current time.
- **Increase source table retention:** `ALTER TABLE source SET DATA_RETENTION_TIME_IN_DAYS = 14;` -- gives streams more time before staleness.
- **Schedule tasks frequently enough** that the stream is consumed well before the retention window expires.
- **Alert on task failures:** A failed task that stops consuming a stream is the most common cause of staleness. Monitor `TASK_HISTORY()` for consecutive failures.
