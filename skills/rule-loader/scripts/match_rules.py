#!/usr/bin/env python3
"""Trampoline — delegates to src/ai_rules/match_rules.py for standalone/hook use."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from ai_rules.match_rules import main

if __name__ == "__main__":
    sys.exit(main())
