# Snowflake MODEL MONITOR (ML Observability)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:model-monitor, kw:ml-observability
**Keywords:** model monitor, drift detection, baseline data, scoring data, ML observability, model performance monitoring, prediction drift, schema alignment, enable_monitoring
**TokenBudget:** ~2950
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 110-snowflake-model-registry.md

## Scope

**What This Rule Covers:**
MODEL MONITOR integration for ML Observability including drift detection, performance monitoring, baseline/scoring table setup, schema alignment, and privilege configuration.

**When to Load This Rule:**
- Creating MODEL MONITORs for ML Observability
- Setting up drift detection and model performance monitoring
- Configuring baseline and scoring tables
- Troubleshooting MODEL MONITOR errors

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **110-snowflake-model-registry.md** - Model Registry core patterns

### External Documentation

- [MODEL MONITOR Overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-observability) - ML Observability and drift detection
- [CREATE MODEL MONITOR Syntax](https://docs.snowflake.com/en/sql-reference/sql/create-model-monitor) - SQL reference for MODEL MONITOR creation

## Contract

### Inputs and Prerequisites

- Model registered in Snowflake Model Registry with `enable_monitoring=True`
- Baseline data table (representative sample of training distribution)
- Scoring data table (production predictions, append-only)
- Warehouse for monitor refresh operations

### Mandatory

- Registry initialized with `options={"enable_monitoring": True}`
- Baseline and scoring table schemas match exactly
- Session context set (USE DATABASE/SCHEMA) before CREATE MODEL MONITOR

### Forbidden

- Creating MODEL MONITOR without `enable_monitoring` on Registry
- Mismatched schemas between baseline and scoring tables

### Execution Steps

1. Initialize Registry with `enable_monitoring=True`
2. Register model with monitoring-enabled Registry
3. Create baseline and scoring tables with matching schemas
4. Set session context and create MODEL MONITOR
5. Grant monitoring privileges

### Output Format

- Registry initialization with monitoring enabled
- CREATE MODEL MONITOR SQL statements
- Baseline/scoring table DDL
- Privilege grant statements

### Validation

- Verify MODEL MONITOR created: `SHOW MODEL MONITORS`
- Check monitor details: `DESC MODEL MONITOR <name>`
- Confirm baseline/scoring schemas match
- Test privilege grants for monitoring role

### Design Principles

- Always enable monitoring at Registry creation time
- Align baseline and scoring schemas before creating monitors
- Set explicit session context for reliable model resolution
- Use views to align schemas when baseline has extra columns

### Post-Execution Checklist

- [ ] Registry initialized with `enable_monitoring=True`
- [ ] Model registered with monitoring-enabled Registry
- [ ] Baseline table created with training data sample
- [ ] Scoring table created with matching schema
- [ ] MODEL MONITOR created with appropriate refresh interval
- [ ] Privileges granted to monitoring role
- [ ] Monitor status verified with SHOW/DESC

## Prerequisites for MODEL MONITOR

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

## Creating a MODEL MONITOR

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

## Schema Alignment for Baseline/Scoring Tables

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

## Required Table Structures

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

## MODEL MONITOR Privileges

```sql
-- Grant privileges for MODEL MONITOR operations
GRANT USAGE ON MODEL ML.REGISTRY.CUSTOMER_CHURN_PREDICTOR TO ROLE ml_monitoring;
GRANT SELECT ON TABLE ML.MONITORING.BASELINE_DATA TO ROLE ml_monitoring;
GRANT SELECT ON TABLE ML.MONITORING.SCORING_DATA TO ROLE ml_monitoring;
GRANT CREATE MODEL MONITOR ON SCHEMA ML.MONITORING TO ROLE ml_monitoring;
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Registering Models Without enable_monitoring Then Wondering Why Monitors Fail**

**Problem:** Developers register a model using a Registry initialized without `options={"enable_monitoring": True}`, then attempt to create a MODEL MONITOR. The CREATE MODEL MONITOR statement fails with "MODEL does not exist or not authorized" even though `SHOW MODELS` lists the model. The only fix is to DROP the model and re-register it with a monitoring-enabled Registry, which disrupts production references.

**Correct Pattern:** Always initialize the Registry with `options={"enable_monitoring": True}` before registering any model you plan to monitor. Treat this as a one-time setup step per registry schema and verify it before the first `log_model` call.

```python
# Wrong: Registry without enable_monitoring — monitors will fail with "MODEL does not exist"
from snowflake.ml.registry import Registry
registry = Registry(session=session, database_name="ML", schema_name="REGISTRY")
registry.log_model(model, model_name="CHURN_MODEL", version_name="v1_0_0")
# Later: CREATE MODEL MONITOR ... MODEL = CHURN_MODEL -> ERROR

# Correct: Always enable monitoring at Registry creation time
registry = Registry(
    session=session,
    database_name="ML",
    schema_name="REGISTRY",
    options={"enable_monitoring": True}  # Required for MODEL MONITOR
)
registry.log_model(model, model_name="CHURN_MODEL", version_name="v1_0_0")
```

**Anti-Pattern 2: Schema Mismatch Between Baseline and Scoring Tables**

**Problem:** The baseline table is created from the full training DataFrame (which includes target columns, metadata, or extra engineered features), while the scoring table only contains the columns populated at inference time. CREATE MODEL MONITOR fails with a schema mismatch error, or drift detection produces misleading results because columns don't align.

**Correct Pattern:** Create a view over the baseline table that selects only the columns present in the scoring table. Use `DESCRIBE TABLE` on both tables to confirm column names and types match exactly before creating the monitor. Define the baseline schema from the scoring schema, not the other way around.

```sql
-- Wrong: Baseline has extra columns not in scoring table — schema mismatch error
CREATE TABLE ML.MONITORING.BASELINE_DATA AS
SELECT * FROM TRAINING_DATA;  -- Includes target, metadata, extra features

CREATE TABLE ML.MONITORING.SCORING_DATA (
    CUSTOMER_ID VARCHAR, FEATURE_1 FLOAT, PREDICTION FLOAT, PREDICTION_TIMESTAMP TIMESTAMP_NTZ
);
-- CREATE MODEL MONITOR ... BASELINE = BASELINE_DATA -> schema mismatch error

-- Correct: Create aligned view matching scoring schema exactly
DESCRIBE TABLE ML.MONITORING.SCORING_DATA;  -- Check columns first

CREATE OR REPLACE VIEW ML.MONITORING.BASELINE_ALIGNED AS
SELECT CUSTOMER_ID, FEATURE_1, PREDICTION, PREDICTION_TIMESTAMP
FROM ML.MONITORING.BASELINE_DATA;  -- Only columns that exist in scoring

-- Use the aligned view as baseline
CREATE MODEL MONITOR churn_monitor
  WITH MODEL = CHURN_MODEL, VERSION = V1_0_0,
    SOURCE = SCORING_DATA, BASELINE = BASELINE_ALIGNED,
    TIMESTAMP_COLUMN = PREDICTION_TIMESTAMP,
    PREDICTION_SCORE_COLUMNS = (PREDICTION),
    ID_COLUMNS = (CUSTOMER_ID), WAREHOUSE = MY_WH,
    REFRESH_INTERVAL = '1 hour', AGGREGATION_WINDOW = '1 day';
```

**Anti-Pattern 3: Skipping Session Context Before CREATE MODEL MONITOR**

**Problem:** Developers run `CREATE MODEL MONITOR` without first setting `USE DATABASE` and `USE SCHEMA`, relying on fully qualified model names. The model reference fails to resolve because MODEL MONITOR uses session context to locate models in the registry, leading to confusing "model not found" errors even with correct fully-qualified names.

**Correct Pattern:** Always set explicit session context with `USE DATABASE <db>; USE SCHEMA <schema>;` immediately before `CREATE MODEL MONITOR`. This ensures the model reference resolves correctly against the registry schema where the model is registered.

```sql
-- Wrong: No session context — model reference fails to resolve
CREATE MODEL MONITOR churn_monitor
  WITH MODEL = ML.REGISTRY.CHURN_MODEL, VERSION = V1_0_0,
    SOURCE = ML.MONITORING.SCORING_DATA,
    TIMESTAMP_COLUMN = PREDICTION_TIMESTAMP,
    PREDICTION_SCORE_COLUMNS = (PREDICTION),
    ID_COLUMNS = (CUSTOMER_ID), WAREHOUSE = MY_WH,
    REFRESH_INTERVAL = '1 hour', AGGREGATION_WINDOW = '1 day';
-- Error: "MODEL does not exist or not authorized" despite correct FQN

-- Correct: Set session context before creating monitor
USE DATABASE ML;
USE SCHEMA MONITORING;

CREATE MODEL MONITOR churn_monitor
  WITH MODEL = CHURN_MODEL, VERSION = V1_0_0,
    SOURCE = SCORING_DATA, BASELINE = BASELINE_ALIGNED,
    TIMESTAMP_COLUMN = PREDICTION_TIMESTAMP,
    PREDICTION_SCORE_COLUMNS = (PREDICTION),
    ID_COLUMNS = (CUSTOMER_ID), WAREHOUSE = MY_WH,
    REFRESH_INTERVAL = '1 hour', AGGREGATION_WINDOW = '1 day';
```
