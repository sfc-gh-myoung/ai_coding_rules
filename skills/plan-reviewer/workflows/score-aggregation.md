# Score Aggregation Workflow

## Overview

This workflow combines results from 8 dimension sub-agents into a final plan review score. It applies the scoring formula, validates calculations, and generates the unified review document.

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
| Executability | 20 | 20 | Critical |
| Completeness | 20 | 20 | Critical |
| Success Criteria | 20 | 20 | Critical |
| Scope | 15 | 15 | Critical |
| Dependencies | 10 | 10 | Standard |
| Decomposition | 5 | 5 | Standard |
| Context | 5 | 5 | Standard |
| Risk Awareness | 5 | 5 | Standard |
| **TOTAL** | **100** | **100** | |

---

## Aggregation Functions

### Primary Aggregation

```python
def aggregate_dimension_results(dimension_results: list) -> dict:
    """Combine 8 dimension worksheets into final review score.
    
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
        max_points = weight
        
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
            'score_calculation': result.get('score_calculation', {})
        })
    
    # Round total score to 1 decimal
    total_score = round(total_score, 1)
    
    return {
        'total_score': total_score,
        'max_score': 100,
        'worksheets': worksheets,
        'verdict': get_verdict(total_score),
        'critical_dimension_overrides': check_critical_overrides(worksheets)
    }


def get_weight_for_dimension(dimension: str) -> int:
    """Return weight for dimension name."""
    WEIGHTS = {
        'executability': 20,
        'completeness': 20,
        'success_criteria': 20,
        'scope': 15,
        'dependencies': 10,
        'decomposition': 5,
        'context': 5,
        'risk_awareness': 5
    }
    return WEIGHTS.get(dimension, 5)
```

### Verdict Determination

```python
def get_verdict(score: float) -> str:
    """Map total score to verdict.
    
    Score Ranges:
    - 90-100: EXCELLENT_PLAN - Ready for execution
    - 80-89: GOOD_PLAN - Minor refinements needed
    - 60-79: NEEDS_WORK - Significant refinement required
    - 40-59: POOR_PLAN - Not executable, major revision
    - <40: INADEQUATE_PLAN - Rewrite from scratch
    """
    
    if score >= 90:
        return "EXCELLENT_PLAN"
    elif score >= 80:
        return "GOOD_PLAN"
    elif score >= 60:
        return "NEEDS_WORK"
    elif score >= 40:
        return "POOR_PLAN"
    else:
        return "INADEQUATE_PLAN"
```

### Critical Dimension Overrides

```python
def check_critical_overrides(worksheets: list) -> dict:
    """Check if critical dimension scores override verdict.
    
    Override Rules:
    - Executability ≤4/10 → Minimum NEEDS_WORK
    - Completeness ≤4/10 → Minimum NEEDS_WORK
    - Success Criteria ≤4/10 → Minimum NEEDS_WORK
    - 2+ critical dimensions ≤4/10 → POOR_PLAN
    """
    
    CRITICAL_DIMENSIONS = ['executability', 'completeness', 'success_criteria']
    CRITICAL_THRESHOLD = 4
    
    overrides = {
        'applied': False,
        'reason': None,
        'original_verdict': None,
        'overridden_verdict': None
    }
    
    critical_failures = []
    
    for ws in worksheets:
        if ws['dimension'] in CRITICAL_DIMENSIONS:
            if ws['raw_score'] <= CRITICAL_THRESHOLD:
                critical_failures.append(ws['dimension'])
    
    if len(critical_failures) >= 2:
        overrides['applied'] = True
        overrides['reason'] = f"2+ critical dimensions below threshold: {critical_failures}"
        overrides['overridden_verdict'] = "POOR_PLAN"
    elif len(critical_failures) == 1:
        overrides['applied'] = True
        overrides['reason'] = f"Critical dimension below threshold: {critical_failures[0]}"
        overrides['overridden_verdict'] = "NEEDS_WORK"
    
    return overrides
```

---

## Validation Functions

### Result Completeness Check

```python
def validate_results_complete(results: list) -> tuple:
    """Ensure all 8 dimensions have valid results.
    
    Returns:
        (is_valid: bool, missing_dimensions: list)
    """
    
    REQUIRED_DIMENSIONS = [
        'executability', 'completeness', 'success_criteria', 'scope',
        'dependencies', 'decomposition', 'context', 'risk_awareness'
    ]
    
    present_dimensions = [r['dimension'] for r in results]
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
    
    for ws in worksheets:
        table += f"| {ws['dimension']} | {ws['raw_score']}/10 | ×{ws['weight']/2} | {ws['points']} | {ws['max_points']} |\n"
    
    table += f"| **TOTAL** | | | **{total_score}** | **100** |\n"
    
    return table
```

### Generate Dimension Details

```python
def format_dimension_details(worksheets: list) -> str:
    """Generate detailed section for each dimension."""
    
    output = ""
    
    for ws in worksheets:
        output += f"\n---\n\n### {ws['dimension'].replace('_', ' ').title()}: {ws['raw_score']}/10 ({ws['points']} points)\n\n"
        
        # Score calculation
        if ws.get('score_calculation'):
            calc = ws['score_calculation']
            output += f"**Tier:** {calc.get('tier', 'N/A')}\n"
            output += f"**Primary Metric:** {calc.get('primary_metric', 'N/A')}\n\n"
        
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
        'executability', 'completeness', 'success_criteria', 'scope',
        'dependencies', 'decomposition', 'context', 'risk_awareness'
    ]
    
    present = {r['dimension'] for r in results}
    
    for dim in REQUIRED:
        if dim not in present:
            results.append({
                'dimension': dim,
                'raw_score': 0,
                'weight': get_weight_for_dimension(dim),
                'evidence': [],
                'issues_found': [],
                'issues_deferred': [],
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
        aggregated['verdict'] = override['overridden_verdict']
    
    # Step 5: Format output
    formatted = format_score_breakdown(aggregated['worksheets'], aggregated['total_score'])
    formatted += format_dimension_details(aggregated['worksheets'])
    
    return (aggregated, formatted)
```
