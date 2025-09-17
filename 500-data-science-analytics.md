**Description:** Rules for performing data science and analytics on Snowflake, focusing on model lifecycle, advanced SQL, and specialized data types.
**AppliesTo:** `notebooks/**/*.ipynb`, `streamlit/**/*`, `models/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-16

# Data Science & Analytics Principles

## Purpose
Establish comprehensive rules for performing data science and analytics on Snowflake, focusing on model lifecycle management, advanced SQL techniques, and specialized data types to ensure reproducible and reliable analytical workflows.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Data science and analytics on Snowflake with ML lifecycle and advanced SQL patterns


## 1. Model Lifecycle & MLOps
- **Requirement:** Ensure reproducibility: pin dependencies, log seeds, and use a dataset snapshot or hash.
- **Requirement:** Use a model registry to store metadata for each version (parameters, metrics, data hash).
- **Requirement:** Establish and compare against a simple, interpretable baseline before complex models.
- **Requirement:** Do not train on unvalidated data; use a data quality gate (e.g., Great Expectations).
- **Requirement:** Keep artifacts and runs immutable; never overwrite past runs.
- **Always:** Implement model monitoring for drift and performance decay; define alert/retrain thresholds.
- **Always:** Store explainability artifacts (e.g., SHAP summaries) with the model.
- **Always:** When a notebook yields a final model, plan to refactor into production-ready scripts.

## 2. Feature Engineering & Preparation
- **Requirement:** Make feature definitions reproducible and versioned.
- **Requirement:** Avoid target leakage; features must not contain post-outcome information.
- **Requirement:** Avoid ad-hoc notebook transformations; prefer upstream computation in Snowflake SQL over Python loops.
- **Requirement:** Monitor feature drift and null ratios over time.
- **Always:** Deduplicate highly correlated features to reduce instability.

## 3. Advanced SQL for Analytics
- **Always:** Use window functions for intra-partition context (e.g., sessionization, ranking) instead of self-joins.
- **Requirement:** In window functions, include a deterministic `ORDER BY`.
- **Consider:** For large datasets, use approximate functions (e.g., `APPROX_PERCENTILE`) when exactness is not required.
- **Requirement:** Avoid deeply nested subqueries; segment logic with CTEs.
- **Always:** For SQL ML tasks, reference the Snowflake Cortex AI-SQL documentation: https://docs.snowflake.com/user-guide/snowflake-cortex/aisql

## 4. Specialized Data & Time Series
- **Requirement:** Keep time series data in a consistent timezone (preferably UTC). Convert to local time only for presentation.
- **Requirement:** Use Snowflake's native geospatial types and functions for spatial analysis.
- **Always:** For vector similarity search, use a vector store and store the embedding model version and dimensions.
- **Always:** Reference the official Snowflake documentation:
  - **SQL Reference**: https://docs.snowflake.com/en/sql-reference
  - **Geospatial Functions**: https://docs.snowflake.com/en/sql-reference/functions/geospatial-spatial-functions
  - **Vector Functions**: https://docs.snowflake.com/en/sql-reference/functions/vector-functions
  - **Snowflake Machine Learning**: https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview

## 5. Visualization Best Practices
- **Requirement:** Use an appropriate visualization tool (e.g., Streamlit for interactivity, SQL for quick dashboards).
- **Requirement:** Ensure visualizations are clear and purposeful; avoid clutter or misleading designs.
- **Always:** Include clear titles, labeled axes, and legends where necessary.
- **Always:** Choose the right chart type (e.g., line for trends, bar for comparisons).

## References

### External Documentation
- [Snowflake for Data Science](https://docs.snowflake.com/en/user-guide/data-science) - Data science workflows and best practices in Snowflake                                                                          
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex) - AI and machine learning capabilities in Snowflake                                                                                  
- [Snowflake ML Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview) - Machine learning development guide

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
- **Python Core**: `200-python-core.md`
- **Data Governance**: `600-data-governance-quality.md`
