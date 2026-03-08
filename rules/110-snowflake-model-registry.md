# Snowflake Model Registry

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-02-25
**LoadTrigger:** kw:model-registry, kw:ml-model, kw:model-monitor, kw:ml-observability
**Keywords:** model governance, model lifecycle, model logging, model inference, RBAC, model privileges, register model, log model, model management, ML registry, model tracking, model metadata, deploy model, model lineage, model monitor, ML observability, task parameter, drift detection, baseline data, scoring data
**TokenBudget:** ~5900
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for using Snowflake Model Registry to manage machine learning models, ensuring secure, performant, and governable ML operations through proper lifecycle management, access control, versioning strategies, MODEL MONITOR integration for ML Observability, and cost optimization.

**When to Load This Rule:**
- Logging models to Snowflake Model Registry
- Managing ML model versions and lifecycle
- Implementing model access control and governance
- Running model inference in Snowflake
- Optimizing model registry costs
- Creating MODEL MONITORs for ML Observability
- Setting up drift detection and model performance monitoring

## References

### External Documentation
- [Snowflake Model Registry Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview) - Complete model registry documentation and API reference
- [Snowflake Model Registry API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/1.2.0/api/registry/snowflake.ml.registry.Registry) - Python API reference for registry operations
- [Snowflake Model Management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management) - Model lifecycle and management best practices
- [MODEL MONITOR Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-observability) - ML Observability and drift detection
- [CREATE MODEL MONITOR Syntax](https://docs.snowflake.com/en/sql-reference/sql/create-model-monitor) - SQL reference for MODEL MONITOR creation

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Data Science Analytics**: `920-data-science-analytics.md`
- **Snowflake Security**: `107-snowflake-security-governance.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`

## Contract

### Inputs and Prerequisites
- Snowflake session with appropriate ML privileges
- Trained ML model (sklearn, xgboost, etc.)
- Sample input data for schema inference
- Required conda dependencies identified

### Mandatory
- `snowflake.ml.registry.Registry` for model operations
- Sample input data for all model registrations
- Comprehensive metadata (comments, metrics, versioning)
- RBAC privilege configuration
- Inference testing before production deployment

### Forbidden
- Registering models without sample input data
- Using generic model names without business context
- Deploying models without testing inference
- Granting excessive privileges (always use least-privilege)
- Overwriting existing model versions

### Execution Steps
1. Create or verify dedicated registry schema exists
2. Initialize Registry with proper session and schema context
3. Prepare sample input data matching training data structure
4. Log model with comprehensive metadata and versioning
5. Configure RBAC privileges (OWNERSHIP, USAGE, READ)
6. Test model inference with validation dataset
7. Set performance metrics and business metadata
8. Enable audit logging and monitoring

### Output Format
- Registered models with semantic version names (v1_2_0 format)
- Comprehensive metadata including metrics and comments
- SQL grants for appropriate RBAC privileges
- Inference validation results
- Model performance dashboard queries

### Validation
- Verify model exists in registry: `SHOW MODELS LIKE '%name%' IN SCHEMA`
- Check model version registered: Query `INFORMATION_SCHEMA.MODEL_VERSIONS`
- Test inference returns expected predictions
- Validate RBAC privileges are correctly assigned
- Confirm metrics and metadata are populated

### Design Principles
- Registry-first approach: all models must be logged and versioned through the Model Registry
- Least-privilege access: use RBAC with appropriate model privileges (OWNERSHIP, USAGE, READ)
- Metadata-driven governance: comprehensive logging of metrics, comments, and lifecycle information
- Cost-conscious inference: choose appropriate compute resources and optimize model serving patterns
- Environment consistency: maintain reproducible model environments and dependencies
- Security-first: implement proper access controls, audit logging, and compliance measures

### Post-Execution Checklist
- [ ] Dedicated schema for registry created
- [ ] Models logged with version and metadata (semantic versioning)
- [ ] Sample input data included for all registrations
- [ ] RBAC privileges configured (least-privilege)
- [ ] Inference tested and validated
- [ ] Performance metrics logged
- [ ] Dependencies pinned in conda_dependencies
- [ ] Audit logging enabled
- [ ] Business metadata and comments added

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Specifying Sample Input Data for Schema Inference**
```python
# Bad: Register model without sample input
from snowflake.ml.registry import Registry
registry = Registry(session=session)

registry.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1"
    # Missing sample_input_data!
)
# Model registered but schema inference fails, can't generate SQL for inference!
```
**Problem:** No input schema captured; can't generate SQL inference; deployment failures

**Correct Pattern:**
```python
# Good: Include sample input data for schema inference
import pandas as pd
from snowflake.ml.registry import Registry

registry = Registry(session=session)

# Create sample input matching training data structure
sample_input = pd.DataFrame({
    'customer_age': [35],
    'account_balance': [50000.0],
    'days_since_last_purchase': [45]
})

registry.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1",
    sample_input_data=sample_input  # Schema captured!
)
```
**Benefits:** Input schema captured; SQL inference enabled; deployment-ready

**Anti-Pattern 2: Using WAREHOUSE Target Platform Without Understanding SQL Compatibility**
```python
# Bad: Use WAREHOUSE platform for complex sklearn model
from snowflake.ml.registry import TargetPlatform

registry.log_model(
    model=complex_sklearn_pipeline,  # Custom transformers, complex preprocessing
    model_name="complex_model",
    version_name="v1",
    target_platforms=[TargetPlatform.WAREHOUSE],  # Fails! Not all sklearn supported
    sample_input_data=sample_df
)
# Error: Custom transformers not supported in SQL translation!
```
**Problem:** SQL translation fails for custom/complex models; deployment failures; production delays

**Correct Pattern:**
```python
# Good: Use SNOWPARK_CONTAINER_SERVICES for complex models
from snowflake.ml.registry import TargetPlatform

registry.log_model(
    model=complex_sklearn_pipeline,
    model_name="complex_model",
    version_name="v1",
    target_platforms=[TargetPlatform.SNOWPARK_CONTAINER_SERVICES],  # Python inference
    sample_input_data=sample_df
)

# Use WAREHOUSE only for simple models (linear, tree-based)
# Check compatibility: https://docs.snowflake.com/en/developer-guide/snowpark-ml/model-registry/overview
```
**Benefits:** Reliable deployment; supports all model types; Python inference flexibility

**Anti-Pattern 3: Not Tagging Models with Metadata for Governance**
```python
# Bad: No metadata, can't discover or govern models
registry.log_model(
    model=trained_model,
    model_name="model_v1",  # Generic name!
    version_name="v1",
    sample_input_data=sample_df
)
# Can't identify: use case, owner, data source, performance, approval status
```
**Problem:** No governance; can't discover models by use case; unclear ownership; compliance risk

**Correct Pattern:**
```python
# Good: Rich metadata for governance and discovery
registry.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1.2.0",  # Semantic versioning
    sample_input_data=sample_df,
    comment="""
    Customer churn prediction model for subscription business
    Owner: data-science-team@company.com
    Training data: customers_2024_q1 (100K rows)
    Use case: Weekly batch predictions for marketing campaigns
    Approval: Approved by Model Governance Board on 2024-11-15
    """,
    metrics={
        'accuracy': 0.87,
        'precision': 0.82,
        'recall': 0.79,
        'f1_score': 0.80,
        'auc_roc': 0.91
    }
)

# Add tags for discovery
session.sql(f"""
    ALTER MODEL customer_churn_predictor
    SET TAG use_case = 'churn_prediction',
            owner_team = 'data_science',
            data_classification = 'CONFIDENTIAL',
            approval_status = 'APPROVED'
""").collect()
```
**Benefits:** Full governance; discoverable by metadata; clear ownership; audit-ready

**Anti-Pattern 4: Not Testing Model Inference After Registration**
```python
# Bad: Register model but never test inference
registry.log_model(
    model=trained_model,
    model_name="fraud_detector",
    version_name="v1",
    sample_input_data=sample_df
)
print("Model registered!")
# Never test: Does inference work? Are predictions correct?
# Discover issues when users complain in production!
```
**Problem:** Silent deployment failures; untested inference; production issues; trust erosion

**Correct Pattern:**
```python
# Good: Test inference immediately after registration
# Step 1: Register model
registry.log_model(
    model=trained_model,
    model_name="fraud_detector",
    version_name="v1",
    target_platforms=[TargetPlatform.WAREHOUSE],
    sample_input_data=sample_df
)

# Step 2: Load model and test inference
fraud_model = registry.get_model("fraud_detector").version("v1")

# Step 3: Test with sample data
test_data = pd.DataFrame({
    'transaction_amount': [150.0, 5000.0],
    'merchant_category': ['grocery', 'electronics'],
    'distance_from_home': [5.2, 500.0]
})

predictions = fraud_model.run(test_data)
print(f"Test predictions: {predictions}")

# Step 4: Validate predictions are reasonable
assert len(predictions) == 2, "Should return 2 predictions"
assert all(0 <= p <= 1 for p in predictions['FRAUD_PROBABILITY']), "Probabilities in [0,1]"

print("✓ Model inference validated, ready for production")
```
**Benefits:** Early error detection; validated inference; confidence in production

**Anti-Pattern 5: Not Enabling Monitoring on Registry When Planning to Use MODEL MONITOR**
```python
# Bad: Initialize Registry without enable_monitoring option
from snowflake.ml.registry import Registry

registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY"
    # Missing options={"enable_monitoring": True}!
)

registry.log_model(
    model=trained_model,
    model_name="fraud_detector",
    version_name="v1_0_0",
    sample_input_data=sample_df
)

# Later, try to create MODEL MONITOR...
# CREATE MODEL MONITOR fraud_monitor...
# ERROR: "MODEL does not exist or not authorized"
# The model EXISTS but MODEL MONITOR can't use it without monitoring enabled at registry level!
```
**Problem:** MODEL MONITOR requires `options={"enable_monitoring": True}` on Registry constructor; models registered without it cannot be monitored and must be re-registered

**Correct Pattern:**
```python
# Good: Enable monitoring on Registry constructor
from snowflake.ml.registry import Registry

registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY",
    options={"enable_monitoring": True}  # REQUIRED for MODEL MONITOR!
)

registry.log_model(
    model=trained_model,
    model_name="fraud_detector",
    version_name="v1_0_0",
    sample_input_data=sample_df
)

# Now MODEL MONITOR creation will work!
```
**Benefits:** MODEL MONITOR compatible; ML Observability enabled; drift detection ready; no re-registration required; production-ready

## Model Registry Setup and Organization

### Registry Initialization
- **Requirement:** Create dedicated schemas for model registries (e.g., `ML.REGISTRY`, `ANALYTICS.MODELS`)
- **Requirement:** Use fully qualified names when referencing registries across databases
- **Rule:** Initialize registry with proper session and database context:

```python
from snowflake.ml.registry import Registry

# Proper registry initialization
reg = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY"
)
```

### Schema Organization
- **Rule:** Separate registries by environment (DEV, STAGING, PROD)
- **Rule:** Use consistent naming conventions:
  - Development: `ML_DEV.REGISTRY`
  - Staging: `ML_STAGING.REGISTRY`
  - Production: `ML_PROD.REGISTRY`
- **Consider:** Create separate schemas for different model types or business domains

## Model Logging and Versioning

### Model Registration Best Practices
- **Requirement:** Always include comprehensive metadata when logging models:

```python
# Comprehensive model logging
mv = reg.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1_2_0",  # Use underscores - periods not allowed in SQL identifiers
    comment="Improved feature engineering with 95% accuracy",
    conda_dependencies=["scikit-learn==1.3.0", "pandas==2.0.3"],
    sample_input_data=X_sample,
    metadata={"training_dataset": "customer_data_2024_q3"}
)
```

### Versioning Strategy
- **Rule:** Use semantic versioning pattern (MAJOR_MINOR_PATCH) for model versions
- **Critical:** Version names must be valid SQL identifiers - use underscores instead of periods (e.g., `"v1_2_0"` not `"v1.2.0"`)
- **Rule:** Increment versions systematically:
  - MAJOR: Breaking changes to model interface or significant architecture changes
  - MINOR: New features, improved performance, or backward-compatible changes
  - PATCH: Bug fixes or minor improvements
- **Requirement:** Never overwrite existing model versions; always create new versions
- **Always:** Set default versions explicitly for production models

### Metadata Management
- **Requirement:** Log comprehensive metrics for each model version:

```python
# Set performance metrics
mv.set_metric("accuracy", 0.95)
mv.set_metric("precision", 0.92)
mv.set_metric("recall", 0.89)
mv.set_metric("f1_score", 0.90)

# Set training context
mv.set_metric("training_info", {
    "dataset_size": 100000,
    "training_duration": "2.5 hours",
    "feature_count": 25,
    "algorithm": "RandomForest"
})
```

- **Rule:** Include business-relevant metrics alongside technical metrics
- **Always:** Document model purpose, assumptions, and limitations in comments

## Access Control and Security

### Role-Based Access Control (RBAC)
- **Rule:** Implement least-privilege access using Snowflake's three model privilege levels:

```sql
-- Grant appropriate privileges
GRANT OWNERSHIP ON MODEL ml.registry.customer_churn_predictor TO ROLE ml_admin;
GRANT USAGE ON MODEL ml.registry.customer_churn_predictor TO ROLE data_scientist;
GRANT READ ON MODEL ml.registry.customer_churn_predictor TO ROLE ml_engineer;
```

### Privilege Guidelines
- **OWNERSHIP:** ML administrators and model owners only
- **USAGE:** Production applications requiring inference capabilities
- **READ:** Development teams needing model inspection and SPCS inference
- **Rule:** Use future grants for automatic privilege assignment:

```sql
-- Automatic privileges for new models
GRANT USAGE ON FUTURE MODELS IN SCHEMA ml.registry TO ROLE production_app;
GRANT READ ON FUTURE MODELS IN SCHEMA ml.registry TO ROLE ml_team;
```

### Security Best Practices
- **Requirement:** Enable audit logging for model access and modifications
- **Rule:** Regular access reviews and cleanup of unused privileges
- **Always:** Use secure stages for model artifacts and dependencies
- **Rule:** Implement row access policies for sensitive model metadata when required

## Model Inference and Serving

### Warehouse-Based Inference
- **Rule:** Choose appropriate warehouse sizes based on model complexity and data volume:

```python
# Efficient inference with proper error handling
try:
    predictions = mv.run(
        input_data,
        function_name="predict",
        warehouse="ML_INFERENCE_WH"  # Right-sized warehouse
    )
    results = predictions.collect()
except Exception as e:
    # Implement proper error handling and logging
    logger.error(f"Model inference failed: {str(e)}")
```

- **Always:** Use result caching when possible for repeated inference patterns
- **Rule:** Implement batch inference for large datasets rather than row-by-row processing

### SPCS-Based Inference
- **Consider:** Use Snowpark Container Services for GPU-intensive models or real-time serving
- **Rule:** Properly configure resource allocation for containerized models
- **Always:** Monitor container resource utilization and costs

### Performance Optimization
- **Always:** Profile inference performance and optimize bottlenecks
- **Rule:** Use appropriate data types and minimize data movement
- **Consider:** Implement model result caching for frequently accessed predictions

## Model Lifecycle Management

### Development to Production Pipeline
- **Requirement:** Establish clear promotion criteria between environments:

```python
# Model promotion workflow
def promote_model(source_reg, target_reg, model_name, version_name):
    # Validate model performance
    source_mv = source_reg.get_model(model_name).version(version_name)
    metrics = source_mv.show_metrics()

    if metrics.get("accuracy", 0) >= 0.90:
        # Export and re-import to target registry
        source_mv.export("/tmp/model_export")
        # Additional validation and import logic
        pass
```

### Model Monitoring and Maintenance
- **Requirement:** Implement model performance monitoring and drift detection
- **Rule:** Set up automated alerts for model performance degradation
- **Always:** Regularly retrain models based on performance thresholds
- **Rule:** Maintain model lineage and dependency tracking

### Version Management
- **Rule:** Implement retention policies for old model versions
- **Always:** Archive rather than delete historical model versions
- **Consider:** Automated cleanup of development versions while preserving production versions

## MODEL MONITOR Integration (ML Observability)

### Prerequisites for MODEL MONITOR
- **Critical Requirement:** Registry MUST be initialized with `options={"enable_monitoring": True}` to use MODEL MONITOR
- **Rule:** The `enable_monitoring` option must be set at Registry creation time - models registered without it cannot be monitored
- **Warning:** Models registered without `enable_monitoring` will cause "MODEL does not exist or not authorized" errors when creating monitors, even though the model exists
- **Rule:** If model was registered without `enable_monitoring`, you must DROP the model and re-register using a monitoring-enabled Registry

### Registry Initialization for MODEL MONITOR
```python
from snowflake.ml.registry import Registry

# REQUIRED: Enable monitoring in options to use MODEL MONITOR
registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY",
    options={"enable_monitoring": True}  # CRITICAL for MODEL MONITOR!
)
```

### Model Registration for MODEL MONITOR
```python
# Initialize with monitoring enabled (see Registry Initialization above)
# Then register model - no special parameters needed if Registry has monitoring enabled
model_ref = registry.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1_0_0",
    comment="Binary classifier for customer churn prediction",
    sample_input_data=X_test.head(5),
    conda_dependencies=["scikit-learn", "pandas", "numpy"]
)
```

### Creating a MODEL MONITOR
- **Requirement:** Prepare baseline and scoring data tables before creating monitor
- **Rule:** Baseline table should contain representative sample of training data distribution
- **Rule:** Scoring table accumulates production predictions for drift comparison
- **Critical:** Set explicit session context (USE DATABASE/SCHEMA) before CREATE MODEL MONITOR to ensure model reference resolves correctly
- **Critical:** Baseline and scoring table schemas MUST match exactly - same columns with same names and compatible types
- **Tip:** You can create MODEL MONITOR without BASELINE for accuracy-only monitoring; add BASELINE later once schemas align

```sql
-- IMPORTANT: Set session context before creating monitor
USE DATABASE ML;
USE SCHEMA MONITORING;

-- Create MODEL MONITOR for drift detection and performance monitoring
CREATE MODEL MONITOR customer_churn_monitor
  WITH 
    MODEL = CUSTOMER_CHURN_PREDICTOR,  -- Uses current schema context
    VERSION = V1_0_0,
    SOURCE = SCORING_DATA,              -- Production predictions
    BASELINE = BASELINE_DATA,           -- Training distribution (optional, enables drift)
    TIMESTAMP_COLUMN = PREDICTION_TIMESTAMP,
    PREDICTION_SCORE_COLUMNS = (PREDICTION),
    ACTUAL_CLASS_COLUMNS = (ACTUAL_LABEL),  -- Optional: for accuracy monitoring
    ID_COLUMNS = (CUSTOMER_ID),
    WAREHOUSE = MY_WH,
    REFRESH_INTERVAL = '1 hour',
    AGGREGATION_WINDOW = '1 day';

-- Check monitor status
SHOW MODEL MONITORS;
DESC MODEL MONITOR customer_churn_monitor;
```

### Schema Alignment for Baseline/Scoring Tables
- **Rule:** Both tables must have identical feature columns for drift detection to work
- **Warning:** Extra columns in baseline that don't exist in scoring will cause schema mismatch errors
- **Pattern:** Create a view over baseline that selects only the columns present in scoring table

```sql
-- If baseline has extra columns, create aligned view
CREATE OR REPLACE VIEW ML.MONITORING.BASELINE_ALIGNED AS
SELECT 
    CUSTOMER_ID,
    FEATURE_1,
    FEATURE_2,
    PREDICTION,
    ACTUAL_LABEL,
    PREDICTION_TIMESTAMP
FROM ML.MONITORING.BASELINE_DATA;
-- Then use BASELINE = BASELINE_ALIGNED in MODEL MONITOR
```

### Required Table Structures
```sql
-- Baseline table: sample from training data
CREATE TABLE ML.MONITORING.BASELINE_DATA (
    CUSTOMER_ID VARCHAR,
    FEATURE_1 FLOAT,
    FEATURE_2 FLOAT,
    -- ... all model input features
    PREDICTION FLOAT,           -- Model prediction
    ACTUAL_LABEL INT,           -- Ground truth (if available)
    PREDICTION_TIMESTAMP TIMESTAMP_NTZ
);

-- Scoring table: production predictions (append-only)
CREATE TABLE ML.MONITORING.SCORING_DATA (
    CUSTOMER_ID VARCHAR,
    FEATURE_1 FLOAT,
    FEATURE_2 FLOAT,
    -- ... all model input features (must match baseline)
    PREDICTION FLOAT,
    ACTUAL_LABEL INT,           -- Populated later when ground truth available
    PREDICTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### MODEL MONITOR Privileges
```sql
-- Grant privileges for MODEL MONITOR operations
GRANT USAGE ON MODEL ML.REGISTRY.CUSTOMER_CHURN_PREDICTOR TO ROLE ml_monitoring;
GRANT SELECT ON TABLE ML.MONITORING.BASELINE_DATA TO ROLE ml_monitoring;
GRANT SELECT ON TABLE ML.MONITORING.SCORING_DATA TO ROLE ml_monitoring;
GRANT CREATE MODEL MONITOR ON SCHEMA ML.MONITORING TO ROLE ml_monitoring;
```

## Cost Governance and Optimization

### Storage Optimization
- **Rule:** Monitor model storage costs and implement cleanup policies
- **Always:** Compress model artifacts when possible
- **Consider:** Archive infrequently used models to lower-cost storage

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
- **Consider:** Automated model registration from notebook environments

### CI/CD Integration
- **Requirement:** Integrate model registry operations into automated ML pipelines
- **Rule:** Implement automated testing for model versions before production deployment
- **Always:** Use version control for model training scripts and registry operations

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
