---
schema_version: v4.0
rule_version: v5.0.0
description: "Business analytics: documented KPIs, audience-fit reports, honest accessible visualizations and supported Snowflake delivery surfaces with freshness context."
last_updated: 2026-10-07
keywords:
  - kw:WCAG accessibility compliance
  - kw:KPI visualization
  - kw:data storytelling narrative
  - kw:ethical visualization standards
  - kw:snowsight
token_budget: ~1050
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 100-snowflake-core.md  # Snowflake SQL patterns
  optional:
    - 101-snowflake-streamlit-core.md  # Streamlit dashboard patterns
    - 920-data-science-analytics.md  # Analytics and visualization patterns
    - 132-snowflake-demo-modeling.md  # Data modeling and naming conventions
---
# Business Analytics and Reporting

## Scope

**What This Rule Covers:**
Business-facing queries, KPI reports and dashboards on Snowflake data: metric definitions, audience fit, layout, chart choice, ethical presentation, WCAG accessibility, freshness context and delivery through Streamlit, Workspaces or BI tools.

**When to Load This Rule:**
When building reports, dashboards or narratives for stakeholders; load `101-snowflake-streamlit-core.md` for Streamlit implementation and `920-data-science-analytics.md` for statistical analysis.

## Contract

### Inputs and Prerequisites

- Audience, decisions supported, KPI definitions and owners, existing reports, palettes and layout standards.
- Approved role/warehouse and read access to business-facing objects, delivery surface (Streamlit, BI tool, Workspaces), accessibility and performance requirements.

### Mandatory

- Confirm the audience, question and decision before building; scope KPI count and granularity to that audience rather than fixed per-role quotas.
- Use documented KPI definitions (calculation, grain, filters, owner, refresh cadence) from the canonical source; do not invent or silently redefine metrics, and flag conflicting definitions.
- Investigate schemas, volumes and freshness with bounded read-only queries; derive freshness from load or data timestamps, not view DDL `LAST_ALTERED`.
- Query explicit columns with filters and aggregation pushed into Snowflake; bind user-selected values as parameters and avoid `SELECT *` in delivered queries.
- Present business-friendly labels with units, currency, time window and Title Case display names; keep technical identifiers hidden unless users need them.
- Show data freshness, active filters, data coverage and known quality caveats on every report.
- Choose charts by question (trends as lines, comparisons as sorted bars, distributions as histograms/box plots); avoid 3D effects, pies with many small slices and unlabeled dual axes.
- Present honestly: zero baselines for bars, consistent intervals and scales, disclosed date ranges and comparisons, intervals or sample sizes for estimates, and no cherry-picking.
- Meet WCAG 2.2 AA: text contrast 4.5:1 (3:1 for large text and non-text graphics), color never the only encoding, keyboard operability, labelled controls, and text or table alternatives for charts.
- Prioritize key KPIs at top, group detail into tabs or drill-downs, and support responsive layouts without hover-only interactions.
- Snowsight Legacy Dashboards are retired and new ones cannot be created; deliver dashboards as Streamlit apps or approved BI tools, and migrate legacy dashboard JSON only with approval.
- Cache results according to data freshness (for example Streamlit `st.cache_data` with TTL aligned to refresh cadence) and measure query and load performance against the project's targets.
- Recommendations in narratives must follow from the evidence shown; state assumptions and uncertainty and do not fabricate figures.
- Verify accessibility, accuracy against source totals and performance before completion; do not claim compliance or speed from inspection alone.

### Execution Steps

1. Confirm audience, decisions, KPIs and delivery surface; investigate sources and freshness read-only.
2. Build queries and visuals with documented metrics, honest encodings, accessible palettes and context.
3. Reconcile figures to source, test contrast/keyboard/screen-reader access and measure performance.
4. Report deliverables, metric sources, verification evidence and limitations.

### Validation

- KPIs match canonical definitions and reconcile to source totals.
- Freshness, filters and caveats visible; labels include units and windows.
- Visualizations honest and WCAG 2.2 AA accessible.
- Delivery surface supported (no new Legacy Dashboards); performance measured.

## References

- [Legacy dashboards deprecation](https://docs.snowflake.com/en/release-notes/bcr-bundles/un-bundled/bcr-2260)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WebAIM contrast checker](https://webaim.org/resources/contrastchecker/)
