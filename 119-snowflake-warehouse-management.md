**Description:** Comprehensive best practices for Snowflake virtual warehouse creation, configuration, and management including CPU/GPU/High-Memory types, GEN 2 preference, sizing, tagging, and cost governance.
**AppliesTo:** `**/*.sql`, `**/*.scl`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-10-07

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

## 1. Warehouse Types and Selection Matrix

### 1.1 Warehouse Type Decision Matrix

| Workload Type | Warehouse Type | Use Cases | Notes |
|---------------|----------------|-----------|-------|
| **General BI/Analytics** | Standard (CPU) | Dashboards, ad-hoc queries, reporting, most SQL workloads | Default choice for 80%+ of workloads |
| **ML Training/Inference** | Snowpark-Optimized (GPU) | Snowpark ML model training, GPU-accelerated UDFs, vector operations | Requires GPU-enabled account features |
| **Complex Aggregations** | High-Memory | Large window functions, complex joins on billions of rows, memory-intensive analytics | Use only when Standard shows memory pressure |
| **ETL/Data Loading** | Standard (CPU) | COPY INTO, data transformation, incremental pipelines | Size based on data volume and SLAs |
| **Streaming/Real-Time** | Standard (CPU) | Snowpipe, continuous data ingestion, low-latency queries | Keep running or very short auto-suspend |

### 1.2 When to Use GPU (Snowpark-Optimized) Warehouses

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

### 1.3 When to Use High-Memory Warehouses

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
  WAREHOUSE_TYPE = 'STANDARD'  -- Type is STANDARD, size includes HIMEM
  WAREHOUSE_SIZE = 'LARGE_HIMEM'  -- High-memory variant
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

## 2. GEN 2 Warehouse Mandate

### 2.1 Always Prefer GEN 2

**Rule:** ALWAYS create new warehouses using GEN 2 edition when available in your Snowflake region and account type.

**Why GEN 2:**
- Better price-performance ratio (typically 20-30% improvement)
- Improved query optimization and execution
- Enhanced resource management
- Better handling of concurrent queries
- Reduced query queueing

**GEN 2 Availability:**
- Check regional availability: `SHOW REGIONS;`
- Enterprise Edition and higher accounts typically have GEN 2 access
- Use `WAREHOUSE_EDITION = 'GEN2'` parameter (upcoming/available based on account)

**Example GEN 2 Warehouse:**
```sql
-- GEN 2 warehouse creation (when explicitly settable)
CREATE OR REPLACE WAREHOUSE WH_BI_TOOLS_GEN2_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  -- WAREHOUSE_EDITION = 'GEN2'  -- Set explicitly when parameter available
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'GEN 2 warehouse for BI tools - improved price-performance';
```

**Note:** As of 2025, GEN 2 is increasingly the default for new warehouses in supported regions. Always verify your account's warehouse edition settings and explicitly request GEN 2 if options exist.

## 3. Warehouse Sizing Guidelines

### 3.1 Size Selection Strategy

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

### 3.2 Multi-Cluster Warehouses

**Use multi-cluster warehouses for:**
- High concurrency workloads (many users, same queries)
- BI tools with unpredictable concurrent users
- Production dashboards with variable traffic

**Configuration Pattern:**
```sql
-- Multi-cluster warehouse for BI concurrency
CREATE OR REPLACE WAREHOUSE WH_BI_PRODUCTION_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 5
  SCALING_POLICY = 'STANDARD'  -- Or 'ECONOMY' for less aggressive scaling
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Multi-cluster warehouse for production BI - scales 1-5 clusters based on queue depth';

-- Apply tags
ALTER WAREHOUSE WH_BI_PRODUCTION_M SET TAG
  COST_CENTER = 'BUSINESS_INTELLIGENCE',
  WORKLOAD_TYPE = 'BI_INTERACTIVE',
  ENVIRONMENT = 'PROD',
  OWNER_TEAM = 'BI_PLATFORM';
```

**Scaling Policy Selection:**
- **STANDARD:** Starts additional clusters immediately when query queue detected (favor performance)
- **ECONOMY:** Waits to start additional clusters (favor cost, tolerates brief queuing)

