# Dimension Sub-Agent Prompt Template

## Overview

This template generates prompts for sub-agents that evaluate a single dimension of documentation. Each sub-agent receives complete context and returns a JSON worksheet.

## Template Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `{dimension_name}` | Dimension being evaluated (e.g., "accuracy") | Coordinator |
| `{weight}` | Point weight for this dimension (1-5) | Dimension config |
| `{doc_content}` | Complete documentation text | Read once by coordinator |
| `{doc_line_count}` | Total lines in target documentation | Calculated |
| `{overlap_rules_for_this_dimension}` | Relevant entries from _overlap-resolution.md | Extracted by coordinator |
| `{rubric_content}` | Full rubric file for this dimension | Read from rubrics/{dimension}.md |

---

## Generated Prompt Structure

```markdown
# Dimension Sub-Agent: {dimension_name}

## Mission

Evaluate the documentation against the **{dimension_name}** rubric.

**Scoring:**
- Raw Score: 0-10
- Weight: {weight}
- Points: Raw × ({weight}/2)
- Max Points: {weight} × 2.5 (for weight 5) or {weight} × (10/weight) scaled

**Output:** JSON worksheet (schema below)

---

## Anti-Optimization Protocol

**CRITICAL:** You MUST follow the complete evaluation process. Shortcuts are FORBIDDEN.

**Forbidden Thoughts:**
- "This will take too long"
- "I can save time by..."
- "The documentation looks generally good"
- "Let me skip to scoring"
- "This dimension probably scores well"

**Required Mindset:**
- "I will read every line of the documentation"
- "I will apply every pattern from the rubric"
- "I will cite specific line numbers as evidence"
- "Quality and accuracy matter more than speed"

**If you find yourself skipping sections:**
1. STOP
2. Re-read this protocol
3. Return to systematic evaluation
4. Complete the full worksheet

---

## Documentation Content

<documentation>
{doc_content}
</documentation>

**Documentation Metadata:**
- Total lines: {doc_line_count}
- Read from line 1 to line {doc_line_count} (no skipping)

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
1. Read the entire rubric before reading the documentation
2. Note all pattern inventories and verification criteria
3. Create empty worksheet
4. Read documentation line-by-line
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
  "max_points": <float, calculated as 10 * (weight/2)>,
  "evidence": [
    {
      "line": <integer>,
      "pattern": "<matched pattern from rubric>",
      "quote": "<exact text from doc, first 80 chars>",
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
  "verification_table": "<completed verification table as markdown>",
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
- `evidence` must have line numbers that exist in documentation
- `issues_found` + `issues_deferred` should be complete
- `points` must equal `raw_score * (weight/2)`
- `verification_table` must be included (markdown format)

---

## Dimension-Specific Fields

### For Accuracy dimension:
- Include `cross_references_verified` count in worksheet_summary
- Track file paths, commands, function names verified

### For Staleness dimension:
- Include `links_validated` count in worksheet_summary
- Track external URLs tested

### For Completeness dimension:
- Include `coverage_gaps` list in issues_found
- Track features documented vs undocumented

---

## Execution Checklist

Before returning JSON, verify:

- [ ] Read rubric completely before documentation
- [ ] Read documentation from line 1 to END (no skipping)
- [ ] Applied all patterns from rubric inventory
- [ ] Checked Non-Issues list to filter false positives
- [ ] Applied Overlap Resolution for ambiguous issues
- [ ] Used Score Decision Matrix (no subjective scoring)
- [ ] Filled all required JSON fields
- [ ] Evidence has specific line numbers
- [ ] Points calculation is correct
- [ ] Verification table included

**If ANY checkbox is unchecked:** Complete that step before returning.

---

## Example Output (for reference only - do NOT copy)

```json
{
  "dimension": "accuracy",
  "raw_score": 7,
  "weight": 5,
  "points": 17.5,
  "max_points": 25,
  "evidence": [
    {"line": 23, "pattern": "file path exists", "quote": "See `src/utils/helpers.py` for details...", "category": "Reference Validation"},
    {"line": 45, "pattern": "command verified", "quote": "Run `npm install` to install dependencies", "category": "Command Verification"},
    {"line": 89, "pattern": "function exists", "quote": "Use the `calculateTotal()` function to...", "category": "API Reference"}
  ],
  "issues_found": [
    {"line": 67, "description": "File path `src/old/legacy.py` does not exist", "severity": "HIGH", "fix_suggestion": "Update to current path: `src/core/modern.py`"},
    {"line": 112, "description": "Command `npm run build:legacy` fails", "severity": "MEDIUM", "fix_suggestion": "Update to `npm run build`"}
  ],
  "issues_deferred": [
    {"line": 156, "description": "External link returns 404", "owned_by": "staleness", "overlap_rule": "Rule 5"}
  ],
  "verification_table": "| Reference | Type | Status | Line |\n|-----------|------|--------|------|\n| src/utils/helpers.py | File | VALID | 23 |\n| npm install | Command | VALID | 45 |\n| src/old/legacy.py | File | INVALID | 67 |",
  "worksheet_summary": {
    "total_patterns_checked": 45,
    "patterns_matched": 42,
    "patterns_not_matched": 3,
    "false_positives_filtered": 1,
    "cross_references_verified": 45
  },
  "score_calculation": {
    "tier": "Good",
    "primary_metric": "93% references valid (42/45)",
    "tie_breaker_applied": false,
    "notes": "93% validity places in Good tier (7/10)"
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
    doc_content: str,
    overlap_rules: str,
    params: dict
) -> str:
    """Generate sub-agent prompt from template."""
    
    # Read rubric content
    rubric_content = read_file(rubric_path)
    
    # Count documentation lines
    doc_line_count = len(doc_content.split('\n'))
    
    # Load template
    template = read_file('workflows/dimension-subagent-template.md')
    
    # Extract template section (between first ``` and last ```)
    prompt_section = extract_prompt_section(template)
    
    # Replace variables
    prompt = prompt_section.replace('{dimension_name}', dimension_name)
    prompt = prompt.replace('{weight}', str(weight))
    prompt = prompt.replace('{doc_content}', doc_content)
    prompt = prompt.replace('{doc_line_count}', str(doc_line_count))
    prompt = prompt.replace('{overlap_rules_for_this_dimension}', overlap_rules)
    prompt = prompt.replace('{rubric_content}', rubric_content)
    
    return prompt
```

## Dimension Configuration

| Dimension | Weight | Rubric Path | Max Points |
|-----------|--------|-------------|------------|
| accuracy | 5 | rubrics/accuracy.md | 25 |
| completeness | 5 | rubrics/completeness.md | 25 |
| clarity | 4 | rubrics/clarity.md | 20 |
| structure | 3 | rubrics/structure.md | 15 |
| staleness | 2 | rubrics/staleness.md | 10 |
| consistency | 1 | rubrics/consistency.md | 5 |

**Scoring Formula:**
```
Points = Raw Score (0-10) × (Weight / 2)

Example: Accuracy raw=8, weight=5 → 8 × 2.5 = 20 points (max 25)
Example: Consistency raw=8, weight=1 → 8 × 0.5 = 4 points (max 5)
```

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

## Dimension-Specific Extraction Rules

### Accuracy (weight 5)
- **Owns:** Wrong file paths, incorrect function names, broken code examples, outdated code examples
- **Defers to Staleness:** Broken external links, deprecated tools
- **Defers to Completeness:** Missing documentation sections

### Completeness (weight 5)
- **Owns:** Missing feature docs, no troubleshooting, missing setup steps
- **Defers to Accuracy:** Wrong references
- **Defers to Structure:** Information organization

### Clarity (weight 4)
- **Owns:** Unexplained jargon, long complex sentences, no examples
- **Defers to Completeness:** Missing glossary
- **Defers to Consistency:** Terminology variation

### Structure (weight 3)
- **Owns:** Wrong heading level, wrong section order, broken heading hierarchy, missing TOC
- **Defers to Consistency:** Mixed list markers
- **Defers to Completeness:** Missing sections

### Staleness (weight 2)
- **Owns:** Broken external links, deprecated commands, old tool versions
- **Defers to Accuracy:** Incorrect code examples (even if old)
- **Defers to Completeness:** Missing version requirements

### Consistency (weight 1)
- **Owns:** Mixed list markers, terminology variation, code style differences
- **Defers to Structure:** Heading hierarchy issues
- **Defers to Clarity:** Readability issues
