"""Unit tests for match_rules.py: scoring algorithm and match_rules."""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import (
    FileContext,
    RuleEntry,
    _score_kw,
    build_manifest,
    match_rules,
)


def _rule(
    filename: str = "test.md",
    kw: list[str] | None = None,
    ext: list[str] | None = None,
    file_pats: list[str] | None = None,
    dir_pats: list[str] | None = None,
    tier: str = "Medium",
    token_budget: int = 1000,
) -> RuleEntry:
    return RuleEntry(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=token_budget,
        depends_required=[],
        depends_optional=[],
        typed_kw=kw or [],
        typed_ext=ext or [],
        file_patterns=file_pats or [],
        dir_patterns=dir_pats or [],
        rule_version="v1.0",
        description="",
        line_count=10,
        last_updated="2026-01-01",
        schema_version="v3.5",
        keywords_raw=[],
    )


# ---------------------------------------------------------------------------
# _score_kw
# ---------------------------------------------------------------------------


class TestScoreKw:
    def test_exact_phrase_match_scores_10(self):
        assert _score_kw("pytest fixtures", "pytest fixtures") == 10

    def test_single_word_into_multiword_rule_scores_5(self):
        """A lone user word inside a multi-word rule keyword is a PARTIAL match.

        It previously scored 10: identical to an exact phrase match: which made
        incidental hits indistinguishable from precise ones and was the dominant
        source of over-matching (generic "deployment" tied with an exact
        "snowcli" hit and displaced the correct rule from the entry cap).
        Scored 5 now, matching the bigram-overlap tier.
        """
        assert _score_kw("pytest", "pytest fixtures") == 5

    def test_multiword_user_token_non_exact_scores_0(self):
        """A multi-word user token (n-gram phrase) scores only on exact equality.

        Partial credit (word-boundary / bigram-overlap / word-level) is reserved
        for single-word tokens so a long contiguous n-gram cannot fuzzily inflate
        unrelated rules. At the system level no signal is lost: ``extract_context``
        emits every sub-n-gram, so the exact bigram token ``"pytest fixtures"`` is
        emitted separately and still exact-matches this rule keyword for 10.
        """
        assert _score_kw("pytest fixtures setup", "pytest fixtures") == 0

    def test_case_insensitive(self):
        assert _score_kw("Streamlit", "streamlit") == 10

    def test_hyphen_normalized(self):
        assert _score_kw("cortex-search", "cortex search") == 10

    def test_underscore_normalized(self):
        assert _score_kw("session_state", "session state") == 10

    def test_multiword_overlap_non_exact_scores_0(self):
        """Bigram overlap no longer scores for multi-word user tokens (exact-only).

        The exact-phrase-scoring decision (Phase 2) removed partial credit for
        multi-word user tokens to stop n-gram inflation. The matching bigram
        ``"test coverage"`` is emitted as its own token by ``extract_context`` and
        would exact-match a rule keyword ``"test coverage"``.
        """
        assert _score_kw("python test coverage", "test coverage report") == 0

    def test_single_word_match_scores_1(self):
        assert _score_kw("snowflake", "snowflake cortex agents") == 1

    def test_short_words_no_match(self):
        assert _score_kw("do", "do something") == 0

    def test_no_match_zero(self):
        assert _score_kw("python", "javascript") == 0


# ---------------------------------------------------------------------------
# match_rules
# ---------------------------------------------------------------------------


class TestMatchRules:
    def test_keyword_match_returns_scored_rules(self):
        rule = _rule("200.md", kw=["streamlit"])
        scored = match_rules(["streamlit"], FileContext(), [rule])
        assert len(scored) == 1
        assert scored[0].rule.filename == "200.md"

    def test_extension_match(self):
        rule = _rule("200.md", ext=[".py"])
        scored = match_rules([], FileContext(extensions=[".py"]), [rule], score_threshold=3)
        assert len(scored) == 1

    def test_below_threshold_excluded(self):
        rule = _rule("200.md", kw=["some long keyword"])
        scored = match_rules(["xyz"], FileContext(), [rule], score_threshold=3)
        assert len(scored) == 0

    def test_sorted_by_score_descending(self):
        r1 = _rule("low.md", kw=["streamlit"])
        r2 = _rule("high.md", kw=["streamlit", "python"])
        scored = match_rules(["streamlit", "python"], FileContext(), [r1, r2])
        assert scored[0].rule.filename == "high.md"

    def test_file_pattern_match(self):
        rule = _rule("200.md", file_pats=["auth.py"])
        scored = match_rules([], FileContext(paths=["src/auth.py"]), [rule])
        assert len(scored) == 1

    def test_dir_pattern_match(self):
        rule = _rule("200.md", dir_pats=["tests"])
        scored = match_rules(
            [], FileContext(paths=["tests/test_foo.py"]), [rule], score_threshold=3
        )
        assert len(scored) == 1

    def test_tier_used_for_tiebreaking(self):
        r_high = _rule("high.md", kw=["python"], tier="High")
        r_low = _rule("low.md", kw=["python"], tier="Low")
        scored = match_rules(["python"], FileContext(), [r_high, r_low])
        assert scored[0].rule.filename == "high.md"
        assert scored[1].rule.filename == "low.md"


