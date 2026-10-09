---
schema_version: v4.0
rule_version: v3.0.0
description: "Language-agnostic design principles for building command-line applications, synthesized as a checklist from the Command Line Interface Guidelines (https://clig.dev). Applies to CLIs written in"
last_updated: 2026-10-06
keywords:
  - kw:clig.dev principles
  - kw:TTY detection
  - kw:stdout stderr separation
  - kw:destructive operation confirmation
  - kw:machine-readable output modes
  - kw:XDG Base Directory
  - kw:typer
token_budget: ~1200
context_tier: Medium
depends:
  optional:
    - 220-python-typer-cli.md  # Typer-specific patterns (Python)
    - 220c-python-typer-rich.md  # Rich console patterns (Python)
    - 300-bash-scripting-core.md  # Bash CLI patterns
---
# Command-Line Interface Design Core

## Scope

**What This Rule Covers:**
Human-friendly, script-safe CLI arguments, output, errors, configuration, interactivity, destructive-operation safety and stable distribution contracts.

**When to Load This Rule:**
When designing/reviewing commands, flags, output modes, exit codes, prompts or configuration in any implementation language.

## Contract

### Inputs and Prerequisites

- Existing CLI source/framework, users, supported platforms and scripting consumers.
- Public command/output contracts, configuration precedence and safety/privacy requirements.
- Safe test fixtures and explicit authorization for real mutations/network/deployment tests.

### Mandatory

- Provide `--help`/`-h` for commands/subcommands and root `--version`/`-V`; help succeeds without connecting to services or modifying state.
- Use coherent command/subcommand names and consistent verb/noun order. Long kebab-case flags accompany short aliases; support `--` termination and values beginning with hyphens using documented syntax.
- Preserve established framework/project conventions. Add subcommands only when complexity warrants; do not add every generic CLI flag speculatively.
- Exit zero on success, nonzero on failure; document meaningful usage/runtime/cancellation exit codes. Explain attempted action, failure and next step on stderr.
- Put primary results on stdout and diagnostics/progress on stderr. Stable JSON/plain output must contain data only, with documented schemas and completeness/partial-failure semantics.
- Detect the relevant stream's TTY before colors, spinners, pagination or Unicode; honor NO_COLOR and no-color overrides, provide ASCII/plain fallback and do not convey meaning solely by color.
- Prompt only on interactive stdin; no-input/noninteractive mode fails fast with a missing-flag hint rather than blocking. Ctrl-C/SIGTERM must cancel cleanly and report partial effects.
- Destructive operations default to preview/plan where feasible, clearly name affected resources and require confirmation/explicit noninteractive approval. A yes/force flag is not authority to exceed approved scope.
- Never accept actual secrets as ordinary flag values or print them in logs. Integrate approved secret manager/stdin/restricted-file/password prompts; disable echo for interactive secret input.
- Document precedence (normally flags > namespaced env > config > defaults) and effective-config inspection with redaction. Use platform-appropriate config locations, not plaintext-secret defaults.
- Bound safe retries/backoff and disclose partial/unknown outcomes; inspect uncertain non-idempotent mutations before replay. Clean only owned temporary resources, never broad user state.
- Telemetry requires explicit opt-in, documented collection and a complete disable mechanism. Preserve public flags/output across compatible releases; deprecate breaking changes with replacements and real migration guidance.

### Execution Steps

1. Inspect current conventions and consumer tests; identify human/script/platform requirements and changed public behavior.
2. Define consistent arguments/help/examples, primary output/error streams, machine-readable schema and exit codes.
3. Implement TTY-aware prompts/color/progress, config precedence/redaction and explicit destructive-action gates.
4. Add safe boundary tests for unknown flags, missing input, piped/redirected output, no-input/NO_COLOR, signals, partial failure and confirmation scope.
5. Validate common invocations and documentation on supported platforms; exercise real side effects only when separately authorized.
6. Review distribution/version/checksum/update behavior appropriate to the language/platform; report actual tested support, not universal binary/package guarantees.

### Validation

- Help/version exit zero without side effects; invalid arguments fail with stderr usage hints.
- Results/stdout and diagnostics/stderr remain separate; JSON/plain output parses and schemas are stable.
- Non-TTY/no-input does not prompt; color/progress/Unicode behavior respects stream and overrides.
- Secrets never appear in argv/examples/logs, effective config redacted and precedence tested.
- Mutations require scoped approval, previews accurate, cancellation/partial outcomes reported, retry semantics safe.
- Public contracts, deprecations, examples and platform claims match tests; telemetry off unless explicitly enabled.

## References

- [Command Line Interface Guidelines](https://clig.dev/)
- [GNU command-line conventions](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)
- [XDG base directories](https://specifications.freedesktop.org/basedir-spec/latest/)
- [NO_COLOR](https://no-color.org/)
