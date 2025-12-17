# Streamlit SQL Error Handling: Comprehensive Reference

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** SnowparkSQLException, error messages, Streamlit errors, Snowflake errors, debug SQL error, fix query error, SQL exception, error troubleshooting, query failed, database error, SQL debugging patterns, exception handling, error recovery, common SQL errors
**TokenBudget:** ~2800
**ContextTier:** Low
**Depends:** rules/100-snowflake-core.md, rules/101-snowflake-streamlit-core.md, rules/101b-snowflake-streamlit-performance.md

## Purpose
Provide comprehensive SQL error handling patterns for Streamlit applications including multiple queries, user inputs, complex joins, and debugging techniques.

## Rule Scope
Detailed SQL error handling patterns and examples

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Wrap all SQL in try/except** - Catch SnowparkSQLException specifically
- **Include error code** - Always show `{e.error_code}` for Snowflake support
- **Show query context** - Table names, operations, filters in every error message
- **List common causes** - Help developers self-diagnose the issue
- **Use st.stop()** - Prevent cascading errors from missing data
- **Number multiple queries** - "Query 1", "Query 2" for easy identification
- **Handle empty results separately** - Use st.warning() vs st.error() for no results

**Pre-Execution Checklist:**
- [ ] Identified all SQL queries that need error handling
- [ ] Confirmed table/schema names exist in Snowflake
- [ ] Reviewed common SQL errors for this data model
- [ ] Planned error messages with adequate context
- [ ] Determined empty result handling strategy

## Contract

<contract>
<inputs_prereqs>
Snowflake session established; SQL queries to execute; tables/schemas accessible
</inputs_prereqs>

<mandatory>
- try/except blocks with SnowparkSQLException
- st.error() for error display
- st.warning() for empty results
- st.info() for query context
- st.stop() to halt execution
</mandatory>

<forbidden>
- Generic Exception catching without SnowparkSQLException
- Silent error handling (no user notification)
- Error messages without query context or error codes
</forbidden>

<steps>
1. Wrap every session.sql() call in try/except
2. Catch SnowparkSQLException before generic Exception
3. Display error message with st.error() including: error text, error code, table names, operation description, common causes
4. Call st.stop() to prevent cascading failures
5. Handle empty DataFrames with st.warning() (yellow) not st.error() (red)
</steps>

<output_format>
Streamlit error messages with full context; stopped execution on SQL failure; empty DataFrame handling
</output_format>

<validation>
Verify all SQL queries have error handling; confirm error messages include all required context; test with invalid queries to see error display
</validation>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Generic Exception Catching Without SnowparkSQLException**
```python
# Bad: Catches all errors without SQL-specific handling
def load_data():
    try:
        df = session.sql("SELECT * FROM ASSETS").to_pandas()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()
```
**Problem:** Loses SQL-specific error information; no error code; can't distinguish SQL errors from network/conversion errors; debugging is difficult

**Correct Pattern:**
```python
# Good: Specific SQL exception handling with context
from snowflake.snowpark.exceptions import SnowparkSQLException

def load_data():
    try:
        df = session.sql("SELECT * FROM ASSETS").to_pandas()
        return df
    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_data()**

        **Error:** {str(e)}
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}

        **Query Context:**
        - Table: ASSETS
        - Operation: Loading all assets

        **Common Causes:**
        - Table does not exist
        - Missing SELECT permission
        - Invalid column names
        """)
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {type(e).__name__}: {e}")
        st.stop()
```
**Benefits:** Clear SQL vs non-SQL errors; error code for support; actionable debugging info; professional error messages


**Anti-Pattern 2: Error Messages Without Query Context**
```python
# Bad: Generic error message - which query failed?
try:
    df1 = session.sql("SELECT * FROM ASSETS").to_pandas()
    df2 = session.sql("SELECT * FROM OUTAGES").to_pandas()
    df3 = session.sql("SELECT * FROM MAINTENANCE").to_pandas()
except SnowparkSQLException as e:
    st.error(f"Database error: {e}")  # Which query?!
    st.stop()
```
**Problem:** When error occurs, impossible to tell which of 3 queries failed; wasted debugging time; no table context; no operation description

