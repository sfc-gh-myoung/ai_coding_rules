---
schema_version: v4.0
rule_version: v5.0.0
description: Schema- and time-grounded feature entities/views, reproducible dataset generation, managed refresh, and model lineage governance.
last_updated: 2026-10-07
keywords:
  - kw:feature store
  - kw:point-in-time correctness
  - kw:feature view versioning
  - kw:entity modeling
  - kw:ASOF JOIN
  - kw:ml lineage integration
  - kw:rbac
token_budget: ~1300
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 110-snowflake-model-registry.md  # Model Registry integration patterns
  optional:
    - 122-snowflake-dynamic-tables.md  # Dynamic Tables for feature views
---
# Snowflake Feature Store Best Practices

## Scope

**What This Rule Covers:**
Feature-store identity, entity keys, managed/external views, temporal dataset construction, versions, access, refresh costs and model integration.

**When to Load This Rule:**
When implementing/reviewing Feature Store entities/views, training/inference retrieval, lineage or governance.

## Contract

### Inputs and Prerequisites

- Actual sources/schema, entity/grain keys, time/availability semantics, training labels/spine, feature definitions and serving freshness needs.
- Installed snowflake-ml-python APIs, current account support/privileges, existing store/views/versions and approved creation/data/compute scope.

### Mandatory

- Inspect existing store and source before registration. A store is a schema, entities are tags, features are columns in dynamic tables/views; SQL changes can affect Python-managed objects. Do not create/delete an entire schema by inference from a feature-store name.
- Use supported FeatureStore constructor/database/name/default_warehouse/CreationMode behavior. Connect to existing store without implicit creation when scope is read-only; inspect mode rather than invent schema arguments or string enums.
- Register supported Entity objects with stable complete join_keys before associated views; verify key existence/types/uniqueness at intended grain. Entity key changes require a reviewed new entity, not silent mutation or fuzzy email matching.
- Define FeatureView with actual Snowpark transformation DataFrame and all entity keys. Time-series views need a timestamp column; declared timestamps alone do not prove historical availability or leakage prevention.
- Managed views specify refresh_freq and use dynamic tables; external views use no managed refresh frequency and an externally maintained feature table. block=False changes waiting behavior, not managed versus external classification.
- Verify dynamic-table query/change-tracking/refresh-mode support and ownership effects. Full refresh may occur for unsupported incremental shapes; registration is not permission to change tracking on unowned sources or guarantee cheap incremental refresh.
- Centralize reusable versioned logic, document business meanings, units, time windows, NULL handling and owner. Exploratory notebook calculations can be valid; promote shared production logic through reviewed definitions rather than prohibit all ad-hoc work.
- Build datasets with supported retrieval/generation APIs and explicit selected registered versions/spine/labels. Do not invent decorators, generate_training_set signatures or feature strings from examples; inspect installed API contracts.
- For temporal training, use appropriate spine time and feature historical timestamp/availability logic with validated ASOF or equivalent semantics. Static features need not force ASOF; future data, equal-time ties, late arrivals, key fanout and missing coverage require tests.
- Preserve training/serving preprocessing, feature ordering/types/time zones and version identity. Current offline-read docs warn about session timezone for some stores; verify storage/time semantics and make any session change explicit/approved.
- Register new versions when logic/columns change; do not overwrite an in-use version. Refresh frequency/warehouse/description updates have distinct lifecycle permissions and cost implications.
- Verify lineage through the supported dataset/training/Registry workflow. A comment naming a dataset or local pandas conversion is not proof of automatic model lineage; capture actual feature/dataset/model version evidence.
- Apply least privilege/classification/policies to actual schema/view/data paths and test consumer behavior. No universal ACCOUNTADMIN prerequisite or broad future grants by default.
- Profile dataset/refresh cost and freshness, bounded local collection and failed refreshes. No fixed MEDIUM/LARGE row thresholds, default one-hour SLA, automatic clustering or materialized-view frequency quota.
- Creation/registration/refresh updates/grants/dataset persistence/deletion are mutations. Inspect consumers/ownership/recovery and get approval; retain failed/uncertain state rather than broad cleanup.

### Execution Steps

1. Inspect source/store APIs and establish entity/time/grain/freshness/security contracts and approved scope.
2. Design versioned entities/views and managed/external refresh behavior with correct current API and source permissions.
3. Prepare temporal/key/NULL/determinism/train-serve tests and bounded dataset/model-lineage integration.
4. Under execution approval, register/build intended objects/datasets and verify freshness, values, lineage, access and costs.
5. Report actual identities/outcomes/gaps and approved lifecycle/recovery decisions without dropping shared schema resources.

### Validation

- Actual API/entity/view/version contracts correct, keys/time semantics and managed/external classification explicit.
- Dataset tests show no temporal leakage/fanout/missing coverage beyond declared policy, train/serve contract preserved.
- Refresh/data/security/lineage/cost evidence supports claims; no inferred guarantee from ASOF, tags or dataset comments.
- Mutation scope and recovery preserve consumers/known-good versions; unrun account checks remain unverified.
- Deliver reviewed definitions/dataset design and exact source/feature/model identities and verification limits.

## References

- [Feature Store architecture](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview)
- [Creating/connecting](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/create)
- [Entities](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/entities)
- [Feature views and refresh behavior](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/feature-views)
- `113a-snowflake-feature-store-patterns.md` for temporal/version/cost review.
- `113b-snowflake-feature-store-engineering.md` for transformations.
