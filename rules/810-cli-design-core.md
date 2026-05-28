# 810-cli-design-core: Command-Line Interface Design Core

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-05-18
**Keywords:** kw:cli, kw:command line, kw:command line interface, kw:clig, kw:clig dev, kw:cli design, kw:cli ux, kw:flags, kw:exit codes, kw:stdout, kw:stderr, kw:no_color, kw:isatty, kw:tty, kw:subcommands, kw:cli help, kw:cli config, kw:xdg, kw:dry-run, kw:machine readable
**TokenBudget:** ~4700
**ContextTier:** Medium
**Depends:** optional:220-python-typer-cli.md, optional:220c-python-typer-rich.md, optional:300-bash-scripting-core.md, optional:600-golang-core.md

## Scope

**What This Rule Covers:**
Language-agnostic design principles for building command-line applications, synthesized as a checklist from the Command Line Interface Guidelines (https://clig.dev). Applies to CLIs written in Python, JavaScript, TypeScript, Go, Rust, Bash, and any other language. Covers philosophy, arguments and flags, output, errors, configuration, environment variables, naming, distribution, telemetry, subcommands, robustness, future-proofing, help, and interactivity.

**When to Load This Rule:**
- Designing a new command-line application or tool
- Reviewing or refactoring an existing CLI for usability
- Adding flags, subcommands, output modes, or configuration to a CLI
- Defining exit codes, error messages, or signal handling
- Choosing between interactive prompts and non-interactive flag-driven flows

## References

### Dependencies

**Must Load First:**

**Related:**
- **220-python-typer-cli.md** - Typer-specific patterns (Python)
- **220c-python-typer-rich.md** - Rich console patterns (Python)
- **300-bash-scripting-core.md** - Bash CLI patterns
- **600-golang-core.md** - Go CLI patterns

### External Documentation

**Official Documentation:**
- [Command Line Interface Guidelines](https://clig.dev) - Canonical source for these principles
- [clig.dev source repository](https://github.com/cli-guidelines/cli-guidelines) - Open-source guide

**Best Practices Guides:**
- [POSIX Utility Argument Syntax](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html) - POSIX conventions
- [GNU Standards for Command Line Interfaces](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html) - GNU long-option conventions
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) - Config and data file locations
- [NO_COLOR](https://no-color.org) - Standard for disabling colored output
- [Semantic Versioning](https://semver.org) - Version numbering for CLI releases

## Contract

### Inputs and Prerequisites

- A CLI application (existing or planned) in any language
- A defined target audience (humans at terminals, scripts, or both)
- Knowledge of the platform(s) the CLI must support (POSIX, Windows, both)
- Access to project source, test suite, and documentation

### Mandatory

- **`--help` and `-h`** on every command and subcommand
- **`--version` and `-V`** on the root command
- **Exit code 0** on success, **non-zero** on failure
- **stdout** for primary output, **stderr** for logs/errors/progress
- **TTY detection** before emitting colors, progress bars, or spinners
- **Long flags** (`--name`) for every short flag (`-n`); short flags are optional
- **Idempotent or `--dry-run` first** for destructive operations
- **Confirmation prompts** for destructive actions when stdin is a TTY; require an explicit `--yes` / `--force` when not

### Forbidden

- **Accepting secrets via flags** (e.g., `--password VALUE`) — leaks to `ps` and shell history; accept via stdin, file, or env var instead
- **Colored output when not a TTY** or when `NO_COLOR` is set or `--no-color` is passed
- **Interactive prompts when stdin is not a TTY** — fail fast with a message describing which flag to pass
- **Silent failures** — every error must produce a non-zero exit and a message on stderr
- **Mixing logs/progress into stdout** when the user pipes the command to another tool
- **Breaking changes without deprecation** — see Future-proofing principles
- **Telemetry without explicit opt-in** and a documented disable mechanism

### Execution Steps

1. Identify the audience(s): humans, scripts, or both — design for both
2. Choose a short, lowercase, memorable command name with no collisions
3. Define arguments and flags using POSIX/GNU conventions and standard flag names
4. Plan output: human-friendly default + machine-readable mode (`--json` / `--plain`)
5. Define exit codes and error message format with actionable remediation
6. Define configuration precedence: flags > env vars > config file > defaults
7. Add TTY-aware behavior for color, prompts, progress, and pagination
8. Add `--help` (with examples), `--version`, `--verbose`/`--quiet`, `--no-input`
9. Plan distribution (single binary preferred; package manager backups)
10. Document everything in `--help`, README, and (if applicable) man pages

### Output Format

- A CLI design specification or implementation that satisfies the Mandatory and Post-Execution Checklist items below
- All user-facing messages, flags, and exit codes documented
- `--help` output that includes at least one example invocation per subcommand

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `AGENTS.md` and `AGENTS.md`.

**CRITICAL:** Before marking any task as complete, ALL of the following checks MUST pass:

**Behavioral Validation:**
- **CRITICAL:** `cmd --help` and `cmd -h` print help and exit 0
- **CRITICAL:** `cmd --version` prints version and exits 0
- **CRITICAL:** Unknown flag exits non-zero and prints a usage hint to stderr
- **CRITICAL:** Successful run prints results to stdout, exits 0; failed run prints diagnostics to stderr, exits non-zero
- **CRITICAL:** `NO_COLOR=1 cmd …` and `cmd … | cat` produce no ANSI color codes
- **CRITICAL:** `cmd … < /dev/null` does not block on prompts when no TTY is present (or fails clearly with a flag hint)
- **CRITICAL:** Destructive subcommands prompt for confirmation on a TTY, or require `--yes` / `--force` otherwise

**Success Criteria:**
- All Post-Execution Checklist items below are checked
- Help output includes at least one example invocation
- A machine-readable output mode (`--json` or `--plain`) exists for any command whose output a script might consume

**Investigation Required:**
1. Read existing CLI source to identify language, framework, and current flag conventions
2. Test current behavior against this checklist before changing anything
3. Identify whether the CLI is consumed by humans, scripts, or both — design must serve all consumers

### Design Principles

- **Human-first, script-friendly:** Default output is for humans; opt into machine-readable with a flag (`--json`, `--plain`, `--quiet`)
- **Composability:** stdin, stdout, stderr; do one thing well; cooperate with pipes
- **Consistency:** Reuse standard flag names (`-h`, `-v`, `-q`, `-o`, `-f`); don't reinvent conventions
- **Discoverability:** `--help` everywhere with examples; clear error messages that name the next step
- **Empathy:** Surprise minimization, escape routes (Ctrl-C always works), forgiving input parsing
- **Robustness:** Idempotency, dry-run, confirmation gates, signal handling, no destructive defaults
- **Conversational:** Treat each invocation as a turn in a dialogue with the user
- **Future-proof:** Stable contracts, explicit deprecations, semantic versioning

### Post-Execution Checklist

**Before Starting:**
- [ ] Identified target audience(s): humans, scripts, or both
- [ ] Identified target platform(s): POSIX, Windows, both
- [ ] Reviewed existing CLI conventions in the project (don't break them silently)

**Philosophy:**
- [ ] Command does one well-defined thing (or is a coherent multi-tool with subcommands)
- [ ] Output is human-readable by default
- [ ] Composes with pipes (reads stdin, writes stdout)
- [ ] Uses traditional UNIX idioms where they apply

**Naming:**
- [ ] Command name is short, lowercase, memorable, and unambiguous
- [ ] Command name does not collide with common existing tools
- [ ] Subcommands use consistent verbs (`create`, `delete`, `list`, `get`)
- [ ] If using `noun verb` or `verb noun` ordering, the choice is consistent across all subcommands

**Arguments and Flags:**
- [ ] Every short flag (`-n`) has a long form (`--name`); long-only is acceptable
- [ ] Standard flag names reused: `-h`/`--help`, `-V`/`--version`, `-v`/`--verbose`, `-q`/`--quiet`, `-o`/`--output`, `-f`/`--force`, `-y`/`--yes`, `-n`/`--dry-run`
- [ ] `--` separator supported to terminate option parsing
- [ ] Boolean flags have `--no-…` opposites where it makes sense
- [ ] Flags are kebab-case (`--dry-run`, not `--dryRun` or `--dry_run`)
- [ ] Required arguments come before optional ones in usage strings
- [ ] Repeatable flags accept multiple occurrences (`-v -v -v` or `-vvv`)
- [ ] Flag values that look like flags are accepted (e.g., `--name=-foo` works)

**Output:**
- [ ] Primary results go to stdout; logs, progress, errors go to stderr
- [ ] Default output is human-readable
- [ ] A machine-readable mode exists: `--json`, `--plain`, or both
- [ ] `--quiet` suppresses non-essential output; `--verbose` adds diagnostic detail
- [ ] Lines are kept short enough to read on a standard terminal (~80 cols when feasible)
- [ ] Symbols (check, cross, arrow) only used when stdout is a TTY and the locale supports them
- [ ] Pagination only when stdout is a TTY (delegate to `$PAGER` / `less`)
- [ ] Tables align cleanly; use `column`-friendly TSV when piped
- [ ] Long-running operations show progress on stderr only when stderr is a TTY

**Color:**
- [ ] No color when stdout is not a TTY
- [ ] No color when `NO_COLOR` environment variable is set (any value)
- [ ] No color when `--no-color` is passed
- [ ] `--color=auto|always|never` flag is supported (auto is default)
- [ ] Color is used to draw attention, never as the only signal (also use text/symbols)

**Errors:**
- [ ] Every error exits non-zero
- [ ] Error messages name (a) what was attempted, (b) what went wrong, (c) what to do next
- [ ] Stack traces / panics are hidden from users by default; revealed under `--debug` or `--verbose`
- [ ] Distinct exit codes for distinct error classes (e.g., usage errors = 2, runtime errors = 1, etc.)
- [ ] Don't print "Error: " in front of an already-clear message; don't repeat the message
- [ ] On usage errors, print a one-line hint (`run cmd --help`)
- [ ] Signals (SIGINT, SIGTERM) are handled gracefully; cleanup runs on Ctrl-C

**Help and Documentation:**
- [ ] `cmd --help`, `cmd -h`, and `cmd help [subcommand]` all work
- [ ] Help text includes a one-line synopsis, usage line, description, options, and at least one example
- [ ] Examples in help cover the most common invocation and one less-obvious case
- [ ] If the CLI is complex enough, a man page or `cmd help <topic>` exists
- [ ] Help is short enough to fit a screen for the most-used commands

**Configuration:**
- [ ] Precedence: command-line flags > environment variables > config file > built-in defaults
- [ ] Config file location follows XDG Base Directory spec on Linux/macOS (`$XDG_CONFIG_HOME` or `~/.config/<cmd>/`)
- [ ] On Windows, config goes in `%APPDATA%\<cmd>\`
- [ ] Config file format is documented (TOML / YAML / JSON)
- [ ] `cmd config` or equivalent inspects current effective configuration
- [ ] Sensitive values (tokens, passwords) are not stored in plain config files by default

**Environment Variables:**
- [ ] Env vars are namespaced with the program name (`MYTOOL_LOG_LEVEL`)
- [ ] Each env var has an equivalent flag, and the flag wins when both are set
- [ ] `NO_COLOR`, `DEBUG`, `EDITOR`, `PAGER`, `HOME`, `XDG_*` are honored where relevant
- [ ] Sensitive env vars (tokens) are not echoed in `--verbose` output

**Secrets and Sensitive Input:**
- [ ] Secrets are NOT accepted via flag values (they leak to `ps` and shell history)
- [ ] Secrets accepted via `--password-file`, `--password-stdin`, or interactive prompt
- [ ] Interactive password prompt disables terminal echo
- [ ] Tokens are redacted in logs and error output

**Subcommands:**
- [ ] Used only when the tool is large enough to justify the complexity
- [ ] Same flag names mean the same thing across all subcommands
- [ ] Global flags work before or after the subcommand where the framework allows
- [ ] Common verbs are consistent (`get`/`list`/`create`/`delete`/`update`)
- [ ] `cmd help <subcommand>` works in addition to `cmd <subcommand> --help`

**Robustness and Safety:**
- [ ] Destructive operations (`delete`, `reset`, `force`) prompt on a TTY, or require `--yes` / `--force` off-TTY
- [ ] `--dry-run` exists for any command that mutates state
- [ ] Operations are idempotent where possible (rerunning is safe)
- [ ] Partial failures are reported clearly; the user knows what succeeded and what didn't
- [ ] Network/IO failures retry with backoff where it makes sense, with a `--no-retry` escape hatch
- [ ] Exits cleanly on Ctrl-C; no orphaned subprocesses or temp files

**Interactivity:**
- [ ] Prompts and TUI elements appear ONLY when stdin is a TTY
- [ ] `--no-input` (or `--non-interactive`) disables all prompts; missing data fails with a flag hint
- [ ] User can always escape (Ctrl-C); for wrappers (SSH, tmux), document the escape sequence
- [ ] Defaults shown in prompts: `Continue? [Y/n]`
- [ ] Prompt text uses sentence case and clear yes/no semantics

**Distribution and Versioning:**
- [ ] Single static binary preferred (Go, Rust); single-file distribution otherwise
- [ ] Available via at least one package manager for the target platform (Homebrew, apt, npm, pipx, …)
- [ ] Versioning follows SemVer
- [ ] `cmd --version` prints version, commit (if applicable), and build date
- [ ] Update / upgrade path documented
- [ ] Releases include checksums and (ideally) signatures

**Telemetry and Analytics:**
- [ ] Telemetry is OFF by default (opt-in)
- [ ] If telemetry is on, the user is told on first run with instructions to disable
- [ ] What is collected is documented in `--help` or a top-level `PRIVACY.md`
- [ ] A single env var or flag fully disables telemetry

**Future-proofing:**
- [ ] Public flag/output contracts are stable across patch and minor versions
- [ ] Removing a flag, command, or output field requires a deprecation cycle and a major bump
- [ ] Deprecated features print a warning to stderr (not stdout) and document the replacement
- [ ] Output schemas (JSON) include a version field if format may evolve

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Accepting Secrets via Command-Line Flags

```text
mytool deploy --password hunter2 --api-token sk_live_…
```

**Problem:** Flag values are visible in `ps`, in shell history, and often in CI logs. The secret leaks to anyone with read access to any of those.

**Correct Pattern:**
```text
mytool deploy --password-stdin                # read from stdin
mytool deploy --password-file ./secret        # read from file with restricted perms
MYTOOL_TOKEN=… mytool deploy                  # read from env var (less safe; OK for CI)
```

**Benefits:** Secrets never appear in process listings or shell history; file-based input integrates with secret managers; stdin works for piping from password managers.

### Anti-Pattern 2: Mixing Logs and Results on stdout

```text
$ mytool list-users | wc -l
[INFO] connecting to api.example.com
[INFO] fetched 42 users
42
44   # incorrect: includes log lines
```

**Problem:** stdout is the program's output channel for downstream consumers. Mixing logs into it breaks every pipe.

**Correct Pattern:**
- Results: stdout
- Logs, progress, status, errors: stderr
- Machine-readable mode (`--json`, `--plain`) emits ONLY data on stdout

**Benefits:** `mytool list-users | wc -l` returns 42; `mytool list-users 2>/dev/null | jq …` works; logs remain visible in interactive use.

### Anti-Pattern 3: Color and Symbols Without TTY Detection

```text
$ mytool status > status.txt
$ cat status.txt
\x1b[32mOK\x1b[0m service-a is up
\x1b[31mFAIL\x1b[0m service-b is down
```

**Problem:** ANSI escape codes pollute redirected output, break log parsers, and corrupt terminals that can't render them. Unicode symbols may not render in all locales or fonts.

**Correct Pattern:**
- Detect `isatty(stdout)` before emitting color or non-ASCII glyphs
- Honor `NO_COLOR` (any value disables color) and `--no-color`
- Provide `--color=auto|always|never` (default: `auto`)
- Fall back to ASCII (`[OK]`, `[FAIL]`) when not a TTY or when locale is C/POSIX

**Benefits:** Output is grep-friendly when redirected, color-rich when interactive, and accessible across locales.

### Anti-Pattern 4: Silent Failure or Generic Exit Codes

```text
$ mytool deploy ./nonexistent.yaml
$ echo $?
1
```

**Problem:** No message on stderr, no hint about what went wrong, single generic exit code. The user (or the calling script) cannot diagnose or branch on the failure.

**Correct Pattern:**
```text
$ mytool deploy ./nonexistent.yaml
mytool: error: file not found: ./nonexistent.yaml
hint: run 'mytool deploy --help' for usage
$ echo $?
2   # 2 = usage / input error; 1 = generic runtime error; 3+ = specific failures
```

**Benefits:** Humans see what's wrong and what to try next; scripts can branch on exit codes; CI logs surface the failure cause.

### Anti-Pattern 5: Destructive Default Behavior

```text
$ mytool migrate
Dropping 3 tables...
Migration complete.
```

**Problem:** No confirmation, no dry-run, no way to preview impact. One typo, accidental shell history expansion, or wrong working directory causes data loss.

**Correct Pattern:**
- Default to a preview (`--dry-run` is implicit, or `migrate plan` and `migrate apply` are separate verbs)
- Prompt for confirmation when stdout is a TTY; print a summary first
- Require `--yes` / `--force` to skip confirmation in non-interactive contexts
- Log every destructive action with enough detail to support a rollback investigation

**Benefits:** Mistakes are caught before data is lost; CI flows remain non-interactive via `--yes`; users build trust in the tool.

### Anti-Pattern 6: Prompts in Non-Interactive Contexts

```text
$ echo "" | mytool init
Project name? _   # blocks forever; CI job times out
```

**Problem:** The CLI assumes a human is present. In scripts, CI, and Docker builds, prompts hang the process and consume a build slot until the timeout fires.

**Correct Pattern:**
- Detect `isatty(stdin)` before prompting
- When stdin is not a TTY, fail with a clear hint: `error: --name is required when stdin is not a TTY`
- Support `--no-input` to force non-interactive mode even on a TTY (useful for testing)

**Benefits:** Scripts fail fast with actionable messages; humans get rich prompts; the same binary works in both contexts.
