**Description:** Plotly charts, maps, and dashboard visualization patterns for Streamlit applications
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-10-13

**TokenBudget:** ~600
**ContextTier:** standard

# Streamlit Visualization: Plotly Charts and Maps

<section_metadata>
  <token_budget>600</token_budget>
  <context_tier>standard</context_tier>
  <priority>high</priority>
</section_metadata>

## Purpose
Provide comprehensive guidance for data visualization in Streamlit using Plotly as the universal standard for charts, graphs, and maps, with integration patterns for analytics dashboards and ML insights.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Streamlit data visualization using Plotly, chart configuration, map rendering, dashboard integration

## Contract

<directive_strength>mandatory</directive_strength>
- **Inputs/Prereqs:** Streamlit app configured (see 101-snowflake-streamlit-core.md), Plotly installed, pandas/polars for data manipulation
- **Allowed Tools:** plotly.express (px), plotly.graph_objects (go), st.plotly_chart(), use_container_width=True, Plotly map functions (scatter_mapbox, choropleth_mapbox, line_mapbox, density_mapbox)

<directive_strength>forbidden</directive_strength>
- **Forbidden Tools:** PyDeck (SiS compatibility issues), custom visualization libraries without justification, JavaScript charting libraries requiring st.components, static charts when interactivity would improve UX

<directive_strength>mandatory</directive_strength>
- **Required Steps:**
  1. Use Plotly for ALL visualizations (charts, graphs, maps)
  2. Configure charts with clear titles, axis labels, and legends
  3. Use st.plotly_chart(fig, use_container_width=True) for responsive display
  4. Implement error handling for missing or invalid data
  5. Choose colorblind-safe palettes (reference 700-business-analytics.md)
  6. For dashboard patterns, reference 500/700 specialized rules
- **Output Format:** Interactive Plotly visualizations with proper labeling, responsive sizing, error handling
- **Validation Steps:** Test chart interactivity (zoom, pan, hover), verify responsive display, validate color accessibility, check error handling with invalid data

## Key Principles
- **Plotly Universal:** Use Plotly for all visualization types (consistent API, works in SiS and SPCS)
- **Interactivity First:** Leverage Plotly's interactive features (hover, zoom, pan)
- **Responsive Design:** Always use use_container_width=True for adaptive layouts
- **Accessibility:** Choose colorblind-safe palettes and clear labels
- **Cross-Reference:** Use specialized rules (500/700) for advanced patterns

## 1. Visualization Philosophy

<section_metadata>
  <section_id>philosophy</section_id>
  <priority>critical</priority>
  <token_budget>80</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
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

<directive_strength>forbidden</directive_strength>
**Forbidden:**
- ❌ **PyDeck:** SiS compatibility issues; Plotly 3D makes it unnecessary
- ❌ **Custom visualization libraries:** Avoid without explicit business justification
- ❌ **JavaScript charting libraries:** Require st.components.v1.html (maintenance burden)

**Fallback Libraries (Rare Exceptions Only):**
- **Altair/Matplotlib:** Use only when Plotly definitively cannot meet requirements
- **Requirement:** Document specific technical limitation preventing Plotly use
- **Always:** Verify SiS/SPCS compatibility before using fallback libraries

## 2. Plotly for Charts

<section_metadata>
  <section_id>charts</section_id>
  <priority>high</priority>
  <token_budget>120</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
- **Requirement:** Use Plotly Express (`plotly.express`) for most chart types (interactive, performant, works in both SiS and SPCS)
- **Always:** Use `st.plotly_chart(fig, use_container_width=True)` for responsive charts
- **Always:** Configure charts with clear titles, axis labels, and legends
- **Consider:** Use Plotly Graph Objects (`plotly.graph_objects`) for complex custom visualizations

