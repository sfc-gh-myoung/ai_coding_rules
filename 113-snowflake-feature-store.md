**Description:** Comprehensive best practices for Snowflake Feature Store, covering feature engineering, entity modeling, feature views, and ML pipeline integration.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Feature store, feature engineering, feature views, entity modeling, ML pipeline, ML features
**Version:** 1.1
**LastUpdated:** 2025-10-13

**TokenBudget:** ~1100
**ContextTier:** Medium

# Snowflake Feature Store Best Practices

## Purpose
Establish comprehensive best practices for using Snowflake Feature Store to create, maintain, and serve ML features, ensuring consistency, reusability, and production-ready feature pipelines that integrate seamlessly with Snowflake ML workflows.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Feature Store (Enterprise Edition), feature engineering, entity modeling, feature views, ML dataset creation, and Model Registry integration

## Contract
- **Inputs/Prereqs:** Snowflake Enterprise Edition; snowflake-ml-python >= 1.5.0; ACCOUNTADMIN or role with CREATE SCHEMA privileges; raw data tables/views; feature engineering requirements; entity definitions
- **Allowed Tools:** Feature Store Python API; SQL feature transformations; Dynamic Tables for managed views; ASOF JOIN for point-in-time correctness; Snowflake Model Registry
- **Forbidden Tools:** Ad-hoc feature calculations in notebooks; duplicated feature logic across projects; unversioned feature transformations; feature stores without access control
- **Required Steps:**
  1. Create or connect to feature store (schema)
  2. Define entities with appropriate tags
  3. Create feature views (Snowflake-managed or external)
  4. Generate training datasets with point-in-time correctness
  5. Integrate with Model Registry for lineage tracking
  6. Implement access control and governance
- **Output Format:** Feature Store schema with organized feature views; Python/SQL feature transformations; training datasets ready for ML workflows
- **Validation Steps:** Verify feature view refresh schedules; test point-in-time joins; validate entity tagging; confirm Model Registry integration; check access controls

## Key Principles
- Feature Store is a schema; feature views are dynamic tables/views; entities are tags
- Centralize feature logic for reuse; avoid duplicating transformations across projects
- Use Snowflake-managed feature views for automatic incremental refresh
- Leverage ASOF JOIN for point-in-time correct training datasets
- Integrate with Model Registry for end-to-end ML lineage and governance
- Apply role-based access control at feature view and entity levels

## 1. Feature Store Setup and Organization

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

## 2. Entity Modeling and Tagging

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

## 3. Feature Views - Snowflake-Managed

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
- **Consider:** Balance freshness requirements vs. compute costs

```python
# Common refresh patterns
refresh_freq="1 hour"    # Real-time features (streaming, high-velocity)
refresh_freq="1 day"     # Daily batch features (most common)
refresh_freq="1 week"    # Static/slow-changing features
```

## 4. Feature Views - External (User-Managed)

### External Feature Views with dbt
- **Rule:** Use external feature views when features are managed by tools like dbt
- **Always:** Register external views to make them discoverable in Feature Store
- **Requirement:** Ensure external pipeline maintains feature freshness

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

## 5. Dataset Generation and Point-in-Time Correctness

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
```
Without ASOF JOIN (data leakage):
  2024-03-01 prediction uses features calculated on 2024-03-31 ❌

With ASOF JOIN (point-in-time correct):
  2024-03-01 prediction uses features calculated on 2024-03-01 ✅
```

## 6. Feature Engineering Patterns

### Aggregation Features
- **Rule:** Use time-window aggregations (7d, 30d, 90d) for behavioral features
- **Always:** Include multiple aggregation functions (COUNT, SUM, AVG, MAX, MIN, STDDEV)
- **Consider:** Create features at multiple time windows for model to learn temporal patterns

```sql
-- Multi-window aggregation pattern
SELECT
    customer_id,
    -- 7-day window
    COUNT(DISTINCT order_id) AS orders_7d,
    SUM(order_amount) AS spend_7d,
    -- 30-day window
    COUNT(DISTINCT order_id) AS orders_30d,
    SUM(order_amount) AS spend_30d,
    -- Ratios (velocity indicators)
    orders_7d / NULLIF(orders_30d, 0) AS order_velocity_ratio
FROM ORDERS
WHERE order_date >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY customer_id
```

### Time-Based Features
- **Rule:** Extract temporal components for cyclical patterns (day_of_week, hour, month)
- **Always:** Use `DATEDIFF` for recency features (days_since_last_purchase)
- **Consider:** Create lag features for time-series forecasting

### Derived and Ratio Features
- **Rule:** Create ratios and derived metrics to capture relationships
- **Always:** Use `NULLIF` to prevent division by zero errors
- **Consider:** Normalize features within feature view for model stability

## 7. Feature Versioning and Lineage

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

## 8. Access Control and Governance

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

## 9. Performance and Cost Optimization

### Feature View Performance
- **Rule:** Use clustering keys on high-cardinality join keys in feature views
- **Always:** Monitor Dynamic Table refresh costs and optimize refresh frequency
- **Consider:** Use materialized views for expensive aggregations queried frequently

### Dataset Generation Optimization
- **Rule:** Filter spine DataFrame to relevant time ranges before joining features
- **Always:** Use appropriate warehouse size based on dataset size and join complexity
- **Consider:** Batch dataset generation for large training sets; use Snowflake ML Jobs for heavy workloads

### Cost Monitoring
```sql
-- Monitor feature view refresh costs
SELECT 
    table_name,
    refresh_action,
    refresh_trigger,
    completion_time,
    credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY
WHERE table_schema = 'CUSTOMER_FEATURE_STORE'
  AND start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY credits_used DESC;
```

