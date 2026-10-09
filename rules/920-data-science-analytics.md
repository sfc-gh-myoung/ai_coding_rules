---
schema_version: v4.0
rule_version: v5.0.0
description: "Data science on Snowflake: read-only investigation, leakage-safe features, warehouse-side processing, registry-versioned models, calibrated uncertainty and honest presentation."
last_updated: 2026-10-07
keywords:
  - kw:snowpark dataframe
  - kw:model registry versioning
  - kw:feature engineering leakage
  - kw:SHAP explainability
  - kw:SQL aggregation over loops
  - kw:pandas NaN handling
  - kw:uncertainty quantification intervals
token_budget: ~1200
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 200-python-core.md  # Python development patterns
  optional:
    - 100-snowflake-core.md  # Snowflake SQL patterns
    - 101-snowflake-streamlit-core.md  # Streamlit dashboard patterns
    - 252-python-pandas-core.md  # Pandas best practices
---
# Data Science and Analytics on Snowflake

## Scope

**What This Rule Covers:**
Analysis and ML on Snowflake with Snowpark/SQL: data investigation, quality gates, feature engineering, training and evaluation, Snowflake Model Registry versioning and lifecycle, explainability, monitoring and result presentation.

**When to Load This Rule:**
When performing analytics, feature engineering or model work against Snowflake data; load `100-snowflake-core.md` for SQL and `252-python-pandas-core.md` for local pandas work.

## Contract

### Inputs and Prerequisites

- Approved connection, role, warehouse and objects; question, target definition, prediction time, population and decision the analysis supports.
- Existing models, features, metric definitions, quality checks, dependency pins and authority for any compute, object creation or registry writes.

### Mandatory

- Investigate before recommending: schemas, row counts, per-column null rates, distributions, key uniqueness, date coverage and freshness using bounded read-only queries (filters, `LIMIT`, `SAMPLE`, `APPROX_*`). Running queries consumes credits and needs the approved warehouse; resizing warehouses, setting timeouts or creating tables are mutations requiring approval.
- Push filtering, joins and aggregation into Snowflake (SQL or Snowpark DataFrames); pull only the rows needed, use `to_pandas_batches()` for large local transfers and avoid row-by-row Python loops over large data.
- Bind user-provided values as parameters and validate identifiers; never interpolate untrusted input into SQL.
- Define the prediction time and build features only from data available at that time (point-in-time joins, as-of filtering); split by time or group when leakage is possible and fit preprocessing on training data only.
- Gate training on project-defined quality checks (DMFs, tests or expectations) with thresholds tied to the use case, not a universal score.
- Compare against a simple baseline, evaluate on held-out data with metrics matching the decision and class balance, and report calibration and subgroup performance where relevant.
- Version reproducible artifacts: pinned dependencies, seeds, data snapshot or query and version, and feature definitions. Log Model Registry versions with metrics, sample input and dependencies; promote using default version, aliases or tags per the project's governance, with privileges CREATE MODEL on the schema and OWNERSHIP/USAGE/READ on models.
- Provide explanations appropriate to the model (SHAP, permutation or coefficient importance) and state that they describe model behavior, not causation.
- Report uncertainty for estimates, forecasts and predictions (confidence or prediction intervals, bootstrap, backtests) and state assumptions, sample sizes and data windows.
- Monitor production models for data and prediction drift and performance using effect sizes and business thresholds (Snowflake ML Observability or project tooling), not p-values alone on large samples.
- Handle missing values deliberately: Snowflake NULL may arrive as NaN, None or NaT in pandas, so use `pd.isna`/`pd.notna` and document imputation.
- Present honestly: bar charts start at zero, label units and time windows, show intervals, avoid 3D or truncated-axis distortion, and meet accessible contrast and colorblind-safe palettes.
- Handle `SnowparkSQLException` with context and close sessions; never embed credentials in notebooks or code.
- Validate results by rerunning queries and tests; do not claim model quality, cost or performance without measured evidence.

### Execution Steps

1. Confirm question, target, prediction time and approved compute; run bounded read-only investigation.
2. Build leakage-safe features and a baseline, then train and evaluate candidate models on held-out data.
3. With approval, log and promote registry versions and configure monitoring; produce explanations and uncertainty.
4. Report findings, metrics with intervals, artifacts, cost/runtime observations and remaining limitations.

### Validation

- Investigation and processing ran warehouse-side with bounded transfers and no unapproved mutations.
- No temporal or target leakage; baseline and holdout evaluation recorded.
- Registry version reproducible with metrics, dependencies and documented promotion.
- Outputs include uncertainty, honest accessible visuals and stated limitations.

## References

- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Snowflake Model Registry](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)
- [Managing models](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management)
- [ML Observability](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-observability)
- [Data metric functions](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [SAMPLE](https://docs.snowflake.com/en/sql-reference/constructs/sample)
