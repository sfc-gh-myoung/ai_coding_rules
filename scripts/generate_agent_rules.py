#!/usr/bin/env python3
"""
Utility: Generate agent-specific rule files from *.md

Supported agents
- cursor: writes .cursor/rules/<name>.mdc with YAML header and Cursor docs comment:
  ---
  description: <text>
  globs:
    - "**/*"
  alwaysApply: false|true
  ---
  <!-- Generated for Cursor project rules. See https://docs.cursor.com/en/context/rules#project-rules -->

- copilot: writes .github/instructions/<name>.md with YAML header and Copilot docs comment:
  ---
  appliesTo:
    - "**/*"
  ---
  <!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

- cline: writes .clinerules/<name>.md with plain Markdown and Cline docs comment:
  <!-- Generated for Cline rules. See https://docs.cline.bot/features/cline-rules -->

- universal: writes rules/<name>.md with pure Markdown (no YAML, no comments):
  Clean markdown suitable for any IDE/agent/LLM

Common behavior
- Reads *.md (skips documentation files: README.md, CHANGELOG.md, CONTRIBUTING.md)
- Also skips AGENTS.md and EXAMPLE_PROMPT.md for all formats (they're guides, not rules)
- Parses metadata from leading markdown header lines:
  - **Description:**
  - **AutoAttach:**
  - **AppliesTo:** (backticks or comma/space-separated)
  - **Keywords:** (comma-separated, for semantic discovery)
  - **Version:**
  - **LastUpdated:**
- Strips the above metadata lines and any existing YAML frontmatter from the body
- Defaults globs/appliesTo to ["**/*"] when absent

Usage
  # Generate Cursor rules (writes to ./.cursor/rules by default)
  python ai_coding_rules/generate_agent_rules.py --agent cursor [--dry-run]

  # Generate Copilot rules (writes to ./.github/instructions by default)
  python ai_coding_rules/generate_agent_rules.py --agent copilot [--dry-run]

  # Generate Cline rules (writes to ./.clinerules by default)
  python ai_coding_rules/generate_agent_rules.py --agent cline [--dry-run]

  # Generate Universal rules (writes to ./rules by default)
  python ai_coding_rules/generate_agent_rules.py --agent universal [--dry-run]

  # Generate to custom base directory (creates ../parent/.cursor/rules)
  python ai_coding_rules/generate_agent_rules.py --agent cursor --destination ../parent

  # CI check mode: exit non-zero if any outputs are stale/missing
  python ai_coding_rules/generate_agent_rules.py --agent cursor --check
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

RE_DESCRIPTION = re.compile(r"^\*\*Description:\*\*\s*(.*)$", re.IGNORECASE)
RE_APPLIES = re.compile(r"^\*\*AppliesTo:\*\*\s*(.*)$", re.IGNORECASE)
RE_AUTO_ATTACH = re.compile(r"^\*\*AutoAttach:\*\*\s*(true|false|.*)$", re.IGNORECASE)
RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.IGNORECASE)
RE_VERSION = re.compile(r"^\*\*Version:\*\*\s*(.*)$", re.IGNORECASE)
RE_LAST_UPDATED = re.compile(r"^\*\*LastUpdated:\*\*\s*(.*)$", re.IGNORECASE)
RE_TYPE = re.compile(r"^\*\*Type:\*\*\s*(.*)$", re.IGNORECASE)
RE_TOKEN_BUDGET = re.compile(r"^\*\*TokenBudget:\*\*\s*(.*)$", re.IGNORECASE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.*)$", re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.IGNORECASE)


def strip_existing_yaml_header(text: str) -> str:
    """Remove a leading YAML frontmatter block if present (--- ... ---)."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + len("\n---\n") :]


def strip_markdown_metadata_lines(text: str) -> str:
    """Remove specific markdown header lines (Description, AutoAttach, AppliesTo, Version, LastUpdated, Type).

    Preserves Keywords, TokenBudget, ContextTier, and Depends as these are universally useful for
    semantic discovery, attention budget management, prioritization, and dependency resolution.
    """
    out_lines: list[str] = []
    for line in text.splitlines():
        ls = line.strip()
        if (
            RE_DESCRIPTION.match(ls)
            or RE_APPLIES.match(ls)
            or RE_AUTO_ATTACH.match(ls)
            or RE_VERSION.match(ls)
            or RE_LAST_UPDATED.match(ls)
            or RE_TYPE.match(ls)
        ):
            continue
        out_lines.append(line)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


