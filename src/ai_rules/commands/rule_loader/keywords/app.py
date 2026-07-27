"""CLI app, commands, and display helpers for the keywords subcommand."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
import typer.core
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from ai_rules._shared.console import (
    console,
    log_error,
    log_info,
    log_success,
    log_warning,
)
from ai_rules.commands.rule_loader.keywords.cache import (
    _load_cache,
    _save_cache,
    update_cache_atomic,
)
from ai_rules.commands.rule_loader.keywords.client import (
    load_snowflake_config,
)
from ai_rules.commands.rule_loader.keywords.collision import (
    _load_exclude_list,
    build_keyword_collision_map,
    find_collision_violations,
)
from ai_rules.commands.rule_loader.keywords.extractor import (
    ExtractionResult,
    KeywordExtractor,
    _deduplicate_across_rules,
)
from ai_rules.commands.rule_loader.keywords.formatting import (
    _emit_rationale_jsonl,
    update_keywords_in_file,
)
from ai_rules.commands.rule_loader.keywords.stoplist import (
    CACHE_FILENAME,
    SKIP_FILES,
    _get_repo_root,
)

# Default keyword count when --count is not passed explicitly
_DEFAULT_COUNT = 6


# ---------------------------------------------------------------------------
# _KeywordsGroup: routes positional paths to 'run' subcommand
# ---------------------------------------------------------------------------


class _KeywordsGroup(typer.core.TyperGroup):
    """Typer group that routes unknown positional args to the ``run`` subcommand.

    Preserves the historical ``ai-rules keywords <path> [--flags]``
    invocation shape while enabling real subcommands like
    ``ai-rules keywords collisions``.
    """

    def resolve_command(self, ctx, args):
        if not args or args[0] not in self.commands:
            args = ["run", *args]
        return super().resolve_command(ctx, args)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def print_diff_rich(result: ExtractionResult) -> None:
    """Print a rich diff between current and suggested keywords."""
    current_lines = []
    suggested_lines = []

    current_lower = {k.lower() for k in result.current_keywords}
    suggested_lower = {k.lower() for k in result.suggested_keywords}

    for kw in result.current_keywords:
        if kw.lower() in suggested_lower:
            current_lines.append(f"[dim]{kw}[/dim]")
        else:
            current_lines.append(f"[red strikethrough]{kw}[/red strikethrough]")

    for kw in result.suggested_keywords:
        if kw.lower() in current_lower:
            suggested_lines.append(f"[dim]{kw}[/dim]")
        else:
            suggested_lines.append(f"[green bold]{kw}[/green bold]")

    current_panel = Panel(
        "\n".join(current_lines) if current_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Current ({len(result.current_keywords)})[/bold]",
        border_style="red",
    )
    suggested_panel = Panel(
        "\n".join(suggested_lines) if suggested_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Suggested ({len(result.suggested_keywords)})[/bold]",
        border_style="green",
    )

    console.print()
    console.print(f"[bold cyan]{result.file_path.name}[/bold cyan]")
    console.print(Columns([current_panel, suggested_panel], equal=True, expand=True))

    if result.removed:
        console.print(
            f"  [red]- Removed ({len(result.removed)}):[/red] {', '.join(sorted(result.removed))}"
        )
    if result.added:
        console.print(
            f"  [green]+ Added ({len(result.added)}):[/green] {', '.join(sorted(result.added))}"
        )
    if result.kept:
        console.print(f"  [dim]= Kept ({len(result.kept)}):[/dim] {', '.join(sorted(result.kept))}")


def print_suggestions_table(results: list[ExtractionResult]) -> None:
    """Print keyword suggestions as a Rich table."""
    table = Table(title="Keyword Suggestions", show_lines=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Current", style="yellow")
    table.add_column("Suggested", style="green")

    for result in results:
        table.add_row(
            result.file_path.name,
            ", ".join(result.current_keywords) if result.current_keywords else "[dim]None[/dim]",
            ", ".join(result.suggested_keywords)
            if result.suggested_keywords
            else "[dim]None[/dim]",
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Typer app
# ---------------------------------------------------------------------------

keywords_app = typer.Typer(
    name="keywords",
    help="Generate semantically relevant keywords for AI coding rule files.",
    invoke_without_command=True,
    no_args_is_help=False,
    cls=_KeywordsGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@keywords_app.callback(invoke_without_command=True)
def _keywords_root(ctx: typer.Context) -> None:
    """Dispatch to ``run`` (with defaults) when no subcommand is invoked."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(keywords, ctx=ctx, path=None)


