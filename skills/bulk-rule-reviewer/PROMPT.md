# Bulk Rule Reviewer - Implementation Guidance

# 🚨 CRITICAL EXECUTION PROTOCOL 🚨

**READ THIS FIRST - NON-NEGOTIABLE REQUIREMENTS**

You are about to execute the bulk-rule-reviewer skill. This skill orchestrates rule-reviewer invocations. You MUST follow the workflow EXACTLY as written.

## Protocol Violations (FORBIDDEN)

Agents commonly attempt these optimizations. **ALL ARE FORBIDDEN:**

### ❌ Reimplementing rule-reviewer logic
**Violation:** "I'll create a Python script that scores rules based on the rubric..."
**Why Forbidden:** Loses domain expertise, rubric complexity, and review consistency

### ❌ Batch processing reviews
**Violation:** "I'll review multiple rules in one pass to save time..."
**Why Forbidden:** Each rule requires isolated context and full attention

### ❌ Abbreviated reviews
**Violation:** "I'll do quick checks instead of full FULL mode reviews..."
**Why Forbidden:** Quality standards require complete evaluation

### ❌ Parallel execution shortcuts
**Violation:** "I'll run 10 reviews at once to finish faster..."
**Why Forbidden:** Context overflow and quality degradation (unless max_parallel explicitly set)

### ❌ Token-saving shortcuts
**Violation:** "I'll skip reading full rule files to save tokens..."
**Why Forbidden:** Incomplete analysis produces invalid scores

## Required Behavior

**YOU MUST:**
1. ✅ Invoke `rule-reviewer` skill for EACH rule file individually
2. ✅ Use exact parameters: target_file, review_date, review_mode, model
3. ✅ Wait for "Review written to: ..." confirmation before continuing
4. ✅ Follow all 4 stages in workflows/ directory sequentially
5. ✅ Show progress updates every 10 reviews (no more frequent to avoid spam)

## Execution Acknowledgment

**Before proceeding, confirm:**
- [ ] I will invoke rule-reviewer for each rule (no reimplementation)
- [ ] I will follow workflows/01-04 exactly as written
- [ ] I will NOT optimize for time/tokens at expense of quality
- [ ] I understand this process takes 5-10 hours for 113 rules
- [ ] I will use resume capability (skip_existing) if interrupted

**If you cannot commit to these requirements, STOP and report error.**

---

## Purpose

Operational instructions for AI agents executing the bulk-rule-reviewer skill. This document bridges skill invocation and workflow execution.

---

## Execution Flow

When a user invokes the bulk-rule-reviewer skill, follow this sequence:

### 1. Input Validation

**Action:** Execute validation checks from `VALIDATION.md`

**Required:**
- Validate review_date format (YYYY-MM-DD)
- Validate review_mode (FULL | FOCUSED | STALENESS)
- Validate model (lowercase-hyphenated)
- Check rules/ directory exists
- Check reviews/ directory writable

**On Failure:** Report errors, exit before workflows

**On Success:** Proceed to Stage 1

---

### 2. Stage 1: Discovery

**Action:** Execute `workflows/01-discovery.md`

**Tasks:**
1. Find all .md files in rules/ directory
2. Apply filter_pattern if specified
3. Sort alphabetically
4. Count matching files

**Output:** List of rule file paths

**Example:**
```
Found 113 rule files

rules/000-global-core.md
rules/001-memory-bank.md
...
```

---

### 3. Stage 2: Review Execution

**Action:** Execute `workflows/02-review-execution.md`

**Inputs:**
- skill_location: Output from Stage 0 ("installed" | "local")
- List of rule file paths (from 01-discovery.md)
- review_date, review_mode, model, skip_existing

**Tasks:**
1. Extract rule name from path
2. Check if review exists (resume capability)
3. If exists AND skip_existing=true: Load score, mark SKIPPED
4. If not exists OR skip_existing=false: Invoke rule-reviewer
5. Parse output path and extract metadata
6. Add to results list
7. Show progress every 10 reviews

**Output:** Results list with scores, verdicts, paths

**Example:**
```
[1/113] Reviewing: rules/000-global-core.md
  ✓ Complete: 100/100 (EXECUTABLE)

[2/113] Reviewing: rules/001-memory-bank.md
  ✓ Complete: 94/100 (EXECUTABLE)

--- Progress: 10/113 complete, 0 failed, 0 skipped ---
    Average score: 91.3/100
```

