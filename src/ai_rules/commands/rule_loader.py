"""``ai-rules rule-loader`` CLI sub-app.

Commands:
- ``eval`` - drive the live SDK against fixtures (pass/fail). 2-signal
  agreement and citation-drift checks are unconditional assertions; any
  failure is a hard blocker.
- ``validate`` - trigger-evidence invariant only (no agent).
- ``list`` - registered fixtures.
- ``doctor`` - verify SDK pin and connection.
- ``create`` - drive the live SDK with a candidate prompt and print a
  paste-ready YAML snippet for new fixture authoring.
- ``refresh`` - re-run an existing fixture and either diff or rewrite
  its expectations against the live-loaded set.
"""

from __future__ import annotations

import contextlib
import difflib
import enum
import os
import sys
from collections.abc import Sequence
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ai_rules._shared.console import (
    console,
    err_console,
    is_progress_capable,
    log_error,
    log_info,
    log_success,
    log_warning,
)
from ai_rules._shared.paths import find_project_root
from ai_rules.rule_loader_eval import SDK_PIN
from ai_rules.rule_loader_eval.annotations import (
    parse_preservation_annotations_from_path,
)
from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS
from ai_rules.rule_loader_eval.diagnostics import (
    format_citation_drift_warning,
    format_debug,
    format_disagreement_warning,
    format_timing_lines,
)
from ai_rules.rule_loader_eval.engine import RunResult
from ai_rules.rule_loader_eval.fixtures import (
    Fixture,
    FixtureValidationError,
    current_updated_timestamp,
    load_fixture,
    load_fixtures,
    read_prompt,
    read_updated,
    validate_rendered_snippet,
)
from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata
from ai_rules.rule_loader_eval.snippet import format_fixture_snippet

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

