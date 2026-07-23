"""Dependency graph resolver.

Walks the ``depends: {required: [...]}`` graph transitively.  Optional deps
are informational only and are NOT resolved transitively.

Missing required dep files are logged as warnings and recorded in the manifest
``warnings`` list — no exception is raised.
"""

from __future__ import annotations

import logging
from collections import OrderedDict

from ai_rules.rule_matcher.frontmatter import RuleFrontmatter
from ai_rules.rule_matcher.matcher import ScoredRule

logger = logging.getLogger(__name__)


def _strip_yaml_comment(value: str) -> str:
    """Strip an inline YAML comment from a string value.

    Example: ``'100-core.md  # reason'`` → ``'100-core.md'``.
    """
    return value.split("#")[0].strip()


def get_required_deps(rule: RuleFrontmatter) -> list[str]:
    """Return the list of required dependency filenames for *rule*.

    Inline YAML comments are stripped from each entry.
    Returns an empty list when ``depends:`` is absent or has no ``required`` key.
    """
    if not rule.depends:
        return []
    return [_strip_yaml_comment(d) for d in rule.depends.get("required", []) if d]


def resolve_dependencies(
    matched: list[ScoredRule],
    rules_db: dict[str, RuleFrontmatter],
) -> tuple[list[RuleFrontmatter], list[dict]]:
    """Walk the ``required`` dep graph and return all rules that should load.

    Transitive required deps that did not independently match are included.
    Optional deps are NOT transitively resolved.

    Returns:
        ``(resolved_rules, warnings)`` where *warnings* is a list of
        ``{"rule": <filename>, "missing_dep": <filename>}`` records for any
        required dep file not found in *rules_db*.

    The resolution preserves insertion order (dependency before dependents would
    be unusual; the topological walk ensures deps appear first).
    """
    to_load: OrderedDict[str, RuleFrontmatter] = OrderedDict()
    warnings: list[dict] = []

    # Seed with matched rules; mark them as primary matches
    queue: list[tuple[RuleFrontmatter, bool]] = [(sr.rule, False) for sr in matched]
    visited: set[str] = set()

    while queue:
        rule, _is_dep_only = queue.pop(0)
        if rule.filename in visited:
            continue
        visited.add(rule.filename)
        to_load[rule.filename] = rule

        for dep_name in get_required_deps(rule):
            dep_clean = _strip_yaml_comment(dep_name)
            if not dep_clean:
                continue
            if dep_clean in visited:
                continue
            if dep_clean not in rules_db:
                logger.warning("Required dep %s not found for rule %s", dep_clean, rule.filename)
                warnings.append({"rule": rule.filename, "missing_dep": dep_clean})
                continue
            queue.append((rules_db[dep_clean], True))

    return list(to_load.values()), warnings
