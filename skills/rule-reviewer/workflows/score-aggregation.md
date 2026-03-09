# Score Aggregation Workflow

Merge dimension results into final review score and generate unified report.

## Overview

> **Scoring Rubric v2.0:** 6 scored dimensions, 100 points total

This workflow handles:
1. Combining 6 dimension scores
2. Applying the scoring formula
3. Applying hard caps (Rule Size, Blocking Issues)
4. Detecting critical dimension overrides
5. Handling partial results
6. Generating the final review document

## Scoring Formula

```
Points = Raw Score (0-10) × Weight
```

| Dimension | Weight | Max Points |
|-----------|--------|------------|
| Actionability | 3.0 | 30 |
| Rule Size | 2.5 | 25 |
| Parsability | 1.5 | 15 |
| Completeness | 1.5 | 15 |
| Consistency | 1.0 | 10 |
| Cross-Agent Consistency | 0.5 | 5 |
| **Total** | **10** | **100** |

**Informational Only (not scored):**
- Token Efficiency - Findings reported in recommendations
- Staleness - Findings reported in recommendations

## Hard Caps

```python
def apply_hard_caps(total_score: float, line_count: int, blocking_issues: int) -> tuple:
    """Apply hard caps for oversized rules and blocking issues."""
    
    capped_score = total_score
    cap_reason = None
    
    # Rule Size hard caps
    if line_count > 700:
        capped_score = min(capped_score, 50)
        cap_reason = f">700 lines ({line_count}) - capped at 50/100"
    elif line_count > 600:
        capped_score = min(capped_score, 70)
        cap_reason = f">600 lines ({line_count}) - capped at 70/100"
    
    # Blocking issues hard caps
    if blocking_issues >= 10:
        return (capped_score, "NOT_EXECUTABLE", f"≥10 blocking issues ({blocking_issues})")
    elif blocking_issues >= 6:
        capped_score = min(capped_score, 80)
        if not cap_reason:
            cap_reason = f"≥6 blocking issues ({blocking_issues}) - capped at 80/100"
    
    return (capped_score, None, cap_reason)
```

## Aggregation Function

```python
def aggregate_dimension_results(dimension_results: list) -> dict:
    """Combine 6 dimension worksheets into final review."""
    
    total_score = 0
    worksheets = []
    failed_dimensions = []
    
    # Weight mapping for v2.0
    weights = {
        'actionability': 3.0,
        'rule_size': 2.5,
        'parsability': 1.5,
        'completeness': 1.5,
        'consistency': 1.0,
        'cross_agent_consistency': 0.5
    }
    
    for result in dimension_results:
        if result.get('status') == 'failed' or result.get('status') == 'timeout':
            failed_dimensions.append({
                'dimension': result['dimension'],
                'weight': weights.get(result['dimension'], 1),
                'max_points': weights.get(result['dimension'], 1) * 10,
                'status': result.get('status'),
                'error': result.get('error')
            })
            continue
        
        # Apply formula: Raw × Weight
        raw_score = result.get('raw_score', 0)
        weight = weights.get(result['dimension'], 1)
        points = raw_score * weight
        max_points = weight * 10
        
        total_score += points
        
        worksheets.append({
            'dimension': result['dimension'],
            'raw_score': raw_score,
            'weight': weight,
            'points': round(points, 1),
            'max_points': max_points,
            'tier': result.get('tier', 'Unknown'),
            'evidence': result.get('evidence', []),
            'issues_found': result.get('issues_found', []),
            'issues_deferred': result.get('issues_deferred', [])
        })
    
    # Calculate max possible score based on completed dimensions
    completed_max = sum(w['max_points'] for w in worksheets)
    full_max = 100  # Always 100 for reference (v2.0)
    
    return {
        'total_score': round(total_score, 1),
        'max_score': full_max,
        'completed_max': completed_max,
        'worksheets': worksheets,
        'failed_dimensions': failed_dimensions,
        'is_partial': len(failed_dimensions) > 0
    }
```

## Critical Dimension Override

```python
def apply_critical_override(aggregated: dict) -> dict:
    """Apply critical dimension override rule."""
    
    # Find Actionability and Completeness scores
    actionability_score = None
    completeness_score = None
    
    for worksheet in aggregated['worksheets']:
        if worksheet['dimension'] == 'actionability':
            actionability_score = worksheet['raw_score']
        elif worksheet['dimension'] == 'completeness':
            completeness_score = worksheet['raw_score']
    
    # Critical override: If both Actionability ≤4/10 AND Completeness ≤4/10
    # → NOT_EXECUTABLE regardless of total score
    override_triggered = False
    if actionability_score is not None and completeness_score is not None:
        if actionability_score <= 4 and completeness_score <= 4:
            override_triggered = True
            aggregated['verdict'] = 'NOT_EXECUTABLE'
            aggregated['override_reason'] = (
                f"Critical dimension override: Actionability ({actionability_score}/10) "
                f"and Completeness ({completeness_score}/10) both ≤4"
            )
    
    if not override_triggered:
        aggregated['verdict'] = determine_verdict(aggregated['total_score'])
        aggregated['override_reason'] = None
    
    return aggregated
```

