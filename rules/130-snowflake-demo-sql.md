---
schema_version: v4.0
rule_version: v2.1.0
description: "SQL file patterns for Snowflake demos, workshops, and customer learning environments. Covers NN_<schema>_<operation>.sql naming, per-schema isolation, progress indicators, educational comments, and demo-safe idempotent patterns."
last_updated: 2026-10-06
keywords:
  - kw:demo sql
  - kw:per-schema isolation
  - kw:rerunnable demos
  - kw:progress indicators
  - kw:inline educational comments
  - kw:schema-based file naming
token_budget: ~1800
context_tier: High
depends:
  required:
    - 102-snowflake-sql-core.md  # General SQL file patterns
  optional:
    - 131-snowflake-demo-creation.md  # Synthetic data generation
    - 132-snowflake-demo-modeling.md  # Data modeling patterns
    - 102a-snowflake-sql-automation.md  # Production patterns
---
# Snowflake SQL: Demo Engineering and Workshops

## Scope

**What This Rule Covers:**
SQL file patterns for Snowflake demos, workshops, and customer learning environments: naming, isolated setup/teardown, verified progress, educational comments and non-destructive creation. Replacement requires explicit authorization; a demo label is not proof of disposability.

**When to Load This Rule:**
Load this rule when creating demo SQL files, rerunnable workshop scripts, educational SQL with inline documentation, or per-schema setup/teardown pairs. For production deployment (CREATE TABLE IF NOT EXISTS + MERGE, environment-agnostic templates), use `102a-snowflake-sql-automation.md` instead.

## Contract

### Inputs and Prerequisites

- Target database exists; confirm CREATE SCHEMA privilege before generating DDL
- Demo audience level known (beginner/intermediate/advanced) to calibrate comment verbosity
- Existing project SQL files reviewed to follow established naming patterns
- FK dependencies across files mapped before finalizing execution order

### Mandatory

**File naming:** `NN_<schema>_<operation>.sql` — reserve `00` for database-level setup, `98`–`99` for teardown, `01`–`89` for operational steps. Every file header must list filename, prerequisites, and objects created or dropped.

**Execution order:** Order files by dependency, not by number. Create dimensions and facts, populate/validate the parent and date dimension rows, then create or replace dependent views only after a separate inventory and authorization check. A table's existence alone does not establish that its required rows are present. CLI orchestration menus must match actual execution order.

**Complete-load gate:** In the final plan explicitly create all base tables, load parent dimensions, load date dimensions, then load facts. Only then run the complete persisted integrity gate; it references facts and cannot run during dimension-only loading. Partial per-table checks must be named separately and must not reference objects not yet created or loaded. Create views afterward and validate their grain/totals last.

**Schema isolation:** Setup and teardown must affect only verified owned objects. Never drop the database or another schema from a schema-scoped file.

**Ownership evidence:** A named or "owned target" schema does not establish that its existing data is disposable, that every object in it is owned, or that replacement is authorized. If ownership, dependency, or disposability is unknown, label it unverified and propose non-destructive creation only; never describe planned demo objects as already verified owned.

**Creation authority:** Non-destructive syntax is a proposal choice, not permission. A target label does not license even `IF NOT EXISTS` DDL, inserts, metadata inspection or checks. Design-only authorization covers supplied-file reads and proposals; all account operations require separate authorization.

**Draft teardown status:** If ownership evidence is unavailable, defer executable teardown and state the inventory/approval prerequisites in prose. Never copy "verified-owned" from an example into a draft. Creation with `IF NOT EXISTS` can retain a pre-existing object and does not prove ownership.

**Partial-ownership safety:** If only specific tables are verified as owned, do not propose `DROP SCHEMA ... CASCADE`. Check dependencies and propose only verified owned objects in child-first order: dependent views before facts, facts before parent dimensions. A proposed name or successful `IF NOT EXISTS` does not establish ownership of an existing object. A proposal is not execution authorization; request approval before any destructive action.

**Cleanup proposal gate:** Every proposal must separately state that actual dependencies are unverified until inventoried, including views, streams, tasks and external consumers. Object names alone do not prove an FK relationship. Give child-first order as conditional when dependency evidence is absent; execution requires both dependency review and explicit approval, even when object ownership is supplied.

**Teardown for exclusively owned disposable schemas:** Schema-wide deletion requires verified exclusive ownership, a complete contained-object inventory, dependency review and separate approval. Otherwise retain the schema and remove only individually authorized objects. Include a deletion warning naming both removed and preserved resources.

