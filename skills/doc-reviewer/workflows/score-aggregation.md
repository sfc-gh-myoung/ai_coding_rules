# Score Aggregation Workflow

## Overview

This workflow combines results from 6 dimension sub-agents into a final documentation review score. It applies the scoring formula, validates calculations, and generates the unified review document.

---

## Scoring Formula

**Per Dimension:**
```
Points = Raw Score (0-10) × (Weight / 2)
```

**Total:**
```
Total Score = Sum of all dimension points
Max Score = 100
```

---

## Dimension Weights

| Dimension | Weight | Max Points | Category |
|-----------|--------|------------|----------|
| Accuracy | 5 | 25 | Critical |
| Completeness | 5 | 25 | Critical |
| Clarity | 4 | 20 | Important |
| Structure | 3 | 15 | Important |
| Staleness | 2 | 10 | Standard |
| Consistency | 1 | 5 | Standard |
| **TOTAL** | **20** | **100** | |

---

## Aggregation Functions

### Primary Aggregation

```python
def aggregate_dimension_results(dimension_results: list) -> dict:
    """Combine 6 dimension worksheets into final review score.
    
    Args:
        dimension_results: List of parsed JSON results from sub-agents
        
    Returns:
        dict with total_score, max_score, worksheets, and verdict
    """
    
    total_score = 0
    worksheets = []
    
    for result in dimension_results:
        # Extract values
        dimension = result['dimension']
        raw_score = result['raw_score']
        weight = result.get('weight', get_weight_for_dimension(dimension))
        
        # Apply formula: Raw × (Weight/2)
        points = raw_score * (weight / 2)
        max_points = 10 * (weight / 2)  # Max raw is 10
        
        # Validate calculation
        assert 0 <= raw_score <= 10, f"Invalid raw_score: {raw_score}"
        assert points <= max_points, f"Points {points} exceed max {max_points}"
        
        total_score += points
        
        worksheets.append({
            'dimension': dimension,
            'raw_score': raw_score,
            'weight': weight,
            'points': points,
            'max_points': max_points,
            'evidence': result.get('evidence', []),
            'issues_found': result.get('issues_found', []),
            'issues_deferred': result.get('issues_deferred', []),
            'verification_table': result.get('verification_table', ''),
            'score_calculation': result.get('score_calculation', {})
        })
    
    # Round total score to 1 decimal
    total_score = round(total_score, 1)
    
    # Check for critical dimension overrides
    overrides = check_critical_overrides(worksheets)
    
    # Apply overrides if needed
    final_verdict = get_verdict(total_score)
    if overrides['applied']:
        final_verdict = overrides['overridden_verdict']
    
    return {
        'total_score': total_score,
        'max_score': 100,
        'worksheets': worksheets,
        'verdict': final_verdict,
        'critical_dimension_overrides': overrides
    }


def get_weight_for_dimension(dimension: str) -> int:
    """Return weight for dimension name."""
    WEIGHTS = {
        'accuracy': 5,
        'completeness': 5,
        'clarity': 4,
        'structure': 3,
        'staleness': 2,
        'consistency': 1
    }
    return WEIGHTS.get(dimension.lower(), 1)
```

### Verdict Determination

```python
def get_verdict(score: float) -> str:
    """Map total score to verdict.
    
    Score Ranges:
    - 90-100: EXCELLENT - High-quality documentation
    - 80-89: GOOD - Minor improvements needed
    - 60-79: NEEDS_IMPROVEMENT - Significant updates required
    - 40-59: POOR - Major revision needed
    - <40: INADEQUATE - Rewrite from scratch
    """
    
    if score >= 90:
        return "EXCELLENT"
    elif score >= 80:
        return "GOOD"
    elif score >= 60:
        return "NEEDS_IMPROVEMENT"
    elif score >= 40:
        return "POOR"
    else:
        return "INADEQUATE"
```

### Critical Dimension Overrides

```python
def check_critical_overrides(worksheets: list) -> dict:
    """Check if critical dimension scores override verdict.
    
    Override Rules:
    - Accuracy ≤4/10 → Cap total at 60 (Minimum NEEDS_IMPROVEMENT)
    - Completeness ≤4/10 → Cap total at 60 (Minimum NEEDS_IMPROVEMENT)
    - Both ≤4/10 → Cap total at 40 (POOR)
    """
    
    CRITICAL_DIMENSIONS = ['accuracy', 'completeness']
    CRITICAL_THRESHOLD = 4
    
    overrides = {
        'applied': False,
        'reason': None,
        'original_verdict': None,
        'overridden_verdict': None,
        'cap_applied': None
    }
    
    critical_failures = []
    
    for ws in worksheets:
        if ws['dimension'].lower() in CRITICAL_DIMENSIONS:
            if ws['raw_score'] <= CRITICAL_THRESHOLD:
                critical_failures.append({
                    'dimension': ws['dimension'],
                    'raw_score': ws['raw_score']
                })
    
    if len(critical_failures) >= 2:
        overrides['applied'] = True
        overrides['reason'] = f"Both critical dimensions below threshold: {[f['dimension'] for f in critical_failures]}"
        overrides['overridden_verdict'] = "POOR"
        overrides['cap_applied'] = 40
    elif len(critical_failures) == 1:
        overrides['applied'] = True
        overrides['reason'] = f"Critical dimension below threshold: {critical_failures[0]['dimension']} ({critical_failures[0]['raw_score']}/10)"
        overrides['overridden_verdict'] = "NEEDS_IMPROVEMENT"
        overrides['cap_applied'] = 60
    
    return overrides
```

