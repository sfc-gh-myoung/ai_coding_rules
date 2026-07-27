"""LLM prompt templates and response parsing for keyword generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from ai_rules.commands.rule_loader.keywords.stoplist import STOP_TERMS


@dataclass
class ParseResult:
    """Result of parsing an LLM keyword response."""

    keywords: list[str] = field(default_factory=list)
    rationale_map: dict[str, str] = field(default_factory=dict)


def _parse_keyword_response(text: str, count: int) -> ParseResult:
    """Parse LLM response text into a ParseResult(keywords, rationale_map).

    Accepts two LLM output shapes:

    1. NEW (T4): a JSON array of objects: ``[{"keyword": "...", "rationale": "..."}, ...]``
    2. LEGACY (backward compat): a JSON array of strings, comma-separated list,
       or newline-separated list.

    Args:
        text: Raw LLM response text.
        count: Upper bound on returned keywords.

    Returns:
        ParseResult with keywords and rationale_map.
    """
    text = text.strip()

    # Try JSON array first (both object shape and string shape live here)
    try:
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            if isinstance(parsed, list) and parsed:
                # NEW shape: list of dicts with keyword+rationale
                if all(isinstance(item, dict) and "keyword" in item for item in parsed):
                    keywords: list[str] = []
                    rationale_map: dict[str, str] = {}
                    for item in parsed:
                        kw = str(item.get("keyword", "")).strip()
                        rationale = str(item.get("rationale", "")).strip()
                        if kw:
                            keywords.append(kw)
                            rationale_map[kw] = rationale
                    keywords = keywords[:count]
                    return ParseResult(
                        keywords=keywords,
                        rationale_map={k: rationale_map[k] for k in keywords},
                    )
                # LEGACY shape: list of strings
                if all(isinstance(k, str) for k in parsed):
                    keywords = [k.strip() for k in parsed if k.strip()][:count]
                    return ParseResult(
                        keywords=keywords,
                        rationale_map=dict.fromkeys(keywords, ""),
                    )
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: try comma-separated
    if "," in text:
        keywords = [k.strip().strip('"').strip("'") for k in text.split(",")]
        keywords = [k for k in keywords if k and k.lower() not in STOP_TERMS]
        if keywords:
            keywords = keywords[:count]
            return ParseResult(keywords=keywords, rationale_map=dict.fromkeys(keywords, ""))

    # Fallback: newline-separated (strip bullet markers)
    lines = text.strip().splitlines()
    keywords = []
    for line in lines:
        line = re.sub(r"^[\s\-*\d.]+", "", line).strip().strip('"').strip("'")
        if line and line.lower() not in STOP_TERMS:
            keywords.append(line)
    keywords = keywords[:count]
    return ParseResult(keywords=keywords, rationale_map=dict.fromkeys(keywords, ""))
