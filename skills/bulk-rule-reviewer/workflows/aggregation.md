# Workflow 03: Score Aggregation

## Purpose

Extract scores, verdicts, and critical issues from individual review files without loading full content. Calculate statistics and prepare data structure for master summary report. Implements context-efficient parsing strategy.

## Inputs

- Results list from review-execution.md containing:
  - `rule_name`: Rule identifier
  - `score`: Overall score (0-100)
  - `verdict`: Verdict enum
  - `critical_issues`: Count of critical issues
  - `review_path`: Path to review file
  - `status`: SUCCESS | FAILED | SKIPPED

## Outputs

- Summary data structure with:
  - **Executive statistics:** Average score, median, distribution by tier
  - **Dimension averages:** Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
  - **Critical issues summary:** Count distribution (0, 1-2, 3+ issues)
  - **Priority tiers:** Rules grouped by score range
  - **Failed reviews:** List of rules with errors

## Implementation

### Step 1: Build Enhanced Metadata Structure

For each review in results list where status = SUCCESS or SKIPPED:

```python
def extract_full_metadata(review_path):
    """Extract comprehensive metadata from review file.
    
    Reads ONLY first 150 lines to avoid context overflow.
    """
    import re
    
    with open(review_path, 'r') as f:
        lines = f.readlines()[:150]  # First 150 lines only
        content = ''.join(lines)
    
    # Overall score: "**Overall:** 85/100"
    score_match = re.search(r'\*\*Overall:\*\* (\d+)/100', content)
    overall_score = int(score_match.group(1)) if score_match else None
    
    # Verdict: "### Agent Executability Verdict\n**EXECUTABLE**"
    verdict_match = re.search(r'### Agent Executability Verdict\s+\*\*([A-Z_]+)\*\*', content)
    verdict = verdict_match.group(1) if verdict_match else "UNKNOWN"
    
    # Critical issues count
    critical_section_match = re.search(r'### Critical Issues\s+(.*?)(?=###|\Z)', content, re.DOTALL)
    if critical_section_match:
        critical_text = critical_section_match.group(1)
        critical_issues = len(re.findall(r'^\d+\.', critical_text, re.MULTILINE))
    else:
        critical_issues = 0
    
    # Dimension scores from table
    # Format: "| Dimension | Score | Weight | Notes |"
    #         "| Actionability | 22/25 | 25% | ... |"
    dimension_scores = {}
    
    # Extract Actionability
    action_match = re.search(r'\|\s*Actionability\s*\|\s*(\d+)/25', content)
    if action_match:
        dimension_scores['actionability'] = int(action_match.group(1))
    
    # Extract Completeness
    complete_match = re.search(r'\|\s*Completeness\s*\|\s*(\d+)/25', content)
    if complete_match:
        dimension_scores['completeness'] = int(complete_match.group(1))
    
    # Extract Consistency
    consist_match = re.search(r'\|\s*Consistency\s*\|\s*(\d+)/15', content)
    if consist_match:
        dimension_scores['consistency'] = int(consist_match.group(1))
    
    # Extract Parsability
    parse_match = re.search(r'\|\s*Parsability\s*\|\s*(\d+)/15', content)
    if parse_match:
        dimension_scores['parsability'] = int(parse_match.group(1))
    
    # Extract Token Efficiency
    token_match = re.search(r'\|\s*Token Efficiency\s*\|\s*(\d+)/10', content)
    if token_match:
        dimension_scores['token_efficiency'] = int(token_match.group(1))
    
    # Extract Staleness
    stale_match = re.search(r'\|\s*Staleness\s*\|\s*(\d+)/10', content)
    if stale_match:
        dimension_scores['staleness'] = int(stale_match.group(1))
    
    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "critical_issues": critical_issues,
        "dimensions": dimension_scores
    }

# Build enhanced results
enhanced_results = []
for result in results:
    if result["status"] in ["SUCCESS", "SKIPPED"]:
        metadata = extract_full_metadata(result["review_path"])
        enhanced_results.append({
            "rule_name": result["rule_name"],
            "overall_score": metadata["overall_score"],
            "verdict": metadata["verdict"],
            "critical_issues": metadata["critical_issues"],
            "dimensions": metadata["dimensions"],
            "review_path": result["review_path"],
            "status": result["status"]
        })
    else:  # FAILED
        enhanced_results.append({
            "rule_name": result["rule_name"],
            "overall_score": None,
            "verdict": "FAILED",
            "critical_issues": None,
            "dimensions": {},
            "review_path": None,
            "status": "FAILED",
            "error_message": result.get("error_message", "Unknown error")
        })
```