## 4. Auto-Suspend and Auto-Resume Configuration

### 4.1 Auto-Suspend Best Practices

**Rule:** ALWAYS enable auto-suspend on all warehouses. Never leave warehouses running indefinitely without documented business justification.

**Recommended Auto-Suspend Settings:**

| Workload Type | Auto-Suspend (seconds) | Rationale |
|---------------|------------------------|-----------|
| **Interactive BI/Dashboards** | 300-600 (5-10 min) | Balance between user experience and cost |
| **Scheduled ETL/Batch** | 60-120 (1-2 min) | Quick shutdown after job completion |
| **Development/Testing** | 60-180 (1-3 min) | Minimize cost during inactive periods |
| **Real-time/Streaming** | 60 (1 min) | Short timeout for near-continuous workloads |
| **ML Training (long jobs)** | 300-600 (5-10 min) | Accommodate interactive experimentation |
| **Production (24/7 critical)** | 600+ (10+ min) | Balance availability with cost control |

**Example Configurations:**
```sql
-- Interactive BI warehouse
CREATE OR REPLACE WAREHOUSE WH_INTERACTIVE_BI_M
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 300  -- 5 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Interactive BI warehouse - 5 min auto-suspend for user experience';

-- Batch ETL warehouse
CREATE OR REPLACE WAREHOUSE WH_ETL_BATCH_L
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60  -- 1 minute
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Batch ETL warehouse - aggressive 1 min auto-suspend for cost control';

-- Development warehouse
CREATE OR REPLACE WAREHOUSE WH_DEV_SANDBOX_XS
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 120  -- 2 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Development sandbox - 2 min auto-suspend to minimize dev costs';
```

### 4.2 Auto-Resume Configuration

**Rule:** ALWAYS set `AUTO_RESUME = TRUE` unless there's a specific reason to prevent automatic resumption.

**When to disable auto-resume (rare):**
- Deprecated warehouses being phased out
- Emergency cost control measures (prefer resource monitors instead)
- Warehouses requiring manual approval before use

## 5. Mandatory Tagging Standards

### 5.1 Required Tags for All Warehouses

**Rule:** EVERY warehouse MUST have the following tags applied for cost tracking, governance, and lifecycle management.

**Mandatory Tags:**

| Tag Name | Purpose | Example Values | Required |
|----------|---------|----------------|----------|
| **COST_CENTER** | Chargeback allocation | FINANCE, MARKETING, DATA_SCIENCE | ✅ Yes |
| **WORKLOAD_TYPE** | Workload categorization | BI_INTERACTIVE, ETL_BATCH, ML_TRAINING | ✅ Yes |
| **ENVIRONMENT** | Deployment stage | DEV, QA, PROD | ✅ Yes |
| **OWNER_TEAM** | Responsible team | DATA_ENGINEERING, ANALYTICS, BI_PLATFORM | ✅ Yes |
| **DATA_CLASSIFICATION** | Data sensitivity | PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED | Recommended |
| **LIFECYCLE_STAGE** | Operational status | ACTIVE, DEPRECATED, EXPERIMENTAL | Recommended |

### 5.2 Tag Creation and Application

**Create Tag Schema (one-time setup):**
```sql
-- Create governance schema for tags
CREATE SCHEMA IF NOT EXISTS GOVERNANCE.TAGS;

-- Create mandatory warehouse tags
CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.COST_CENTER
  ALLOWED_VALUES 'FINANCE', 'MARKETING', 'DATA_SCIENCE', 'ENGINEERING', 'OPERATIONS', 'SALES'
  COMMENT = 'Cost center for chargeback allocation';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.WORKLOAD_TYPE
  ALLOWED_VALUES 'BI_INTERACTIVE', 'BI_SCHEDULED', 'ETL_BATCH', 'ETL_STREAMING', 
                 'ML_TRAINING', 'ML_INFERENCE', 'ANALYTICS', 'DATA_LOADING', 'DEVELOPMENT'
  COMMENT = 'Workload type classification for optimization';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.ENVIRONMENT
  ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD'
  COMMENT = 'Deployment environment';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.OWNER_TEAM
  COMMENT = 'Team responsible for warehouse management and costs';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.DATA_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
  COMMENT = 'Highest data classification level processed';

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.LIFECYCLE_STAGE
  ALLOWED_VALUES 'ACTIVE', 'DEPRECATED', 'EXPERIMENTAL', 'DECOMMISSIONED'
  COMMENT = 'Operational lifecycle stage';
```

