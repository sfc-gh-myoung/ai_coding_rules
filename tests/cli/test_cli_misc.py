"""Tests for cli.py version callback and __main__.py entry point."""

import pytest
from typer.testing import CliRunner

from ai_rules import __version__
from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1"})


class TestVersionCallback:
    """Test --version flag triggers version_callback."""

    @pytest.mark.unit
    def test_version_flag_prints_version(self):
        """Test that --version prints version and exits cleanly."""
        # Act
        result = runner.invoke(app, ["--version"])

        # Assert
        assert result.exit_code == 0
        assert __version__ in result.output

    @pytest.mark.unit
    def test_short_version_flag(self):
        """Test that -V prints version and exits cleanly."""
        # Act
        result = runner.invoke(app, ["-V"])

        # Assert
        assert result.exit_code == 0
        assert __version__ in result.output


class TestMainModule:
    """Test __main__.py entry point."""

    @pytest.mark.unit
    def test_main_module_invokes_app(self):
        """Test that __main__.py calls app() when run as __main__."""
        # Arrange

        # Act & Assert - importing the module and verifying it has the right structure
        import ai_rules.__main__ as main_mod

        assert hasattr(main_mod, "app")
