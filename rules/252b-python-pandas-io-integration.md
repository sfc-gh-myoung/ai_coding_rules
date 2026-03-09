# Pandas IO and Integration Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:streamlit-pandas, kw:plotly-pandas, kw:pandas-io, kw:cache-data
**Keywords:** pandas Streamlit, pandas Plotly, cache_data, DataFrame caching, interactive filtering, CSV download, aggregate visualization, data loading
**TokenBudget:** ~1550
**ContextTier:** Medium
**Depends:** 252-python-pandas-core.md

## Scope

**What This Rule Covers:**
Pandas integration with Streamlit (caching, filtering, download) and Plotly (aggregation before plotting, performance), plus efficient data loading patterns.

**When to Load This Rule:**
- Integrating Pandas with Streamlit caching and widgets
- Visualizing DataFrames with Plotly
- Building interactive data apps
- Exporting processed DataFrames

## References

### Dependencies

**Must Load First:**
- **252-python-pandas-core.md** - Core Pandas patterns

**Related:**
- **252a-python-pandas-performance.md** - Memory optimization and groupby
- **101a-snowflake-streamlit-visualization.md** - Plotly chart patterns
- **101b-snowflake-streamlit-performance.md** - Caching strategies

## Contract

### Inputs and Prerequisites

- Pandas 2.x+ DataFrames (from 252 core)
- Streamlit for UI integration (optional)
- Plotly for visualization (optional)

### Mandatory

- **Always:** Cache DataFrame loading with `@st.cache_data`
- **Always:** Aggregate data before Plotly visualization (never plot 1M+ raw rows)
- **Rule:** Optimize dtypes inside cached loading functions
- **Rule:** Use `df.query()` for interactive filtering with Streamlit widgets

### Forbidden

- Plotting raw large DataFrames without aggregation (slow, cluttered)
- Missing `@st.cache_data` on data loading functions
- Using `inplace=True` inside cached functions (confusing behavior)

### Execution Steps

1. Wrap data loading in `@st.cache_data(ttl=...)`
2. Optimize dtypes inside the cached function
3. Use query() for interactive filtering from widgets
4. Aggregate before Plotly visualization
5. Provide CSV download for filtered data

### Output Format

Cached data loading, interactive Streamlit filtering, aggregated Plotly charts, CSV download.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Data loading cached with @st.cache_data
- [ ] dtypes optimized in cached function
- [ ] Data aggregated before plotting
- [ ] Interactive filtering works correctly

### Design Principles

- **Cache Early:** Cache data loading and processing together
- **Aggregate Before Plot:** Never send raw millions of rows to Plotly
- **Interactive:** Use Streamlit widgets with query() for filtering

### Post-Execution Checklist

- [ ] @st.cache_data applied to loading functions
- [ ] dtypes optimized inside cache
- [ ] Plotly charts use aggregated data
- [ ] Interactive filtering with query()
- [ ] CSV download available

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Plotting Raw Large DataFrames

**Problem:** Sending millions of rows to Plotly makes the chart slow to render and visually cluttered.

**Correct Pattern:** Aggregate data before plotting to reduce row count.

```python
# Wrong: Plot 1M rows (slow, cluttered)
fig = px.scatter(df, x='date', y='value')  # df has 1M rows

# Correct: Aggregate first, then plot
df_daily = df.groupby('date').agg({'value': 'mean'}).reset_index()
fig = px.line(df_daily, x='date', y='value')  # 365 rows - fast!
```

### Anti-Pattern 2: Missing Cache on Data Loading

**Problem:** Without caching, data reloads on every Streamlit rerun (widget interaction, page refresh).

**Correct Pattern:** Wrap data loading with `@st.cache_data` and optimize dtypes inside the cached function.

```python
# Wrong: Reloads every rerun
def load_data():
    return pd.read_csv('large_data.csv')

# Correct: Cached with TTL
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv('large_data.csv')
    df['category'] = df['category'].astype('category')
    return df
```

## Streamlit Integration

### Efficient Caching with Pandas

```python
import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_and_process_data():
    """Cache DataFrame loading and dtype optimization together."""
    df = pd.read_csv('large_data.csv')

    # Optimize dtypes for memory
    df['category'] = df['category'].astype('category')
    df['status_code'] = df['status_code'].astype('int8')

    # Pre-compute expensive operations
    df['total'] = df['price'] * df['quantity']

    return df

df = load_and_process_data()
```

### Interactive Filtering

```python
# User filters
category = st.selectbox('Category', df['category'].unique())
min_price = st.slider('Min Price', 0, 1000, 100)

# Efficient filtering with query()
filtered_df = df.query('category == @category and price >= @min_price')
st.dataframe(filtered_df)
```

### Download Processed Data

```python
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_df)
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)
```

## Plotly Integration

### Aggregate Before Plotting

```python
import plotly.express as px

# Pre-process for Plotly
df_viz = (
    df
    .groupby(['date', 'category'])
    .agg({'sales': 'sum'})
    .reset_index()
    .sort_values('date')
)

fig = px.line(df_viz, x='date', y='sales', color='category')
st.plotly_chart(fig, width="stretch")
```

## Output Format Example

```python
import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv('data.csv')
    df['category'] = df['category'].astype('category')
    df['status_code'] = df['status_code'].astype('int8')
    df['total'] = df['price'] * df['quantity']
    return df

df = load_data()

category = st.selectbox('Category', df['category'].unique())
filtered_df = df.query('category == @category')

df_viz = filtered_df.groupby('date').agg({'total': 'sum'}).reset_index()
fig = px.line(df_viz, x='date', y='total')
st.plotly_chart(fig, width="stretch")
```
