---
schema_version: v4.0
rule_version: v5.0.0
description: "Foundational zsh scripting patterns covering unique zsh features, script structure, variables, functions, and essential practices to leverage zsh's advanced capabilities while maintaining"
last_updated: 2026-10-06
keywords:
  - kw:z shell scripting
  - kw:parameter expansion modifiers
  - kw:emulate setopt
  - kw:1-indexed arrays
  - kw:extended glob patterns
  - kw:namespace pollution prevention
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
  optional:
    - 310a-zsh-advanced-features.md  # Advanced zsh features, completion, and modules
    - 310b-zsh-compatibility.md  # Cross-shell compatibility and migration strategies
---
# Zsh Scripting Core Best Practices

## Scope

**What This Rule Covers:**
Zsh options/emulation, arrays, parameter expansion, scoped functions, startup configuration and safe resources.

**When to Load This Rule:**
When editing zsh scripts/configuration, migrating shell behavior or debugging indexing/glob/option differences.

## Contract

### Inputs and Prerequisites

- Actual zsh version/options, script versus sourced/startup context and target platforms.
- Bash foundation safety guidance read, interpreted under zsh semantics rather than copied blindly.
- Current config/callers and authorized startup/resource changes.

### Mandatory

- Use a zsh shebang for zsh-specific standalone code. In functions, emulate -L zsh localizes options; deliberately set ERR_EXIT/NO_UNSET/PIPE_FAIL or ERR_RETURN according to expected return/exit behavior.
- Native arrays are normally one-indexed; KSH_ARRAYS changes indexing/expansion semantics. Test the active mode instead of assuming Bash equivalence.
- Quote command arguments and use arrays/"$@". zsh does not normally split scalar expansions like Bash, but glob/options still affect behavior; never enable SH_WORD_SPLIT globally as a blanket fix.
- Use local typed variables and namespace custom startup functions; avoid special/read-only parameter collisions and overwriting PATH/system command names.
- Use built-in path/case modifiers where clearer, but validate empty/root paths and actual expansion syntax. Do not substitute undocumented modifiers for correctness.
- Globs use deliberate EXTENDED_GLOB/NULL_GLOB/qualifiers and no-match behavior. Avoid parsed ls, eval, untrusted dynamic patterns or blanket option changes.
- Use zparseopts/autoload/modules only with actual availability and validated argument order; inspect required inputs before indexing $1.
- Own temporary resources/child processes and preserve exit status in cleanup; do not broad-delete dirs or kill unverified PIDs after interruption.
- Startup files depend on login/interactive/system/user contexts; keep expensive/network work out of universal startup and do not claim a simplified order covers every execution mode.
- Cross-shell emulation does not guarantee compatibility. Keep POSIX functions actually portable and test every supported shell; ShellCheck support for Bash is not zsh semantic verification.

### Execution Steps

1. Read script/config/callers and inspect version/context/options before modification.
2. Set function-local emulation/options and minimal named variables/arrays/argument validation.
3. Implement zsh modifiers/globs and resource cleanup with explicit mode/ownership assumptions.
4. Run zsh -n and safe runtime tests for array indices, scalar/quoted expansion, empty/no-match paths, error return and traps.
5. Validate startup/interactive/login and other shells only where supported; report actual platform checks and unverified paths.

### Validation

- Syntax/runtime checks pass for actual target zsh/options, not inferred Bash behavior.
- Array/mode/glob/quoting differences deliberate and special parameters not shadowed.
- Function options local, startup namespace/PATH preserved and no import-time network effects.
- Inputs/tools/resource outcomes verified, traps scoped and status preserved.
- Compatibility tested or explicitly unavailable; no destructive cleanup/upgrade unasked.

## References

- [Zsh manual](https://zsh.sourceforge.io/Doc/)
- [Zsh options](https://zsh.sourceforge.io/Doc/Release/Options.html)
- [Zsh expansion](https://zsh.sourceforge.io/Doc/Release/Expansion.html)
- `310a-zsh-advanced-features.md` for completion/modules/glob detail.
- `310b-zsh-compatibility.md` for cross-shell migration.
