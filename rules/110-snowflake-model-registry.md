---
schema_version: v4.0
rule_version: v5.0.0
description: Reproducible Snowflake model registration, signatures, tested serving targets, least privilege, and controlled lifecycle promotion.
last_updated: 2026-10-07
keywords:
  - kw:model registry
  - kw:ml model versioning
  - kw:model inference serving
  - kw:model RBAC privileges
  - kw:sample input schema
  - kw:model metadata governance
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md
---
# Snowflake Model Registry

## Scope

**What This Rule Covers:**
Model/environment identity, registry versioning, input/output signatures, serving compatibility, governance, promotion and observability.

**When to Load This Rule:**
When logging, reviewing, serving, securing, or promoting models through Snowflake Model Registry.

## Contract

### Inputs and Prerequisites

- Actual model type/artifact, training/preprocessing contract, expected signatures, representative bounded input and validation data.
- Installed snowflake-ml-python version/API, dependencies, approved registry/compute target, privileges and registration/inference scope.

### Mandatory

- Inspect existing registry/model versions and project conventions before logging or creating schemas. Use supported Registry/SQL APIs with explicit database/schema/session identity; a dedicated new schema is not always necessary.
- Capture signatures through supported sample_input_data or explicit signatures, accounting for model-type exceptions. Do not forbid every registration without samples; verify names/order/types/shape/NULL behavior and preprocessing consistency.
- Keep samples/artifacts within approved data scope; no real sensitive rows/secrets in comments, metrics or external validators. Serialized models/custom code are executable artifacts and must be trusted/reviewed before loading.
- Bind Python/package/custom-code dependencies reproducibly and verify target compatibility. Warehouse support depends on dependencies, GPU needs, model size and supported methods, not a blanket SQL-translation restriction for complex sklearn.
- Select supported warehouse/SPCS targets and invocation methods from the installed API. SPCS does not support every possible model automatically; deployment/service/compute resources require separate approval and cost review.
- Use unique project-compatible model/version names and immutable reviewed artifacts. Do not overwrite existing versions or assume quoted identifiers require one fixed semantic-version convention.
- Record actual evaluation metrics, data/version provenance, purpose, owner and limitations with supported metadata fields. Never fabricate accuracy, approval board decisions, tags or unknown log_model parameters.
- Grant least privilege by use: USAGE supports warehouse inference; READ supports SPCS inference and metadata access according to current documentation. Review ownership/future-grant scope separately; registry logging does not authorize self-grants.
- Test registered methods/signatures and outputs against independent local/reference predictions, with suitable tolerances, malformed/NULL/empty input, preprocessing, batching, latency and resource limits before promotion.
- Pin inference to the intended version/alias and review default-version changes against consumers. Caching must include model version/input identity and cannot assume nondeterministic predictions are interchangeable.
- Promotion must preserve reviewed artifact/environment and pass project quality/business gates in authorized lower environments. Inspect supported copy/export/relog workflows rather than pass a ModelVersion object as a guessed log_model input.
- Maintain monitoring/drift/data-quality owners and retraining criteria appropriate to the use case. Verify current monitoring prerequisites/options; an inaccessible MODEL MONITOR is not proof of one missing Registry flag.
- Retain known-good versions, audit actual changes/costs, and define scoped approved archive/deletion policy. Model registration, serving, default changes, tags, monitors and cleanup are account mutations, not implicit validation authority.

### Execution Steps

1. Inspect model/environment and existing registry identity, signatures, target support, privileges, consumers and recovery needs.
2. Prepare immutable artifact/dependencies and supported logging parameters with truthful metadata/evaluation evidence.
3. Run local interface/reference tests; register only under explicit account mutation approval.
4. Validate registered inference in approved scope against expected predictions and serving/security/resource behavior.
5. Promote/default/serve/monitor only after relevant approval and gates; report actual version identity and unresolved checks.

### Validation

- Signatures/preprocessing match actual model and data; no guessed parameters, sample requirements or target guarantees.
- Artifact/dependency/version identity preserved, meaningful metrics supported by tests and sensitive metadata protected.
- Least-privilege warehouse/SPCS use and actual inference behavior verified before approved promotion.
- Known-good retention, consumer compatibility, cost/monitoring/recovery documented without unapproved cleanup.
- Output includes registration/serving design, exact artifact/version/tests and limitations; unlogged/unrun model operations remain unverified.

## References

- [Model Registry overview and signatures](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)
- [Model management](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-management)
- [Model observability](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/model-observability)
- `110a-snowflake-model-monitor.md` for monitoring.
- `110b-snowflake-model-registry-operations.md` for operational controls.
