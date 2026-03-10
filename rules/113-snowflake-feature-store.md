# Snowflake Feature Store Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:feature-store, kw:ml-features
**Keywords:** feature views, entity modeling, ML pipeline, ASOF JOIN, point-in-time correctness, Dynamic Tables, feature versioning, create features, feature catalog, feature pipeline, feature discovery, feature registry, feature lineage
**TokenBudget:** ~4300
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 110-snowflake-model-registry.md
**Companions:** 113a-snowflake-feature-store-patterns.md, 113b-snowflake-feature-store-engineering.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for Snowflake Feature Store: creating, maintaining, and serving ML features with consistency and reusability. Covers feature engineering, entity modeling, feature views (Snowflake-managed and external), point-in-time correctness with ASOF JOIN, ML dataset creation, and Model Registry integration for production-ready pipelines.

**When to Load This Rule:**
- Implementing Snowflake Feature Store for ML projects
- Creating feature views and entity definitions
- Generating training datasets with point-in-time correctness
- Integrating features with Model Registry
- Setting up feature governance and access control

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **110-snowflake-model-registry.md** - Model Registry integration patterns

**Related:**
- **122-snowflake-dynamic-tables.md** - Dynamic Tables for feature views

### External Documentation

**Feature Store Documentation:**
- [Snowflake Feature Store](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview) - Official Feature Store documentation
- [Feature Store Python API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/latest/api/feature_store) - Python API reference

## Contract

### Inputs and Prerequisites

- Snowflake Enterprise Edition
- snowflake-ml-python >= 1.5.0
- ACCOUNTADMIN or role with CREATE SCHEMA privileges
- Raw data tables/views
- Feature engineering requirements
- Entity definitions

### Mandatory

- Initialize Feature Store with `FeatureStore()` before any feature operations
- Register entities with `register_entity()` before creating feature views
- Use `generate_dataset()` with `spine_timestamp_col` for point-in-time correctness
- Version all feature views when registering with `register_feature_view()`
- Integrate with Model Registry for lineage tracking

### Forbidden

- Ad-hoc feature calculations in notebooks
- Duplicated feature logic across projects
- Unversioned feature transformations
- Feature stores without access control

### Execution Steps

1. Create or connect to feature store (schema)
2. Define entities with appropriate tags
3. Create feature views (Snowflake-managed or external)
4. Generate training datasets with point-in-time correctness
5. Integrate with Model Registry for lineage tracking
6. Implement access control and governance

### Output Format

- Feature Store schema with organized feature views
- Python/SQL feature transformations
- Training datasets ready for ML workflows

### Validation

**Pre-Task-Completion Checks:**
- Feature view refresh schedules configured
- Point-in-time joins tested
- Entity tagging validated
- Model Registry integration confirmed
- Access controls checked

**Success Criteria:**
- Feature views refresh correctly
- ASOF JOINs produce point-in-time correct datasets
- Model Registry shows feature lineage
- Access controls enforce governance

### Design Principles

- Feature Store is a schema; feature views are dynamic tables/views; entities are tags
- Centralize feature logic for reuse; avoid duplicating transformations across projects
- Use Snowflake-managed feature views for automatic incremental refresh
- Leverage ASOF JOIN for point-in-time correct training datasets
- Integrate with Model Registry for end-to-end ML lineage and governance
- Apply role-based access control at feature view and entity levels

### Post-Execution Checklist

- [ ] Feature Store schema created
- [ ] Entities defined with tags
- [ ] Feature views implemented (Snowflake-managed or external)
- [ ] Point-in-time joins configured with ASOF JOIN
- [ ] Training datasets generated and validated
- [ ] Model Registry integration complete
- [ ] Access controls applied
- [ ] Feature versioning tracked

## Anti-Patterns and Common Mistakes

> **See companion rule:** `113a-snowflake-feature-store-patterns.md` for 4 detailed anti-pattern/correct-pattern pairs covering data leakage, versioning, non-deterministic functions, and refresh cost monitoring.

**Key rules:** Always use ASOF JOIN for training data, version all feature views, use only deterministic transformations, and monitor refresh costs.

**Anti-Pattern 1: Generating Training Datasets Without Point-in-Time Correctness**

**Problem:** Developers join features to training labels using a standard JOIN on entity keys without considering temporal alignment. This causes data leakage — the model trains on feature values computed from future data that would not have been available at prediction time. The model appears to perform well in offline evaluation but degrades in production because it no longer has access to "future" features.

**Correct Pattern:** Always use `generate_dataset()` with `spine_timestamp_col` to enable ASOF JOIN. This ensures each training example only sees feature values that existed at the time of the observation.

