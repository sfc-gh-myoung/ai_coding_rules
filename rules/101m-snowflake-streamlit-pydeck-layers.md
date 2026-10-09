---
schema_version: v4.0
rule_version: v3.0.0
description: "PyDeck layer reference: choose deck.gl layers by data shape, use correct per-layer parameters and accessors, compose layers deliberately and keep picking and data volume bounded."
last_updated: 2026-10-07
keywords:
  - kw:pydeck layer types
  - kw:HexagonLayer aggregation
  - kw:GeoJsonLayer extrusion
  - kw:ArcLayer flow visualization
  - kw:multi-layer composition
  - kw:deck.gl accessor syntax
  - kw:streamlit
token_budget: ~950
context_tier: Low
depends:
  optional:
    - 101j-snowflake-streamlit-viz-pydeck.md  # Core PyDeck patterns, ViewState, coordinate validation
---
# PyDeck Layer Reference

## Scope

**What This Rule Covers:**
Selecting and configuring deck.gl layers through pydeck (ScatterplotLayer, HexagonLayer, HeatmapLayer, ColumnLayer, GeoJsonLayer, ArcLayer, PathLayer, PointCloudLayer, TerrainLayer, H3 layers), accessors, picking and multi-layer composition.

**When to Load This Rule:**
When configuring specific PyDeck layers; load `101j-snowflake-streamlit-viz-pydeck.md` for view state, basemaps, validation and WebGL limits.

## Contract

### Inputs and Prerequisites

- Installed pydeck/deck.gl versions, data shape per layer (points, origin–destination pairs, paths, polygons/GeoJSON, H3 indexes, elevation tiles) and volume.
- Map purpose, interactivity needs and any external tile or data URLs with their access requirements.

### Mandatory

- Choose the layer from the data and question: Scatterplot for individual points, Hexagon/Grid/H3 or Heatmap for density, Column for values at locations, GeoJson/Polygon for areas and extrusion, Arc for flows, Path for routes, PointCloud for 3D points, Terrain for elevation tiles.
- Use parameters documented for that layer and version (for example meter-based `radius` and `coverage` on HexagonLayer, `radius_pixels`/`intensity`/`threshold` on HeatmapLayer); unknown or mismatched properties are silently ignored, so check the layer catalog.
- Accessors: string expressions (for example `"[longitude, latitude]"`) evaluate per row against column names; plain Python lists are constants. Do not pass whole pandas Series, and keep column names free of characters that break expressions.
- Precompute colors, sizes and elevations as columns in Snowflake or pandas, scaled to valid ranges (RGBA 0–255) with colorblind-safe palettes, rather than complex inline expressions.
- Set `pickable=True` only on layers that need hover or click and supply matching tooltip fields; picking large layers costs performance.
- Bound volume per layer: aggregate in Snowflake (H3 or grid cells, flow summaries, simplified polygons) and measure rendering instead of relying on fixed feature counts; client-side aggregation still transfers all points.
- External data, GeoJSON or tile URLs need trusted HTTPS sources, licensing compliance and, in Snowflake runtimes, an approved external access integration; prefer data from Snowflake.
- Compose multiple layers in one Deck in an intentional draw order (areas, then flows, then points) with consistent coordinate systems.
- Verify each layer renders, picks and performs correctly in the target runtime.

### Execution Steps

1. Read data shape, volume and versions; select layers for the question.
2. Prepare aggregated data and precomputed visual columns; configure layer-specific parameters and accessors.
3. Compose the Deck, render in the target runtime and test picking and performance.
4. Report layers, parameters, data preparation and verification evidence.

### Validation

- Layer type matches data and question; parameters valid for the layer.
- Accessors reference real columns; visual encodings precomputed and accessible.
- Picking scoped; data volume bounded; external sources approved.
- Rendering and interaction verified.

## References

- [deck.gl layer catalog](https://deck.gl/docs/api-reference/layers)
- [pydeck Layer](https://deckgl.readthedocs.io/en/latest/layer.html)
- [st.pydeck_chart](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart)
- [Snowflake H3 functions](https://docs.snowflake.com/en/sql-reference/functions/h3_latlng_to_cell)