**Correct Pattern:**
```python
# Good: Label each query with context
try:
    # Query 1: Assets
    df1 = session.sql("SELECT * FROM ASSETS").to_pandas()
except SnowparkSQLException as e:
    st.error(f"""
    **SQL Query Failed: Query 1 - Load Assets**

    **Error:** {str(e)}
    **Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
    **Table:** ASSETS
    """)
    st.stop()

try:
    # Query 2: Outages
    df2 = session.sql("SELECT * FROM OUTAGES").to_pandas()
except SnowparkSQLException as e:
    st.error(f"""
    **SQL Query Failed: Query 2 - Load Outages**

    **Error:** {str(e)}
    **Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
    **Table:** OUTAGES
    """)
    st.stop()

# ... Query 3 similar pattern
```
**Benefits:** Immediate identification of failing query; table context clear; numbered queries for easy reference; fast debugging


**Anti-Pattern 3: No st.stop() After SQL Errors**
```python
# Bad: Continues execution after SQL failure
try:
    df = session.sql("SELECT * FROM MISSING_TABLE").to_pandas()
except SnowparkSQLException as e:
    st.error(f"Query failed: {e}")
    # Missing st.stop()!

# Code continues executing with df undefined
transformers = df[df['type'] == 'TRANSFORMER']  # NameError!
st.dataframe(transformers)  # Cascading failures
```
**Problem:** Cascading errors from undefined variables; confusing error messages; user sees multiple red boxes; unprofessional UX

**Correct Pattern:**
```python
# Good: Stop execution after SQL error
try:
    df = session.sql("SELECT * FROM ASSETS").to_pandas()
except SnowparkSQLException as e:
    st.error(f"""
    **SQL Query Failed**
    {str(e)}
    """)
    st.stop()  # Halt execution immediately

# Code below only runs if query succeeded
transformers = df[df['type'] == 'TRANSFORMER']
st.dataframe(transformers)
```
**Benefits:** Prevents cascading errors; clean single error message; professional error handling; user knows exactly what failed


**Anti-Pattern 4: Using st.warning() for SQL Errors**
```python
# Bad: Yellow warning for critical SQL failure
try:
    df = session.sql("SELECT * FROM ASSETS").to_pandas()
except SnowparkSQLException as e:
    st.warning(f"Database issue: {e}")  # Wrong severity!
    return pd.DataFrame()  # Returns empty, silently fails
```
**Problem:** SQL failures are critical errors, not warnings; yellow color minimizes severity; returning empty DataFrame hides the problem; user may not notice

**Correct Pattern:**
```python
# Good: Red error for SQL failures, yellow for empty results
try:
    df = session.sql("SELECT * FROM ASSETS").to_pandas()

    # Empty results are warnings (data issue, not failure)
    if df.empty:
        st.warning("""
        **No assets found** matching the filter criteria.

        This could mean:
        - No assets in database yet
        - Filters too restrictive
        - Check date range settings
        """)
        return pd.DataFrame()

    return df

except SnowparkSQLException as e:
    # SQL failures are errors (system issue, critical)
    st.error(f"""
    **SQL Query Failed**

    **Error:** {str(e)}
    **Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
    **Table:** ASSETS
    """)
    st.stop()
```
**Benefits:** Correct severity levels; distinguishes data issues from system failures; user knows difference between "no data" vs "broken query"


**Anti-Pattern 5: Missing Error Codes in Error Messages**
```python
# Bad: No error code for Snowflake support
try:
    df = session.sql("SELECT * FROM ASSETS").to_pandas()
except SnowparkSQLException as e:
    st.error(f"SQL failed: {str(e)}")  # No error code!
    st.stop()
```
**Problem:** Snowflake support requires error codes for diagnosis; error messages are verbose, codes are unique identifiers; difficult to search documentation

**Correct Pattern:**
```python
# Good: Always include error code
try:
    df = session.sql("SELECT * FROM ASSETS").to_pandas()
except SnowparkSQLException as e:
    st.error(f"""
    **SQL Query Failed**

    **Error Message:** {str(e)}
    **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}

    **Table:** ASSETS
    **Operation:** Loading all assets

    **Debugging:**
    Use error code to search Snowflake docs:
    https://docs.snowflake.com/en/user-guide/admin-error-codes.html
    """)
    st.stop()
```
**Benefits:** Error code enables fast Snowflake support lookup; documentation searchable by code; professional error handling; reproducible error reporting