## Verdict Determination

```python
def determine_verdict(total_score: float) -> str:
    """Determine verdict based on 100-point scale (v2.0)."""
    
    if total_score >= 90:
        return "EXECUTABLE"
    elif total_score >= 75:
        return "EXECUTABLE_WITH_REFINEMENTS"
    elif total_score >= 50:
        return "NEEDS_REFINEMENT"
    else:
        return "NOT_EXECUTABLE"
```

| Score Range | Verdict | Description |
|-------------|---------|-------------|
| 90-100 | EXECUTABLE | Production-ready |
| 75-89 | EXECUTABLE_WITH_REFINEMENTS | Good, minor fixes |
| 50-74 | NEEDS_REFINEMENT | Needs work |
| <50 | NOT_EXECUTABLE | Major issues |

## Partial Results Handling

When fewer than 6 dimensions complete successfully:

```python
def aggregate_with_partial_results(dimension_results: list) -> dict:
    """Aggregate results even when some dimensions failed (v2.0)."""
    
    completed = [r for r in dimension_results if r.get('status') == 'completed']
    failed = [r for r in dimension_results if r.get('status') != 'completed']
    
    # Calculate partial score using v2.0 weights
    completed_weight = sum(r['weight'] for r in completed)
    partial_score = sum(r['raw_score'] * r['weight'] for r in completed)
    
    # Extrapolate if we have enough data
    if len(completed) >= 3:
        # Scale up to 100-point max
        extrapolated_score = (partial_score / completed_weight) * 100
    else:
        extrapolated_score = None
    
    confidence = "high" if len(completed) >= 5 else "medium" if len(completed) >= 3 else "low"
    
    report = {
        "status": "partial" if failed else "complete",
        "completed_dimensions": len(completed),
        "failed_dimensions": len(failed),
        "failed_dimension_names": [r['dimension'] for r in failed],
        "partial_score": round(partial_score, 1),
        "partial_max": completed_weight,
        "extrapolated_score": round(extrapolated_score, 1) if extrapolated_score else None,
        "confidence": confidence,
        "disclaimer": None
    }
    
    if failed:
        report["disclaimer"] = (
            f"WARNING: {len(failed)} dimensions failed ({', '.join(report['failed_dimension_names'])}). "
            f"Score of {report['partial_score']}/{report['partial_max']} is incomplete. "
        )
        if extrapolated_score:
            report["disclaimer"] += f"Extrapolated: ~{report['extrapolated_score']}/100 ({confidence} confidence)"
    
    return report
```

## Rule Size Flag Handling

```python
def apply_rule_size_flags(aggregated: dict) -> dict:
    """Apply Rule Size flags to aggregated results (v2.0)."""
    
    rule_size_result = None
    for worksheet in aggregated['worksheets']:
        if worksheet['dimension'] == 'rule_size':
            rule_size_result = worksheet
            break
    
    if not rule_size_result:
        return aggregated
    
    # v2.0 flags: SPLIT_RECOMMENDED, SPLIT_REQUIRED, NOT_DEPLOYABLE, BLOCKED
    flag = None
    for issue in rule_size_result.get('issues_found', []):
        if issue.get('description') in ['SPLIT_RECOMMENDED', 'SPLIT_REQUIRED', 'NOT_DEPLOYABLE', 'BLOCKED']:
            flag = issue['description']
            break
    
    if flag:
        aggregated['rule_size_flag'] = flag
        
        if flag == 'BLOCKED':
            aggregated['verdict'] = 'NOT_EXECUTABLE'
            aggregated['override_reason'] = f"Rule Size flag: BLOCKED (≥10 blocking issues)"
        elif flag == 'NOT_DEPLOYABLE':
            aggregated['verdict'] = 'NOT_EXECUTABLE'
            aggregated['override_reason'] = f"Rule Size flag: NOT_DEPLOYABLE (>700 lines)"
        elif flag == 'SPLIT_REQUIRED':
            if aggregated['verdict'] in ['EXECUTABLE', 'EXECUTABLE_WITH_REFINEMENTS']:
                aggregated['verdict'] = 'NEEDS_REFINEMENT'
                aggregated['rule_size_warning'] = f"Deployment blocked until split (>600 lines)"
        # SPLIT_RECOMMENDED is advisory only - no verdict change
    
    return aggregated
```

## Generate Review Document

