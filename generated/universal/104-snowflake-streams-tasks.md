**Keywords:** Streams, Tasks, incremental loading, CDC, change data capture, scheduled tasks, pipeline automation, MERGE patterns, SQL, Snowflake, task DAG, AFTER dependencies, Task History, create stream, create task, debug stream, task troubleshooting, stream consumption, task execution error, stream lag
**TokenBudget:** ~1150
**ContextTier:** High
**Depends:** 100-snowflake-core

# Snowflake Streams and Tasks

## Purpose
Establish patterns for building robust, incremental data pipelines using Snowflake Streams and Tasks, covering change data capture, scheduling, idempotency, and monitoring for reliable data processing workflows.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Streams and Tasks for incremental data pipelines and automated workflows


## Key Principles
- Capture changes with STREAM; apply with TASK-driven MERGE; chain tasks for DAGs.
- Ensure idempotency; consume stream at end of transaction; monitor with Task History.
- Follow official docs for implementation details and idempotent DDL.

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

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

## 1. Incremental Pipeline Design
- **Requirement:** Use a `STREAM` to capture change data (`INSERT`, `UPDATE`, `DELETE`) on a source table.
- **Requirement:** Use a `TASK` to schedule a `MERGE` that consumes the stream and applies changes to the target.
- **Requirement:** Build task graphs (DAGs) for multi-step pipelines with explicit dependencies.
- **Always:** Assign tasks to appropriate warehouses following `119-snowflake-warehouse-management.md` sizing and configuration guidance.

## 2. Idempotency and Monitoring
- **Requirement:** Tasks and DML must be idempotent. Use `CREATE OR REPLACE` for DDL and ensure re-runs do not duplicate data.
- **Always:** Consume the `STREAM` at the end of the transaction so its offset advances correctly.
- **Always:** Monitor task execution and status using Snowsight's Task History.

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template

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
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Demo Engineering**: `102-snowflake-sql-demo-engineering.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Data Loading**: `108-snowflake-data-loading.md`

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
