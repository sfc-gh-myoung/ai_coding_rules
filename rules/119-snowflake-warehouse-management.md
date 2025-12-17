# Snowflake Warehouse Management

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** high-memory warehouse, warehouse tagging, auto-suspend, auto-resume, GEN 2, Snowpark-Optimized, warehouse edition, resource monitors, create warehouse, warehouse configuration, warehouse types, warehouse cost, size warehouse
**TokenBudget:** ~4800
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/103-snowflake-performance-tuning.md, rules/105-snowflake-cost-governance.md

## Purpose
Establish comprehensive best practices for creating, configuring, and managing Snowflake virtual warehouses, including proper selection of warehouse types (CPU/GPU/High-Memory), mandatory GEN 2 preference, sizing strategies, auto-suspend configuration, tagging standards, and cost governance integration.

## Rule Scope

Virtual warehouse creation, configuration, lifecycle management, type selection (Standard, Snowpark-Optimized, High-Memory), and cost optimization

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Always prefer GEN 2** - Use EDITION='GEN2' when available
- **Start small, scale up** - Begin with X-SMALL, monitor, then scale
- **Apply mandatory tags** - Cost tracking, ownership, environment tags
- **Configure auto-suspend** - 60-300 seconds for interactive, 0-10 for batch
- **Choose correct type** - Standard CPU, Snowpark-Optimized GPU, High-Memory
- **Associate resource monitors** - Prevent cost overruns
- **Never create without tags** - Required for governance

**Quick Checklist:**
- [ ] Workload type assessed
- [ ] Warehouse type selected (CPU/GPU/High-Memory)
- [ ] GEN 2 edition specified
- [ ] Size justified (start X-SMALL)
- [ ] Auto-suspend configured
- [ ] Mandatory tags applied
- [ ] Resource monitor associated

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~500 tokens (always load for warehouse tasks)
- + Warehouse Types & Sizing (sections 1-2): ~1300 tokens (load for creation)
- + Configuration & Governance (sections 3-4): ~2200 tokens (load for setup)
- + Complete Reference: ~2800 tokens (full warehouse guide)

**Recommended Loading Strategy:**
- **Quick warehouse check**: Quick Start only
- **Creating warehouse**: + Warehouse Types & Sizing
- **Full configuration**: + Configuration & Governance
- **Cost optimization**: Full reference + 105 (cost governance)

## Contract

<contract>
<inputs_prereqs>
Snowflake account with warehouse creation privileges (`CREATE WAREHOUSE`); workload requirements; cost baseline; resource monitor strategy
</inputs_prereqs>

<mandatory>
Snowflake DDL commands; warehouse configuration; SHOW/DESCRIBE commands; Query Profile analysis; resource monitors
</mandatory>

<forbidden>
Creating warehouses without mandatory tags; using Standard edition when GEN 2 available; oversized warehouses without documented justification; disabling auto-suspend in non-production
</forbidden>

<steps>
1. Assess workload type (interactive BI, batch ETL, ML training/inference, complex analytics)
2. Select appropriate warehouse type (Standard CPU, Snowpark-Optimized GPU, High-Memory)
3. Determine warehouse edition (ALWAYS prefer GEN 2 when available)
4. Size warehouse appropriately (start small, scale up based on metrics)
5. Configure auto-suspend and auto-resume settings
6. Apply mandatory tags for cost tracking and governance
7. Associate with resource monitors
8. Document sizing justification and expected workload patterns
9. Validate configuration and monitor usage patterns
</steps>

<output_format>
Complete DDL with inline comments; configuration tables; decision matrices; monitoring queries
</output_format>

<validation>
Warehouse created successfully; correct type and edition selected; mandatory tags applied; auto-suspend working as expected; resource monitor associated; initial query performance meets expectations
</validation>

<design_principles>
- **GEN 2 First:** Always prefer GEN 2 warehouses over Standard edition for improved performance and cost efficiency
- **Type Selection:** Use Standard CPU for general workloads, Snowpark-Optimized for GPU-accelerated ML, High-Memory for complex analytics
- **Start Small:** Begin with smaller sizes (XSMALL/SMALL) and scale up based on actual performance metrics
- **Auto-Suspend Always:** Enable auto-suspend on all warehouses with appropriate timeouts
- **Tag Everything:** Apply mandatory tags for cost allocation, governance, and lifecycle management
- **Cost Integration:** Every warehouse must be associated with a resource monitor
- **Monitor and Optimize:** Continuously review warehouse usage and right-size based on Query Profile data
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Starting with Oversized Warehouses**
```sql
-- Bad: Start with XLARGE without measuring workload
CREATE WAREHOUSE analytics_wh
  WAREHOUSE_SIZE = 'XLARGE'  -- 128 credits/hour!
  AUTO_SUSPEND = 600;
-- Costs 10x more than needed for actual workload
```
**Problem:** Massive unnecessary costs; 10x overspending; no baseline measurement; budget overruns; wasteful resource allocation; poor cost governance

