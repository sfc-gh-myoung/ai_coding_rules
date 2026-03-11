# Sub-Agent Prompt Template

## Purpose

Defines the complete prompt template for sub-agents executing parallel rule reviews. Includes full anti-optimization protocol, canary checks, and verification requirements.

## Template Structure

The prompt is assembled from these sections:
1. **Mission** - What the sub-agent must accomplish
2. **Anti-Optimization Protocol** - Prevents shortcuts
3. **Rule List** - Specific rules assigned to this worker
4. **Execution Protocol** - Step-by-step workflow
5. **Output Requirements** - What to return to coordinator

---

## Complete Prompt Template

```markdown
# Rule Review Sub-Agent: Worker {worker_num}/{total_workers}

## Mission

You are Sub-Agent {worker_num} of {total_workers} in a parallel bulk review operation. Your task is to review {rule_count} rules and write comprehensive reviews to `{output_root}/rule-reviews/`.

**Your assigned rules:**
{rules_list}

**Parameters:**
- review_date: {review_date}
- review_mode: {review_mode}
- model: {model}
- output_root: {output_root}
- skip_existing: {skip_existing}

---

## CRITICAL: Anti-Optimization Protocol

**FOUNDATIONAL PRINCIPLE:** This task prioritizes ACCURACY over efficiency.

**Forbidden Optimization Thoughts:**
- "This will take too long"
- "I can save time by..."
- "Token costs are high"
- "Let me create a faster approach"
- "Let me batch these rules together"
- "I can process multiple rules at once"

**Required Mindset:**
- "I will complete the full process for EACH rule"
- "Quality signals are worth the cost"
- "I was launched knowing the scope - proceed with the work"

**If you find yourself thinking about optimizing:**
1. STOP
2. Re-read this section
3. Return to processing ONE rule at a time

**MANDATORY: One Rule At A Time**

NEVER batch multiple rules. Each rule MUST be processed individually:
1. Read ONE rule file completely
2. Run schema validator for THAT rule
3. Apply ALL rubrics to THAT rule
4. Write review file for THAT rule
5. THEN move to next rule

---

## Execution Protocol

### For EACH rule in your assigned list:

**Step 1: Pre-Rule Canary Check (SILENT)**

Before reading the rule, verify internally:
- What will I find? → "I don't know yet" (CORRECT)
- Can I reuse previous work? → "No, different rule" (CORRECT)
- Any wrong answer → Re-read Anti-Optimization Protocol

**Step 2: Load rule-reviewer Skill and Output Template**

If not already loaded:
```
Read: skills/rule-reviewer/SKILL.md
Read: skills/rule-reviewer/examples/TEMPLATE.md  # CRITICAL: Output format specification
```

**IMPORTANT:** The TEMPLATE.md defines the EXACT output format for reviews. Your reviews MUST match this structure.

**Step 3: Read Rule File**

```
Read: {rule_path}
```

**Step 4: Post-Read Canary Check (SILENT)**

Verify you can:
- Name 3 specific things unique to THIS rule
- Cite a specific line number with content
- State the exact TokenBudget value

Unable to verify → Re-read the rule file

**Step 5: Run Schema Validation**

```bash
uv run ai-rules validate {rule_path}
```

**Step 6: Perform Agent Execution Test**

Count blocking issues:
- Undefined thresholds ("large", "significant", "appropriate")
- Missing conditional branches (no explicit else)
- Ambiguous actions (multiple interpretations)
- Visual formatting (ASCII art, arrows, diagrams)

Cap score at 60 if ≥10 blocking issues.

**Step 7: Score Dimensions**

Load rubrics progressively as needed:
- `skills/rule-reviewer/rubrics/actionability.md`
- `skills/rule-reviewer/rubrics/completeness.md`
- `skills/rule-reviewer/rubrics/consistency.md`
- `skills/rule-reviewer/rubrics/parsability.md`
- `skills/rule-reviewer/rubrics/token-efficiency.md`
- `skills/rule-reviewer/rubrics/rule-size.md`
- `skills/rule-reviewer/rubrics/staleness.md`
- `skills/rule-reviewer/rubrics/cross-agent-consistency.md`

**Step 8: Mid-Review Canary (after dimension 3) (SILENT)**

- Have I loaded the rubric for EACH dimension? (If NO → Go back)
- Do my first 3 dimensions have distinct line references? (If NO → Find new evidence)

**Step 9: Generate Recommendations**

- Specific line numbers
- Quantified fixes
- Expected score improvements

**Step 10: Verify Review Authenticity**

Before writing, verify review contains:
- ≥15 line references (FULL mode)
- Direct quotes with line numbers
- Rule-specific findings (not generic)
- Size: 3000-8000 bytes

**FAILURE → Delete and redo with actual analysis**

**Step 11: Write Review File**

Path: `{output_root}/rule-reviews/{rule_name}-{model}-{review_date}.md`

If file exists and skip_existing=true: Skip this rule.
If file exists and skip_existing=false: Use sequential numbering (-01, -02, etc.)

**Step 12: Track Result**

Add to results:
```json
{
  "rule_name": "{rule_name}",
  "score": {score},
  "verdict": "{verdict}",
  "review_path": "{review_path}",
  "status": "SUCCESS"
}
```

**Step 13: Progress Output**

Output exactly:
```
[{current}/{total}] Complete: {rule_name}.md → {score}/100
```

---

## Evidence Requirements

Every review MUST include:

| Requirement | Minimum | Example |
|-------------|---------|---------|
| Line references | ≥15 distinct | "line 47", "lines 120-135" |
| Direct quotes | ≥3 with line numbers | `Line 156: "Use pd.to_datetime()"` |
| Metadata citation | TokenBudget value | "TokenBudget ~6550 at line 12" |
| Pattern names | ≥2 exact names | "Anti-Pattern 2: Using Deprecated..." |
| Code references | ≥1 function/class name | "The `ensure_python_datetime()` helper" |

**Zero-Recommendation Rule:**
Reviews with "No recommendations" MUST justify with ≥3 specific search attempts with line references.

---

## Output Format

When all assigned rules are complete, return this JSON summary:

```json
{
  "worker_num": {worker_num},
  "total_rules": {rule_count},
  "completed": [
    {
      "rule_name": "000-global-core",
      "score": 95,
      "verdict": "EXECUTABLE",
      "review_path": "reviews/rule-reviews/000-global-core-claude-sonnet-45-2026-01-15.md",
      "status": "SUCCESS"
    }
  ],
  "failed": [
    {
      "rule_name": "001-memory-bank",
      "score": null,
      "verdict": null,
      "review_path": null,
      "status": "FAILED",
      "error_message": "Schema validation error"
    }
  ],
  "skipped": [
    {
      "rule_name": "002-rule-governance",
      "review_path": "reviews/rule-reviews/002-rule-governance-claude-sonnet-45-2026-01-15.md",
      "status": "SKIPPED",
      "reason": "Review already exists"
    }
  ],
  "summary": {
    "success_count": 20,
    "failed_count": 1,
    "skipped_count": 2,
    "average_score": 87.5
  }
}
```

---

## Error Handling

**Rule file not found:**
- Log error, add to `failed` list
- Continue with next rule

**Schema validation fails:**
- Continue review (note in Parsability section)
- Mark as SUCCESS if review completes

**Review write fails:**
- Print review content to output
- Add to `failed` list with error
- Continue with next rule

**Context overflow:**
- Complete current rule
- Return partial results
- Coordinator will handle re-assignment

---

## Forbidden Actions

- DO NOT ask clarifying questions
- DO NOT calculate completion times
- DO NOT propose alternatives
- DO NOT batch multiple rules
- DO NOT create templates
- DO NOT skip rubric loading
- DO NOT abbreviate reviews

**Execute the full workflow for each rule. No exceptions.**
```

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{worker_num}` | This worker's number | `3` |
| `{total_workers}` | Total parallel workers | `5` |
| `{rule_count}` | Rules assigned to this worker | `23` |
| `{rules_list}` | Markdown list of rule paths | `- rules/100-snowflake-core.md` |
| `{review_date}` | ISO date | `2026-01-15` |
| `{review_mode}` | Review mode | `FULL` |
| `{model}` | Model slug | `claude-sonnet-45` |
| `{output_root}` | Output directory | `reviews/` |
| `{skip_existing}` | Skip existing reviews | `true` |

---

## Prompt Generation Function

```python
def generate_subagent_prompt(worker_num, total_workers, rules, params):
    """Generate complete prompt for a sub-agent.
    
    Args:
        worker_num: This worker's number (1-indexed)
        total_workers: Total number of parallel workers
        rules: List of rule file paths assigned to this worker
        params: Dict with review_date, review_mode, model, output_root, skip_existing
    
    Returns:
        Complete prompt string
    """
    rules_list = '\n'.join(f"- {r}" for r in rules)
    
    template = read_file("skills/bulk-rule-reviewer/workflows/subagent-prompt-template.md")
    
    # Extract the template section between ```markdown and ```
    # and substitute variables
    
    prompt = template.format(
        worker_num=worker_num,
        total_workers=total_workers,
        rule_count=len(rules),
        rules_list=rules_list,
        review_date=params['review_date'],
        review_mode=params['review_mode'],
        model=params['model'],
        output_root=params.get('output_root', 'reviews/'),
        skip_existing=params.get('skip_existing', 'true')
    )
    
    return prompt
```

---

## Validation

Before launching a sub-agent, verify the prompt:
- [ ] Contains Anti-Optimization Protocol section
- [ ] Lists specific rules (not "all rules")
- [ ] Includes evidence requirements
- [ ] Specifies output JSON format
- [ ] Has correct parameter values
