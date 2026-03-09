# Snowflake SQL: Stored Procedure Anti-Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** stored procedure anti-patterns, dollar quoting, EXECUTE AS, bind variables, SQL injection, dynamic SQL, unqualified names
**TokenBudget:** ~1700
**ContextTier:** Low
**Depends:** 102b-snowflake-sql-procedures.md

## Scope

**What This Rule Covers:**
Common anti-patterns in Snowflake SQL stored procedures and UDFs: incorrect delimiter usage, missing EXECUTE AS, SQL injection via string concatenation, literal `$$` in bodies, and unqualified object names.

**When to Load This Rule:**
- Reviewing or debugging stored procedures
- Troubleshooting quoting or delimiter errors
- Security review of dynamic SQL in procedures
- Code review for Snowflake procedure best practices

## References

### Dependencies

**Must Load First:**
- **102b-snowflake-sql-procedures.md** - Procedure creation patterns and templates

## Contract

### Inputs and Prerequisites

- Existing stored procedure or UDF code for review
- Understanding of `$$` delimiters and EXECUTE AS model (see 102b)

### Mandatory

- Fix all anti-patterns before deploying procedures to production
- Use `$$` delimiters, explicit EXECUTE AS, and bind variables

### Forbidden

- Deploying procedures with any of the anti-patterns listed below

### Execution Steps

1. Review procedure code against each anti-pattern
2. Fix delimiter issues (single quotes to `$$`)
3. Add explicit EXECUTE AS clause
4. Replace string concatenation with bind variables
5. Fully qualify all object names

### Output Format

Corrected SQL procedure code with anti-patterns resolved.

### Validation

- Procedure creates without syntax errors
- No SQL injection vectors in dynamic SQL
- EXECUTE AS explicitly specified on all procedures

### Post-Execution Checklist

- [ ] No single-quote delimiters on bodies with string literals
- [ ] EXECUTE AS explicitly specified
- [ ] Bind variables used for dynamic SQL values
- [ ] No literal `$$` inside procedure bodies
- [ ] All object names fully qualified

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
