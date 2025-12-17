# Snowflake Streams and Tasks

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** scheduled tasks, pipeline automation, MERGE patterns, SQL, Snowflake, task DAG, AFTER dependencies, Task History, create stream, create task, debug stream, task troubleshooting, stream consumption, task execution error, stream lag
**TokenBudget:** ~1800
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Establish patterns for building robust, incremental data pipelines using Snowflake Streams and Tasks, covering change data capture, scheduling, idempotency, and monitoring for reliable data processing workflows.

## Rule Scope

Snowflake Streams and Tasks for incremental data pipelines and automated workflows

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **CREATE STREAM on source table** - captures INSERT/UPDATE/DELETE changes
- **CREATE TASK with MERGE** - consumes stream and applies changes to target
- **Chain tasks for DAGs:** Use `AFTER task1, task2` for dependencies
- **Consume stream at end of transaction** - ensures offset advances correctly
- **Use CREATE OR REPLACE** - ensures idempotent DDL operations
- **Monitor with Task History** - check execution status in Snowsight
- **Never consume stream mid-transaction** - breaks incremental processing

**Quick Checklist:**
- [ ] CREATE STREAM on source table
- [ ] CREATE TASK with MERGE statement
- [ ] Assign task to appropriate warehouse (see 119-snowflake-warehouse-management.md)
- [ ] Set SCHEDULE or AFTER dependencies
- [ ] Ensure idempotent operations (CREATE OR REPLACE, MERGE)
- [ ] Test stream consumption advances offset
- [ ] Monitor in Snowsight Task History

> **Investigation Required**
> When applying this rule:
> 1. Read existing STREAM and TASK definitions BEFORE making recommendations
> 2. Verify stream type (STANDARD, APPEND_ONLY) matches use case
> 3. Never speculate about task dependencies - check SHOW TASKS output
> 4. Review Task History for actual execution patterns
> 5. Make grounded recommendations based on investigated pipeline structure

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
- Capture changes with STREAM; apply with TASK-driven MERGE; chain tasks for DAGs.
- Ensure idempotency; consume stream at end of transaction; monitor with Task History.
- Follow official docs for implementation details and idempotent DDL.
</design_principles>

</contract>

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

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

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

## References

### External Documentation
- [Streams Management](https://docs.snowflake.com/en/user-guide/streams-manage) - Change data capture with streams for incremental processing
- [Tasks Introduction](https://docs.snowflake.com/en/user-guide/tasks-intro) - Scheduled task execution and workflow automation
- [Idempotent DDL](https://docs.snowflake.com/en/sql-reference/sql-ddl-idempotent) - CREATE OR REPLACE patterns for reliable automation

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Data Loading**: `rules/108-snowflake-data-loading.md`

## 1. Incremental Pipeline Design
- **Requirement:** Use a `STREAM` to capture change data (`INSERT`, `UPDATE`, `DELETE`) on a source table.
- **Requirement:** Use a `TASK` to schedule a `MERGE` that consumes the stream and applies changes to the target.
- **Requirement:** Build task graphs (DAGs) for multi-step pipelines with explicit dependencies.
- **Always:** Assign tasks to appropriate warehouses following `119-snowflake-warehouse-management.md` sizing and configuration guidance.

## 2. Idempotency and Monitoring
- **Requirement:** Tasks and DML must be idempotent. Use `CREATE OR REPLACE` for DDL and ensure re-runs do not duplicate data.
- **Always:** Consume the `STREAM` at the end of the transaction so its offset advances correctly.
- **Always:** Monitor task execution and status using Snowsight's Task History.

## Related Rules

**Closely Related** (consider loading together):
- `122-snowflake-dynamic-tables` - For alternative declarative approach to CDC pipelines
- `119-snowflake-warehouse-management` - For warehouse sizing and configuration for task execution

**Sometimes Related** (load if specific scenario):
- `103-snowflake-performance-tuning` - When optimizing task SQL statements
- `124-snowflake-data-quality-core` - When triggering tasks based on data quality events
- `111-snowflake-observability-core` - When monitoring task execution and stream consumption

**Complementary** (different aspects of same domain):
- `100-snowflake-core` - For naming conventions and DDL fundamentals
- `107-snowflake-security-governance` - For RBAC on tasks and streams
- `105-snowflake-cost-governance` - For monitoring task compute costs