rule_loader_app = typer.Typer(
    name="rule-loader",
    help="Rule Loading Evaluator: live-agent sanity check.",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_FIXTURE_FAIL = 1
EXIT_DRIFT = 2
EXIT_SDK_OR_CONN = 3
EXIT_FIXTURE_INVALID = 4
EXIT_INTERNAL = 5

# Alias: infra-error exit code (SDK / model / connection unreachable).
# Reuses EXIT_SDK_OR_CONN (3) so existing CI/scripts that distinguish
# 0/1/3 keep working.
EXIT_INFRA_ERROR = EXIT_SDK_OR_CONN


def _resolve_connection(connection: str | None) -> str | None:
    """Return the resolved connection name, or None if no connection is configured.

    Preference order: explicit ``--connection`` arg > ``SNOWFLAKE_CONNECTION_NAME`` env var.
    Returns ``None`` when neither is set.
    """
    if connection:
        return connection
    env_value = os.environ.get("SNOWFLAKE_CONNECTION_NAME")
    return env_value if env_value else None


def _require_connection_or_exit(connection: str | None) -> str:
    """Resolve the connection or exit with a clear banner.

    Called BEFORE any SDK invocation by commands that need a live agent
    (eval, refresh, refresh-all). Catches the most common silent failure:
    SDK fails with stop_reason=error_during_execution because no connection
    is configured.
    """
    resolved = _resolve_connection(connection)
    if not resolved:
        log_error("=" * 78)
        log_error("INFRA ERROR: No Snowflake connection configured.")
        log_error("The agent SDK will fail with stop_reason=error_during_execution.")
        log_error("")
        log_error("Fix one of:")
        log_error("  1. export SNOWFLAKE_CONNECTION_NAME=<connection-name>")
        log_error("  2. Pass --connection <connection-name> to this command")
        log_error("  3. Run `snow connection list` to see configured connections")
        log_error("=" * 78)
        raise typer.Exit(EXIT_INFRA_ERROR)
    return resolved


def _fixtures_dir(project_root: Path) -> Path:
    return project_root / "fixtures" / "rule_loader_eval"


def _rules_dir(project_root: Path) -> Path:
    return project_root / "rules"


# ---------------------------------------------------------------------------
# ProgressTracker (shared Rich progress UI)
# ---------------------------------------------------------------------------


class ProgressMode(enum.StrEnum):
    """Selected presentation mode for live progress UI."""

    AUTO = "auto"
    SCREEN = "screen"
    RICH = "rich"
    PLAIN = "plain"
    JSON = "json"
    NONE = "none"


def resolve_progress_mode(value: str | None) -> ProgressMode:
    """Resolve a ``--progress`` flag value to a concrete mode.

    Accepts ``auto`` (default), ``screen``, ``rich``, ``plain``, ``json``, or
    ``none``.

    - ``auto`` (or ``None``) → ``SCREEN`` when stderr is a capable TTY, else
      ``NONE``.
    - ``screen`` → ``SCREEN`` (Rich alternate-screen Live dashboard).
    - ``rich`` → ``SCREEN`` (back-compat alias; the legacy normal-buffer Rich
      live UI was retired because SDK chatter could corrupt the bar).
    - ``plain`` / ``json`` / ``none`` → unchanged.

    Raises:
        typer.BadParameter: for any other value.
    """
    raw = (value or "auto").strip().lower()
    if raw == "auto":
        return ProgressMode.SCREEN if is_progress_capable() else ProgressMode.NONE
    if raw in ("screen", "rich"):
        return ProgressMode.SCREEN
    if raw == "plain":
        return ProgressMode.PLAIN
    if raw == "json":
        return ProgressMode.JSON
    if raw == "none":
        return ProgressMode.NONE
    raise typer.BadParameter(
        f"--progress value {value!r} not recognised; expected auto|screen|rich|plain|json|none"
    )


def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with ``Z`` suffix and seconds precision."""
    from datetime import datetime

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ProgressTracker:
    """Mode-aware progress UI shared by ``validate``, ``eval``, ``refresh``, and ``refresh-all``.

    Five presentation modes:

    - :attr:`ProgressMode.SCREEN` — Rich ``Live(screen=True, transient=True)``
      alternate-screen dashboard with a parent ``N/M`` bar, an active-fixtures
      table (one row per in-flight slot), and a recent-completions ledger
      (bounded, default 10 rows). Restores the normal terminal on exit, so
      no stale frames remain in scrollback. ``RICH`` is an alias for
      ``SCREEN`` since the legacy normal-buffer mode was retired.
    - :attr:`ProgressMode.PLAIN` — One log line per ``start``/``done`` event
      written to stderr with an ISO 8601 UTC timestamp prefix and optional
      ``[wN]`` slot tag. Greppable, terminal-width-independent.
    - :attr:`ProgressMode.JSON` — One JSON object per event on stderr
      (``start_run``, ``start``, ``done``, ``end_run``). Designed for
      CI / observability tools.
    - :attr:`ProgressMode.NONE` — No-op; ``start_item`` / ``finish_item``
      return immediately. Used when piped, in CI, or when the user passes
      ``--no-progress``.

    All modes are safe to call from multiple coroutines; the underlying
    Rich ``Progress`` object is thread-safe.
    """

    # Rich Live refresh rate (Hz). 6 is the Rich-recommended sweet spot for
    # smooth animation without burning CPU on long-running batches.
    _RICH_REFRESH_HZ: int = 6
    _RECENT_LEDGER_MAX: int = 5

    def __init__(  # noqa: D107
        self,
        total: int,
        *,
        mode: ProgressMode = ProgressMode.SCREEN,
        description: str = "Processing",
        id_pad: int = 0,
    ) -> None:
        self._total = total
        self._mode = mode
        self._description = description
        self._id_pad = id_pad
        self._parent_progress: Progress | None = None
        self._live: Live | None = None
        self._parent_task: int | None = None
        self._start_times: dict[str, float] = {}
        self._active: dict[str, dict[str, object]] = {}
        from collections import deque

        self._recent: deque[dict[str, object]] = deque(maxlen=self._RECENT_LEDGER_MAX)
        self._completed: int = 0
        self._failed: int = 0
        self._concurrency: int = 0
        self._pid: int = 0
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._total_cost_usd: float = 0.0
        import time as _time

        self._run_start_perf: float = _time.perf_counter()

    @property
    def mode(self) -> ProgressMode:
        """The active presentation mode."""
        return self._mode

    def __enter__(self) -> ProgressTracker:  # noqa: D105
        if self._mode in (ProgressMode.SCREEN, ProgressMode.RICH):
            self._parent_progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=err_console,
                expand=True,
            )
            self._parent_task = self._parent_progress.add_task(self._description, total=self._total)
            self._live = Live(
                self._build_screen_renderable(),  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                console=err_console,
                refresh_per_second=self._RICH_REFRESH_HZ,
                screen=True,
                transient=True,
                redirect_stdout=False,
                redirect_stderr=False,
            )
            self._live.__enter__()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:  # noqa: D105
        if self._live is not None:
            with contextlib.suppress(Exception):
                self._live.__exit__(exc_type, exc, tb)  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        self._live = None
        self._parent_progress = None
        self._parent_task = None
        self._start_times.clear()
        self._active.clear()

    def start_run(self, *, pid: int, concurrency: int) -> None:
        """Record run-start metadata. Emits a JSON event in JSON mode."""
        import time as _time

        self._pid = pid
        self._concurrency = concurrency
        self._run_start_perf = _time.perf_counter()
        if self._mode is ProgressMode.JSON:
            self._emit_json(
                event="start_run",
                ts=_utc_now_iso(),
                pid=pid,
                concurrency=concurrency,
                total=self._total,
            )
        self._refresh()

    def end_run(self, *, succeeded: int, failed: int, wall_seconds: float) -> None:
        """Emit a run-end footer (JSON mode only)."""
        if self._mode is ProgressMode.JSON:
            self._emit_json(
                event="end_run",
                ts=_utc_now_iso(),
                wall_seconds=round(wall_seconds, 3),
                succeeded=succeeded,
                failed=failed,
                total=self._total,
            )

    def start_item(self, fixture_id: str, *, slot: int | None = None) -> None:
        """Mark a fixture as actively in flight."""
        import time

        now = time.perf_counter()
        self._start_times[fixture_id] = now
        label = self._format_label(fixture_id, slot)
        if self._mode in (ProgressMode.SCREEN, ProgressMode.RICH):
            self._active[fixture_id] = {
                "slot": slot,
                "label": label,
                "fixture_id": fixture_id,
                "start": now,
            }
            self._refresh()
        elif self._mode is ProgressMode.PLAIN:
            err_console.out(f"[{_utc_now_iso()}] start  {label}")
        elif self._mode is ProgressMode.JSON:
            self._emit_json(
                event="start",
                ts=_utc_now_iso(),
                slot=slot,
                fixture=fixture_id,
                total=self._total,
            )

    def finish_item(
        self,
        fixture_id: str,
        *,
        ok: bool = True,
        slot: int | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_cost_usd: float = 0.0,
    ) -> None:
        """Mark a fixture as done (advances the parent bar / emits a log line)."""
        import time

        elapsed = time.perf_counter() - self._start_times.pop(fixture_id, time.perf_counter())
        if ok:
            self._completed += 1
        else:
            self._failed += 1
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._total_cost_usd += total_cost_usd
        ts = _utc_now_iso()
        label = self._format_label(fixture_id, slot)

        if self._mode in (ProgressMode.SCREEN, ProgressMode.RICH):
            self._active.pop(fixture_id, None)
            self._recent.append(
                {
                    "ts": ts,
                    "ok": ok,
                    "slot": slot,
                    "label": label,
                    "fixture_id": fixture_id,
                    "elapsed": elapsed,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_cost_usd": total_cost_usd,
                }
            )
            if self._parent_progress is not None and self._parent_task is not None:
                self._parent_progress.update(self._parent_task, advance=1)  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
            self._refresh()
        elif self._mode is ProgressMode.PLAIN:
            status = "ok" if ok else "FAIL"
            tok_str = (
                f"  in={input_tokens:,} out={output_tokens:,}"
                if (input_tokens or output_tokens)
                else ""
            )
            cost_str = f"  ${total_cost_usd:.4f}" if total_cost_usd else ""
            err_console.out(f"[{ts}] done   {label}  {status}  {elapsed:.1f}s{tok_str}{cost_str}")
        elif self._mode is ProgressMode.JSON:
            self._emit_json(
                event="done",
                ts=ts,
                slot=slot,
                fixture=fixture_id,
                ok=ok,
                elapsed_seconds=round(elapsed, 3),
                total=self._total,
                completed=self._completed + self._failed,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost_usd=total_cost_usd,
            )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _format_label(self, fixture_id: str, slot: int | None) -> str:
        """Render a fixture id with optional ``[wN]`` slot prefix and padding."""
        pad = max(self._id_pad, len(fixture_id))
        fid = f"{fixture_id:<{pad}}" if pad else fixture_id
        return f"[w{slot}] {fid}" if slot is not None else fid

    def _emit_json(self, **payload: object) -> None:
        """Serialise a JSON event to stderr."""
        import json as _json

        err_console.out(_json.dumps(payload, separators=(",", ":")))

    def _refresh(self) -> None:
        """Re-render the screen dashboard if Live is active."""
        if self._live is None or self._mode not in (
            ProgressMode.SCREEN,
            ProgressMode.RICH,
        ):
            return
        with contextlib.suppress(Exception):
            self._live.update(self._build_screen_renderable())  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]

    def _build_screen_renderable(self, width: int | None = None) -> object:
        """Return the dashboard renderable for screen-backed Live."""
        import time as _time

        from rich.panel import Panel
        from rich.rule import Rule
        from rich.text import Text

        # Detect terminal width for responsive layout
        if width is None:
            if self._live is not None:
                with contextlib.suppress(Exception):
                    width = self._live.console.size.width
            if width is None:
                width = err_console.width or 120

        elapsed = _time.perf_counter() - self._run_start_perf
        done = self._completed + self._failed

        # §4-A Structured summary bar (Table.grid, grouped key/value pairs)
        pct = f"{100 * done // self._total}%" if self._total else "—"
        ok_part = Text(f"✓ {self._completed}", style="green")
        fail_text = f"✗ {self._failed}"
        fail_part = Text(fail_text, style="red") if self._failed > 0 else Text(fail_text)
        outcomes_val = Text.assemble(ok_part, "  ", fail_part)

        throughput_k: str = ""
        throughput_v: str = ""
        if self._total_input_tokens or self._total_output_tokens or self._total_cost_usd:
            tok_in = self._fmt_tokens_human(self._total_input_tokens)
            tok_out = self._fmt_tokens_human(self._total_output_tokens)
            throughput_k = "Throughput"
            throughput_v = f"{tok_in} in / {tok_out} out  ${self._total_cost_usd:.4f}"

        summary = Table.grid(padding=(0, 2))
        for _ in range(6):
            summary.add_column(no_wrap=True)
        summary.add_row(
            "[bold cyan]Progress[/bold cyan]",
            f"{done}/{self._total} ({pct})",
            "[bold cyan]Outcomes[/bold cyan]",
            outcomes_val,
            f"[bold cyan]{throughput_k}[/bold cyan]" if throughput_k else "",
            throughput_v,
        )
        summary.add_row(
            "[bold cyan]Elapsed[/bold cyan]",
            self._fmt_seconds(elapsed),
            "[bold cyan]ETA[/bold cyan]",
            self._calc_eta(elapsed),
            "[bold cyan]Concurrency[/bold cyan]",
            str(self._concurrency),
        )

        # §4-B §4-C §4-D §4-J: aligned leading columns, responsive breakpoints
        now = _time.perf_counter()
        compact = width < 80  # §4-J: compact single-line form
        include_time = width >= 100  # §4-J: drop time col when < 100
        collapse_tokens = width < 100  # §4-J: collapse in+out sum when < 100
        include_cost = width >= 120  # §4-J: cost col only in full layout

        # -- Active table: status | worker | fixture | elapsed --
        if compact:
            active_tbl = Table.grid(padding=(0, 1))
            active_tbl.add_column(width=1)
            active_tbl.add_column(width=4)
            active_tbl.add_column(no_wrap=True, overflow="ellipsis", max_width=max(width - 15, 10))
            active_tbl.add_column(justify="right", width=7)
        else:
            active_tbl = Table(
                title="Active", title_style="bold cyan", expand=True, show_edge=False
            )
            active_tbl.add_column("", width=1)
            active_tbl.add_column("worker", width=6)
            active_tbl.add_column("fixture", no_wrap=True, overflow="ellipsis", ratio=1)
            active_tbl.add_column("elapsed", justify="right", width=8)

        if self._active:
            for state in self._active.values():
                a_slot = state.get("slot")
                wstr = f"w{a_slot}" if a_slot is not None else "—"
                fid = str(state.get("fixture_id", ""))
                start = float(state.get("start", now))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                active_tbl.add_row("●", wstr, fid, self._fmt_seconds(now - start))
        else:
            active_tbl.add_row("", "—", "(idle)", "—")

        # -- Recent table: status | worker | fixture | elapsed [| time] [| in+out|tokens] [| cost] --
        if compact:
            recent_tbl = Table.grid(padding=(0, 1))
            recent_tbl.add_column(width=1)
            recent_tbl.add_column(width=4)
            recent_tbl.add_column(no_wrap=True, overflow="ellipsis", max_width=max(width - 15, 10))
            recent_tbl.add_column(justify="right", width=7)
        else:
            recent_tbl = Table(
                title=f"Recent completions (last {self._RECENT_LEDGER_MAX})",
                title_style="bold cyan",
                expand=True,
                show_edge=False,
            )
            recent_tbl.add_column("", width=1)
            recent_tbl.add_column("worker", width=6)
            recent_tbl.add_column("fixture", no_wrap=True, overflow="ellipsis", ratio=1)
            recent_tbl.add_column("elapsed", justify="right", width=8)
            if include_time:
                recent_tbl.add_column("time", justify="right", width=8)
            recent_tbl.add_column(
                "tokens" if collapse_tokens else "in+out",
                justify="right",
                width=10 if collapse_tokens else 14,
            )
            if include_cost:
                recent_tbl.add_column("cost", justify="right", width=9)

        if self._recent:
            for entry in self._recent:
                ok = bool(entry.get("ok", True))
                marker = Text("✓", style="green") if ok else Text("✗", style="red")
                r_slot = entry.get("slot")
                wstr = f"w{r_slot}" if r_slot is not None else "—"
                fid = str(entry.get("fixture_id", ""))
                elapsed_e = float(entry.get("elapsed", 0.0))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                if compact:
                    recent_tbl.add_row(marker, wstr, fid, self._fmt_seconds(elapsed_e))
                else:
                    in_tok = int(entry.get("input_tokens", 0))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                    out_tok = int(entry.get("output_tokens", 0))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                    cost_val = float(entry.get("total_cost_usd", 0.0))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                    ts = str(entry.get("ts", ""))
                    row: list[object] = [marker, wstr, fid, self._fmt_seconds(elapsed_e)]
                    if include_time:
                        row.append(self._fmt_ts_compact(ts))
                    if collapse_tokens:
                        combined = in_tok + out_tok
                        row.append(self._fmt_tokens_human(combined) if combined else "—")
                    else:
                        row.append(
                            f"{self._fmt_tokens_human(in_tok)}+{self._fmt_tokens_human(out_tok)}"
                            if (in_tok or out_tok)
                            else "—"
                        )
                    if include_cost:
                        row.append(f"${cost_val:.4f}" if cost_val else "—")
                    recent_tbl.add_row(*row)  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        else:
            if compact:
                recent_tbl.add_row("", "—", "(none yet)", "—")
            else:
                empty: list[object] = ["", "—", "(none yet)", "—"]
                if include_time:
                    empty.append("—")
                empty.append("—")
                if include_cost:
                    empty.append("—")
                recent_tbl.add_row(*empty)  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]

        footer = "[dim]Ctrl-C cancels. Use --debug to replay captured SDK output on failure.[/dim]"

        # §4-H section separators between summary, active, recent
        body = Group(
            summary,
            self._parent_progress if self._parent_progress is not None else Table.grid(),
            Rule(style="blue dim"),
            active_tbl,
            Rule(style="blue dim"),
            recent_tbl,
            Rule(style="blue dim"),
            footer,
        )
        # §4-F: Panel title is the single source of the description
        return Panel(body, title=self._description, border_style="blue")

    @staticmethod
    def _fmt_seconds(seconds: float) -> str:
        """Format a duration as H:MM:SS or MM:SS."""
        if seconds < 0:
            seconds = 0.0
        total = int(seconds)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _calc_eta(self, elapsed: float) -> str:
        """Compute ETA string from completed-rate x remaining items."""
        done = self._completed + self._failed
        if done == 0 or self._total == 0:
            return "—"
        remaining = self._total - done
        if remaining <= 0:
            return "done"
        eta_s = (elapsed / done) * remaining
        return "~" + self._fmt_seconds(eta_s)

    @staticmethod
    def _fmt_tokens_human(n: int) -> str:
        """Format token count as e.g. '11.2k', '1.4M'."""
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n / 1_000:.1f}k"
        return str(n)

    @staticmethod
    def _fmt_ts_compact(ts_iso: str) -> str:
        """Extract HH:MM:SS from ISO UTC timestamp (e.g. '2026-06-11T20:48:49Z')."""
        if len(ts_iso) >= 19 and ts_iso[10] == "T":
            return ts_iso[11:19]
        return ts_iso


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


@rule_loader_app.command("validate")
def validate_fixtures_cmd(
    fixture_id: Annotated[
        str | None, typer.Option("--fixture", help="Validate only this fixture id.")
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-v",
            help="Print full Python traceback for each failure (verbose mode).",
        ),
    ] = False,
    progress: Annotated[
        str,
        typer.Option(
            "--progress",
            "-P",
            help=(
                "Progress UI mode: auto|screen|rich|plain|json|none. Auto "
                "(default) shows a Rich alternate-screen dashboard on a TTY "
                "and is silent when piped/CI/NO_COLOR. ``screen`` and ``rich`` "
                "both select the alternate-screen dashboard. Bare ``-P`` is "
                "an alias for ``screen``."
            ),
        ),
    ] = "auto",
    no_progress: Annotated[
        bool,
        typer.Option(
            "--no-progress",
            help="Alias for ``--progress=none``. Disables the live UI.",
        ),
    ] = False,
) -> None:
    """Run the trigger-evidence invariant; no agent invocation.

    By default, reports every failing fixture (path + id + message) instead
    of bailing on the first error, so a single run shows all problems.
    Pass ``--debug`` / ``-v`` to also print the full Python traceback for
    each failure. The ``--progress`` flag controls the live UI mode (see
    ``--help`` for accepted values).
    """
    import traceback

    import yaml as _yaml

    from ai_rules.rule_loader_eval.fixtures import _parse_fixture, validate_fixture

    if no_progress:
        progress = "none"
    mode = resolve_progress_mode(progress)

    root = find_project_root()
    fixtures_dir = _fixtures_dir(root)
    rules = load_rules_metadata(_rules_dir(root))

    if fixture_id is not None:
        try:
            fx = load_fixture(fixtures_dir, fixture_id, rules=rules, enforce_invariant=True)
        except FixtureValidationError as exc:
            log_error(f"{fixture_id}: {exc}")
            if debug:
                err_console.print(traceback.format_exc())
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc
        log_success(f"validated 1 fixture: {fx.id}")
        return

    # Bulk mode: parse + validate each fixture independently so every failure
    # is reported, not just the first.
    yaml_paths = sorted(p for p in fixtures_dir.glob("*.yaml") if p.is_file())
    failures: list[tuple[Path, str, str]] = []  # (relative path, id, message)
    passed = 0

    with ProgressTracker(total=len(yaml_paths), mode=mode, description="validate") as tracker:
        for path in yaml_paths:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            raw_id: str = path.stem
            ok = True
            tracker.start_item(path.stem)
            try:
                with path.open(encoding="utf-8") as fh:
                    raw = _yaml.safe_load(fh)
                if isinstance(raw, dict) and isinstance(raw.get("id"), str):
                    raw_id = raw["id"]
                fixture = _parse_fixture(path, raw)
                validate_fixture(fixture, rules)
                passed += 1
            except FixtureValidationError as exc:
                failures.append((rel, raw_id, str(exc)))
                ok = False
                if debug:
                    err_console.print(f"[dim]── traceback for {rel}[/dim]")
                    err_console.print(traceback.format_exc())
            except Exception as exc:
                failures.append((rel, raw_id, f"unexpected error: {exc!r}"))
                ok = False
                if debug:
                    err_console.print(f"[dim]── traceback for {rel}[/dim]")
                    err_console.print(traceback.format_exc())
            finally:
                tracker.finish_item(path.stem, ok=ok)

    if failures:
        for rel, fid, msg in failures:
            log_error(f"{rel} (id={fid}): {msg}")
        log_error(f"{len(failures)} of {len(yaml_paths)} fixture(s) failed validation")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    log_success(f"validated {passed} fixture(s)")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@rule_loader_app.command("list")
def list_fixtures_cmd(
    variant: Annotated[
        str | None, typer.Option("--variant", help="Filter by simple|complex.")
    ] = None,
) -> None:
    """List registered fixtures with their required/dependency rules."""
    root = find_project_root()
    rules = load_rules_metadata(_rules_dir(root))
    fixtures = load_fixtures(_fixtures_dir(root), rules=rules)
    if variant:
        fixtures = [f for f in fixtures if f.variant == variant]

    table = Table(title="Rule Loader Eval Fixtures")
    table.add_column("ID", style="cyan")
    table.add_column("Variant")
    table.add_column("Required")
    table.add_column("Deps")
    table.add_column("Forbidden")
    for f in fixtures:
        table.add_row(
            f.id,
            f.variant,
            ", ".join(f.required),
            ", ".join(f.dependencies) or "—",
            ", ".join(f.forbidden) or "—",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# doctor + SDK guard
# ---------------------------------------------------------------------------


def _ensure_sdk_and_connection() -> None:
    """Hard-fail when the SDK is missing or the version pin doesn't match."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            installed = version("cortex-code-agent-sdk")
        except PackageNotFoundError:
            installed = "missing"
        if installed != SDK_PIN:
            log_error(
                f"cortex-code-agent-sdk version mismatch: installed={installed} "
                f"pin={SDK_PIN}; install via `uv sync --group live-agent` or bump "
                f"the pin in src/ai_rules/rule_loader_eval/__init__.py via PR"
            )
            raise typer.Exit(EXIT_SDK_OR_CONN)
    except ImportError as exc:  # pragma: no cover
        log_error(f"unable to check SDK installation: {exc}")
        raise typer.Exit(EXIT_SDK_OR_CONN) from exc


def _doctor_check(
    *,
    require_connection: bool = False,
    with_smoke: bool = False,
    connection: str | None = None,
) -> None:
    """Run pre-flight checks: SDK pin, connection resolution, fixture parse, optional smoke probe.

    When ``require_connection=True``, exits ``EXIT_INFRA_ERROR`` if no connection
    is configured. When ``with_smoke=True``, runs a trivial agent invocation to
    verify the model is actually reachable; exits ``EXIT_INFRA_ERROR`` on any
    infra error from the smoke probe.
    """
    root = find_project_root()
    log_info(f"project root: {root}")
    log_info(f"SDK pin: {SDK_PIN}")

    _ensure_sdk_and_connection()
    log_success(f"cortex-code-agent-sdk {SDK_PIN} matches pin")

    if require_connection:
        resolved = _require_connection_or_exit(connection)
        log_info(f"connection: {resolved}")
    else:
        env_value = os.environ.get("SNOWFLAKE_CONNECTION_NAME")
        if connection:
            log_info(f"connection (--connection): {connection}")
        elif env_value:
            log_info(f"SNOWFLAKE_CONNECTION_NAME={env_value}")
        else:
            log_warning("SNOWFLAKE_CONNECTION_NAME not set; live runs will use SDK default")

    fixtures_dir = _fixtures_dir(root)
    if not fixtures_dir.exists():
        log_error(f"fixtures dir missing: {fixtures_dir}")
        raise typer.Exit(EXIT_FIXTURE_INVALID)
    rules = load_rules_metadata(_rules_dir(root))
    try:
        fixtures = load_fixtures(fixtures_dir, rules=rules)
    except FixtureValidationError as exc:
        log_error(str(exc))
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc
    log_success(f"{len(fixtures)} fixtures pass trigger-evidence invariant")

    if with_smoke:
        from ai_rules.rule_loader_eval.agent_runner import run_live

        log_info("running smoke probe to verify model availability...")
        smoke = run_live(
            "__smoke__",
            "Reply with the single word OK.",
            project_root=root,
            max_turns=2,
            effort="low",
            model="auto",
            connection=connection,
        )
        if getattr(smoke, "is_infra_error", False):
            log_error("=" * 78)
            log_error(f"INFRA ERROR (smoke probe): {smoke.infra_error_detail}")
            log_error("The agent SDK could not complete a trivial request.")
            log_error("")
            log_error("Likely causes:")
            log_error("  - Model unavailable / quota exhausted")
            log_error("  - Auth / PAT expired")
            log_error("  - Network or proxy blocking the model endpoint")
            log_error("")
            log_error("Remediation:")
            log_error("  - Check ~/.snowflake/cortex/config.toml")
            log_error("  - Run `snow connection test --connection <name>`")
            log_error("=" * 78)
            raise typer.Exit(EXIT_INFRA_ERROR)
        log_success(f"smoke probe OK ({smoke.duration_ms}ms; turns={smoke.turns})")


@rule_loader_app.command("doctor")
def doctor_cmd(
    with_smoke: Annotated[
        bool,
        typer.Option(
            "--with-smoke",
            help="Run a trivial agent call to verify the model is reachable (adds ~3-5s).",
        ),
    ] = False,
    connection: Annotated[
        str | None,
        typer.Option(
            "--connection", help="Snowflake connection name (overrides SNOWFLAKE_CONNECTION_NAME)."
        ),
    ] = None,
) -> None:
    """Verify SDK pin, connection, and fixture parse. Optionally runs a smoke probe."""
    _doctor_check(require_connection=False, with_smoke=with_smoke, connection=connection)


# ---------------------------------------------------------------------------
# eval
# ---------------------------------------------------------------------------


def _run_single_eval(
    *,
    fixtures: list[Fixture],
    root: Path,
    resolved_connection: str,
    strict_forbidden: bool,
    max_turns: int,
    effort: str,
    model: str,
    mode: ProgressMode,
    debug: bool,
    out_dir: Path | None,
    label: str,
    run_number: int | None = None,
    concurrency: int = 1,
) -> tuple[list[RunResult], bool]:
    """Execute a single eval pass. Returns (results, is_infra_error).

    Fixtures are evaluated through the shared concurrent driver capped at
    ``concurrency`` in-flight (``1`` = sequential). Results are re-sorted to input
    fixture order before printing/snapshot so output is deterministic regardless
    of completion order. The unified ``ProgressTracker`` is driven with
    ``start_run`` + per-fixture ``slot`` in every mode (including ``concurrency==1``).

    Fail-fast: the first ``InfraError`` aborts the pass (in-flight fixtures are
    cancelled, queued fixtures are skipped), the aborting fixture is recorded as a
    synthetic INFRA row, cancelled/queued fixtures are surfaced as diagnostics only
    (never as fixture failures or snapshot rows), and ``(results, True)`` is
    returned so the caller skips the snapshot and aborts remaining runs.

    When ``run_number`` is set, it is displayed in the progress description.
    """
    from ai_rules.rule_loader_eval.concurrency import run_concurrent
    from ai_rules.rule_loader_eval.engine import InfraError, run_fixture_async
    from ai_rules.rule_loader_eval.engine import _synthetic_failure as _synth

    desc = f"eval run {run_number}" if run_number is not None else "eval"
    rules_meta = load_rules_metadata(_rules_dir(root))
    index_by_id = {f.id: i for i, f in enumerate(fixtures)}
    id_pad = max((len(f.id) for f in fixtures), default=0)

    async def _work(fixture: Fixture, slot: int) -> RunResult:
        return await run_fixture_async(
            fixture,
            project_root=root,
            rules_meta=rules_meta,
            strict_forbidden=strict_forbidden,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=resolved_connection,
        )

    def _exc_to_result(fixture: Fixture, exc: Exception) -> RunResult:
        # Non-aborting (non-Infra) per-fixture error -> synthetic FAIL row.
        return _synth(fixture, exc)

    try:
        with ProgressTracker(
            total=len(fixtures), mode=mode, description=desc, id_pad=id_pad
        ) as tracker:
            tracker.start_run(pid=os.getpid(), concurrency=concurrency)

            def _on_start(fixture: Fixture, slot: int) -> None:
                tracker.start_item(fixture.id, slot=slot)

            def _on_outcome(result: RunResult, slot: int) -> None:
                run = result.run
                tracker.finish_item(
                    result.fixture_id,
                    ok=result.passed,
                    slot=slot,
                    input_tokens=run.input_tokens if run else 0,
                    output_tokens=run.output_tokens if run else 0,
                    total_cost_usd=run.total_cost_usd if run else 0.0,
                )

            summary = run_concurrent(
                list(fixtures),
                concurrency=concurrency,
                work=_work,
                exception_to_result=_exc_to_result,
                should_abort_exception=lambda fixture, exc: isinstance(exc, InfraError),
                on_start=_on_start,
                on_outcome=_on_outcome,
            )
    except RuntimeError as exc:
        log_error(str(exc))
        raise typer.Exit(EXIT_SDK_OR_CONN) from exc

    # Determinism: re-sort completed results to input fixture order.
    results: list[RunResult] = sorted(
        summary.results, key=lambda r: index_by_id.get(r.fixture_id, len(fixtures))
    )

    # Fail-fast: fold the aborting fixture in as a synthetic INFRA row so the
    # detection block below returns (results, True). Cancelled/queued fixtures
    # (summary.not_run) are diagnostics only — never added as fixture rows.
    if summary.aborted is not None and isinstance(summary.aborted.exception, InfraError):
        results.append(_synth(summary.aborted.item, summary.aborted.exception, infra=True))
        results.sort(key=lambda r: index_by_id.get(r.fixture_id, len(fixtures)))
        if summary.not_run:
            skipped = ", ".join(nr.item.id for nr in summary.not_run)
            log_info(f"not run due to infra fail-fast ({len(summary.not_run)}): {skipped}")

    _print_results(results)
    _print_failure_details(results, debug=debug, effort=effort, model=model)

    infra_results = [r for r in results if getattr(r.run, "is_infra_error", False)]
    if infra_results:
        first = infra_results[0]
        log_error("=" * 78)
        log_error(f"INFRA ERROR detected at fixture: {first.fixture_id}")
        log_error(f"Detail: {first.run.infra_error_detail or '(no detail)'}")
        log_error("Eval aborted (fail-fast). Remaining fixtures were not run.")
        log_error("")
        log_error("Remediation:")
        log_error("  - uv run ai-rules rule-loader doctor --with-smoke --connection <name>")
        log_error("  - Verify SNOWFLAKE_CONNECTION_NAME or pass --connection to eval")
        log_error("  - snow connection test --connection <name>")
        log_error("=" * 78)
        return results, True

    if out_dir is not None:
        from ai_rules.rule_loader_eval.snapshot import (
            capture_meta,
            serialize_run_result,
            write_eval_snapshot,
        )

        fixture_by_id = {f.id: f for f in fixtures}
        snapshot_rows = []
        for r in results:
            fx = fixture_by_id.get(r.fixture_id)
            if fx is None:
                continue
            snapshot_rows.append(serialize_run_result(r, fx))
        meta = capture_meta(root, model=model, max_turns=max_turns, effort=effort, label=label)
        write_eval_snapshot(out_dir, snapshot_rows, meta)
        log_info(f"wrote eval snapshot to {out_dir}")

    return results, False


def _print_aggregate_summary(all_run_results: list[list[RunResult]], n_runs: int) -> None:
    """Print per-fixture pass rate across multiple runs."""
    from collections import Counter

    fixture_pass_counts: Counter[str] = Counter()
    fixture_total_counts: Counter[str] = Counter()

    for results in all_run_results:
        for r in results:
            fixture_total_counts[r.fixture_id] += 1
            if r.passed:
                fixture_pass_counts[r.fixture_id] += 1

    all_fixture_ids = sorted(fixture_total_counts.keys())
    total_passed_all = sum(
        1 for fid in all_fixture_ids if fixture_pass_counts[fid] == fixture_total_counts[fid]
    )
    total_failed_any = len(all_fixture_ids) - total_passed_all

    table = Table(title=f"Aggregate Summary — {n_runs} run(s)")
    table.add_column("Fixture")
    table.add_column("Pass Rate", justify="center")
    table.add_column("Result", justify="center")
    for fid in all_fixture_ids:
        passed = fixture_pass_counts[fid]
        total = fixture_total_counts[fid]
        rate = f"{passed}/{total}"
        if passed == total:
            result_str = "[green]stable pass[/green]"
        elif passed == 0:
            result_str = "[red]stable fail[/red]"
        else:
            result_str = "[yellow]flaky[/yellow]"
        table.add_row(fid, rate, result_str)

    console.print(table)
    total_fixture_runs = sum(fixture_total_counts.values())
    total_passes = sum(fixture_pass_counts.values())
    if total_fixture_runs > 0:
        console.print(
            f"\n[bold]Overall:[/bold] {total_passes}/{total_fixture_runs} fixture-runs passed "
            f"({total_passes * 100 // total_fixture_runs}%). "
            f"{total_passed_all} stable pass, {total_failed_any} with at least one failure."
        )


def _print_resource_summary(all_run_results: list[list[RunResult]]) -> None:
    """Print min/max/avg for turns, tokens, and duration across all fixture calls."""
    import statistics

    all_turns: list[int] = []
    all_input_tokens: list[int] = []
    all_output_tokens: list[int] = []
    all_duration_ms: list[int] = []
    all_cost: list[float] = []

    for results in all_run_results:
        for r in results:
            run = r.run
            all_turns.append(run.turns)
            all_duration_ms.append(run.duration_ms)
            if run.input_tokens:
                all_input_tokens.append(run.input_tokens)
            if run.output_tokens:
                all_output_tokens.append(run.output_tokens)
            if run.total_cost_usd:
                all_cost.append(run.total_cost_usd)

    if not all_turns:
        return

    def _stat_row(label: str, values: Sequence[int | float], fmt: str = ",") -> tuple[str, ...]:
        if not values:
            return (label, "—", "—", "—")
        mn = min(values)
        mx = max(values)
        avg = statistics.mean(values)
        if fmt == ",":
            return (label, f"{mn:,}", f"{mx:,}", f"{avg:,.0f}")
        elif fmt == "s":
            return (label, f"{mn / 1000:.1f}s", f"{mx / 1000:.1f}s", f"{avg / 1000:.1f}s")
        elif fmt == "$":
            return (label, f"${mn:.4f}", f"${mx:.4f}", f"${avg:.4f}")
        return (label, str(mn), str(mx), f"{avg:.1f}")

    table = Table(title="Resource Usage Summary")
    table.add_column("Metric")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Avg", justify="right")
    table.add_row(*_stat_row("Turns", all_turns))
    table.add_row(*_stat_row("Input tokens", all_input_tokens))
    table.add_row(*_stat_row("Output tokens", all_output_tokens))
    total_tokens = (
        [i + o for i, o in zip(all_input_tokens, all_output_tokens, strict=False)]
        if all_input_tokens and all_output_tokens
        else []
    )
    table.add_row(*_stat_row("Total tokens", total_tokens))
    table.add_row(*_stat_row("Duration", all_duration_ms, fmt="s"))
    if all_cost:
        table.add_row(*_stat_row("Cost (USD)", all_cost, fmt="$"))
    console.print(table)


@rule_loader_app.command("eval")
def eval_cmd(
    fixture_id: Annotated[
        str | None, typer.Option("--fixture", help="Run only this fixture id.")
    ] = None,
    strict_forbidden: Annotated[
        bool,
        typer.Option("--strict-forbidden", help="Treat forbidden hits as failures."),
    ] = False,
    max_turns: Annotated[int, typer.Option("--max-turns")] = DEFAULT_MAX_TURNS,
    effort: Annotated[str, typer.Option("--effort")] = DEFAULT_EFFORT,
    model: Annotated[str, typer.Option("--model")] = "auto",
    connection: Annotated[
        str | None, typer.Option("--connection", help="Snowflake CLI connection name.")
    ] = None,
    out_dir: Annotated[
        Path | None,
        typer.Option(
            "--out-dir",
            help=(
                "Base directory for eval snapshots. With --runs > 1, each run "
                "writes to <out-dir>-run-N. With --runs 1, writes directly to "
                "this path. Auto-generates 'out/eval-run-N' when omitted."
            ),
        ),
    ] = None,
    label: Annotated[
        str,
        typer.Option(
            "--label",
            help="Base label stored in meta.json. With --runs > 1, '-run-N' is appended.",
        ),
    ] = "",
    runs: Annotated[
        int,
        typer.Option(
            "--runs",
            help="Number of eval passes to execute (default 3). Accounts for LLM variance.",
        ),
    ] = 3,
    concurrency: Annotated[
        int,
        typer.Option(
            "--concurrency",
            help=(
                "Max fixtures evaluated in parallel WITHIN each run (default 1 = "
                "sequential). Runs (--runs) still execute one at a time. Unlike "
                "'refresh-all' (default 2), eval defaults to 1 to preserve "
                "deterministic sequential behavior; N>1 raises live SDK load."
            ),
        ),
    ] = 1,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable developer diagnostics (timing, signal disagreements, debug dump) to stderr.",
        ),
    ] = False,
    progress: Annotated[
        str,
        typer.Option(
            "--progress",
            "-P",
            help=(
                "Progress UI mode: auto|screen|rich|plain|json|none. Auto "
                "(default) shows a Rich alternate-screen dashboard on a TTY, "
                "falls back to silent on pipes/CI. ``screen`` and ``rich`` "
                "both select the alternate-screen dashboard."
            ),
        ),
    ] = "auto",
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Alias for ``--progress=none``."),
    ] = False,
) -> None:
    r"""Run fixtures through the live Cortex Code Agent SDK.

    Executes --runs passes (default 3) to account for LLM variance.
    Each run writes a snapshot to <out-dir>-run-N (auto-generated when
    --out-dir is omitted). An aggregate summary table is printed after
    all runs complete showing per-fixture pass rates.

    Use ``--concurrency N`` to evaluate up to N fixtures in parallel WITHIN
    each run (default 1 = sequential; --runs still executes one pass at a
    time). Output is deterministic regardless of completion order: results
    are re-sorted to input-fixture order before tables/snapshots. Unlike
    ``refresh-all`` (default 2), eval defaults to 1 to preserve the
    sequential baseline; N>1 raises live SDK load. The first infra error
    cancels in-flight fixtures, skips queued ones, skips the snapshot, and
    aborts remaining runs.

    Three checks are unconditional per fixture:
    1. Required + dependencies must all be present in the loaded set.
    2. The 2-signal agreement check (tool reads vs ``## Rules Loaded``;
       legacy ``## Reads Performed`` checked when present) must hold.
    3. Citation drift (declared line counts vs. actual rule line counts)
       must be empty.

    Any of the three failing fails the fixture. There are no escape
    flags - rule-loading correctness is non-negotiable.

    Infra errors (SDK/model/connection down) abort remaining runs
    immediately (fail-fast).

    **Fast profile** (development iteration)::

        uv run ai-rules rule-loader eval \\
            --fixture <id> \\
            --effort low \\
            --runs 1 \\
            --debug

    This runs a single fixture with low-effort (faster SDK responses) and
    no multi-run aggregation. Useful for rapid iteration during rule edits.
    Expect higher variance — use ``--runs 3`` (default) for definitive results.
    """
    if runs < 1:
        log_error("--runs must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if concurrency < 1:
        log_error("--concurrency must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if no_progress:
        progress = "none"
    mode = resolve_progress_mode(progress)

    root = find_project_root()
    resolved_connection = _require_connection_or_exit(connection)
    rules = load_rules_metadata(_rules_dir(root))
    if fixture_id:
        try:
            fixtures = [load_fixture(_fixtures_dir(root), fixture_id, rules=rules)]
        except FixtureValidationError as exc:
            log_error(str(exc))
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc
    else:
        try:
            fixtures = load_fixtures(_fixtures_dir(root), rules=rules)
        except FixtureValidationError as exc:
            log_error(str(exc))
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    _ensure_sdk_and_connection()

    all_run_results: list[list[RunResult]] = []
    any_failure = False

    for run_idx in range(1, runs + 1):
        if runs > 1:
            log_info(f"{'═' * 60}")
            log_info(f"Run {run_idx}/{runs}")
            log_info(f"{'═' * 60}")

        if runs == 1:
            run_out_dir = out_dir
            run_label = label
        else:
            if out_dir is not None:
                run_out_dir = Path(f"{out_dir}-run-{run_idx}")
            else:
                run_out_dir = Path(f"out/eval-run-{run_idx}")
            run_label = f"{label}-run-{run_idx}" if label else f"run-{run_idx}"

        results, is_infra = _run_single_eval(
            fixtures=fixtures,
            root=root,
            resolved_connection=resolved_connection,
            strict_forbidden=strict_forbidden,
            max_turns=max_turns,
            effort=effort,
            model=model,
            mode=mode,
            debug=debug,
            out_dir=run_out_dir,
            label=run_label,
            run_number=run_idx if runs > 1 else None,
            concurrency=concurrency,
        )
        all_run_results.append(results)

        if any(not r.passed for r in results):
            any_failure = True

        if is_infra:
            log_error(f"Infra error on run {run_idx}/{runs}. Aborting remaining runs.")
            raise typer.Exit(EXIT_INFRA_ERROR)

    if runs > 1:
        console.print()
        _print_aggregate_summary(all_run_results, runs)

    console.print()
    _print_resource_summary(all_run_results)

    if any_failure:
        raise typer.Exit(EXIT_FIXTURE_FAIL)
    log_success(f"all {len(fixtures)} fixture(s) passed across {runs} run(s)")


def _print_results(results: list[RunResult]) -> None:
    table = Table(title="Rule Loader Eval — pass/fail")
    table.add_column("Fixture")
    table.add_column("Result")
    table.add_column("Turns", justify="right")
    table.add_column("Input Tk", justify="right")
    table.add_column("Output Tk", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Missing required")
    table.add_column("Missing dependencies")
    table.add_column("Forbidden present")
    table.add_column("Signal mismatch")
    table.add_column("Citation drift")
    table.add_column("Output")
    for r in results:
        run = r.run
        input_tk = f"{run.input_tokens:,}" if run.input_tokens else "—"
        output_tk = f"{run.output_tokens:,}" if run.output_tokens else "—"
        duration = f"{run.duration_ms / 1000:.1f}s" if run.duration_ms else "—"
        table.add_row(
            r.fixture_id,
            "[green]pass[/green]" if r.passed else "[red]fail[/red]",
            str(run.turns) if run.turns else "—",
            input_tk,
            output_tk,
            duration,
            ", ".join(r.match.missing_required) or "—",
            ", ".join(r.match.missing_dependencies) or "—",
            ", ".join(r.match.forbidden_present) or "—",
            str(len(r.signal_report.disagreements)) if r.signal_report.disagreements else "—",
            str(len(r.citation_drifts)) if r.citation_drifts else "—",
            str(len(r.run.output_violations)) if r.run.output_violations else "—",
        )
    console.print(table)


def _print_failure_details(
    results: list[RunResult], *, debug: bool = False, effort: str = "", model: str = ""
) -> None:
    """For every failing fixture, print why it failed (signal/drift specifics).

    When ``debug`` is True, additionally emit the full debug dump and
    per-event timing trace for every run (pass or fail) to stderr.
    """
    for r in results:
        if r.passed:
            if debug:
                for line in format_debug(r.run):
                    print(line, file=sys.stderr)
                for line in format_timing_lines(r.run, effort=effort, model=model):
                    print(line, file=sys.stderr)
            continue
        console.print(f"\n[bold red]FAIL[/bold red] {r.fixture_id}")
        if not r.signal_report.ok:
            console.print(format_disagreement_warning(r.run, signal_report=r.signal_report))
        drift_msg = format_citation_drift_warning(r.citation_drifts)
        if drift_msg:
            console.print(drift_msg)
        if r.run.output_violations:
            console.print("Output contract violations:")
            for violation in r.run.output_violations:
                console.print(f"  - {violation}")
        if debug:
            for line in format_debug(r.run):
                print(line, file=sys.stderr)
            for line in format_timing_lines(r.run, effort=effort, model=model):
                print(line, file=sys.stderr)


# ---------------------------------------------------------------------------
# create (new fixture authoring)
# ---------------------------------------------------------------------------


@rule_loader_app.command("create")
def create_cmd(
    prompt: Annotated[
        str | None,
        typer.Option("--prompt", help="Literal prompt text."),
    ] = None,
    prompt_file: Annotated[
        Path | None,
        typer.Option("--prompt-file", help="Read prompt from a plain-text file."),
    ] = None,
    fixture_id: Annotated[
        str | None,
        typer.Option("--id", help="Fixture id (used in the snippet header)."),
    ] = None,
    variant: Annotated[
        str,
        typer.Option("--variant", help="simple | complex (used in the snippet)."),
    ] = "simple",
    write_path: Annotated[
        Path | None,
        typer.Option("--write", help="Write the skeleton to this path."),
    ] = None,
    max_turns: Annotated[int, typer.Option("--max-turns")] = DEFAULT_MAX_TURNS,
    effort: Annotated[str, typer.Option("--effort")] = DEFAULT_EFFORT,
    model: Annotated[str, typer.Option("--model")] = "auto",
    connection: Annotated[str | None, typer.Option("--connection")] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable developer diagnostics (timing, signal disagreements, debug dump) to stderr.",
        ),
    ] = False,
) -> None:
    """Drive the live agent against a candidate prompt and print a YAML skeleton.

    Use to author a brand-new fixture from a candidate prompt. The
    skeleton includes mechanical ``# suggested:`` comments derived from
    the rule metadata snapshot + prompt text.

    2-signal disagreement and citation-drift warnings always print to
    stderr when present. ``--debug`` adds the full debug dump and
    per-event timing trace.
    """
    if (prompt is None) == (prompt_file is None):
        log_error("provide exactly one of --prompt or --prompt-file")
        raise typer.Exit(EXIT_INTERNAL)
    if prompt_file is not None:
        prompt = prompt_file.read_text(encoding="utf-8")
    assert prompt is not None

    run = _drive_live(
        fixture_id or "candidate",
        prompt,
        max_turns=max_turns,
        effort=effort,
        model=model,
        connection=connection,
    )
    root = find_project_root()
    snippet = format_fixture_snippet(
        run, prompt, fixture_id, variant, root, current_updated_timestamp()
    )
    console.print(snippet)
    _emit_diagnostics(run, debug=debug, effort=effort, model=model)

    if write_path is not None:
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text(snippet + "\n", encoding="utf-8")
        log_success(f"wrote {write_path}")


# ---------------------------------------------------------------------------
# refresh (drift detection on existing fixture)
# ---------------------------------------------------------------------------


@rule_loader_app.command("refresh", no_args_is_help=True)
def refresh_cmd(
    fixture_path: Annotated[
        Path,
        typer.Argument(help="Path to an existing fixture YAML."),
    ],
    write: Annotated[
        bool,
        typer.Option(
            "--write",
            help="Replace the on-disk fixture with the regenerated skeleton.",
        ),
    ] = False,
    max_turns: Annotated[int, typer.Option("--max-turns")] = DEFAULT_MAX_TURNS,
    effort: Annotated[str, typer.Option("--effort")] = DEFAULT_EFFORT,
    model: Annotated[str, typer.Option("--model")] = "auto",
    connection: Annotated[str | None, typer.Option("--connection")] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable developer diagnostics (timing, signal disagreements, debug dump) to stderr.",
        ),
    ] = False,
    progress: Annotated[
        str,
        typer.Option(
            "--progress",
            "-P",
            help=(
                "Progress UI mode: auto|screen|rich|plain|json|none. Auto "
                "(default) shows a Rich alternate-screen dashboard on a TTY. "
                "``screen`` and ``rich`` both select the alternate-screen "
                "dashboard."
            ),
        ),
    ] = "auto",
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Alias for ``--progress=none``."),
    ] = False,
) -> None:
    """Re-run an existing fixture and report drift, optionally rewriting it.

    Default (read-only): regenerate the skeleton, print a unified diff
    against the on-disk YAML, and exit 0 if no drift, 2 if drift is
    detected, 4 if the fixture file is unparseable.

    With ``--write``: replace the on-disk file with the regenerated
    skeleton (snapshot-style 'accept' verb). Note: ``--write``
    regenerates from the suggestion engine, which sorts rules and emits
    canonical inline ``# suggested:`` comments. Hand-edited comments
    and custom ordering are lost.

    Pass ``--debug`` to also print the full debug dump and per-event
    timing trace to stderr. The ``--progress`` flag controls the live
    UI mode (auto|screen|rich|plain|json|none).
    """
    if not fixture_path.exists():
        log_error(f"fixture file not found: {fixture_path}")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if no_progress:
        progress = "none"
    mode = resolve_progress_mode(progress)

    prompt = read_prompt(fixture_path)
    fixture_id = _extract_id(fixture_path)
    variant = _extract_variant(fixture_path)

    fid_for_progress = fixture_id or fixture_path.stem
    if mode is not ProgressMode.NONE:
        with ProgressTracker(total=1, mode=mode, description="refresh") as tracker:
            tracker.start_item(fid_for_progress)
            try:
                run = _drive_live(
                    fid_for_progress,
                    prompt,
                    max_turns=max_turns,
                    effort=effort,
                    model=model,
                    connection=connection,
                )
                tracker.finish_item(
                    fid_for_progress,
                    ok=True,
                    input_tokens=run.input_tokens,
                    output_tokens=run.output_tokens,
                    total_cost_usd=run.total_cost_usd,
                )
            except Exception:
                tracker.finish_item(fid_for_progress, ok=False)
                raise
    else:
        run = _drive_live(
            fid_for_progress,
            prompt,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=connection,
        )
    root = find_project_root()
    if write:
        updated_value = current_updated_timestamp()
    else:
        # Preserve the on-disk timestamp so drift detection only flags real
        # semantic changes. Fall back to "now" if the existing fixture has no
        # readable updated: field (e.g. legacy / partially-authored).
        updated_value = read_updated(fixture_path) or current_updated_timestamp()
    preserved = parse_preservation_annotations_from_path(fixture_path)
    new_snippet = (
        format_fixture_snippet(
            run, prompt, fixture_id, variant, root, updated_value, preserved=preserved
        )
        + "\n"
    )
    old_text = fixture_path.read_text(encoding="utf-8") if fixture_path.exists() else ""

    # Round-trip validation gate: rendered candidate must pass the same
    # trigger-evidence invariant the validate command applies. On failure,
    # write the candidate alongside the target as ``<path>.invalid`` and
    # refuse to overwrite. This makes refresh / refresh-all output a hard
    # contract: anything written to the target path passes validate.
    rules = load_rules_metadata(_rules_dir(root))
    invariant_errors = validate_rendered_snippet(
        new_snippet, fixture_id or fixture_path.stem, rules
    )

    if write:
        if invariant_errors:
            invalid_path = fixture_path.with_suffix(fixture_path.suffix + ".invalid")
            invalid_path.write_text(new_snippet, encoding="utf-8")
            log_error(f"refresh produced an invalid fixture; refusing to overwrite {fixture_path}")
            for err in invariant_errors:
                log_error(f"  - {err}")
            log_warning(f"candidate written to {invalid_path}")
            _emit_diagnostics(run, debug=debug, effort=effort, model=model)
            raise typer.Exit(EXIT_FIXTURE_FAIL)
        fixture_path.write_text(new_snippet, encoding="utf-8")
        log_success(f"rewrote {fixture_path}")
        _emit_diagnostics(run, debug=debug, effort=effort, model=model)
        return

    # Read-only diff path. Surface invariant errors as a warning even when
    # not writing so authors see what would block --write.
    if invariant_errors:
        log_warning(
            f"rendered candidate would FAIL validate ({len(invariant_errors)} error(s)); "
            f"--write would be refused:"
        )
        for err in invariant_errors:
            log_warning(f"  - {err}")

    diff = list(
        difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_snippet.splitlines(keepends=True),
            fromfile=str(fixture_path),
            tofile=f"{fixture_path} (regenerated)",
        )
    )
    _emit_diagnostics(run, debug=debug, effort=effort, model=model)
    if not diff:
        log_success(f"no drift in {fixture_path}")
        return
    sys.stdout.writelines(diff)
    log_warning(f"drift detected in {fixture_path}; rerun with --write to accept")
    raise typer.Exit(EXIT_DRIFT)


