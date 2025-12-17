# Snowflake Model Registry

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** model governance, model lifecycle, model logging, model inference, RBAC, model privileges, register model, log model, model management, ML registry, model tracking, model metadata, deploy model, model lineage
**TokenBudget:** ~3550
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md

## Purpose
Establish comprehensive best practices for using Snowflake Model Registry to manage machine learning models, ensuring secure, performant, and governable ML operations through proper lifecycle management, access control, versioning strategies, and cost optimization.

## Rule Scope

Snowflake Model Registry operations including model logging, versioning, access control, inference, and lifecycle management for Python ML models

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~450 tokens (always load for model registry tasks)
- + Model Logging & Versioning (sections 1-2): ~1100 tokens (load for registration)
- + Inference & Governance (sections 3-4): ~2000 tokens (load for deployment)
- + Complete Reference: ~2600 tokens (full model registry guide)

**Recommended Loading Strategy:**
- **Understanding model registry**: Quick Start only
- **Logging models**: + Model Logging & Versioning
- **Model inference**: + Inference & Governance
- **Production MLOps**: Full reference

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Registry-first approach** - All models logged through Model Registry
- **Use least-privilege RBAC** - Grant only needed privileges (OWNERSHIP, USAGE, READ)
- **Version all models** - Comprehensive versioning with metadata
- **Log metrics and comments** - Track model performance and lineage
- **Optimize inference** - Choose appropriate compute, optimize serving
- **Maintain environment consistency** - Pin dependencies, reproducible envs
- **Never deploy unregistered models** - Always use Model Registry

**Quick Checklist:**
- [ ] Dedicated schema for registry created
- [ ] Models logged with version and metadata
- [ ] RBAC privileges configured
- [ ] Inference tested and optimized
- [ ] Dependencies pinned
- [ ] Audit logging enabled
- [ ] Lifecycle stages tracked

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
- Registry-first approach: all models must be logged and versioned through the Model Registry
- Least-privilege access: use RBAC with appropriate model privileges (OWNERSHIP, USAGE, READ)
- Metadata-driven governance: comprehensive logging of metrics, comments, and lifecycle information
- Cost-conscious inference: choose appropriate compute resources and optimize model serving patterns
- Environment consistency: maintain reproducible model environments and dependencies
- Security-first: implement proper access controls, audit logging, and compliance measures
> **Investigation Required**
> When working with Model Registry:
> 1. Verify registry exists: `SHOW SCHEMAS LIKE '%REGISTRY%' IN DATABASE <db>;`
> 2. Check model exists before operations: `SHOW MODELS LIKE '%name%' IN SCHEMA <db>.<schema>;`
> 3. Verify model version exists: `SELECT * FROM <db>.<schema>.INFORMATION_SCHEMA.MODELS WHERE MODEL_NAME = '<name>';`
> 4. Check permissions before logging: `SHOW GRANTS ON SCHEMA <db>.<schema>;`
> 5. Never assume conda dependencies - check available packages in Snowflake conda channel
> 6. Test model inference before production deployment
>
> **Anti-Pattern:**
> "Let me log this model - it should work with these dependencies."
>
> **Correct Pattern:**
> "Let me verify the registry exists and check available conda packages first."
> [checks registry, verifies conda channel has required packages]
> "Registry verified. Required packages available in Snowflake conda channel. Logging model..."
</design_principles>

</contract>

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
**Problem:** No input schema captured; can't generate SQL inference; deployment failures; unclear model signature; unusable for SQL-based predictions

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
**Benefits:** Input schema captured; SQL inference enabled; clear model signature; deployment-ready; production-usable; automatic schema validation


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
**Problem:** SQL translation fails for custom/complex models; deployment failures; wasted time; emergency fallback required; production delays

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
**Benefits:** Reliable deployment; supports all model types; no SQL translation issues; Python inference flexibility; production-ready; predictable behavior


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
**Problem:** No governance; can't discover models by use case; unclear ownership; no performance tracking; audit gaps; compliance risk; chaos at scale

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
**Benefits:** Full governance; discoverable by metadata; clear ownership; performance tracked; audit-ready; compliance-friendly; scalable model management


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
**Problem:** Silent deployment failures; untested inference; production issues; user complaints; emergency fixes; trust erosion; unprofessional

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
**Benefits:** Early error detection; validated inference; confidence in production; no surprises; professional deployment; reliable predictions; user trust

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read existing model registry setup BEFORE logging models** - Check registry schema, naming conventions
> 2. **Verify model format compatibility** - Check if model type supported by registry
> 3. **Never assume RBAC privileges** - Query existing privileges to understand access patterns
> 4. **Check inference patterns** - Review how existing models are served
> 5. **Test model loading** - Validate model can be loaded and run inference before deployment
>
> **Anti-Pattern:**
> "Logging model to registry... (without checking registry structure)"
> "Granting OWNERSHIP... (without understanding least-privilege needs)"
>
> **Correct Pattern:**
> "Let me check your Model Registry setup first."
> [reads registry schema, checks existing models, reviews privileges]
> "I see you organize models by ML.REGISTRY schema with version tags. Logging new model following this pattern..."

## Output Format Examples

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## References

### External Documentation
- [Snowflake Model Registry Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview) - Complete model registry documentation and API reference
- [Snowflake Model Registry API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/1.2.0/api/registry/snowflake.ml.registry.Registry) - Python API reference for registry operations
- [Snowflake Model Management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management) - Model lifecycle and management best practices
- [Snowflake ML Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview) - Complete Snowflake ML ecosystem documentation
- [Snowflake Security Guide](https://docs.snowflake.com/en/user-guide/security) - Security features and access control implementation

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Data Science Analytics**: `rules/920-data-science-analytics.md`
- **Snowflake Security**: `rules/107-snowflake-security-governance.md`
- **Snowflake Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Snowflake Notebooks**: `rules/109-snowflake-notebooks.md`

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
