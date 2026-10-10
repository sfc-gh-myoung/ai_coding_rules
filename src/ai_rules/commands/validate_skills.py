"""Structural validator for skills/*/SKILL.md entrypoints.

Checks:
  1. YAML frontmatter (name, description, version).
  2. Version/changelog parity against CHANGELOG.md in the skill directory.
  3. Local file references in SKILL.md resolve to existing files (one level).
  4. SKILL.md does not exceed 250 lines.
  5. Canonical H2 headings (with narrow aliases) are present.
  6. Prose style advisory (INFO only, never blocks CI).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.table import Table

from ai_rules._shared.console import console, err_console, log_error, log_info
from ai_rules._shared.paths import find_project_root, get_schemas_dir

_FRONTMATTER_FENCE = re.compile(r"^---\s*$")
_MARKDOWN_LINK = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


@dataclass
class SkillError:
    """A single validation finding for a skill file."""

    severity: str  # CRITICAL | HIGH | MEDIUM | INFO
    message: str
    error_group: str
    line_num: int | None = None
    fix_suggestion: str | None = None

    def format_brief(self) -> str:
        """One-line summary."""
        loc = f" (line {self.line_num})" if self.line_num else ""
        return f"[{self.error_group}] {self.message}{loc}"


@dataclass
class SkillResult:
    """Aggregated validation outcome for one SKILL.md."""

    skill_dir: Path
    errors: list[SkillError] = field(default_factory=list)
    passed_checks: int = 0

    @property
    def has_blocking(self) -> bool:
        """True when any CRITICAL or HIGH finding is present."""
        return any(e.severity in ("CRITICAL", "HIGH") for e in self.errors)

    @property
    def is_clean(self) -> bool:
        """True when no findings at all."""
        return not self.errors

    @property
    def skill_name(self) -> str:
        """Skill directory name."""
        return self.skill_dir.name


class SkillSchemaValidator:
    """Validate SKILL.md files against schemas/skill-schema.yml."""

    def __init__(
        self,
        schema_path: Path | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialise validator.

        Args:
            schema_path: Path to skill-schema.yml; defaults to schemas/skill-schema.yml.
            project_root: Project root used for path resolution.
        """
        self.project_root = project_root or find_project_root()
        if schema_path is None:
            schema_path = get_schemas_dir(self.project_root) / "skill-schema.yml"
        self.schema_path = schema_path
        self.schema = self._load_schema()

    # ── Schema loading ───────────────────────────────────────────────────────

    def _load_schema(self) -> dict[str, Any]:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Skill schema not found: {self.schema_path}")
        with open(self.schema_path) as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError(f"Skill schema must be a YAML mapping: {self.schema_path}")
        return data

    # ── Public API ────────────────────────────────────────────────────────────

    def validate_skill_dir(self, skill_dir: Path) -> SkillResult:
        """Validate SKILL.md inside *skill_dir*.

        Args:
            skill_dir: Directory containing SKILL.md (e.g. skills/rule-creator/).

        Returns:
            SkillResult with all findings and passed-check count.
        """
        result = SkillResult(skill_dir=skill_dir)
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            result.errors.append(
                SkillError(
                    severity="CRITICAL",
                    message="SKILL.md not found",
                    error_group="File",
                    fix_suggestion="Every skill directory must contain a SKILL.md entrypoint.",
                )
            )
            return result

        try:
            content = skill_md.read_text(encoding="utf-8")
        except OSError as exc:
            result.errors.append(
                SkillError(
                    severity="CRITICAL",
                    message=f"Cannot read SKILL.md: {exc}",
                    error_group="File",
                )
            )
            return result

        lines = content.splitlines()

        self._check_frontmatter(content, result)
        self._check_max_lines(lines, result)
        self._check_required_headings(lines, result)
        self._check_local_refs(content, skill_dir, result)
        self._check_changelog_parity(skill_dir, result)

        return result

    # ── Check: frontmatter ────────────────────────────────────────────────────

    def _parse_frontmatter(self, content: str) -> dict[str, Any] | None:
        """Return parsed frontmatter dict or None if absent/unparseable."""
        lines = content.splitlines()
        if not lines or not _FRONTMATTER_FENCE.match(lines[0]):
            return None
        for idx in range(1, min(len(lines), 200)):
            if _FRONTMATTER_FENCE.match(lines[idx]):
                block = "\n".join(lines[1:idx])
                try:
                    data = yaml.safe_load(block)
                except yaml.YAMLError:
                    return None
                return data if isinstance(data, dict) else None
        return None

    def _check_frontmatter(self, content: str, result: SkillResult) -> None:
        fm = self._parse_frontmatter(content)
        fm_config = self.schema.get("frontmatter", {})
        required_fields = fm_config.get("required_fields", [])

        if fm is None:
            for field_cfg in required_fields:
                result.errors.append(
                    SkillError(
                        severity=field_cfg.get("severity", "CRITICAL"),
                        message=field_cfg["error_message"],
                        error_group="Frontmatter",
                        line_num=1,
                        fix_suggestion=f"Add YAML frontmatter block with '{field_cfg['name']}' field.",
                    )
                )
            return

        for field_cfg in required_fields:
            key = field_cfg["name"]
            raw = fm.get(key)

            if raw is None:
                result.errors.append(
                    SkillError(
                        severity=field_cfg.get("severity", "CRITICAL"),
                        message=field_cfg["error_message"],
                        error_group="Frontmatter",
                        line_num=1,
                        fix_suggestion=f"Add '{key}:' to the YAML frontmatter block.",
                    )
                )
                continue

            value = str(raw).strip()

            # min_length check
            min_len = field_cfg.get("min_length")
            if min_len and len(value) < min_len:
                result.errors.append(
                    SkillError(
                        severity=field_cfg.get("severity", "HIGH"),
                        message=field_cfg["error_message"],
                        error_group="Frontmatter",
                        line_num=1,
                    )
                )
                continue

            # pattern check
            pattern = field_cfg.get("pattern")
            if pattern and not re.match(pattern, value):
                result.errors.append(
                    SkillError(
                        severity=field_cfg.get("severity", "CRITICAL"),
                        message=field_cfg["error_message"],
                        error_group="Frontmatter",
                        line_num=1,
                        fix_suggestion=f"Expected pattern: {pattern}",
                    )
                )
                continue

            result.passed_checks += 1

    # ── Check: max lines ──────────────────────────────────────────────────────

    def _check_max_lines(self, lines: list[str], result: SkillResult) -> None:
        struct = self.schema.get("structure", {})
        max_lines: int = struct.get("max_lines", 250)
        total = len(lines)
        if total > max_lines:
            result.errors.append(
                SkillError(
                    severity=struct.get("max_lines_severity", "HIGH"),
                    message=struct.get(
                        "max_lines_error_message",
                        f"SKILL.md exceeds {max_lines} lines ({total} found)",
                    ),
                    error_group="Size",
                    line_num=max_lines + 1,
                    fix_suggestion=(
                        f"Move content beyond line {max_lines} to "
                        "workflows/, references/, or examples/ subdirectories."
                    ),
                )
            )
        else:
            result.passed_checks += 1

    # ── Check: required headings ──────────────────────────────────────────────

    @staticmethod
    def _normalise(text: str) -> str:
        """Case-fold and strip for heading comparison."""
        return text.strip().lower()

    def _find_h2_headings(self, lines: list[str]) -> set[str]:
        """Return the set of normalised H2 heading texts found outside code fences."""
        headings: set[str] = set()
        in_fence = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^##\s+(.+)$", line)
            if m:
                headings.add(self._normalise(m.group(1)))
        return headings

    def _check_required_headings(self, lines: list[str], result: SkillResult) -> None:
        struct = self.schema.get("structure", {})
        required = struct.get("required_headings", [])
        present = self._find_h2_headings(lines)

        for heading_cfg in required:
            canonical: str = heading_cfg["canonical"]
            aliases: list[str] = heading_cfg.get("aliases", [])
            candidates = {self._normalise(canonical)} | {self._normalise(a) for a in aliases}
            if candidates & present:
                result.passed_checks += 1
            else:
                result.errors.append(
                    SkillError(
                        severity=heading_cfg.get("severity", "HIGH"),
                        message=heading_cfg.get(
                            "error_message",
                            f"Missing required heading: ## {canonical}",
                        ),
                        error_group="Structure",
                        fix_suggestion=f"Add '## {canonical}' section to SKILL.md.",
                    )
                )

    # ── Check: local file references ──────────────────────────────────────────

    def _check_local_refs(self, content: str, skill_dir: Path, result: SkillResult) -> None:
        checks_cfg = self.schema.get("checks", {})
        refs_cfg = checks_cfg.get("local_file_refs", {})
        if not refs_cfg.get("enabled", True):
            return

        exclude_patterns: list[str] = refs_cfg.get("exclude_patterns", [])
        compiled_excludes = [re.compile(p) for p in exclude_patterns]
        severity = refs_cfg.get("severity", "HIGH")

        lines = content.splitlines()
        for line_no, line in enumerate(lines, 1):
            for m in _MARKDOWN_LINK.finditer(line):
                target = m.group(1).strip()

                # Skip anchors, external URLs, mailto, etc.
                if any(exc.search(target) for exc in compiled_excludes):
                    continue

                # Strip query-string / fragment for existence check.
                file_part = re.split(r"[?#]", target)[0]
                if not file_part:
                    continue

                ref_path = skill_dir / file_part
                if ref_path.exists():
                    result.passed_checks += 1
                else:
                    result.errors.append(
                        SkillError(
                            severity=severity,
                            message=f"{refs_cfg.get('error_message', 'Local file reference not found')}: {target}",
                            error_group="Links",
                            line_num=line_no,
                            fix_suggestion=(
                                f"Create '{file_part}' relative to {skill_dir.name}/ "
                                "or remove the link."
                            ),
                        )
                    )

    # ── Check: changelog parity ───────────────────────────────────────────────

    def _extract_frontmatter_version(self, content: str) -> str | None:
        """Return the raw version string from frontmatter, or None."""
        fm = self._parse_frontmatter(content)
        if fm is None:
            return None
        raw = fm.get("version")
        return str(raw).strip() if raw is not None else None

    def _extract_changelog_version(self, changelog_path: Path, pattern: str) -> str | None:
        """Return the first semver found in CHANGELOG.md using *pattern*."""
        try:
            text = changelog_path.read_text(encoding="utf-8")
        except OSError:
            return None
        compiled = re.compile(pattern, re.MULTILINE)
        m = compiled.search(text)
        return m.group(1) if m else None

    def _check_changelog_parity(self, skill_dir: Path, result: SkillResult) -> None:
        checks_cfg = self.schema.get("checks", {})
        parity_cfg = checks_cfg.get("changelog_parity", {})
        if not parity_cfg.get("enabled", True):
            return

        changelog = skill_dir / "CHANGELOG.md"
        if not changelog.exists():
            # No changelog - skip this check entirely (not an error).
            return

        skill_md = skill_dir / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
        except OSError:
            return

        fm_version = self._extract_frontmatter_version(content)
        if fm_version is None:
            # Missing version already reported by _check_frontmatter.
            return

        pattern = parity_cfg.get("version_pattern", r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?")
        cl_version = self._extract_changelog_version(changelog, pattern)
        if cl_version is None:
            result.errors.append(
                SkillError(
                    severity=parity_cfg.get("severity", "HIGH"),
                    message="CHANGELOG.md exists but no semver entry was found",
                    error_group="Changelog",
                    fix_suggestion=(
                        "Add a heading like '## 1.0.0' or '## [1.0.0]' to CHANGELOG.md."
                    ),
                )
            )
            return

        if fm_version != cl_version:
            result.errors.append(
                SkillError(
                    severity=parity_cfg.get("severity", "HIGH"),
                    message=(
                        f"{parity_cfg.get('error_message', 'Version mismatch')}: "
                        f"frontmatter={fm_version}, CHANGELOG={cl_version}"
                    ),
                    error_group="Changelog",
                    fix_suggestion=(
                        f"Set 'version: {cl_version}' in SKILL.md frontmatter "
                        f"or add a '## {fm_version}' entry to CHANGELOG.md."
                    ),
                )
            )
        else:
            result.passed_checks += 1

    # ── Formatting ────────────────────────────────────────────────────────────

    def format_result(self, result: SkillResult) -> None:
        """Print a compact Rich summary for *result*."""
        if result.is_clean:
            console.print(
                f"  [green]✓[/green] {result.skill_name} ({result.passed_checks} checks passed)"
            )
            return

        blocking = [e for e in result.errors if e.severity in ("CRITICAL", "HIGH")]
        advisory = [e for e in result.errors if e.severity not in ("CRITICAL", "HIGH")]

        status = "[red]✗[/red]" if blocking else "[yellow]⚠[/yellow]"
        console.print(f"  {status} {result.skill_name}")

        for err in blocking:
            console.print(f"      [red]{err.format_brief()}[/red]")
            if err.fix_suggestion:
                console.print(f"        Fix: {err.fix_suggestion}")

        for err in advisory:
            console.print(f"      [dim]{err.format_brief()}[/dim]")


# ── Typer command ─────────────────────────────────────────────────────────────


def validate_skills(
    path: Annotated[
        Path,
        typer.Argument(
            help="Directory to scan for skill subdirectories (e.g. skills/).",
            show_default=False,
        ),
    ],
    schema: Annotated[
        Path | None,
        typer.Option(
            "--schema",
            help="Path to skill-schema.yml (default: schemas/skill-schema.yml).",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show per-check detail for every skill."),
    ] = False,
) -> None:
    """Validate skills/*/SKILL.md files against schemas/skill-schema.yml.

    Checks frontmatter fields, version/changelog parity, local file references,
    maximum 250 lines, and canonical section headings.  Prose style issues are
    advisory only and never block the build.

    Examples:
        ai-rules validate-skills skills/
        ai-rules validate-skills skills/rule-creator/
        ai-rules validate-skills skills/ --verbose
    """
    try:
        project_root = find_project_root()
    except FileNotFoundError:
        log_error("Could not find project root (no pyproject.toml found)")
        raise typer.Exit(1) from None

    try:
        validator = SkillSchemaValidator(schema_path=schema, project_root=project_root)
    except FileNotFoundError as exc:
        log_error(str(exc))
        raise typer.Exit(1) from None
    except Exception as exc:
        log_error(f"Error loading skill schema: {exc}")
        raise typer.Exit(1) from None

    if not path.exists():
        log_error(f"Path not found: {path}")
        raise typer.Exit(1) from None

    # Collect skill directories: either path IS a single skill dir (contains
    # SKILL.md directly) or it is a parent that holds multiple skill dirs.
    if (path / "SKILL.md").exists():
        skill_dirs = [path]
    elif path.is_dir():
        skill_dirs = sorted(d for d in path.iterdir() if d.is_dir())
        # Filter to dirs that contain SKILL.md (skip bare subdirs).
        skill_dirs = [d for d in skill_dirs if (d / "SKILL.md").exists()]
    else:
        log_error(f"Path is not a directory: {path}")
        raise typer.Exit(1) from None

    if not skill_dirs:
        log_info(f"No skill directories (containing SKILL.md) found in {path}")
        raise typer.Exit(0) from None

    results: list[SkillResult] = []
    for skill_dir in skill_dirs:
        result = validator.validate_skill_dir(skill_dir)
        results.append(result)
        if verbose:
            validator.format_result(result)
            if result.errors:
                # Show detail in verbose mode
                for err in result.errors:
                    sev_color = {
                        "CRITICAL": "red",
                        "HIGH": "yellow",
                        "MEDIUM": "blue",
                        "INFO": "dim",
                    }.get(err.severity, "white")
                    prefix = f"    [{sev_color}][{err.error_group}] {err.severity}[/{sev_color}]"
                    console.print(f"{prefix}: {err.message}")
                    if err.fix_suggestion:
                        console.print(f"      Fix: {err.fix_suggestion}")

    total = len(results)
    clean = sum(1 for r in results if r.is_clean)
    failed = sum(1 for r in results if r.has_blocking)
    advisory_only = sum(1 for r in results if r.errors and not r.has_blocking)

    # Summary table
    summary = Table(title="Skill Validation Summary")
    summary.add_column("Metric", style="bold")
    summary.add_column("Count", justify="right")
    summary.add_row("Total skills", str(total))
    summary.add_row("[green]Clean[/green]", str(clean))
    summary.add_row("[yellow]Advisory only[/yellow]", str(advisory_only))
    summary.add_row("[red]Failed[/red]", str(failed))
    console.print(summary)

    if not verbose:
        # Non-verbose: list failing skills with first error
        if failed:
            console.print("\n[red bold]FAILED SKILLS:[/red bold]")
            for result in results:
                if result.has_blocking:
                    first_blocking = next(
                        e for e in result.errors if e.severity in ("CRITICAL", "HIGH")
                    )
                    console.print(f"  • [red]{result.skill_name}[/red]: {first_blocking.message}")
        # Advisory items listed even in non-verbose mode for visibility.
        if advisory_only:
            console.print("\n[yellow]ADVISORY (INFO only – not blocking):[/yellow]")
            for result in results:
                if result.errors and not result.has_blocking:
                    for err in result.errors:
                        console.print(f"  • [dim]{result.skill_name}: {err.message}[/dim]")

    if failed:
        err_console.print(f"[red]{failed} skill(s) failed structural validation.[/red]")
        raise typer.Exit(1) from None

    raise typer.Exit(0)
