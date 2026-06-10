"""Index generator command for ai-rules CLI.

Auto-generates RULES_INDEX.md from production-ready rule file metadata.
Renders templates/RULES_INDEX.md.template with a Markdown table (one row per
rule: filename | tier | ~tokens | ext | file | dir | kw) for self-contained
grep-based discovery. The {{rules_path}} placeholder in the template is
preserved at generate time and substituted at deploy time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root

# Regex patterns for metadata extraction
RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.IGNORECASE)
RE_TOKEN_BUDGET = re.compile(r"^\*\*TokenBudget:\*\*\s*(.*)$", re.IGNORECASE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.*)$", re.IGNORECASE)
RE_LOAD_TRIGGER = re.compile(r"^\*\*LoadTrigger:\*\*\s*(.*)$", re.IGNORECASE)

# Marker in the template where the generated flat table is injected
RULE_TABLE_MARKER = "<!-- RULE_TABLE -->"

# Default template path relative to project root
TEMPLATE_RELATIVE = Path("templates") / "RULES_INDEX.md.template"

# Files to skip during scanning
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
    "RULES_INDEX.md",
}


@dataclass
class RuleMetadata:
    """Extracted metadata from a production-ready rule file."""

    filename: str  # e.g., "000-global-core.md"
    filepath: Path  # Full path to rule file
    keywords: str  # Comma-separated typed keywords (v3.3: kw:/ext:/file:/dir:)
    depends: str  # Dependencies or "—" if None
    scope: str  # Extracted scope (kept for backward compat; not emitted in flat line)

    # Optional fields
    token_budget: str | None = None  # e.g. "~1800"
    context_tier: str | None = None  # e.g. "High"
    load_trigger: str | None = None  # legacy LoadTrigger (v3.2 fallback)


def extract_metadata(filepath: Path) -> RuleMetadata:
    """Extract metadata from a single rule file.

    Parses the first ~30 lines of the file for metadata fields.

    Args:
        filepath: Path to the rule file.

    Returns:
        RuleMetadata object with extracted information.

    Raises:
        ValueError: If the file cannot be read.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        raise ValueError(f"Failed to read {filepath}: {exc}") from exc

    lines = content.split("\n")

    metadata: dict[str, object] = {
        "filename": filepath.name,
        "filepath": filepath,
        "keywords": "",
        "depends": "—",
        "token_budget": None,
        "context_tier": None,
        "load_trigger": None,
        "scope": "",
    }

    for line in lines[:30]:
        stripped = line.strip()

        if match := RE_KEYWORDS.match(stripped):
            metadata["keywords"] = match.group(1).strip()

        elif match := RE_DEPENDS.match(stripped):
            depends_val = match.group(1).strip()
            if depends_val.lower() in {"none", "—", "", "n/a"}:
                metadata["depends"] = "—"
            else:
                deps = [d.strip() for d in depends_val.split(",")]
                deps = [d if d.endswith(".md") else f"{d}.md" for d in deps]
                metadata["depends"] = ", ".join(deps)

        elif match := RE_TOKEN_BUDGET.match(stripped):
            metadata["token_budget"] = match.group(1).strip()

        elif match := RE_CONTEXT_TIER.match(stripped):
            metadata["context_tier"] = match.group(1).strip()

        elif match := RE_LOAD_TRIGGER.match(stripped):
            metadata["load_trigger"] = match.group(1).strip()

    if not metadata["keywords"]:
        log_warning(f"{filepath.name} missing Keywords field, using empty string")

    return RuleMetadata(
        filename=str(metadata["filename"]),
        filepath=Path(str(metadata["filepath"])),
        keywords=str(metadata["keywords"] or ""),
        depends=str(metadata["depends"] or "—"),
        scope=str(metadata["scope"] or ""),
        token_budget=str(metadata["token_budget"]) if metadata["token_budget"] else None,
        context_tier=str(metadata["context_tier"]) if metadata["context_tier"] else None,
        load_trigger=str(metadata["load_trigger"]) if metadata["load_trigger"] else None,
    )


