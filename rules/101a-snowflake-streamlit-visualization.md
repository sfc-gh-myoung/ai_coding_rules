---
schema_version: v4.0
rule_version: v6.0.0
description: "Streamlit visualization router: choose Plotly, Altair or PyDeck by need, size charts with current width API, label clearly, aggregate data and keep charts accessible."
last_updated: 2026-10-07
keywords:
  - kw:st.plotly_chart
  - kw:st.pydeck_chart
  - kw:st.altair_chart
  - kw:library selection
  - kw:use_container_width
  - kw:WebGL context limits
token_budget: ~950
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns
    - 101-snowflake-streamlit-core.md  # Streamlit core patterns
  optional:
    - 940-business-analytics.md  # Dashboard design patterns
    - 101h-snowflake-streamlit-timeseries.md  # Time series smoothing
---
# Streamlit Visualization Library Selection

## Scope

**What This Rule Covers:**
Choosing among Streamlit native charts, Plotly, Altair and PyDeck; chart sizing, labeling, data volume, WebGL limits, accessibility and empty/invalid data handling, routing to 101i/101k/101j/101m.

**When to Load This Rule:**
At the start of any Streamlit charting task; then load `101i-snowflake-streamlit-viz-plotly.md`, `101k-snowflake-streamlit-viz-altair.md` or `101j-snowflake-streamlit-viz-pydeck.md` for the chosen library.

## Contract

### Inputs and Prerequisites

- Question each chart answers, data shape and volume, interactivity and map needs, existing chart libraries and palettes.
- Installed Streamlit and library versions for the runtime (Conda channel or PyPI) and accessibility requirements.

### Mandatory

- Prefer the library already used by the app; otherwise Plotly for standard charts and simple 2D maps, Altair for declarative and linked selections, PyDeck for 3D, aggregation layers or large GPU point/layer rendering, and native `st.*_chart` for simple quick charts.
- Add only libraries available in the runtime's dependency source and pin them per runtime conventions.
- Size charts with the installed Streamlit API: current versions use `width="stretch"`/`"content"` or pixel widths and deprecate `use_container_width`; keep existing usage consistent and migrate when upgrading. Fixed sizes are acceptable where the layout requires them.
- Give every chart a title or heading, axis labels with units, legends where series exist and readable tooltips.
- Aggregate or sample in Snowflake before rendering; choose limits from measured rendering performance rather than fixed row thresholds.
- Plotly switches to WebGL above roughly 1,000 points and PyDeck always uses WebGL; browsers cap WebGL contexts per page, so limit simultaneous WebGL charts, isolate heavy maps, or use SVG rendering where appropriate.
- Handle empty results, NULLs and invalid coordinates (drop NaN, range-check latitude/longitude) before charting, with a clear message instead of a broken chart.
- Use colorblind-safe palettes, never color alone for meaning, adequate contrast, and provide a data table or text summary for critical charts.
- Avoid misleading encodings (truncated bar axes, inconsistent scales, 3D effects) per `940-business-analytics.md`.
- Verify charts render in the target runtime with real data volumes, interaction and resize; do not claim rendering from code review alone.

### Execution Steps

1. Identify the chart question, data volume, interactivity and existing libraries.
2. Select the library and load its specialized rule; prepare aggregated, validated data.
3. Implement labeled, accessible charts with correct sizing and empty-state handling.
4. Run the app in the target runtime, test interactions and report evidence and gaps.

### Validation

- Library justified and available in the runtime; versions pinned.
- Sizing uses the installed API; titles, labels and units present.
- Data aggregated and validated; empty states handled; WebGL usage bounded.
- Accessible palettes and alternatives provided; rendering verified.

## References

- [Streamlit chart elements](https://docs.streamlit.io/develop/api-reference/charts)
- [st.plotly_chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Vega-Altair](https://altair-viz.github.io/)
- [pydeck](https://deckgl.readthedocs.io/en/latest/)
