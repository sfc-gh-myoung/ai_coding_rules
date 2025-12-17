# Python DateTime Handling Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** datetime, pandas, timezone, datetime64, timedelta, UTC, date arithmetic, tz_localize, tz_convert, datetime.now(UTC)
**TokenBudget:** ~3700
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Establish comprehensive datetime handling practices across Python, Pandas, Plotly, and Streamlit to prevent type errors, timezone bugs, and performance issues while ensuring Pandas 2.x compatibility and cross-library interoperability.

## Rule Scope

DateTime handling for Python stdlib, Pandas, Plotly, Streamlit with focus on type safety, timezone management, date arithmetic, and performance optimization

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use datetime.now(UTC)** - NEVER use deprecated datetime.utcnow()
- **Always be timezone-aware** - Use UTC or explicit timezones, never naive datetimes
- **Use pd.to_datetime()** - With format= parameter for performance
- **Convert before plotting** - Use .to_pydatetime() for Plotly/Streamlit
- **Pandas 2.x compatibility** - Use datetime64[ns, UTC] not datetime64[ns]
- **Never compare mixed types** - Convert pd.Timestamp ↔ datetime before comparison

**Quick Checklist:**
- [ ] All datetime objects are timezone-aware
- [ ] datetime.now(UTC) used (not utcnow())
- [ ] pd.to_datetime() includes format parameter
- [ ] Timezone conversions use tz_localize/tz_convert
- [ ] Plotly/Streamlit dates converted with to_pydatetime()
- [ ] Date arithmetic uses appropriate types
- [ ] Type conversions handled explicitly

## Contract

<contract>
<inputs_prereqs>
Python 3.11+, pandas 2.x+, understanding of datetime types, timezone awareness requirements
</inputs_prereqs>

<mandatory>
pd.to_datetime(), pd.Timestamp, pd.Timedelta, pd.DateOffset, datetime.datetime, dt accessor methods, tz_localize(), tz_convert(), strftime(), to_pydatetime()
</mandatory>

<forbidden>
Mixed datetime type comparisons without conversion, hardcoded timezone offsets, parsing dates without format specification, ignoring timezone information
</forbidden>

<steps>
1. Use consistent datetime types within operations (convert mixed types)
2. Always be explicit about timezones (tz_localize, tz_convert)
3. Parse dates with format specification when structure is known
4. Use pd.Timedelta for duration arithmetic, DateOffset for calendar arithmetic
5. Convert to Python datetime for cross-library compatibility when needed
6. Validate datetime columns before visualization
7. Optimize large time series for performance
</steps>

<output_format>
Type-safe datetime operations, explicit timezone handling, performant time series code
</output_format>

<validation>
All datetime operations type-compatible, timezone handling explicit, no mixed-type comparison errors, performance tested on large datasets
</validation>

<design_principles>
- **Type Safety First:** Never mix datetime types in comparisons without explicit conversion
- **Timezone Explicit:** Always specify timezone handling (UTC default, convert as needed)
- **Pandas 2.x Compatible:** Use patterns that work with strict type checking in Pandas 2.x+
- **Performance Aware:** Optimize datetime operations for large time series
- **Cross-Library Safe:** Ensure datetime types work across Python, Pandas, Plotly, Streamlit
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Comparing pd.Timestamp with Python datetime Without Conversion**
```python
# Bad: Direct comparison causes TypeError in Pandas 2.x+
import pandas as pd
from datetime import datetime, UTC

pd_ts = pd.Timestamp('2024-10-23 14:30:00', tz='UTC')
py_dt = datetime.now(UTC)
if pd_ts > py_dt:  # TypeError: Cannot compare tz-aware with tz-naive
    print("Future date")
```
**Problem:** Mixed datetime types cause TypeError in Pandas 2.x; implicit conversions unreliable; timezone mismatch errors; code breaks on upgrade

**Correct Pattern:**
```python
# Good: Explicit type conversion before comparison
pd_ts = pd.Timestamp('2024-10-23 14:30:00', tz='UTC')
py_dt = datetime.now(UTC)
if pd_ts.to_pydatetime() > py_dt:  # Explicit conversion
    print("Future date")
# OR: Convert both to same type
if pd.Timestamp(py_dt) > pd_ts:
    print("Future date")
```
**Benefits:** Type-safe comparisons; Pandas 2.x compatible; explicit timezone handling; no implicit conversion surprises


