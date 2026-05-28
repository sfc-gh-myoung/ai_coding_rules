"""Shared YAML skeleton renderer for the rule-loader eval CLI.

Used by ``ai-rules rule-loader create`` (author a brand-new fixture from
a candidate prompt) and ``ai-rules rule-loader refresh`` (regenerate an
existing fixture's expectations from a fresh live run). Pure formatter
over an :class:`AgentRun` plus the rule metadata snapshot.

Renders fixtures under the valid-by-construction contract:

- Loaded rules with no typed-Keywords trigger evidence are emitted under
  ``optional:`` with ``# auto-demoted`` and a per-rule ``# missing:``
  hint, never under ``required:``.
- N-gram-derived prompt phrases appear as inline ``# n-gram (no rule):``
  comments under ``kw:``, never as YAML values.
- Optional ``preserved`` mapping (from author-supplied ``# preserve``
  annotations) overrides the live-run classification on a per-rule basis.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata
from ai_rules.rule_loader_eval.suggestions import (
    Suggestions,
    build_suggestions,
)

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import AgentRun


def format_fixture_snippet(  # noqa: D417
    run: AgentRun,
    prompt: str,
    fixture_id: str | None,
    variant: str,
    project_root: Path,
    updated: str,
    *,
    preserved: dict[str, str] | None = None,
) -> str:
    """Render a paste-ready fixture YAML skeleton from the live-loaded set.

    Inline ``# suggested: <reason>`` comments are produced mechanically
    from the rule metadata snapshot + prompt text:

    - ``required`` vs ``dependencies`` vs ``optional`` split via the
      ``**Depends:**`` DAG and the auto-demote rule (loaded rules with no
      typed-Keywords trigger evidence go to ``optional`` with a ``# auto-demoted``
      reason).
    - ``trigger_evidence`` (kw/ext/file/dir) by case-insensitive substring
      match of each rule's typed ``Keywords`` values against the
      prompt.
    - ``ngram_kw_suggestions`` rendered as inline ``# n-gram (no rule):``
      comments below the ``kw:`` block.

    Suggestions are advisory: authors review and edit before committing.

    The ``updated`` argument is rendered verbatim into the YAML and must
    be a valid ISO 8601 timestamp with offset (callers control whether
    the value is "now" or preserved from disk).

    Args:
        preserved: optional ``{rule_path: section}`` map from
            :func:`ai_rules.rule_loader_eval.annotations.parse_preservation_annotations`.
            When a rule appears in this map, the renderer pins it to that section
            (``required`` / ``optional`` / ``forbidden``) regardless of the live
            run's classification, and emits a trailing ``# preserve`` annotation
            on the line. Stale preservations (rule no longer loaded) emit a
            ``# preserve: stale (not loaded by live agent this run)`` warning.
    """
    rules_meta = load_rules_metadata(project_root / "rules")
    sugg = build_suggestions(run.loaded, prompt, rules_meta)
    sugg = _apply_preserved(sugg, preserved or {})

    fid = fixture_id or "TODO-fixture-id"
    lines = [
        "schema_version: 2",
        f"updated: {updated}",
        f"id: {fid}",
        "description: # TODO",
        f"variant: {variant}",
        "prompt: |",
    ]
    for pl in prompt.splitlines() or [""]:
        lines.append(f"  {pl}")

    lines.append("expected:")

    # required:
    lines.append("  required:")
    if sugg.required:
        for rule in sugg.required:
            lines.append(_format_classification_line(rule, sugg, "required", preserved or {}))
    else:
        lines.append("    # TODO: no required rules detected — review run.loaded")

    # dependencies:
    lines.append("  dependencies:")
    if sugg.dependencies:
        for rule in sugg.dependencies:
            lines.append(_format_classification_line(rule, sugg, "dependencies", preserved or {}))
    else:
        lines.append("    []   # suggested: no transitive deps detected")

    # forbidden:
    forbidden_rules = sorted(
        r for r, section in (preserved or {}).items() if section == "forbidden"
    )
    if forbidden_rules:
        lines.append("  forbidden:")
        for rule in forbidden_rules:
            lines.append(_format_classification_line(rule, sugg, "forbidden", preserved or {}))
    else:
        lines.append("  forbidden: []")

    # optional:
    if sugg.optional:
        lines.append("  optional:")
        for rule in sugg.optional:
            lines.append(_format_classification_line(rule, sugg, "optional", preserved or {}))
            hint = _format_missing_hint(rule, sugg)
            if hint is not None:
                lines.append(hint)
    else:
        lines.append("  optional: []")

    # trigger_evidence:
    lines.append("trigger_evidence:")
    for kind in ("kw", "ext", "file", "dir"):
        values = sugg.trigger_evidence.get(kind, ())
        if values:
            joined = ", ".join(values)
            lines.append(f"  {kind}: [{joined}]   # suggested")
        else:
            lines.append(f"  {kind}: []")
        if kind == "kw":
            for phrase in sugg.ngram_kw_suggestions:
                # Quote phrase to disambiguate from punctuation; YAML comments
                # ignore quoting so this is purely human-readable.
                lines.append(f'    # n-gram (no rule): "{phrase}"')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_classification_line(
    rule: str,
    sugg: Suggestions,
    section: str,
    preserved: dict[str, str],
) -> str:
    """Format a single ``- rules/X.md  # comment`` line for a classification section."""
    pieces: list[str] = []

    if section == "required":
        reason = sugg.rule_reasons.get(rule, "")
        if reason:
            pieces.append(f"# suggested: {reason}")
    elif section == "dependencies":
        reason = sugg.rule_reasons.get(rule, "dep")
        pieces.append(f"# suggested: {reason}")
    elif section == "optional":
        reason = sugg.rule_reasons.get(rule, "auto-demoted: no trigger evidence")
        # Detect stale preservation: in optional but not in auto_demoted set means
        # the rule was preserved but didn't appear in the live run at all.
        if (
            rule in preserved
            and preserved.get(rule) == "optional"
            and rule not in sugg.auto_demoted
        ):
            pieces.append("# preserve: stale (not loaded by live agent this run)")
        else:
            pieces.append(f"# {reason}")
    elif section == "forbidden":
        # Forbidden is preserve-only; nothing to suggest.
        pass

    # Append # preserve annotation if user pinned it.
    if (
        rule in preserved
        and preserved[rule] == section
        and not any("# preserve" in p for p in pieces)
    ):
        # Avoid duplicating the stale preserve note.
        pieces.append("# preserve")

    comment = "  ".join(pieces) if pieces else ""
    if comment:
        return f"    - {rule}  {comment}"
    return f"    - {rule}"


