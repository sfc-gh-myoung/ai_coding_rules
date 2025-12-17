# Data Science & Analytics Principles

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Data science, Snowflake, pandas, Snowpark, ML, model lifecycle, feature engineering, NaN handling, model versioning, Jupyter
**TokenBudget:** ~6150
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Establish comprehensive rules for performing data science and analytics on Snowflake, focusing on model lifecycle management, ML/AI insight presentation, advanced SQL techniques, performance optimization, and ethical visualization practices to ensure reproducible, performant, and trustworthy analytical workflows.

## Rule Scope
Data science and analytics on Snowflake with ML lifecycle, visualization best practices, performance optimization, and Snowflake-native tooling integration

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use Snowpark for data access** - Avoid pandas read_sql, use Snowpark DataFrame
- **Version models in registry** - Every trained model must be versioned
- **Validate data quality** - Use DMFs before training
- **Optimize SQL first** - SQL aggregation before Python loops
- **Cache Streamlit data** - Use `@st.cache_data` for expensive queries
- **Document model explainability** - Include SHAP values and feature importance
- **Never SELECT * without LIMIT** - Causes cost explosion

**Quick Checklist:**
- [ ] Snowpark DataFrame API used
- [ ] Models versioned in registry
- [ ] Data quality validated
- [ ] SQL optimized (Query Profile <5s)
- [ ] Streamlit caching implemented
- [ ] SHAP values generated
- [ ] Visualizations accessible (WCAG AA)
## Contract

<contract>
<inputs_prereqs>
- Snowflake connection with appropriate warehouse (CPU/GPU based on workload)
- Python 3.11+ with snowflake-snowpark-python, pandas/polars, scikit-learn/snowflake-ml
- Jupyter/Snowflake Notebooks environment or Streamlit for visualization
- Model registry access (Snowflake Model Registry or external)
- Data quality validation framework (DMFs, Great Expectations)
- Query performance monitoring enabled (Query Profile access)
</inputs_prereqs>

<mandatory>
- Snowflake SQL (CTEs, window functions, aggregations)
- Python for ML/analytics (scikit-learn, snowflake-ml, pandas/polars)
- Snowflake Model Registry for model versioning
- Query Profile for cost/performance analysis
- Data quality frameworks (DMFs, Great Expectations)
- Streamlit for interactive dashboards
- Git for version control (notebooks, SQL, configs)
</mandatory>

<forbidden>
- SELECT * FROM large_tables without LIMIT (cost explosion)
- Python loops over millions of rows (use SQL aggregation)
- Unversioned model artifacts (breaks reproducibility)
- Training on unvalidated data (use data quality gates)
- Misleading visualizations (truncated axes without indicators, 3D pie charts)
- Hardcoded credentials or secrets in notebooks
</forbidden>

<steps>
1. **Investigate data first:** Read actual data schemas, distributions, volumes before recommending approaches
2. **Establish baseline:** Create simple interpretable model before complex approaches
3. **Validate data quality:** Run DMF checks or Great Expectations before training
4. **Optimize SQL:** Use Query Profile to validate performance and cost
5. **Version everything:** Pin dependencies, log seeds, hash datasets
6. **Document metrics:** Define calculations, owners, update frequency
7. **Present with uncertainty:** Show confidence intervals, not just point estimates
8. **Test accessibility:** Verify WCAG 2.1 AA compliance for visualizations
9. **Monitor drift:** Implement model and feature monitoring
10. **Refactor to production:** Convert successful notebooks to production scripts
</steps>

<output_format>
- Reproducible notebook with clear sections (Data Load, EDA, Feature Engineering, Modeling, Evaluation, Deployment)
- SQL queries optimized for performance (use CTEs, explicit columns, APPROX_* where appropriate)
- Streamlit dashboards with <2s load time, cached data operations
- Model artifacts stored in registry with metadata (parameters, metrics, data hash, explainability)
- Documentation including metric definitions, assumptions, data quality status
</output_format>

<validation>
1. Run Query Profile on all dashboard queries (verify <5s execution, <$0.10 cost)
2. Validate model performance on holdout set
3. Test visualizations with screen reader (NVDA, JAWS)
4. Check color contrast ratios (4.5:1 minimum)
5. Verify data freshness indicators present
6. Confirm all metrics have documented definitions
7. Test with production-like data volumes
8. Validate model explainability artifacts generated
</validation>

<design_principles>
- **Reproducibility First:** Pin dependencies, version data, log all randomness sources
- **Performance at Scale:** SQL aggregation over Python loops; use APPROX_* functions; sample for EDA
- **Cost Awareness:** Monitor warehouse consumption; optimize queries; cache results
- **Explainability Required:** Store SHAP values, feature importance, counterfactuals with models
- **Ethical Visualization:** No misleading charts; transparent about uncertainty; accessible to all users
- **Snowflake-Native:** Leverage Snowpark, Model Registry, Streamlit, Cortex AI
- **Investigation-First:** Verify data characteristics before recommending approaches
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Loading Full Dataset into Python**
```python
# BAD: Fetching millions of rows, then filtering
df = session.sql("SELECT * FROM sales_fact").to_pandas() # Expensive!
filtered = df[df['region'] == 'US']
```
**Problem:**
- Pulls all data across network (slow, expensive)
- Exhausts memory for large tables
- Wastes warehouse compute credits

