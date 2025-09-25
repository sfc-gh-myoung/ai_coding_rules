**Description:** Comprehensive best practices for Snowflake Model Registry, covering model lifecycle, security, versioning, and governance.
**AppliesTo:** `**/*.py`, `**/*.sql`, `**/*.ipynb`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-17

# Snowflake Model Registry

## Purpose
Establish comprehensive best practices for using Snowflake Model Registry to manage machine learning models, ensuring secure, performant, and governable ML operations through proper lifecycle management, access control, versioning strategies, and cost optimization.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Model Registry operations including model logging, versioning, access control, inference, and lifecycle management for Python ML models

## Key Principles
- Registry-first approach: all models must be logged and versioned through the Model Registry
- Least-privilege access: use RBAC with appropriate model privileges (OWNERSHIP, USAGE, READ)
- Metadata-driven governance: comprehensive logging of metrics, comments, and lifecycle information
- Cost-conscious inference: choose appropriate compute resources and optimize model serving patterns
- Environment consistency: maintain reproducible model environments and dependencies
- Security-first: implement proper access controls, audit logging, and compliance measures

## 1. Model Registry Setup and Organization

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

## 2. Model Logging and Versioning

### Model Registration Best Practices
- **Requirement:** Always include comprehensive metadata when logging models:

```python
# Comprehensive model logging
mv = reg.log_model(
    model=trained_model,
    model_name="customer_churn_predictor",
    version_name="v1.2.0",
    comment="Improved feature engineering with 95% accuracy",
    conda_dependencies=["scikit-learn==1.3.0", "pandas==2.0.3"],
    sample_input_data=X_sample,
    metadata={"training_dataset": "customer_data_2024_q3"}
)
```

### Versioning Strategy
- **Rule:** Use semantic versioning (MAJOR.MINOR.PATCH) for model versions
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

## 3. Access Control and Security

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

## 4. Model Inference and Serving

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

## 5. Model Lifecycle Management

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

## 6. Cost Governance and Optimization

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

## 7. Model Registry Queries and Administration

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

## 8. Integration with ML Workflows

### Notebook Integration
- **Rule:** Use registry operations within Snowflake notebooks for seamless ML workflows
- **Always:** Document model experiments and results in notebook metadata
- **Consider:** Automated model registration from notebook environments

### CI/CD Integration
- **Requirement:** Integrate model registry operations into automated ML pipelines
- **Rule:** Implement automated testing for model versions before production deployment
- **Always:** Use version control for model training scripts and registry operations

## 9. Compliance and Governance

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Snowflake Model Registry Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview) - Complete model registry documentation and API reference
- [Snowflake Model Registry API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/1.2.0/api/registry/snowflake.ml.registry.Registry) - Python API reference for registry operations
- [Snowflake Model Management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management) - Model lifecycle and management best practices
- [Snowflake ML Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview) - Complete Snowflake ML ecosystem documentation
- [Snowflake Security Guide](https://docs.snowflake.com/en/user-guide/security) - Security features and access control implementation

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
- **Snowflake Security**: `107-snowflake-security-governance.md`
- **Snowflake Cost Governance**: `105-snowflake-cost-governance.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
