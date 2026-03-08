# Overlap Validator Workflow

## Overview

This workflow validates that no issues are double-counted across dimension worksheets. It cross-references evidence from all 6 sub-agents against the overlap resolution rules in `_overlap-resolution.md`.

---

## Overlap Resolution Rules Summary

From `rubrics/_overlap-resolution.md`, key ownership rules:

| Issue Type | Primary Dimension | NOT Counted In |
|------------|-------------------|----------------|
| Wrong file path | Accuracy | Completeness |
| Broken external link | Staleness | Accuracy |
| Outdated code example | Accuracy | Staleness |
| Missing feature docs | Completeness | Structure |
| Unexplained jargon | Clarity | Completeness |
| Wrong heading level | Structure | Consistency |
| Mixed list markers | Consistency | Structure |
| Deprecated command | Staleness | Accuracy |
| No troubleshooting | Completeness | Structure |
| Long complex sentence | Clarity | Consistency |

---

## Required Dimensions

```python
REQUIRED_DIMENSIONS = [
    'accuracy', 'completeness', 'clarity', 
    'structure', 'staleness', 'consistency'
]
```

---

## Validation Functions

### Primary Validation

```python
def validate_no_overlaps(dimension_results: list, overlap_rules: str) -> list:
    """Ensure no double-counting across dimensions.
    
    Args:
        dimension_results: List of parsed JSON results from sub-agents
        overlap_rules: Content of _overlap-resolution.md
        
    Returns:
        List of violation objects (empty if no overlaps detected)
    """
    
    # Parse overlap rules into lookup structure
    ownership_rules = parse_overlap_rules(overlap_rules)
    
    # Build line citation index
    line_citations = {}  # line_num -> list of {dimension, pattern, quote}
    
    for result in dimension_results:
        dimension = result['dimension'].lower()
        
        for evidence in result.get('evidence', []):
            line = evidence.get('line')
            
            if line is None:
                continue
            
            if line not in line_citations:
                line_citations[line] = []
            
            line_citations[line].append({
                'dimension': dimension,
                'pattern': evidence.get('pattern', ''),
                'quote': evidence.get('quote', ''),
                'category': evidence.get('category', '')
            })
    
    # Detect violations
    violations = []
    
    for line, citations in line_citations.items():
        if len(citations) > 1:
            # Multiple dimensions cite same line
            violation = check_overlap_violation(line, citations, ownership_rules)
            if violation:
                violations.append(violation)
    
    return violations
```

### Parse Overlap Rules

```python
def parse_overlap_rules(overlap_rules: str) -> dict:
    """Parse _overlap-resolution.md into lookup structure.
    
    Returns:
        dict mapping issue patterns to primary dimension
    """
    
    ownership = {}
    
    # Parse table rows
    lines = overlap_rules.split('\n')
    in_table = False
    
    for line in lines:
        if '| Issue Type |' in line:
            in_table = True
            continue
        
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            
            if len(parts) >= 3:
                issue_type = parts[0].lower()
                primary = parts[1].lower()
                not_counted_in = [d.strip().lower() for d in parts[2].split(',')]
                
                ownership[issue_type] = {
                    'primary': primary,
                    'not_counted_in': not_counted_in
                }
    
    # Add pattern-based rules for doc-reviewer
    ownership['wrong file path'] = {'primary': 'accuracy', 'not_counted_in': ['completeness']}
    ownership['broken link'] = {'primary': 'staleness', 'not_counted_in': ['accuracy']}
    ownership['outdated code'] = {'primary': 'accuracy', 'not_counted_in': ['staleness']}
    ownership['missing feature'] = {'primary': 'completeness', 'not_counted_in': ['structure']}
    ownership['unexplained jargon'] = {'primary': 'clarity', 'not_counted_in': ['completeness']}
    ownership['wrong heading'] = {'primary': 'structure', 'not_counted_in': ['consistency']}
    ownership['mixed markers'] = {'primary': 'consistency', 'not_counted_in': ['structure']}
    ownership['deprecated'] = {'primary': 'staleness', 'not_counted_in': ['accuracy']}
    ownership['missing troubleshooting'] = {'primary': 'completeness', 'not_counted_in': ['structure']}
    ownership['complex sentence'] = {'primary': 'clarity', 'not_counted_in': ['consistency']}
    
    return ownership
```

### Check Overlap Violation

