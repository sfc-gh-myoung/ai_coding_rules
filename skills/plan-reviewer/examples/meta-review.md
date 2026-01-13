# META-REVIEW Mode Example

This example demonstrates analyzing multiple reviews of the same document to assess consistency and identify the most reliable review.

## Input

```text
target_files: [
  reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md,
  reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-gpt-52-2025-12-16.md,
  reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-opus45-2025-12-16.md
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
- **plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md** - Model: Claude Sonnet 4.5, Score: 87/100, Critical Issues: 0, Lines: 285
- **plan-IMPROVE_RULE_LOADING-gpt-52-2025-12-16.md** - Model: GPT-5.2, Score: 73/100, Critical Issues: 2, Lines: 198
- **plan-IMPROVE_RULE_LOADING-claude-opus45-2025-12-16.md** - Model: Claude Opus 4.5, Score: 83/100, Critical Issues: 1, Lines: 265

**Score Variance:** 14 points (14% spread)

---

### Consistency Analysis

- **Score spread** - Value: 8 points, Assessment: High variance (>10% = investigate)
- **Critical issues agreement** - Value: 1/3 reviews found 2+ issues, Assessment: Low consensus on critical findings
- **Verification table presence** - Value: 3/3 reviews, Assessment: Consistent methodology
- **Line citations** - Value: 3/3 reviews, Assessment: All reviews cite evidence
- **Verdict agreement** - Value: 2/3 EXECUTABLE, Assessment: One review disagrees

### Score Breakdown by Dimension
- **Executability** - Sonnet: 16/20, GPT: 12/20, Opus: 16/20, Variance: 4, Consensus: 14/20
- **Completeness** - Sonnet: 20/20, GPT: 16/20, Opus: 18/20, Variance: 4, Consensus: 18/20
- **Success Criteria** - Sonnet: 16/20, GPT: 12/20, Opus: 14/20, Variance: 4, Consensus: 14/20
- **Scope** - Sonnet: 15/15, GPT: 12/15, Opus: 15/15, Variance: 3, Consensus: 14/15
- **Dependencies** - Sonnet: 10/10, GPT: 10/10, Opus: 10/10, Variance: 0, Consensus: 10/10
- **Decomposition** - Sonnet: 4/5, GPT: 4/5, Opus: 4/5, Variance: 0, Consensus: 4/5
- **Context** - Sonnet: 4/5, GPT: 4/5, Opus: 4/5, Variance: 0, Consensus: 4/5
- **Risk Awareness** - Sonnet: 3/5, GPT: 3/5, Opus: 3/5, Variance: 0, Consensus: 3/5

**High variance dimensions:** Executability, Completeness, Success Criteria, Scope
**Perfect agreement dimensions:** Decomposition, Dependencies, Context, Risk Awareness

---

### Issue Detection Comparison
- **"pytest" vs "task test" inconsistency** - Sonnet: , GPT: , Opus: , Consensus: 1/3 found
- **Scope mismatch (7 files stated vs `find` command)** - Sonnet: , GPT: , Opus: , Consensus: 2/3 found
- **Missing time estimates** - Sonnet: , GPT: , Opus: , Consensus: 3/3 found
- **Incomplete error recovery (Phase 2)** - Sonnet: , GPT: , Opus: , Consensus: 3/3 found
- **Ambiguous phrase: "as needed" (Line 89)** - Sonnet: , GPT: , Opus: , Consensus: 3/3 found

**Issue Detection Rate:**
- Sonnet: 3/5 issues (60%)
- GPT: 5/5 issues (100%)
- Opus: 4/5 issues (80%)

---

### Calibration Assessment

**Scoring Calibration:**

- **Sonnet** - Calibration Issue: Missed executability issues → scored too high, Impact: +2 points inflation
- **GPT** - Calibration Issue: No calibration issues detected, Impact: Accurate
- **Opus** - Calibration Issue: Minor: rounded up on Success Criteria, Impact: +1 point inflation

**Most Thorough:** GPT-5.2
- Found all 5 issues
- Most detailed verification tables
- Provided actionable fixes for each issue

**Most Generous:** Claude Sonnet 4.5
- Scored 87/100 despite missing 2 critical issues
- Executability score not adjusted for found ambiguities

**Best Calibrated:** GPT-5.2
- Scores align with Scoring Impact Rules
- Issues detected match score deductions
- Verdict (NEEDS_REFINEMENT) consistent with findings

---

### Meta-Review Scores
- **Sonnet** - Thoroughness: 3/5, Evidence: 5/5, Calibration: 3/5, Actionability: 4/5, Total: 15/20
- **GPT** - Thoroughness: 5/5, Evidence: 4/5, Calibration: 5/5, Actionability: 5/5, Total: 19/20
- **Opus** - Thoroughness: 4/5, Evidence: 5/5, Calibration: 4/5, Actionability: 4/5, Total: 17/20

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

- **Sonnet** - Score: 87/100, Calibration Weight: 0.75, Weighted Contribution: 65.3
- **GPT** - Score: 73/100, Calibration Weight: 1.00, Weighted Contribution: 73.0
- **Opus** - Score: 83/100, Calibration Weight: 0.90, Weighted Contribution: 74.7

**Weighted Sum:** 213.0
**Sum of Weights:** 2.65
**Consensus Score:** 80/100 (rounded)

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
1.  Accept GPT-5.2's findings as authoritative
2.  Investigate why Sonnet missed the pytest/task inconsistency
3. 📝 Update SKILL.md to clarify Executability scoring for command inconsistencies
4. 🔄 Re-run Sonnet review after rubric clarification

**Consensus Verdict:** EXECUTABLE_WITH_REFINEMENTS (80/100)
- Plan requires 2 fixes before agent execution:
  1. Resolve pytest vs task command inconsistency
  2. Fix scope mismatch (7 files vs find command)

---

**Output written to:** reviews/summaries/_meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
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

