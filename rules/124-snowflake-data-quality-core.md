---
schema_version: v4.0
rule_version: v5.0.0
description: "Data quality metric/expectation semantics, scoped associations and schedules, dedicated results, costs, and verified remediation."
last_updated: 2026-10-07
keywords:
  - kw:Data Metric Functions
  - kw:DMF expectations
  - kw:system DMF
  - kw:serverless quality monitoring
  - kw:quality event tables
  - kw:DMF scheduling patterns
  - kw:dmf
token_budget: ~1600
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 105-snowflake-cost-governance.md  # Resource monitors and cost optimization
    - 107-snowflake-security-governance.md  # Access control and security policies
  optional:
    - 124a-snowflake-data-quality-custom.md  # Custom DMF creation patterns
    - 124b-snowflake-data-quality-operations.md  # Operational patterns and remediation
---
# Snowflake Data Quality Monitoring Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Essential data quality contract; load for data quality tasks.

## Scope

**What This Rule Covers:**
Profiling, system/custom metric selection, expectation semantics, associations/access, scheduled evaluation/results, costs, and accountable remediation.

**When to Load This Rule:**
When designing or troubleshooting DMFs/data quality checks. Read `124a-snowflake-data-quality-custom.md` for custom functions and `124b-snowflake-data-quality-operations.md` for schedules/results/recovery.

## Contract

### Inputs and Prerequisites

- Exact supported objects/columns, business integrity/SLA, data population/NULL/time semantics, existing checks, and baseline profile.
- Enterprise+ and actual feature/account support, approved association/schedule/test scope, effective execution role and result-view privileges.
- Agreed metric units/thresholds, monitoring cadence, budget, notification content/recipients, and remediation owners.

### Mandatory

- Inspect existing DMFs/associations/schedules before creating anything; profile actual distribution through permitted Snowsight or bounded SQL. Define expectations from business rules and baseline, not guessed row counts/percentages or universal UI/warehouse requirements.
- Prefer appropriate system SNOWFLAKE.CORE metrics; custom checks need a distinct business requirement. DMF measures a scalar; expectation defines acceptable VALUE; notification/remediation is separate. A successful metric call is not proof a quality check passed.
- Verify current supported object kinds, association limit, sharing/reader/trial restrictions. Current docs allow 50000 associations/account, not the old 10000. DMFs cannot attach to tags, streams or hybrid tables, shared tables/views or reader-account objects; inspect current support before deployment.
- Associations require EXECUTE DATA METRIC FUNCTION on account, function USAGE, and supported object authority. Owner-role execution is default; documented EXECUTE AS ROLE with SELECT supports non-owner checks. Database roles cannot hold account execution privilege; ownership transfer is a separate approved governance change, not automatic repair.
- Custom DMFs use CREATE DATA METRIC FUNCTION, TABLE arguments, deterministic scalar SQL and RETURNS NUMBER. Python DMFs and mandatory FLOAT return claims are unsupported; ordinary Python UDFs are not interchangeable quality metrics.
- Match system metric signature/type/units: NULL_COUNT is a count, not a rate; rates require a defined denominator. FRESHNESS returns seconds and its column/no-column semantics/types differ; no minutes assumption or automatic TIMESTAMP_NTZ compatibility.
- Handle empty/all-NULL/no-change/future timestamps and tolerated missing values deliberately. Preserve unknown/no-data rather than coercing every NULL into pass/zero. Duplicate/unique counts must use documented NULL/composite-key behavior.
- Associate with ordered actual columns/table arguments using supported ALTER TABLE/VIEW or parenthesized WITH DATA METRIC FUNCTION on creation where supported. Replacement recreates bindings; IF NOT EXISTS does not retrofit them. Inspect existing associations after lifecycle changes.
- Use named EXPECTATION expressions on DMF associations with VALUE, supported Boolean comparisons/operators and actual boundary/units. Expressions cannot query tables/views/UDFs; compute percentage/range/business logic in a suitable metric instead of embedding a subquery or obsolete MODIFY DATA METRIC SCHEDULE EXPECT syntax.
- Set DATA_METRIC_SCHEDULE with documented intervals/cron/eligible TRIGGER_ON_CHANGES. All associated DMFs follow the object schedule unless suspended. Trigger semantics/object support and scheduling-change delay must be verified; reclustering is not a general trigger.
- Scheduled evaluations use serverless compute; manual testing/profiling has its own query cost. Track DATA_QUALITY_MONITORING_USAGE_HISTORY plus logging/storage/query overhead; warehouse monitors do not impose serverless credit ceilings.
- Results reside in dedicated SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS_RAW and supported flattened results/expectation-status views/functions, not the arbitrary account event table. Verify role-specific access models and schema; do not invent RECORD_TYPE=DATA_METRIC_FUNCTION or generic expectation_result fields.
- Use measurement_time versus scheduled_time deliberately, distinguish evaluation result from expectation violation and execution failure, and avoid duplicating one metric across multiple expectation rows. Inspect actual association/metric/object identities and latest result freshness.
- Test direct DMF values and supported expectation evaluation in approved isolated scope. Notification delivery, schema coverage and quality trends are separate gates; do not create alerts or send data externally by implication.
- Document issue ownership, severity/SLA, allowed quarantine/circuit-breaker/remediation, and recheck after source/schema changes. Quality failure does not authorize deleting rows, loosening expectations, removing masking or transferring ownership.

### Execution Steps

1. Read existing checks/objects/access and profile approved data; define quality requirement, metric population/units and expected edge behavior.
2. Select system/custom checks and named expectations; review supported associations/execution role, schedule, costs and recovery.
3. Apply only approved definitions/associations/settings and run permitted representative/boundary evaluation.
4. Inspect dedicated results/expectation status, evaluation errors/freshness, usage and authorized delivery; reconcile against independent known values.
5. Record coverage, outcomes, owner/remediation and remaining account/runtime gaps; refine thresholds only through business review.

### Validation

- Actual support/permissions, associations/roles, metric signatures/types/units and schedule are established.
- Values/expectations pass positive and boundary/empty/NULL cases; counts/rates and seconds/minutes are not conflated.
- Dedicated results are fresh/accessible, failure/no-data separate from violations, and multi-expectation joins do not inflate totals.
- Cost/alert/remediation boundaries are reviewed; no silent expected-loss tolerance or autonomous deletion/protection removal.
- Output includes checks/expectations, schedule/coverage, actual results, costs, owners and unresolved verification. Schema success alone is not quality correctness.

## References

- [Data quality support, limits, and costs](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [Associations and schedules](https://docs.snowflake.com/en/user-guide/data-quality-working)
- [Expectations and dedicated results](https://docs.snowflake.com/en/user-guide/data-quality-expectations)
- [Data quality access control](https://docs.snowflake.com/en/user-guide/data-quality-access-control)
- [CREATE DATA METRIC FUNCTION](https://docs.snowflake.com/en/sql-reference/sql/create-data-metric-function)
- [FRESHNESS units and types](https://docs.snowflake.com/en/sql-reference/functions/dmf_freshness)
