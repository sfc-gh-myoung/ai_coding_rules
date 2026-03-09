# Workflow 02: Review Execution

## Purpose

Execute the rule-reviewer workflow for each rule file discovered in Stage 1. This workflow FOLLOWS the documented review process by loading and applying the rule-reviewer skill's methodology. Manages progress tracking, error handling, resume capability, and result collection.

## Critical Understanding

**Skills cannot invoke other skills programmatically.** This workflow achieves batch processing by:

1. **Loading** `skills/rule-reviewer/SKILL.md` to understand the review workflow
2. **Following** that workflow for each rule file
3. **Using** progressive disclosure to load rubrics/ as needed
4. **Maintaining** the same quality standards as single-rule reviews

This is how skill composition works in Claude Code - orchestrator skills load and follow worker skill workflows.

## Inputs

- skill_location: Output from Stage 0 ("installed" | "local")
- List of rule file paths (from discovery.md)
- `review_date`: Date stamp for reviews (YYYY-MM-DD)
- `review_mode`: FULL | FOCUSED | STALENESS
- `model`: Model identifier (e.g., claude-sonnet-45)
- `skip_existing`: Boolean (default: true)
- `max_parallel`: Integer 1-10 (default: 5) - Number of concurrent sub-agents
- `output_root`: Root directory for output files (default: `reviews/`)

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

### Step 0: Execution Mode Decision

**CRITICAL: Choose execution path based on `max_parallel` parameter.**

```python
def choose_execution_mode(max_parallel, rule_file_paths, params):
    """Route to parallel or sequential execution.
    
    Args:
        max_parallel: Number of concurrent workers (default: 5)
        rule_file_paths: List of rule files from discovery
        params: Dict with review_date, review_mode, model, etc.
    
    Returns:
        Results list from chosen execution mode
    """
    if max_parallel >= 2:
        # PARALLEL EXECUTION (default)
        print(f"Execution mode: PARALLEL ({max_parallel} sub-agents)")
        print("See: workflows/parallel-execution.md")
        return execute_parallel(max_parallel, rule_file_paths, params)
    else:
        # SEQUENTIAL EXECUTION (legacy)
        print("Execution mode: SEQUENTIAL (single agent)")
        return execute_sequential(rule_file_paths, params)
```

#### Parallel Execution Path (max_parallel ≥ 2)

When parallel mode is selected, delegate to `workflows/parallel-execution.md`:

1. **Partition rules** into `max_parallel` groups
2. **Launch sub-agents** with prompts from `workflows/subagent-prompt-template.md`
3. **Monitor progress** via `agent_output` tool
4. **Aggregate results** when all complete

**Benefits:**
- 5× speedup (~50 minutes vs 4-6 hours)
- Fresh context per sub-agent (no drift)
- Isolated failures

**See:** `workflows/parallel-execution.md` for full implementation

#### Sequential Execution Path (max_parallel = 1)

When sequential mode is selected, continue with the steps below (Step 1 onwards).

**Use sequential when:**
- Debugging/troubleshooting
- Very small rule sets (< 10 rules)
- Explicit user preference

---

## Sequential Execution Implementation

*The following steps apply only when `max_parallel = 1`.*

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
    print("   Execute rule-reviewer workflow for EACH rule")
    print("   Load rule-reviewer/SKILL.md to understand process")
    print("   Load rubrics/*.md for dimension scoring")
    print("   Run ai-rules validate for each rule")
    print("   NO batch processing or parallel shortcuts")
    print("   FULL reviews (not abbreviated)")
    print("   Sequential execution (unless max_parallel set)")
    print()
    print("Estimated time: 4-6 hours for 129 rules")
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
#  FORBIDDEN - This violates protocol
for rule_batch in chunks(rule_files, batch_size=10):
    results = batch_review_rules(rule_batch)  # WRONG!
```

**Correct Pattern:**
```python
#  REQUIRED - Individual workflow execution
for rule_path in rule_file_paths:
    # Load rule-reviewer workflow if not already loaded
    if not workflow_loaded:
        load_rule_reviewer_skill()
        workflow_loaded = True
    
    # Execute complete review workflow for this rule
    review_result = execute_rule_review_workflow(
        target_file=rule_path,
        review_date=review_date,
        review_mode=review_mode,
        model=model
    )
