# Workflow 02: Review Execution

## Purpose

Orchestrate rule-reviewer skill invocation for each rule file discovered in Stage 1. Manages progress tracking, error handling, resume capability, and result collection.

## Inputs

- skill_location: Output from Stage 0 ("installed" | "local")
- List of rule file paths (from discovery.md)
- `review_date`: Date stamp for reviews (YYYY-MM-DD)
- `review_mode`: FULL | FOCUSED | STALENESS
- `model`: Model identifier (e.g., claude-sonnet-45)
- `skip_existing`: Boolean (default: true)

## Outputs

- Results list with metadata for each review:
  - `rule_name`: Extracted from file path (e.g., "100-snowflake-core")
  - `score`: Overall score (0-100)
  - `verdict`: EXECUTABLE | EXECUTABLE_WITH_REFINEMENTS | NEEDS_REFINEMENT | NOT_EXECUTABLE
  - `critical_issues`: Count of critical issues
  - `review_path`: Path to generated review file
  - `status`: SUCCESS | FAILED | SKIPPED
  - `error_message`: Error details (if FAILED)

## Implementation

### Step 1: Initialize Progress Tracking

```python
total_files = len(rule_file_paths)
completed = 0
failed = 0
skipped = 0
results = []

print(f"Starting bulk review: {total_files} rules")
print(f"Review mode: {review_mode} | Model: {model} | Date: {review_date}")
print(f"Skip existing: {skip_existing}\n")
```

### Step 1.5: Protocol Enforcement Check

**Anti-Pattern Detection (CRITICAL):**

Before processing any rules, verify the agent understands protocol requirements:

```python
def verify_protocol_compliance():
    """Ensure agent commits to following protocol exactly."""
    
    print("="*60)
    print("PROTOCOL VERIFICATION")
    print("="*60)
    print()
    print("This workflow REQUIRES:")
    print("  ✓ Invoke rule-reviewer skill for EACH rule")
    print("  ✓ NO batch processing or parallel shortcuts")
    print("  ✓ NO reimplementation of review logic")
    print("  ✓ FULL reviews (not abbreviated)")
    print("  ✓ Sequential execution (unless max_parallel set)")
    print()
    print("Estimated time: 5-10 hours for 113 rules")
    print("Resume capability: Use skip_existing=true to resume after interruption")
    print()
    print("="*60)
    print()
    
    # This serves as documentation/reminder; agent cannot self-verify
    # User must monitor for protocol violations during execution

verify_protocol_compliance()
```

**Monitor for These Violations:**

**Violation Pattern 1: Batch implementation attempt**
```python
# ❌ FORBIDDEN - This violates protocol
for rule_batch in chunks(rule_files, batch_size=10):
    results = batch_review_rules(rule_batch)  # WRONG!
```

**Correct Pattern:**
```python
# ✅ REQUIRED - Individual invocations
for rule_path in rule_file_paths:
    review_result = invoke_rule_reviewer(  # Correct!
        target_file=rule_path,
        review_date=review_date,
        review_mode=review_mode,
        model=model,
        skill_location=skill_location
    )
```

**Violation Pattern 2: Python reimplementation**
```python
# ❌ FORBIDDEN - Recreating rule-reviewer logic
def quick_score_rule(rule_content):
    score = calculate_actionability(rule_content)  # WRONG!
    return score
```

**Correct Pattern:**
```python
# ✅ REQUIRED - Delegate to rule-reviewer skill
review_result = invoke_rule_reviewer(...)  # Correct!
```

**Violation Detection:**

If execution completes in < 2 hours for 100+ rules: **LIKELY PROTOCOL VIOLATION**
- Expected: 3-5 minutes per review × 113 rules = 5.6-9.4 hours minimum
- If faster: Agent probably took shortcuts

**User Action:** Inspect review files for quality/completeness