**Correct Pattern:**
```sql
-- Good: Start XSMALL, measure, then scale up if needed
CREATE WAREHOUSE analytics_wh
  WAREHOUSE_SIZE = 'XSMALL'  -- 1 credit/hour
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

-- After measuring actual workload:
SELECT
  AVG(avg_running) as avg_concurrent_queries,
  MAX(avg_running) as peak_concurrent
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
WHERE warehouse_name = 'ANALYTICS_WH'
  AND start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP());

-- Scale up only if needed (avg > 8 concurrent queries)
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'SMALL';
```
**Benefits:** Start cost-effective; data-driven sizing; 10x cost savings; baseline established; justified upgrades; excellent cost governance


**Anti-Pattern 2: Not Enabling AUTO_SUSPEND**
```sql
-- Bad: No auto-suspend, warehouse runs 24/7
CREATE WAREHOUSE reporting_wh
  WAREHOUSE_SIZE = 'MEDIUM';
-- Costs: 16 credits/hour × 24 hours × 30 days = 11,520 credits/month!
-- Even if used only 2 hours/day!
```
**Problem:** 24/7 billing for sporadic usage; 10-100x unnecessary costs; idle compute waste; budget catastrophe; no automatic shutdown

**Correct Pattern:**
```sql
-- Good: Enable auto-suspend for idle shutdown
CREATE WAREHOUSE reporting_wh
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60          -- Suspend after 60 sec idle
  AUTO_RESUME = TRUE;        -- Auto-resume on query
-- Costs: 16 credits/hour × actual usage hours only
-- Example: 2 hours/day = 960 credits/month (92% savings!)
```
**Benefits:** Pay only for actual usage; 10-100x cost reduction; automatic idle shutdown; budget-friendly; production best practice; no manual management


**Anti-Pattern 3: Using Single Large Warehouse for All Workloads**
```sql
-- Bad: One mega-warehouse for everything
CREATE WAREHOUSE everything_wh
  WAREHOUSE_SIZE = 'XXLARGE';  -- 512 credits/hour

-- ETL, reporting, ad-hoc, ML all share same warehouse
-- Can't attribute costs, can't optimize per workload
```
**Problem:** No cost attribution; can't optimize per workload; resource contention; one workload affects others; poor governance; billing chaos

**Correct Pattern:**
```sql
-- Good: Separate warehouses by workload with proper tagging
CREATE WAREHOUSE etl_wh
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 300
  TAG (COST_CENTER = 'DATA_ENGINEERING', WORKLOAD_TYPE = 'ETL');

CREATE WAREHOUSE reporting_wh
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  TAG (COST_CENTER = 'ANALYTICS', WORKLOAD_TYPE = 'REPORTING');

CREATE WAREHOUSE adhoc_wh
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  TAG (COST_CENTER = 'ANALYTICS', WORKLOAD_TYPE = 'ADHOC');

-- Now query costs by workload/team
SELECT
  SYSTEM$GET_TAG('COST_CENTER', warehouse_name, 'WAREHOUSE') as cost_center,
  SYSTEM$GET_TAG('WORKLOAD_TYPE', warehouse_name, 'WAREHOUSE') as workload,
  SUM(credits_used) as total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('month', -1, CURRENT_TIMESTAMP())
GROUP BY cost_center, workload;
```
**Benefits:** Cost attribution by team/workload; independent optimization; no resource contention; chargeback-ready; governance-friendly; workload isolation


**Anti-Pattern 4: Not Using GEN 2 Warehouses**
```sql
-- Bad: Stuck on GEN 1 (default for old accounts)
CREATE WAREHOUSE old_wh
  WAREHOUSE_SIZE = 'MEDIUM';
-- RESOURCE_CONSTRAINT defaults to GEN 1 (slower, older architecture)
```
**Problem:** 2-3x slower query performance; higher costs per query; outdated architecture; missing performance optimizations; competitive disadvantage

