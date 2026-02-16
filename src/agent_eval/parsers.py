"""Response parsing utilities for extracting scoring fields."""

import re
from typing import Any


def extract_fields(response: str) -> dict[str, Any]:
    """Extract scoring fields from agent response.

    Args:
        response: Raw agent response text.

    Returns:
        Dict containing extracted fields:
            - preflight_present: bool
            - gate1_checked, gate2_checked, gate3_checked: bool
            - gate2_keywords: str
            - mode_declared: bool
            - task_switch_value: str
            - rules_loaded: list[str]
            - foundation_loaded: bool
    """
    fields: dict[str, Any] = {
        "preflight_present": "PRE-FLIGHT:" in response,
        "gate1_checked": "- [x] Gate 1" in response,
        "gate2_checked": "- [x] Gate 2" in response,
        "gate3_checked": "- [x] Gate 3" in response,
        "gate2_keywords": "",
        "mode_declared": bool(re.search(r"MODE:\s*(PLAN|ACT)", response)),
        "task_switch_value": "",
        "rules_loaded": [],
        "foundation_loaded": False,
    }

    gate2_match = re.search(r"Gate 2:.*searched for:\s*(.+?)(?:\n|$)", response)
    if gate2_match:
        fields["gate2_keywords"] = gate2_match.group(1).strip()

    task_switch_match = re.search(r"Task Switch:\s*(.+?)(?:\n|$)", response)
    if task_switch_match:
        fields["task_switch_value"] = task_switch_match.group(1).strip()

    rules_section = re.search(r"## Rules Loaded\n((?:- .+\n?)+)", response, re.MULTILINE)
    if rules_section:
        rules_text = rules_section.group(1)
        fields["rules_loaded"] = re.findall(r"rules/([^\s\)]+)", rules_text)

    fields["foundation_loaded"] = any("000-global-core" in r for r in fields["rules_loaded"])

    return fields


def evaluate_criterion(criterion: str, fields: dict[str, Any], response: str) -> bool:
    """Evaluate a single criterion against extracted fields.

    Args:
        criterion: Criterion string in format "field operator expected_value".
        fields: Extracted fields from response.
        response: Raw response text.

    Returns:
        True if criterion is met, False otherwise.
    """
    parts = criterion.split(maxsplit=2)
    if len(parts) < 2:
        return False

    field_name = parts[0]
    operator = parts[1]
    expected = parts[2] if len(parts) > 2 else ""

    if field_name == "response":
        actual: Any = response.lower()
        expected = expected.lower()
    elif field_name in fields:
        actual = fields[field_name]
    else:
        return False

    result = False
    if operator == "equals":
        if isinstance(actual, bool):
            result = actual == (expected.lower() == "true")
        else:
            result = str(actual).lower() == expected.lower()
    elif operator == "contains":
        if isinstance(actual, list):
            result = any(expected.lower() in item.lower() for item in actual)
        else:
            result = expected.lower() in str(actual).lower()
    elif operator == "not_contains":
        if expected.lower() == "empty":
            result = bool(actual)
        elif isinstance(actual, list):
            result = not any(expected.lower() in item.lower() for item in actual)
        else:
            result = expected.lower() not in str(actual).lower()
    elif operator == "matches":
        result = bool(re.search(expected, str(actual), re.IGNORECASE))
    elif operator == "true":
        result = actual is True
    elif operator == "false":
        result = actual is False

    return result


def score_response(test_case: dict[str, Any], response: str) -> dict[str, Any]:
    """Score an agent response against test case criteria.

    Args:
        test_case: Test case definition with criteria.
        response: Agent response to score.

    Returns:
        Result dict with test_id, result (PASS/FAIL), score, and criteria_results.
    """
    fields = extract_fields(response)
    criteria = test_case.get("criteria", [])
    pass_threshold = test_case.get("pass_threshold", 100)

    criteria_results = []
    met_count = 0

    for criterion in criteria:
        met = evaluate_criterion(criterion, fields, response)
        criteria_results.append({"criterion": criterion, "met": met})
        if met:
            met_count += 1

    max_score = len(criteria)
    score_percent = (met_count / max_score * 100) if max_score > 0 else 0
    result = "PASS" if score_percent >= pass_threshold else "FAIL"

    return {
        "test_id": test_case["test_id"],
        "name": test_case["name"],
        "category": test_case["category"],
        "priority": test_case["priority"],
        "result": result,
        "score": met_count,
        "max_score": max_score,
        "score_percent": round(score_percent, 1),
        "criteria_results": criteria_results,
    }
