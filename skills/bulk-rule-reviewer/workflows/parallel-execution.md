# Workflow: Parallel Execution with Sub-Agents

## Purpose

Execute bulk rule reviews using parallel sub-agents to achieve:
1. **5× speedup** (~50 minutes instead of 4-6 hours for 129 rules)
2. **Eliminate context drift** (fresh context per sub-agent)
3. **Improved fault tolerance** (isolated failures)

## When to Use

- **Parallel execution (default):** `max_parallel >= 2`
- **Sequential execution:** `max_parallel = 1` (legacy behavior)

## Architecture

```
Main Agent (Coordinator)
│
├── Stage 1: Discovery
│   └── Find all rules, partition into N groups
│
├── Stage 2: Launch Sub-Agents (parallel)
│   ├── Sub-Agent 1: rules group 1 [background]
│   ├── Sub-Agent 2: rules group 2 [background]
│   ├── Sub-Agent 3: rules group 3 [background]
│   ├── Sub-Agent 4: rules group 4 [background]
│   └── Sub-Agent 5: rules group 5 [background]
│
├── Stage 3: Monitor Progress
│   └── Poll each sub-agent via agent_output
│
├── Stage 4: Collect Results
│   └── Aggregate summaries from all sub-agents
│
└── Stage 5: Generate Master Summary
    └── Combine results into _bulk-review-{model}-{date}.md
```

## Implementation

### Step 1: Partition Rules by Domain

Group rules by their numeric prefix to keep related rules together:

```python
def partition_rules_by_domain(rule_files, num_workers=5):
    """Partition rules into domain-based groups for parallel processing.
    
    Domain groupings:
    - 000-0xx: Foundation/Meta rules
    - 100-1xx: Snowflake rules
    - 200-2xx: Python rules
    - 300-4xx: Shell/JS/TS rules
    - 500-9xx: Other/Project rules
    """
    domains = {
        'foundation': [],  # 000-099
        'snowflake': [],   # 100-199
        'python': [],      # 200-299
        'scripting': [],   # 300-499
        'other': []        # 500-999
    }
    
    for rule_path in rule_files:
        rule_name = extract_rule_name(rule_path)
        prefix = int(rule_name.split('-')[0])
        
        if prefix < 100:
            domains['foundation'].append(rule_path)
        elif prefix < 200:
            domains['snowflake'].append(rule_path)
        elif prefix < 300:
            domains['python'].append(rule_path)
        elif prefix < 500:
            domains['scripting'].append(rule_path)
        else:
            domains['other'].append(rule_path)
    
    # Combine into N roughly-equal groups
    all_rules = []
    for domain_rules in domains.values():
        all_rules.extend(domain_rules)
    
    return chunk_list(all_rules, num_workers)


def chunk_list(items, num_chunks):
    """Split list into N roughly-equal chunks."""
    chunk_size = len(items) // num_chunks
    remainder = len(items) % num_chunks
    
    chunks = []
    start = 0
    for i in range(num_chunks):
        # Distribute remainder across first chunks
        end = start + chunk_size + (1 if i < remainder else 0)
        if start < len(items):
            chunks.append(items[start:end])
        start = end
    
    return [c for c in chunks if c]  # Remove empty chunks
```

### Step 2: Launch Sub-Agents

```python
def launch_parallel_subagents(rule_groups, params):
    """Launch parallel sub-agents for rule reviews.
    
    Args:
        rule_groups: List of rule file lists (one per sub-agent)
        params: Dict with review_date, review_mode, model, output_root, etc.
    
    Returns:
        List of agent_ids for monitoring
    """
    agent_ids = []
    
    for i, rules in enumerate(rule_groups):
        worker_num = i + 1
        rules_list = '\n'.join(f"- {r}" for r in rules)
        
        prompt = generate_subagent_prompt(
            worker_num=worker_num,
            total_workers=len(rule_groups),
            rules=rules,
            params=params
        )
        
        # Launch background sub-agent
        agent_id = task(
            subagent_type="general-purpose",
            description=f"Review rules batch {worker_num}",
            prompt=prompt,
            run_in_background=True,
            agent_mode="autonomous"
        )
        
        agent_ids.append({
            'id': agent_id,
            'worker_num': worker_num,
            'rules': rules,
            'status': 'running'
        })
        
        print(f"[Coordinator] Launched Sub-Agent {worker_num}/{len(rule_groups)} "
              f"with {len(rules)} rules")
    
    return agent_ids
```

### Step 3: Monitor Progress

