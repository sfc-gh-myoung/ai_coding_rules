**Keywords:** SQL error handling, SnowparkSQLException, error debugging, user inputs, complex joins, error messages, Streamlit errors, Snowflake errors, debug SQL error, fix query error, SQL exception, error troubleshooting, query failed, database error, SQL debugging patterns, exception handling, error recovery, common SQL errors
**TokenBudget:** ~3050
**ContextTier:** Reference
**Depends:** 100-snowflake-core, 101-snowflake-streamlit-core, 101b-snowflake-streamlit-performance

# Streamlit SQL Error Handling: Comprehensive Reference

## Purpose
Provide comprehensive SQL error handling patterns for Streamlit applications including multiple queries, user inputs, complex joins, and debugging techniques.

## Rule Type and Scope
- **Type:** Appendix
- **Scope:** Detailed SQL error handling patterns and examples

## Quick Start
For basic SQL error handling, see 101b-snowflake-streamlit-performance.md Section 3.1.
This appendix provides comprehensive examples for advanced scenarios.

## Contract

- **Inputs/Prereqs:** Snowflake session established; SQL queries to execute; tables/schemas accessible
- **Allowed Tools:** 
  - try/except blocks with SnowparkSQLException
  - st.error() for error display
  - st.warning() for empty results
  - st.info() for query context
  - st.stop() to halt execution
- **Forbidden Tools:**
  - Generic Exception catching without SnowparkSQLException
  - Silent error handling (no user notification)
  - Error messages without query context or error codes
- **Required Steps:**
  1. Wrap every session.sql() call in try/except
  2. Catch SnowparkSQLException before generic Exception
  3. Display error message with st.error() including: error text, error code, table names, operation description, common causes
  4. Call st.stop() to prevent cascading failures
  5. Handle empty DataFrames with st.warning() (yellow) not st.error() (red)
- **Output Format:** Streamlit error messages with full context; stopped execution on SQL failure; empty DataFrame handling
- **Validation Steps:** Verify all SQL queries have error handling; confirm error messages include all required context; test with invalid queries to see error display


**Pattern for Multiple Related Queries:**
```python
def load_dashboard_data():
    """Load all data needed for dashboard with granular error handling."""
    
    # Query 1: Load assets
    try:
        session = get_snowflake_session()
        assets_df = session.sql("""
            SELECT asset_id, asset_type, install_date
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        """).to_pandas()
        assets_df.columns = [col.lower() for col in assets_df.columns]
        
    except SnowparkSQLException as e:
        st.error(f"""
        **Query 1 Failed: Load Grid Assets**
        
        **Error:** {str(e)}
        **Table:** UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Common Causes:**
        - Table GRID_ASSETS does not exist in GRID_DATA schema
        - Missing SELECT permission on GRID_ASSETS
        - UTILITY_DEMO_V2 database or GRID_DATA schema does not exist
        """)
        st.stop()
    
    # Query 2: Load failures
    try:
        failures_df = session.sql("""
            SELECT asset_id, failure_time, failure_reason, repair_cost
            FROM UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS
            WHERE failure_time >= DATEADD(month, -6, CURRENT_DATE())
        """).to_pandas()
        failures_df.columns = [col.lower() for col in failures_df.columns]
        
    except SnowparkSQLException as e:
        st.error(f"""
        **Query 2 Failed: Load Failure Events**
        
        **Error:** {str(e)}
        **Table:** UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS
        **Filter:** Last 6 months of failure events
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Common Causes:**
        - Table FAILURE_EVENTS does not exist in GRID_DATA schema
        - Column failure_time has different name or does not exist
        - Invalid date function (check DATEADD syntax)
        - Missing SELECT permission on FAILURE_EVENTS
        """)
        st.stop()
    
    # Query 3: Aggregate metrics
    try:
        metrics_df = session.sql("""
            SELECT 
                asset_type,
                COUNT(*) as total_assets,
                SUM(CASE WHEN install_date < '2010-01-01' THEN 1 ELSE 0 END) as old_assets
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
            GROUP BY asset_type
        """).to_pandas()
        metrics_df.columns = [col.lower() for col in metrics_df.columns]
        
    except SnowparkSQLException as e:
        st.error(f"""
        **Query 3 Failed: Calculate Asset Metrics**
        
        **Error:** {str(e)}
        **Table:** UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        **Operation:** Aggregate asset counts by type
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Common Causes:**
        - Column asset_type or install_date does not exist
        - Invalid date format in comparison ('2010-01-01')
        - GROUP BY syntax error
        - Insufficient permissions for aggregation
        """)
        st.stop()
    
    return assets_df, failures_df, metrics_df
```

**Key Features:**
- **Numbered queries:** "Query 1", "Query 2", "Query 3" show execution order
- **Specific operation names:** "Load Grid Assets", "Load Failure Events", "Calculate Asset Metrics"
- **Contextual details:** Each error shows relevant table, filters, operations
- **Independent error handling:** Each query has its own try/except block
- **Cascading prevention:** `st.stop()` prevents downstream errors from missing data

