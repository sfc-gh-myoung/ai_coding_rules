**Description:** Performance optimization, caching strategies, and data loading patterns for Streamlit applications
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Streamlit caching, @st.cache_data, @st.cache_resource, performance optimization, slow Streamlit, data loading, query optimization, NULL handling, pandas NaN
**Version:** 1.2
**LastUpdated:** 2025-10-18

**TokenBudget:** ~550
**ContextTier:** standard

# Streamlit Performance: Caching and Optimization

<section_metadata>
  <token_budget>500</token_budget>
  <context_tier>standard</context_tier>
  <priority>high</priority>
</section_metadata>

## Purpose
Provide comprehensive guidance for optimizing Streamlit application performance through caching strategies, efficient data loading from Snowflake, progress indicators, and performance profiling.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Streamlit performance optimization, caching patterns, Snowflake data loading, progress indicators

## Contract

<directive_strength>mandatory</directive_strength>
- **Inputs/Prereqs:** Streamlit app configured (see 101-snowflake-streamlit-core.md), Snowflake connection established, pandas/polars for data manipulation
- **Allowed Tools:** @st.cache_data, @st.cache_resource, st.spinner(), st.progress(), st.status(), Snowflake session.table(), session.sql()

<directive_strength>forbidden</directive_strength>
- **Forbidden Tools:** Raw SQL loops without aggregation, redundant database connections, unoptimized queries without LIMIT or WHERE clauses, operations without user feedback

<directive_strength>mandatory</directive_strength>
- **Required Steps:**
  1. Cache database queries with @st.cache_data and appropriate ttl
  2. Cache connections and expensive objects with @st.cache_resource
  3. Normalize Snowflake column names to lowercase immediately after loading
  4. Show user feedback for operations >2s (st.spinner) or >5s (st.progress + st.status)
  5. Avoid raw database query loops; fetch all needed data at once
  6. Profile performance and target <2s load time
- **Output Format:** Optimized Streamlit app with <2s initial load, cached data operations, normalized column names, appropriate progress indicators
- **Validation Steps:** Test cache behavior, verify column name normalization, measure load time, validate progress indicators show for long operations

## Key Principles
- **Cache Aggressively:** Use @st.cache_data for queries, @st.cache_resource for connections
- **Normalize Early:** Convert Snowflake UPPERCASE column names to lowercase immediately
- **Fetch Once:** Avoid query loops; aggregate in SQL and fetch once
- **User Feedback:** Show progress for operations >2 seconds
- **Profile Always:** Target <2s load time, measure and optimize

## 1. Caching Strategies

<section_metadata>
  <section_id>caching</section_id>
  <priority>critical</priority>
  <token_budget>150</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
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
        st.warning("⚠️ Some metrics unavailable - showing cached values where possible")
    
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

<section_metadata>
  <section_id>snowflake_data</section_id>
  <priority>critical</priority>
  <token_budget>120</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
**Column Name Normalization (CRITICAL):**
- **Critical:** Snowflake returns column names in **UPPERCASE** by default, which causes `KeyError` when accessing with lowercase
- **Always:** Normalize column names to lowercase immediately after loading data from Snowflake
- **Rule:** Apply normalization in data loader functions, not in UI code, to ensure consistency

**Problem:**
```python
# ❌ This will fail with KeyError: 'asset_type'
df = session.table('GRID_ASSETS').to_pandas()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```

**Solution:**
```python
# ✓ Correct - Normalize column names to lowercase
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

<directive_strength>mandatory</directive_strength>
- **Always:** Use fully qualified table names (`DATABASE.SCHEMA.TABLE`) to avoid context issues
- **Always:** Apply normalization to both `session.table().to_pandas()` and `session.sql(query).to_pandas()` results
- **Rule:** Document this normalization in function docstrings to inform other developers

**Why This Matters:**
- **Consistency:** Python code conventionally uses lowercase for column names (snake_case)
- **Portability:** Local dev environments may use lowercase; Snowflake uses uppercase
- **Error Prevention:** Prevents `KeyError` exceptions that are hard to debug in production
- **Best Practice:** Single normalization point in data loaders vs. scattered `.upper()` calls in UI code

## 3. Progress Indicators and User Feedback

<section_metadata>
  <section_id>progress</section_id>
  <priority>high</priority>
  <token_budget>80</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
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

## 4. Performance Optimization Patterns

<directive_strength>mandatory</directive_strength>
**Avoid raw database query loops; fetch all needed data at once and cache it:**

**❌ Anti-Pattern:**
```python
# Inefficient: N+1 query problem
for region in regions:
    df = session.sql(f"SELECT * FROM sales WHERE region = '{region}'").to_pandas()
    process(df)
