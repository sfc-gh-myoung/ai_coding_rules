---
schema_version: v4.0
rule_version: v3.0.0
description: "Isolated Typer CliRunner tests for actual command paths, output/exits, async execution and ANSI/environment behavior."
last_updated: 2026-10-07
keywords:
  - kw:CliRunner
  - kw:ANSI escape suppression
  - kw:Typer command testing
  - kw:exit code verification
  - kw:CLI mock dependencies
  - kw:async command testing
  - kw:pytest
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 206-python-pytest.md  # Pytest patterns
  optional:
    - 220c-python-typer-rich.md  # Rich integration (affects test output)
---
# Python Typer CLI Testing Strategies

## Scope

**What This Rule Covers:**
Real command/group invocation, exit/stdout/stderr assertions, environment/TTY settings, temp filesystem and async/mock/integration boundaries.

**When to Load This Rule:**
When writing/debugging CLI tests. Read `220-python-typer-cli.md` for app invocation and `220c-python-typer-rich.md` for rendering/version-specific terminal behavior.

## Contract

### Inputs and Prerequisites

- Current app/entrypoint/group structure, conftest/mock conventions and installed Typer/Click/Rich versions.
- Expected exits/output/effects and isolated temporary files/config/env; no production or external-service effects.

### Mandatory

- Reuse existing runner/fixture conventions and test actual callback/single-command/group paths. Subcommands are separate argv tokens; flattened single-command apps may not require a command token. Verify actual help instead of guessing.
- Use deterministic color/terminal settings for plain-text tests: NO_COLOR and TERM=dumb are useful, but actual behavior depends on consoles/force-terminal/Click versions. Assert no escapes when that is the contract; test intentional styled output separately rather than globally forbidding ANSI.
- Assert exit_code and appropriate stdout/stderr/result.exception plus meaningful side effects. Runtime error diagnostics normally belong on stderr; combined output is not always identical across Click versions. Don't call a failed invocation successful because expected text appears.
- Test valid input, parse errors/help/version, missing/malformed files, permissions/config precedence, failed external operations, cancellation/dry-run and machine JSON output. Assert dry-run/help creates no files/network activity.
- Use tmp_path/isolated filesystem and explicit test env/HOME/config to avoid reading/writing real user settings. Actual temp file I/O is valuable; don't mock every filesystem operation and lose path/atomic-write coverage.
- Restore monkeypatch/env/settings/signal state and capture prior overrides; prevent global app state leaking across invocations. CliRunner manipulates interpreter globals and isn't a thread-safe concurrency harness.
- Patch dependencies where the code looks them up and use async-aware mocks; assert calls and awaited effects, not just mocked return. Unit mocks don't validate real database/HTTP/packaging integrations.
- Typer/CliRunner coroutine support must be established for the installed version; ordinary Click-style dispatch doesn't automatically await arbitrary async def commands. Test a verified sync wrapper/async bridge and assert the coroutine actually executed. Test underlying async service separately with project's async runner.
- Test installable entrypoint/subprocess when packaging/env/signals/TTY are relevant and authorized; imported app invocation alone doesn't establish PATH/distribution behavior. Bound subprocesses and cleanup, no new dependency install by implication.
- Use configured project coverage target and focused assertions, not universal 80% or snapshots of every cosmetic help line. Keep real skips/failures visible and protect source/input evidence.

### Execution Steps

1. Read app/tests/tool versions and determine actual command/output/async/side-effect contract.
2. Add focused isolated success/error/help/JSON/effect tests with precise mock boundary.
3. Exercise sequential invocation cleanup and real temp-file behavior; add authorized subprocess cases if needed.
4. Run focused then applicable project checks/coverage and report integration/TTY/platform gaps.

### Validation

- Actual argv paths execute intended callbacks; output/exits/errors/side effects are asserted.
- Plain/styled/JSON streams and env/config/temp state are deterministic and restored.
- Async work actually awaited; external mocks correctly scoped and no unauthorized calls/files.
- Tests and project coverage gates pass; packaging/concurrency evidence is not inferred from CliRunner alone.

## References

- [Typer testing](https://typer.tiangolo.com/tutorial/testing/)
- [Click runner and isolation](https://click.palletsprojects.com/en/stable/testing/)
- [Pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [Rich Console terminal detection](https://rich.readthedocs.io/en/stable/console.html)
