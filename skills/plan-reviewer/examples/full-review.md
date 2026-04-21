# FULL Mode Example

This example demonstrates a complete FULL mode review of a plan file.

## Custom Output Directory

```text
target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
output_root: mytest/
```

**Output written to:** `mytest/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

---

## Default Output Directory

## Input

```text
target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

## Expected Output

```markdown
## Plan Review: IMPROVE_RULE_LOADING.md

**Plan:** plans/IMPROVE_RULE_LOADING.md
**Review Date:** 2025-12-16
**Review Mode:** FULL
**Reviewing Model:** Claude Sonnet 4.5

---

### Scores
- **Executability** - Max: 20, Raw: 4/5, Points: 16/20, Notes: 3 ambiguous phrases found ("consider", "as needed")
- **Completeness** - Max: 20, Raw: 5/5, Points: 20/20, Notes: All phases have setup, validation, cleanup
- **Success Criteria** - Max: 20, Raw: 4/5, Points: 16/20, Notes: 90% tasks have criteria; 2 tasks lack verification
- **Scope** - Max: 15, Raw: 5/5, Points: 15/15, Notes: Clear in/out scope, defined start/end state
- **Dependencies** - Max: 10, Raw: 5/5, Points: 10/10, Notes: All dependencies explicit with blockers noted
- **Decomposition** - Max: 5, Raw: 4/5, Points: 4/5, Notes: 2 tasks could be split further
- **Context** - Max: 5, Raw: 4/5, Points: 4/5, Notes: Minor domain knowledge assumed
- **Risk Awareness** - Max: 5, Raw: 3/5, Points: 3/5, Notes: Risks identified but fallbacks sparse

**Overall:** 88/100

### Overall Score Interpretation

- **90-100** - Assessment: Excellent, Verdict: EXECUTABLE
- ****80-89**** - Assessment: **Good**, Verdict: **EXECUTABLE_WITH_REFINEMENTS**
- **60-79** - Assessment: Needs Work, Verdict: NEEDS_REFINEMENT
- **<60** - Assessment: Poor/Inadequate, Verdict: NOT_EXECUTABLE

### Agent Executability Verdict
**EXECUTABLE_WITH_REFINEMENTS**

Plan is ready for agent execution with minor improvements recommended.
All critical dimensions score 4/5 or higher; no blocking issues found.

---

### Executability Audit

- **"consider using"** - Line(s): 45, Issue: Requires judgment, Proposed Fix: "use `grep -r`"
- **"as needed"** - Line(s): 89, Issue: Undefined trigger, Proposed Fix: "if file count > 10, then batch"
- **"may need to"** - Line(s): 123, Issue: Conditional unclear, Proposed Fix: "if tests fail, run `pytest -v`"

**Ambiguous Phrase Count:** 3
**Steps with Explicit Commands:** 45/48 (94%)

### Completeness Audit

- **Phase 1: Analysis** - Setup: , Validation: , Cleanup: , Error Recovery: 
- **Phase 2: Implementation** - Setup: , Validation: , Cleanup: , Error Recovery: Partial
- **Phase 3: Testing** - Setup: , Validation: , Cleanup: , Error Recovery: 
- **Phase 4: Documentation** - Setup: , Validation: , Cleanup: N/A, Error Recovery: N/A

**Phases with Full Coverage:** 3/4 (75%)
**Missing Elements:** Phase 2 error recovery incomplete

### Success Criteria Audit

- **1.1 Scan files** - Has Criteria?: , Verifiable by Agent?: , Notes: "find returns 0 exit code"
- **1.2 Analyze patterns** - Has Criteria?: , Verifiable by Agent?: , Notes: "patterns documented" - subjective
- **2.1 Update rules** - Has Criteria?: , Verifiable by Agent?: , Notes: "grep confirms changes"
- **2.2 Test changes** - Has Criteria?: , Verifiable by Agent?: , Notes: "pytest passes"
- **3.1 Run full suite** - Has Criteria?: , Verifiable by Agent?: , Notes: "0 failures"

**Tasks with Criteria:** 48/50 (96%)
**Agent-Verifiable:** 45/50 (90%)

---

### Plan Perspective Checklist

- [x] **Agent execution test:** Yes - agent can execute end-to-end
  with 3 minor clarifications needed
- [x] **Ambiguity count:** 3 phrases (within 4/5 threshold)
- [x] **Validation coverage:** 75% phases fully covered
- [x] **Success criteria coverage:** 90% agent-verifiable
- [x] **Scope clarity:** Explicit start/end, clear boundaries

---

### Critical Issues (Must Fix Before Agent Execution)

None identified.

### Improvements (Should Fix)

1. **Location:** Line 45
   **Problem:** "consider using" requires agent judgment
   **Recommendation:** Replace with explicit command: `use grep -r "pattern" ./rules/`

2. **Location:** Line 89
   **Problem:** "as needed" has no defined trigger
   **Recommendation:** Add condition: `if $(find . -name "*.md" | wc -l) > 10`

3. **Location:** Phase 2, Error Recovery
   **Problem:** Incomplete error recovery documentation
   **Recommendation:** Add rollback command: `git checkout -- rules/`

### Minor Suggestions (Nice to Have)

1. Add time estimates per task for progress tracking
2. Consider adding checkpoints for long-running phases
3. Document parallel execution opportunities

---

**Output written to:** reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
```

## Key Points Demonstrated

1. **All 8 dimensions scored** with justifications
2. **Point calculations** applied correctly (88/100)
3. **All 3 verification tables** completed with evidence
4. **Checklist answered** with scoring impact notes
5. **Recommendations prioritized** (Critical > Improvements > Minor)
6. **Line numbers cited** for all issues
7. **Verdict assigned** based on score and thresholds

---

## FULL Mode With `timing_enabled: true`

### Input

```text
target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2026-04-21
review_mode: FULL
model: claude-opus-47
timing_enabled: true
execution_mode: parallel
```

### Quick Reference Execution (abbreviated)

```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)

$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill plan-reviewer --target plans/IMPROVE_RULE_LOADING.md \
    --model claude-opus-47 --mode FULL
# → run_id: 7a1c...

# (8 dimensions, each bracketed)
$PYTHON ... checkpoint --run-id 7a1c... --name dim_executability_start
# ...score...
$PYTHON ... checkpoint --run-id 7a1c... --name dim_executability_end
# (repeat for completeness, success_criteria, scope, dependencies,
#  decomposition, context, risk_awareness)

$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id 7a1c... \
    --output-file reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-opus-47-2026-04-21.md \
    --skill plan-reviewer --format markdown --auto-dimension-timings
# → PER_DIMENSION_STATUS=derived
```

### Expected Per-Dimension Timing Section (embedded in output)

```markdown
### Per-Dimension Timing

| Dimension         | Duration (s) | Mode        | Notes |
|-------------------|-------------:|-------------|-------|
| executability     | 1.35         | derived     | |
| completeness      | 1.39         | derived     | |
| success_criteria  | 1.48         | derived     | |
| scope             | 1.17         | derived     | |
| dependencies      | 0.76         | derived     | |
| decomposition     | 0.60         | derived     | |
| context           | 0.54         | derived     | |
| risk_awareness    | 0.48         | derived     | |
```

### Gate 7 Outcome

- 8 rows present → Gate 7 **PASSES**.
- If any row missing or heading absent → Gate 7 **REJECTS** the review per
  `workflows/file-write.md`.

