"""Focused tests for src/ai_rules/artifact_io.py (C17 safe-write requirements).

Coverage:
  - Path containment: escaping paths are rejected before any write.
  - No-overwrite byte preservation: existing content unchanged when replace=False.
  - Atomic write semantics: temp file staged, fsynced, then os.replace.
  - Pair publication: Markdown published first, JSON last; orphan boundary.
  - Orphan Markdown discovery: is_orphan_markdown / discover_accepted_json.
  - Error class distinctions: ArtifactIOError vs ArtifactDefectError.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_rules.artifact_io import (
    ArtifactDefectError,
    ArtifactIOError,
    atomic_write_json,
    atomic_write_text,
    check_containment,
    discover_accepted_json,
    is_orphan_markdown,
    publish_pair,
)

# ---------------------------------------------------------------------------
# check_containment
# ---------------------------------------------------------------------------


class TestCheckContainment:
    def test_direct_child_is_allowed(self, tmp_path: Path) -> None:
        check_containment(tmp_path / "output.json", tmp_path)

    def test_nested_child_is_allowed(self, tmp_path: Path) -> None:
        check_containment(tmp_path / "a" / "b" / "output.json", tmp_path)

    def test_sibling_directory_is_rejected(self, tmp_path: Path) -> None:
        sibling = tmp_path.parent / "other"
        with pytest.raises(ArtifactDefectError, match="escapes output root"):
            check_containment(sibling / "output.json", tmp_path)

    def test_traversal_via_dotdot_is_rejected(self, tmp_path: Path) -> None:
        escape = tmp_path / ".." / "escape.json"
        with pytest.raises(ArtifactDefectError, match="escapes output root"):
            check_containment(escape, tmp_path)

    def test_root_itself_as_path_is_allowed(self, tmp_path: Path) -> None:
        # A path equal to root (file named as root's name in parent) is out
        # of root; path equal to root/something is in root.
        check_containment(tmp_path / "x", tmp_path)

    def test_absolute_escape_is_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactDefectError):
            check_containment(Path("/etc/passwd"), tmp_path)

    def test_error_is_defect_not_io(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactDefectError):
            check_containment(tmp_path.parent / "escape", tmp_path)
        # Must NOT be an ArtifactIOError
        try:
            check_containment(tmp_path.parent / "escape", tmp_path)
        except ArtifactDefectError:
            pass
        except ArtifactIOError:
            pytest.fail("Containment error must be ArtifactDefectError, not ArtifactIOError")


# ---------------------------------------------------------------------------
# atomic_write_text -- overwrite refusal / byte preservation
# ---------------------------------------------------------------------------


class TestAtomicWriteTextOverwrite:
    def test_output_root_rejects_escaping_path(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactDefectError, match="escapes output root"):
            atomic_write_text(tmp_path.parent / "escape.txt", "data", output_root=tmp_path)

    def test_new_file_is_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        atomic_write_text(dest, "hello")
        assert dest.read_text(encoding="utf-8") == "hello"

    def test_overwrite_refused_by_default(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        dest.write_text("original", encoding="utf-8")
        with pytest.raises(ArtifactDefectError, match="Overwrite refused"):
            atomic_write_text(dest, "new content")

    def test_existing_bytes_unchanged_after_refusal(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        original = "precious bytes"
        dest.write_text(original, encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            atomic_write_text(dest, "something else")
        assert dest.read_text(encoding="utf-8") == original

    def test_replace_true_overwrites(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        dest.write_text("old", encoding="utf-8")
        atomic_write_text(dest, "new", replace=True)
        assert dest.read_text(encoding="utf-8") == "new"

    def test_overwrite_refusal_is_defect_not_io(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        dest.write_text("x", encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            atomic_write_text(dest, "y")


# ---------------------------------------------------------------------------
# atomic_write_text -- atomic staging semantics
# ---------------------------------------------------------------------------


class TestAtomicWriteTextStagingSemantics:
    def test_no_temp_file_left_on_success(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        atomic_write_text(dest, "data")
        temps = list(tmp_path.glob("*.tmp"))
        assert temps == [], f"Stale temp files found: {temps}"

    def test_no_temp_file_left_on_os_replace_failure(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        with patch("os.replace", side_effect=OSError("simulated")):
            with pytest.raises(ArtifactIOError):
                atomic_write_text(dest, "data")
        temps = list(tmp_path.glob("*.tmp"))
        assert temps == [], f"Stale temp files found: {temps}"

    def test_final_content_matches_input(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        content = "line1\nline2\n"
        atomic_write_text(dest, content)
        assert dest.read_text(encoding="utf-8") == content

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "a" / "b" / "c" / "out.txt"
        atomic_write_text(dest, "deep")
        assert dest.exists()

    def test_io_error_on_replace_failure_is_io_error_class(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        with patch("os.replace", side_effect=OSError("disk full")):
            with pytest.raises(ArtifactIOError, match="Atomic write failed"):
                atomic_write_text(dest, "data")


# ---------------------------------------------------------------------------
# atomic_write_json
# ---------------------------------------------------------------------------


class TestAtomicWriteJson:
    def test_writes_valid_json(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        atomic_write_json(dest, {"key": "value", "n": 42})
        doc = json.loads(dest.read_text(encoding="utf-8"))
        assert doc == {"key": "value", "n": 42}

    def test_output_is_pretty_printed(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        atomic_write_json(dest, {"b": 2, "a": 1})
        text = dest.read_text(encoding="utf-8")
        assert text.endswith("\n")
        parsed = json.loads(text)
        assert parsed == {"a": 1, "b": 2}

    def test_keys_are_sorted(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        atomic_write_json(dest, {"z": 3, "a": 1, "m": 2})
        text = dest.read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ":" in ln]
        keys_in_order = [ln.strip().split(":")[0].strip('"') for ln in lines]
        assert keys_in_order == sorted(keys_in_order)

    def test_overwrite_refused_by_default(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        dest.write_text("{}", encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            atomic_write_json(dest, {"new": True})

    def test_existing_bytes_preserved_on_refusal(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        original = '{"original": true}\n'
        dest.write_text(original, encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            atomic_write_json(dest, {"overwrite": True})
        assert dest.read_text(encoding="utf-8") == original

    def test_non_serializable_raises_io_error(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        with pytest.raises(ArtifactIOError, match="JSON serialization failed"):
            atomic_write_json(dest, object())

    def test_replace_true_overwrites(self, tmp_path: Path) -> None:
        dest = tmp_path / "result.json"
        atomic_write_json(dest, {"v": 1})
        atomic_write_json(dest, {"v": 2}, replace=True)
        assert json.loads(dest.read_text())["v"] == 2


# ---------------------------------------------------------------------------
# publish_pair -- Markdown-first, JSON-last ordering
# ---------------------------------------------------------------------------


class TestPublishPair:
    def test_output_root_rejects_escaping_json_path(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactDefectError, match="escapes output root"):
            publish_pair(
                tmp_path / "review.md",
                tmp_path.parent / "escape.json",
                "# Report\n",
                {},
                output_root=tmp_path,
            )

    def test_both_files_written(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_pair(md_path, json_path, "# Report\n", {"status": "ok"})
        assert md_path.exists()
        assert json_path.exists()

    def test_md_content_correct(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_pair(md_path, json_path, "## Heading\n", {"v": 1})
        assert md_path.read_text(encoding="utf-8") == "## Heading\n"

    def test_json_content_correct(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_pair(md_path, json_path, "text", {"score": 95})
        doc = json.loads(json_path.read_text(encoding="utf-8"))
        assert doc == {"score": 95}

    def test_overwrite_refused_for_md(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        md_path.write_text("existing md", encoding="utf-8")
        with pytest.raises(ArtifactDefectError, match="Overwrite refused"):
            publish_pair(md_path, json_path, "new md", {})

    def test_overwrite_refused_for_json(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        json_path.write_text("{}", encoding="utf-8")
        with pytest.raises(ArtifactDefectError, match="Overwrite refused"):
            publish_pair(md_path, json_path, "# md", {"new": True})

    def test_existing_md_bytes_preserved_on_refusal(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        original_md = "# Original\n"
        md_path.write_text(original_md, encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            publish_pair(md_path, json_path, "# New\n", {})
        assert md_path.read_text(encoding="utf-8") == original_md

    def test_existing_json_bytes_preserved_on_refusal(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        original_json = '{"original": true}\n'
        json_path.write_text(original_json, encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            publish_pair(md_path, json_path, "# md", {"overwrite": True})
        assert json_path.read_text(encoding="utf-8") == original_json

    def test_replace_true_overwrites_both(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_pair(md_path, json_path, "old md", {"v": 1})
        publish_pair(md_path, json_path, "new md", {"v": 2}, replace=True)
        assert md_path.read_text(encoding="utf-8") == "new md"
        assert json.loads(json_path.read_text())["v"] == 2

    def test_no_temp_files_left_on_success(self, tmp_path: Path) -> None:
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_pair(md_path, json_path, "text", {})
        temps = list(tmp_path.glob("*.tmp"))
        assert temps == []

    def test_no_temp_files_left_when_json_replace_fails(self, tmp_path: Path) -> None:
        """Staging files are cleaned up when os.replace for JSON fails."""
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"

        call_count = 0

        def replace_side_effect(src: str, dst: str) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("simulated json replace failure")
            os.rename(src, dst)

        with patch("os.replace", side_effect=replace_side_effect):
            with pytest.raises(ArtifactIOError):
                publish_pair(md_path, json_path, "text", {})

        temps = list(tmp_path.glob("*.tmp"))
        assert temps == []

    def test_md_published_before_json_ordering(self, tmp_path: Path) -> None:
        """Verify MD is written before JSON by tracking os.replace call order."""
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"
        publish_order: list[str] = []

        original_replace = os.replace

        def tracking_replace(src: str, dst: str) -> None:
            publish_order.append(Path(dst).suffix)
            original_replace(src, dst)

        with patch("os.replace", side_effect=tracking_replace):
            publish_pair(md_path, json_path, "md text", {"json": True})

        assert publish_order == [".md", ".json"], (
            f"Expected ['.md', '.json'] ordering, got {publish_order}"
        )


# ---------------------------------------------------------------------------
# Orphan Markdown discovery boundary
# ---------------------------------------------------------------------------


class TestOrphanMarkdown:
    def test_md_without_json_is_orphan(self, tmp_path: Path) -> None:
        md = tmp_path / "review.md"
        md.write_text("# Report", encoding="utf-8")
        assert is_orphan_markdown(md) is True

    def test_md_with_json_is_not_orphan(self, tmp_path: Path) -> None:
        md = tmp_path / "review.md"
        json_file = tmp_path / "review.json"
        md.write_text("# Report", encoding="utf-8")
        json_file.write_text("{}", encoding="utf-8")
        assert is_orphan_markdown(md) is False

    def test_discover_accepted_json_excludes_orphan_md(self, tmp_path: Path) -> None:
        """discover_accepted_json returns JSON files; orphan MD is not returned."""
        orphan_md = tmp_path / "orphan.md"
        orphan_md.write_text("# Orphan", encoding="utf-8")
        accepted_json = tmp_path / "accepted.json"
        accepted_json.write_text('{"ok": true}', encoding="utf-8")
        accepted_md = tmp_path / "accepted.md"
        accepted_md.write_text("# Accepted", encoding="utf-8")

        result = discover_accepted_json(tmp_path)
        assert result == [accepted_json]

    def test_discover_accepted_json_returns_all_json(self, tmp_path: Path) -> None:
        """All .json files are returned regardless of md sibling presence."""
        j1 = tmp_path / "a.json"
        j2 = tmp_path / "b.json"
        j1.write_text("{}", encoding="utf-8")
        j2.write_text("{}", encoding="utf-8")
        (tmp_path / "a.md").write_text("md", encoding="utf-8")
        # b.json has no companion md; still returned as accepted JSON

        result = discover_accepted_json(tmp_path)
        assert sorted(result) == sorted([j1, j2])

    def test_discover_accepted_json_empty_dir(self, tmp_path: Path) -> None:
        assert discover_accepted_json(tmp_path) == []

    def test_discover_accepted_json_nonexistent_dir_raises_io_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent"
        with pytest.raises(ArtifactIOError, match="Cannot scan directory"):
            discover_accepted_json(missing)

    def test_publish_pair_then_interrupted_leaves_orphan_md(self, tmp_path: Path) -> None:
        """Simulates interrupted publication: MD visible, JSON absent => orphan."""
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"

        call_count = 0

        def replace_side_effect(src: str, dst: str) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                # Simulate crash after MD is published but before JSON replace
                raise OSError("simulated crash")
            os.rename(src, dst)

        with patch("os.replace", side_effect=replace_side_effect):
            with pytest.raises(ArtifactIOError):
                publish_pair(md_path, json_path, "# Report\n", {"v": 1})

        # MD is visible; JSON absent => orphan
        assert md_path.exists()
        assert not json_path.exists()
        assert is_orphan_markdown(md_path) is True

    def test_orphan_md_excluded_from_discover_accepted(self, tmp_path: Path) -> None:
        """After interrupted publication, discover_accepted_json finds no JSON."""
        md_path = tmp_path / "review.md"
        json_path = tmp_path / "review.json"

        call_count = 0

        def replace_side_effect(src: str, dst: str) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("simulated crash")
            os.rename(src, dst)

        with patch("os.replace", side_effect=replace_side_effect):
            with pytest.raises(ArtifactIOError):
                publish_pair(md_path, tmp_path / "review.json", "# md", {"v": 1})

        accepted = discover_accepted_json(tmp_path)
        assert accepted == []


# ---------------------------------------------------------------------------
# Error class distinctions
# ---------------------------------------------------------------------------


class TestErrorClassDistinctions:
    def test_containment_violation_is_defect(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactDefectError):
            check_containment(Path("/etc/hosts"), tmp_path)

    def test_overwrite_refusal_is_defect(self, tmp_path: Path) -> None:
        dest = tmp_path / "f.txt"
        dest.write_text("x", encoding="utf-8")
        with pytest.raises(ArtifactDefectError):
            atomic_write_text(dest, "y")

    def test_os_replace_failure_is_io_error(self, tmp_path: Path) -> None:
        dest = tmp_path / "f.txt"
        with patch("os.replace", side_effect=OSError("disk full")):
            with pytest.raises(ArtifactIOError):
                atomic_write_text(dest, "data")

    def test_json_serialization_failure_is_io_error(self, tmp_path: Path) -> None:
        dest = tmp_path / "f.json"
        with pytest.raises(ArtifactIOError):
            atomic_write_json(dest, {"bad": object()})

    def test_directory_scan_failure_is_io_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope"
        with pytest.raises(ArtifactIOError):
            discover_accepted_json(missing)

    def test_defect_error_is_not_io_error(self, tmp_path: Path) -> None:
        dest = tmp_path / "f.txt"
        dest.write_text("x", encoding="utf-8")
        exc = None
        try:
            atomic_write_text(dest, "y")
        except ArtifactDefectError as e:
            exc = e
        assert exc is not None
        assert not isinstance(exc, ArtifactIOError)

    def test_io_error_is_not_defect_error(self, tmp_path: Path) -> None:
        dest = tmp_path / "f.txt"
        with patch("os.replace", side_effect=OSError("io")):
            exc = None
            try:
                atomic_write_text(dest, "data")
            except ArtifactIOError as e:
                exc = e
            assert exc is not None
            assert not isinstance(exc, ArtifactDefectError)
