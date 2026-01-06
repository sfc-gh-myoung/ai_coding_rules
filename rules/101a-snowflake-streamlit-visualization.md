# Streamlit Visualization: Plotly Charts and Maps

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-05
**Keywords:** st.plotly_chart, st.map, dashboard, interactive charts, map visualization, time series smoothing, data aggregation, create chart, chart types, plotly express, dashboard layout, chart configuration, streamlit plotting, chart customization
**TokenBudget:** ~5900
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core.md, 940-business-analytics.md

## Scope

**What This Rule Covers:**
Comprehensive data visualization in Streamlit using Plotly as the universal standard for charts, graphs, and maps, with integration patterns for analytics dashboards and ML insights.

**When to Load This Rule:**
- Creating charts and graphs in Streamlit
- Building interactive dashboards
- Implementing map visualizations
- Configuring Plotly charts for Streamlit
- Visualizing time series data
- Creating business analytics dashboards
- Rendering data aggregations visually

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **101-snowflake-streamlit-core.md** - Streamlit core patterns and navigation

**Recommended:**
- **940-business-analytics.md** - Business analytics patterns and metrics

**Related:**
- **100-snowflake-core.md** - Snowflake SQL for data preparation
- **103-snowflake-performance-tuning.md** - Query optimization for visualization

### External Documentation

