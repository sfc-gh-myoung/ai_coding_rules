"""Tests for the behavioral compliance scorer."""

from __future__ import annotations

from ai_rules.progressive_eval.behavioral_scorer import (
    BehavioralCheck,
    CheckResult,
    CheckType,
    ConversationTranscript,
    Turn,
    evaluate_check,
    score_fixture,
)


def _make_transcript(
    *,
    assistant_text: str = "",
    tool_calls: list[dict] | None = None,
    rule_tokens: int = 0,
) -> ConversationTranscript:
    turns = []
    if tool_calls:
        turns.append(Turn(role="assistant", content="", tool_calls=tool_calls))
    turns.append(Turn(role="assistant", content=assistant_text))
    return ConversationTranscript(
        fixture_id="test",
        turns=tuple(turns),
        rule_tokens_loaded=rule_tokens,
    )


class TestOutputPattern:
    def test_pattern_match(self):
        check = BehavioralCheck(
            id="test-1",
            description="",
            rule_source="",
            check_type=CheckType.OUTPUT_PATTERN,
            pattern=r"QUALIFY\s+ROW_NUMBER",
        )
        transcript = _make_transcript(assistant_text="SELECT * QUALIFY ROW_NUMBER() OVER ...")
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.PASS

    def test_pattern_no_match(self):
        check = BehavioralCheck(
            id="test-2",
            description="",
            rule_source="",
            check_type=CheckType.OUTPUT_PATTERN,
            pattern=r"QUALIFY\s+ROW_NUMBER",
        )
        transcript = _make_transcript(assistant_text="SELECT * FROM (SELECT *, ROW_NUMBER()...)")
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.FAIL

    def test_empty_transcript(self):
        check = BehavioralCheck(
            id="test-3",
            description="",
            rule_source="",
            check_type=CheckType.OUTPUT_PATTERN,
            pattern="anything",
        )
        transcript = ConversationTranscript(fixture_id="test", turns=())
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.INCONCLUSIVE


class TestToolCallPresent:
    def test_tool_found(self):
        check = BehavioralCheck(
            id="tc-1",
            description="",
            rule_source="",
            check_type=CheckType.TOOL_CALL_PRESENT,
            tool="Bash",
        )
        transcript = _make_transcript(tool_calls=[{"name": "Bash", "input": {"command": "pytest"}}])
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.PASS

    def test_tool_with_pattern(self):
        check = BehavioralCheck(
            id="tc-2",
            description="",
            rule_source="",
            check_type=CheckType.TOOL_CALL_PRESENT,
            tool="Bash",
            pattern="pytest",
        )
        transcript = _make_transcript(
            tool_calls=[{"name": "Bash", "input": {"command": "pytest tests/"}}]
        )
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.PASS

    def test_tool_not_found(self):
        check = BehavioralCheck(
            id="tc-3",
            description="",
            rule_source="",
            check_type=CheckType.TOOL_CALL_PRESENT,
            tool="Bash",
        )
        transcript = _make_transcript(
            tool_calls=[{"name": "Read", "input": {"file_path": "foo.py"}}]
        )
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.FAIL


class TestToolCallSequence:
    def test_sequence_found(self):
        check = BehavioralCheck(
            id="seq-1",
            description="",
            rule_source="",
            check_type=CheckType.TOOL_CALL_SEQUENCE,
            pattern="Read,Edit,Bash",
        )
        transcript = _make_transcript(
            tool_calls=[
                {"name": "Read", "input": {}},
                {"name": "Edit", "input": {}},
                {"name": "Bash", "input": {}},
            ]
        )
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.PASS

    def test_sequence_not_found(self):
        check = BehavioralCheck(
            id="seq-2",
            description="",
            rule_source="",
            check_type=CheckType.TOOL_CALL_SEQUENCE,
            pattern="Edit,Read,Bash",
        )
        transcript = _make_transcript(
            tool_calls=[
                {"name": "Read", "input": {}},
                {"name": "Edit", "input": {}},
                {"name": "Bash", "input": {}},
            ]
        )
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.FAIL


class TestTokenBudget:
    def test_within_budget(self):
        check = BehavioralCheck(
            id="tok-1",
            description="",
            rule_source="",
            check_type=CheckType.TOKEN_BUDGET,
            threshold=15000,
        )
        transcript = _make_transcript(rule_tokens=10000)
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.PASS

    def test_over_budget(self):
        check = BehavioralCheck(
            id="tok-2",
            description="",
            rule_source="",
            check_type=CheckType.TOKEN_BUDGET,
            threshold=15000,
        )
        transcript = _make_transcript(rule_tokens=20000)
        result = evaluate_check(check, transcript)
        assert result.result == CheckResult.FAIL


class TestScoreFixture:
    def test_all_pass(self):
        checks = [
            BehavioralCheck(
                id="c1",
                description="",
                rule_source="",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern="hello",
            ),
            BehavioralCheck(
                id="c2",
                description="",
                rule_source="",
                check_type=CheckType.TOOL_CALL_PRESENT,
                tool="Bash",
            ),
        ]
        transcript = _make_transcript(
            assistant_text="hello world",
            tool_calls=[{"name": "Bash", "input": {}}],
        )
        score = score_fixture("test-fixture", checks, transcript)
        assert score.score == 1.0
        assert score.passed is True

    def test_partial_pass(self):
        checks = [
            BehavioralCheck(
                id="c1",
                description="",
                rule_source="",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern="hello",
            ),
            BehavioralCheck(
                id="c2",
                description="",
                rule_source="",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern="missing",
            ),
        ]
        transcript = _make_transcript(assistant_text="hello world")
        score = score_fixture("test-fixture", checks, transcript)
        assert score.score == 0.5
        assert score.passed is False

    def test_inconclusive_excluded_from_denominator(self):
        checks = [
            BehavioralCheck(
                id="c1",
                description="",
                rule_source="",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern="hello",
            ),
            BehavioralCheck(
                id="c2",
                description="",
                rule_source="",
                check_type=CheckType.TOKEN_BUDGET,
                threshold=None,
            ),
        ]
        transcript = _make_transcript(assistant_text="hello world")
        score = score_fixture("test-fixture", checks, transcript)
        assert score.score == 1.0
        assert score.inconclusive_checks == 1
