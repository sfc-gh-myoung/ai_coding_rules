---
schema_version: v4.0
rule_version: v5.0.0
description: Reproducible governed Snowflake notebooks with runtime-aware dependencies, explicit cell state, and bounded computation.
last_updated: 2026-10-07
keywords:
  - kw:Snowflake Notebooks
  - kw:reproducible notebook execution
  - kw:Snowpark DataFrame computation
  - kw:cell naming conventions
  - kw:nbqa ruff linting
  - kw:notebook state management
token_budget: ~1200
context_tier: Medium
depends: {}
---
# Snowflake Notebook Directives

## Scope

**What This Rule Covers:**
Notebook structure, runtime/environment binding, live cell state, reproducibility, security, Snowpark computation, quality checks, and scheduling readiness.

**When to Load This Rule:**
When creating/reviewing Snowflake notebooks, debugging cell state, or preparing notebook workflows for production.

## Contract

### Inputs and Prerequisites

- Actual notebook surface (Workspaces, legacy warehouse/container runtime, or local Jupyter), live cell outline/source, supported tools, current packages, and expected outputs.
- Authorized data/compute scope, role/session configuration, execution/mutation boundaries, and secret/external-access requirements.

### Mandatory

- Identify the current surface before applying UI, package, metadata, or scheduling instructions. Workspaces notebooks and legacy notebooks differ; inspect actual capabilities instead of applying Packages-panel-only or pip-prohibited rules universally.
- Use live notebook APIs when provided for cell outline, source, and outputs; on-disk serialization may not represent live state. Never silently edit an exported copy while claiming the live notebook changed.
- Organize configuration/imports near the top, focused transformation/validation/visualization cells, and Markdown narrative for assumptions/business meanings. Keep dependencies explicit; no hidden variables from deleted or out-of-order cells.
- Use descriptive action_subject names where the surface supports named cells and project conventions require them. Do not require arbitrary metadata.name fields in all Jupyter files; preserve cell IDs and platform-specific metadata through supported editors.
- Bind runtime and dependency versions with the surface's supported environment/package mechanism. Document any installation/init cells and network needs; avoid speculative global environments or unapproved package downloads.
- Use the provided Snowpark session in managed environments when supported, not manual password connections. Local Jupyter uses the project's approved connection mechanism. Secrets stay in approved integrations/stores, never notebook source, outputs, URLs, or committed metadata.
- Push large filters/joins/aggregations to Snowflake through Snowpark/SQL and collect only bounded results appropriate to local memory. A fixed number of to_pandas calls is not a safety guarantee; inspect actual row/byte volume and schema.
- Resolve source columns before calculations and imports before use. SQL-cell result interoperability is surface-specific; do not assume every cell automatically creates the same named DataFrame type.
- Parameterize approved environment/date/input scope, seed random generators where useful, and document external data/time dependencies. Reproducibility means correct fresh-state execution, not identical volatile inputs by assertion.
- Fresh-session run-all is a runtime test only after reviewing cells for SQL/cloud/file mutations, costs, and external sends. Obtain execution approval; restarting can discard unsaved state, and running all cells is not inherently read-only.
- Apply project lint/format/tests to production-bound notebooks using supported Ruff/native notebook or nbqa workflows. Inspect installed syntax/configuration; no tool download, broad auto-fix, or claimed pass solely from valid notebook JSON.
- Extract reusable/production logic into tested .py/.sql modules when complexity/reuse warrants it, not a universal 500-line cutoff. Keep notebook narrative/results as useful consumers of those modules.
- Scheduling is separate deployment: inspect actual Workspaces/legacy scheduler, role, compute, parameters, output persistence, idempotency, alerts and retry/recovery. Do not convert every notebook into an invented task recipe.
- Preserve unrelated cells/outputs and save before risky operations. Redact sensitive outputs before approved sharing/version control; record interrupted executions and inspect owned changes before recovery/replay.

### Execution Steps

1. Inspect live notebook structure, runtime/session, package bindings, and all intended cell dependencies without executing cells.
2. Build scoped configuration/imports, narrative, computations, and validations with actual schema/session APIs.
3. Check metadata/serialization and run applicable local quality checks; extract reusable logic where justified.
4. Under execution approval, run from fresh state top-to-bottom, verify outputs/side effects and memory limits, and retain failures.
5. Save/version through approved workflow; prepare scheduling/sharing only if requested and authorized.

### Validation

- Cells/narrative and dependency order clear; supported names/IDs/metadata preserved and live changes accurately reported.
- Runtime/package/session/secret handling matches actual surface; no hidden-state, undefined-column/import, or large unbounded collection.
- Authorized fresh-state execution and applicable lint/format/test outcomes recorded; unexecuted notebook/SQL remains unverified.
- Parameters, reproducibility assumptions, compute costs, recovery and production extraction documented.
- Deliver notebook/source changes and verification limits without automatic upload, schedule, or publication.

## References

- [Notebooks in Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- [Legacy notebook runtimes](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks)
- [Snowpark for Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Ruff notebook support](https://docs.astral.sh/ruff/configuration/#jupyter-notebook-discovery)
- `109d-snowflake-notebooks-linting.md` for quality workflows.
- `104-snowflake-streams-tasks.md` for approved task orchestration where applicable.
