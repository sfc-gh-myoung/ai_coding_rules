"""Index generator command for ai-rules CLI.

Auto-generates RULES_INDEX.md from production-ready rule file metadata.
Renders templates/RULES_INDEX.md.template with the F4 flat-line format —
one line per rule (filename tier=<T> [ext=..] [file=..] [dir=..] kw=<w1> ...) —
for self-contained grep-based discovery by agents. The {{rules_path}}
placeholder in the template is preserved at generate time and substituted at
deploy time.

Metadata extraction is dual-parse (schema v3.5):
- YAML frontmatter (`---` fence at top-of-file) is the canonical form; parsed
  via `yaml.safe_load` and takes precedence when present.
- Inline `**Field:**` markers remain supported as a fallback for pre-v3.5
  rule files during the migration rollout.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root

# Marker in the template where the generated index rows are injected
RULE_TABLE_MARKER = "<!-- RULE_TABLE -->"

# Default template path relative to project root
TEMPLATE_RELATIVE = Path("templates") / "RULES_INDEX.md.template"

# .index-stats.json — B5 sanity-threshold facts + counts consumed by rule-loader
# skill workflows. Schema documented in the "Rule-Loading Improvements
# Implementation Plan (Track B + Track C)" §5.3.
STATS_FILENAME = ".index-stats.json"
# schema_version bumped from "2" to "3" when collapsing dual-index to single
# compact RULES_INDEX.md (COMPACT format F4 is now the only generated index).
STATS_SCHEMA_VERSION = "3"
INDEX_FORMAT_VERSION = "F4"

# Volatile fields that must be ignored when comparing an on-disk stats file
# against a freshly regenerated one (they legitimately change every run).
STATS_VOLATILE_KEYS = ("generated_at", "git_sha")
# Sanity thresholds published for consumption by the rule-loader skill's
# activity-matching workflow. Values are constants at this schema version.
_SANITY_THRESHOLDS: dict[str, Any] = {
    "min_matches_common_keyword": 1,
    "max_matches_broad_query": 50,
    "zero_result_is_anomaly": True,
    # Corpus-wide floor for total ``kw:`` tokens across the index. Fails
    # ``ai-rules index check`` when a regeneration produces fewer entries than
    # this value; guards against mass keyword deletion during schema-migration
    # or bulk rule-edit runs (§5.4 failure mode mitigation).
    "keyword_entries_min": 1200,
}

# Files to skip during scanning
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
    "RULES_INDEX.md",
    "002i-rule-loadtrigger.md",  # DEPRECATED TOMBSTONE — retained for inbound-link stability, excluded from discovery index
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


FRONTMATTER_FENCE_RE = re.compile(r"^---\s*$")


def _parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Parse a leading YAML frontmatter block if present.

    Returns the parsed mapping when the file begins with a `---` fence and a
    closing `---` fence is found; otherwise returns None.
    """
    lines = content.split("\n")
    if not lines or not FRONTMATTER_FENCE_RE.match(lines[0]):
        return None
    for idx in range(1, min(len(lines), 200)):
        if FRONTMATTER_FENCE_RE.match(lines[idx]):
            block = "\n".join(lines[1:idx])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError:
                return None
            return data if isinstance(data, dict) else None
    return None


def _normalize_depends_yaml(value: Any) -> str:
    """Normalize a YAML `depends:` structure into the F4 flat comma-separated form.

    Accepts either a mapping `{required: [...], optional: [...]}` or a flat
    list of typed strings (`required:foo.md`, `optional:bar.md`). Returns "—"
    for empty/None input.
    """
    if not value:
        return "—"
    entries: list[str] = []
    if isinstance(value, dict):
        for key in ("required", "optional"):
            items = value.get(key) or []
            for item in items:
                if not item:
                    continue
                name = str(item).strip()
                if not name.endswith(".md"):
                    name = f"{name}.md"
                entries.append(f"{key}:{name}")
    elif isinstance(value, list):
        for item in value:
            if not item:
                continue
            name = str(item).strip()
            if ":" not in name:
                name = f"required:{name}"
            prefix, rest = name.split(":", 1)
            if not rest.endswith(".md"):
                rest = f"{rest}.md"
            entries.append(f"{prefix}:{rest}")
    if not entries:
        return "—"
    return ", ".join(entries)


