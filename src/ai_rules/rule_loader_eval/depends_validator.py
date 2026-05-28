"""Depends propagation validator.

For each rule in the loaded set, verifies that every ``required:`` dependency
listed in that rule's ``Depends:`` block is also present in the loaded set.

A violation means the agent loaded rule X but skipped rule Y even though
X's metadata says ``required: Y`` — a breach of contract R8.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


@dataclass(frozen=True)
class DependsViolation:
    """A single R8 propagation violation."""

    parent: str
    """The rule that was loaded."""

    missing_dep: str
    """The required dep of ``parent`` that was NOT loaded."""

    def __str__(self) -> str:  # noqa: D105
        return f"{self.parent} requires {self.missing_dep} (not loaded)"


def validate_depends_propagation(
    loaded: tuple[str, ...] | list[str],
    rules_meta: dict[str, RuleMetadata],
) -> list[DependsViolation]:
    """Return R8 violations for the given loaded set.

    For each rule path in ``loaded``, look up its ``depends_required`` list
    from ``rules_meta``. Any required dep that is not also in ``loaded`` is
    a violation.

    Args:
        loaded: iterable of rule paths (relative) that the agent loaded.
        rules_meta: mapping from rule path to ``RuleMetadata`` for the corpus.

    Returns:
        List of ``DependsViolation`` objects, one per missing dep. Empty when
        all required deps are satisfied.
    """
    loaded_set = set(loaded)
    violations: list[DependsViolation] = []
    for rule_path in sorted(loaded_set):
        meta = rules_meta.get(rule_path)
        if meta is None:
            continue
        for dep in meta.depends_required:
            if dep not in loaded_set:
                violations.append(DependsViolation(parent=rule_path, missing_dep=dep))
    return sorted(violations, key=lambda v: (v.parent, v.missing_dep))


def format_violations(violations: list[DependsViolation]) -> list[str]:
    """Format violations as human-readable lines for CLI / compare output."""
    if not violations:
        return []
    lines = [f"  R8 violation: {v}" for v in violations]
    return lines
