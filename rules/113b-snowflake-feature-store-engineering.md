# Snowflake Feature Store: Feature Engineering Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:feature-engineering
**Keywords:** feature engineering, aggregation features, time-based features, recency features, frequency features, monetary features, velocity features, RFM features, windowed aggregations, derived features
**TokenBudget:** ~2300
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 113-snowflake-feature-store.md

## Scope

**What This Rule Covers:**
Feature engineering patterns for Snowflake Feature Store including aggregation features, time-based features, derived ratios, and common RFM (Recency, Frequency, Monetary) patterns. Provides SQL templates for building reusable feature transformations.

**When to Load This Rule:**
- Building feature transformations for ML models
- Creating aggregation features (time-window, rolling)
- Implementing RFM or behavioral features
- Designing feature views with derived metrics

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
- Raw data tables with event/transaction data
- Entity definitions for feature subjects

### Mandatory

- Use deterministic functions only in feature transformations
- Use NULLIF to prevent division by zero in ratio features
- Include multiple time windows for behavioral features (7d, 30d, 90d)

### Forbidden

- Non-deterministic functions (CURRENT_TIMESTAMP, RANDOM) in feature definitions
- Division without NULLIF protection
- Single time-window features when multiple windows provide signal

### Execution Steps

1. Identify feature subjects (entities) and raw data sources
2. Design aggregation features with appropriate time windows
3. Create time-based and recency features
4. Build derived ratio and velocity features
5. Register as feature views with versioning

### Output Format

- SQL feature transformation queries
- Feature view definitions with refresh schedules

### Validation

- All transformations are deterministic
- Division operations protected with NULLIF
- Time windows aligned with business requirements
- Feature views registered and refreshing correctly

### Design Principles

- Multi-window aggregations capture temporal patterns
- Deterministic transformations ensure reproducibility
- NULLIF prevents division-by-zero errors in ratios
- RFM patterns cover most behavioral feature needs

### Post-Execution Checklist

- [ ] Aggregation features created with multiple time windows
- [ ] Time-based features use deterministic functions
- [ ] Ratio features protected with NULLIF
- [ ] Feature views registered with versioning
- [ ] Refresh schedules configured

## Aggregation Features

- **Rule:** Use time-window aggregations (7d, 30d, 90d) for behavioral features
- **Requirement:** Include multiple aggregation functions (COUNT, SUM, AVG, MAX, MIN, STDDEV)
- **Rule:** Create features at multiple time windows for model to learn temporal patterns

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

## Time-Based Features

- **Rule:** Extract temporal components for cyclical patterns (day_of_week, hour, month)
- **Requirement:** Use `DATEDIFF` for recency features (days_since_last_purchase)
- **Rule:** Use lag features for time-series forecasting scenarios

## Derived and Ratio Features

- **Rule:** Create ratios and derived metrics to capture relationships
- **Requirement:** Use `NULLIF` to prevent division by zero errors
- **Rule:** Normalize features within feature view when model stability requires it

## Common Feature Patterns (RFM)

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

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Non-Deterministic Functions in Feature Definitions**

**Problem:** Developers use `CURRENT_TIMESTAMP()`, `RANDOM()`, or `UUID_STRING()` directly inside feature view transformations. Because feature views are refreshed on a schedule, these functions produce different values on every refresh, making features non-reproducible. A model trained on features computed at time T gets different feature values when the view refreshes at time T+1, causing training-serving skew and making debugging nearly impossible.

**Correct Pattern:** Pass timestamps and random seeds as columns from the source table, not as function calls in the transformation. For recency features, compute `DATEDIFF('day', event_timestamp, refresh_timestamp)` where `refresh_timestamp` is a concrete column value populated at ingestion time, not `CURRENT_DATE()`. This ensures the same input rows always produce the same feature values.

