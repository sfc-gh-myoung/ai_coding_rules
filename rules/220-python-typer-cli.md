---
schema_version: v4.0
rule_version: v5.0.0
description: "Typed Typer commands, stable invocation/help/exit contracts, thin business boundaries, safe output and packaging."
last_updated: 2026-10-07
keywords:
  - kw:Typer CLI
  - kw:typer.Argument
  - kw:typer.Option
  - kw:exit code handling
  - kw:console script entry points
  - kw:Rich terminal output
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Core Python patterns and uv usage
  optional:
    - 201-python-lint-format.md  # Ruff linting and formatting standards
    - 203-python-project-setup.md  # Python project structure and uv setup
    - 230-python-pydantic.md  # Pydantic integration with Typer
---
# Python Typer CLI Development Best Practices

## Scope

**What This Rule Covers:**
Command/group structure, typed arguments/options, help, errors, async orchestration, signals, completion and console entry points.

**When to Load This Rule:**
When building/modifying Typer commands. Read `220a-python-typer-config.md` for settings, `220b-python-typer-testing.md` for tests and `220c-python-typer-rich.md` for terminal rendering.

## Contract

### Inputs and Prerequisites

- Existing app/group callbacks/entrypoints, installed Typer/Click/Rich versions, toolchain and current command compatibility.
- Intended inputs/outputs/exits, path/data authority, noninteractive behavior and supported platforms.

### Mandatory

- Read current CLI modules, project.scripts and option aliases before adding commands. Keep business logic callable without CLI; do not replace argparse/Click elsewhere unasked or force new module layouts based on command count.
- Respect existing manager/dependency locks and installed Typer packaging; don't prescribe stale typer[all] extras or install by implication. Console entrypoint must reference the actual callable included in the built distribution.
- Use typed Annotated metadata where supported and consistent, explicit names/help and valid optional/default types. Avoid mutable shared defaults; confirm installed API before inventing default_factory options.
- Distinguish arguments/options, repeatable values, enum/ranges/path modes and group invocation. Typer single-command flattening differs from grouped apps; callbacks/no-args-help/aliases must preserve actual compatibility. Configure -h help explicitly if desired; it isn't guaranteed default.
- Validate intended read/write paths, extensions/permissions and explicit output location. Dry-run/help/completion must not mutate, install, contact services or create directories through eager callbacks. A path validator isn't ownership/deletion approval.
- Use documented exit codes: success zero, parse errors normally two, runtime failures nonzero and interruption appropriate to platform. raise typer.Exit/Abort deliberately; don't catch them in a broad handler and turn successful cancellation/help into unexpected failure.
- Send machine results to stdout and diagnostics/progress to stderr; structured mode contains parseable output without Rich banners/ANSI. Escape or disable Rich markup for untrusted filenames/errors; never print credentials/full private exception bodies by default.
- Expected failures give actionable safe context; unexpected errors retain internal trace only under approved debug policy. Don't return normally after a failed operation or treat absent output as success.
- Typer coroutine execution support depends on actual version/interface. Use a verified synchronous entry wrapper invoking the async service when required; CliRunner doesn't automatically make arbitrary async command functions awaited. Bound concurrency/requests and close clients.
- For long-running work define cancellation/partial-output and uncertain-write recovery; preserve exit status and existing signal handlers in finally. Custom signal installation is platform/main-thread dependent; don't claim one Unix convention covers every host.
- Completion callbacks are read-only, bounded and secret-safe; use supported shell_complete interface or existing compatible API. Installing completion modifies shell configuration and needs approval.
- Document command examples/version/configuration sources and test installed entrypoint/help as well as imported app. No hardcoded home paths, arbitrary output overwrites or unapproved publication.

### Execution Steps

1. Inspect current app/toolchain/entrypoint and define compatible command/result/error contract.
2. Implement minimal typed command and thin service call, safe path/output/config and cleanup boundaries.
3. Test actual group/single invocation, help, validation, failure/noninteractive/cancellation and structured output.
4. Run project checks and permitted packaging/entrypoint smoke; report supported-platform gaps.

### Validation

- Parameters/help/groups/aliases and packaged entrypoint work under actual installed versions.
- Runtime/parse/interruption exits and stdout/stderr/JSON contracts are asserted.
- Dry-run/help/completion are side-effect-free and paths/secrets/partial writes scoped safely.
- Async service actually executes, resources/signals clean up and project checks pass; no unauthorized installation/publication.

## References

- [Typer arguments/options](https://typer.tiangolo.com/tutorial/)
- [Command groups](https://typer.tiangolo.com/tutorial/subcommands/)
- [Testing](https://typer.tiangolo.com/tutorial/testing/)
- [Click exceptions](https://click.palletsprojects.com/en/stable/exceptions/)
- [Packaging entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