# ---------------------------------------------------------------------------
# refresh-all (batch refresh)
# ---------------------------------------------------------------------------


@rule_loader_app.command("refresh-all")
def refresh_all_cmd(
    glob: Annotated[
        str | None,
        typer.Option(
            "--glob",
            help="Glob pattern (relative to repo root) selecting fixture YAMLs.",
        ),
    ] = None,
    all_fixtures: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Process every fixture under fixtures/rule_loader_eval/.",
        ),
    ] = False,
    concurrency: Annotated[
        int,
        typer.Option("--concurrency", help="Max in-flight SDK sessions."),
    ] = 2,
    out_dir: Annotated[
        Path | None,
        typer.Option(
            "--out-dir",
            help="Write per-fixture YAML + summary.json here. Omit to stream to stdout.",
        ),
    ] = None,
    max_turns: Annotated[int, typer.Option("--max-turns")] = DEFAULT_MAX_TURNS,
    effort: Annotated[str, typer.Option("--effort")] = DEFAULT_EFFORT,
    model: Annotated[str, typer.Option("--model")] = "auto",
    connection: Annotated[str | None, typer.Option("--connection")] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable developer diagnostics (timing, signal disagreements, debug dump) to stderr per fixture.",
        ),
    ] = False,
    progress: Annotated[
        str,
        typer.Option(
            "--progress",
            "-P",
            help=(
                "Progress UI mode: auto|screen|rich|plain|json|none. Auto "
                "(default) shows a Rich alternate-screen dashboard with the "
                "active fixtures and a recent-completions ledger; falls back "
                "to silent when piped/CI/NO_COLOR. ``screen`` and ``rich`` "
                "both select the alternate-screen dashboard."
            ),
        ),
    ] = "auto",
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Alias for ``--progress=none``."),
    ] = False,
) -> None:
    """Batch-capture or refresh fixtures concurrently against the live SDK.

    Resolves ``--glob`` or ``--all`` to a list of fixture YAMLs (defaulting
    to ``--all`` when neither is given), drives each through
    ``run_live_async`` (capped by ``--concurrency``), and writes regenerated
    skeletons either to ``--out-dir`` (per-fixture files + ``summary.json``)
    or stdout.

    When ``--progress`` is active (default on a TTY) and ``--out-dir`` is
    omitted, YAML payload is spooled to a bounded temp file (1 MB in RAM,
    spills to disk above) and replayed to stdout only when stdout is a pipe;
    on an interactive TTY a one-line "wrote N fixtures" hint is shown
    instead, leaving the bar's scrollback uncluttered.

    Pass ``--debug`` to also print the full debug dump and per-event
    timing trace for each fixture to stderr (and to replay any captured
    SDK chatter that was hidden while the bar was active).

    Exit codes:
    - ``0`` — every fixture succeeded.
    - ``1`` — at least one fixture failed.
    - ``3`` — SDK / connection error.
    - ``4`` — invalid arguments (e.g., concurrency < 1, no fixtures matched).
    """
    import json
    import shutil
    import tempfile

    from ai_rules.rule_loader_eval.batch import (
        BatchItem,
        BatchOutcome,
        expand_glob,
        extract_batch_item,
        run_batch,
        validate_unique_output_names,
    )
    from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk

    if no_progress:
        progress = "none"
    mode = resolve_progress_mode(progress)

    # R6: default to --all when neither flag is given. Mutex remains in force.
    if glob is None and not all_fixtures:
        all_fixtures = True
        log_info("no --glob or --all given; defaulting to --all")
    elif glob is not None and all_fixtures:
        log_error("--glob and --all are mutually exclusive")
        raise typer.Exit(EXIT_INTERNAL)
    if concurrency < 1:
        log_error("--concurrency must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    root = find_project_root()
    if all_fixtures:
        paths = expand_glob("fixtures/rule_loader_eval/*.yaml", root)
    else:
        assert glob is not None
        paths = expand_glob(glob, root)
    if not paths:
        log_error("no fixtures matched")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    items = []
    for p in paths:
        try:
            items.append(extract_batch_item(p))
        except ValueError as exc:
            log_error(str(exc))
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc
    try:
        validate_unique_output_names(items)
    except ValueError as exc:
        log_error(str(exc))
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    _ensure_sdk_and_connection()

    # Run-start header: pid for cross-instance disambiguation, concurrency
    # so the user sees how many slots are in play, total for capacity.
    log_info(f"refresh-all  pid={os.getpid()}  concurrency={concurrency}  total={len(items)}")

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    # R3: when progress is active and no --out-dir, spool YAML to a bounded
    # temp file and replay only when stdout is non-TTY.
    payload_spool: tempfile.SpooledTemporaryFile | None = None
    if out_dir is None and mode is not ProgressMode.NONE:
        payload_spool = tempfile.SpooledTemporaryFile(  # noqa: SIM115
            max_size=1_048_576, mode="w+", encoding="utf-8"
        )

    # When SDK chatter is being captured, the test/runtime sys.stdout is
    # swapped to a buffer; bypass that with sys.__stdout__ so YAML payload
    # still reaches the real terminal / pipe. When NOT capturing, prefer the
    # current sys.stdout so test runners (Click's CliRunner) see the output.
    capture_sdk = mode not in (ProgressMode.NONE, ProgressMode.JSON)
    payload_stdout = sys.__stdout__ if capture_sdk else sys.stdout

    # Pad child fixture-id descriptions to the longest id for tidy alignment
    # as concurrent children come and go.
    id_pad = max((len(it.id) for it in items), default=0)

    # Round-trip validation gate state: track per-fixture invariant
    # failures so the refresh-all output is a hard contract. A fixture
    # whose rendered snippet fails the invariant is NEVER written to the
    # target path; instead a ``<safe_id>.yaml.invalid`` candidate is written
    # next to it (when --out-dir is set) and the run exits non-zero.
    rules_meta_for_validate = load_rules_metadata(_rules_dir(root))
    invalid_count: dict[str, int] = {"n": 0}
    invalid_fixtures: list[tuple[str, list[str]]] = []
    auto_demote_count: dict[str, int] = {"n": 0}

    def _on_start(item: BatchItem, slot: int) -> None:
        tracker.start_item(item.id, slot=slot)

    def _on_outcome(outcome: BatchOutcome, slot: int) -> None:
        finish_called = False
        try:
            if not outcome.succeeded:
                log_warning(f"[{outcome.item.id}] {outcome.error_type}: {outcome.error_message}")
                return
            assert outcome.run is not None
            preserved = parse_preservation_annotations_from_path(outcome.item.path)
            variant_for_render = _extract_variant(outcome.item.path)
            snippet = format_fixture_snippet(
                outcome.run,
                outcome.item.prompt,
                outcome.item.id,
                variant_for_render,
                root,
                current_updated_timestamp(),
                preserved=preserved,
            )
            invariant_errors = validate_rendered_snippet(
                snippet, outcome.item.id, rules_meta_for_validate
            )
            if invariant_errors:
                # Refuse to write the target. Drop a .invalid candidate
                # next to the target when --out-dir is in play; otherwise
                # log only.
                invalid_count["n"] += 1
                invalid_fixtures.append((outcome.item.id, invariant_errors))
                if out_dir is not None:
                    invalid_path = out_dir / f"{outcome.item.safe_id}.yaml.invalid"
                    invalid_path.write_text(snippet + "\n", encoding="utf-8")
                    log_warning(
                        f"[{outcome.item.id}] rendered candidate FAILED invariant; "
                        f"wrote {invalid_path} and skipped target overwrite"
                    )
                else:
                    log_warning(
                        f"[{outcome.item.id}] rendered candidate FAILED invariant; "
                        f"target unchanged ({len(invariant_errors)} error(s))"
                    )
                for err in invariant_errors:
                    log_warning(f"  - {err}")
                # Mark the outcome as failed for tracker reporting so the
                # progress UI reflects the refusal-to-overwrite.
                tracker.finish_item(
                    outcome.item.id,
                    ok=False,
                    slot=slot,
                    input_tokens=outcome.run.input_tokens,
                    output_tokens=outcome.run.output_tokens,
                    total_cost_usd=outcome.run.total_cost_usd,
                )
                finish_called = True
                return
            # Tally auto-demote count for the run summary.
            try:
                from ai_rules.rule_loader_eval.suggestions import build_suggestions

                _sugg = build_suggestions(
                    outcome.run.loaded, outcome.item.prompt, rules_meta_for_validate
                )
                auto_demote_count["n"] += len(_sugg.auto_demoted)
            except Exception:
                pass
            if out_dir is not None:
                (out_dir / f"{outcome.item.safe_id}.yaml").write_text(
                    snippet + "\n", encoding="utf-8"
                )
            elif payload_spool is not None:
                payload_spool.write(f"# fixture: {outcome.item.id}\n{snippet}\n\n")
            else:
                # ProgressMode.NONE + no out_dir: stream straight to stdout.
                print(f"# fixture: {outcome.item.id}", file=payload_stdout)
                print(snippet, file=payload_stdout)
                print(file=payload_stdout)
            if debug:
                _emit_diagnostics(outcome.run, debug=True, effort=effort, model=model)
        finally:
            if not finish_called:
                _run = outcome.run
                tracker.finish_item(
                    outcome.item.id,
                    ok=outcome.succeeded,
                    slot=slot,
                    input_tokens=_run.input_tokens if _run else 0,
                    output_tokens=_run.output_tokens if _run else 0,
                    total_cost_usd=_run.total_cost_usd if _run else 0.0,
                )

    # R2: suppress SDK chatter while progress UI is active. quiet_sdk is a
    # no-op when capture=False. Top-level try/except handles SIGINT
    # (KeyboardInterrupt) so the Live region tears down cleanly via its
    # __exit__, restoring the terminal before the process exits.
    #
    # Replay-after-exit policy: SDK buffer replay must NOT happen inside the
    # ProgressTracker context, because in SCREEN mode the alternate screen
    # discards anything written there on exit. Capture the buffer text and
    # any deferred error/exception, then replay (and re-raise) after the
    # tracker has torn down.
    sdk_replay_text: str = ""
    summary = None
    pending_runtime_error: RuntimeError | None = None
    pending_other: BaseException | None = None
    try:
        with ProgressTracker(
            total=len(items), mode=mode, description="refresh-all", id_pad=id_pad
        ) as tracker:
            tracker.start_run(pid=os.getpid(), concurrency=concurrency)
            with quiet_sdk(capture=capture_sdk) as sdk_buf:
                try:
                    summary = run_batch(
                        items,
                        concurrency=concurrency,
                        project_root=root,
                        max_turns=max_turns,
                        effort=effort,
                        model=model,
                        connection=connection,
                        on_start=_on_start,
                        on_outcome=_on_outcome,
                    )
                except RuntimeError as exc:
                    pending_runtime_error = exc
                except KeyboardInterrupt:
                    # asyncio.run translates SIGINT to CancelledError inside
                    # gather; in-flight tasks are cancelled fast.
                    if sdk_buf is not None:
                        sdk_replay_text = sdk_buf.getvalue()
                    raise
                except Exception as exc:
                    pending_other = exc
                else:
                    if debug and sdk_buf is not None:
                        sdk_replay_text = sdk_buf.getvalue()
                    assert summary is not None
                    tracker.end_run(
                        succeeded=summary.succeeded,
                        failed=summary.failed,
                        wall_seconds=summary.wall_seconds,
                    )
                if (
                    pending_runtime_error is not None or pending_other is not None
                ) and sdk_buf is not None:
                    sdk_replay_text = sdk_buf.getvalue()
    except KeyboardInterrupt:
        # Tracker.__exit__ has already run -- terminal restored. Print a
        # brief summary and exit with the POSIX SIGINT convention (130).
        if sdk_replay_text:
            _replay_text(sdk_replay_text)
        log_warning("interrupted by user; in-flight calls cancelled")
        if payload_spool is not None:
            payload_spool.close()
        raise typer.Exit(130) from None

    # Live has exited -- safe to replay captured SDK chatter and surface
    # any deferred error to the normal terminal buffer.
    if sdk_replay_text:
        _replay_text(sdk_replay_text)
    if pending_runtime_error is not None:
        log_error(str(pending_runtime_error))
        raise typer.Exit(EXIT_SDK_OR_CONN) from pending_runtime_error
    if pending_other is not None:
        raise pending_other

    # R3: replay the spool only when stdout is non-TTY; on a TTY suppress and
    # emit a one-line hint so the user isn't flooded with scrollback YAML.
    if payload_spool is not None:
        payload_spool.flush()
        spool_size = payload_spool.tell()
        payload_spool.seek(0)
        # Use the real stdout for the isatty probe (the captured CliRunner
        # stream pretends to be TTY-less, which is what we want there too).
        real_stdout = sys.__stdout__
        is_tty = real_stdout is not None and real_stdout.isatty()
        if not is_tty and payload_stdout is not None:
            shutil.copyfileobj(payload_spool, payload_stdout)
        else:
            assert summary is not None
            log_info(
                f"wrote {summary.total} fixture(s) to internal buffer "
                f"({spool_size:,} bytes); re-run with `--out-dir <dir>` "
                f"or pipe stdout to capture"
            )
        payload_spool.close()

    if out_dir is not None:
        assert summary is not None
        summary_blob = {
            "concurrency": summary.concurrency,
            "wall_seconds": summary.wall_seconds,
            "total": summary.total,
            "succeeded": summary.succeeded,
            "failed": summary.failed,
            "outcomes": [
                {
                    "id": o.item.id,
                    "safe_id": o.item.safe_id,
                    "path": str(o.item.path),
                    "succeeded": o.succeeded,
                    "error_type": o.error_type,
                    "error_message": o.error_message,
                }
                for o in summary.outcomes
            ],
        }
        (out_dir / "summary.json").write_text(
            json.dumps(summary_blob, indent=2) + "\n", encoding="utf-8"
        )

    assert summary is not None
    log_info(
        f"batch complete: {summary.succeeded}/{summary.total} succeeded "
        f"in {summary.wall_seconds:.2f}s (concurrency={summary.concurrency})"
    )
    if auto_demote_count["n"] > 0:
        log_info(
            f"auto-demoted {auto_demote_count['n']} rule occurrence(s) across {summary.total} "
            f"fixture(s) (loaded with no trigger evidence in prompt)"
        )
    if invalid_count["n"] > 0:
        log_error(
            f"{invalid_count['n']} fixture(s) failed round-trip validation; "
            f"refused to overwrite target paths"
        )
        raise typer.Exit(EXIT_FIXTURE_FAIL)
    if summary.failed:
        raise typer.Exit(EXIT_FIXTURE_FAIL)


# ---------------------------------------------------------------------------
# merge-snapshots (noise-resistant baseline construction)
# ---------------------------------------------------------------------------


@rule_loader_app.command("merge-snapshots")
def merge_snapshots_cmd(
    snapshot_dirs: Annotated[
        list[Path],
        typer.Argument(
            help="Two or more snapshot directories produced by 'eval --out-dir'.",
        ),
    ],
    out_dir: Annotated[
        Path,
        typer.Option(
            "--out-dir",
            "-o",
            help="Write the merged snapshot here (meta.json + eval/<fixture>.json + eval/summary.json).",
        ),
    ],
    label: Annotated[
        str,
        typer.Option(
            "--label",
            help="Label embedded into the merged snapshot's meta.json.",
        ),
    ] = "merged",
) -> None:
    r"""Merge N snapshot directories into one noise-resistant baseline.

    Aggregation policy (fixed; matches plan Q1-Q4 decisions):

    - Pass status: strict-majority (a fixture passes when it passed in
      more than half of the input runs that contained it).
    - Loaded set: strict-majority (a rule appears in merged loaded when
      it appeared in more than half of input runs that contained the
      fixture).
    - Missing fixtures: filled from available runs (a fixture in some
      runs but not others is included with majority computed over the
      runs that contained it).
    - Numeric metrics (turns, duration_ms, signal_disagreements,
      citation_drifts): median across runs.

    Use this command to build a stable baseline from multiple
    ``eval --out-dir`` runs before comparing to a post-change snapshot.
    Typical workflow::

        for i in 1 2 3; do
          uv run ai-rules rule-loader eval --out-dir out/baseline-$i \\
            --label baseline-run-$i
        done
        uv run ai-rules rule-loader merge-snapshots \\
          out/baseline-1 out/baseline-2 out/baseline-3 \\
          -o out/baseline-merged --label baseline-merged
        uv run ai-rules rule-loader compare out/baseline-merged out/post
    """
    from ai_rules.rule_loader_eval.compare import (
        merge_snapshots,
        render_merge_summary,
    )
    from ai_rules.rule_loader_eval.snapshot import (
        read_eval_snapshot,
        write_eval_snapshot,
    )

    if len(snapshot_dirs) < 2:
        log_error("merge-snapshots requires at least 2 snapshot directories")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    snapshots = []
    for d in snapshot_dirs:
        try:
            snapshots.append(read_eval_snapshot(d))
        except (FileNotFoundError, ValueError) as exc:
            log_error(f"failed to read snapshot {d}: {exc}")
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    try:
        merged = merge_snapshots(snapshots, label=label)
    except ValueError as exc:
        log_error(str(exc))
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    write_eval_snapshot(out_dir, list(merged.fixtures), merged.meta)
    for line in render_merge_summary(merged, len(snapshots)):
        log_info(line)
    log_success(f"wrote merged snapshot to {out_dir}")


# ---------------------------------------------------------------------------
# compare (A/B diff between two snapshots)
# ---------------------------------------------------------------------------


@rule_loader_app.command("compare")
def compare_cmd(
    baseline_dir: Annotated[
        Path,
        typer.Argument(help="Snapshot directory for the baseline state."),
    ],
    post_dir: Annotated[
        Path,
        typer.Argument(help="Snapshot directory for the post-change state."),
    ],
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Output format: table (default), json, or markdown.",
        ),
    ] = "table",
    alias_map: Annotated[
        Path | None,
        typer.Option(
            "--alias-map",
            help=(
                "JSON file mapping {old_rule_path: new_rule_path}. Used to "
                "neutralize cosmetic renames (e.g. 002i -> 002-rule-governance) "
                "so they do not show as drift. Optional."
            ),
        ),
    ] = None,
    exit_on_regression: Annotated[
        bool,
        typer.Option(
            "--exit-on-regression",
            help=(
                "Upgrade the advisory drift-only exit code (2) to the regression "
                "code (1) so any drift fails CI."
            ),
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help=(
                "Show full per-fixture blocks for load-drift-only fixtures and include "
                "universal-churn rules in per-fixture blocks. Default collapses both "
                "to summary lines."
            ),
        ),
    ] = False,
    ignore_flaky: Annotated[
        bool,
        typer.Option(
            "--ignore-flaky/--no-ignore-flaky",
            help=(
                "Exclude fixtures whose post-snapshot flake_score >= --flake-threshold "
                "from the REGRESSIONS bucket (they appear under FLAKY instead). "
                "Default True under v3.15.0 — flaky fixtures are advisory and do not gate the verdict."
            ),
        ),
    ] = True,
    flake_threshold: Annotated[
        float,
        typer.Option(
            "--flake-threshold",
            help="Jaccard-distance threshold for classifying a fixture as flaky (default 0.50 under v3.15.0).",
        ),
    ] = 0.50,
) -> None:
    """Diff two rule-loader snapshots and emit a delta report.

    Snapshots are produced by ``rule-loader eval --out-dir <dir>`` (and
    optionally ``refresh-all --out-dir <dir>``). The diff focuses on
    outcomes (pass/fail, loaded set, signal/citation drift, timing) so it
    survives schema or rule-discovery changes.

    Exit codes:

    - ``0`` — no per-fixture changes; rule loading is byte-identical.
    - ``2`` — drift detected (loaded sets shifted) but no pass→fail
      regressions. Advisory; review and decide.
    - ``1`` — at least one fixture regressed (pass → fail). Block landing.

    Pass ``--exit-on-regression`` to treat any drift as a hard failure.
    """
    from ai_rules.rule_loader_eval.compare import (
        EXIT_DRIFT_ONLY,
        EXIT_NO_CHANGE,
        EXIT_REGRESSION,
        compare_snapshots,
        parse_alias_map,
        render_json,
        render_markdown,
        render_table,
    )
    from ai_rules.rule_loader_eval.snapshot import read_eval_snapshot

    if output_format not in {"table", "json", "markdown"}:
        log_error(f"--format must be one of table|json|markdown, got {output_format!r}")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    try:
        baseline = read_eval_snapshot(baseline_dir)
        post = read_eval_snapshot(post_dir)
    except (FileNotFoundError, ValueError) as exc:
        log_error(f"failed to read snapshot: {exc}")
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    try:
        aliases = parse_alias_map(alias_map)
    except ValueError as exc:
        log_error(f"invalid --alias-map: {exc}")
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    report = compare_snapshots(
        baseline,
        post,
        alias_map=aliases,
        flake_threshold=flake_threshold,
        ignore_flaky=ignore_flaky,
    )

    if output_format == "table":
        for line in render_table(report, verbose=verbose):
            print(line)
    elif output_format == "json":
        print(render_json(report))
    else:  # markdown
        for line in render_markdown(report, verbose=verbose):
            print(line)

    code = report.exit_code
    if exit_on_regression and code == EXIT_DRIFT_ONLY:
        code = EXIT_REGRESSION
    if code != EXIT_NO_CHANGE:
        raise typer.Exit(code)