```

### Step 2: Process Each Rule File

```python
for rule_path in rule_file_paths:
    # Extract rule name from path
    # Example: "rules/100-snowflake-core.md" → "100-snowflake-core"
    rule_name = extract_rule_name(rule_path)
    
    # Build expected review file path
    expected_review_path = f"reviews/{rule_name}-{model}-{review_date}.md"
    
    # Check if review already exists (resume capability)
    if skip_existing and file_exists(expected_review_path):
        print(f"✓ Skipping {rule_name} (review exists)")
        
        # Load existing score from file (read first 100 lines)
        existing_score = extract_score_from_existing_review(expected_review_path)
        
        results.append({
            "rule_name": rule_name,
            "score": existing_score["score"],
            "verdict": existing_score["verdict"],
            "critical_issues": existing_score["critical_issues"],
            "review_path": expected_review_path,
            "status": "SKIPPED"
        })
        
        skipped += 1
        continue
    
    # Invoke rule-reviewer skill
    completed += 1
    print(f"[{completed}/{total_files}] Reviewing: {rule_path}")
    
    try:
        # Invoke rule-reviewer with parameters
        review_result = invoke_rule_reviewer(
            target_file=rule_path,
            review_date=review_date,
            review_mode=review_mode,
            model=model,
            skill_location=skill_location
        )
        
        # Parse output from rule-reviewer response
        # Expected format: "Review written to: reviews/100-snowflake-core-claude-sonnet-45-2026-01-06.md"
        review_path = parse_review_path(review_result)
        
        # Extract score and verdict (read first 100 lines only)
        metadata = extract_metadata_from_review(review_path)
        
        results.append({
            "rule_name": rule_name,
            "score": metadata["score"],
            "verdict": metadata["verdict"],
            "critical_issues": metadata["critical_issues"],
            "review_path": review_path,
            "status": "SUCCESS"
        })
        
        print(f"  ✓ Complete: {metadata['score']}/100 ({metadata['verdict']})")
        
    except Exception as e:
        # Log error and continue with next file
        failed += 1
        error_message = str(e)
        
        print(f"  ✗ Failed: {error_message}")
        
        results.append({
            "rule_name": rule_name,
            "score": None,
            "verdict": "FAILED",
            "critical_issues": None,
            "review_path": None,
            "status": "FAILED",
            "error_message": error_message
        })
    
    # Show running statistics
    if completed % 10 == 0:
        avg_score = calculate_average_score(results)
        print(f"\n--- Progress: {completed}/{total_files} complete, {failed} failed, {skipped} skipped ---")
        print(f"    Average score: {avg_score}/100\n")
```

### Step 3: Summary Report

```python
print(f"\n{'='*60}")
print(f"Bulk Review Complete")
print(f"{'='*60}")
print(f"Total rules: {total_files}")
print(f"Successful: {completed - failed}")
print(f"Failed: {failed}")
print(f"Skipped: {skipped}")
print(f"Average score: {calculate_average_score(results)}/100")
print(f"{'='*60}\n")

return results
```

## Helper Functions

### extract_rule_name(file_path)

```python
def extract_rule_name(file_path):
    """Extract rule name from file path.
    
    Example: "rules/100-snowflake-core.md" → "100-snowflake-core"
    """
    import os
    basename = os.path.basename(file_path)  # "100-snowflake-core.md"
    name_without_ext = os.path.splitext(basename)[0]  # "100-snowflake-core"
    return name_without_ext
```

### file_exists(path)

```python
def file_exists(path):
    """Check if file exists at given path."""
    import os
    return os.path.exists(path)
```

### extract_metadata_from_review(review_path)

```python
def extract_metadata_from_review(review_path):
    """Extract score, verdict, and critical issues from review file.
    
    Reads ONLY first 100 lines to avoid context overflow.
    """
    import re
    
    with open(review_path, 'r') as f:
        lines = f.readlines()[:100]  # First 100 lines only
        content = ''.join(lines)
    
    # Extract overall score: "**Overall:** 85/100"
    score_match = re.search(r'\*\*Overall:\*\* (\d+)/100', content)
    score = int(score_match.group(1)) if score_match else None
    
    # Extract verdict: "### Agent Executability Verdict\n**EXECUTABLE**"
    verdict_match = re.search(r'### Agent Executability Verdict\s+\*\*([A-Z_]+)\*\*', content)
    verdict = verdict_match.group(1) if verdict_match else "UNKNOWN"
    
    # Count critical issues (count occurrences of "### Critical Issues" header)
    # Then count numbered items in that section
    critical_section_match = re.search(r'### Critical Issues\s+(.*?)(?=###|\Z)', content, re.DOTALL)
    if critical_section_match:
        critical_text = critical_section_match.group(1)
        # Count numbered items: "1.", "2.", etc.
        critical_issues = len(re.findall(r'^\d+\.', critical_text, re.MULTILINE))
    else:
        critical_issues = 0
    
    return {
        "score": score,
        "verdict": verdict,
        "critical_issues": critical_issues
    }
```

### parse_review_path(review_result_text)

```python
def parse_review_path(review_result_text):
    """Parse review file path from rule-reviewer output.
    
    Expected format: "Review written to: reviews/100-snowflake-core-claude-sonnet-45-2026-01-06.md"
    """
    import re
    
    match = re.search(r'Review written to:\s+(.+\.md)', review_result_text)
    if match:
        return match.group(1).strip()
    else:
        raise ValueError("Could not parse review path from rule-reviewer output")
