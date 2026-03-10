# Data Science & Analytics Principles

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** Data science, Snowflake, pandas, Snowpark, ML, model lifecycle, feature engineering, NaN handling, model versioning, Jupyter
**TokenBudget:** ~3750
**ContextTier:** High
**Depends:** 200-python-core.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Comprehensive rules for data science and analytics on Snowflake. Covers model lifecycle management, ML/AI insight presentation, advanced SQL techniques, performance optimization, and ethical visualization practices for reproducible, performant analytical workflows.

**When to Load This Rule:**
- Performing data science or ML tasks on Snowflake
- Building analytical workflows with Snowpark
- Creating ML models with Snowflake Model Registry
- Optimizing data science queries for performance
- Building Streamlit dashboards for analytics
- Implementing feature engineering pipelines

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **200-python-core.md** - Python development patterns

**Related:**
- **100-snowflake-core.md** - Snowflake SQL patterns
- **101-snowflake-streamlit-core.md** - Streamlit dashboard patterns
- **110-snowflake-model-registry.md** - Model versioning and registry
- **252-python-pandas-core.md** - Pandas best practices

### External Documentation

- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Snowflake Model Registry](https://docs.snowflake.com/en/developer-guide/snowpark-ml/model-registry/overview)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Contract

### Inputs and Prerequisites

- Snowflake connection with appropriate warehouse
- Python 3.11+ with snowflake-snowpark-python, pandas/polars, scikit-learn
- Model registry access (Snowflake Model Registry)
- Data quality validation framework (DMFs, Great Expectations)

### Mandatory

- MUST investigate data before recommending models or approaches. Investigation checklist:
  1. Row count: `SELECT COUNT(*) FROM table`
  2. Null percentages per column: `SELECT column_name, COUNT(*) - COUNT(column_name) AS nulls FROM table`
  3. Value distributions: `SELECT APPROX_PERCENTILE(col, ARRAY_CONSTRUCT(0.25, 0.5, 0.75, 0.95)) FROM table`
  4. Date range coverage: `SELECT MIN(date_col), MAX(date_col), DATEDIFF('day', MIN(date_col), MAX(date_col)) FROM table`
  5. Schema validation: Confirm expected columns exist with correct types
- MUST version model artifacts in Snowflake Model Registry with metrics and data lineage
- MUST profile data distributions and validate quality before setting thresholds or training. Quality gate:
  1. Run DMF checks or Great Expectations suite
  2. Verify quality score ≥0.9 (or project-defined threshold)
  3. Check for target leakage: no future-dated features relative to prediction target
  4. Confirm no duplicate rows in training set: `SELECT COUNT(*) - COUNT(DISTINCT key_col) FROM table`
- MUST use SQL aggregation over Python loops for large-scale data processing
- MUST quantify uncertainty (confidence intervals, prediction intervals) in all outputs

### Forbidden

- SELECT * FROM large_tables without LIMIT (cost explosion)
- Python loops over millions of rows (use SQL aggregation)
- Unversioned model artifacts (breaks reproducibility)
- Training on unvalidated data
- Misleading visualizations (truncated axes, 3D pie charts)
- Hardcoded credentials in notebooks

### Execution Steps

1. Investigate data: Read schemas, distributions, volumes BEFORE recommending
2. Establish baseline: Simple interpretable model before complex approaches
3. Validate data quality: Run DMF checks before training
4. Optimize SQL: Use Query Profile to validate performance and cost
5. Version everything: Pin dependencies, log seeds, hash datasets
6. Document metrics: Define calculations, owners, update frequency
7. Present with uncertainty: Show confidence intervals, not just point estimates
8. Monitor drift: Implement model and feature monitoring

### Output Format

- Reproducible notebook (Data Load, EDA, Feature Engineering, Modeling, Evaluation)
- SQL queries optimized (<5s execution)
- Streamlit dashboards (<2s load, cached operations)
- Model artifacts in registry with metadata, explainability

### Validation

**Success Criteria:**
- Query Profile <5s execution, <$0.10 cost for dashboard queries
- Model performance validated on holdout set
- Visualizations accessible (WCAG 2.1 AA, 4.5:1 contrast)
- Data freshness indicators present
- Model explainability artifacts generated

### Design Principles

- **Reproducibility First:** Pin dependencies, version data, log randomness
- **Performance at Scale:** SQL aggregation over Python loops; use APPROX_* functions
- **Cost Awareness:** Monitor warehouse consumption; cache results
- **Explainability Required:** Store SHAP values, feature importance with models
- **Ethical Visualization:** No misleading charts; transparent about uncertainty
- **Investigation-First:** Verify data characteristics before recommendations

### Post-Execution Checklist

- [ ] Snowpark DataFrame API used for data access
- [ ] Models versioned in Snowflake Model Registry
- [ ] Data quality validated (DMFs or Great Expectations)
- [ ] SQL optimized (Query Profile <5s)
- [ ] Streamlit caching implemented (`@st.cache_data`)
- [ ] SHAP values or feature importance generated
- [ ] Visualizations accessible (WCAG 2.1 AA)
- [ ] Dependencies pinned
- [ ] Uncertainty quantified (confidence intervals)

### Investigation Required

Before starting data science tasks on Snowflake, complete these checks:

1. **Check available warehouses:** `SHOW WAREHOUSES` — identify warehouse size appropriate for ML workloads (MEDIUM+ recommended for training)
2. **Review existing models:** `SHOW MODELS IN SCHEMA` — check if related models already exist in Model Registry
3. **Identify data freshness:** `SELECT MAX(loaded_at) FROM table` — confirm data is recent enough for analysis
4. **Check data volume:** `SELECT COUNT(*) FROM table` — determines SQL-first (>100K rows) vs Python-acceptable (<100K rows) approach
5. **Review existing features:** Check for existing feature engineering queries or feature stores in the schema
6. **Verify tool availability:** Confirm `snowflake-snowpark-python`, `scikit-learn`, `shap` are in project dependencies

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Loading Full Dataset into Python

```python
# BAD: Fetching millions of rows
df = session.sql("SELECT * FROM sales_fact").to_pandas()
filtered = df[df['region'] == 'US']
```

**Problem:** Pulls all data across network (slow, expensive), exhausts memory.

**Correct Pattern:**
```python
df = session.sql("""
    SELECT order_date, SUM(sales_amount) AS total_sales
    FROM sales_fact WHERE region = 'US'
    GROUP BY 1
""").to_pandas()
```

### Anti-Pattern 2: Misleading Y-Axis Truncation

```python
# BAD: Makes 3% growth look like 300% growth
fig = go.Figure(go.Bar(y=[95000, 96000, 97000]))
fig.update_yaxis(range=[94000, 98000])
```

**Problem:** Visually exaggerates small changes, misleads stakeholders.

**Correct Pattern:**
```python
fig.update_yaxis(range=[0, 100000])  # Zero baseline
fig.add_annotation(text="Sales grew 3% ($2K increase)")
```

### Anti-Pattern 3: Model Without Explainability

```python
# BAD: Black box
model.fit(X_train, y_train)
predictions = model.predict(X_test)  # No explanation!
```

**Problem:** Business can't understand drivers, impossible to debug.

**Correct Pattern:**
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)
st.pyplot(shap.plots.waterfall(shap_values[0]))
```

### Anti-Pattern 4: Training on Unvalidated Data

```python
# BAD: No quality checks
model.fit(X_train, y_train)
```

**Problem:** Data quality issues corrupt model.

**Correct Pattern:**
```python
quality_report = dqm.check_data_quality(table="customer_features")
if quality_report['quality_score'] < 0.9:
    raise ValueError(f"Data quality insufficient: {quality_report['issues']}")
