---
schema_version: v4.0
rule_version: v3.0.0
description: "Altair in Streamlit: explicit encoding types, labeled declarative charts, linked selections, current sizing API, row-limit handling and colorblind-safe schemes."
last_updated: 2026-10-07
keywords:
  - kw:altair declarative encoding
  - kw:vega-lite grammar
  - kw:mark_point mark_line mark_bar
  - kw:st.altair_chart
  - kw:interval selection brushing
  - kw:data type suffixes
token_budget: ~850
context_tier: Medium
depends:
  optional:
    - 101a-snowflake-streamlit-visualization.md  # Visualization overview and library selection
---
# Altair in Streamlit

## Scope

**What This Rule Covers:**
Vega-Altair charts via `st.altair_chart`: marks, encodings and type suffixes, transforms, layering, faceting and concatenation, interval/point selections and Streamlit selection events, themes, scales, row limits and error handling.

**When to Load This Rule:**
When building declarative statistical charts or linked views in Streamlit; load `101a-snowflake-streamlit-visualization.md` first for library selection.

## Contract

### Inputs and Prerequisites

- Installed Streamlit, Altair (v5 APIs such as `selection_point`/`selection_interval` and `add_params`) and optional VegaFusion versions for the runtime.
- Data shape, types and volume, chart question and existing themes or palettes.

### Mandatory

- Declare encoding types explicitly (`:Q`, `:N`, `:O`, `:T`) and cast columns to match (datetimes to datetime, categories to string) instead of relying on inference.
- Title charts and label axes and legends with units; add tooltips with formatted fields.
- Use the installed Altair API: v5 selections with `add_params` and `alt.condition`/`alt.when`; avoid removed v4 selection helpers.
- Size with the installed `st.altair_chart` API (`width`/`height`; `use_container_width` is deprecated); set explicit sub-chart sizes for faceted and concatenated charts.
- Respect Altair's default 5,000-row embedded-data limit: aggregate in Snowflake, sample with disclosure, or enable VegaFusion when installed rather than silently disabling the limit.
- Keep encodings readable: split overloaded charts into linked views instead of stacking many channels on one mark.
- Use colorblind-safe schemes (for example `viridis`, `tableau10`, or explicit safe ranges) and never color alone; avoid red-green conditional highlighting.
- When using `on_select` with Streamlit, name selections, handle empty selections and keep derived state in session state.
- Handle empty data and type errors with clear messages before rendering.
- Verify rendering, selections, tooltips and resize in the target runtime with realistic data.

### Execution Steps

1. Read data types, volume, versions and the chart question.
2. Build typed, labeled charts with transforms, selections and accessible schemes.
3. Run in the target runtime and test interaction, row-limit handling and resizing.
4. Report charts, versions, data handling and evidence.

### Validation

- Encoding types explicit and consistent with data.
- Current Altair and Streamlit APIs used; faceted sizes explicit.
- Row limits handled transparently; schemes colorblind-safe.
- Interactivity verified in the target runtime.

## References

- [st.altair_chart](https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart)
- [Vega-Altair](https://altair-viz.github.io/)
- [Encodings](https://altair-viz.github.io/user_guide/encodings/index.html)
- [Interactive charts](https://altair-viz.github.io/user_guide/interactions/index.html)
- [Large datasets](https://altair-viz.github.io/user_guide/large_datasets.html)
