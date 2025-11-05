---
appliesTo:
  - "**/*.sql"
  - "**/*.scl"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Warehouse management, warehouse sizing, CPU warehouse, GPU warehouse, high-memory warehouse, warehouse tagging, auto-suspend, auto-resume
**Depends:** 100-snowflake-core, 103-snowflake-performance-tuning, 105-snowflake-cost-governance

**TokenBudget:** ~1100
**ContextTier:** High

# Snowflake Warehouse Management

## Purpose
Establish comprehensive best practices for creating, configuring, and managing Snowflake virtual warehouses, including proper selection of warehouse types (CPU/GPU/High-Memory), mandatory GEN 2 preference, sizing strategies, auto-suspend configuration, tagging standards, and cost governance integration.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Virtual warehouse creation, configuration, lifecycle management, type selection (Standard, Snowpark-Optimized, High-Memory), and cost optimization

## Contract
- **Inputs/Prereqs:** Snowflake account with warehouse creation privileges (`CREATE WAREHOUSE`); workload requirements; cost baseline; resource monitor strategy
- **Allowed Tools:** Snowflake DDL commands; warehouse configuration; SHOW/DESCRIBE commands; Query Profile analysis; resource monitors
- **Forbidden Tools:** Creating warehouses without mandatory tags; using Standard edition when GEN 2 available; oversized warehouses without documented justification; disabling auto-suspend in non-production
- **Required Steps:**
  1. Assess workload type (interactive BI, batch ETL, ML training/inference, complex analytics)
  2. Select appropriate warehouse type (Standard CPU, Snowpark-Optimized GPU, High-Memory)
  3. Determine warehouse edition (ALWAYS prefer GEN 2 when available)
  4. Size warehouse appropriately (start small, scale up based on metrics)
  5. Configure auto-suspend and auto-resume settings
  6. Apply mandatory tags for cost tracking and governance
  7. Associate with resource monitors
  8. Document sizing justification and expected workload patterns
  9. Validate configuration and monitor usage patterns
- **Output Format:** Complete DDL with inline comments; configuration tables; decision matrices; monitoring queries
- **Validation Steps:** Warehouse created successfully; correct type and edition selected; mandatory tags applied; auto-suspend working as expected; resource monitor associated; initial query performance meets expectations

## Key Principles
- **GEN 2 First:** Always prefer GEN 2 warehouses over Standard edition for improved performance and cost efficiency
- **Type Selection:** Use Standard CPU for general workloads, Snowpark-Optimized for GPU-accelerated ML, High-Memory for complex analytics
- **Start Small:** Begin with smaller sizes (XSMALL/SMALL) and scale up based on actual performance metrics
- **Auto-Suspend Always:** Enable auto-suspend on all warehouses with appropriate timeouts
- **Tag Everything:** Apply mandatory tags for cost allocation, governance, and lifecycle management
- **Cost Integration:** Every warehouse must be associated with a resource monitor
- **Monitor and Optimize:** Continuously review warehouse usage and right-size based on Query Profile data

## 1. Warehouse Types and Resource Constraints

### 1.1 Resource Constraint Options (GEN 2 Mandate)

**Rule:** ALWAYS use `RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'` for new standard warehouses when available (generally available in most AWS/Azure regions, Enterprise Edition+).

**Why GEN 2:** 20-30% better price-performance, ARM architecture, improved query optimization, better concurrency handling.

**Available Resource Constraints:**

| Type | Constraint | Architecture | Memory | Use When |
|------|-----------|--------------|--------|----------|
| **Standard GEN 1** | `STANDARD_GEN_1` | x86 | Standard | Legacy/compatibility only |
| **Standard GEN 2** ✅ | `STANDARD_GEN_2` | ARM | Standard | **Default for all new warehouses** |
| **High-Memory** | `MEMORY_16X` | ARM | 16X (256GB @ LARGE) | Memory-intensive queries (prove need first) |
| **High-Memory x86** | `MEMORY_16X_x86` | x86 | 16X | x86-specific compatibility + memory |
| **Snowpark GPU** | *(implicit)* | GPU | Standard | ML training, GPU UDFs (set WAREHOUSE_TYPE) |

**Note:** Snowpark-Optimized uses `WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'` (GPU implicit, no RESOURCE_CONSTRAINT needed).

### 1.2 Warehouse Type Decision Matrix