### Step 2: Calculate Executive Statistics

```python
# Filter successful reviews only
successful_reviews = [r for r in enhanced_results if r["overall_score"] is not None]
failed_reviews = [r for r in enhanced_results if r["status"] == "FAILED"]

# Overall scores
scores = [r["overall_score"] for r in successful_reviews]
average_score = round(sum(scores) / len(scores), 1) if scores else 0
median_score = sorted(scores)[len(scores) // 2] if scores else 0

# Distribution by tier
excellent = [r for r in successful_reviews if r["overall_score"] >= 90]  # 90-100
good = [r for r in successful_reviews if 80 <= r["overall_score"] < 90]  # 80-89
needs_work = [r for r in successful_reviews if 60 <= r["overall_score"] < 80]  # 60-79
poor = [r for r in successful_reviews if r["overall_score"] < 60]  # <60

distribution = {
    "excellent": len(excellent),
    "good": len(good),
    "needs_work": len(needs_work),
    "poor": len(poor)
}

# Verdict distribution
verdict_counts = {}
for r in successful_reviews:
    verdict = r["verdict"]
    verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

executive_stats = {
    "total_reviewed": len(enhanced_results),
    "successful": len(successful_reviews),
    "failed": len(failed_reviews),
    "average_score": average_score,
    "median_score": median_score,
    "distribution": distribution,
    "verdict_counts": verdict_counts
}
```

### Step 3: Calculate Dimension Averages

```python
# Aggregate dimension scores across all successful reviews
dimension_totals = {
    "actionability": [],
    "completeness": [],
    "consistency": [],
    "parsability": [],
    "token_efficiency": [],
    "staleness": []
}

for r in successful_reviews:
    for dim, value in r["dimensions"].items():
        if value is not None:
            dimension_totals[dim].append(value)

# Calculate averages
dimension_averages = {}
dimension_max = {
    "actionability": 25,
    "completeness": 25,
    "consistency": 15,
    "parsability": 15,
    "token_efficiency": 10,
    "staleness": 10
}

for dim, values in dimension_totals.items():
    if values:
        avg = round(sum(values) / len(values), 1)
        max_val = dimension_max[dim]
        percentage = round((avg / max_val) * 100, 1)
        dimension_averages[dim] = {
            "average": avg,
            "max": max_val,
            "percentage": percentage
        }
```

### Step 4: Analyze Critical Issues Distribution

```python
# Group by critical issues count
zero_critical = [r for r in successful_reviews if r["critical_issues"] == 0]
low_critical = [r for r in successful_reviews if 1 <= r["critical_issues"] <= 2]
high_critical = [r for r in successful_reviews if r["critical_issues"] >= 3]

critical_analysis = {
    "zero_issues": len(zero_critical),
    "low_issues": len(low_critical),  # 1-2 issues
    "high_issues": len(high_critical),  # 3+ issues
    "zero_percentage": round(len(zero_critical) / len(successful_reviews) * 100, 1) if successful_reviews else 0,
    "low_percentage": round(len(low_critical) / len(successful_reviews) * 100, 1) if successful_reviews else 0,
    "high_percentage": round(len(high_critical) / len(successful_reviews) * 100, 1) if successful_reviews else 0
}
```

### Step 5: Group by Priority Tiers

