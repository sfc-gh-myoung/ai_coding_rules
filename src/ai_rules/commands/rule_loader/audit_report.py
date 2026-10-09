"""Diagnostic triage report over corpus-audit unresolved misses.

Reads the audit artifact and disposition sidecar (both read-only), classifies
each unresolved miss into an evidence-grounded category using the externalized
taxonomy, and renders a JSON + markdown report pair atomically.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Annotated, Any, cast

import typer

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover — Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from ai_rules._shared.console import log_error, log_success
from ai_rules.commands.rule_loader.audit import (
    DEFAULT_DISPOSITIONS,
    DEFAULT_OUTPUT,
    evaluate,
)
from ai_rules.commands.rule_loader.rank_snapshot import canonical_json

# --- Taxonomy loading ---

_TAXONOMY_PATH = Path(__file__).parent / "taxonomy.toml"

# Punctuation chars that signal "punctuated" trigger shape.
_PUNCT_CHARS = re.compile(r"[@./%$]|(?<!\s)-(?!\s)")


class UsableInputError(Exception):
    """Raised when input files are fatally invalid."""


class AtomicWriteError(Exception):
    """Raised when atomic rename of output files fails."""


def load_taxonomy(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and validate the category taxonomy from TOML.

    Returns a list of category dicts sorted by precedence.
    """
    toml_path = path or _TAXONOMY_PATH
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    categories = data.get("categories")
    if not isinstance(categories, dict) or not categories:
        msg = "taxonomy.toml: missing or empty [categories] section"
        raise UsableInputError(msg)

    entries: list[dict[str, Any]] = []
    for name, spec in categories.items():
        if "precedence" not in spec:
            msg = f"taxonomy.toml: category {name!r} missing 'precedence' key"
            raise UsableInputError(msg)
        entries.append({"name": name, **spec})

    entries.sort(key=lambda e: e["precedence"])
    return entries


# --- Trigger shape derivation ---


def derive_trigger_shape(trigger_value: str) -> str:
    """Derive trigger_shape from trigger_value.

    Returns "punctuated", "single-token", or "multi-token".
    """
    if _PUNCT_CHARS.search(trigger_value):
        return "punctuated"
    tokens = trigger_value.strip().split()
    if len(tokens) <= 1:
        return "single-token"
    return "multi-token"


# --- Input validation ---


_REQUIRED_ARTIFACT_KEYS = {"artifact", "records"}
_REQUIRED_IDENTITY_KEYS = {
    "rules_digest",
    "matcher_digest",
    "schema_version",
    "generator_version",
}
_REQUIRED_RECORD_KEYS = {
    "rule_id",
    "trigger_kind",
    "trigger_value",
    "probe",
    "prompt_source",
    "in_manifest",
    "score",
    "rank",
}


def validate_artifact(data: Any) -> None:
    """Validate artifact schema. Raises UsableInputError on failure."""
    if not isinstance(data, dict):
        raise UsableInputError("artifact: top-level must be an object")

    for key in _REQUIRED_ARTIFACT_KEYS:
        if key not in data:
            raise UsableInputError(f"artifact: missing required key {key!r}")

    identity = data["artifact"]
    if not isinstance(identity, dict):
        raise UsableInputError("artifact: 'artifact' block must be an object")
    for key in _REQUIRED_IDENTITY_KEYS:
        if key not in identity:
            raise UsableInputError(f"artifact: identity block missing required key {key!r}")

    records = data["records"]
    if not isinstance(records, list):
        raise UsableInputError("artifact: 'records' must be a list")

    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise UsableInputError(f"artifact: record[{i}] must be an object")
        r = cast("dict[str, Any]", rec)
        for key in _REQUIRED_RECORD_KEYS:
            if key not in r:
                raise UsableInputError(f"artifact: record[{i}] missing required key {key!r}")
        # Type checks
        if not isinstance(r["in_manifest"], bool):
            raise UsableInputError(
                f"artifact: record[{i}].in_manifest must be bool, got {type(r['in_manifest']).__name__}"
            )
        if r["score"] is not None and not isinstance(r["score"], (int, float)):
            raise UsableInputError(
                f"artifact: record[{i}].score must be int/float/null, got {type(r['score']).__name__}"
            )
        if r["rank"] is not None and not isinstance(r["rank"], int):
            raise UsableInputError(
                f"artifact: record[{i}].rank must be int/null, got {type(r['rank']).__name__}"
            )
        for str_key in ("rule_id", "trigger_kind", "trigger_value", "probe", "prompt_source"):
            if not isinstance(r[str_key], str):
                raise UsableInputError(
                    f"artifact: record[{i}].{str_key} must be str, got {type(r[str_key]).__name__}"
                )


