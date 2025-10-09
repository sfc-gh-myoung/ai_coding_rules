**Description:** Rules for managing and optimizing Snowflake costs, including resource monitors and workload right-sizing.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~250
**ContextTier:** High

# Snowflake Cost Governance

## Purpose
Establish comprehensive cost management and optimization strategies for Snowflake environments, including resource monitoring, warehouse right-sizing, and governance policies to control and predict cloud data warehouse spending.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake cost management, resource monitors, and credit usage optimization

## Contract
- **Inputs/Prereqs:** Snowflake account with ACCOUNTADMIN privileges; understanding of workload patterns; cost baseline
- **Allowed Tools:** Snowflake SQL commands; resource monitor configuration; warehouse management commands
- **Forbidden Tools:** Commands that create oversized warehouses without justification; disabling resource monitors
- **Required Steps:**
  1. Analyze workload patterns and resource usage
  2. Configure resource monitors with appropriate credit quotas
  3. Right-size warehouses based on workload requirements
  4. Implement auto-suspend and auto-resume settings
  5. Set up cost notification and alerting systems
- **Output Format:** SQL DDL for resource monitors; warehouse configuration commands; cost governance policies
- **Validation Steps:** Resource monitors active; credit usage within expected ranges; warehouses auto-suspend correctly

## Key Principles
- Treat cost as a first-class constraint; right-size warehouses; enable AUTO_SUSPEND.
- Use Resource Monitors and anomaly detection; set quotas and triggers.
- Reference official cost and monitor docs for setup.

## 1. Cost Optimization Principles
- **Requirement:** Treat cost as a primary design factor.
- **Always:** Follow comprehensive warehouse management practices in `119-snowflake-warehouse-management.md` for type selection, sizing, tagging, and configuration.
- **Requirement:** Verify all warehouses follow mandatory tagging and resource monitor association requirements.
- **Always:** Apply object tagging for cost attribution and chargeback. See `123-snowflake-object-tagging.md` for comprehensive tagging patterns and cost tracking queries.

## 2. Resource Management
- **Always:** Use Resource Monitors to track and control credit usage.
- **Always:** Create resource monitors with specific `CREDIT_QUOTA` and `TRIGGERS` to suspend or notify on thresholds.
- **Always:** Use Snowflake's anomaly detection features to monitor for unexpected credit spikes.

## Quick Compliance Checklist
- [ ] All warehouse creation follows `119-snowflake-warehouse-management.md` (type, size, tags, auto-suspend)
- [ ] Resource monitors created with appropriate credit quotas for account/warehouse level
- [ ] Notification triggers set at 75% and 90% of credit quota
- [ ] Suspend triggers configured at 100% of quota to prevent overruns
- [ ] Warehouses have mandatory tags applied (COST_CENTER, WORKLOAD_TYPE, ENVIRONMENT, OWNER_TEAM)
- [ ] Clustering keys applied only to tables with proven skew issues
- [ ] Time Travel retention period appropriate for data recovery needs (not default 1 day for all)
- [ ] Automatic scaling policies configured for variable workloads
- [ ] Cost monitoring dashboards and alerts configured
- [ ] Regular review process established for credit usage patterns

## Validation
- **Success Checks:** Resource monitors are active and tracking usage; warehouses suspend automatically after idle period; credit usage aligns with expectations; cost alerts trigger appropriately; warehouse sizes match workload requirements
- **Negative Tests:** Oversized warehouses fail cost review; missing resource monitors allow unchecked spending; disabled auto-suspend causes unnecessary credit consumption; inadequate monitoring misses cost spikes

## Response Template
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
- **Snowflake Core**: `100-snowflake-core.md`
- **Performance Tuning**: `103-snowflake-performance-tuning.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Object Tagging**: `123-snowflake-object-tagging.md`
- **Security Governance**: `107-snowflake-security-governance.md`
