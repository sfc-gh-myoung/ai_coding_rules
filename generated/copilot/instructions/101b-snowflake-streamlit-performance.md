---
appliesTo:
  - "**/*.py"
  - "streamlit/**/*"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Streamlit performance, @st.cache_data, @st.cache_resource, data loading, query optimization, SQL error handling, st.error, SnowparkSQLException, progress tracking, st.fragment, NULL handling
**TokenBudget:** ~6600
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core, 103-snowflake-performance-tuning

# Streamlit Performance: Caching and Optimization

## Purpose
Provide comprehensive guidance for optimizing Streamlit application performance through caching strategies, efficient data loading from Snowflake, SQL error handling with detailed debugging information, progress indicators, and performance profiling.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Streamlit performance optimization, caching patterns, Snowflake data loading, SQL error handling and debugging, progress indicators

## Contract

**MANDATORY:**
- **Inputs/Prereqs:** Streamlit app configured (see 101-snowflake-streamlit-core.md), Snowflake connection established, pandas/polars for data manipulation
- **Allowed Tools:** @st.cache_data, @st.cache_resource, st.spinner(), st.progress(), st.status(), Snowflake session.table(), session.sql()

**FORBIDDEN:**
- **Forbidden Tools:** Raw SQL loops without aggregation, redundant database connections, unoptimized queries without LIMIT or WHERE clauses, operations without user feedback

**MANDATORY:**
- **Required Steps:**
  1. Cache database queries with @st.cache_data and appropriate ttl
  2. Cache connections and expensive objects with @st.cache_resource
  3. Normalize Snowflake column names to lowercase immediately after loading
  4. Wrap all SQL queries in try/except blocks with detailed error messages using st.error()
  5. Show user feedback for operations >2s (st.spinner) or >5s (st.progress + st.status)
  6. Avoid raw database query loops; fetch all needed data at once
  7. Profile performance and target <2s load time
- **Output Format:** Optimized Streamlit app with <2s initial load, cached data operations, normalized column names, comprehensive SQL error handling with red st.error() boxes, appropriate progress indicators
- **Validation Steps:** Test cache behavior, verify column name normalization, test SQL error handling with invalid queries, measure load time, validate progress indicators show for long operations

## Key Principles
- **Cache Aggressively:** Use @st.cache_data for queries, @st.cache_resource for connections
- **Normalize Early:** Convert Snowflake UPPERCASE column names to lowercase immediately
- **Error Visibility:** Wrap all SQL queries in try/except with detailed st.error() messages showing which query failed and why
- **Fetch Once:** Avoid query loops; aggregate in SQL and fetch once
- **User Feedback:** Show progress for operations >2 seconds
- **Profile Always:** Target <2s load time, measure and optimize

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Cache database queries:** `@st.cache_data(ttl=300)` for query results
- **Cache connections:** `@st.cache_resource` for database connections/expensive objects
- **Normalize columns immediately:** `df.columns = df.columns.str.lower()` after Snowflake fetch
- **Wrap SQL in try/except:** Use `st.error()` with specific query name, full error message, table names, and error code
- **Show progress:** Use `st.spinner()` for ops >2s, `st.progress()+st.status()` for >5s
- **Fetch once:** Aggregate in SQL, avoid query loops (use WHERE, GROUP BY, LIMIT)
- **Target <2s load time:** Profile with Chrome DevTools, optimize slowest queries
- **Never run query loops** - fetch all data at once with aggregation

**Quick Checklist:**
- [ ] Add `@st.cache_data(ttl=...)` to query functions
- [ ] Add `@st.cache_resource` to connection functions
- [ ] Normalize column names: `df.columns = df.columns.str.lower()`
- [ ] Wrap all SQL queries in try/except with SnowparkSQLException
- [ ] Error messages show query name, full error, table name, and error code
- [ ] Add progress indicators for operations >2 seconds
- [ ] Verify queries use WHERE/LIMIT clauses
- [ ] Test cache behavior with different inputs
- [ ] Test SQL error handling with invalid query
- [ ] Measure load time (<2s target)

## 1. Caching Strategies


**MANDATORY:**
**Cache database queries and data fetches with @st.cache_data:**
- **Use Case:** Query results, dataframes, computed data
- **Parameters:** `ttl` (time-to-live) for cache expiration
- **Behavior:** Cached per unique set of input parameters

