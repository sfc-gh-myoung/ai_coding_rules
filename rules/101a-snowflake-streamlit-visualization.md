# Streamlit Visualization: Overview and Library Selection

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-01-12
**Keywords:** st.plotly_chart, st.pydeck_chart, st.altair_chart, dashboard, interactive charts, map visualization, chart types, visualization selection, streamlit plotting
**TokenBudget:** ~1650
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core.md

## Scope

**What This Rule Covers:**
Router rule for Streamlit visualization library selection. Provides quick guidance on choosing between Plotly, PyDeck, and Altair, then delegates to specialized sub-rules for detailed patterns.

**When to Load This Rule:**
- Starting any visualization task in Streamlit
- Deciding which charting library to use
- Need quick reference for library selection criteria

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns
- **101-snowflake-streamlit-core.md** - Streamlit core patterns

**Library-Specific Deep Dives (load as needed):**
- **101i-snowflake-streamlit-viz-plotly.md** - Plotly Express, Graph Objects, animations, faceting, tile maps
- **101j-snowflake-streamlit-viz-pydeck.md** - PyDeck layers, 3D visualization, WebGL limits
- **101k-snowflake-streamlit-viz-altair.md** - Declarative grammar, linked views, statistical charts

**Related:**
- **940-business-analytics.md** - Dashboard design patterns
- **101h-snowflake-streamlit-timeseries.md** - Time series smoothing

### External Documentation

- [Streamlit Chart Elements](https://docs.streamlit.io/develop/api-reference/charts) - All chart types
- [Plotly Express](https://plotly.com/python/plotly-express/) - High-level Plotly API
- [PyDeck Documentation](https://deckgl.readthedocs.io/en/latest/) - deck.gl Python bindings
- [Altair Documentation](https://altair-viz.github.io/) - Declarative visualization

## Contract

### Inputs and Prerequisites

- Streamlit 1.46+ with visualization libraries installed
- Data prepared in pandas DataFrame
- Chart requirements identified

### Mandatory

- **Select appropriate library** using guidance below
- **Responsive display** - Always use `width="stretch"` (Plotly/PyDeck) or `use_container_width=True` (Altair)
- **Clear labels** - Title, axis labels, legends on every chart
- **Colorblind-safe palettes** - Avoid red-green only schemes

### Forbidden

- Hardcoded chart dimensions
- Missing axis labels or titles
- More than 8 PyDeck charts per page (WebGL limit)

### Execution Steps

1. Identify visualization requirements (chart type, data size, interactivity needs)
2. Select library using decision guide below
3. Load appropriate sub-rule for detailed patterns
4. Implement with responsive display and clear labels
5. Test interactivity and responsiveness

### Output Format

```python
import streamlit as st
import plotly.express as px

fig = px.line(df, x='date', y='value', title='Chart Title')
st.plotly_chart(fig, width="stretch")
```

### Validation

- [ ] Appropriate library selected for use case
- [ ] `width="stretch"` or `use_container_width=True` used
- [ ] Clear title and axis labels present
- [ ] Colorblind-safe colors applied

### Post-Execution Checklist

- [ ] Charts render correctly and are interactive
- [ ] Responsive on different screen sizes
- [ ] No console errors

## Library Selection Decision Guide

### Default Choice: Plotly

**Use Plotly (`st.plotly_chart`) for:**
- Standard charts (line, bar, scatter, histogram, box, violin)
- 2D maps (scatter_map, choropleth_map, density_map)
- Animations and temporal sliders
- Most dashboard visualizations

**Load:** `101i-snowflake-streamlit-viz-plotly.md`

### Use PyDeck When

**Use PyDeck (`st.pydeck_chart`) for:**
- 3D visualizations (extruded polygons, 3D scatter)
- Hexbin aggregation (HexagonLayer)
- Terrain/elevation data
- Point clouds (>100k points with GPU acceleration)
- Complex multi-layer geospatial compositing

**Constraints:** Maximum ~8 PyDeck charts per page (WebGL limit)

**Load:** `101j-snowflake-streamlit-viz-pydeck.md`

### Use Altair When

**Use Altair (`st.altair_chart`) for:**
- Linked brushing/selection across views
- Statistical/analytical visualizations
- Declarative grammar preference
- Rapid exploratory data analysis

**Load:** `101k-snowflake-streamlit-viz-altair.md`

### Quick Reference

**Trend over time:** Plotly `px.line()`
**Category comparison:** Plotly `px.bar()`
**Distribution:** Plotly `px.histogram()`, `px.box()`
**Correlation:** Plotly `px.scatter()`
**2D map:** Plotly `px.scatter_map()`
**3D map:** PyDeck `HexagonLayer`, `ColumnLayer`
**Linked views:** Altair with `selection_interval()`

## Universal Best Practices

**Responsive Display:**
```python
st.plotly_chart(fig, width="stretch")
st.pydeck_chart(deck, width="stretch")
st.altair_chart(chart, use_container_width=True)
```

**Colorblind-Safe Palette:**
```python
SAFE_COLORS = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC']
```

**Coordinate Validation (Maps):**
```python
df_valid = df.dropna(subset=['lat', 'lon'])
df_valid = df_valid[
    df_valid['lat'].between(-90, 90) & 
    df_valid['lon'].between(-180, 180)
]
```

## Cross-References

**Dashboard Design:** See `940-business-analytics.md` for audience segmentation, visual hierarchy, KPI presentation

**Large Dataset Optimization:** Pre-aggregate in SQL, use `@st.cache_data`, sample for EDA

**Time Series Smoothing:** See `101h-snowflake-streamlit-timeseries.md` for `resample()` patterns

**Datetime Handling:** See `251-python-datetime-handling.md` for Pandas 2.0+ type compatibility

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Wrong Library for Use Case

**Problem:**
```python
import pydeck as pdk
deck = pdk.Deck(layers=[pdk.Layer('ScatterplotLayer', data=df)])
st.pydeck_chart(deck)
```

**Why It Fails:** Using PyDeck for simple 2D scatter maps adds unnecessary complexity. PyDeck is for 3D, aggregation layers, and advanced WebGL features.

**Correct Pattern:**
```python
import plotly.express as px
fig = px.scatter_map(df, lat='lat', lon='lon')
st.plotly_chart(fig, use_container_width=True)
```

### Anti-Pattern 2: Hardcoded Chart Dimensions

**Problem:**
```python
st.plotly_chart(fig, width=800, height=600)
```

**Why It Fails:** Fixed dimensions break on mobile, tablets, and different screen sizes. Charts should be responsive.

**Correct Pattern:**
```python
st.plotly_chart(fig, use_container_width=True)
```
