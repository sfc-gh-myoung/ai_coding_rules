---
schema_version: v4.0
rule_version: v3.0.0
description: Ordered fail-closed Task deployment workflows with explicit scope, preconditions, and actual artifact verification.
last_updated: 2026-10-07
keywords:
  - kw:Taskfile deployment automation
  - kw:five-step deployment workflow
  - kw:deployment task preconditions
  - kw:sequential task execution
  - kw:stage file upload tasks
  - kw:notebook streamlit deployment
  - kw:snowsight
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 820-taskfile-automation.md
---
# Snowflake App Deployment Taskfile Patterns

## Scope

**What This Rule Covers:**
Task-based packaging/transfers/object publication, environment binding, shared helpers, preflight gates, sequencing and failure evidence.

**When to Load This Rule:**
When implementing or reviewing Taskfile-based Snowflake application deployment.

## Contract

### Inputs and Prerequisites

- Existing Taskfile/includes/helpers, installed Task/CLI versions, supported app lifecycle scripts, manifest and approved environments.
- Explicit target/account/role/compute/prefix policy, operation ownership, deployment approval and separate cleanup/publication scope.

### Mandatory

- Match existing task naming/layout and shared helpers. Define necessary package/upload/update/publish/verify operations; do not mandate five tasks or a destructive drop-remove-upload-create sequence.
- Use ordered cmds task calls for dependent steps; deps may execute concurrently and must not encode ordered publication/cleanup. Parallelize only independent work with disjoint mutation scopes.
- Validate source files, dependency config, manifest, required variables/tools, target allowlist, and approval before any mutation. Repeat relevant preconditions on directly callable upload/update tasks to prevent bypass.
- Use valid precondition objects with sh and msg as supported, not a standalone message entry or invented test field. Preconditions and dynamic variables can execute shell; task --list/--dry are not unconditional sandboxes.
- Resolve environment via a validated enum/map; reject unknown values, missing accounts or inconsistent database/schema/stage rather than silently falling back to dev. Production needs explicit promotion authorization.
- Pass scoped variables to shared helpers consistently and quote filesystem/shell arguments. Task templates are not SQL escaping; validate SQL identifiers/literals at the renderer layer and avoid shell interpolation injection.
- Pin tools through project-managed versions and supported command syntax. Credentials stay in approved config/secret stores, never vars printed through task output or inline YAML SQL strings containing secrets.
- Preserve established script-based SQL rendering and runtime-aware compression/path/publication semantics from deployment rules. No blanket environment.yml requirement for every runtime.
- Fail closed on command/nonzero transfer or verification errors; do not ignore_error or append success output regardless of prior outcome. Keep exact exit/query/artifact evidence with redacted sensitive data.
- Verify manifest files/content and effective source/runtime/live-version/grants, not only LIST/SHOW display or task count. App health calls may execute SQL and need approval.
- Cleanup/drop tasks are explicit exceptional operations with independently checked ownership/path/deletion approval; deploy must not implicitly delete shared artifacts or an existing production object.
- Local/CI entrypoints share configuration and intended artifact identity; publication, scheduling, Git commit/push, and external notifications require their own authorization.

### Execution Steps

1. Read Task/helpers/SQL and identify intended ordered lifecycle and direct-call preconditions.
2. Implement minimal tasks/includes with validated environment bindings and preflight before mutation.
3. Parse/check automation and inspect safe dry/list behavior; run local helper tests without deploying.
4. Under deployment approval, execute ordered transfer/update/publication and manifest/object/functionality verification.
5. Retain failed/partial outcomes, inspect current state and invoke only scoped approved recovery.

### Validation

- Valid Task syntax/helper paths, preconditions before every mutating entrypoint, no unsafe dynamic variable/argument injection.
- Dependent steps sequential, unknown environment rejected, credentials protected and production gate explicit.
- Effective artifact/runtime/viewer access and actual per-step exit results verified where authorized.
- No forced destructive five-step workflow or success claim from --list alone; unrun account checks disclosed.
- Deliver Task changes, script contracts, ownership/recovery boundaries and exact local/runtime outcomes.

## References

- [Task guide](https://taskfile.dev/docs/guide)
- [Task schema](https://taskfile.dev/docs/reference/schema)
- [CREATE STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- `820-taskfile-automation.md` for Task semantics.
- `109b-snowflake-app-deployment-core.md` and `109g-snowflake-app-deployment-sql-scripts.md` for approved lifecycle/transfer details.
