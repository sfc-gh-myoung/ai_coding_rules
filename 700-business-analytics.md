**Description:** Directives for creating business-oriented queries, reports, and visualizations for a business audience.
**AppliesTo:** `**/*.sql`, `reports/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Business Analytics & Reporting Directives

## Purpose
Provide directives for creating business-oriented queries, reports, and visualizations targeted at non-technical stakeholders, emphasizing clarity, actionable insights, and effective data storytelling.

## 1. Persona and Goal
- **Requirement:** Target a business analyst audience; provide clear, actionable insights for non-technical stakeholders (marketing, finance, operations).
- **Requirement:** Emphasize what happened and business implications, not technical implementation details.

## 2. Query Principles
- **Requirement:** Ensure queries are human-readable; avoid unnecessary complexity.
- **Requirement:** Use descriptive column aliases (e.g., `total_sales`, `customer_country`); avoid cryptic aliases.
- **Requirement:** Output only meaningful business columns; exclude technical identifiers unless requested.
- **Always:** Focus on aggregation and summarization (`SUM`, `COUNT`, `AVG`, `GROUP BY`, `CASE`).

## 3. Visualization and Reporting
- **Requirement:** Make visualizations self-explanatory with clear titles, labeled axes, and legends.
- **Always:** Choose the right chart type for the data:
  - **Trends over time**: Line charts.
  - **Comparisons between categories**: Bar charts.
  - **Composition of a whole**: Pie charts or stacked bar charts (use sparingly).
  - **Distribution**: Histograms or box plots.
- **Always:** Structure reports with a clear narrative: start with key findings, followed by supporting charts and data.

## 4. Documentation & Communication
- **Requirement:** Include a business-oriented explanation of findings; translate technical outputs into plain language answering a business question.
- **Always:** Provide guidance on filters/parameters.
- **Always:** State assumptions (e.g., data freshness, filtering criteria).