| Workload Type | Warehouse Type | Use Cases | Notes |
|---------------|----------------|-----------|-------|
| **General BI/Analytics** | Standard (CPU) | Dashboards, ad-hoc queries, reporting, most SQL workloads | Default choice for 80%+ of workloads |
| **ML Training/Inference** | Snowpark-Optimized (GPU) | Snowpark ML model training, GPU-accelerated UDFs, vector operations | Requires GPU-enabled account features |
| **Complex Aggregations** | High-Memory | Large window functions, complex joins on billions of rows, memory-intensive analytics | Use only when Standard shows memory pressure |
| **ETL/Data Loading** | Standard (CPU) | COPY INTO, data transformation, incremental pipelines | Size based on data volume and SLAs |
| **Streaming/Real-Time** | Standard (CPU) | Snowpipe, continuous data ingestion, low-latency queries | Keep running or very short auto-suspend |

### 1.3 When to Use GPU (Snowpark-Optimized) Warehouses

**Use GPU warehouses for:**
- Snowpark ML model training with large datasets
- GPU-accelerated Python UDFs using libraries like cuDF, cuML, PyTorch
- Vector similarity searches at scale
- Image/video processing workloads
- Deep learning inference requiring GPU acceleration

**DO NOT use GPU warehouses for:**
- Standard SQL queries (no performance benefit, higher cost)
- Simple transformations or aggregations
- Dashboard queries or BI tools
- Tasks that don't leverage GPU-accelerated libraries

**Example GPU Warehouse Creation:**
```sql
-- GPU warehouse for ML model training
CREATE OR REPLACE WAREHOUSE WH_ML_TRAINING_GPU_M
  WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 300  -- 5 minutes for ML workloads
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'GPU-accelerated warehouse for Snowpark ML training - see confluence.company.com/ml-warehouse-docs';

-- Apply mandatory tags
ALTER WAREHOUSE WH_ML_TRAINING_GPU_M SET TAG
  COST_CENTER = 'DATA_SCIENCE',
  WORKLOAD_TYPE = 'ML_TRAINING',
  ENVIRONMENT = 'PROD',
  OWNER_TEAM = 'DATA_SCIENCE';
```

### 1.4 When to Use High-Memory Warehouses

**Use High-Memory warehouses for:**
- Queries with massive intermediate result sets
- Complex window functions over billions of rows
- Large Cartesian products or multi-way joins
- Memory-intensive Python/Java UDFs in Snowpark
- Queries that spill to remote storage (check Query Profile)

**DO NOT use High-Memory warehouses for:**
- Queries that can be optimized with better SQL
- Workloads with proper clustering and pruning
- Standard aggregations and filters
- "Just in case" - only after proving memory pressure

**Example High-Memory Warehouse Creation:**
```sql
-- High-memory warehouse for complex analytics
CREATE OR REPLACE WAREHOUSE WH_ANALYTICS_HIMEM_L
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'LARGE'
  RESOURCE_CONSTRAINT = 'MEMORY_16X'  -- 16X memory (256 GB for LARGE)
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'High-memory warehouse for complex financial aggregations - Query Profile showed memory spilling on LARGE';

-- Apply mandatory tags
ALTER WAREHOUSE WH_ANALYTICS_HIMEM_L SET TAG
  COST_CENTER = 'FINANCE',
  WORKLOAD_TYPE = 'COMPLEX_ANALYTICS',
  ENVIRONMENT = 'PROD',
  OWNER_TEAM = 'ANALYTICS';
```

## 2. Warehouse Sizing Guidelines

### 2.1 Size Selection Strategy

**Start Small, Scale Up:**
1. Begin with XSMALL or SMALL for new workloads
2. Monitor Query Profile for queueing and execution time
3. Scale up incrementally (one size at a time)
4. Document justification for sizes above MEDIUM

**Sizing Reference:**

| Size | Servers/Credits per Hour | Best For | Typical Use Cases |
|------|--------------------------|----------|-------------------|
| **XSMALL** | 1 / 1 | Single-user queries, testing, light dashboards | Dev/test, personal analytics |
| **SMALL** | 2 / 2 | Small team BI, light ETL, scheduled reports | Team dashboards, nightly loads |
| **MEDIUM** | 4 / 4 | Department-wide BI, moderate ETL, concurrent users | Production BI tools, daily ETL |
| **LARGE** | 8 / 8 | Heavy ETL, complex queries, high concurrency | Enterprise dashboards, large transformations |
| **XLARGE** | 16 / 16 | Very large datasets, time-critical workloads | Critical ETL, real-time analytics |
| **2X/3X/4XLARGE** | 32-128 / 32-128 | Massive parallel processing, extreme performance needs | Rare; requires executive approval |