```python
# Wrong: Standard join causes data leakage — features may include future data
spine_df = session.sql("SELECT customer_id, churned AS label FROM CHURN_LABELS")
features_df = session.table("CUSTOMER_FEATURES")
# Simple join has no temporal awareness — 2024-03-01 label gets 2024-03-31 features
train_df = spine_df.join(features_df, on="customer_id")

# Correct: Use generate_dataset with spine_timestamp_col for ASOF JOIN
spine_df = session.sql("""
    SELECT customer_id, observation_date, churned AS label
    FROM CHURN_LABELS WHERE observation_date >= '2024-01-01'
""")
training_data = fs.generate_dataset(
    spine_df=spine_df,
    features=[customer_purchases_fv, customer_engagement_fv],
    spine_timestamp_col="observation_date",  # Enables ASOF JOIN
    name="churn_training_v1",
    version="1.0"
)
```

**Anti-Pattern 2: Registering Feature Views Without Versioning**

**Problem:** Feature view transformations are updated in place without incrementing the version. When a model is retrained on the updated features, there is no record of which feature definition produced the original training data. Debugging model performance regressions becomes impossible because you cannot reproduce the exact features used in a prior training run.

**Correct Pattern:** Always version feature views when registering and increment the version whenever the transformation logic changes. This enables reproducibility and lineage tracking through the Model Registry.

```python
# Wrong: Overwriting feature view without version tracking
fv = FeatureView(name="CUSTOMER_PURCHASES", entities=[customer_entity],
                 feature_df=session.sql("SELECT customer_id, COUNT(*) AS orders FROM ORDERS GROUP BY 1"))
fs.register_feature_view(feature_view=fv, version="1.0")
# Later, transformation changes but version stays the same — lineage broken
fv_updated = FeatureView(name="CUSTOMER_PURCHASES", entities=[customer_entity],
                         feature_df=session.sql("SELECT customer_id, COUNT(*) AS orders, SUM(amount) AS spend FROM ORDERS GROUP BY 1"))
fs.register_feature_view(feature_view=fv_updated, version="1.0")  # Overwrites!

# Correct: Increment version when transformation changes
fs.register_feature_view(feature_view=fv_updated, version="1.1")  # New version preserves lineage
```

## Feature Store Setup and Organization

### Creating a Feature Store
- **Always:** A feature store is simply a Snowflake schema - create or designate existing schema
- **Rule:** Use descriptive naming convention: `<DOMAIN>_FEATURE_STORE` (e.g., `CUSTOMER_FEATURE_STORE`, `GRID_FEATURE_STORE`)
- **Requirement:** Set up proper access control before adding feature views

```python
from snowflake.ml.feature_store import FeatureStore

# Create or connect to feature store
fs = FeatureStore(
    session=session,
    database="ML_DATABASE",
    name="CUSTOMER_FEATURE_STORE",  # This creates/uses schema CUSTOMER_FEATURE_STORE
    default_warehouse="FEATURE_ENGINEERING_WH",
    creation_mode="create_if_not_exists"
)
```

```sql
-- Alternative: Create schema directly via SQL
CREATE SCHEMA IF NOT EXISTS ML_DATABASE.CUSTOMER_FEATURE_STORE
  COMMENT = 'Feature store for customer analytics and churn prediction models';

-- Set up access control
GRANT USAGE ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE DATA_SCIENTIST;
GRANT CREATE DYNAMIC TABLE ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE ML_ENGINEER;
```

### Feature Store Organization
- **Rule:** Organize feature views by domain and entity (customers, products, transactions)
- **Always:** Use clear naming: `<ENTITY>_<AGGREGATION>_<TIMEFRAME>` (e.g., `customer_purchases_30d`, `product_views_weekly`)
- **Rule:** Document feature definitions, transformations, and business logic in comments

## Entity Modeling and Tagging

### Defining Entities
- **Requirement:** Entities represent the subject matter of features (customers, products, assets, etc.)
- **Always:** Register entities with feature store before creating feature views
- **Rule:** Use singular nouns for entity names (`CUSTOMER`, not `CUSTOMERS`)

```python
# Register entity
customer_entity = fs.register_entity(
    name="CUSTOMER",
    join_keys=["customer_id"],  # Primary key columns
    desc="Customer entity for behavioral and demographic features"
)

# Register multiple entities
product_entity = fs.register_entity(
    name="PRODUCT",
    join_keys=["product_id"],
    desc="Product entity for catalog and performance features"
)
```

**Backend Implementation:**
- Entities are implemented as Snowflake **tags**
- Tags are applied to feature views to associate them with entities
- Multiple feature views can share the same entity

### Join Keys Best Practices
- **Always:** Use stable, immutable identifiers as join keys (customer_id, not email)
- **Rule:** For composite keys, specify all columns in join_keys list
- **Avoid:** Using mutable attributes or timestamps as entity join keys

## Feature Views - Snowflake-Managed

