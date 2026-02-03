# Review Execution Workflow

## Purpose

Execute plan review per specified mode using **batch rubric loading** (NOT progressive disclosure).

**Key Change:** Load ALL rubric definitions BEFORE reading plan to prevent interpretation drift.

---

## Phase 1: Load All Rubric Definitions (MANDATORY)

**Purpose:** Lock in scoring criteria interpretation BEFORE reviewing plan. Prevents interpretation drift.

**Duration:** 10-15 minutes (one-time upfront cost)

### Step 1.1: Read Rubric Files in Order

**Read these 9 files completely (do NOT skip to plan yet):**

1. `rubrics/_overlap-resolution.md` (prerequisite for all dimensions)
2. `rubrics/executability.md` (20 points, weight 4)
3. `rubrics/completeness.md` (20 points, weight 4)
4. `rubrics/success-criteria.md` (20 points, weight 4)
5. `rubrics/scope.md` (15 points, weight 3)
6. `rubrics/dependencies.md` (10 points, weight 2)
7. `rubrics/decomposition.md` (5 points, weight 1)
8. `rubrics/context.md` (5 points, weight 1)
9. `rubrics/risk-awareness.md` (5 points, weight 1)

**Why this order:** Critical dimensions (higher weight) read first to prioritize understanding.

### Step 1.2: Extract Key Information

From EACH rubric, extract and record:
- **Pattern definitions:** Exact phrases, regex patterns (from Complete Pattern Inventory when added)
- **Non-Issues list:** What NOT to count (false positive patterns)
- **Worksheet template:** Table structure to fill
- **Counting protocol:** Step-by-step enumeration instructions
- **Score decision matrix:** Raw count/percentage → tier → score mapping
- **Ambiguous case rules:** Resolution rules for borderline cases

**Create reference document (for use during review):**

```markdown
# Rubric Definitions Summary

## Overlap Resolution Rules
[Paste key rules from _overlap-resolution.md]

## Executability
- **Patterns:** 5 categories (conditional qualifiers, vague actions, thresholds, implicit commands, missing branches)
- **Non-Issues:** (See rubric when Phase 2 implemented)
- **Counting:** 5 passes (line 1 to END per category)
- **Scoring:** 0-2→9-10/10, 3-4→8/10, 5-6→7/10, 7-8→6/10, 9-10→5/10, 11-13→4/10, 14-16→3/10, 17-19→2/10, 20-25→1/10, >25→0/10
- **Formula:** Raw × 2 = Points (out of 20)

## Success Criteria
- **Patterns:** Task coverage %, measurable %, agent-testable %
- **Non-Issues:** (See rubric when Phase 2 implemented)
- **Counting:** List all tasks, assess each (Y/N for criteria/measurable/testable), calculate %
- **Scoring:** 100%→10/10, 95-99%→9/10, 90-94%→8/10, 85-89%→7/10, etc.
- **Formula:** Raw × 2 = Points (out of 20)

## Completeness
- **Elements:** Setup (5), Validation (3), Error Recovery (count), Cleanup (4), Edge Cases (12)
- **Scoring:** Based on element coverage per category
- **Formula:** Raw × 2 = Points (out of 20)

## Scope
- **Elements:** 4 boundaries, unbounded phrases count, in/out-of-scope items, termination
- **Scoring:** Based on boundaries + unbounded phrase count
- **Formula:** Raw × 1.5 = Points (out of 15)

## Dependencies
- **Elements:** 5 categories, tool versions %, environment (6 elements)
- **Scoring:** Based on category coverage + completeness
- **Formula:** Raw × 1 = Points (out of 10)

## Decomposition
- **Elements:** Task sizing (in-range %), parallelization, grouping
- **Scoring:** Based on in-range % + parallelization + grouping
- **Formula:** Raw × 0.5 = Points (out of 5)

## Context
- **Elements:** Rationale coverage %, non-obvious explained, assumptions (4 types), tradeoffs
- **Scoring:** Based on rationale % + assumptions + tradeoffs
- **Formula:** Raw × 0.5 = Points (out of 5)

## Risk Awareness
- **Elements:** 4 categories, risk assessment, mitigation %, rollback (4 elements)
- **Scoring:** Based on category coverage + mitigation + rollback
- **Formula:** Raw × 0.5 = Points (out of 5)
```

