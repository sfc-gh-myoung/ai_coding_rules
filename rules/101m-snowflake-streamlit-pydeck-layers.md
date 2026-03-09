# PyDeck Layer Reference

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** pydeck layers, HexagonLayer, ScatterplotLayer, GeoJsonLayer, ArcLayer, ColumnLayer, HeatmapLayer, PathLayer, TerrainLayer, PointCloudLayer, multi-layer
**TokenBudget:** ~2450
**ContextTier:** Low
**Depends:** 101j-snowflake-streamlit-viz-pydeck.md

## Scope

**What This Rule Covers:**
Complete layer pattern reference for PyDeck visualization, including 8 layer types and multi-layer composition.

**When to Load This Rule:**
- Need specific PyDeck layer configuration syntax
- Building multi-layer geospatial visualizations
- Choosing between layer types for a specific use case

## References

### Dependencies

**Must Load First:**
- **101j-snowflake-streamlit-viz-pydeck.md** - Core PyDeck patterns, ViewState, coordinate validation

## Contract

### Inputs and Prerequisites

- PyDeck core patterns from 101j understood
- Data with latitude/longitude coordinates

### Mandatory

- Use layer patterns exactly as shown (deck.gl API is strict)
- Always include `pickable=True` for interactive layers

### Forbidden

- Mixing layer parameters between layer types

### Execution Steps

1. Select layer type based on use case
2. Configure layer with required parameters
3. Combine with ViewState from 101j

### Output Format

Configured PyDeck layer ready for `pdk.Deck(layers=[...])`.

### Validation

- Layer renders without JavaScript console errors
- Tooltips display on hover for pickable layers

### Post-Execution Checklist

- [ ] Layer type matches use case
- [ ] Required parameters set for chosen layer type
- [ ] pickable=True for interactive layers

## HexagonLayer (Density Aggregation)

```python
layer = pdk.Layer(
    'HexagonLayer',
    data=df,
    get_position='[longitude, latitude]',
    radius=200,
    elevation_scale=50,
    elevation_range=[0, 1000],
    extruded=True,
    coverage=0.8,
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=df['latitude'].mean(),
    longitude=df['longitude'].mean(),
    zoom=10,
    pitch=50,
    bearing=-27
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/dark-v10'
)
st.pydeck_chart(deck, width="stretch")
```

## ScatterplotLayer (Large Point Datasets)

```python
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_color='[category == "A" ? 255 : 0, category == "B" ? 255 : 0, 200, 180]',
    get_radius='value * 10',
    radius_min_pixels=2,
    radius_max_pixels=50,
    pickable=True,
    opacity=0.8,
    stroked=True,
    line_width_min_pixels=1
)
```

## GeoJsonLayer (Polygons with Extrusion)

```python
layer = pdk.Layer(
    'GeoJsonLayer',
    data=geojson_url,
    opacity=0.8,
    stroked=True,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation='properties.height',
    get_fill_color='[255, 255, properties.value * 2.55]',
    get_line_color=[255, 255, 255],
    pickable=True
)
```

## ArcLayer (Flow/Connection Visualization)

```python
layer = pdk.Layer(
    'ArcLayer',
    data=connections_df,
    get_source_position='[source_lon, source_lat]',
    get_target_position='[target_lon, target_lat]',
    get_source_color='[64, 255, 0]',
    get_target_color='[0, 128, 200]',
    get_width='flow_volume / 100',
    pickable=True,
    auto_highlight=True
)
```

## ColumnLayer (3D Bar Charts on Map)

```python
layer = pdk.Layer(
    'ColumnLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_elevation='value',
    elevation_scale=100,
    radius=50,
    get_fill_color='[value * 2, 100, 200, 200]',
    pickable=True,
    auto_highlight=True
)
```

## HeatmapLayer (Continuous Density)

```python
layer = pdk.Layer(
    'HeatmapLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_weight='intensity',
    aggregation=pdk.types.String('MEAN'),
    radius_pixels=50,
    intensity=1,
    threshold=0.05
)
```

## PathLayer (Routes/Trajectories)

```python
layer = pdk.Layer(
    'PathLayer',
    data=routes_df,
    get_path='coordinates',
    get_color='[255, 100, 100]',
    width_scale=20,
    width_min_pixels=2,
    get_width=5,
    pickable=True
)
```

## TerrainLayer (3D Terrain Visualization)

```python
layer = pdk.Layer(
    'TerrainLayer',
    elevation_decoder={
        'rScaler': 256,
        'gScaler': 1,
        'bScaler': 1/256,
        'offset': -32768
    },
    elevation_data='https://example.com/terrain-tiles/{z}/{x}/{y}.png',
    texture='https://example.com/satellite/{z}/{x}/{y}.png',
    bounds=[-122.52, 37.70, -122.35, 37.82]
)
```

