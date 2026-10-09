---
schema_version: v4.0
rule_version: v3.0.0
description: "Consistent Rich consoles, safe terminal text, stdout/stderr contracts, TTY-aware progress and per-invocation state."
last_updated: 2026-10-07
keywords:
  - kw:Rich library
  - kw:Typer Rich integration
  - kw:shared console module
  - kw:dual console stdout stderr
  - kw:color detection environment
  - kw:Live progress display
  - kw:pytest
token_budget: ~950
context_tier: Medium
depends:
  required:
    - 220-python-typer-cli.md  # Core Typer CLI patterns
  optional:
    - 220b-python-typer-testing.md  # Testing with ANSI suppression
---
# Python Typer CLI Rich Integration

## Scope

**What This Rule Covers:**
Reusable console configuration, untrusted text, pipeable outputs, progress/rendering width and invocation state.

**When to Load This Rule:**
When adding Rich tables/status/Live output or diagnosing terminal/test rendering. Read `220b-python-typer-testing.md` for runner isolation.

## Contract

### Inputs and Prerequisites

- Existing console/output helpers, Typer/Click/Rich versions, stream/TTY/color policy and machine-output contract.
- Supported terminal sizes, untrusted/private text and test capture behavior; current callback/context state.

### Mandatory

- Reuse established console/configuration owners rather than create inconsistent globals in every command. Dependency-injected or file-target consoles are valid when lifecycle/stream demands differ; no blanket one-instance rule.
- Data/results go to stdout; progress/status/errors to stderr. JSON/CSV modes must be machine-parseable without banners, tables, ANSI or incidental log messages. Set exit status independently from colors/status labels.
- Respect terminal detection and explicit color options, NO_COLOR/TERM/dumb and existing CI policy. Don't force_terminal=True just because pytest isn't imported; pipes/files can otherwise acquire escapes. no_color disables colors, not necessarily every style/cursor sequence.
- Escape/disable markup for untrusted paths/data/errors; construct Text for literal content when useful. Rich markup escaping alone doesn't sanitize malicious terminal control sequences; apply a bounded literal/control policy where external data is printed.
- Use consistent helpers and per-invocation ctx.obj/config, not mutable global verbose/format settings leaking between commands/tests. Callbacks must preserve nested command state intentionally.
- Match output width/overflow to supported terminal sizes: fold meaningful text, ellipsize/crop only when truncation is clear and full details remain accessible. Fixed width 120 doesn't guarantee long content won't wrap; test narrow terminals.
- Use status for a single ongoing operation, Progress for measured totals and Live for multiple evolving rows. Keep displays on stderr, bounded refresh and context-manager cleanup; non-TTY mode should emit useful static status rather than cursor control spam.
- Mark done only after operation/required checks succeed. Preserve per-item failures and return nonzero for failed work; don't catch every exception, show an error row, then claim the whole sync succeeded.
- Files use explicit encoding/newline, safe authorized destinations and a nonterminal console or plain serializer. Verify no escape sequences in actual bytes; printing a styled confirmation doesn't establish the file exists or data is complete.
- Optional enum choices improve constrained options but don't replace runtime/domain validation. Rich output isn't a reason to invent packages/install requirements, change CLI choices, expose secrets or upload reports.

### Execution Steps

1. Read console/config/callback and stdout/stderr conventions; define literal/machine/TTY behavior.
2. Add minimal shared/injected rendering with escaping, width and progress lifecycle.
3. Test plain/styled/JSON/file/narrow-terminal/failure cases and successive invocation state.
4. Run project checks and report real stream/file behavior and any terminal/platform gaps.

### Validation

- stdout/stderr and machine formats remain clean; exit codes reflect operation outcomes.
- TTY/color/control/markup handling safe for untrusted text, redirected files and CI.
- Tables fit supported widths, progress closes on failure/cancellation, state doesn't leak.
- File bytes and confirmations truthful; no hidden install/external sends.

## References

- [Rich Console](https://rich.readthedocs.io/en/stable/console.html)
- [Rich markup](https://rich.readthedocs.io/en/stable/markup.html)
- [Rich Live](https://rich.readthedocs.io/en/stable/live.html)
- [Rich tables](https://rich.readthedocs.io/en/stable/tables.html)
