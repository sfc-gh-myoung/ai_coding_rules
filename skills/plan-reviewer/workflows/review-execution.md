# Review Execution Workflow

## Purpose

Execute the plan review according to the specified mode.

## Mode-Specific Execution

### FULL Mode

1. **Read plan file** completely
2. **Apply PROMPT.md rubric:**
   - Evaluate all 8 dimensions
   - Complete verification tables (Executability Audit, Completeness Audit, Success Criteria Audit)
   - Answer Plan Perspective Checklist
3. **Calculate point score:**
   - Executability: raw × 4 = /20
   - Completeness: raw × 4 = /20
   - Success Criteria: raw × 4 = /20
   - Scope: raw × 3 = /15
   - Dependencies: raw × 2 = /10
   - Decomposition, Context, Risk Awareness: raw × 1 = /5 each
   - Total: /100
4. **Apply Scoring Impact Rules** (algorithmic overrides)
5. **Determine verdict:** EXECUTABLE, NEEDS_REFINEMENT, or NOT_EXECUTABLE
6. **Generate recommendations** prioritized by impact

### COMPARISON Mode

1. **Read all plan files** completely
2. **For each plan:**
   - Execute FULL mode review (all 8 dimensions)
   - Record individual scores
3. **Create comparative analysis:**
   - Side-by-side dimension scores
   - Head-to-head winner per dimension
   - Evidence for each comparison
4. **Declare winner:**
   - Highest total score
   - If tied: prefer plan with higher critical dimension scores
5. **Generate rationale** for recommendation

### META-REVIEW Mode

1. **Read all review files** completely
2. **Extract from each review:**
   - Overall score
   - Critical issues found
   - Dimension-by-dimension scores
3. **Calculate variance metrics:**
   - Score spread (max - min)
   - Issue detection rate per review
   - Verification table completeness
4. **Evaluate each review on META-REVIEW dimensions:**
   - Thoroughness (5 points)
   - Evidence Quality (5 points)
   - Calibration (5 points)
   - Actionability (5 points)
5. **Determine consensus:**
   - Weight reviews by calibration score
   - Calculate weighted average
6. **Identify best review** and explain why

## Verification Table Requirements

### Executability Audit (FULL mode)

Must include:
- All ambiguous phrases found with line numbers
- Proposed fixes for each
- Total count

### Completeness Audit (FULL mode)

Must include:
- Phase-by-phase coverage (Setup, Validation, Cleanup, Error Recovery)
- Percentage with full coverage

### Success Criteria Audit (FULL mode)

Must include:
- Task-by-task criteria presence
- Agent-verifiability assessment
- Percentages

## Quality Checks

Before finalizing:
- [ ] All 8 dimensions scored with justification
- [ ] All verification tables completed
- [ ] Plan Perspective Checklist answered
- [ ] Scoring Impact Rules applied
- [ ] Recommendations include line numbers

## Next Step

Proceed to `file-write.md`.

