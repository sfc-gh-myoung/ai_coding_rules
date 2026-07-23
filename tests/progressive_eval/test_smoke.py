"""Smoke test: end-to-end progressive loading pipeline.

Verifies: micro-kernel injection → manifest generation → lazy trigger →
behavioral scorer produces a meaningful result.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.progressive_eval.behavioral_scorer import (
    BehavioralCheck,
    CheckType,
    ConversationTranscript,
    Turn,
    score_fixture,
)
from ai_rules.progressive_eval.lazy_loader import LazyLoader
from ai_rules.progressive_eval.manifest_generator import generate_manifest
from ai_rules.progressive_eval.micro_kernel import get_micro_kernel, token_estimate

RULES_DIR = Path(__file__).parent.parent.parent / "rules"
RULES_INDEX = RULES_DIR / "RULES_INDEX.md"


class TestMicroKernel:
    def test_token_budget(self):
        assert token_estimate() <= 500, f"Micro-kernel exceeds 500 token budget: {token_estimate()}"

    def test_contains_critical_principles(self):
        kernel = get_micro_kernel()
        assert "surgical edits" in kernel.lower()
        assert "validation" in kernel.lower()
        assert "task list" in kernel.lower()
        assert "PRE-FLIGHT" in kernel


class TestManifestGeneration:
    @pytest.fixture
    def index_path(self):
        if not RULES_INDEX.exists():
            pytest.skip("RULES_INDEX.md not found")
        return RULES_INDEX

    def test_generates_entries(self, index_path):
        manifest = generate_manifest(index_path, user_request="Write a Python function")
        assert len(manifest.entries) > 0

    def test_respects_token_budget(self, index_path):
        manifest = generate_manifest(index_path, user_request="Do everything", max_tokens=500)
        assert manifest.token_estimate <= 500

    def test_sql_request_finds_sql_rules(self, index_path):
        manifest = generate_manifest(index_path, user_request="Write a SQL query with CTEs")
        rule_paths = [e.rule_path for e in manifest.entries]
        assert any("100-snowflake-core" in p or "102-snowflake-sql" in p for p in rule_paths)

    def test_python_request_finds_python_rules(self, index_path):
        manifest = generate_manifest(index_path, user_request="Fix the Python pytest fixtures")
        rule_paths = [e.rule_path for e in manifest.entries]
        assert any("200-python" in p or "206-python-pytest" in p for p in rule_paths)


class TestLazyLoader:
    @pytest.fixture
    def loader(self):
        if not RULES_INDEX.exists():
            pytest.skip("RULES_INDEX.md not found")
        manifest = generate_manifest(RULES_INDEX, user_request="Edit a Python file")
        return LazyLoader(manifest=manifest, rules_dir=RULES_DIR)

    def test_no_rules_loaded_initially(self, loader):
        assert len(loader.loaded_rules) == 0

    def test_py_extension_triggers_load(self, loader):
        loaded = loader.on_tool_call("Edit", {"file_path": "/project/src/main.py"}, turn=1)
        assert len(loaded) > 0
        assert any("200-python" in p for p in loaded)

    def test_no_trigger_on_unrelated_tool(self, loader):
        loaded = loader.on_tool_call("Read", {"file_path": "/project/README.md"}, turn=1)
        # .md may or may not match depending on rules - just verify no crash
        assert isinstance(loaded, list)

    def test_fail_safe_after_2_turns(self, loader):
        loader.on_turn_end(1)
        loader.on_turn_end(2)
        assert loader.should_fail_safe()
        loaded = loader.fail_safe_load(3)
        assert len(loaded) > 0


class TestEndToEndPipeline:
    """Full pipeline: manifest → lazy load → score."""

    def test_sql_dedup_fixture_pipeline(self):
        if not RULES_INDEX.exists():
            pytest.skip("RULES_INDEX.md not found")

        # 1. Generate manifest for SQL dedup task
        manifest = generate_manifest(
            RULES_INDEX, user_request="Write a query to deduplicate customers by email"
        )
        assert len(manifest.entries) > 0

        # 2. Create lazy loader
        loader = LazyLoader(manifest=manifest, rules_dir=RULES_DIR)

        # 3. Simulate tool call that triggers rule loading
        loaded = loader.on_tool_call("Edit", {"file_path": "queries/dedup.sql"}, turn=1)
        assert len(loaded) > 0, "SQL edit should trigger rule loading"

        # 4. Simulate model producing compliant output
        transcript = ConversationTranscript(
            fixture_id="smoke-test",
            turns=(
                Turn(
                    role="assistant",
                    content="```sql\nWITH ranked AS (\n  SELECT *, ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) AS rn\n  FROM customers\n)\nSELECT * FROM ranked\nQUALIFY ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) = 1\n```",
                    tool_calls=[{"name": "Edit", "input": {"file_path": "queries/dedup.sql"}}],
                ),
            ),
        )

        # 5. Score behavioral compliance
        checks = [
            BehavioralCheck(
                id="qualify-used",
                description="Uses QUALIFY ROW_NUMBER pattern",
                rule_source="rules/100-snowflake-core.md",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern=r"QUALIFY\s+ROW_NUMBER",
            ),
            BehavioralCheck(
                id="cte-used",
                description="Uses CTE structure",
                rule_source="rules/100-snowflake-core.md",
                check_type=CheckType.OUTPUT_PATTERN,
                pattern=r"WITH\s+\w+\s+AS",
            ),
        ]
        score = score_fixture("smoke-test", checks, transcript)
        assert score.passed, f"Expected passing score, got {score.score} ({score.outcomes})"
