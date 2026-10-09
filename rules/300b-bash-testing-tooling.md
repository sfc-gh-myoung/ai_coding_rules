---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive bash testing, debugging, and modern tooling integration including ShellCheck, CI/CD workflows, and development practices to ensure script quality and reliability."
last_updated: 2026-10-06
keywords:
  - kw:ShellCheck
  - kw:Bats
  - kw:bash unit testing
  - kw:pre-commit hooks
  - kw:debug mode implementation
  - kw:cicd shell validation
token_budget: ~800
context_tier: Medium
depends:
  required:
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
  optional:
    - 300a-bash-security.md  # Security testing considerations
---
# Bash Testing and Tooling

## Scope

**What This Rule Covers:**
Safe shell syntax/static/format/behavior tests, error paths, debugging and CI/hook integration.

**When to Load This Rule:**
When testing shell helpers, configuring ShellCheck/Bats or diagnosing script failures.

## Contract

### Inputs and Prerequisites

- Existing scripts/tests/automation and actual Bash/ShellCheck/formatter/test versions.
- Authorized disposable fixtures and mock external boundaries, not real deployment targets.

### Mandatory

- Inspect source before sourcing/running it; a script may deploy/delete on import unless main execution is guarded. Test reusable functions through existing seams or safe subprocess fixtures.
- Run bash -n, configured ShellCheck and shfmt plus behavioral tests (Bats or existing framework). Do not install a new framework/hook/CI action without scope/approval.
- Test state-mutating/input/external/credential boundaries with failure cases as well as happy path, including spaces/newlines/dashes, missing tools, permission, signals and partial outcomes.
- Assertions fail nonzero; a homegrown runner that prints FAIL then exits0 is not validation. Arithmetic post-increment at zero can fail under errexit; test actual strict-mode behavior.
- Use scoped temps/cleanup and controlled external command doubles. Do not send destructive test strings to real system resources or cloud endpoints.
- Specific ShellCheck exceptions need real justification; unavailable linter is not reason to add disable comments or declare manual inspection equivalent.
- Debug/trace stderr output must redact secrets and private data; set-x can expose expanded credentials. Capture safe line/function/status evidence rather than unconditional raw commands.
- CI/local/hook tools pinned and commands coherent; no claim latest hosted CI green from local tests. Preserve project coverage policy; counting function calls is not branch/line coverage.

### Execution Steps

1. Read scripts/config/tests and identify actual safe test entry points/runtime support.
2. Run static syntax/lint/format and minimal regression/error-path tests in isolated local fixtures.
3. Add scoped tests for demonstrated defects, cleanup/cancellation and failure propagation; don't build a parallel bespoke framework unnecessarily.
4. Diagnose failures with redacted evidence and bounded retries only for safe checks; preserve unsuccessful recorded benchmarks where required.
5. Run required full automation and document actual coverage/selection/platform limitations and unverified CI.

### Validation

- Syntax/static/format/test commands actually run and fail on demonstrated bad behavior.
- Assertions and runner exit codes meaningful, resources cleaned on error/signals and protected files unchanged.
- Input/error/external boundaries covered, no real deployment/destruction during tests.
- Traces/logs redact secrets; tool absence reported rather than suppressed.
- CI/hook integration is authorized/current, coverage metrics real and no false hosted results.

## References

- [ShellCheck wiki](https://github.com/koalaman/shellcheck/wiki)
- [Bats documentation](https://bats-core.readthedocs.io/en/stable/)
- [shfmt](https://github.com/mvdan/sh)
- [Google shell guide](https://google.github.io/styleguide/shellguide.html)
