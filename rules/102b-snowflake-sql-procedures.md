# Snowflake SQL: Stored Procedures and UDFs

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential patterns for Snowflake SQL Scripting stored procedures and UDFs.
> Load when creating or modifying procedures/functions using LANGUAGE SQL.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-02-18
**Keywords:** stored procedure, CREATE PROCEDURE, UDF, CREATE FUNCTION, dollar quoting, nested quotes, EXECUTE AS, EXECUTE IMMEDIATE, dynamic SQL, bind variables, OWNER, CALLER, RESTRICTED CALLER, SQL scripting, procedure body
**TokenBudget:** ~5700
**ContextTier:** High
**Depends:** 102-snowflake-sql-core.md
**LoadTrigger:** kw:stored-procedure, kw:create-procedure, kw:udf, kw:create-function

## Scope

**What This Rule Covers:**
Best practices for authoring Snowflake SQL Scripting stored procedures and user-defined functions (UDFs). Covers body delimiter selection (`$$` vs single quotes), nested quoting strategies, the EXECUTE AS security model (OWNER, CALLER, RESTRICTED CALLER), EXECUTE IMMEDIATE for dynamic SQL, bind variable usage, and structural templates. Focused exclusively on LANGUAGE SQL handlers.

**When to Load This Rule:**
- Creating stored procedures with LANGUAGE SQL
- Creating SQL UDFs or UDTFs
- Choosing between `$$` and single-quote body delimiters
- Handling nested quotes inside procedure bodies
- Deciding between EXECUTE AS OWNER, CALLER, or RESTRICTED CALLER
- Writing dynamic SQL with EXECUTE IMMEDIATE
- Debugging quoting or escaping errors in procedures

## References

### Dependencies

**Must Load First:**
- **102-snowflake-sql-core.md** - SQL file patterns, fully qualified names, reserved characters

**Related:**
- **102a-snowflake-sql-automation.md** - Production CI/CD patterns for SQL deployment
- **100-snowflake-core.md** - Snowflake fundamentals

### External Documentation