### 2.2 Multi-Cluster Warehouses

**Use multi-cluster for:** High concurrency (many users, unpredictable traffic). **Scaling policies:** STANDARD (immediate, favor performance) vs ECONOMY (delayed, favor cost).

```sql
CREATE OR REPLACE WAREHOUSE WH_BI_PRODUCTION_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 5
  SCALING_POLICY = 'STANDARD'  -- Or 'ECONOMY'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Multi-cluster BI warehouse - scales 1-5 clusters';
-- Apply tags (see Section 4 for tag setup)
```

## 3. Auto-Suspend and Auto-Resume Configuration

**Rule:** ALWAYS enable auto-suspend. ALWAYS set `AUTO_RESUME = TRUE` (except deprecated warehouses or emergency cost control).

**Recommended Auto-Suspend Settings:**

| Workload Type | Seconds | Rationale |
|---------------|---------|-----------|
| **Interactive BI** | 300-600 (5-10 min) | Balance UX and cost |
| **Batch ETL** | 60-120 (1-2 min) | Quick shutdown post-job |
| **Dev/Test** | 60-180 (1-3 min) | Minimize dev costs |
| **Streaming** | 60 (1 min) | Near-continuous use |
| **ML Training** | 300-600 (5-10 min) | Interactive experimentation |
| **24/7 Critical** | 600+ (10+ min) | Balance availability/cost |

```sql
-- Example: Interactive BI with 5-min timeout
CREATE OR REPLACE WAREHOUSE WH_INTERACTIVE_BI_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'
  AUTO_SUSPEND = 300  -- Adjust per workload type above
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Interactive BI - 5min auto-suspend';
```

## 4. Mandatory Tagging Standards

### 4.1 Required Tags for All Warehouses

**Rule:** EVERY warehouse MUST have the following tags applied for cost tracking, governance, and lifecycle management.

**Note:** For comprehensive object tagging guidance including tag creation, inheritance, and governance patterns, see `123-snowflake-object-tagging.md`.

**Mandatory Tags:**

| Tag Name | Purpose | Example Values | Required |
|----------|---------|----------------|----------|
| **COST_CENTER** | Chargeback allocation | FINANCE, MARKETING, DATA_SCIENCE | ✅ Yes |
| **WORKLOAD_TYPE** | Workload categorization | BI_INTERACTIVE, ETL_BATCH, ML_TRAINING | ✅ Yes |
| **ENVIRONMENT** | Deployment stage | DEV, QA, PROD | ✅ Yes |
| **OWNER_TEAM** | Responsible team | DATA_ENGINEERING, ANALYTICS, BI_PLATFORM | ✅ Yes |
| **DATA_CLASSIFICATION** | Data sensitivity | PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED | Recommended |
| **LIFECYCLE_STAGE** | Operational status | ACTIVE, DEPRECATED, EXPERIMENTAL | Recommended |

### 4.2 Tag Schema Setup and Application

```sql
-- One-time tag schema setup
CREATE SCHEMA IF NOT EXISTS GOVERNANCE.TAGS;

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.COST_CENTER
  ALLOWED_VALUES 'FINANCE', 'MARKETING', 'DATA_SCIENCE', 'ENGINEERING', 'OPERATIONS', 'SALES';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.WORKLOAD_TYPE
  ALLOWED_VALUES 'BI_INTERACTIVE', 'BI_SCHEDULED', 'ETL_BATCH', 'ETL_STREAMING', 
                 'ML_TRAINING', 'ML_INFERENCE', 'ANALYTICS', 'DATA_LOADING', 'DEVELOPMENT';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.ENVIRONMENT
  ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.OWNER_TEAM;

-- Apply tags to warehouses (after creation)
ALTER WAREHOUSE WH_[NAME] SET TAG
  GOVERNANCE.TAGS.COST_CENTER = '[VALUE]',
  GOVERNANCE.TAGS.WORKLOAD_TYPE = '[VALUE]',
  GOVERNANCE.TAGS.ENVIRONMENT = '[VALUE]',
  GOVERNANCE.TAGS.OWNER_TEAM = '[VALUE]';
```

