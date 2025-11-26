# Streamlit SQL Error Handling: Comprehensive Reference

## Metadata

**SchemaVersion:** v3.0
**Keywords:** SnowparkSQLException, error messages, Streamlit errors, Snowflake errors, debug SQL error, fix query error, SQL exception, error troubleshooting, query failed, database error, SQL debugging patterns, exception handling, error recovery, common SQL errors
**TokenBudget:** ~1200
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