### Step 1.3: Create All 8 Empty Worksheets

**Prepare worksheets BEFORE reading plan (copy templates from rubrics):**

**1. Executability Worksheet:**
```
| Pass | Line | Quote | Category | Pattern | Note |
|------|------|-------|----------|---------|------|
[Empty - to be filled in Phase 2]
```

**2. Completeness Worksheet:**
```
Setup: [Y/N checklist]
Validation: [Y/N checklist]
Error Recovery: [Y/N checklist]
Cleanup: [Y/N checklist]
Edge Cases: [Count by category]
```

**3. Success Criteria Worksheet:**
```
| Task | Line | Name | Criteria? | Measurable? | Testable? | Verification |
|------|------|------|-----------|-------------|-----------|--------------|
[Empty]
```

**4. Scope Worksheet:**
```
Boundaries: [4 Y/N checks]
In-scope items: [Count]
Out-of-scope items: [Count]
Unbounded phrases: [List with lines]
Termination: [Quality assessment]
```

**5. Dependencies Worksheet:**
```
Categories: [5 Y/N checks]
Tool versions: [Coverage %]
Environment: [6 Y/N checks]
```

**6. Decomposition Worksheet:**
```
Task sizes: [Count by category]
In-range %: [Calculation]
Parallelization: [Assessment]
Grouping: [Assessment]
```

**7. Context Worksheet:**
```
Decisions: [List with rationale Y/N]
Non-obvious values: [List with explanation Y/N]
Assumptions: [4 types Y/N]
Tradeoffs: [Assessment]
```

**8. Risk Awareness Worksheet:**
```
Risks by category: [4 columns]
Assessment completeness: [Per risk]
Mitigation coverage: [%]
Rollback: [4 elements Y/N]
```

### Step 1.4: Verification Checkpoint

**Self-check before proceeding to Phase 2:**
- [ ] All 9 files read completely? (8 rubrics + overlap resolution when available)
- [ ] Pattern definitions extracted for each dimension?
- [ ] Non-Issues lists recorded for each? (when available)
- [ ] All 8 worksheets created (empty templates copied)?
- [ ] Score matrices understood (can look up scores)?
- [ ] Ambiguous case handling clear?
- [ ] Overlap resolution rules understood? (when available)

**If ANY checkbox is NO:**
- Return to Step 1.1
- Re-read files
- Clarify understanding

**GATE:** Do NOT proceed to Phase 2 until ALL checkboxes are YES.

**Why this gate matters:** Proceeding without complete understanding causes interpretation drift, overlapping dimension ownership, and score variance.

---

## Phase 2: Read Plan and Fill All Worksheets

**Purpose:** Systematic enumeration of plan using locked-in rubric definitions.

**Duration:** 30-45 minutes (depending on plan length)

### Step 2.1: Read Plan Completely (No Scoring Yet)

**Instructions:**
1. Read target plan file from line 1 to END
2. Record structure (phases, sections, tasks)
3. Note line numbers for reference
4. Do NOT score yet (just read for familiarity)

**Why read first:** Understanding plan structure helps with contextual checks (e.g., "Is threshold defined elsewhere?")

### Step 2.2: Fill Worksheets Systematically

**For EACH dimension, execute counting protocol from rubric:**

**Executability (5 passes):**
- Pass 1: Scan line 1 to END for conditional qualifiers (Category 1)
- Pass 2: Scan line 1 to END for vague actions (Category 2)
- Pass 3: Scan line 1 to END for undefined thresholds (Category 3)
- Pass 4: Scan line 1 to END for implicit commands (Category 4)
- Pass 5: Scan line 1 to END for missing branches (Category 5)
- Record all matches in worksheet with line numbers

**Success Criteria:**
- List ALL tasks (numbered or inferred, per Task Counting Standard)
- For each task: Assess criteria present? measurable? testable?
- Record verification commands or "human review"

**Scope:**
- Check 4 boundaries (what/how much/when/what NOT)
- Scan line 1 to END for unbounded phrases
- Count in-scope items
- Count out-of-scope items
- Assess termination conditions

