# Snowflake Cost Governance

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** budget alerts, spend tracking, Snowflake, SQL, CREDIT_QUOTA, WAREHOUSE_METERING_HISTORY, object tagging, monitor credits, warehouse spending, cost alerts, credit limits, budget management, resource monitor, tag enforcement
**TokenBudget:** ~1700
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Establish comprehensive cost management and optimization strategies for Snowflake environments, including resource monitoring, warehouse right-sizing, and governance policies to control and predict cloud data warehouse spending.

## Rule Scope

Snowflake cost management, resource monitors, and credit usage optimization

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Create Resource Monitors** - set CREDIT_QUOTA and TRIGGERS (75%, 90%, 100%)
- **Right-size warehouses:** Follow 119-snowflake-warehouse-management.md sizing guidance
- **Enable AUTO_SUSPEND** - prevent idle warehouse costs (suspend after 60 seconds of inactivity)
- **Apply object tagging:** Use 123-snowflake-object-tagging.md for cost attribution
- **Set up cost alerts:** Notify at 75%, 90%; suspend at 100% of quota
- **Monitor credit usage:** Check WAREHOUSE_METERING_HISTORY regularly
- **Don't create oversized warehouses** - start small, scale up if needed

**Quick Checklist:**
- [ ] CREATE RESOURCE MONITOR with CREDIT_QUOTA
- [ ] Set TRIGGERS: 75% NOTIFY, 90% NOTIFY, 100% SUSPEND
- [ ] Apply monitor to warehouse: ALTER WAREHOUSE SET RESOURCE_MONITOR
- [ ] Verify AUTO_SUSPEND enabled (60-300 seconds)
- [ ] Apply mandatory tags (COST_CENTER, WORKLOAD_TYPE, OWNER_TEAM)
- [ ] Review credit usage: SELECT * FROM WAREHOUSE_METERING_HISTORY
- [ ] Set up cost dashboards and alerts

> **Investigation Required**
> When applying this rule:
> 1. Query WAREHOUSE_METERING_HISTORY to review current credit usage BEFORE making recommendations
> 2. Verify existing resource monitors and quotas
> 3. Never speculate about cost issues - check actual credit consumption
> 4. Review warehouse auto-suspend settings in SHOW WAREHOUSES
> 5. Make grounded recommendations based on investigated usage patterns

## Contract

<contract>
<inputs_prereqs>
Snowflake account with ACCOUNTADMIN privileges; understanding of workload patterns; cost baseline
</inputs_prereqs>

<mandatory>
Snowflake SQL commands; resource monitor configuration; warehouse management commands
</mandatory>

<forbidden>
Commands that create oversized warehouses without justification; disabling resource monitors
</forbidden>

<steps>
1. Analyze workload patterns and resource usage
2. Configure resource monitors with appropriate credit quotas
3. Right-size warehouses based on workload requirements
4. Implement auto-suspend and auto-resume settings
5. Set up cost notification and alerting systems
</steps>

<output_format>
SQL DDL for resource monitors; warehouse configuration commands; cost governance policies
</output_format>

<validation>
Resource monitors active; credit usage within expected ranges; warehouses auto-suspend correctly
</validation>

<design_principles>
- Treat cost as a first-class constraint; right-size warehouses; enable AUTO_SUSPEND.
- Use Resource Monitors and anomaly detection; set quotas and triggers.
- Reference official cost and monitor docs for setup.
</design_principles>

</contract>

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

## Post-Execution Checklist
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

## Validation
- **Success Checks:** Resource monitors are active and tracking usage; warehouses suspend automatically after idle period; credit usage aligns with expectations; cost alerts trigger appropriately; warehouse sizes match workload requirements
- **Negative Tests:** Oversized warehouses fail cost review; missing resource monitors allow unchecked spending; disabled auto-suspend causes unnecessary credit consumption; inadequate monitoring misses cost spikes

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

## References

### External Documentation
- [Cost Management Guide](https://docs.snowflake.com/en/guides-overview-cost) - Comprehensive cost optimization strategies and monitoring
- [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) - Credit usage tracking, quotas, and automated controls

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Object Tagging**: `rules/123-snowflake-object-tagging.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`

## 1. Cost Optimization Principles
- **Requirement:** Treat cost as a primary design factor.
- **Always:** Follow comprehensive warehouse management practices in `119-snowflake-warehouse-management.md` for type selection, sizing, tagging, and configuration.
- **Requirement:** Verify all warehouses follow mandatory tagging and resource monitor association requirements.
- **Always:** Apply object tagging for cost attribution and chargeback. See `123-snowflake-object-tagging.md` for comprehensive tagging patterns and cost tracking queries.

## 2. Resource Management
- **Always:** Use Resource Monitors to track and control credit usage.
- **Always:** Create resource monitors with specific `CREDIT_QUOTA` and `TRIGGERS` to suspend or notify on thresholds.
- **Always:** Use Snowflake's anomaly detection features to monitor for unexpected credit spikes.

## Related Rules

**Closely Related** (consider loading together):
- `119-snowflake-warehouse-management` - For warehouse sizing, auto-suspend config affecting costs
- `103-snowflake-performance-tuning` - For optimizing queries to reduce compute costs

**Sometimes Related** (load if specific scenario):
- `111-snowflake-observability-core` - When monitoring warehouse usage and query costs via telemetry
- `106c-snowflake-semantic-views-integration` - When monitoring Cortex Analyst API costs
- `115-snowflake-cortex-agents-core` - When monitoring agent execution costs

**Complementary** (different aspects of same domain):
- `100-snowflake-core` - For tagging conventions (COST_CENTER, WORKLOAD_TYPE, OWNER_TEAM)
- `107-snowflake-security-governance` - For RBAC on resource monitors and cost controls