---

## Validation Functions

### Result Completeness Check

```python
def validate_results_complete(results: list) -> tuple:
    """Ensure all 6 dimensions have valid results.
    
    Returns:
        (is_valid: bool, missing_dimensions: list)
    """
    
    REQUIRED_DIMENSIONS = [
        'accuracy', 'completeness', 'clarity', 
        'structure', 'staleness', 'consistency'
    ]
    
    present_dimensions = [r['dimension'].lower() for r in results]
    missing = [d for d in REQUIRED_DIMENSIONS if d not in present_dimensions]
    
    return (len(missing) == 0, missing)
```

### Score Calculation Verification

```python
def verify_score_calculations(aggregated: dict) -> list:
    """Verify all score calculations are correct.
    
    Returns:
        list of calculation errors (empty if all correct)
    """
    
    errors = []
    
    recalculated_total = 0
    
    for ws in aggregated['worksheets']:
        expected_points = ws['raw_score'] * (ws['weight'] / 2)
        
        if abs(ws['points'] - expected_points) > 0.01:
            errors.append({
                'dimension': ws['dimension'],
                'expected': expected_points,
                'actual': ws['points'],
                'error': 'Points calculation mismatch'
            })
        
        if ws['points'] > ws['max_points']:
            errors.append({
                'dimension': ws['dimension'],
                'points': ws['points'],
                'max': ws['max_points'],
                'error': 'Points exceed maximum'
            })
        
        recalculated_total += ws['points']
    
    if abs(aggregated['total_score'] - recalculated_total) > 0.1:
        errors.append({
            'expected_total': recalculated_total,
            'actual_total': aggregated['total_score'],
            'error': 'Total score mismatch'
        })
    
    return errors
```

---

## Output Formatting

### Generate Score Breakdown Table

```python
def format_score_breakdown(worksheets: list, total_score: float) -> str:
    """Generate markdown table of score breakdown."""
    
    table = """| Dimension | Raw | Weight | Points | Max |
|-----------|-----|--------|--------|-----|
"""
    
    # Sort by weight (highest first)
    sorted_ws = sorted(worksheets, key=lambda x: x['weight'], reverse=True)
    
    for ws in sorted_ws:
        table += f"| {ws['dimension'].title()} | {ws['raw_score']}/10 | ×{ws['weight']/2} | {ws['points']} | {ws['max_points']} |\n"
    
    table += f"| **TOTAL** | | | **{total_score}** | **100** |\n"
    
    return table
```

### Generate Dimension Details

```python
def format_dimension_details(worksheets: list) -> str:
    """Generate detailed section for each dimension."""
    
    output = ""
    
    # Sort by weight (highest first)
    sorted_ws = sorted(worksheets, key=lambda x: x['weight'], reverse=True)
    
    for ws in sorted_ws:
        output += f"\n---\n\n### {ws['dimension'].title()}: {ws['raw_score']}/10 ({ws['points']} points)\n\n"
        
        # Score calculation
        if ws.get('score_calculation'):
            calc = ws['score_calculation']
            output += f"**Tier:** {calc.get('tier', 'N/A')}\n"
            output += f"**Primary Metric:** {calc.get('primary_metric', 'N/A')}\n\n"
        
        # Verification table (if present)
        if ws.get('verification_table'):
            output += "**Verification Table:**\n"
            output += ws['verification_table'] + "\n\n"
        
        # Evidence
        if ws.get('evidence'):
            output += "**Evidence:**\n"
            for ev in ws['evidence'][:5]:
                output += f"- Line {ev.get('line', '?')}: {ev.get('pattern', '?')} - \"{ev.get('quote', '')[:50]}...\"\n"
            output += "\n"
        
        # Issues found
        if ws.get('issues_found'):
            output += f"**Issues Found ({len(ws['issues_found'])}):**\n"
            for issue in ws['issues_found'][:5]:
                severity = issue.get('severity', 'MEDIUM')
                output += f"- [{severity}] Line {issue.get('line', '?')}: {issue.get('description', '')}\n"
            if len(ws['issues_found']) > 5:
                output += f"- ... and {len(ws['issues_found']) - 5} more\n"
            output += "\n"
        
        # Issues deferred
        if ws.get('issues_deferred'):
            output += f"**Issues Deferred ({len(ws['issues_deferred'])}):**\n"
            for issue in ws['issues_deferred']:
                output += f"- Line {issue.get('line', '?')}: → {issue.get('owned_by', '?')} ({issue.get('overlap_rule', '')})\n"
            output += "\n"
    
    return output
```

