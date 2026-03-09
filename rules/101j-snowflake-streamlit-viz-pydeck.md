# Streamlit Visualization: PyDeck Deep Dive

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** pydeck, st.pydeck_chart, deck.gl, 3D visualization, hexagon layer, scatterplot layer, geojson layer, arc layer, heatmap layer, terrain, point cloud, WebGL, geospatial
**TokenBudget:** ~2550
**ContextTier:** Medium
**Depends:** 101a-snowflake-streamlit-visualization.md

## Scope

**What This Rule Covers:**
PyDeck (deck.gl) visualization patterns for Streamlit, including 3D visualizations, hexbin aggregation, terrain rendering, and large-scale geospatial data. PyDeck excels where Plotly reaches limitations.

**When to Load This Rule:**
- Creating 3D extruded visualizations
- Hexbin aggregation for dense point data
- Rendering terrain or elevation data
- Visualizing point clouds
- Large datasets (>100k points) requiring GPU acceleration
- Complex multi-layer geospatial compositing

## References

### Dependencies

**Must Load First:**
- **101a-snowflake-streamlit-visualization.md** - Visualization overview and library selection

**Related:**
- **101i-snowflake-streamlit-viz-plotly.md** - Plotly for 2D charts and maps

### External Documentation

**Official Documentation:**
- [st.pydeck_chart()](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart) - Streamlit integration
- [PyDeck Documentation](https://deckgl.readthedocs.io/en/latest/) - Python library docs
- [deck.gl Layer Catalog](https://deck.gl/docs/api-reference/layers) - All available layers

**Best Practices:**
- [PyDeck Layer Overview](https://deckgl.readthedocs.io/en/latest/layer.html) - Layer configuration guide

## Contract

### Inputs and Prerequisites

- Streamlit 1.46+ with pydeck installed
- Data with latitude/longitude coordinates
- Understanding of WebGL limitations

### Mandatory

- **width="stretch"** - Always use for responsive maps
- **WebGL limit awareness** - Maximum ~8 PyDeck charts per page
- **ViewState configuration** - Always set initial view (lat, lon, zoom, pitch, bearing)
- **Coordinate validation** - Validate lat/lon before rendering

### Forbidden

- More than 8 PyDeck charts on single page (WebGL context limit)
- Missing ViewState configuration
- Unvalidated coordinates
- Using PyDeck for simple 2D maps (use Plotly instead)

### Execution Steps

1. Import pydeck as pdk and streamlit as st
2. Validate coordinate data (lat/lon within valid ranges)
3. Select layer type per PyDeck vs Plotly decision matrix (When to Use section)
4. Configure ViewState (latitude, longitude, zoom, pitch, bearing)
5. Create Deck combining layers and view state
6. Render with `st.pydeck_chart(deck, width="stretch")`

### Output Format

```python
import pydeck as pdk
import streamlit as st

layer = pdk.Layer('ScatterplotLayer', data=df, get_position='[longitude, latitude]')
view_state = pdk.ViewState(latitude=37.77, longitude=-122.4, zoom=10)
deck = pdk.Deck(layers=[layer], initial_view_state=view_state)
st.pydeck_chart(deck, width="stretch")
```

### Validation

- [ ] ViewState configured with valid coordinates
- [ ] Coordinate data validated before rendering
- [ ] Maximum 8 PyDeck charts per page
- [ ] `width="stretch"` used for responsive display
- [ ] Tooltips configured for interactivity

### Post-Execution Checklist

- [ ] All PyDeck charts use `width="stretch"`
- [ ] WebGL limit not exceeded
- [ ] Map renders correctly with all layers
- [ ] Tooltips display on hover

## When to Use PyDeck vs Plotly

**2D scatter map:** Use **Plotly** `px.scatter_map()`
**2D choropleth:** Use **Plotly** `px.choropleth_map()`
**3D extruded buildings:** Use **PyDeck** `PolygonLayer`
**Hexbin aggregation:** Use **PyDeck** `HexagonLayer`
**Point cloud (>100k):** Use **PyDeck** `ScatterplotLayer`
**Arc/flow visualization:** Use **PyDeck** `ArcLayer`
**Terrain/elevation:** Use **PyDeck** `TerrainLayer`
**Simple line routes:** Use **Plotly** `px.line_map()`
**Animated timeline:** Use **Plotly** (animation_frame)

## Core PyDeck Structure

```python
import pydeck as pdk
import streamlit as st

layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_color='[200, 30, 0, 160]',
    get_radius=100,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=37.7749,
    longitude=-122.4194,
    zoom=11,
    pitch=45,
    bearing=0
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={'text': '{name}\nValue: {value}'}
)

st.pydeck_chart(deck, width="stretch")
```

## Common Layer Patterns

See **101m-snowflake-streamlit-pydeck-layers.md** for complete layer patterns: ScatterplotLayer, HexagonLayer, GeoJsonLayer, ArcLayer, ColumnLayer, HeatmapLayer, PathLayer, TerrainLayer, PointCloudLayer, and multi-layer composition.

## ViewState Configuration

```python
view_state = pdk.ViewState(
    latitude=37.7749,
    longitude=-122.4194,
    zoom=11,
    min_zoom=5,
    max_zoom=18,
    pitch=45,
    bearing=-27
)

view_state = pdk.data_utils.compute_view(points_df[['longitude', 'latitude']])
view_state.pitch = 45
view_state.bearing = 0
```

## Map Styles

```python
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/light-v10'
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=None
)
```

**Available Mapbox styles:**
- `mapbox://styles/mapbox/light-v10` - Light theme
- `mapbox://styles/mapbox/dark-v10` - Dark theme
- `mapbox://styles/mapbox/streets-v11` - Street map
- `mapbox://styles/mapbox/satellite-v9` - Satellite imagery
- `None` - No basemap (transparent)

## Coordinate Validation

```python
def validate_coordinates(df, lat_col='latitude', lon_col='longitude'):
    """Validate and clean coordinate data for PyDeck."""
    df_clean = df.dropna(subset=[lat_col, lon_col])
    df_clean = df_clean[
        (df_clean[lat_col].between(-90, 90)) &
        (df_clean[lon_col].between(-180, 180))
    ]
    
    if len(df_clean) == 0:
        st.warning("No valid coordinates found")
        return None
    
    if len(df_clean) < len(df):
        st.info(f"Filtered {len(df) - len(df_clean)} invalid coordinates")
    
    return df_clean

df_valid = validate_coordinates(df)
if df_valid is not None:
    st.pydeck_chart(deck, width="stretch")
```

## Expression Parser

PyDeck supports JavaScript expressions for dynamic styling:

```python
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_color='[status == "active" ? 0 : 255, status == "active" ? 255 : 0, 0, 180]',
    get_radius='value > 100 ? 500 : 200'
)
```

## Tooltips

```python
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        'html': '<b>{name}</b><br/>Value: {value}<br/>Status: {status}',
        'style': {
            'backgroundColor': 'steelblue',
            'color': 'white'
        }
    }
)
```

## Performance Considerations

```python
if len(df) > 100000:
    df_sample = df.sample(n=100000, random_state=42)
    st.info(f"Sampling {100000:,} of {len(df):,} points for performance")
else:
    df_sample = df

layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_sample,
    get_position='[longitude, latitude]',
    radius_min_pixels=1,
    radius_max_pixels=10
)
```

## WebGL Context Limit Warning

```python
MAX_PYDECK_CHARTS = 8

def render_pydeck_safely(deck, chart_count):
    """Render PyDeck chart with WebGL limit awareness."""
    if chart_count >= MAX_PYDECK_CHARTS:
        st.warning(f"WebGL limit reached ({MAX_PYDECK_CHARTS} charts max). Consider consolidating layers.")
        return chart_count
    
    st.pydeck_chart(deck, width="stretch")
    return chart_count + 1
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing ViewState

**Problem:** Creating PyDeck charts without initial view state configuration.
```python
deck = pdk.Deck(layers=[layer])
st.pydeck_chart(deck)
```

**Correct Pattern:**
```python
view_state = pdk.ViewState(latitude=37.77, longitude=-122.4, zoom=10)
deck = pdk.Deck(layers=[layer], initial_view_state=view_state)
st.pydeck_chart(deck, width="stretch")
```

### Anti-Pattern 2: Using PyDeck for Simple 2D Maps

**Problem:** Using PyDeck for simple scatter plots when Plotly is more appropriate.
```python
layer = pdk.Layer('ScatterplotLayer', data=df, ...)
```

**Correct (use Plotly for 2D):**
```python
fig = px.scatter_map(df, lat='latitude', lon='longitude', ...)
st.plotly_chart(fig, width="stretch")
```

### Anti-Pattern 3: Too Many PyDeck Charts

**Problem:** Creating separate PyDeck charts in a loop, hitting WebGL context limits.

```python
for region in regions:
    deck = pdk.Deck(layers=[create_layer(region)], ...)
    st.pydeck_chart(deck)
```

**Correct Pattern:**
```python
# Consolidate all regions into one chart with multiple layers
layers = [create_layer(region) for region in regions]
deck = pdk.Deck(layers=layers, initial_view_state=view_state)
st.pydeck_chart(deck, width="stretch")
```

## Validation Checklist

- [ ] Using `width="stretch"` for responsive display
- [ ] ViewState configured with valid lat (-90 to 90), lon (-180 to 180), zoom (5-18), pitch (0-60)
- [ ] Coordinates validated before rendering
- [ ] Maximum 8 PyDeck charts per page
- [ ] Using PyDeck only for 3D/hexbin/terrain use cases
- [ ] Tooltips configured for interactivity
- [ ] Large datasets sampled or aggregated
- [ ] Map style: light-v10 for data overlay, dark-v10 for glowing effects, None for clean 3D