**Correct Pattern:**
```python
# GOOD: Filter in SQL, aggregate before fetch
df = session.sql("""
 SELECT
 order_date,
 SUM(sales_amount) AS total_sales
 FROM sales_fact
 WHERE region = 'US'
 AND order_date >= DATEADD('month', -12, CURRENT_DATE())
 GROUP BY 1
""").to_pandas()
```
**Benefits:**
- 100x faster query execution
- Minimal memory usage
- Lower warehouse costs


**Anti-Pattern 2: Misleading Y-Axis Truncation**
```python
# BAD: Truncated axis exaggerates small changes
fig = go.Figure(go.Bar(x=['Q1', 'Q2', 'Q3'], y=[95000, 96000, 97000]))
fig.update_yaxis(range=[94000, 98000]) # Starts at 94K, not 0
```
**Problem:**
- Makes 3% growth look like 300% growth
- Misleads stakeholders into overreacting
- Violates ethical visualization principles

**Correct Pattern:**
```python
# GOOD: Include zero baseline or clearly mark truncation
fig = go.Figure(go.Bar(x=['Q1', 'Q2', 'Q3'], y=[95000, 96000, 97000]))
fig.update_yaxis(range=[0, 100000]) # Zero baseline for magnitude comparison
fig.add_annotation(text="Sales grew 3% ($2K increase)", xref="paper", yref="paper")
```
**Benefits:**
- Honest representation of magnitude
- Builds trust with stakeholders
- Avoids misinterpretation


**Anti-Pattern 3: Model Without Explainability**
```python
# BAD: Black box model with no interpretability
model = XGBClassifier()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
# No explanation of why predictions were made!
```
**Problem:**
- Business can't understand what drives predictions
- Impossible to debug model failures
- Regulatory compliance issues

**Correct Pattern:**
```python
# GOOD: Model with SHAP explanations
import shap

model = XGBClassifier()
model.fit(X_train, y_train)

# Generate and store explanations
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# Visualize for stakeholders
st.subheader("Why This Prediction?")
st.pyplot(shap.plots.waterfall(shap_values[0], show=False))

# Store with model
registry.log_artifact(
 model_name="churn_predictor",
 artifact_name="shap_explainer",
 artifact_data=explainer
)
```
**Benefits:**
- Stakeholders understand model drivers
- Easier to debug and improve
- Builds trust in AI systems


**Anti-Pattern 4: Training on Unvalidated Data**
```python
# BAD: Train directly on raw data
model.fit(X_train, y_train)
```
**Problem:**
- Data quality issues corrupt model
- Outliers and nulls cause training failures
- No awareness of data drift

**Correct Pattern:**
```python
# GOOD: Validate data quality first
from snowflake.ml.data_quality import DataQualityMonitor

# Run quality checks
dqm = DataQualityMonitor(session)
quality_report = dqm.check_data_quality(
 table="ml_features.customer_features",
 checks=["completeness", "uniqueness", "validity"]
)

if quality_report['quality_score'] < 0.9:
 raise ValueError(f"Data quality insufficient: {quality_report['issues']}")

# Proceed with training only if data passes
model.fit(X_train, y_train)
```
**Benefits:**
- Prevents garbage-in-garbage-out
- Early detection of data issues
- Higher quality models


**Anti-Pattern 5: No Confidence Intervals**
```python
# BAD: Point estimates only
st.metric("Predicted Revenue", f"${prediction:,.0f}")
```
**Problem:**
- Stakeholders don't understand uncertainty
- Overconfidence in predictions
- Poor decision-making

**Correct Pattern:**
```python
# GOOD: Show uncertainty ranges
st.metric(
 "Predicted Revenue",
 f"${point_estimate:,.0f}",
 help=f"95% Confidence Interval: ${lower_bound:,.0f} - ${upper_bound:,.0f}"
)

# Visualize prediction intervals
fig = go.Figure()
fig.add_trace(go.Scatter(
 x=dates, y=point_estimates, name='Forecast',
 line=dict(color='blue')
))
fig.add_trace(go.Scatter(
 x=dates, y=upper_bounds, name='95% Upper',
 fill='tonexty', line=dict(color='rgba(0,0,255,0.2)')
))
st.plotly_chart(fig)
```
**Benefits:**
- Transparent about model uncertainty
- Better risk assessment
- Informed decision-making

> **Investigation Required**
> When applying this rule:
>
> 1. **Read referenced data BEFORE making recommendations**
> - Check actual table schemas with `DESCRIBE TABLE`
> - Sample data to understand distributions
> - Check row counts and data volumes
>
> 2. **Verify assumptions against actual code/data**
> - Don't assume feature engineering logic
> - Don't guess model performance
> - Don't speculate about data quality
>
> 3. **Never speculate about data characteristics**
> - Don't say "this probably contains..." without checking
> - Don't assume column names or data types
> - Don't guess at cardinality or distributions
>
> 4. **If uncertain, explicitly state need to investigate:**
> - "Let me read the table schema first to give you accurate guidance."
> - "I need to check the actual data volumes before recommending an approach."
> - "Let me verify the current model performance before suggesting improvements."
>
> 5. **Make grounded, hallucination-free recommendations**
> - Base suggestions on actual observed data characteristics
> - Reference specific column names and values from investigation
> - Provide concrete examples from actual data
>
> **Example Investigation Pattern:**
> ```python
> # GOOD: Investigate first
> schema = session.sql("DESCRIBE TABLE sales_fact").collect()
> row_count = session.sql("SELECT COUNT(*) FROM sales_fact").collect()[0][0]
> sample = session.sql("SELECT * FROM sales_fact SAMPLE (100 ROWS)").to_pandas()
>
> # Now make informed recommendations
> if row_count > 1_000_000:
> st.info(" Large table detected. Recommend using APPROX_COUNT_DISTINCT for dashboard.")
> ```

