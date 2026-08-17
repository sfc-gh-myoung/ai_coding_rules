"""Version-consistency guard: __init__.__version__ must match pyproject.toml version.

This test acts as a regression guard for the known 3.5.3/3.7.3 drift and the
upcoming 3.8.0 bump.  Two properties are asserted:

1. __version__ == pyproject version  (catches future drift)
2. Both equal the target release "3.8.0" (fails pre-implementation, passes after)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import ai_rules

TARGET_VERSION = "3.8.0"
_PYPROJECT_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def _read_pyproject_version() -> str:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    m = _PYPROJECT_RE.search(text)
    assert m, "Could not find version line in pyproject.toml"
    return m.group(1)


class TestVersionConsistency:
    """__version__ and pyproject.toml version must stay in sync."""

    @pytest.mark.unit
    def test_init_version_matches_pyproject(self):
        """__init__.__version__ must equal pyproject.toml version (no drift)."""
        pyproject_version = _read_pyproject_version()
        assert ai_rules.__version__ == pyproject_version, (
            f"ai_rules.__version__={ai_rules.__version__!r} does not match "
            f"pyproject.toml version={pyproject_version!r}"
        )

    @pytest.mark.unit
    def test_version_is_target(self):
        """Both __version__ and pyproject.toml version must equal 3.8.0."""
        pyproject_version = _read_pyproject_version()
        assert ai_rules.__version__ == TARGET_VERSION, (
            f"ai_rules.__version__={ai_rules.__version__!r} != {TARGET_VERSION!r}"
        )
        assert pyproject_version == TARGET_VERSION, (
            f"pyproject.toml version={pyproject_version!r} != {TARGET_VERSION!r}"
        )

    @pytest.mark.unit
    def test_readme_badge_shows_target_version(self):
        """README.md version badge must reference 3.8.0."""
        readme = Path(__file__).parent.parent / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert f"badge/version-{TARGET_VERSION}" in content, (
            f"README.md badge does not show version {TARGET_VERSION!r}. "
            f"Found: {list(re.findall(r'badge/version-[^ )]+', content))}"
        )