model.fit(X_train, y_train)
```

### Anti-Pattern 5: No Confidence Intervals

```python
# BAD: Point estimates only
st.metric("Predicted Revenue", f"${prediction:,.0f}")
```

**Problem:** Stakeholders don't understand uncertainty.

**Correct Pattern:**
```python
st.metric("Predicted Revenue", f"${point:,.0f}",
          help=f"95% CI: ${lower:,.0f} - ${upper:,.0f}")
```

## Pandas NULL Handling

**Critical:** Snowflake NULL becomes pandas NaN, not Python None.

```python
# BAD: Doesn't catch NaN
if duration is not None: formatted = f"{duration:.1f}s"

# GOOD: Use pandas-aware functions
import pandas as pd
if pd.notna(duration): formatted = f"{duration:.1f}s"
```

**Always use:** `pd.notna(x)`, `pd.isna(x)`, `df.fillna()`, `df.dropna()`
**Never use on DataFrames:** `x is None`, `x == None`, `not x`

## Model Lifecycle and MLOps

**Reproducibility:**
```python
registry.log_model(
    model=trained_model, model_name="customer_churn",
    version_name="v2", metrics={"accuracy": 0.89},
    tags={"data_hash": data_hash}
)
```

**Baseline & Validation:** Always compare against simple baseline; implement data quality gates.

**Monitoring:** Detect drift with statistical tests:
```python
ks_stat, p_value = ks_2samp(baseline_preds, current_preds)
if p_value < 0.05: alert("Model drift detected")
```

**Explainability:** Store SHAP values with model artifacts.

## Feature Engineering

**Avoid Target Leakage:**
```sql
-- BAD: Future information
SELECT customer_id, total_purchases_next_30_days FROM customers;

