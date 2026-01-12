# Streamlit Performance: Caching and Optimization

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** @st.cache_data, @st.cache_resource, st.fragment, NULL handling, slow streamlit, streamlit caching, optimize streamlit, fix slow queries, fragment batch processing, streamlit performance, app slow, loading data, caching pattern
**TokenBudget:** ~5450
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core.md, 103-snowflake-performance-tuning.md

## Scope

**What This Rule Covers:**
Comprehensive guidance for optimizing Streamlit application performance through caching strategies (@st.cache_data, @st.cache_resource), efficient data loading from Snowflake with column normalization, progress indicators (st.spinner, st.progress, fragments), and performance profiling targeting <2s load times. For detailed SQL error handling patterns, see 101e-snowflake-streamlit-sql-errors.md.

**When to Load This Rule:**
- Optimizing slow Streamlit applications
- Implementing caching strategies for database queries
- Adding progress indicators for long operations
- Fixing KeyError issues from Snowflake column names
- Resolving query loop performance problems
- Profiling and targeting <2s load time
- For SQL error handling, load 101e-snowflake-streamlit-sql-errors.md

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns and session management
- **103-snowflake-performance-tuning.md** - Snowflake query optimization

**Related:**
- **101e-snowflake-streamlit-sql-errors.md** - Comprehensive SQL error handling patterns
- **101a-snowflake-streamlit-visualization.md** - Chart/visualization performance
- **101c-snowflake-streamlit-security.md** - Secure caching patterns
- **105-snowflake-cost-governance.md** - Cost monitoring for cached queries
- **111-snowflake-observability-core.md** - Query profiling and monitoring
- **119-snowflake-warehouse-management.md** - Warehouse sizing for query performance
- **251-python-datetime-handling.md** - Datetime optimization for time series
- **252-python-pandas.md** - DataFrame optimization and caching

### External Documentation