```python
import streamlit as st
import pandas as pd

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_grid_assets() -> pd.DataFrame:
    """Load grid assets from Snowflake with normalized column names."""
    session = get_snowflake_session()
    df = session.table('UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS').to_pandas()
    
    # CRITICAL: Normalize column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    return df

# First call: executes query
assets = load_grid_assets()  # Hits database

# Subsequent calls within ttl: returns cached result
assets = load_grid_assets()  # Returns cache (fast!)
```

**Cache expensive objects and connections with @st.cache_resource:**
- **Use Case:** Database connections, ML models, large objects
- **Parameters:** No ttl (persists for session lifetime)
- **Behavior:** Shared across all users and reruns

```python
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session() -> Session:
    """Create and cache Snowflake connection."""
    return Session.builder.configs(st.secrets["snowflake"]).create()

# First call: creates connection
session = get_snowflake_session()  # Creates new session

# Subsequent calls: reuses connection
session = get_snowflake_session()  # Reuses cached session
```

**Cache Comparison:**
| Feature | @st.cache_data | @st.cache_resource |
|---------|----------------|---------------------|
| **Use Case** | Data, query results | Connections, models |
| **TTL Support** | Yes (recommended) | No (session lifetime) |
| **Serialization** | Pickled | Stored as-is |
| **Thread Safety** | Yes | No (use with caution) |

### Caching with NULL-Safe Data

**Rule**: Validate cached data doesn't contain unexpected NaN values that cause display errors:

```python
import pandas as pd

@st.cache_data(ttl=300)
def load_metrics():
    """Load KPI metrics from Snowflake with NULL-safe handling."""
    session = get_snowflake_session()
    df = session.sql("SELECT metric_name, value FROM kpis").to_pandas()
    
    # Validate no critical NaN values before caching
    if df["value"].isna().any():
        st.warning("Some metrics unavailable - showing cached values where possible")
    
    return df

# Use cached data with NULL-safe display
metrics_df = load_metrics()
for _, row in metrics_df.iterrows():
    value = row["value"]
    if pd.notna(value):
        st.metric(row["metric_name"], f"{value:.2f}")
    else:
        st.metric(row["metric_name"], "N/A")
```

**Performance Note**: Validating for NaN in cached data prevents expensive re-computation when display errors occur. Using `pd.notna()` instead of `is not None` correctly handles Snowflake NULL values that become pandas NaN.

**Why This Matters:**
- Snowflake NULL → pandas NaN (not Python None)
- Standard Python checks (`is not None`) don't catch NaN
- Format strings (`.1f`, `.0f`) crash on NaN values
- Cached NaN values persist and cause repeated errors

## 2. Data Loading from Snowflake - Critical Column Name Normalization


**MANDATORY:**
**Column Name Normalization (CRITICAL):**
- **Critical:** Snowflake returns column names in **UPPERCASE** by default, which causes `KeyError` when accessing with lowercase
- **Always:** Normalize column names to lowercase immediately after loading data from Snowflake
- **Rule:** Apply normalization in data loader functions, not in UI code, to ensure consistency

**Problem:**
```python
# This will fail with KeyError: 'asset_type'
df = session.table('GRID_ASSETS').to_pandas()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```

**Solution:**
```python
# CORRECT - Normalize column names to lowercase
df = session.table('UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS').to_pandas()
df.columns = [col.lower() for col in df.columns]  # Critical!
transformers = df[df['asset_type'] == 'TRANSFORMER']  # Works!
```

**Best Practices for Data Loaders:**
```python
@st.cache_data(ttl=600)
def load_grid_assets() -> pd.DataFrame:
    """
    Load grid assets from Snowflake.
    
    Returns:
        DataFrame with lowercase column names for Python consistency
    """
    session = get_snowflake_session()
    df = session.table('UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS').to_pandas()
    
    # Normalize to lowercase for consistency
    df.columns = [col.lower() for col in df.columns]
    
    return df
```

**MANDATORY:**
- **Always:** Use fully qualified table names (`DATABASE.SCHEMA.TABLE`) to avoid context issues
- **Always:** Apply normalization to both `session.table().to_pandas()` and `session.sql(query).to_pandas()` results
- **Rule:** Document this normalization in function docstrings to inform other developers

**Why This Matters:**
- **Consistency:** Python code conventionally uses lowercase for column names (snake_case)
- **Portability:** Local dev environments may use lowercase; Snowflake uses uppercase
- **Error Prevention:** Prevents `KeyError` exceptions that are hard to debug in production
- **Best Practice:** Single normalization point in data loaders vs. scattered `.upper()` calls in UI code

