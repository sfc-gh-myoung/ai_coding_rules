"""Tests for ai_rules._shared.paths module.

Covers find_project_root, get_rules_dir, get_schemas_dir.
"""

from pathlib import Path

import pytest

from ai_rules._shared.paths import find_project_root, get_rules_dir, get_schemas_dir


class TestFindProjectRoot:
    """Test find_project_root walk-up logic."""

    @pytest.mark.unit
    def test_finds_root_from_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test finding project root when pyproject.toml exists in CWD."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        monkeypatch.chdir(tmp_path)

        # Act
        result = find_project_root()

        # Assert
        assert result == tmp_path

    @pytest.mark.unit
    def test_finds_root_from_child_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test walking up from a nested child directory."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        child = tmp_path / "src" / "deep" / "nested"
        child.mkdir(parents=True)
        monkeypatch.chdir(child)

        # Act
        result = find_project_root()

        # Assert
        assert result == tmp_path

    @pytest.mark.unit
    def test_raises_when_no_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test FileNotFoundError when no pyproject.toml exists anywhere."""
        # Arrange - use an isolated temp dir with no pyproject.toml
        isolated = tmp_path / "isolated"
        isolated.mkdir()
        monkeypatch.chdir(isolated)
        # Remove pyproject.toml from all parents (tmp_path won't have one)
        # The walk-up will eventually reach / without finding pyproject.toml

        # Act & Assert
        # This may or may not raise depending on whether /pyproject.toml exists
        # on the test machine. We test the concept: if we monkeypatch Path.cwd
        # to return a path with no pyproject.toml ancestors, it should raise.
        import unittest.mock

        fake_root = Path("/tmp/test_no_pyproject_exists_here")
        with (
            unittest.mock.patch("ai_rules._shared.paths.Path.cwd", return_value=fake_root),
            unittest.mock.patch.object(
                Path,
                "parents",
                new_callable=lambda: property(lambda self: []),
            ),
        ):
            # Simpler approach: just monkeypatch so exists() returns False
            pass

        # Direct approach: mock cwd to a path where no ancestor has pyproject.toml
        with (
            unittest.mock.patch(
                "ai_rules._shared.paths.Path.cwd",
                return_value=Path("/nonexistent/deep/path"),
            ),
            pytest.raises(FileNotFoundError, match="Could not find project root"),
        ):
            find_project_root()


class TestGetRulesDir:
    """Test get_rules_dir function."""

    @pytest.mark.unit
    def test_with_explicit_root(self, tmp_path: Path):
        """Test get_rules_dir with explicit project_root."""
        # Act
        result = get_rules_dir(project_root=tmp_path)

        # Assert
        assert result == tmp_path / "rules"

    @pytest.mark.unit
    def test_without_root_uses_find(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test get_rules_dir without project_root calls find_project_root."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        monkeypatch.chdir(tmp_path)

        # Act
        result = get_rules_dir()

        # Assert
        assert result == tmp_path / "rules"


class TestGetSchemasDir:
    """Test get_schemas_dir function."""

    @pytest.mark.unit
    def test_with_explicit_root(self, tmp_path: Path):
        """Test get_schemas_dir with explicit project_root."""
        # Act
        result = get_schemas_dir(project_root=tmp_path)

        # Assert
        assert result == tmp_path / "schemas"

    @pytest.mark.unit
    def test_without_root_uses_find(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test get_schemas_dir without project_root calls find_project_root."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        monkeypatch.chdir(tmp_path)

        # Act
        result = get_schemas_dir()

        # Assert
        assert result == tmp_path / "schemas"
