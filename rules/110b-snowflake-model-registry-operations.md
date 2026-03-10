# Snowflake Model Registry: Operations & Governance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:model-registry-operations
**Keywords:** model cost governance, model queries, model administration, model compliance, model audit, model maintenance, resource monitor ML, model integration, CI/CD models, notebook models
**TokenBudget:** ~3100
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 110-snowflake-model-registry.md

## Scope

**What This Rule Covers:**
Operational patterns for Snowflake Model Registry including cost governance, storage/compute optimization, administrative queries, model maintenance, CI/CD integration, and compliance documentation.

**When to Load This Rule:**
- Optimizing model registry costs (storage and compute)
- Running administrative queries against model registry
- Implementing model maintenance and cleanup workflows
- Integrating model registry with CI/CD pipelines or notebooks
- Establishing compliance and audit processes for ML models

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **110-snowflake-model-registry.md** - Model Registry core patterns

**Related:**
- **105-snowflake-cost-governance.md** - Cost monitoring and governance
- **119-snowflake-warehouse-management.md** - Warehouse sizing

### External Documentation

- [Snowflake Model Registry Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview) - Complete model registry documentation
- [Snowflake Model Management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management) - Model lifecycle and management

## Contract

### Inputs and Prerequisites

- Model Registry configured (see 110-snowflake-model-registry.md)
- Access to INFORMATION_SCHEMA for model queries
- ACCOUNTADMIN or cost monitoring role for resource monitors

### Mandatory

- Resource monitors for ML compute workloads
- Regular model auditing and cleanup
- Compliance documentation for production models

### Forbidden

- Running inference on oversized warehouses without monitoring
- Ignoring stale model versions (>90 days unused)

### Execution Steps

1. Set up resource monitors for ML workloads
2. Create administrative query views for model governance
3. Implement model maintenance and cleanup workflows
4. Integrate with CI/CD and notebook environments
5. Establish compliance documentation processes

### Output Format

- Resource monitor DDL statements
- Administrative SQL queries for model governance
- Model maintenance workflows
- Integration patterns for CI/CD and notebooks

### Validation

- Resource monitors active and triggering appropriately
- Administrative queries returning expected results
- Stale models identified and cleaned up
- Compliance documentation current

### Design Principles

- Cost-conscious inference: choose appropriate compute resources
- Regular auditing: identify and clean up unused models
- Automated governance: use queries to enforce policies
- Environment consistency: CI/CD integration for reproducibility

### Post-Execution Checklist

- [ ] Resource monitors configured for ML workloads
- [ ] Administrative query views created
- [ ] Model cleanup workflow established
- [ ] CI/CD integration implemented
- [ ] Compliance documentation process defined

## Cost Governance and Optimization

### Storage Optimization
- **Rule:** Monitor model storage costs and implement cleanup policies
- **Always:** Compress model artifacts when possible
- **Rule:** Archive infrequently used models to lower-cost storage

### Compute Optimization
- **Rule:** Right-size warehouses for model training and inference workloads
- **Always:** Use auto-suspend and auto-resume for inference warehouses
- **Rule:** Monitor inference costs and optimize batch sizes

### Resource Monitoring
- **Requirement:** Implement resource monitors for model-related compute:

```sql
-- Create resource monitor for ML workloads
CREATE RESOURCE MONITOR ml_workload_monitor
WITH CREDIT_QUOTA = 1000
TRIGGERS
  ON 75 PERCENT DO NOTIFY
  ON 90 PERCENT DO SUSPEND
  ON 100 PERCENT DO SUSPEND_IMMEDIATE;
```

**Cost Attribution by Model:**
```sql
-- Estimate inference cost by model using query history
SELECT
    REGEXP_SUBSTR(query_text, 'MODEL\\s+([\\w.]+)', 1, 1, 'i', 1) AS model_name,
    COUNT(*) AS inference_count,
    SUM(total_elapsed_time) / 1000 AS total_seconds,
    SUM(credits_used_cloud_services) AS cloud_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_text ILIKE '%!predict%'
  AND start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY model_name
ORDER BY cloud_credits DESC;
```

## Model Registry Queries and Administration

### Information Schema Queries
- **Always:** Use `INFORMATION_SCHEMA.MODEL_VERSIONS` for model governance:

```sql
-- Model performance dashboard
SELECT
    catalog_name,
    schema_name,
    model_name,
    model_version_name,
    metadata:metric:accuracy AS accuracy,
    metadata:metric:f1_score AS f1_score,
    comment,
    owner,
    created_on,
    last_altered_on
FROM ml.information_schema.model_versions
WHERE schema_name = 'REGISTRY'
ORDER BY accuracy DESC;
```

