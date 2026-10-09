---
schema_version: v4.0
rule_version: v5.0.0
description: "Zsh compatibility strategies, bash migration patterns, and cross-shell scripting best practices for mixed environments, ensuring seamless transitions and portable script solutions."
last_updated: 2026-10-06
keywords:
  - kw:bash vs zsh
  - kw:emulate mode
  - kw:array indexing differences
  - kw:POSIX compliance
  - kw:shell detection
  - kw:setopt explicit
token_budget: ~900
context_tier: Low
depends:
  required:
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
  optional:
    - 310-zsh-scripting-core.md  # Foundation zsh scripting patterns
    - 310a-zsh-advanced-features.md  # Advanced zsh features
    - 310c-zsh-compatibility-platforms.md  # Platforms, testing, and performance
---
# Zsh Compatibility and Cross-Shell Scripting

## Scope

**What This Rule Covers:**
Explicit shell targets, syntax/option differences, POSIX portability and evidence-driven Bash/zsh migration.

**When to Load This Rule:**
When converting shell code or claiming compatibility across Bash, zsh or POSIX shells.

## Contract

### Inputs and Prerequisites

- Existing scripts/callers/startup context and actual supported shell versions/platforms.
- Authorized migration scope, recoverable owned beforeimages and safe runtime fixtures.

### Mandatory

- Choose actual target shells based on requirements, not arbitrary file-size/iteration thresholds. Match shebang to syntax; executing a script with an explicit different interpreter ignores its shebang choice.
- POSIX code must avoid shell-specific arrays, [[ ]], setopt/shopt/local assumptions and incompatible parameter expansions. Runtime branches cannot hide syntax another parser rejects.
- zsh emulate -L sh approximates selected behavior, not complete Bash-library compatibility. Native arrays/indexing, scalar splitting, globbing and regex captures need explicit tests/options.
- Detect actual shell/runtime capabilities using reliable version/context evidence, not $0 filename alone or uname failure guesses. Reuse a validated helper when needed without adding one gratuitously.
- Feature checks must themselves parse safely in every intended shell and localize option changes; don't execute zsh-only modifiers in a purported portable probe.
- Translate Bash declare/shopt/BASH_SOURCE/BASH_REMATCH deliberately to zsh semantics and verify sourced versus executed path detection. No blind sed conversion or invented compatibility shim that overwrites builtins.
- Quote arrays/arguments and preserve original values, no unsafe eval/dynamic glob expansion on untrusted patterns.
- Preserve original/recoverable source and unrelated edits. Backup creation success checked; rollback only task-owned bytes after inspecting current drift, not whole-file overwrite of concurrent changes.
- Test actual supported shells/platforms; missing binary means unverified, not silent skip or install permission. Bash ShellCheck is not zsh syntax/semantic certification.

### Execution Steps

1. Read current scripts/config/callers and list supported shell/version/environment contracts.
2. Identify incompatible syntax/options and choose POSIX subset or separate shell-specific implementation based on actual needs.
3. Apply scoped semantic migration, deliberate function-local emulation and safe feature routing.
4. Run each target shell's syntax check and safe runtime boundary tests for arrays, expansion, globs, regex, sourcing and status/traps.
5. Compare outputs/side effects with original behavior and report tested shells, unsupported paths and exact failures.

### Validation

- Shebang/actual parser/options match intended syntax; no unreachable incompatible syntax hidden in branches.
- Array indices/splitting/glob/regex/source-path behavior tested across claimed targets.
- Missing tools/shells explicit, no fake portability from static search.
- Migration preserves data/authority/unrelated edits, backups/rollback scoped and output consistent.
- No unrequested shell install/startup change or broad automatic transformation.

## References

- [Zsh compatibility FAQ](https://zsh.sourceforge.io/FAQ/zshfaq03.html)
- [POSIX shell](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Zsh emulation](https://zsh.sourceforge.io/Doc/Release/Shell-Builtin-Commands.html)
- `310c-zsh-compatibility-platforms.md` for platform testing and benchmarks.