def _format_missing_hint(rule: str, sugg: Suggestions) -> str | None:
    """Return the ``# missing: kw=...; ext=...; file=...; dir=...`` hint line.

    Returns ``None`` if the rule has no missing-trigger metadata recorded.

    When the rule has NO typed-Keywords file-context triggers at all, emits a
    different hint so the empty case is visible to the author. The most common
    fix is to add ``ext:``, ``file:``, or ``dir:`` entries to the rule's
    ``Keywords:`` field.
    """
    triggers = sugg.missing_triggers.get(rule)
    if triggers is None:
        return None
    has_any = any(triggers.get(kind) for kind in ("kw", "ext", "file", "dir"))
    if not has_any:
        return "      # missing: rule has no file-context triggers (ext:/file:/dir:)"
    parts: list[str] = []
    for kind in ("kw", "ext", "file", "dir"):
        vals = triggers.get(kind, ())
        if vals:
            parts.append(f"{kind}={', '.join(vals)}")
    return f"      # missing: {'; '.join(parts)}"


def _apply_preserved(sugg: Suggestions, preserved: dict[str, str]) -> Suggestions:
    """Return a copy of *sugg* with classification overridden by *preserved*.

    A rule listed in *preserved* is moved to its preserved section regardless
    of its live-run classification. Stale entries (preserved but not loaded)
    are still emitted in the preserved section so the author sees them.
    """
    if not preserved:
        return sugg

    # Start from current classification.
    required = list(sugg.required)
    dependencies = list(sugg.dependencies)
    optional = list(sugg.optional)
    auto_demoted = set(sugg.auto_demoted)
    auto_demoted_was_dep = set(sugg.auto_demoted_was_dep)
    missing_triggers = dict(sugg.missing_triggers)
    rule_reasons = dict(sugg.rule_reasons)

    sections = {
        "required": required,
        "dependencies": dependencies,
        "optional": optional,
    }

    for rule, target_section in preserved.items():
        if target_section not in ("required", "dependencies", "optional", "forbidden"):
            continue
        # Remove rule from any current section.
        for section_list in sections.values():
            if rule in section_list:
                section_list.remove(rule)

        if target_section == "forbidden":
            # Forbidden is rendered separately; just drop from auto_demoted bookkeeping.
            auto_demoted.discard(rule)
            auto_demoted_was_dep.discard(rule)
            continue

        sections[target_section].append(rule)
        # When pinning, drop auto-demote flags so the renderer doesn't double-emit
        # the auto-demoted reason on a preserved line.
        if target_section != "optional":
            auto_demoted.discard(rule)
            auto_demoted_was_dep.discard(rule)
            missing_triggers.pop(rule, None)
            rule_reasons[rule] = rule_reasons.get(rule) or "preserved by author"

    # Re-sort each section for deterministic output.
    for name in sections:
        sections[name].sort()

    return Suggestions(
        required=tuple(sections["required"]),
        dependencies=tuple(sections["dependencies"]),
        optional=tuple(sections["optional"]),
        rule_reasons=rule_reasons,
        trigger_evidence=sugg.trigger_evidence,
        ngram_kw_suggestions=sugg.ngram_kw_suggestions,
        auto_demoted=frozenset(auto_demoted),
        auto_demoted_was_dep=frozenset(auto_demoted_was_dep),
        missing_triggers=missing_triggers,
    )
