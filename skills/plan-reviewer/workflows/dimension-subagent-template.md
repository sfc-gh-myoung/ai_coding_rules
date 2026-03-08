# Dimension Sub-Agent Prompt Template

## Overview

This template generates prompts for sub-agents that evaluate a single dimension of a plan. Each sub-agent receives complete context and returns a JSON worksheet.

## Template Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `{dimension_name}` | Dimension being evaluated (e.g., "executability") | Coordinator |
| `{weight}` | Point weight for this dimension (5-20) | Dimension config |
| `{plan_content}` | Complete plan text | Read once by coordinator |
| `{overlap_rules_for_this_dimension}` | Relevant entries from _overlap-resolution.md | Extracted by coordinator |
| `{rubric_content}` | Full rubric file for this dimension | Read from rubrics/{dimension}.md |

---

## Generated Prompt Structure

```markdown
# Dimension Sub-Agent: {dimension_name}

## Mission

Evaluate the plan against the **{dimension_name}** rubric.

**Scoring:**
- Raw Score: 0-10
- Weight: {weight}
- Points: Raw × ({weight}/2)
- Max Points: {weight}

**Output:** JSON worksheet (schema below)

---

## Anti-Optimization Protocol

**CRITICAL:** You MUST follow the complete evaluation process. Shortcuts are FORBIDDEN.

**Forbidden Thoughts:**
- "This will take too long"
- "I can save time by..."
- "The plan looks generally good"
- "Let me skip to scoring"
- "This dimension probably scores well"

**Required Mindset:**
- "I will read every line of the plan"
- "I will apply every pattern from the rubric"
- "I will cite specific line numbers as evidence"
- "Quality and accuracy matter more than speed"

**If you find yourself skipping sections:**
1. STOP
2. Re-read this protocol
3. Return to systematic evaluation
4. Complete the full worksheet

---

## Plan Content

<plan>
{plan_content}
</plan>

**Plan Metadata:**
- Total lines: {plan_line_count}
- Read from line 1 to line {plan_line_count} (no skipping)

---

## Overlap Resolution Rules

The following issues belong to OTHER dimensions. Do NOT count them in {dimension_name}:

<overlap_rules>
{overlap_rules_for_this_dimension}
</overlap_rules>

**Protocol:**
1. If you find an issue that matches an overlap rule → Add to `issues_deferred`
2. Note which dimension owns it
3. Do NOT include in your `issues_found` or scoring

---

## Rubric: {dimension_name}

<rubric>
{rubric_content}
</rubric>

**Required Actions:**
1. Read the entire rubric before reading the plan
2. Note all pattern inventories
3. Create empty worksheet
4. Read plan line-by-line
5. Match against patterns
6. Fill worksheet
7. Calculate score using Score Decision Matrix
8. Return JSON

---

## Output Format

Return ONLY a valid JSON object. No markdown, no explanation, just JSON.

**Schema:**
```json
{
  "dimension": "{dimension_name}",
  "raw_score": <integer 0-10>,
  "weight": {weight},
  "points": <float, calculated as raw_score * (weight/2)>,
  "max_points": {weight},
  "evidence": [
    {
      "line": <integer>,
      "pattern": "<matched pattern from rubric>",
      "quote": "<exact text from plan, first 80 chars>",
      "category": "<rubric category>"
    }
  ],
  "issues_found": [
    {
      "line": <integer>,
      "description": "<issue description>",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "fix_suggestion": "<recommended fix>"
    }
  ],
  "issues_deferred": [
    {
      "line": <integer>,
      "description": "<issue description>",
      "owned_by": "<dimension that owns this issue>",
      "overlap_rule": "<rule number from _overlap-resolution.md>"
    }
  ],
  "worksheet_summary": {
    "total_patterns_checked": <integer>,
    "patterns_matched": <integer>,
    "patterns_not_matched": <integer>,
    "false_positives_filtered": <integer>
  },
  "score_calculation": {
    "tier": "<tier name from Score Decision Matrix>",
    "primary_metric": "<main metric used>",
    "tie_breaker_applied": <boolean>,
    "notes": "<calculation notes>"
  }
}
```

**Validation Requirements:**
- `raw_score` must be 0-10 integer
- `evidence` must have at least 3 entries for scores 7+
- `evidence` must have line numbers that exist in plan
- `issues_found` + `issues_deferred` should be complete
- `points` must equal `raw_score * (weight/2)`

---

## Execution Checklist

Before returning JSON, verify:

- [ ] Read rubric completely before plan
- [ ] Read plan from line 1 to END (no skipping)
- [ ] Applied all patterns from rubric inventory
- [ ] Checked Non-Issues list to filter false positives
- [ ] Applied Overlap Resolution for ambiguous issues
- [ ] Used Score Decision Matrix (no subjective scoring)
- [ ] Filled all required JSON fields
- [ ] Evidence has specific line numbers
- [ ] Points calculation is correct

**If ANY checkbox is unchecked:** Complete that step before returning.

---

## Example Output (for reference only - do NOT copy)

```json
{
  "dimension": "executability",
  "raw_score": 7,
  "weight": 20,
  "points": 14,
  "max_points": 20,
  "evidence": [
    {"line": 45, "pattern": "if necessary", "quote": "Update dependencies if necessary before...", "category": "Conditional Qualifier"},
    {"line": 89, "pattern": "ensure", "quote": "Ensure database is running", "category": "Implicit Command"},
    {"line": 156, "pattern": "if/no else", "quote": "If tests pass: deploy to staging", "category": "Missing Branch"}
  ],
  "issues_found": [
    {"line": 45, "description": "Vague conditional 'if necessary'", "severity": "MEDIUM", "fix_suggestion": "Replace with specific condition: 'if package.json modified'"},
    {"line": 89, "description": "Implicit command without verification method", "severity": "MEDIUM", "fix_suggestion": "Add verification: 'pg_isready returns 0'"}
  ],
  "issues_deferred": [
    {"line": 200, "description": "Missing error recovery", "owned_by": "completeness", "overlap_rule": "Rule 2"}
  ],
  "worksheet_summary": {
    "total_patterns_checked": 95,
    "patterns_matched": 6,
    "patterns_not_matched": 89,
    "false_positives_filtered": 2
  },
  "score_calculation": {
    "tier": "Good",
    "primary_metric": "5-6 blocking issues",
    "tie_breaker_applied": false,
    "notes": "6 blocking issues places in Good tier (7/10)"
  }
}
```

---

## Final Instruction

Return ONLY the JSON worksheet. Do not include any text before or after the JSON.
```