**Apply Tags to Warehouses:**
```sql
-- Complete warehouse creation with tagging
CREATE OR REPLACE WAREHOUSE WH_MARKETING_ANALYTICS_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Marketing analytics warehouse for campaign reporting and attribution';

-- Apply all mandatory tags
ALTER WAREHOUSE WH_MARKETING_ANALYTICS_M SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'MARKETING',
  GOVERNANCE.TAGS.WORKLOAD_TYPE = 'BI_INTERACTIVE',
  GOVERNANCE.TAGS.ENVIRONMENT = 'PROD',
  GOVERNANCE.TAGS.OWNER_TEAM = 'MARKETING_ANALYTICS',
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL',
  GOVERNANCE.TAGS.LIFECYCLE_STAGE = 'ACTIVE';
```

### 5.3 Tag Validation Query

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

## 6. Cost Governance and Resource Monitor Integration

### 6.1 Resource Monitor Association

**Rule:** EVERY production warehouse MUST be associated with a resource monitor. Development warehouses SHOULD have monitors with appropriate quotas.

**Resource Monitor Strategy:**
```sql
-- Account-level resource monitor (safety net)
CREATE RESOURCE MONITOR IF NOT EXISTS RM_ACCOUNT_MONTHLY
  WITH CREDIT_QUOTA = 50000  -- Adjust based on contract
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS 
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- Set account-level monitor
ALTER ACCOUNT SET RESOURCE_MONITOR = RM_ACCOUNT_MONTHLY;

-- Workload-specific monitors
CREATE RESOURCE MONITOR IF NOT EXISTS RM_BI_WORKLOADS
  WITH CREDIT_QUOTA = 5000
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS 
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

CREATE RESOURCE MONITOR IF NOT EXISTS RM_DEV_WORKLOADS
  WITH CREDIT_QUOTA = 500
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS 
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND_IMMEDIATE;  -- Aggressive for dev

CREATE RESOURCE MONITOR IF NOT EXISTS RM_ML_WORKLOADS
  WITH CREDIT_QUOTA = 3000
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS 
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- Associate warehouses with monitors
ALTER WAREHOUSE WH_BI_PRODUCTION_M SET RESOURCE_MONITOR = RM_BI_WORKLOADS;
ALTER WAREHOUSE WH_DEV_SANDBOX_XS SET RESOURCE_MONITOR = RM_DEV_WORKLOADS;
ALTER WAREHOUSE WH_ML_TRAINING_GPU_M SET RESOURCE_MONITOR = RM_ML_WORKLOADS;
```

### 6.2 Cost Monitoring Queries

**Daily warehouse cost tracking:**
```sql
-- Daily warehouse costs (last 30 days)
SELECT 
  warehouse_name,
  DATE_TRUNC('day', start_time) AS usage_date,
  SUM(credits_used) AS daily_credits,
  COUNT(DISTINCT query_id) AS query_count,
  AVG(execution_time) / 1000 AS avg_execution_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name, DATE_TRUNC('day', start_time)
ORDER BY warehouse_name, usage_date DESC;

-- Warehouse efficiency analysis
SELECT 
  warehouse_name,
  SUM(credits_used) AS total_credits,
  SUM(credits_used_compute) AS compute_credits,
  SUM(credits_used_cloud_services) AS cloud_services_credits,
  ROUND(SUM(credits_used_cloud_services) / NULLIF(SUM(credits_used), 0) * 100, 2) AS cloud_services_pct,
  COUNT(DISTINCT DATE_TRUNC('day', start_time)) AS active_days
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;

-- Identify idle or underutilized warehouses
SELECT 
  w.name AS warehouse_name,
  w.size,
  w.auto_suspend,
  COALESCE(SUM(wm.credits_used), 0) AS credits_last_30d,
  COALESCE(COUNT(DISTINCT wm.query_id), 0) AS queries_last_30d,
  DATEDIFF(day, MAX(wm.start_time), CURRENT_TIMESTAMP()) AS days_since_last_use
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES w
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
  ON wm.warehouse_name = w.name
  AND wm.start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
WHERE w.deleted IS NULL
GROUP BY w.name, w.size, w.auto_suspend
HAVING credits_last_30d < 10 OR queries_last_30d < 100
ORDER BY days_since_last_use DESC;
```