## 3. SQL Error Handling and Debugging


**MANDATORY:**
**Show specific error messages that identify which query failed and why:**
- **Always:** Wrap SQL queries in try/except blocks with descriptive context
- **Always:** Display SQL errors using `st.error()` with red styling
- **Always:** Include the full SQL error message and query context
- **Always:** Identify which specific query/operation failed
- **Never:** Show generic error messages that don't help debugging

**Critical Rule:** Every SQL query must have error handling that shows:
1. Which query failed (descriptive name/purpose)
2. The full SQL error message from Snowflake
3. Relevant context (table names, filters, parameters)

### 3.1 Basic SQL Error Handling Pattern

**Standard Pattern:**
```python
import streamlit as st
from snowflake.snowpark.exceptions import SnowparkSQLException

@st.cache_data(ttl=600)
def load_grid_assets():
    """Load grid assets from Snowflake with comprehensive error handling."""
    try:
        session = get_snowflake_session()
        query = """
            SELECT asset_id, asset_type, latitude, longitude, install_date
            FROM UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
            WHERE asset_type IN ('TRANSFORMER', 'SUBSTATION')
        """
        df = session.sql(query).to_pandas()
        df.columns = [col.lower() for col in df.columns]
        return df
        
    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_grid_assets()**
        
        **Error:** {str(e)}
        
        **Query Context:**
        - Table: UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        - Operation: Loading grid assets (transformers and substations)
        - SQL Error Code: {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Possible Causes:**
        - Table does not exist or has been renamed
        - Missing permissions (SELECT privilege required)
        - Invalid column names in query
        - Database/schema does not exist
        """)
        st.stop()  # Stop execution to prevent cascading errors
        
    except Exception as e:
        st.error(f"""
        **Unexpected Error: load_grid_assets()**
        
        **Error Type:** {type(e).__name__}
        **Error Message:** {str(e)}
        
        **Query Context:**
        - Table: UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS
        - Operation: Loading grid assets
        
        Please contact support if this error persists.
        """)
        st.stop()
```

**Why This Pattern:**
- **Specific identification:** "load_grid_assets()" tells exactly which query failed
- **Full error details:** Shows complete Snowflake error message
- **Context:** Table name, operation description, error code
- **Actionable guidance:** Lists possible causes for common SQL errors
- **Red st.error() box:** Makes errors immediately visible

### 3.2 Error Handling for Multiple Queries

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

## 4. Progress Indicators and User Feedback


**MANDATORY:**
**Show user feedback for operations that may take time:**
- **2-5 seconds:** Use `st.spinner()` with descriptive message
- **>5 seconds:** Use `st.progress()` with `st.status()` for detailed progress tracking

**st.spinner() for Short Operations (2-5s):**
```python
with st.spinner("Loading data from Snowflake..."):
    data = load_data()
st.success(f"Loaded {len(data):,} records successfully!")
```

**st.progress() + st.status() for Long Operations (>5s):**
```python
progress_bar = st.progress(0)
status_text = st.empty()

for i, batch in enumerate(data_batches):
    status_text.text(f"Processing batch {i+1}/{len(data_batches)}...")
    process_batch(batch)
    progress_bar.progress((i + 1) / len(data_batches))

status_text.empty()
progress_bar.empty()
st.success("All batches processed!")
```

### 3.3 Advanced: Real-Time Progress with Fragments

**RECOMMENDED:**
**Use `st.fragment` with `run_every` for automatic polling and real-time progress updates:**
- **Use Case:** Long-running operations (>30s) requiring live progress without user interaction
- **Pattern:** Fragment auto-refreshes every N seconds, polling progress table/API
- **Benefit:** Only fragment reruns (not full app), preserving rest of UI and user interaction state

**When to Use Fragments:**
- Database operations with progress table tracking (Snowflake stored procedures, Cortex AI functions)
- API polling for job status (external services, batch processing)
- Streaming data updates (real-time analytics, monitoring)
- Real-time monitoring dashboards (live metrics, status boards)

**Official Documentation:**
- **API Reference:** https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- **Architecture Guide:** https://docs.streamlit.io/develop/concepts/architecture/fragments

**Complete Working Example (from Call Center Analytics):**

