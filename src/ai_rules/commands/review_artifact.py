"""Typer command group for review artifact operations.

Commands
--------
  validate      Validate a canonical review JSON against rule-review-result/v1.
  render        Render a canonical review JSON to deterministic Markdown.
  verify-pair   Verify a JSON/Markdown pair for integrity.
  verify-repair Verify a repair candidate changes only allowed JSON pointers.
  aggregate     Summarize multiple accepted review JSONs.

Exit codes (shared across all commands)
----------------------------------------
  0  Success.
  1  LLM-authored schema or semantic violation — preserve rejected JSON; request
     bounded repair of listed paths.
  2  Missing, unreadable, invalid UTF-8, or invalid JSON input — retry producer
     only if no usable artifact exists.
  3  Deterministic implementation or pair-integrity defect — stop; do not consume
     an LLM retry.
  4  Repair-integrity violation — preserve candidate and retry within the cap.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ai_rules.review_results import (
    SCHEMA_VERSION,
    extract_integrity_footer,
    load_and_validate_review,
    render_review_markdown,
    validate_review_result,
)

review_artifact_app = typer.Typer(
    name="review-artifact",
    help="Operations on canonical rule-review-result/v1 JSON artifacts.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

_out = Console(stderr=False)
_err = Console(stderr=True)


def _emit_json(payload: dict, *, err: bool = False) -> None:
    """Write a machine-readable JSON payload as plain text.

    These payloads (aggregate summaries, typed diagnostics) are a data contract
    consumed by automation, so they must never carry Rich syntax-highlighting
    ANSI. Rich's ``print_json`` colorizes whenever the singleton console detects
    a color terminal, which corrupts downstream ``json.loads``. Emitting plain
    text via ``print`` keeps stdout/stderr parseable regardless of color state.
    """
    stream = sys.stderr if err else sys.stdout
    print(json.dumps(payload, indent=2, sort_keys=False), file=stream)


def _typed_diagnostic(
    status: str,
    error_class: str,
    errors: list[dict],
    repairable_paths: list[str] | None = None,
) -> dict:
    d: dict = {
        "status": status,
        "error_class": error_class,
        "artifact_kind": "rule-review",
        "errors": errors,
    }
    if repairable_paths is not None:
        d["repairable_paths"] = repairable_paths
    return d


def _issue_to_error(issue: str) -> dict:
    """Convert a validator issue string to a typed error dict."""
    path = issue.split(":")[0] if issue.startswith("/") else "/unknown"
    return {
        "code": "semantic_violation",
        "path": path,
        "message": issue,
        "remediation": "Correct the field and resubmit.",
    }


# ── validate ──────────────────────────────────────────────────────────────────


@review_artifact_app.command(name="validate")
def validate_cmd(
    input: Annotated[Path, typer.Option("--input", "-i", help="Path to review JSON file.")],
) -> None:
    """Validate a canonical rule-review-result/v1 JSON file.

    Exit 0 if valid; exit 1 on semantic violations; exit 2 on I/O errors.
    """
    try:
        issues = load_and_validate_review(input)
    except ValueError as exc:
        diagnostic = _typed_diagnostic(
            "failed",
            "io_error",
            [
                {
                    "code": "io_error",
                    "path": "/",
                    "message": str(exc),
                    "remediation": "Check the file exists and is valid JSON.",
                }
            ],
        )
        _emit_json(diagnostic, err=True)
        raise typer.Exit(2) from None

    if not issues:
        _out.print(f"[green]valid[/green] {input}")
        return

    errors = [_issue_to_error(i) for i in issues]
    repairable = list({e["path"] for e in errors})
    diagnostic = _typed_diagnostic("failed", "semantic_violation", errors, repairable)
    _emit_json(diagnostic, err=True)
    raise typer.Exit(1)


# ── render ────────────────────────────────────────────────────────────────────


@review_artifact_app.command(name="render")
def render_cmd(
    input: Annotated[Path, typer.Option("--input", "-i", help="Path to review JSON file.")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Path to write rendered Markdown.")
    ],
    replace: Annotated[
        bool, typer.Option("--replace", help="Overwrite existing output file.")
    ] = False,
) -> None:
    """Render a review JSON to deterministic Markdown with an integrity footer.

    Exit 0 on success; exit 2 on I/O error; exit 3 on defect.
    """
    try:
        raw = input.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as exc:
        _err.print(f"[red]error[/red] cannot read {input}: {exc}")
        raise typer.Exit(2) from None

    try:
        review = json.loads(raw)
    except json.JSONDecodeError as exc:
        _err.print(f"[red]error[/red] invalid JSON in {input}: {exc}")
        raise typer.Exit(2) from None

    if output.exists() and not replace:
        _err.print(f"[red]error[/red] {output} already exists; use --replace to overwrite")
        raise typer.Exit(3) from None

    try:
        md = render_review_markdown(review, json_path=input)
    except Exception as exc:
        _err.print(f"[red]defect[/red] renderer error: {exc}")
        raise typer.Exit(3) from None

    output.write_text(md, encoding="utf-8")
    _out.print(f"[green]rendered[/green] {output}")


# ── verify-pair ───────────────────────────────────────────────────────────────


@review_artifact_app.command(name="verify-pair")
def verify_pair_cmd(
    input: Annotated[Path, typer.Option("--input", "-i", help="Path to canonical review JSON.")],
    markdown: Annotated[Path, typer.Option("--markdown", "-m", help="Path to rendered Markdown.")],
) -> None:
    """Verify a JSON/Markdown pair for integrity.

    Exit 0 if the pair is valid and the Markdown is byte-for-byte identical to a
    fresh render from the JSON. Exit 3 on any integrity violation (hand-edited
    Markdown, changed JSON, missing sentinel, or mismatched SHA-256).
    """
    # Load JSON
    try:
        raw_json = input.read_text(encoding="utf-8")
        review = json.loads(raw_json)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _err.print(f"[red]error[/red] cannot read JSON: {exc}")
        raise typer.Exit(2) from None

    # Load Markdown
    try:
        md_text = markdown.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as exc:
        _err.print(f"[red]error[/red] cannot read Markdown: {exc}")
        raise typer.Exit(2) from None

    # Extract footer
    try:
        extract_integrity_footer(md_text)
    except ValueError as exc:
        _err.print(f"[red]pair-integrity defect[/red] {exc}")
        raise typer.Exit(3) from None

    # Byte-rerender and compare
    try:
        rerendered = render_review_markdown(review, json_path=input)
    except Exception as exc:
        _err.print(f"[red]defect[/red] renderer error during verification: {exc}")
        raise typer.Exit(3) from None

    if md_text != rerendered:
        _err.print(
            "[red]pair-integrity defect[/red] Markdown does not match a fresh render "
            "from the JSON. The Markdown may have been hand-edited or the JSON changed."
        )
        raise typer.Exit(3) from None

    _out.print(f"[green]verified[/green] pair {input} + {markdown}")


# ── verify-repair ─────────────────────────────────────────────────────────────


@review_artifact_app.command(name="verify-repair")
def verify_repair_cmd(
    baseline: Annotated[Path, typer.Option("--baseline", help="Path to original rejected JSON.")],
    candidate: Annotated[
        Path, typer.Option("--candidate", help="Path to repaired JSON candidate.")
    ],
    allowed_path: Annotated[
        list[str] | None, typer.Option("--allowed-path", help="JSON pointer(s) allowed to differ.")
    ] = None,
) -> None:
    """Verify a repair candidate changes only allowed JSON pointers.

    Exit 0 if candidate differs from baseline only at the allowed paths.
    Exit 1 if the candidate has semantic violations.
    Exit 4 if the candidate changes fields outside the allowed paths.
    Exit 2 on I/O errors.
    """
    allowed: set[str] = set(allowed_path or [])

    # Load both
    for path, label in ((baseline, "baseline"), (candidate, "candidate")):
        try:
            path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError) as exc:
            _err.print(f"[red]error[/red] cannot read {label}: {exc}")
            raise typer.Exit(2) from None

    try:
        base_doc = json.loads(baseline.read_text(encoding="utf-8"))
        cand_doc = json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _err.print(f"[red]error[/red] invalid JSON: {exc}")
        raise typer.Exit(2) from None

    # Validate candidate
    issues = validate_review_result(cand_doc)
    if issues:
        errors = [_issue_to_error(i) for i in issues]
        repairable = list({e["path"] for e in errors})
        diagnostic = _typed_diagnostic("failed", "semantic_violation", errors, repairable)
        _emit_json(diagnostic, err=True)
        raise typer.Exit(1) from None

    # Check that only allowed pointers changed
    drifted = _find_top_level_drifts(base_doc, cand_doc) - {_strip_pointer(p) for p in allowed}
    if drifted:
        diagnostic = _typed_diagnostic(
            "failed",
            "repair_integrity_violation",
            [
                {
                    "code": "unauthorized_drift",
                    "path": f"/{k}",
                    "message": f"field '/{k}' changed but is not in allowed-path list",
                    "remediation": "Restrict repair to the listed allowed-path values.",
                }
                for k in sorted(drifted)
            ],
        )
        _emit_json(diagnostic, err=True)
        raise typer.Exit(4) from None

    _out.print(f"[green]verified[/green] repair {candidate}")


def _strip_pointer(pointer: str) -> str:
    """Normalize a JSON pointer to a bare top-level key (strip leading '/')."""
    return pointer.lstrip("/").split("/")[0]


def _find_top_level_drifts(base: dict, candidate: dict) -> set[str]:
    """Return top-level keys that differ between base and candidate."""
    all_keys = set(base) | set(candidate)
    return {k for k in all_keys if base.get(k) != candidate.get(k)}


# ── aggregate ─────────────────────────────────────────────────────────────────


@review_artifact_app.command(name="aggregate")
def aggregate_cmd(
    input: Annotated[
        list[Path], typer.Option("--input", "-i", help="Path(s) to accepted review JSON files.")
    ],
) -> None:
    """Summarize multiple accepted review JSONs.

    Prints a JSON summary with verdict distribution, score statistics, and
    blocking-issue totals. Exit 1 if any input fails validation.
    """
    results: list[dict] = []
    any_invalid = False

    for path in input:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as exc:
            _err.print(f"[red]error[/red] cannot read {path}: {exc}")
            any_invalid = True
            continue
        except json.JSONDecodeError as exc:
            _err.print(f"[red]error[/red] invalid JSON in {path}: {exc}")
            any_invalid = True
            continue

        issues = validate_review_result(doc)
        if issues:
            _err.print(f"[yellow]invalid[/yellow] {path}: {issues[0]}")
            any_invalid = True
            continue

        results.append(doc)

    if not results:
        _err.print("[red]error[/red] no valid inputs")
        raise typer.Exit(1) from None

    scores = [float(r["score"]) for r in results if r.get("score") is not None]
    verdicts: dict[str, int] = {}
    total_blocking = 0
    for r in results:
        v = r.get("verdict", "unknown")
        verdicts[v] = verdicts.get(v, 0) + 1
        total_blocking += r.get("blocking_issue_count", 0)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "review_count": len(results),
        "score_mean": round(sum(scores) / len(scores), 2) if scores else None,
        "score_min": min(scores) if scores else None,
        "score_max": max(scores) if scores else None,
        "verdict_distribution": verdicts,
        "total_blocking_issues": total_blocking,
        "rules": [r.get("rule_name") for r in results],
    }
    _emit_json(summary)

    if any_invalid:
        raise typer.Exit(1) from None
