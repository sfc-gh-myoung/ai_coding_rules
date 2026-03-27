# Dimension Sub-Agent Template

Template for generating dimension-specific evaluation prompts for parallel rule review.

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{dimension_name}` | Dimension being evaluated | `actionability` |
| `{weight}` | Dimension weight (0.5-3.0) | `3.0` |
| `{max_points}` | Maximum points (weight × 10) | `30` |
| `{target_file}` | Path to rule file | `rules/200-python-core.md` |
| `{line_count}` | Rule file line count | `450` |
| `{file_type}` | File type (rule \| project) | `rule` |
| `{rule_content}` | Full rule file content | (markdown content) |
| `{rubric_content}` | Dimension rubric content | (rubric markdown) |
| `{overlap_rules}` | Dimension-specific overlap rules | (extracted rules) |

## Sub-Agent Prompt Template

```markdown
# Dimension Sub-Agent: {dimension_name}

## Mission
Evaluate the rule against the {dimension_name} rubric.
Weight: {weight}, Maximum Points: {max_points}

## Target File
**Path:** {target_file}
**Line Count:** {line_count}
**File Type:** {file_type}

## Rule Content
```markdown
{rule_content}
```

## Rubric ({weight} weight, {max_points} max points)
{rubric_content}

## Overlap Resolution Rules
{overlap_rules}

## Instructions
1. Read the rule content completely from line 1 to END
2. Apply ONLY the {dimension_name} rubric criteria
3. For overlapping issues, apply these rules to determine ownership:
   - If this dimension does NOT own an issue per the rules, record in `issues_deferred`
   - Do NOT score issues owned by other dimensions
4. Fill the Mandatory Issue Inventory template from the rubric
5. Calculate score using the Score Decision Matrix
6. Return structured JSON output

## Anti-Optimization Protocol

**CRITICAL: These rules are NON-NEGOTIABLE**

1. **NO SHORTCUTS**: Evaluate every pattern in the rubric. Do not skip patterns.

2. **NO SUMMARIZATION**: Report ALL evidence found, not "representative examples."

3. **NO EARLY TERMINATION**: Continue evaluation even after finding issues.

4. **NO SCORE ANCHORING**: Evidence drives score, not pre-determination.

5. **NO CROSS-DIMENSION DRIFT**: Stay within {dimension_name} only. If you find an issue owned by another dimension, record it in `issues_deferred`.

6. **COMPLETE OUTPUT**: Your JSON response MUST include ALL fields.

**Violation Detection:** Coordinator will flag:
- `evidence` array with <50% of rubric patterns checked
- `issues_deferred` empty when overlap rules indicate shared patterns
- Execution time <20s (indicates skipped evaluation)

## Output Format
Return ONLY this JSON structure:
```json
{
  "dimension": "{dimension_name}",
  "raw_score": <0-10>,
  "weight": {weight},
  "tier": "<tier name from rubric>",
  "start_epoch": "<time.time() at evaluation start>",
  "end_epoch": "<time.time() at evaluation end>",
  "evidence": [
    {"line": <N>, "pattern": "<pattern matched>", "quote": "<exact quote>"}
  ],
  "issues_found": [
    {"line": <N>, "description": "<issue>", "severity": "<blocking|warning>"}
  ],
  "issues_deferred": [
    {"line": <N>, "description": "<issue>", "owned_by": "<other dimension>"}
  ],
  "inventory_complete": <true|false>,
  "status": "completed"
}
```

## Timing Instrumentation

Record wall-clock time around your evaluation:
1. Before step 1 (reading rule content): Record `start_epoch` = current Unix timestamp
2. After step 5 (calculating score): Record `end_epoch` = current Unix timestamp
3. Include both in your JSON output

```

## Dimension Configuration

> **Scoring Rubric v2.0:** 6 scored dimensions (100 points). Token Efficiency and Staleness are informational only.

### Scored Dimensions

| Dimension | Weight | Max Points | Rubric File | Deterministic |
|-----------|--------|------------|-------------|---------------|
| Actionability | 3.0 | 30 | `actionability.md` | No |
| Rule Size | 2.5 | 25 | `rule-size.md` | **Yes** (inline) |
| Parsability | 1.5 | 15 | `parsability.md` | No |
| Completeness | 1.5 | 15 | `completeness.md` | No |
| Consistency | 1.0 | 10 | `consistency.md` | No |
| Cross-Agent Consistency | 0.5 | 5 | `cross-agent-consistency.md` | No |

### Informational Only (not scored)

| Dimension | Rubric File | Notes |
|-----------|-------------|-------|
| Token Efficiency | `token-efficiency.md` | Merged into Rule Size |
| Staleness | `staleness.md` | Findings reported only |

**Note:** Rule Size is computed inline by coordinator (100% deterministic via `wc -l`), not by sub-agent.

## Overlap Resolution Rules Extraction

Each sub-agent receives dimension-specific overlap rules. The coordinator extracts rules where the dimension is mentioned as owner or where it must defer to another dimension.

### Priority Rules (applied in order, first match wins)

1. **Parsability**: Schema/YAML validation errors → Parsability ALWAYS wins
2. **Actionability**: Ambiguous/undefined instructions → Actionability (blocks execution)
3. **Completeness**: Missing coverage/edge cases → Completeness (scope gap)
4. **Consistency**: Self-contradiction → Consistency (internal conflict)
5. **Cross-Agent Consistency**: Agent-specific logic/hardcoded names → Cross-Agent
6. **Token Efficiency** (informational): Duplicated/redundant content → Token Efficiency findings
7. **Staleness** (informational): Outdated patterns/tools/references → Staleness findings

### Issue Type to Owner Mapping

```
undefined_helper        → actionability
missing_verification    → actionability
ambiguous_instruction   → actionability
unimplementable_step    → actionability
missing_parameter       → completeness
missing_error_handling  → completeness
missing_edge_case       → completeness
incomplete_coverage     → completeness
schema_violation        → parsability
yaml_invalid            → parsability
metadata_missing        → parsability
internal_conflict       → consistency
terminology_mismatch    → consistency
redundant_section       → token_efficiency (informational)
repeated_instruction    → token_efficiency (informational)
deprecated_tool         → staleness (informational)
outdated_pattern        → staleness (informational)
hardcoded_agent         → cross_agent_consistency
```

## Usage by Coordinator

```python
def generate_dimension_prompt(dimension_name: str, weight: int, rubric_path: str,
                               rule_content: str, overlap_rules: str, params: dict) -> str:
    """Generate dimension-specific evaluation prompt."""
    
    # Read rubric content
    rubric_content = read_file(f"skills/rule-reviewer/{rubric_path}")
    
    # Read template
    template = read_file("skills/rule-reviewer/workflows/dimension-subagent-template.md")
    
    # Extract the prompt template section
    prompt_template = extract_template_section(template)
    
    # Substitute variables
    return prompt_template.format(
        dimension_name=dimension_name,
        weight=weight,
        max_points=weight * 5,
        target_file=params['target_file'],
        line_count=params.get('line_count', 'unknown'),
        file_type=params.get('file_type', 'rule'),
        rule_content=rule_content,
        rubric_content=rubric_content,
        overlap_rules=overlap_rules
    )
```
