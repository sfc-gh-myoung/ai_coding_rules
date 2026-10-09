"""Centralized live-agent defaults for all rule-loader commands and library helpers.

Defaults bumped 2026-05-17 from (low / 15) to (medium / 25) after baseline
A/B characterisation showed the SDK stopped reasoning early at low effort,
producing ~14% per-fixture pass-rate flake. Medium effort + 25 turns
empirically narrows the variance band.
"""

DEFAULT_MAX_TURNS = 25
DEFAULT_EFFORT = "medium"
