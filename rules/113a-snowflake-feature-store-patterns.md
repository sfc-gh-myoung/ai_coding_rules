# Snowflake Feature Store: Anti-Patterns and Common Mistakes

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:feature-store-patterns
**Keywords:** feature store anti-patterns, data leakage, point-in-time correctness, feature versioning mistakes, non-deterministic features, feature view costs, feature store governance
**TokenBudget:** ~2300
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 113-snowflake-feature-store.md

## Scope

**What This Rule Covers:**
Anti-patterns and common mistakes when implementing Snowflake Feature Store, including data leakage from improper joins, feature versioning errors, non-deterministic transformations, unmonitored refresh costs, and governance gaps.

**When to Load This Rule:**
- Reviewing or auditing Feature Store implementations
- Debugging feature-related model performance issues
- Investigating data leakage or train/serve skew
- Optimizing feature view refresh costs

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **113-snowflake-feature-store.md** - Feature Store core patterns

### External Documentation

- [Snowflake Feature Store](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview) - Official Feature Store documentation

## Contract

### Inputs and Prerequisites

- Feature Store configured (see 113-snowflake-feature-store.md)
- Existing feature views and entity definitions
- Understanding of ML training/inference pipelines

### Mandatory

- Use ASOF JOIN for point-in-time correctness in training datasets
- Version all feature views with semantic versioning
- Use only deterministic functions in feature transformations
- Monitor feature view refresh costs

### Forbidden

- Regular JOINs for training data that require temporal correctness
- Overwriting feature view versions without incrementing
- Non-deterministic functions (CURRENT_TIMESTAMP, RANDOM) in feature definitions
- Unmonitored aggressive refresh schedules

### Execution Steps

1. Review existing feature views for anti-pattern violations
2. Fix data leakage issues with ASOF JOIN
3. Implement proper versioning strategy
4. Replace non-deterministic transformations
5. Set up cost monitoring for feature view refreshes

### Output Format

- Corrected feature view definitions
- Cost monitoring queries
- Versioning strategy documentation

### Validation

- ASOF JOINs produce point-in-time correct datasets
- Feature views use semantic versioning
- All transformations are deterministic
- Refresh costs are monitored and within budget

### Design Principles

- Point-in-time correctness prevents data leakage
- Versioning enables reproducibility and rollback
- Deterministic transformations ensure training/inference consistency
- Cost monitoring prevents runaway refresh expenses

### Post-Execution Checklist

- [ ] All training datasets use ASOF JOIN
- [ ] Feature views versioned with semantic versioning
- [ ] Non-deterministic functions removed from features
- [ ] Refresh cost monitoring configured
- [ ] Governance metadata applied to all feature views

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Using ASOF JOIN for Point-in-Time Correctness**
```python
# Bad: Regular JOIN causes data leakage
training_data = entities_df.join(
    features_df,
    on='customer_id',
    how='left'
)
# Uses latest feature values, not values at prediction time!
# Leaks future information into training data!
```
**Problem:** Data leakage; inflated model performance; production model fails

**Correct Pattern:**
```python
# Good: ASOF JOIN for point-in-time correctness
from snowflake.ml.feature_store import FeatureStore

fs = FeatureStore(session, database='FEATURE_STORE_DB', schema='CUSTOMER_FEATURES')

training_data = fs.generate_training_set(
    spine_df=entities_df,  # Has customer_id and prediction_timestamp
    features=[
        'customer_features@v1',
        'transaction_features@v2'
    ],
    spine_timestamp_col='prediction_timestamp',  # Point-in-time!
    exclude_columns=['internal_id']
)

# ASOF JOIN ensures features use only data available before prediction_timestamp
# No data leakage, realistic training data
```
**Benefits:** No data leakage; realistic model performance; production accuracy matches training

**Anti-Pattern 2: Not Versioning Feature Views**
```python
# Bad: Overwrite feature view without versioning
@fv(name='customer_features', version='v1')
def customer_features(df):
    return df.select('customer_id', 'age', 'income')

# Later: Change feature logic but keep same name/version
@fv(name='customer_features', version='v1')  # Same name!
def customer_features(df):
    return df.select('customer_id', 'age_bucket', 'income_log')  # Different features!

# Models trained on old features break, can't reproduce results!
```
**Problem:** Can't reproduce models; training/inference mismatch; broken lineage

**Correct Pattern:**
```python
# Good: Semantic versioning for feature views
from snowflake.ml.feature_store import FeatureStore, FeatureView

fs = FeatureStore(session, database='FEATURE_STORE_DB', schema='CUSTOMER_FEATURES')

# Version 1.0: Initial features
@fv(name='customer_features', version='1.0')
def customer_features_v1(df):
    return df.select(
        col('customer_id'),
        col('age'),
        col('income')
    )

# Version 2.0: Breaking change - different feature engineering
@fv(name='customer_features', version='2.0')  # New version!
def customer_features_v2(df):
    return df.select(
        col('customer_id'),
        when(col('age') < 30, 'young')
         .when(col('age') < 50, 'middle')
         .otherwise('senior').alias('age_bucket'),
        log(col('income') + 1).alias('income_log')
    )

# Models reference specific versions
model_v1 = train_model(features='customer_features@1.0')
model_v2 = train_model(features='customer_features@2.0')

# Can reproduce, rollback, and maintain multiple versions
```
**Benefits:** Reproducible models; clear lineage; rollback capability