**Official Documentation:**
- [Streamlit Plotly Chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart) - st.plotly_chart() reference
- [Plotly Express](https://plotly.com/python/plotly-express/) - High-level plotting API
- [Plotly Python](https://plotly.com/python/) - Complete Plotly documentation

**Best Practices Guides:**
- [Streamlit Dashboard Examples](https://streamlit.io/gallery) - Dashboard inspiration
- [Plotly Chart Types](https://plotly.com/python/basic-charts/) - Chart selection guide
- **Responsive display:** `st.plotly_chart(fig, use_container_width=True)` always
- **Clear labeling:** Title, axis labels, legends on every chart
- **Plotly Express first:** Use `plotly.express` for standard charts (simpler API)
- **Accessibility:** Colorblind-safe palettes (e.g., plotly.colors.qualitative.Safe)
- **Maps:** Use Plotly mapbox functions (scatter_mapbox, choropleth_mapbox, line_mapbox)
- **Never use PyDeck** - has SiS compatibility issues; Plotly 3D replaces it

**Quick Checklist:**
- [ ] Import `plotly.express as px`
- [ ] Create chart with clear title and axis labels
- [ ] Display with `st.plotly_chart(fig, use_container_width=True)`
- [ ] Test interactivity (hover, zoom, pan)
- [ ] Verify colorblind-safe palette
- [ ] Add error handling for missing/invalid data

## Contract

### Inputs and Prerequisites

- Streamlit 1.46+ with Plotly installed
- 101-snowflake-streamlit-core.md patterns established
- Data prepared in pandas DataFrame
- Chart requirements identified

### Mandatory

- **Use Plotly for ALL visualizations** - charts, graphs, and maps (never PyDeck)
- **st.plotly_chart()** - Standard method for rendering Plotly figures
- **plotly.express** - Use for quick, high-level charts
- **Responsive design** - Charts adapt to container width
- **Clear axis labels** - Always label x/y axes and provide titles
- **Consistent theming** - Match Streamlit theme from config.toml

### Forbidden

- PyDeck for maps (use Plotly maps instead)
- Matplotlib or other plotting libraries (Plotly only)
- Hardcoded chart dimensions (use `use_container_width=True`)
- Missing axis labels or titles
- Inconsistent color schemes across dashboard

### Execution Steps

1. Prepare data in pandas DataFrame
2. Choose appropriate Plotly chart type (bar, line, scatter, map, etc.)
3. Create chart using plotly.express or plotly.graph_objects
4. Configure chart layout (titles, labels, colors)
5. Render with st.plotly_chart(fig, use_container_width=True)
6. Test responsiveness and interactivity

### Output Format

```python
import streamlit as st
import plotly.express as px
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [10, 15, 13, 17, 20],
    'category': ['A', 'B', 'A', 'B', 'A']
})

# Create chart
fig = px.line(
    df,
    x='x',
    y='y',
    color='category',
    title='Sample Time Series',
    labels={'x': 'Time Period', 'y': 'Value'}
)

# Render in Streamlit
st.plotly_chart(fig, use_container_width=True)
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Code Quality:**
- **CRITICAL:** All visualizations use Plotly (no PyDeck, Matplotlib, etc.)
- **CRITICAL:** Charts rendered with st.plotly_chart()
- **CRITICAL:** `use_container_width=True` for responsive design
- **Format Check:** All charts have titles and axis labels
- **Format Check:** Consistent color scheme across dashboard

**Functionality:**
- **CRITICAL:** Charts display correctly and are interactive
- **CRITICAL:** Charts responsive to container width
- **Data Quality:** Data properly prepared in pandas DataFrame
- **Performance:** Charts render quickly without lag

**Success Criteria:**
- All charts use Plotly
- Charts are responsive and interactive
- Consistent theming across dashboard
- Clear labels and titles
- No errors in console

**Investigation Required:**
1. **Review existing dashboard** to understand current chart patterns
2. **Check data preparation** to ensure DataFrame is correctly formatted
3. **Verify Plotly version** for compatibility with features
4. **Test responsiveness** on different screen sizes

**Anti-Pattern Examples:**
- Using PyDeck for maps
- Missing `use_container_width=True`
- Hardcoded chart dimensions
- Inconsistent colors across charts

**Correct Pattern:**
- "Let me check your existing dashboard and data first."
- [reviews existing charts, checks DataFrame structure]
- "I see you're using Plotly. Here's the new chart following the same pattern..."
- [implements with proper labels, responsive sizing, theme consistency]

### Design Principles

- **Plotly Universal:** Use Plotly for all visualization types
- **Responsive First:** Always use `use_container_width=True`
- **Clear Communication:** Label axes, provide titles, add context
- **Consistent Theming:** Match Streamlit theme from config.toml
- **Interactive by Default:** Leverage Plotly's built-in interactivity
- **Performance Conscious:** Optimize data preparation, limit chart complexity

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md, 101-snowflake-streamlit-core.md)
- [ ] Plotly installed
- [ ] Existing dashboard patterns reviewed
- [ ] Data prepared in DataFrame

**After Completion:**
- [ ] **CRITICAL:** All visualizations use Plotly
- [ ] **CRITICAL:** Charts rendered with st.plotly_chart()
- [ ] **CRITICAL:** `use_container_width=True` for responsiveness
- [ ] All charts have titles and axis labels
- [ ] Consistent color scheme across dashboard
- [ ] Charts are interactive
- [ ] Charts display correctly on different screen sizes
- [ ] No console errors
- [ ] CHANGELOG.md and README.md updated as required

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using PyDeck for maps in SiS**
```python
import pydeck as pdk

# Will fail or behave unpredictably in SiS
deck = pdk.Deck(layers=[...])
st.pydeck_chart(deck)
```
**Problem:** PyDeck has serialization issues in SiS; Snowflake doesn't guarantee compatibility

**Correct Pattern:**
```python
import plotly.express as px

# Use Plotly - works universally
fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=10)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)
```

**Anti-Pattern 2: Not using use_container_width**
```python
fig = px.line(df, x="date", y="value")
st.plotly_chart(fig)  # Fixed width, not responsive
```
**Problem:** Chart doesn't adapt to screen size; poor mobile experience

**Correct Pattern:**
```python
fig = px.line(df, x="date", y="value")
st.plotly_chart(fig, use_container_width=True)  # Responsive
```

**Anti-Pattern 3: Missing error handling for maps**
```python
fig = px.scatter_mapbox(df, lat="lat", lon="lon")  # Fails if lat/lon invalid
st.plotly_chart(fig, use_container_width=True)
```
**Problem:** Missing or invalid coordinates cause exceptions

**Correct Pattern:**
```python
# Validate coordinates before mapping
df_valid = df.dropna(subset=['lat', 'lon'])
df_valid = df_valid[(df_valid['lat'].between(-90, 90)) &
                     (df_valid['lon'].between(-180, 180))]

if len(df_valid) > 0:
    fig = px.scatter_mapbox(df_valid, lat="lat", lon="lon", zoom=10)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No valid coordinates to display on map")
```

**Anti-Pattern 4: Poor color choices (not colorblind-safe)**
```python
# Red-green palette (bad for colorblind users)
fig = px.bar(df, x="category", y="value", color="status",
             color_discrete_map={"good": "green", "bad": "red"})
```
**Problem:** ~8% of males have red-green colorblindness

**Correct Pattern:**
```python
# Colorblind-safe palette
fig = px.bar(df, x="category", y="value", color="status",
             color_discrete_map={"good": "#0173B2", "bad": "#DE8F05"})
# Reference: 940-business-analytics.md for complete palettes
```

**Anti-Pattern 5: Mixed datetime types in comparisons (Pandas 2.0+ incompatibility)**
```python
# WRONG: Comparing pandas Timestamp with Python datetime
for timestamp in failure_timestamps:
    failure_time = pd.to_datetime(timestamp).to_pydatetime()  # Python datetime
    # df["hour"].min() returns pandas Timestamp - type mismatch!
    if df["hour"].min() <= failure_time <= df["hour"].max():  # TypeError!
        fig.add_vline(x=failure_time, ...)
```
**Problem:** Pandas 2.0+ enforces strict type checking for datetime operations. Comparing pandas Timestamps (from `.min()/.max()`) with Python datetimes causes `TypeError: unsupported operand type(s) for +: 'int' and 'datetime.datetime'`.

**Correct Pattern:**
```python
# Helper function for consistent datetime handling
def ensure_python_datetime(dt):
    """Convert any datetime-like to Python datetime."""
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, datetime.datetime):
        return dt
    if hasattr(dt, 'to_pydatetime'):
        return dt.to_pydatetime()
    return pd.to_datetime(dt).to_pydatetime()

# Use helper for consistent comparisons
for timestamp in failure_timestamps:
    try:
        # Convert all to Python datetime for consistency
        failure_time = ensure_python_datetime(timestamp)
        hour_min = ensure_python_datetime(df["hour"].min())
        hour_max = ensure_python_datetime(df["hour"].max())

        # Now all are Python datetimes - comparison works!
        if hour_min and hour_max and hour_min <= failure_time <= hour_max:
            fig.add_vline(x=failure_time, ...)
    except Exception as e:
        st.warning(f"Could not add marker: {type(e).__name__}: {str(e)[:100]}")
```
**Benefits:**
- Prevents TypeError from mixed datetime types
- Works consistently across Pandas 1.x and 2.x
- Handles edge cases (None, NaT, different datetime formats)
- Clear error messages for debugging

**Note:** For comprehensive datetime handling guidance including type conversions, timezone management, and date arithmetic, see `251-python-datetime-handling.md`.

## Visualization Philosophy

**MANDATORY:**
**Primary Library: Plotly (Universal Standard)**
- **Requirement:** Use Plotly for ALL charts, graphs, and maps
- **Rationale:**
  - Consistent API across all visualization types
  - Works seamlessly in both SiS and SPCS (no serialization issues)
  - Comprehensive feature set including 3D support (scatter_3d, surface plots)
  - Active maintenance and Snowflake integration
  - Large community and extensive documentation

**Plotly Capabilities:**
- **Charts:** Bar, line, scatter, heatmap, box, violin, histogram, and more
- **Maps:** scatter_mapbox, choropleth_mapbox, line_mapbox, density_mapbox
- **3D Visualizations:** scatter_3d, surface plots, mesh plots
- **Advanced:** Animations, subplots, custom interactivity

**FORBIDDEN:**
**Forbidden:**
- **PyDeck:** SiS compatibility issues; Plotly 3D makes it unnecessary
- **Custom visualization libraries:** Avoid without explicit business justification
- **JavaScript charting libraries:** Require st.components.v1.html (maintenance burden)

**Fallback Libraries (Rare Exceptions Only):**
- **Altair/Matplotlib:** Use only when Plotly definitively cannot meet requirements
- **Requirement:** Document specific technical limitation preventing Plotly use
- **Always:** Verify SiS/SPCS compatibility before using fallback libraries

## Plotly for Charts

**MANDATORY:**
- **Requirement:** Use Plotly Express (`plotly.express`) for most chart types (interactive, performant, works in both SiS and SPCS)
- **Always:** Use `st.plotly_chart(fig, use_container_width=True)` for responsive charts
- **Always:** Configure charts with clear titles, axis labels, and legends
- **Consider:** Use Plotly Graph Objects (`plotly.graph_objects`) for complex custom visualizations

**Plotly Express Best Practices:**
```python
import plotly.express as px
import streamlit as st

# [PASS] Simple interactive chart with Plotly Express
df = load_data()
fig = px.line(
    df,
    x='date',
    y='value',
    title='Time Series Analysis',
    labels={'value': 'Metric Value', 'date': 'Date'},
    hover_data=['category']
)
st.plotly_chart(fig, use_container_width=True)

# [PASS] Multi-series chart with color mapping
fig = px.bar(
    df,
    x='region',
    y='sales',
    color='product',
    title='Sales by Region and Product',
    labels={'sales': 'Sales ($)', 'region': 'Region'},
    color_discrete_map={
        'Product A': '#FF6B6B',
        'Product B': '#4ECDC4',
        'Product C': '#45B7D1'
    }
)
st.plotly_chart(fig, use_container_width=True)
```

**Plotly Graph Objects (Advanced):**
```python
import plotly.graph_objects as go

# [PASS] Customized chart with Graph Objects
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines+markers',
    name='Actual',
    line=dict(color='#FF6B6B', width=2),
    marker=dict(size=6)
))
fig.update_layout(
    title='Custom Visualization',
    xaxis_title='Date',
    yaxis_title='Value',
    hovermode='x unified',
    showlegend=True
)
st.plotly_chart(fig, use_container_width=True)
```

**Common Chart Types:**
```python
# Line chart
fig = px.line(df, x='date', y='value', title='Trend Over Time')

