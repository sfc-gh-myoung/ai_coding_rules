# Snowflake Model Registry

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:model-registry, kw:ml-model
**Keywords:** model governance, model lifecycle, model logging, model inference, RBAC, model privileges, register model, log model, model management, ML registry, model tracking, model metadata, deploy model, model lineage
**TokenBudget:** ~3900
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md
**Companions:** 110a-snowflake-model-monitor.md, 110b-snowflake-model-registry-operations.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for using Snowflake Model Registry to manage machine learning models, ensuring secure, performant, and governable ML operations through proper lifecycle management, access control, and versioning strategies.

**When to Load This Rule:**
- Logging models to Snowflake Model Registry
- Managing ML model versions and lifecycle
- Implementing model access control and governance
- Running model inference in Snowflake

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

```sql
-- Discovery queries
SHOW MODELS IN SCHEMA ml.registry;
SELECT * FROM INFORMATION_SCHEMA.MODEL_VERSIONS WHERE MODEL_NAME = 'customer_churn_predictor';
```

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
    version_name="v1_2_0",  # Semantic versioning (underscores, not periods)
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
# First, ensure tags exist
session.sql("CREATE TAG IF NOT EXISTS use_case ALLOWED_VALUES 'churn_prediction', 'fraud_detection', 'recommendation'").collect()
session.sql("CREATE TAG IF NOT EXISTS owner_team").collect()
session.sql("CREATE TAG IF NOT EXISTS data_classification ALLOWED_VALUES 'PUBLIC', 'CONFIDENTIAL', 'RESTRICTED'").collect()
session.sql("CREATE TAG IF NOT EXISTS approval_status ALLOWED_VALUES 'PENDING', 'APPROVED', 'REJECTED'").collect()

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

> See **110b-snowflake-model-registry-operations.md** for the full inference testing anti-pattern with correct validation workflow.

**Anti-Pattern 5: Not Enabling Monitoring on Registry When Planning to Use MODEL MONITOR**

> See **110a-snowflake-model-monitor.md** for the full monitoring enablement anti-pattern with correct `options={"enable_monitoring": True}` pattern.

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
    # Add options={"enable_monitoring": True} if using MODEL MONITOR (see 110a)
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
# Note: Snowflake does not have a direct cross-registry export/import API.
# Cross-environment promotion requires re-logging the model in the target registry.
def promote_model(source_session, target_session, model_name, version_name):
    # 1. Validate model performance in source
    source_reg = Registry(session=source_session, database_name="ML_DEV", schema_name="REGISTRY")
    source_mv = source_reg.get_model(model_name).version(version_name)
    metrics = source_mv.show_metrics()

    if metrics.get("accuracy", 0) >= 0.90:
        # 2. Re-log model in target registry with the original model object
        target_reg = Registry(session=target_session, database_name="ML_PROD", schema_name="REGISTRY")
        target_reg.log_model(
            model=source_mv,  # Pass model version as source
            model_name=model_name,
            version_name=version_name,
            sample_input_data=sample_df
        )
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

> **See companion rule:** `110a-snowflake-model-monitor.md` for complete MODEL MONITOR patterns including prerequisites, creation syntax, schema alignment, required table structures, and privilege grants.

- **Critical Requirement:** Registry MUST be initialized with `options={"enable_monitoring": True}` to use MODEL MONITOR
- **Warning:** Models registered without `enable_monitoring` will cause "MODEL does not exist or not authorized" errors when creating monitors

## Cost Governance, Queries, and Operations

> **See companion rule:** `110b-snowflake-model-registry-operations.md` for cost governance, resource monitoring, administrative queries, model maintenance, CI/CD integration, and compliance patterns.