```sql
-- Wrong: Non-deterministic function in feature view — values change on every refresh
SELECT
    customer_id,
    DATEDIFF('day', MAX(order_date), CURRENT_DATE()) AS days_since_last_order,
    UUID_STRING() AS feature_id
FROM ORDERS
GROUP BY customer_id;
-- Result: days_since_last_order changes every day, feature_id changes every refresh

-- Correct: Use a concrete timestamp column for deterministic recency features
SELECT
    customer_id,
    DATEDIFF('day', MAX(order_date), snapshot_date) AS days_since_last_order
FROM ORDERS
-- snapshot_date is a concrete column populated at ingestion, not a function call
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM ORDERS)
GROUP BY customer_id, snapshot_date;
```

**Anti-Pattern 2: Division Without NULLIF Protection in Ratio Features**

**Problem:** Ratio features like `total_spend / order_count` or `clicks / impressions` are computed without guarding against zero denominators. When a customer has zero orders or zero impressions, the query produces a division-by-zero error or returns NULL, which silently propagates through downstream aggregations and model training. Entire batch feature computations can fail because one entity has a zero denominator.

**Correct Pattern:** Always wrap denominators with `NULLIF(denominator, 0)` so division by zero returns NULL instead of erroring. Then handle NULLs explicitly with `COALESCE` if the model requires a default value: `COALESCE(total_spend / NULLIF(order_count, 0), 0) AS avg_order_value`.

```sql
-- Wrong: Division by zero when customer has no orders — query error or silent NULL
SELECT
    customer_id,
    total_spend / order_count AS avg_order_value,
    clicks / impressions AS click_through_rate
FROM CUSTOMER_METRICS;
-- Fails when order_count=0 or impressions=0

-- Correct: NULLIF protection with COALESCE for default values
SELECT
    customer_id,
    COALESCE(total_spend / NULLIF(order_count, 0), 0) AS avg_order_value,
    COALESCE(clicks / NULLIF(impressions, 0), 0) AS click_through_rate
FROM CUSTOMER_METRICS;
```

**Anti-Pattern 3: Using a Single Time Window for Behavioral Features**

**Problem:** A feature like `orders_30d` captures only one time horizon. The model cannot distinguish between a customer who placed 10 orders spread evenly over 30 days versus one who placed all 10 in the last 2 days. Single-window features miss acceleration, deceleration, and recency signals that are critical for churn prediction, fraud detection, and recommendation models.

**Correct Pattern:** Always create features at multiple time windows (e.g., 7d, 30d, 90d) and include ratio features between windows. `orders_7d / NULLIF(orders_30d, 0) AS order_velocity_ratio` captures whether activity is accelerating or decelerating. This gives the model temporal pattern information without requiring complex time-series architectures.

```sql
-- Wrong: Single time window — no temporal signal for the model
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS orders_30d,
    SUM(order_amount) AS spend_30d
FROM ORDERS
WHERE order_date >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY customer_id;

-- Correct: Multiple windows with velocity ratios
SELECT
    customer_id,
    -- Multi-window counts
    COUNT_IF(order_date >= DATEADD('day', -7, CURRENT_DATE())) AS orders_7d,
    COUNT_IF(order_date >= DATEADD('day', -30, CURRENT_DATE())) AS orders_30d,
    COUNT_IF(order_date >= DATEADD('day', -90, CURRENT_DATE())) AS orders_90d,
    -- Multi-window spend
    SUM(IFF(order_date >= DATEADD('day', -7, CURRENT_DATE()), order_amount, 0)) AS spend_7d,
    SUM(IFF(order_date >= DATEADD('day', -30, CURRENT_DATE()), order_amount, 0)) AS spend_30d,
    -- Velocity ratios — captures acceleration/deceleration
    orders_7d / NULLIF(orders_30d, 0) AS order_velocity_7d_30d,
    orders_30d / NULLIF(orders_90d, 0) AS order_velocity_30d_90d
FROM ORDERS
WHERE order_date >= DATEADD('day', -90, CURRENT_DATE())
GROUP BY customer_id;
```