**Completeness:**
- Check setup elements (5 items)
- Check validation phases (3 phases)
- Count error recovery scenarios with steps
- Check cleanup elements (4 items)
- Count edge cases addressed (12 items)

**Dependencies:**
- Check 5 categories present
- Count tools with versions
- Check 6 environment elements

**Decomposition:**
- List tasks with duration estimates
- Classify by size category
- Calculate in-range %
- Assess parallelization and grouping

**Context:**
- List key decisions, check rationale
- List non-obvious values, check explanations
- Check 4 assumption types
- Assess tradeoff documentation

**Risk Awareness:**
- List risks, classify into 4 categories
- Check probability/impact for each
- Calculate mitigation coverage %
- Check 4 rollback elements

### Step 2.3: Apply Non-Issues Filters

**For EACH dimension worksheet:**
1. Review EACH flagged item
2. Check against Non-Issues list for that dimension (when implemented)
3. If match found: Remove (mark with ~~strikethrough~~)
4. Add note: "~~Line 83: Implicit (FALSE POSITIVE: verification at line 87)~~"
5. Recalculate totals

**Why this step matters:** Reduces false positive rate by 20-30%, improves score accuracy.

### Step 2.4: Resolve Overlaps

**For items that could belong to multiple dimensions:**
1. Check `_overlap-resolution.md` matrix (when available)
2. Use Blocking Issue Classification Matrix in executability.md
3. Assign to PRIMARY dimension only
4. Note in secondary dimension: "See [Primary] for [issue]"
5. Remove from secondary worksheet (don't count twice)

**Example:**
```
Issue: "Missing else branch after git status check"
Could be: Executability OR Completeness
Check matrix: Executability is primary (blocks execution)
Action: Count in Executability only
Note in Completeness: "See Executability for missing branch issue"
```

---

## Phase 3: Calculate Scores and Generate Review

**Purpose:** Convert completed worksheets into dimension scores and final review document.

**Duration:** 15-20 minutes

### Step 3.1: Calculate Dimension Scores

**For EACH dimension:**
1. Extract totals from worksheet (adjusted after filtering)
2. Look up in Score Decision Matrix from rubric
3. Find tier matching raw count/percentage
4. Record raw score (0-10)
5. Apply tie-breaking rules if on boundary
6. Calculate points: Raw score × weight multiplier
7. Record points / max points

**Example (Executability):**
- Worksheet total (adjusted): 5 blocking issues
- Score matrix lookup: 5-6 tier = 7/10 raw score
- Formula: 7 × 2 = 14 points
- Result: 14/20 points

### Step 3.2: Calculate Overall Score

**Sum weighted points:**
```
Overall Score = Sum of all dimension points

Executability:    [XX]/20
Completeness:     [XX]/20
Success Criteria: [XX]/20
Scope:            [XX]/15
Dependencies:     [XX]/10
Decomposition:    [XX]/5
Context:          [XX]/5
Risk Awareness:   [XX]/5
---
TOTAL:           [XXX]/100
```

### Step 3.3: Apply Critical Dimension Overrides

**Check critical dimensions:**
- Executability ≤4/10 → Minimum NEEDS_WORK
- Completeness ≤4/10 → Minimum NEEDS_WORK
- Success Criteria ≤4/10 → Minimum NEEDS_WORK
- 2+ critical dimensions ≤4/10 → POOR_PLAN

### Step 3.4: Determine Verdict

- **90-100** - Verdict: EXCELLENT_PLAN, Meaning: Ready for execution
- **80-89** - Verdict: GOOD_PLAN, Meaning: Minor refinements needed
- **60-79** - Verdict: NEEDS_WORK, Meaning: Significant refinement required
- **40-59** - Verdict: POOR_PLAN, Meaning: Not executable, major revision
- **<40** - Verdict: INADEQUATE_PLAN, Meaning: Rewrite from scratch

### Step 3.5: Generate Review Document

**Structure:**
1. Executive Summary (score, verdict, key strengths/issues)
2. Score Breakdown Table (dimension | raw | weight | points)
3. For EACH dimension:
   - Assessment paragraph
   - **Completed Worksheet** (REQUIRED)
   - Strengths list (3-5 items)
   - Issues list (with line numbers)
   - Recommendations (Priority 1/2/3)
4. Overall Recommendations
5. Next Steps

**Critical:** ALWAYS include completed worksheets in review output. Required for verification and future comparisons.

### Step 3.6: Quality Check

**Before finalizing review, verify:**
- [ ] All 8 dimension scores calculated?
- [ ] All 8 worksheets included in output?
- [ ] Line numbers referenced for all issues?
- [ ] Overlap resolution rules cited where applicable?
- [ ] Non-Issues patterns referenced for skipped items?
- [ ] Score calculations shown with matrix lookup?
- [ ] Overall score = sum of dimension points?
- [ ] Verdict matches score tier?

**If ANY checkbox is NO:** Review is incomplete, must be fixed before submission.

---

## Mode-Specific Execution

### FULL Mode

Execute Phases 1-3 above for single plan.

### COMPARISON Mode

**Steps:**
1. Execute Phase 1 (load rubrics) ONCE
2. For each plan:
   - Execute Phases 2-3
   - Record individual scores and recommendations
3. Create comparative analysis:
   - Build side-by-side dimension comparison table
   - Declare winner per dimension with evidence
   - Calculate total scores
4. Declare overall winner:
   - Highest total score wins
   - If tied: Prefer plan with higher critical dimension scores
5. Generate integration recommendations

### META-REVIEW Mode

**Steps:**
1. Read all review files completely
2. Extract from each review:
   - Overall score, dimension scores, verdict
   - Critical issues found
   - Model used
3. Calculate variance metrics
4. Identify agreement/disagreement areas
5. Generate consistency analysis

---

## Error Handling

**If plan file missing:**
- Error: "Plan file not found: [path]"
- Abort review

**If rubric file missing:**
- Error: "Rubric not found: [path]"
- Cannot score dimension
- Abort review

**If worksheet incomplete:**
- Error: "Worksheet for [dimension] incomplete"
- Cannot calculate score
- Return to Phase 2

---

## Output

Returns populated review structure ready for file write:
- Metadata section
- Executive summary
- Score breakdown
- Dimension-by-dimension analysis with worksheets
- Recommendations
- Verdict

---

## Exhaustive Enumeration Protocol (MANDATORY)

### Requirements

**For EACH dimension with patterns to match:**

1. **Start-to-End Coverage**
   - Review EVERY line from line 1 to final line
   - No skipping sections
   - No early termination

2. **One Pass Per Pattern**
   - Complete one pattern category before starting next
   - Do not multi-task

3. **Track ALL Matches**
   - Record EVERY pattern match in worksheet
   - Include line number for each
   - Do not rely on memory

4. **Show Your Work**
   - Include completed worksheet in review output

### Anti-Patterns to Avoid

**❌ DON'T:** "I scanned the plan and found approximately 8-10 issues"
**✅ DO:** "I enumerated all lines and found exactly 8 issues (see worksheet)"

**❌ DON'T:** "I reviewed the main sections"
**✅ DO:** "I reviewed lines 1-1513 (complete plan)"

**❌ DON'T:** "I remember seeing several 'as needed' phrases"
**✅ DO:** "Worksheet shows 4 'as needed' phrases: lines 23, 67, 145, 289"

### Enforcement

**Reviews missing evidence of exhaustive enumeration are INVALID:**
- Missing worksheets → INVALID (regenerate review)
- Approximate counts (e.g., "~8 issues") → INVALID (provide exact count)
- No line numbers → INVALID (add line references)

### Worksheet Completeness Verification

**Run after generating review to verify worksheet inclusion:**

```bash
# Verify all 8 dimension worksheets present in review output
REVIEW_FILE="reviews/plan-reviews/[plan]-[date]-[model].md"

# Check for worksheet tables (must return ≥8)
grep -c "| Line |" "$REVIEW_FILE"

# Check for line number references (must return >0 for each dimension)
grep -E "Line [0-9]+" "$REVIEW_FILE" | wc -l

# Verify no approximate counts
grep -E "(approximately|~|about) [0-9]+" "$REVIEW_FILE" && echo "FAIL: Approximate counts found" || echo "PASS"
```

### Verification Gate

**Three checks MUST pass:**
1. `grep -c "| Line |"` MUST return ≥8
2. `grep -E "Line [0-9]+"` MUST return >0
3. Approximate count check MUST return "PASS"

**IF ANY check fails:** Review is INVALID, regenerate with proper enumeration.

### Enumeration Coverage Declaration

**Every review output MUST include:**

```markdown
## Enumeration Coverage

**Plan analyzed:** [filename]
**Lines reviewed:** 1 to [last line number]
**Coverage:** 100% (no sections skipped)

**Passes completed:**
- [ ] Executability Pass 1-5
- [ ] Success Criteria task enumeration
- [ ] Scope boundary check
- [ ] Completeness element check
- [ ] Dependencies category check
- [ ] Decomposition task sizing
- [ ] Context decision inventory
- [ ] Risk Awareness category classification
```

---

## Optional: Post-Review Consistency Check

**When to use:** After generating a review when prior reviews exist for the same plan.

**Purpose:** Detect variance between current and prior reviews to ensure scoring consistency.

### Step 1: Detect Prior Reviews

```bash
# Find existing reviews for this plan
PLAN_NAME="${target_file%.*}"  # Remove extension
ls reviews/plan-reviews/${PLAN_NAME}-${MODEL}-*.md 2>/dev/null | sort
```

**If no prior reviews:** Skip consistency check (first review for this plan).

### Step 2: Load Most Recent Prior Review

**Extract from prior review:**
- Overall score (e.g., 72/100)
- Verdict (e.g., NEEDS_WORK)
- Blocking issues count
- Per-dimension scores (8 values)

### Step 3: Calculate Variance

**Per-dimension variance:**
```
For each dimension:
  delta = abs(current_score - prior_score)
```

**Overall variance:**
```
overall_delta = abs(current_total - prior_total)
```

**Expected thresholds:**
| Metric | Expected | High Variance If |
|--------|----------|------------------|
| Blocking Issues | ≤2 | >3 |
| Per Dimension (critical) | ≤1 point | >1 |
| Per Dimension (standard) | ≤0.5 points | >0.5 |
| Overall Score | ≤5 points | >5 |

### Step 4: Assess Consistency

**If all variance ≤ expected:**
- Status: ✅ CONSISTENT
- No investigation needed
- Include brief consistency note in output

**If any variance > expected:**
- Status: ⚠️ HIGH VARIANCE
- Investigation REQUIRED
- Document cause of variance

### Step 5: Report Variance

**Include in review output (after Score Breakdown):**

```markdown
## Review Consistency Check

**Prior review:** [filename]
**Prior score:** [XX]/100
**Current score:** [YY]/100
**Variance:** ±Z points [CONSISTENT ✅ / HIGH VARIANCE ⚠️]

| Dimension | Prior | Current | Delta | Status |
|-----------|-------|---------|-------|--------|
| Executability | X/10 | Y/10 | ±Z | OK/FLAGGED |
| Completeness | X/10 | Y/10 | ±Z | OK/FLAGGED |
| ... | ... | ... | ... | ... |

[If HIGH VARIANCE: Investigation notes explaining cause]
```

### High Variance Investigation

**If variance exceeds thresholds:**

1. **Compare worksheets**
   - Check issue counts in both reviews
   - Identify specific items that differ

2. **Check methodology**
   - Were Non-Issues filters applied in both?
   - Was overlap resolution consistent?
   - Were same pattern inventories used?

3. **Determine cause**
   - Plan genuinely changed → document changes
   - Counting error in prior → note correction
   - Interpretation drift → flag for rubric clarification

4. **Document in output**
   ```markdown
   ### Variance Investigation
   
   **Dimension with variance:** [dimension]
   **Prior count:** [X] issues
   **Current count:** [Y] issues
   **Difference:** ±Z issues
   
   **Cause:** [explanation]
   **Resolution:** [action taken or recommendation]
   ```

### Consistency Check Recommendation

**After high variance:**
- If plan unchanged → Re-review with explicit worksheet comparison
- If methodology issue → Update rubric/workflow documentation
- If persistent variance → Flag for skill improvement

**See:** `workflows/consistency-check.md` for comprehensive consistency protocols including Score Locking