### Model Maintenance Queries
- **Rule:** Regular model auditing and cleanup:

```sql
-- Identify models without recent usage
SELECT
    model_name,
    model_version_name,
    last_altered_on,
    DATEDIFF('day', last_altered_on, CURRENT_TIMESTAMP()) as days_since_update
FROM ml.information_schema.model_versions
WHERE days_since_update > 90
ORDER BY days_since_update DESC;
```

## Integration with ML Workflows

### Notebook Integration
- **Rule:** Use registry operations within Snowflake notebooks for seamless ML workflows
- **Always:** Document model experiments and results in notebook metadata

### CI/CD Integration
- **Requirement:** Integrate model registry operations into automated ML pipelines
- **Rule:** Implement automated testing for model versions before production deployment
- **Always:** Use version control for model training scripts and registry operations

> See **Anti-Pattern 3** below for a complete validation gate example with schema checks, holdout tests, and production comparison.

## Compliance and Governance

### Model Documentation
- **Requirement:** Maintain comprehensive model documentation including:
  - Model purpose and business use case
  - Training data sources and characteristics
  - Model limitations and assumptions
  - Performance metrics and validation results

### Audit and Compliance
- **Rule:** Implement audit logging for all model registry operations
- **Always:** Maintain model lineage and data provenance information
- **Requirement:** Regular compliance reviews for model access and usage

**Model Documentation Template** (use as comment when logging models):
```
Model: <model_name> v<version>
Purpose: <business use case>
Owner: <team/email>
Training Data: <source table, row count, date range>
Limitations: <known edge cases or constraints>
Approved By: <governance board, date>
```

**Model Access Audit Query:**
```sql
-- Audit model access via ACCESS_HISTORY
SELECT
    user_name,
    query_start_time,
    direct_objects_accessed
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY,
    LATERAL FLATTEN(direct_objects_accessed) obj
WHERE obj.value:objectName::STRING ILIKE '%CHURN_PREDICTOR%'
  AND query_start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP())
ORDER BY query_start_time DESC;
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Running Inference on Oversized Warehouses Without Cost Controls**

**Problem:** Developers use their default XL or 2XL warehouse for model inference because it's convenient, without considering that inference workloads are often lightweight and don't need large compute. Without a resource monitor, a batch inference job on an oversized warehouse silently burns through credits — a simple scoring query that needs an XS warehouse runs on a 2XL at 64x the cost per hour.

**Correct Pattern:** Create a dedicated right-sized warehouse for inference (typically XS or S) with auto-suspend enabled, and attach a resource monitor with NOTIFY and SUSPEND triggers. Profile inference latency on smaller warehouses before scaling up — most single-model scoring jobs perform identically on XS as on XL.

```sql
-- Wrong: Running inference on default oversized warehouse without cost controls
USE WAREHOUSE ANALYTICS_2XL_WH;  -- 64 credits/hour
SELECT model!predict(INPUT_DATA:*) AS prediction
FROM PRODUCTION_SCORING_DATA;  -- Burns credits needlessly

-- Correct: Dedicated right-sized warehouse with resource monitor
CREATE WAREHOUSE IF NOT EXISTS ML_INFERENCE_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  COMMENT = 'Dedicated warehouse for model inference';

CREATE RESOURCE MONITOR ml_inference_monitor
  WITH CREDIT_QUOTA = 100
  TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO SUSPEND
    ON 100 PERCENT DO SUSPEND_IMMEDIATE;

ALTER WAREHOUSE ML_INFERENCE_WH SET RESOURCE_MONITOR = ml_inference_monitor;

USE WAREHOUSE ML_INFERENCE_WH;
SELECT model!predict(INPUT_DATA:*) AS prediction
FROM PRODUCTION_SCORING_DATA;
```

**Anti-Pattern 2: Accumulating Stale Model Versions Without Cleanup**

**Problem:** Teams register new model versions for every experiment or training run but never drop old ones. Over months, the registry accumulates hundreds of unused versions that consume storage, clutter governance queries, and make it difficult to identify which version is actually in production. `SHOW MODELS` returns pages of results with no indication of which versions matter.

**Correct Pattern:** Implement a scheduled cleanup workflow that queries `INFORMATION_SCHEMA.MODEL_VERSIONS` for versions not altered in >90 days, cross-references with production deployment records, and drops unused versions. Tag production versions with a comment like "PRODUCTION" and set up an alert for registries exceeding a version count threshold.

```sql
-- Wrong: Hundreds of stale versions accumulate with no cleanup
-- SHOW MODELS IN SCHEMA ML.REGISTRY;  -- Returns 200+ versions, no way to tell which is production