```python
def monitor_subagents(agent_ids, poll_interval_seconds=60):
    """Poll sub-agents for progress updates.
    
    Args:
        agent_ids: List of agent info dicts from launch_parallel_subagents
        poll_interval_seconds: How often to check (default 60s)
    
    Returns:
        Updated agent_ids with status and results
    """
    all_complete = False
    
    while not all_complete:
        all_complete = True
        
        for agent_info in agent_ids:
            if agent_info['status'] == 'complete':
                continue
            
            # Check agent status
            output = agent_output(agent_id=agent_info['id'])
            
            if output.status == 'complete':
                agent_info['status'] = 'complete'
                agent_info['result'] = parse_subagent_result(output.messages)
                print(f"[Coordinator] Sub-Agent {agent_info['worker_num']} complete: "
                      f"{len(agent_info['result']['completed'])} reviews")
            elif output.status == 'failed':
                agent_info['status'] = 'failed'
                agent_info['error'] = output.error_message
                print(f"[Coordinator] Sub-Agent {agent_info['worker_num']} FAILED: "
                      f"{agent_info['error']}")
            else:
                all_complete = False
        
        if not all_complete:
            # Show progress summary
            running = sum(1 for a in agent_ids if a['status'] == 'running')
            complete = sum(1 for a in agent_ids if a['status'] == 'complete')
            print(f"[Coordinator] Progress: {complete}/{len(agent_ids)} workers complete, "
                  f"{running} running")
            
            # Wait before next poll
            time.sleep(poll_interval_seconds)
    
    return agent_ids
```

### Step 4: Aggregate Results

```python
def aggregate_subagent_results(agent_ids):
    """Combine results from all sub-agents into unified results list.
    
    Args:
        agent_ids: List of agent info dicts with results
    
    Returns:
        Consolidated results list for master summary
    """
    all_results = []
    failed_agents = []
    
    for agent_info in agent_ids:
        if agent_info['status'] == 'complete':
            all_results.extend(agent_info['result']['completed'])
            all_results.extend(agent_info['result']['failed'])
        else:
            # Agent itself failed - mark all its rules as failed
            failed_agents.append(agent_info['worker_num'])
            for rule_path in agent_info['rules']:
                all_results.append({
                    'rule_name': extract_rule_name(rule_path),
                    'score': None,
                    'verdict': 'AGENT_FAILED',
                    'review_path': None,
                    'status': 'FAILED',
                    'error_message': f"Sub-agent {agent_info['worker_num']} failed: "
                                    f"{agent_info.get('error', 'Unknown error')}"
                })
    
    if failed_agents:
        print(f"[Coordinator] WARNING: Sub-agents {failed_agents} failed")
    
    # Sort by rule name for consistent output
    all_results.sort(key=lambda r: r['rule_name'])
    
    return all_results
```

## Sub-Agent Prompt Template

See `workflows/subagent-prompt-template.md` for the complete prompt template that includes:
- Full anti-optimization protocol
- Canary checks for each rule
- Verification requirements (≥15 line refs, 3000-8000 bytes)
- Output format specification

## File Write Strategy

**Direct writes to shared directory** - No conflicts because:

1. Each sub-agent reviews *different* rules
2. Filenames are unique: `{rule-name}-{model}-{date}.md`
3. Different rules = different filenames = no conflicts

```
Sub-Agent 1 writes: 000-global-core-claude-sonnet-45-2026-01-15.md
Sub-Agent 2 writes: 100-snowflake-core-claude-sonnet-45-2026-01-15.md
                    ↑ Different rules, different files
```

## Error Handling

### Sub-Agent Failure

If a sub-agent fails completely:
1. Mark all its assigned rules as `AGENT_FAILED`
2. Continue with results from successful sub-agents
3. Include failure details in master summary
4. User can re-run with `filter_pattern` for failed rules only

### Partial Sub-Agent Failure

If a sub-agent completes but some reviews failed:
1. Sub-agent returns both `completed` and `failed` lists
2. Aggregator includes both in master summary
3. Individual failures don't stop other reviews

### Resume Capability

With `skip_existing=true` (default):
1. Sub-agents check for existing review files before reviewing
2. Already-completed reviews are skipped
3. Re-running after failure only processes incomplete rules

## Performance Characteristics

| Metric | Sequential (max_parallel=1) | Parallel (max_parallel=5) |
|--------|----------------------------|---------------------------|
| Total time | 4-6 hours | ~50 minutes |
| Token cost | ~50K | ~250K (5× skill loading) |
| Dollar cost | ~$0.45 | ~$2.25 |
| Context drift risk | High (after rule 50) | None |
| Fault tolerance | Single point of failure | Isolated failures |

## Integration Points

**Input from:** `workflows/discovery.md` (rule file list)
**Output to:** `workflows/aggregation.md` (consolidated results)
**Uses:** `workflows/subagent-prompt-template.md` (prompt generation)

## Testing Checklist

- [ ] Partitioning produces balanced groups
- [ ] All sub-agents launch successfully
- [ ] Progress monitoring works
- [ ] Results aggregation handles all statuses
- [ ] File writes don't conflict
- [ ] Resume capability works after partial failure
- [ ] Master summary includes all rules
