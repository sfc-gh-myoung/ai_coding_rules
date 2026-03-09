# Pandas Core Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:pandas, kw:dataframe
**Keywords:** pandas, DataFrame, vectorization, SettingWithCopyWarning, method chaining, loc, iloc, np.where, np.select, apply, iterrows
**TokenBudget:** ~2200
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Core Pandas best practices: vectorization over loops, explicit indexing with .loc/.iloc, method chaining, conditional operations, and anti-pattern avoidance.

**When to Load This Rule:**
- Working with Pandas DataFrames or Series
- Debugging SettingWithCopyWarning errors
- Replacing loops with vectorized operations
- Building data transformation pipelines

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Modern Python tooling and practices

**Related:**
- **251-python-datetime-core.md** - Datetime handling for Pandas
- **252a-python-pandas-performance.md** - Memory optimization, groupby, merge, eval/query
- **252b-python-pandas-io-integration.md** - Streamlit, Plotly, file I/O integration

### External Documentation
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [Enhancing Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [Indexing and Selecting Data](https://pandas.pydata.org/docs/user_guide/indexing.html)

## Contract

### Inputs and Prerequisites

Python 3.11+, pandas 2.x+, basic NumPy knowledge

### Mandatory

- **Always:** Use vectorized operations instead of loops (10x-100x+ faster)
- **Always:** Use .loc/.iloc for explicit indexing (prevents SettingWithCopyWarning)
- **Rule:** Use method chaining for clear data pipelines
- **Rule:** Use np.where/np.select for conditional column operations

### Forbidden

- `iterrows()` for computation (read-only display OK)
- `apply()` when vectorization is possible
- Chained assignment without .loc (e.g., `df[mask]['col'] = val`)
- `df.append()` (deprecated in Pandas 2.x)
- `inplace=True` (generally discouraged; use assignment instead)

### Execution Steps

1. Use vectorized operations instead of loops
2. Use .loc/.iloc for explicit indexing
3. Use method chaining for transformation pipelines
4. Profile performance for operations on large DataFrames
5. Validate with: `uvx ruff check .` and `uv run pytest tests/`

### Output Format

Performant Pandas code with vectorized operations, explicit indexing, and clear method chains.

### Validation

**Pre-Task-Completion Checks:**
- Vectorized operations used instead of iterrows() for computation
- .loc/.iloc used for explicit indexing (no chained assignment)
- Method chaining used for data pipelines

**Negative Tests:**
- iterrows() loop (should be very slow)
- Chained assignment (should warn)

### Design Principles

- **Vectorization First:** Always prefer vectorized operations over loops (10x-100x+ faster)
- **Explicit Indexing:** Use .loc/.iloc to prevent SettingWithCopyWarning
- **Method Chaining:** Chain operations for clarity and efficiency

### Post-Execution Checklist

- [ ] Vectorized operations used instead of iterrows()
- [ ] apply() avoided when vectorization possible
- [ ] .loc/.iloc used for explicit indexing
- [ ] Method chaining used for data pipelines
- [ ] No deprecated APIs (df.append, inplace=True)

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: iterrows() for Computation

**Problem:** Python loops with iterrows() are 50x-100x+ slower than vectorized operations due to Python interpreter overhead per iteration.

**Correct Pattern:** Use vectorized Pandas operations for column arithmetic.

```python
# Wrong: 100x slower for large DataFrames
for idx, row in df.iterrows():
    df.at[idx, 'total'] = row['price'] * row['quantity']

# Correct: Vectorized operation (100x+ faster)
df['total'] = df['price'] * df['quantity']
```

### Anti-Pattern 2: Chained Assignment (SettingWithCopyWarning)

**Problem:** Chained indexing may modify a copy instead of the original DataFrame. Changes silently lost.

**Correct Pattern:** Use `.loc` for explicit indexing to modify the original DataFrame.

```python
# Wrong: May not modify original DataFrame
df[df['status'] == 'active']['price'] = df['price'] * 1.1

# Correct: Explicit .loc indexing
df.loc[df['status'] == 'active', 'price'] *= 1.1
```

### Anti-Pattern 3: apply() When Vectorization Works

**Problem:** apply() with axis=1 is nearly as slow as iterrows().

**Correct Pattern:** Use vectorized arithmetic instead of row-wise apply.

```python
# Wrong: Unnecessary apply() (10x slower)
df['total'] = df.apply(lambda row: row['price'] * row['qty'], axis=1)

# Correct: Vectorized multiplication
df['total'] = df['price'] * df['qty']
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing DataFrame operations BEFORE optimizing** - Check for iterrows(), apply(), chained assignment
> 2. **Profile actual performance** - Measure before and after
> 3. **Never speculate about DataFrame shape** - Use df.shape, df.dtypes
> 4. **Check memory usage** - Use df.memory_usage(deep=True)

## Vectorization Patterns

### Simple Arithmetic

```python
df['total'] = df['price'] * df['quantity']
df['discount'] = df['price'] * 0.1
df['final_price'] = df['price'] - df['discount']
```

### Conditional Operations

```python
import numpy as np

# Single condition
df['category'] = np.where(df['price'] > 100, 'expensive', 'affordable')

# Multiple conditions
df['tier'] = np.select(
    [df['score'] >= 90, df['score'] >= 70, df['score'] >= 50],
    ['A', 'B', 'C'],
    default='F'
)
```

### String Operations

```python
df['upper_name'] = df['name'].str.upper()
df['first_word'] = df['description'].str.split().str[0]
df['contains_keyword'] = df['text'].str.contains('important', case=False)
```

### When iterrows() is Acceptable

Read-only operations where vectorization is not possible:

```python
# ACCEPTABLE: Display in Streamlit (read-only)
for _, row in df.iterrows():
    st.metric(row['metric_name'], f"{row['value']:.2f}")

# ACCEPTABLE: External API calls per row
for _, row in df.iterrows():
    result = complex_external_api_call(row['id'])
```

### When apply() is Appropriate

Complex operations with no vectorized equivalent:

```python
def complex_calculation(row):
    if row['type'] == 'A':
        return row['value'] * row['factor'] ** 2
    elif row['type'] == 'B':
        return row['value'] / row['denominator']
    else:
        return row['default_value']

df['result'] = df.apply(complex_calculation, axis=1)
```

## Explicit Indexing with .loc/.iloc

### Preventing SettingWithCopyWarning

```python
# BAD: Chained indexing - may modify copy
df[df['status'] == 'active']['price'] = 100

# GOOD: .loc for explicit indexing
df.loc[df['status'] == 'active', 'price'] = 100

# GOOD: Multiple columns
df.loc[df['status'] == 'active', ['price', 'cost']] *= 1.1
```

### Working with DataFrame Subsets

```python
# GOOD: Explicit copy if you want a separate DataFrame
subset = df[df['category'] == 'A'].copy()
subset['price'] *= 1.1  # No warning, independent copy

# GOOD: Modify original directly
df.loc[df['category'] == 'A', 'price'] *= 1.1
```

### Query Method for Filtering

```python
# Cleaner syntax for complex filters
expensive = df.query('price > 100 and category == "electronics"')

# Reference local variables with @
min_price = 50
filtered = df.query('price >= @min_price')
```

## Method Chaining

### Readable Pipelines

```python
result = (
    df
    .query('status == "active"')
    .assign(
        total=lambda x: x['price'] * x['quantity'],
        discount=lambda x: x['total'] * 0.1,
    )
    .groupby('category')
    .agg({'total': 'sum', 'discount': 'sum'})
    .reset_index()
    .sort_values('total', ascending=False)
)
```

### Assign for New Columns in Chain

```python
df_processed = (
    df
    .assign(
        total=lambda x: x['price'] * x['qty'],
        tax=lambda x: x['total'] * 0.08,
        final_price=lambda x: x['total'] + x['tax'],
    )
)
```

## Index Operations

### When to Use Index

```python
# Time series data
df_ts = df.set_index('timestamp').sort_index()
df_ts['2024-01':'2024-03']  # Slice by date range

# MultiIndex for hierarchical data
df_multi = df.set_index(['country', 'city', 'date'])
df_multi.loc[('USA', 'New York')]
```

### Reset Index After Operations

```python
result = (
    df
    .groupby('category')['sales']
    .sum()
    .reset_index()  # Convert index back to column
)
```