-- GOOD: Only historical features
SELECT customer_id, avg_purchase_last_90_days FROM customers
WHERE as_of_date <= training_date;
```

**SQL-First Approach:**
```python
# BAD: Python loops
for customer_id in ids: features = calculate(customer_id)

# GOOD: SQL aggregation
features = session.sql("""
    SELECT customer_id, COUNT(*) AS cnt, AVG(amount) AS avg
    FROM purchases GROUP BY 1
""").to_pandas()
```

## Advanced SQL for Analytics

**Window Functions:**
```sql
SELECT customer_id, order_date, order_amount,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rank
FROM orders QUALIFY rank <= 5;
```

**Approximate Functions (for 100M+ rows):**
```sql
SELECT region, APPROX_COUNT_DISTINCT(customer_id) AS unique_customers,
       APPROX_PERCENTILE(order_amount, 0.5) AS median
FROM orders GROUP BY region;
```

**Sampling for EDA:**
```sql
SELECT * FROM large_table SAMPLE (1);  -- 1% sample
SELECT * FROM large_table SAMPLE (10000 ROWS);  -- Fixed size
```

## ML Visualization Patterns

**Confusion Matrix:**
```python
cm = confusion_matrix(y_test, y_pred)
fig = ff.create_annotated_heatmap(z=cm, colorscale='Blues')
st.metric("Precision", f"{report['1']['precision']:.2%}")
```

**Feature Importance:**
```python
importance = pd.DataFrame({'feature': names, 'importance': model.feature_importances_})
fig = go.Figure(go.Bar(x=importance['importance'], y=importance['feature'], orientation='h'))
```

**Uncertainty Visualization:**
```python
fig.add_trace(go.Scatter(x=dates, y=point_estimates, name='Forecast'))
fig.add_trace(go.Scatter(x=dates, y=upper_bounds, fill='tonexty', name='95% Upper'))
```

## Performance Optimization

**SQL-First:**
```python
# Filter in SQL, not pandas (use parameterized queries to prevent injection)
query = session.sql(
    "SELECT * FROM sales_fact WHERE region = ? AND order_date >= DATEADD('year', -1, CURRENT_DATE()) LIMIT 10000",
    params=[selection]
).to_pandas()
```

**Streamlit Caching:** See 940-business-analytics.md for Streamlit caching patterns.

**Timeout Handling:**
```python
session.sql("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300").collect()
```

## Ethical Visualization

See 940-business-analytics.md for ethical visualization guidelines.

## Snowpark Error Handling

```python
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