### 3.3 Error Handling with User Inputs

**Pattern for Parameterized Queries:**
```python
def load_assets_by_type(asset_type: str):
    """
    Load assets filtered by type with user input validation.
    
    Args:
        asset_type: User-selected asset type (TRANSFORMER, SUBSTATION, etc.)
    """
    try:
        session = get_snowflake_session()
        
        # Show what we're querying
        st.info(f"Loading {asset_type} assets from database...")
        
        query = """
            SELECT asset_id, asset_type, latitude, longitude, install_date
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
            WHERE asset_type = ?
        """
        
        df = session.sql(query, params=[asset_type]).to_pandas()
        df.columns = [col.lower() for col in df.columns]
        
        if df.empty:
            st.warning(f"""
            **No assets found for type: {asset_type}**
            
            This could mean:
            - No assets of this type exist in the database
            - The asset type name is misspelled
            - Data has not been loaded yet
            
            Available asset types can be checked with:
            `SELECT DISTINCT asset_type FROM GRID_ASSETS`
            """)
            return pd.DataFrame()
        
        return df
        
    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_assets_by_type()**
        
        **Error:** {str(e)}
        
        **Query Context:**
        - Table: UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        - Operation: Loading assets by type
        - Filter: asset_type = '{asset_type}'
        - SQL Error Code: {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Possible Causes:**
        - Table GRID_ASSETS does not exist
        - Column asset_type does not exist or has different name
        - Invalid asset type value: '{asset_type}'
        - Missing SELECT permission
        - Database connection lost
        """)
        st.stop()
```

**Key Features:**
- **User context:** Shows the user's input (asset_type) in error message
- **Empty result handling:** Distinguishes between SQL errors and no results found
- **Actionable guidance:** Suggests SQL to check available values
- **st.warning() for empty results:** Uses warning (yellow) vs error (red) for non-error empty results

### 3.4 Error Handling with Complex Joins

**Pattern for Multi-Table Queries:**
```python
def load_failure_analysis():
    """Load failure analysis with asset details (complex join)."""
    try:
        session = get_snowflake_session()
        
        query = """
            SELECT 
                a.asset_id,
                a.asset_type,
                a.install_date,
                f.failure_time,
                f.failure_reason,
                f.repair_cost,
                DATEDIFF(year, a.install_date, f.failure_time) as age_at_failure
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS a
            INNER JOIN UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS f
                ON a.asset_id = f.asset_id
            WHERE f.failure_time >= DATEADD(year, -1, CURRENT_DATE())
            ORDER BY f.failure_time DESC
        """
        
        df = session.sql(query).to_pandas()
        df.columns = [col.lower() for col in df.columns]
        return df
        
    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_failure_analysis()**
        
        **Error:** {str(e)}
        
        **Query Context:**
        - Operation: Join GRID_ASSETS with FAILURE_EVENTS
        - Tables:
          - UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS (alias: a)
          - UTILITY_DEMO_V2.GRID_DATA.FAILURE_EVENTS (alias: f)
        - Join Condition: a.asset_id = f.asset_id
        - Filter: failure_time >= last 1 year
        - SQL Error Code: {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Possible Causes:**
        - One or both tables do not exist
        - Column asset_id does not exist in GRID_ASSETS or FAILURE_EVENTS
        - Columns install_date, failure_time, failure_reason, or repair_cost missing
        - Invalid join condition (check column names match)
        - DATEDIFF function syntax error
        - Missing SELECT permission on one or both tables
        
        **Debugging Steps:**
        1. Verify both tables exist: `SHOW TABLES IN GRID_DATA`
        2. Check GRID_ASSETS columns: `DESC TABLE GRID_ASSETS`
        3. Check FAILURE_EVENTS columns: `DESC TABLE FAILURE_EVENTS`
        4. Test join condition: `SELECT a.asset_id, f.asset_id FROM GRID_ASSETS a, FAILURE_EVENTS f LIMIT 1`
        """)
        st.stop()
```

**Key Features:**
- **Join details:** Shows both tables, aliases, and join condition
- **All context:** Lists every column referenced in the query
- **Debugging steps:** Provides specific SQL commands to diagnose the issue
- **Error code:** Includes Snowflake error code for support tickets

### 3.5 Error Handling Best Practices Checklist

**MANDATORY Checklist for Every SQL Query:**
- [ ] Wrapped in try/except with SnowparkSQLException
- [ ] Error message shows specific query/function name
- [ ] Error message includes full Snowflake error text: `{str(e)}`
- [ ] Error message shows SQL error code: `{e.error_code}`
- [ ] Error message shows table name(s) involved
- [ ] Error message shows operation description
- [ ] Error message lists common causes specific to that query
- [ ] Uses `st.error()` for red box visibility
- [ ] Includes `st.stop()` to prevent cascading failures
- [ ] Generic Exception catch after SnowparkSQLException