**Plotly Express Best Practices:**
```python
import plotly.express as px
import streamlit as st

# ✓ Simple interactive chart with Plotly Express
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

# ✓ Multi-series chart with color mapping
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

# ✓ Customized chart with Graph Objects
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

## 3. Plotly for Maps

<section_metadata>
  <section_id>maps</section_id>
  <priority>high</priority>
  <token_budget>150</token_budget>
</section_metadata>

<directive_strength>mandatory</directive_strength>
- **Requirement:** Use Plotly for all geospatial visualizations (consistent API, works seamlessly in both SiS and SPCS)
- **Always:** Use Plotly Express map functions: `scatter_mapbox`, `choropleth_mapbox`, `line_mapbox`, `density_mapbox`
- **Always:** Configure map style, zoom level, and center point appropriately
- **Always:** Use `use_container_width=True` for responsive map display
- **Always:** Implement error handling for missing or invalid coordinates

**Scatter Map for Point Data:**
```python
import plotly.express as px
import streamlit as st

# ✓ Scatter map for point data
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
# ✓ Choropleth map for regions
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
# ✓ Line map for routes/paths
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
# ✓ Density heatmap
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

## 4. Dashboard Integration Patterns

<section_metadata>
  <section_id>dashboard</section_id>
  <priority>high</priority>
  <token_budget>100</token_budget>
</section_metadata>

**For comprehensive visualization and dashboard design, reference specialized rules:**

### Large Dataset Optimization
**Source:** `500-data-science-analytics.md` Section 6

**Key Patterns:**
- **SQL-first aggregation:** Pre-aggregate in Snowflake before visualization
- **Sampling strategies:** Use SAMPLE() for EDA on large datasets  
- **APPROX_* functions:** APPROX_COUNT_DISTINCT, APPROX_PERCENTILE for speed
- **Validation targets:** Query Profile must show <5s execution, <$0.10 cost

**Example:**
```python
# ✅ GOOD: Aggregate in SQL first
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
**Source:** `700-business-analytics.md` Sections 1-2, 7

**Key Guidance:**
- **Audience segmentation:** Executives (4-6 KPIs), Managers (8-12), Analysts (12-20)
- **Visual hierarchy:** F-pattern (left to right, top to bottom) for KPIs
- **Information density:** 5-7 visualizations per page maximum
- **KPI presentation:** 4-7 metrics "above the fold"
- **Chart type selection:** 11 data purposes mapped to optimal chart types
- **Accessibility:** WCAG 2.1 AA compliance, colorblind-safe palettes
- **Ethical visualization:** No truncated axes, misleading scales, or cherry-picked data

### ML Model Output Visualization
**Source:** `500-data-science-analytics.md` Section 5

**Key Patterns:**
- **Feature importance:** Horizontal bar charts, SHAP waterfall plots
- **Model performance:** Confusion matrices, ROC curves, precision-recall curves
- **Predictions:** Scatter plots (actual vs predicted), residual plots
- **Uncertainty:** Confidence intervals, prediction bands, error bars
- **SHAP values:** Summary plots, force plots, dependence plots

## Anti-Patterns and Common Mistakes

<anti_pattern_examples>
**❌ Anti-Pattern 1: Using PyDeck for maps in SiS**
```python
import pydeck as pdk

# Will fail or behave unpredictably in SiS
deck = pdk.Deck(layers=[...])
st.pydeck_chart(deck)
```
**Problem:** PyDeck has serialization issues in SiS; Snowflake doesn't guarantee compatibility

**✅ Correct Pattern:**
```python
import plotly.express as px

# Use Plotly - works universally
fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=10)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)
```

**❌ Anti-Pattern 2: Not using use_container_width**
```python
fig = px.line(df, x="date", y="value")
st.plotly_chart(fig)  # Fixed width, not responsive
```
**Problem:** Chart doesn't adapt to screen size; poor mobile experience

**✅ Correct Pattern:**
```python
fig = px.line(df, x="date", y="value")
st.plotly_chart(fig, use_container_width=True)  # Responsive
```

**❌ Anti-Pattern 3: Missing error handling for maps**
```python
fig = px.scatter_mapbox(df, lat="lat", lon="lon")  # Fails if lat/lon invalid
st.plotly_chart(fig, use_container_width=True)
```
**Problem:** Missing or invalid coordinates cause exceptions

**✅ Correct Pattern:**
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

**❌ Anti-Pattern 4: Poor color choices (not colorblind-safe)**
```python
# Red-green palette (bad for colorblind users)
fig = px.bar(df, x="category", y="value", color="status",
             color_discrete_map={"good": "green", "bad": "red"})