---

### 4. Stage 3: Aggregation

**Action:** Execute `workflows/03-aggregation.md`

**Tasks:**
1. Extract full metadata from each review file (first 150 lines only)
2. Calculate executive statistics (average, median, distribution)
3. Calculate dimension averages (all 6 dimensions)
4. Analyze critical issues distribution
5. Group by priority tiers (Priority 1-4)
6. Build summary data structure

**Output:** summary_data structure

**Example:**
```
[Stage 3: Aggregation]

Extracting metadata from 111 review files...
  ✓ Scores extracted (111/111)
  ✓ Verdicts parsed (111/111)
  ✓ Dimension scores aggregated (111/111)

Calculating statistics...
  ✓ Executive summary complete
  ✓ Priority tiers assigned
```

---

### 5. Stage 4: Summary Report

**Action:** Execute `workflows/04-summary-report.md`

**Tasks:**
1. Generate markdown report sections
2. Calculate impact × effort ratios for recommendations
3. Write to reviews/_bulk-review-<model>-<date>.md
4. Handle no-overwrite (increment suffix if needed)
5. Print file path

**Output:** Master summary report file path

**Example:**
```
[Stage 4: Summary Report]

Generating master summary report...
  ✓ Executive summary
  ✓ Priority 1-4 sections
  ✓ Top 10 recommendations
  ✓ Appendix table

============================================================
Master summary report written to:
  reviews/_bulk-review-claude-sonnet-45-2026-01-06.md
============================================================
```

---

## Key Implementation Notes

### Context Management

**CRITICAL:** Only read first 150 lines of each review file

**Why:** 113 full reviews exceed context limits

**Implementation:**
```python
with open(review_path, 'r') as f:
    lines = f.readlines()[:150]  # First 150 lines only
    content = ''.join(lines)
```

**Never:** Load full review content into context

---

### Stateless Execution

**Principle:** Each review is independent

**Implementation:**
- Review failure doesn't stop batch
- Log errors, continue with next file
- Failed reviews marked in summary
- Resume capability skips completed reviews

**Example Error Handling:**
```python
try:
    review_result = invoke_rule_reviewer(rule_path, ...)
except Exception as e:
    print(f"  ✗ Failed: {str(e)}")
    results.append({
        "rule_name": rule_name,
        "status": "FAILED",
        "error_message": str(e)
    })
    continue  # Don't stop batch
```

---

### Resume Capability

**Check Before Invoking:**
```python
expected_path = f"reviews/{rule_name}-{model}-{review_date}.md"

if skip_existing and os.path.exists(expected_path):
    print(f"✓ Skipping {rule_name} (review exists)")
    # Load score from existing file
    metadata = extract_metadata_from_review(expected_path)
    results.append({"status": "SKIPPED", ...})
    continue
```

**Benefits:**
- Resume after interruption
- Idempotent execution
- Save 3-4 hours on retry

---

### Progress Tracking

**Show Progress Every 10 Reviews:**
```python
if completed % 10 == 0:
    avg_score = calculate_average_score(results)
    print(f"\n--- Progress: {completed}/{total} complete, {failed} failed, {skipped} skipped ---")
    print(f"    Average score: {avg_score}/100\n")
```

**Why:** Keep user informed during long-running execution (5-10 hours)

---

### No-Overwrite Logic

**Master Summary File:**
```python
base_filename = f"reviews/_bulk-review-{model}-{review_date}.md"

if os.path.exists(base_filename):
    counter = 1
    while True:
        incremented = f"reviews/_bulk-review-{model}-{review_date}-{counter:02d}.md"
        if not os.path.exists(incremented):
            output_path = incremented
            break
        counter += 1
else:
    output_path = base_filename
```

**Result:** No data loss from overwriting existing summaries

---

## Error Handling Patterns

### Review Invocation Failure

**Cause:** Malformed rule, context overflow, missing metadata

**Response:**
1. Log error with rule name: `✗ Failed: <error>`
2. Add FAILED entry to results
3. Continue with next rule
4. Include in "Failed Reviews" section

**Don't:** Stop entire batch

---

### Score Extraction Failure

**Cause:** Review file missing expected format

**Response:**
1. Log warning: `⚠ Warning: Could not extract score`
2. Use defaults: score=None, verdict="PARSE_ERROR"
3. Continue processing

