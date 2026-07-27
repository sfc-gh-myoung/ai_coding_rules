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

import asyncio
import difflib
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.table import Table

from ai_rules._shared.console import (
    console,
    err_console,
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
    from ai_rules.rule_loader_eval.results_writer import (
        ResultsRunWriter,
        RunPassWriter,
    )

rule_loader_app = typer.Typer(
    name="rule-loader",
    help="Rule Loading Evaluator: live-agent sanity check.",
    no_args_is_help=True,
)

# Register keywords sub-app under rule-loader
from ai_rules.commands.rule_loader.keywords.app import keywords_app  # noqa: E402

rule_loader_app.add_typer(keywords_app, name="keywords")

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
# Plain-log helpers (harness-eval-bench style; replaces the removed Rich
# Live/screen ProgressTracker). Every rule-loader CLI command emits plain
# per-item and per-run lines to stderr via ``err_console`` / the shared
# ``log_*`` helpers; static one-shot summary tables (`_print_results`,
# `_print_aggregate_summary`, `_print_resource_summary`) still use Rich.
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with ``Z`` suffix and seconds precision."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fmt_tokens_human(n: int) -> str:
    """Format token count as e.g. '11.2k', '1.4M' (compact stderr lines)."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _log_run_banner(name: str, *, pid: int, concurrency: int, total: int) -> None:
    """Emit the per-run banner line (analogous to harness's run header)."""
    log_info(f"{name}  pid={pid}  concurrency={concurrency}  total={total}")


def _log_item_start(fixture_id: str) -> None:
    """Emit a per-item start line to stderr."""
    err_console.out(f"[{_utc_now_iso()}] start  {fixture_id}")


def _log_item_finish(
    fixture_id: str,
    *,
    ok: bool,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_cost_usd: float = 0.0,
    duration_ms: int | None = None,
    turns: int = 0,
) -> None:
    """Emit a per-item finish line to stderr with tokens/cost/duration/turns when available."""
    status = "pass" if ok else "fail"
    parts: list[str] = [status]
    if input_tokens or output_tokens:
        parts.append(f"in={_fmt_tokens_human(input_tokens)} out={_fmt_tokens_human(output_tokens)}")
    if total_cost_usd:
        parts.append(f"${total_cost_usd:.4f}")
    if duration_ms is not None and duration_ms > 0:
        parts.append(f"elapsed={duration_ms / 1000:.1f}s")
    parts.append(f"turns={turns}")
    err_console.out(f"[{_utc_now_iso()}] done   {fixture_id}  {' '.join(parts)}")


def _log_run_summary(
    name: str, *, succeeded: int, failed: int, wall_seconds: float | None = None
) -> None:
    """Emit the per-run summary line."""
    total = succeeded + failed
    tail = f" in {wall_seconds:.2f}s" if wall_seconds is not None else ""
    log_info(f"{name}: {succeeded}/{total} succeeded{tail}")


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
) -> None:
    """Run the trigger-evidence invariant; no agent invocation.

    By default, reports every failing fixture (path + id + message) instead
    of bailing on the first error, so a single run shows all problems.
    Pass ``--debug`` / ``-v`` to also print the full Python traceback for
    each failure.
    """
    import traceback

    import yaml as _yaml

    from ai_rules.rule_loader_eval.fixtures import _parse_fixture, validate_fixture

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

    _log_run_banner("validate", pid=os.getpid(), concurrency=1, total=len(yaml_paths))
    for path in yaml_paths:
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        raw_id: str = path.stem
        ok = True
        _log_item_start(path.stem)
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
            _log_item_finish(path.stem, ok=ok)

    if failures:
        for rel, fid, msg in failures:
            log_error(f"{rel} (id={fid}): {msg}")
        log_error(f"{len(failures)} of {len(yaml_paths)} fixture(s) failed validation")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    log_success(f"validated {passed} fixture(s)")

    # ── manifest validation (valid-*.json fixtures) ──────────────────────────
    # Validate every fixtures/rule_loader_eval/manifests/valid-*.json file.
    # These must pass validate_manifest; invalid-* files are for unit tests only.
    import json as _json

    from ai_rules.rule_loader_eval.manifest import load_and_validate_manifest

    manifests_dir = fixtures_dir / "manifests"
    if manifests_dir.is_dir():
        valid_manifest_paths = sorted(p for p in manifests_dir.glob("valid-*.json") if p.is_file())
        manifest_failures: list[tuple[Path, list[str]]] = []
        for mp in valid_manifest_paths:
            mrel = mp.relative_to(root) if mp.is_relative_to(root) else mp
            issues = load_and_validate_manifest(mp)
            if issues:
                manifest_failures.append((mrel, issues))
                if debug:
                    for iss in issues:
                        err_console.print(f"  {iss}")
            else:
                # Extra shape assertion for the token-budget deferral fixture.
                if mp.stem == "valid-token-budget-deferral":
                    try:
                        data = _json.loads(mp.read_text(encoding="utf-8"))
                        non_foundation = [
                            e
                            for e in data.get("load_sequence", [])
                            if e.get("reason_type") != "foundation"
                        ]
                        deferred = data.get("deferred_rules", [])
                        if len(non_foundation) < 1:
                            manifest_failures.append(
                                (
                                    mrel,
                                    [
                                        "token-budget fixture must have >=1 non-foundation "
                                        "entry in load_sequence"
                                    ],
                                )
                            )
                        if len(deferred) < 1:
                            manifest_failures.append(
                                (
                                    mrel,
                                    ["token-budget fixture must have >=1 entry in deferred_rules"],
                                )
                            )
                    except Exception as exc:
                        manifest_failures.append((mrel, [f"shape assertion error: {exc!r}"]))

        if manifest_failures:
            for mrel, missues in manifest_failures:
                for iss in missues:
                    log_error(f"{mrel}: {iss}")
            log_error(f"{len(manifest_failures)} valid manifest fixture(s) failed validation")
            raise typer.Exit(EXIT_FIXTURE_INVALID)

        if valid_manifest_paths:
            log_success(f"validated {len(valid_manifest_paths)} manifest fixture(s)")


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
    debug: bool,
    out_dir: Path | None,
    label: str,
    run_number: int | None = None,
    concurrency: int = 1,
    pass_writer: RunPassWriter | None = None,
    retry_infra: int = 1,
) -> tuple[list[RunResult], bool]:
    """Execute a single eval pass. Returns (results, is_infra_error).

    Fixtures are evaluated through the shared concurrent driver capped at
    ``concurrency`` in-flight (``1`` = sequential). Results are re-sorted to input
    fixture order before printing/snapshot so output is deterministic regardless
    of completion order. Progress is reported as plain per-fixture start/finish
    lines on stderr (harness-eval-bench style); the streaming ``results/``
    layout owned by ``pass_writer`` is the machine-readable interface.

    Fail-fast: the first ``InfraError`` aborts the pass (in-flight fixtures are
    cancelled, queued fixtures are skipped), the aborting fixture is recorded as a
    synthetic INFRA row, cancelled/queued fixtures are surfaced as diagnostics only
    (never as fixture failures or snapshot rows), and ``(results, True)`` is
    returned so the caller skips the snapshot and aborts remaining runs.
    """
    from ai_rules.rule_loader_eval.concurrency import run_concurrent
    from ai_rules.rule_loader_eval.engine import InfraError, run_fixture_async
    from ai_rules.rule_loader_eval.engine import _synthetic_failure as _synth

    desc = f"eval run {run_number}" if run_number is not None else "eval"
    rules_meta = load_rules_metadata(_rules_dir(root))
    index_by_id = {f.id: i for i, f in enumerate(fixtures)}

    # Build prompt factory (always progressive/manifest-based)
    _prompt_cache: dict[str, str] = {}
    from ai_rules.rule_loader_eval.agent_runner import build_prompt

    rules_index_path = root / "rules"
    log_info("[eval] Using production hook pathway (match_rules + micro-kernel)")

    async def _work(fixture: Fixture, slot: int) -> RunResult:
        if fixture.id not in _prompt_cache:
            _prompt_cache[fixture.id] = build_prompt(fixture.prompt, rules_index_path)
        sys_prompt = _prompt_cache[fixture.id]

        last_exc: InfraError | None = None
        for attempt in range(1, retry_infra + 1):
            try:
                return await run_fixture_async(
                    fixture,
                    project_root=root,
                    rules_meta=rules_meta,
                    strict_forbidden=strict_forbidden,
                    max_turns=max_turns,
                    effort=effort,
                    model=model,
                    connection=resolved_connection,
                    system_prompt=sys_prompt,
                )
            except InfraError as exc:
                last_exc = exc
                if attempt < retry_infra:
                    log_info(
                        f"  infra retry {attempt}/{retry_infra} for {fixture.id}"
                        f" (waiting 30s, excluded from timing)"
                    )
                    await asyncio.sleep(30)
        assert last_exc is not None  # loop always runs at least once
        raise last_exc

    def _exc_to_result(fixture: Fixture, exc: Exception) -> RunResult:
        # Non-aborting (non-Infra) per-fixture error -> synthetic FAIL row.
        return _synth(fixture, exc)

    def _on_start(fixture: Fixture, slot: int) -> None:
        _log_item_start(fixture.id)
        if pass_writer is not None:
            pass_writer.mark_fixture_started(fixture.id)

    def _on_outcome(result: RunResult, slot: int) -> None:
        run = result.run
        _log_item_finish(
            result.fixture_id,
            ok=result.passed,
            input_tokens=run.input_tokens if run else 0,
            output_tokens=run.output_tokens if run else 0,
            total_cost_usd=run.total_cost_usd if run else 0.0,
            duration_ms=run.duration_ms if run else 0,
            turns=run.turns if run else 0,
        )
        # Stream transcript then write fixture result. Ordering matches §7.5:
        # transcript first, then <id>.json, then run_meta.json flips to
        # `completed` inside write_fixture_result.
        if pass_writer is not None and run is not None:
            try:
                pass_writer.write_transcript_from_events(result.fixture_id, run.events)
                pass_writer.write_fixture_result(result)
            except OSError as exc:
                log_error(f"results/ writer error for {result.fixture_id}: {exc}")

    _log_run_banner(desc, pid=os.getpid(), concurrency=concurrency, total=len(fixtures))

    try:
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


