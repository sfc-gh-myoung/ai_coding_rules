# Workflow 04: Summary Report Generation

## Purpose

Generate master summary report from aggregated data with prioritized improvement recommendations. Creates actionable report for quality audits, pre-release validation, and technical debt tracking.

## Inputs

- `summary_data`: Data structure from aggregation.md
- `review_date`: Date stamp (YYYY-MM-DD)
- `review_mode`: FULL | FOCUSED | STALENESS
- `model`: Model identifier

## Outputs

- Master summary report file: `reviews/_bulk-review-<model>-<date>.md`
- Console message with file path

## Implementation

### Step 1: Build Report Header

```markdown
# Bulk Rule Review Summary

**Review Date:** {review_date}
**Model:** {model}
**Rules Reviewed:** {total_reviewed}
**Review Mode:** {review_mode}
**Completion Status:** {successful}/{total_reviewed} ({failed} failed)

---
```

### Step 2: Executive Summary Section

```markdown
## Executive Summary

### Score Distribution

- **Average Score:** {average_score}/100
- **Median Score:** {median_score}/100
- **Excellent (90-100):** {excellent_count} rules ({excellent_pct}%)
- **Good (80-89):** {good_count} rules ({good_pct}%)
- **Needs Work (60-79):** {needs_work_count} rules ({needs_work_pct}%)
- **Poor (<60):** {poor_count} rules ({poor_pct}%)

### Dimension Analysis

- **Average Actionability:** {actionability_avg}/25 ({actionability_pct}%)
- **Average Completeness:** {completeness_avg}/25 ({completeness_pct}%)
- **Average Consistency:** {consistency_avg}/15 ({consistency_pct}%)
- **Average Parsability:** {parsability_avg}/15 ({parsability_pct}%)
- **Average Token Efficiency:** {token_efficiency_avg}/10 ({token_efficiency_pct}%)
- **Average Staleness:** {staleness_avg}/10 ({staleness_pct}%)

### Critical Issues Summary

- **Rules with 0 critical issues:** {zero_issues} ({zero_pct}%)
- **Rules with 1-2 critical issues:** {low_issues} ({low_pct}%)
- **Rules with 3+ critical issues:** {high_issues} ({high_pct}%)

---
```

### Step 3: Priority 1 Section (Urgent)

For each rule in priority_1 (score <60):

```markdown
## Priority 1: Urgent (Score <60) - {count} Rules

{Verdict: NOT_EXECUTABLE - Agents cannot execute without extensive judgment calls}

### {index}. rules/{rule_name}.md - {score}/100 ({verdict})

**Scores:** Actionability: {action}/25 | Completeness: {complete}/25 | Consistency: {consist}/15

**Critical Issues:** {critical_count} issues identified
- {Summary of top issues from review - if available}

**Impact:** {Impact description based on score/verdict}

**Recommendation:** {Recommended action - rewrite, major refactor, etc.}

**Estimated Effort:** {Effort estimate based on score - e.g., 4-6 hours}

**Review:** {review_path}

---
```

### Step 4: Priority 2 Section (High)

For top 5-10 rules in priority_2 (score 60-79):

```markdown
## Priority 2: High (Score 60-79) - {count} Rules

{Verdict: NEEDS_REFINEMENT - Significant improvements required}

### Top {top_count} Rules Needing Attention:

{index}. **rules/{rule_name}.md - {score}/100** ({verdict})
   - **Issues:** {critical_count} critical issues - {summary}
   - **Quick wins:** {Actionable improvements}
   - **Effort:** ~{effort_estimate}
   - **Review:** {review_path}

---
```

### Step 5: Priority 3 Section (Medium)

Aggregate summary for priority_3 (score 80-89):

```markdown
## Priority 3: Medium (Score 80-89) - {count} Rules

**Status:** EXECUTABLE_WITH_REFINEMENTS

**Aggregate Issues:**
- Undefined thresholds: {threshold_count} total across {count} rules (avg {avg_per_rule} per rule)
- Minor consistency issues: {consistency_count} rules
- Token budget variance >5%: {token_variance_count} rules

**Recommendation:** Address opportunistically during regular updates. Not urgent.

**Sample Rules:**
- rules/{example_1}.md - {score_1}/100
- rules/{example_2}.md - {score_2}/100
- rules/{example_3}.md - {score_3}/100

---
```

### Step 6: Priority 4 Section (Excellent)

Brief summary for priority_4 (score 90-100):

```markdown
## Priority 4: Excellent (Score 90-100) - {count} Rules

**Status:** EXECUTABLE (production-ready)

**Example Rules:**
- rules/{top_rule_1}.md - {score_1}/100
- rules/{top_rule_2}.md - {score_2}/100
- rules/{top_rule_3}.md - {score_3}/100
- ... ({remaining_count} more)

**Maintenance:** Quarterly staleness reviews only. No immediate action needed.

---
```

### Step 7: Failed Reviews Section

If failed_reviews exists:

```markdown
## Failed Reviews - {count} Rules

{index}. **rules/{rule_name}.md** - Review failed ({error_message})

**Action Required:** Manual review needed. Common causes:
- Malformed markdown syntax
- Context overflow (rule too large)
- Missing required metadata

---
```

### Step 8: Top 10 Improvement Recommendations

Calculate impact × effort ratio and rank:

