---
schema_version: v4.0
rule_version: v5.0.0
description: Ownership-scoped Snowflake app packaging, version-aware deployment, source integrity, and safe lifecycle recovery.
last_updated: 2026-10-07
keywords:
  - kw:staged application lifecycle
  - kw:five-step deployment workflow
  - kw:AUTO_COMPRESS FALSE
  - kw:REMOVE before PUT
  - kw:Streamlit ADD LIVE VERSION
  - kw:stage as source of truth
token_budget: ~1250
context_tier: Medium
depends:
  required:
    - 109-snowflake-notebooks.md  # Notebook deployment object lifecycle patterns
---
# Snowflake Application Deployment Automation: Core Patterns

## Scope

**What This Rule Covers:**
Reproducible app/notebook staged artifacts, automation, source/object lifecycle, supported publication, verification, and ownership-scoped recovery.

**When to Load This Rule:**
When preparing or reviewing Snowflake app/notebook deployment automation and staged source management.

## Contract

### Inputs and Prerequisites

- Existing scripts/Make/Task/CI, actual app type/runtime, client version/renderer, source manifest, dependency files, and approved target environment.
- Current source/object/live-version state, grants/consumers, stage ownership/path inventory, and explicit deployment/cleanup authority.

### Mandatory

- Read existing deployment helpers and preserve project conventions. Separate packaging, transfer, object update, publication, verification and optional cleanup; do not mandate five targets or DROP/REMOVE before every update.
- Preserve existing objects/data/grants where supported. Destructive drop/recreate needs specific ownership and deletion approval, downtime/consumer impact review, and recovery; IF EXISTS does not authorize deletion.
- Prefer versioned app-owned artifact prefixes or exact manifest reconciliation. REMOVE only approved stale owned paths after proving they are unnecessary and preserving recovery versions; never clear a shared stage/prefix by default.
- Version-controlled reviewed source plus manifest/hash is the authoritative artifact; stages and copied app versions are deployment locations. Verify local, uploaded, and effective runtime identity instead of calling an arbitrary stage canonical.
- For staged application assets that must remain readable (.py/.yml/.ipynb), explicitly disable PUT compression with AUTO_COMPRESS=FALSE or verified CLI equivalent. SQL PUT defaults TRUE; current snow stage copy docs default FALSE. Inspect the installed version and wrapper flags rather than transfer defaults between interfaces.
- Preserve relative directories and verify entrypoint/dependency/media assets. PUT does not recursively preserve arbitrary divergent paths; use supported transfer tooling and test path mapping. Inspect transfer results, not just query-history success.
- Distinguish Streamlit FROM source copies from legacy ROOT_LOCATION and current notebook/Workspace deployment. FROM copies source at creation; later source-stage edits do not automatically update that app.
- For Streamlit FROM apps, use supported object/version updates and approved initialization/publication (ADD LIVE VERSION FROM LAST when required). Owner UI initialization exists, but automation should explicitly verify live state and intended non-owner access.
- Match MAIN_FILE and dependency format to runtime: warehouse versus container requirements differ. Inspect available package versions rather than mandate Streamlit >=1.50 globally; runtime migration requires its own compatibility/concurrency review.
- Bind account/role/database/schema/warehouse/compute and approved stage prefix explicitly. Verify operation-specific READ/WRITE/creation/ownership privileges; credentials stay in approved stores/config, never SQL/automation logs.
- Pin project-supported CLI/dependencies and inspect actual flags/template mode. No universal 3.12 minimum or uvx snow package assumption; quote shell paths separately from SQL identifiers/literals.
- Explicitly sequence dependent automation; Make prerequisites/Task deps can run concurrently. Fail closed on missing source, wrong target, failed transfer, creation or publication; no success banner before effective app checks.
- Test dev/test before approved production promotion using the same reviewed artifact. Browser/app execution can issue SQL or external calls and needs appropriate authorization; deployment correctness is not just object existence.
- Retain per-step results and inspect uncertain state before rerun. Recover only owned approved artifacts/objects and preserve grants/live versions/unrelated work; do not automatically replay broad teardown.

### Execution Steps

1. Inspect actual lifecycle/source/version/automation and resolve approved scope, ownership, compatibility and recovery.
2. Package reviewed assets and manifest; design data-preserving ordered transfer/update/publication with scoped cleanup only when needed.
3. Run local package/script/renderer/precondition checks without cloud mutation.
4. Under explicit deployment approval, transfer and verify files, update/create the intended object, initialize/publish as needed, then inspect effective configuration.
5. Test intended consumer behavior/access, record failures/partial state, and apply approved recovery or retention cleanup only after evidence review.

### Validation

- Manifest and relative paths match effective application source; compression/entrypoint/dependency/runtime bindings correct.
- Exact target/ownership verified, no blanket DROP/REMOVE, grants/consumers and recovery versions preserved.
- Automation ordered and fail-closed, secrets not exposed, actual transfer/object/publication outcomes recorded.
- App functionality and intended viewer access tested where authorized; no universal deployment-time guarantee.
- Deliver scoped deployment design/scripts/runbook and actual checks; unexecuted cloud/app/browser validation remains unverified.

## References

- [PUT transfer/compression semantics](https://docs.snowflake.com/en/sql-reference/sql/put)
- [CREATE STREAMLIT source/runtime behavior](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [ALTER STREAMLIT lifecycle](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [Notebooks in Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- `109g-snowflake-app-deployment-sql-scripts.md` and `109h-snowflake-app-deployment-taskfile.md` for tooling details.
- `109i-snowflake-app-deployment-advanced.md` for promotion/recovery.
