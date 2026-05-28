"""Determinism test for match_loaded_rules and build_suggestions.

Verifies that calling either function 100x with identical inputs
produces byte-identical output every time.  Any nondeterminism in
set/dict iteration order or random tie-breaks would manifest as a
flake in this test and must be fixed immediately.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_loader_eval.matcher import match_loaded_rules
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata
from ai_rules.rule_loader_eval.suggestions import build_suggestions


def _meta(
    path: str, triggers: tuple[str, ...] = (), depends_required: tuple[str, ...] = ()
) -> RuleMetadata:
    return RuleMetadata(
        path=Path(path),
        triggers=triggers,
        typed_kw=tuple(t[3:] for t in triggers if t.startswith("kw:")),
        depends_required=depends_required,
    )


def _rules_meta() -> dict[str, RuleMetadata]:
    return {
        "rules/999-test-core.md": _meta("rules/999-test-core.md"),
        "rules/100-snowflake-core.md": _meta("rules/100-snowflake-core.md", ("kw:snowflake",)),
        "rules/101-streamlit.md": _meta(
            "rules/101-streamlit.md",
            ("kw:streamlit", "kw:dashboard"),
            depends_required=("rules/100-snowflake-core.md",),
        ),
        "rules/200-python-core.md": _meta("rules/200-python-core.md", ("kw:python",)),
        "rules/206-pytest.md": _meta(
            "rules/206-pytest.md",
            ("kw:pytest", "kw:testing"),
            depends_required=("rules/200-python-core.md",),
        ),
    }


_PROMPT = "Build a Streamlit dashboard on Snowflake with pytest tests"


class TestMatchLoadedRulesDeterminism:
    def test_identical_calls_produce_identical_output(self) -> None:
        rules_meta = _rules_meta()
        loaded = (
            "rules/999-test-core.md",
            "rules/100-snowflake-core.md",
            "rules/101-streamlit.md",
        )
        required = ("rules/999-test-core.md", "rules/100-snowflake-core.md")
        dependencies = ("rules/101-streamlit.md",)

        first = match_loaded_rules(
            loaded=loaded,
            required=required,
            dependencies=dependencies,
            forbidden=(),
            optional=(),
        )
        for _ in range(99):
            result = match_loaded_rules(
                loaded=loaded,
                required=required,
                dependencies=dependencies,
                forbidden=(),
                optional=(),
            )
            assert result == first, f"nondeterminism detected: {result} != {first}"

    def test_with_missing_required_deterministic(self) -> None:
        loaded = ("rules/999-test-core.md",)
        required = ("rules/999-test-core.md", "rules/100-snowflake-core.md")
        first = match_loaded_rules(
            loaded=loaded, required=required, dependencies=(), forbidden=(), optional=()
        )
        for _ in range(49):
            result = match_loaded_rules(
                loaded=loaded, required=required, dependencies=(), forbidden=(), optional=()
            )
            assert result == first


class TestBuildSuggestionsDeterminism:
    def test_identical_calls_produce_identical_output(self) -> None:
        rules_meta = _rules_meta()
        loaded = (
            "rules/999-test-core.md",
            "rules/100-snowflake-core.md",
            "rules/101-streamlit.md",
            "rules/200-python-core.md",
        )
        first = build_suggestions(
            loaded=loaded,
            prompt=_PROMPT,
            rules_meta=rules_meta,
        )
        for _ in range(49):
            result = build_suggestions(
                loaded=loaded,
                prompt=_PROMPT,
                rules_meta=rules_meta,
            )
            assert result == first, "nondeterminism detected in build_suggestions"
