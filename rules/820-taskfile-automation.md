---
schema_version: v4.0
rule_version: v5.0.0
description: "Core directives for creating and maintaining project automation using Taskfile.yml, ensuring consistent, portable, and well-documented task management."
last_updated: 2026-10-06
keywords:
  - kw:Taskfile.yml
  - kw:task runner automation
  - kw:uvx ephemeral tools
  - kw:command auto-detection
  - kw:cross-platform task portability
  - kw:pipefail error propagation
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 202-markup-config-validation.md  # YAML validation patterns
  optional:
    - 820a-taskfile-advanced-patterns.md  # Advanced patterns
    - 200-python-core.md  # Python automation patterns
    - 300-bash-scripting-core.md  # Shell scripting patterns
---
# Taskfile Automation Directives

## Scope

**What This Rule Covers:**
Discoverable, portable Task automation with explicit dependencies, safe interpolation, environment checks and accurate failure propagation.

**When to Load This Rule:**
When creating/editing Taskfile YAML or reviewing task sequencing, platform behavior and helper-script integration.

## Contract

### Inputs and Prerequisites

- Existing Taskfile/includes/distribution overrides, actual Task version and supported platforms.
- Project manifests/lockfiles, toolchain, task consumers and mutation/cleanup boundaries.
- Required YAML validation guidance read; approved local test environment.

### Mandatory

- Preserve project Task conventions/version compatibility. In this project use `version: '3.45'` and `set: [pipefail]`; do not impose that minimum on unrelated projects without checking required features.
- Provide descriptive public task `desc`, discoverable default help and consistent namespace:action names. Mark implementation-only tasks internal.
- Use explicit tool preconditions and useful errors; do not silently switch toolchains. Python commands follow the detected manager, using locked uv runs here and bounded/pinned ephemeral tools only when appropriate.
- Quote paths/variables through supported shell-quoting helpers. YAML colons in commands need quoted scalars/block syntax; SQL/shell/Go-template quoting are separate layers.
- Encode ordering explicitly: dependencies may run concurrently, so dependent build/test/deploy or destructive steps must use ordered task calls/commands rather than unordered deps.
- Use requires/preconditions for required inputs and actual readiness. Status/sources/generates skip only when their evidence really proves the result current; a stale flag file does not prove deployment success.
- Guard OS-specific commands with platforms and document supported systems. Do not claim Windows support or lack of support from assumptions about the embedded shell; verify current Task capabilities.
- Prefer maintained helper scripts for nontrivial control flow and structured parsing; avoid giant nested template/shell command strings.
- Keep check-only and fix/install/lock-update/deploy/cleanup tasks distinct. Explicitly authorize external effects and deletion, with target confinement and preserved unrelated/staged work.
- Dry-run/listing are previews, not proof of safety; dynamic vars or shell interpolation can execute during evaluation. Read their implementations before invoking them.

### Execution Steps

1. Read Taskfile, includes and helper scripts; inspect version/platform/toolchain and available task conventions.
2. Implement minimal tasks with description, quoted inputs, explicit tool/parameter checks and safe ordered dependencies.
3. Validate YAML/schema and inspect listing/dry-run behavior after reviewing dynamic evaluation for side effects.
4. Run focused safe tasks/negative cases for missing tools/params, quoted paths, pipeline failure and dependency ordering.
5. Run appropriate full automation gates; report exact executed/skipped outcomes and environment limitations.

### Validation

- Task schema/list/default help work; public descriptions and namespaces accurate.
- Pipeline failures propagate and ordered operations do not race through concurrent deps.
- Variables/paths safely quoted, required inputs fail clearly, no implicit fallback/tool installation.
- Platforms/version features tested, no unsupported portability assertions.
- Fingerprints/status accurately represent current outputs; no stale-success masking.
- Mutating tasks remain separate/authorized, cleanup confined, dry-run not reported as execution validation.

## References

- [Task documentation](https://taskfile.dev/docs/)
- [Task schema](https://taskfile.dev/schema.json)
- [uv project execution](https://docs.astral.sh/uv/concepts/projects/run/)
- `820a-taskfile-advanced-patterns.md` for larger automation workflows.
