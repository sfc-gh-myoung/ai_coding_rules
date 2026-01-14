# Streamlit Visualization: Plotly Deep Dive

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** plotly, plotly express, graph objects, st.plotly_chart, interactive charts, scatter, line, bar, histogram, heatmap, box plot, violin, sunburst, treemap, animations, faceting, subplots
**TokenBudget:** ~3150
**ContextTier:** Medium
**Depends:** 101a-snowflake-streamlit-visualization.md

## Scope

**What This Rule Covers:**
Deep patterns for Plotly visualization in Streamlit, including Plotly Express for rapid development, Graph Objects for custom visualizations, advanced features like animations, faceting, and subplots.

**When to Load This Rule:**
- Building charts with Plotly Express or Graph Objects
- Creating animated visualizations
- Implementing faceted/small multiples charts
- Customizing chart appearance and interactivity
- Building complex multi-trace visualizations

## References

### Dependencies

**Must Load First:**
- **101a-snowflake-streamlit-visualization.md** - Visualization overview and library selection

**Related:**
- **101j-snowflake-streamlit-viz-pydeck.md** - PyDeck for 3D/geospatial
- **940-business-analytics.md** - Dashboard design patterns

### External Documentation

**Official Documentation:**
- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html) - Complete function reference
- [Plotly Graph Objects](https://plotly.com/python/graph-objects/) - Low-level API
- [st.plotly_chart()](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart) - Streamlit integration

**Best Practices:**
- [Plotly Fundamentals](https://plotly.com/python/plotly-fundamentals/) - Core concepts
- [Styling Plotly Express](https://plotly.com/python/styling-plotly-express/) - Customization guide

## Contract

### Inputs and Prerequisites

- Streamlit 1.46+ with plotly installed
- Data in pandas DataFrame format
- 101a visualization patterns understood

### Mandatory

- **Plotly Express first** - Use `px.*` for standard charts (5-100x less code than Graph Objects)
- **width="stretch"** - Always use for responsive charts
- **Clear labels** - Title, axis labels, and legends on every chart
- **Colorblind-safe palettes** - Use `plotly.colors.qualitative.Safe` or similar

### Forbidden

- Missing `width="stretch"` parameter
- Unlabeled axes or missing titles
- Red-green only color schemes
- Hardcoded pixel dimensions

### Execution Steps

1. Import plotly.express as px and streamlit as st
2. Prepare data in pandas DataFrame format
3. Select appropriate chart type for data purpose
4. Create chart with clear title, axis labels, and colorblind-safe palette
5. Render with `st.plotly_chart(fig, width="stretch")`
6. Test interactivity (hover, zoom, pan)

### Output Format

```python
import plotly.express as px
import streamlit as st

fig = px.line(df, x='date', y='value', title='Chart Title',
              labels={'date': 'Date', 'value': 'Value'})
st.plotly_chart(fig, width="stretch")
```

### Validation

- [ ] Chart renders without errors
- [ ] `width="stretch"` used for responsive display
- [ ] Title and axis labels present
- [ ] Colorblind-safe palette applied
- [ ] Interactivity works (hover tooltips, zoom, pan)

### Post-Execution Checklist

- [ ] All charts use `width="stretch"`
- [ ] Consistent styling across dashboard
- [ ] No console errors
- [ ] Charts render quickly (<2s)

## Plotly Express Quick Reference

### Chart Type Selection

**Trend over time:** `px.line()`, `px.area()`
**Category comparison:** `px.bar()`, `px.histogram()`
**Correlation/relationship:** `px.scatter()`
**Distribution:** `px.histogram()`, `px.box()`, `px.violin()`
**Part-to-whole:** `px.pie()`, `px.sunburst()`, `px.treemap()`
**Ranking:** `px.bar()` (horizontal)
**Geospatial 2D:** `px.scatter_map()`, `px.choropleth_map()`
**3D scatter:** `px.scatter_3d()`
**Flow/process:** `px.funnel()`, `px.sankey()`
**Matrix/correlation:** `px.imshow()`

### Basic Patterns

```python
import plotly.express as px
import streamlit as st

df = load_data()

fig = px.line(
    df,
    x='date',
    y='value',
    color='category',
    title='Trend Analysis',
    labels={'date': 'Date', 'value': 'Metric Value', 'category': 'Category'},
    hover_data=['additional_info']
)
st.plotly_chart(fig, width="stretch")
```

### Multi-Series with Color Mapping

```python
fig = px.bar(
    df,
    x='region',
    y='sales',
    color='product',
    barmode='group',
    title='Sales by Region and Product',
    color_discrete_map={
        'Product A': '#0173B2',
        'Product B': '#DE8F05', 
        'Product C': '#029E73'
    }
)
st.plotly_chart(fig, width="stretch")
```

### Distribution Analysis

```python
fig = px.histogram(
    df,
    x='value',
    color='category',
    marginal='box',
    nbins=50,
    title='Value Distribution by Category',
    opacity=0.7
)
st.plotly_chart(fig, width="stretch")

fig = px.violin(
    df,
    x='category',
    y='value',
    color='category',
    box=True,
    points='outliers',
    title='Distribution Comparison'
)
st.plotly_chart(fig, width="stretch")
```

## Faceting (Small Multiples)

```python
fig = px.scatter(
    df,
    x='x_metric',
    y='y_metric',
    color='category',
    facet_col='region',
    facet_row='year',
    facet_col_wrap=3,
    title='Metrics by Region and Year',
    category_orders={'region': ['North', 'South', 'East', 'West']}
)
fig.update_layout(height=600)
st.plotly_chart(fig, width="stretch")
```

## Animations

```python
fig = px.scatter(
    df,
    x='gdp_per_capita',
    y='life_expectancy',
    size='population',
    color='continent',
    hover_name='country',
    animation_frame='year',
    animation_group='country',
    log_x=True,
    size_max=60,
    range_x=[100, 100000],
    range_y=[25, 90],
    title='Development Over Time'
)
st.plotly_chart(fig, width="stretch")
```

## Graph Objects for Custom Charts

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=['Revenue', 'Costs', 'Profit', 'Margin'],
    specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
           [{'type': 'bar'}, {'type': 'indicator'}]]
)

fig.add_trace(
    go.Scatter(x=df['date'], y=df['revenue'], mode='lines+markers', name='Revenue'),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df['date'], y=df['costs'], mode='lines', name='Costs', fill='tozeroy'),
    row=1, col=2
)