# ---------------------------------------------------------------------------
# suggest-kw (kw: improvement proposals from fixture outcome)
# ---------------------------------------------------------------------------


@rule_loader_app.command("suggest-kw")
def suggest_kw_cmd(
    fixture_id: Annotated[
        str | None,
        typer.Argument(
            help=(
                "Fixture id to analyse (e.g. 'complex-snowcli-deploy'). "
                "Omit to analyse all failing fixtures in --from-snapshot."
            )
        ),
    ] = None,
    from_snapshot: Annotated[
        Path | None,
        typer.Option(
            "--from-snapshot",
            help=(
                "Snapshot directory produced by 'rule-loader eval --out-dir'. "
                "When provided, uses the snapshot's missing_required and "
                "forbidden_present data instead of running live eval."
            ),
        ),
    ] = None,
    rule: Annotated[
        str | None,
        typer.Option(
            "--rule",
            help="Restrict suggestions to a single rule path (relative, e.g. 'rules/109b-....md').",
        ),
    ] = None,
    top_k: Annotated[
        int,
        typer.Option("--top-k", help="Number of candidate kw: terms to show per rule."),
    ] = 5,
) -> None:
    """Propose kw: edits to fix missing-required and spurious-load failures.

    Mines the fixture prompt for IDF-scored n-gram candidates and shows
    exactly which kw: to add (missing-required) or narrow (spurious).

    Examples::

        uv run ai-rules rule-loader suggest-kw complex-snowcli-deploy
        uv run ai-rules rule-loader suggest-kw --from-snapshot out/post-v3.3
    """
    from ai_rules.rule_loader_eval.fixtures import load_fixture
    from ai_rules.rule_loader_eval.kw_suggester import (
        KwProposal,
        render_proposals_table,
        suggest_for_fixture,
    )
    from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata
    from ai_rules.rule_loader_eval.snapshot import read_eval_snapshot

    project_root = find_project_root()
    rules_meta = load_rules_metadata(_rules_dir(project_root))

    if from_snapshot is not None:
        try:
            snap = read_eval_snapshot(from_snapshot)
        except (FileNotFoundError, ValueError) as exc:
            log_error(f"failed to read snapshot: {exc}")
            raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

        fx_rows = [f for f in snap.fixtures if (fixture_id is None or f.fixture_id == fixture_id)]
        if not fx_rows:
            log_error(
                f"fixture {fixture_id!r} not found in snapshot"
                if fixture_id
                else "snapshot contains no fixtures"
            )
            raise typer.Exit(EXIT_FIXTURE_INVALID)

        all_proposals: list[KwProposal] = []
        for fx_snap in fx_rows:
            if fx_snap.passed and not fx_snap.missing_required:
                continue
            try:
                fx = load_fixture(_fixtures_dir(project_root), fx_snap.fixture_id)
            except Exception:
                continue
            missing = list(fx_snap.missing_required)
            spurious = [
                r
                for r in fx_snap.loaded
                if r not in set(fx_snap.expected_required)
                and r not in set(fx_snap.expected_dependencies)
                and r not in set(fx_snap.expected_optional)
            ]
            if rule:
                missing = [r for r in missing if r == rule]
                spurious = [r for r in spurious if r == rule]
            proposals = suggest_for_fixture(fx.prompt, missing, spurious, rules_meta, top_k=top_k)
            if proposals:
                print(f"\n=== {fx_snap.fixture_id} ===")
                for line in render_proposals_table(proposals):
                    print(line)
            all_proposals.extend(proposals)
        if not all_proposals:
            print("No proposals — all fixtures passed or have no missing/spurious rules.")
        return

    if fixture_id is None:
        log_error("provide a fixture id or pass --from-snapshot")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    try:
        fx = load_fixture(_fixtures_dir(project_root), fixture_id)
    except Exception as exc:
        log_error(f"failed to load fixture {fixture_id!r}: {exc}")
        raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    missing = list(fx.required)
    spurious: list[str] = []
    if rule:
        missing = [r for r in missing if r == rule]
    proposals = suggest_for_fixture(fx.prompt, missing, spurious, rules_meta, top_k=top_k)
    print(f"\n=== {fixture_id} ===")
    for line in render_proposals_table(proposals):
        print(line)


