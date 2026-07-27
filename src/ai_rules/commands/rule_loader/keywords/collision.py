"""Corpus-wide keyword collision map and post-filter utilities."""

from __future__ import annotations

from pathlib import Path

from ai_rules.commands.rule_loader.keywords.stoplist import _get_repo_root


def _get_default_exclude_list_path() -> Path:
    """Return the default exclude-list path (lazy — not computed at import time)."""
    return _get_repo_root() / ".workbench" / "config" / "exclude_list.txt"


def _load_exclude_list(path: Path | None = None) -> set[str]:
    """Return the set of rule filenames to exclude from collision counts."""
    resolved = path or _get_default_exclude_list_path()
    excluded: set[str] = set()
    if resolved.exists():
        for line in resolved.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                excluded.add(stripped)
    return excluded


def build_keyword_collision_map(
    rules_index_path: Path | None = None,
    exclude_list_path: Path | None = None,
) -> dict[str, list[str]]:
    """Build an inverted index from rule frontmatter: keyword → list of rule filenames.

    Args:
        rules_index_path: Unused (retained for API compatibility). Rules directory
            is inferred from the repo root.
        exclude_list_path: Path to the exclude list (defaults to workbench copy).

    Returns:
        Mapping from lower-cased keyword token to the sorted list of production
        rule filenames that declare it in their ``keywords:`` frontmatter field.
    """
    excluded = _load_exclude_list(exclude_list_path)
    rules_dir = _get_repo_root() / "rules"
    if not rules_dir.exists():
        return {}

    try:
        from ai_rules.match_rules import load_rules_db

        db = load_rules_db(rules_dir)
    except (ImportError, FileNotFoundError):
        return {}

    inverted: dict[str, set[str]] = {}
    for rule in db.values():
        if rule.filename in excluded:
            continue
        for kw in rule.typed_kw:
            key = kw.lower()
            if key:
                inverted.setdefault(key, set()).add(rule.filename)

    return {kw: sorted(rules) for kw, rules in inverted.items()}


def find_collision_violations(
    collision_map: dict[str, list[str]],
    max_collision: int,
) -> dict[str, list[str]]:
    """Return the subset of the collision map that exceeds the threshold."""
    return {kw: rules for kw, rules in collision_map.items() if len(rules) > max_collision}


def apply_collision_postfilter(
    keywords: list[str],
    rationale_candidates: list[str],
    collision_map: dict[str, list[str]],
    max_collision: int,
    *,
    current_rule_filename: str | None = None,
) -> list[str]:
    """Reject over-threshold keywords, substituting next-best rationale candidates.

    Args:
        keywords: Post-merge candidate list, in preference order.
        rationale_candidates: Additional keywords the LLM ranked but the merge
            step did not select.
        collision_map: Output of :func:`build_keyword_collision_map`.
        max_collision: Reject a keyword when it appears in strictly more than
            ``max_collision`` rules in the corpus.
        current_rule_filename: When set, the current rule is excluded from the
            collision count.

    Returns:
        Filtered keyword list with rejects replaced by next eligible entry
        from ``rationale_candidates``.
    """

    def _count_for(kw: str) -> int:
        rules = collision_map.get(kw.lower(), [])
        if current_rule_filename and current_rule_filename in rules:
            return len(rules) - 1
        return len(rules)

    accepted: list[str] = []
    seen_lower: set[str] = set()
    pool = list(rationale_candidates)

    def _try_add(candidate: str) -> bool:
        key = candidate.lower()
        if key in seen_lower:
            return False
        if _count_for(candidate) > max_collision:
            return False
        accepted.append(candidate)
        seen_lower.add(key)
        return True

    for kw in keywords:
        if _try_add(kw):
            continue
        # Rejected — try to substitute from the rationale pool
        substituted = False
        while pool:
            candidate = pool.pop(0)
            if _try_add(candidate):
                substituted = True
                break
        if not substituted:
            continue

    return accepted