```python
import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor

# ========================================================================
# STREAMLIT FRAGMENT PATTERN: Live Progress Tracking
# ========================================================================
# This pattern implements Streamlit's recommended approach for long-running
# operations with real-time progress updates.
#
# Key Components:
# 1. st.session_state - Persists active operation state across reruns
# 2. @st.fragment(run_every="0.5s") - Auto-refreshing fragment that polls progress
# 3. Conditional rendering - Fragment called outside button's if block
# 4. ThreadPoolExecutor - Non-blocking stored procedure execution
# 5. st.stop() - Halts fragment auto-refresh when operation completes
#
# Why This Works:
# - Button click sets session_state.active_analysis_file
# - Fragment conditionally rendered on EVERY rerun (not just inside if block)
# - Fragment's run_every triggers automatic reruns every 0.5s
# - When complete, fragment clears session state and calls st.stop()
#
# Reference: https://docs.streamlit.io/develop/concepts/architecture/fragments
# ========================================================================

def initialize_analysis_progress(audio_file: str):
    """Initialize progress tracking in database table"""
    session.sql(f"""
        INSERT INTO UTILITY_DEMO_V2.CUSTOMER_DATA.ANALYSIS_PROGRESS 
        (AUDIO_FILE_NAME, STATUS, CURRENT_STEP, TOTAL_STEPS)
        VALUES ('{audio_file}', 'in_progress', 0, 18)
    """).collect()

def call_stored_procedure_async(proc_name: str, *args):
    """Execute stored procedure in background thread"""
    executor = ThreadPoolExecutor(max_workers=1)
    def run_proc():
        return session.call(proc_name, *args)
    return executor.submit(run_proc)

@st.fragment(run_every="0.5s")
def show_analysis_progress_live(audio_file):
    """
    Auto-refreshing fragment that polls ANALYSIS_PROGRESS table.
    
    Fragment Pattern (Streamlit Best Practice):
    - Decorated with @st.fragment(run_every="0.5s") for automatic polling
    - Called conditionally based on st.session_state.active_analysis_file
    - Uses st.stop() to halt auto-refresh when operation completes
    - Clears session state to prevent re-triggering on subsequent reruns
    
    Why This Works:
    - Fragment reruns independently every 0.5s (not entire app)
    - Reads progress from database table updated by stored procedure
    - Displays live updates without blocking main thread
    - Stops cleanly when operation completes (no infinite loops)
    
    Reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
    Pattern: https://docs.streamlit.io/develop/concepts/architecture/fragments
    """
    # Query current progress from database
    progress_result = session.sql(f"""
        SELECT STATUS, CURRENT_STEP, TOTAL_STEPS, STEP_DESCRIPTION, LAST_UPDATED
        FROM UTILITY_DEMO_V2.CUSTOMER_DATA.ANALYSIS_PROGRESS
        WHERE AUDIO_FILE_NAME = '{audio_file}'
        ORDER BY LAST_UPDATED DESC
        LIMIT 1
    """).collect()
    
    if not progress_result:
        st.warning("⏳ Initializing analysis...")
        return
    
    p = progress_result[0].as_dict()
    
    # Show live progress bar and status
    if p["STATUS"] == "in_progress" and p["TOTAL_STEPS"] > 0:
        progress_pct = p["CURRENT_STEP"] / p["TOTAL_STEPS"]
        st.progress(progress_pct, text=f"Step {p['CURRENT_STEP']}/{p['TOTAL_STEPS']}")
        st.info(f"🔄 {p['STEP_DESCRIPTION']}")
        
        # Show elapsed time
        if "analysis_start_time" in st.session_state:
            elapsed = time.time() - st.session_state.analysis_start_time
            st.caption(f"Elapsed: {int(elapsed)}s")
    
    # Stop polling when complete
    if p["STATUS"] in ["completed", "partial", "failed"]:
        if p["STATUS"] == "completed":
            st.success(f"Analysis complete! Processed {p['CURRENT_STEP']}/{p['TOTAL_STEPS']} steps")
        elif p["STATUS"] == "partial":
            st.warning(f"Partial completion: {p['CURRENT_STEP']}/{p['TOTAL_STEPS']} steps")
        else:  # failed
            st.error(f"Analysis failed at step {p['CURRENT_STEP']}: {p['STEP_DESCRIPTION']}")
        
        # Clear session state to stop fragment
        if "active_analysis_file" in st.session_state:
            del st.session_state.active_analysis_file
        if "analysis_in_progress" in st.session_state:
            st.session_state.analysis_in_progress = False
        if "analysis_start_time" in st.session_state:
            del st.session_state.analysis_start_time
        if "analysis_future" in st.session_state:
            del st.session_state.analysis_future
        
        st.stop()  # Stop fragment auto-refresh

# Main app code
st.title("Call Center Analytics")

# CRITICAL: Conditional fragment rendering (outside button block)
# This ensures fragment continues to run on every rerun triggered by run_every
if st.session_state.get("active_analysis_file"):
    st.info(f"Analyzing: {st.session_state.active_analysis_file}")
    show_analysis_progress_live(st.session_state.active_analysis_file)

# Button handler (only runs when button is clicked)
if st.button(
    "🔍 Analyze Transcription",
    type="primary",
    disabled=st.session_state.get("analysis_in_progress", False),
):
    selected_file = "call_de_20250924_003.mp3"
    
    # Set session state to trigger fragment
    st.session_state.active_analysis_file = selected_file
    st.session_state.analysis_in_progress = True
    st.session_state.analysis_start_time = time.time()
    
    # Initialize progress tracking
    with st.spinner("🚀 Launching analysis..."):
        initialize_analysis_progress(selected_file)
        future = call_stored_procedure_async(
            "UTILITY_DEMO_V2.CUSTOMER_DATA.SP_ANALYZE_CALL_TRANSCRIPTION_PROGRESSIVE",
            selected_file,
        )
        st.session_state.analysis_future = future
    
    st.rerun()  # Trigger rerun to show fragment
```

