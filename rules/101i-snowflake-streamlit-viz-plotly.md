---
schema_version: v4.0
rule_version: v3.0.0
description: "Plotly in Streamlit: Express-first charts, Graph Objects when needed, current width and map APIs, labeled colorblind-safe encodings, bounded data volume and verified interactivity."
last_updated: 2026-10-07
keywords:
  - kw:plotly express
  - kw:graph objects
  - kw:st.plotly_chart
  - kw:chart animations
  - kw:faceting subplots
  - kw:colorblind-safe palettes
token_budget: ~900
context_tier: Medium
depends:
  optional:
    - 101a-snowflake-streamlit-visualization.md  # Visualization overview and library selection
    - 101j-snowflake-streamlit-viz-pydeck.md  # PyDeck for 3D/geospatial
    - 940-business-analytics.md  # Dashboard design patterns
---
# Plotly in Streamlit

## Scope

**What This Rule Covers:**
Plotly Express and Graph Objects charts rendered with `st.plotly_chart`: chart selection, faceting, subplots, animations, tile maps, hierarchical charts, layout, palettes, selections, performance and error states.

**When to Load This Rule:**
When building or reviewing Plotly charts in Streamlit; load `101a-snowflake-streamlit-visualization.md` first for library selection.

## Contract

### Inputs and Prerequisites

- Installed Streamlit and Plotly versions for the runtime, data shape and volume, chart questions and existing styling conventions.

### Mandatory

- Use Plotly Express for standard charts and Graph Objects or `make_subplots` when Express cannot express the layout (mixed trace types, Sankey, indicators).
- Size with the installed `st.plotly_chart` API: `width` defaults to `"stretch"` in current versions and `use_container_width` is deprecated; set `height` deliberately for faceted or subplot figures.
- Use map functions available in the installed Plotly version (MapLibre-based `scatter_map`, `choropleth_map`, `density_map` in recent releases; check the installed version's deprecation notes before using `*_mapbox` variants) and tile styles that need no token unless one is managed as a secret.
- Title charts, label axes and legends with units, format ticks and hover values, and order categories meaningfully.
- Use colorblind-safe qualitative palettes (for example `px.colors.qualitative.Safe`) and diverging/sequential scales such as Viridis, Cividis or RdBu; avoid red-green scales like RdYlGn and never rely on color alone.
- Use 3D charts, pies with many slices and animations only when they aid the question; prefer small multiples for comparisons.
- Bound data volume: aggregate or sample in Snowflake, use WebGL (`render_mode="webgl"`, automatic above about 1,000 points) for dense scatter, and measure rendering rather than relying on fixed row cutoffs.
- When using selections (`on_select`), handle empty selections and keep selection state in session state.
- Handle empty data, missing columns and import errors with clear messages before building figures.
- Verify rendering, hover, zoom, selection and resize in the target runtime with realistic data.

### Execution Steps

1. Read data, versions and the chart question; choose chart type and API.
2. Build labeled, accessible figures with correct sizing, palettes and volume controls.
3. Run the app and test interactivity, empty states and performance.
4. Report charts, versions, evidence and limitations.

### Validation

- Express or Graph Objects used appropriately; current width and map APIs.
- Titles, labels, units and colorblind-safe palettes present; no red-green scales.
- Data volume bounded; empty and error states handled.
- Interactivity verified in the target runtime.

## References

- [st.plotly_chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Graph Objects](https://plotly.com/python/graph-objects/)
- [Tile maps](https://plotly.com/python/tile-scatter-maps/)
- [Discrete colors](https://plotly.com/python/discrete-color/)
