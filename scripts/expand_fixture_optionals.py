"""Option B: expand fixture optional: lists with transitive dep-chain rules.

For each fixture YAML, computes the transitive required: closure of its
``expected.required`` rules and appends any closure members not already
in ``required``, ``optional``, or ``forbidden`` to the fixture's
``optional:`` list, annotated with ``# dep-chain: required by <parent>``.

Safety guards:
- Optional-growth guard: if the number of deps to add would exceed
  ``len(required)``, the fixture is skipped with a warning.
- Idempotent: re-running produces identical YAML output.
- Comment-preserving: uses ruamel.yaml (NOT PyYAML) for round-trip.

Usage::

    uv run python scripts/expand_fixture_optionals.py [--dry-run]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq

# ---------------------------------------------------------------------------
# Bootstrap: project root on sys.path so ai_rules can be imported
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ai_rules.rule_loader_eval.depends_validator import expand_required_closure  # noqa: E402
from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
_log = logging.getLogger(__name__)

FIXTURES_DIR = PROJECT_ROOT / "fixtures" / "rule_loader_eval"
RULES_DIR = PROJECT_ROOT / "rules"

# Marker prefix used in comments so idempotency check can detect existing entries
_DEP_CHAIN_PREFIX = "dep-chain: required by"


def _parent_comment(dep: str, required: list[str], rules_meta: dict) -> str:
    """Return deterministic parent attribution comment for a dep.

    The parent is the alphabetically first rule in ``required`` whose
    transitive closure includes ``dep``.
    """
    for parent in sorted(required):
        closure = set(expand_required_closure([parent], rules_meta))
        if dep in closure:
            return f"# {_DEP_CHAIN_PREFIX} {parent.split('/')[-1]}"
    return f"# {_DEP_CHAIN_PREFIX} (unknown)"


def _already_annotated(optional_seq: CommentedSeq | list, dep: str) -> bool:
    """Return True if dep is already in the seq (idempotency check)."""
    return any(str(item).strip() == dep for item in optional_seq)


def process_fixture(
    fixture_path: Path,
    rules_meta: dict,
    *,
    dry_run: bool = False,
) -> int:
    """Expand optional: list of one fixture file. Returns number of deps added."""
    yaml = YAML()
    yaml.preserve_quotes = True
    with fixture_path.open(encoding="utf-8") as fh:
        doc = yaml.load(fh)

    expected = doc.get("expected") or {}
    required: list[str] = list(expected.get("required") or [])
    optional: list[str] = list(expected.get("optional") or [])
    forbidden: list[str] = list(expected.get("forbidden") or [])

    if not required:
        return 0

    # Compute transitive dep closure of all required rules
    closure = set(expand_required_closure(required, rules_meta))

    # Existing sets (strip inline comments from optional entries)
    required_set = set(required)
    existing_optional_set = {str(e).strip() for e in optional}
    forbidden_set = set(forbidden)

    # Deps to add: in closure but not already accounted for
    to_add = sorted(
        dep
        for dep in closure
        if dep not in required_set and dep not in existing_optional_set and dep not in forbidden_set
    )

    if not to_add:
        return 0

    # Optional-growth guard: skip if POST-script optional total would exceed required count.
    # This enforces AC-6: no fixture should have more optional entries than required entries.
    post_script_optional_count = len(optional) + len(to_add)
    if post_script_optional_count > len(required):
        _log.warning(
            "SKIP %s: adding %d dep-chain entries would push optional (%d→%d) > required (%d)",
            fixture_path.name,
            len(to_add),
            len(optional),
            post_script_optional_count,
            len(required),
        )
        return 0

    _log.info("%s: adding %d dep-chain entries to optional", fixture_path.name, len(to_add))

    if dry_run:
        for dep in to_add:
            comment = _parent_comment(dep, required, rules_meta)
            _log.info("  DRY-RUN would add: %s  %s", dep, comment)
        return len(to_add)

    # Build updated optional list using ruamel.yaml CommentedSeq
    optional_seq = expected.get("optional")
    if optional_seq is None:
        optional_seq = CommentedSeq()
        expected["optional"] = optional_seq

    for dep in to_add:
        comment_text = _parent_comment(dep, required, rules_meta)
        idx = len(optional_seq)
        optional_seq.append(dep)
        optional_seq.yaml_add_eol_comment(comment_text.lstrip("# "), idx)

    with fixture_path.open("w", encoding="utf-8") as fh:
        yaml.dump(doc, fh)

    return len(to_add)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    rules_meta = load_rules_metadata(RULES_DIR)
    _log.info("Loaded %d rules from %s", len(rules_meta), RULES_DIR)

    fixtures = sorted(FIXTURES_DIR.glob("*.yaml"))
    _log.info("Processing %d fixture files", len(fixtures))

    total_added = 0
    skipped = 0
    for fixture_path in fixtures:
        try:
            added = process_fixture(fixture_path, rules_meta, dry_run=args.dry_run)
            total_added += added
        except Exception as exc:
            _log.error("ERROR processing %s: %s", fixture_path.name, exc)
            skipped += 1

    _log.info(
        "Done. Total dep-chain entries added: %d (skipped %d fixture(s) on error)",
        total_added,
        skipped,
    )


if __name__ == "__main__":
    main()