def scan_rules(rules_dir: Path) -> list[RuleMetadata]:
    """Scan rules/ directory and return sorted list of RuleMetadata.

    Args:
        rules_dir: Path to the rules directory.

    Returns:
        List of RuleMetadata objects, sorted by filename.
    """
    rules = []

    for filepath in sorted(rules_dir.rglob("*.md")):
        if filepath.name in SKIP_FILES:
            continue
        if "examples" in filepath.parts:
            continue

        try:
            metadata = extract_metadata(filepath)
            rules.append(metadata)
        except ValueError as exc:
            log_warning(str(exc))
            continue
        except Exception as exc:
            log_error(f"Error processing {filepath}: {exc}")
            continue

    rules.sort(key=lambda r: r.filename)
    return rules


def parse_load_triggers(
    rules: list[RuleMetadata],
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    """Parse typed Keywords entries (v3.3) into categorized mappings.

    v3.3 folds the legacy ``LoadTrigger:`` field into ``Keywords:`` using
    typed prefixes (``kw:``, ``ext:``, ``file:``, ``dir:``). This parser
    walks each rule's ``keywords`` value, splits on commas, and bins
    each typed entry by prefix.

    Args:
        rules: List of RuleMetadata objects (v3.3 typed Keywords).

    Returns:
        Tuple of (dir_triggers, ext_triggers, file_triggers, kw_triggers).
        Each dict maps trigger value (without prefix) to rule filename.
    """
    dir_triggers: dict[str, str] = {}
    ext_triggers: dict[str, str] = {}
    file_triggers: dict[str, str] = {}
    kw_triggers: dict[str, str] = {}

    for rule in rules:
        sources: list[str] = []
        if rule.keywords:
            sources.append(rule.keywords)
        if rule.load_trigger:
            sources.append(rule.load_trigger)

        seen: set[str] = set()
        for source in sources:
            for raw in source.split(","):
                trigger = raw.strip()
                if not trigger or trigger in seen:
                    continue
                seen.add(trigger)
                if trigger.startswith("dir:"):
                    dir_triggers[trigger[4:]] = rule.filename
                elif trigger.startswith("ext:"):
                    ext_triggers[trigger[4:]] = rule.filename
                elif trigger.startswith("file:"):
                    file_triggers[trigger[5:]] = rule.filename
                elif trigger.startswith("kw:"):
                    kw_triggers[trigger[3:]] = rule.filename

    return dir_triggers, ext_triggers, file_triggers, kw_triggers


def _split_typed_tokens(keywords_str: str) -> dict[str, list[str]]:
    """Split v3.3 typed Keywords tokens by prefix kind.

    Args:
        keywords_str: Raw ``**Keywords:**`` value.

    Returns:
        Dict with keys ``kw``, ``ext``, ``file``, ``dir`` mapping to
        lists of values (without the prefix).
    """
    result: dict[str, list[str]] = {"kw": [], "ext": [], "file": [], "dir": []}
    for entry in keywords_str.split(","):
        entry = entry.strip()
        if not entry:
            continue
        for prefix in ("kw:", "ext:", "file:", "dir:"):
            if entry.startswith(prefix):
                result[prefix[:-1]].append(entry[len(prefix) :])
                break
    return result


def generate_flat_line(rule: RuleMetadata) -> str:
    """Render one self-contained Markdown table row for a rule.

    Format: ``| filename | tier | ~tokens | ext | file | dir | kw |``

    Every cell is always present (empty typed groups render as ``-``), so a
    grep hit on any row is self-contained: the filename is the first column
    and tier/tokens follow. Typed prefixes (``tier:``, ``ext:``, ``file:``,
    ``dir:``, ``kw:``) are retained inside cells for grep matching.

    Args:
        rule: RuleMetadata for the rule to render.

    Returns:
        A single Markdown table row string without a trailing newline.
    """
    tokens = _split_typed_tokens(rule.keywords)

    ext = ", ".join(f"ext:{v}" for v in tokens["ext"]) if tokens["ext"] else "-"
    file_ = ", ".join(f"file:{v}" for v in tokens["file"]) if tokens["file"] else "-"
    dir_ = ", ".join(f"dir:{v}" for v in tokens["dir"]) if tokens["dir"] else "-"
    kw = ", ".join(f"kw:{v}" for v in tokens["kw"]) if tokens["kw"] else "-"

    tier = f"tier:{rule.context_tier}" if rule.context_tier else "tier:-"
    budget = rule.token_budget if rule.token_budget else "~-"

    cells = [rule.filename, tier, budget, ext, file_, dir_, kw]
    # Escape any literal pipes so they don't break the Markdown table
    cells = [c.replace("|", "\\|") for c in cells]
    return "| " + " | ".join(cells) + " |"


def render_rules_index(rules: list[RuleMetadata], template_path: Path) -> str:
    """Render RULES_INDEX.md by injecting the flat rule table into the template.

    Replaces the ``<!-- RULE_TABLE -->`` marker in the template with one
    flat line per rule (sorted by filename).

    Args:
        rules: Sorted list of RuleMetadata objects.
        template_path: Path to ``templates/RULES_INDEX.md.template``.

    Returns:
        Complete RULES_INDEX.md content as a string.

    Raises:
        ValueError: If the template does not exist or lacks the marker.
    """
    if not template_path.exists():
        raise ValueError(f"Template not found: {template_path}")

    template = template_path.read_text(encoding="utf-8")

    if RULE_TABLE_MARKER not in template:
        raise ValueError(
            f"Template {template_path} does not contain the '{RULE_TABLE_MARKER}' marker."
        )

    rows = "\n".join(generate_flat_line(r) for r in rules)
    return template.replace(RULE_TABLE_MARKER, rows)


def _normalize_for_check(text: str) -> str:
    """Normalize RULES_INDEX content for deterministic comparison.

    Args:
        text: Content to normalize.

    Returns:
        Normalized content with trailing whitespace stripped per line.
    """
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def _show_diff(current: str, generated: str) -> None:
    """Show a Rich diff between current and generated content.

    Args:
        current: Current file content.
        generated: Newly generated content.
    """
    import difflib

    current_lines = _normalize_for_check(current).splitlines(keepends=True)
    generated_lines = _normalize_for_check(generated).splitlines(keepends=True)

    diff = list(
        difflib.unified_diff(
            current_lines,
            generated_lines,
            fromfile="current RULES_INDEX.md",
            tofile="generated RULES_INDEX.md",
            lineterm="",
        )
    )

    if not diff:
        return

    diff_text = Text()
    for line in diff[:100]:
        line = line.rstrip("\n")
        if line.startswith("+++") or line.startswith("---"):
            diff_text.append(line + "\n", style="bold")
        elif line.startswith("@@"):
            diff_text.append(line + "\n", style="cyan")
        elif line.startswith("+"):
            diff_text.append(line + "\n", style="green")
        elif line.startswith("-"):
            diff_text.append(line + "\n", style="red")

    if len(diff) > 100:
        diff_text.append(f"\n... ({len(diff) - 100} more lines)\n", style="dim")

    console.print(Panel(diff_text, title="[bold]Diff[/bold]", border_style="yellow"))


index_app = typer.Typer(
    name="index",
    help="Generate and check RULES_INDEX.md from rule metadata.",
    no_args_is_help=True,
)


def _resolve_template(project_root: Path) -> Path:
    """Return the RULES_INDEX template path, with a helpful error if missing."""
    template_path = project_root / TEMPLATE_RELATIVE
    if not template_path.exists():
        log_error(f"RULES_INDEX template not found: {template_path}")
        log_error(f"Expected: {TEMPLATE_RELATIVE}")
        raise typer.Exit(code=1) from None
    return template_path


def _scan_and_generate(
    rules_dir: Path | None,
) -> tuple[list[RuleMetadata], str, Path]:
    """Resolve rules dir, scan, load template, and render content.

    Args:
        rules_dir: Optional explicit rules directory path.

    Returns:
        Tuple of (rules list, rendered content, resolved rules_dir).

    Raises:
        typer.Exit: On any failure.
    """
    if rules_dir is None:
        try:
            project_root = find_project_root()
            rules_dir = project_root / "rules"
        except FileNotFoundError:
            if Path("rules").exists():
                rules_dir = Path("rules")
                project_root = Path.cwd()
            else:
                log_error("rules/ directory not found in current directory")
                raise typer.Exit(code=1) from None
    else:
        # Derive project_root from rules_dir (assume rules/ is directly under root)
        project_root = rules_dir.parent

    if not rules_dir.exists():
        log_error(f"Rules directory not found: {rules_dir}")
        raise typer.Exit(code=1) from None

    log_info(f"Using {rules_dir}/ directory")

    log_info(f"Scanning {rules_dir}...")
    try:
        rules = scan_rules(rules_dir)
    except Exception as exc:
        log_error(f"Error scanning rules: {exc}")
        raise typer.Exit(code=1) from None

    if not rules:
        log_error(f"No rule files found in {rules_dir}")
        raise typer.Exit(code=1) from None

    log_success(f"Found {len(rules)} rule files")

    template_path = _resolve_template(project_root)

    try:
        content = render_rules_index(rules, template_path)
    except Exception as exc:
        log_error(f"Error rendering RULES_INDEX.md: {exc}")
        raise typer.Exit(code=1) from None

    return rules, content, rules_dir


@index_app.command(name="generate")
def generate(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Print generated content without writing to file.",
        ),
    ] = False,
    rules_dir: Annotated[
        Path | None,
        typer.Option(
            "--rules-dir",
            help="Path to rules directory (default: rules/).",
        ),
    ] = None,
) -> None:
    """Generate RULES_INDEX.md from rule metadata using the template.

    Renders ``templates/RULES_INDEX.md.template`` with a flat one-line-per-rule
    table (format: filename | tier | ~tokens | ext | file | dir | kw) for
    self-contained grep-based discovery.

    Examples:
        # Generate RULES_INDEX.md
        ai-rules index generate

        # Preview output without writing
        ai-rules index generate --dry-run

        # Use custom rules directory
        ai-rules index generate --rules-dir custom/rules
    """
    rules, content, rules_dir = _scan_and_generate(rules_dir)

    if dry_run:
        console.print()
        console.rule("[bold]Generated RULES_INDEX.md content[/bold]")
        console.print()
        lines = content.split("\n")
        preview = "\n".join(lines[:100])
        console.print(Syntax(preview, "markdown", theme="monokai", line_numbers=True))
        if len(lines) > 100:
            console.print(f"\n[dim]... ({len(lines) - 100} more lines)[/dim]")
        return

    output_path = rules_dir / "RULES_INDEX.md"
    try:
        output_path.write_text(content, encoding="utf-8")
        log_success(f"Generated {output_path}")
        log_info(f"{len(rules)} rules indexed")
    except Exception as exc:
        log_error(f"Error writing {output_path}: {exc}")
        raise typer.Exit(code=1) from None