```python
def generate_review_document(aggregated: dict, params: dict, context: dict) -> str:
    """Generate the final review markdown document."""
    
    # Build score table
    score_table = "| Dimension | Raw | Points | Max | Tier |\n"
    score_table += "|-----------|-----|--------|-----|------|\n"
    
    for ws in aggregated['worksheets']:
        score_table += f"| {ws['dimension'].replace('_', ' ').title()} | {ws['raw_score']}/10 | {ws['points']} | {ws['max_points']} | {ws['tier']} |\n"
    
    # Add failed dimensions
    for fd in aggregated.get('failed_dimensions', []):
        score_table += f"| {fd['dimension'].replace('_', ' ').title()} | FAILED | - | {fd['max_points']} | {fd['status']} |\n"
    
    # Build document
    doc = f"""# Rule Review: {params['target_file']}

**Review Date:** {params['review_date']}
**Model:** {params.get('model', 'unknown')}
**Mode:** {params.get('review_mode', 'FULL')}
**Execution Mode:** parallel

## Executive Summary

**Total Score:** {aggregated['total_score']}/{aggregated['max_score']}
**Verdict:** {aggregated['verdict']}
"""

    if aggregated.get('override_reason'):
        doc += f"\n**Override:** {aggregated['override_reason']}\n"
    
    if aggregated.get('rule_size_flag'):
        doc += f"\n**Rule Size Flag:** {aggregated['rule_size_flag']}\n"
    
    if aggregated.get('is_partial'):
        doc += f"\n⚠️ **Partial Review:** {len(aggregated['failed_dimensions'])} dimensions failed\n"

    doc += f"""
## Dimension Scores

{score_table}

## Dimension Analysis
"""

    # Add each dimension's details
    for ws in aggregated['worksheets']:
        doc += f"""
### {ws['dimension'].replace('_', ' ').title()}

**Score:** {ws['raw_score']}/10 ({ws['points']}/{ws['max_points']} points)
**Tier:** {ws['tier']}

**Evidence:**
"""
        for ev in ws.get('evidence', [])[:5]:  # Top 5 evidence items
            doc += f"- Line {ev.get('line', 'N/A')}: `{ev.get('pattern', '')}` - \"{ev.get('quote', '')[:100]}\"\n"
        
        if ws.get('issues_found'):
            doc += "\n**Issues:**\n"
            for issue in ws['issues_found'][:5]:
                severity = issue.get('severity', 'warning')
                doc += f"- [{severity.upper()}] Line {issue.get('line', 'N/A')}: {issue.get('description', '')}\n"

    # Add recommendations section
    doc += """
## Recommendations

"""
    # Collect all issues sorted by severity
    all_issues = []
    for ws in aggregated['worksheets']:
        for issue in ws.get('issues_found', []):
            all_issues.append({
                'dimension': ws['dimension'],
                'severity': issue.get('severity', 'warning'),
                'line': issue.get('line'),
                'description': issue.get('description')
            })
    
    blocking = [i for i in all_issues if i['severity'] == 'blocking']
    warnings = [i for i in all_issues if i['severity'] == 'warning']
    
    if blocking:
        doc += "### Blocking Issues\n\n"
        for i, issue in enumerate(blocking[:10], 1):
            doc += f"{i}. **{issue['dimension']}** (Line {issue['line']}): {issue['description']}\n"
    
    if warnings:
        doc += "\n### Warnings\n\n"
        for i, issue in enumerate(warnings[:10], 1):
            doc += f"{i}. **{issue['dimension']}** (Line {issue['line']}): {issue['description']}\n"

    doc += f"""
## Post-Review Checklist

- [{'x' if aggregated['total_score'] >= 50 else ' '}] Score above minimum threshold (50)
- [{'x' if not aggregated.get('override_reason') else ' '}] No critical overrides triggered
- [{'x' if not aggregated.get('is_partial') else ' '}] All dimensions evaluated
- [{'x' if aggregated.get('rule_size_flag') not in ['NOT_DEPLOYABLE', 'BLOCKED'] else ' '}] Rule size within limits

## Conclusion

This rule scored **{aggregated['total_score']}/100** and received verdict **{aggregated['verdict']}**.

---
*Generated by rule-reviewer (parallel execution mode)*
*Review completed: {params['review_date']}*
"""

    return doc
```

## Output File Path

```python
def get_output_path(params: dict) -> str:
    """Generate output file path with no-overwrite safety."""
    
    output_root = params.get('output_root', 'reviews/')
    target_file = params['target_file']
    model = params.get('model', 'unknown')
    review_date = params['review_date']
    overwrite = params.get('overwrite', False)
    
    # Extract rule name from path
    import os
    rule_name = os.path.splitext(os.path.basename(target_file))[0]
    
    base_path = f"{output_root}/rule-reviews/{rule_name}-{model}-{review_date}"
    
    if overwrite:
        return f"{base_path}.md"
    
    # No-overwrite: increment if exists
    if not os.path.exists(f"{base_path}.md"):
        return f"{base_path}.md"
    
    for i in range(1, 100):
        path = f"{base_path}-{i:02d}.md"
        if not os.path.exists(path):
            return path
    
    raise ValueError(f"Maximum review versions exceeded for {rule_name}")
```

## Version History

- **v1.0.0:** Initial score aggregation workflow for parallel execution
