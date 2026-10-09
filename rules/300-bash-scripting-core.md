---
schema_version: v4.0
rule_version: v5.0.0
description: "Foundational bash scripting patterns covering script structure, variables, functions, and essential error handling practices to create reliable, maintainable, and portable shell scripts."
last_updated: 2026-10-06
keywords:
  - kw:set -euo pipefail
  - kw:variable quoting
  - kw:trap cleanup handlers
  - kw:shellcheck static analysis
  - kw:local function variables
  - kw:bash script structure
  - kw:taskfile
token_budget: ~1000
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - 300a-bash-security.md  # Security patterns for Bash scripts
    - 300d-bash-advanced.md  # Advanced patterns, performance, code style, debugging
    - 820-taskfile-automation.md  # Build automation patterns
---
# Bash Scripting Core Best Practices

## Scope

**What This Rule Covers:**
Quoted arguments, explicit failures, input validation, functions, owned temporary resources and portable Bash scripts.

**When to Load This Rule:**
When modifying Bash scripts/helpers, traps, pipelines, argument parsing or shell validation.

## Contract

### Inputs and Prerequisites

- Existing scripts, shebang, actual Bash/platform support and required commands.
- Current callers/tests, cleanup/resource ownership and explicit mutation permissions.
- ShellCheck/shfmt or project-configured syntax/format tools available.

### Mandatory

- Use an appropriate Bash shebang and deliberate strict handling, usually set -euo pipefail for standalone scripts. errexit has conditional/pipeline exceptions; explicitly check critical commands and do not rely on strict mode as universal error detection.
- Quote argument expansions/substitutions, use arrays for argument lists and forward with "$@". Avoid eval, unsafe source or command strings from user data.
- Check argument counts before reading $1 under nounset; use deliberate optional defaults, local variables and descriptive names. Split declarations from command substitution when declaration builtins would mask exit status.
- Validate exact inputs, supported operations, files/directories/tools and approved target scope before mutation. Missing tools/permissions produce actionable stderr errors, not silent fallback or installation.
- Keep results on stdout and diagnostics on stderr, use printf for predictable text and meaningful nonzero exit codes. Do not print successful completion after partial/failed operations.
- Cleanup only resources created/owned by this invocation. Use mktemp, validated nonempty paths, exit-status-preserving traps and controlled cancellation of owned child processes.
- Do not broad rm/cache cleanup/restore, follow untrusted symlinks or overwrite staged/unrelated files. File ownership alone does not make sourced code trusted; prefer a structured config parser over source.
- Process filenames with safe globs/null-delimited paths, not parsed ls or whitespace-separated substitutions. Handle no-match globs, leading dashes and newline/space names.
- Bash4-only features are not available in default macOS Bash3.2; inspect actual version and preserve project's support policy rather than demanding unrequested upgrades.
- Keep nontrivial logic in maintained scripts, not nested quoted inline shell code; structured data uses a parser, not fragile grep/awk approximations.

### Execution Steps

1. Read script/callers/tests and current platform/tool/version assumptions.
2. Implement minimal validated argument/function flow with arrays, quoting and explicit error propagation.
3. Add lifecycle cleanup only for actual owned resources, preserving status and cancellation behavior.
4. Run bash -n, configured ShellCheck and shfmt checks, then safe regression cases for empty inputs, special filenames, missing tools, permission and failure paths.
5. Run required project checks and report actual outcomes/unsupported platforms. Do not execute deployment/destructive targets merely to validate syntax.

### Validation

- Syntax/lint/format pass on supported Bash versions; exceptions documented specifically.
- Quoting/arrays/defaults preserve arguments and no unsafe eval/source/data-command mixing.
- Required inputs/tools checked before effects and failures propagate accurately.
- Traps preserve exit code, clean owned resources only and no unrelated files/staged work affected.
- Filename/no-match/leading-dash cases and cancellation/partial outcomes tested safely.

## References

- [Bash manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/)
- [Google shell guide](https://google.github.io/styleguide/shellguide.html)
- [Bash pitfalls](https://mywiki.wooledge.org/BashPitfalls)
- `300a-bash-security.md` for security boundaries.
- `300b-bash-testing-tooling.md` for shell test tooling.