```python
def check_overlap_violation(line: int, citations: list, ownership_rules: dict) -> dict:
    """Check if multiple citations on same line constitute a violation.
    
    Args:
        line: Line number with multiple citations
        citations: List of citation objects from different dimensions
        ownership_rules: Parsed ownership rules
        
    Returns:
        Violation object if overlap detected, None otherwise
    """
    
    # Get dimensions citing this line
    dimensions = [c['dimension'] for c in citations]
    patterns = [c['pattern'].lower() for c in citations]
    
    # Check each pattern against ownership rules
    for i, pattern in enumerate(patterns):
        for issue_type, rules in ownership_rules.items():
            if issue_type in pattern or pattern in issue_type:
                primary = rules['primary']
                claiming_dim = dimensions[i]
                
                # Check if claiming dimension is NOT the primary owner
                if claiming_dim.lower() != primary.lower():
                    # This is a potential violation
                    other_dims = [d for d in dimensions if d != claiming_dim]
                    
                    if primary.lower() in [d.lower() for d in other_dims]:
                        # Both primary owner and non-owner cite this line
                        return {
                            'line': line,
                            'pattern': pattern,
                            'claimed_by': claiming_dim,
                            'owned_by': primary,
                            'all_claimers': dimensions,
                            'rule_matched': issue_type,
                            'severity': 'HIGH'
                        }
    
    # No violation if same pattern can legitimately belong to multiple dimensions
    # (e.g., different aspects of same line)
    return None
```

---

## Additional Validation Functions

### Detect Same Issue Text

```python
def detect_duplicate_issues(dimension_results: list) -> list:
    """Detect same issue description across dimensions.
    
    This catches cases where line numbers differ but the issue is the same.
    """
    
    duplicates = []
    issue_texts = {}  # normalized text -> list of {dimension, line, original}
    
    for result in dimension_results:
        dimension = result['dimension']
        
        for issue in result.get('issues_found', []):
            description = issue.get('description', '')
            normalized = normalize_issue_text(description)
            
            if normalized in issue_texts:
                # Potential duplicate
                existing = issue_texts[normalized]
                duplicates.append({
                    'issue_text': description,
                    'first_occurrence': existing,
                    'duplicate': {
                        'dimension': dimension,
                        'line': issue.get('line'),
                        'original': description
                    }
                })
            else:
                issue_texts[normalized] = {
                    'dimension': dimension,
                    'line': issue.get('line'),
                    'original': description
                }
    
    return duplicates


def normalize_issue_text(text: str) -> str:
    """Normalize issue text for comparison."""
    import re
    
    # Remove line numbers
    text = re.sub(r'line \d+', '', text.lower())
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```

### Validate Deferred Issues

```python
def validate_deferred_issues(dimension_results: list) -> list:
    """Verify that deferred issues appear in the owning dimension.
    
    Returns:
        List of orphaned deferred issues (should be empty)
    """
    
    orphans = []
    
    # Build index of all issues by line
    issues_by_line = {}
    
    for result in dimension_results:
        dimension = result['dimension']
        
        for issue in result.get('issues_found', []):
            line = issue.get('line')
            if line not in issues_by_line:
                issues_by_line[line] = []
            issues_by_line[line].append({
                'dimension': dimension,
                'description': issue.get('description', '')
            })
    
    # Check each deferred issue
    for result in dimension_results:
        dimension = result['dimension']
        
        for deferred in result.get('issues_deferred', []):
            line = deferred.get('line')
            owned_by = deferred.get('owned_by', '').lower()
            
            # Check if owner has this issue
            if line in issues_by_line:
                owner_has_it = any(
                    i['dimension'].lower() == owned_by
                    for i in issues_by_line[line]
                )
                
                if not owner_has_it:
                    orphans.append({
                        'deferred_by': dimension,
                        'deferred_to': owned_by,
                        'line': line,
                        'description': deferred.get('description', ''),
                        'status': 'ORPHANED - owner did not capture'
                    })
            else:
                orphans.append({
                    'deferred_by': dimension,
                    'deferred_to': owned_by,
                    'line': line,
                    'description': deferred.get('description', ''),
                    'status': 'ORPHANED - no dimension captured'
                })
    
    return orphans
```

---

## Violation Reporting

### Format Violation Report

```python
def format_violation_report(violations: list, duplicates: list, orphans: list) -> str:
    """Generate markdown report of all overlap issues."""
    
    if not violations and not duplicates and not orphans:
        return "## Overlap Validation: PASSED\n\nNo overlap violations detected.\n"
    
    report = "## Overlap Validation: ISSUES DETECTED\n\n"
    
    if violations:
        report += f"### Line Overlap Violations ({len(violations)})\n\n"
        report += "| Line | Pattern | Claimed By | Should Be |\n"
        report += "|------|---------|------------|----------|\n"
        for v in violations:
            report += f"| {v['line']} | {v['pattern'][:30]} | {v['claimed_by']} | {v['owned_by']} |\n"
        report += "\n"
    
    if duplicates:
        report += f"### Duplicate Issues ({len(duplicates)})\n\n"
        for d in duplicates:
            report += f"- \"{d['issue_text'][:50]}...\" in {d['first_occurrence']['dimension']} and {d['duplicate']['dimension']}\n"
        report += "\n"
    
    if orphans:
        report += f"### Orphaned Deferred Issues ({len(orphans)})\n\n"
        for o in orphans:
            report += f"- Line {o['line']}: deferred from {o['deferred_by']} to {o['deferred_to']} - {o['status']}\n"
        report += "\n"
    
    return report
```

