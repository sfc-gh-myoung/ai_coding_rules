# Pandas Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** pandas, DataFrame, vectorization, SettingWithCopyWarning, memory optimization, dtypes, groupby, merge, performance, method chaining
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Establish comprehensive Pandas best practices focusing on vectorization, performance optimization, memory efficiency, and anti-pattern avoidance to prevent common issues like 100x+ performance slowdowns, SettingWithCopyWarning errors, and memory exhaustion in data-intensive workflows.

## Rule Scope

Pandas DataFrame/Series operations, performance optimization, memory management, integration with Streamlit and Plotly

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Never use iterrows() for computation** - Use vectorized operations (100x faster)
- **Always use .loc/.iloc for assignment** - Prevents SettingWithCopyWarning
- **Optimize dtypes immediately** - Use categorical, int8/int16 instead of int64/object
- **Filter before groupby** - Pre-filter data to reduce processing
- **Use method chaining** - `df.query(...).groupby(...).agg(...)` for clarity
- **Validate merge keys** - Use `validate` parameter in merge()
- **Never use chained assignment** - `df[df['col'] > 0]['new'] = 1` causes warnings

**Quick Checklist:**
- [ ] Vectorized operations (no iterrows for computation)
- [ ] Explicit indexing with .loc/.iloc
- [ ] Optimized dtypes (categorical, smaller ints)
- [ ] Pre-filtering before aggregation
- [ ] Method chaining for readability
- [ ] Merge validation enabled
- [ ] No chained assignment

## Contract

<contract>
<inputs_prereqs>
Python 3.11+, pandas 2.x+, understanding of DataFrame operations, basic NumPy knowledge
</inputs_prereqs>

<mandatory>
Vectorized operations, .loc/.iloc indexers, groupby(), merge(), concat(), astype(), query(), eval(), method chaining
</mandatory>

<forbidden>
iterrows() for computation (read-only OK), apply() when vectorization possible, chained assignment without .loc, df.append() (deprecated), inplace=True (generally discouraged)
</forbidden>

<steps>
1. Use vectorized operations instead of loops (10x-100x+ faster)
2. Use .loc/.iloc for explicit indexing (prevents SettingWithCopyWarning)
3. Optimize dtypes for memory efficiency
4. Pre-filter before groupby/aggregation operations
5. Use efficient merge strategies (validate merge keys)
6. Profile performance for operations on large DataFrames
7. Integrate efficiently with Streamlit caching and Plotly visualization
</steps>

<output_format>
Performant Pandas code, minimal memory footprint, clear anti-pattern avoidance
</output_format>

<validation>
Performance benchmarking (vectorized vs loop), memory profiling (dtype optimization), no SettingWithCopyWarning, efficient DataFrame operations
</validation>

<design_principles>
- **Vectorization First:** Always prefer vectorized operations over loops (10x-100x+ faster)
- **Explicit Indexing:** Use .loc/.iloc to prevent SettingWithCopyWarning
- **Memory Conscious:** Optimize dtypes and use categorical data where appropriate
- **Method Chaining:** Chain operations for clarity and efficiency
- **Integration Ready:** Design for efficient Streamlit caching and Plotly visualization
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: iterrows() for computation (100x slower)**
```python
# Problem: Using iterrows() for computation
for _, row in df.iterrows():
    df.at[row.name, 'total'] = row['price'] * row['qty']
```
**Problem:** 100x slower than vectorization - iterates row-by-row in Python instead of using NumPy's optimized operations.

**Correct Pattern:**
```python
# Vectorized operation
df['total'] = df['price'] * df['qty']
```
**Benefits:** 100x+ faster execution using NumPy-level vectorization.

**Anti-Pattern 2: apply() when vectorization possible (10x slower)**
```python
# Problem: Using apply() when vectorization available
df['total'] = df.apply(lambda row: row['price'] * row['qty'], axis=1)
```
**Problem:** 10x slower than vectorization - applies Python function to each row instead of vectorized operations.

**Correct Pattern:**
```python
# Vectorized operation
df['total'] = df['price'] * df['qty']
```
**Benefits:** 10x+ faster by using pandas vectorized multiplication.