```

**✅ Correct:**
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

## 5. Performance Profiling

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

<directive_strength>recommended</directive_strength>
- **Consider:** Use Python profilers (cProfile, line_profiler) for computational bottlenecks
- **Always:** Test with production-like data volumes during development
- **Requirement:** Use Snowflake Query Profile to validate query performance

## Anti-Patterns and Common Mistakes

<anti_pattern_examples>
**❌ Anti-Pattern 1: No caching for expensive operations**
```python
def load_data():
    # Runs every rerun - slow!
    return session.table('LARGE_TABLE').to_pandas()

df = load_data()  # Hits database every time
```
**Problem:** Database queried on every widget interaction

**✅ Correct Pattern:**
```python
@st.cache_data(ttl=600)
def load_data():
    df = session.table('LARGE_TABLE').to_pandas()
    df.columns = [col.lower() for col in df.columns]
    return df

df = load_data()  # Cached, hits database once per ttl
```

**❌ Anti-Pattern 2: Forgetting column normalization**
```python
@st.cache_data(ttl=600)
def load_assets():
    return session.table('ASSETS').to_pandas()

df = load_assets()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```
**Problem:** Snowflake returns UPPERCASE column names; Python expects lowercase

**✅ Correct Pattern:**
```python
@st.cache_data(ttl=600)
def load_assets():
    df = session.table('ASSETS').to_pandas()
    df.columns = [col.lower() for col in df.columns]  # CRITICAL
    return df

df = load_assets()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # Works!
```

**❌ Anti-Pattern 3: No user feedback for slow operations**
```python
data = expensive_operation()  # User sees blank screen
```
**Problem:** User doesn't know if app is working or frozen

**✅ Correct Pattern:**
```python
with st.spinner("Processing data..."):
    data = expensive_operation()
st.success("Processing complete!")
```

**❌ Anti-Pattern 4: Recreating connections on every call**
```python
def get_connection():
    return Session.builder.configs(st.secrets["snowflake"]).create()

# Creates new connection every rerun!
session1 = get_connection()
session2 = get_connection()
```
**Problem:** Connection creation is expensive; wastes resources

**✅ Correct Pattern:**
```python
@st.cache_resource
def get_connection():
    return Session.builder.configs(st.secrets["snowflake"]).create()

# Reuses cached connection
session1 = get_connection()
session2 = get_connection()  # Same session object
```
</anti_pattern_examples>

## Quick Compliance Checklist
- [ ] @st.cache_data used for all database queries with appropriate ttl
- [ ] @st.cache_resource used for connections and expensive objects
- [ ] Snowflake column names normalized to lowercase immediately after loading
- [ ] Progress indicators shown for operations >2 seconds
- [ ] No raw SQL loops; data aggregated in SQL and fetched once
- [ ] Initial load time <2 seconds with cached data
- [ ] All data loader functions have column normalization
- [ ] Cache behavior tested (verify data refreshes after ttl)

## Validation
- **Success Checks:** Cache hits on subsequent loads, column names lowercase after normalization, progress indicators show for slow operations, initial load <2s, no database query loops
- **Negative Tests:** Clear cache and verify data reloads, test column access with lowercase (should work), remove progress indicator and verify user sees feedback gap, test with production data volume

<investigate_before_answering>
When applying this rule:
1. Read data loading code BEFORE making recommendations
2. Verify @st.cache_data and @st.cache_resource usage
3. Check if column names are normalized after Snowflake queries
4. Never speculate about cache behavior - inspect the decorators and ttl values
5. Verify Snowflake connection patterns (should be cached)
6. Check for query loops that should be replaced with single aggregated query
</investigate_before_answering>

## Response Template
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
    
    Returns:
        DataFrame with lowercase column names
    """
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

<model_specific_guidance model="claude-4">
**Claude 4 Streamlit Performance Optimizations:**
- Parallel code analysis: Can review multiple data loader functions simultaneously for caching patterns
- Context awareness: Efficiently track cache usage patterns across multiple files
- Investigation-first: Excel at discovering missing @st.cache_data decorators and column normalization issues
- Pattern recognition: Quickly identify query loops that should be replaced with aggregated queries
</model_specific_guidance>