---

## Edge Cases

### Handle Empty Results

```python
def handle_empty_results(results: list) -> list:
    """Fill in defaults for missing dimensions."""
    
    REQUIRED = [
        'accuracy', 'completeness', 'clarity', 
        'structure', 'staleness', 'consistency'
    ]
    
    present = {r['dimension'].lower() for r in results}
    
    for dim in REQUIRED:
        if dim not in present:
            results.append({
                'dimension': dim,
                'raw_score': 0,
                'weight': get_weight_for_dimension(dim),
                'evidence': [],
                'issues_found': [],
                'issues_deferred': [],
                'verification_table': '',
                'validation': 'missing'
            })
    
    return results
```

### Handle Partial Results

```python
def handle_partial_results(result: dict) -> dict:
    """Ensure result has all required fields."""
    
    defaults = {
        'dimension': 'unknown',
        'raw_score': 0,
        'evidence': [],
        'issues_found': [],
        'issues_deferred': [],
        'verification_table': '',
        'worksheet_summary': {},
        'score_calculation': {}
    }
    
    for key, default_value in defaults.items():
        if key not in result:
            result[key] = default_value
    
    return result
```

---

## Integration Example

```python
def aggregate_and_format_review(dimension_results: list) -> tuple:
    """Full aggregation pipeline.
    
    Returns:
        (aggregated: dict, formatted: str)
    """
    
    # Step 1: Handle missing/partial results
    results = handle_empty_results(dimension_results)
    results = [handle_partial_results(r) for r in results]
    
    # Step 2: Aggregate scores
    aggregated = aggregate_dimension_results(results)
    
    # Step 3: Verify calculations
    errors = verify_score_calculations(aggregated)
    if errors:
        print(f"WARNING: {len(errors)} calculation errors detected")
        for e in errors:
            print(f"  - {e}")
    
    # Step 4: Apply critical overrides
    if aggregated['critical_dimension_overrides']['applied']:
        override = aggregated['critical_dimension_overrides']
        print(f"OVERRIDE: {override['reason']}")
        # Verdict already applied in aggregate_dimension_results
    
    # Step 5: Format output
    formatted = format_score_breakdown(aggregated['worksheets'], aggregated['total_score'])
    formatted += format_dimension_details(aggregated['worksheets'])
    
    return (aggregated, formatted)
```

---

## Review Document Generation

```python
def generate_review_document(
    doc_path: str,
    final_score: dict,
    results: list,
    violations: list,
    model: str,
    date: str
) -> str:
    """Generate final review document."""
    
    doc_name = os.path.basename(doc_path).replace('.md', '')
    
    doc = f"""# Documentation Review: {doc_name}

**Date:** {date}
**Model:** {model}
**Mode:** FULL (Parallel Execution)
**Target:** {doc_path}

---

## Summary

| Score | Verdict |
|-------|---------|
| **{final_score['total_score']}/100** | **{final_score['verdict']}** |

"""
    
    # Add critical override note if applicable
    if final_score['critical_dimension_overrides']['applied']:
        override = final_score['critical_dimension_overrides']
        doc += f"""**Override Applied:** {override['reason']}

"""
    
    doc += """---

## Score Breakdown

"""
    doc += format_score_breakdown(final_score['worksheets'], final_score['total_score'])
    
    # Add dimension details
    doc += format_dimension_details(final_score['worksheets'])
    
    # Add overlap violations if any
    if violations:
        doc += "\n---\n\n## Overlap Violations\n\n"
        for v in violations:
            doc += f"- Line {v['line']}: {v['pattern']} claimed by {v['claimed_by']}, owned by {v['owned_by']}\n"
    
    # Add priority fixes
    doc += "\n---\n\n## Priority Fixes\n\n"
    all_issues = []
    for ws in final_score['worksheets']:
        for issue in ws.get('issues_found', []):
            issue['from_dimension'] = ws['dimension']
            all_issues.append(issue)
    
    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_issues = sorted(all_issues, key=lambda x: severity_order.get(x.get('severity', 'MEDIUM'), 2))
    
    for i, issue in enumerate(sorted_issues[:5], 1):
        doc += f"{i}. [{issue.get('severity', 'MEDIUM')}] Line {issue.get('line', '?')}: {issue.get('description', '')}\n"
        if issue.get('fix_suggestion'):
            doc += f"   - Fix: {issue['fix_suggestion']}\n"
    
    doc += "\n\n.... Generated with [Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)\n"
    
    return doc
```
