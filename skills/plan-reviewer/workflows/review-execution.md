# Review Execution Workflow

## Purpose

Execute plan review per specified mode using progressive rubric loading.

## Mode-Specific Execution

### FULL Mode

**Steps:**

1. **Read plan file** completely

2. **Score dimensions** (progressive loading - read rubric only when scoring):

   **Critical dimensions (75 points):**
   
   - **Executability (20 points):**
     - Read `../rubrics/executability.md`
     - Count ambiguous phrases
     - Verify explicit commands
     - Check conditional completeness
   
   - **Completeness (20 points):**
     - Read `../rubrics/completeness.md`
     - Check setup, validation, error recovery, cleanup
     - Verify edge case coverage
   
   - **Success Criteria (20 points):**
     - Read `../rubrics/success-criteria.md`
     - Verify measurable, agent-testable criteria
     - Check completion signals
   
   - **Scope (15 points):**
     - Read `../rubrics/scope.md`
     - Check boundaries, termination conditions
     - Verify in-scope/out-of-scope sections

   **Standard dimensions (25 points):**
   
   - **Dependencies (10 points):**
     - Read `../rubrics/dependencies.md`
     - Check tool versions, access requirements
     - Verify ordering dependencies
   
   - **Decomposition (5 points):**
     - Read `../rubrics/decomposition.md`
     - Check task sizing (30-120 min)
     - Identify parallelization opportunities
   
   - **Context (5 points):**
     - Read `../rubrics/context.md`
     - Check rationale, assumptions, tradeoffs
   
   - **Risk Awareness (5 points):**
     - Read `../rubrics/risk-awareness.md`
     - Check failure scenarios, mitigations, rollback

3. **Agent Execution Test** (pre-scoring gate):
   - Count blocking issues (see `../rubrics/executability.md`)
   - If ≥10: Cap total score at 60/100
   - If ≥20: Cap total score at 40/100

4. **Calculate total score:**
   ```
   Total = (Executability × 4) + (Completeness × 4) + (Success Criteria × 4)
         + (Scope × 3) + (Dependencies × 2)
         + (Decomposition × 1) + (Context × 1) + (Risk Awareness × 1)
   Max = 100 points
   ```

5. **Apply critical dimension overrides:**
   - Executability ≤2/5 → Minimum NEEDS_WORK
   - Completeness ≤2/5 → Minimum NEEDS_WORK
   - Success Criteria ≤2/5 → Minimum NEEDS_WORK
   - 2+ critical dimensions ≤2/5 → POOR_PLAN

6. **Determine verdict:**
- **90-100** - Verdict: EXCELLENT_PLAN, Meaning: Ready for execution
- **80-89** - Verdict: GOOD_PLAN, Meaning: Minor refinements needed
- **60-79** - Verdict: NEEDS_WORK, Meaning: Significant refinement required
- **40-59** - Verdict: POOR_PLAN, Meaning: Not executable, major revision
- **<40** - Verdict: INADEQUATE_PLAN, Meaning: Rewrite from scratch

7. **Generate recommendations** with specific examples

---

### COMPARISON Mode

**Steps:**

1. **Read all plan files** completely

2. **For each plan:**
   - Execute FULL mode review (all 8 dimensions)
   - Record individual scores and recommendations

3. **Create comparative analysis:**
   - Build side-by-side dimension comparison table
   - Declare winner per dimension with evidence
   - Calculate total scores

4. **Declare overall winner:**
   - Highest total score wins
   - If tied: Prefer plan with higher critical dimension scores

5. **Generate integration recommendations:**
   - Identify best elements from each plan
   - Suggest combining strengths

6. **Format output:**
   - Individual plan summaries
   - Comparison table
   - Winner declaration with rationale
   - Integration recommendations

---

### META-REVIEW Mode

**Steps:**

1. **Read all review files** completely

2. **Extract from each review:**
   - Overall score
   - Dimension-by-dimension scores
   - Verdict
   - Critical issues found
   - Model used

3. **Calculate variance metrics:**
   ```python
   import statistics
   
   scores = [review.total_score for review in reviews]
   mean_score = statistics.mean(scores)
   stdev_score = statistics.stdev(scores)
   variance = statistics.variance(scores)
   ```

4. **Identify agreement/disagreement:**
   - Dimensions with high agreement (stdev <5)
   - Dimensions with high disagreement (stdev >10)
   - Verdict consensus (all agree?)

5. **Analyze patterns:**
   - Which model is strictest?
   - Which dimensions have most variance?
   - Are there systematic biases?

6. **Format output:**
   - Score distribution table
   - Variance analysis
   - Agreement/disagreement breakdown
   - Patterns and insights
   - Recommendations for plan improvement

---

## Progressive Disclosure

**Key principle:** Only read rubric files when scoring that dimension.

**Don't:**
-  Read all rubrics upfront
-  Load unused rubrics in FOCUSED/STALENESS modes

**Do:**
-  Read rubric immediately before scoring dimension
-  Apply rubric criteria to plan content
-  Move to next dimension

---

## Error Handling

**If plan file missing:**
- Error: "Plan file not found: [path]"
- Abort review

**If rubric file missing:**
- Error: "Rubric not found: [path]"
- Cannot score dimension
- Abort review

**If multiple plans in FULL mode:**
- Error: "FULL mode requires single plan, use COMPARISON for multiple"
- Abort review

**If review files invalid in META-REVIEW:**
- Warning: "Skipping invalid review: [path]"
- Continue with valid reviews

---

## Output

Returns populated review structure ready for file write:
- Metadata section
- Executive summary
- Score breakdown
- Dimension-by-dimension analysis
- Recommendations
- Verdict