# Bar chart
fig = px.bar(df, x='category', y='count', title='Count by Category')

# Scatter plot
fig = px.scatter(df, x='x', y='y', color='group', size='size', title='Correlation')

# Histogram
fig = px.histogram(df, x='value', nbins=50, title='Distribution')

# Box plot
fig = px.box(df, x='category', y='value', title='Value Distribution')

# Heatmap
fig = px.imshow(correlation_matrix, title='Correlation Matrix')
```

## Plotly for Maps

**MANDATORY:**
- **Requirement:** Use Plotly for all geospatial visualizations (consistent API, works seamlessly in both SiS and SPCS)
- **Always:** Use Plotly Express map functions: `scatter_mapbox`, `choropleth_mapbox`, `line_mapbox`, `density_mapbox`
- **Always:** Configure map style, zoom level, and center point appropriately
- **Always:** Use `use_container_width=True` for responsive map display
- **Always:** Implement error handling for missing or invalid coordinates

**Scatter Map for Point Data:**
```python
import plotly.express as px
import streamlit as st

# [PASS] Scatter map for point data
assets = load_grid_assets()
fig = px.scatter_mapbox(
    assets,
    lat='latitude',
    lon='longitude',
    color='asset_type',
    size='capacity',
    hover_name='asset_id',
    hover_data=['status', 'last_maintenance'],
    color_discrete_map={
        'TRANSFORMER': '#FF6B6B',
        'SUBSTATION': '#4ECDC4',
        'GENERATOR': '#45B7D1'
    },
    zoom=10,
    height=600
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)
```

**Choropleth Map for Regions:**
```python
# [PASS] Choropleth map for regions
region_data = load_regional_metrics()
fig = px.choropleth_mapbox(
    region_data,
    geojson=regions_geojson,
    locations='region_id',
    color='metric_value',
    color_continuous_scale='Viridis',
    mapbox_style="carto-positron",
    zoom=8,
    center={"lat": 37.7749, "lon": -122.4194},
    opacity=0.5,
    hover_name='region_name',
    hover_data=['population', 'metric_value']
)
st.plotly_chart(fig, use_container_width=True)
```

**Line Map for Routes/Paths:**
```python
# [PASS] Line map for routes/paths
route_data = load_route_data()
fig = px.line_mapbox(
    route_data,
    lat='latitude',
    lon='longitude',
    color='route_id',
    zoom=10,
    height=600
)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)
```

**Density Heatmap:**
```python
# [PASS] Density heatmap
event_data = load_event_locations()
fig = px.density_mapbox(
    event_data,
    lat='latitude',
    lon='longitude',
    z='event_count',
    radius=10,
    zoom=10,
    mapbox_style="stamen-terrain"
)
st.plotly_chart(fig, use_container_width=True)
```

**Map Styles:**
- `"open-street-map"` - Free, no token required
- `"carto-positron"` - Light theme, clean
- `"carto-darkmatter"` - Dark theme
- `"stamen-terrain"` - Terrain visualization
- `"mapbox://styles/..."` - Custom Mapbox styles (requires token)

## Dashboard Integration Patterns

**For comprehensive visualization and dashboard design, reference specialized rules:**

### Large Dataset Optimization
**Source:** `920-data-science-analytics.md` Section 6

**Key Patterns:**
- **SQL-first aggregation:** Pre-aggregate in Snowflake before visualization
- **Sampling strategies:** Use SAMPLE() for EDA on large datasets
- **APPROX_* functions:** APPROX_COUNT_DISTINCT, APPROX_PERCENTILE for speed
- **Validation targets:** Query Profile must show <5s execution, <$0.10 cost

**Example:**
```python
# GOOD: Aggregate in SQL first
@st.cache_data(ttl=600)
def load_summary_data():
    query = """
    SELECT
        DATE_TRUNC('day', order_date) as date,
        region,
        COUNT(DISTINCT customer_id) as customers,
        SUM(revenue) as total_revenue
    FROM orders
    WHERE order_date >= DATEADD(day, -90, CURRENT_DATE())
    GROUP BY 1, 2
    ORDER BY 1 DESC
    """
    return session.sql(query).to_pandas()