## Post-Execution Checklist

- [ ] Data investigation completed before recommendations
- [ ] Data quality validation implemented (DMFs or Great Expectations)
- [ ] SQL queries optimized (CTEs, explicit columns, APPROX_* where appropriate)
- [ ] Query Profile analyzed for performance and cost
- [ ] Model artifacts versioned in registry with metadata
- [ ] Explainability artifacts generated (SHAP, feature importance)
- [ ] Visualizations show uncertainty (confidence intervals, prediction bands)
- [ ] Accessibility tested (WCAG 2.1 AA compliance, screen reader, keyboard nav)
- [ ] Data freshness and quality indicators displayed
- [ ] Metric definitions documented
- [ ] Streamlit caching implemented (@st.cache_data, @st.cache_resource)
- [ ] Ethical visualization standards followed (no misleading charts)
- [ ] Anti-patterns avoided (confirmed via checklist review)

## Validation

- **Success Checks:**
 - Query Profile shows <5s execution time and <$0.10 cost per query
 - Model achieves >80% performance on holdout set
 - SHAP values generated and stored with model
 - Visualizations pass WCAG 2.1 AA color contrast checker
 - Screen reader successfully narrates all chart titles and data
 - Data freshness indicator shows <6 hours staleness

> **Investigation Required**
> When applying this rule:
> 1. **Profile data BEFORE analysis** - Check row counts, distributions, data types
> 2. **Verify model registry access** - Confirm ML registry connection and permissions
> 3. **Never assume data quality** - Check for NULLs, outliers, data drift
> 4. **Check query cost** - Review Query Profile before productionizing
> 5. **Test visualizations** - Verify accessibility with screen readers and color contrast
>
> **Anti-Pattern:**
> "Training model on data... (without checking data quality first)"
> "Using SELECT *... (without LIMIT or cost analysis)"
>
> **Correct Pattern:**
> "Let me profile your data first."
> [checks row counts, NULLs, distributions, Query Profile]
> "I see 50M rows with 2% NULLs. Using APPROX_COUNT_DISTINCT and sampling..."
 - All metrics have documented definitions
 - Streamlit dashboard loads in <2 seconds

- **Negative Tests:**
 - Query without LIMIT on large table (should timeout or fail cost check)
 - Model training on data with <80% quality score (should raise error)
 - Chart with truncated Y-axis without annotation (should fail ethics review)
 - Visualization using red/green only (should fail colorblind accessibility test)
 - Dashboard without data freshness timestamp (should fail compliance check)
 - Prediction without confidence interval (should fail uncertainty requirement)

## Output Format Examples

```python
# Data Science Analytics Implementation

# 1. DATA INVESTIGATION
schema = session.sql("DESCRIBE TABLE source_table").collect()
row_count = session.sql("SELECT COUNT(*) FROM source_table").collect()[0][0]
sample = session.sql("SELECT * FROM source_table SAMPLE (100 ROWS)").to_pandas()

# 2. DATA QUALITY CHECK
quality_report = run_dmf_checks(table="source_table")
if quality_report['quality_score'] < 0.9:
 raise ValueError(f"Data quality insufficient: {quality_report}")

# 3. OPTIMIZED SQL QUERY
query = """
WITH base_data AS (
 SELECT
 customer_id,
 order_date,
 SUM(order_amount) AS total_amount
 FROM orders
 WHERE order_date >= DATEADD('year', -1, CURRENT_DATE())
 GROUP BY 1, 2
),
aggregated AS (
 SELECT
 customer_id,
 COUNT(*) AS order_count,
 AVG(total_amount) AS avg_order_value
 FROM base_data
 GROUP BY 1
)
SELECT * FROM aggregated;
"""

# 4. PERFORMANCE VALIDATION
df = session.sql(query).to_pandas()
# Check Query Profile: <5s, <$0.10

# 5. VISUALIZATION WITH ACCESSIBILITY
import plotly.graph_objects as go

fig = go.Figure(go.Bar(
 x=df['category'],
 y=df['value'],
 marker=dict(color='#0173B2') # Colorblind-safe
))
fig.update_layout(
 title="Sales by Category (Accessible)",
 xaxis_title="Category",
 yaxis_title="Sales ($)",
 yaxis=dict(range=[0, df['value'].max() * 1.1]) # Zero baseline
)
st.plotly_chart(fig)

# 6. DATA QUALITY INDICATORS
st.caption(f"Data as of: {last_update} | Quality Score: {quality_score:.0%}")
```

## References