def parse_applies_to(text: str) -> list[str]:
    """Parse `**AppliesTo:**` into a list of globs.

    Supports backtick-delimited entries or comma/whitespace separated tokens.
    """
    globs: list[str] = []
    for line in text.splitlines():
        m = RE_APPLIES.match(line.strip())
        if not m:
            continue
        raw = m.group(1).strip()
        ticked = re.findall(r"`([^`]+)`", raw)
        if ticked:
            globs.extend([p.strip() for p in ticked if p.strip()])
        else:
            parts = re.split(r"[,\s]+", raw)
            globs.extend([p for p in parts if p])
        break
    # De-duplicate, preserve order
    seen = set()
    unique: list[str] = []
    for g in globs:
        if g not in seen:
            unique.append(g)
            seen.add(g)
    return unique


def serialize_list_yaml(key: str, values: list[str], default: str) -> str:
    """Serialize values as list-style YAML with the given key.

    When values is empty, use [default].
    """
    if not values:
        values = [default]
    lines = ["---", f"{key}:"]
    lines.extend([f'  - "{v}"' for v in values])
    lines.append("---\n")
    return "\n".join(lines)


def convert_md_references_to_mdc(text: str) -> str:
    """Convert *.md references to *.mdc for Cursor rules.

    Converts patterns like:
    - filename.md -> filename.mdc
    - @filename.md -> @filename.mdc
    - path/to/file.md -> path/to/file.mdc

    Preserves documentation files like README.md, CHANGELOG.md, CONTRIBUTING.md
    """
    # Preserve common documentation files
    preserved_files = {
        "readme.md",
        "changelog.md",
        "contributing.md",
        "license.md",
        "authors.md",
        "security.md",
    }

    def replace_md_ref(match):
        full_match = match.group(0)
        filename = match.group(2).lower()  # Get the filename part in lowercase

        # Don't convert preserved documentation files
        if filename in preserved_files:
            return full_match

        # Convert .md to .mdc
        return match.group(1) + match.group(2)[:-3] + ".mdc"

    # Pattern matches: optional @ + filename + .md
    # Group 1: prefix (including @)
    # Group 2: filename.md
    pattern = r"(@?)([\w\-/]+\.md)(?=\s|$|[^\w\-/.])"

    return re.sub(pattern, replace_md_ref, text, flags=re.IGNORECASE)


