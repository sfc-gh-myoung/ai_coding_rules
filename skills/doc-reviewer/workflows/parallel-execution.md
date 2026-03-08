# Parallel Execution Workflow

## Overview

This workflow coordinates 6 parallel sub-agents to evaluate documentation across all dimensions simultaneously. The coordinator is responsible for:

1. Loading shared context (documentation content, overlap rules)
2. Launching 6 sub-agents with 5s delay between each
3. Monitoring progress via polling
4. Collecting and validating results
5. Detecting overlap violations
6. Aggregating scores into final review

---

## Prerequisites

Before starting parallel execution:

```bash
# Verify all rubric files exist (should be 7: 6 dimensions + _overlap-resolution.md)
ls skills/doc-reviewer/rubrics/*.md | wc -l  # Should be 7

# Verify template exists
test -f skills/doc-reviewer/workflows/dimension-subagent-template.md && echo "OK"

# Verify overlap rules exist
head -20 skills/doc-reviewer/rubrics/_overlap-resolution.md
```

### Prerequisites Checklist

- [ ] 7 rubric files exist: `ls skills/doc-reviewer/rubrics/*.md | wc -l` → expect 7
- [ ] Overlap rules loaded: `head -20 skills/doc-reviewer/rubrics/_overlap-resolution.md`
- [ ] Template file exists: `test -f skills/doc-reviewer/workflows/dimension-subagent-template.md`
- [ ] Target documentation readable and <10K lines

---

## Phase 1: Setup

### 1.1 Load Documentation Content

```python
def load_doc_content(doc_path: str) -> dict:
    """Read documentation once, pass to all sub-agents."""
    
    content = read_file(doc_path)
    lines = content.split('\n')
    
    return {
        'content': content,
        'line_count': len(lines),
        'path': doc_path
    }
```

### 1.2 Load Overlap Resolution Rules

```python
def load_overlap_rules() -> str:
    """Load _overlap-resolution.md once for all sub-agents."""
    
    return read_file('skills/doc-reviewer/rubrics/_overlap-resolution.md')
```

### 1.3 Prepare Dimension Configuration

```python
DIMENSIONS = [
    {"name": "accuracy", "weight": 5, "max_pts": 25, "rubric": "rubrics/accuracy.md"},
    {"name": "completeness", "weight": 5, "max_pts": 25, "rubric": "rubrics/completeness.md"},
    {"name": "clarity", "weight": 4, "max_pts": 20, "rubric": "rubrics/clarity.md"},
    {"name": "structure", "weight": 3, "max_pts": 15, "rubric": "rubrics/structure.md"},
    {"name": "staleness", "weight": 2, "max_pts": 10, "rubric": "rubrics/staleness.md"},
    {"name": "consistency", "weight": 1, "max_pts": 5, "rubric": "rubrics/consistency.md"},
]

# Points formula: raw_score * (weight / 2)
# Example: Accuracy raw=8, weight=5 → 8 * 2.5 = 20 points (max 25)
```

---

## Phase 2: Launch Sub-Agents

### 2.1 Generate Dimension Prompts

```python
def generate_dimension_prompt(dim: dict, doc: dict, overlap_rules: str) -> str:
    """Generate sub-agent prompt from template."""
    
    # Load template
    template = read_file('workflows/dimension-subagent-template.md')
    
    # Load rubric
    rubric_content = read_file(dim['rubric'])
    
    # Extract overlap rules for this dimension
    dim_overlap_rules = extract_overlap_rules_for(dim['name'], overlap_rules)
    
    # Replace template variables
    prompt = template
    prompt = prompt.replace('{dimension_name}', dim['name'])
    prompt = prompt.replace('{weight}', str(dim['weight']))
    prompt = prompt.replace('{doc_content}', doc['content'])
    prompt = prompt.replace('{doc_line_count}', str(doc['line_count']))
    prompt = prompt.replace('{overlap_rules_for_this_dimension}', dim_overlap_rules)
    prompt = prompt.replace('{rubric_content}', rubric_content)
    
    return prompt
```

### 2.2 Launch All Sub-Agents