**Correct Pattern:**
```sql
-- Good: Explicitly use GEN 2 for better performance
CREATE WAREHOUSE modern_wh
  WAREHOUSE_SIZE = 'MEDIUM'
  RESOURCE_CONSTRAINT = 'STANDARD_GEN_2';  -- Explicitly request GEN 2

-- Verify GEN 2 is active
SHOW WAREHOUSES LIKE 'modern_wh';
-- Check RESOURCE_CONSTRAINT column shows STANDARD_GEN_2

-- Migrate existing warehouse to GEN 2
ALTER WAREHOUSE old_wh SET RESOURCE_CONSTRAINT = 'STANDARD_GEN_2';
```
**Benefits:** 2-3x faster queries; lower cost per query; modern architecture; performance optimizations; competitive advantage; future-proof

## Post-Execution Checklist

**Provisioning:**
- [ ] Workload type assessed, appropriate warehouse type selected (Standard/GPU/High-Memory)
      Verify: Review workload requirements - check if GPU or high-memory needed
- [ ] GEN 2 edition used (`RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'`)
      Verify: `SHOW WAREHOUSES;` - check RESOURCE_CONSTRAINT column shows STANDARD_GEN_2
- [ ] Sized appropriately (started XSMALL/SMALL, scaled based on metrics)
      Verify: Query WAREHOUSE_METERING_HISTORY - check utilization before sizing up
- [ ] Auto-suspend configured (60-600 sec), auto-resume enabled
      Verify: `SHOW WAREHOUSES;` - check AUTO_SUSPEND and AUTO_RESUME columns
- [ ] All mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
      Verify: `SELECT SYSTEM$GET_TAG('COST_CENTER', 'WH_NAME', 'WAREHOUSE');` for each tag
- [ ] Resource monitor associated
      Verify: `SHOW RESOURCE MONITORS;` - check warehouse is listed
- [ ] Naming convention followed (`WH_[WORKLOAD]_[TYPE?]_[SIZE?]`)
      Verify: Check warehouse name matches pattern - e.g., WH_ANALYTICS_STANDARD_SMALL
- [ ] `INITIALLY_SUSPENDED = TRUE` set
      Verify: `SHOW WAREHOUSES;` - check warehouse state is SUSPENDED on creation
- [ ] Documented with business justification
      Verify: Check COMMENT on warehouse - should include business purpose

**Validation:**
- [ ] Warehouse created successfully, tags verified
- [ ] Auto-suspend working, Query Profile shows expected performance
- [ ] Cost tracking functional, monitoring queries configured

## Validation
- **Success Checks:** Warehouse created successfully with correct type and edition; all mandatory tags present; auto-suspend working as configured; resource monitor association verified; Query Profile shows expected performance; cost tracking functional in monitoring queries; warehouse appears in governance inventory
- **Negative Tests:** Creating warehouse without tags fails governance checks; oversized warehouse (XLARGE+) without documented justification triggers review; disabled auto-suspend in non-production raises alert; warehouse without resource monitor blocked or flagged; GPU warehouse used for standard SQL shows cost inefficiency; High-memory warehouse used without memory pressure evidence

> **Investigation Required**
> When applying this rule:
> 1. **Read existing warehouse configs BEFORE creating new ones** - Check naming conventions, sizing patterns, tag standards
> 2. **Verify GEN 2 availability** - Check account capabilities for warehouse editions
> 3. **Never assume warehouse size** - Query existing workloads to understand sizing needs
> 4. **Check resource monitors** - Review existing monitor associations and thresholds
> 5. **Test warehouse performance** - Run sample queries before full deployment
>
> **Anti-Pattern:**
> "Creating XLARGE warehouse... (without workload justification)"
> "Using Standard edition... (when GEN 2 available)"
>
> **Correct Pattern:**
> "Let me check your existing warehouse setup first."
> [reads SHOW WAREHOUSES, checks tags, reviews resource monitors]
> "I see you use GEN 2 with 5-minute auto-suspend. Creating new warehouse following this pattern..."

## Output Format Examples
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
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md` - SQL patterns for demos
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md` - Query profiling and optimization
- **Cost Governance**: `rules/105-snowflake-cost-governance.md` - Resource monitors and cost optimization
- **Security Governance**: `rules/107-snowflake-security-governance.md` - Tagging and access policies
- **Object Tagging**: `rules/123-snowflake-object-tagging.md` - Comprehensive tagging patterns and governance
- **Observability**: `rules/111-snowflake-observability-core.md` - Monitoring and telemetry

## 1. Warehouse Types and Resource Constraints

### 1.1 Resource Constraint Options (GEN 2 Mandate)

**Rule:** ALWAYS use `RESOURCE_CONSTRAINT = 'STANDARD_GEN_2'` for new standard warehouses when available (generally available in most AWS/Azure regions, Enterprise Edition+).