@index_app.command(name="check")
def check(
    rules_dir: Annotated[
        Path | None,
        typer.Option(
            "--rules-dir",
            help="Path to rules directory (default: rules/).",
        ),
    ] = None,
) -> None:
    """Check if RULES_INDEX.md is up-to-date (exit 1 if not, for CI).

    Examples:
        # Check if up-to-date
        ai-rules index check

        # Check with custom rules directory
        ai-rules index check --rules-dir custom/rules
    """
    _rules, content, rules_dir = _scan_and_generate(rules_dir)

    output_path = rules_dir / "RULES_INDEX.md"

    if not output_path.exists():
        log_error(f"{output_path} does not exist")
        console.print("\n[yellow]Run:[/yellow] ai-rules index generate")
        raise typer.Exit(code=1) from None

    try:
        current_content = output_path.read_text(encoding="utf-8")
    except Exception as exc:
        log_error(f"Error reading {output_path}: {exc}")
        raise typer.Exit(code=1) from None

    if _normalize_for_check(current_content) == _normalize_for_check(content):
        log_success("RULES_INDEX.md is up-to-date")
        return
    else:
        log_error("RULES_INDEX.md is out of date")
        console.print()
        _show_diff(current_content, content)
        console.print()
        console.print("[yellow]Run to update:[/yellow]")
        console.print("  ai-rules index generate")
        raise typer.Exit(code=1) from None