```markdown
## Top 10 Improvement Recommendations

**Prioritized by Impact × Effort ratio (high impact, low effort first):**

{index}. **{rule_name}.md ({score}/100)** - {action_summary} [{priority} impact, {effort}]
   - Current issues: {issue_summary}
   - Recommended fixes: {fix_summary}
   - Expected improvement: +{delta} points

**Total Estimated Effort for Top 10:** ~{total_effort} hours
**Expected Score Improvement:** +{avg_delta} points average across 10 rules

---
```

### Step 9: Next Steps Section

```markdown
## Next Steps

### Immediate (this week)
- Address Priority 1 rules ({priority_1_names})
- Fix failed reviews ({failed_names})

### Short-term (this month)
- Address Priority 2 rules with <75 score
- Implement quick wins from Top 10 list (items 5-10)

### Long-term (quarterly)
- Periodic bulk reviews to track improvement trends
- Update this baseline as rules are improved
- Consider automated quality gates for CI/CD

---
```

### Step 10: Appendix (All Rules by Score)

```markdown
## Appendix: All Rules by Score

| Rank | Rule | Score | Verdict | Critical Issues | Review |
|------|------|-------|---------|----------------|--------|
| 1 | 000-global-core | 100 | EXECUTABLE | 0 | [review](reviews/...) |
| 2 | 100-snowflake-core | 100 | EXECUTABLE | 0 | [review](reviews/...) |
| ... | ... | ... | ... | ... | ... |
| 113 | xyz-deprecated | 45 | NOT_EXECUTABLE | 7 | [review](reviews/...) |

---

**Report Generated:** {timestamp}
**Tool Version:** bulk-rule-reviewer v1.0.0
```

## File Writing and No-Overwrite Logic

```python
def write_summary_report(summary_data, review_date, model, review_mode):
    """Write master summary report to file with no-overwrite protection."""
    import os
    from datetime import datetime
    
    # Build base filename
    base_filename = f"reviews/_bulk-review-{model}-{review_date}.md"
    
    # Check if file exists
    if os.path.exists(base_filename):
        # Increment suffix: _bulk-review-claude-sonnet-45-2026-01-06-01.md
        counter = 1
        while True:
            incremented_filename = f"reviews/_bulk-review-{model}-{review_date}-{counter:02d}.md"
            if not os.path.exists(incremented_filename):
                output_path = incremented_filename
                break
            counter += 1
    else:
        output_path = base_filename
    
    # Generate report content
    report_content = generate_report_markdown(summary_data, review_date, model, review_mode)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    # Print success message
    print(f"\n{'='*60}")
    print(f"Master summary report written to:")
    print(f"  {output_path}")
    print(f"{'='*60}\n")
    
    return output_path
```

## Helper Functions

### calculate_impact_effort_ratio(rule_data)

```python
def calculate_impact_effort_ratio(rule_data):
    """Calculate impact × effort ratio for prioritization.
    
    Impact factors:
    - Score (lower = higher impact)
    - Critical issues count
    - Verdict severity
    
    Effort factors:
    - Score delta to next tier
    - Number of missing components
    """
    score = rule_data["overall_score"]
    critical = rule_data["critical_issues"]
    
    # Impact score (0-100, higher = more impactful)
    # Low scores have high impact
    impact = 100 - score + (critical * 5)
    
    # Effort estimate (hours)
    if score < 60:
        effort = 4 + (critical * 0.5)  # 4-6 hours
    elif score < 70:
        effort = 2 + (critical * 0.5)  # 2-3 hours
    elif score < 80:
        effort = 1 + (critical * 0.25)  # 1-1.5 hours
    elif score < 90:
        effort = 0.5 + (critical * 0.1)  # 30-45 min
    else:
        effort = 0.25  # 15 min
    
    # Impact × Effort ratio (higher = better ROI)
    ratio = impact / effort if effort > 0 else 0
    
    return {
        "impact": impact,
        "effort": effort,
        "ratio": ratio
    }
```

### format_effort_estimate(hours)

```python
def format_effort_estimate(hours):
    """Format effort estimate as human-readable string."""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}min"
    else:
        return f"{hours:.1f}h" if hours != int(hours) else f"{int(hours)}h"
```

## Error Handling

### Empty Results

**Cause:** All reviews failed, no successful data

**Action:**
1. Generate minimal report with executive summary showing 0 success
2. List all failed reviews with error messages
3. Include troubleshooting section

### File Write Failure

**Cause:** Cannot write to reviews/ directory

**Action:**
1. Print OUTPUT_FILE directive with full report content
2. User must manually save to file
3. Report error in console

### Malformed Summary Data

**Cause:** Aggregation workflow produced incomplete data structure

**Action:**
1. Use default values for missing fields
2. Log warnings for each missing section
3. Generate partial report with available data

## Performance Notes

- Report generation is fast (<2 seconds)
- Markdown formatting is straightforward
- File writing is atomic (no partial writes)
- No-overwrite logic ensures no data loss

## Integration Points

**Input:** summary_data from aggregation.md
**Output:** Master summary file path

This is the final workflow in the bulk review pipeline.

## Testing Checklist

- [ ] Generates valid markdown structure
- [ ] All sections populated with correct data
- [ ] Priority tiers sorted correctly
- [ ] Top 10 recommendations calculated accurately
- [ ] No-overwrite logic works (increments suffix)
- [ ] Failed reviews listed with error messages
- [ ] Appendix table formatted correctly
- [ ] File path returned to user