@dataclass
class AgentSpec:
    name: str
    dest_dir: Path
    header_key: str  # "globs" for cursor, "appliesTo" for copilot
    prepend_comment: str | None

    def build_header(
        self, patterns: list[str], description: str | None = None, always_apply: bool | None = None
    ) -> str:
        """Build the agent-specific YAML header block."""
        if self.name == "cursor":
            patterns = patterns or []
            if not patterns:
                patterns = ["**/*"]
            # YAML-safe single-line description: escape quotes and replace newlines
            safe_desc = (
                (description or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
            )
            lines = ["---", f'description: "{safe_desc}"', "globs:"]
            lines.extend([f'  - "{p}"' for p in patterns])
            always_val = str(bool(always_apply)).lower() if always_apply is not None else "false"
            lines.append(f"alwaysApply: {always_val}")
            lines.append("---\n")
            return "\n".join(lines)
        elif self.name == "cline":
            # Cline uses plain Markdown with no YAML header
            return ""
        elif self.name == "universal":
            # Universal uses pure Markdown with no YAML header or comments
            return ""
        # copilot: simple list YAML (no extra fields)
        # Ensure all patterns are quoted and safe
        safe_patterns = [p.replace("\\", "\\\\").replace('"', '\\"') for p in (patterns or [])]
        return serialize_list_yaml(self.header_key, safe_patterns, default="**/*")


class AgentRuleGenerator:
    """Generate agent-specific rule files from *.md."""

    def __init__(self, agent: str, source: Path, destination: Path, dry_run: bool = False) -> None:
        self.agent = agent
        self.source = source
        self.destination = destination
        self.dry_run = dry_run

        if agent == "cursor":
            self.spec = AgentSpec(
                name="cursor",
                dest_dir=destination,
                header_key="globs",
                prepend_comment=(
                    "<!-- Generated for Cursor project rules. "
                    "See https://docs.cursor.com/en/context/rules#project-rules -->\n\n"
                ),
            )
        elif agent == "copilot":
            self.spec = AgentSpec(
                name="copilot",
                dest_dir=destination,
                header_key="appliesTo",
                prepend_comment=(
                    "<!-- Generated for GitHub Copilot repository instructions. "
                    "See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->\n\n"
                ),
            )
        elif agent == "cline":
            self.spec = AgentSpec(
                name="cline",
                dest_dir=destination,
                header_key="",  # Cline doesn't use header keys
                prepend_comment=(
                    "<!-- Generated for Cline rules. "
                    "See https://docs.cline.bot/features/cline-rules -->\n\n"
                ),
            )
        elif agent == "universal":
            self.spec = AgentSpec(
                name="universal",
                dest_dir=destination,
                header_key="",  # Universal doesn't use header keys
                prepend_comment=None,  # No generated comments for universal
            )
        else:
            raise ValueError("agent must be one of: 'cursor', 'copilot', 'cline', 'universal'")

    def run(self) -> None:
        """Execute generation for all *.md files.

        In normal mode, writes files only when content changes.
        In --check mode, exits with non-zero status if any outputs are stale or missing.
        """
        self.destination.mkdir(parents=True, exist_ok=True)
        stale_found = False
        for md_path in sorted(self.source.glob("*.md")):
            # Skip documentation files that are not rules
            filename_lower = md_path.name.lower()
            if filename_lower in ("readme.md", "changelog.md", "contributing.md"):
                continue
            # Skip AGENTS.md and EXAMPLE_PROMPT.md for all formats (they're guides, not rules)
            if filename_lower in ("agents.md", "example_prompt.md"):
                continue
            is_stale = self._process_file(md_path)
            stale_found = stale_found or is_stale

        # Copy discovery files for universal format
        if self.agent == "universal":
            self._copy_discovery_files()

        if getattr(self, "check_mode", False) and stale_found:
            print("One or more agent rule outputs are stale. Re-run without --check to update.")
            sys.exit(1)

    def _copy_discovery_files(self) -> None:
        """Copy discovery files from discovery/ to universal output directory."""
        discovery_dir = Path("discovery")
        if not discovery_dir.exists():
            return

        discovery_files = ["AGENTS.md", "EXAMPLE_PROMPT.md", "RULES_INDEX.md"]
        for file_name in discovery_files:
            src = discovery_dir / file_name
            if src.exists():
                dst = self.destination / file_name
                if not self.dry_run:
                    shutil.copy2(src, dst)
                    try:
                        rel = os.path.relpath(dst, start=Path.cwd())
                        print(f"Copied {file_name} to {rel}")
                    except Exception:
                        print(f"Copied {file_name} to {dst}")
                else:
                    print(f"[DRY-RUN] Would copy: {file_name} to {dst}")

    def _process_file(self, md_path: Path) -> bool:
        src_text = md_path.read_text(encoding="utf-8")

        # Clean body
        body = strip_existing_yaml_header(src_text)
        body = strip_markdown_metadata_lines(body)

        # Convert *.md references to *.mdc for Cursor rules only
        if self.agent == "cursor":
            body = convert_md_references_to_mdc(body)

        # Parse metadata
        description, _, always_apply = self._parse_description_and_autoattach(
            src_text, md_path.stem
        )
        patterns = parse_applies_to(src_text)

        # Build header
        header = self.spec.build_header(
            patterns, description=description, always_apply=always_apply
        )
        comment = self.spec.prepend_comment or ""

        # Destination path
        if self.agent == "cursor":
            dst_path = self.destination / (md_path.stem + ".mdc")
        else:
            dst_path = self.destination / md_path.name

        out_text = header + comment + body

        # Normalize single trailing newline
        if not out_text.endswith("\n"):
            out_text += "\n"

        # Skip rewrite if unchanged
        if dst_path.exists():
            try:
                existing = dst_path.read_text(encoding="utf-8")
            except Exception:
                existing = None
            if existing is not None and existing == out_text:
                # unchanged
                return False

        if self.dry_run:
            print(f"[DRY-RUN] Would write: {dst_path}")
            return True

        dst_path.write_text(out_text, encoding="utf-8")
        # Print a friendly relative path when possible, otherwise absolute path
        try:
            rel = os.path.relpath(dst_path, start=Path.cwd())
            print(f"Wrote {rel}")
        except Exception:
            print(f"Wrote {dst_path}")
        return True

    @staticmethod
    def _parse_description_and_autoattach(
        text: str, fallback_name: str
    ) -> tuple[str, bool | None, bool | None]:
        """Extract description and auto-attach flag from markdown header lines.

        Returns (description, unused_globs_placeholder, always_apply)
        The middle return value is unused and kept for signature compatibility.
        """
        description: str | None = None
        always_apply: bool | None = None

        for line in text.splitlines():
            if description is None:
                m = RE_DESCRIPTION.match(line.strip())
                if m:
                    description = m.group(1).strip()
                    continue
            m = RE_AUTO_ATTACH.match(line.strip())
            if m:
                val = m.group(1).strip().lower()
                if val in ("true", "false"):
                    always_apply = val == "true"
                continue

        if description is None:
            description = fallback_name

        return description, None, always_apply


def main() -> None:
    """CLI entry point for agent rules generation."""
    parser = argparse.ArgumentParser(description="Generate agent rules from *.md")
    parser.add_argument(
        "--agent",
        choices=["cursor", "copilot", "cline", "universal"],
        required=True,
        help="Target agent",
    )
    parser.add_argument(
        "--source",
        default=None,
        help=(
            "Source directory containing .md rule files. "
            "Auto-detects: templates/ if exists, else ai_coding_rules/, else current directory."
        ),
    )
    parser.add_argument(
        "--legacy-paths",
        action="store_true",
        help=(
            "Use legacy output paths (.cursor/rules/, .github/instructions/, .clinerules/, rules/) "
            "instead of new generated/ structure"
        ),
    )
    parser.add_argument(
        "--destination",
        help=(
            "Base directory for output. Agent-specific subdirectories will be created within this directory. "
            "Defaults to current directory, creating .cursor/rules, .github/instructions, or .clinerules as appropriate."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run without writing files"
    )
    parser.add_argument(
        "--check", action="store_true", help="Exit non-zero if any outputs are stale/missing"
    )
    args = parser.parse_args()

    # Auto-detect source directory
    if args.source:
        source = Path(args.source).resolve()
    else:
        # Try templates/ first (new structure)
        if Path("templates").exists() and list(Path("templates").glob("*.md")):
            source = Path("templates").resolve()
            print("✓ Using source directory: templates/ (new structure)")
        # Fall back to ai_coding_rules/ (legacy)
        elif Path("ai_coding_rules").exists():
            source = Path("ai_coding_rules").resolve()
            print("✓ Using source directory: ai_coding_rules/ (legacy structure)")
        # Fall back to current directory
        else:
            source = Path(".").resolve()
            print("✓ Using source directory: . (current directory)")

    if not source.exists():
        raise SystemExit(f"Source directory not found: {source}")

    # Determine base directory and output paths
    if args.destination:
        base_dir = Path(args.destination).resolve()
    elif args.legacy_paths:
        base_dir = Path(".").resolve()
    else:
        base_dir = Path("generated").resolve()

    # Create agent-specific subdirectory within base
    if args.legacy_paths:
        # Legacy paths: output to IDE-expected locations
        if args.agent == "cursor":
            destination = Path(".cursor/rules").resolve()
        elif args.agent == "copilot":
            destination = Path(".github/instructions").resolve()
        elif args.agent == "cline":
            destination = Path(".clinerules").resolve()
        else:  # universal
            destination = Path("rules").resolve()
    else:
        # New structure: output to generated/ subdirectories
        if args.agent == "cursor":
            destination = base_dir / "cursor" / "rules"
        elif args.agent == "copilot":
            destination = base_dir / "copilot" / "instructions"
        elif args.agent == "cline":
            destination = base_dir / "cline"
        else:  # universal
            destination = base_dir / "universal"

    generator = AgentRuleGenerator(
        agent=args.agent, source=source, destination=destination, dry_run=args.dry_run
    )
    generator.check_mode = bool(args.check)
    generator.run()


if __name__ == "__main__":
    main()