## 10. Integration with Model Registry

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
registry = Registry(session=session)
model_ref = registry.log_model(
    model,
    model_name="CHURN_PREDICTOR",
    version_name="v1.0",
    comment=f"Trained on {training_data.name} (Feature Store lineage tracked)"
)
```

## 11. Common Feature Patterns

### Recency Features
```sql
-- Days since last event
DATEDIFF('day', MAX(event_timestamp), CURRENT_DATE()) AS days_since_last_event
```

### Frequency Features
```sql
-- Count distinct events in time window
COUNT(DISTINCT event_id) AS events_30d
```

### Monetary Features
```sql
-- Spend aggregations with nullif for safety
SUM(amount) AS total_spend_30d,
AVG(amount) AS avg_transaction_value,
SUM(amount) / NULLIF(COUNT(*), 0) AS spend_per_transaction
```

### Velocity and Trend Features
```sql
-- Compare recent vs. historical behavior
orders_7d / NULLIF(orders_30d, 0) AS order_acceleration,
spend_7d - spend_30d AS spend_trend
```

## 12. Best Practices Summary

### Feature View Design
- **Rule:** One feature view per logical feature group (purchase behavior, engagement metrics, demographics)
- **Always:** Include timestamp column for temporal features
- **Rule:** Use consistent feature naming across views (lowercase, underscores)
- **Consider:** Pre-aggregate at feature view level; avoid expensive joins during dataset generation

### Data Quality
- **Requirement:** Handle NULL values explicitly in feature transformations
- **Always:** Use `COALESCE` or `IFNULL` for default values
- **Rule:** Document expected feature distributions and ranges
- **Consider:** Implement data quality checks on feature views

### Reproducibility
- **Requirement:** Version all feature views and datasets
- **Always:** Use deterministic transformations (avoid RANDOM(), CURRENT_TIMESTAMP() without context)
- **Rule:** Document feature engineering decisions and rationale
- **Always:** Test feature generation produces consistent results across runs

## Quick Compliance Checklist
- [ ] Feature store schema created with proper access control
- [ ] Entities registered with appropriate join keys
- [ ] Feature views use SQL or Python transformations (no ad-hoc calculations)
- [ ] Snowflake-managed feature views have refresh schedules configured
- [ ] Training datasets use ASOF JOIN for point-in-time correctness
- [ ] Feature views versioned with semantic versioning
- [ ] Model Registry integration implemented for lineage tracking
- [ ] Sensitive features have data masking policies applied
- [ ] Feature naming follows consistent convention
- [ ] Refresh costs monitored and optimized
- [ ] Feature definitions documented with business logic and rationale

## Validation
- **Success Checks:** Feature views refresh successfully on schedule; datasets generate with expected schema and row counts; ASOF JOIN preserves temporal correctness; Model Registry shows feature lineage; access controls prevent unauthorized access; features produce consistent values across generations
- **Negative Tests:** Attempt to access features without proper role (should fail); generate dataset without spine timestamp (should warn about data leakage); modify feature view without versioning (should be tracked); use stale features in inference (lineage should detect mismatch)

## Response Template
```python
# Feature Store initialization
from snowflake.ml.feature_store import FeatureStore, FeatureView, Entity

fs = FeatureStore(
    session=session,
    database="ML_DATABASE",
    name="DOMAIN_FEATURE_STORE",
    default_warehouse="FEATURE_WH",
    creation_mode="create_if_not_exists"
)

# Entity registration
entity = fs.register_entity(
    name="ENTITY_NAME",
    join_keys=["entity_id"],
    desc="Entity description"
)

# Managed feature view
@feature_view(
    name="ENTITY_FEATURES_30D",
    entities=[entity],
    refresh_freq="1 day"
)
def entity_features(session):
    return session.sql("""
        SELECT
            entity_id,
            COUNT(*) AS count_30d,
            SUM(value) AS sum_30d
        FROM SOURCE_TABLE
        WHERE timestamp >= DATEADD('day', -30, CURRENT_DATE())
        GROUP BY entity_id
    """)

fv = fs.register_feature_view(feature_view=entity_features, version="1.0")

# Generate training dataset
training_data = fs.generate_dataset(
    spine_df=spine_df,
    features=[fv],
    spine_timestamp_col="observation_date",
    name="training_dataset",
    version="1.0"
)
```

## References

### External Documentation
- [Snowflake Feature Store Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview) - Complete Feature Store documentation and architecture
- [Introduction to Feature Store Quickstart](https://quickstarts.snowflake.com/guide/intro-to-feature-store/index.html) - Hands-on tutorial for entities, feature views, and datasets
- [Feature Store API Reference](https://docs.snowflake.com/en/developer-guide/snowflake-ml/reference/latest/api/feature_store/snowflake.ml.feature_store) - Python API documentation
- [Snowflake ML Python Package](https://docs.snowflake.com/en/developer-guide/snowflake-ml/snowpark-ml) - Installation and setup guide
- [Dynamic Tables](https://docs.snowflake.com/en/user-guide/dynamic-tables-about) - Backend implementation for managed feature views
- [Feature Store with dbt](https://quickstarts.snowflake.com/guide/getting-started-with-snowflake-feature-store-and-dbt/index.html) - Integration patterns for external feature views

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Model Registry**: `110-snowflake-model-registry.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Data Governance**: `107-snowflake-security-governance.md`
- **Python Core**: `200-python-core.md`