### External Documentation
- [Snowflake for Data Science](https://docs.snowflake.com/en/user-guide/data-science) - Data science workflows and best practices in Snowflake
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex) - AI and machine learning capabilities in Snowflake
- [Snowflake ML Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview) - Machine learning development guide
- [Snowflake Model Registry](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview) - Model versioning and management
- [SHAP Documentation](https://shap.readthedocs.io/) - Model explainability and interpretability
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Web accessibility standards
- [Plotly Python Documentation](https://plotly.com/python/) - Interactive visualization library
- [Streamlit Documentation](https://docs.streamlit.io/) - Streamlit app development

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Snowflake SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Snowflake Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Snowflake Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Snowflake Notebooks**: `rules/109-snowflake-notebooks.md`
- **Snowflake Model Registry**: `rules/110-snowflake-model-registry.md`
- **Snowflake Observability**: `rules/111-snowflake-observability-core.md`
- **Snowflake Feature Store**: `rules/113-snowflake-feature-store.md`
- **Snowflake Cortex AISQL**: `rules/114-snowflake-cortex-aisql.md`
- **Snowflake Data Quality**: `rules/124-snowflake-data-quality-core.md`
- **Snowflake Streamlit UI**: `rules/101-snowflake-streamlit-core.md`
- **Python Core**: `rules/200-python-core.md`
- **DateTime Handling**: `rules/251-python-datetime-handling.md`
- **Pandas Best Practices**: `rules/252-pandas-best-practices.md`
- **Data Governance**: `rules/930-data-governance-quality.md`

> ** Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - **Context awareness:** Track token budget; prioritize investigation-first sections
> - **Explicit behavior:** Request "comprehensive analysis with uncertainty quantification" to get full implementation
> - **Parallel tool calls:** Generate SHAP values, confusion matrix, ROC curve simultaneously
> - **State discovery:** Leverage filesystem to check existing model artifacts before regenerating
> - **Investigation-first:** Excel at schema discovery and data profiling - use this capability

## Anti-Patterns: Pandas NULL Handling

**Note:** For comprehensive Pandas performance optimization, vectorization patterns, and anti-patterns, see `252-pandas-best-practices.md`. For datetime handling across Pandas, Python, and visualization libraries, see `251-python-datetime-handling.md`.

**Anti-Pattern 1: Using Python None checks on pandas DataFrames**
```python
# Snowflake query returns NULL for missing duration
df = session.sql("SELECT audio_file, duration_seconds FROM transcriptions").to_pandas()

# WRONG: is not None doesn't detect pandas NaN
duration = df["duration_seconds"].iloc[0]
if duration is not None:
 formatted = f"{duration:.1f}s" # CRASHES if duration is NaN
```

**Problem**: Snowflake NULL becomes pandas NaN, not Python None. The check `is not None` returns True for NaN values, but format strings crash on NaN.

**Correct Pattern:**
```python
import pandas as pd

df = session.sql("SELECT audio_file, duration_seconds FROM transcriptions").to_pandas()

duration = df["duration_seconds"].iloc[0]
if pd.notna(duration): # Correctly identifies NaN
 formatted = f"{duration:.1f}s" # Safe
else:
 formatted = "Unknown"
```

**Benefits**: Prevents "unsupported format string passed to NoneType" errors; works correctly with Snowflake NULL values.

**Anti-Pattern 2: Formatting without NULL validation**
```python
# Direct formatting without checking for NULL/NaN
file_size = df["SIZE"].mean()
st.metric("Avg Size", f"{file_size:.1f} KB") # CRASHES if all NULL
```

**Problem**: If all values are NULL, mean() returns NaN, causing format string error.

**Correct Pattern:**
```python
file_size = df["SIZE"].mean()
if pd.notna(file_size):
 st.metric("Avg Size", f"{file_size:.1f} KB")
else:
 st.metric("Avg Size", "N/A")
```

**Benefits**: Graceful degradation when data is unavailable; no crashes.

### Pandas NULL Checking Functions

**Always use pandas-aware functions for DataFrame values:**

**Recommended Functions:**
- **`pd.notna(x)`** - Check if NOT null/NaN (use before formatting, calculations)
- **`pd.isna(x)`** - Check if null/NaN (use for filtering, validation)
- **`pd.isnull(x)`** - Alias for pd.isna() (same behavior)
- **`df.fillna(value)`** - Replace NaN with value (use for data preparation)
- **`df.dropna()`** - Remove rows with NaN (use for data cleaning)

**Do NOT use these on DataFrame values:**
- `x is None` - Doesn't catch NaN
- `x == None` - Doesn't catch NaN
- `not x` - Treats 0 as falsy

## 1. Model Lifecycle & MLOps

**MANDATORY:**

### Reproducibility Requirements
- **Requirement:** Ensure full reproducibility: pin all dependencies (uv.lock, requirements.txt), log random seeds, use dataset snapshot or hash
- **Requirement:** Use Snowflake Model Registry to store metadata for each version:
 ```python
 from snowflake.ml.registry import Registry

 registry = Registry(session=session)
 model_ref = registry.log_model(
 model=trained_model,
 model_name="customer_churn_predictor",
 version_name="v2_xgboost",
 metrics={"accuracy": 0.89, "f1": 0.85},
 tags={"data_hash": data_hash, "feature_version": "v3"},
 python_version="3.11",
 conda_dependencies=dependencies
 )
 ```

### Baseline & Validation
- **Requirement:** Establish and compare against simple, interpretable baseline (logistic regression, decision tree) before complex models
- **Requirement:** Do not train on unvalidated data; implement data quality gate:
 ```sql
 -- Run DMF checks before model training
 SELECT SYSTEM$GET_DATA_QUALITY_METRICS_LAST_RUN(
 'analytics_db.ml_features.customer_features'
 );
 ```

### Immutability & Monitoring
- **Requirement:** Keep artifacts and runs immutable; never overwrite past runs (use versioning)
- **Always:** Implement model monitoring for drift and performance decay:
 ```python
 # Monitor prediction distribution shift
 from scipy.stats import ks_2samp

 baseline_preds = model.predict(baseline_data)
 current_preds = model.predict(current_data)

 ks_stat, p_value = ks_2samp(baseline_preds, current_preds)
 if p_value < 0.05:
 alert("Model drift detected: prediction distribution shifted")
 ```

### Explainability & Production Readiness
- **Always:** Store explainability artifacts (SHAP summaries, feature importance, counterfactuals) with model:
 ```python
 import shap

 explainer = shap.TreeExplainer(model)
 shap_values = explainer.shap_values(X_test)

 # Store with model
 registry.log_artifact(
 model_name="customer_churn_predictor",
 version_name="v2_xgboost",
 artifact_name="shap_values",
 artifact_data=shap_values
 )
 ```

- **Always:** When notebook yields final model, refactor into production scripts:
 - Extract data pipeline into SQL stored procedures
 - Extract feature engineering into feature store
 - Extract model training into scheduled task
 - Extract predictions into Streamlit app or REST API

## 2. Feature Engineering & Preparation

**MANDATORY:**

### Versioning & Leakage Prevention
- **Requirement:** Make feature definitions reproducible and versioned (use Snowflake Feature Store or versioned views)
- **Requirement:** Avoid target leakage; features must not contain post-outcome information:
 ```sql
 -- BAD: Future information leakage
 SELECT
 customer_id,
 days_since_last_purchase,
 total_purchases_next_30_days -- This is the target!
 FROM customers;

 -- GOOD: Only historical features
 SELECT
 customer_id,
 days_since_last_purchase,
 avg_purchase_amount_last_90_days,
 purchase_frequency_last_year
 FROM customers
 WHERE as_of_date <= training_date;
 ```

### SQL-First Approach
- **Requirement:** Avoid ad-hoc notebook transformations; prefer upstream computation in Snowflake SQL over Python loops:
 ```python
 # BAD: Python loops over millions of rows
 for customer_id in customer_ids:
 features = calculate_features(customer_id) # Slow!

 # GOOD: SQL aggregation
 features_df = session.sql("""
 WITH customer_activity AS (
 SELECT
 customer_id,
 COUNT(*) AS purchase_count,
 AVG(purchase_amount) AS avg_purchase,
 DATEDIFF('day', MAX(purchase_date), CURRENT_DATE()) AS days_since_last
 FROM purchases
 GROUP BY customer_id
 )
 SELECT * FROM customer_activity
 """).to_pandas()
 ```

### Monitoring & Correlation
- **Requirement:** Monitor feature drift and null ratios over time using DMFs
- **Always:** Deduplicate highly correlated features (|correlation| > 0.95) to reduce model instability

## 3. Advanced SQL for Analytics

**MANDATORY:**

### Window Functions & CTEs
- **Always:** Use window functions for intra-partition context (sessionization, ranking) instead of self-joins:
 ```sql
 -- Window function for ranking
 SELECT
 customer_id,
 order_date,
 order_amount,
 ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS recency_rank
 FROM orders
 QUALIFY recency_rank <= 5; -- Top 5 recent orders per customer
 ```

- **Requirement:** In window functions, include deterministic `ORDER BY` to avoid non-deterministic results
- **Requirement:** Avoid deeply nested subqueries; segment logic with CTEs for readability and optimization

### Performance at Scale
- **Consider:** For large datasets, use approximate functions when exactness not required:
 ```sql
 -- For 100M+ rows, approximate functions save compute
 SELECT
 region,
 APPROX_COUNT_DISTINCT(customer_id) AS unique_customers, -- Much faster
 APPROX_PERCENTILE(order_amount, 0.5) AS median_order,
 APPROX_TOP_K(product_id, 10) AS top_products
 FROM orders
 GROUP BY region;
 ```

- **Always:** Use SAMPLE for exploratory data analysis to reduce costs:
 ```sql
 -- EDA on 1% sample
 SELECT * FROM large_table SAMPLE (1);

 -- Fixed row count
 SELECT * FROM large_table SAMPLE (10000 ROWS);
 ```

### Cortex AI Integration
- **Always:** For SQL ML tasks, reference Snowflake Cortex AI-SQL documentation: https://docs.snowflake.com/user-guide/snowflake-cortex/aisql
 ```sql
 -- Sentiment analysis at scale
 SELECT
 review_id,
 SNOWFLAKE.CORTEX.SENTIMENT(review_text) AS sentiment_score,
 SNOWFLAKE.CORTEX.CLASSIFY_TEXT(review_text, ['positive', 'negative', 'neutral']) AS sentiment_class
 FROM product_reviews;
 ```

## 4. Specialized Data & Time Series

**MANDATORY:**

### Time Series Best Practices
- **Requirement:** Keep time series data in consistent timezone (UTC); convert to local time only for presentation
- **Always:** Use proper time series aggregation with explicit intervals:
 ```sql
 SELECT
 DATE_TRUNC('hour', event_timestamp) AS hour,
 COUNT(*) AS event_count,
 AVG(metric_value) AS avg_metric
 FROM events
 WHERE event_timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())
 GROUP BY 1
 ORDER BY 1;
 ```

### Geospatial Analysis
- **Requirement:** Use Snowflake's native geospatial types and functions:
 ```sql
 -- Distance calculation
 SELECT
 store_id,
 customer_id,
 ST_DISTANCE(store_location, customer_location) AS distance_meters
 FROM stores
 CROSS JOIN customers
 WHERE ST_DWITHIN(store_location, customer_location, 5000); -- Within 5km
 ```

### Vector Similarity Search
- **Always:** For vector similarity search, use vector store and document model version/dimensions:
 ```sql
 -- Create vector column
 ALTER TABLE products ADD COLUMN embedding VECTOR(FLOAT, 768);

 -- Similarity search
 SELECT
 product_id,
 product_name,
 VECTOR_COSINE_SIMILARITY(embedding, :query_embedding) AS similarity
 FROM products
 ORDER BY similarity DESC
 LIMIT 10;
 ```

- **Always:** Reference official Snowflake documentation:
 - **SQL Reference**: https://docs.snowflake.com/en/sql-reference
 - **Geospatial Functions**: https://docs.snowflake.com/en/sql-reference/functions/geospatial-spatial-functions
 - **Vector Functions**: https://docs.snowflake.com/en/sql-reference/functions/vector-functions
 - **Snowflake Machine Learning**: https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview

## 5. ML/AI Insight Presentation & Visualization

**MANDATORY:**

### Model Performance Visualization

**Confusion Matrix:**
```python
import streamlit as st
import plotly.figure_factory as ff
from sklearn.metrics import confusion_matrix, classification_report

# Always include precision, recall, F1
cm = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)

fig = ff.create_annotated_heatmap(
 z=cm,
 x=['Predicted Negative', 'Predicted Positive'],
 y=['Actual Negative', 'Actual Positive'],
 colorscale='Blues'
)
fig.update_layout(title=f"Confusion Matrix | Accuracy: {report['accuracy']:.2%}")
st.plotly_chart(fig)

# Show detailed metrics
st.metric("Precision", f"{report['1']['precision']:.2%}")
st.metric("Recall", f"{report['1']['recall']:.2%}")
st.metric("F1 Score", f"{report['1']['f1-score']:.2%}")
```

**ROC/PR Curves:**
```python
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import plotly.graph_objects as go

# ROC Curve with AUC and optimal threshold
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

# Find optimal threshold (Youden's J statistic)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

fig = go.Figure()
fig.add_trace(go.Scatter(x=fpr, y=tpr, name=f'ROC (AUC={roc_auc:.3f})'))
fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random', line=dict(dash='dash')))
fig.add_annotation(x=fpr[optimal_idx], y=tpr[optimal_idx],
 text=f'Optimal Threshold: {optimal_threshold:.3f}')
st.plotly_chart(fig)
```

**Learning Curves:**
```python
# Show train vs validation to detect overfitting
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
 estimator, X, y, cv=5, n_jobs=-1,
 train_sizes=np.linspace(0.1, 1.0, 10)
)

fig = go.Figure()
fig.add_trace(go.Scatter(x=train_sizes, y=train_scores.mean(axis=1), name='Training Score'))
fig.add_trace(go.Scatter(x=train_sizes, y=val_scores.mean(axis=1), name='Validation Score'))
fig.update_layout(
 title='Learning Curves - Check for Overfitting',
 xaxis_title='Training Set Size',
 yaxis_title='Score'
)
# Annotate if overfitting detected
if train_scores[-1].mean() - val_scores[-1].mean() > 0.1:
 fig.add_annotation(text='Overfitting Detected', x=train_sizes[-1], y=train_scores[-1].mean())
st.plotly_chart(fig)
```

### Explainability Patterns

**Feature Importance (Horizontal Bar Chart):**
```python
# Sorted descending for easy interpretation
feature_importance = pd.DataFrame({
 'feature': feature_names,
 'importance': model.feature_importances_
}).sort_values('importance', ascending=True) # Ascending for horizontal bars

fig = go.Figure(go.Bar(
 x=feature_importance['importance'],
 y=feature_importance['feature'],
 orientation='h'
))
fig.update_layout(
 title='Feature Importance - Top Drivers',
 xaxis_title='Importance Score',
 height=max(400, len(feature_importance) * 20) # Dynamic height
)
st.plotly_chart(fig)
```

**SHAP Values (Waterfall for Individual Predictions):**
```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# Waterfall for single prediction
st.subheader("Why This Prediction?")
st.pyplot(shap.plots.waterfall(shap_values[0], show=False))

# Beeswarm for population
st.subheader("Feature Impact Across All Predictions")
st.pyplot(shap.plots.beeswarm(shap_values, show=False))
```

**Partial Dependence Plots:**
```python
from sklearn.inspection import PartialDependenceDisplay

# Show feature interactions
features = ['age', 'income', ('age', 'income')] # Include 2D interaction
fig, ax = plt.subplots(figsize=(12, 4))
PartialDependenceDisplay.from_estimator(model, X_train, features, ax=ax)
st.pyplot(fig)
```

**Counterfactual Explanations:**
```python
# "If X changed to Y, prediction would be Z"
st.subheader("What-If Analysis")
col1, col2 = st.columns(2)
with col1:
 st.metric("Current Prediction", "High Risk (85%)")
 st.write("Current Values:")
 st.write(f"- Days Since Last Purchase: 45")
 st.write(f"- Purchase Frequency: 2.3/month")

with col2:
 st.metric("Alternative Scenario", "Low Risk (25%)", delta="-60%", delta_color="inverse")
 st.write("If Changed To:")
 st.write(f"- Days Since Last Purchase: 10 (-35 days)")
 st.write(f"- Purchase Frequency: 4.5/month (+2.2)")
```

### Uncertainty Communication

**MANDATORY:**

**Show Prediction Intervals, Not Just Point Estimates:**
```python
# For regression models, show confidence intervals
from sklearn.ensemble import GradientBoostingRegressor

# Train with quantile loss for prediction intervals
lower_model = GradientBoostingRegressor(loss='quantile', alpha=0.05)
upper_model = GradientBoostingRegressor(loss='quantile', alpha=0.95)
point_model = GradientBoostingRegressor()

lower_model.fit(X_train, y_train)
upper_model.fit(X_train, y_train)
point_model.fit(X_train, y_train)

# Visualize with uncertainty bands
fig = go.Figure()
fig.add_trace(go.Scatter(
 x=X_test_dates,
 y=point_model.predict(X_test),
 name='Prediction',
 line=dict(color='blue')
))
fig.add_trace(go.Scatter(
 x=X_test_dates,
 y=upper_model.predict(X_test),
 fill=None,
 mode='lines',
 line=dict(color='rgba(0,0,255,0.3)', dash='dash'),
 name='95% Upper Bound'
))
fig.add_trace(go.Scatter(
 x=X_test_dates,
 y=lower_model.predict(X_test),
 fill='tonexty',
 mode='lines',
 line=dict(color='rgba(0,0,255,0.3)', dash='dash'),
 name='95% Lower Bound'
))
st.plotly_chart(fig)
```

**Model Confidence Indicators:**
```python
# Show when model is uncertain
confidence = model.predict_proba(X_test).max(axis=1)

high_confidence = (confidence > 0.8).sum()
low_confidence = (confidence < 0.6).sum()

col1, col2, col3 = st.columns(3)
col1.metric("High Confidence", f"{high_confidence} predictions",
 delta=f"{high_confidence/len(X_test):.0%}")
col2.metric("Medium Confidence", f"{len(X_test)-high_confidence-low_confidence}")
col3.metric("Low Confidence ", f"{low_confidence}",
 delta=f"{low_confidence/len(X_test):.0%}", delta_color="inverse")

# Flag low confidence predictions for review
st.warning(f"{low_confidence} predictions have <60% confidence. Manual review recommended.")
```

## 6. Performance Optimization for Large Datasets

**MANDATORY:**

### SQL-First Aggregation
```python
# BAD: Fetching 10M rows then filtering in Pandas (slow, expensive)
df = session.sql("SELECT * FROM sales_fact").to_pandas() # Pulls all data!
filtered = df[df['region'] == user_selection]

# GOOD: Filter in SQL, fetch only needed data
query = f"""
 SELECT
 order_date,
 product_category,
 SUM(sales_amount) AS total_sales,
 APPROX_COUNT_DISTINCT(customer_id) AS unique_customers
 FROM sales_fact
 WHERE region = '{user_selection}'
 AND order_date >= DATEADD('year', -1, CURRENT_DATE())
 GROUP BY 1, 2
 LIMIT 10000
"""
df = session.sql(query).to_pandas()
```

### Sampling Strategies
```sql
-- For EDA and visualization development, sample first
SELECT * FROM large_table SAMPLE (1000 ROWS); -- Fixed sample size

-- For model training, stratified sampling
SELECT *
FROM customers SAMPLE (10) SEED (42) -- 10% reproducible sample
WHERE status = 'active';
```

### Incremental Loading with Streams
```sql
-- Use Snowflake Streams for dashboard data refresh
CREATE OR REPLACE STREAM dashboard_changes ON TABLE sales_fact;

-- Refresh dashboard data incrementally
MERGE INTO dashboard_aggregates t
USING (
 SELECT
 order_date,
 region,
 SUM(sales_amount) AS total_sales
 FROM dashboard_changes
 GROUP BY 1, 2
) s
ON t.order_date = s.order_date AND t.region = s.region
WHEN MATCHED THEN UPDATE SET t.total_sales = t.total_sales + s.total_sales
WHEN NOT MATCHED THEN INSERT VALUES (s.order_date, s.region, s.total_sales);
```

### Result Caching in Streamlit
```python
import streamlit as st

# Cache data for 1 hour to reduce warehouse usage
@st.cache_data(ttl=3600)
def load_dashboard_data(region: str, start_date: str):
 return session.sql(f"""
 SELECT * FROM dashboard_aggregates
 WHERE region = '{region}'
 AND order_date >= '{start_date}'
 """).to_pandas()

# Cache ML model (remains in memory across sessions)
@st.cache_resource
def load_model():
 from snowflake.ml.registry import Registry
 registry = Registry(session=session)
 return registry.get_model("churn_predictor").default.run
```

### Query Timeout Handling
```python
# Set timeout for long-running queries
session.sql("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300").collect()

# Handle timeouts gracefully
try:
 result = session.sql(complex_query).to_pandas()
except Exception as e:
 if "timeout" in str(e).lower():
 st.error("Query timed out. Try reducing date range or adding filters.")
 st.info(" Tip: Use SAMPLE or pre-aggregated tables for faster results.")
 else:
 raise
```

## 7. Ethical Visualization & Accessibility

**FORBIDDEN:**

### Forbidden Manipulations
- **Never truncate Y-axis without clear visual indicators** (break lines, annotations stating "axis starts at X")
- **Never use 3D pie charts** (distorts slice proportions)
- **Never omit zero baseline for bar/column charts** showing magnitude comparisons
- **Never use inconsistent time intervals** on time series charts
- **Never cherry-pick date ranges** to show desired trends without disclosure
- **Never use dual Y-axes with different scales** unless clearly marked and justified

**MANDATORY:**

### Required Disclosures
```python
# Data freshness timestamp on every dashboard
st.caption(f"Data as of: {last_refresh_time} | Refreshed: {time_since_refresh} ago")

# Sample size and confidence intervals
st.info(f"Based on {len(df):,} records | Confidence: 95% ±{margin_of_error:.1%}")

# Exclusions or filters applied
if filters_applied:
 st.warning(f"Filters active: {', '.join(filters_applied)}")

# Data quality warnings
if data_quality_score < 0.9:
 st.error(f"Data quality: {data_quality_score:.0%} | {issues_found} issues detected")
```

### WCAG 2.1 AA Compliance

**Color Contrast Requirements:**
- **Text:** 4.5:1 contrast ratio minimum
- **UI Components:** 3:1 contrast ratio minimum
- **Test tool:** https://webaim.org/resources/contrastchecker/

**Colorblind-Safe Palettes:**
```python
# Use colorblind-safe palettes
COLORBLIND_SAFE = [
 '#0173B2', # Blue
 '#DE8F05', # Orange
 '#029E73', # Green
 '#CC78BC', # Purple
 '#CA9161', # Brown
 '#ECE133', # Yellow
]

# AVOID red/green only distinction
# Use red/green + icons + pattern fills
fig.add_trace(go.Bar(
 x=categories,
 y=positive_values,
 name='Profit ▲',
 marker=dict(color='green', pattern_shape="/")
))
fig.add_trace(go.Bar(
 x=categories,
 y=negative_values,
 name='Loss ▼',
 marker=dict(color='red', pattern_shape="\\")
))
```

**Screen Reader Support:**
```python
# Add alt text for charts
fig.update_layout(
 title="Monthly Sales Trend",
 title_text="Line chart showing monthly sales from Jan to Dec 2024. Sales increased from $1M to $3M.",
 xaxis_title="Month",
 yaxis_title="Sales ($M)"
)

# Provide data table alternative
with st.expander("View Data Table (Screen Reader Accessible)"):
 st.dataframe(df)
```

**Keyboard Navigation:**
- Ensure all interactive elements (filters, buttons) are keyboard accessible
- Test with Tab, Enter, Space, Arrow keys
- Provide visible focus indicators

## 8. Data Quality & Metric Documentation

**MANDATORY:**

### Data Quality Indicators
```python
# Freshness indicator
hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
freshness_status = "🟢 Fresh" if hours_since_update < 6 else "🟡 Stale" if hours_since_update < 24 else " Outdated"

col1, col2, col3 = st.columns(3)
col1.metric("Data Freshness", f"{hours_since_update:.1f}h ago", delta=freshness_status)
col2.metric("Completeness", f"{completeness_pct:.0%}", delta=f"{missing_count:,} nulls", delta_color="inverse")
col3.metric("Quality Score", quality_grade, delta=f"Passed {checks_passed}/{total_checks} checks")

# Detailed quality issues
if quality_issues:
 with st.expander("Data Quality Issues"):
 for issue in quality_issues:
 st.warning(f"- {issue['column']}: {issue['description']}")
```

### Metric Definition Catalog
```python
# Document metrics in code and UI
METRIC_DEFINITIONS = {
 "MRR": {
 "name": "Monthly Recurring Revenue",
 "definition": "Sum of active subscription values at month end",
 "calculation": "SUM(subscription_amount) WHERE status = 'active'",
 "owner": "Finance Team",
 "update_frequency": "Daily at 00:00 UTC",
 "data_quality_checks": ["No negative values", "Month-over-month change < 50%"]
 }
}

# Show in UI
with st.expander("ℹ️ Metric Definition"):
 metric = METRIC_DEFINITIONS["MRR"]
 st.write(f"**{metric['name']}**")
 st.write(f"*Definition:* {metric['definition']}")
 st.code(metric['calculation'], language='sql')
 st.caption(f"Owner: {metric['owner']} | Updated: {metric['update_frequency']}")
```
