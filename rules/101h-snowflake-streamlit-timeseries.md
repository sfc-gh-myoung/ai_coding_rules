# Streamlit Time Series: Smoothing and Aggregation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**Keywords:** time series smoothing, data aggregation, resample, SCADA data, high-frequency data, trend analysis, rolling average, EWMA, exponential smoothing
**TokenBudget:** ~2550
**ContextTier:** Low
**Depends:** 101a-snowflake-streamlit-visualization.md

## Scope

**What This Rule Covers:**
Time-based aggregation and smoothing patterns for high-frequency data visualization in Streamlit applications.

**When to Load This Rule:**
- Visualizing high-frequency sensor data (SCADA, PMU, IoT)
- Reducing noise in time series charts
- Building dashboards with trend analysis
- Working with data at 15-minute or finer intervals
- Any chart with >1000 data points causing performance issues

## References

### Dependencies

**Must Load First:**
- **101a-snowflake-streamlit-visualization.md** - Core visualization patterns

### Related

- **251-python-datetime-core.md** - Datetime optimization for time series

## Contract

### Inputs and Prerequisites

- DataFrame with time series data (timestamp column + value columns)
- pandas >= 1.3.0 (for resample improvements), Streamlit >= 1.20.0
- High-frequency data causing noisy visualizations or performance issues
- pandas library available

### When to Apply Smoothing

- High-frequency data creates noisy, cluttered visualizations (e.g., 15-minute SCADA readings = ~96 points/day)
- Users struggle to identify trends due to excessive detail
- Chart performance degrades with thousands of data points
- Business stakeholders need trend analysis, not granular fluctuations

### Mandatory

- Always show original and smoothed data point counts to users
- Provide user controls for aggregation level and method
- Default to mean aggregation for smoothest results

### Forbidden

- Smoothing without showing original data point count
- Applying smoothing without user control options
- Using inappropriate aggregation (e.g., mean for preserving peaks)

### Execution Steps

1. Identify timestamp and value columns in DataFrame
2. Add UI controls for aggregation level and method
3. Apply `smooth_time_series_data()` function
4. Display original vs smoothed point counts to user
5. Render smoothed data in chart

### Output Format

Smoothed DataFrame with reduced data points and user feedback showing reduction.

### Validation

- Chart renders without performance issues
- Trends visible in smoothed data
- User informed of data reduction

### Post-Execution Checklist

- [ ] UI controls for aggregation level provided
- [ ] UI controls for aggregation method provided
- [ ] Original and smoothed counts displayed
- [ ] Method matches use case: mean for trends, median for noisy data, max for peak detection, min for valley detection, ewma for adaptive smoothing

## Smoothing Function

```python
def smooth_time_series_data(
    df: pd.DataFrame,
    time_col: str,
    value_cols: list,
    aggregation_level: str = "1H",
    method: str = "mean",
) -> pd.DataFrame:
    """
    Smooth time series data by aggregating to specified intervals.

    Reduces noise in high-frequency data (e.g., 15-minute SCADA readings) by
    aggregating to coarser time intervals using configurable aggregation methods.

    Args:
        df: DataFrame with time series data
        time_col: Name of timestamp column to use for resampling
        value_cols: List of value columns to aggregate
        aggregation_level: Pandas frequency string ("15min", "30min", "1H", "2H", "4H")
        method: Aggregation method ("mean", "median", "max", "min", "ewma")

    Returns:
        Smoothed DataFrame with reduced number of data points
    """
    if df.empty:
        return df
    if time_col not in df.columns:
        raise ValueError(f"Column '{time_col}' not found in DataFrame")
    df = df.copy()  # Prevent mutation of caller's DataFrame
    df[time_col] = pd.to_datetime(df[time_col])
    df_indexed = df.set_index(time_col)
    available_cols = [col for col in value_cols if col in df_indexed.columns]

    df_resampled = df_indexed[available_cols].resample(aggregation_level)

    if method == "mean":
        df_smooth = df_resampled.mean()
    elif method == "median":
        df_smooth = df_resampled.median()
    elif method == "max":
        df_smooth = df_resampled.max()
    elif method == "min":
        df_smooth = df_resampled.min()
    elif method == "ewma":
        # Resample first to reduce points, then apply EWMA for adaptive smoothing
        df_smooth = df_indexed[available_cols].resample(aggregation_level).mean()
        df_smooth = df_smooth.ewm(span=12, adjust=False).mean()
    else:
        raise ValueError(f"Unknown method: {method}")

    return df_smooth.reset_index()
```

**Timezone handling:** `resample()` requires timezone-consistent data. For mixed-timezone data from Snowflake (e.g., TIMESTAMP_LTZ columns), normalize before resampling:
```python
df[time_col] = pd.to_datetime(df[time_col], utc=True)
```
If all timestamps are already UTC (common with TIMESTAMP_NTZ), no conversion is needed.

## UI Controls Pattern

