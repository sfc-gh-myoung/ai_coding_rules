# Parallel Execution Workflow

## Overview

This workflow coordinates 8 parallel sub-agents to evaluate a plan across all dimensions simultaneously. The coordinator is responsible for:

1. Loading shared context (plan content, overlap rules)
2. Launching 8 sub-agents with 5s delay between each
3. Monitoring progress via polling
4. Collecting and validating results
5. Detecting overlap violations
6. Aggregating scores into final review

---

## Prerequisites

Before starting parallel execution:

```bash
# Verify all rubric files exist
ls skills/plan-reviewer/rubrics/*.md | wc -l  # Should be 9

# Verify template exists
test -f skills/plan-reviewer/workflows/dimension-subagent-template.md && echo "OK"
```

---

## Phase 1: Setup

### 1.1 Load Plan Content

```python
def load_plan_content(plan_path: str) -> dict:
    """Read plan once, pass to all sub-agents."""
    
    content = read_file(plan_path)
    lines = content.split('\n')
    
    return {
        'content': content,
        'line_count': len(lines),
        'path': plan_path
    }
```

### 1.2 Load Overlap Resolution Rules

```python
def load_overlap_rules() -> str:
    """Load _overlap-resolution.md once for all sub-agents."""
    
    return read_file('skills/plan-reviewer/rubrics/_overlap-resolution.md')
```

### 1.3 Prepare Dimension Configuration

```python
DIMENSIONS = [
    {"name": "executability", "weight": 20, "rubric": "rubrics/executability.md"},
    {"name": "completeness", "weight": 20, "rubric": "rubrics/completeness.md"},
    {"name": "success_criteria", "weight": 20, "rubric": "rubrics/success-criteria.md"},
    {"name": "scope", "weight": 15, "rubric": "rubrics/scope.md"},
    {"name": "dependencies", "weight": 10, "rubric": "rubrics/dependencies.md"},
    {"name": "decomposition", "weight": 5, "rubric": "rubrics/decomposition.md"},
    {"name": "context", "weight": 5, "rubric": "rubrics/context.md"},
    {"name": "risk_awareness", "weight": 5, "rubric": "rubrics/risk-awareness.md"},
]
```

---

## Phase 2: Launch Sub-Agents

### 2.1 Generate Dimension Prompts

```python
def generate_dimension_prompt(dim: dict, plan: dict, overlap_rules: str) -> str:
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
    prompt = prompt.replace('{plan_content}', plan['content'])
    prompt = prompt.replace('{plan_line_count}', str(plan['line_count']))
    prompt = prompt.replace('{overlap_rules_for_this_dimension}', dim_overlap_rules)
    prompt = prompt.replace('{rubric_content}', rubric_content)
    
    return prompt
```

### 2.2 Launch All Sub-Agents

```python
def launch_dimension_subagents(plan: dict, overlap_rules: str, params: dict) -> list:
    """Launch 8 parallel sub-agents for dimension evaluation."""
    
    import time
    
    agents = []
    
    for dim in DIMENSIONS:
        prompt = generate_dimension_prompt(dim, plan, overlap_rules)
        
        # Launch sub-agent using runSubagent tool
        # NOTE: This is the actual Cortex Code tool invocation
        agent_id = runSubagent(
            subagent_type="generalPurpose",
            description=f"Evaluate {dim['name']} dimension",
            prompt=prompt,
            readonly=True  # Sub-agents only read, don't write
        )
        
        agents.append({
            'id': agent_id,
            'dimension': dim['name'],
            'weight': dim['weight'],
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
def monitor_subagents(agents: list, timeout_seconds: int = 90) -> list:
    """Poll sub-agents for completion, handle timeouts."""
    
    import time
    
    completed = []
    
    while len(completed) < len(agents):
        for agent in agents:
            if agent['status'] == 'completed':
                continue
            
            # Poll for output
            result = get_agent_output(agent['id'])
            
            if result is not None:
                # Sub-agent completed
                agent['status'] = 'completed'
                agent['result'] = result
                completed.append(agent)
                
                # Parse JSON result
                try:
                    parsed = json.loads(result)
                    print(f"Dimension {agent['dimension']} complete: {parsed['raw_score']}/10")
                except json.JSONDecodeError:
                    agent['status'] = 'parse_error'
                    print(f"WARNING: {agent['dimension']} returned invalid JSON")
            
            elif time.time() - agent['started_at'] > timeout_seconds:
                # Timeout - trigger retry
                agent['status'] = 'timeout'
                print(f"TIMEOUT: {agent['dimension']} after {timeout_seconds}s")
        
        # Progress update
        print(f"Progress: {len(completed)}/8 dimensions evaluated")
        
        # Poll every 30 seconds
        time.sleep(30)
    
    return agents
```

### 3.2 Handle Failures