fig.add_trace(
    go.Bar(x=df['quarter'], y=df['profit'], name='Profit'),
    row=2, col=1
)

fig.add_trace(
    go.Indicator(
        mode='gauge+number+delta',
        value=df['margin'].iloc[-1],
        delta={'reference': df['margin'].iloc[-2]},
        gauge={'axis': {'range': [0, 100]}},
        title={'text': 'Current Margin %'}
    ),
    row=2, col=2
)

fig.update_layout(height=600, title_text='Financial Dashboard')
st.plotly_chart(fig, width="stretch")
```

## Tile Maps (Geospatial 2D)

```python
fig = px.scatter_map(
    df,
    lat='latitude',
    lon='longitude',
    color='category',
    size='value',
    hover_name='name',
    hover_data=['address', 'status'],
    color_discrete_map={'Active': '#029E73', 'Inactive': '#D55E00'},
    zoom=10,
    map_style='carto-positron',
    title='Location Overview'
)
fig.update_layout(margin={'r': 0, 't': 50, 'l': 0, 'b': 0})
st.plotly_chart(fig, width="stretch")

fig = px.choropleth_map(
    df,
    geojson=geojson_data,
    locations='region_id',
    featureidkey='properties.id',
    color='metric_value',
    color_continuous_scale='Viridis',
    center={'lat': 37.7749, 'lon': -122.4194},
    zoom=8,
    opacity=0.6,
    title='Regional Metrics'
)
st.plotly_chart(fig, width="stretch")