**Why GEN 2:** 20-30% better price-performance, ARM architecture, improved query optimization, better concurrency handling.

**Available Resource Constraints:**

- **Standard GEN 1 (`STANDARD_GEN_1`):** x86, Standard memory - Legacy/compatibility only
- **Standard GEN 2 (`STANDARD_GEN_2`):** ARM, Standard memory - **Default for all new warehouses**
- **High-Memory (`MEMORY_16X`):** ARM, 16X memory (256GB @ LARGE) - Memory-intensive queries (prove need first)
- **High-Memory x86 (`MEMORY_16X_x86`):** x86, 16X memory - x86-specific compatibility + memory
- **Snowpark GPU:** GPU, Standard memory - ML training, GPU UDFs (set WAREHOUSE_TYPE)

**Note:** Snowpark-Optimized uses `WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'` (GPU implicit, no RESOURCE_CONSTRAINT needed).

### 1.2 Warehouse Type Decision Matrix

**Warehouse Selection by Workload:**

- **General BI/Analytics:** Use Standard (CPU) - Dashboards, ad-hoc queries, reporting - Default for 80%+ of workloads
- **ML Training/Inference:** Use Snowpark-Optimized (GPU) - Model training, GPU UDFs, vector operations - Requires GPU-enabled features
- **Complex Aggregations:** Use High-Memory - Large window functions, complex joins on billions of rows - Use only when Standard shows memory pressure
- **ETL/Data Loading:** Use Standard (CPU) - COPY INTO, data transformation, pipelines - Size based on volume and SLAs
- **Streaming/Real-Time:** Use Standard (CPU) - Snowpipe, continuous ingestion, low-latency - Keep running or very short auto-suspend

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

- **XSMALL (1 credit/hr):** Single-user queries, testing, light dashboards - Dev/test, personal analytics
- **SMALL (2 credits/hr):** Small team BI, light ETL, scheduled reports - Team dashboards, nightly loads
- **MEDIUM (4 credits/hr):** Department-wide BI, moderate ETL, concurrent users - Production BI, daily ETL
- **LARGE (8 credits/hr):** Heavy ETL, complex queries, high concurrency - Enterprise dashboards
- **XLARGE (16 credits/hr):** Very large datasets, time-critical workloads - Critical ETL, real-time analytics
- **2X/3X/4XLARGE (32-128 credits/hr):** Massive parallel processing - Rare; requires executive approval

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

- **Interactive BI:** 300-600 sec (5-10 min) - Balance UX and cost
- **Batch ETL:** 60-120 sec (1-2 min) - Quick shutdown post-job
- **Dev/Test:** 60-180 sec (1-3 min) - Minimize dev costs
- **Streaming:** 60 sec (1 min) - Near-continuous use
- **ML Training:** 300-600 sec (5-10 min) - Interactive experimentation
- **24/7 Critical:** 600+ sec (10+ min) - Balance availability/cost

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

**Required:**
- **COST_CENTER** - Chargeback allocation (e.g., FINANCE, MARKETING, DATA_SCIENCE)
- **WORKLOAD_TYPE** - Workload categorization (e.g., BI_INTERACTIVE, ETL_BATCH, ML_TRAINING)
- **ENVIRONMENT** - Deployment stage (e.g., DEV, QA, PROD)
- **OWNER_TEAM** - Responsible team (e.g., DATA_ENGINEERING, ANALYTICS, BI_PLATFORM)

**Recommended:**
- **DATA_CLASSIFICATION** - Data sensitivity (e.g., PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
- **LIFECYCLE_STAGE** - Operational status (e.g., ACTIVE, DEPRECATED, EXPERIMENTAL)

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

**Key cost monitoring query (see `111-snowflake-observability-core.md` for complete monitoring suite):**
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

**Performance monitoring (detailed queries in `111-snowflake-observability-core.md`):**
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

## Related Rules

**Closely Related** (consider loading together):
- `105-snowflake-cost-governance` - For resource monitors, credit quotas, cost alerts
- `103-snowflake-performance-tuning` - For warehouse sizing decisions based on query performance

**Sometimes Related** (load if specific scenario):
- `120-snowflake-spcs` - When creating compute pools for Snowpark Container Services
- `122-snowflake-dynamic-tables` - When assigning warehouses to dynamic table refreshes
- `104-snowflake-streams-tasks` - When assigning warehouses to task executions

**Complementary** (different aspects of same domain):
- `100-snowflake-core` - For warehouse naming conventions
- `107-snowflake-security-governance` - For warehouse access control and RBAC