**Fragment Pattern Requirements:**

**MANDATORY:**
- **Session State Persistence:** Store active operation state in `st.session_state` for cross-rerun tracking
- **Conditional Rendering:** Fragment MUST be called outside button's `if` block to persist across reruns
- **Cleanup on Completion:** Clear session state variables when operation completes to stop fragment
- **Use `st.stop()`:** Call `st.stop()` inside fragment to halt auto-refresh when done
- **Read-Only Display:** Fragment body should only contain display elements (no widgets)

**Anti-Patterns and Limitations:**

**Anti-Pattern 1: Creating Fragment Inside Button Block**
```python
if st.button("Start"):
    @st.fragment(run_every="1s")  # Fragment won't persist after button resets
    def show_progress():
        st.write("Progress...")
    show_progress()
```
**Problem:** Button state resets on rerun, fragment disappears after first auto-refresh.

**Correct Pattern:**
```python
# Fragment defined at module level
@st.fragment(run_every="1s")
def show_progress():
    if st.session_state.get("active"):
        st.write("Progress...")

# Conditional rendering based on session state
if st.session_state.get("active"):
    show_progress()

if st.button("Start"):
    st.session_state.active = True
    st.rerun()
```
**Benefits:** Fragment persists across reruns, continues polling until session state cleared.

---

**Anti-Pattern 2: Using Widgets Inside Fragments**
```python
@st.fragment(run_every="1s")
def fragment_with_widgets():
    user_input = st.text_input("Name")  # FORBIDDEN in fragments
    st.write(f"Hello {user_input}")
```
**Problem:** Streamlit explicitly forbids widgets in fragment bodies (design limitation).

**Correct Pattern:**
```python
# Widgets outside fragment
user_input = st.text_input("Name")

@st.fragment(run_every="1s")
def display_only_fragment():
    st.write(f"Hello {user_input}")  # Read-only display OK
```
**Benefits:** Follows Streamlit's fragment constraints, works reliably.

---

**Anti-Pattern 3: No Termination Condition**
```python
@st.fragment(run_every="1s")
def infinite_polling():
    st.write("Polling forever...")  # Never stops
```
**Problem:** Fragment runs indefinitely, wasting resources and degrading UX.

**Correct Pattern:**
```python
@st.fragment(run_every="1s")
def polling_with_termination():
    status = check_operation_status()
    st.write(f"Status: {status}")
    
    if status == "complete":
        del st.session_state.active_operation
        st.stop()  # Halt auto-refresh
```
**Benefits:** Cleans up automatically when operation completes.

**Performance Considerations:**
- **Polling Frequency:** Balance between responsiveness and database load (0.5s-2s typical)
- **Scoped Reruns:** Only fragment reruns, not entire app (preserves user inputs, scroll position)
- **Database Load:** Each auto-refresh queries database; ensure queries are indexed and fast (<100ms)
- **Connection Pooling:** Use Streamlit's `st.connection()` for efficient connection management