```python
# Priority 1: Urgent (score <60, NOT_EXECUTABLE)
priority_1 = sorted(poor, key=lambda r: r["overall_score"])

# Priority 2: High (score 60-79, NEEDS_REFINEMENT)
priority_2 = sorted(needs_work, key=lambda r: r["overall_score"])

# Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
priority_3 = sorted(good, key=lambda r: r["overall_score"])

# Priority 4: Excellent (score 90-100, EXECUTABLE)
priority_4 = sorted(excellent, key=lambda r: -r["overall_score"])  # Descending

priority_tiers = {
    "priority_1": priority_1,
    "priority_2": priority_2,
    "priority_3": priority_3,
    "priority_4": priority_4
}
```

### Step 6: Build Summary Data Structure

```python
summary_data = {
    "executive_stats": executive_stats,
    "dimension_averages": dimension_averages,
    "critical_analysis": critical_analysis,
    "priority_tiers": priority_tiers,
    "failed_reviews": failed_reviews,
    "all_reviews": enhanced_results  # For appendix
}

return summary_data
```

## Output Data Structure

```python
{
    "executive_stats": {
        "total_reviewed": 113,
        "successful": 111,
        "failed": 2,
        "average_score": 87.2,
        "median_score": 89,
        "distribution": {
            "excellent": 45,   # 90-100
            "good": 52,        # 80-89
            "needs_work": 14,  # 60-79
            "poor": 2          # <60
        },
        "verdict_counts": {
            "EXECUTABLE": 45,
            "EXECUTABLE_WITH_REFINEMENTS": 52,
            "NEEDS_REFINEMENT": 14,
            "NOT_EXECUTABLE": 2
        }
    },
    "dimension_averages": {
        "actionability": {"average": 21.4, "max": 25, "percentage": 85.6},
        "completeness": {"average": 22.1, "max": 25, "percentage": 88.4},
        "consistency": {"average": 13.8, "max": 15, "percentage": 92.0},
        "parsability": {"average": 14.2, "max": 15, "percentage": 94.7},
        "token_efficiency": {"average": 8.9, "max": 10, "percentage": 89.0},
        "staleness": {"average": 9.1, "max": 10, "percentage": 91.0}
    },
    "critical_analysis": {
        "zero_issues": 98,
        "low_issues": 10,
        "high_issues": 5,
        "zero_percentage": 87.0,
        "low_percentage": 9.0,
        "high_percentage": 4.0
    },
    "priority_tiers": {
        "priority_1": [...],  # List of rules with score <60
        "priority_2": [...],  # List of rules with score 60-79
        "priority_3": [...],  # List of rules with score 80-89
        "priority_4": [...]   # List of rules with score 90-100
    },
    "failed_reviews": [...],  # List of failed reviews with error messages
    "all_reviews": [...]      # Complete list for appendix
}
```

## Error Handling

### Missing Score in Review File

**Cause:** Review file generated but doesn't contain expected score format

**Action:**
1. Log warning: "Could not extract score from <review_path>"
2. Use default: overall_score = None, verdict = "PARSE_ERROR"
3. Include in failed_reviews section

### Missing Dimension Scores

**Cause:** Review file missing dimension score table

**Action:**
1. Use empty dict for dimensions: `{}`
2. Skip this review in dimension average calculations
3. Continue processing (non-fatal)

### Empty Results List

**Cause:** All reviews failed

**Action:**
1. Return summary_data with zero stats
2. Report in master summary: "No successful reviews"
3. List all failed reviews with error messages

## Performance Notes

- Only reads first 150 lines of each review file (context efficient)
- No full review content loaded into memory
- Regex parsing is fast (<1ms per file)
- Total aggregation time: <5 seconds for 113 reviews

## Integration with Next Workflow

**Output of this workflow** → **Input to summary-report.md**

The summary_data structure produced by this workflow is used by the summary report workflow to generate the master markdown report with prioritized recommendations.

## Testing Checklist

- [ ] Extracts scores correctly from review files
- [ ] Calculates averages accurately
- [ ] Groups by priority tiers correctly
- [ ] Handles missing scores gracefully
- [ ] Dimension parsing works for all 6 dimensions
- [ ] Critical issues counted accurately
- [ ] Failed reviews tracked with error messages
- [ ] Context efficient (only first 150 lines read)
