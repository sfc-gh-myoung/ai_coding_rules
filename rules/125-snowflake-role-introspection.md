# 125-snowflake-role-introspection: Snowflake Role Introspection

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:role, kw:introspection, kw:access
**Keywords:** account roles, database roles, SHOW GRANTS, role introspection, RBAC, Python automation, error 000906, too many qualifiers, grants inspection, programmatic RBAC
**TokenBudget:** ~1850
**ContextTier:** Medium
**Depends:** 000-global-core.md, 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Patterns for programmatically inspecting Snowflake roles and grants, handling both account-scoped roles and database roles to avoid SQL compilation errors when automating RBAC audits and permission checks. Covers role type detection, syntax differences, error handling (000906), and Python automation patterns.

**When to Load This Rule:**
- Writing Python scripts or Jupyter notebooks that introspect roles
- Automating RBAC audits and permission checks
- Encountering SQL compilation error 000906 ("too many qualifiers")
- Building tools that need to distinguish account roles from database roles
- Troubleshooting `SHOW GRANTS` failures

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Core foundation patterns
- **100-snowflake-core.md** - Snowflake foundation patterns

**Related:**
- **107-snowflake-security-governance.md** - RBAC and privilege patterns
- **200-python-core.md** - Python development patterns

### External Documentation

- [SHOW GRANTS](https://docs.snowflake.com/en/sql-reference/sql/show-grants) - Grant inspection syntax
- [Database Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#database-roles) - Database role concepts
- [Account Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#account-roles) - Account role concepts

## Contract

### Inputs and Prerequisites

- Access to Snowflake account
- Roles with SHOW GRANTS privileges
- Understanding of account vs database role distinction
- `snowflake-connector-python` or equivalent

### Mandatory

- Detect role type by checking for `.` in role name (after stripping outer quotes)
- Use `SHOW GRANTS TO ROLE` for account roles
- Use `SHOW GRANTS TO DATABASE ROLE` for database roles
- Handle SQL compilation error 000906
- Handle quoted identifiers containing dots (e.g., `"my.role"` is an account role)

### Forbidden

- Using `SHOW GRANTS TO ROLE` for database roles
- Assuming all roles are account-scoped
- Ignoring role name qualifiers (dots)

### Execution Steps

1. Extract role name from query result or user input
2. Detect if role is database role by checking for `.` character in name
3. Construct appropriate `SHOW GRANTS` command based on role type
4. Execute command and handle results
5. Validate results include expected grant structure

### Output Format

Python functions produce:
- Lists of grants for both role types
- Transparent handling of account and database roles
- Proper error handling for SQL compilation errors

### Validation

**Pre-Task-Completion Checks:**
- Script distinguishes between account roles and database roles
- Role name qualification detection implemented (check for `.`)
- Correct `SHOW GRANTS` syntax used for each role type
- Error handling catches SQL compilation error 000906

**Success Criteria:**
- Test with account roles (`ACCOUNTADMIN`, `PUBLIC`) succeeds
- Test with database roles (`SNOWFLAKE.CORTEX_USER`, `DB.SCHEMA.ROLE`) succeeds
- No SQL compilation errors
- Expected grant structure returned

**Negative Tests:**
- Invalid role names fail gracefully
- Error 000906 handled correctly

### Design Principles

- **Type detection:** Distinguish account roles from database roles by checking for qualifiers
- **Correct syntax:** Use appropriate `SHOW GRANTS` syntax for each role type
- **Error handling:** Catch and handle SQL compilation error 000906
- **Transparency:** Functions handle both role types seamlessly

### Post-Execution Checklist

- [ ] Script distinguishes between account roles and database roles
- [ ] Role name qualification detection implemented (check for `.` character)
- [ ] Correct `SHOW GRANTS` syntax used for each role type
- [ ] Error handling catches SQL compilation error 000906
- [ ] Test cases include both account roles and database roles
- [ ] Script tested with production role names

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Account Role Syntax for All Roles**
```python
# Bad: Assumes all roles are account-scoped
def get_role_grants(role_name):
    return execute_query(f"SHOW GRANTS TO ROLE {role_name}")
# Fails for database roles like SNOWFLAKE.CORTEX_USER
```
**Problem:** Database roles have qualifiers (dots) and require different syntax; script crashes with error 000906

**Correct Pattern:** See canonical `get_role_grants()` in Output Format Examples section.

**Anti-Pattern 2: Hard-Coding Role Type Assumptions**
```python
# Bad: Only handles SNOWFLAKE.* database roles
def get_role_grants(role_name):
    if role_name.startswith('SNOWFLAKE.'):
        return execute_query(f"SHOW GRANTS TO DATABASE ROLE {role_name}")
    return execute_query(f"SHOW GRANTS TO ROLE {role_name}")
# Misses custom database roles like MYDB.PUBLIC.CUSTOM_ROLE
```
**Problem:** Only handles `SNOWFLAKE.*` database roles; misses custom database roles in user databases

**Correct Pattern:** Use generic dot detection after stripping quotes:
```python
def is_database_role(role_name):
    if role_name.startswith('"') and role_name.endswith('"'):
        return False
    return '.' in role_name.strip('"')
```

## Output Format Examples

```python
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

def execute_query(cursor, query):
    """Execute SQL and return results."""
    cursor.execute(query)
    return cursor.fetchall()

def is_database_role(role_name):
    """Detect if role is a database role by checking for dots outside quotes.
    
    Quoted identifiers like '"my.dotted.role"' are account roles despite containing dots.
    """
    stripped = role_name.strip('"')
    # If the original had outer quotes and stripping removed them, it's a quoted account role
    if role_name.startswith('"') and role_name.endswith('"'):
        return False
    return '.' in stripped

def get_role_grants(cursor, role_name):
    """Get grants for a Snowflake role (account or database role).
    
    Handles quoted identifiers, database roles, and error 000906.
    Role names should come from trusted sources (SHOW ROLES output).
    
    Args:
        cursor: Snowflake cursor (DictCursor recommended)
        role_name: Role name (e.g., 'PUBLIC', 'SNOWFLAKE.CORTEX_USER', '"my.role"')
    Returns:
        List of grant dictionaries
    """
    try:
        if is_database_role(role_name):
            query = f"SHOW GRANTS TO DATABASE ROLE {role_name}"
        else:
            query = f"SHOW GRANTS TO ROLE {role_name}"
        return execute_query(cursor, query)
    except ProgrammingError as e:
        if '000906' in str(e):
            # Retry with opposite syntax
            alt_query = (f"SHOW GRANTS TO ROLE {role_name}" 
                        if is_database_role(role_name)
                        else f"SHOW GRANTS TO DATABASE ROLE {role_name}")
            return execute_query(cursor, alt_query)
        raise

# Usage — role names should come from SHOW ROLES (trusted source)
conn = snowflake.connector.connect(...)
cur = conn.cursor(snowflake.connector.DictCursor)

account_grants = get_role_grants(cur, 'ACCOUNTADMIN')
db_role_grants = get_role_grants(cur, 'SNOWFLAKE.CORTEX_USER')
quoted_grants = get_role_grants(cur, '"my.dotted.role"')  # Account role despite dots
```

**Security Note:** The `role_name` parameter uses f-strings in SHOW GRANTS commands. Ensure role names come from trusted sources (e.g., `SHOW ROLES` output) rather than untrusted user input. For user-provided names, validate against the output of `SHOW ROLES` before use.
