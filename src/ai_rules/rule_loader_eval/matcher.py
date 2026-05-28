"""Expected vs actual rule-set comparison.

The fixture declares two lists:
- ``required``: rules the prompt directly should match.
- ``dependencies``: rules transitively pulled in by required rules
  (declared in rules' Depends / Must Load First metadata).

Pass/fail is driven by the union: the agent's loaded set must contain
both. Failure messages partition the gap into ``missing_required`` and
``missing_dependencies`` so authors can see whether the gap is in
direct discovery or in dependency loading.

``forbidden`` rules MUST NOT be loaded. By default this is warn-only;
``strict_forbidden=True`` converts to hard-fail.

Citation validation checks the line count in ``**Rules Loaded**`` (or, for legacy
backward-compat, ``## Reads Performed``) against a snapshot of rule metadata
taken at eval start. Mismatches are reported as fabrication signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import Citation
    from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


@dataclass(frozen=True)
class CitationDrift:
    """A single citation that does not match the actual rule file.

    ``field`` is one of ``path`` or ``line_count``.
    """

    rule_path: str
    field: str
    declared: str
    actual: str
    section: str
    """Either ``Rules Loaded`` (primary) or ``Reads Performed`` (legacy backward-compat)."""


@dataclass(frozen=True)
class MatchResult:
    """Outcome of comparing expected vs actual loaded-rules sets."""

    missing_required: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    forbidden_present: tuple[str, ...]
    optional_loaded: tuple[str, ...]
    unloaded_optional: tuple[str, ...] = field(default_factory=tuple)
    """Rules expected as ``optional`` (incl. ``optional:`` Depends) that the agent did NOT load.
    Informational only — not counted toward pass/fail."""
    extras: tuple[str, ...] = field(default_factory=tuple)
    """Rules loaded that aren't in required/dependencies/forbidden/optional."""
    passed: bool = True
    warnings: tuple[str, ...] = field(default_factory=tuple)
    citation_drifts: tuple[CitationDrift, ...] = field(default_factory=tuple)
    """Per-citation mismatches against the rules-metadata snapshot."""


def match_loaded_rules(
    *,
    loaded: tuple[str, ...] | list[str] | set[str],
    required: tuple[str, ...] | list[str],
    dependencies: tuple[str, ...] | list[str] = (),
    forbidden: tuple[str, ...] | list[str] = (),
    optional: tuple[str, ...] | list[str] = (),
    strict_forbidden: bool = False,
) -> MatchResult:
    """Compare loaded rules to expected sets.

    Args:
        loaded: rules the agent actually loaded.
        required: rules that MUST be loaded (direct matches).
        dependencies: rules that MUST be loaded (transitively).
        forbidden: rules that MUST NOT be loaded.
        optional: informational; loaded or not.
        strict_forbidden: when True, forbidden presence fails the run.

    Returns:
        :class:`MatchResult`. ``passed`` is False iff any required or
        dependency rule is missing, or (when ``strict_forbidden``) any
        forbidden rule is present.
    """
    loaded_set = set(loaded)
    required_set = set(required)
    deps_set = set(dependencies)
    forbidden_set = set(forbidden)
    optional_set = set(optional)

    missing_required = tuple(sorted(required_set - loaded_set))
    missing_dependencies = tuple(sorted(deps_set - loaded_set))
    forbidden_present = tuple(sorted(loaded_set & forbidden_set))
    optional_loaded = tuple(sorted(loaded_set & optional_set))
    unloaded_optional = tuple(sorted(optional_set - loaded_set))
    extras = tuple(sorted(loaded_set - required_set - deps_set - forbidden_set - optional_set))

    warnings: list[str] = []
    for rule in forbidden_present:
        warnings.append(f"forbidden rule loaded: {rule}")

    passed = not missing_required and not missing_dependencies
    if forbidden_present:
        # v3.15.0: forbidden rules always fail when listed in the fixture's
        # forbidden block. Pre-v3.15 the strict_forbidden flag gated this;
        # the flag is now a no-op (kept for signature compatibility) since
        # forbidden lists are explicit fixture authoring intent.
        passed = False
    elif strict_forbidden and forbidden_present:
        passed = False

    return MatchResult(
        missing_required=missing_required,
        missing_dependencies=missing_dependencies,
        forbidden_present=forbidden_present,
        optional_loaded=optional_loaded,
        unloaded_optional=unloaded_optional,
        extras=extras,
        passed=passed,
        warnings=tuple(warnings),
    )


def validate_citations(
    *,
    citations: dict[str, Citation],
    rules_meta: dict[str, RuleMetadata],
    section: str,
) -> tuple[CitationDrift, ...]:
    """Compare declared citations against a rule-metadata snapshot.

    Citations follow the form ``<path> (<reason>) — N lines``. This function
    emits a ``CitationDrift`` for each path or line-count mismatch.

    Args:
        citations: per-path declared citations (from the agent response).
        rules_meta: snapshot of rule metadata captured at eval start.
        section: ``Rules Loaded`` (primary) or ``Reads Performed`` (legacy),
            used for attribution in drift records.

    Returns:
        Tuple of :class:`CitationDrift` records sorted by rule path.
    """
    drifts: list[CitationDrift] = []
    for path, citation in sorted(citations.items()):
        if citation.failed:
            continue
        meta = rules_meta.get(path)
        if meta is None:
            drifts.append(
                CitationDrift(
                    rule_path=path,
                    field="path",
                    declared=path,
                    actual="<rule file not in snapshot>",
                    section=section,
                )
            )
            continue
        if (
            citation.line_count is not None
            and meta.line_count
            and abs(citation.line_count - meta.line_count) > 1
        ):
            # Tolerate ±1 line drift. Different tools count file lines
            # differently: ``wc -l`` reports newline count, the Read tool
            # reports visual line count (often N+1 when the file ends with
            # a trailing newline). A 1-line gap is a tool-semantics
            # artifact, not fabrication. Anything larger is real drift.
            drifts.append(
                CitationDrift(
                    rule_path=path,
                    field="line_count",
                    declared=str(citation.line_count),
                    actual=str(meta.line_count),
                    section=section,
                )
            )
    return tuple(drifts)
