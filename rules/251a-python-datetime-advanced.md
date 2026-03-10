# Python DateTime Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:timedelta, kw:dateoffset, kw:date-arithmetic, kw:time-series
**Keywords:** datetime arithmetic, Timedelta, DateOffset, business days, calendar math, relativedelta, performance, downsampling, resample
**TokenBudget:** ~2600
**ContextTier:** Medium
**Depends:** 251-python-datetime-core.md

## Scope

**What This Rule Covers:**
Date arithmetic (Timedelta vs DateOffset), calendar calculations, performance optimization for time series, and downsampling strategies.

**When to Load This Rule:**
- Performing date arithmetic or calendar calculations
- Working with business days or month/year boundaries
- Optimizing datetime performance in large datasets
- Downsampling time series for visualization

## References

### Dependencies

**Must Load First:**
- **251-python-datetime-core.md** - Core datetime types and timezone handling

**Related:**
- **251b-python-datetime-integration.md** - Streamlit, Plotly, SQL integration
- **252-python-pandas-core.md** - Pandas performance patterns

## Contract

### Inputs and Prerequisites

- Pandas 2.x+ with datetime columns (from 251 core)
- `python-dateutil` for relativedelta: `uv add python-dateutil`

### Mandatory

- **Always:** Use `pd.Timedelta` for fixed durations (days, hours, seconds)
- **Always:** Use `pd.DateOffset` for calendar periods (months, years, business days)
- **Rule:** Use vectorized Pandas operations instead of Python datetime loops
- **Rule:** Downsample large time series before visualization

### Forbidden

- Using `timedelta(days=30)` for "one month" (month lengths vary 28-31 days)
- Row-level datetime iteration with iterrows() (use vectorized operations)
- Chained datetime assignment without .loc (causes SettingWithCopyWarning)

### Execution Steps

1. Choose Timedelta (fixed) or DateOffset (calendar-aware) based on need
2. Use vectorized operations for DataFrame datetime arithmetic
3. Downsample time series for visualization performance
4. Test edge cases (month boundaries, DST transitions, leap years)

### Output Format

Vectorized datetime arithmetic, calendar-aware calculations, performance-optimized time series.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Timedelta used for fixed durations only
- [ ] DateOffset used for calendar periods
- [ ] No row-level datetime iteration
- [ ] Large time series downsampled for rendering

### Design Principles

- **Calendar-aware:** Use DateOffset for month/year arithmetic
- **Vectorized:** Never iterate rows for datetime math
- **Performance:** Downsample before visualization

### Investigation Required

Before implementing date arithmetic, agents MUST check:

- [ ] **Existing arithmetic patterns**: Search for `Timedelta`, `DateOffset`, `relativedelta` in the codebase to match existing approach
- [ ] **Datetime types in use**: Run `df.dtypes` to identify datetime64 vs object columns before applying arithmetic
- [ ] **Dataset size**: Check `df.shape[0]` — vectorized ops critical for >10K rows, `.apply()` acceptable for <1K
- [ ] **python-dateutil status**: Check `pyproject.toml` for `python-dateutil` — needed for `relativedelta` age calculations
- [ ] **Business calendar requirements**: Ask whether custom holidays apply before using `BDay()` — may need `CustomBusinessDay`

### Post-Execution Checklist

- [ ] Correct arithmetic type chosen (Timedelta vs DateOffset)
- [ ] Vectorized operations used throughout
- [ ] Performance optimized for dataset size
- [ ] Edge cases tested (month boundaries, leap years)

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Timedelta for Calendar Arithmetic

**Problem:** `timedelta(days=30)` does not correctly handle "one month" since month lengths vary (28-31 days). Business logic errors result.

**Correct Pattern:** Use `pd.DateOffset` for calendar-aware arithmetic that handles variable month lengths.

```python
# Wrong: Timedelta doesn't handle month boundaries
from datetime import datetime, timedelta, UTC
start = datetime(2024, 1, 31, tzinfo=UTC)
next_month = start + timedelta(days=30)  # Feb 29, not "end of Feb"!

# Correct: DateOffset handles calendar arithmetic correctly
import pandas as pd
start = pd.Timestamp(datetime(2024, 1, 31, tzinfo=UTC))
next_month = start + pd.DateOffset(months=1)  # Correctly yields Feb 29
next_year = start + pd.DateOffset(years=1)    # Handles leap years
```

### Anti-Pattern 2: Chained DateTime Assignment Without .loc

**Problem:** Modifying a copy, not the original DataFrame. Changes silently lost.

**Correct Pattern:** Use `.loc` for explicit assignment to ensure changes apply to the original DataFrame.

```python
# Wrong: SettingWithCopyWarning, changes not applied
df[df['active'] == True]['date'] = df['date'] + pd.Timedelta(days=1)

# Correct: Use .loc for explicit assignment
df.loc[df['active'], 'date'] = df.loc[df['active'], 'date'] + pd.Timedelta(days=1)
```

