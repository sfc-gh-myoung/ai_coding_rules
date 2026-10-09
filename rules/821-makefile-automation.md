---
schema_version: v4.0
rule_version: v3.0.0
description: "Core directives for creating and maintaining project automation using Makefiles, ensuring consistent, portable, and well-documented target management with GNU Make."
last_updated: 2026-10-06
keywords:
  - kw:GNU Make
  - kw:make target
  - kw:phony declaration
  - kw:self-documenting help
  - kw:uv uvx integration
  - kw:tool auto-detection
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 821a-makefile-advanced-patterns.md  # Advanced patterns (conditionals, categorized help, platform detection)
    - 820-taskfile-automation.md  # Alternative task runner (Taskfile.yml)
    - 300-bash-scripting-core.md  # Shell scripting patterns used in targets
---
# Makefile Automation Directives

## Scope

**What This Rule Covers:**
Discoverable GNU Make targets, actual dependency sequencing, shell/tool configuration, guards and confined cleanup.

**When to Load This Rule:**
When creating/editing Makefiles or reviewing recipes, prerequisites, recursive Make and portability.

## Contract

### Inputs and Prerequisites

- Existing Makefile/includes, GNU Make version, platform and actual project toolchain.
- Current target consumers and approved file/resource mutation boundaries.
- Safe local tests and language rules for recipe/helper implementation.

### Mandatory

- Read current files before editing. Use a discoverable default help target (`.DEFAULT_GOAL := help` where established) and descriptions for public targets.
- Mark non-file operations `.PHONY`; file-producing targets need accurate prerequisites/output paths. Do not mark real outputs phony merely to force reruns.
- Use literal recipe tabs unless the project explicitly configures a supported alternative. Set Bash only when required and available; preserve POSIX portability where intended.
- Choose variable assignment deliberately: `:=` evaluates once, `=` recursively; allow documented user tool overrides. A command-v fallback does not verify tool availability: fail clearly at use.
- Use the detected Python manager/toolchain; locked uv/uvx patterns apply when that is the project's actual choice, not a universal ban on other managers.
- Validate required parameters at the intended target scope without breaking unrelated help targets. Quote paths/data and do not pass untrusted shell fragments or secrets in argv.
- Prerequisites are a dependency graph, not guaranteed left-to-right execution under parallel Make. Encode required ordering through dependencies/ordered submakes; use `.NOTPARALLEL` only when appropriate.
- Recursive recipes use `$(MAKE)` to preserve flags/jobserver behavior. Each recipe line normally has its own shell; `.ONESHELL` requires a compatible GNU Make and deliberate error handling.
- Read recipes and parse-time shell expressions before `make -n`: shell expansion and recursive Make can still execute. A dry-run is not a sandbox or runtime-success proof.
- Separate check/fix/install/lock-update/deploy/cleanup targets. Cleanup deletes only verified generated paths and does not blanket-ignore errors or remove arbitrary caches/venvs without approval.
- Provide one coherent CI entry point invoking actual required checks, with successful completion reported only after each check succeeds.

### Execution Steps

1. Inspect existing Makefile/includes, manifests, shell requirements, version and target conventions.
2. Add/update minimal targets with accurate prerequisites, phony declarations, public help and parameter/tool guards.
3. Review quoting, per-line shell state, variable evaluation, parallel races and recursive Make semantics.
4. Run safe listing/preview after inspecting parse-time side effects; test missing parameters/tools, target-name collisions and failure propagation in fixtures.
5. Execute authorized focused/full validation tasks, preserving generated-artifact/cleanup scope and recording true outcomes.

### Validation

- Default/help discoverability and public targets correct; phony/file-target identities accurate.
- Recipes use correct indentation, quoting, tool/version assumptions and actionable guard errors.
- Parallel builds respect actual dependencies; recursive Make preserves flags and jobserver usage.
- Dry-run effects disclosed, no falsely certified deployment/runtime result.
- Cleanup confined to owned generated paths, errors not hidden and destructive/external effects separately approved.
- CI checks, changelog/documented invocation and actual automation remain consistent.

## References

- [GNU Make manual](https://www.gnu.org/software/make/manual/make.html)
- [POSIX Make](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/make.html)
- [uv tools](https://docs.astral.sh/uv/concepts/tools/)
- `821a-makefile-advanced-patterns.md` for larger Make workflows.
