# Cross-Agent Consistency Rubric (5 points)

## Purpose

Measures whether rule content produces consistent interpretation and execution
across ALL major agents (GPT, Claude, Gemini, Cursor, Cline, Claude Code,
Gemini CLI, GitHub Copilot).

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Scoring Criteria

### 10/10 (5 points): Perfect
- 0 agent-specific interpretations required
- All conditionals use explicit if/else with defined outcomes
- All thresholds quantified with exact values
- No features assuming specific tool availability
- No model-specific terminology or capabilities assumed

### 9/10 (4.5 points): Near-Perfect
- 1 minor agent-specific consideration
- 99%+ universal conditionals

### 8/10 (4 points): Excellent
- 2-3 minor agent-specific considerations
- 97-98% universal conditionals

### 7/10 (3.5 points): Good
- 4-5 agent-specific considerations
- 95-96% universal conditionals

### 6/10 (3 points): Acceptable
- 6-8 agent-specific considerations
- 90-94% universal conditionals

### 5/10 (2.5 points): Borderline
- 9-11 agent-specific considerations
- 85-89% universal conditionals

### 4/10 (2 points): Needs Work
- 12-14 agent-specific considerations
- 80-84% universal conditionals

### 3/10 (1.5 points): Poor
- 15-17 agent-specific considerations
- 70-79% universal conditionals

### 2/10 (1 point): Very Poor
- 18-20 agent-specific considerations
- 60-69% universal conditionals

### 1/10 (0.5 points): Inadequate
- 21-25 agent-specific considerations
- 50-59% universal conditionals

### 0/10 (0 points): Not Cross-Agent Compatible
- >25 agent-specific considerations
- <50% universal conditionals

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
- Explicit conditionals with all branches defined
- Quantified thresholds

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

**Expected variance:** ±1 consideration count

**Verification:**
- Use inventory table with line numbers
- Count by category
- Calculate percentage from explicit conditional count
