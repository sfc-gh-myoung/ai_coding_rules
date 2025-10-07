**Description:** Directives for creating business-oriented queries, reports, and visualizations for a business audience.
**AppliesTo:** `**/*.sql`, `reports/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~200
**ContextTier:** Low

# Business Analytics & Reporting Directives

## Purpose
Provide directives for creating business-oriented queries, reports, and visualizations targeted at non-technical stakeholders, emphasizing clarity, actionable insights, and effective data storytelling.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Business-oriented queries, reports, and visualizations for business audience consumption


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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Business Intelligence Best Practices](https://docs.microsoft.com/en-us/power-bi/guidance/) - Microsoft Power BI guidance for business analytics                                                                      
- [Data Visualization Principles](https://www.tableau.com/learn/articles/data-visualization) - Tableau's guide to effective data visualization                                                                          
- [SQL for Business Analysis](https://mode.com/sql-tutorial/) - Comprehensive SQL tutorial focused on business analytics

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Streamlit UI**: `101-snowflake-streamlit-ui.md`
- **Data Governance**: `600-data-governance-quality.md`