### 4.3 Tag Validation Query

```sql
-- Verify all warehouses have required tags
SELECT 
  w.name AS warehouse_name,
  w.size AS warehouse_size,
  w.auto_suspend,
  tt.tag_name,
  tt.tag_value
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES w
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tt
  ON tt.object_name = w.name
  AND tt.object_domain = 'WAREHOUSE'
WHERE w.deleted IS NULL
ORDER BY w.name, tt.tag_name;

-- Find warehouses missing mandatory tags
WITH required_tags AS (
  SELECT 'COST_CENTER' AS tag_name UNION ALL
  SELECT 'WORKLOAD_TYPE' UNION ALL
  SELECT 'ENVIRONMENT' UNION ALL
  SELECT 'OWNER_TEAM'
),
warehouse_tags AS (
  SELECT 
    object_name AS warehouse_name,
    tag_name
  FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
  WHERE object_domain = 'WAREHOUSE'
    AND deleted IS NULL
)
SELECT 
  w.name AS warehouse_name,
  rt.tag_name AS missing_tag
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES w
CROSS JOIN required_tags rt
LEFT JOIN warehouse_tags wt
  ON wt.warehouse_name = w.name
  AND wt.tag_name = rt.tag_name
WHERE w.deleted IS NULL
  AND wt.warehouse_name IS NULL
ORDER BY w.name, rt.tag_name;
```

## 5. Cost Governance and Resource Monitors

**Rule:** EVERY production warehouse MUST be associated with a resource monitor.

```sql
-- Account-level monitor (safety net)
CREATE RESOURCE MONITOR IF NOT EXISTS RM_ACCOUNT_MONTHLY
  WITH CREDIT_QUOTA = 50000
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 75 PERCENT DO NOTIFY, ON 100 PERCENT DO SUSPEND;

ALTER ACCOUNT SET RESOURCE_MONITOR = RM_ACCOUNT_MONTHLY;

-- Workload-specific monitors
CREATE RESOURCE MONITOR IF NOT EXISTS RM_BI_WORKLOADS
  WITH CREDIT_QUOTA = 5000 FREQUENCY = MONTHLY
  TRIGGERS ON 75 PERCENT DO NOTIFY, ON 100 PERCENT DO SUSPEND;

-- Associate warehouse with monitor
ALTER WAREHOUSE WH_[NAME] SET RESOURCE_MONITOR = RM_BI_WORKLOADS;
```

**Key cost monitoring query (see `111-snowflake-observability.md` for complete monitoring suite):**
```sql
-- Identify idle/underutilized warehouses
SELECT w.name, w.size, COALESCE(SUM(wm.credits_used), 0) AS credits_30d
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES w
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
  ON wm.warehouse_name = w.name AND wm.start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
WHERE w.deleted IS NULL
GROUP BY w.name, w.size
HAVING credits_30d < 10
ORDER BY credits_30d DESC;
```

## 6. Naming Conventions and Lifecycle

**Naming Pattern:** `WH_[WORKLOAD]_[TYPE?]_[SIZE?]`
- **Examples:** `WH_MARKETING_M`, `WH_ML_TRAINING_GPU_M`, `WH_ANALYTICS_HIMEM_XL`, `WH_DEV_SANDBOX_XS`

**Right-Sizing Signals:**
- **Scale UP:** Consistent queueing (queued_overload_time > 0), P95 execution time > requirements, missing SLAs
- **Scale DOWN:** Utilization < 30%, no queueing in 30 days, queries finish well within SLAs
- **Use Multi-Cluster:** High concurrency but individual queries fast

**Performance monitoring (detailed queries in `111-snowflake-observability.md`):**
```sql
-- Quick queue check
SELECT warehouse_name, AVG(queued_overload_time)/1000 AS avg_queue_sec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY warehouse_name HAVING avg_queue_sec > 0;
```

### 6.1 Warehouse Decommissioning

```sql
-- 1. Mark deprecated, disable auto-resume
ALTER WAREHOUSE WH_OLD SET TAG GOVERNANCE.TAGS.LIFECYCLE_STAGE = 'DEPRECATED';
ALTER WAREHOUSE WH_OLD SET AUTO_RESUME = FALSE;

-- 2. Monitor usage for 7 days
SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE warehouse_name = 'WH_OLD' AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP());

-- 3. Drop after confirming zero usage
DROP WAREHOUSE IF EXISTS WH_OLD;
```

