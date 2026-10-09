"""Prompt-hygiene tests for the rule-loader eval agent runner.

After the legacy-mode removal, the eval seed prompt must not carry any stale
RULES_INDEX.md or AGENTS.md bootstrap language.
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
    "rules/RULES_INDEX.md",
    "RULES_INDEX.md is the single agent discovery index",
)


def test_seed_prompt_no_legacy_index_refs() -> None:
    """The module-level seed system prompt does not reference the deleted RULES_INDEX.md."""
    prompt = agent_runner._SEED_SYSTEM_PROMPT
    for token in FORBIDDEN:
        assert token not in prompt, f"stale token in seed prompt: {token!r}"
    # Confirm the prompt references the deterministic matcher approach instead
    assert (
        "deterministic matcher" in prompt or "frontmatter" in prompt or "000-global-core" in prompt
    )


def test_agent_runner_source_has_no_stale_index_refs() -> None:
    """No stale dual-index references remain in agent_runner.py."""
    src = Path(inspect.getfile(agent_runner)).read_text()
    for token in FORBIDDEN:
        assert token not in src, f"stale token in agent_runner.py: {token!r}"