---

## Integration with Parallel Execution

### Full Validation Pipeline

```python
def run_overlap_validation(dimension_results: list, overlap_rules: str) -> dict:
    """Run complete overlap validation pipeline.
    
    Returns:
        dict with:
        - passed: bool
        - violations: list
        - duplicates: list
        - orphans: list
        - report: str
    """
    
    # Run all validations
    violations = validate_no_overlaps(dimension_results, overlap_rules)
    duplicates = detect_duplicate_issues(dimension_results)
    orphans = validate_deferred_issues(dimension_results)
    
    # Generate report
    report = format_violation_report(violations, duplicates, orphans)
    
    # Determine pass/fail
    passed = len(violations) == 0 and len(duplicates) == 0
    # Note: orphans are warnings, not failures
    
    return {
        'passed': passed,
        'violations': violations,
        'duplicates': duplicates,
        'orphans': orphans,
        'report': report,
        'summary': {
            'total_violations': len(violations),
            'total_duplicates': len(duplicates),
            'total_orphans': len(orphans)
        }
    }
```

---

## Test Cases

### Test Non-Overlapping Input

```python
def test_no_overlaps():
    """Verify empty violations for non-overlapping results."""
    
    results = [
        {
            'dimension': 'accuracy',
            'evidence': [{'line': 10, 'pattern': 'file path exists', 'quote': 'test'}]
        },
        {
            'dimension': 'completeness',
            'evidence': [{'line': 20, 'pattern': 'missing feature', 'quote': 'test'}]
        }
    ]
    
    overlap_rules = "# Mock rules"
    violations = validate_no_overlaps(results, overlap_rules)
    
    assert violations == [], f"Expected no violations, got {violations}"
```

### Test Detected Overlap

```python
def test_detect_overlap():
    """Verify violation detected when same line claimed by wrong dimension."""
    
    results = [
        {
            'dimension': 'accuracy',
            'evidence': [{'line': 10, 'pattern': 'wrong file path', 'quote': 'src/old.py'}]
        },
        {
            'dimension': 'completeness',  # Should not claim "wrong file path"
            'evidence': [{'line': 10, 'pattern': 'wrong file path', 'quote': 'src/old.py'}]
        }
    ]
    
    overlap_rules = "| Wrong file path | Accuracy | Completeness |"
    violations = validate_no_overlaps(results, overlap_rules)
    
    assert len(violations) == 1, f"Expected 1 violation, got {len(violations)}"
    assert violations[0]['owned_by'] == 'accuracy'
```

### Test All 6 Dimensions Present

```python
def test_all_dimensions_present():
    """Verify validation with all 6 dimensions."""
    
    results = [
        {'dimension': 'accuracy', 'evidence': [], 'issues_found': []},
        {'dimension': 'completeness', 'evidence': [], 'issues_found': []},
        {'dimension': 'clarity', 'evidence': [], 'issues_found': []},
        {'dimension': 'structure', 'evidence': [], 'issues_found': []},
        {'dimension': 'staleness', 'evidence': [], 'issues_found': []},
        {'dimension': 'consistency', 'evidence': [], 'issues_found': []},
    ]
    
    overlap_rules = ""
    validation_result = run_overlap_validation(results, overlap_rules)
    
    assert validation_result['passed'] == True
    assert validation_result['summary']['total_violations'] == 0
```

### Test Deferred Issue Tracking

```python
def test_deferred_issues():
    """Verify deferred issues are tracked to owning dimension."""
    
    results = [
        {
            'dimension': 'accuracy',
            'evidence': [],
            'issues_found': [],
            'issues_deferred': [
                {'line': 50, 'description': 'Broken link', 'owned_by': 'staleness', 'overlap_rule': 'Rule 5'}
            ]
        },
        {
            'dimension': 'staleness',
            'evidence': [],
            'issues_found': [
                {'line': 50, 'description': 'Broken external link returns 404', 'severity': 'HIGH'}
            ],
            'issues_deferred': []
        }
    ]
    
    orphans = validate_deferred_issues(results)
    
    assert len(orphans) == 0, f"Expected no orphans, got {orphans}"
```

---

## Decision Priority Order

When a violation is detected and ownership is ambiguous, use this priority order:

1. **Accuracy** (weight 5) - Factual errors take precedence
2. **Completeness** (weight 5) - Coverage gaps  
3. **Clarity** (weight 4) - Accessibility issues
4. **Structure** (weight 3) - Organization problems
5. **Staleness** (weight 2) - Currency/time issues
6. **Consistency** (weight 1) - Formatting variations

Higher-weighted dimensions have ownership priority in ambiguous cases.