-- Correct: Identify and clean up stale model versions
-- Step 1: Find stale versions (not altered in 90+ days, not tagged PRODUCTION)
SELECT model_name, model_version_name, last_altered_on,
    DATEDIFF('day', last_altered_on, CURRENT_TIMESTAMP()) AS days_stale,
    comment
FROM ML.INFORMATION_SCHEMA.MODEL_VERSIONS
WHERE DATEDIFF('day', last_altered_on, CURRENT_TIMESTAMP()) > 90
  AND (comment IS NULL OR comment NOT ILIKE '%PRODUCTION%')
ORDER BY days_stale DESC;

-- Step 2: Tag production versions so they are never cleaned up
ALTER MODEL ML.REGISTRY.CHURN_PREDICTOR MODIFY VERSION V2_1_0
  SET COMMENT = 'PRODUCTION - deployed 2024-06-15';

-- Step 3: Drop confirmed stale versions
ALTER MODEL ML.REGISTRY.CHURN_PREDICTOR DROP VERSION V1_0_0;
ALTER MODEL ML.REGISTRY.CHURN_PREDICTOR DROP VERSION V1_1_0;
```

**Automated Cleanup Task:**
```sql
-- Schedule weekly cleanup of stale model versions
CREATE OR REPLACE TASK model_cleanup_task
  WAREHOUSE = ADMIN_WH
  SCHEDULE = 'USING CRON 0 6 * * MON America/Los_Angeles'
AS
  -- Generates DROP statements for stale non-production versions
  -- Review output before enabling task; adjust threshold as needed
  SELECT 'ALTER MODEL ML.REGISTRY.' || model_name || ' DROP VERSION ' || model_version_name || ';'
  FROM ML.INFORMATION_SCHEMA.MODEL_VERSIONS
  WHERE DATEDIFF('day', last_altered_on, CURRENT_TIMESTAMP()) > 90
    AND (comment IS NULL OR comment NOT ILIKE '%PRODUCTION%');
```

**Anti-Pattern 3: Deploying Model Versions Without Automated Validation**

**Problem:** A new model version is registered and immediately promoted to production without running validation tests. The model may have been trained on stale data, have degraded accuracy on edge cases, or have incompatible input/output schemas compared to the previous version. Issues are only discovered when downstream consumers report bad predictions.

**Correct Pattern:** Integrate model validation into your CI/CD pipeline. Before promoting any version, run automated checks: validate input/output schema compatibility with the previous version, execute a holdout test set to confirm metrics meet minimum thresholds, and compare performance against the currently deployed version. Only promote after all gates pass.

```python
# Wrong: Register and immediately use in production without validation
from snowflake.ml.registry import Registry
registry = Registry(session=session, database_name="ML", schema_name="REGISTRY")
model_ref = registry.log_model(model, model_name="CHURN_MODEL", version_name="v2_0_0")
# Immediately promoted — no validation, no comparison to previous version

# Correct: Validate before promoting to production
model_ref = registry.log_model(
    model, model_name="CHURN_MODEL", version_name="v2_0_0",
    sample_input_data=X_test.head(5),
    comment="Candidate — pending validation"
)

# Gate 1: Schema compatibility check
prev_version = registry.get_model("CHURN_MODEL").version("v1_0_0")
new_version = registry.get_model("CHURN_MODEL").version("v2_0_0")

# Gate 2: Run holdout test set and check metrics
predictions = new_version.run(X_holdout, function_name="predict")
# Note: Check predictions.columns to find the actual output column name
output_col = predictions.columns[-1]  # Typically the last column
accuracy = (predictions[output_col] == y_holdout).mean()
assert accuracy >= 0.85, f"Accuracy {accuracy} below threshold 0.85"

# Gate 3: Compare against current production version
prod_predictions = prev_version.run(X_holdout, function_name="predict")
prod_accuracy = (prod_predictions[output_col] == y_holdout).mean()
assert accuracy >= prod_accuracy * 0.98, "New version regression vs production"

# All gates passed — tag as production via SQL
session.sql("""
    ALTER MODEL ML.REGISTRY.CHURN_MODEL MODIFY VERSION V2_0_0
    SET COMMENT = 'PRODUCTION - validated and promoted'
""").collect()
```