**Anti-Pattern 3: Chained assignment (SettingWithCopyWarning)**
```python
# Problem: Chained assignment triggers warning
df[df['active']]['price'] = df['price'] * 1.1
```
**Problem:** Triggers SettingWithCopyWarning - ambiguous whether modifying view or copy of DataFrame.

**Correct Pattern:**
```python
# Explicit .loc indexing
df.loc[df['active'], 'price'] *= 1.1
```
**Benefits:** Clear, unambiguous assignment that avoids warnings and ensures correct behavior.

**Anti-Pattern 4: Inefficient dtype usage (wastes 87.5% memory)**
```python
df['status_code'] = df['status_code']  # int64 (8 bytes)
```
**Correct:** `df['status_code'] = df['status_code'].astype('int8')  # 1 byte`

**Anti-Pattern 5: Multiple groupby calls (slow)**
```python
sum_sales = df.groupby('category')['sales'].sum()
mean_sales = df.groupby('category')['sales'].mean()
```
**Correct:** `result = df.groupby('category')['sales'].agg(['sum', 'mean'])`

**Anti-Pattern 6: Using inplace=True (unclear, error-prone)**
```python
df.dropna(inplace=True)
df.sort_values('date', inplace=True)
```
**Correct:** `df = df.dropna().sort_values('date')  # Clear assignment`

**Anti-Pattern 7: Loading huge files entirely (out of memory)**
```python
df = pd.read_csv('10gb_file.csv')
```
**Correct:** `for chunk in pd.read_csv('10gb_file.csv', chunksize=10000):`

## Post-Execution Checklist

- [ ] Vectorized operations used instead of iterrows() for computation
- [ ] apply() avoided when vectorization possible
- [ ] .loc/.iloc used for explicit indexing (no chained assignment)
- [ ] dtypes optimized for memory efficiency
- [ ] Categorical data used for repeating strings
- [ ] GroupBy operations use .agg() for multiple aggregations
- [ ] Merge operations validated (validate= and indicator=)
- [ ] Method chaining used for clear data pipelines
- [ ] Streamlit caching applied to DataFrame operations
- [ ] Data aggregated before Plotly visualization
- [ ] DateTime operations reference 251-python-datetime-handling.md

## Validation

- **Success Checks:** Vectorized operations 10x+ faster than loops, no SettingWithCopyWarning, memory usage optimized (dtype checks), efficient GroupBy/merge operations, Streamlit app loads quickly with caching
- **Negative Tests:** iterrows() loop (should be very slow), chained assignment (should warn), int64 for small integers (should waste memory), multiple separate groupby calls (should be slower than single .agg()), missing cache_data decorator (should reload data every rerun)

> **Investigation Required**
> When applying this rule:
> 1. **Read existing DataFrame operations BEFORE optimizing** - Check current code for iterrows(), apply(), chained assignment patterns
> 2. **Profile actual performance** - Measure execution time before and after optimization
> 3. **Never speculate about DataFrame shape** - Use df.shape, df.dtypes to understand actual data structure
> 4. **Check memory usage** - Use df.memory_usage(deep=True) to verify dtype optimization impact
> 5. **Make grounded recommendations based on investigated code** - Don't optimize without measuring
>
> **Anti-Pattern:**
> "Based on typical Pandas usage, you probably have this performance issue..."
> "Let me vectorize this - it should be faster..."
>
> **Correct Pattern:**
> "Let me check your current Pandas operations first."
> [reads code, profiles performance, checks dtypes]
> "I see you're using iterrows() in process_data() (5.2s for 100k rows). Here's a vectorized version (0.05s, 100x faster)..."

## Output Format Examples

