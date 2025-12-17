# Streamlit Performance: Caching and Optimization

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** @st.cache_data, @st.cache_resource, SQL error handling, st.error, SnowparkSQLException, st.fragment, NULL handling, slow streamlit, streamlit caching, optimize streamlit, fix slow queries, fragment batch processing
**TokenBudget:** ~5950
**ContextTier:** High
**Depends:** rules/101-snowflake-streamlit-core.md, rules/103-snowflake-performance-tuning.md

## Purpose
Provide comprehensive guidance for optimizing Streamlit application performance through caching strategies, efficient data loading from Snowflake, SQL error handling with detailed debugging information, progress indicators, and performance profiling.

## Rule Scope

Streamlit performance optimization, caching patterns, Snowflake data loading, SQL error handling and debugging, progress indicators

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~500 tokens (always load for performance tasks)
- + Caching Strategies (section 1): ~1200 tokens (load for caching issues)
- + Data Loading & Error Handling (sections 2-3): ~2100 tokens (load for data/SQL issues)
- + Complete Reference: ~3800 tokens (full performance guide)

**Recommended Loading Strategy:**
- **Quick performance check**: Quick Start only
- **Caching problems**: + Caching Strategies
- **Data/SQL issues**: + Data Loading & Error Handling
- **Complete optimization**: Full reference

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

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

## Contract

<contract>
<inputs_prereqs>
Streamlit app configured (see 101-snowflake-streamlit-core.md), Snowflake connection established, pandas/polars for data manipulation
</inputs_prereqs>

<mandatory>
@st.cache_data, @st.cache_resource, st.spinner(), st.progress(), st.status(), Snowflake session.table(), session.sql()
</mandatory>

<forbidden>
Raw SQL loops without aggregation, redundant database connections, unoptimized queries without LIMIT or WHERE clauses, operations without user feedback
</forbidden>

<steps>
1. Cache database queries with @st.cache_data and appropriate ttl
2. Cache connections and expensive objects with @st.cache_resource
3. Normalize Snowflake column names to lowercase immediately after loading
4. Wrap all SQL queries in try/except blocks with detailed error messages using st.error()
5. Show user feedback for operations >2s (st.spinner) or >5s (st.progress + st.status)
6. Avoid raw database query loops; fetch all needed data at once
7. Profile performance and target <2s load time
</steps>

<output_format>
Optimized Streamlit app with <2s initial load, cached data operations, normalized column names, comprehensive SQL error handling with red st.error() boxes, appropriate progress indicators
</output_format>

<validation>
Test cache behavior, verify column name normalization, test SQL error handling with invalid queries, measure load time, validate progress indicators show for long operations
</validation>

<design_principles>
- **Cache Aggressively:** Use @st.cache_data for queries, @st.cache_resource for connections
- **Normalize Early:** Convert Snowflake UPPERCASE column names to lowercase immediately
- **Error Visibility:** Wrap all SQL queries in try/except with detailed st.error() messages showing which query failed and why
- **Fetch Once:** Avoid query loops; aggregate in SQL and fetch once
- **User Feedback:** Show progress for operations >2 seconds
- **Profile Always:** Target <2s load time, measure and optimize
> **Investigation Required**
> When optimizing Streamlit performance:
> 1. Profile the application first - use Chrome DevTools or st.profiler to identify actual bottlenecks
> 2. Check query execution times in Snowflake (QUERY_HISTORY view) before optimizing
> 3. Verify cache behavior - confirm TTL values and check st.cache_data/st.cache_resource are being used
> 4. Never assume column names - always normalize after fetching from Snowflake
> 5. Test error handling - verify st.error() messages appear when queries fail
> 6. Measure impact - profile before/after optimization to verify improvements
>
> **Anti-Pattern:**
> "Let me add caching everywhere to speed this up."
>
> **Correct Pattern:**
> "Let me profile the application first to see which operations are slow."
> [profiles with Chrome DevTools]
> "The load_dashboard_data() function takes 4.2s. Let me check the Snowflake query history."
> [checks QUERY_HISTORY]
> "The query itself runs in 0.3s, so the issue is likely in data processing. Let me add caching."
</design_principles>

</contract>

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

## Post-Execution Checklist
- [ ] @st.cache_data used for all database queries with appropriate ttl
      Verify: Search code for "session.sql" without @st.cache_data decorator
- [ ] @st.cache_resource used for connections and expensive objects
      Verify: Check connection/session creation functions have @st.cache_resource
- [ ] Snowflake column names normalized to lowercase immediately after loading
      Verify: Check for ".columns = " or ".columns.str.lower()" after each .to_pandas()
- [ ] All SQL queries wrapped in try/except with SnowparkSQLException
      Verify: Search for "session.sql" without surrounding try/except block
- [ ] Error messages use st.error() and show query name, full error, table, and error code
      Verify: Check st.error() calls include query name and table name
- [ ] Progress indicators shown for operations >2 seconds
      Verify: Profile with Chrome DevTools; check slow operations have st.spinner/st.progress
- [ ] No raw SQL loops; data aggregated in SQL and fetched once
      Verify: Search for "session.sql" inside "for" loops or list comprehensions
- [ ] Initial load time <2 seconds with cached data
      Verify: Profile with Chrome DevTools Network tab; check initial page load time
- [ ] All data loader functions have column normalization
      Verify: Check each function with .to_pandas() includes column normalization
