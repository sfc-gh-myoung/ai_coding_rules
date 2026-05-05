**Task:** Review all `*.md` rules in the `rules/` directory.  Ensure the rules are conformant with the following design criteria. Provide recommendations for improving each rule.

**Design Priorities (Strictly Enforced):**
- **Priority 1 (CRITICAL):** Agent understanding and execution reliability. All wording must be unambiguous and unequivocal so autonomous non-human agents can consistently and reliably understand and execute directives.
- **Priority 2 (HIGH):** Rule discovery efficacy and determinism.
- **Priority 3 (HIGH):** Context window and token utilization efficiency.
- **Priority 4 (LOW):** Human developer maintainability. Priorities 1, 2 and 3 significantly outweigh Priority 4.

**Requirements:**
1. Recommendations must be universally effective across ALL agents and LLMs (GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot).
2. Recommendations must ensure consistent behavior across all autonomous agents, not just some of them.
