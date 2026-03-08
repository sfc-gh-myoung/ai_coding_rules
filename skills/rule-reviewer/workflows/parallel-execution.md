# Parallel Execution Workflow

Coordinator workflow for parallel dimension evaluation using sub-agents.

## Overview

This workflow enables parallel evaluation of rule dimensions by launching 7 sub-agents (one per non-deterministic dimension) while computing Rule Size inline.

```
Coordinator (Main Agent)
│
├── Phase 1: Setup
│   ├── Validate inputs (target_file, review_date, review_mode, model)
│   ├── Detect file type (rule vs project)
│   ├── Run schema validation (if rule file)
│   ├── Read rule content once
│   ├── Load overlap resolution rules
│   └── Prepare shared context
│
├── Phase 2: Parallel Dimension Evaluation
│   ├── INLINE: Rule Size (100% deterministic - `wc -l`)
│   ├── SA-1: Actionability (25pts) [background]
│   ├── SA-2: Completeness (25pts) [background]
│   ├── SA-3: Consistency (15pts) [background]
│   ├── SA-4: Parsability (15pts) [background]
│   ├── SA-5: Token Efficiency (10pts) [background]
│   ├── SA-6: Staleness (10pts) [background]
│   └── SA-7: Cross-Agent Consistency (5pts) [background]
│
├── Phase 3: Collect & Validate Results
│   ├── Gather 7 dimension worksheets + Rule Size result
│   ├── Verify no overlap violations
│   └── Flag any double-counted issues
│
└── Phase 4: Score Aggregation & Report
    ├── Apply scoring formula: Raw × (Weight/2)
    ├── Apply critical dimension override
    ├── Calculate total score
    └── Generate unified review document
```

## Pre-Launch Validation

Before launching sub-agents, validate the rule file:

```python
def validate_rule_file(rule_path: str) -> dict:
    """Validate rule file before sub-agent launch."""
    
    errors = []
    warnings = []
    
    # Check file exists
    if not os.path.exists(rule_path):
        errors.append(f"Rule file not found: {rule_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # Check file size
    size = os.path.getsize(rule_path)
    if size == 0:
        errors.append(f"Rule file is empty (0 bytes): {rule_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    if size < 500:
        warnings.append(f"Rule file unusually small ({size} bytes)")
    
    # Check file is readable
    try:
        with open(rule_path, 'r') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Cannot read rule file: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # Check for YAML frontmatter
    if not content.startswith('---'):
        warnings.append("Missing YAML frontmatter (expected for rule files)")
    
    # Check for minimum structure
    if content.count('#') < 3:
        warnings.append("Rule has fewer than 3 headers. May be poorly structured.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "size_bytes": size,
        "line_count": content.count('\n') + 1
    }
```

## Phase 1: Setup

### 1.1 Input Validation

```python
def validate_inputs(params: dict) -> tuple[bool, list]:
    """Validate all required inputs."""
    errors = []
    
    # Required parameters
    if not params.get('target_file'):
        errors.append("target_file is required")
    if not params.get('review_date'):
        errors.append("review_date is required")
    if not params.get('review_mode'):
        errors.append("review_mode is required")
    
    # Date format validation
    if params.get('review_date'):
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', params['review_date']):
            errors.append(f"review_date must be YYYY-MM-DD format, got: {params['review_date']}")
    
    # Mode validation
    valid_modes = ['FULL', 'FOCUSED', 'STALENESS']
    if params.get('review_mode') and params['review_mode'] not in valid_modes:
        errors.append(f"review_mode must be one of {valid_modes}")
    
    return len(errors) == 0, errors
```

### 1.2 File Type Detection

```bash
target_basename=$(basename "$target_file")

if [[ "$target_basename" =~ ^(AGENTS|PROJECT)\.md$ ]]; then
    FILE_TYPE="project"
    SKIP_SCHEMA=true
elif [[ "$target_file" == rules/*.md ]]; then
    FILE_TYPE="rule"
    SKIP_SCHEMA=false
else
    echo "ERROR: Target must be AGENTS.md, PROJECT.md, or rules/*.md"
    exit 1
fi
```

### 1.3 Load Shared Context