## Post-Execution Checklist

- [ ] All session.sql() calls wrapped in try/except blocks
- [ ] SnowparkSQLException caught before generic Exception
- [ ] Error messages include error code: {e.error_code}
- [ ] Error messages show table names and schemas
- [ ] Error messages describe the operation being attempted
- [ ] Error messages list 3-5 common causes
- [ ] st.error() used for SQL exceptions (red box)
- [ ] st.warning() used for empty results (yellow box)
- [ ] st.stop() called after displaying SQL errors
- [ ] Multi-query functions number queries ("Query 1", "Query 2")
- [ ] Parameterized queries show user input in error context
- [ ] Join queries show both tables and join condition in error message

> **Investigation Required**
> When applying this rule:
> 1. Read existing SQL queries and error handling BEFORE making recommendations
> 2. Verify table names, schema names, and column names match actual Snowflake objects
> 3. Never speculate about error codes or causes without checking actual query context
> 4. Test error messages by intentionally triggering errors (missing tables, wrong columns)
> 5. Make grounded recommendations based on investigated SQL patterns and error scenarios

## Validation

- Test SQL error handling with intentionally invalid queries (missing tables, wrong column names, syntax errors)
- Verify error messages display all required context: error code, table names, operation description
- Confirm empty result handling uses st.warning() not st.error()
- Validate multi-query scenarios show which specific query failed
- Check that st.stop() prevents downstream errors when SQL fails
- Ensure parameterized queries show user input values in error messages

## Output Format Examples

```python
# Complete error handling pattern for Streamlit SQL queries
import streamlit as st
from snowflake.snowpark.exceptions import SnowparkSQLException

def load_data_with_error_handling():
    """Load data with comprehensive error handling."""
    try:
        session = get_snowflake_session()

        query = """
            SELECT asset_id, asset_type, install_date
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
            WHERE install_date >= DATEADD(year, -5, CURRENT_DATE())
        """

        df = session.sql(query).to_pandas()
        df.columns = [col.lower() for col in df.columns]

        if df.empty:
            st.warning("""
            **No assets found** matching the filter criteria (last 5 years).

            This could mean:
            - No assets installed in the last 5 years
            - Data not yet loaded
            - Check available date range with: `SELECT MIN(install_date), MAX(install_date) FROM GRID_ASSETS`
            """)
            return pd.DataFrame()

        return df

    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_data_with_error_handling()**

        **Error:** {str(e)}
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}

        **Query Context:**
        - Table: UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        - Operation: Loading assets from last 5 years
        - Filter: install_date >= 5 years ago

        **Common Causes:**
        - Table GRID_ASSETS does not exist in GRID_DATA schema
        - Column install_date does not exist or has different name
        - Missing SELECT permission on GRID_ASSETS
        - Database UTILITY_DEMO_V2 or schema GRID_DATA does not exist
        - Invalid date function syntax (DATEADD)

        **Debugging Steps:**
        1. Verify table exists: `SHOW TABLES IN UTILITY_DEMO_V2.GRID_DATA`
        2. Check columns: `DESC TABLE UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS`
        3. Test permissions: `SELECT COUNT(*) FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS`
        """)
        st.stop()

    except Exception as e:
        st.error(f"""
        **Unexpected Error: load_data_with_error_handling()**

        **Error:** {str(e)}

        This is not a SQL error. Possible causes:
        - Snowflake session not established
        - Network connectivity issue
        - Pandas conversion error
        """)
        st.stop()
```

## Connection Error Handling in Streamlit

For connection-level errors (authentication, network policy, VPN issues), see `100f-snowflake-connection-errors.md` for classification logic. This section covers Streamlit-specific presentation.

### Connection Error UI Pattern