**Snowflake:**
- [CREATE PROCEDURE](https://docs.snowflake.com/en/sql-reference/sql/create-procedure) - Full syntax reference
- [CREATE FUNCTION](https://docs.snowflake.com/en/sql-reference/sql/create-function) - UDF syntax reference
- [Writing Stored Procedures in Snowflake Scripting](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-snowflake-scripting) - SQL Scripting guide
- [Dollar-Quoted String Constants](https://docs.snowflake.com/en/sql-reference/data-types-text#dollar-quoted-string-constants) - Quoting rules
- [EXECUTE IMMEDIATE](https://docs.snowflake.com/en/sql-reference/sql/execute-immediate) - Dynamic SQL execution
- [Constructing SQL at Runtime](https://docs.snowflake.com/en/user-guide/querying-construct-at-runtime) - Dynamic SQL patterns
- [Caller's Rights and Owner's Rights](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-rights) - Security model

## Contract

### Inputs and Prerequisites

- Role with CREATE PROCEDURE privilege on target schema (for procedures) or CREATE FUNCTION privilege (for UDFs)
- For caller's rights procedures, the calling role needs object-level privileges on referenced objects
- For owner's rights procedures, the owner role must have privileges on all referenced objects
- Understanding of procedure/function purpose and parameters
- Knowledge of whether caller context access is needed (session variables, caller's role)
- Access to Snowflake CLI or Snowsight for testing

### Mandatory

- Use `$$` delimiters for all procedure and UDF bodies
- Fully qualify all object names inside procedure bodies (DATABASE.SCHEMA.OBJECT)
- Explicitly specify `EXECUTE AS OWNER` or `EXECUTE AS CALLER` on every procedure
- Use bind variables (`?` with `USING`) in EXECUTE IMMEDIATE when possible
- Use `CREATE OR REPLACE PROCEDURE` with `COMMENT` for documentation
- Prefix variable references with `:` in SQL statements within Snowflake Scripting blocks

### Forbidden

- Single-quote delimiters for procedure bodies that contain any string literals
- Literal `$$` sequences inside a `$$`-delimited body (causes premature termination)
- String concatenation of user-supplied values in EXECUTE IMMEDIATE (SQL injection risk)
- Omitting `EXECUTE AS` clause (silently defaults to OWNER, which may not be intended)
- Unqualified object names inside procedure bodies (breaks when called from different contexts)

### Execution Steps

1. Determine whether the logic requires a procedure (side effects, DML) or function (pure computation, usable in SELECT)
2. Choose `EXECUTE AS` mode based on security requirements (see decision matrix below)
3. Define parameter list with explicit types and optional DEFAULT values
4. Write the body between `$$` delimiters using Snowflake Scripting (DECLARE/BEGIN/END)
5. Use fully qualified object names for all tables, views, and stages referenced in the body
6. For dynamic SQL, use EXECUTE IMMEDIATE with bind variables (`?` and `USING`) instead of string concatenation
7. Add a `COMMENT` to the CREATE statement describing purpose and parameters
8. Test the procedure with `CALL` and verify behavior under the intended execution context

### Output Format

SQL files (.sql) containing CREATE OR REPLACE PROCEDURE or CREATE OR REPLACE FUNCTION statements with `$$`-delimited bodies, explicit EXECUTE AS clause, and descriptive COMMENT.

### Validation

**Test Requirements:**
- Procedure creates without syntax errors
- Single quotes inside body do not cause delimiter conflicts
- Dynamic SQL executes correctly with bind variables
- Procedure behaves correctly under its EXECUTE AS context
- All object references resolve from any calling context

**Success Criteria:**
- Body uses `$$` delimiters (not single quotes)
- EXECUTE AS explicitly specified
- No unqualified object names in body
- EXECUTE IMMEDIATE uses bind variables where possible
- COMMENT present on the object

### Design Principles

- **Readability First**: `$$` delimiters eliminate quote-escaping noise, making procedure bodies readable as plain SQL
- **Explicit Security**: Always declare EXECUTE AS to make the security model visible and intentional
- **Injection Prevention**: Bind variables in EXECUTE IMMEDIATE prevent SQL injection by design
- **Context Independence**: Fully qualified names ensure procedures work regardless of the caller's USE DATABASE/SCHEMA

### Post-Execution Checklist

- [ ] Body delimited with `$$` (not single quotes)
- [ ] `EXECUTE AS OWNER`, `CALLER`, or `RESTRICTED CALLER` explicitly specified
- [ ] All object names fully qualified (DATABASE.SCHEMA.OBJECT)
- [ ] Dynamic SQL uses bind variables with `USING` clause
- [ ] No literal `$$` inside the procedure body
- [ ] `COMMENT` added describing purpose
- [ ] Tested via `CALL` under intended role/context
- [ ] Variable references use `:variable_name` syntax in SQL statements

## Body Delimiter Selection

### Always Use `$$` for Procedure and UDF Bodies

**Rule:** Wrap procedure and UDF bodies in `$$` (dollar-quoted string constants), not single quotes.

**Why:** Inside `$$` delimiters, single quotes, backslashes, and newlines are treated literally. No escaping is needed. This makes procedure bodies readable and maintainable.

**Standard pattern:**
```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.update_status(
    record_id INTEGER,
    new_status VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
COMMENT = 'Update record status and return confirmation'
AS
$$
DECLARE
    old_status VARCHAR;
BEGIN
    SELECT status INTO :old_status
    FROM my_db.my_schema.records
    WHERE id = :record_id;

    UPDATE my_db.my_schema.records
    SET status = :new_status, updated_at = CURRENT_TIMESTAMP()
    WHERE id = :record_id;

    RETURN 'Updated from ' || :old_status || ' to ' || :new_status;
END;
$$;
```

### When Single Quotes Are Acceptable

Single-quote delimiters are only acceptable for trivial one-line bodies with no internal string literals:

```sql
-- Acceptable: no internal quotes
CREATE OR REPLACE FUNCTION my_db.my_schema.double_it(x NUMBER)
RETURNS NUMBER
LANGUAGE SQL
AS 'SELECT x * 2';
```

For anything more complex, use `$$`. There is no benefit to single quotes, and they create maintenance burden as soon as string literals are added.

### GET_DDL Behavior

`GET_DDL()` returns procedure definitions with single-quote delimiters regardless of how they were originally created. This is a Snowflake behavior, not a problem with your code. Always store your source-of-truth definitions in version control using `$$` delimiters.

## Quoting Rules Inside Procedure Bodies

### Single Quotes for String Literals

Inside a `$$`-delimited body, use single quotes normally for string literals:

```sql
AS
$$
BEGIN
    -- Single quotes work naturally inside $$
    INSERT INTO my_db.my_schema.audit_log (event, message)
    VALUES ('STATUS_CHANGE', 'Record updated successfully');
    RETURN 'Done';
END;
$$;
```

### Escaping Single Quotes Inside Strings

When a string literal itself must contain a single quote, double it (`''`):

```sql
AS
$$
DECLARE
    msg VARCHAR;
BEGIN
    -- Doubling the single quote: O''Brien
    msg := 'Customer O''Brien updated';
    RETURN :msg;
END;
$$;
```

This is standard SQL escaping and is the only escaping you need inside `$$` bodies.

### Double Quotes for Identifiers

Use double quotes for case-sensitive or special-character identifiers:

```sql
AS
$$
BEGIN
    -- Double quotes preserve case and allow special characters
    UPDATE my_db.my_schema."MixedCaseTable"
    SET "Column With Spaces" = 'value'
    WHERE "Primary-Key" = :input_id;
END;
$$;
```

### The `$$` Limitation

You cannot include a literal `$$` sequence inside a `$$`-delimited body. This is rarely an issue, but if needed, construct it from parts:

```sql
AS
$$
DECLARE
    dollar_signs VARCHAR;
BEGIN
    -- Build '$$' from concatenation if needed
    dollar_signs := '$' || '$';
    RETURN dollar_signs;
END;
$$;
```

### Nested Quoting in Dynamic SQL

When building SQL strings inside a procedure, quotes must be escaped within the string context. Each nesting level requires doubling:

```sql
AS
$$
DECLARE
    dynamic_sql VARCHAR;
BEGIN
    -- The inner string literal 'ACTIVE' needs doubled quotes
    -- because it is inside a VARCHAR string
    dynamic_sql := 'SELECT * FROM my_db.my_schema.users WHERE status = ''ACTIVE''';
    EXECUTE IMMEDIATE :dynamic_sql;
END;
$$;
```

**Prefer bind variables** over string construction to avoid nested quoting entirely (see EXECUTE IMMEDIATE section below).

## EXECUTE AS Security Model

### Overview

Every procedure runs under one of three security contexts. The default is OWNER. Always specify it explicitly.

**OWNER (default):**
- Runs as: Procedure owner's role
- Session variables: Not accessible
- Use when: Procedure needs elevated privileges the caller lacks

**CALLER:**
- Runs as: Caller's current role
- Session variables: Accessible
- Use when: Procedure should operate within caller's permissions

**RESTRICTED CALLER:**
- Runs as: Owner's privileges, restricted to caller's accessible objects
- Session variables: Not accessible
- Use when: Owner-level operations scoped to caller's object visibility

### EXECUTE AS OWNER

The procedure runs with the owner's grants. Callers do not need direct access to underlying objects. Session variables set by the caller are not accessible.

```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.archive_old_records(
    days_threshold INTEGER DEFAULT 90
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
COMMENT = 'Archive records older than threshold days. Runs with elevated privileges.'
AS
$$
DECLARE
    rows_moved INTEGER;
BEGIN
    INSERT INTO my_db.my_schema.records_archive
    SELECT * FROM my_db.my_schema.records
    WHERE created_at < DATEADD(DAY, -:days_threshold, CURRENT_DATE());

    rows_moved := SQLROWCOUNT;

    DELETE FROM my_db.my_schema.records
    WHERE created_at < DATEADD(DAY, -:days_threshold, CURRENT_DATE());

    RETURN :rows_moved || ' records archived';
END;
$$;
```

### EXECUTE AS CALLER

The procedure runs with the caller's current role and can access session variables. Use when the procedure should respect the caller's permissions.

```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.get_my_records()
RETURNS TABLE (id INTEGER, name VARCHAR, status VARCHAR)
LANGUAGE SQL
EXECUTE AS CALLER
COMMENT = 'Return records visible to the calling role'
AS
$$
DECLARE
    res RESULTSET;
BEGIN
    -- Runs with caller permissions: only sees what caller can see
    res := (SELECT id, name, status FROM my_db.my_schema.records);
    RETURN TABLE(res);
END;
$$;
```

### EXECUTE AS RESTRICTED CALLER

A hybrid: runs with owner's privileges but only on objects the caller can also access. Prevents privilege escalation while allowing owner-level operations on shared objects.

```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.generate_report(
    schema_name VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS RESTRICTED CALLER
COMMENT = 'Generate report on schema objects visible to caller'
AS
$$
DECLARE
    obj_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO :obj_count
    FROM my_db.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = :schema_name;

    RETURN :schema_name || ' contains ' || :obj_count || ' tables';
END;
$$;
```

### Decision Matrix

Use this to choose the right execution context:

- **Does the procedure need to access objects the caller cannot?** Use OWNER
- **Should the procedure respect the caller's row-level or object-level permissions?** Use CALLER
- **Does it need owner privileges but scoped to caller-visible objects?** Use RESTRICTED CALLER
- **Does the procedure need to read session variables set by the caller?** Use CALLER (OWNER cannot read session variables)

## EXECUTE IMMEDIATE and Dynamic SQL

### Bind Variables (Preferred)

Use `?` placeholders with the `USING` clause to pass values safely. This prevents SQL injection and avoids nested quoting:

```sql
AS
$$
DECLARE
    rs RESULTSET;
    query VARCHAR DEFAULT 'SELECT * FROM my_db.my_schema.orders WHERE region = ? AND amount > ?';
BEGIN
    rs := (EXECUTE IMMEDIATE :query USING (region_param, min_amount));
    RETURN TABLE(rs);
END;
$$;
```

**Bind variables work for:** values in WHERE clauses, INSERT VALUES, and other data positions.

**Bind variables do not work for:** table names, column names, schema names, or other identifiers. For those, use string concatenation with validation.

### String Concatenation (When Bind Variables Are Not Possible)

When you must construct identifiers dynamically (table names, column names), concatenate strings. Validate inputs to prevent injection:

```sql
AS
$$
DECLARE
    query VARCHAR;
    row_count INTEGER;
BEGIN
    -- Validate: only allow alphanumeric and underscore in table names
    IF (:table_name RLIKE '^[A-Za-z_][A-Za-z0-9_]*$') THEN
        query := 'SELECT COUNT(*) FROM my_db.my_schema.' || :table_name;
        EXECUTE IMMEDIATE :query INTO :row_count;
        RETURN :row_count;
    ELSE
        RETURN -1;  -- Invalid table name
    END IF;
END;
$$;
```

### Nested Quote Escaping in Dynamic SQL

When dynamic SQL must contain string literals, each nesting level doubles the quotes. This gets complex fast -- prefer bind variables to avoid it:

```sql
AS
$$
DECLARE
    dynamic_sql VARCHAR;
BEGIN
    -- Level 1: The procedure body (inside $$, no escaping needed)
    -- Level 2: The VARCHAR string assigned to dynamic_sql ('' escaping)
    -- The inner string 'ACTIVE' becomes ''ACTIVE'' inside the VARCHAR
    dynamic_sql := 'UPDATE my_db.my_schema.users SET status = ''ACTIVE'' WHERE id = ?';
    EXECUTE IMMEDIATE :dynamic_sql USING (:user_id);
END;
$$;
```

**Quote nesting reference:**

- **Inside `$$` body (direct SQL):** `'value'` -- normal, no escaping
- **Inside a VARCHAR string in `$$` body:** `''value''` -- doubled
- **Inside a VARCHAR inside another VARCHAR:** `''''value''''` -- quadrupled

Avoid going beyond two levels. Refactor into multiple statements or use bind variables instead.

## Exception Handling in Stored Procedures

### EXCEPTION Block Pattern

Use EXCEPTION blocks within BEGIN...END to catch and handle errors in SQL stored procedures:

```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.safe_data_load(
    source_table VARCHAR,
    target_table VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
COMMENT = 'Load data with error handling'
AS
$$
DECLARE
    row_count INTEGER;
    err_msg VARCHAR;
BEGIN
    MERGE INTO my_db.my_schema.target_data t
    USING my_db.my_schema.source_data s
        ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET t.value = s.value
    WHEN NOT MATCHED THEN INSERT (id, value) VALUES (s.id, s.value);

    row_count := SQLROWCOUNT;
    RETURN 'Success: ' || :row_count || ' rows merged';

EXCEPTION
    WHEN statement_error THEN
        -- SQLCODE contains the error number, SQLERRM contains the message
        err_msg := 'Statement error ' || SQLCODE || ': ' || SQLERRM;
        INSERT INTO my_db.my_schema.error_log (proc_name, error_message, error_time)
        VALUES ('safe_data_load', :err_msg, CURRENT_TIMESTAMP());
        RETURN :err_msg;
    WHEN other THEN
        -- Catch-all for any other exception
        err_msg := 'Unexpected error ' || SQLCODE || ': ' || SQLERRM;
        INSERT INTO my_db.my_schema.error_log (proc_name, error_message, error_time)
        VALUES ('safe_data_load', :err_msg, CURRENT_TIMESTAMP());
        RAISE;  -- Re-raise after logging
END;
$$;
```

**Key EXCEPTION handlers:**
- `WHEN statement_error THEN` -- catches SQL statement execution errors
- `WHEN expression_error THEN` -- catches expression evaluation errors
- `WHEN other THEN` -- catch-all for any unhandled exception
- `SQLCODE` -- numeric error code
- `SQLERRM` -- error message text
- `RAISE` -- re-raise the current exception after handling

## Procedure and UDF Structure Templates

### Stored Procedure Template

```sql
CREATE OR REPLACE PROCEDURE <database>.<schema>.<procedure_name>(
    <param1> <TYPE> [DEFAULT <value>],
    <param2> <TYPE>,
    <output_param> OUT <TYPE>
)
RETURNS <return_type>
LANGUAGE SQL
EXECUTE AS <OWNER | CALLER | RESTRICTED CALLER>
COMMENT = '<Purpose description>'
AS
$$
DECLARE
    -- Variable declarations
    result_var <TYPE>;
BEGIN
    -- Procedure logic
    RETURN result_var;
END;
$$;
```

### UDF Template

```sql
CREATE OR REPLACE FUNCTION <database>.<schema>.<function_name>(
    <param1> <TYPE>,
    <param2> <TYPE>
)
RETURNS <return_type>
LANGUAGE SQL
COMMENT = '<Purpose description>'
AS
$$
    SELECT <expression>
$$;
```

**Note:** UDFs do not support EXECUTE AS -- they always run with the caller's context for SQL UDFs.

### Table Function (UDTF) Template

```sql
CREATE OR REPLACE FUNCTION <database>.<schema>.<function_name>(
    <param1> <TYPE>
)
RETURNS TABLE (<col1> <TYPE>, <col2> <TYPE>)
LANGUAGE SQL
COMMENT = '<Purpose description>'
AS
$$
    SELECT col1, col2
    FROM <database>.<schema>.<source_table>
    WHERE <condition>
$$;
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Single-Quote Delimiters for Bodies with Strings

**Problem:**
```sql
-- Quoting nightmare: every internal quote must be escaped
CREATE OR REPLACE PROCEDURE my_db.my_schema.log_event(event_name VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
AS
'
BEGIN
    INSERT INTO my_db.my_schema.audit_log (event, message)
    VALUES (:event_name, ''Event processed at '' || CURRENT_TIMESTAMP()::VARCHAR);
    RETURN ''Done'';
END;
';
```

**Why It Fails:** Every single quote inside the body must be doubled. As procedures grow, this becomes unreadable and error-prone. Adding a new string literal requires finding and escaping quotes correctly. Debugging is difficult because the visual noise obscures the actual SQL logic.

**Correct Pattern:**
```sql
-- Clean: $$ eliminates all escaping
CREATE OR REPLACE PROCEDURE my_db.my_schema.log_event(event_name VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
BEGIN
    INSERT INTO my_db.my_schema.audit_log (event, message)
    VALUES (:event_name, 'Event processed at ' || CURRENT_TIMESTAMP()::VARCHAR);
    RETURN 'Done';
END;
$$;
```

**Benefits:** Readable body; no escaping needed for string literals; easier maintenance; standard practice.

### Anti-Pattern 2: Omitting EXECUTE AS (Silent Default to OWNER)

**Problem:**
```sql
-- No EXECUTE AS specified: silently defaults to OWNER
CREATE OR REPLACE PROCEDURE my_db.my_schema.check_access()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Developer expects this to run as CALLER but it runs as OWNER
    -- Session variables are inaccessible, caller permissions ignored
    RETURN CURRENT_ROLE();
END;
$$;
```

**Why It Fails:** The default is OWNER, which means the procedure runs with the creating role's privileges. If the developer intended CALLER rights (to respect the calling user's permissions or access session variables), the procedure silently does the wrong thing. This is a common source of security and permission bugs.

**Correct Pattern:**
```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.check_access()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
COMMENT = 'Returns the current role of the calling user'
AS
$$
BEGIN
    RETURN CURRENT_ROLE();
END;
$$;
```

**Benefits:** Intent is explicit; no ambiguity about security context; easier code review; prevents privilege surprises.

### Anti-Pattern 3: String Concatenation Instead of Bind Variables

**Problem:**
```sql
AS
$$
DECLARE
    query VARCHAR;
    rs RESULTSET;
BEGIN
    -- SQL injection risk: region_param is concatenated directly
    query := 'SELECT * FROM my_db.my_schema.orders WHERE region = ''' || :region_param || '''';
    rs := (EXECUTE IMMEDIATE :query);
    RETURN TABLE(rs);
END;
$$;
```

**Why It Fails:** Direct string concatenation allows SQL injection if the parameter contains malicious input (e.g., `' OR 1=1 --`). It also introduces nested quoting complexity that makes the code fragile and hard to read.

**Correct Pattern:**
```sql
AS
$$
DECLARE
    query VARCHAR DEFAULT 'SELECT * FROM my_db.my_schema.orders WHERE region = ?';
    rs RESULTSET;
BEGIN
    rs := (EXECUTE IMMEDIATE :query USING (:region_param));
    RETURN TABLE(rs);
END;
$$;
```

**Benefits:** Prevents SQL injection; eliminates nested quoting; cleaner code; better performance (Snowflake can cache the query plan).

### Anti-Pattern 4: Literal `$$` Inside a Dollar-Quoted Body

**Problem:**
```sql
AS
$$
BEGIN
    -- This terminates the body prematurely!
    RETURN 'The delimiter is $$';
END;
$$;
```

**Why It Fails:** The `$$` inside the string literal is interpreted as the closing delimiter for the procedure body. Everything after it becomes a syntax error. This is the one limitation of dollar-quoting.

**Correct Pattern:**
```sql
AS
$$
DECLARE
    result VARCHAR;
BEGIN
    result := '$' || '$';
    RETURN 'The delimiter is ' || :result;
END;
$$;
```

**Benefits:** Avoids premature body termination; works correctly; clear intent.

### Anti-Pattern 5: Unqualified Object Names Inside Procedure Bodies

**Problem:**
```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.refresh_summary()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
BEGIN
    -- Relies on session context for object resolution
    TRUNCATE TABLE summary_table;
    INSERT INTO summary_table SELECT * FROM source_table;
    RETURN 'Refreshed';
END;
$$;
```

**Why It Fails:** When the procedure is called from a different database or schema context, `summary_table` and `source_table` resolve to the caller's current schema (for CALLER) or may fail entirely. This makes the procedure fragile and non-portable.

**Correct Pattern:**
```sql
CREATE OR REPLACE PROCEDURE my_db.my_schema.refresh_summary()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
COMMENT = 'Truncate and reload the summary table from source'
AS
$$
BEGIN
    TRUNCATE TABLE my_db.my_schema.summary_table;
    INSERT INTO my_db.my_schema.summary_table
    SELECT * FROM my_db.my_schema.source_table;
    RETURN 'Refreshed';
END;
$$;
```

**Benefits:** Works from any calling context regardless of the caller's current database or schema; no silent wrong-table bugs; fully portable.