- [ ] Cache behavior tested (verify data refreshes after ttl)
      Verify: Wait for TTL expiry + refresh page; check data updates
- [ ] SQL error handling tested with invalid query
      Verify: Temporarily break query (invalid table name); check st.error() appears

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

## Output Format Examples
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
- **Streamlit Core**: `rules/101-snowflake-streamlit-core.md`
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Snowflake Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Snowflake Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **DateTime Handling**: `rules/251-python-datetime-handling.md` (datetime optimization for time series)
- **Pandas Best Practices**: `rules/252-pandas-best-practices.md` (DataFrame optimization and caching patterns)

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Streamlit Performance Optimizations:**
> - Parallel code analysis: Can review multiple data loader functions simultaneously for caching patterns
> - Context awareness: Efficiently track cache usage patterns across multiple files
> - Investigation-first: Excel at discovering missing @st.cache_data decorators and column normalization issues
> - Pattern recognition: Quickly identify query loops that should be replaced with aggregated queries

## Implementation Details

### Common Pitfalls

**Pitfall 1: Using st.cache_data on Queries That Modify Data** [WARNING]
- **Trigger words**: "UPDATE", "INSERT", "DELETE", "MERGE" in cached query functions
- **Why critical**: Cached functions with side effects cause data inconsistency - modifications won't execute on subsequent runs
- **Correct approach**: Never cache data-modifying queries; only use @st.cache_data for SELECT queries
- **Detection**: Review all @st.cache_data decorated functions for DML statements

**Pitfall 2: Fragment Batch Processing Without Proper State Management** [WARNING]
- **Trigger words**: "st.fragment" with stateful operations, batch processing without st.session_state
- **Why critical**: Fragments re-run independently, causing state loss or duplicate processing
- **Correct approach**: Use st.session_state to track fragment processing state; see Section 4
- **Detection**: Check if fragment functions use stateful variables without st.session_state

**Pitfall 3: Not Handling NULL/NaN in Pandas Before Charting** [WARNING]
- **Trigger words**: "st.line_chart", "st.bar_chart" with NULL/NaN values from Snowflake
- **Why critical**: Charts break or display incorrectly with NULL/NaN values
- **Correct approach**: Use `.fillna(0)` or `.dropna()` before charting; see Section 2
- **Detection**: Test charts with NULL-containing data from Snowflake

**Pitfall 4: Cache Invalidation Without TTL** [WARNING]
- **Trigger words**: "@st.cache_data()" without ttl parameter for frequently-updated data
- **Why critical**: Stale data shown to users; cache never refreshes automatically
- **Correct approach**: Always set ttl parameter for data that changes: `@st.cache_data(ttl=300)`
- **Detection**: Review @st.cache_data decorators for missing ttl on time-sensitive queries

**Pitfall 5: Query Loops Instead of Aggregation** [WARNING]
- **Trigger words**: "for" loop with query execution inside, repeated session.sql() calls
- **Why critical**: Massive performance degradation - O(n) queries instead of O(1)
- **Correct approach**: Use SQL WHERE, GROUP BY, JOIN to aggregate before fetching; see Section 5
- **Detection**: Search for "session.sql" inside loops or list comprehensions

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

**@st.cache_data:**
- Use Case: Data, query results
- TTL Support: Yes (recommended)
- Serialization: Pickled
- Thread Safety: Yes

**@st.cache_resource:**
- Use Case: Connections, models
- TTL Support: No (session lifetime)
- Serialization: Stored as-is
- Thread Safety: No (use with caution)

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
- Snowflake NULL becomes pandas NaN (not Python None)
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

### 3.2 Advanced Error Handling Patterns

**For comprehensive error handling patterns, see:**
- **101e-snowflake-streamlit-sql-errors.md** - Detailed examples for:
  - Multiple query error handling
  - User input validation and SQL injection prevention
  - Complex join error debugging
  - Error handling best practices checklist
  - Anti-patterns and common mistakes

**When to use the appendix:**
- Multiple related queries requiring granular error handling
- User-provided inputs in SQL queries
- Complex joins with potential data quality issues
- Need for comprehensive error message templates

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
    "[SEARCH] Analyze Transcription",
    type="primary",
    disabled=st.session_state.get("analysis_in_progress", False),
):
    selected_file = "call_de_20250924_003.mp3"

    # Set session state to trigger fragment
    st.session_state.active_analysis_file = selected_file
    st.session_state.analysis_in_progress = True
    st.session_state.analysis_start_time = time.time()

    # Initialize progress tracking
    with st.spinner("[DEPLOY] Launching analysis..."):
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

## Related Rules

**Closely Related** (consider loading together):
- `101-snowflake-streamlit-core` - For fundamental Streamlit patterns and session management
- `101e-snowflake-streamlit-sql-errors` - For comprehensive SQL error handling patterns (extracted from this rule)
- `103-snowflake-performance-tuning` - For optimizing underlying Snowflake queries

**Sometimes Related** (load if specific scenario):
- `101a-snowflake-streamlit-visualization` - When optimizing chart/visualization performance
- `101c-snowflake-streamlit-security` - When implementing secure caching patterns
- `111-snowflake-observability-core` - When adding query profiling and monitoring

**Complementary** (different aspects of same domain):
- `119-snowflake-warehouse-management` - For warehouse sizing affecting query performance
- `105-snowflake-cost-governance` - For monitoring costs of cached query executions