```

**Violation Pattern 2: Skipping rubrics**
```python
#  FORBIDDEN - Scoring without rubric consultation
def quick_score_rule(rule_content):
    score = estimate_actionability(rule_content)  # WRONG! No rubric
    return score
```

**Correct Pattern:**
```python
#  REQUIRED - Load rubric and score according to criteria
def score_actionability(rule_content):
    rubric = load_file("skills/rule-reviewer/rubrics/actionability.md")
    # Apply rubric criteria to rule content
    score = apply_rubric_criteria(rule_content, rubric)
    return score
```

**Violation Detection:**

If execution completes in < 2 hours for 100+ rules: **LIKELY PROTOCOL VIOLATION**
- Expected: 3-5 minutes per review × 113 rules = 5.6-9.4 hours minimum
- If faster: Agent probably took shortcuts

**User Action:** Inspect review files for quality/completeness

```

### Step 2: Process Each Rule File

```python
# Load rule-reviewer workflow once at the start
workflow_loaded = False

for rule_path in rule_file_paths:
    # Extract rule name from path
    # Example: "rules/100-snowflake-core.md" → "100-snowflake-core"
    rule_name = extract_rule_name(rule_path)
    
    # Build expected review file path
    expected_review_path = f"reviews/rule-reviews/{rule_name}-{model}-{review_date}.md"
    
    # Check if review already exists (resume capability)
    if skip_existing and file_exists(expected_review_path):
        print(f" Skipping {rule_name} (review exists)")
        
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
    
    # Load rule-reviewer workflow on first iteration
    if not workflow_loaded:
        print("Loading rule-reviewer workflow...")
        load_rule_reviewer_skill()
        workflow_loaded = True
    
    # Execute rule-reviewer workflow
    completed += 1
    print(f"[{completed}/{total_files}] Reviewing: {rule_path}")
    
    try:
        # Execute complete review workflow following rule-reviewer/SKILL.md
        review_result = execute_rule_review_workflow(
            target_file=rule_path,
            review_date=review_date,
            review_mode=review_mode,
            model=model
        )
        
        # Review workflow writes file and returns path
        review_path = review_result["review_path"]
        
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
        
        print(f"   Complete: {metadata['score']}/100 ({metadata['verdict']})")
        
    except Exception as e:
        # Log error and continue with next file
        failed += 1
        error_message = str(e)
        
        print(f"   Failed: {error_message}")
        
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

### Step 4: Drift Detection After Each Review (MANDATORY)

**After writing each review file, check for context drift:**

```python
def check_for_drift(review_path, rule_number):
    """Detect optimization drift via review quality indicators."""
    import os
    
    review_size = os.path.getsize(review_path)
    
    # Size-based drift detection
    if review_size < 2500:
        print(f"DRIFT DETECTED at rule #{rule_number}: Review only {review_size} bytes")
        print("Executing context refresh...")
        read_file("skills/bulk-rule-reviewer/CRITICAL_CONTEXT.md")
        return True
    
    # Periodic context refresh (every 10 rules)
    if rule_number % 10 == 0:
        print(f"Context refresh at rule #{rule_number}")
        read_file("skills/bulk-rule-reviewer/CRITICAL_CONTEXT.md")
    
    return False

# In main loop, after writing review:
drift_detected = check_for_drift(review_path, completed)
if drift_detected:
    # Re-read full SKILL.md if drift detected
    read_file("skills/bulk-rule-reviewer/SKILL.md")
```

**Why structural enforcement?** LLM context summarization drops "older" content (skill instructions from start) to make room for "newer" content (rules and reviews). File re-reads inject fresh context that cannot be summarized.

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

### load_rule_reviewer_skill()

```python
def load_rule_reviewer_skill():
    """Load rule-reviewer skill to understand its workflow.
    
    This function reads the rule-reviewer SKILL.md to understand the
    complete review process that will be followed for each rule.
    """
    skill_doc = read_file("skills/rule-reviewer/SKILL.md")
    print(f"  Loaded rule-reviewer workflow ({len(skill_doc)} chars)")
    
    # Note rubric locations for progressive disclosure during reviews
    rubric_paths = {
        "actionability": "skills/rule-reviewer/rubrics/actionability.md",
        "completeness": "skills/rule-reviewer/rubrics/completeness.md",
        "consistency": "skills/rule-reviewer/rubrics/consistency.md",
        "parsability": "skills/rule-reviewer/rubrics/parsability.md",
        "token-efficiency": "skills/rule-reviewer/rubrics/token-efficiency.md",
        "staleness": "skills/rule-reviewer/rubrics/staleness.md"
    }
    
    return skill_doc, rubric_paths