```python
def launch_dimension_subagents(doc: dict, overlap_rules: str, params: dict) -> list:
    """Launch 6 parallel sub-agents for dimension evaluation."""
    
    import time
    
    agents = []
    
    for dim in DIMENSIONS:
        prompt = generate_dimension_prompt(dim, doc, overlap_rules)
        
        # Launch sub-agent using Task tool
        # NOTE: This is the actual Cortex Code tool invocation
        agent_id = Task(
            subagent_type="general-purpose",
            description=f"Evaluate {dim['name']} dimension",
            prompt=prompt,
            run_in_background=True,
            agent_mode="autonomous"
        )
        
        agents.append({
            'id': agent_id,
            'dimension': dim['name'],
            'weight': dim['weight'],
            'max_pts': dim['max_pts'],
            'status': 'running',
            'started_at': time.time(),
            'result': None
        })
        
        # 5s delay to avoid API rate limiting
        time.sleep(5)
        
        print(f"Launched: {dim['name']} (agent_id: {agent_id})")
    
    return agents
```

---

## Phase 3: Monitor Progress

### 3.1 During-Execution Monitoring

```python
def monitor_subagents(agents: list, timeout_seconds: int = 120) -> list:
    """Poll sub-agents for completion, handle timeouts."""
    
    import time
    
    completed = []
    
    while len(completed) < len(agents):
        for agent in agents:
            if agent['status'] == 'completed':
                continue
            
            # Poll for output using agent_output tool
            result = agent_output(agent_id=agent['id'])
            
            if result is not None and result.status == 'completed':
                # Sub-agent completed
                agent['status'] = 'completed'
                agent['result'] = result.output
                completed.append(agent)
                
                # Parse JSON result
                try:
                    parsed = json.loads(result.output)
                    print(f"Dimension {agent['dimension']} complete: {parsed['raw_score']}/10")
                except json.JSONDecodeError:
                    agent['status'] = 'parse_error'
                    print(f"WARNING: {agent['dimension']} returned invalid JSON")
            
            elif time.time() - agent['started_at'] > timeout_seconds:
                # Timeout - trigger retry
                agent['status'] = 'timeout'
                print(f"TIMEOUT: {agent['dimension']} after {timeout_seconds}s")
        
        # Progress update
        print(f"Progress: {len(completed)}/6 dimensions evaluated")
        
        # Poll every 30 seconds
        time.sleep(30)
    
    return agents
```

### Monitoring Commands

**Check sub-agent status:**
```bash
cortex ctx show tasks | grep -E "(accuracy|completeness|clarity|structure|staleness|consistency)"
```

**Verify all 6 completed:**
```bash
COMPLETED=$(cortex ctx show tasks --json | jq '[.[] | select(.status=="done")] | length')
if [ "$COMPLETED" -ne 6 ]; then
  echo "ERROR: Only $COMPLETED/6 dimensions complete"
  exit 1
fi
```

### 3.2 Handle Failures

```python
def handle_failed_agents(agents: list, doc: dict, overlap_rules: str) -> list:
    """Retry failed sub-agents or fall back to sequential."""
    
    MAX_RETRIES = 2
    
    for agent in agents:
        if agent['status'] in ['timeout', 'parse_error']:
            retries = 0
            
            while retries < MAX_RETRIES and agent['status'] != 'completed':
                print(f"Retrying {agent['dimension']} (attempt {retries + 1}/{MAX_RETRIES})")
                
                # Re-launch sub-agent with extended timeout
                dim = next(d for d in DIMENSIONS if d['name'] == agent['dimension'])
                prompt = generate_dimension_prompt(dim, doc, overlap_rules)
                
                agent_id = Task(
                    subagent_type="general-purpose",
                    description=f"Evaluate {dim['name']} dimension (retry)",
                    prompt=prompt,
                    run_in_background=True,
                    agent_mode="autonomous"
                )
                
                agent['id'] = agent_id
                agent['started_at'] = time.time()
                
                # Wait for result with extended timeout
                time.sleep(180)  # 3 minutes for retry
                result = agent_output(agent_id=agent_id)
                
                if result and result.status == 'completed':
                    try:
                        parsed = json.loads(result.output)
                        agent['status'] = 'completed'
                        agent['result'] = result.output
                    except json.JSONDecodeError:
                        retries += 1
                else:
                    retries += 1
            
            if agent['status'] != 'completed':
                # Fall back to sequential evaluation
                print(f"FALLBACK: Evaluating {agent['dimension']} sequentially")
                agent['result'] = evaluate_dimension_sequential(
                    agent['dimension'],
                    doc,
                    overlap_rules
                )
                agent['status'] = 'completed_sequential'
    
    return agents
```

