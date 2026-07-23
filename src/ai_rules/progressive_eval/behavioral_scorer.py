"""Behavioral compliance scorer for progressive rule loading evaluation.

Evaluates whether model output actually follows rule guidance by checking
artifacts (code, tool calls, diffs) rather than self-reported loading.

Input: A ConversationTranscript containing all turns with role, content,
and SDK tool_calls metadata.

Output: Per-fixture BehavioralScore with pass/fail per check and aggregate.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum


class CheckType(Enum):
    """Types of behavioral compliance checks."""

    OUTPUT_PATTERN = "output_pattern"
    TOOL_CALL_PRESENT = "tool_call_present"
    TOOL_CALL_ABSENT = "tool_call_absent"
    TOOL_CALL_SEQUENCE = "tool_call_sequence"
    OUTPUT_ABSENT = "output_absent"
    TOKEN_BUDGET = "token_budget"


class CheckResult(Enum):
    """Outcome of a single behavioral check."""

    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class BehavioralCheck:
    """One behavioral check specification from a fixture."""

    id: str
    description: str
    rule_source: str
    check_type: CheckType
    pattern: str | None = None
    tool: str | None = None
    threshold: float | None = None

    @classmethod
    def from_dict(cls, d: dict) -> BehavioralCheck:
        return cls(
            id=d["id"],
            description=d["description"],
            rule_source=d["rule_source"],
            check_type=CheckType(d["check_type"]),
            pattern=d.get("pattern"),
            tool=d.get("tool"),
            threshold=d.get("threshold"),
        )


@dataclass(frozen=True)
class CheckOutcome:
    """Result of evaluating one BehavioralCheck."""

    check_id: str
    result: CheckResult
    reason: str


@dataclass(frozen=True)
class Turn:
    """One turn in a conversation transcript."""

    role: str
    content: str
    tool_calls: list[dict] | None = None


@dataclass(frozen=True)
class ConversationTranscript:
    """Full conversation for scoring."""

    fixture_id: str
    turns: tuple[Turn, ...]
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    rule_tokens_loaded: int = 0

    @property
    def assistant_messages(self) -> list[str]:
        return [t.content for t in self.turns if t.role == "assistant"]

    @property
    def final_assistant_message(self) -> str:
        msgs = self.assistant_messages
        return msgs[-1] if msgs else ""

    @property
    def all_tool_calls(self) -> list[dict]:
        calls = []
        for t in self.turns:
            if t.tool_calls:
                calls.extend(t.tool_calls)
        return calls


@dataclass(frozen=True)
class BehavioralScore:
    """Aggregate scoring result for one fixture run."""

    fixture_id: str
    outcomes: tuple[CheckOutcome, ...]
    total_checks: int
    passed_checks: int
    inconclusive_checks: int

    @property
    def score(self) -> float:
        denominator = self.total_checks - self.inconclusive_checks
        if denominator <= 0:
            return 0.0
        return self.passed_checks / denominator

    @property
    def passed(self) -> bool:
        return self.score >= 1.0


def evaluate_check(check: BehavioralCheck, transcript: ConversationTranscript) -> CheckOutcome:
    """Evaluate a single behavioral check against a conversation transcript."""
    if check.check_type == CheckType.OUTPUT_PATTERN:
        return _eval_output_pattern(check, transcript)
    elif check.check_type == CheckType.OUTPUT_ABSENT:
        return _eval_output_absent(check, transcript)
    elif check.check_type == CheckType.TOOL_CALL_PRESENT:
        return _eval_tool_call_present(check, transcript)
    elif check.check_type == CheckType.TOOL_CALL_ABSENT:
        return _eval_tool_call_absent(check, transcript)
    elif check.check_type == CheckType.TOOL_CALL_SEQUENCE:
        return _eval_tool_call_sequence(check, transcript)
    elif check.check_type == CheckType.TOKEN_BUDGET:
        return _eval_token_budget(check, transcript)
    else:
        return CheckOutcome(
            check_id=check.id,
            result=CheckResult.INCONCLUSIVE,
            reason=f"unknown check_type: {check.check_type}",
        )


def score_fixture(
    fixture_id: str,
    checks: list[BehavioralCheck],
    transcript: ConversationTranscript,
) -> BehavioralScore:
    """Score all behavioral checks for one fixture run."""
    outcomes = []
    for check in checks:
        outcomes.append(evaluate_check(check, transcript))

    passed = sum(1 for o in outcomes if o.result == CheckResult.PASS)
    inconclusive = sum(1 for o in outcomes if o.result == CheckResult.INCONCLUSIVE)

    return BehavioralScore(
        fixture_id=fixture_id,
        outcomes=tuple(outcomes),
        total_checks=len(outcomes),
        passed_checks=passed,
        inconclusive_checks=inconclusive,
    )


# ---------------------------------------------------------------------------
# Check evaluators
# ---------------------------------------------------------------------------


def _eval_output_pattern(
    check: BehavioralCheck, transcript: ConversationTranscript
) -> CheckOutcome:
    """Check if a pattern appears in the final assistant message."""
    text = transcript.final_assistant_message
    if not text:
        return CheckOutcome(
            check_id=check.id,
            result=CheckResult.INCONCLUSIVE,
            reason="no assistant message in transcript",
        )
    if check.pattern and re.search(check.pattern, text, re.MULTILINE | re.DOTALL):
        return CheckOutcome(check_id=check.id, result=CheckResult.PASS, reason="pattern matched")
    return CheckOutcome(
        check_id=check.id,
        result=CheckResult.FAIL,
        reason=f"pattern not found: {check.pattern}",
    )


def _eval_output_absent(check: BehavioralCheck, transcript: ConversationTranscript) -> CheckOutcome:
    """Check that a pattern does NOT appear in any assistant message."""
    for msg in transcript.assistant_messages:
        if check.pattern and re.search(check.pattern, msg, re.MULTILINE | re.DOTALL):
            return CheckOutcome(
                check_id=check.id,
                result=CheckResult.FAIL,
                reason=f"forbidden pattern found: {check.pattern}",
            )
    return CheckOutcome(
        check_id=check.id, result=CheckResult.PASS, reason="pattern absent as expected"
    )


def _eval_tool_call_present(
    check: BehavioralCheck, transcript: ConversationTranscript
) -> CheckOutcome:
    """Check if a specific tool was called, optionally with a pattern on its input."""
    tool_calls = transcript.all_tool_calls
    for tc in tool_calls:
        tc_name = tc.get("name", tc.get("tool", ""))
        if tc_name == check.tool:
            if check.pattern:
                input_str = json.dumps(tc.get("input", tc.get("parameters", {})))
                if re.search(check.pattern, input_str):
                    return CheckOutcome(
                        check_id=check.id,
                        result=CheckResult.PASS,
                        reason="tool called with matching input",
                    )
            else:
                return CheckOutcome(
                    check_id=check.id, result=CheckResult.PASS, reason=f"tool {check.tool} called"
                )
    return CheckOutcome(
        check_id=check.id,
        result=CheckResult.FAIL,
        reason=f"tool {check.tool} not found in transcript"
        + (f" with pattern {check.pattern}" if check.pattern else ""),
    )


def _eval_tool_call_absent(
    check: BehavioralCheck, transcript: ConversationTranscript
) -> CheckOutcome:
    """Check that a specific tool was NOT called."""
    tool_calls = transcript.all_tool_calls
    for tc in tool_calls:
        tc_name = tc.get("name", tc.get("tool", ""))
        if tc_name == check.tool:
            if check.pattern:
                input_str = json.dumps(tc.get("input", tc.get("parameters", {})))
                if re.search(check.pattern, input_str):
                    return CheckOutcome(
                        check_id=check.id,
                        result=CheckResult.FAIL,
                        reason=f"forbidden tool {check.tool} was called with matching input",
                    )
            else:
                return CheckOutcome(
                    check_id=check.id,
                    result=CheckResult.FAIL,
                    reason=f"forbidden tool {check.tool} was called",
                )
    return CheckOutcome(
        check_id=check.id, result=CheckResult.PASS, reason="tool not called as expected"
    )


def _eval_tool_call_sequence(
    check: BehavioralCheck, transcript: ConversationTranscript
) -> CheckOutcome:
    """Check that tool calls appear in a specific order (pattern is comma-separated tool names)."""
    if not check.pattern:
        return CheckOutcome(
            check_id=check.id,
            result=CheckResult.INCONCLUSIVE,
            reason="no sequence pattern specified",
        )

    expected_seq = [t.strip() for t in check.pattern.split(",")]
    tool_calls = transcript.all_tool_calls
    call_names = [tc.get("name", tc.get("tool", "")) for tc in tool_calls]

    # Check subsequence (not necessarily contiguous)
    seq_idx = 0
    for name in call_names:
        if seq_idx < len(expected_seq) and name == expected_seq[seq_idx]:
            seq_idx += 1
    if seq_idx == len(expected_seq):
        return CheckOutcome(
            check_id=check.id, result=CheckResult.PASS, reason="tool sequence found in order"
        )
    return CheckOutcome(
        check_id=check.id,
        result=CheckResult.FAIL,
        reason=f"tool sequence not found; expected {expected_seq}, got {call_names[:10]}",
    )


def _eval_token_budget(check: BehavioralCheck, transcript: ConversationTranscript) -> CheckOutcome:
    """Check that token usage is within budget threshold."""
    if check.threshold is None:
        return CheckOutcome(
            check_id=check.id, result=CheckResult.INCONCLUSIVE, reason="no threshold specified"
        )

    actual = transcript.rule_tokens_loaded
    if actual <= check.threshold:
        return CheckOutcome(
            check_id=check.id,
            result=CheckResult.PASS,
            reason=f"rule tokens {actual} ≤ threshold {check.threshold}",
        )
    return CheckOutcome(
        check_id=check.id,
        result=CheckResult.FAIL,
        reason=f"rule tokens {actual} > threshold {check.threshold}",
    )
