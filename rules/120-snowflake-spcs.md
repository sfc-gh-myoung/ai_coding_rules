---
schema_version: v4.0
rule_version: v5.0.0
description: 'Safe SPCS compute pools, image/spec deployment, endpoint authorization, resource planning, and evidence-based recovery.'
last_updated: 2026-10-07
keywords:
- kw:Snowpark Container Services
- kw:compute pool instance families
- kw:OCI image deployment
- kw:service specification YAML
- kw:platform events monitoring
- kw:GPU workload configuration
- kw:SPCS
token_budget: ~1450
context_tier: High
depends:
  required:
  - 100-snowflake-core.md
  optional:
  - 105-snowflake-cost-governance.md
  - 111-snowflake-observability-core.md
  - 119-snowflake-warehouse-management.md
---
# Snowflake Snowpark Container Services (SPCS)

## Scope

**What This Rule Covers:**
Compute-pool selection, reproducible images/service specs, private data access, endpoint permissions, monitoring, and scoped lifecycle recovery.

**When to Load This Rule:**
When deploying or troubleshooting containers on SPCS, sizing CPU/GPU pools, or reviewing service specifications and access.

## Contract

### Inputs and Prerequisites

- Existing service/pool/repository/spec, actual account region/capabilities, application resource/latency needs, and permitted deployment scope.
- OCI image/build identity, authorized repository/stage access, and object-specific compute-pool/service/secret privileges.
- Current service-spec schema and installed tooling. Do not use an unverified ENABLE_SNOWPARK_CONTAINER_SERVICES parameter as a capability gate.

### Mandatory

- Read current application/spec and pool/service inventory before choosing resources. Inspect available instance families and region support through authorized metadata; static cloud/family tables are not account capability evidence.
- Prefer appropriate current-generation CPU/memory families where supported; legacy/current naming differs by cloud. Select GPU capacity only for actual GPU-dependent workloads; match image architecture, drivers/libraries, node memory, and schedulable resource requests.
- Use reproducible versioned images, not mutable latest tags in production. Verify repository paths and actual image identity; pushing an image or uploading specs requires authorized destination and data scope.
- Validate spec fields against the current SPCS reference, not Kubernetes fields assumed compatible. Define requests/limits and readiness checks appropriate to the service. GPU requests/limits must both be specified with equal counts; memory/CPU and replicas must fit pool nodes.
- A health endpoint must test the dependencies it claims healthy. Never emit database=ok without a real bounded check; distinguish liveness from readiness so unavailable dependencies do not create misleading success or restart storms.
- Keep secrets out of images/spec values/logs. Reference approved Snowflake secret objects using supported placement fields and least privilege. Use supported container Snowflake authentication when suitable, not a baked-in database password.
- Default endpoints to internal unless public access is required and approved. Public ingress uses Snowflake authentication and endpoint service-role authorization; public=true alone is not anonymous access. Do not invent an authentication: SNOWFLAKE_JWT spec field.
- Distinguish deployment privileges from endpoint consumption: CREATE SERVICE and pool USAGE enable deployment; BIND SERVICE ENDPOINT enables public endpoint creation, not consumer access. Grant appropriate service roles to consumers only with authorization; review database/schema access and owner-role effects.
- Container database access normally uses service-owner authority unless supported caller semantics are explicitly configured. Enforce tenant/user data boundaries in application design; authenticated ingress does not automatically apply each caller's database permissions.
- Use approved external access integrations/network rules for required egress and supported stage/block/local/memory volume semantics. Do not equate ephemeral container storage with durable persistence or allow unauthorized external transmission.
- Reuse supported connector/client connections with bounded concurrency and cleanup; do not invent a snowflake.connector.pooling API. Push down large data operations and bound in-container memory rather than fetching entire datasets.
- Export structured sanitized stdout/stderr with documented logExporters/event-table configuration. Diagnose service/container status, readiness, image pulls, resource scheduling, and runtime logs; no READY-only success claim or unsupported status/event function.
- Right-size pool nodes and service replicas from measured demand. A running service can keep a pool active despite sparse requests; distinguish service suspend from pool suspend and current auto-suspend limitations. Use documented compute-pool consumption views, not an assumed COMPUTE_POOL_HISTORY view.
- Updates, suspend/resume, pool reassignment, and drops require approved ownership and impact review. Confirm ALTER syntax supports each intended change; capture current spec/image/grants and persistent data for rollback. Do not drop shared pools or services for routine repair.
- For rolling or blue-green changes verify compatibility, consumer routing, readiness, and old-version retention before cleanup. Reconcile uncertain outcomes before retrying; platform events are diagnosis evidence, not permission to mutate resources.

### Execution Steps

1. Inspect existing source/spec/image identities, pool families/capacity, access, volumes, and current service health in permitted scope.
2. Plan the smallest deployment with reproducible image, schedulable resources, real probes, secrets, internal/public endpoints, and rollback.
3. Validate local specification/configuration; push/create/update only under explicit deployment approval.
4. Inspect effective service/container readiness, logs/events, authorized endpoint/data access, and representative workload/resource behavior.
5. Report deployment artifacts, observed status, costs, access boundaries, failed attempts, and remaining runtime/availability gaps.

### Validation

- Spec fields/image/pool architecture and resource requirements match current documentation and actual supported capacity.
- Probes verify the health they report; READY state, endpoint reachability, and meaningful application behavior are checked separately.
- Secret/egress/volume controls and service-owner/caller boundaries prevent confidential exposure; consumer roles are scoped.
- Load, OOM/backpressure, connection cleanup, logging, lifecycle/cost behavior, and rollback are tested or explicitly unverified.
- Output includes spec/deployment design and monitoring/recovery evidence; no unapproved public exposure, push, grant, or teardown.

## References

- [SPCS overview](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview)
- [Specification fields, resources, probes, secrets, and endpoints](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference)
- [Service lifecycle, communication, and service roles](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-services)
- [Compute pools](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-compute-pool)
- [Instance families](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/instance-families)
- [Monitoring services](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/monitoring-services)
- `105-snowflake-cost-governance.md` for consumption review and `111-snowflake-observability-core.md` for telemetry when needed.