# Visualize aggregated data (already aggregated, fast to render)
df = load_summary_data()
fig = px.line(df, x="date", y="total_revenue", color="region")
st.plotly_chart(fig, use_container_width=True)
```

### Business Dashboard Design Patterns
**Source:** `940-business-analytics.md` Sections 1-2, 7

**Key Guidance:**
- **Audience segmentation:** Executives (4-6 KPIs), Managers (8-12), Analysts (12-20)
- **Visual hierarchy:** F-pattern (left to right, top to bottom) for KPIs
- **Information density:** 5-7 visualizations per page maximum
- **KPI presentation:** 4-7 metrics "above the fold"
- **Chart type selection:** 11 data purposes mapped to optimal chart types
- **Accessibility:** WCAG 2.1 AA compliance, colorblind-safe palettes
- **Ethical visualization:** No truncated axes, misleading scales, or cherry-picked data

### ML Model Output Visualization
**Source:** `920-data-science-analytics.md` Section 5

**Key Patterns:**
- **Feature importance:** Horizontal bar charts, SHAP waterfall plots
- **Model performance:** Confusion matrices, ROC curves, precision-recall curves
- **Predictions:** Scatter plots (actual vs predicted), residual plots
- **Uncertainty:** Confidence intervals, prediction bands, error bars
- **SHAP values:** Summary plots, force plots, dependence plots

## Time Series Data Smoothing

**RECOMMENDED:**
**When to Apply Smoothing:**
- High-frequency data creates noisy, cluttered visualizations (e.g., 15-minute SCADA readings = ~96 points/day)
- Users struggle to identify trends due to excessive detail
- Chart performance degrades with thousands of data points
- Business stakeholders need trend analysis, not granular fluctuations

**Recommended Smoothing Approach: Time-Based Aggregation**

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

**Best Practices for User Controls:**

```python
# Add UI controls for smoothing
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