def _replay_text(text: str, *, prefix: str = "[sdk] ") -> None:
    """Replay captured SDK output to the real stderr after Live exits.

    Mirrors :func:`replay_buffer` but accepts plain text so the alternate
    screen can be torn down before the replay reaches the terminal.
    """
    if not text:
        return
    for line in text.splitlines():
        if line.strip():
            print(f"{prefix}{line}", file=sys.__stderr__)


def _drive_live(
    fixture_id: str,
    prompt: str,
    *,
    max_turns: int,
    effort: str,
    model: str,
    connection: str | None,
) -> AgentRun:
    """Common path used by `create` and `refresh`: SDK guard + run_live."""
    _ensure_sdk_and_connection()
    from ai_rules.rule_loader_eval.agent_runner import run_live

    root = find_project_root()
    return run_live(
        fixture_id,
        prompt,
        project_root=root,
        max_turns=max_turns,
        effort=effort,
        model=model,
        connection=connection,
    )


def _emit_diagnostics(run: AgentRun, *, debug: bool, effort: str, model: str) -> None:
    """Print warnings + (when --debug) full diagnostic dump and per-event timing to stderr."""
    if run.disagreements:
        log_warning(format_disagreement_warning(run))
    drift_msg = format_citation_drift_warning_for_run(run)
    if drift_msg:
        log_warning(drift_msg)
    if not debug:
        return
    for line in format_debug(run):
        print(line, file=sys.stderr)
    for line in format_timing_lines(run, effort=effort, model=model):
        print(line, file=sys.stderr)


def format_citation_drift_warning_for_run(run: AgentRun) -> str | None:
    """Compute drift for an AgentRun and format it; None when clean."""
    from ai_rules.rule_loader_eval.diagnostics import citation_drift

    rules_meta = load_rules_metadata(_rules_dir(find_project_root()))
    drifts = citation_drift(run, rules_meta)
    return format_citation_drift_warning(drifts)


def _extract_id(fixture_path: Path) -> str | None:
    """Read top-level `id:` from an existing fixture YAML, if present."""
    import yaml

    try:
        raw = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if isinstance(raw, dict):
        value = raw.get("id")
        if isinstance(value, str) and value:
            return value
    return None


def _extract_variant(fixture_path: Path) -> str:
    """Read top-level `variant:` from an existing fixture YAML; default 'simple'."""
    import yaml

    try:
        raw = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return "simple"
    if isinstance(raw, dict):
        value = raw.get("variant")
        if isinstance(value, str) and value in {"simple", "complex"}:
            return value
    return "simple"