**Streamlit Performance:**
- [Streamlit Caching](https://docs.streamlit.io/develop/concepts/architecture/caching) - Comprehensive caching guide
- [st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) - Cache data and dataframes
- [st.cache_resource](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource) - Cache connections and resources
- [Optimize Performance](https://docs.streamlit.io/develop/concepts/architecture/app-design) - Performance optimization patterns
- [st.fragment](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) - Fragment API for scoped reruns

**Progress Indicators:**
- [st.spinner](https://docs.streamlit.io/develop/api-reference/status/st.spinner) - Simple loading spinner
- [st.progress](https://docs.streamlit.io/develop/api-reference/status/st.progress) - Progress bar for long operations
- [st.status](https://docs.streamlit.io/develop/api-reference/status/st.status) - Detailed status updates

**Snowflake Performance:**
- [Snowflake Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) - Query performance analysis
- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index) - Snowpark for Python documentation

### Related Rules

**Closely Related** (consider loading together):
- **101-snowflake-streamlit-core.md** - fundamental Streamlit patterns and session management
- **101e-snowflake-streamlit-sql-errors.md** - comprehensive SQL error handling patterns (extracted from this rule)
- **103-snowflake-performance-tuning.md** - optimizing underlying Snowflake queries

**Sometimes Related** (load if specific scenario):
- **101a-snowflake-streamlit-visualization.md** - optimizing chart/visualization performance
- **101c-snowflake-streamlit-security.md** - implementing secure caching patterns
- **111-snowflake-observability-core.md** - adding query profiling and monitoring

**Complementary** (different aspects of same domain):
- **119-snowflake-warehouse-management.md** - warehouse sizing affecting query performance
- **105-snowflake-cost-governance.md** - monitoring costs of cached query executions

## Contract

### Inputs and Prerequisites

Streamlit app configured (see 101-snowflake-streamlit-core.md), Snowflake connection established, pandas/polars for data manipulation

### Mandatory

@st.cache_data, @st.cache_resource, st.spinner(), st.progress(), st.status(), Snowflake session.table(), session.sql()

### Forbidden

- Raw SQL loops without aggregation
- Redundant database connections
- Unoptimized queries without LIMIT or WHERE clauses
- Operations without user feedback (>2s without spinner)

### Execution Steps

1. Cache database queries with @st.cache_data and appropriate ttl
2. Cache connections and expensive objects with @st.cache_resource
3. Normalize Snowflake column names to lowercase immediately after loading
4. Show user feedback for operations >2s (st.spinner) or >5s (st.progress + st.status)
5. Avoid raw database query loops; fetch all needed data at once
6. Profile performance and target <2s load time
7. For SQL error handling, apply patterns from 101e-snowflake-streamlit-sql-errors.md

### Output Format

Optimized Streamlit app with <2s initial load, cached data operations, normalized column names, appropriate progress indicators. For SQL error handling output, see 101e-snowflake-streamlit-sql-errors.md.

### Validation

**Test Requirements:**
- Test cache behavior with different inputs
- Verify column name normalization (lowercase after Snowflake fetch)
- Measure load time (<2s target)
- Validate progress indicators show for long operations
- For SQL error testing, see 101e-snowflake-streamlit-sql-errors.md

**Success Criteria:**
- Cache hits on subsequent loads
- Column names lowercase after normalization
- Progress indicators show for slow operations
- Initial load <2s
- No database query loops
- Error messages identify specific query that failed

**Negative Tests:**
- Clear cache and verify data reloads
- Test column access with lowercase (should work)
- Test with production data volume
- For SQL error negative tests, see 101e-snowflake-streamlit-sql-errors.md

> **Investigation Required**
> When applying this rule:
> 1. Read data loading code BEFORE making recommendations
> 2. Verify @st.cache_data and @st.cache_resource usage
> 3. Check if column names are normalized after Snowflake queries
> 4. Never speculate about cache behavior - inspect the decorators and ttl values
> 5. Verify Snowflake connection patterns (should be cached)
> 6. Check for query loops that should be replaced with single aggregated query
> 7. For SQL error handling investigation, see 101e-snowflake-streamlit-sql-errors.md

### Design Principles

- **Cache Aggressively:** Use @st.cache_data for queries, @st.cache_resource for connections
- **Normalize Early:** Convert Snowflake UPPERCASE column names to lowercase immediately
- **Fetch Once:** Avoid query loops; aggregate in SQL and fetch once
- **User Feedback:** Show progress for operations >2 seconds
- **Profile Always:** Target <2s load time, measure and optimize
- **Error Handling:** For SQL error patterns, see 101e-snowflake-streamlit-sql-errors.md

### Post-Execution Checklist

- [ ] @st.cache_data used for all database queries with appropriate ttl
      Verify: Search code for "session.sql" without @st.cache_data decorator
- [ ] @st.cache_resource used for connections and expensive objects
      Verify: Check connection/session creation functions have @st.cache_resource
- [ ] Snowflake column names normalized to lowercase immediately after loading
      Verify: Check for ".columns = " or ".columns.str.lower()" after each .to_pandas()
- [ ] Progress indicators shown for operations >2 seconds
      Verify: Profile with Chrome DevTools; check slow operations have st.spinner/st.progress
- [ ] No raw SQL loops; data aggregated in SQL and fetched once
      Verify: Search for "session.sql" inside "for" loops or list comprehensions
- [ ] Initial load time <2 seconds with cached data
      Verify: Profile with Chrome DevTools Network tab; check initial page load time
- [ ] All data loader functions have column normalization
      Verify: Check each function with .to_pandas() includes column normalization
- [ ] For SQL error handling checklist, see 101e-snowflake-streamlit-sql-errors.md
- [ ] Cache behavior tested (verify data refreshes after ttl)
      Verify: Wait for TTL expiry + refresh page; check data updates
- [ ] SQL error handling tested with invalid query
      Verify: Temporarily break query (invalid table name); check st.error() appears

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
df = load_assets()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```
**Problem:** Snowflake returns UPPERCASE column names; Python expects lowercase. See "Data Loading from Snowflake" section below for normalization pattern.

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

## Output Format Examples

### Caching Pattern with Column Normalization

```python
import streamlit as st
import pandas as pd
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session() -> Session:
    """Create and cache Snowflake connection."""
    return Session.builder.configs(st.secrets["snowflake"]).create()

@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    """
    Load data from Snowflake with caching.
    For SQL error handling, see 101e-snowflake-streamlit-sql-errors.md.

    Returns:
        DataFrame with lowercase column names
    """
    session = get_snowflake_session()

    try:
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

## Caching Strategies

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

**For NULL/NaN handling patterns, see Section "Pandas NULL Handling" in `101-snowflake-streamlit-core.md`.**

**Key Rules for Caching:**
- Validate cached data doesn't contain unexpected NaN values that cause display errors
- Use `pd.notna()` instead of `is not None` to correctly handle Snowflake NULL values that become pandas NaN
- Format strings (`.1f`, `.0f`) crash on NaN values - validate first

```python
@st.cache_data(ttl=300)
def load_metrics():
    """Load KPI metrics from Snowflake with NULL-safe handling."""
    session = get_snowflake_session()
    df = session.sql("SELECT metric_name, value FROM kpis").to_pandas()
    if df["value"].isna().any():
        st.warning("Some metrics unavailable")
    return df

metrics_df = load_metrics()
for _, row in metrics_df.iterrows():
    value = row["value"]
    if pd.notna(value):
        st.metric(row["metric_name"], f"{value:.2f}")
    else:
        st.metric(row["metric_name"], "N/A")
```

## Data Loading from Snowflake - Critical Column Name Normalization

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

## SQL Error Handling and Debugging

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

**For comprehensive SQL error handling patterns and examples, see 101e-snowflake-streamlit-sql-errors.md.**

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

## Progress Indicators and User Feedback

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

**For long-running operations (>30s) requiring live progress updates, see `101g-snowflake-streamlit-fragments.md`.**

Covers: `@st.fragment(run_every=...)`, session state persistence, conditional rendering, anti-patterns, and complete working examples.

## Performance Optimization Patterns

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

## Performance Profiling

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