def _normalize_keywords_yaml(value: Any) -> str:
    """Normalize a YAML `keywords:` list into the inline comma-separated form."""
    if not value:
        return ""
    if isinstance(value, list):
        return ", ".join(str(k).strip() for k in value if str(k).strip())
    return str(value).strip()


def extract_metadata(filepath: Path) -> RuleMetadata:
    """Extract metadata from a single rule file (YAML frontmatter, schema v3.5).

    All production rule files begin with a ``---`` fenced YAML frontmatter
    block; keys are ``keywords``, ``depends``, ``token_budget``,
    ``context_tier``, and (legacy) ``load_trigger``. Files without frontmatter
    are treated as unmigrated / tombstone entries: metadata defaults are
    returned and a warning is logged. There is no inline ``**Field:**``
    fallback path; the pre-v3.5 dual-parse window closed in Phase 4 cutover.

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

    frontmatter = _parse_frontmatter(content)
    if frontmatter is not None:
        # Canonical YAML path (schema v3.5). Keys are lowercase_snake.
        if (kw := frontmatter.get("keywords")) is not None:
            metadata["keywords"] = _normalize_keywords_yaml(kw)
        if (dep := frontmatter.get("depends")) is not None:
            metadata["depends"] = _normalize_depends_yaml(dep)
        if (tb := frontmatter.get("token_budget")) is not None:
            metadata["token_budget"] = str(tb).strip()
        if (ct := frontmatter.get("context_tier")) is not None:
            metadata["context_tier"] = str(ct).strip()
        if (lt := frontmatter.get("load_trigger")) is not None:
            metadata["load_trigger"] = str(lt).strip()

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


def render_rules_index(
    rules: list[RuleMetadata],
    template_path: Path,
    desc_map: dict[str, str] | None = None,
) -> str:
    """Render RULES_INDEX.md by injecting compact index rows into the template.

    Replaces the ``<!-- RULE_TABLE -->`` marker in the template with one
    :func:`render_index_line` row per rule (sorted by filename).

    Args:
        rules: Sorted list of RuleMetadata objects.
        template_path: Path to ``templates/RULES_INDEX.md.template``.
        desc_map: Optional mapping of ``{filename: desc_text}`` to preserve
            existing ``desc="..."`` fields across regeneration.

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

    _desc = desc_map or {}
    rows = "\n".join(render_index_line(r, _desc.get(r.filename, "")) for r in rules)
    return template.replace(RULE_TABLE_MARKER, rows)


def _hyphenate_keyword(kw: str) -> str:
    """Convert a keyword's internal whitespace to hyphens for F4 emission.

    F4's ``kw=`` block is space-separated (see plan §3.2); any keyword
    containing an internal space would break word-boundary grep. The
    canonical form hyphenates internal whitespace runs so ``"surgical
    edits"`` renders as ``surgical-edits``. Already-hyphenated keywords
    pass through unchanged. Empty strings return empty.

    Args:
        kw: Raw keyword value (from ``**Keywords:**`` after ``kw:`` strip).

    Returns:
        The keyword with any internal whitespace collapsed to single hyphens.
    """
    stripped = kw.strip()
    if not stripped:
        return ""
    # Collapse any run of whitespace to a single hyphen.
    return re.sub(r"\s+", "-", stripped)


def render_index_line(rule: RuleMetadata, desc: str = "") -> str:
    """Render one F4-format row of the index.

    Format (F4):

        ``<filename> tier=<T> [ext=<e1>,<e2>] [file=<f1>] [dir=<d1>] kw=<w1> <w2> ... [desc="<sentence>"]``

    Fields are space-delimited. ``filename``, ``tier=``, and ``kw=`` are
    always present; ``ext=``, ``file=``, and ``dir=`` are emitted only when
    the rule has typed triggers of that kind (omitted otherwise to save
    tokens). ``tier=-`` renders when ``ContextTier`` is missing. Keywords
    inside the ``kw=`` block are space-separated with any internal
    whitespace hyphenated (``surgical edits`` → ``surgical-edits``). Rules
    with no keywords render ``kw=-``. This grammar is optimised for
    ``grep -iwE <word>`` recall and BPE-tokenises efficiently.

    Args:
        rule: RuleMetadata for the rule to render.
        desc: Optional description string (sourced from existing ``desc=`` field).

    Returns:
        A single-line string without a trailing newline.
    """
    tokens = _split_typed_tokens(rule.keywords)

    tier_value = rule.context_tier if rule.context_tier else "-"
    parts: list[str] = [rule.filename, f"tier={tier_value}"]

    if tokens["ext"]:
        parts.append(f"ext={','.join(tokens['ext'])}")
    if tokens["file"]:
        parts.append(f"file={','.join(tokens['file'])}")
    if tokens["dir"]:
        parts.append(f"dir={','.join(tokens['dir'])}")

    if tokens["kw"]:
        hyphenated = [_hyphenate_keyword(k) for k in tokens["kw"]]
        hyphenated = [h for h in hyphenated if h]
        parts.append("kw=" + " ".join(hyphenated) if hyphenated else "kw=-")
    else:
        parts.append("kw=-")

    if desc:
        parts.append(f'desc="{desc}"')

    return " ".join(parts)


