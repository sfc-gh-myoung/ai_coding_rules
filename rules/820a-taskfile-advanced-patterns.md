---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced Taskfile patterns including categorized help output, subtask file organization, cross-platform patterns, and AI agent integration considerations."
last_updated: 2026-10-06
keywords:
  - kw:taskfile includes
  - kw:categorized help output
  - kw:subtask file organization
  - kw:cross-platform task guards
  - kw:task namespaces
  - kw:AI agent task discovery
token_budget: ~900
context_tier: Low
depends:
  required:
    - 820-taskfile-automation.md  # Core Taskfile patterns
---
# Taskfile Advanced Patterns

## Scope

**What This Rule Covers:**
Includes/namespaces, categorized help, variable scopes, platform-specific workflows, incremental status and agent-consumable automation.

**When to Load This Rule:**
When a Taskfile's complexity warrants modules/help grouping or when reviewing portability, CI sequencing and machine-readable discovery.

## Contract

### Inputs and Prerequisites

- Core Task guidance read, existing root/includes/helper source and actual Task version.
- Task users, platform matrix, workflow dependency/authorization boundaries and dynamic-variable behavior.

### Mandatory

- Use stable namespace:action names with ergonomic aliases and descriptions; internal tasks remain internal. Categorized help is useful for larger sets, not a required redesign at an arbitrary eighth task.
- Split into modules when domain/reuse/platform complexity warrants it; file size is a signal, not sufficient cause. Keep existing project module conventions.
- Define includes with explicit `taskfile` paths and intended `dir`; `dir` is execution directory, not a universally reliable implicit include selector. Validate paths against current Task documentation/version.
- Required modules fail clearly when missing; optional includes may use optional:true only when absence is intended. Avoid circular includes or flattening until collision behavior is verified.
- Keep variable scope/precedence explicit at root/include/task. Quote values via supported helpers rather than nested escaping; dynamic sh vars can execute during list/preview.
- Guard OS-specific actions and verify supported platform behavior, using actual Task platform facilities rather than guessed uname fallback labels.
- Use ordered commands for dependent validation/build/deploy; deps may be parallel. Do not deploy simply because CI environment variable exists.
- Fingerprints/status must prove outputs current, including lock/config changes. Directory existence alone does not prove environment dependencies synchronized.
- Agent output should support structured status/errors, stable exit codes and plain/JSON forms where useful; no decorative Unicode/emoji requirement, secrets or verbose repeated command echo.
- Installation, publication, cleanup and cloud mutations remain explicit separately authorized tasks, never hidden in discovery/check tasks.

### Execution Steps

1. Inspect root and included Taskfiles/helpers, namespaces, actual platform/version matrix and user overrides.
2. Choose minimal modular/help changes and preserve public names/aliases unless breaking change is approved.
3. Define include paths, variable scopes, platform guards and required/optional module behavior.
4. Encode actual dependency sequence, safe preconditions and honest status/fingerprint contracts.
5. Run schema/list/preview checks after reviewing dynamic evaluation; exercise missing includes, collisions, quoted paths and failure cases safely.
6. Verify representative platforms/CI and machine-readable output; report unsupported or untested paths explicitly.

### Validation

- Includes resolve and no circular/flattened-name ambiguity; optional absence intentional.
- Help matches actual public tasks, descriptions/aliases discoverable and no terminal overflow.
- Platform/version/variable assumptions verified, quoting safe and secrets redacted.
- Dependencies sequence correctly; status cannot silently skip required sync/checks.
- Agent/CI outcomes accurate, no unauthorized install/deploy/cleanup from previews.

## References

- [Task documentation](https://taskfile.dev/docs/)
- [Task schema](https://taskfile.dev/schema.json)
- `820-taskfile-automation.md` for core safety and sequencing.
