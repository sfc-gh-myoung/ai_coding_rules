---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced bash scripting patterns including associative arrays, performance optimization with built-ins, code style and formatting standards, ShellCheck integration, debugging techniques,"
last_updated: 2026-10-06
keywords:
  - kw:associative arrays
  - kw:parameter expansion
  - kw:shellcheck
  - kw:debug mode
  - kw:bash built-ins
  - kw:usage documentation
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 300-bash-scripting-core.md  # Foundation bash patterns (variables, functions, error handling)
  optional:
    - 300a-bash-security.md  # Comprehensive security patterns for Bash scripts
    - 300b-bash-testing-tooling.md  # Testing frameworks and CI/CD tooling
---
# Bash Advanced Patterns and Style

## Scope

**What This Rule Covers:**
Version-supported arrays/expansion, maintainable help/debugging, safe permissions and measured shell optimization.

**When to Load This Rule:**
When using advanced Bash features or reviewing performance, style, diagnostics and ShellCheck behavior.

## Contract

### Inputs and Prerequisites

- Actual Bash versions/platforms, script/caller/tests and current style/lint configuration.
- Demonstrated performance need and authorized resource/configuration scope.

### Mandatory

- Associative arrays need Bash4+ and some tests/expansions need later versions; guard actual required feature support, especially macOS Bash3.2.
- Prefer built-ins/parameter expansion when equally clear/correct; substitutions like path%/* are not universal dirname equivalents for slashless/root/trailing-slash inputs. Test edge semantics before replacing working commands.
- Use local variables, meaningful constants and project indentation/function naming. Do not rewrite adjacent code just to match a generic four-space rule.
- Distinguish unset/empty/default expansion and safe arrays under nounset. Split command substitutions from local/readonly declarations to retain failures.
- Arithmetic commands return status based on result; post-increment at zero can trigger errexit. Use deliberate increment forms or explicit error handling, not an unsafe copied pattern.
- Help names real arguments/options/examples and exits safely without side effects; diagnostics/debug output stderr, primary return data stdout.
- Debug tracing is opt-in and redacted; set-x/PS4 can expose secrets. Keep secret operations untraced, no unconditional raw command dump.
- Specific ShellCheck directives need justification and do not authorize sourcing arbitrary configs. Validate safe source paths/content or use structured parsing.
- mktemp creates restrictive resources on many platforms; verify actual permissions/umask and apply required policy without modifying unrelated files. Cleanup only owned temps, never broad chmod/rm defaults.
- Optimize from measurements; built-in/subprocess tradeoffs need semantics and real benefit, not universal no-external-command mandates.

### Execution Steps

1. Inspect runtime support, source/tests/style and exact bottleneck or usability problem.
2. Apply minimal arrays/expansion/help/debug changes, validating option and edge behavior.
3. Review strict-mode arithmetic, substitutions, cleanup/permissions and secret tracing.
4. Run syntax/ShellCheck/format plus actual regression cases and benchmark only relevant operations.
5. Document required versions/usage and tested performance or unavailable checks.

### Validation

- Runtime feature guards correct, parameter expansion preserves edge inputs and arrays/quotes safe.
- Strict-mode failures not hidden by declaration builtins/arithmetic/subshells.
- Help/diagnostics accurate, debug redacted and no stdout pollution.
- Temporary permissions/cleanup confined, suppressions specific and no unsafe source.
- Static/behavior tests pass and optimization evidence distinguishes estimates from measurements.

## References

- [Bash expansion](https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html)
- [Bash arithmetic](https://www.gnu.org/software/bash/manual/html_node/Shell-Arithmetic.html)
- [ShellCheck](https://www.shellcheck.net/)
- [Google shell style](https://google.github.io/styleguide/shellguide.html)