def validate_sidecar_toplevel(data: Any) -> None:
    """Validate sidecar top-level structure. Raises UsableInputError only for non-object."""
    if not isinstance(data, dict):
        raise UsableInputError(f"sidecar: top-level must be an object, got {type(data).__name__}")


# --- Classifier ---


def classify(record: dict[str, Any], taxonomy: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    """Assign exactly one category to an unresolved miss via taxonomy precedence.

    Returns (category_name, evidence_object).
    """
    shape = derive_trigger_shape(record["trigger_value"])
    score = record["score"]
    rank = record["rank"]

    for entry in taxonomy:
        ts = entry["trigger_shape"]
        shape_match = ts == "any" or ts == shape
        if entry["predicate"] == "score != null AND rank != null":
            if score is not None and rank is not None and shape_match:
                return entry["name"], _evidence(score, rank, shape)
        elif (
            entry["predicate"] == "score == null AND rank == null"
            and score is None
            and rank is None
            and shape_match
        ):
            return entry["name"], _evidence(score, rank, shape)

    # Fallback — should not happen with a complete taxonomy
    return "no-score-unexplained", _evidence(score, rank, shape)


def _evidence(score: Any, rank: Any, shape: str) -> dict[str, Any]:
    return {
        "score": score,
        "rank": rank,
        "trigger_shape": shape,
        "inferred_cause": False,
    }


# --- Report assembly ---


def build_report(
    artifact_data: dict[str, Any],
    dispositions: dict[str, dict[str, Any]],
    taxonomy: list[dict[str, Any]],
    audit_path: Path,
    dispositions_path: Path,
) -> dict[str, Any]:
    """Build the canonical report envelope."""
    identity = artifact_data["artifact"]
    records = artifact_data["records"]

    misses, integrity_errors = evaluate(records, identity, dispositions)

    rows: list[dict[str, Any]] = []
    for rec in misses:
        category, evidence = classify(rec, taxonomy)
        action = next(
            (e["recommended_action"] for e in taxonomy if e["name"] == category),
            "manual review — unexplained",
        )
        rows.append(
            {
                "rule": rec["rule_id"],
                "trigger_kind": rec["trigger_kind"],
                "trigger_value": rec["trigger_value"],
                "probe": rec["probe"],
                "source": rec["prompt_source"],
                "score": rec["score"],
                "rank": rec["rank"],
                "category": category,
                "evidence": evidence,
                "recommended_action": action,
            }
        )

    rows.sort(key=lambda r: (r["category"], r["rule"], r["trigger_kind"], r["trigger_value"]))

    category_counts: dict[str, int] = {}
    for row in rows:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1

    return {
        "artifact": identity,
        "summary": {
            "unresolved_count": len(rows),
            "category_counts": category_counts,
            "generated_from": {
                "audit": str(audit_path),
                "dispositions": str(dispositions_path),
            },
        },
        "integrity_errors": integrity_errors,
        "rows": rows,
    }


# --- Markdown rendering ---


def _escape_cell(value: str) -> str:
    """Escape pipe chars and normalize newlines for markdown table cells."""
    return value.replace("|", "\\|").replace("\n", " ")


def _truncate(value: str, max_width: int = 60) -> str:
    if len(value) <= max_width:
        return value
    return value[: max_width - 3] + "..."


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report as a markdown table."""
    lines: list[str] = []
    lines.append("# Audit Triage Report")
    lines.append("")
    lines.append(f"Unresolved misses: {report['summary']['unresolved_count']}")
    lines.append("")

    counts = report["summary"]["category_counts"]
    if counts:
        lines.append("## Category Summary")
        lines.append("")
        for cat, n in sorted(counts.items()):
            lines.append(f"- **{cat}**: {n}")
        lines.append("")

    if report["integrity_errors"]:
        lines.append("## Integrity Errors")
        lines.append("")
        for err in report["integrity_errors"]:
            lines.append(f"- {_escape_cell(err)}")
        lines.append("")

    lines.append("## Triage Table")
    lines.append("")
    header = "| rule | trigger_kind | trigger_value | probe | source | score | rank | category | recommended_action |"
    sep = "|------|--------------|---------------|-------|--------|-------|------|----------|-------------------|"
    lines.append(header)
    lines.append(sep)

    for row in report["rows"]:
        cells = [
            _escape_cell(row["rule"]),
            _escape_cell(row["trigger_kind"]),
            _escape_cell(row["trigger_value"]),
            _escape_cell(_truncate(row["probe"])),
            _escape_cell(row["source"]),
            str(row["score"]) if row["score"] is not None else "null",
            str(row["rank"]) if row["rank"] is not None else "null",
            _escape_cell(row["category"]),
            _escape_cell(row["recommended_action"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    return "\n".join(lines)


# --- Atomic write ---


def atomic_write_pair(json_path: Path, md_path: Path, json_content: str, md_content: str) -> None:
    """Write both files atomically via temp + rename.

    On any failure, cleans up temp files. Raises AtomicWriteError on rename failure.
    """
    json_tmp = json_path.with_suffix(json_path.suffix + ".tmp")
    md_tmp = md_path.with_suffix(md_path.suffix + ".tmp")

    try:
        json_tmp.write_text(json_content, encoding="utf-8")
        md_tmp.write_text(md_content, encoding="utf-8")
    except OSError as e:
        # Clean up any partial temp files
        json_tmp.unlink(missing_ok=True)
        md_tmp.unlink(missing_ok=True)
        raise AtomicWriteError(f"failed to write temp files: {e}") from e

    try:
        os.replace(str(json_tmp), str(json_path))
    except OSError as e:
        json_tmp.unlink(missing_ok=True)
        md_tmp.unlink(missing_ok=True)
        raise AtomicWriteError(f"failed to rename {json_tmp} -> {json_path}: {e}") from e

    try:
        os.replace(str(md_tmp), str(md_path))
    except OSError as e:
        # JSON already committed — roll it back
        json_path.unlink(missing_ok=True)
        md_tmp.unlink(missing_ok=True)
        raise AtomicWriteError(
            f"failed to rename {md_tmp} -> {md_path} (JSON rolled back): {e}"
        ) from e


# --- CLI command ---


def audit_report_cmd(
    audit: Annotated[
        Path, typer.Option("--audit", help="Corpus-audit JSON artifact path.")
    ] = DEFAULT_OUTPUT,
    dispositions_path: Annotated[
        Path,
        typer.Option("--dispositions", help="Disposition sidecar JSON path."),
    ] = DEFAULT_DISPOSITIONS,
    output: Annotated[
        Path,
        typer.Option("--output", help="Output JSON path (.md sibling created automatically)."),
    ] = Path("reports/rule-loader-corpus-audit-report.json"),
) -> None:
    """Generate a diagnostic triage report over unresolved corpus-audit misses."""
    # Load and validate artifact
    if not audit.is_file():
        log_error(f"audit artifact not found: {audit}")
        raise typer.Exit(code=1) from None

    try:
        artifact_data = json.loads(audit.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log_error(f"cannot read audit artifact: {e}")
        raise typer.Exit(code=1) from None

    try:
        validate_artifact(artifact_data)
    except UsableInputError as e:
        log_error(str(e))
        raise typer.Exit(code=1) from None

    # Load and validate sidecar
    if dispositions_path.is_file():
        try:
            sidecar_data = json.loads(dispositions_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log_error(f"cannot read sidecar: {e}")
            raise typer.Exit(code=1) from None
        try:
            validate_sidecar_toplevel(sidecar_data)
        except UsableInputError as e:
            log_error(str(e))
            raise typer.Exit(code=1) from None
    else:
        sidecar_data = {}

    # Load taxonomy
    try:
        taxonomy = load_taxonomy()
    except (UsableInputError, OSError) as e:
        log_error(f"taxonomy load failed: {e}")
        raise typer.Exit(code=1) from None

    # Build report
    report = build_report(artifact_data, sidecar_data, taxonomy, audit, dispositions_path)

    # Render
    json_content = canonical_json(report)
    md_content = render_markdown(report)

    # Atomic write
    json_path = output
    md_path = output.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        atomic_write_pair(json_path, md_path, json_content, md_content)
    except AtomicWriteError as e:
        log_error(str(e))
        raise typer.Exit(code=2) from None

    log_success(
        f"report written: {json_path} + {md_path} "
        f"({report['summary']['unresolved_count']} unresolved misses, "
        f"{len(report['integrity_errors'])} integrity errors)"
    )
