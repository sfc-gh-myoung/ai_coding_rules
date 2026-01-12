# Streamlit Time Series: Smoothing and Aggregation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** time series smoothing, data aggregation, resample, SCADA data, high-frequency data, trend analysis, rolling average, EWMA, exponential smoothing
**TokenBudget:** ~1600
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

- **251-python-datetime-handling.md** - Datetime optimization for time series

## Contract

### When to Apply Smoothing

- High-frequency data creates noisy, cluttered visualizations (e.g., 15-minute SCADA readings = ~96 points/day)
- Users struggle to identify trends due to excessive detail
- Chart performance degrades with thousands of data points
- Business stakeholders need trend analysis, not granular fluctuations

### Mandatory

- Always show original and smoothed data point counts to users
- Provide user controls for aggregation level and method
- Default to mean aggregation for smoothest results

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
        method: Aggregation method ("mean", "median", "max", "min")

    Returns:
        Smoothed DataFrame with reduced number of data points
    """
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

    return df_smooth.reset_index()
```

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
        options=["mean", "median", "max", "min"],
        index=0,  # Default to mean
        help="Mean provides smoothest results, max/min preserve extremes"
    )

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

| Source Data | Target Level | Reduction | Use Case |
|------------|--------------|-----------|----------|
| 15-min SCADA | 1H | 4x | Executive dashboards, trend analysis |
| 15-min SCADA | 2H | 8x | High-level overviews, long time periods |
| 1-min PMU | 15min | 15x | Grid stability monitoring |
| Hourly transformer | None | 0% | Already appropriate granularity |

### Method Selection

- **mean:** Smoothest results, best for general trends
- **median:** Robust to outliers, good for noisy data
- **max:** Preserves peak values (voltage spikes, load peaks)
- **min:** Preserves valley values (voltage sags)

## Performance Impact

- 15-min SCADA (96 points/day) aggregated to 1H (24 points/day) = 75% reduction
- Faster chart rendering, better UX, preserved patterns
- Always display both original and smoothed counts to user