try:
    result = session.sql("SELECT ...").collect()
except SnowparkSQLException as e:
    logger.error(f"Snowpark query failed: {e.message}")
    raise
```

MUST handle `SnowparkSQLException` in production Snowpark code. For session management, use context managers or explicit `session.close()` in finally blocks.

### Error Recovery Patterns

**Warehouse Timeout (query exceeds STATEMENT_TIMEOUT_IN_SECONDS):**
- Increase warehouse size: `ALTER WAREHOUSE wh SET WAREHOUSE_SIZE = 'LARGE'`
- Optimize query: Use `APPROX_*` functions, add filters, reduce data volume
- Use sampling for EDA: `SELECT * FROM table SAMPLE (10000 ROWS)`

**Out-of-Memory (DataFrame exceeds Python memory):**
- Switch to SQL aggregation — never pull raw rows to Python
- Use Snowpark DataFrame API instead of `to_pandas()` for transformations
- If pandas is required, use chunked reading: `session.sql("...").to_pandas_batches()`

**Model Convergence Failure:**
- Check data distributions for extreme outliers or skew
- Reduce feature count: start with top-N by importance
- Increase training iterations or adjust learning rate
- Verify no target leakage inflating apparent performance

**Snowflake Model Registry Errors:**
- `Model not found`: Verify model name and schema: `SHOW MODELS IN SCHEMA`
- `Version already exists`: Use a new version name or delete the existing version
- `Insufficient privileges`: Request MODEL_ADMIN role for the target schema

## Model Deployment Lifecycle

- **Registry:** Version all models in Snowflake Model Registry or MLflow with metrics, data lineage, and SHAP values
- **Staging:** Promote models through stages: development, staging, production
- **Deployment Checklist:** Validate on holdout set, stage in registry, run integration tests, promote to production
- **Monitoring:** Set up drift detection and performance monitoring before promoting to production

## AI Agent Integration

- Structure analysis outputs as structured data (JSON/YAML) for agent consumption
- Include metadata (timestamp, confidence score, data range, model version) with analysis results
- Design visualization functions to be callable programmatically, not just interactively
- Expose metric definitions as queryable data for agent self-service

### Structured Analysis Output Pattern

```python
import json
from datetime import datetime

def create_analysis_result(
    analysis_name: str,
    predictions: dict,
    model_version: str,
    confidence: float,
    data_range: tuple[str, str]
) -> dict:
    """Create structured output for AI agent consumption."""
    return {
        "analysis": analysis_name,
        "timestamp": datetime.utcnow().isoformat(),
        "model_version": model_version,
        "confidence": confidence,
        "data_range": {"start": data_range[0], "end": data_range[1]},
        "predictions": predictions,
        "metadata": {
            "framework": "snowpark-ml",
            "output_format": "json",
            "schema_version": "1.0"
        }
    }

# Usage:
result = create_analysis_result(
    analysis_name="customer_churn_prediction",
    predictions={"churn_rate": 0.15, "at_risk_count": 342},
    model_version="v2.1",
    confidence=0.89,
    data_range=("2025-01-01", "2025-12-31")
)
# Agent can parse: result["predictions"]["churn_rate"]
```

### Queryable Metric Definitions

```sql
-- Create a metrics registry table for agent self-service
CREATE TABLE IF NOT EXISTS analytics.metrics_registry (
    metric_name VARCHAR,
    calculation_sql VARCHAR,
    owner VARCHAR,
    update_frequency VARCHAR,
    last_calculated TIMESTAMP_NTZ,
    description VARCHAR
);

-- Agents can query available metrics:
SELECT metric_name, description, last_calculated
FROM analytics.metrics_registry
WHERE update_frequency = 'daily'
ORDER BY last_calculated DESC;
```