```python
col1, col2 = st.columns(2)
with col1:
    aggregation_level = st.selectbox(
        "Data Aggregation Level",
        options=["15min", "30min", "1H", "2H", "4H"],
        index=2,  # Default to 1 hour
        help="Aggregate data to reduce noise in visualization"
    )
with col2:
    smoothing_method = st.selectbox(
        "Aggregation Method",
        options=["mean", "median", "max", "min", "ewma"],
        index=0,  # Default to mean
        help="Mean provides smoothest results, max/min preserve extremes, ewma for adaptive smoothing"
    )

# NOTE: When "ewma" is selected, aggregation_level controls output resolution
# (data is resampled first, then EWMA applied). The `span` parameter in the
# smoothing function controls the EWMA decay -- higher span = smoother.

original_count = len(scada_data)
if aggregation_level != "15min":
    scada_smooth = smooth_time_series_data(
        scada_data,
        "timestamp",
        ["voltage_kv", "power_factor"],
        aggregation_level,
        smoothing_method
    )
    st.info(f"Smoothed from {original_count:,} to {len(scada_smooth):,} points")
else:
    scada_smooth = scada_data
```

## Aggregation Guidelines

### Aggregation Level Selection

**15-minute SCADA to 1 hour (1H):**
- Reduction: 4x
- Use case: Executive dashboards, trend analysis

**15-minute SCADA to 2 hours (2H):**
- Reduction: 8x
- Use case: High-level overviews, long time periods

**1-minute PMU to 15 minutes (15min):**
- Reduction: 15x
- Use case: Grid stability monitoring

**Hourly transformer data:**
- Reduction: None (0%)
- Use case: Already appropriate granularity

### Method Selection

- **mean:** Smoothest results, best for general trends
- **median:** Robust to outliers, good for noisy data
- **max:** Preserves peak values (voltage spikes, load peaks)
- **min:** Preserves valley values (voltage sags)
- **ewma:** Exponentially weighted moving average for adaptive smoothing

### EWMA (Exponentially Weighted Moving Average)

For adaptive smoothing that gives more weight to recent observations:

```python
def ewma_smooth(
    df: pd.DataFrame,
    value_col: str,
    span: int = 12,
) -> pd.Series:
    """
    Apply EWMA smoothing. Recent values weighted more heavily.
    
    Args:
        df: DataFrame with time series
        value_col: Column to smooth
        span: Decay span (higher = smoother, lower = more reactive)
    
    Returns:
        EWMA-smoothed series
    """
    return df[value_col].ewm(span=span, adjust=False).mean()

# Usage
df['voltage_ewma'] = ewma_smooth(df, 'voltage_kv', span=12)
```

**When to use EWMA vs resampling:**
- **EWMA:** Preserves original time resolution, smooths noise adaptively
- **Resampling:** Reduces data points, fixed time intervals

### Gap Detection

Detect gaps in time series data (e.g., missing sensor readings):

```python
def detect_gaps(df: pd.DataFrame, time_col: str, threshold: str = "1H") -> pd.DataFrame:
    """Flag rows where the time gap exceeds the threshold."""
    df = df.sort_values(time_col)
    df['gap'] = df[time_col].diff().gt(pd.Timedelta(threshold)).fillna(False)
    return df
```

## SQL-Side Aggregation

For large datasets, aggregate in Snowflake before pulling into Python:

```sql
-- Aggregate 15-minute SCADA data to hourly using TIME_SLICE
SELECT
    TIME_SLICE(timestamp, 1, 'HOUR') AS hour_bucket,
    AVG(voltage_kv) AS avg_voltage,
    MAX(voltage_kv) AS max_voltage,
    MIN(voltage_kv) AS min_voltage,
    COUNT(*) AS reading_count
FROM scada_readings
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY hour_bucket
ORDER BY hour_bucket;

-- Alternative using DATE_TRUNC for calendar-aligned buckets
SELECT
    DATE_TRUNC('HOUR', timestamp) AS hour_bucket,
    AVG(power_factor) AS avg_power_factor
FROM scada_readings
GROUP BY hour_bucket
ORDER BY hour_bucket;
```

## Performance Impact

- 15-min SCADA (96 points/day) aggregated to 1H (24 points/day) = 75% reduction
- Faster chart rendering, better UX, preserved patterns
- Always display both original and smoothed counts to user
- **NaN behavior:** `resample().mean()` skips NaN by default, but `resample().max()` and `resample().min()` propagate NaN -- this matters for sensor data with missing readings. Use `resample().max(min_count=1)` to treat all-NaN windows as NaN while still computing max when at least one value exists.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Aggregating Without User Awareness

**Problem:**
```python
df_smooth = df.resample('1H').mean()
st.line_chart(df_smooth)
```

**Why It Fails:** User doesn't know data was aggregated. Original granularity and reduction percentage should be displayed for transparency.

**Correct Pattern:**
```python
original_count = len(df)
df_smooth = df.resample('1H').mean()
st.info(f"Smoothed from {original_count:,} to {len(df_smooth):,} points (75% reduction)")
st.line_chart(df_smooth)
```

### Anti-Pattern 2: Using Wrong Aggregation Method

**Problem:**
```python
voltage_data = df['voltage_kv'].resample('1H').mean()
```

**Why It Fails:** Using mean for voltage obscures dangerous spikes. Peak voltage values matter for grid safety.

**Correct Pattern:**
```python
voltage_max = df['voltage_kv'].resample('1H').max()
voltage_min = df['voltage_kv'].resample('1H').min()
```