**Don't:** Crash or skip file

---

### Context Overflow

**Cause:** Too many reviews in memory

**Response:**
1. Switch to minimal output mode (reduce verbosity)
2. Continue execution
3. If overflow persists, abort and report progress

**Prevention:** Only read first 150 lines of each review

---

### Empty Rules Directory

**Cause:** No .md files found

**Response:**
1. Report error: "No rule files found in rules/"
2. Exit gracefully (don't generate empty summary)

**Don't:** Create empty/invalid summary

---

## Performance Optimization

### Sequential Execution (Default)

**Setting:** max_parallel=1

**Why:**
- Prevents context overflow
- Stable and predictable
- Recommended for batches >50 rules

**Trade-off:** Slower (5-10 hours for 113 rules)

---

### Parallel Execution (Experimental)

**Setting:** max_parallel >1

**Benefits:** Faster execution (potential)

**Risks:**
- Context overflow more likely
- Complex error handling
- Not recommended for large batches

**Use Case:** Small batches (<20 rules) only

---

### Context Efficiency

**Only Load What's Needed:**
- Review files: First 150 lines only
- Metadata extraction: Regex parsing (fast)
- No full review content in context

**Result:** Can handle 113 reviews without overflow

---

## Output Files

### Individual Reviews (111 files)

**Naming:** `<rule-name>-<model>-<date>.md`

**Example:** `100-snowflake-core-claude-sonnet-45-2026-01-06.md`

**Location:** `reviews/` directory

**Format:** Standard rule-reviewer output

---

### Master Summary (1 file)

**Naming:** `_bulk-review-<model>-<date>.md`

**Example:** `_bulk-review-claude-sonnet-45-2026-01-06.md`

**Location:** `reviews/` directory

**Format:** Consolidated report (see `workflows/04-summary-report.md`)

**Sections:**
1. Executive Summary
2. Priority 1-4
3. Failed Reviews
4. Top 10 Recommendations
5. Next Steps
6. Appendix

---

## Success Criteria Checklist

Before considering execution complete, verify:

- [ ] All matching rules reviewed (or filtered subset)
- [ ] Individual review files written to reviews/
- [ ] Master summary report generated
- [ ] Prioritized improvement list included
- [ ] No context overflow occurred
- [ ] Resume capability functional (if needed)
- [ ] Error handling graceful (failed reviews logged)
- [ ] File path returned to user

---

## Common Pitfalls

### ❌ Loading Full Review Files

**Problem:** Context overflow

**Solution:** Only read first 150 lines

---

### ❌ Stopping on First Failure

**Problem:** Incomplete batch

**Solution:** Log error, continue with next file

---

### ❌ No Progress Tracking

**Problem:** User has no visibility (7+ hours execution)

**Solution:** Print progress every 10 reviews

---

### ❌ Overwriting Existing Summaries

**Problem:** Data loss

**Solution:** Increment suffix (-01, -02) if file exists

---

### ❌ Skipping Validation

**Problem:** Invalid inputs cause cryptic errors mid-execution

**Solution:** Always run validation first (VALIDATION.md)

---

## Integration with rule-reviewer

**Dependency:** This skill requires rule-reviewer skill to be available

**Invocation Pattern:**
```
For each rule file:
  Use the rule-reviewer skill.
  
  target_file: <rule_path>
  review_date: <date>
  review_mode: <mode>
  model: <model>
```

**Parse Output:**
```
Expected: "Review written to: reviews/<filename>.md"
Extract: File path for metadata extraction
```

---

## Monitoring and Debugging

### Progress Indicators

**During Execution:**
- `[N/M] Reviewing: <file>` - Current file
- `✓ Complete: X/100 (VERDICT)` - Success
- `✗ Failed: <error>` - Failure
- `✓ Skipping <rule> (review exists)` - Resume
- `--- Progress: N/M complete ---` - Every 10 reviews

### Final Summary

**At Completion:**
```
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

---

## Related Documentation

- **SKILL.md:** Skill definition and input contract
- **README.md:** Usage guide for users
- **VALIDATION.md:** Input validation rules
- **workflows/*.md:** Detailed workflow implementations
- **examples/*.md:** Complete walkthrough examples
- **tests/*.md:** Test cases and validation

---

**For questions or issues during execution, refer to workflow files in `workflows/` directory for detailed step-by-step instructions.**
