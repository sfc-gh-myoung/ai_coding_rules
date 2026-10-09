---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced Makefile patterns including categorized help output, conditional logic, variable assignment types, include directives, platform detection, and AI agent integration considerations."
last_updated: 2026-10-06
keywords:
  - kw:categorized help
  - kw:makefile conditionals
  - kw:variable assignment operators
  - kw:makefile include directives
  - kw:platform detection
  - kw:AI agent integration
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 821-makefile-automation.md  # Core Makefile patterns
  optional:
    - 820a-taskfile-advanced-patterns.md  # Equivalent patterns for Taskfile
    - 300-bash-scripting-core.md  # Shell patterns used in recipes
---
# Makefile Advanced Patterns

## Scope

**What This Rule Covers:**
GNU Make variable flavor, includes, parse/runtime conditionals, categorized help, platform logic, recursive builds and agent/CI contracts.

**When to Load This Rule:**
When reviewing complex Make variables/includes/platform variants or larger target discovery and CI workflows.

## Contract

### Inputs and Prerequisites

- Core Make guidance read, existing files/includes, actual GNU Make version and platform matrix.
- Public target/variable consumers and safe authorized test fixtures.

### Mandatory

- Choose `:=` for intentional once-at-parse computation, `=` for deferred expansion, `?=` for unset defaults and `+=` for deliberate accumulation. Variable evaluation can run shell code; do not call preview blindly.
- Use consistent uppercase descriptive variables and preserve documented command-line/environment overrides; `override` must be intentional, not used to defeat user configuration.
- Use Make conditionals for parse-time selection and shell conditionals for runtime behavior. Inspect whitespace/strip semantics instead of claiming every trailing space universally breaks comparisons.
- Required includes use include; optional local/platform modules use -include. Optional omission must not hide a required build/test gate. Included files define valid variables/targets, not free-standing recipes.
- Group help when actual workflow complexity warrants; auto-generated help must cover included files and remain accurate. Do not impose fixed columns/emoji or a universal eight-target threshold.
- Platform-specific commands require guarded/verified variants or actionable unsupported errors; never assume uname failure means Windows.
- Prefer an include-visible dependency graph when directories share artifacts. Recursive Make can be appropriate for isolated subsystems; use `$(MAKE)` with explicit target, preserve jobserver flags and test cross-directory dependencies.
- Encode CI ordering explicitly; parallel prerequisites can race. Check/fix/install/deploy/cleanup operations remain distinct with clear permissions and partial-outcome reporting.
- Machine-readable output must not mix decorative help/logs into data. Idempotence means tested intended rerun effects, not absence of all side effects.

### Execution Steps

1. Read files/includes, inspect Make version, current variable definitions, platform targets and caller overrides.
2. Select minimal module/help/variable changes based on demonstrated complexity and consumers.
3. Validate include presence/cycles, variable flavor, parse/runtime conditionals, quoting and parallel dependency graph.
4. Run safe help/preview after inspecting shell/recursive evaluation; test missing optional/required includes, parameters and platform errors in fixtures.
5. Run authorized focused/CI targets and verify outputs/exit codes and downstream compatibility.

### Validation

- Variable values/evaluation timing match intent, override paths documented, no secret/unsafe shell interpolation.
- Required includes fail clearly, optional includes intentional; all public targets documented.
- Platform guards and actual GNU Make features verified; no false preview/no-side-effect guarantee.
- Recursive or included builds preserve dependencies/jobserver semantics and safe ordering.
- CI/agent output accurately reports results, tests not silently skipped and mutating tasks separately authorized.

## References

- [GNU Make variables](https://www.gnu.org/software/make/manual/make.html#Using-Variables)
- [GNU Make conditionals](https://www.gnu.org/software/make/manual/make.html#Conditionals)
- [GNU Make includes](https://www.gnu.org/software/make/manual/make.html#Include)
- [GNU Make parallel execution](https://www.gnu.org/software/make/manual/make.html#Parallel)