## Date Arithmetic

### Timedelta (Fixed Duration Arithmetic)

Use for: fixed time periods (days, hours, seconds).

```python
import pandas as pd

# Add/subtract fixed durations
df['next_week'] = df['date'] + pd.Timedelta(days=7)
df['yesterday'] = df['date'] - pd.Timedelta(days=1)
df['in_2_hours'] = df['timestamp'] + pd.Timedelta(hours=2)

# Calculate duration between dates
df['days_between'] = (df['end_date'] - df['start_date']).dt.days
df['hours_between'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
```

### DateOffset (Calendar-Aware Arithmetic)

Use for: calendar periods that vary (months, years, business days).

```python
from pandas.tseries.offsets import DateOffset, BDay, MonthEnd

# Add months (handles varying month lengths)
df['next_month'] = df['date'] + DateOffset(months=1)

# Next business day (skips weekends)
df['next_business_day'] = df['date'] + BDay(1)

# End of month
df['month_end'] = df['date'] + MonthEnd(0)      # Current month end
df['next_month_end'] = df['date'] + MonthEnd(1)  # Next month end
```

### Custom Business Days

For business calendars with holidays:

```python
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

us_bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())

# Skip US holidays AND weekends:
df['next_business_day'] = df['date'] + us_bday

# Custom holiday list:
holidays = ['2024-12-25', '2024-01-01', '2024-07-04']
custom_bday = CustomBusinessDay(holidays=holidays)
```

### DST Transition Warning

```python
# Arithmetic across DST transitions can shift times:
ts = pd.Timestamp('2024-03-10 01:00', tz='America/New_York')
result = ts + pd.Timedelta(hours=1)
# Result: 2024-03-10 03:00 (skips 2:00 AM — spring forward)
# Use DateOffset for calendar-aware arithmetic when DST matters
```

### Common Date Math Patterns

> **Note:** `relativedelta` has no vectorized Pandas equivalent. Using `.apply()` below
> is an acceptable exception to the "use vectorized operations" mandate (Mandatory item 3).
> For datasets >100K rows, consider the vectorized approximation.

```python
from dateutil.relativedelta import relativedelta

# Acceptable .apply() — no vectorized alternative for calendar-aware age:
df['age_years'] = df['birth_date'].apply(
    lambda bd: relativedelta(pd.Timestamp.now(), bd).years if pd.notna(bd) else None
)

# For large datasets — vectorized approximation (±1 day accuracy):
df['age_approx'] = (pd.Timestamp.now(tz='UTC') - df['birth_date']).dt.days // 365

# Days since event
df['days_since_order'] = (pd.Timestamp.now() - df['order_date']).dt.days

# Weeks between dates
df['weeks_between'] = (df['end_date'] - df['start_date']).dt.days // 7

# Quarter start/end
df['quarter_start'] = df['date'].dt.to_period('Q').dt.start_time
df['quarter_end'] = df['date'].dt.to_period('Q').dt.end_time
```

### Generating Date Sequences

Use `pd.date_range()` to create date sequences for indices, filling gaps, or test data:

```python
import pandas as pd

# Daily range:
dates = pd.date_range(start='2024-01-01', periods=365, freq='D')

# Business days only:
biz_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='B')

# Monthly start dates:
months = pd.date_range(start='2024-01', periods=12, freq='MS')  # Month Start

# With timezone:
utc_dates = pd.date_range(start='2024-01-01', periods=24, freq='h', tz='UTC')

# Fill gaps in time series:
full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
df_complete = df.reindex(full_index).ffill()
```

## Performance Optimization

### Plotly Rendering Optimization

Convert to strings when datetime interactivity not needed:

```python
import streamlit as st

@st.cache_data(ttl=3600)
def load_time_series_data():
    df = session.sql("SELECT date, value FROM time_series").to_pandas()
    # For Plotly: Convert to string for faster rendering
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    return df

df = load_time_series_data()
fig = px.line(df, x='date_str', y='value')
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
df_hourly = df.set_index('timestamp').resample('h').mean().reset_index()
df_daily = df.set_index('timestamp').resample('D').mean().reset_index()
```

### Time-Based GroupBy

Use `pd.Grouper(freq=...)` for groupby with time frequencies:

```python
# Monthly aggregation with groupby (alternative to resample):
monthly = df.groupby(pd.Grouper(key='date', freq='M')).agg(
    total_sales=('amount', 'sum'),
    order_count=('order_id', 'count'),
    avg_price=('price', 'mean'),
)

# Grouper + categorical column — sales by month and region:
by_month_region = df.groupby([
    pd.Grouper(key='date', freq='M'),
    'region'
]).agg(total=('amount', 'sum'))

# When to use Grouper vs resample:
# - resample: DatetimeIndex required, simpler syntax
# - Grouper: works with any datetime column, combines with non-time groups
```