```python
def load_shared_context(params: dict) -> dict:
    """Load all context needed by sub-agents."""
    
    # Read rule content once
    rule_content = read_file(params['target_file'])
    
    # Load overlap resolution rules
    overlap_rules = read_file("skills/rule-reviewer/rubrics/_overlap-resolution.md")
    
    # Get line count for Rule Size
    line_count = len(rule_content.split('\n'))
    
    return {
        'rule_content': rule_content,
        'overlap_rules': overlap_rules,
        'line_count': line_count,
        'file_type': params.get('file_type', 'rule'),
        'target_file': params['target_file']
    }
```

## Phase 2: Parallel Dimension Evaluation

### 2.1 Rule Size (Inline - 100% Deterministic)

Rule Size is computed directly by the coordinator since it requires no LLM evaluation:

```python
def compute_rule_size_inline(rule_path: str) -> dict:
    """Compute Rule Size dimension inline (100% deterministic)."""
    
    import subprocess
    result = subprocess.run(['wc', '-l', rule_path], capture_output=True, text=True)
    line_count = int(result.stdout.strip().split()[0])
    
    # Score based on rule-size.md rubric
    if line_count <= 300:
        raw_score = 10
        flag = None
        tier = "Optimal"
    elif line_count <= 400:
        raw_score = 9
        flag = None
        tier = "Good"
    elif line_count <= 500:
        raw_score = 8
        flag = None
        tier = "Acceptable"
    elif line_count <= 600:
        raw_score = 6
        flag = "OPTIMIZATION_RECOMMENDED"
        tier = "Needs Attention"
    elif line_count <= 800:
        raw_score = 4
        flag = "SPLITTING_REQUIRED"
        tier = "Critical"
    else:
        raw_score = 0
        flag = "NOT_DEPLOYABLE"
        tier = "Blocking"
    
    return {
        "dimension": "rule_size",
        "raw_score": raw_score,
        "weight": 2,
        "tier": tier,
        "line_count": line_count,
        "flag": flag,
        "evidence": [{"line": "N/A", "pattern": "line_count", "quote": f"{line_count} lines"}],
        "issues_found": [{"description": flag, "severity": "blocking"}] if flag else [],
        "issues_deferred": [],
        "inventory_complete": True,
        "status": "completed"
    }
```

### 2.2 Launch Sub-Agents

```python
def launch_dimension_subagents(context: dict, params: dict) -> list:
    """Launch 7 parallel sub-agents for dimension evaluation."""
    
    dimensions = [
        ("actionability", 5, "rubrics/actionability.md"),
        ("completeness", 5, "rubrics/completeness.md"),
        ("consistency", 3, "rubrics/consistency.md"),
        ("parsability", 3, "rubrics/parsability.md"),
        ("token_efficiency", 2, "rubrics/token-efficiency.md"),
        ("staleness", 2, "rubrics/staleness.md"),
        ("cross_agent_consistency", 1, "rubrics/cross-agent-consistency.md"),
    ]
    
    agent_ids = []
    for dim_name, weight, rubric_path in dimensions:
        # Generate dimension-specific prompt
        prompt = generate_dimension_prompt(
            dimension_name=dim_name,
            weight=weight,
            rubric_path=rubric_path,
            rule_content=context['rule_content'],
            overlap_rules=extract_overlap_rules_for(dim_name, context['overlap_rules']),
            params=params
        )
        
        # Launch background sub-agent using Task tool
        agent_id = task(
            subagent_type="general-purpose",
            description=f"Evaluate {dim_name}",
            prompt=prompt,
            run_in_background=True,
            agent_mode="autonomous"
        )
        
        # 5s delay between launches to avoid API rate limiting
        time.sleep(5)
        
        agent_ids.append({
            'id': agent_id,
            'dimension': dim_name,
            'weight': weight,
            'status': 'running'
        })
    
    return agent_ids
```

### 2.3 Extract Overlap Rules

