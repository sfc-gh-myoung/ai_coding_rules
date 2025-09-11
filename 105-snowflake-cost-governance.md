**Description:** Rules for managing and optimizing Snowflake costs, including resource monitors and workload right-sizing.
**AppliesTo:** `**/*.sql`
**AutoAttach:** false
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake Cost Governance

## TL;DR
- Treat cost as a first-class constraint; right-size warehouses; enable AUTO_SUSPEND.
- Use Resource Monitors and anomaly detection; set quotas and triggers.
- Reference official cost and monitor docs for setup.

## 1. Cost Optimization Principles
- **Requirement:** Treat cost as a primary design factor.
- **Always:** Right-size virtual warehouses based on workload type (smaller for concurrency, larger for performance-critical jobs).
- **Requirement:** Enable `AUTO_SUSPEND` on all virtual warehouses.

## 2. Resource Management
- **Always:** Use Resource Monitors to track and control credit usage.
- **Always:** Create resource monitors with specific `CREDIT_QUOTA` and `TRIGGERS` to suspend or notify on thresholds.
- **Always:** Use Snowflake's anomaly detection features to monitor for unexpected credit spikes.

## 3. Documentation
- **Always:** Reference the official documentation:
  - **Cost Management**: https://docs.snowflake.com/en/guides-overview-cost
  - **Resource Monitors**: https://docs.snowflake.com/en/user-guide/resource-monitors