**Anti-Pattern 2: Using Deprecated `datetime.utcnow()`**
```python
# Bad: Deprecated API returns naive datetime
from datetime import datetime
timestamp = datetime.utcnow()  # Deprecated, naive datetime
```
**Problem:** Deprecated in Python 3.12+; returns naive datetime (no timezone); timezone-unaware comparisons fail; will be removed in future versions

**Correct Pattern:**
```python
# Good: Modern timezone-aware datetime
from datetime import datetime, UTC
timestamp = datetime.now(UTC)  # Timezone-aware, future-proof
```
**Benefits:** Timezone-aware datetime; Python 3.11+ best practice; no deprecation warnings; explicit UTC handling; future-proof


**Anti-Pattern 3: Parsing Dates Without Format Specification**
```python
# Bad: Slow inference on large datasets
import pandas as pd
df = pd.read_csv('large_file.csv')
df['date'] = pd.to_datetime(df['date'])  # Infers format, slow
```
**Problem:** 10-100x slower on large datasets; format inference overhead; inconsistent parsing; may misinterpret ambiguous dates (MM/DD vs DD/MM)

**Correct Pattern:**
```python
# Good: Explicit format specification for performance
df = pd.read_csv('large_file.csv')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')  # Fast, explicit
```
**Benefits:** 10-100x faster parsing; consistent date interpretation; no ambiguity; predictable behavior across locales


**Anti-Pattern 4: Using Timedelta for Calendar Arithmetic**
```python
# Bad: Timedelta doesn't handle month/year boundaries correctly
from datetime import datetime, timedelta, UTC
start = datetime(2024, 1, 31, tzinfo=UTC)
next_month = start + timedelta(days=30)  # Feb 29, not Mar 31!
```
**Problem:** Month lengths vary (28-31 days); leap years not handled; off-by-one errors; "add 1 month" becomes "add 30 days"; incorrect for business logic

**Correct Pattern:**
```python
# Good: Use DateOffset for calendar arithmetic
import pandas as pd
from datetime import datetime, UTC
start = pd.Timestamp(datetime(2024, 1, 31, tzinfo=UTC))
next_month = start + pd.DateOffset(months=1)  # Correctly yields Feb 29
next_year = start + pd.DateOffset(years=1)    # Handles leap years
```
**Benefits:** Calendar-aware arithmetic; handles month boundaries; leap year support; business logic correctness; "add 1 month" means "same day next month"

## Post-Execution Checklist

- [ ] All datetime type conversions handled explicitly (no mixed-type comparisons)
- [ ] Timezone operations are explicit (tz_localize, tz_convert)
- [ ] Date parsing uses format specification when structure is known
- [ ] Timedelta used for duration arithmetic, DateOffset for calendar arithmetic
- [ ] Large time series optimized (string conversion, downsampling, aggregation)
- [ ] Pandas 2.x compatibility validated (no TypeError on comparisons)
- [ ] Cross-library datetime handling tested (Python, Pandas, Plotly, Streamlit)
- [ ] Helper function (ensure_python_datetime) used for mixed-type scenarios

## Validation

- **Success Checks:** All datetime operations type-safe, timezone handling explicit, no Pandas 2.x TypeErrors, large time series render quickly, cross-library compatibility verified
- **Negative Tests:** Mixed datetime comparison without conversion (should fail), timezone-naive comparison with tz-aware (should warn), ambiguous date parsing (should coerce or error), inefficient datetime loops (should be slow)

> **Investigation Required**
> When applying this rule:
> 1. **Read data files BEFORE datetime operations** - Check existing date formats, timezone awareness
> 2. **Verify Pandas version** - Check if Pandas 2.x compatibility needed
> 3. **Never assume datetime types** - Check df.dtypes to see datetime64 vs object
> 4. **Check existing timezone handling** - Read code to understand if tz-aware or naive
> 5. **Test datetime conversions** - Verify Plotly/Streamlit compatibility after changes
>
> **Anti-Pattern:**
> "Converting to datetime... (without checking existing format)"
> "Using datetime.utcnow()... (deprecated method)"
>
> **Correct Pattern:**
> "Let me check your datetime column formats first."
> [reads data, checks dtypes, reviews timezone handling]
> "I see you have timezone-aware datetime64[ns, UTC]. Converting for Plotly with to_pydatetime()..."