### Failure Handling

**If sub-agent times out (>120s):**
```bash
# Retry once with extended timeout
cortex task resume $AGENT_ID --timeout 180s

# If still fails, mark dimension as SKIPPED
cortex ctx remember "$DIMENSION: SKIPPED (timeout after 2 attempts)"
```

**If 3+ sub-agents fail:**
```bash
# Fallback to sequential execution
echo "WARN: Parallel execution failed, falling back to sequential"
# Use workflows/review-execution.md instead
```

**If JSON parsing fails:**
```bash
# Extract partial results
jq -r '.raw_score // "ERROR"' < $RESULT_FILE
# Log for manual review
cortex ctx remember "MANUAL_REVIEW_NEEDED: $DIMENSION output malformed"
```

---

## Phase 4: Collect & Validate Results

### 4.1 Parse Sub-Agent Results

```python
def collect_dimension_results(agents: list) -> list:
    """Parse JSON results from all sub-agents."""
    
    results = []
    
    for agent in agents:
        if agent['result']:
            try:
                parsed = json.loads(agent['result'])
                
                # Validate required fields
                assert 'dimension' in parsed
                assert 'raw_score' in parsed
                assert 0 <= parsed['raw_score'] <= 10
                assert 'evidence' in parsed
                assert 'issues_found' in parsed
                
                results.append(parsed)
                
            except (json.JSONDecodeError, AssertionError) as e:
                print(f"ERROR: Invalid result from {agent['dimension']}: {e}")
                results.append({
                    'dimension': agent['dimension'],
                    'raw_score': 0,
                    'weight': agent['weight'],
                    'points': 0,
                    'max_points': agent['max_pts'],
                    'evidence': [],
                    'issues_found': [],
                    'issues_deferred': [],
                    'verification_table': '',
                    'validation': 'failed'
                })
    
    return results
```

### 4.2 Validate No Overlaps

See `workflows/overlap-validator.md` for detailed implementation.

```python
def validate_no_overlaps(results: list, overlap_rules: str) -> list:
    """Check for double-counted issues across dimensions."""
    
    # Import from overlap-validator.md
    from overlap_validator import run_overlap_validation
    
    validation = run_overlap_validation(results, overlap_rules)
    
    if not validation['passed']:
        print(f"WARNING: {validation['summary']['total_violations']} overlap violations detected")
        for v in validation['violations']:
            print(f"  Line {v['line']}: claimed by {v['claimed_by']}, owned by {v['owned_by']}")
    
    return validation['violations']
```

---

## Phase 5: Aggregate & Report

### 5.1 Calculate Final Score

See `workflows/score-aggregation.md` for detailed implementation.

```python
def aggregate_final_score(results: list) -> dict:
    """Combine dimension scores into final review."""
    
    # Import from score-aggregation.md
    from score_aggregation import aggregate_dimension_results
    
    return aggregate_dimension_results(results)
```