## Quick Compliance Checklist

**Provisioning:**
- [ ] Workload type assessed, appropriate warehouse type selected (Standard/GPU/High-Memory)
- [ ] GEN 2 edition used (`RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'`)
- [ ] Sized appropriately (started XSMALL/SMALL, scaled based on metrics)
- [ ] Auto-suspend configured (60-600 sec), auto-resume enabled
- [ ] All mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
- [ ] Resource monitor associated
- [ ] Naming convention followed (`WH_[WORKLOAD]_[TYPE?]_[SIZE?]`)
- [ ] `INITIALLY_SUSPENDED = TRUE` set
- [ ] Documented with business justification

**Validation:**
- [ ] Warehouse created successfully, tags verified
- [ ] Auto-suspend working, Query Profile shows expected performance
- [ ] Cost tracking functional, monitoring queries configured

## Validation
- **Success Checks:** Warehouse created successfully with correct type and edition; all mandatory tags present; auto-suspend working as configured; resource monitor association verified; Query Profile shows expected performance; cost tracking functional in monitoring queries; warehouse appears in governance inventory
- **Negative Tests:** Creating warehouse without tags fails governance checks; oversized warehouse (XLARGE+) without documented justification triggers review; disabled auto-suspend in non-production raises alert; warehouse without resource monitor blocked or flagged; GPU warehouse used for standard SQL shows cost inefficiency; High-memory warehouse used without memory pressure evidence

## Response Template
```sql
-- Standard CPU warehouse for BI workloads (GEN 2 preferred)
CREATE OR REPLACE WAREHOUSE WH_[WORKLOAD]_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'  -- Use GEN 2 when available (omit if not available)
  AUTO_SUSPEND = 300  -- 5 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = '[Purpose and business justification - link to docs if extensive]';

-- Apply mandatory tags
ALTER WAREHOUSE WH_[WORKLOAD]_M SET TAG
  GOVERNANCE.TAGS.COST_CENTER = '[COST_CENTER]',
  GOVERNANCE.TAGS.WORKLOAD_TYPE = '[WORKLOAD_TYPE]',
  GOVERNANCE.TAGS.ENVIRONMENT = '[ENV]',
  GOVERNANCE.TAGS.OWNER_TEAM = '[TEAM]',
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = '[CLASSIFICATION]',
  GOVERNANCE.TAGS.LIFECYCLE_STAGE = 'ACTIVE';

-- Associate with resource monitor
ALTER WAREHOUSE WH_[WORKLOAD]_M SET RESOURCE_MONITOR = [MONITOR_NAME];

-- Verify configuration
SHOW WAREHOUSES LIKE 'WH_[WORKLOAD]_M';
SELECT * FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('WH_[WORKLOAD]_M', 'WAREHOUSE'));
```

## References

### External Documentation
- [Virtual Warehouses Overview](https://docs.snowflake.com/en/user-guide/warehouses-overview) - Complete warehouse concepts, sizing, and management
- [Warehouse Considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations) - Performance tuning and best practices
- [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse) - Complete DDL syntax reference
- [Multi-Cluster Warehouses](https://docs.snowflake.com/en/user-guide/warehouses-multicluster) - Concurrency scaling and policies
- [Snowpark-Optimized Warehouses](https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized) - GPU-accelerated warehouse documentation
- [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) - Credit usage tracking and controls
- [Tag-Based Policies](https://docs.snowflake.com/en/user-guide/object-tagging) - Object tagging for governance and cost allocation
- [Warehouse Credit Usage](https://docs.snowflake.com/en/user-guide/credits) - Credit consumption and billing

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md` - Foundational Snowflake practices
- **SQL Demo Engineering**: `102-snowflake-sql-demo-engineering.md` - SQL patterns for demos
- **Performance Tuning**: `103-snowflake-performance-tuning.md` - Query profiling and optimization
- **Cost Governance**: `105-snowflake-cost-governance.md` - Resource monitors and cost optimization
- **Security Governance**: `107-snowflake-security-governance.md` - Tagging and access policies
- **Object Tagging**: `123-snowflake-object-tagging.md` - Comprehensive tagging patterns and governance
- **Observability**: `111-snowflake-observability.md` - Monitoring and telemetry