### Creating Managed Feature Views
- **Requirement:** Snowflake-managed feature views use Dynamic Tables for automatic incremental refresh
- **Always:** Specify refresh schedule based on data freshness requirements
- **Rule:** Use SQL or Python transformations; prefer SQL for performance at scale

```python
from snowflake.ml.feature_store import FeatureView

# Create Snowflake-managed feature view with SQL transformation
@feature_view(
    name="CUSTOMER_PURCHASES_30D",
    entities=[customer_entity],
    refresh_freq="1 day",  # Automatic refresh schedule
    desc="30-day customer purchase aggregations"
)
def customer_purchase_features(session):
    return session.sql("""
        SELECT
            customer_id,
            COUNT(DISTINCT order_id) AS orders_30d,
            SUM(order_amount) AS total_spend_30d,
            AVG(order_amount) AS avg_order_value_30d,
            MAX(order_date) AS last_order_date,
            DATEDIFF('day', MAX(order_date), CURRENT_DATE()) AS days_since_last_order
        FROM ORDERS
        WHERE order_date >= DATEADD('day', -30, CURRENT_DATE())
        GROUP BY customer_id
    """)

# Register with feature store
customer_purchases_fv = fs.register_feature_view(
    feature_view=customer_purchase_features,
    version="1.0"
)
```

### Refresh Schedule Best Practices
- **Always:** Align refresh frequency with source data update cadence
- **Rule:** Use incremental refresh for large datasets (default behavior with Dynamic Tables)
- **Rule:** Set target lag to 1 hour for standard features; reduce to 5 minutes only for fraud detection or real-time serving features

```python
# Common refresh patterns
refresh_freq="1 hour"    # Real-time features (streaming, high-velocity)
refresh_freq="1 day"     # Daily batch features (most common)
refresh_freq="1 week"    # Static/slow-changing features
```

## Feature Views - External (User-Managed)

### External Feature Views with dbt
- **Rule:** Use external feature views when features are managed by tools like dbt
- **Always:** Register external views to make them discoverable in Feature Store
- **Requirement:** Ensure external pipeline maintains feature freshness — verify with:
  ```sql
  SELECT MAX(update_ts) FROM ML_DATABASE.DBT_MODELS.CUSTOMER_SEGMENTS;
  -- Alert if MAX(update_ts) < DATEADD('hour', -24, CURRENT_TIMESTAMP())
  ```

```python
# Register existing view/table as external feature view
external_fv = FeatureView(
    name="DBT_CUSTOMER_SEGMENTS",
    entities=[customer_entity],
    feature_df=session.table("ML_DATABASE.DBT_MODELS.CUSTOMER_SEGMENTS"),
    desc="Customer segments from dbt pipeline (externally managed)"
)

fs.register_feature_view(
    feature_view=external_fv,
    version="1.0",
    block=False  # External - don't create managed refresh
)
```

### When to Use External vs. Managed
- **Snowflake-Managed:** New features; standard aggregations; want automatic refresh
- **External:** Existing dbt/Airflow pipelines; complex multi-step transformations; custom orchestration

## Dataset Generation and Point-in-Time Correctness

### Creating Training Datasets
- **Critical:** Use `generate_dataset()` with ASOF JOIN for point-in-time correctness
- **Always:** Specify spine DataFrame with timestamps to avoid data leakage
- **Rule:** Include all relevant feature views; feature store handles joins automatically

```python
# Spine DataFrame - observations with labels and timestamps
spine_df = session.sql("""
    SELECT
        customer_id,
        observation_date,
        churned AS label  -- Target variable
    FROM CUSTOMER_CHURN_LABELS
    WHERE observation_date >= '2024-01-01'
""")

# Generate training dataset with point-in-time correctness
training_data = fs.generate_dataset(
    spine_df=spine_df,
    features=[
        customer_purchases_fv,    # 30-day purchase features
        customer_engagement_fv,   # Engagement metrics
        customer_demographics_fv  # Static demographic features
    ],
    spine_timestamp_col="observation_date",  # Critical for ASOF JOIN
    name="churn_training_v1",
    version="1.0",
    desc="Churn prediction training dataset - Q1 2024"
)

# Access dataset as DataFrame
train_df = training_data.read.to_pandas()
```

### Point-in-Time Correctness
- **Critical:** ASOF JOIN ensures features use only data available at prediction time
- **Always:** Specify `spine_timestamp_col` to enable temporal correctness
- **Rule:** Use same dataset generation process for training and inference to prevent train/serve skew

**Why This Matters:**
```text
Without ASOF JOIN (data leakage):
  2024-03-01 prediction uses features calculated on 2024-03-31

With ASOF JOIN (point-in-time correct):
  2024-03-01 prediction uses features calculated on 2024-03-01
```

## Feature Engineering Patterns

> **See companion rule:** `113b-snowflake-feature-store-engineering.md` for aggregation features, time-based features, derived ratios, and common RFM (Recency, Frequency, Monetary) patterns with SQL templates.

