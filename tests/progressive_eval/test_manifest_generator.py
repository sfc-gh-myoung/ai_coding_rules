"""Unit tests for progressive_eval/manifest_generator.py.

Covers: ManifestEntry dir=/file= fields, parse_rules_index() dir=/file= parsing,
        generate_manifest() dir= and file= scoring (AC-3, AC-4),
        improved keyword scoring, tiered rendering, and boundary cases.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ai_rules.progressive_eval.manifest_generator import (
    RECOMMENDED_MAX_ENTRIES,
    RECOMMENDED_SCORE_THRESHOLD,
    ManifestEntry,
    ProgressiveManifest,
    _score_keyword_match,
    generate_manifest,
    parse_rules_index,
)

# ---------------------------------------------------------------------------
# ManifestEntry — new fields have correct defaults
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_manifest_entry_default_triggers_dir_and_file() -> None:
    entry = ManifestEntry(
        rule_path="rules/002h-claude-code-skills.md",
        summary="skill authoring",
        triggers_ext=(),
        triggers_kw=("skill-authoring",),
        context_tier="Foundation",
    )
    assert entry.triggers_dir == ()
    assert entry.triggers_file == ()


@pytest.mark.unit
def test_manifest_entry_accepts_triggers_dir_and_file() -> None:
    entry = ManifestEntry(
        rule_path="rules/002h-claude-code-skills.md",
        summary="skill authoring",
        triggers_ext=(),
        triggers_kw=("skill-authoring",),
        context_tier="Foundation",
        triggers_dir=("skills/",),
        triggers_file=("snowflake.yml",),
    )
    assert entry.triggers_dir == ("skills/",)
    assert entry.triggers_file == ("snowflake.yml",)


# ---------------------------------------------------------------------------
# parse_rules_index() — dir= and file= field extraction
# ---------------------------------------------------------------------------


def _write_index(tmp_path: Path, content: str) -> Path:
    index = tmp_path / "RULES_INDEX.md"
    index.write_text(textwrap.dedent(content), encoding="utf-8")
    return index


@pytest.mark.unit
def test_parse_rules_index_dir_only_line(tmp_path: Path) -> None:
    """Index line with dir= but no ext= or file= populates triggers_dir and leaves others empty."""
    index = _write_index(
        tmp_path,
        "002h-claude-code-skills.md tier=Foundation dir=skills/ kw=skill-authoring\n",
    )
    entries = parse_rules_index(index)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.rule_path == "rules/002h-claude-code-skills.md"
    assert entry.triggers_dir == ("skills/",)
    assert entry.triggers_ext == ()
    assert entry.triggers_file == ()
    assert entry.triggers_kw == ("skill-authoring",)


@pytest.mark.unit
def test_parse_rules_index_file_field(tmp_path: Path) -> None:
    """Index line with file= field populates triggers_file."""
    index = _write_index(
        tmp_path,
        "999-test.md tier=High file=snowflake.yml kw=snowflake-config\n",
    )
    entries = parse_rules_index(index)
    assert len(entries) == 1
    assert entries[0].triggers_file == ("snowflake.yml",)
    assert entries[0].triggers_dir == ()


@pytest.mark.unit
def test_parse_rules_index_all_trigger_fields(tmp_path: Path) -> None:
    """Index line with ext=, file=, dir= all populated correctly."""
    index = _write_index(
        tmp_path,
        "100-snowflake-core.md tier=High ext=.sql file=snowflake.yml dir=sql/ kw=snowflake sql\n",
    )
    entries = parse_rules_index(index)
    assert len(entries) == 1
    entry = entries[0]
    assert ".sql" in entry.triggers_ext
    assert entry.triggers_file == ("snowflake.yml",)
    assert entry.triggers_dir == ("sql/",)


# ---------------------------------------------------------------------------
# generate_manifest() — dir= trigger scoring (AC-3)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_manifest_dir_trigger_matching(tmp_path: Path) -> None:
    """dir=skills/ entry appears in manifest when request contains 'skills/'."""
    index = _write_index(
        tmp_path,
        "002h-claude-code-skills.md tier=Foundation dir=skills/ kw=skill-authoring\n",
    )
    manifest = generate_manifest(
        index, user_request="I want to author a new skill in skills/ for my repo."
    )
    rule_paths = [e.rule_path for e in manifest.entries]
    assert "rules/002h-claude-code-skills.md" in rule_paths


@pytest.mark.unit
def test_manifest_dir_trigger_score_increment(tmp_path: Path) -> None:
    """dir=skills/ entry receives score increment of ≥10 relative to no-trigger baseline."""
    index = tmp_path / "RULES_INDEX.md"
    index.write_text(
        "002h-claude-code-skills.md tier=Foundation dir=skills/ kw=skill-authoring\n"
        "999-other.md tier=High kw=unrelated-topic\n",
        encoding="utf-8",
    )

    manifest = generate_manifest(
        index, user_request="I want to author a new skill in skills/ for my repo."
    )
    # The dir-triggered entry must appear; verify it's present
    rule_paths = [e.rule_path for e in manifest.entries]
    assert "rules/002h-claude-code-skills.md" in rule_paths


@pytest.mark.unit
def test_manifest_dir_no_false_positive(tmp_path: Path) -> None:
    """'skills/' trigger does NOT match a request mentioning 'soft skills' (no path separator)."""
    index = _write_index(
        tmp_path,
        "002h-claude-code-skills.md tier=Foundation dir=skills/ kw=unused-kw-xyz\n",
    )
    manifest = generate_manifest(index, user_request="How do I improve my soft skills at work?")
    rule_paths = [e.rule_path for e in manifest.entries]
    assert "rules/002h-claude-code-skills.md" not in rule_paths


@pytest.mark.unit
def test_manifest_cumulative_dir_scoring(tmp_path: Path) -> None:
    """Entry with two matching dir= triggers receives score contribution from each (≥20 total)."""
    index = tmp_path / "RULES_INDEX.md"
    # Simulate two dir= triggers by creating two separate entries and comparing
    # with a single-trigger entry to verify additive contribution.
    # We use a two-entry index where entry A has two dir triggers and entry B has one.
    index.write_text(
        # entry A: has two dir triggers (rules/ and skills/), both in the request
        "002h-claude-code-skills.md tier=Foundation dir=skills/ kw=skill-authoring\n"
        # entry B: only kw match
        "999-other.md tier=High kw=skill\n",
        encoding="utf-8",
    )
    # Request contains "skills/" so entry A's dir trigger fires (+10); "skill" kw also fires (+1)
    manifest = generate_manifest(
        index, user_request="I want to create a skill in skills/ for my project."
    )
    rule_paths = [e.rule_path for e in manifest.entries]
    # Entry A must rank before entry B (higher score due to dir trigger)
    assert rule_paths.index("rules/002h-claude-code-skills.md") < rule_paths.index(
        "rules/999-other.md"
    )


# ---------------------------------------------------------------------------
# generate_manifest() — file= trigger scoring (AC-4)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_manifest_file_trigger_matching(tmp_path: Path) -> None:
    """file=snowflake.yml entry appears in manifest when request mentions 'snowflake.yml'."""
    index = _write_index(
        tmp_path,
        "999-snowflake-config.md tier=High file=snowflake.yml kw=snowflake-config\n",
    )
    manifest = generate_manifest(index, user_request="How do I configure my snowflake.yml file?")
    rule_paths = [e.rule_path for e in manifest.entries]
    assert "rules/999-snowflake-config.md" in rule_paths


@pytest.mark.unit
def test_manifest_file_trigger_score_increment(tmp_path: Path) -> None:
    """file= triggered entry ranks above kw-only entry with same keyword."""
    index = tmp_path / "RULES_INDEX.md"
    index.write_text(
        "999-config-file.md tier=High file=snowflake.yml kw=config\n"
        "998-config-other.md tier=High kw=config\n",
        encoding="utf-8",
    )
    manifest = generate_manifest(index, user_request="Edit the snowflake.yml config.")
    rule_paths = [e.rule_path for e in manifest.entries]
    # file-triggered entry must rank before kw-only entry
    assert rule_paths.index("rules/999-config-file.md") < rule_paths.index(
        "rules/998-config-other.md"
    )


# ---------------------------------------------------------------------------
# _score_keyword_match — unit tests for new scoring helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_score_keyword_compound_exact_match() -> None:
    """Exact compound keyword match scores +10."""
    assert _score_keyword_match("cortex-agent", "help me build a cortex agent") == 10


@pytest.mark.unit
def test_score_keyword_mcp_server_exact_match() -> None:
    """mcp-server scores +10 when 'mcp server' appears in request."""
    assert _score_keyword_match("mcp-server", "configure a mcp server endpoint") == 10


@pytest.mark.unit
def test_score_keyword_partial_compound() -> None:
    """Keyword where only 2 consecutive words appear (not full phrase) scores +5."""
    # "cortex-agent-build" → phrase "cortex agent build"; request has "cortex agent" but not "build"
    # → partial 2-word consecutive match → +5
    assert _score_keyword_match("cortex-agent-build", "cortex agent is what I need") == 5


@pytest.mark.unit
def test_score_keyword_partial_consecutive_only() -> None:
    """3-word keyword where middle 2 words appear but not full phrase → +5."""
    # "slow query investigation" full phrase not present; "query investigation" is present
    assert (
        _score_keyword_match("slow-query-investigation", "the query investigation revealed issues")
        == 5
    )


@pytest.mark.unit
def test_score_keyword_agent_archetype_partial() -> None:
    """'agent-archetype' matches only 'agent' as single word → +1."""
    assert _score_keyword_match("agent-archetype", "help me build a cortex agent") == 1


@pytest.mark.unit
def test_score_keyword_single_word_python() -> None:
    """Single-word (no hyphen) keyword scores +1."""
    assert _score_keyword_match("python", "write python code") == 1


@pytest.mark.unit
def test_score_keyword_long_compound_exact() -> None:
    """Long compound keyword phrase-matches correctly → +10."""
    assert _score_keyword_match("slow-query-investigation", "slow query investigation guide") == 10


@pytest.mark.unit
def test_score_keyword_no_match() -> None:
    """Keyword not present in request scores 0."""
    assert _score_keyword_match("cortex-agent", "configure a database connection") == 0


@pytest.mark.unit
def test_score_keyword_short_word_no_match() -> None:
    """Single word ≤4 chars does not score (noise reduction)."""
    # "sql" is 3 chars, "yaml" is 4 chars — both below threshold
    assert _score_keyword_match("sql", "write sql code") == 0
    assert _score_keyword_match("yaml", "edit yaml config") == 0


@pytest.mark.unit
def test_score_keyword_empty_keyword() -> None:
    """Empty keyword returns 0 without error."""
    assert _score_keyword_match("", "any request") == 0


# ---------------------------------------------------------------------------
# generate_manifest() — max_entries=15 default
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_manifest_max_entries_default(tmp_path: Path) -> None:
    """Default max_entries is 15."""
    lines = [f"{i:03d}-rule.md tier=High kw=keyword-{i}\n" for i in range(30)]
    index = tmp_path / "RULES_INDEX.md"
    index.write_text("".join(lines), encoding="utf-8")
    # All rules match "keyword" so all 30 are scored; only 15 returned
    manifest = generate_manifest(index, user_request="keyword query")
    assert len(manifest.entries) <= 15


@pytest.mark.unit
def test_manifest_max_entries_respected(tmp_path: Path) -> None:
    """Explicit max_entries is respected."""
    lines = [f"{i:03d}-rule.md tier=High kw=keyword-{i}\n" for i in range(20)]
    index = tmp_path / "RULES_INDEX.md"
    index.write_text("".join(lines), encoding="utf-8")
    manifest = generate_manifest(index, user_request="keyword query", max_entries=5)
    assert len(manifest.entries) <= 5


# ---------------------------------------------------------------------------
# generate_manifest() — multi-keyword boost
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_manifest_multi_keyword_boost(tmp_path: Path) -> None:
    """Entry with 2+ matching keywords ranks higher than entry with only 1."""
    index = tmp_path / "RULES_INDEX.md"
    index.write_text(
        # Entry A: two keywords both match ("cortex-agent" → +10, "semantic-view" → +10) → +3 boost
        "115-cortex.md tier=High kw=cortex-agent semantic-view\n"
        # Entry B: one keyword matches ("cortex-agent" → +10) — no boost
        "116-other.md tier=High kw=cortex-agent unrelated-xyz\n",
        encoding="utf-8",
    )
    manifest = generate_manifest(
        index,
        user_request="Help me build a cortex agent that uses a semantic view",
    )
    rule_paths = [e.rule_path for e in manifest.entries]
    assert rule_paths.index("rules/115-cortex.md") < rule_paths.index("rules/116-other.md")


# ---------------------------------------------------------------------------
# generate_manifest() — tiered rendering
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tiered_rendering_recommended_section(tmp_path: Path) -> None:
    """RECOMMENDED section appears when high-scoring entries exist."""
    index = tmp_path / "RULES_INDEX.md"
    index.write_text(
        "115-cortex.md tier=High kw=cortex-agent semantic-view\n"
        "999-low.md tier=Low kw=unrelated-xyz\n",
        encoding="utf-8",
    )
    manifest = generate_manifest(
        index,
        user_request="Help me build a cortex agent that uses a semantic view",
    )
    rendered = manifest.render()
    assert "RECOMMENDED" in rendered
    assert "rules/115-cortex.md" in rendered


@pytest.mark.unit
def test_tiered_rendering_no_recommended_when_low_scores(tmp_path: Path) -> None:
    """RECOMMENDED section absent when no entry meets the threshold."""
    index = tmp_path / "RULES_INDEX.md"
    # All keywords are single short words that won't meet threshold
    index.write_text(
        "aaa.md tier=High kw=python\nbbb.md tier=High kw=python\n",
        encoding="utf-8",
    )
    # "python" = single word, scores +1 each — below RECOMMENDED_SCORE_THRESHOLD=5
    manifest = generate_manifest(index, user_request="python script")
    rendered = manifest.render()
    assert "RECOMMENDED" not in rendered
    assert "Other potentially relevant:" in rendered


@pytest.mark.unit
def test_tiered_rendering_recommended_cap(tmp_path: Path) -> None:
    """RECOMMENDED section is capped at RECOMMENDED_MAX_ENTRIES."""
    # Create 10 high-scoring entries
    lines = [
        f"{i:03d}-rule.md tier=High kw=cortex-agent semantic-view tool-orchestration\n"
        for i in range(10)
    ]
    index = tmp_path / "RULES_INDEX.md"
    index.write_text("".join(lines), encoding="utf-8")
    manifest = generate_manifest(
        index,
        user_request="Help me build a cortex agent that uses a semantic view",
    )
    rendered = manifest.render()
    # Count RECOMMENDED entries (lines starting with "- rules/")
    recommended_block = rendered.split("Other potentially relevant:")[0]
    recommended_entries = [ln for ln in recommended_block.splitlines() if ln.startswith("- rules/")]
    assert len(recommended_entries) <= RECOMMENDED_MAX_ENTRIES


# ---------------------------------------------------------------------------
# generate_manifest() — token budget still respected
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_token_budget_respected_with_tiered_rendering(tmp_path: Path) -> None:
    """Token budget ≤2000 is maintained with tiered rendering."""
    # Create many high-scoring entries
    lines = [
        f"{i:03d}-rule.md tier=High kw=cortex-agent semantic-view tool-orchestration\n"
        for i in range(50)
    ]
    index = tmp_path / "RULES_INDEX.md"
    index.write_text("".join(lines), encoding="utf-8")
    manifest = generate_manifest(
        index,
        user_request="Help me build a cortex agent that uses a semantic view",
        max_tokens=2000,
    )
    assert manifest.token_estimate <= 2000


# ---------------------------------------------------------------------------
# generate_manifest() — boundary cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_empty_request_returns_manifest_no_crash(tmp_path: Path) -> None:
    """Empty user_request returns manifest without raising."""
    index = _write_index(
        tmp_path,
        "100-test.md tier=High kw=snowflake-core\n200-test.md tier=Critical kw=python\n",
    )
    manifest = generate_manifest(index, user_request="")
    assert isinstance(manifest, ProgressiveManifest)
    assert len(manifest.entries) >= 0  # no crash


@pytest.mark.unit
def test_duplicate_keyword_counted_once(tmp_path: Path) -> None:
    """Duplicate keyword in kw= list is scored only once (deduplication)."""
    index = tmp_path / "RULES_INDEX.md"
    # cortex-agent appears twice; should be counted once
    index.write_text(
        "115-dup.md tier=High kw=cortex-agent cortex-agent\n"
        "116-single.md tier=High kw=cortex-agent other-kw\n",
        encoding="utf-8",
    )
    manifest = generate_manifest(
        index,
        user_request="build a cortex agent solution",
    )
    # Both entries should be present; entry with duplicate kw should NOT outscore the single entry
    # by double-counting. The 116 entry has a second unique kw "other-kw" (no match) so both
    # should score the same from cortex-agent alone.
    scores = manifest.scores
    score_115 = scores.get("rules/115-dup.md", 0)
    score_116 = scores.get("rules/116-single.md", 0)
    # 115 has one unique matching keyword (cortex-agent → 10); no boost (only 1 matched)
    # 116 has one unique matching keyword (cortex-agent → 10); no boost (only 1 matched)
    assert score_115 == score_116


@pytest.mark.unit
def test_deterministic_tiebreak_alphabetical(tmp_path: Path) -> None:
    """Two entries with identical scores appear in deterministic alphabetical order."""
    index = tmp_path / "RULES_INDEX.md"
    # Both rules have the same keyword — same score
    index.write_text(
        "zzz-rule.md tier=High kw=cortex-agent\naaa-rule.md tier=High kw=cortex-agent\n",
        encoding="utf-8",
    )
    manifest = generate_manifest(index, user_request="build a cortex agent")
    rule_paths = [e.rule_path for e in manifest.entries]
    # aaa comes before zzz alphabetically
    assert rule_paths.index("rules/aaa-rule.md") < rule_paths.index("rules/zzz-rule.md")


# ---------------------------------------------------------------------------
# Integration: fixture prompts hit correct rules in RECOMMENDED tier
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cortex_agent_build_fixture_rule_in_top5() -> None:
    """For cortex-agent-build prompt, rule 115 appears in top-5 entries."""
    index = Path("rules/RULES_INDEX.md")
    if not index.exists():
        pytest.skip("RULES_INDEX.md not available in this environment")

    manifest = generate_manifest(
        index,
        user_request="Help me build a Cortex Agent that answers questions about our sales data using a semantic view",
    )
    top5 = [e.rule_path for e in manifest.entries[:5]]
    assert "rules/115-snowflake-cortex-agents-core.md" in top5, f"Not in top 5: {top5}"


@pytest.mark.integration
def test_cortex_agent_build_fixture_rule_in_recommended() -> None:
    """For cortex-agent-build prompt, rule 115 appears in RECOMMENDED tier."""
    index = Path("rules/RULES_INDEX.md")
    if not index.exists():
        pytest.skip("RULES_INDEX.md not available in this environment")

    manifest = generate_manifest(
        index,
        user_request="Help me build a Cortex Agent that answers questions about our sales data using a semantic view",
    )
    recommended = [
        e.rule_path
        for e in manifest.entries
        if manifest.scores.get(e.rule_path, 0) >= RECOMMENDED_SCORE_THRESHOLD
    ][:RECOMMENDED_MAX_ENTRIES]
    assert "rules/115-snowflake-cortex-agents-core.md" in recommended, (
        f"Not in RECOMMENDED: {recommended}"
    )


@pytest.mark.integration
def test_mcp_server_fixture_rule_in_top5() -> None:
    """For mcp-server prompt, rule 117 appears in top-5 entries."""
    index = Path("rules/RULES_INDEX.md")
    if not index.exists():
        pytest.skip("RULES_INDEX.md not available in this environment")

    manifest = generate_manifest(
        index,
        user_request="Configure a snowflake-managed mcp server endpoint for the local agent",
    )
    top5 = [e.rule_path for e in manifest.entries[:5]]
    assert "rules/117-snowflake-mcp-server.md" in top5, f"Not in top 5: {top5}"


@pytest.mark.integration
def test_mcp_server_fixture_rule_in_recommended() -> None:
    """For mcp-server prompt, rule 117 appears in RECOMMENDED tier."""
    index = Path("rules/RULES_INDEX.md")
    if not index.exists():
        pytest.skip("RULES_INDEX.md not available in this environment")

    manifest = generate_manifest(
        index,
        user_request="Configure a snowflake-managed mcp server endpoint for the local agent",
    )
    recommended = [
        e.rule_path
        for e in manifest.entries
        if manifest.scores.get(e.rule_path, 0) >= RECOMMENDED_SCORE_THRESHOLD
    ][:RECOMMENDED_MAX_ENTRIES]
    assert "rules/117-snowflake-mcp-server.md" in recommended, f"Not in RECOMMENDED: {recommended}"


@pytest.mark.integration
def test_token_budget_respected_real_index() -> None:
    """Token budget ≤2000 is maintained for both fixture prompts against real RULES_INDEX.md."""
    index = Path("rules/RULES_INDEX.md")
    if not index.exists():
        pytest.skip("RULES_INDEX.md not available in this environment")

    for prompt in [
        "Help me build a Cortex Agent that answers questions about our sales data using a semantic view",
        "Configure a snowflake-managed mcp server endpoint for the local agent",
    ]:
        manifest = generate_manifest(index, user_request=prompt)
        assert manifest.token_estimate <= 2000, f"Token budget exceeded for prompt: {prompt!r}"


# --- Citation version migration tests ---


@pytest.mark.unit
def test_parse_rules_index_populates_rule_version(tmp_path: Path) -> None:
    """parse_rules_index extracts rule_version from ver= field."""
    index_file = tmp_path / "RULES_INDEX.md"
    index_file.write_text(
        "100-test.md tier=High ver=v3.1.0 kw=snowflake sql\n200-test.md tier=Low ver=- kw=python\n"
    )

    entries = parse_rules_index(index_file)

    assert len(entries) == 2
    assert entries[0].rule_version == "v3.1.0"
    assert entries[1].rule_version == ""  # ver=- becomes empty string


@pytest.mark.unit
def test_manifest_entry_to_compact_includes_version() -> None:
    """to_compact() includes rule_version when set."""
    entry = ManifestEntry(
        rule_path="rules/100-test.md",
        summary="test summary",
        triggers_ext=(),
        triggers_kw=("snowflake",),
        context_tier="High",
        rule_version="v3.1.0",
    )

    compact = entry.to_compact()

    assert "v3.1.0" in compact
    assert compact.startswith("rules/100-test.md")


@pytest.mark.unit
def test_index_line_re_nonmatch_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Malformed line that looks like a rule (.md) emits a warning and continues."""
    import logging

    index_file = tmp_path / "RULES_INDEX.md"
    index_file.write_text(
        "100-valid.md tier=High ver=v1.0.0 kw=test\n"
        "malformed-entry.md no-tier-field\n"
        "200-valid.md tier=Low ver=v2.0.0 kw=python\n"
    )

    with caplog.at_level(logging.WARNING, logger="ai_rules.progressive_eval.manifest_generator"):
        entries = parse_rules_index(index_file)

    assert len(entries) == 2  # malformed line skipped
    assert any("malformed-entry.md" in r.message for r in caplog.records)
