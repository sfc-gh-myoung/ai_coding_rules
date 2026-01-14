# Snowflake Cost Governance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** budget alerts, spend tracking, Snowflake, SQL, CREDIT_QUOTA, WAREHOUSE_METERING_HISTORY, object tagging, monitor credits, warehouse spending, cost alerts, credit limits, budget management, resource monitor, tag enforcement
**TokenBudget:** ~1900
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Comprehensive cost management and optimization strategies for Snowflake environments, including resource monitoring, warehouse right-sizing, and governance policies to control and predict cloud data warehouse spending.

**When to Load This Rule:**
- Setting up resource monitors and budget alerts
- Tracking Snowflake credit usage and costs
- Optimizing warehouse spending
- Implementing cost governance policies
- Analyzing cost trends and anomalies

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **100-snowflake-core.md** - Snowflake SQL patterns and best practices

### External Documentation
- [Cost Management Guide](https://docs.snowflake.com/en/guides-overview-cost) - Comprehensive cost optimization strategies and monitoring
- [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) - Credit usage tracking, quotas, and automated controls

### Related Rules

**Closely Related** (consider loading together):
- **119-snowflake-warehouse-management.md** - Warehouse sizing, auto-suspend config affecting costs
- **103-snowflake-performance-tuning.md** - Optimizing queries to reduce compute costs

**Sometimes Related** (load if specific scenario):
- **111-snowflake-observability-core.md** - Monitoring warehouse usage and query costs via telemetry
- **106c-snowflake-semantic-views-integration.md** - Monitoring Cortex Analyst API costs
- **115-snowflake-cortex-agents-core.md** - Monitoring agent execution costs

**Complementary** (different aspects of same domain):
- **100-snowflake-core.md** - Tagging conventions (COST_CENTER, WORKLOAD_TYPE, OWNER_TEAM)
- **107-snowflake-security-governance.md** - RBAC on resource monitors and cost controls
- **123-snowflake-object-tagging.md** - Object tagging for cost tracking

## Contract

### Inputs and Prerequisites

Snowflake account with ACCOUNTADMIN privileges; understanding of workload patterns; cost baseline

### Mandatory

Snowflake SQL commands; resource monitor configuration; warehouse management commands

### Forbidden

Commands that create oversized warehouses without justification; disabling resource monitors

### Execution Steps

1. Analyze workload patterns and resource usage
2. Configure resource monitors with appropriate credit quotas
3. Right-size warehouses based on workload requirements
4. Implement auto-suspend and auto-resume settings
5. Set up cost notification and alerting systems

### Output Format

SQL DDL for resource monitors; warehouse configuration commands; cost governance policies

### Validation

Resource monitors active; credit usage within expected ranges; warehouses auto-suspend correctly

### Design Principles

- Treat cost as a first-class constraint; right-size warehouses; enable AUTO_SUSPEND.
- Use Resource Monitors and anomaly detection; set quotas and triggers.
- Reference official cost and monitor docs for setup.

### Post-Execution Checklist

- [ ] All warehouse creation follows `119-snowflake-warehouse-management.md` (type, size, tags, auto-suspend)
      Verify: `SHOW WAREHOUSES;` - check all required fields match 119 standards
- [ ] Resource monitors created with appropriate credit quotas for account/warehouse level
      Verify: `SHOW RESOURCE MONITORS;` - check credit limits align with budget
- [ ] Notification triggers set at 75% and 90% of credit quota
      Verify: Check resource monitor config - should have NOTIFY_AT = 75, 90
- [ ] Suspend triggers configured at 100% of quota to prevent overruns
      Verify: Check resource monitor has SUSPEND_AT = 100 or SUSPEND_IMMEDIATE_AT = 100
- [ ] Warehouses have mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
      Verify: Query SYSTEM$GET_TAG for each warehouse - all 4 tags should return values
- [ ] Clustering keys applied only to tables with proven skew issues
      Verify: `SHOW CLUSTERING KEYS;` - verify each has documented skew analysis
- [ ] Time Travel retention period appropriate for data recovery needs (not default 1 day for all)
      Verify: `SHOW TABLES;` - check DATA_RETENTION_TIME_IN_DAYS varies by criticality
- [ ] Automatic scaling policies configured for variable workloads
      Verify: Check warehouse MIN_CLUSTER_COUNT and MAX_CLUSTER_COUNT settings
- [ ] Cost monitoring dashboards and alerts configured
      Verify: Query WAREHOUSE_METERING_HISTORY - ensure dashboards exist and refresh
- [ ] Regular review process established for credit usage patterns
      Verify: Check for scheduled queries/tasks that report on usage trends

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Unbounded Warehouses Without Resource Monitors

**Problem:** Creating warehouses without associating them with resource monitors, allowing unlimited credit consumption.

**Why It Fails:** A single runaway query or misconfigured pipeline can consume thousands of credits in hours. Without monitors, there's no automatic suspension or alerting, leading to bill shock at month-end.

**Correct Pattern:**
```sql
-- BAD: Warehouse without resource monitor
CREATE WAREHOUSE WH_ETL_XL WAREHOUSE_SIZE = 'X-LARGE';
-- No credit limits, no alerts, no automatic suspension

-- GOOD: Always associate with resource monitor
CREATE RESOURCE MONITOR rm_etl_daily
  WITH CREDIT_QUOTA = 100 FREQUENCY = DAILY
  TRIGGERS ON 75 PERCENT DO NOTIFY
           ON 90 PERCENT DO NOTIFY
           ON 100 PERCENT DO SUSPEND;

CREATE WAREHOUSE WH_ETL_XL WAREHOUSE_SIZE = 'X-LARGE'
  RESOURCE_MONITOR = rm_etl_daily
  AUTO_SUSPEND = 60;
```

### Anti-Pattern 2: Oversized Warehouses as Default

**Problem:** Starting with X-Large or larger warehouses "to be safe" instead of right-sizing based on actual workload needs.

**Why It Fails:** Larger warehouses cost exponentially more (4X-Large = 128 credits/hour vs X-Small = 1 credit/hour). Most workloads don't benefit from oversizing; query performance often depends on data clustering and query design, not raw compute.

**Correct Pattern:**
```sql
-- BAD: Starting large without justification
CREATE WAREHOUSE WH_REPORTS WAREHOUSE_SIZE = '2X-LARGE';
-- 64 credits/hour for queries that might run fine on SMALL

-- GOOD: Start small, scale based on evidence
CREATE WAREHOUSE WH_REPORTS WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

-- Monitor query performance, scale up only if:
-- 1. Query queue times > 30 seconds consistently
-- 2. QUERY_HISTORY shows spillage to remote storage
-- 3. Workload analysis justifies larger size
```

## Output Format Examples
```sql
-- Resource Monitor Setup
CREATE RESOURCE MONITOR IF NOT EXISTS rm_analytics_monthly
  WITH CREDIT_QUOTA = 5000
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- For warehouse creation with tagging and resource monitors,
-- see complete examples in 119-snowflake-warehouse-management.md

-- Apply monitor to existing warehouse
ALTER WAREHOUSE WH_ANALYTICS_M SET RESOURCE_MONITOR = rm_analytics_monthly;
```

## Cost Optimization Principles
- **Requirement:** Treat cost as a primary design factor.
- **Always:** Follow comprehensive warehouse management practices in `119-snowflake-warehouse-management.md` for type selection, sizing, tagging, and configuration.
- **Requirement:** Verify all warehouses follow mandatory tagging and resource monitor association requirements.
- **Always:** Apply object tagging for cost attribution and chargeback. See `123-snowflake-object-tagging.md` for comprehensive tagging patterns and cost tracking queries.

## Resource Management
- **Always:** Use Resource Monitors to track and control credit usage.
- **Always:** Create resource monitors with specific `CREDIT_QUOTA` and `TRIGGERS` to suspend or notify on thresholds.
- **Always:** Use Snowflake's anomaly detection features to monitor for unexpected credit spikes.
