# Streamlit Visualization: Altair Deep Dive

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-13
**Keywords:** altair, vega-lite, st.altair_chart, declarative visualization, grammar of graphics, mark_point, mark_line, mark_bar, encoding, selection, interactive, layered charts
**TokenBudget:** ~3350
**ContextTier:** Medium
**Depends:** 101a-snowflake-streamlit-visualization.md

## Scope

**What This Rule Covers:**
Altair visualization patterns using the declarative grammar of graphics approach. Altair excels at statistical visualizations and linked multi-view displays with minimal code.

**When to Load This Rule:**
- Building statistical/analytical visualizations
- Creating linked interactive views
- Rapid exploratory data analysis
- Declarative chart specification preferred
- Complex encoding relationships (color, size, shape by data)

## References

### Dependencies

**Must Load First:**
- **101a-snowflake-streamlit-visualization.md** - Visualization overview and library selection

**Related:**
- **101i-snowflake-streamlit-viz-plotly.md** - Plotly for general-purpose charts

### External Documentation

**Official Documentation:**
- [Altair Documentation](https://altair-viz.github.io/) - Official Vega-Altair docs
- [st.altair_chart()](https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart) - Streamlit integration
- [Vega-Lite](https://vega.github.io/vega-lite/) - Underlying grammar specification

**Best Practices:**
- [Altair Gallery](https://altair-viz.github.io/gallery/index.html) - Example visualizations
- [Encoding Types](https://altair-viz.github.io/user_guide/encoding.html) - Data encoding reference

## Contract

### Inputs and Prerequisites

- Streamlit 1.46+ with altair installed
- Data in pandas DataFrame format
- Understanding of declarative visualization concepts

### Mandatory

- **Declarative encoding** - Map data columns to visual properties
- **width="stretch"** - Use for responsive charts OR set explicit container width
- **Clear encoding** - Explicit axis titles and labels

### Forbidden

- Mixing imperative and declarative styles unnecessarily
- Missing axis labels/titles
- Overly complex single charts (split into linked views instead)

### Execution Steps

1. Import altair as alt and streamlit as st
2. Prepare data in pandas DataFrame format
3. Create Chart with appropriate mark type (point, line, bar, etc.)
4. Define encodings with data type suffixes (:Q, :N, :O, :T)
5. Add properties (title, dimensions) and configure styling
6. Render with `st.altair_chart(chart, use_container_width=True)`

### Output Format

```python
import altair as alt
import streamlit as st

chart = alt.Chart(df).mark_point().encode(
    x='x:Q', y='y:Q', color='category:N'
).properties(title='Chart Title')
st.altair_chart(chart, use_container_width=True)
```

### Validation

- [ ] Data type suffixes specified for all encodings
- [ ] `use_container_width=True` used for responsive display
- [ ] Clear axis titles and labels present
- [ ] Appropriate chart type for data relationship
- [ ] Interactive selections tested (if applicable)

### Post-Execution Checklist

- [ ] All charts use `use_container_width=True`
- [ ] Colorblind-safe color schemes applied
- [ ] Tooltips configured for hover information
- [ ] Large datasets sampled or using vegafusion

## When to Use Altair vs Plotly

**Quick statistical exploration:** Use **Altair** - concise syntax
**Linked brushing/selection:** Use **Altair** - native support
**Complex dashboard:** Use **Plotly** - more layout control
**Maps/geospatial:** Use **Plotly** - better map support
**Animations:** Use **Plotly** - native animation_frame
**3D visualizations:** Use **Plotly** - scatter_3d, surface
**Custom interactivity:** Use **Plotly** - more flexibility

## Core Altair Concepts

### Grammar of Graphics

```python
import altair as alt
import streamlit as st

chart = alt.Chart(df).mark_point().encode(
    x='x_column:Q',
    y='y_column:Q',
    color='category:N',
    size='value:Q'
).properties(
    title='Scatter Plot'
)

st.altair_chart(chart, use_container_width=True)
```

### Data Types

**`:Q` (Quantitative):** Continuous numeric values
**`:N` (Nominal):** Categorical, unordered
**`:O` (Ordinal):** Categorical, ordered
**`:T` (Temporal):** Date/time values

## Basic Chart Types

### Scatter Plot

```python
chart = alt.Chart(df).mark_point().encode(
    x=alt.X('x:Q', title='X Axis Label'),
    y=alt.Y('y:Q', title='Y Axis Label'),
    color=alt.Color('category:N', legend=alt.Legend(title='Category')),
    tooltip=['name', 'x', 'y', 'category']
).properties(
    title='Scatter Plot',
    width=600,
    height=400
)
st.altair_chart(chart, use_container_width=True)
```

### Line Chart

```python
chart = alt.Chart(df).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('value:Q', title='Value'),
    color='series:N',
    strokeDash='series:N'
).properties(
    title='Time Series'
)
st.altair_chart(chart, use_container_width=True)
```

### Bar Chart

```python
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('category:N', sort='-y', title='Category'),
    y=alt.Y('value:Q', title='Value'),
    color=alt.Color('category:N', legend=None)
).properties(
    title='Bar Chart'
)
st.altair_chart(chart, use_container_width=True)
```

### Histogram

```python
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('value:Q', bin=alt.Bin(maxbins=30), title='Value'),
    y=alt.Y('count()', title='Frequency'),
    color='category:N'
).properties(
    title='Distribution'
)
st.altair_chart(chart, use_container_width=True)
```

### Heatmap

```python
chart = alt.Chart(df).mark_rect().encode(
    x=alt.X('x_category:O', title='X'),
    y=alt.Y('y_category:O', title='Y'),
    color=alt.Color('value:Q', scale=alt.Scale(scheme='viridis'), title='Value')
).properties(
    title='Heatmap'
)
st.altair_chart(chart, use_container_width=True)
```

### Box Plot

```python
chart = alt.Chart(df).mark_boxplot().encode(
    x=alt.X('category:N', title='Category'),
    y=alt.Y('value:Q', title='Value'),
    color='category:N'
).properties(
    title='Distribution by Category'
)
st.altair_chart(chart, use_container_width=True)
```

## Layered Charts

```python
base = alt.Chart(df).encode(
    x=alt.X('date:T', title='Date')
)

line = base.mark_line().encode(
    y=alt.Y('value:Q', title='Value')
)

points = base.mark_point(filled=True, size=50).encode(
    y='value:Q',
    color=alt.condition(
        alt.datum.value > threshold,
        alt.value('red'),
        alt.value('steelblue')
    )
)

rule = alt.Chart(pd.DataFrame({'y': [threshold]})).mark_rule(
    strokeDash=[5, 5],
    color='gray'
).encode(y='y:Q')

chart = (line + points + rule).properties(title='Trend with Threshold')
st.altair_chart(chart, use_container_width=True)
```

## Interactive Selection

### Interval Selection (Brushing)

```python
brush = alt.selection_interval()

points = alt.Chart(df).mark_point().encode(
    x='x:Q',
    y='y:Q',
    color=alt.condition(brush, 'category:N', alt.value('lightgray'))
).add_params(brush)

bars = alt.Chart(df).mark_bar().encode(
    x='count()',
    y='category:N',
    color='category:N'
).transform_filter(brush)

chart = points & bars
st.altair_chart(chart, use_container_width=True)
```

### Point Selection (Click)

```python
selection = alt.selection_point(fields=['category'])

chart = alt.Chart(df).mark_point().encode(
    x='x:Q',
    y='y:Q',
    color=alt.condition(selection, 'category:N', alt.value('lightgray')),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_params(selection)

st.altair_chart(chart, use_container_width=True)
```

### Legend Selection

```python
selection = alt.selection_point(fields=['category'], bind='legend')

chart = alt.Chart(df).mark_line().encode(
    x='date:T',
    y='value:Q',
    color='category:N',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.1))
).add_params(selection)

st.altair_chart(chart, use_container_width=True)
```

## Faceting (Small Multiples)

```python
chart = alt.Chart(df).mark_line().encode(
    x='date:T',
    y='value:Q',
    color='series:N'
).properties(
    width=200,
    height=150
).facet(
    column='region:N',
    row='year:O'
)

st.altair_chart(chart)
```

## Concatenation

### Horizontal Concatenation

```python
chart1 = alt.Chart(df).mark_bar().encode(x='category:N', y='value:Q')
chart2 = alt.Chart(df).mark_line().encode(x='date:T', y='value:Q')

combined = chart1 | chart2
st.altair_chart(combined, use_container_width=True)
```

### Vertical Concatenation

```python
combined = chart1 & chart2
st.altair_chart(combined, use_container_width=True)
```

## Data Transformations

```python
chart = alt.Chart(df).mark_bar().encode(
    x='category:N',
    y='mean(value):Q'
)

chart = alt.Chart(df).transform_filter(
    alt.datum.value > 0
).transform_calculate(
    log_value='log(datum.value)'
).mark_point().encode(
    x='x:Q',
    y='log_value:Q'
)

chart = alt.Chart(df).transform_window(
    rolling_mean='mean(value)',
    frame=[-7, 0]
).mark_line().encode(
    x='date:T',
    y='rolling_mean:Q'
)
```

## Styling and Themes

```python
alt.themes.enable('dark')

chart = alt.Chart(df).mark_point().encode(
    x='x:Q',
    y='y:Q'
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16,
    anchor='start'
).configure_legend(
    titleFontSize=12,
    labelFontSize=11
)
```

## Color Scales

```python
chart = alt.Chart(df).mark_point().encode(
    x='x:Q',
    y='y:Q',
    color=alt.Color('value:Q', scale=alt.Scale(scheme='viridis'))
)

chart = alt.Chart(df).mark_bar().encode(
    x='category:N',
    y='value:Q',
    color=alt.Color('category:N', scale=alt.Scale(
        domain=['A', 'B', 'C'],
        range=['#0173B2', '#DE8F05', '#029E73']
    ))
)
```

## Performance with Large Data

```python
alt.data_transformers.enable('vegafusion')

if len(df) > 5000:
    df_sample = df.sample(n=5000, random_state=42)
    st.caption(f"Showing sample of {5000:,} from {len(df):,} rows")
else:
    df_sample = df

chart = alt.Chart(df_sample).mark_point().encode(...)
```

## Common Anti-Patterns

**Anti-Pattern: Missing data type suffix**
```python
alt.Chart(df).encode(x='date', y='value')
```

**Correct:**
```python
alt.Chart(df).encode(x='date:T', y='value:Q')
```

**Anti-Pattern: Not using use_container_width**
```python
st.altair_chart(chart)
```

**Correct:**
```python
st.altair_chart(chart, use_container_width=True)
```

**Anti-Pattern: Overloading single chart**
```python
chart = alt.Chart(df).mark_point().encode(
    x='x:Q', y='y:Q', color='c1:N', size='s:Q', 
    shape='c2:N', opacity='o:Q', strokeWidth='sw:Q'
)
```

**Correct (split into linked views):**
```python
brush = alt.selection_interval()
scatter = alt.Chart(df).mark_point().encode(x='x:Q', y='y:Q', color='c1:N').add_params(brush)
detail = alt.Chart(df).mark_bar().encode(x='c2:N', y='count()').transform_filter(brush)
chart = scatter | detail
```

## Validation Checklist

- [ ] Using `use_container_width=True` for responsive display
- [ ] Data type suffixes specified (`:Q`, `:N`, `:O`, `:T`)
- [ ] Clear axis titles and labels
- [ ] Appropriate chart type for data relationship
- [ ] Large datasets sampled or using vegafusion
- [ ] Interactive selections tested
- [ ] Colorblind-safe color schemes
- [ ] Tooltips configured for hover information

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Fixed Chart Width

**Problem:**
```python
st.altair_chart(chart)
```

**Why It Fails:** Chart has fixed width, breaks on mobile and different screen sizes.

**Correct Pattern:**
```python
st.altair_chart(chart, use_container_width=True)
```

### Anti-Pattern 2: Overloading Single Chart

**Problem:**
```python
chart = alt.Chart(df).mark_point().encode(
    x='x:Q', y='y:Q', color='c1:N', size='s:Q', 
    shape='c2:N', opacity='o:Q', strokeWidth='sw:Q'
)
```

**Why It Fails:** Too many encodings make chart unreadable. Users can't interpret 7+ visual dimensions simultaneously.

**Correct Pattern:**
```python
brush = alt.selection_interval()
scatter = alt.Chart(df).mark_point().encode(
    x='x:Q', y='y:Q', color='c1:N'
).add_params(brush)
detail = alt.Chart(df).mark_bar().encode(
    x='c2:N', y='count()'
).transform_filter(brush)
chart = scatter | detail
```