```python
def extract_overlap_rules_for(dimension: str, overlap_rules_content: str) -> str:
    """Extract overlap rules relevant to a specific dimension."""
    
    # Priority rules mapping
    PRIORITY_RULES = {
        "parsability": [
            ("Rule 1", "Schema/YAML validation errors → Parsability ALWAYS wins"),
        ],
        "actionability": [
            ("Rule 2", "Ambiguous/undefined instructions → Actionability (blocks execution)"),
            ("Rule 2", "Missing verification commands → Actionability"),
            ("Rule 2", "Undefined helper functions → Actionability"),
        ],
        "completeness": [
            ("Rule 3", "Missing coverage/edge cases → Completeness (scope gap)"),
            ("Rule 3", "Missing prerequisites → Completeness"),
            ("Rule 3", "Missing error handling → Completeness"),
        ],
        "consistency": [
            ("Rule 4", "Self-contradiction → Consistency (internal conflict)"),
            ("Rule 4", "Terminology inconsistency → Consistency"),
        ],
        "token_efficiency": [
            ("Rule 5", "Duplicated/redundant content → Token Efficiency"),
        ],
        "staleness": [
            ("Rule 6", "Outdated patterns/tools/references → Staleness"),
        ],
        "cross_agent_consistency": [
            ("Rule 7", "Agent-specific logic/hardcoded names → Cross-Agent Consistency"),
        ],
    }
    
    # Issue type ownership
    OWNERSHIP_MATRIX = {
        "undefined_helper": "actionability",
        "missing_verification": "actionability",
        "ambiguous_instruction": "actionability",
        "missing_parameter": "completeness",
        "missing_error_handling": "completeness",
        "schema_violation": "parsability",
        "yaml_invalid": "parsability",
        "internal_conflict": "consistency",
        "redundant_section": "token_efficiency",
        "deprecated_tool": "staleness",
        "hardcoded_agent": "cross_agent_consistency",
    }
    
    dim_key = dimension.lower().replace("-", "_")
    relevant_rules = PRIORITY_RULES.get(dim_key, [])
    owned_types = [k for k, v in OWNERSHIP_MATRIX.items() if v == dim_key]
    
    rules_text = "\n".join([f"- {r[0]}: {r[1]}" for r in relevant_rules]) or "- No primary ownership rules"
    types_text = ", ".join(owned_types) or "None exclusively owned"
    
    return f"""### {dimension.title()} Ownership Rules

**Priority Rules (first match wins):**
{rules_text}

**Issue Types Owned by {dimension}:**
{types_text}

**Decision Protocol:**
1. Check if issue matches a priority rule (Rules 1-7 in order)
2. First matching rule determines ownership
3. If no rule match, use issue type matrix above
4. If issue type not in matrix, default to Completeness
5. Document ownership decision with reasoning in issues_deferred
"""
```

## Phase 3: Collect & Validate Results

### 3.1 Monitor Sub-Agent Progress

```python
def collect_dimension_results(agent_ids: list, timeout_seconds: int = 90) -> list:
    """Collect results from all sub-agents with timeout handling."""
    
    import time
    
    results = []
    pending = agent_ids.copy()
    start_time = time.time()
    
    while pending and (time.time() - start_time) < timeout_seconds * len(agent_ids):
        for agent in pending[:]:
            # Poll agent output
            output = agent_output(agent_id=agent['id'])
            
            if output.get('status') == 'completed':
                # Parse JSON result from agent output
                result = parse_dimension_result(output['messages'])
                result['dimension'] = agent['dimension']
                result['weight'] = agent['weight']
                results.append(result)
                pending.remove(agent)
                print(f"✓ {agent['dimension']} complete: {result['raw_score']}/10")
            elif output.get('status') == 'failed':
                # Record failure
                results.append({
                    'dimension': agent['dimension'],
                    'weight': agent['weight'],
                    'status': 'failed',
                    'error': output.get('error', 'Unknown error')
                })
                pending.remove(agent)
                print(f"✗ {agent['dimension']} failed: {output.get('error')}")
        
        if pending:
            time.sleep(30)  # Poll every 30 seconds
    
    # Handle timeouts
    for agent in pending:
        results.append({
            'dimension': agent['dimension'],
            'weight': agent['weight'],
            'status': 'timeout',
            'error': f'Timed out after {timeout_seconds}s'
        })
        print(f"⏱ {agent['dimension']} timed out")
    
    return results
```

### 3.2 Validate No Overlaps