def _extract_desc_map(index_path: Path) -> dict[str, str]:
    """Read existing ``desc="..."`` fields from an index file.

    Parses each line of the form::

        <filename> tier=... kw=... desc="<sentence>"

    Args:
        index_path: Path to an existing RULES_INDEX.md (may not exist).

    Returns:
        Mapping of ``{filename: description_text}``.
    """
    desc_map: dict[str, str] = {}
    if not index_path.exists():
        return desc_map
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        return desc_map  # Unreadable; proceed without desc= fields
    desc_re = re.compile(r'^(\S+\.md)\s+.*?\bdesc="([^"]+)"')
    for line in text.splitlines():
        m = desc_re.match(line)
        if m:
            desc_map[m.group(1)] = m.group(2)
    return desc_map


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


def _resolve_git_sha(project_root: Path) -> str:
    """Return the current git HEAD SHA for ``project_root`` or ``"unknown"``.

    Best-effort: any failure (missing git binary, not a repo, timeout) yields
    ``"unknown"``. The value is a volatile stats field (see
    ``STATS_VOLATILE_KEYS``) so it never contributes to ``check`` equality.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _count_keyword_entries(rules: list[RuleMetadata]) -> int:
    """Total number of ``kw:`` typed tokens across all rules."""
    return sum(len(_split_typed_tokens(r.keywords)["kw"]) for r in rules)


def _tier_counts(rules: list[RuleMetadata]) -> dict[str, int]:
    """Return lowercased-tier -> count mapping across the four canonical tiers.

    Rules with no ``ContextTier`` metadata contribute to none of the four
    buckets; unrecognised tier names are still counted so schema drift is
    visible rather than silently dropped.
    """
    counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for rule in rules:
        if not rule.context_tier:
            continue
        tier = rule.context_tier.strip().lower()
        counts[tier] = counts.get(tier, 0) + 1
    return counts


def render_index_stats(
    rules: list[RuleMetadata],
    rendered_index: str,
    project_root: Path,
) -> dict[str, Any]:
    """Render the ``.index-stats.json`` body.

    Args:
        rules: Sorted list of RuleMetadata objects (as returned by
            :func:`scan_rules`).
        rendered_index: Full rendered ``RULES_INDEX.md`` content; used to
            count total index lines.
        project_root: Project root path; used to look up the current git SHA
            for the ``git_sha`` field.

    Returns:
        A JSON-serialisable dict with schema_version, format_version,
        generated_at, git_sha, counts, tiers, and sanity_thresholds.
    """
    rules_with_deps = sum(1 for r in rules if r.depends and r.depends != "—")
    counts: dict[str, int] = {
        "rules": len(rules),
        "index_lines": len(rendered_index.splitlines()),
        "keyword_entries": _count_keyword_entries(rules),
        "rules_with_deps": rules_with_deps,
    }
    return {
        "schema_version": STATS_SCHEMA_VERSION,
        "format_version": INDEX_FORMAT_VERSION,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_sha": _resolve_git_sha(project_root),
        "counts": counts,
        "tiers": _tier_counts(rules),
        "sanity_thresholds": dict(_SANITY_THRESHOLDS),
    }


def _stats_output_path(rules_dir: Path) -> Path:
    """Return the target path for ``.index-stats.json`` inside ``rules_dir``."""
    return rules_dir / STATS_FILENAME


def _serialize_stats(stats: dict[str, Any]) -> str:
    """Serialise ``stats`` to canonical JSON (sorted keys, 2-space indent, trailing newline)."""
    return json.dumps(stats, indent=2, sort_keys=True) + "\n"


def _write_index_stats(stats: dict[str, Any], rules_dir: Path) -> Path:
    """Write ``stats`` to ``.index-stats.json`` under ``rules_dir`` and return the path."""
    output_path = _stats_output_path(rules_dir)
    output_path.write_text(_serialize_stats(stats), encoding="utf-8")
    return output_path


def _normalize_stats_for_check(stats: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``stats`` with volatile fields blanked for equality checks.

    ``generated_at`` and ``git_sha`` are stripped to empty strings so that
    ``check`` mode doesn't spuriously fail when only the timestamp or the
    working-tree commit has changed.
    """
    normalized = dict(stats)
    for key in STATS_VOLATILE_KEYS:
        if key in normalized:
            normalized[key] = ""
    return normalized


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
    """Resolve rules dir, scan, load template, and render the index.

    Args:
        rules_dir: Optional explicit rules directory path.

    Returns:
        Tuple of (rules list, rendered index content, resolved rules_dir).

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

    # Preserve existing desc= fields across regeneration (manually-authored).
    existing_index_path = rules_dir / "RULES_INDEX.md"
    desc_map = _extract_desc_map(existing_index_path)

    try:
        content = render_rules_index(rules, template_path, desc_map)
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

    Renders ``templates/RULES_INDEX.md.template`` with one F4 compact row per
    rule for grep-based discovery.

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

    # Emit .index-stats.json alongside RULES_INDEX.md so the rule-loader
    # skill's sanity thresholds and expected-volume counts have an
    # authoritative, regenerated source of truth.
    stats = render_index_stats(rules, content, rules_dir.parent)
    try:
        stats_path = _write_index_stats(stats, rules_dir)
    except Exception as exc:
        log_error(f"Error writing {_stats_output_path(rules_dir)}: {exc}")
        raise typer.Exit(code=1) from None
    log_success(f"Generated {stats_path}")


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
    else:
        log_error("RULES_INDEX.md is out of date")
        console.print()
        _show_diff(current_content, content)
        console.print()
        console.print("[yellow]Run to update:[/yellow]")
        console.print("  ai-rules index generate")
        raise typer.Exit(code=1) from None

    # .index-stats.json must also be current. Volatile fields
    # (generated_at, git_sha) are normalised out before comparison so only a
    # real content drift (count/tier/schema change) fails the check.
    stats_path = _stats_output_path(rules_dir)
    if not stats_path.exists():
        log_error(f"{stats_path} does not exist")
        console.print("\n[yellow]Run:[/yellow] ai-rules index generate")
        raise typer.Exit(code=1) from None

    try:
        current_stats_text = stats_path.read_text(encoding="utf-8")
        current_stats = json.loads(current_stats_text)
    except Exception as exc:
        log_error(f"Error reading {stats_path}: {exc}")
        raise typer.Exit(code=1) from None

    generated_stats = render_index_stats(_rules, content, rules_dir.parent)

    if _normalize_stats_for_check(current_stats) != _normalize_stats_for_check(generated_stats):
        log_error(f"{stats_path.name} is out of date")
        console.print()
        console.print("[yellow]Run to update:[/yellow]")
        console.print("  ai-rules index generate")
        raise typer.Exit(code=1) from None

    log_success(".index-stats.json is up-to-date")

    # Corpus-wide `kw:` count sanity threshold (§5.4). Regenerated
    # `counts.keyword_entries` must meet or exceed the stored floor; a lower
    # value indicates mass keyword deletion or a regressed parser. The check
    # is bypassed for tiny corpora (<20 rules) so unit tests that seed a
    # single-rule scratch directory do not trip the production floor.
    total_rules = int(generated_stats.get("counts", {}).get("rules", 0))
    if total_rules >= 20:
        regenerated_kw_entries = int(generated_stats.get("counts", {}).get("keyword_entries", 0))
        kw_min = int(
            generated_stats.get("sanity_thresholds", {}).get(
                "keyword_entries_min", _SANITY_THRESHOLDS["keyword_entries_min"]
            )
        )
        if regenerated_kw_entries < kw_min:
            log_error(
                f"Corpus keyword_entries={regenerated_kw_entries} is below sanity floor {kw_min}"
            )
            console.print(
                "\n[yellow]This usually means a mass keyword deletion or a regressed metadata parser.[/yellow]"
            )
            raise typer.Exit(code=1) from None
        log_success(
            f"keyword_entries sanity check passed ({regenerated_kw_entries} ≥ floor {kw_min})"
        )
