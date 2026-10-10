"""Tests for src/ai_rules/commands/validate_skills.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ai_rules.commands.validate_skills import SkillResult, SkillSchemaValidator

REPO_ROOT = Path(__file__).resolve().parents[1]


def _make_skill(
    tmp_path: Path,
    *,
    frontmatter: str | None = None,
    body: str = "",
    changelog: str | None = None,
    extra_files: dict[str, str] | None = None,
    name: str = "my-skill",
) -> Path:
    """Create a minimal skill directory."""
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    if frontmatter is None:
        frontmatter = (
            "name: my-skill\ndescription: A sufficiently long skill description.\nversion: 1.0.0"
        )
    content = f"---\n{frontmatter}\n---\n\n{body}"
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    if changelog is not None:
        (skill_dir / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    for rel_path, text in (extra_files or {}).items():
        target = skill_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return skill_dir


def _validator() -> SkillSchemaValidator:
    return SkillSchemaValidator(project_root=REPO_ROOT)


class TestFrontmatter:
    def test_valid_frontmatter_passes(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes something.\n\n## Use this skill when\n- Always.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        fm_errors = [e for e in result.errors if e.error_group == "Frontmatter"]
        assert fm_errors == []

    def test_missing_frontmatter_is_critical(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "no-fm"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# No Frontmatter\n\nJust prose.\n")
        result = _validator().validate_skill_dir(skill_dir)
        severities = {e.severity for e in result.errors if e.error_group == "Frontmatter"}
        assert "CRITICAL" in severities

    def test_missing_name_field(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="description: Long enough description here.\nversion: 1.0.0",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        msgs = [e.message for e in result.errors if e.error_group == "Frontmatter"]
        assert any("name" in m.lower() for m in msgs)

    def test_invalid_name_pattern(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="name: My_Skill\ndescription: Long enough description here.\nversion: 1.0.0",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        msgs = [e.message for e in result.errors if e.error_group == "Frontmatter"]
        assert any("name" in m.lower() for m in msgs)

    def test_description_too_short(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="name: my-skill\ndescription: Short.\nversion: 1.0.0",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        msgs = [e.message for e in result.errors if e.error_group == "Frontmatter"]
        assert any("description" in m.lower() for m in msgs)

    def test_version_with_v_prefix_is_invalid(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="name: my-skill\ndescription: Long enough description here.\nversion: v1.0.0",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        msgs = [e.message for e in result.errors if e.error_group == "Frontmatter"]
        assert any("version" in m.lower() for m in msgs)

    def test_version_two_part_is_invalid(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="name: my-skill\ndescription: Long enough description here.\nversion: 1.0",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        msgs = [e.message for e in result.errors if e.error_group == "Frontmatter"]
        assert any("version" in m.lower() for m in msgs)

    def test_valid_three_part_version(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            frontmatter="name: my-skill\ndescription: A sufficiently long skill description.\nversion: 2.3.11",
            body="## Purpose\nSomething.\n\n## Use this skill when\n- x\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        assert not result.has_blocking


class TestMaxLines:
    def test_under_limit_passes(self, tmp_path: Path) -> None:
        body = "## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        size_errors = [e for e in result.errors if e.error_group == "Size"]
        assert size_errors == []

    @staticmethod
    def _skill_with_total_lines(tmp_path: Path, total: int) -> Path:
        """Build a SKILL.md with exactly *total* lines (frontmatter included)."""
        # Frontmatter block is 6 lines; the headings and bullet add 3 more.
        padding = "x\n" * (total - 9)
        body = f"## Purpose\n{padding}## Use this skill when\n- Yes.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        lines = (skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines()
        assert len(lines) == total
        return skill_dir

    def test_250_lines_passes(self, tmp_path: Path) -> None:
        skill_dir = self._skill_with_total_lines(tmp_path, 250)
        result = _validator().validate_skill_dir(skill_dir)
        size_errors = [e for e in result.errors if e.error_group == "Size"]
        assert size_errors == []

    def test_251_lines_fails(self, tmp_path: Path) -> None:
        skill_dir = self._skill_with_total_lines(tmp_path, 251)
        result = _validator().validate_skill_dir(skill_dir)
        size_errors = [e for e in result.errors if e.error_group == "Size"]
        assert size_errors, "Expected Size error for oversized SKILL.md"
        assert size_errors[0].severity == "HIGH"
        assert "250" in size_errors[0].message


class TestRequiredHeadings:
    def test_canonical_headings_present(self, tmp_path: Path) -> None:
        body = "## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        heading_errors = [e for e in result.errors if e.error_group == "Structure"]
        assert heading_errors == []

    def test_when_to_use_alias_accepted(self, tmp_path: Path) -> None:
        body = "## Purpose\nDoes things.\n\n## When to Use\n- Yes.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        heading_errors = [e for e in result.errors if e.error_group == "Structure"]
        assert heading_errors == []

    def test_missing_purpose_fails(self, tmp_path: Path) -> None:
        body = "## Use this skill when\n- Yes.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        heading_errors = [e for e in result.errors if e.error_group == "Structure"]
        assert any("purpose" in e.message.lower() for e in heading_errors)

    def test_missing_when_section_fails(self, tmp_path: Path) -> None:
        body = "## Purpose\nDoes things.\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        heading_errors = [e for e in result.errors if e.error_group == "Structure"]
        assert any("when" in e.message.lower() for e in heading_errors)

    def test_headings_inside_code_fence_ignored(self, tmp_path: Path) -> None:
        lines_body = [
            "## Purpose",
            "Does things.",
            "",
            "## Use this skill when",
            "- Yes.",
            "",
            "```markdown",
            "## FakeSection",
            "```",
        ]
        body = "\n".join(lines_body) + "\n"
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        heading_errors = [e for e in result.errors if e.error_group == "Structure"]
        assert heading_errors == []


class TestLocalFileRefs:
    def test_existing_relative_link_passes(self, tmp_path: Path) -> None:
        body = (
            "## Purpose\nDoes things.\n\n"
            "## Use this skill when\n- Yes.\n\n"
            "See [workflow](workflows/step1.md) for details.\n"
        )
        skill_dir = _make_skill(
            tmp_path, body=body, extra_files={"workflows/step1.md": "# Step 1\n"}
        )
        result = _validator().validate_skill_dir(skill_dir)
        link_errors = [e for e in result.errors if e.error_group == "Links"]
        assert link_errors == []

    def test_missing_relative_link_fails(self, tmp_path: Path) -> None:
        body = (
            "## Purpose\nDoes things.\n\n"
            "## Use this skill when\n- Yes.\n\n"
            "See [workflow](workflows/missing.md) for details.\n"
        )
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        link_errors = [e for e in result.errors if e.error_group == "Links"]
        assert link_errors, "Expected a Links error for missing file"
        assert "missing.md" in link_errors[0].message

    def test_http_links_not_checked(self, tmp_path: Path) -> None:
        body = (
            "## Purpose\nDoes things.\n\n"
            "## Use this skill when\n- Yes.\n\n"
            "See [external](https://example.com) for more.\n"
        )
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        link_errors = [e for e in result.errors if e.error_group == "Links"]
        assert link_errors == []

    def test_anchor_links_not_checked(self, tmp_path: Path) -> None:
        body = (
            "## Purpose\nDoes things.\n\n"
            "## Use this skill when\n- Yes.\n\n"
            "Go to [section](#purpose).\n"
        )
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        link_errors = [e for e in result.errors if e.error_group == "Links"]
        assert link_errors == []

    def test_no_crash_on_code_fenced_links(self, tmp_path: Path) -> None:
        body = (
            "## Purpose\nDoes things.\n\n"
            "## Use this skill when\n- Yes.\n\n"
            "```\n[missing](workflows/ghost.md)\n```\n"
        )
        skill_dir = _make_skill(tmp_path, body=body)
        result = _validator().validate_skill_dir(skill_dir)
        assert isinstance(result, SkillResult)


class TestChangelogParity:
    def test_matching_versions_pass(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
            changelog="# CHANGELOG\n\n## 1.0.0\n\n- Initial release.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors == []

    def test_mismatched_versions_fail(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
            changelog="# CHANGELOG\n\n## 2.0.0\n\n- Big update.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors, "Expected Changelog error for version mismatch"
        assert cl_errors[0].severity == "HIGH"

    def test_no_changelog_skips_check(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors == []

    def test_changelog_with_v_prefix_matches(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
            changelog="# CHANGELOG\n\n## v1.0.0\n\n- Initial release.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors == []

    def test_changelog_bracket_notation_matches(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
            changelog="# CHANGELOG\n\n## [1.0.0] - 2026-01-01\n\n- Initial.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors == []

    def test_changelog_no_semver_entry_fails(self, tmp_path: Path) -> None:
        skill_dir = _make_skill(
            tmp_path,
            body="## Purpose\nDoes things.\n\n## Use this skill when\n- Yes.\n",
            changelog="# CHANGELOG\n\nNo versions yet.\n",
        )
        result = _validator().validate_skill_dir(skill_dir)
        cl_errors = [e for e in result.errors if e.error_group == "Changelog"]
        assert cl_errors, "Expected Changelog error when CHANGELOG has no version entry"


class TestDirectoryScan:
    def test_real_skills_have_no_blocking_errors(self) -> None:
        skills_root = REPO_ROOT / "skills"
        if not skills_root.exists():
            pytest.skip("skills/ directory not found")
        validator = SkillSchemaValidator(project_root=REPO_ROOT)
        failed: list[str] = []
        for skill_dir in sorted(skills_root.iterdir()):
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
                continue
            result = validator.validate_skill_dir(skill_dir)
            if result.has_blocking:
                blocking = [
                    e.format_brief() for e in result.errors if e.severity in ("CRITICAL", "HIGH")
                ]
                failed.append(f"{skill_dir.name}: {blocking}")
        assert failed == [], "Existing skills have structural validation failures:\n" + "\n".join(
            failed
        )

    def test_validator_handles_missing_skill_md(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty-skill"
        empty_dir.mkdir()
        result = _validator().validate_skill_dir(empty_dir)
        assert result.has_blocking
        assert any(e.error_group == "File" for e in result.errors)


class TestSchemaLoading:
    def test_default_schema_loads_from_repo(self) -> None:
        validator = SkillSchemaValidator(project_root=REPO_ROOT)
        assert "frontmatter" in validator.schema
        assert "structure" in validator.schema

    def test_missing_schema_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            SkillSchemaValidator(
                schema_path=tmp_path / "nonexistent.yml",
                project_root=REPO_ROOT,
            )

    def test_skill_schema_yml_is_valid_yaml(self) -> None:
        schema_path = REPO_ROOT / "schemas" / "skill-schema.yml"
        data = yaml.safe_load(schema_path.read_text())
        assert isinstance(data, dict)
        assert data.get("version") is not None