### execute_rule_review_workflow(target_file, review_date, review_mode, model)

```python
def execute_rule_review_workflow(target_file, review_date, review_mode, model):
    """Execute the complete rule-reviewer workflow for a single rule.
    
    Follows the workflow defined in skills/rule-reviewer/SKILL.md:
    1. Validate inputs
    2. Run schema validation (ai-rules validate)
    3. Perform Agent Execution Test
    4. Score dimensions (load rubrics progressively as needed)
    5. Generate recommendations
    6. Write review file
    
    This function implements the workflow by following the documentation,
    not by "invoking" the rule-reviewer skill (which is not possible).
    
    Args:
        target_file: Path to rule file (e.g., rules/100-snowflake-core.md)
        review_date: Date stamp (YYYY-MM-DD)
        review_mode: FULL | FOCUSED | STALENESS
        model: Model identifier (e.g., claude-sonnet-45)
    
    Returns:
        dict with keys: review_path, score, verdict, critical_issues
    """
    # Step 1: Validate inputs
    validate_review_inputs(target_file, review_date, review_mode, model)
    
    # Step 2: Run schema validation
    schema_results = run_schema_validation(target_file)
    
    # Step 3: Read rule file
    rule_content = read_file(target_file)
    
    # Step 4: Agent Execution Test
    blocking_issues = perform_agent_execution_test(rule_content)
    
    # Step 5: Score dimensions (load rubrics progressively)
    dimension_scores = score_dimensions(rule_content, review_mode, blocking_issues)
    
    # Step 6: Generate recommendations
    recommendations = generate_recommendations(
        rule_content, 
        dimension_scores, 
        schema_results, 
        blocking_issues
    )
    
    # Step 7: Write review file
    review_path = write_review_file(
        target_file=target_file,
        review_date=review_date,
        model=model,
        dimension_scores=dimension_scores,
        schema_results=schema_results,
        blocking_issues=blocking_issues,
        recommendations=recommendations
    )
    
    return {
        "review_path": review_path,
        "score": dimension_scores["overall"],
        "verdict": dimension_scores["verdict"],
        "critical_issues": len(blocking_issues)
    }
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
   Failed: Malformed markdown syntax in rule file
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
 Skipping 100-snowflake-core (review exists)
 Skipping 101-snowflake-sql-style (review exists)
[3/113] Reviewing: rules/102-snowflake-warehouse-sizing.md
   Complete: 85/100 (EXECUTABLE_WITH_REFINEMENTS)
```

## Progress Tracking

**CRITICAL: Silent Processing Mode**

All internal analysis (canary checks, dimension scoring, evidence gathering) is SILENT.
Only show the minimal progress output below. Do NOT display:
- Canary check questions/answers
- Post-Read verification details ("3 unique things...")
- Agent Execution Test scan results
- Dimension score breakdowns during processing
- Evidence citations while analyzing

**Output Format (ONLY this format):**

```
Starting bulk review: 129 rules
Review mode: FULL | Model: claude-sonnet-45 | Date: 2026-01-06
Skip existing: true

[1/113] Starting: 000-global-core.md
[1/113] Complete: 000-global-core.md → 100/100
[2/113] Starting: 001-memory-bank.md
[2/113] Complete: 001-memory-bank.md → 92/100
[3/113] Starting: 002-rule-governance.md
[3/113] Complete: 002-rule-governance.md → 88/100
...

--- Progress: 10/113, avg 89.3 ---

[11/113] Starting: 100-snowflake-core.md
[11/113] Complete: 100-snowflake-core.md → 95/100
...

--- Progress: 20/113, avg 87.8 ---

...

============================================================
Bulk Review Complete
============================================================
Total: 113 | Success: 111 | Failed: 2 | Skipped: 0
Average score: 87.2/100
============================================================
```

**What goes WHERE:**

| Content | Destination |
|---------|-------------|
| Progress (Starting/Complete) | Console |
| Canary checks | Internal only (silent) |
| Dimension scores with evidence | Review FILE |
| Agent Execution Test details | Review FILE |
| Recommendations with line numbers | Review FILE |

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
