# Pandas Performance and Memory Optimization

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:pandas-performance, kw:groupby, kw:merge, kw:memory-optimization
**Keywords:** pandas performance, memory optimization, dtype, categorical, groupby, merge, join, eval, query, chunking, sparse, thread-safety, multiprocessing
**TokenBudget:** ~2550
**ContextTier:** Medium
**Depends:** 252-python-pandas-core.md

## Scope

**What This Rule Covers:**
Pandas performance optimization: memory-efficient dtypes, categorical data, groupby/merge best practices, eval/query expressions, chunked processing, and thread-safety.

**When to Load This Rule:**
- Optimizing Pandas memory usage
- Implementing efficient groupby or merge operations
- Processing large datasets in chunks
- Using eval()/query() for performance
- Running Pandas in concurrent/parallel environments

## References

### Dependencies

**Must Load First:**
- **252-python-pandas-core.md** - Core Pandas patterns

**Related:**
- **252b-python-pandas-io-integration.md** - Streamlit, Plotly, file I/O
- **251-python-datetime-core.md** - Datetime handling

### External Documentation
- [Enhancing Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [GroupBy Operations](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Merge, Join, Concatenate](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Categorical Data](https://pandas.pydata.org/docs/user_guide/categorical.html)

## Contract

### Inputs and Prerequisites

- Pandas 2.x+ DataFrames (from 252 core)
- Understanding of data types and memory layout

### Mandatory

- **Always:** Optimize dtypes for memory efficiency on datasets >100K rows
- **Always:** Use categorical for string columns with cardinality <50% of row count
- **Rule:** Pre-filter before groupby/aggregation
- **Rule:** Validate merge keys with `validate=` and `indicator=`
- **Rule:** Use eval()/query() for memory-efficient expressions on large DataFrames

### Forbidden

- Default int64/float64 when smaller types suffice (on datasets >100K rows)
- Multiple separate groupby calls when .agg() works
- Merging on non-indexed columns for repeated operations
- Using Pandas DataFrames across threads without copying

### Execution Steps

1. Profile memory with `df.memory_usage(deep=True)`
2. Optimize dtypes (int8/16/32, float32, category)
3. Pre-filter data before groupby
4. Validate merges with `validate=` parameter
5. Use eval()/query() for large DataFrame expressions
6. Chunk large file reads

### Output Format

Memory-optimized DataFrames, efficient groupby/merge operations, chunked processing pipelines.

### Validation

**Pre-Task-Completion Checks:**
- [ ] dtypes optimized for memory efficiency
- [ ] Categorical used for repeating strings
- [ ] GroupBy uses single .agg() call
- [ ] Merges validated with validate= parameter

### Design Principles

- **Memory Conscious:** Optimize dtypes and use categorical data
- **Batch Over Individual:** Single .agg() over multiple groupby calls
- **Validate Joins:** Always check merge key integrity
- **Thread-Safe:** Copy DataFrames for parallel workloads

### Post-Execution Checklist

- [ ] dtypes optimized
- [ ] Categorical data used for repeating strings
- [ ] GroupBy operations use .agg()
- [ ] Merge operations validated
- [ ] eval()/query() used where beneficial
- [ ] Large files chunked
- [ ] Thread-safety considered

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Default Dtypes Wasting Memory

**Problem:** Default int64/float64 use 8 bytes per value. With proper dtype selection, 87.5% memory savings are possible.

**Correct Pattern:** Use the smallest dtype that fits the data range.

```python
# Wrong: Default int64 (8 bytes per value)
df['status_code'] = df['status_code']  # int64

# Correct: Smallest dtype that fits range
df['status_code'] = df['status_code'].astype('int8')    # 0-127 (1 byte)
df['small_int'] = df['small_int'].astype('int16')        # -32768 to 32767 (2 bytes)
df['percentage'] = df['percentage'].astype('float32')    # Often sufficient (4 bytes)
```

### Anti-Pattern 2: Multiple Separate GroupBy Calls

**Problem:** Each groupby call scans the entire DataFrame. Multiple calls multiply scan time.

**Correct Pattern:** Use a single `.agg()` call to compute all aggregations in one scan.

```python
# Wrong: Three full scans
sum_sales = df.groupby('category')['sales'].sum()
mean_sales = df.groupby('category')['sales'].mean()
count_sales = df.groupby('category')['sales'].count()

# Correct: Single scan with .agg()
result = df.groupby('category')['sales'].agg(['sum', 'mean', 'count'])
```

## Memory Optimization

### Dtype Optimization

```python
# Check memory usage
print(df.memory_usage(deep=True))
print(df.info(memory_usage='deep'))

# Optimize integer types
df['status_code'] = df['status_code'].astype('int8')
df['small_int'] = df['small_int'].astype('int16')
df['medium_int'] = df['medium_int'].astype('int32')

# Optimize float types
df['percentage'] = df['percentage'].astype('float32')
```

### Categorical Data

Use for columns with repeating string values (up to 90%+ memory savings for low-cardinality columns):

```python
# Convert to categorical
df['category'] = df['category'].astype('category')
# Example: 800 KB object column becomes 100 KB categorical (87.5% savings)

# Read CSV with categorical columns
df = pd.read_csv('data.csv', dtype={'category': 'category', 'status': 'category'})
```

### Chunking for Large Files

```python
# Process in chunks instead of loading entire file
chunk_size = 10_000
totals = []
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    totals.append(chunk['sales'].sum())
total_sales = sum(totals)
```

### Sparse Data

```python
# For data with many zeros/missing values (e.g., 95% zeros)
df['sparse_column'] = pd.arrays.SparseArray(df['column'])
# 800 KB dense column becomes 40 KB sparse (95% savings)
```

## Efficient GroupBy Operations

### Pre-Filter Before GroupBy

```python
# BAD: Group all data, then filter results
result = df.groupby('category')['sales'].sum()
result = result[result > 1000]

# GOOD: Filter first, then group (faster)
filtered_df = df[df['active'] == True]
result = filtered_df.groupby('category')['sales'].sum()
```

### Multiple Aggregations

```python
# Different aggregations per column
result = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': 'sum',
    'quantity': ['min', 'max'],
})

# Named aggregations (cleaner output)
result = df.groupby('category').agg(
    total_sales=('sales', 'sum'),
    avg_sales=('sales', 'mean'),
    order_count=('order_id', 'count'),
)
```

### GroupBy with Transform

```python
# Add group statistics back to original DataFrame
df['category_mean'] = df.groupby('category')['sales'].transform('mean')
df['pct_of_category'] = df['sales'] / df['category_mean']
```

## Merge and Join Best Practices

### Validate Merge Keys

```python
# ALWAYS validate merges to catch data quality issues
result = df1.merge(df2, on='id', how='left', validate='1:1')
# validate options: '1:1', '1:m', 'm:1', 'm:m'

# Check for merge issues
result = df1.merge(df2, on='id', how='left', indicator=True)
print(result['_merge'].value_counts())
```

### Merge Performance

```python
# For repeated merges, index the join columns first
df1_indexed = df1.set_index('customer_id')
df2_indexed = df2.set_index('customer_id')
result = df1_indexed.join(df2_indexed, how='left').reset_index()
```

## Expression Evaluation

### eval() for Computed Columns

```python
# Memory-efficient: avoids creating intermediate arrays
df = df.eval('total = price * quantity')
df = df.eval('margin = (price - cost) / price * 100')

# Multiple expressions
df = df.eval('''
    total = price * quantity
    tax = total * 0.08
    final_price = total + tax
''')
```

### query() vs eval()

```python
# query() filters rows
expensive = df.query('price > 100 and category == "electronics"')

# eval() computes columns
df = df.eval('profit = revenue - cost')

# Both support @variable syntax
min_price = 50
df.query('price >= @min_price')
```

## Thread-Safety

Pandas DataFrames are NOT thread-safe. Concurrent read-write access from multiple threads causes data corruption.

```python
# BAD: Shared DataFrame across threads
import threading

shared_df = pd.DataFrame(...)
def worker(df):
    df['new_col'] = df['col'] * 2  # Race condition!

# GOOD: Copy for each worker, or use multiprocessing
import multiprocessing

def worker(df_copy):
    df_copy['new_col'] = df_copy['col'] * 2
    return df_copy

# Use multiprocessing for parallel pandas workloads
with multiprocessing.Pool(4) as pool:
    chunks = np.array_split(df, 4)
    results = pool.map(worker, chunks)
    df_result = pd.concat(results)
```

## Error Recovery

### Dtype Conversion Failures

```python
# Safe dtype conversion with error handling
try:
    df['col'] = df['col'].astype('int8')
except (ValueError, OverflowError):
    # Values outside int8 range (-128 to 127)
    df['col'] = pd.to_numeric(df['col'], downcast='integer')
```

### Merge Key Mismatches

```python
# Detect merge issues before they cause silent data loss
result = df1.merge(df2, on='id', how='left', indicator=True)
unmatched = result[result['_merge'] == 'left_only']
if len(unmatched) > 0:
    print(f"WARNING: {len(unmatched)} rows in df1 have no match in df2")
result = result.drop(columns='_merge')
```

### Chunked Processing Failures

```python
# Resilient chunk processing — skip bad chunks instead of failing entirely
results = []
for i, chunk in enumerate(pd.read_csv('huge.csv', chunksize=10_000)):
    try:
        results.append(chunk['sales'].sum())
    except Exception as e:
        print(f"WARNING: Chunk {i} failed: {e}, skipping")
total = sum(results)
```

### Empty DataFrame Edge Cases

```python
# Always guard against empty DataFrames after filtering
filtered = df.query('status == "active"')
if filtered.empty:
    print("No active records found")
    result = pd.DataFrame(columns=df.columns)  # Return empty with same schema
else:
    result = filtered.groupby('category')['sales'].sum().reset_index()
```
