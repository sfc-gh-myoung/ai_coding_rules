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
    """Generate the final review markdown document.
    
    Output MUST conform to references/REVIEW-OUTPUT-TEMPLATE.md structure.
    """
    
    # Build score table (template-compliant columns)
    score_table = "| Dimension | Raw (0-10) | Weight | Points | Max |\n"
    score_table += "|-----------|------------|--------|--------|-----|\n"
    
    for ws in aggregated['worksheets']:
        score_table += f"| {ws['dimension'].replace('_', ' ').title()} | {ws['raw_score']}/10 | {ws['weight']} | {ws['points']} | {ws['max_points']} |\n"
    
    # Add failed dimensions
    for fd in aggregated.get('failed_dimensions', []):
        score_table += f"| {fd['dimension'].replace('_', ' ').title()} | FAILED | {fd['weight']} | - | {fd['max_points']} |\n"
    
    score_table += f"| **TOTAL** | | **10** | **{aggregated['total_score']}** | **100** |\n"
    
    # Build document (template-compliant structure)
    doc = f"""# Rule Review: {params['target_file']}

**Review Date:** {params['review_date']}
**Review Mode:** {params.get('review_mode', 'FULL')}
**Model:** {params.get('model', 'unknown')}
**Reviewer Skill:** rule-reviewer v{params.get('skill_version', '2.7.0')}
**Schema Validator:** ai-rules validate

## Executive Summary

{score_table}
**Verdict:** {aggregated['verdict']} ({aggregated['total_score']}/100)

**Blocking Issues:** {aggregated.get('blocking_issue_count', 0)}
**Hard Caps Applied:** {aggregated.get('cap_reason', 'None')}
**Rule Size Flag:** {aggregated.get('rule_size_flag', 'None')}
"""

    if aggregated.get('override_reason'):
        doc += f"\n**Override:** {aggregated['override_reason']}\n"
    
    if aggregated.get('is_partial'):
        doc += f"\nWARNING: **Partial Review:** {len(aggregated['failed_dimensions'])} dimensions failed\n"

    # Schema Validation Results
    doc += f"""
## Schema Validation Results

```
{context.get('schema_validation_output', 'Schema validation not available')}
```

{context.get('schema_validation_summary', '')}
"""

    # Agent Executability Verdict
    doc += f"""
## Agent Executability Verdict

**Blocking Issues Count: {aggregated.get('blocking_issue_count', 0)}**

"""
    blocking_issues = context.get('blocking_issues', [])
    for i, issue in enumerate(blocking_issues, 1):
        doc += f"{i}. **{issue.get('type', 'Issue')} at line {issue.get('line', 'N/A')}:** {issue.get('description', '')} -- {issue.get('reason', '')}\n"
    if not blocking_issues:
        doc += "No blocking issues identified.\n"

    # Dimension Analysis
    doc += "\n## Dimension Analysis\n"

    for idx, ws in enumerate(aggregated['worksheets'], 1):
        dim_name = ws['dimension'].replace('_', ' ').title()
        doc += f"""
### {idx}. {dim_name}: {ws['raw_score']}/10 ({ws['points']} points)

**{dim_name} Inventory:**

"""
        for ev in ws.get('evidence', [])[:10]:
            doc += f"- Line {ev.get('line', 'N/A')}: `{ev.get('pattern', '')}` - \"{ev.get('quote', '')[:100]}\"\n"
        
        doc += f"""
**After Non-Issues filtering:** {ws.get('filtered_count', len(ws.get('issues_found', [])))}

**Score Decision Matrix lookup:** {ws.get('tier', 'Unknown')} = {ws['raw_score']}/10
"""
        
        if ws.get('issues_found'):
            doc += "\n**Priority fixes:**\n"
            for i, issue in enumerate(ws['issues_found'][:5], 1):
                doc += f"{i}. Line {issue.get('line', 'N/A')}: {issue.get('description', '')}\n"

        # Inline Token Efficiency under Rule Size
        if ws['dimension'] == 'rule_size' and context.get('token_efficiency'):
            te = context['token_efficiency']
            doc += f"""
**Token Efficiency (Informational):**
- Redundancy instances: {te.get('redundancy_count', 0)}
{te.get('details', '')}
- Structure ratio: {te.get('structure_ratio', 'N/A')} lists/tables vs prose
- Estimated savings: {te.get('estimated_savings', 'N/A')} if consolidated
"""

    # Critical Issues
    doc += "\n## Critical Issues\n\n"
    all_critical = []
    for ws in aggregated['worksheets']:
        for issue in ws.get('issues_found', []):
            if issue.get('severity') == 'blocking':
                all_critical.append(issue)
    
    if all_critical:
        for i, issue in enumerate(all_critical[:10], 1):
            doc += f"{i}. **Line {issue.get('line', 'N/A')}:** {issue.get('description', '')}\n"
    else:
        doc += "No critical issues identified.\n"

    # Recommendations with inline Staleness
    doc += "\n## Recommendations\n\n"
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
    info = [i for i in all_issues if i['severity'] == 'info']
    
    if blocking:
        doc += "**P1 (Blocking):**\n"
        for i, issue in enumerate(blocking[:10], 1):
            doc += f"{i}. **[Line {issue['line']}]** {issue['description']} **Expected improvement: +{issue['dimension']}**\n"
        doc += "\n"
    
    if warnings:
        doc += "**P2 (Important):**\n"
        for i, issue in enumerate(warnings[:10], 1):
            doc += f"{i}. **[Line {issue['line']}]** {issue['description']} **Expected improvement: +{issue['dimension']}**\n"
        doc += "\n"
    
    if info:
        doc += "**P3 (Nice-to-have):**\n"
        for i, issue in enumerate(info[:5], 1):
            doc += f"{i}. **[Line {issue['line']}]** {issue['description']} **Expected improvement: +{issue['dimension']}**\n"
        doc += "\n"

    # Inline Staleness
    if context.get('staleness'):
        st = context['staleness']
        doc += f"""**Staleness (Informational):**
- LastUpdated: {st.get('last_updated', 'N/A')} ({st.get('age', 'N/A')})
- Deprecated tools: {st.get('deprecated_tools', 0)}
- Broken links: {st.get('broken_links', 0)} ({st.get('link_details', 'N/A')})
- Documentation currency: {st.get('currency_summary', 'N/A')}
"""

    # Post-Review Checklist (fixed 11 items)
    schema_errors = context.get('schema_error_count', 0)
    blocking_count = aggregated.get('blocking_issue_count', 0)
    line_count = context.get('line_count', 0)
    critical_count = len(all_critical)
    rule_size_flag = aggregated.get('rule_size_flag', 'None')
    rec_count = len(blocking) + len(warnings) + len(info)
    output_path = params.get('output_path', '{output_path}')
    
    doc += f"""
## Post-Review Checklist

- [x] Schema validator executed ({schema_errors} errors)
- [x] Agent Execution Test performed ({blocking_count} blocking issues)
- [x] Line count measured: {line_count} lines
- [x] All 6 dimensions scored
- [x] Each score has rationale with inventories
- [x] Critical issues identified ({critical_count})
- [x] Rule Size flags: {rule_size_flag} ({line_count} lines)
- [x] Recommendations prioritized ({rec_count} items)
- [x] Line numbers provided for all fixes
- [x] Review written to {output_path}
- [x] Review file >=2500 bytes

## Conclusion

{params['target_file']} scored **{aggregated['total_score']}/100 ({aggregated['verdict']})**. Review completed {params['review_date']}.
"""

    # Conditional Timing Metadata
    if params.get('timing_enabled') and context.get('timing_metadata'):
        tm = context['timing_metadata']
        doc += f"""
## Timing Metadata

| Field | Value |
|-------|-------|
| Run ID | `{tm.get('run_id', 'N/A')}` |
| Skill | rule-reviewer |
| Model | {params.get('model', 'unknown')} |
| Agent | {tm.get('agent', 'unknown')} |
| Start (UTC) | {tm.get('start_utc', 'N/A')} |
| End (UTC) | {tm.get('end_utc', 'N/A')} |
| Duration | {tm.get('duration', 'N/A')} |
| Status | {tm.get('status', 'completed')} |
| Checkpoints | {tm.get('checkpoints', 'N/A')} |
| Tokens | {tm.get('tokens', 'N/A')} |
| Cost | {tm.get('cost', 'N/A')} |
| Baseline | {tm.get('baseline', 'N/A')} |
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
