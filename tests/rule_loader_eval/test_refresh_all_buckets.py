"""Tests for refresh-all classification of ``required:`` vs ``optional:`` Depends.

Verifies that ``build_suggestions`` honors the bucket distinction defined by
the depends-required-optional-split plan: ``required:`` Depends drive the
strict ``dependencies`` bucket (classified via the parent's DAG), while
``optional:`` Depends do not — they remain candidates for ``required`` when
they have their own trigger evidence, and auto-demote to ``optional`` when
they don't.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_loader_eval.rules_meta import RuleMetadata
from ai_rules.rule_loader_eval.suggestions import build_suggestions

FOUNDATION = "rules/999-test-core.md"


def _meta(
    path: str,
    *,
    triggers: tuple[str, ...] = (),
    depends_required: tuple[str, ...] = (),
    depends_optional: tuple[str, ...] = (),
) -> RuleMetadata:
    """Construct a minimal RuleMetadata stub for the classifier."""
    kinds = frozenset(t.split(":", 1)[0] for t in triggers if ":" in t)
    return RuleMetadata(
        path=Path(path),
        triggers=triggers,
        trigger_kinds=kinds,
        depends=depends_required + depends_optional,
        depends_required=depends_required,
        depends_optional=depends_optional,
    )


def _foundation_meta() -> RuleMetadata:
    return _meta(FOUNDATION)


def test_required_dep_with_evidence_goes_to_dependencies() -> None:
    """A ``required:`` Depends with its own trigger evidence is classified as a dependency."""
    parent = "rules/parent-req.md"
    dep = "rules/dep-req.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(parent, triggers=("kw:parentword",), depends_required=(dep,)),
        dep: _meta(dep, triggers=("kw:depword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep),
        prompt="parentword and depword in the prompt",
        rules_meta=rules_meta,
    )
    assert dep in suggestions.dependencies
    assert dep not in suggestions.required
    assert dep not in suggestions.optional


def test_required_dep_without_evidence_auto_demotes_to_optional_was_dep() -> None:
    """A ``required:`` Depends with no own evidence is auto-demoted (was_dep)."""
    parent = "rules/parent-req.md"
    dep = "rules/dep-req.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(parent, triggers=("kw:parentword",), depends_required=(dep,)),
        dep: _meta(dep, triggers=("kw:depword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep),
        prompt="parentword only; the dep keyword is absent",
        rules_meta=rules_meta,
    )
    assert dep in suggestions.optional
    assert dep in suggestions.auto_demoted
    assert dep in suggestions.auto_demoted_was_dep
    assert dep not in suggestions.dependencies


def test_optional_dep_with_evidence_stays_in_required_not_dependencies() -> None:
    """An ``optional:`` Depends with its own evidence does NOT collapse to dependencies.

    This is the load-bearing behavioral difference vs ``required:``: optional
    deps are not considered transitive dependencies of the parent, so a loaded
    optional dep with its own trigger evidence stands on its own merit and
    remains in ``required``.

    Note: parent declares ``required:`` foundation so that the classifier's
    transitional fallback (``depends_required or depends``) does not kick in
    and treat the entire combined ``depends`` tuple as required.
    """
    parent = "rules/parent-opt.md"
    dep = "rules/dep-opt.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(
            parent,
            triggers=("kw:parentword",),
            depends_required=(FOUNDATION,),
            depends_optional=(dep,),
        ),
        dep: _meta(dep, triggers=("kw:depword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep),
        prompt="parentword and depword in the prompt",
        rules_meta=rules_meta,
    )
    assert dep in suggestions.required
    assert dep not in suggestions.dependencies
    assert dep not in suggestions.optional


def test_optional_dep_without_evidence_auto_demotes_without_was_dep_flag() -> None:
    """An ``optional:`` Depends without evidence auto-demotes but is NOT marked was_dep."""
    parent = "rules/parent-opt.md"
    dep = "rules/dep-opt.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(
            parent,
            triggers=("kw:parentword",),
            depends_required=(FOUNDATION,),
            depends_optional=(dep,),
        ),
        dep: _meta(dep, triggers=("kw:depword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep),
        prompt="parentword only",
        rules_meta=rules_meta,
    )
    assert dep in suggestions.optional
    assert dep in suggestions.auto_demoted
    assert dep not in suggestions.auto_demoted_was_dep
    assert dep not in suggestions.dependencies


def test_mixed_required_and_optional_buckets_in_single_rule() -> None:
    """A parent with both bucket types routes each dep to its correct lane."""
    parent = "rules/parent-mixed.md"
    req_dep = "rules/dep-required.md"
    opt_dep = "rules/dep-optional.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(
            parent,
            triggers=("kw:parentword",),
            depends_required=(req_dep,),
            depends_optional=(opt_dep,),
        ),
        req_dep: _meta(req_dep, triggers=("kw:reqword",)),
        opt_dep: _meta(opt_dep, triggers=("kw:optword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, req_dep, opt_dep),
        prompt="parentword reqword optword all present",
        rules_meta=rules_meta,
    )
    # required-bucket dep with evidence -> classic dependency
    assert req_dep in suggestions.dependencies
    assert req_dep not in suggestions.required
    # optional-bucket dep with evidence -> stays in required, not dependencies
    assert opt_dep in suggestions.required
    assert opt_dep not in suggestions.dependencies


def test_empty_optional_bucket_still_classifies_required_dep() -> None:
    """Rule with only ``required:`` Depends and no ``optional:`` works correctly."""
    parent = "rules/parent-only-required.md"
    dep = "rules/dep.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(parent, triggers=("kw:parentword",), depends_required=(dep,)),
        dep: _meta(dep, triggers=("kw:depword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep),
        prompt="parentword depword",
        rules_meta=rules_meta,
    )
    assert dep in suggestions.dependencies
    assert dep not in suggestions.optional


def test_buckets_sorted_and_deterministic() -> None:
    """Output tuples are sorted and stable across runs."""
    parent = "rules/parent.md"
    dep_a = "rules/aaa.md"
    dep_b = "rules/bbb.md"
    dep_c = "rules/ccc.md"
    rules_meta = {
        FOUNDATION: _foundation_meta(),
        parent: _meta(
            parent,
            triggers=("kw:parentword",),
            depends_required=(dep_b, dep_a),
            depends_optional=(dep_c,),
        ),
        dep_a: _meta(dep_a, triggers=("kw:aword",)),
        dep_b: _meta(dep_b, triggers=("kw:bword",)),
        dep_c: _meta(dep_c, triggers=("kw:cword",)),
    }
    suggestions = build_suggestions(
        loaded=(FOUNDATION, parent, dep_a, dep_b, dep_c),
        prompt="parentword aword bword cword",
        rules_meta=rules_meta,
    )
    assert suggestions.dependencies == tuple(sorted(suggestions.dependencies))
    assert suggestions.required == tuple(sorted(suggestions.required))
    # required-bucket deps in dependencies; optional-bucket dep in required
    assert dep_a in suggestions.dependencies
    assert dep_b in suggestions.dependencies
    assert dep_c in suggestions.required


def test_rule_119_canonical_mixed_bucket_case() -> None:
    """Mirror the canonical fixture: rule 119 has required:100 and optional:103/105.

    When all four are loaded with prompt evidence for each, 100 should be a
    dependency (required: bucket of 119), and 103/105 should be in required
    (optional: bucket has its own evidence).
    """
    r000 = FOUNDATION
    r100 = "rules/100-snowflake-core.md"
    r103 = "rules/103-snowflake-performance-tuning.md"
    r105 = "rules/105-snowflake-cost-governance.md"
    r119 = "rules/119-snowflake-warehouse-management.md"
    rules_meta = {
        r000: _foundation_meta(),
        r100: _meta(r100, triggers=("kw:snowflake",)),
        r103: _meta(r103, triggers=("kw:performance",)),
        r105: _meta(r105, triggers=("kw:cost",)),
        r119: _meta(
            r119,
            triggers=("kw:warehouse",),
            depends_required=(r100,),
            depends_optional=(r103, r105),
        ),
    }
    suggestions = build_suggestions(
        loaded=(r000, r100, r103, r105, r119),
        prompt="warehouse snowflake performance cost tuning",
        rules_meta=rules_meta,
    )
    assert r100 in suggestions.dependencies
    assert r103 in suggestions.required
    assert r105 in suggestions.required
    assert r119 in suggestions.required
