---
schema_version: v4.0
rule_version: v5.0.0
description: Evidence-based model cost/access audits, compatibility gates, retention decisions, and approved production operations.
last_updated: 2026-10-07
keywords:
  - kw:model registry operations
  - kw:ML cost governance
  - kw:model version cleanup
  - kw:inference warehouse sizing
  - kw:model compliance audit
  - kw:cicd model validation
token_budget: ~1150
context_tier: Low
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 110-snowflake-model-registry.md  # Model Registry core patterns
  optional:
    - 105-snowflake-cost-governance.md  # Cost monitoring and governance
    - 119-snowflake-warehouse-management.md  # Warehouse sizing
---
# Snowflake Model Registry: Operations and Governance

## Scope

**What This Rule Covers:**
Model inventory/access/cost evidence, measured inference sizing, controlled version retirement, compatibility/evaluation gates and audit documentation.

**When to Load This Rule:**
When auditing registry operations, designing model CI/CD, tuning inference costs or reviewing model retention/compliance.

## Contract

### Inputs and Prerequisites

- Actual registry/version/service inventory, method signatures, production/default/alias references, model ownership and retention policy.
- Authorized model/usage/audit access, serving compute, baseline metrics, deployment gates, privacy and recovery requirements.

### Mandatory

- Inspect actual SHOW/DESCRIBE/API/usage schemas before administrative queries. Do not invent MODEL_VERSIONS fields or assume a metric's JSON path; model/version inventory and serving history have different grains.
- Account for model artifact storage, registration/management, warehouse inference, SPCS serving and monitoring costs. Resource monitors cover applicable warehouse spend, not every ML/SPCS service or a precise account hard cap.
- Right-size with actual model/input/batch/concurrency/profile evidence; no XS/S default or assertion most models run identically on XS and XL. Configure standard warehouse lifecycle within workload/approved policy.
- Use supported MODEL_SERVING_USAGE_HISTORY and relevant metering evidence for attribution, with scope/latency/estimation caveats. Regex over query text/cloud-service credits is not a reliable model-compute bill.
- Keep artifact packaging managed by supported Registry APIs. Do not manually compress internal artifacts or archive to an external host to save storage without authorized export and recovery support.
- Retirement requires actual serving/default/alias/consumer references, usage evidence, legal/recovery requirements and ownership. Last-altered date is not last-used date; a comment lacking PRODUCTION is not proof a version is disposable.
- Keep reviewed known-good versions and recovery metadata. Generate a candidate retirement report first; DROP VERSION/service/model and automatic cleanup schedules require specific approval and dependency review.
- Apply schema/method compatibility, independent holdout/business metrics, edge cases and regression tests before promotion. Use actual prediction column names/types and row/ID alignment, not predictions.columns[-1] or arbitrary universal accuracy thresholds.
- Prevent evaluation leakage and compare candidate/current versions on identical appropriate data, preprocessing and metrics. A model tagged approved or logged successfully has not passed inference/deployment gates.
- Version training/packaging/deployment scripts through existing project workflow; commits/pushes are separately authorized. CI has least-privilege scoped credentials and protected production promotion; notebook integration does not expand execution authority.
- Document actual purpose, owner, training/evaluation provenance, limitations, approval evidence and lifecycle status without sensitive metadata. Audit access/change records with exact identities and supported views; substring name matches can collide.
- Assign review/monitoring/remediation owners and cadence from risk. Keep monitoring/results and compliance review distinct; no invented governance board approval or guarantee that registry use meets regulations.
- All grants, monitor/warehouse creation, default/alias changes, retirement and external notifications are mutations requiring approved scope. Inspect uncertain outcomes before retry/recovery.

### Execution Steps

1. Inspect model/version/consumer inventory, actual metadata/usage schemas and current cost/access controls.
2. Prepare scoped cost/usage/access findings and candidate retention decisions with evidence and caveats.
3. Implement local CI/interface/evaluation tests and reviewed promotion/recovery gates without account mutation.
4. Under explicit execution approval, test deployed inference and apply approved lifecycle changes; verify effective version/access/result behavior.
5. Report measured outcomes, retained/retired identities and unverified gaps; preserve failures and unrelated versions.

### Validation

- Inventory/query fields and attribution grounded in actual schema; no last-altered-as-usage or regex-as-invoice assumptions.
- Tested signatures/predictions/data alignment and business gates precede approved promotion.
- Scoped cost controls and retirement preserve consumers/known-good recovery; no automatic age/comment-based DROP.
- Audit/approval metadata truthful, secrets protected, CI/notebook privileges bounded.
- Deliver operations queries/design, findings and actual validation limits without claiming unexecuted cleanup or compliance success.

## References

- [Model Registry overview and costs](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)
- [Model management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management)
- [MODEL_SERVING_USAGE_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/model_serving_usage_history)
- `110-snowflake-model-registry.md` for interface/registration requirements.
- `105-snowflake-cost-governance.md` for metering/control limitations.
