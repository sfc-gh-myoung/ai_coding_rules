"""Interactive configuration wizard for ai-coding-rules.

Generates `.ai-coding-rules.yaml` in the project root based on user preferences.
Register as: ai-rules configure
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Interactive configuration for ai-coding-rules.")


_LANGUAGE_PREFIXES = {
    "python": ["000", "002", "003", "200", "201", "206"],
    "sql": ["000", "002", "100"],
    "javascript": ["000", "002", "420"],
    "typescript": ["000", "002", "430"],
    "bash": ["000", "002", "300"],
    "golang": ["000", "002", "600"],
}

_FRAMEWORK_PREFIXES = {
    "fastapi": ["200"],
    "streamlit": ["200"],
    "htmx": ["420"],
    "react": ["420", "430"],
}

_PLATFORM_PREFIXES = {
    "snowflake": ["100", "101"],
    "aws": ["000"],
    "gcp": ["000"],
    "azure": ["000"],
}


@app.command()
def configure(
    output: Path = typer.Option(  # noqa: B008
        Path(".ai-coding-rules.yaml"),
        help="Path to write the config file",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print config without writing"),
) -> None:
    """Generate .ai-coding-rules.yaml by answering a few questions."""
    typer.echo("ai-coding-rules configuration wizard")
    typer.echo("=" * 40)

    languages_raw = typer.prompt(
        "Languages (comma-separated: python, sql, javascript, typescript, bash, golang)",
        default="python",
    )
    frameworks_raw = typer.prompt(
        "Frameworks (comma-separated: fastapi, streamlit, htmx, react) [optional]",
        default="",
    )
    platforms_raw = typer.prompt(
        "Cloud platforms (comma-separated: snowflake, aws, gcp, azure) [optional]",
        default="",
    )

    languages = [x.strip().lower() for x in languages_raw.split(",") if x.strip()]
    frameworks = [x.strip().lower() for x in frameworks_raw.split(",") if x.strip()]
    platforms = [x.strip().lower() for x in platforms_raw.split(",") if x.strip()]

    # Collect include_prefixes from selections
    prefixes: set[str] = {"000", "002", "003"}
    for lang in languages:
        prefixes.update(_LANGUAGE_PREFIXES.get(lang, []))
    for fw in frameworks:
        prefixes.update(_FRAMEWORK_PREFIXES.get(fw, []))
    for pl in platforms:
        prefixes.update(_PLATFORM_PREFIXES.get(pl, []))

    config = {
        "version": 1,
        "domains": {
            "languages": languages,
            "frameworks": frameworks,
            "platforms": platforms,
        },
        "rules_filter": {
            "include_prefixes": sorted(prefixes),
            "exclude_prefixes": [],
        },
    }

    yaml_text = yaml.dump(config, default_flow_style=False, sort_keys=False)

    if dry_run:
        typer.echo("\n--- .ai-coding-rules.yaml (dry-run) ---")
        typer.echo(yaml_text)
        return

    output.write_text(yaml_text, encoding="utf-8")
    typer.echo(f"\n✓ Written: {output}")
    typer.echo("Run `ai-rules configure --dry-run` to preview changes.")
