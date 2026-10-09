---
schema_version: v4.0
rule_version: v3.0.0
description: "PyDeck in Streamlit: deck.gl layers for 3D, aggregation and large geospatial data, explicit view state, managed basemap keys, validated coordinates and bounded WebGL usage."
last_updated: 2026-10-07
keywords:
  - kw:pydeck
  - kw:deck.gl layers
  - kw:3D geospatial
  - kw:WebGL context limit
  - kw:ViewState configuration
  - kw:hexbin aggregation
  - kw:streamlit
token_budget: ~1000
context_tier: Medium
depends:
  optional:
    - 101a-snowflake-streamlit-visualization.md  # Visualization overview and library selection
    - 101i-snowflake-streamlit-viz-plotly.md  # Plotly for 2D charts and maps
---
# PyDeck in Streamlit

## Scope

**What This Rule Covers:**
`st.pydeck_chart` with deck.gl layers (scatter, hexagon, column, polygon, GeoJSON, arc, terrain), view state, basemaps and API keys, tooltips, selections, data volume, WebGL limits and error handling; layer details in `101m-snowflake-streamlit-pydeck-layers.md`.

**When to Load This Rule:**
When maps need 3D, aggregation layers, many points or multi-layer compositing; use `101i-snowflake-streamlit-viz-plotly.md` for simple 2D maps.

## Contract

### Inputs and Prerequisites

- Installed Streamlit and pydeck versions for the runtime, coordinate columns and CRS (WGS84 longitude/latitude), data volume and map purpose.
- Basemap provider requirements (Carto default, Mapbox optional) and whether the runtime has external access for tiles.

### Mandatory

- Use PyDeck where it adds value (3D extrusion, hexbin/grid aggregation, arcs, terrain, very large point sets, layered composition); prefer Plotly for simple 2D maps.
- Set an explicit `pdk.ViewState` (latitude, longitude, zoom, pitch, bearing) or compute it from the data, and keep zoom/pitch bounds sensible for the extent.
- Validate coordinates before rendering: drop NULLs, range-check latitude (−90..90) and longitude (−180..180), confirm longitude/latitude order and report filtered rows.
- Basemaps: Streamlit uses Carto tiles by default; Mapbox styles require a key passed through `api_keys` or `MAPBOX_API_KEY` from managed secrets, never hard-coded. In Snowflake runtimes, tile hosts may need an external access integration, or use `map_style=None`.
- Size with the installed API (`width="stretch"` default and explicit `height`; `use_container_width` is deprecated).
- Each chart is a WebGL context and browsers cap contexts per page; combine layers into one deck, isolate maps in tabs or pages, and measure rather than assuming a fixed count.
- Bound data: aggregate (H3, hexagon or grid) or sample in Snowflake before transfer, pass only needed columns and use pixel radius limits for dense points; disclose sampling.
- Tooltips show labeled, formatted fields; render untrusted text only through text tooltips, not raw HTML.
- Accessor expressions must reference existing columns; prefer precomputed color/size columns over complex JavaScript expressions.
- Cache data loading, not Deck objects, and handle empty data and rendering failures with clear messages.
- Verify rendering, interaction and basemap loading in the target runtime and browsers.

### Execution Steps

1. Read data, coordinates, volume, versions and basemap constraints; confirm PyDeck is warranted.
2. Prepare validated, aggregated data and build layers, view state, tooltips and basemap configuration.
3. Run in the target runtime and test interaction, performance and basemap access.
4. Report layers, data handling, keys/integrations required and verification evidence.

### Validation

- PyDeck justified; view state explicit; coordinates validated.
- Basemap keys managed as secrets; tile access available or basemap disabled.
- WebGL usage bounded; data aggregated or sampled with disclosure.
- Rendering verified in the target runtime.

## References

- [st.pydeck_chart](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart)
- [pydeck](https://deckgl.readthedocs.io/en/latest/)
- [deck.gl layer catalog](https://deck.gl/docs/api-reference/layers)
- [External network access](https://docs.snowflake.com/en/developer-guide/external-network-access/external-network-access-overview)
