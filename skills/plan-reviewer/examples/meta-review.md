# META-REVIEW Mode Example

This example demonstrates analyzing multiple reviews of the same document to assess consistency and identify the most reliable review.

## Input

```text
target_files: [
  reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md,
  reviews/plan-IMPROVE_RULE_LOADING-gpt-52-2025-12-16.md,
  reviews/plan-IMPROVE_RULE_LOADING-claude-opus45-2025-12-16.md
]
original_document: plans/IMPROVE_RULE_LOADING.md
review_date: 2025-12-16
review_mode: META-REVIEW
model: claude-sonnet45
```

## Expected Output

```markdown
## Meta-Review: IMPROVE_RULE_LOADING Reviews

**Document Reviewed:** plans/IMPROVE_RULE_LOADING.md
**Review Date:** 2025-12-16
**Reviewing Model:** Claude Sonnet 4.5
**Reviews Analyzed:** 3

---

### Reviews Summary
| Review File | Model | Score | Critical Issues | Lines |
|-------------|-------|-------|-----------------|-------|
| plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md | Claude Sonnet 4.5 | 52/60 | 0 | 285 |
| plan-IMPROVE_RULE_LOADING-gpt-52-2025-12-16.md | GPT-5.2 | 44/60 | 2 | 198 |
| plan-IMPROVE_RULE_LOADING-claude-opus45-2025-12-16.md | Claude Opus 4.5 | 50/60 | 1 | 265 |

**Score Variance:** 8 points (13.3% spread)

---

### Consistency Analysis

| Metric | Value | Assessment |
|--------|-------|------------|
| Score spread | 8 points | ⚠️ High variance (>10% = investigate) |
| Critical issues agreement | 1/3 reviews found 2+ issues | ⚠️ Low consensus on critical findings |
| Verification table presence | 3/3 reviews | ✅ Consistent methodology |
| Line citations | 3/3 reviews | ✅ All reviews cite evidence |
| Verdict agreement | 2/3 EXECUTABLE | ⚠️ One review disagrees |

### Score Breakdown by Dimension
| Dimension | Sonnet | GPT | Opus | Variance | Consensus |
|-----------|--------|-----|------|----------|-----------|
| Executability | 8/10 | 6/10 | 8/10 | 2 | 7/10 |
| Completeness | 10/10 | 8/10 | 9/10 | 2 | 9/10 |
| Success Criteria | 8/10 | 6/10 | 7/10 | 2 | 7/10 |
| Scope | 10/10 | 8/10 | 10/10 | 2 | 9/10 |
| Decomposition | 4/5 | 4/5 | 4/5 | 0 | 4/5 |
| Dependencies | 5/5 | 5/5 | 5/5 | 0 | 5/5 |
| Context | 4/5 | 4/5 | 4/5 | 0 | 4/5 |
| Risk Awareness | 3/5 | 3/5 | 3/5 | 0 | 3/5 |

**High variance dimensions:** Executability, Completeness, Success Criteria, Scope
**Perfect agreement dimensions:** Decomposition, Dependencies, Context, Risk Awareness

---

### Issue Detection Comparison
| Issue | Sonnet | GPT | Opus | Consensus |
|-------|--------|-----|------|-----------|
| "pytest" vs "task test" inconsistency | ❌ | ✅ | ❌ | 1/3 found |
| Scope mismatch (7 files stated vs `find` command) | ❌ | ✅ | ✅ | 2/3 found |
| Missing time estimates | ✅ | ✅ | ✅ | 3/3 found |
| Incomplete error recovery (Phase 2) | ✅ | ✅ | ✅ | 3/3 found |
| Ambiguous phrase: "as needed" (Line 89) | ✅ | ✅ | ✅ | 3/3 found |

**Issue Detection Rate:**
- Sonnet: 3/5 issues (60%)
- GPT: 5/5 issues (100%)
- Opus: 4/5 issues (80%)

---

### Calibration Assessment

**Scoring Calibration:**

| Review | Calibration Issue | Impact |
|--------|-------------------|--------|
| Sonnet | Missed executability issues → scored too high | +2 points inflation |
| GPT | No calibration issues detected | Accurate |
| Opus | Minor: rounded up on Success Criteria | +1 point inflation |

**Most Thorough:** GPT-5.2
- Found all 5 issues
- Most detailed verification tables
- Provided actionable fixes for each issue

**Most Generous:** Claude Sonnet 4.5
- Scored 52/60 despite missing 2 critical issues
- Executability score not adjusted for found ambiguities

**Best Calibrated:** GPT-5.2
- Scores align with Scoring Impact Rules
- Issues detected match score deductions
- Verdict (NEEDS_REFINEMENT) consistent with findings

---

### Meta-Review Scores
| Review | Thoroughness | Evidence | Calibration | Actionability | Total |
|--------|--------------|----------|-------------|---------------|-------|
| Sonnet | 3/5 | 5/5 | 3/5 | 4/5 | 15/20 |
| GPT | 5/5 | 4/5 | 5/5 | 5/5 | 19/20 |
| Opus | 4/5 | 5/5 | 4/5 | 4/5 | 17/20 |

**Dimension Analysis:**

**Thoroughness (Did review check all required elements?):**
- Sonnet: 3/5 - Missed 2 issues found by other reviewers
- GPT: 5/5 - Found all issues, complete verification tables
- Opus: 4/5 - Good coverage, missed 1 issue

**Evidence Quality (Are scores supported by citations?):**
- Sonnet: 5/5 - All findings cite line numbers
- GPT: 4/5 - Good citations, one finding lacks specific line
- Opus: 5/5 - Excellent evidence throughout

**Calibration (Does scoring match rubric?):**
- Sonnet: 3/5 - Scores not adjusted for findings
- GPT: 5/5 - Scores match Scoring Impact Rules exactly
- Opus: 4/5 - Minor inflation on one dimension

**Actionability (Are recommendations implementable?):**
- Sonnet: 4/5 - Good recommendations, some lack specifics
- GPT: 5/5 - Every recommendation includes exact fix
- Opus: 4/5 - Clear recommendations, some generic

---

### Consensus Determination

**Method:** Weighted average adjusted for calibration confidence

| Review | Score | Calibration Weight | Weighted Contribution |
|--------|-------|-------------------|----------------------|
| Sonnet | 52/60 | 0.75 | 39.0 |
| GPT | 44/60 | 1.00 | 44.0 |
| Opus | 50/60 | 0.90 | 45.0 |

**Weighted Sum:** 128.0
**Sum of Weights:** 2.65
**Consensus Score:** 48/60 (rounded)

**Confidence Level:** Medium
- High score variance suggests rubric interpretation differences
- Standard dimensions show perfect agreement (good)
- Critical dimensions vary (concerning)

---

### Recommendation

**Most Reliable Review:** GPT-5.2 (19/20 meta-score)

**Rationale:**
1. Highest issue detection rate (100%)
2. Best calibration with rubric definitions
3. Most actionable recommendations
4. Verdict (NEEDS_REFINEMENT) aligns with consensus score

**Action Items:**
1. ✅ Accept GPT-5.2's findings as authoritative
2. ⚠️ Investigate why Sonnet missed the pytest/task inconsistency
3. 📝 Update PROMPT.md to clarify Executability scoring for command inconsistencies
4. 🔄 Re-run Sonnet review after rubric clarification

**Consensus Verdict:** NEEDS_REFINEMENT (48/60)
- Plan requires 2 fixes before agent execution:
  1. Resolve pytest vs task command inconsistency
  2. Fix scope mismatch (7 files vs find command)

---

**Output written to:** reviews/meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
```

## Key Points Demonstrated

1. **Score variance calculated** (8 points, 13.3%)
2. **Per-dimension breakdown** shows where disagreement occurs
3. **Issue detection comparison** - who found what
4. **Calibration assessment** - identifies scoring inflation/deflation
5. **Meta-scores assigned** to each review (Thoroughness, Evidence, Calibration, Actionability)
6. **Consensus calculation** with weighted averaging
7. **Most reliable review identified** with rationale
8. **Action items** for improving review consistency

