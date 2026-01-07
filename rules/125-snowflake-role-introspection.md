# 125-snowflake-role-introspection: Snowflake Role Introspection

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** account roles, database roles, SHOW GRANTS, role introspection, RBAC, Python automation, error 000906, too many qualifiers, grants inspection, programmatic RBAC
**TokenBudget:** ~2100
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

- Detect role type by checking for `.` in role name
- Use `SHOW GRANTS TO ROLE` for account roles
- Use `SHOW GRANTS TO DATABASE ROLE` for database roles
- Handle SQL compilation error 000906

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

# Fails with: ProgrammingError: 000906 (42000): SQL compilation error:
# role identifier 'SNOWFLAKE.CORTEX_USER' has too many qualifiers
```
**Problem:** Database roles have qualifiers (dots) and require different syntax; script crashes when encountering `SNOWFLAKE.CORTEX_USER`, `DB.SCHEMA.ROLE`, or other database roles

**Correct Pattern:**
```python
# Good: Detects role type and uses correct syntax
def get_role_grants(role_name):
    if '.' in role_name:
        # Database role: use DATABASE ROLE syntax
        return execute_query(f"SHOW GRANTS TO DATABASE ROLE {role_name}")
    else:
        # Account role: use standard ROLE syntax
        return execute_query(f"SHOW GRANTS TO ROLE {role_name}")
```
**Benefits:** Handles both account roles (`ACCOUNTADMIN`, `PUBLIC`) and database roles (`SNOWFLAKE.CORTEX_USER`) correctly; no SQL compilation errors; works across all role types

**Anti-Pattern 2: Hard-Coding Role Type Assumptions**
```python
# Bad: Hard-codes assumptions about which roles are database roles
def get_role_grants(role_name):
    if role_name.startswith('SNOWFLAKE.'):
        return execute_query(f"SHOW GRANTS TO DATABASE ROLE {role_name}")
    else:
        return execute_query(f"SHOW GRANTS TO ROLE {role_name}")

# Fails for custom database roles like MYDB.PUBLIC.CUSTOM_ROLE
```
**Problem:** Only handles `SNOWFLAKE.*` database roles; misses custom database roles in user databases; brittle logic tied to specific naming patterns

**Correct Pattern:**
```python
# Good: Generic detection based on qualification structure
def get_role_grants(role_name):
    """Get grants for any role type (account or database)."""
    # Database roles have format: DB.SCHEMA.ROLE or SNOWFLAKE.ROLE
    # Account roles are unqualified: ACCOUNTADMIN, PUBLIC, etc.
    if '.' in role_name:
        query = f"SHOW GRANTS TO DATABASE ROLE {role_name}"
    else:
        query = f"SHOW GRANTS TO ROLE {role_name}"

    return execute_query(query)
```
**Benefits:** Works for all database role patterns (`SNOWFLAKE.CORTEX_USER`, `MYDB.PUBLIC.CUSTOM`, `DB.ROLE`); no hard-coded role names; future-proof against new database role patterns

## Post-Execution Checklist

- [ ] Script handles both account roles and database roles without errors
- [ ] Role type detection logic implemented (check for `.` in name)
- [ ] Correct `SHOW GRANTS` syntax used for each detected type
- [ ] Error handling catches and reports SQL compilation error 000906
- [ ] Test cases verify both account roles (`PUBLIC`, `ACCOUNTADMIN`) and database roles (`SNOWFLAKE.CORTEX_USER`)

## Validation

**Success Checks:**
- Execute `get_role_grants('PUBLIC')` without errors
- Execute `get_role_grants('SNOWFLAKE.CORTEX_USER')` without errors
- Execute `get_role_grants('MYDB.PUBLIC.CUSTOM_ROLE')` without errors
- Verify all return correct grant structures

**Negative Tests:**
- Attempting `SHOW GRANTS TO ROLE SNOWFLAKE.CORTEX_USER` fails with error 000906
- Detection logic correctly identifies `DB.SCHEMA.ROLE` as database role
- Detection logic correctly identifies `ACCOUNTADMIN` as account role

## Output Format Examples

```python
import snowflake.connector

def execute_query(query):
    """Execute SQL and return results (implementation depends on connection setup)."""
    cursor = conn.cursor(snowflake.connector.DictCursor)
    cursor.execute(query)
    return cursor.fetchall()

def get_role_grants(role_name):
    """
    Get grants for a Snowflake role (account or database role).

    Args:
        role_name: Role name (e.g., 'PUBLIC', 'SNOWFLAKE.CORTEX_USER')

    Returns:
        List of grant dictionaries
    """
    if '.' in role_name:
        query = f"SHOW GRANTS TO DATABASE ROLE {role_name}"
    else:
        query = f"SHOW GRANTS TO ROLE {role_name}"

    return execute_query(query)

# Example usage
account_grants = get_role_grants('ACCOUNTADMIN')
db_role_grants = get_role_grants('SNOWFLAKE.CORTEX_USER')
custom_grants = get_role_grants('MYDB.PUBLIC.CUSTOM_ROLE')
```

```python
# Example: Role hierarchy traversal handling both types
def check_role_hierarchy(role_name, visited=None):
    """Recursively check role hierarchy for both account and database roles."""
    if visited is None:
        visited = set()

    if role_name in visited:
        return  # Avoid infinite loops
    visited.add(role_name)

    # Get grants using type-aware function
    grants = get_role_grants(role_name)

    for grant in grants:
        # Check for parent role grants
        if grant.get('granted_on') == 'ROLE':
            parent_role = grant.get('name')
            print(f"{role_name} inherits from {parent_role}")
            # Recursively check parent (may be account or database role)
            check_role_hierarchy(parent_role, visited)
```