# ---------------------------------------------------------------------------
# Worker function for ThreadPoolExecutor batch processing
# ---------------------------------------------------------------------------


def _process_one(
    file_path: Path,
    extractor: KeywordExtractor,
    count: int,
    use_api: bool,
    cache: dict,
    force: bool,
    cache_path: Path,
) -> ExtractionResult:
    """Process a single rule file. Called from worker threads.

    Note: _emit_rationale_jsonl must NOT be called from this function;
    it must be called post-batch in the main thread only.
    """
    result = extractor.suggest_keywords(
        file_path,
        count=count,
        use_api=use_api,
        cache=cache,
        force=force,
    )
    # Persist cache entry immediately under a file lock (concurrent-safe)
    from ai_rules.commands.rule_loader.keywords.cache import _content_hash

    content = file_path.read_text(encoding="utf-8")
    update_cache_atomic(
        cache_path,
        str(file_path.resolve()),
        _content_hash(content),
        result.suggested_keywords,
    )
    return result


# ---------------------------------------------------------------------------
# 'run' command
# ---------------------------------------------------------------------------


@keywords_app.command("run")
def keywords(
    ctx: typer.Context,
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to rule file or directory.",
            show_default=False,
        ),
    ] = None,
    connection: Annotated[
        str,
        typer.Option(
            "-c",
            "--connection",
            help="Snowflake connection name from ~/.snowflake/connections.toml.",
        ),
    ] = "default",
    update: Annotated[
        bool,
        typer.Option("--update", "-u", help="Update the Keywords field in-place."),
    ] = False,
    diff: Annotated[
        bool,
        typer.Option("--diff", "-d", help="Show diff between current and suggested keywords."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Bypass cache and re-generate keywords."),
    ] = False,
    count: Annotated[
        int | None,
        typer.Option(
            "--count",
            "-n",
            help=(
                "Maximum number of keywords. LLM chooses 5 to this limit. "
                "Default is 6; pass explicitly to silence the default-change warning. "
                "Use --force-count to bypass the 5-7 range guard."
            ),
        ),
    ] = None,
    force_count: Annotated[
        bool,
        typer.Option(
            "--force-count",
            help="Bypass the 5-7 keyword count guard (for power users).",
        ),
    ] = False,
    model: Annotated[
        str,
        typer.Option(
            "--model",
            help="LLM model name for keyword generation.",
        ),
    ] = "claude-sonnet-4-5",
    workers: Annotated[
        int,
        typer.Option(
            "--workers",
            help="Number of parallel workers for batch (directory) mode. Default 4.",
        ),
    ] = 4,
    deduplicate: Annotated[
        bool,
        typer.Option(
            "--deduplicate",
            "-D",
            help="Remove over-shared keywords across rules (directory only).",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug output."),
    ] = False,
    rationale: Annotated[
        bool,
        typer.Option(
            "--rationale",
            help="Append per-keyword rationale to .workbench/audit/keyword_rationale.jsonl.",
        ),
    ] = False,
    rationale_output: Annotated[
        Path | None,
        typer.Option(
            "--rationale-output",
            help="Override the rationale JSONL destination (default: "
            ".workbench/audit/keyword_rationale.jsonl).",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="Write a JSON manifest of {filename, keywords, rationale} entries "
            "for every processed rule to this path (aggregated after all rules run).",
        ),
    ] = None,
    exclude_list: Annotated[
        Path | None,
        typer.Option(
            "--exclude-list",
            help="Path to the exclude list of rule filenames to omit from --output.",
        ),
    ] = None,
) -> None:
    """Generate semantically relevant keywords for AI coding rule files.

    Uses claude-sonnet-4-5 via Snowflake Cortex to summarize rule content into
    contextually meaningful keywords. High-confidence heuristic signals
    (technology terms, code languages) supplement LLM output.
    Results are cached based on file content hash.

    Reads Snowflake credentials from ~/.snowflake/connections.toml using the
    'default' connection. Override with -c/--connection. Falls back to
    heuristic extraction when credentials are not available.

    Examples:
        # Suggest keywords for a single file
        ai-rules rule-loader keywords run rules/100-snowflake-core.md

        # Use a specific Snowflake connection
        ai-rules rule-loader keywords run rules/ -c my_connection

        # Update the Keywords field in-place
        ai-rules rule-loader keywords run rules/100-snowflake-core.md --update

        # Show diff between current and suggested keywords
        ai-rules rule-loader keywords run rules/100-snowflake-core.md --diff

        # Bypass cache and re-generate
        ai-rules rule-loader keywords run rules/100-snowflake-core.md --force

        # Batch directory with 8 workers
        ai-rules rule-loader keywords run rules/ --workers 8
    """
    # --count sentinel: emit warning when user has not passed --count explicitly
    if count is None:
        log_warning(
            "--count default has changed from 15 to 6; "
            "pass --count explicitly to silence this warning."
        )
        count = _DEFAULT_COUNT

    if path is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    if not path.exists():
        log_error(f"Path does not exist: {path}")
        raise typer.Exit(1)

    extractor = KeywordExtractor(debug=debug, connection_name=connection, model=model)

    use_api = True
    try:
        config = load_snowflake_config(connection)
        account = config.get("account", config.get("accountname", ""))
        token = config.get("token") or config.get("password", "")
        if not account or not token:
            use_api = False
            log_info(
                f"Connection '{connection}' missing account or token; using heuristic fallback"
            )
    except (FileNotFoundError, ValueError) as e:
        use_api = False
        log_info(f"Snowflake connection not available; using heuristic fallback: {e}")

    cache_dir = path if path.is_dir() else path.parent
    cache_path = cache_dir / CACHE_FILENAME
    cache = _load_cache(cache_path)

    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("*.md"))
        files = [f for f in files if f.name not in SKIP_FILES]

    if not files:
        log_error(f"No rule files found in {path}")
        raise typer.Exit(1)

    results: list[ExtractionResult] = []
    updated_count = 0
    unchanged_count = 0

    # Batch mode: use ThreadPoolExecutor when processing a directory with workers > 1
    if path.is_dir() and len(files) > 1 and workers > 1:
        import time as _time

        t0 = _time.monotonic()
        completed: list[ExtractionResult] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _process_one, f, extractor, count, use_api, dict(cache), force, cache_path
                ): f
                for f in files
            }
            for future in as_completed(futures):
                fp = futures[future]
                try:
                    completed.append(future.result())
                except Exception as e:
                    log_error(f"Error processing {fp}: {e}")
                    if debug:
                        raise
        # Sort results to match file order for deterministic output
        name_to_result = {r.file_path.name: r for r in completed}
        results = [name_to_result[f.name] for f in files if f.name in name_to_result]
        elapsed = _time.monotonic() - t0
        log_info(f"Processed {len(results)} rules in {elapsed:.1f}s ({workers} workers)")
        # Reload cache (workers wrote atomically; merge back for _save_cache below)
        cache = _load_cache(cache_path)
    else:
        for file_path in files:
            try:
                result = extractor.suggest_keywords(
                    file_path,
                    count=count,
                    use_api=use_api,
                    cache=cache,
                    force=force,
                )
                results.append(result)
            except Exception as e:
                log_error(f"Error processing {file_path}: {e}")
                if debug:
                    raise

    if deduplicate and len(results) > 1:
        _deduplicate_across_rules(results)

    for result in results:
        if diff:
            print_diff_rich(result)
        elif update:
            if update_keywords_in_file(result.file_path, result.suggested_keywords):
                log_success(f"Updated: {result.file_path.name}")
                updated_count += 1
            else:
                log_info(f"No change: {result.file_path.name}")
                unchanged_count += 1

    # Save cache (sequential path — batch path already wrote atomically per file)
    if not (path.is_dir() and len(files) > 1 and workers > 1):
        _save_cache(cache_path, cache)

    # T7: emit per-keyword rationale JSONL — ALWAYS in main thread, never from workers
    if rationale:
        target = rationale_output or (
            _get_repo_root() / ".workbench" / "audit" / "keyword_rationale.jsonl"
        )
        emitted = _emit_rationale_jsonl(results, target)
        log_success(f"Appended {emitted} rationale entries to {target} (rules={len(results)})")

    # Emit aggregate JSON manifest
    if output is not None:
        excluded = _load_exclude_list(exclude_list)
        manifest_entries = [
            {
                "filename": r.file_path.name,
                "keywords": list(r.suggested_keywords),
                "rationale": dict(r.rationale_map),
            }
            for r in results
            if r.file_path.name not in excluded
        ]
        manifest = {
            "generated_at": datetime.now(UTC).isoformat(),
            "count_limit": count,
            "connection": connection,
            "source_path": str(path),
            "rule_count": len(manifest_entries),
            "excluded_count": len(results) - len(manifest_entries),
            "rules": manifest_entries,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        log_success(
            f"Wrote keyword manifest to {output} "
            f"(rules={len(manifest_entries)}, excluded={manifest['excluded_count']})"
        )

    if not diff and not update:
        print_suggestions_table(results)

    if update:
        console.print()
        if updated_count > 0:
            log_success(f"Updated {updated_count} file(s)")
        if unchanged_count > 0:
            log_info(f"Unchanged: {unchanged_count} file(s)")


# ---------------------------------------------------------------------------
# 'collisions' command
# ---------------------------------------------------------------------------


@keywords_app.command("collisions")
def collisions_command(
    rules_dir: Annotated[
        Path,
        typer.Option("--rules-dir", help="Directory containing rule files."),
    ] = Path("rules"),
    max_collision: Annotated[
        int,
        typer.Option(
            "--max-collision",
            help="Report tokens appearing in strictly more than this many production rules.",
        ),
    ] = 3,
    exclude_list: Annotated[
        Path | None,
        typer.Option(
            "--exclude-list",
            help="Path to the exclude list of rule filenames to omit from counts.",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="Write JSON collision report to this path (stdout when omitted).",
        ),
    ] = None,
) -> None:
    """Emit a JSON collision map for keywords across production rules.

    Reads rule frontmatter from ``<rules_dir>`` and produces the map
    ``{keyword: [<rule filenames>...]}``. ``--max-collision`` also surfaces
    the violating subset in the JSON payload.
    """
    if not rules_dir.exists():
        log_error(f"rules-dir not found at {rules_dir}")
        raise typer.Exit(1)

    collision_map = build_keyword_collision_map(
        rules_index_path=None,
        exclude_list_path=exclude_list,
    )
    violations = find_collision_violations(collision_map, max_collision)

    report = {
        "rules_dir": str(rules_dir),
        "max_collision": max_collision,
        "total_keywords": len(collision_map),
        "violation_count": len(violations),
        "collision_map": collision_map,
        "violations": violations,
    }

    payload = json.dumps(report, indent=2, sort_keys=True)

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        log_success(
            f"Wrote collision report to {output} "
            f"(keywords={len(collision_map)}, violations={len(violations)})"
        )
    else:
        console.print(payload)