## Feature Versioning and Lineage

### Feature View Versioning
- **Requirement:** Version all feature views for reproducibility
- **Always:** Use semantic versioning (1.0, 1.1, 2.0) when registering
- **Rule:** Increment version when feature definition changes

```python
# Initial registration
fs.register_feature_view(feature_view=customer_fv, version="1.0")

# Updated transformation - increment version
fs.register_feature_view(feature_view=customer_fv_updated, version="1.1")

# Breaking change - increment major version
fs.register_feature_view(feature_view=customer_fv_v2, version="2.0")
```

### ML Lineage Integration
- **Always:** Feature Store automatically tracks lineage with Model Registry
- **Rule:** When training models, retrieve features through Feature Store for lineage capture
- **Requirement:** Document which feature view versions were used for each model version

## Access Control and Governance

### RBAC for Feature Store
- **Requirement:** Implement role-based access control at schema and feature view levels
- **Always:** Grant least-privilege access to feature views
- **Rule:** Separate roles for feature engineering vs. feature consumption

```sql
-- Feature engineering role (create/update features)
CREATE ROLE FEATURE_ENGINEER;
GRANT USAGE ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE FEATURE_ENGINEER;
GRANT CREATE DYNAMIC TABLE ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE FEATURE_ENGINEER;
GRANT CREATE VIEW ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE FEATURE_ENGINEER;

-- Data scientist role (consume features)
CREATE ROLE DATA_SCIENTIST;
GRANT USAGE ON SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE DATA_SCIENTIST;
GRANT SELECT ON ALL DYNAMIC TABLES IN SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE DATA_SCIENTIST;
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE DATA_SCIENTIST;

-- Future grants for new feature views
GRANT SELECT ON FUTURE DYNAMIC TABLES IN SCHEMA ML_DATABASE.CUSTOMER_FEATURE_STORE TO ROLE DATA_SCIENTIST;
```

### Sensitive Data Protection
- **Requirement:** Apply data masking policies to features containing PII
- **Always:** Tag sensitive features with appropriate classification tags
- **Rule:** Use row access policies to restrict feature access by role or context

## Performance and Cost Optimization

### Feature View Performance
- **Rule:** Use clustering keys on high-cardinality join keys in feature views
- **Always:** Monitor Dynamic Table refresh costs and optimize refresh frequency
- **Rule:** Use materialized views for expensive aggregations queried more than 10 times per day

### Dataset Generation Optimization
- **Rule:** Filter spine DataFrame to relevant time ranges before joining features
- **Always:** Use appropriate warehouse size based on dataset size and join complexity:
  - `MEDIUM` for datasets < 10M rows
  - `LARGE` for 10M–100M rows
  - `XLARGE` for > 100M rows
- **Rule:** Batch dataset generation for training sets exceeding 10M rows; use Snowflake ML Jobs for datasets exceeding 100M rows

### Cost Monitoring

See Anti-Pattern 4 (Steps 2-3) for detailed cost monitoring queries using `DYNAMIC_TABLE_REFRESH_HISTORY`. Monitor weekly to track refresh costs per feature view and optimize TARGET_LAG accordingly.

```sql
-- Quick cost check: refresh credits per feature view (last 7 days)
SELECT name, SUM(credits_used) AS total_credits, COUNT(*) AS refresh_count
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  DATE_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
GROUP BY name ORDER BY total_credits DESC;
```

## Integration with Model Registry

### End-to-End ML Pipeline
- **Always:** Use Feature Store datasets in model training for automatic lineage tracking
- **Rule:** Reference feature view versions in model metadata
- **Requirement:** Ensure inference uses same feature generation logic as training

```python
from snowflake.ml.registry import Registry
from snowflake.ml.modeling.xgboost import XGBClassifier

# Generate training dataset
training_data = fs.generate_dataset(
    spine_df=spine_df,
    features=[customer_purchases_fv, customer_engagement_fv],
    name="churn_training_q1_2024",
    version="1.0"
)

# Train model
X = training_data.read.to_pandas().drop(['label'], axis=1)
y = training_data.read.to_pandas()['label']
model = XGBClassifier().fit(X, y)

# Register model with lineage to feature views
# NOTE: options={"enable_monitoring": True} is REQUIRED on Registry if you plan to use MODEL MONITOR
registry = Registry(
    session=session,
    options={"enable_monitoring": True}  # Required for MODEL MONITOR
)
model_ref = registry.log_model(
    model,
    model_name="CHURN_PREDICTOR",
    version_name="v1_0_0",  # Use underscores (periods not valid in SQL identifiers)
    sample_input_data=X.head(5),  # Required for schema inference
    comment=f"Trained on {training_data.name} (Feature Store lineage tracked)"
)
```