```python
def validate_no_overlaps(dimension_results: list, overlap_rules: str) -> list:
    """Ensure no double-counting across dimensions."""
    
    line_citations = {}  # line_num -> list of (dimension, pattern)
    violations = []
    
    for result in dimension_results:
        if result.get('status') != 'completed':
            continue
            
        for evidence in result.get('evidence', []):
            line = evidence.get('line')
            if line is None or line == 'N/A':
                continue
                
            if line in line_citations:
                # Check if overlap is allowed
                owner = get_owner(evidence['pattern'], overlap_rules)
                
                if owner != result['dimension']:
                    violations.append({
                        'line': line,
                        'claimed_by': result['dimension'],
                        'owned_by': owner,
                        'pattern': evidence['pattern']
                    })
            else:
                line_citations[line] = []
            
            line_citations[line].append((result['dimension'], evidence['pattern']))
    
    return violations
```

### 3.3 Get Issue Owner

```python
def get_owner(issue_pattern: str, overlap_rules_content: str) -> str:
    """Determine dimension owner for an issue based on pattern."""
    
    OWNERSHIP = {
        # Parsability owns (Rule 1 - always wins for schema)
        "schema": "parsability",
        "yaml": "parsability",
        "frontmatter": "parsability",
        
        # Actionability owns (Rule 2 - blocks execution)
        "undefined": "actionability",
        "ambiguous": "actionability",
        "verification": "actionability",
        
        # Completeness owns (Rule 3 - scope gaps)
        "missing": "completeness",
        "error handling": "completeness",
        "edge case": "completeness",
        
        # Consistency owns (Rule 4 - self-contradiction)
        "contradict": "consistency",
        "inconsistent": "consistency",
        "mismatch": "consistency",
        
        # Token Efficiency owns (Rule 5 - duplication)
        "redundant": "token_efficiency",
        "duplicate": "token_efficiency",
        
        # Staleness owns (Rule 6 - outdated)
        "deprecated": "staleness",
        "outdated": "staleness",
        
        # Cross-Agent Consistency owns (Rule 7)
        "hardcoded": "cross_agent_consistency",
    }
    
    pattern_lower = issue_pattern.lower()
    
    # Priority order check
    priority_order = [
        "schema", "yaml", "frontmatter",  # Rule 1
        "undefined", "ambiguous",  # Rule 2
        "contradict",  # Rule 4
        "redundant", "duplicate",  # Rule 5
        "deprecated", "outdated",  # Rule 6
        "hardcoded",  # Rule 7
        "missing", "error handling",  # Rule 3 (lower priority)
    ]
    
    for key in priority_order:
        if key in pattern_lower:
            return OWNERSHIP[key]
    
    # Default: completeness catches unmatched
    return "completeness"
```

## Phase 4: Score Aggregation

See `score-aggregation.md` for detailed aggregation workflow.

## Threshold Rationale

| Value | Location | Rationale |
|-------|----------|-----------|
| **30s polling** | Phase 3 | Balance between responsiveness and API overhead |
| **90s timeout** | Phase 3 | 1.5× median dimension evaluation time |
| **5s launch delay** | Phase 2 | API rate limit safety margin |
| **7 sub-agents** | Phase 2 | 8 dimensions minus Rule Size (inline) |
| **Max 2 retries** | Error handling | Diminishing returns after 2 failures |

## Error Handling

### Sub-Agent Failure

If a sub-agent fails:
1. Record the failure with error message
2. Continue collecting other results
3. Report partial results with disclaimer
4. Recommend re-running with `execution_mode: sequential`

### Timeout Handling

If sub-agent times out:
1. Kill the agent
2. Mark dimension as incomplete
3. Continue with available results
4. Note which dimensions are missing in report

### Overlap Violations

If overlap violations detected:
1. Log each violation with line/dimension info
2. Defer to the owning dimension's score
3. Flag the issue for coordinator review
4. Note violations in final report

## Execution Mode Selection

```markdown
IF execution_mode == "parallel":
    → Follow this workflow (parallel-execution.md)
ELSE:
    → Follow existing serial workflow in review-execution.md
```

## Version History

- **v1.0.0:** Initial parallel execution workflow