# ---------------------------------------------------------------------------
# Phase 1: extraction hygiene + dependency pre-cap (context-bloat controls)
# ---------------------------------------------------------------------------


class TestExtractionHygiene:
    """Trailing sentence punctuation used to destroy the extension signal."""

    def test_trailing_period_does_not_lose_extension(self):
        from ai_rules.match_rules import _extract_from_prompt

        _, ext, paths = _extract_from_prompt("Please review the file\njobs/extract_load.py.")
        assert ".py" in ext, "trailing '.' must not defeat extension detection"
        assert "jobs/extract_load.py" in paths
        assert not any(p.endswith(".") for p in paths)

    def test_trailing_comma_stripped_from_path(self):
        from ai_rules.match_rules import _extract_from_prompt

        _, ext, paths = _extract_from_prompt("Check src/app.sql, then stop.")
        assert ".sql" in ext
        assert "src/app.sql" in paths

    def test_bare_extension_still_detected(self):
        from ai_rules.match_rules import _extract_from_prompt

        _, ext, _ = _extract_from_prompt("Anything with .py files")
        assert ".py" in ext


class TestDependencyPreCap:
    """build_manifest caps direct entries but appends deps uncapped."""

    def test_max_direct_limits_dependency_closure(self):
        from dataclasses import replace

        from ai_rules.match_rules import ScoredRule, resolve_dependencies

        db = {
            "a.md": replace(_rule("a.md"), depends_required=["dep-a.md"]),
            "b.md": replace(_rule("b.md"), depends_required=["dep-b.md"]),
            "dep-a.md": _rule("dep-a.md"),
            "dep-b.md": _rule("dep-b.md"),
        }
        matched = [ScoredRule(rule=db["a.md"], score=10), ScoredRule(rule=db["b.md"], score=9)]

        uncapped, _ = resolve_dependencies(matched, db)
        assert {r.filename for r in uncapped} == {"a.md", "b.md", "dep-a.md", "dep-b.md"}

        # Only the top match survives the cap, so only its dependency should ship.
        capped, _ = resolve_dependencies(matched, db, max_direct=1)
        assert {r.filename for r in capped} == {"a.md", "dep-a.md"}
        assert "dep-b.md" not in {r.filename for r in capped}


class TestMatcherManifestBoundary:
    def test_foundation_is_inserted_when_matches_omit_it(self) -> None:
        """The matcher manifest always starts with the foundation rule."""
        foundation = _rule("000-global-core.md", tier="Critical")
        direct = _rule("200-python-core.md", kw=["python"], tier="High")
        manifest = build_manifest(
            [direct],
            [],
            matched_filenames={direct.filename},
            foundation=foundation,
        )

        assert manifest["load_sequence"][0]["rule_path"] == "rules/000-global-core.md"
        assert manifest["candidate_rules"][0]["rule_path"] == "rules/000-global-core.md"


class TestRemovedIndexReferences:
    def test_active_rule_loader_guidance_uses_matcher_not_deleted_index(self) -> None:
        """Live rule-loader documentation must not route discovery through an index."""
        project_root = Path(__file__).resolve().parents[2]
        active_guidance = (
            project_root / "skills/rule-loader/workflows/activity-matching.md",
            project_root / "skills/rule-loader/workflows/dependency-resolution.md",
            project_root / "skills/rule-loader/examples/python-api.md",
            project_root / "skills/rule-loader/examples/streamlit-dashboard.md",
            project_root / "skills/rule-loader/examples/multi-domain.md",
            project_root / "skills/rule-loader/examples/token-budget-deferral.md",
            project_root / "skills/rule-loader/tests/test-scenarios.md",
            project_root / "rules/002-rule-governance.md",
            project_root / "rules/002n-agent-protocol-reference.md",
        )

        for path in active_guidance:
            content = path.read_text(encoding="utf-8")
            assert "RULES_INDEX.md" not in content, path
            assert "rules/rule frontmatter" not in content, path

        activity_workflow = active_guidance[0].read_text(encoding="utf-8")
        assert "match_rules.py --prompt" in activity_workflow
        assert "--rules-dir rules/" in activity_workflow

    def test_rule_protocol_routes_runtime_discovery_through_hook_or_skill(self) -> None:
        """Normal agent guidance must not tell agents to invoke the matcher directly."""
        project_root = Path(__file__).resolve().parents[2]
        protocol = (project_root / "rules/002n-agent-protocol-reference.md").read_text(
            encoding="utf-8"
        )

        assert "The hook automatically injects a metadata-only manifest" in protocol
        assert "invoke `$rule-loader`" in protocol
        assert "Agents must not invoke it directly during ordinary task execution" in protocol
        assert "[Agent executes: python3 src/ai_rules/match_rules.py" not in protocol
        assert "Run `match_rules.py --prompt" not in protocol