def _write_pass_artifacts(
    pass_writer: RunPassWriter,
    results: list[RunResult],
    *,
    status: str,
) -> None:
    """Emit per-pass ``summary.json`` and flip ``run_meta.json`` to done.

    Phase 2 helper. Derives per-pass counts + totals from the already-sorted
    ``results`` list and delegates atomic writes to the writer. Kept small so
    Phase 3 (TUI removal) can wire equivalent stderr summary lines without
    touching this helper.
    """
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errors = sum(1 for r in results if getattr(r.run, "is_infra_error", False))
    failed = total - passed - errors
    failures = [r.fixture_id for r in results if not r.passed]

    turns_total = 0
    input_total = 0
    output_total = 0
    duration_total = 0
    cost_total = 0.0
    for r in results:
        run = r.run
        if run is None:
            continue
        turns_total += int(getattr(run, "turns", 0) or 0)
        input_total += int(getattr(run, "input_tokens", 0) or 0)
        output_total += int(getattr(run, "output_tokens", 0) or 0)
        duration_total += int(getattr(run, "duration_ms", 0) or 0)
        cost_total += float(getattr(run, "total_cost_usd", 0.0) or 0.0)

    totals: dict[str, int | float] = {
        "turns": turns_total,
        "input_tokens": input_total,
        "output_tokens": output_total,
        "duration_ms": duration_total,
        "total_cost_usd": cost_total,
    }

    pass_writer.write_pass_summary(
        total=total,
        passed=passed,
        failed=failed,
        errors=errors,
        totals=totals,
        failures=failures,
    )
    pass_writer.finalize_pass(status=status)


