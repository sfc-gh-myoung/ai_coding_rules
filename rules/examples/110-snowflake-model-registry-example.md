# 110 Example: Model Registry with MODEL MONITOR

> **EXAMPLE FILE** - Reference implementation for `110-snowflake-model-registry.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 110-snowflake-model-registry.md
**Demonstrates:** End-to-end model registration with `enable_monitoring` option for MODEL MONITOR compatibility
**Use When:** Registering ML models that will be monitored for drift and performance degradation
**Version:** 1.1
**Last Validated:** 2026-02-25

## Prerequisites

- [ ] Snowflake account with Model Registry feature enabled
- [ ] Role with CREATE MODEL privilege in target schema
- [ ] Trained sklearn, XGBoost, or compatible model
- [ ] Sample input data for schema inference

## Critical: The enable_monitoring Option

**Why This Example Exists:** Models registered with a Registry that does NOT have `options={"enable_monitoring": True}` cannot be used with MODEL MONITOR. The error message "MODEL does not exist or not authorized" is misleading - the model exists but the Registry wasn't configured for monitoring. You must DROP and re-register the model using a monitoring-enabled Registry.

**Always include `options={"enable_monitoring": True}` when:**
- You plan to use MODEL MONITOR for ML Observability
- You want drift detection or performance monitoring
- You're building production ML pipelines

## Implementation

### Step 1: Set Up Registry Schema and Tables

```sql
-- Create dedicated schema for ML models and monitoring
CREATE SCHEMA IF NOT EXISTS ML.REGISTRY;
CREATE SCHEMA IF NOT EXISTS ML.MONITORING;

-- Grant necessary privileges
GRANT USAGE ON DATABASE ML TO ROLE data_scientist;
GRANT USAGE ON SCHEMA ML.REGISTRY TO ROLE data_scientist;
GRANT USAGE ON SCHEMA ML.MONITORING TO ROLE data_scientist;
GRANT CREATE MODEL ON SCHEMA ML.REGISTRY TO ROLE data_scientist;
```

### Step 2: Create Monitoring Tables BEFORE Model Registration

```sql
-- Baseline table: representative sample of training data distribution
-- This captures what "normal" looks like for drift detection
CREATE OR REPLACE TABLE ML.MONITORING.CHURN_BASELINE_DATA (
    CUSTOMER_ID VARCHAR,
    ACCOUNT_AGE_DAYS NUMBER,
    TOTAL_PURCHASES NUMBER,
    AVG_ORDER_VALUE FLOAT,
    DAYS_SINCE_LAST_PURCHASE NUMBER,
    SUPPORT_TICKETS_30D NUMBER,
    -- Model outputs
    PREDICTION FLOAT,           -- Predicted probability
    PREDICTION_CLASS INT,       -- Binary prediction (0/1)
    ACTUAL_LABEL INT,           -- Ground truth (populated later)
    PREDICTION_TIMESTAMP TIMESTAMP_NTZ
);