---

## Coordinator Integration

The coordinator uses this template as follows:

```python
def generate_dimension_prompt(
    dimension_name: str,
    weight: int,
    rubric_path: str,
    plan_content: str,
    overlap_rules: str,
    params: dict
) -> str:
    """Generate sub-agent prompt from template."""
    
    # Read rubric content
    rubric_content = read_file(rubric_path)
    
    # Count plan lines
    plan_line_count = len(plan_content.split('\n'))
    
    # Load template
    template = read_file('workflows/dimension-subagent-template.md')
    
    # Extract template section (between first ``` and last ```)
    prompt_section = extract_prompt_section(template)
    
    # Replace variables
    prompt = prompt_section.replace('{dimension_name}', dimension_name)
    prompt = prompt.replace('{weight}', str(weight))
    prompt = prompt.replace('{plan_content}', plan_content)
    prompt = prompt.replace('{plan_line_count}', str(plan_line_count))
    prompt = prompt.replace('{overlap_rules_for_this_dimension}', overlap_rules)
    prompt = prompt.replace('{rubric_content}', rubric_content)
    
    return prompt
```

## Dimension Configuration

| Dimension | Weight | Rubric Path | Max Points |
|-----------|--------|-------------|------------|
| executability | 20 | rubrics/executability.md | 20 |
| completeness | 20 | rubrics/completeness.md | 20 |
| success_criteria | 20 | rubrics/success-criteria.md | 20 |
| scope | 15 | rubrics/scope.md | 15 |
| dependencies | 10 | rubrics/dependencies.md | 10 |
| decomposition | 5 | rubrics/decomposition.md | 5 |
| context | 5 | rubrics/context.md | 5 |
| risk_awareness | 5 | rubrics/risk-awareness.md | 5 |

## Overlap Rules Extraction

For each dimension, extract relevant rules from `_overlap-resolution.md`:

```python
def extract_overlap_rules_for(dimension_name: str, overlap_rules: str) -> str:
    """Extract overlap rules relevant to this dimension."""
    
    relevant_rules = []
    
    # Parse overlap rules
    for rule in parse_overlap_rules(overlap_rules):
        if rule['primary'] == dimension_name:
            relevant_rules.append(f"✓ You OWN: {rule['issue_type']}")
        elif dimension_name in rule['not_counted_in']:
            relevant_rules.append(f"✗ DEFER to {rule['primary']}: {rule['issue_type']}")
    
    return '\n'.join(relevant_rules)
```
