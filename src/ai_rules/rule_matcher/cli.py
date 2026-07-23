r"""CLI entry point for the deterministic rule matcher.

Usage::

    python -m ai_rules.rule_matcher \\
        --keywords "streamlit,deploy" \\
        --extensions ".py" \\
        --paths "src/app.py" \\
        --rules-dir ./rules \\
        --format manifest-v2

Exit codes:
    0  — success, at least one rule matched.
    1  — no rules matched (still emits valid JSON with ``load_sequence: []``).
    2  — fatal error (missing rules-dir, JSON serialisation failure).
         NOT returned for individual malformed rule files.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import typer

from ai_rules.rule_matcher.dependency import resolve_dependencies
from ai_rules.rule_matcher.frontmatter import load_rules_db
from ai_rules.rule_matcher.manifest import build_manifest
from ai_rules.rule_matcher.matcher import FileContext, match_rules

app = typer.Typer(add_completion=False)
logger = logging.getLogger(__name__)


@app.command()
def main(
    keywords: str = typer.Option("", help="Comma-separated user keywords"),
    extensions: str = typer.Option("", help="Comma-separated file extensions (e.g. .py,.sql)"),
    paths: str = typer.Option("", help="Comma-separated file paths for glob matching"),
    rules_dir: Path = typer.Option(Path("rules"), help="Path to rules directory"),
    format: str = typer.Option("manifest-v2", help="Output format (only manifest-v2 supported)"),
    max_entries: int = typer.Option(3, help="Max direct-match entries in load_sequence"),
    max_tokens: int = typer.Option(20_000, help="Token budget ceiling"),
) -> None:
    """Run the deterministic rule matcher and emit JSON to stdout."""
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    ext_list = [e.strip() for e in extensions.split(",") if e.strip()]
    path_list = [p.strip() for p in paths.split(",") if p.strip()]

    try:
        rules_db = load_rules_db(rules_dir)
    except FileNotFoundError as exc:
        _fatal(f"rules-dir not found: {exc}")

    file_ctx = FileContext(extensions=ext_list, paths=path_list)
    scored = match_rules(kw_list, file_ctx, list(rules_db.values()))
    matched_filenames = {sr.rule.filename for sr in scored}

    resolved, warnings = resolve_dependencies(scored, rules_db)
    manifest = build_manifest(
        resolved,
        warnings,
        matched_filenames=matched_filenames,
        max_entries=max_entries,
        max_tokens=max_tokens,
    )

    try:
        output = json.dumps(manifest.to_dict(), indent=2)
    except (TypeError, ValueError) as exc:
        _fatal(f"JSON serialisation failed: {exc}")

    print(output)
    raise typer.Exit(code=0 if manifest.load_sequence else 1)


def _fatal(message: str) -> None:
    """Print error JSON to stderr and exit with code 2."""
    payload = json.dumps({"error": message, "load_sequence": []})
    print(payload, file=sys.stderr)
    raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