```
**Problem:** ~8% of males have red-green colorblindness

**✅ Correct Pattern:**
```python
# Colorblind-safe palette
fig = px.bar(df, x="category", y="value", color="status",
             color_discrete_map={"good": "#0173B2", "bad": "#DE8F05"})
# Reference: 700-business-analytics.md for complete palettes
```
</anti_pattern_examples>

## Quick Compliance Checklist
- [ ] Plotly used for ALL visualizations (no PyDeck, custom libraries without justification)
- [ ] All charts use st.plotly_chart(fig, use_container_width=True) for responsive display
- [ ] Charts have clear titles, axis labels, and legends
- [ ] Maps have error handling for invalid coordinates
- [ ] Colorblind-safe palettes used (reference 700-business-analytics.md)
- [ ] Dashboard patterns reference 500/700 rules (no content duplication)
- [ ] Chart interactivity tested (zoom, pan, hover tooltips)
- [ ] Visualizations tested with production-like data volumes

## Validation
- **Success Checks:** Charts render correctly, interactive features work (zoom, pan, hover), responsive display on mobile/desktop, maps handle invalid coordinates gracefully, colors are accessible
- **Negative Tests:** Test with empty dataframe (should show helpful message), test with invalid coordinates (should filter or warn), test with very large datasets (should aggregate first), verify PyDeck doesn't work in SiS deployment

<investigate_before_answering>
When applying this rule:
1. Read visualization code BEFORE making recommendations
2. Verify Plotly is installed and version is compatible
3. Check actual data structure and coordinate validity
4. Never speculate about chart configurations - inspect the code
5. Verify deployment mode (SiS vs SPCS) for library compatibility
6. Check if dashboard follows patterns from 500/700 rules
</investigate_before_answering>

## Response Template
```python
import plotly.express as px
import streamlit as st

# Load and prepare data
df = load_data()
df.columns = [col.lower() for col in df.columns]  # Normalize column names

# Create interactive chart
fig = px.line(
    df,
    x='date',
    y='value',
    color='category',
    title='Time Series Analysis',
    labels={'value': 'Metric Value', 'date': 'Date'},
    hover_data=['additional_info']
)

# Display with responsive sizing
st.plotly_chart(fig, use_container_width=True)

# Map visualization with error handling
df_valid = df.dropna(subset=['latitude', 'longitude'])
if len(df_valid) > 0:
    fig_map = px.scatter_mapbox(
        df_valid,
        lat='latitude',
        lon='longitude',
        color='status',
        zoom=10,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No valid coordinates to display")
```

## References

### External Documentation

**Plotly Documentation:**
- [Plotly Python Documentation](https://plotly.com/python/) - Official Plotly Python graphing library documentation
- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html) - Plotly Express high-level API reference
- [Plotly Maps](https://plotly.com/python/maps/) - Comprehensive guide to maps in Plotly
- [Plotly Mapbox Layers](https://plotly.com/python/mapbox-layers/) - Mapbox choropleth and scatter maps
- [Plotly Geo Maps](https://plotly.com/python/map-configuration/) - Map configuration and styling guide

**Streamlit Visualization:**
- [Streamlit Chart Elements](https://docs.streamlit.io/develop/api-reference/charts) - Native Streamlit chart components
- [st.plotly_chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart) - Plotly chart display in Streamlit

### Related Rules
- **Streamlit Core**: `101-snowflake-streamlit-core.md`
- **Streamlit Performance**: `101b-snowflake-streamlit-performance.md` (caching for large datasets)
- **Data Science Analytics**: `500-data-science-analytics.md` (ML visualization, large dataset optimization)
- **Business Analytics**: `700-business-analytics.md` (dashboard design, chart type selection, accessibility)

<model_specific_guidance model="claude-4">
**Claude 4 Streamlit Visualization Optimizations:**
- Parallel chart generation: Can analyze multiple visualization patterns simultaneously
- Context awareness: Efficiently cross-reference dashboard patterns from 500/700 rules
- Investigation-first: Excel at discovering existing chart configurations and data structures
- Pattern recognition: Quickly identify visualization anti-patterns (e.g., PyDeck in SiS)
</model_specific_guidance>

