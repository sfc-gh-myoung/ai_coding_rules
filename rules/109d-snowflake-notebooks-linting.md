---
schema_version: v4.0
rule_version: v3.0.0
description: Reproducible notebook lint/format gates using supported Ruff or nbqa workflows without erasing outputs or metadata.
last_updated: 2026-10-07
keywords:
  - kw:nbqa
  - kw:notebook linting
  - kw:Ruff notebook integration
  - kw:uvx nbqa commands
  - kw:notebook cell quality
  - kw:notebook automation targets
token_budget: ~950
context_tier: Low
depends:
  required:
    - 109-snowflake-notebooks.md
    - 201-python-lint-format.md
---
# Snowflake Notebook Code Quality and Linting

## Scope

**What This Rule Covers:**
Notebook source discovery, reproducible lint/format checks, project configuration, scoped fixes/exceptions, and local/CI consistency.

**When to Load This Rule:**
When configuring or running notebook quality gates, reviewing lint failures, or preparing notebooks for production.

## Contract

### Inputs and Prerequisites

- Actual notebook surface/source, current tool versions/configuration/locks, intended files and production/exploratory status.
- Read notebook and project quality automation before edits; determine live API versus exported-file workflow and mutation permissions.

### Mandatory

- Prefer established project tools. Ruff has native notebook lint/format support; nbqa is an alternative/adapter where needed, not a mandatory industry-standard layer.
- Bind tool/runtime versions through existing locked environment; uvx may install/download packages and does not make dependencies unnecessary. No unapproved tool/environment changes.
- Run explicit read-only lint and format checks on intended notebook source using installed supported syntax. Native Ruff uses check and format --check; nbqa subcommand forwarding varies by tool/version and must be verified before prescribing commands.
- Share/inherit project quality settings with scoped notebook exceptions. Ruff uses nearest configuration and does not automatically merge parent settings; inspect actual selected config and discovery/exclusions.
- Ensure intended notebooks are discovered, checkpoint copies excluded, and SQL/magic cells handled by supported tooling. Report skipped/unparseable cells; do not assume Python lint validates SQL or notebook execution.
- Fix undefined/import/order/syntax and applicable style/docstring issues without blanket noqa or disabling whole notebook checks. Missing third-party runtime packages do not inherently block Ruff static lint; type-ignore comments do not suppress unrelated lint rules.
- Apply auto-fix/format only to owned requested files after inspecting the proposed change; avoid unsafe fixes and preserve cell IDs/metadata/source boundaries/unrelated outputs. Do not clear outputs just to lint code: lint tooling normally analyzes source, not saved traceback outputs.
- Validate serialized notebooks using appropriate structured APIs and review source/metadata diffs. Generic metadata.name is not universally required; do not rewrite live notebooks through a mismatched export format.
- Production-bound notebooks require applicable checks before completion. Exploratory/unsupported-syntax exceptions must be narrowly documented; temporary status is not permission for unbounded data pulls, secret exposure, or broad suppression.
- Tutorial code demonstrates correct runnable patterns; do not introduce intentional unsafe executable examples and suppress their diagnostics for pedagogy.
- Local and CI invoke consistent project targets/configuration and report actual exit codes/diagnostics. A no-files match is not a notebook quality pass; lint/format success is not fresh-state runtime correctness.

### Execution Steps

1. Inspect source and configured file discovery, tool versions, notebook support, and local/CI entrypoints.
2. Run scoped read-only lint/format checks; map findings to real cells/source and distinguish unsupported syntax from code defects.
3. Correct owned source and justified targeted settings; preserve metadata/outputs and recheck serialization.
4. Rerun both gates and document exclusions/errors; run notebook execution tests separately only with authorization.

### Validation

- Intended notebooks actually checked with reproducible tool/config identity; no accidental broad exclusions.
- Applicable lint/format issues resolved and exceptions narrow/reasoned, no arbitrary suppression percentage target.
- Cell IDs/source/metadata/unrelated outputs preserved; no unapproved download, output wipe, or unsafe auto-fix.
- Deliver exact checks/exit results and remaining cell/runtime limitations; unavailable runtime tests remain unverified.

## References

- [Ruff configuration and notebook discovery](https://docs.astral.sh/ruff/configuration/)
- [nbqa command examples](https://nbqa.readthedocs.io/en/latest/examples.html)
- `109-snowflake-notebooks.md` for live/runtime boundaries.
- `201-python-lint-format.md` for shared quality gates.
- `820-taskfile-automation.md` and `821-makefile-automation.md` for project entrypoints.