## 5. Performance Optimization Patterns

**MANDATORY:**
**Avoid raw database query loops; fetch all needed data at once and cache it:**

**Anti-Pattern:**
```python
# Inefficient: N+1 query problem
for region in regions:
    df = session.sql(f"SELECT * FROM sales WHERE region = '{region}'").to_pandas()
    process(df)
```

**Correct:**
```python
# Efficient: Single query with aggregation
@st.cache_data(ttl=600)
def load_all_sales() -> pd.DataFrame:
    query = """
    SELECT region, product, SUM(amount) as total
    FROM sales
    GROUP BY region, product
    """
    df = session.sql(query).to_pandas()
    df.columns = [col.lower() for col in df.columns]
    return df

df = load_all_sales()  # Single query, cached
```

**Performance Target:**
- **Initial Load:** <2 seconds with cached data
- **Query Execution:** <5s (optimize with Query Profile if slower)
- **Cost:** <$0.10 per query (reference 105-snowflake-cost-governance.md)

## 6. Performance Profiling

**Monitor rerun frequency and identify unnecessary reruns:**
```python
import streamlit as st

# Debug: Log rerun count
if 'rerun_count' not in st.session_state:
    st.session_state.rerun_count = 0
st.session_state.rerun_count += 1

# Display in expander for debugging
with st.expander("Debug Info"):
    st.write(f"Rerun count: {st.session_state.rerun_count}")
```

**RECOMMENDED:**
- **Consider:** Use Python profilers (cProfile, line_profiler) for computational bottlenecks
- **Always:** Test with production-like data volumes during development
- **Requirement:** Use Snowflake Query Profile to validate query performance

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: No caching for expensive operations**
```python
def load_data():
    # Runs every rerun - slow!
    return session.table('LARGE_TABLE').to_pandas()

df = load_data()  # Hits database every time
```
**Problem:** Database queried on every widget interaction

**Correct Pattern:**
```python
@st.cache_data(ttl=600)
def load_data():
    df = session.table('LARGE_TABLE').to_pandas()
    df.columns = [col.lower() for col in df.columns]
    return df

df = load_data()  # Cached, hits database once per ttl
```

**Anti-Pattern 2: Forgetting column normalization**
```python
@st.cache_data(ttl=600)
def load_assets():
    return session.table('ASSETS').to_pandas()

df = load_assets()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```
**Problem:** Snowflake returns UPPERCASE column names; Python expects lowercase

**Correct Pattern:**
```python
@st.cache_data(ttl=600)
def load_assets():
    df = session.table('ASSETS').to_pandas()
    df.columns = [col.lower() for col in df.columns]  # CRITICAL
    return df

df = load_assets()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # Works!
```

**Anti-Pattern 3: No user feedback for slow operations**
```python
data = expensive_operation()  # User sees blank screen
```
**Problem:** User doesn't know if app is working or frozen

**Correct Pattern:**
```python
with st.spinner("Processing data..."):
    data = expensive_operation()
st.success("Processing complete!")
```

**Anti-Pattern 4: Recreating connections on every call**
```python
def get_connection():
    return Session.builder.configs(st.secrets["snowflake"]).create()

# Creates new connection every rerun!
session1 = get_connection()
session2 = get_connection()
```
**Problem:** Connection creation is expensive; wastes resources

**Correct Pattern:**
```python
@st.cache_resource
def get_connection():
    return Session.builder.configs(st.secrets["snowflake"]).create()

# Reuses cached connection
session1 = get_connection()
session2 = get_connection()  # Same session object
```

## Quick Compliance Checklist
- [ ] @st.cache_data used for all database queries with appropriate ttl
- [ ] @st.cache_resource used for connections and expensive objects
- [ ] Snowflake column names normalized to lowercase immediately after loading
- [ ] All SQL queries wrapped in try/except with SnowparkSQLException
- [ ] Error messages use st.error() and show query name, full error, table, and error code
- [ ] Progress indicators shown for operations >2 seconds
- [ ] No raw SQL loops; data aggregated in SQL and fetched once
- [ ] Initial load time <2 seconds with cached data
- [ ] All data loader functions have column normalization
- [ ] Cache behavior tested (verify data refreshes after ttl)
- [ ] SQL error handling tested with invalid query