def _write_aggregate_and_finalize(
    writer: ResultsRunWriter,
    all_run_results: list[list[RunResult]],
    runs: int,
    *,
    status: str,
) -> None:
    """Compute per-fixture + aggregate totals and write run-root ``summary.json``.

    Phase 2 helper. ``flake_score`` is the fraction of a fixture's runs whose
    result differs from the modal result (§5.4 of the plan).
    """
    from collections import Counter

    fixture_counts: dict[str, Counter[str]] = {}
    fixture_totals: dict[str, int] = {}
    total_cost = 0.0
    total_input = 0
    total_output = 0
    total_duration = 0
    total_signal_disagreements = 0
    total_citation_drifts = 0

    for pass_results in all_run_results:
        for r in pass_results:
            fixture_totals[r.fixture_id] = fixture_totals.get(r.fixture_id, 0) + 1
            counter = fixture_counts.setdefault(r.fixture_id, Counter())
            if getattr(r.run, "is_infra_error", False):
                result_str = "error"
            elif r.passed:
                result_str = "pass"
            else:
                result_str = "fail"
            counter[result_str] += 1

            run = r.run
            if run is not None:
                total_cost += float(getattr(run, "total_cost_usd", 0.0) or 0.0)
                total_input += int(getattr(run, "input_tokens", 0) or 0)
                total_output += int(getattr(run, "output_tokens", 0) or 0)
                total_duration += int(getattr(run, "duration_ms", 0) or 0)
            report = getattr(r, "signal_report", None)
            if report is not None:
                disagreements = getattr(report, "disagreements", ())
                total_signal_disagreements += len(disagreements) if disagreements else 0
            total_citation_drifts += len(r.citation_drifts or ())

    per_fixture: dict[str, dict[str, object]] = {}
    flaky: list[str] = []
    pass_rates: list[float] = []
    for fid, counter in fixture_counts.items():
        n = fixture_totals[fid]
        passes = counter.get("pass", 0)
        fails = counter.get("fail", 0) + counter.get("error", 0)
        modal = counter.most_common(1)[0][1] if counter else n
        flake_score = round((n - modal) / n, 3) if n else 0.0
        pass_rate = round(passes / n, 3) if n else 0.0
        per_fixture[fid] = {
            "n_runs": n,
            "passes": passes,
            "fails": fails,
            "flake_score": flake_score,
            "pass_rate": pass_rate,
        }
        if 0 < passes < n:
            flaky.append(fid)
        pass_rates.append(pass_rate)

    mean_pass_rate = round(sum(pass_rates) / len(pass_rates), 3) if pass_rates else 0.0

    aggregate: dict[str, object] = {
        "schema_version": "ai-rules-eval-aggregate/v1",
        "runs": int(runs),
        "fixture_count": len(fixture_counts),
        "per_fixture": per_fixture,
        "aggregate": {
            "mean_pass_rate": mean_pass_rate,
            "flaky_fixtures": sorted(flaky),
            "total_cost_usd": total_cost,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_duration_ms": total_duration,
            "total_signal_disagreements": total_signal_disagreements,
            "total_citation_drifts": total_citation_drifts,
        },
    }
    writer.write_aggregate_summary(aggregate)  # ty: ignore[invalid-argument-type]
    writer.finalize(status=status)


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
                "Root directory for streaming eval results (default: "
                "'results/'). Each invocation creates a fresh "
                "<model>_<runs>x_<timestamp>/ subdirectory here. "
                "Overrides the AI_RULES_RESULTS_DIR env var when set."
            ),
        ),
    ] = None,
    label: Annotated[
        str,
        typer.Option(
            "--label",
            help="Optional label recorded in manifest.json.",
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
    retry_infra: Annotated[
        int,
        typer.Option(
            "--retry-infra",
            help=(
                "Retry a fixture N times on infra error before fail-fast "
                "(default 1 = no retry). Delay between retries (30s) is "
                "excluded from fixture timing."
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
) -> None:
    r"""Run fixtures through the live Cortex Code Agent SDK.

    Executes --runs passes (default 3) to account for LLM variance. Each
    invocation writes to a fresh ``results/<model>_<runs>x_<timestamp>/``
    directory (override with ``--out-dir`` or the ``AI_RULES_RESULTS_DIR``
    env var). Per-fixture JSON + JSONL transcripts stream to disk as each
    fixture finishes; a run-root ``summary.json`` aggregates across passes.
    An aggregate summary table is also printed to stderr after all runs
    complete showing per-fixture pass rates.

    Use ``--concurrency N`` to evaluate up to N fixtures in parallel WITHIN
    each run (default 1 = sequential; --runs still executes one pass at a
    time). Output is deterministic regardless of completion order: results
    are re-sorted to input-fixture order before tables/snapshots. Unlike
    ``refresh-all`` (default 2), eval defaults to 1 to preserve the
    sequential baseline; N>1 raises live SDK load. The first infra error
    cancels in-flight fixtures, skips queued ones, and aborts remaining
    runs.

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
    Expect higher variance -- use ``--runs 3`` (default) for definitive results.
    """
    if runs < 1:
        log_error("--runs must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if concurrency < 1:
        log_error("--concurrency must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if retry_infra < 1:
        log_error("--retry-infra must be >= 1")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

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

    # Phase 2: streaming results/<run_dir>/ writer. Constructed once per
    # invocation; per-pass writers threaded into _run_single_eval so
    # transcript + <id>.json + run_meta.json are written incrementally as
    # each fixture finishes. `--out-dir` (Phase 3) overrides the results
    # root; env var `AI_RULES_RESULTS_DIR` is a secondary override.
    from ai_rules import __version__ as _ai_rules_version
    from ai_rules.rule_loader_eval.results_writer import (
        ResultsRunWriter,
        build_run_dir_name,
        make_run_context,
        resolve_results_root,
    )

    results_root = resolve_results_root(out_dir)
    run_context = make_run_context(
        model_requested=model,
        effort=effort,
        max_turns=max_turns,
        strict_forbidden=strict_forbidden,
        concurrency=concurrency,
        runs_requested=runs,
        label=label or None,
        connection=resolved_connection,
        ai_rules_version=_ai_rules_version,
        fixture_selection=(fixture_id,) if fixture_id else ("all",),
        fixture_count=len(fixtures),
    )
    _started_dt = datetime.fromisoformat(run_context.started_at)
    _existing = (
        {p.name for p in results_root.iterdir() if p.is_dir()} if results_root.exists() else set()
    )
    _run_dir_name = build_run_dir_name(
        run_context.model_requested,
        run_context.runs_requested,
        _started_dt,
        run_id=run_context.run_id,
        existing=_existing,
    )
    results_writer = ResultsRunWriter(
        root=results_root,
        run_dir_name=_run_dir_name,
        context=run_context,
    )

    all_run_results: list[list[RunResult]] = []
    any_failure = False

    for run_idx in range(1, runs + 1):
        if runs > 1:
            log_info(f"{'═' * 60}")
            log_info(f"Run {run_idx}/{runs}")
            log_info(f"{'═' * 60}")

        pass_writer = results_writer.start_pass(run_idx)

        results, is_infra = _run_single_eval(
            fixtures=fixtures,
            root=root,
            resolved_connection=resolved_connection,
            strict_forbidden=strict_forbidden,
            max_turns=max_turns,
            effort=effort,
            model=model,
            debug=debug,
            out_dir=None,
            label=label,
            run_number=run_idx if runs > 1 else None,
            concurrency=concurrency,
            pass_writer=pass_writer,
            retry_infra=retry_infra,
        )
        all_run_results.append(results)

        _write_pass_artifacts(pass_writer, results, status="failed" if is_infra else "completed")

        if any(not r.passed for r in results):
            any_failure = True

        if is_infra:
            log_error(f"Infra error on run {run_idx}/{runs}. Aborting remaining runs.")
            _write_aggregate_and_finalize(
                results_writer, all_run_results, len(all_run_results), status="failed"
            )
            raise typer.Exit(EXIT_INFRA_ERROR)

    if runs > 1:
        console.print()
        _print_aggregate_summary(all_run_results, runs)

    console.print()
    _print_resource_summary(all_run_results)

    _write_aggregate_and_finalize(
        results_writer,
        all_run_results,
        runs,
        status="failed" if any_failure else "completed",
    )

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
    timing trace to stderr.
    """
    if not fixture_path.exists():
        log_error(f"fixture file not found: {fixture_path}")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    prompt = read_prompt(fixture_path)
    fixture_id = _extract_id(fixture_path)
    variant = _extract_variant(fixture_path)

    fid_for_progress = fixture_id or fixture_path.stem
    _log_item_start(fid_for_progress)
    try:
        run = _drive_live(
            fid_for_progress,
            prompt,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=connection,
        )
        _log_item_finish(
            fid_for_progress,
            ok=True,
            input_tokens=run.input_tokens,
            output_tokens=run.output_tokens,
            total_cost_usd=run.total_cost_usd,
            turns=run.turns,
        )
    except Exception:
        _log_item_finish(fid_for_progress, ok=False)
        raise
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
            help="Write per-fixture YAML + summary.json here (overrides AI_RULES_RESULTS_DIR; CLI > env). Omit both to stream to stdout.",
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
            help="Enable developer diagnostics (timing, signal disagreements, debug dump) to stderr.",
        ),
    ] = False,
) -> None:
    """Batch-capture or refresh fixtures concurrently against the live SDK.

    Resolves ``--glob`` or ``--all`` to a list of fixture YAMLs (defaulting
    to ``--all`` when neither is given), drives each through
    ``run_live_async`` (capped by ``--concurrency``), and writes regenerated
    skeletons either to ``--out-dir`` / ``AI_RULES_RESULTS_DIR`` (per-fixture
    files + ``summary.json``) or stdout. When an output dir is resolved the
    SDK is silenced so stderr stays clean; without one the YAML payload streams
    to stdout alongside SDK output.

    Pass ``--debug`` to also print the full debug dump and per-event
    timing trace for each fixture to stderr (and to replay any captured
    SDK chatter).

    Exit codes:
    - ``0`` -- every fixture succeeded.
    - ``1`` -- at least one fixture failed.
    - ``3`` -- SDK / connection error.
    - ``4`` -- invalid arguments (e.g., concurrency < 1, no fixtures matched).
    """
    import json

    from ai_rules.rule_loader_eval.batch import (
        BatchItem,
        BatchOutcome,
        expand_glob,
        extract_batch_item,
        run_batch,
        validate_unique_output_names,
    )
    from ai_rules.rule_loader_eval.results_writer import resolve_optional_results_root
    from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk

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

    resolved_out_dir = resolve_optional_results_root(out_dir)
    _log_run_banner("refresh-all", pid=os.getpid(), concurrency=concurrency, total=len(items))

    if resolved_out_dir is not None:
        resolved_out_dir.mkdir(parents=True, exist_ok=True)

    # Capture SDK chatter only when an output dir is resolved (§6.2 explicit
    # capture logic). Without one the YAML payload streams to the user's
    # stdout, so muting the SDK gains nothing and just hides diagnostics.
    capture_sdk = resolved_out_dir is not None
    payload_stdout = sys.__stdout__ if capture_sdk else sys.stdout

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
        _log_item_start(item.id)

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
                if resolved_out_dir is not None:
                    invalid_path = resolved_out_dir / f"{outcome.item.safe_id}.yaml.invalid"
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
                _log_item_finish(
                    outcome.item.id,
                    ok=False,
                    input_tokens=outcome.run.input_tokens,
                    output_tokens=outcome.run.output_tokens,
                    total_cost_usd=outcome.run.total_cost_usd,
                    turns=outcome.run.turns,
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
            if resolved_out_dir is not None:
                (resolved_out_dir / f"{outcome.item.safe_id}.yaml").write_text(
                    snippet + "\n", encoding="utf-8"
                )
            else:
                # No output dir resolved: stream YAML straight to stdout alongside SDK output.
                print(f"# fixture: {outcome.item.id}", file=payload_stdout)
                print(snippet, file=payload_stdout)
                print(file=payload_stdout)
            if debug:
                _emit_diagnostics(outcome.run, debug=True, effort=effort, model=model)
        finally:
            if not finish_called:
                _run = outcome.run
                _log_item_finish(
                    outcome.item.id,
                    ok=outcome.succeeded,
                    input_tokens=_run.input_tokens if _run else 0,
                    output_tokens=_run.output_tokens if _run else 0,
                    total_cost_usd=_run.total_cost_usd if _run else 0.0,
                    turns=_run.turns if _run else 0,
                )

    # Suppress SDK chatter only when an output dir is resolved (quiet_sdk is a no-op
    # when capture=False). Top-level try/except handles SIGINT so
    # KeyboardInterrupt still surfaces cleanly.
    sdk_replay_text: str = ""
    summary = None
    pending_runtime_error: RuntimeError | None = None
    pending_other: BaseException | None = None
    try:
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
                if sdk_buf is not None:
                    sdk_replay_text = sdk_buf.getvalue()
                raise
            except Exception as exc:
                pending_other = exc
            else:
                if debug and sdk_buf is not None:
                    sdk_replay_text = sdk_buf.getvalue()
                assert summary is not None
                _log_run_summary(
                    "refresh-all",
                    succeeded=summary.succeeded,
                    failed=summary.failed,
                    wall_seconds=summary.wall_seconds,
                )
            if (
                pending_runtime_error is not None or pending_other is not None
            ) and sdk_buf is not None:
                sdk_replay_text = sdk_buf.getvalue()
    except KeyboardInterrupt:
        if sdk_replay_text:
            _replay_text(sdk_replay_text)
        log_warning("interrupted by user; in-flight calls cancelled")
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

    if resolved_out_dir is not None:
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
        (resolved_out_dir / "summary.json").write_text(
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
                "neutralize cosmetic renames (e.g. old-rule.md -> new-rule.md) "
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
    from ai_rules.rule_loader_eval.diagnostics import version_citation_drift

    rules_meta = load_rules_metadata(_rules_dir(find_project_root()))
    drifts = version_citation_drift(run, rules_meta)
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


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


@rule_loader_app.command("report")
def report_cmd(
    fmt: Annotated[
        str,
        typer.Option("--format", help="Output format: html, md, both"),
    ] = "both",
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output directory (defaults to <project_root>/reports/)"),
    ] = None,
    results_dir: Annotated[
        Path | None,
        typer.Option(
            "--results-dir", help="Results directory (defaults to <project_root>/results/)"
        ),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail on any extraction error instead of skipping model"),
    ] = False,
) -> None:
    """Generate compliance reports from eval results.

    Discovers the latest run per model in --results-dir, extracts statistics,
    and renders HTML and/or Markdown reports to --output.
    """
    from ai_rules.rule_loader_eval.report_generator import generate_reports

    project_root = find_project_root()
    resolved_results = results_dir if results_dir is not None else project_root / "results"
    resolved_output = output if output is not None else project_root / "reports"

    if not resolved_results.exists() or not resolved_results.is_dir():
        log_error(
            f"Results directory not found: {resolved_results}\n"
            "Pass --results-dir <path> to specify the location of eval results."
        )
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    # Validate that at least one summary.json exists
    summaries = list(resolved_results.glob("*/summary.json"))
    if not summaries:
        log_error(
            f"No summary.json files found under {resolved_results}\n"
            "Run 'ai-rules rule-loader eval' first to produce results."
        )
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    formats: list[str]
    if fmt == "both":
        formats = ["html", "md"]
    elif fmt in ("html", "md"):
        formats = [fmt]
    else:
        log_error(f"Unknown format {fmt!r}. Use html, md, or both.")
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    if strict:
        # In strict mode, validate extraction before rendering
        from ai_rules.rule_loader_eval.report_generator import (
            discover_results,
            extract_model_stats,
        )

        discovered = discover_results(resolved_results)
        if not discovered:
            log_error("No valid result directories found.")
            raise typer.Exit(EXIT_FIXTURE_INVALID)
        for model, run_dir in sorted(discovered.items()):
            try:
                extract_model_stats(run_dir)
            except Exception as exc:
                log_error(f"Extraction failed for model {model!r}: {exc}")
                raise typer.Exit(EXIT_FIXTURE_INVALID) from exc

    written = generate_reports(
        results_dir=resolved_results,
        output_dir=resolved_output,
        formats=formats,
    )

    if not written:
        log_error(
            "No reports were generated. Check --results-dir contains valid summary.json files."
        )
        raise typer.Exit(EXIT_FIXTURE_INVALID)

    for path in written:
        log_success(f"Report written: {path}")
    raise typer.Exit(EXIT_OK)
