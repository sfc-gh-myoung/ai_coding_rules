# Cross-Agent Consistency Rubric (5 points)

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

> **Why inventories are required:** Eliminates counting variance (same rule → same inventory → same score), prevents false negatives, provides auditable evidence, enables verification.

### Inventory Template

**Agent-Specific Considerations:**

| Line | Issue Type | Description | Weight |
|------|------------|-------------|--------|
| 45 | Tool assumption | "Use Claude's file search" | 1.0 |
| 67 | Conditional gap | "if large table" (no else) | 1.0 |
| 89 | Capability assumption | "context window allows" | 1.0 |
| 110 | Soft assumption | Assumes read_file tool | 0.5 |

**Conditional Completeness:**

| Line | Conditional | Has Else/Default? |
|------|-------------|-------------------|
| 45 | if error_occurs | Y/N |
| 67 | when file_large | Y/N |
| 89 | if timeout | Y/N |

**Summary:**

| Metric | Count |
|--------|-------|
| Total conditionals | NN |
| Conditionals with explicit else/default | NN |
| Universal conditional % | NN% |

### Counting Protocol

> **Standard 5-Step Counting Protocol:**
> 1. **Create Empty Inventory** — Copy template above into working document. Do NOT start reading rule yet.
> 2. **Read Rule Systematically** — Start at line 1, read to END (no skipping). Record all matches with line numbers.
> 3. **Calculate Raw Totals** — Sum counts by category using dimension-specific definitions.
> 4. **Check Non-Issues List** — Review EACH flagged item against this dimension's Non-Issues section. Remove false positives with note. Recalculate totals.
> 5. **Look Up Score** — Use adjusted totals in Score Decision Matrix. Record score with inventory evidence.
>
> **Inter-run consistency:** Use inventory tables with line numbers for evidence. If variance exceeds threshold documented below, re-count using checklists and document ambiguous cases.
>
> **Dimension-specific:** Count agent-specific considerations (1.0 or 0.5 each), count conditionals with/without explicit else, calculate universal conditional %. Use lower of consideration count tier OR universal % tier.

## Purpose

Measures whether rule content produces consistent interpretation and execution
across ALL major agents (GPT, Claude, Gemini, Cursor, Cline, Claude Code,
Gemini CLI, GitHub Copilot).

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Score Decision Matrix

**Score Tier Criteria (use lower of two factors):**
- **10/10 (5 pts):** 0 considerations, 99%+ universal conditionals
- **9/10 (4.5 pts):** 1 consideration, 99%+ universal conditionals
- **8/10 (4 pts):** 2-3 considerations, 97-98% universal conditionals
- **7/10 (3.5 pts):** 4-5 considerations, 95-96% universal conditionals
- **6/10 (3 pts):** 6-8 considerations, 90-94% universal conditionals
- **5/10 (2.5 pts):** 9-11 considerations, 85-89% universal conditionals
- **4/10 (2 pts):** 12-14 considerations, 80-84% universal conditionals
- **3/10 (1.5 pts):** 15-17 considerations, 70-79% universal conditionals
- **2/10 (1 pt):** 18-20 considerations, 60-69% universal conditionals
- **1/10 (0.5 pts):** 21-25 considerations, 50-59% universal conditionals
- **0/10 (0 pts):** >25 considerations OR <50% universal conditionals

**Tie-Breaking Rules:**
1. If consideration count and universal % suggest different tiers: Use LOWER tier
2. If on boundary (e.g., exactly 5 considerations): Use HIGHER tier
3. If 0.5-weight issues create fractional total: Round to nearest integer

## What Counts as Agent-Specific Consideration

### Count 1.0 each:

**Tool Assumptions:**
- References tool only available in specific agent (e.g., "use Claude's artifacts")
- Assumes MCP server availability without fallback
- References IDE-specific features without alternative

**Capability Assumptions:**
- Assumes specific context window size
- Assumes multimodal capabilities
- Assumes code execution environment
- References agent-specific memory/persistence

**Terminology Issues:**
- Uses model-specific jargon (e.g., "constitutional AI" for Claude-specific behavior)
- References specific model versions without generalization

**Conditional Gaps:**
- if/when without else (agents may default differently)
- Implicit defaults (different agents assume different defaults)

### Count 0.5 each:

**Soft Assumptions:**
- Terminology that most but not all agents understand
- Features available in most agents but not guaranteed
- Ordering preferences that may vary by agent

### Do NOT Count:

- Universal programming concepts
- Standard tool references (git, npm, pytest, etc.)
- Standard agent tool operations (read_file/Read, edit/Edit, list_dir/Glob, grep/Grep, search — these are universal operations with platform-specific names)
- Explicit conditionals with all branches defined
- Quantified thresholds
- Issues already assigned to Actionability via overlap resolution Rule 2 (do not double-count)

## Worked Example

**Target:** Rule with cross-agent issues

### Step 1: Identify Agent-Specific Considerations

```
Line 45: "Use Claude's file search" - Tool assumption (1.0)
Line 67: "if large table" (no else) - Conditional gap (1.0)
Line 89: "context window allows" - Capability assumption (1.0)
Line 110: Assumes read_file tool exists - Soft assumption (0.5)
Line 130: "appropriate timeout" undefined - Agents may interpret differently (1.0)
```

### Step 2: Count Issues

**Total:** 4.5 (round to 5)

### Step 3: Calculate Universal Conditional %

```
Total conditionals: 20
Conditionals with explicit else/default: 17
Universal %: 17/20 = 85%
```

### Step 4: Determine Score

- 5 agent-specific considerations → 6-8 range → 6/10
- 85% universal → 85-89% range → 5/10

**Final:** 5/10 (lower of the two) = 2.5 points

### Step 5: Document in Review

```markdown
## Cross-Agent Consistency: 5/10 (2.5 points)

**Agent-specific considerations:** 5
- Line 45: Tool assumption (Claude-specific file search)
- Line 67: Missing else branch
- Line 89: Context window capability assumption
- Line 110: Tool availability assumption (0.5)
- Line 130: Undefined threshold (agent interpretation varies)

**Universal conditionals:** 85% (17/20)

**Priority fixes:**
1. Line 45: Replace with generic "Use available file search tool"
2. Line 67: Add explicit else branch
3. Line 130: Quantify "appropriate timeout" (e.g., ">30 seconds")
```

## Inter-Run Consistency Target

**Expected variance:** ±1 consideration count. Verify using inventory table with line numbers, count by category, calculate percentage from explicit conditional count.

## Non-Issues (Do NOT Count)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Universal Programming Concepts
**Pattern:** Standard programming/tooling terminology
**Example:** "Use git for version control", "Run pytest"
**Why NOT an issue:** All agents understand standard tools
**Action:** Remove from inventory with note "Universal tool/concept"

### Pattern 2: Explicit Conditionals
**Pattern:** Conditional with all branches defined
**Example:** "If file exists, read it. Otherwise, create it."
**Why NOT an issue:** All branches are explicit
**Action:** Remove from inventory with note "Complete conditional"

### Pattern 3: Quantified Thresholds
**Pattern:** Specific numeric thresholds
**Example:** "For tables >10M rows, use streaming"
**Why NOT an issue:** Threshold is objective, not agent-dependent
**Action:** Remove from inventory with note "Quantified threshold"

### Pattern 4: Fallback Instructions
**Pattern:** Primary method with explicit fallback
**Example:** "Use ruff. If unavailable, use flake8 + black."
**Why NOT an issue:** Fallback covers agents without primary tool
**Action:** Remove from inventory with note "Has fallback"
