"""Prompt-hygiene tests for the rule-loader eval agent runner.

After the dual-index collapse, the eval seed prompt must reference the single
generated ``rules/RULES_INDEX.md`` and must not carry any stale
dual-index / "human-only" language.
"""

from __future__ import annotations

import inspect
from pathlib import Path

from ai_rules.rule_loader_eval import agent_runner

FORBIDDEN = (
    "RULES_INDEX_COMPACT.md",
    "human-only",
    "human reference only",
    "~4x",
    "Do NOT read RULES_INDEX.md",
)


def test_seed_prompt_uses_single_index() -> None:
    """The module-level seed system prompt points agents at rules/RULES_INDEX.md."""
    prompt = agent_runner._SEED_SYSTEM_PROMPT
    assert "rules/RULES_INDEX.md" in prompt
    for token in FORBIDDEN:
        assert token not in prompt, f"stale token in seed prompt: {token!r}"


def test_agent_runner_source_has_no_stale_index_refs() -> None:
    """No stale dual-index references remain anywhere in agent_runner.py.

    Covers both the module constant and the inline prompt copy in ``run_live``.
    """
    src = Path(inspect.getfile(agent_runner)).read_text()
    assert "rules/RULES_INDEX.md" in src
    for token in FORBIDDEN:
        assert token not in src, f"stale token in agent_runner.py: {token!r}"