### 5.2 Generate Review Document

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
    
    review = f"""# Documentation Review: {doc_name}

**Date:** {date}
**Model:** {model}
**Mode:** FULL (Parallel Execution)
**Target:** {doc_path}

---

## Summary

| Score | Verdict |
|-------|---------|
| **{final_score['total_score']}/100** | **{final_score['verdict']}** |

---

## Score Breakdown

| Dimension | Raw | Weight | Points | Max |
|-----------|-----|--------|--------|-----|
"""
    
    for ws in sorted(final_score['worksheets'], key=lambda x: x['weight'], reverse=True):
        review += f"| {ws['dimension'].title()} | {ws['raw_score']}/10 | ×{ws['weight']/2} | {ws['points']} | {ws['max_points']} |\n"
    
    review += f"| **TOTAL** | | | **{final_score['total_score']}** | **100** |\n"
    
    # Add dimension details
    for result in sorted(results, key=lambda x: get_weight_for_dimension(x['dimension']), reverse=True):
        review += f"\n---\n\n### {result['dimension'].title()}: {result['raw_score']}/10\n\n"
        
        if result.get('verification_table'):
            review += "**Verification Table:**\n"
            review += result['verification_table'] + "\n\n"
        
        if result.get('evidence'):
            review += "**Evidence:**\n"
            for ev in result['evidence'][:5]:
                review += f"- Line {ev['line']}: {ev['pattern']} - \"{ev['quote'][:50]}...\"\n"
        
        if result.get('issues_found'):
            review += "\n**Issues:**\n"
            for issue in result['issues_found'][:5]:
                review += f"- [{issue.get('severity', 'MEDIUM')}] Line {issue['line']}: {issue['description']}\n"
    
    # Add overlap violations if any
    if violations:
        review += "\n---\n\n## Overlap Violations\n\n"
        for v in violations:
            review += f"- Line {v['line']}: {v['pattern']} claimed by {v['claimed_by']}, owned by {v['owned_by']}\n"
    
    review += "\n\n.... Generated with [Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)\n"
    
    return review


def get_verdict(score: float) -> str:
    """Map score to verdict."""
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

---

## Complete Execution Flow

```python
def execute_parallel_review(doc_path: str, params: dict) -> str:
    """Main entry point for parallel documentation review."""
    
    print("=== Parallel Documentation Review ===")
    print(f"Target: {doc_path}")
    
    # Phase 1: Setup
    print("\nPhase 1: Loading documentation and rules...")
    doc = load_doc_content(doc_path)
    overlap_rules = load_overlap_rules()
    print(f"Documentation loaded: {doc['line_count']} lines")
    
    # Phase 2: Launch sub-agents
    print("\nPhase 2: Launching 6 dimension sub-agents...")
    agents = launch_dimension_subagents(doc, overlap_rules, params)
    print(f"Launched {len(agents)} sub-agents")
    
    # Phase 3: Monitor progress
    print("\nPhase 3: Monitoring sub-agent progress...")
    agents = monitor_subagents(agents, timeout_seconds=120)
    agents = handle_failed_agents(agents, doc, overlap_rules)
    
    # Phase 4: Collect & validate
    print("\nPhase 4: Collecting and validating results...")
    results = collect_dimension_results(agents)
    violations = validate_no_overlaps(results, overlap_rules)
    
    # Phase 5: Aggregate & report
    print("\nPhase 5: Aggregating scores and generating report...")
    final_score = aggregate_final_score(results)
    
    review = generate_review_document(
        doc_path=doc_path,
        final_score=final_score,
        results=results,
        violations=violations,
        model=params.get('model', 'unknown'),
        date=params.get('date', 'unknown')
    )
    
    print(f"\n=== Review Complete ===")
    print(f"Final Score: {final_score['total_score']}/100")
    print(f"Verdict: {final_score['verdict']}")
    
    return review
```

---

## Error Recovery Reference

| Error | Detection | Recovery |
|-------|-----------|----------|
| Sub-agent timeout | No response after 120s | Retry up to 2 times with 180s timeout, then sequential fallback |
| JSON parse failure | Invalid JSON in result | Retry with schema reminder, then default to 0 score |
| API rate limiting | 429 response | 5s delay already applied; increase to 10s if persistent |
| Resource exhaustion | Sub-agent crashes | Reduce parallelism to batches of 3 |
| 3+ sub-agents fail | Failure count ≥3 | Fallback to sequential execution |

---

## Performance Targets

| Metric | Sequential | Parallel | Improvement |
|--------|------------|----------|-------------|
| Execution time | ~12-15 min | ~3-4 min | 3-4× faster |
| Token cost | ~12K | ~72K | 6× higher |
| Context freshness | Degraded after dim 3 | Fresh for all | Better accuracy |
| Fault tolerance | Restart from beginning | Retry single dimension | Improved |

---

## Related Workflows

- **`workflows/dimension-subagent-template.md`** - Template for sub-agent prompts
- **`workflows/parallel-specs.md`** - Timeout handling, schemas, edge cases
- **`workflows/score-aggregation.md`** - Result combination and verdict
- **`workflows/overlap-validator.md`** - Deduplication validation
- **`workflows/review-execution.md`** - Sequential fallback workflow