## Validation
- **Success Checks:** Cache hits on subsequent loads, column names lowercase after normalization, SQL errors display red st.error() boxes with full context, progress indicators show for slow operations, initial load <2s, no database query loops, error messages identify specific query that failed
- **Negative Tests:** Clear cache and verify data reloads, test column access with lowercase (should work), test with invalid table name (should show detailed error), test with missing column (should show SQL error with code), remove progress indicator and verify user sees feedback gap, test with production data volume

> **Investigation Required**  
> When applying this rule:
> 1. Read data loading code BEFORE making recommendations
> 2. Verify @st.cache_data and @st.cache_resource usage
> 3. Check if column names are normalized after Snowflake queries
> 4. Check if SQL queries have try/except blocks with detailed error messages
> 5. Verify error messages use st.error() and include query name, full error, table, and error code
> 6. Never speculate about cache behavior - inspect the decorators and ttl values
> 7. Verify Snowflake connection patterns (should be cached)
> 8. Check for query loops that should be replaced with single aggregated query

## Response Template
```python
import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

@st.cache_resource
def get_snowflake_session() -> Session:
    """Create and cache Snowflake connection."""
    return Session.builder.configs(st.secrets["snowflake"]).create()

@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    """
    Load data from Snowflake with caching and comprehensive error handling.
    
    Returns:
        DataFrame with lowercase column names
    """
    try:
        session = get_snowflake_session()
        
        with st.spinner("Loading data from Snowflake..."):
            query = """
            SELECT 
                region,
                product,
                SUM(amount) as total_amount
            FROM sales
            WHERE order_date >= DATEADD(day, -90, CURRENT_DATE())
            GROUP BY region, product
            """
            df = session.sql(query).to_pandas()
            
            # CRITICAL: Normalize column names
            df.columns = [col.lower() for col in df.columns]
        
        return df
        
    except SnowparkSQLException as e:
        st.error(f"""
        **SQL Query Failed: load_data()**
        
        **Error:** {str(e)}
        **SQL Error Code:** {e.error_code if hasattr(e, 'error_code') else 'N/A'}
        
        **Query Context:**
        - Table: sales
        - Operation: Loading sales data (last 90 days, aggregated by region/product)
        
        **Common Causes:**
        - Table 'sales' does not exist
        - Missing columns: region, product, amount, order_date
        - Insufficient SELECT permission on sales table
        - Invalid date function syntax
        """)
        st.stop()
        
    except Exception as e:
        st.error(f"""
        **Unexpected Error: load_data()**
        
        **Error Type:** {type(e).__name__}
        **Error Message:** {str(e)}
        
        Please contact support if this error persists.
        """)
        st.stop()

# Load data (cached)
df = load_data()
st.success(f"Loaded {len(df):,} records")

# Access with lowercase column names
st.dataframe(df[['region', 'product', 'total_amount']])
```

## References

### External Documentation

**Streamlit Performance:**
- [Streamlit Caching](https://docs.streamlit.io/develop/concepts/architecture/caching) - Comprehensive caching guide
- [st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) - Cache data and dataframes
- [st.cache_resource](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource) - Cache connections and resources
- [Optimize Performance](https://docs.streamlit.io/develop/concepts/architecture/app-design) - Performance optimization patterns

**Progress Indicators:**
- [st.spinner](https://docs.streamlit.io/develop/api-reference/status/st.spinner) - Simple loading spinner
- [st.progress](https://docs.streamlit.io/develop/api-reference/status/st.progress) - Progress bar for long operations
- [st.status](https://docs.streamlit.io/develop/api-reference/status/st.status) - Detailed status updates

**Snowflake Performance:**
- [Snowflake Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query performance analysis
- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index) - Snowpark for Python documentation

### Related Rules
- **Streamlit Core**: `101-snowflake-streamlit-core.md`
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Snowflake Cost Governance**: `105-snowflake-cost-governance.md`
- **DateTime Handling**: `251-python-datetime-handling.md` (datetime optimization for time series)
- **Pandas Best Practices**: `252-pandas-best-practices.md` (DataFrame optimization and caching patterns)

> **🤖 Claude 4 Specific Guidance**  
> **Claude 4 Streamlit Performance Optimizations:**
> - Parallel code analysis: Can review multiple data loader functions simultaneously for caching patterns
> - Context awareness: Efficiently track cache usage patterns across multiple files
> - Investigation-first: Excel at discovering missing @st.cache_data decorators and column normalization issues
> - Pattern recognition: Quickly identify query loops that should be replaced with aggregated queries