```python
from snowflake.connector.errors import DatabaseError
import streamlit as st
import time

# Import classification from 100f patterns
from snowflake_error_utils import classify_snowflake_connection_error, SnowflakeErrorType

def handle_connection_error(error: DatabaseError):
    """
    Handle connection errors with Streamlit-specific UI.
    
    Uses classification from 100f-snowflake-connection-errors.md
    and presents with Streamlit widgets.
    """
    error_msg = str(error)
    error_code = error.errno if hasattr(error, 'errno') else ""
    
    error_type, guidance = classify_snowflake_connection_error(error_msg, str(error_code))
    
    if error_type == SnowflakeErrorType.NETWORK_POLICY:
        # VPN disconnection - auto-retry with UI feedback
        with st.expander("🌐 Network Policy Violation", expanded=True):
            st.warning(guidance)
            st.info("**Tip:** Reconnect to your VPN and wait 5 seconds")
            
            if st.button("Retry Connection"):
                with st.spinner("Waiting for VPN reconnection..."):
                    time.sleep(5)
                    st.rerun()
    
    elif error_type == SnowflakeErrorType.AUTH_EXPIRED:
        # Authentication expired - show command to run
        with st.expander("🔐 Authentication Expired", expanded=True):
            st.error(guidance)
            st.code("snow connection test", language="bash")
            st.info("After running the command, refresh this page")
            
            if st.button("I've refreshed auth - Retry"):
                st.rerun()
    
    elif error_type == SnowflakeErrorType.TRANSIENT:
        # Transient error - auto-retry with backoff
        st.warning(guidance)
        with st.spinner("Retrying connection..."):
            time.sleep(2)
            st.rerun()
    
    else:
        # Generic connection error
        with st.expander("🔌 Connection Error", expanded=True):
            st.error(guidance)
            st.code(error_msg, language="text")
            
            if st.button("Retry Connection"):
                st.rerun()
```

### Auto-Retry with Exponential Backoff

```python
import time
from typing import Optional

def connect_with_retry(
    connection_params: dict,
    max_retries: int = 3,
    base_delay: float = 2.0
) -> Optional[object]:
    """
    Attempt Snowflake connection with exponential backoff.
    
    Shows progress in Streamlit UI.
    """
    for attempt in range(max_retries):
        try:
            conn = snowflake.connector.connect(**connection_params)
            st.success(f"✅ Connected on attempt {attempt + 1}")
            return conn
            
        except DatabaseError as e:
            error_type, guidance = classify_snowflake_connection_error(str(e), str(e.errno))
            
            # Don't retry auth errors (user action required)
            if error_type == SnowflakeErrorType.AUTH_EXPIRED:
                st.error(guidance)
                return None
            
            # Don't retry network policy errors initially (VPN reconnect needed)
            if error_type == SnowflakeErrorType.NETWORK_POLICY and attempt == 0:
                st.warning(guidance)
                st.info("Waiting for VPN reconnection...")
                time.sleep(5)  # Give time for VPN to reconnect
            
            # Retry transient errors with backoff
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                st.warning(f"Attempt {attempt + 1} failed. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                st.error(f"❌ Connection failed after {max_retries} attempts")
                st.error(guidance)
                return None
    
    return None
```

### Session State Recovery

```python
def ensure_connection():
    """
    Ensure Snowflake connection exists in session state.
    
    Creates new connection if needed, with error handling.
    """
    if 'snowflake_session' not in st.session_state:
        try:
            st.session_state.snowflake_session = snowflake.connector.connect(
                connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME")
            )
        except DatabaseError as e:
            handle_connection_error(e)
            st.stop()
    
    return st.session_state.snowflake_session
```

## References

### Internal Documentation
- **100f-snowflake-connection-errors.md:** Connection error classification logic (network policy vs auth vs connection)
- **101b-snowflake-streamlit-performance.md:** Performance optimization patterns including basic SQL error handling
- **101-snowflake-streamlit-core.md:** Core Streamlit patterns and st.error(), st.warning(), st.stop() usage
- **100-snowflake-core.md:** Snowflake SQL best practices and query patterns

### External Documentation
- [Snowflake Error Codes Reference](https://docs.snowflake.com/en/user-guide/admin-error-codes.html) - Complete list of SQL error codes
- [Snowpark Python API - Exceptions](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/api/snowflake.snowpark.exceptions.SnowparkSQLException.html) - SnowparkSQLException documentation
- [Streamlit Error Handling](https://docs.streamlit.io/develop/api-reference/status) - st.error(), st.warning(), st.info(), st.stop()
- [Python Exception Handling Best Practices](https://docs.python.org/3/tutorial/errors.html) - General exception handling patterns
