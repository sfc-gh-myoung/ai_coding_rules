"""Manifest builder — produces ``rule-loader-manifest/v2`` output.

The token-budget enforcement replicates the inline while-loop from
``manifest_generator.py:257-262``.  There is NO separate ``budget_manager``
object; the cap is applied directly in ``build_manifest()``.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_rules.rule_matcher.frontmatter import RuleFrontmatter


@dataclass
class ManifestRule:
    """Lightweight rule entry emitted in the manifest."""

    filename: str
    rule_version: str
    context_tier: str
    token_budget: int | None
    description: str
    is_dependency_only: bool = False

    def to_dict(self) -> dict:
        d: dict = {
            "filename": self.filename,
            "rule_path": f"rules/{self.filename}",
            "context_tier": self.context_tier,
            "rule_version": self.rule_version,
            "description": self.description,
        }
        if self.token_budget is not None:
            d["token_budget"] = self.token_budget
        if self.is_dependency_only:
            d["is_dependency_only"] = True
        return d


@dataclass
class DeferredRule:
    filename: str
    reason: str

    def to_dict(self) -> dict:
        return {"filename": self.filename, "reason": self.reason}


@dataclass
class RuleLoaderManifest:
    schema: str
    load_sequence: list[ManifestRule]
    deferred_rules: list[DeferredRule]
    candidate_rules: list[ManifestRule]
    warnings: list[dict]

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema,
            "load_sequence": [r.to_dict() for r in self.load_sequence],
            "deferred_rules": [d.to_dict() for d in self.deferred_rules],
            "candidate_rules": [r.to_dict() for r in self.candidate_rules],
            "warnings": self.warnings,
        }


def _to_manifest_rule(rule: RuleFrontmatter, is_dep_only: bool = False) -> ManifestRule:
    return ManifestRule(
        filename=rule.filename,
        rule_version=rule.rule_version,
        context_tier=rule.context_tier,
        token_budget=rule.token_budget,
        description=rule.description,
        is_dependency_only=is_dep_only,
    )


def _token_estimate(rules: list[ManifestRule]) -> int:
    return sum(r.token_budget or 0 for r in rules)


def build_manifest(
    resolved: list[RuleFrontmatter],
    warnings: list[dict],
    *,
    matched_filenames: set[str] | None = None,
    max_entries: int = 5,
    max_tokens: int = 20_000,
) -> RuleLoaderManifest:
    """Apply entry count and token budget caps, return a ``rule-loader-manifest/v2``.

    Rules resolved solely through the dependency graph (``is_dependency_only``)
    do NOT count against *max_entries* — they are always included.

    Token budget enforcement replicates the inline while-loop from
    ``manifest_generator.py:257-262``: keeps popping the last entry until the
    estimate fits within *max_tokens*. Foundation rules (000-*) and
    dependency-only rules are protected from eviction.

    Args:
        resolved: Dependency-resolved list (matched rules + their required deps).
        warnings: Missing-dep warnings from ``resolve_dependencies()``.
        matched_filenames: Set of filenames that scored >= 1 (not dep-only).
            If ``None``, all *resolved* rules are treated as direct matches.
        max_entries: Domain/activity rule cap (default 5).
        max_tokens: R4 token ceiling (default 20 000).
    """
    if matched_filenames is None:
        matched_filenames = {r.filename for r in resolved}

    deferred: list[DeferredRule] = []
    candidate_rules = [_to_manifest_rule(r) for r in resolved]

    # Split resolved into capped direct matches and always-included deps
    direct: list[ManifestRule] = []
    deps_only: list[ManifestRule] = []
    for rule in resolved:
        is_dep = rule.filename not in matched_filenames
        mr = _to_manifest_rule(rule, is_dep_only=is_dep)
        if is_dep:
            deps_only.append(mr)
        else:
            direct.append(mr)

    # Apply max_entries cap to direct matches only
    capped_direct = direct[:max_entries]
    for mr in direct[max_entries:]:
        deferred.append(DeferredRule(filename=mr.filename, reason="entry_cap"))

    load_sequence = capped_direct + deps_only

    # Token budget enforcement — protect foundation and deps from eviction
    while _token_estimate(load_sequence) > max_tokens and len(load_sequence) > 1:
        # Find the last non-protected entry to remove
        # Protected: foundation (000-*) and dependency-only rules
        removed_idx = None
        for i in range(len(load_sequence) - 1, -1, -1):
            entry = load_sequence[i]
            is_foundation = entry.filename.startswith("000-")
            if not is_foundation and not entry.is_dependency_only:
                removed_idx = i
                break
        if removed_idx is None:
            break  # Only protected entries remain; cannot shrink further
        removed = load_sequence.pop(removed_idx)
        deferred.append(DeferredRule(filename=removed.filename, reason="token_budget"))

    return RuleLoaderManifest(
        schema="rule-loader-manifest/v2",
        load_sequence=load_sequence,
        deferred_rules=deferred,
        candidate_rules=candidate_rules,
        warnings=warnings,
    )