fig = px.density_map(
    df,
    lat='latitude',
    lon='longitude',
    z='event_count',
    radius=15,
    zoom=10,
    map_style='stamen-terrain',
    title='Event Density'
)
st.plotly_chart(fig, width="stretch")
```

## Hierarchical Charts

```python
fig = px.sunburst(
    df,
    path=['continent', 'country', 'city'],
    values='population',
    color='gdp_per_capita',
    color_continuous_scale='RdBu',
    title='Population Hierarchy'
)
st.plotly_chart(fig, width="stretch")

fig = px.treemap(
    df,
    path=[px.Constant('All'), 'category', 'subcategory', 'item'],
    values='sales',
    color='profit_margin',
    color_continuous_scale='RdYlGn',
    title='Sales Breakdown'
)
st.plotly_chart(fig, width="stretch")
```

## Layout Customization

```python
fig.update_layout(
    title={'text': 'Chart Title', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='X Axis Label',
    yaxis_title='Y Axis Label',
    legend_title='Legend',
    font=dict(family='Arial', size=12),
    hovermode='x unified',
    template='plotly_white',
    margin=dict(l=60, r=20, t=60, b=60)
)

fig.update_xaxes(tickangle=45, tickformat='%Y-%m-%d')
fig.update_yaxes(tickprefix='$', tickformat=',.0f')
```

## Colorblind-Safe Palettes

```python
COLORBLIND_SAFE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#CA9161', '#FBAFE4', '#949494']

fig = px.bar(df, x='category', y='value', color='group',
             color_discrete_sequence=COLORBLIND_SAFE)

import plotly.colors
fig = px.scatter(df, x='x', y='y', color='category',
                 color_discrete_sequence=plotly.colors.qualitative.Safe)
```

## Performance Optimization

```python
if len(df) > 5000:
    fig = px.scatter(df, x='x', y='y', render_mode='webgl')

@st.cache_data(ttl=600)
def create_expensive_figure(data):
    fig = px.scatter_matrix(data, dimensions=['a', 'b', 'c', 'd'])
    return fig

fig = create_expensive_figure(df)
st.plotly_chart(fig, width="stretch")
```

## Common Anti-Patterns

**Anti-Pattern: Missing responsive width**
```python
st.plotly_chart(fig)
```

**Correct:**
```python
st.plotly_chart(fig, width="stretch")
```

**Anti-Pattern: Overusing Graph Objects**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='lines'))
fig.update_layout(title='Simple Line')
```

**Correct (simpler with Express):**
```python
fig = px.line(df, x='x', y='y', title='Simple Line')
```

**Anti-Pattern: Red-green color scheme**
```python
color_map = {'good': 'green', 'bad': 'red'}
```

**Correct:**
```python
color_map = {'good': '#029E73', 'bad': '#D55E00'}
```

## Validation Checklist

- [ ] Using `width="stretch"` for all charts
- [ ] Clear title and axis labels present
- [ ] Colorblind-safe palette used
- [ ] Appropriate chart type for data purpose
- [ ] Interactive features tested (hover, zoom, pan)
- [ ] Performance acceptable for data size
- [ ] Consistent styling across dashboard

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Graph Objects for Simple Charts

**Problem:**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='lines'))
fig.update_layout(title='Simple Line')
```

**Why It Fails:** Graph Objects require verbose code for simple visualizations. Plotly Express provides the same result with less code.

**Correct Pattern:**
```python
fig = px.line(df, x='x', y='y', title='Simple Line')
```

### Anti-Pattern 2: Red-Green Color Scheme

**Problem:**
```python
color_map = {'good': 'green', 'bad': 'red'}
```

**Why It Fails:** Red-green colorblindness affects ~8% of males. Use colorblind-safe alternatives.

**Correct Pattern:**
```python
color_map = {'good': '#029E73', 'bad': '#D55E00'}
```
