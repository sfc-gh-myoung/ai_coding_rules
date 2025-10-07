**Description:** Guidance for building robust, incremental data pipelines using Snowflake Streams and Tasks.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

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
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Streams Management](https://docs.snowflake.com/en/user-guide/streams-manage) - Change data capture with streams for incremental processing                                                                           
- [Tasks Introduction](https://docs.snowflake.com/en/user-guide/tasks-intro) - Scheduled task execution and workflow automation                                                                                         
- [Idempotent DDL](https://docs.snowflake.com/en/sql-reference/sql-ddl-idempotent) - CREATE OR REPLACE patterns for reliable automation

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Data Loading**: `108-snowflake-data-loading.md`
