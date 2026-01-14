# Snowflake Streams and Tasks

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** scheduled tasks, pipeline automation, MERGE patterns, SQL, Snowflake, task DAG, AFTER dependencies, Task History, create stream, create task, debug stream, task troubleshooting, stream consumption, task execution error, stream lag
**TokenBudget:** ~2550
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

- Source table(s) with change data capture requirements
- Target table(s) for incremental updates
- Warehouse for task execution
- ACCOUNTADMIN or role with CREATE STREAM, CREATE TASK privileges
- Understanding of data update patterns (frequency, volume, latency requirements)
- Idempotency requirements defined

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
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
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