```python
def handle_failed_agents(agents: list, plan: dict, overlap_rules: str) -> list:
    """Retry failed sub-agents or fall back to sequential."""
    
    MAX_RETRIES = 2
    
    for agent in agents:
        if agent['status'] in ['timeout', 'parse_error']:
            retries = 0
            
            while retries < MAX_RETRIES and agent['status'] != 'completed':
                print(f"Retrying {agent['dimension']} (attempt {retries + 1}/{MAX_RETRIES})")
                
                # Re-launch sub-agent
                dim = next(d for d in DIMENSIONS if d['name'] == agent['dimension'])
                prompt = generate_dimension_prompt(dim, plan, overlap_rules)
                
                agent_id = runSubagent(
                    subagent_type="generalPurpose",
                    description=f"Evaluate {dim['name']} dimension (retry)",
                    prompt=prompt,
                    readonly=True
                )
                
                agent['id'] = agent_id
                agent['started_at'] = time.time()
                
                # Wait for result with shorter timeout
                time.sleep(60)
                result = get_agent_output(agent_id)
                
                if result:
                    try:
                        parsed = json.loads(result)
                        agent['status'] = 'completed'
                        agent['result'] = result
                    except json.JSONDecodeError:
                        retries += 1
                else:
                    retries += 1
            
            if agent['status'] != 'completed':
                # Fall back to sequential evaluation
                print(f"FALLBACK: Evaluating {agent['dimension']} sequentially")
                agent['result'] = evaluate_dimension_sequential(
                    agent['dimension'],
                    plan,
                    overlap_rules
                )
                agent['status'] = 'completed_sequential'
    
    return agents
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
                    'evidence': [],
                    'issues_found': [],
                    'issues_deferred': [],
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
    from overlap_validator import validate_overlaps
    
    violations = validate_overlaps(results, overlap_rules)
    
    if violations:
        print(f"WARNING: {len(violations)} overlap violations detected")
        for v in violations:
            print(f"  Line {v['line']}: claimed by {v['claimed_by']}, owned by {v['owned_by']}")
    
    return violations
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
    plan_path: str,
    final_score: dict,
    results: list,
    violations: list,
    model: str,
    date: str
) -> str:
    """Generate final review document."""
    
    plan_name = os.path.basename(plan_path).replace('.md', '')
    
    doc = f"""# Plan Review: {plan_name}

**Date:** {date}
**Model:** {model}
**Mode:** FULL (Parallel Execution)
**Plan:** {plan_path}

---

## Summary

| Score | Verdict |
|-------|---------|
| **{final_score['total_score']}/100** | **{get_verdict(final_score['total_score'])}** |

---

## Score Breakdown

| Dimension | Raw | Weight | Points | Max |
|-----------|-----|--------|--------|-----|
"""
    
    for ws in final_score['worksheets']:
        doc += f"| {ws['dimension']} | {ws['raw_score']}/10 | ×{ws['weight']/2} | {ws['points']} | {ws['max_points']} |\n"
    
    doc += f"| **TOTAL** | | | **{final_score['total_score']}** | **100** |\n"
    
    # Add dimension details
    for result in results:
        doc += f"\n---\n\n### {result['dimension'].title()}: {result['raw_score']}/10\n\n"
        
        if result.get('evidence'):
            doc += "**Evidence:**\n"
            for ev in result['evidence'][:5]:
                doc += f"- Line {ev['line']}: {ev['pattern']} - \"{ev['quote'][:50]}...\"\n"
        
        if result.get('issues_found'):
            doc += "\n**Issues:**\n"
            for issue in result['issues_found'][:5]:
                doc += f"- Line {issue['line']}: {issue['description']}\n"
    
    # Add overlap violations if any
    if violations:
        doc += "\n---\n\n## Overlap Violations\n\n"
        for v in violations:
            doc += f"- Line {v['line']}: {v['pattern']} claimed by {v['claimed_by']}, owned by {v['owned_by']}\n"
    
    doc += "\n\n.... Generated with [Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)\n"
    
    return doc


def get_verdict(score: float) -> str:
    """Map score to verdict."""
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

---

## Complete Execution Flow

```python
def execute_parallel_review(plan_path: str, params: dict) -> str:
    """Main entry point for parallel plan review."""
    
    print("=== Parallel Plan Review ===")
    print(f"Plan: {plan_path}")
    
    # Phase 1: Setup
    print("\nPhase 1: Loading plan and rules...")
    plan = load_plan_content(plan_path)
    overlap_rules = load_overlap_rules()
    print(f"Plan loaded: {plan['line_count']} lines")
    
    # Phase 2: Launch sub-agents
    print("\nPhase 2: Launching 8 dimension sub-agents...")
    agents = launch_dimension_subagents(plan, overlap_rules, params)
    print(f"Launched {len(agents)} sub-agents")
    
    # Phase 3: Monitor progress
    print("\nPhase 3: Monitoring sub-agent progress...")
    agents = monitor_subagents(agents, timeout_seconds=90)
    agents = handle_failed_agents(agents, plan, overlap_rules)
    
    # Phase 4: Collect & validate
    print("\nPhase 4: Collecting and validating results...")
    results = collect_dimension_results(agents)
    violations = validate_no_overlaps(results, overlap_rules)
    
    # Phase 5: Aggregate & report
    print("\nPhase 5: Aggregating scores and generating report...")
    final_score = aggregate_final_score(results)
    
    review = generate_review_document(
        plan_path=plan_path,
        final_score=final_score,
        results=results,
        violations=violations,
        model=params.get('model', 'unknown'),
        date=params.get('date', 'unknown')
    )
    
    print(f"\n=== Review Complete ===")
    print(f"Final Score: {final_score['total_score']}/100")
    print(f"Verdict: {get_verdict(final_score['total_score'])}")
    
    return review
```

---

## Error Recovery Reference

| Error | Detection | Recovery |
|-------|-----------|----------|
| Sub-agent timeout | No response after 90s | Retry up to 2 times, then sequential fallback |
| JSON parse failure | Invalid JSON in result | Retry with schema reminder, then regex fallback |
| API rate limiting | 429 response | 5s delay already applied; increase to 10s if persistent |
| Resource exhaustion | Sub-agent crashes | Reduce parallelism to batches of 4 |

---

## Performance Targets

| Metric | Sequential | Parallel | Improvement |
|--------|------------|----------|-------------|
| Execution time | ~15-20 min | ~3-5 min | 4-6× faster |
| Token cost | ~15K | ~120K | 8× higher |
| Context freshness | Degraded after dim 4 | Fresh for all | Better accuracy |
| Fault tolerance | Restart from beginning | Retry single dimension | Improved |
