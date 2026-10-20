"""Deterministic report selection, generation, and artifact verification commands."""

import json
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import log_error, log_info, log_success
from ai_rules._shared.paths import find_project_root
from ai_rules.rule_loader_eval.evidence_report import (
    ReportError,
    build_payload,
    create_selection,
    load_selection,
    verify_artifact,
    write_generation,
)
from ai_rules.rule_loader_eval.report_generator import discover_results


def report_cmd(
    output: Annotated[
        Path | None, typer.Option("--output", help="Parent for immutable report generations.")
    ] = None,
    results_dir: Annotated[
        Path | None, typer.Option("--results-dir", help="Latest-run inspection root; no rankings.")
    ] = None,
    selection: Annotated[
        Path | None,
        typer.Option("--selection", help="Explicit evidence-bound comparison selection JSON."),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict", help="Accepted for compatibility; evidence errors always fail closed."
        ),
    ] = False,
    connection: Annotated[
        str | None,
        typer.Option(
            "--connection", help="Compatibility option; local reports never authenticate."
        ),
    ] = None,
) -> None:
    """Render an offline comparison from explicit selection, or labeled inspection."""
    if selection is not None and results_dir is not None:
        log_error("--selection and --results-dir are mutually exclusive")
        raise typer.Exit(4)
    if connection:
        log_info("--connection is not used: deterministic local reporting makes no AI or SQL calls")
    try:
        root = find_project_root()
        if selection:
            selected = load_selection(selection)
        else:
            discovered = discover_results(results_dir or root / "results")
            selected = create_selection(list(discovered.values()))
        payload = build_payload(selected, inspection=selection is None)
        generation = write_generation(payload, output or root / "reports")
        log_success(f"Report written: {generation / 'report.html'}")
        log_success(f"Evidence written: {generation / 'report.json'}")
    except (ReportError, OSError) as exc:
        log_error(str(exc))
        raise typer.Exit(4) from exc


def verify_report_cmd(
    generation: Annotated[
        Path, typer.Argument(help="Directory containing report.html and report.json.")
    ],
) -> None:
    """Verify artifact contract, embedded data, source hashes, and exact metrics."""
    try:
        totals = verify_artifact(generation)
    except (ReportError, OSError, ValueError) as exc:
        log_error(str(exc))
        raise typer.Exit(4) from exc
    log_success(f"Verified {totals['observed']} observed / {totals['planned']} planned samples")


def select_report_cmd(
    runs: Annotated[list[Path], typer.Argument(help="Exact selected run directories.")],
    output: Annotated[Path, typer.Option("--output", help="New selection JSON; never overwrites.")],
    archives: Annotated[
        list[Path] | None,
        typer.Option(
            "--archive", help="Interrupted evidence retained outside competitive metrics."
        ),
    ] = None,
    excluded: Annotated[
        list[str] | None,
        typer.Option("--exclude", help="Model=reason; repeat for explicit exclusions."),
    ] = None,
) -> None:
    """Snapshot exact local runs and embedded rates before comparative reporting."""
    try:
        exclusions = {}
        for entry in excluded or []:
            model, separator, reason = entry.partition("=")
            if not separator or not model or not reason or model in exclusions:
                raise ReportError("Each exclusion must be a unique model=reason")
            exclusions[model] = reason
        selection = create_selection(runs, archives=archives, exclusions=exclusions)
        build_payload(selection)
        if any(output.resolve().is_relative_to(path.resolve()) for path in runs + (archives or [])):
            raise ReportError("Selection output must not be inside source evidence")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(selection, indent=2, allow_nan=False) + "\n")
    except (ReportError, OSError) as exc:
        log_error(str(exc))
        raise typer.Exit(4) from exc
    log_success(f"Selection written: {output}")