## 7. Warehouse Naming Conventions

**Rule:** Follow consistent naming pattern: `WH_[WORKLOAD]_[TYPE?]_[SIZE?]`

**Pattern Components:**
- **Prefix:** Always `WH_` to group warehouses in object explorers
- **Workload:** Descriptive name (MARKETING, ETL, ML_TRAINING, BI_TOOLS)
- **Type (optional):** GPU, HIMEM for non-standard types
- **Size (optional):** S, M, L, XL suffix when multiple sizes exist

**Examples:**
- `WH_MARKETING_M` - Marketing team warehouse, Medium
- `WH_ETL_BATCH_L` - ETL batch processing, Large
- `WH_ML_TRAINING_GPU_M` - ML training with GPU, Medium
- `WH_ANALYTICS_HIMEM_XL` - High-memory analytics, XLarge
- `WH_BI_TOOLS` - BI tools warehouse (size may vary with multi-cluster)
- `WH_DEV_SANDBOX_XS` - Development sandbox, XSmall

## 8. Query Monitoring and Performance Optimization

### 8.1 Warehouse Performance Monitoring

**Monitor these key metrics:**
```sql
-- Warehouse queue depth and performance
SELECT 
  warehouse_name,
  DATE_TRUNC('hour', start_time) AS hour,
  COUNT(*) AS query_count,
  AVG(queued_overload_time) / 1000 AS avg_queue_seconds,
  MAX(queued_overload_time) / 1000 AS max_queue_seconds,
  AVG(execution_time) / 1000 AS avg_execution_seconds,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time) / 1000 AS p95_execution_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
  AND warehouse_name IS NOT NULL
GROUP BY warehouse_name, DATE_TRUNC('hour', start_time)
HAVING AVG(queued_overload_time) > 0  -- Show only when queueing occurred
ORDER BY warehouse_name, hour DESC;

-- Identify queries that would benefit from larger warehouse
SELECT 
  query_id,
  query_text,
  warehouse_name,
  warehouse_size,
  total_elapsed_time / 1000 AS elapsed_seconds,
  execution_time / 1000 AS execution_seconds,
  bytes_scanned / POWER(1024, 3) AS gb_scanned,
  partitions_scanned,
  partitions_total,
  ROUND(partitions_scanned / NULLIF(partitions_total, 0) * 100, 2) AS pruning_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND execution_time > 60000  -- Over 1 minute
  AND warehouse_name IS NOT NULL
ORDER BY execution_time DESC
LIMIT 100;
```

### 8.2 Right-Sizing Recommendations

**When to scale UP:**
- Consistent query queueing (queued_overload_time > 0)
- P95 execution time exceeds business requirements
- Critical queries missing SLA targets
- Query Profile shows good pruning but long execution

**When to scale DOWN:**
- Average utilization consistently < 30%
- Queries complete well within SLA targets
- No queueing in past 30 days
- Cost optimization initiative without performance impact

**When to use Multi-Cluster:**
- Concurrency issues but individual queries are fast
- Same queries run by many users simultaneously
- BI tool query patterns with unpredictable peaks

## 9. Warehouse Lifecycle Management

### 9.1 Warehouse Provisioning Checklist