```python
import pandas as pd
import streamlit as st
import plotly.express as px

# Efficient data loading with caching
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv('data.csv')

    # Optimize dtypes
    df['category'] = df['category'].astype('category')
    df['status_code'] = df['status_code'].astype('int8')

    # Vectorized operations
    df['total'] = df['price'] * df['quantity']
    df['discount'] = df['total'] * 0.1

    return df

# Load data
df = load_data()

# Interactive filtering
category = st.selectbox('Category', df['category'].unique())
filtered_df = df.query('category == @category')

# Aggregate for visualization
df_viz = filtered_df.groupby('date').agg({'total': 'sum'}).reset_index()

# Plot
fig = px.line(df_viz, x='date', y='total')
st.plotly_chart(fig, use_container_width=True)
```

## References

### External Documentation

**Pandas Documentation:**
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html) - Comprehensive Pandas guide
- [Enhancing Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html) - Official performance optimization guide
- [Indexing and Selecting Data](https://pandas.pydata.org/docs/user_guide/indexing.html) - .loc/.iloc best practices
- [GroupBy Operations](https://pandas.pydata.org/docs/user_guide/groupby.html) - GroupBy documentation
- [Merge, Join, Concatenate](https://pandas.pydata.org/docs/user_guide/merging.html) - Merge best practices
- [Categorical Data](https://pandas.pydata.org/docs/user_guide/categorical.html) - Memory optimization with categorical

**Performance Resources:**
- [Pandas Optimization Tips](https://pandas.pydata.org/docs/user_guide/cookbook.html#optimization) - Official optimization cookbook

### Related Rules
- **Python Core**: `rules/200-python-core.md` - Modern Python tooling
- **DateTime Handling**: `rules/251-python-datetime-handling.md` - Comprehensive datetime guidance for Pandas
- **Streamlit Visualization**: `rules/101a-snowflake-streamlit-visualization.md` - Plotly chart patterns
- **Streamlit Performance**: `rules/101b-snowflake-streamlit-performance.md` - Caching strategies
- **Data Science Analytics**: `rules/920-data-science-analytics.md` - ML workflows and analytics patterns

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Pandas Optimizations:**
> - Performance comparison: Generate benchmarks showing vectorization speedups
> - Anti-pattern detection: Identify iterrows()/apply() usage in code reviews
> - Memory profiling: Analyze DataFrame memory usage and suggest dtype optimizations
> - Integration awareness: Cross-reference datetime operations with 251-python-datetime-handling.md

## 1. Vectorization vs Iteration

**FORBIDDEN:**

### Why Loops Are Slow

**Problem:** Python loops with iterrows() are 50x-100x+ slower than vectorized operations

**Reason:**
- Each loop iteration involves Python interpreter overhead
- Vectorized operations use optimized C/Cython code
- NumPy array operations process data in bulk

### Anti-Pattern: iterrows() for Computation

**NEVER USE iterrows() FOR COMPUTATION**
```python
# BAD: 100x slower for large DataFrames
total = 0
for idx, row in df.iterrows():
    total += row['price'] * row['quantity']

# BAD: Modifying DataFrame in loop (very slow)
for idx, row in df.iterrows():
    df.at[idx, 'total'] = row['price'] * row['quantity']
```

**Correct: Vectorized Operations**
```python
# GOOD: 100x faster
total = (df['price'] * df['quantity']).sum()

# GOOD: Create new column with vectorized operation
df['total'] = df['price'] * df['quantity']
```

### When iterrows() is Acceptable

**Read-only operations where vectorization not possible:**
```python
# ACCEPTABLE: Displaying rows in Streamlit (read-only)
for _, row in df.iterrows():
    st.metric(row['metric_name'], f"{row['value']:.2f}")

# ACCEPTABLE: Complex business logic that can't be vectorized
for _, row in df.iterrows():
    result = complex_external_api_call(row['id'])
    process_result(result)
```

### Vectorization Patterns

**Simple arithmetic:**
```python
# Element-wise operations
df['total'] = df['price'] * df['quantity']
df['discount'] = df['price'] * 0.1
df['final_price'] = df['price'] - df['discount']
```

**Conditional operations:**
```python
# Using np.where for conditionals
import numpy as np

df['category'] = np.where(df['price'] > 100, 'expensive', 'affordable')

# Multiple conditions
df['tier'] = np.select(
    [df['score'] >= 90, df['score'] >= 70, df['score'] >= 50],
    ['A', 'B', 'C'],
    default='F'
)
```

**String operations:**
```python
# Vectorized string methods
df['upper_name'] = df['name'].str.upper()
df['first_word'] = df['description'].str.split().str[0]
df['contains_keyword'] = df['text'].str.contains('important', case=False)
```

## 2. Anti-Pattern: apply() When Vectorization Works

**FORBIDDEN:**

### When apply() is Slow

**Problem:** apply() with axis=1 (row-wise) is nearly as slow as iterrows()

**Anti-Pattern: apply() for Simple Operations**
```python
# BAD: Unnecessary apply() (10x slower)
df['total'] = df.apply(lambda row: row['price'] * row['qty'], axis=1)

# BAD: apply() for string operations
df['upper'] = df['name'].apply(lambda x: x.upper())

# BAD: apply() for conditionals
df['category'] = df['price'].apply(lambda x: 'high' if x > 100 else 'low')
```

**Correct: Direct Vectorization**
```python
# GOOD: Vectorized multiplication
df['total'] = df['price'] * df['qty']

# GOOD: Vectorized string method
df['upper'] = df['name'].str.upper()

# GOOD: Vectorized conditional
df['category'] = np.where(df['price'] > 100, 'high', 'low')
```

### When apply() is Appropriate

**Complex operations that can't be vectorized:**
```python
# ACCEPTABLE: Complex function with no vectorized equivalent
def complex_calculation(row):
    # Multiple interdependent steps
    if row['type'] == 'A':
        return row['value'] * row['factor'] ** 2
    elif row['type'] == 'B':
        return row['value'] / row['denominator']
    else:
        return row['default_value']

df['result'] = df.apply(complex_calculation, axis=1)

# ACCEPTABLE: Calling external libraries per row
df['parsed_date'] = df['date_str'].apply(pd.to_datetime, errors='coerce')
```

### Performance Comparison

```python
import timeit

# Setup
df = pd.DataFrame({'price': range(10000), 'qty': range(10000)})

# iterrows: ~1000ms
timeit.timeit(lambda: [row['price'] * row['qty'] for _, row in df.iterrows()], number=10)

# apply with axis=1: ~100ms
timeit.timeit(lambda: df.apply(lambda row: row['price'] * row['qty'], axis=1), number=10)

# Vectorized: ~1ms (1000x faster than iterrows!)
timeit.timeit(lambda: df['price'] * df['qty'], number=10)
```

## 3. Chained Assignment (SettingWithCopyWarning)

**FORBIDDEN:**

### Understanding the Warning

**Problem:** Chained assignment may modify a copy instead of the original DataFrame

**Anti-Pattern: Chained Indexing**
```python
# BAD: SettingWithCopyWarning - might not modify original!
df[df['status'] == 'active']['price'] = df['price'] * 1.1

# BAD: Double indexing
df['2024']['sales'] = df['sales'] * 1.05  # SettingWithCopyWarning!

# BAD: Filtering then modifying
active_df = df[df['active'] == True]
active_df['price'] = active_df['price'] * 1.1  # Modifying copy!
```

**Correct: Use .loc for Explicit Indexing**
```python
# GOOD: Explicit .loc indexing
df.loc[df['status'] == 'active', 'price'] = df.loc[df['status'] == 'active', 'price'] * 1.1

# GOOD: More concise with multiplication assignment
df.loc[df['status'] == 'active', 'price'] *= 1.1

# GOOD: Multiple columns
df.loc[df['status'] == 'active', ['price', 'cost']] *= 1.1
```

### Working with DataFrame Subsets

**Anti-Pattern: Modifying Filtered DataFrame**
```python
# BAD: Create subset, then modify (may not affect original)
subset = df[df['category'] == 'A']
subset['price'] = subset['price'] * 1.1  # SettingWithCopyWarning!
```

**Correct: Explicit Copy or Direct Modification**
```python
# GOOD Option 1: Explicitly copy if you want a separate DataFrame
subset = df[df['category'] == 'A'].copy()
subset['price'] = subset['price'] * 1.1  # No warning, but doesn't affect original

# GOOD Option 2: Modify original directly with .loc
df.loc[df['category'] == 'A', 'price'] *= 1.1  # Modifies original
```

### Query Method Alternative

```python
# Alternative: Use .query() for complex filtering (cleaner syntax)
df.loc[df.query('status == "active" and price > 100').index, 'discount'] = 0.15
```

## 4. Memory Optimization

**MANDATORY:**

### Dtype Optimization

**Problem:** Default dtypes waste memory (int64, float64 use 8 bytes per value)

**Impact:** 87.5% memory savings possible with proper dtype selection

```python
# Check memory usage
print(df.memory_usage(deep=True))
print(df.info(memory_usage='deep'))

# BAD: Default int64 (8 bytes per value)
df['status_code'] = df['status_code']  # int64

# GOOD: Optimize to smallest dtype that fits range
df['status_code'] = df['status_code'].astype('int8')  # 0-127 range (1 byte)
df['small_int'] = df['small_int'].astype('int16')  # -32768 to 32767 (2 bytes)
df['medium_int'] = df['medium_int'].astype('int32')  # 4 bytes

# Float optimization
df['percentage'] = df['percentage'].astype('float32')  # Often sufficient (4 bytes)
```

### Categorical Data

**Use for:** Columns with repeating string values (massive memory savings)

```python
# BAD: Store repeated strings (huge memory usage)
df['category'] = df['category']  # object dtype, stores full string each time

# GOOD: Convert to categorical (stores codes + categories once)
df['category'] = df['category'].astype('category')

# Example savings
print(df['category'].memory_usage(deep=True))  # Before: 800 KB
df['category'] = df['category'].astype('category')
print(df['category'].memory_usage(deep=True))  # After: 100 KB (87.5% savings!)

# Read CSV with categorical columns
df = pd.read_csv('data.csv', dtype={'category': 'category', 'status': 'category'})
```

### Chunking for Large Files

```python
# BAD: Load entire 10GB file into memory
df = pd.read_csv('huge_file.csv')  # Out of memory error!

# GOOD: Process in chunks
chunk_size = 10000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    # Process each chunk
    result = process_chunk(chunk)
    save_result(result)

# Aggregate across chunks
totals = []
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    totals.append(chunk['sales'].sum())
total_sales = sum(totals)
```

### Sparse Data

```python
# For data with many zeros/missing values
df['sparse_column'] = pd.arrays.SparseArray(df['column'])

# Example: 95% zeros
print(df['column'].memory_usage())  # 800 KB
df['sparse'] = pd.arrays.SparseArray(df['column'])
print(df['sparse'].memory_usage())  # 40 KB (95% savings!)
```

## 5. Efficient GroupBy Operations

**MANDATORY:**

### Pre-Filter Before GroupBy

```python
# BAD: Group all data, then filter
result = df.groupby('category')['sales'].sum()
result = result[result > 1000]

# GOOD: Filter first, then group (faster)
filtered_df = df[df['active'] == True]
result = filtered_df.groupby('category')['sales'].sum()
```

### Multiple Aggregations

```python
# BAD: Multiple separate groupby calls (slow)
sum_sales = df.groupby('category')['sales'].sum()
mean_sales = df.groupby('category')['sales'].mean()
count_sales = df.groupby('category')['sales'].count()

# GOOD: Single groupby with agg() (much faster)
result = df.groupby('category')['sales'].agg(['sum', 'mean', 'count'])

# GOOD: Different aggregations per column
result = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': 'sum',
    'quantity': ['min', 'max']
})
```

### Named Aggregations

```python
# BEST: Named aggregations (cleaner output columns)
result = df.groupby('category').agg(
    total_sales=('sales', 'sum'),
    avg_sales=('sales', 'mean'),
    order_count=('order_id', 'count')
)
```

### GroupBy with Transform

```python
# Add group statistics back to original DataFrame
df['category_mean'] = df.groupby('category')['sales'].transform('mean')
df['pct_of_category'] = df['sales'] / df['category_mean']
```

## 6. Merge and Join Best Practices

**MANDATORY:**

### Validate Merge Keys

```python
# ALWAYS: Validate merge to catch data quality issues
result = df1.merge(df2, on='id', how='left', validate='1:1')
# validate options: '1:1', '1:m', 'm:1', 'm:m'

# Check for merge issues
result = df1.merge(df2, on='id', how='left', indicator=True)
print(result['_merge'].value_counts())
# left_only: rows only in df1
# right_only: rows only in df2
# both: successful matches
```

### Merge Performance

```python
# BAD: Merge on non-indexed columns (slow for large data)
result = df1.merge(df2, on='customer_id', how='left')

# GOOD: Set index for repeated merges (much faster)
df1_indexed = df1.set_index('customer_id')
df2_indexed = df2.set_index('customer_id')
result = df1_indexed.join(df2_indexed, how='left').reset_index()
```

### Multiple Key Merges

```python
# Merge on multiple columns
result = df1.merge(df2, on=['date', 'store_id'], how='inner')

# Different column names
result = df1.merge(df2, left_on='customer_id', right_on='cust_id', how='left')
```

## 7. Method Chaining

### Readable Pipelines

```python
# GOOD: Method chaining for data pipeline clarity
result = (
    df
    .query('status == "active"')
    .assign(
        total=lambda x: x['price'] * x['quantity'],
        discount=lambda x: x['total'] * 0.1
    )
    .groupby('category')
    .agg({'total': 'sum', 'discount': 'sum'})
    .reset_index()
    .sort_values('total', ascending=False)
)
```

### Assign for New Columns

```python
# GOOD: .assign() for multiple new columns in chain
df_processed = (
    df
    .assign(
        total=lambda x: x['price'] * x['qty'],
        tax=lambda x: x['total'] * 0.08,
        final_price=lambda x: x['total'] + x['tax']
    )
)
```

## 8. Index Operations

### When to Use Index

```python
# GOOD: Set index for time series data
df_ts = df.set_index('timestamp').sort_index()
df_ts['2024-01':'2024-03']  # Slice by date range

# GOOD: MultiIndex for hierarchical data
df_multi = df.set_index(['country', 'city', 'date'])
df_multi.loc[('USA', 'New York')]  # Access by hierarchy
```

### Reset Index After Operations

```python
# Most operations preserve index - reset when needed
result = (
    df
    .groupby('category')['sales']
    .sum()
    .reset_index()  # Convert index back to column
)
```

## 9. Streamlit Integration Patterns

### Efficient Caching with Pandas

```python
import streamlit as st

# GOOD: Cache DataFrame loading and processing
@st.cache_data(ttl=3600)
def load_and_process_data():
    df = pd.read_csv('large_data.csv')

    # Optimize dtypes for memory
    df['category'] = df['category'].astype('category')
    df['status_code'] = df['status_code'].astype('int8')

    # Pre-compute expensive operations
    df['total'] = df['price'] * df['quantity']

    return df

# Use cached data
df = load_and_process_data()
```

### Interactive Filtering

```python
# User filters
category = st.selectbox('Category', df['category'].unique())
min_price = st.slider('Min Price', 0, 1000, 100)

# Efficient filtering
filtered_df = df.query('category == @category and price >= @min_price')
st.dataframe(filtered_df)
```

### Download Processed Data

```python
# Provide CSV download of filtered data
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

## 10. Plotly Integration Patterns

### Aggregate Before Plotting

```python
import plotly.express as px

# BAD: Plot 1M rows (slow, cluttered)
fig = px.scatter(df, x='date', y='value')  # df has 1M rows

# GOOD: Aggregate first
df_daily = df.groupby('date').agg({'value': 'mean'}).reset_index()
fig = px.line(df_daily, x='date', y='value')  # 365 rows - fast!
```

### Prepare Data for Visualization

```python
# Pre-process for Plotly
df_viz = (
    df
    .groupby(['date', 'category'])
    .agg({'sales': 'sum'})
    .reset_index()
    .sort_values('date')
)

fig = px.line(df_viz, x='date', y='sales', color='category')
st.plotly_chart(fig, use_container_width=True)
```