**Common SQL Error Codes to Handle:**
- **002003:** SQL compilation error (syntax, missing columns)
- **002043:** Object does not exist (table/schema/database)
- **002001:** SQL access control error (insufficient permissions)
- **090105:** Cannot perform operation (data type mismatch)

**Example with Error Code Guidance:**
```python
except SnowparkSQLException as e:
    error_code = e.error_code if hasattr(e, 'error_code') else None
    
    # Provide specific guidance based on error code
    if error_code == '002043':
        guidance = "The table, schema, or database does not exist. Verify object names are correct."
    elif error_code == '002003':
        guidance = "SQL syntax error or column does not exist. Check column names and SQL syntax."
    elif error_code == '002001':
        guidance = "Insufficient permissions. You need SELECT privilege on this table."
    else:
        guidance = "See full error message above for details."
    
    st.error(f"""
    **SQL Query Failed: {query_name}**
    
    **Error:** {str(e)}
    **SQL Error Code:** {error_code}
    
    **Guidance:** {guidance}
    
    **Query Context:**
    - Table: {table_name}
    - Operation: {operation_description}
    """)
    st.stop()
```

### 3.6 Anti-Pattern: Generic Error Messages

**NEVER DO THIS:**
```python
# BAD: Generic, unhelpful error message
try:
    df = session.sql(query).to_pandas()
except Exception:
    st.error("An error occurred")  # Useless!

# BAD: Missing query context
try:
    df = session.sql(query).to_pandas()
except SnowparkSQLException as e:
    st.error(f"Query failed: {e}")  # Better, but still insufficient
    
# BAD: No error code or context
try:
    df = session.sql(query).to_pandas()
except Exception as e:
    st.error("Database error")  # Doesn't help debug
```

**Why This Is Bad:**
- Can't identify which of multiple queries failed
- Missing SQL error code needed for Snowflake documentation lookup
- No table/schema context to verify object existence
- No actionable guidance on how to fix the issue
- Wastes developer time trying to reproduce and diagnose

**ALWAYS DO THIS:**
```python
# GOOD: Specific, actionable error message
try:
    query = "SELECT * FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS"
    df = session.sql(query).to_pandas()
    df.columns = [col.lower() for col in df.columns]
    
except SnowparkSQLException as e:
    st.error(f"""
    **SQL Query Failed: load_grid_assets()**
    
    **Error:** {str(e)}
    **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
    
    **Query Context:**
    - Table: UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
    - Operation: Loading all grid assets
    
    **Common Causes:**
    - Table does not exist (run setup SQL first)
    - Missing SELECT permission
    - Database/schema does not exist
    """)
    st.stop()
```

**Benefits of Good Error Messages:**
- **Immediate identification:** Know exactly which query failed
- **Full diagnostic info:** Error text + code + context
- **Actionable:** Lists specific things to check/fix
- **Professional:** Shows proper error handling in production apps
- **Debuggable:** Other developers can diagnose without reproducing

## Quick Start TL;DR (Essential Patterns Reference)

**MANDATORY:**
**Essential Patterns:**
- **Wrap all SQL in try/except** - Catch SnowparkSQLException specifically
- **Include error code** - Always show `{e.error_code}` for Snowflake support
- **Show query context** - Table names, operations, filters in every error message
- **List common causes** - Help developers self-diagnose the issue
- **Use st.stop()** - Prevent cascading errors from missing data
- **Number multiple queries** - "Query 1", "Query 2" for easy identification
- **Handle empty results separately** - Use st.warning() vs st.error() for no results

## Validation

- Test SQL error handling with intentionally invalid queries (missing tables, wrong column names, syntax errors)
- Verify error messages display all required context: error code, table names, operation description
- Confirm empty result handling uses st.warning() not st.error()
- Validate multi-query scenarios show which specific query failed
- Check that st.stop() prevents downstream errors when SQL fails
- Ensure parameterized queries show user input values in error messages

## Quick Compliance Checklist

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

## Response Template

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

## References

### Internal Documentation
- **101b-snowflake-streamlit-performance.md:** Performance optimization patterns including basic SQL error handling
- **101-snowflake-streamlit-core.md:** Core Streamlit patterns and st.error(), st.warning(), st.stop() usage
- **100-snowflake-core.md:** Snowflake SQL best practices and query patterns

### External Documentation
- [Snowflake Error Codes Reference](https://docs.snowflake.com/en/user-guide/admin-error-codes.html) - Complete list of SQL error codes
- [Snowpark Python API - Exceptions](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/api/snowflake.snowpark.exceptions.SnowparkSQLException.html) - SnowparkSQLException documentation
- [Streamlit Error Handling](https://docs.streamlit.io/develop/api-reference/status) - st.error(), st.warning(), st.info(), st.stop()
- [Python Exception Handling Best Practices](https://docs.python.org/3/tutorial/errors.html) - General exception handling patterns

