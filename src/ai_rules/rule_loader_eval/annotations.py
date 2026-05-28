"""Parse author-supplied ``# preserve`` annotations from existing fixture YAML.

The refresh / refresh-all driver reads the existing on-disk fixture before
regenerating, extracts any rule lines marked with ``# preserve`` (or
``# preserve: <reason>``) under ``required:``, ``dependencies:``,
``optional:``, or ``forbidden:`` sections, and passes the resulting
``{rule_path: section}`` map to :func:`snippet.format_fixture_snippet` so
those classifications survive across regenerations.

Parsing is text-level (regex line-by-line) rather than YAML-level because
``yaml.safe_load`` discards comments. The parser is intentionally narrow:

- Recognised section headers: ``required:``, ``dependencies:``,
  ``optional:``, ``forbidden:``. Any other top-level key resets the active
  section.
- A rule line is recognised as ``- rules/<name>.md``  optionally followed
  by inline comments. The line carries a preservation annotation when any
  of its comments contains the case-insensitive token ``preserve`` either
  bare (``# preserve``) or with a reason suffix (``# preserve: locked``).
- Indentation is required (``- `` must be preceded by whitespace) but its
  exact level is not enforced; this keeps the parser robust to trivial
  formatting differences.
"""

from __future__ import annotations

import re
from pathlib import Path

_VALID_SECTIONS = ("required", "dependencies", "optional", "forbidden")

# Matches a section header line, e.g. ``  required:`` or ``  required: []``.
# We ignore the inline-empty-list form because no rule lines follow it.
_SECTION_HEADER_RE = re.compile(
    r"^\s*(required|dependencies|optional|forbidden)\s*:\s*(\[\s*\])?\s*(?:#.*)?$",
    re.IGNORECASE,
)

# Matches a rule line, e.g. ``    - rules/100-snowflake-core.md  # comment``.
# Captures the rule path and the trailing comment string (if any).
_RULE_LINE_RE = re.compile(
    r"^\s*-\s*(rules/[A-Za-z0-9._/-]+\.md)\s*(#.*)?$",
)

# Matches a top-level YAML key (no leading whitespace) so we know to reset
# the active section. The expected fixture keys are ``schema_version``,
# ``updated``, ``id``, ``description``, ``variant``, ``prompt``,
# ``expected``, ``trigger_evidence``, ``notes``.
_TOP_LEVEL_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*:")

# Matches a ``# preserve`` annotation (possibly followed by ``: <reason>``).
# Allows additional comments on the same line; we just need to detect the
# token. Word boundary on ``preserve`` so we don't false-match ``preserved``.
_PRESERVE_TOKEN_RE = re.compile(r"#\s*preserve(?:\b|\s|:|$)", re.IGNORECASE)


def parse_preservation_annotations(yaml_text: str) -> dict[str, str]:
    """Return a ``{rule_path: section}`` map of preserved classifications.

    Walks *yaml_text* line by line, tracks the active section header, and
    records any ``- rules/X.md`` line whose trailing comment contains a
    ``# preserve`` token. Conflicting annotations (same rule preserved in
    two sections) are resolved by keeping the FIRST occurrence so behaviour
    is deterministic and predictable for authors.

    Args:
        yaml_text: full text of an existing fixture YAML file. Empty string
            or whitespace-only input returns ``{}``.

    Returns:
        Mapping from ``rules/<name>.md`` to one of ``"required"``,
        ``"dependencies"``, ``"optional"``, ``"forbidden"``. Empty when no
        annotations are present.
    """
    if not yaml_text or not yaml_text.strip():
        return {}

    out: dict[str, str] = {}
    active_section: str | None = None

    for raw_line in yaml_text.splitlines():
        section_match = _SECTION_HEADER_RE.match(raw_line)
        if section_match:
            active_section = section_match.group(1).lower()
            continue

        # Reset section when we hit any top-level key (no indentation).
        if raw_line and not raw_line[0].isspace() and _TOP_LEVEL_KEY_RE.match(raw_line):
            active_section = None
            continue

        if active_section is None:
            continue

        rule_match = _RULE_LINE_RE.match(raw_line)
        if not rule_match:
            continue

        rule_path = rule_match.group(1)
        trailing = rule_match.group(2) or ""
        if not _PRESERVE_TOKEN_RE.search(trailing):
            continue

        # First-occurrence wins for conflicts.
        if rule_path not in out:
            out[rule_path] = active_section

    return out


def parse_preservation_annotations_from_path(path: Path) -> dict[str, str]:
    """Convenience wrapper: read *path* (if it exists) and parse its annotations.

    Returns ``{}`` for a missing or unreadable file rather than raising, so
    the refresh driver can transparently handle the create-new-fixture case.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    return parse_preservation_annotations(text)