-- Scoring table: accumulates production predictions
CREATE OR REPLACE TABLE ML.MONITORING.CHURN_SCORING_DATA (
    CUSTOMER_ID VARCHAR,
    ACCOUNT_AGE_DAYS NUMBER,
    TOTAL_PURCHASES NUMBER,
    AVG_ORDER_VALUE FLOAT,
    DAYS_SINCE_LAST_PURCHASE NUMBER,
    SUPPORT_TICKETS_30D NUMBER,
    -- Model outputs
    PREDICTION FLOAT,
    PREDICTION_CLASS INT,
    ACTUAL_LABEL INT,
    PREDICTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Step 3: Train and Register Model WITH Monitoring-Enabled Registry

```python
from snowflake.snowpark import Session
from snowflake.ml.registry import Registry
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# Establish session
session = Session.builder.configs(connection_params).create()

# CRITICAL: Initialize registry WITH enable_monitoring option
# This is REQUIRED for MODEL MONITOR to work
registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY",
    options={"enable_monitoring": True}  # REQUIRED for MODEL MONITOR!
)

# Prepare training data (example)
training_df = session.table("ML.TRAINING.CHURN_FEATURES").to_pandas()
X = training_df.drop(['CUSTOMER_ID', 'CHURNED'], axis=1)
y = training_df['CHURNED']

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
model.fit(X, y)

# Register model - no special parameters needed when Registry has monitoring enabled
model_ref = registry.log_model(
    model=model,
    model_name="CUSTOMER_CHURN_PREDICTOR",
    version_name="V1_0_0",  # Use underscores - periods invalid in SQL identifiers
    comment="""
    Customer churn binary classifier using Random Forest.
    Owner: ml-team@company.com
    Training data: ML.TRAINING.CHURN_FEATURES (50,000 rows)
    Use case: Daily batch predictions for retention campaigns
    """,
    sample_input_data=X.head(5),  # REQUIRED for schema inference
    conda_dependencies=[
        "scikit-learn==1.3.0",
        "pandas==2.0.3",
        "numpy==1.24.0"
    ],
    metrics={
        'accuracy': 0.87,
        'precision': 0.82,
        'recall': 0.79,
        'f1_score': 0.80,
        'auc_roc': 0.91
    }
)

print(f"Model registered: {model_ref.model_name} version {model_ref.version_name}")
```

### Step 4: Verify Model Registration

```python
# Verify model was registered correctly
models = registry.show_models()
print(models[['name', 'default_version_name', 'comment']])

# Get model version details
mv = registry.get_model("CUSTOMER_CHURN_PREDICTOR").version("V1_0_0")

# Show metrics
print("Model metrics:", mv.show_metrics())

# Test inference
test_input = pd.DataFrame({
    'ACCOUNT_AGE_DAYS': [365, 30],
    'TOTAL_PURCHASES': [25, 2],
    'AVG_ORDER_VALUE': [150.0, 45.0],
    'DAYS_SINCE_LAST_PURCHASE': [7, 90],
    'SUPPORT_TICKETS_30D': [0, 3]
})

predictions = mv.run(test_input)
print("Test predictions:", predictions)
```

### Step 5: Populate Baseline Data

```python
# Get baseline sample from training data (or holdout set)
baseline_df = session.table("ML.TRAINING.CHURN_FEATURES").sample(n=1000)
baseline_pandas = baseline_df.to_pandas()

# Get features for prediction
X_baseline = baseline_pandas.drop(['CUSTOMER_ID', 'CHURNED'], axis=1)

# Run inference on baseline
baseline_predictions = mv.run(X_baseline)

# Combine with original data
baseline_pandas['PREDICTION'] = baseline_predictions['output_feature_0']
baseline_pandas['PREDICTION_CLASS'] = (baseline_pandas['PREDICTION'] > 0.5).astype(int)
baseline_pandas['ACTUAL_LABEL'] = baseline_pandas['CHURNED']
baseline_pandas['PREDICTION_TIMESTAMP'] = pd.Timestamp.now()

# Write to baseline table
baseline_final = baseline_pandas[[
    'CUSTOMER_ID', 'ACCOUNT_AGE_DAYS', 'TOTAL_PURCHASES',
    'AVG_ORDER_VALUE', 'DAYS_SINCE_LAST_PURCHASE', 'SUPPORT_TICKETS_30D',
    'PREDICTION', 'PREDICTION_CLASS', 'ACTUAL_LABEL', 'PREDICTION_TIMESTAMP'
]]

session.write_pandas(
    baseline_final, 
    "CHURN_BASELINE_DATA",
    database="ML",
    schema="MONITORING",
    overwrite=True
)

print(f"Baseline data populated: {len(baseline_final)} rows")
```

### Step 6: Create MODEL MONITOR

```sql
-- Create MODEL MONITOR for drift detection and performance monitoring
CREATE MODEL MONITOR ML.MONITORING.CHURN_MODEL_MONITOR
  WITH 
    MODEL = ML.REGISTRY.CUSTOMER_CHURN_PREDICTOR,
    VERSION = V1_0_0,
    SOURCE_TABLE = ML.MONITORING.CHURN_SCORING_DATA,
    BASELINE_TABLE = ML.MONITORING.CHURN_BASELINE_DATA,
    TIMESTAMP_COLUMN = PREDICTION_TIMESTAMP,
    PREDICTION_COLUMN = PREDICTION,
    LABEL_COLUMN = ACTUAL_LABEL,
    ID_COLUMNS = (CUSTOMER_ID),
    SCHEDULE = 'USING CRON 0 8 * * * America/Los_Angeles';

-- Verify monitor created successfully
SHOW MODEL MONITORS;

-- Describe monitor configuration
DESC MODEL MONITOR ML.MONITORING.CHURN_MODEL_MONITOR;
```

### Step 7: Grant MODEL MONITOR Privileges

```sql
-- Create monitoring role
CREATE ROLE IF NOT EXISTS ml_monitoring;

-- Grant access to model
GRANT USAGE ON MODEL ML.REGISTRY.CUSTOMER_CHURN_PREDICTOR TO ROLE ml_monitoring;

-- Grant access to monitoring tables
GRANT SELECT ON TABLE ML.MONITORING.CHURN_BASELINE_DATA TO ROLE ml_monitoring;
GRANT SELECT, INSERT ON TABLE ML.MONITORING.CHURN_SCORING_DATA TO ROLE ml_monitoring;

-- Grant monitor access
GRANT MONITOR ON MODEL MONITOR ML.MONITORING.CHURN_MODEL_MONITOR TO ROLE ml_monitoring;
```

## Common Errors and Solutions

### Error: "MODEL does not exist or not authorized"

**Symptom:** CREATE MODEL MONITOR fails with this error even though SHOW MODELS confirms model exists.

**Root Cause:** Model was registered using a Registry without `options={"enable_monitoring": True}`.

**Solution:**
```python
# Step 1: Drop the existing model
# DROP MODEL ML.REGISTRY.CUSTOMER_CHURN_PREDICTOR;

# Step 2: Re-create Registry with monitoring enabled
registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY",
    options={"enable_monitoring": True}  # THIS IS THE FIX!
)

# Step 3: Re-register the model
model_ref = registry.log_model(
    model=model,
    model_name="CUSTOMER_CHURN_PREDICTOR",
    version_name="V1_0_0",
    sample_input_data=X.head(5),
    # ... other parameters
)
```

### Error: "Invalid identifier 'V1.0.0'"

**Symptom:** Version name with periods causes SQL errors.

**Root Cause:** Periods are not valid in SQL identifiers.

**Solution:** Use underscores instead: `V1_0_0` not `V1.0.0`

### Error: "Sample input data required"

**Symptom:** Model inference fails or generates incorrect schema.

**Root Cause:** Model was registered without `sample_input_data`.

**Solution:** Always provide `sample_input_data=X.head(5)` during registration.

## Validation Checklist

- [ ] Registry initialized with `options={"enable_monitoring": True}`
- [ ] Version name uses underscores (not periods)
- [ ] `sample_input_data` provided for schema inference
- [ ] Baseline table populated with training distribution sample
- [ ] Scoring table created for production predictions
- [ ] MODEL MONITOR created successfully (no errors)
- [ ] SHOW MODEL MONITORS returns the new monitor
- [ ] Appropriate RBAC privileges granted