```

### calculate_average_score(results)

```python
def calculate_average_score(results):
    """Calculate average score from results list."""
    scores = [r["score"] for r in results if r["score"] is not None]
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 1)
```

### invoke_rule_reviewer(target_file, review_date, review_mode, model, skill_location)

```python
def invoke_rule_reviewer(target_file, review_date, review_mode, model, skill_location):
    """Invoke rule-reviewer skill with location-aware logic.
    
    Args:
        target_file: Path to rule file (e.g., rules/100-snowflake-core.md)
        review_date: Date stamp (YYYY-MM-DD)
        review_mode: FULL | FOCUSED | STALENESS
        model: Model identifier (e.g., claude-sonnet-45)
        skill_location: "installed" | "local"
    
    Returns:
        Text response from rule-reviewer including review file path
    """
    if skill_location == "installed":
        # Use agent's skill invocation mechanism
        result = invoke_skill(
            "rule-reviewer",
            target_file=target_file,
            review_date=review_date,
            review_mode=review_mode,
            model=model
        )
    elif skill_location == "local":
        # Execute local skill manually by following SKILL.md
        skill_template = read_file("skills/rule-reviewer/SKILL.md")
        
        # Substitute parameters into template
        prompt = skill_template.replace("[path/to/rule.md]", target_file)
        prompt = prompt.replace("[YYYY-MM-DD]", review_date)
        prompt = prompt.replace("[FULL | FOCUSED | STALENESS]", review_mode)
        
        # Execute the prompt instructions directly
        result = execute_rule_reviewer_workflow(prompt, model)
    else:
        raise ValueError(f"Unknown skill_location: {skill_location}")
    
    return result
```

## Error Handling

### Review Invocation Failure

**Cause:** rule-reviewer skill fails (malformed rule, context overflow, etc.)

**Action:**
1. Log error with rule name and error message
2. Add FAILED entry to results list
3. Continue with next rule (don't stop batch)
4. Include in "Failed Reviews" section of master summary

**Example:**
```
  ✗ Failed: Malformed markdown syntax in rule file
```

### Score Extraction Failure

**Cause:** Review file generated but score/verdict not parseable

**Action:**
1. Log warning
2. Use default values: score=None, verdict="PARSE_ERROR"
3. Include in results with PARSE_ERROR status
4. Continue with next rule

**Example:**
```
  ⚠ Warning: Could not extract score from review file
```

### Context Overflow

**Cause:** Too many reviews in memory, context limit approaching

**Action:**
1. Switch to minimal output mode
2. Reduce progress output verbosity
3. Continue execution
4. If overflow persists, abort and report progress

### File Write Failure

**Cause:** Cannot write review file to disk (permissions, disk full)

**Action:**
1. Print OUTPUT_FILE directive for manual save
2. Log error in results
3. Continue with next rule

## Resume Capability

**How It Works:**

1. Before invoking rule-reviewer, check if review file already exists
2. If `skip_existing=true` AND file exists: Load score from existing file, mark as SKIPPED
3. If `skip_existing=false` OR file doesn't exist: Invoke rule-reviewer normally

**Benefits:**
- Can resume after interruption (context overflow, timeout, error)
- Avoid wasting work re-reviewing already-completed rules
- Idempotent execution (running multiple times produces same result)

**Example:**
```
✓ Skipping 100-snowflake-core (review exists)
✓ Skipping 101-snowflake-sql-style (review exists)
[3/113] Reviewing: rules/102-snowflake-warehouse-sizing.md
  ✓ Complete: 85/100 (EXECUTABLE_WITH_REFINEMENTS)
```

## Progress Tracking

**Output Format:**

```
Starting bulk review: 113 rules
Review mode: FULL | Model: claude-sonnet-45 | Date: 2026-01-06
Skip existing: true

[1/113] Reviewing: rules/000-global-core.md
  ✓ Complete: 100/100 (EXECUTABLE)
[2/113] Reviewing: rules/001-memory-bank.md
  ✓ Complete: 92/100 (EXECUTABLE)
[3/113] Reviewing: rules/002-rule-governance.md
  ✓ Complete: 88/100 (EXECUTABLE_WITH_REFINEMENTS)
...

--- Progress: 10/113 complete, 0 failed, 0 skipped ---
    Average score: 89.3/100

[11/113] Reviewing: rules/100-snowflake-core.md
  ✓ Complete: 100/100 (EXECUTABLE)
...

--- Progress: 20/113 complete, 1 failed, 0 skipped ---
    Average score: 87.8/100

...

============================================================
Bulk Review Complete
============================================================
Total rules: 113
Successful: 111
Failed: 2
Skipped: 0
Average score: 87.2/100
============================================================
```

## Performance Notes

- Average review time: 3-5 minutes per rule (varies by rule length and complexity)
- Total expected time for 113 rules: 5.6-9.4 hours (sequential execution)
- Resume capability critical for long-running batches
- Progress updates every 10 rules reduce output verbosity

## Integration with Next Workflow

**Output of this workflow** → **Input to aggregation.md**

The results list produced by this workflow is passed to the aggregation workflow, which calculates statistics and prepares data for the master summary report.

## Testing Checklist

- [ ] Successfully invokes rule-reviewer for single rule
- [ ] Handles review failure gracefully (logs error, continues)
- [ ] Resume capability works (skips existing reviews)
- [ ] Progress tracking displays correctly
- [ ] Score extraction works from review files
- [ ] Results list contains all expected fields
- [ ] Failed reviews marked with error messages