## Output Format Examples

```python
import datetime
import pandas as pd
import streamlit as st

# Helper for type-safe datetime conversions
def ensure_python_datetime(dt):
    """Convert any datetime-like to Python datetime."""
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, datetime.datetime):
        return dt
    if hasattr(dt, 'to_pydatetime'):
        return dt.to_pydatetime()
    return pd.to_datetime(dt).to_pydatetime()

# Parse dates with explicit format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Explicit timezone handling
df['date'] = df['date'].dt.tz_localize('UTC')
df['date_eastern'] = df['date'].dt.tz_convert('US/Eastern')

# Date arithmetic
df['next_week'] = df['date'] + pd.Timedelta(days=7)
df['next_month'] = df['date'] + pd.DateOffset(months=1)

# Type-safe comparisons
start_date = ensure_python_datetime(df['date'].min())
end_date = ensure_python_datetime(df['date'].max())

# Streamlit integration
user_date = st.date_input('Select Date')
user_ts = pd.Timestamp(user_date)
filtered_df = df[df['date'] >= user_ts]
```

## References

### External Documentation

**Python datetime:**
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html) - Official Python datetime module reference
- [Python datetime Tutorial](https://docs.python.org/3/library/datetime.html#datetime-objects) - datetime object methods and properties

**Pandas datetime:**
- [Pandas Time Series / Date Functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html) - Comprehensive time series guide
- [Pandas to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) - Date parsing reference
- [Pandas Timedelta](https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.html) - Duration arithmetic
- [Pandas DateOffset](https://pandas.pydata.org/docs/reference/api/pandas.tseries.offsets.DateOffset.html) - Calendar-aware arithmetic
- [Pandas dt accessor](https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.html) - Datetime properties and methods

**Timezone handling:**
- [pytz Documentation](https://pypi.org/project/pytz/) - Timezone database for Python
- [Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html) - Python 3.9+ timezone support

### Related Rules
- **Python Core**: `rules/200-python-core.md` - Modern Python tooling and practices
- **Pandas Best Practices**: `rules/252-pandas-best-practices.md` - Pandas performance and anti-patterns
- **Streamlit Visualization**: `rules/101a-snowflake-streamlit-visualization.md` - Plotly datetime visualization patterns
- **Streamlit Performance**: `rules/101b-snowflake-streamlit-performance.md` - Caching and optimization for time series
- **Data Science Analytics**: `rules/920-data-science-analytics.md` - Time series analysis and ML workflows

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 DateTime Optimizations:**
> - Investigation-first: Check actual datetime types in DataFrames before making recommendations
> - Parallel validation: Test datetime conversions across multiple scenarios simultaneously
> - Context awareness: Reference existing datetime patterns from 101a and 500 rules
> - Error prevention: Emphasize Pandas 2.x compatibility in all datetime code

## 1. DateTime Type System

### Three Main DateTime Representations

**Python datetime.datetime:**
```python
import datetime

# Native Python datetime
py_dt = datetime.datetime(2024, 10, 23, 14, 30, 0)
py_dt_now = datetime.datetime.now()

# Timezone-aware
import pytz
py_dt_utc = datetime.datetime.now(pytz.UTC)
```

**Pandas Timestamp (extends Python datetime):**
```python
import pandas as pd

# Pandas Timestamp (compatible with Python datetime)
pd_ts = pd.Timestamp('2024-10-23 14:30:00')
pd_ts_now = pd.Timestamp.now()

# Timezone-aware Timestamp
pd_ts_utc = pd.Timestamp.now(tz='UTC')
```

**NumPy datetime64 / Pandas Series dtype:**
```python
import numpy as np

# NumPy datetime64
np_dt = np.datetime64('2024-10-23T14:30:00')

# Pandas Series with datetime64[ns] dtype (most common)
df['date'] = pd.to_datetime(df['date'])  # Creates datetime64[ns] column
print(df['date'].dtype)  # datetime64[ns]
```

### Type Hierarchy and Compatibility

```
datetime64[ns] (NumPy/Pandas Series)
    ↓
pd.Timestamp (Pandas scalar, extends datetime.datetime)
    ↓
datetime.datetime (Python stdlib)
```

**Key Insight:** Pandas Series operations return datetime64[ns] arrays, but individual elements are pd.Timestamp objects.

## 2. Type Conversions and Safety

**MANDATORY:**

### Universal DateTime Conversion Helper

**Problem:** Pandas 2.x enforces strict type checking, causing TypeErrors when comparing pd.Timestamp with datetime.datetime.

**Solution:** Normalize all datetime-like objects to Python datetime for comparisons.

```python
import datetime
import pandas as pd

def ensure_python_datetime(dt):
    """
    Convert any datetime-like object to Python datetime.

    Handles:
    - None/NaT: returns None
    - datetime.datetime: unchanged
    - pd.Timestamp: converted via to_pydatetime()
    - Strings: parsed via pd.to_datetime

    Safe for Pandas 2.x+ strict type checking.
    """
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, datetime.datetime):
        return dt
    if hasattr(dt, 'to_pydatetime'):
        return dt.to_pydatetime()
    # Parse strings or other formats
    return pd.to_datetime(dt).to_pydatetime()
```

### Common Use Case: Mixed Type Comparisons

**Anti-Pattern: Direct comparison (Pandas 2.x TypeError)**
```python
# BAD: Comparing pd.Timestamp with Python datetime
for timestamp in failure_timestamps:
    failure_time = pd.to_datetime(timestamp).to_pydatetime()  # Python datetime
    # df["hour"].min() returns pd.Timestamp - TYPE MISMATCH!
    if df["hour"].min() <= failure_time <= df["hour"].max():  # TypeError!
        add_marker(failure_time)
```

**Correct Pattern: Normalize types**
```python
# GOOD: Convert all to Python datetime for consistency
for timestamp in failure_timestamps:
    try:
        # Normalize all datetime-like objects
        failure_time = ensure_python_datetime(timestamp)
        hour_min = ensure_python_datetime(df["hour"].min())
        hour_max = ensure_python_datetime(df["hour"].max())

        # Now all are Python datetimes - comparison safe!
        if hour_min and hour_max and hour_min <= failure_time <= hour_max:
            add_marker(failure_time)
    except Exception as e:
        st.warning(f"Could not add marker: {type(e).__name__}: {str(e)[:100]}")
```

### DataFrame-Level Type Conversions

```python
# Convert string column to datetime
df['date'] = pd.to_datetime(df['date'])

# Convert datetime to string (for display or Plotly performance)
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

# Convert to Python datetime objects (for compatibility)
df['date_python'] = df['date'].apply(lambda x: x.to_pydatetime() if pd.notna(x) else None)

# Convert timezone-aware to tz-naive (remove timezone info)
df['date'] = df['date'].dt.tz_localize(None)
```

## 3. Date Parsing Best Practices

**MANDATORY:**

### Explicit Format Specification

**Always:** Specify date format when structure is known (10x+ faster, prevents ambiguity)

```python
# GOOD: Explicit format (fast, unambiguous)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# GOOD: ISO 8601 format (recommended standard)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S')

# ACCEPTABLE: Infer format (slower, but flexible)
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)

# BAD: No format specification (ambiguous MM/DD vs DD/MM)
df['date'] = pd.to_datetime(df['date'])  # 01/02/2024 - Jan 2 or Feb 1?
```

### Error Handling During Parsing

```python
# Handle parsing errors gracefully
df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Invalid becomes NaT
df['date'] = pd.to_datetime(df['date'], errors='ignore')  # Keep original on error

# Report parsing failures
invalid_dates = df[df['date'].isna()]
if len(invalid_dates) > 0:
    st.warning(f"{len(invalid_dates)} dates failed to parse")
```

### Read CSV with Date Parsing

```python
# BEST: Parse dates during CSV read (most efficient)
df = pd.read_csv('data.csv',
                 parse_dates=['order_date', 'ship_date'],
                 date_format='%Y-%m-%d')

# For multiple date formats
df = pd.read_csv('data.csv',
                 parse_dates=['order_date'],
                 date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d', errors='coerce'))
```

## 4. Timezone Management

**MANDATORY:**

### Core Principles

**Always:**
- Store data in UTC
- Convert to local timezone only for display
- Be explicit about timezone operations

### Timezone Operations

**Make timezone-aware (localize):**
```python
# Add timezone info to tz-naive datetime
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].dt.tz_localize('UTC')  # Assume UTC

# Handle ambiguous times (DST transitions)
df['date'] = df['date'].dt.tz_localize('US/Eastern', ambiguous='infer')
```

**Convert between timezones:**
```python
# Convert from one timezone to another
df['date_utc'] = df['date'].dt.tz_convert('UTC')
df['date_eastern'] = df['date'].dt.tz_convert('US/Eastern')
df['date_pacific'] = df['date'].dt.tz_convert('US/Pacific')
```

**Remove timezone info (make tz-naive):**
```python
# Remove timezone (for libraries that don't support tz-aware)
df['date'] = df['date'].dt.tz_localize(None)

# Alternative: Convert to UTC first, then remove tz
df['date'] = df['date'].dt.tz_convert('UTC').dt.tz_localize(None)
```

### Streamlit Timezone Display

```python
import streamlit as st

# User selects timezone
user_tz = st.selectbox('Timezone', ['UTC', 'US/Eastern', 'US/Pacific', 'Europe/London'])

# Convert for display
df_display = df.copy()
df_display['date'] = df_display['date'].dt.tz_convert(user_tz)
st.dataframe(df_display)
```

## 5. Date Arithmetic and Math

**MANDATORY:**

### Timedelta (Duration Arithmetic)

**Use for:** Fixed time periods (days, hours, seconds)

```python
# Add/subtract fixed durations
df['next_week'] = df['date'] + pd.Timedelta(days=7)
df['yesterday'] = df['date'] - pd.Timedelta(days=1)
df['in_2_hours'] = df['timestamp'] + pd.Timedelta(hours=2)

# Calculate duration between dates
df['days_between'] = (df['end_date'] - df['start_date']).dt.days
df['hours_between'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
```

### DateOffset (Calendar-Aware Arithmetic)

**Use for:** Calendar periods that vary (months, years, business days)

```python
from pandas.tseries.offsets import DateOffset, BDay, MonthEnd

# Add months (handles varying month lengths)
df['next_month'] = df['date'] + DateOffset(months=1)

# Next business day (skips weekends and holidays)
df['next_business_day'] = df['date'] + BDay(1)

# End of month
df['month_end'] = df['date'] + MonthEnd(0)  # Current month end
df['next_month_end'] = df['date'] + MonthEnd(1)  # Next month end
```

### Common Date Math Patterns

```python
# Age calculation
df['age_years'] = (pd.Timestamp.now() - df['birth_date']).dt.days // 365

# Days since event
df['days_since_order'] = (pd.Timestamp.now() - df['order_date']).dt.days

# Weeks between dates
df['weeks_between'] = (df['end_date'] - df['start_date']).dt.days // 7

# Quarter start/end
df['quarter_start'] = df['date'].dt.to_period('Q').dt.start_time
df['quarter_end'] = df['date'].dt.to_period('Q').dt.end_time
```

## 6. Performance Optimization for Time Series

**MANDATORY:**

### Plotly Rendering Optimization

**Problem:** Plotly is slow rendering datetime x-axes with large datasets

**Solution:** Convert to strings when datetime interactivity not needed

```python
@st.cache_data(ttl=3600)
def load_time_series_data():
    df = session.sql("SELECT date, value FROM time_series").to_pandas()

    # For Plotly: Convert to string for faster rendering
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

    return df

# Use string column for x-axis
df = load_time_series_data()
fig = px.line(df, x='date_str', y='value')
st.plotly_chart(fig, use_container_width=True)
```

### Timezone-Naive for Performance

```python
# Remove timezone if not needed (faster operations)
df['date'] = df['date'].dt.tz_localize(None)

# Or convert to UTC and remove timezone
df['date'] = df['date'].dt.tz_convert('UTC').dt.tz_localize(None)
```

### Downsample Large Time Series

```python
# Resample to reduce data points
df_hourly = df.set_index('timestamp').resample('H').mean().reset_index()
df_daily = df.set_index('timestamp').resample('D').mean().reset_index()

# For visualization: Aggregate before plotting
@st.cache_data(ttl=3600)
def load_aggregated_data(granularity='day'):
    query = f"""
    SELECT
        DATE_TRUNC('{granularity}', timestamp) as date,
        AVG(value) as avg_value,
        COUNT(*) as count
    FROM time_series_table
    GROUP BY 1
    ORDER BY 1
    """
    return session.sql(query).to_pandas()
```

## 7. Streamlit Integration Patterns

### Date Input Widgets

```python
import streamlit as st
import pandas as pd

# Date range selection
start_date = st.date_input('Start Date', value=pd.to_datetime('2024-01-01'))
end_date = st.date_input('End Date', value=pd.Timestamp.now())

# Convert to pandas Timestamp for filtering
start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date)

# Filter DataFrame
filtered_df = df[(df['date'] >= start_ts) & (df['date'] <= end_ts)]
```

### Datetime Display Formatting

```python
# Format dates for display
df_display = df.copy()
df_display['date'] = df_display['date'].dt.strftime('%B %d, %Y')  # "October 23, 2024"

st.dataframe(df_display)

# Or use styling
st.dataframe(
    df.style.format({'date': lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else 'N/A'})
)
```

## 8. Anti-Patterns and Common Errors

**Anti-Pattern 1: Mixed datetime type comparisons**
```python
# BAD: Pandas 2.x TypeError
failure_time = datetime.datetime.now()
if df["timestamp"].min() <= failure_time <= df["timestamp"].max():  # TypeError!
    process()
```
**Problem:** Comparing pd.Timestamp (from .min()/.max()) with Python datetime causes TypeError in Pandas 2.x

**Correct:**
```python
# GOOD: Normalize to Python datetime
failure_time = ensure_python_datetime(datetime.datetime.now())
ts_min = ensure_python_datetime(df["timestamp"].min())
ts_max = ensure_python_datetime(df["timestamp"].max())
if ts_min and ts_max and ts_min <= failure_time <= ts_max:
    process()
```

**Anti-Pattern 2: Ignoring timezones**
```python
# BAD: Implicit timezone assumptions
df['date'] = pd.to_datetime(df['date'])  # What timezone?
df_filtered = df[df['date'] > datetime.datetime.now()]  # Comparing tz-naive with tz-aware?
```
**Problem:** Timezone ambiguity causes bugs with international data

**Correct:**
```python
# GOOD: Explicit timezone handling
df['date'] = pd.to_datetime(df['date']).dt.tz_localize('UTC')
now_utc = pd.Timestamp.now(tz='UTC')
df_filtered = df[df['date'] > now_utc]
```

**Anti-Pattern 3: Inefficient datetime parsing**
```python
# BAD: No format specification (slow, ambiguous)
df['date'] = pd.to_datetime(df['date'])
```
**Problem:** 10x slower, ambiguous date formats (01/02/2024 - Jan 2 or Feb 1?)

**Correct:**
```python
# GOOD: Explicit format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
```

**Anti-Pattern 4: Using Python datetime for vectorized operations**
```python
# BAD: Loop with Python datetime
for idx, row in df.iterrows():
    row['next_week'] = row['date'] + datetime.timedelta(days=7)
```
**Problem:** 100x slower than vectorized Pandas operations

**Correct:**
```python
# GOOD: Vectorized Pandas operation
df['next_week'] = df['date'] + pd.Timedelta(days=7)
```

**Anti-Pattern 5: Chained datetime operations without assignment**
```python
# BAD: Modifying copy, not original
df[df['active'] == True]['date'] = df['date'] + pd.Timedelta(days=1)  # SettingWithCopyWarning!
```
**Problem:** SettingWithCopyWarning, changes not applied to original DataFrame

**Correct:**
```python
# GOOD: Use loc for explicit assignment
df.loc[df['active'] == True, 'date'] = df.loc[df['active'] == True, 'date'] + pd.Timedelta(days=1)
```
