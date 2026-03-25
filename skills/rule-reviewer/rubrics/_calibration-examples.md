# Calibration Examples

Reference examples for borderline classification decisions. Consult these BEFORE finalizing inventory counts.

## Actionability Calibration

### Example A: Ambiguous Documentation Update
**Source:** "Update relevant documentation" (no criteria for "relevant")
**Classification:** Ambiguous action — **1 blocking issue**
**Rationale:** Agent cannot determine which files to update; "relevant" has no criteria
**Correct fix:** "Update README.md for public API changes, CHANGELOG.md for user-visible behavior, docstrings for modified functions"

### Example B: Defined Synonym
**Source:** "minimal changes" where line N defines "Surgical Editing Principle (also referred to as 'minimal changes')"
**Classification:** **Non-Issue** (Pattern 1: Defined Term)
**Rationale:** Explicit cross-reference exists; term is quantified by its definition section

### Example C: Agent Tool Names with Fallback
**Source:** "Use read_file, list_dir, grep to investigate. If tool discovery fails, list available tools and ask user for guidance."
**Classification:** **Non-Issue** (Pattern 9: Standard Agent Tool Operations + Pattern 4: Imperative with Implicit Default)
**Rationale:** (1) read_file/list_dir/grep are universal agent operations, (2) explicit fallback provided

### Example D: Validation Checklist Items
**Source:** "- [ ] Rules loaded section present" / "- [ ] Validation executed" / "- [ ] Minimal edits applied"
**Classification:** **Non-Issue** (Pattern 10: Status Assertion Checklists)
**Rationale:** Checklist gates assert completion state; implicit action is "verify this condition holds"

## Completeness Calibration

### Example E: Concurrency for Workflow Rules
**Source:** Rule governs single-agent workflow execution (e.g., 000-global-core.md)
**Classification:** Concurrency edge cases = **N/A** (Pattern 3: Not Applicable to Domain)
**Rationale:** Single-agent execution model; no multi-user or race condition scenarios
**Denominator adjustment:** Remove /3 concurrency items from edge case denominator

### Example F: Data Anomalies for Non-Data Rules
**Source:** Rule governs agent behavior patterns, not data processing
**Classification:** Data anomalies = **Partially N/A** (Pattern 3)
**Rationale:** Missing fields and format issues may apply (e.g., malformed rule files); duplicates and encoding typically do not
**Denominator adjustment:** Reduce /4 to /2 applicable items

## Cross-Agent Calibration

### Example G: Tool Names — NOT Agent-Specific
**Source:** "Use read_file to inspect" / "edit with old_string/new_string"
**Classification:** **Do NOT count** as agent-specific consideration
**Rationale:** Universal agent operations; all platforms have equivalents (Read/read_file, Edit/edit, etc.)

### Example H: AGENTS.md Bootstrap Assumption
**Source:** "This rule assumes the AGENTS.md bootstrap protocol has been completed" (no fallback)
**Classification:** **1.0 agent-specific consideration** (Conditional gap)
**Rationale:** No fallback if AGENTS.md is unavailable; different agents may handle missing bootstrap differently