**Anti-Pattern 3: Using Non-Deterministic Functions in Feature Engineering**
```python
# Bad: Non-deterministic transformations
@fv(name='transaction_features', version='v1')
def transaction_features(df):
    return df.select(
        col('transaction_id'),
        col('amount'),
        CURRENT_TIMESTAMP().alias('feature_created_at'),  # Changes every run!
        uniform(0, 1, random()).alias('random_feature')   # Different every time!
    )

# Training and inference produce different feature values!
```
**Problem:** Training/inference mismatch; non-reproducible; model instability

**Correct Pattern:**
```python
# Good: Deterministic transformations only
@fv(name='transaction_features', version='v1')
def transaction_features(df):
    return df.select(
        col('transaction_id'),
        col('amount'),
        col('transaction_timestamp'),  # Use existing timestamp column
        (col('amount') * 0.1).alias('amount_scaled'),  # Deterministic math
        when(col('amount') > 1000, 1).otherwise(0).alias('high_value_flag')  # Deterministic logic
    )

# If you need current time context, use spine timestamp
@fv(name='time_aware_features', version='v1')
def time_aware_features(df):
    # df already has event_timestamp from source
    return df.select(
        col('customer_id'),
        col('event_timestamp'),
        datediff('day', col('last_purchase_date'), col('event_timestamp')).alias('days_since_last_purchase')
        # Deterministic: same inputs always produce same outputs
    )
```
**Benefits:** Reproducible features; training/inference consistency; reliable predictions

**Anti-Pattern 4: Not Monitoring Feature View Refresh Costs**
```python
# Bad: Set aggressive refresh schedule without monitoring
CREATE DYNAMIC TABLE customer_features_view
TARGET_LAG = '1 MINUTE'  -- Refreshes constantly!
WAREHOUSE = LARGE_WH     -- Expensive warehouse!
AS
SELECT
  customer_id,
  -- Complex aggregations over millions of rows
  COUNT(*) OVER (PARTITION BY customer_id ORDER BY timestamp ROWS BETWEEN 1000 PRECEDING AND CURRENT ROW) as rolling_count
FROM raw_events;

-- Bills hundreds of dollars per day, features rarely used!
```
**Problem:** Runaway costs; unnecessary refreshes; wasted credits; budget overruns

**Correct Pattern:**
```python
# Good: Monitor costs and optimize refresh schedule

# Step 1: Start with conservative refresh schedule
CREATE DYNAMIC TABLE customer_features_view
TARGET_LAG = '1 HOUR'    -- Less frequent initially
WAREHOUSE = SMALL_WH     -- Start small
AS
SELECT
  customer_id,
  COUNT(*) as purchase_count,
  SUM(amount) as total_spend
FROM transactions
GROUP BY customer_id;

# Step 2: Monitor refresh costs
SELECT
  table_name,
  refresh_action,
  completion_time,
  credits_used,
  rows_inserted,
  rows_updated
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY
WHERE table_name = 'CUSTOMER_FEATURES_VIEW'
  AND start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

# Step 3: Calculate cost per refresh
SELECT
  AVG(credits_used) as avg_credits_per_refresh,
  SUM(credits_used) as total_credits_weekly,
  COUNT(*) as refresh_count
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY
WHERE table_name = 'CUSTOMER_FEATURES_VIEW'
  AND start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP());

# Step 4: Optimize based on actual usage
-- If features rarely change, increase TARGET_LAG to reduce costs
ALTER DYNAMIC TABLE customer_features_view
SET TARGET_LAG = '4 HOURS';  -- Reduce refresh frequency

-- If costs still high, use smaller warehouse
ALTER DYNAMIC TABLE customer_features_view
SET WAREHOUSE = XSMALL_WH;

# Step 5: Set up cost alerts
CREATE OR REPLACE TASK monitor_feature_costs
WAREHOUSE = MONITORING_WH
SCHEDULE = '1 DAY'
AS
INSERT INTO feature_cost_alerts
SELECT
  table_name,
  SUM(credits_used) as daily_credits,
  CURRENT_DATE() as alert_date
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY
WHERE start_time >= DATEADD('day', -1, CURRENT_TIMESTAMP())
GROUP BY table_name
HAVING SUM(credits_used) > 10;  -- Alert if >10 credits/day
```
**Benefits:** Cost visibility; optimized refreshes; budget control; proactive alerts
