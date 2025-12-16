# FULL Mode Example

This example demonstrates a complete FULL mode review of a plan file.

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

### Scores (Weighted)
| Criterion | Weight | Raw | Weighted | Notes |
|-----------|--------|-----|----------|-------|
| Executability | 2× | 4/5 | 8/10 | 3 ambiguous phrases found ("consider", "as needed") |
| Completeness | 2× | 5/5 | 10/10 | All phases have setup, validation, cleanup |
| Success Criteria | 2× | 4/5 | 8/10 | 90% tasks have criteria; 2 tasks lack verification |
| Scope | 2× | 5/5 | 10/10 | Clear in/out scope, defined start/end state |
| Decomposition | 1× | 4/5 | 4/5 | 2 tasks could be split further |
| Dependencies | 1× | 5/5 | 5/5 | All dependencies explicit with blockers noted |
| Context | 1× | 4/5 | 4/5 | Minor domain knowledge assumed |
| Risk Awareness | 1× | 3/5 | 3/5 | Risks identified but fallbacks sparse |

**Overall:** 52/60 (weighted)

### Overall Score Interpretation

| Score Range | Assessment | Verdict |
|-------------|------------|---------|
| 54-60/60 (90-100%) | Excellent | EXECUTABLE |
| **48-53/60 (80-89%)** | **Good** | **EXECUTABLE with minor refinements** |
| 36-47/60 (60-79%) | Needs Work | NEEDS_REFINEMENT |
| <36/60 (<60%) | Poor/Inadequate | NOT_EXECUTABLE |

### Agent Executability Verdict
**EXECUTABLE**

Plan is ready for agent execution with minor improvements recommended.
All critical dimensions score 4/5 or higher; no blocking issues found.

---

### Executability Audit

| Phrase | Line(s) | Issue | Proposed Fix |
|--------|---------|-------|--------------|
| "consider using" | 45 | Requires judgment | "use `grep -r`" |
| "as needed" | 89 | Undefined trigger | "if file count > 10, then batch" |
| "may need to" | 123 | Conditional unclear | "if tests fail, run `pytest -v`" |

**Ambiguous Phrase Count:** 3
**Steps with Explicit Commands:** 45/48 (94%)

### Completeness Audit

| Phase | Setup | Validation | Cleanup | Error Recovery |
|-------|-------|------------|---------|----------------|
| Phase 1: Analysis | ✅ | ✅ | ✅ | ✅ |
| Phase 2: Implementation | ✅ | ✅ | ✅ | ⚠️ Partial |
| Phase 3: Testing | ✅ | ✅ | ✅ | ✅ |
| Phase 4: Documentation | ✅ | ✅ | N/A | N/A |

**Phases with Full Coverage:** 3/4 (75%)
**Missing Elements:** Phase 2 error recovery incomplete

### Success Criteria Audit

| Task/Milestone | Has Criteria? | Verifiable by Agent? | Notes |
|----------------|---------------|---------------------|-------|
| 1.1 Scan files | ✅ | ✅ | "find returns 0 exit code" |
| 1.2 Analyze patterns | ✅ | ⚠️ | "patterns documented" - subjective |
| 2.1 Update rules | ✅ | ✅ | "grep confirms changes" |
| 2.2 Test changes | ✅ | ✅ | "pytest passes" |
| 3.1 Run full suite | ✅ | ✅ | "0 failures" |

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

**Output written to:** reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
```

## Key Points Demonstrated

1. **All 8 dimensions scored** with justifications
2. **Weighted calculations** applied correctly (52/60)
3. **All 3 verification tables** completed with evidence
4. **Checklist answered** with scoring impact notes
5. **Recommendations prioritized** (Critical > Improvements > Minor)
6. **Line numbers cited** for all issues
7. **Verdict assigned** based on score and thresholds