**Reruns:** Default to non-destructive proposals. Confirm disposable ownership and explicit authorization before `CREATE OR REPLACE TABLE`; it can discard existing data. `IF NOT EXISTS` does not reconcile an existing definition. Before including `CREATE OR REPLACE VIEW` or stage replacement in an executable plan, inspect existing objects, grants and dependents and obtain authorization. A design-only sketch must label replacement conditional on those checks, not imply that views are safe to replace because they retain no table rows.

**Progress indicators:** Emit a PASS status only after verifying that each preceding step succeeded; never claim completion after a partial or skipped load.

**Educational comments:** Explain why each step exists. Define acronyms inline and document columns' purpose, units and valid values.

```sql
-- ============================================================================
-- Filename: 01_analytics_setup.sql
-- Prerequisites: Database DEMO_DB must exist
-- Creates: ANALYTICS schema, CUSTOMERS table, ORDERS table
-- ============================================================================

-- ANALYTICS groups all customer analytics objects in one namespace
CREATE SCHEMA IF NOT EXISTS DEMO_DB.ANALYTICS
    COMMENT = 'Customer analytics for demo';
SELECT '[PASS] ANALYTICS schema created' AS progress;

-- Verify key uniqueness and parent references in the data before loading.
CREATE TABLE IF NOT EXISTS DEMO_DB.ANALYTICS.CUSTOMERS (
    customer_id   INT           PRIMARY KEY,
    customer_name VARCHAR(100)  NOT NULL  COMMENT 'Full customer name',
    segment       VARCHAR(20)             COMMENT 'Values: enterprise, smb, consumer'
) COMMENT = 'Customer master data';
SELECT '[PASS] CUSTOMERS created' AS progress;

-- ORDERS references CUSTOMERS; CUSTOMERS must exist first (dependency order)
CREATE TABLE IF NOT EXISTS DEMO_DB.ANALYTICS.ORDERS (
    order_id    INT           PRIMARY KEY,
    customer_id INT           NOT NULL  COMMENT 'References CUSTOMERS.customer_id',
    order_date  DATE          NOT NULL,
    amount_usd  NUMBER(10,2)  NOT NULL  COMMENT 'Order total in US dollars'
) COMMENT = 'Order transactions';
SELECT '[PASS] ORDERS created' AS progress;

SELECT 'ANALYTICS setup complete!' AS status;
```

When only `CUSTOMERS` and `ORDERS` are verified owned, propose an object-scoped teardown and review dependencies before any separately authorized execution:

```sql
-- ============================================================================
-- Filename: 99_analytics_teardown.sql
-- EXAMPLE PRECONDITION: Both tables independently verified owned; deletion approved.
-- WARNING: Deletes data in CUSTOMERS and ORDERS only.
-- Preserve: ANALYTICS schema, other objects, database, shared resources.
-- ============================================================================
DROP TABLE IF EXISTS DEMO_DB.ANALYTICS.ORDERS;
DROP TABLE IF EXISTS DEMO_DB.ANALYTICS.CUSTOMERS;
```

### Execution Steps

1. Confirm target database exists and required privileges are in place
2. Identify demo audience level and schema isolation strategy
3. Map FK dependencies across all files before writing setup scripts
4. Create `NN_<schema>_setup.sql` with file header, step comments, progress indicators
5. Draft an object-scoped teardown with a WARNING block and dependency review; use a schema-scoped teardown only after separately verifying exclusive ownership and approval
6. Order execution so referenced tables are created before referencing tables
7. Align CLI orchestration menus with actual execution order
8. When separately authorized, run setup DDL; generate facts and a covering date range; explicitly load parent dimensions, date dimensions and facts before post-load checks; create views only after persisted checks pass. Test in a disposable environment; teardown requires separate authorization. Otherwise report each check as unexecuted

### Validation

- Report actual rerun results only when execution was authorized and performed
- `[PASS]` indicators appear only after verified successful steps
- All object names fully qualified (`DB.SCHEMA.OBJECT`)
- Every setup file has a matching teardown file
- Teardown targets only verified owned objects; schema-wide deletion requires exclusive ownership and separate authorization
- File headers list prerequisites and created objects
- Referenced tables precede referencing tables in all execution paths
- Required parent/date dimension rows are populated and coverage checked before creating dependent views
- Partial-ownership cleanup: only verified owned tables proposed in child-first order, dependencies checked; explicit authorization obtained before execution

## References

- [Snowflake SQL Command Reference](https://docs.snowflake.com/en/sql-reference-commands.html)
- [Snowflake Quickstarts](https://quickstarts.snowflake.com/)
