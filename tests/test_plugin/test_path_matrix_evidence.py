"""Evidence artifact contract tests for plugin rule-path remediation."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "reports" / "acr-plan-path-matrix"
REQUIRED_HEADERS = ("# Date:", "# Host:", "# Command:", "# Result:")
ACTIVE_EVIDENCE = ("macos.txt", "foreign-workspace-smoke.txt")
OPTIONAL_EVIDENCE = {"linux.txt": "NOT RUN", "windows.txt": "OUT OF SCOPE"}
PLACEHOLDER_TERMS = (
    "placeholder",
    "not yet recorded",
    "replace this content",
    "todo",
)


def _evidence_files() -> list[Path]:
    return sorted(EVIDENCE_DIR.glob("*.txt"))


def test_evidence_files_are_trackable() -> None:
    """Path-matrix evidence must not be ignored by git."""
    files = _evidence_files()
    assert files, f"no evidence files found under {EVIDENCE_DIR}"
    for evidence_file in files:
        result = subprocess.run(
            ["git", "check-ignore", str(evidence_file.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0, f"evidence file is ignored: {evidence_file}"


def test_evidence_files_have_basic_provenance_headers() -> None:
    """Evidence files must include the agreed basic provenance fields."""
    for evidence_file in _evidence_files():
        text = evidence_file.read_text(encoding="utf-8")
        for header in REQUIRED_HEADERS:
            assert header in text, f"{evidence_file} missing {header}"


def test_active_evidence_files_are_final_not_placeholders() -> None:
    """Active evidence files must contain real evidence, not placeholder language."""
    for name in ACTIVE_EVIDENCE:
        evidence_file = EVIDENCE_DIR / name
        assert evidence_file.exists(), f"missing active evidence file: {evidence_file}"
        text = evidence_file.read_text(encoding="utf-8").lower()
        for term in PLACEHOLDER_TERMS:
            assert term not in text, f"{evidence_file} contains placeholder term {term!r}"
        assert "# result: pass" in text, f"{evidence_file} must record PASS result"


def test_optional_scope_files_do_not_claim_pass_without_evidence() -> None:
    """Optional/out-of-scope files may exist but cannot be mistaken for pass evidence."""
    for name, expected_result in OPTIONAL_EVIDENCE.items():
        evidence_file = EVIDENCE_DIR / name
        if not evidence_file.exists():
            continue
        text = evidence_file.read_text(encoding="utf-8")
        assert f"# Result: {expected_result}" in text