## PointCloudLayer (Large Point Sets)

```python
layer = pdk.Layer(
    'PointCloudLayer',
    data=points_df,
    get_position='[longitude, latitude, elevation]',
    get_color='[255, height * 2, 0]',
    get_normal='[0, 0, 1]',
    point_size=2,
    pickable=True,
    auto_highlight=True
)
```

## Multi-Layer Composition

```python
scatter_layer = pdk.Layer(
    'ScatterplotLayer',
    data=points_df,
    get_position='[longitude, latitude]',
    get_color='[255, 0, 0, 160]',
    get_radius=50,
    pickable=True
)

arc_layer = pdk.Layer(
    'ArcLayer',
    data=connections_df,
    get_source_position='[src_lon, src_lat]',
    get_target_position='[dst_lon, dst_lat]',
    get_source_color='[0, 255, 0]',
    get_target_color='[255, 0, 0]',
    get_width=2
)

polygon_layer = pdk.Layer(
    'GeoJsonLayer',
    data=boundaries_geojson,
    opacity=0.3,
    stroked=True,
    filled=True,
    get_fill_color='[100, 100, 200, 80]',
    get_line_color='[255, 255, 255]'
)

deck = pdk.Deck(
    layers=[polygon_layer, arc_layer, scatter_layer],
    initial_view_state=view_state,
    tooltip={'text': '{name}'}
)
st.pydeck_chart(deck, width="stretch")
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Wrong Accessor Syntax for Layer Properties**

**Problem:** Passing Python lists or tuples directly to properties like `get_position` or `get_color` instead of using deck.gl's JavaScript accessor string syntax. This causes the layer to silently render nothing or throw cryptic JavaScript errors, since pydeck serializes these accessors as deck.gl expressions evaluated client-side.

```python
# WRONG - Python list won't be evaluated per-row
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position=[df['longitude'], df['latitude']],  # Passes entire Series objects
    get_color=(255, 0, 0),  # Tuple works for static, but inconsistent style
)
```

**Correct Pattern:** Use bracket-notation strings for column-based accessors, and Python lists only for static literal values.

```python
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',  # String accessor - evaluated per row
    get_color=[255, 0, 0, 180],            # Static list - same for all points
)
```

**Anti-Pattern 2: Forgetting `pickable=True` on Interactive Layers**

**Problem:** Configuring a tooltip on the Deck but omitting `pickable=True` on the layer. The map renders correctly but hover/click interactions silently do nothing, leading developers to debug the tooltip configuration when the actual issue is at the layer level.

```python
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_radius=100,
    # Missing pickable=True
)
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={'text': '{name}: {value}'}  # Tooltip configured but never triggers
)
```

**Correct Pattern:** Always set `pickable=True` on any layer that should respond to hover or click events.

```python
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_radius=100,
    pickable=True,  # Required for tooltip interaction
)
```

**Anti-Pattern 3: Mixing Up HexagonLayer and HeatmapLayer Parameters**

**Problem:** Applying HexagonLayer aggregation parameters (like `radius`, `elevation_scale`, `coverage`) to a HeatmapLayer, or vice versa. These layer types both visualize density but have completely different APIs. Mismatched parameters are silently ignored, producing unexpected visual output with no error.

```python
# WRONG - radius (meters) and coverage are HexagonLayer params, not HeatmapLayer
layer = pdk.Layer(
    'HeatmapLayer',
    data=df,
    get_position='[longitude, latitude]',
    radius=200,          # Ignored; HeatmapLayer uses radius_pixels
    coverage=0.8,        # HexagonLayer-only parameter
    elevation_scale=50,  # HeatmapLayer has no 3D extrusion
)
```

**Correct Pattern:** Use the correct parameters for each layer type. HeatmapLayer uses `radius_pixels`, `intensity`, and `threshold`. HexagonLayer uses `radius` (in meters), `coverage`, and `elevation_scale`.

```python
# HeatmapLayer - pixel-based parameters
heat_layer = pdk.Layer(
    'HeatmapLayer',
    data=df,
    get_position='[longitude, latitude]',
    get_weight='intensity',
    radius_pixels=50,
    intensity=1,
    threshold=0.05,
)

# HexagonLayer - meter-based parameters
hex_layer = pdk.Layer(
    'HexagonLayer',
    data=df,
    get_position='[longitude, latitude]',
    radius=200,
    elevation_scale=50,
    coverage=0.8,
    extruded=True,
    pickable=True,
)
```
