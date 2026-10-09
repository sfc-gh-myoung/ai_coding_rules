---
schema_version: v4.0
rule_version: v3.0.0
description: "The mandatory Pre-Task-Completion Validation Gate for all Python tasks: linting, formatting, type checking, syntax validation, test execution, and documentation updates. Includes the ty vs mypy"
last_updated: 2026-10-06
keywords:
  - kw:pre-task completion gate
  - kw:ty vs mypy decision
  - kw:zero-tolerance validation
  - kw:toolchain-specific validation commands
  - kw:validation failure recovery sequence
  - kw:pre-commit hook automation
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Core Python patterns and toolchain detection
  optional:
    - 201-python-lint-format.md  # Detailed Ruff linting and formatting
    - 206-python-pytest.md  # Comprehensive testing patterns
---
# Python Pre-Task-Completion Validation Gate

## Scope

**What This Rule Covers:**
Actual lint, format, type, syntax and test evidence before Python implementation completion, with scoped recovery and truthful unavailable-check reporting.

**When to Load This Rule:**
Before completing Python changes, configuring validation or investigating a failing check.

## Contract

### Inputs and Prerequisites

- Read Python core, current project manifests/lockfiles, automation, CI and applicable test files.
- Modified Python paths and current owned/staged/unrelated changes identified.
- Authorized existing tools/interpreter, not an assumed global install or substitute toolchain.

### Mandatory

- Run configured lint, formatting check, type checking, syntax validation and relevant tests on modified Python. Use project automation first; focused passes do not replace required full project gates.
- Match actual Ruff/Black/Flake8 and ty/mypy/pyright config, Python support and manager. Do not switch tools or install dependencies just because a check is unavailable.
- A config/lock marker establishes tool choice, not availability or successful execution. Missing test config does not prove a suite absent; discover it or report unknown.
- Never claim completion when an applicable check fails, did not run or returned partial/unknown outcome. Explicit user waivers must be named with their risk.
- Report actual command/exit/results and relevant skips, xfails/deselections/coverage; do not lower thresholds or remove tests merely to pass.
- Distinguish mocked/synthetic check outputs from real execution. A fixed synthetic failure remains reported verbatim and unresolved; it proves neither repaired-code correctness nor unrelated staged-work causation.
- Fix root causes before suppressions. Use specific documented ignore codes only when justified; never blanket noqa/type-ignore or disabled gates.
- Review safe auto-fixes and their scope before applying. Formatting can modify unrelated lines; do not call every broad format operation always safe.
- Preserve unrelated/staged work. Do not stash/reset/whole-file restore to test pre-existing failures without explicit approval; inspect evidence or use an approved isolated comparison instead.
- Changelog records applicable user-facing changes, README updates changed setup/usage; documentation never authorizes a commit.

### Execution Steps

1. Inspect manifests, lockfiles, automation/CI, current diff and check availability. Select actual interpreter/checker, not a guessed version or performance claim.
2. Run check-only lint and formatting, configured type checker and syntax validation on modified files. Use ast parsing or correctly invoked py_compile/compileall; these do not execute tests.
3. Run focused regression tests, then the full suite/gates required by project risk and completion criteria.
4. On failure, read the exact diagnostic, inspect uncertain state and repair only owned changes. Rerun affected checks after reviewing fixes; do not mask errors with a toolchain change.
5. Update required user documentation and record all actual outcomes/limitations. Keep status partial until applicable gates pass or explicit waivers are disclosed.

### Validation

- Actual lint/format/type/syntax checks pass under detected configuration and modified-path scope.
- Tests pass at required scope with coverage threshold preserved; unavailable/synthetic checks never represented as real passes.
- CI/local commands consistent and pinned tool versions respected; any unverified platform/tool gap explicit.
- Recovery preserves staged/unrelated bytes, no broad rollback or unsupported attribution.
- Hook integration uses approved configured tools; do not bypass hooks or install them without authorization.
- ty/mypy selection follows present configuration and framework requirements; verify current plugin/features in documentation rather than asserting universal speed/strictness guarantees.

## References

- [Ruff](https://docs.astral.sh/ruff/)
- [ty](https://docs.astral.sh/ty/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [pytest](https://docs.pytest.org/en/stable/)
- [Python py_compile](https://docs.python.org/3/library/py_compile.html)