- [ ] Workload type assessed and documented
- [ ] Appropriate warehouse type selected (Standard/GPU/High-Memory)
- [ ] GEN 2 edition verified and used
- [ ] Starting size determined (prefer XSMALL/SMALL)
- [ ] Auto-suspend configured (60-600 seconds based on workload)
- [ ] Auto-resume enabled (TRUE in most cases)
- [ ] All mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
- [ ] Resource monitor associated
- [ ] Warehouse documented in inventory/wiki
- [ ] Cost baseline and budget allocated
- [ ] Monitoring alerts configured
- [ ] Initial performance validation completed

### 9.2 Warehouse Decommissioning Process

**Steps to decommission a warehouse:**
```sql
-- 1. Mark as deprecated
ALTER WAREHOUSE WH_OLD_WAREHOUSE SET TAG
  GOVERNANCE.TAGS.LIFECYCLE_STAGE = 'DEPRECATED';

-- 2. Notify users and redirect workloads
UPDATE GOVERNANCE.WAREHOUSE_INVENTORY
SET status = 'DEPRECATED',
    deprecation_date = CURRENT_TIMESTAMP(),
    replacement_warehouse = 'WH_NEW_WAREHOUSE',
    decommission_target_date = DATEADD(day, 30, CURRENT_TIMESTAMP())
WHERE warehouse_name = 'WH_OLD_WAREHOUSE';

-- 3. Disable auto-resume (prevent accidental use)
ALTER WAREHOUSE WH_OLD_WAREHOUSE SET AUTO_RESUME = FALSE;

-- 4. After grace period, suspend and verify no usage
ALTER WAREHOUSE WH_OLD_WAREHOUSE SUSPEND;

-- 5. Monitor for any attempted usage
SELECT 
  query_id,
  user_name,
  role_name,
  start_time,
  query_text
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE warehouse_name = 'WH_OLD_WAREHOUSE'
  AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

-- 6. Final decommission after confirming zero usage
DROP WAREHOUSE IF EXISTS WH_OLD_WAREHOUSE;
```

## Quick Compliance Checklist
- [ ] Warehouse type appropriately selected (Standard CPU / GPU / High-Memory)
- [ ] GEN 2 edition preferred and used when available
- [ ] Warehouse sized appropriately (started small, scaled based on metrics)
- [ ] Auto-suspend configured (60-600 seconds, never disabled without justification)
- [ ] Auto-resume enabled (TRUE unless specific reason)
- [ ] All mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
- [ ] Resource monitor associated with warehouse
- [ ] Naming convention followed (WH_[WORKLOAD]_[TYPE?]_[SIZE?])
- [ ] INITIALLY_SUSPENDED = TRUE set for new warehouses
- [ ] Multi-cluster settings appropriate for concurrency needs
- [ ] Warehouse documented with business justification and expected workload
- [ ] Performance monitoring queries configured and reviewed regularly

## Validation
- **Success Checks:** Warehouse created successfully with correct type and edition; all mandatory tags present; auto-suspend working as configured; resource monitor association verified; Query Profile shows expected performance; cost tracking functional in monitoring queries; warehouse appears in governance inventory
- **Negative Tests:** Creating warehouse without tags fails governance checks; oversized warehouse (XLARGE+) without documented justification triggers review; disabled auto-suspend in non-production raises alert; warehouse without resource monitor blocked or flagged; GPU warehouse used for standard SQL shows cost inefficiency; High-memory warehouse used without memory pressure evidence

## Response Template
```sql
-- Standard CPU warehouse for BI workloads (GEN 2)
CREATE OR REPLACE WAREHOUSE WH_[WORKLOAD]_M
  WAREHOUSE_TYPE = 'STANDARD'
  WAREHOUSE_SIZE = 'MEDIUM'
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
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md` - SQL optimization patterns
- **Performance Tuning**: `103-snowflake-performance-tuning.md` - Query profiling and optimization
- **Cost Governance**: `105-snowflake-cost-governance.md` - Resource monitors and cost optimization
- **Security Governance**: `107-snowflake-security-governance.md` - Tagging and access policies
- **Observability**: `111-snowflake-observability.md` - Monitoring and telemetry