# Apply smoothing
original_count = len(scada_data)
if aggregation_level != "15min":
    scada_smooth = smooth_time_series_data(
        scada_data,
        "timestamp",
        ["voltage_kv", "power_factor"],
        aggregation_level,
        smoothing_method
    )
    st.info(f"[CHART] Smoothed from {original_count:,} to {len(scada_smooth):,} points")
else:
    scada_smooth = scada_data
```

**Aggregation Level Guidelines:**
- **15-minute SCADA to 1 hour (1H):** 4x reduction - Executive dashboards, trend analysis
- **15-minute SCADA to 2 hours (2H):** 8x reduction - High-level overviews, long time periods
- **1-minute PMU to 15 minutes (15min):** 15x reduction - Grid stability monitoring
- **Hourly transformer to None (1H):** No reduction - Already appropriate granularity

**Method Selection:**
- **mean:** Smoothest results, best for general trends
- **median:** Robust to outliers, good for noisy data
- **max:** Preserves peak values (voltage spikes, load peaks)
- **min:** Preserves valley values (voltage sags)

**Performance Impact:**
- 15-min SCADA (96 points/day) aggregated to 1H (24 points/day) = 75% reduction
- Faster chart rendering, better UX, preserved patterns
- Always display both original and smoothed counts to user
