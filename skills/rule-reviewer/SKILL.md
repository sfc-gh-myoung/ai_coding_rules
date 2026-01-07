---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using 6-dimension rubric and write results to reviews/ with no-overwrite safety. Use when reviewing rule files, auditing rule quality, checking rule staleness, validating rule compliance, or analyzing agent executability.
version: 2.0.0
---

# Rule Reviewer

Execute comprehensive agent-centric reviews evaluating whether autonomous agents can execute rules without judgment calls.

## Quick Start

```
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

Output: `reviews/200-python-core-claude-sonnet-45-2026-01-06.md`

## Scoring System (100 points)

| Dimension | Weight | Max | Key Question |
|-----------|--------|-----|--------------|
| Actionability | 25% | 25 | Can agents execute without judgment? |
| Completeness | 25% | 25 | All scenarios covered? |
| Consistency | 15% | 15 | Internal alignment correct? |
| Parsability | 15% | 15 | Schema valid? |
| Token Efficiency | 10% | 10 | Within ±15% budget? |
| Staleness | 10% | 10 | Current patterns? |

**Detailed rubrics:** `rubrics/[dimension].md`

## Review Modes

- **FULL:** All 6 dimensions (3-5 min per rule)
- **FOCUSED:** Actionability + Completeness only (50 points max, 2-3 min)
- **STALENESS:** Staleness dimension only (10 points max, 1 min)

## Workflow

1. **Validate inputs**
   - Date format: YYYY-MM-DD
   - File exists under rules/
   - Mode: FULL | FOCUSED | STALENESS

2. **Run schema validation**
   ```bash
   uv run python scripts/schema_validator.py [target_file]
   ```
   Parse output for CRITICAL/HIGH/MEDIUM errors

3. **Agent Execution Test**
   Count blocking issues (cap score at 60 if ≥10):
   - Undefined thresholds ("large", "significant", "appropriate")
   - Missing conditional branches (no explicit else)
   - Ambiguous actions (multiple interpretations)
   - Visual formatting (ASCII art, arrows, diagrams)

4. **Score dimensions**
   Read rubrics/ as needed for each dimension:
   - `rubrics/actionability.md`
   - `rubrics/completeness.md`
   - `rubrics/consistency.md`
   - `rubrics/parsability.md`
   - `rubrics/token-efficiency.md`
   - `rubrics/staleness.md`

5. **Generate recommendations**
   - Specific line numbers
   - Quantified fixes
   - Expected score improvements

6. **Write review**
   Path: `reviews/[rule-name]-[model]-[date].md`
   Auto-increment: `-01.md`, `-02.md` if exists

**See workflows/** for detailed error handling

## Verdicts

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | EXECUTABLE | Production-ready |
| 80-89 | EXECUTABLE_WITH_REFINEMENTS | Good, minor fixes |
| 60-79 | NEEDS_REFINEMENT | Needs work |
| <60 | NOT_EXECUTABLE | Major issues |

**Critical dimension override:** If both Actionability ≤2/5 AND Completeness ≤2/5 → NOT_EXECUTABLE regardless of total score

## Required Sections in Review

1. Executive Summary (scores table)
2. Schema Validation Results
3. Agent Executability Verdict
4. Dimension Analysis (6 sections for FULL mode)
5. Critical Issues (list)
6. Recommendations (prioritized)
7. Post-Review Checklist
8. Conclusion

## Inputs

- **target_file:** Path to rule (e.g., `rules/200-python-core.md`)
- **review_date:** ISO 8601 format (YYYY-MM-DD)
- **review_mode:** FULL | FOCUSED | STALENESS
- **model:** Lowercase-hyphenated slug (e.g., `claude-sonnet-45`)
- **timing_enabled:** (optional) true | false (default: false)

## Integration with Other Skills

### With bulk-rule-reviewer

bulk-rule-reviewer invokes this skill once per rule file. **Never** implement review logic yourself when bulk-rule-reviewer calls you.

### With skill-timing

If `timing_enabled: true`:
1. **Before review:** skill-timing creates timing session
2. **During review:** Checkpoints recorded
3. **After review:** Timing metadata appended to review file

See `../skill-timing/workflows/` for integration details

## Error Handling

**Schema validator fails:**
- Continue review
- Note validation unavailable in Parsability section
- Recommend manual schema check

**Rule file not found:**
- Report: "File not found: [path]"
- Verify path and try again

**Review write fails:**
- Print: `OUTPUT_FILE: [path]`
- Print full review content
- User must save manually

**See:** `workflows/error-handling.md`

## No-Overwrite Safety

If `reviews/[rule-name]-[model]-[date].md` exists:
- Try `-01.md`
- Try `-02.md`
- Increment until available

Never overwrite existing reviews.

## Progressive Disclosure

Don't load all rubrics at once. Read as needed:
- Scoring Actionability → Read `rubrics/actionability.md`
- Scoring Completeness → Read `rubrics/completeness.md`
- Etc.

Only load what you need for current dimension.

## Validation Requirements

**Pre-execution:**
- [ ] target_file exists under rules/
- [ ] review_date matches YYYY-MM-DD format
- [ ] review_mode is valid enum
- [ ] model slug is lowercase-hyphenated

**During execution:**
- [ ] Schema validation attempted
- [ ] Agent Execution Test completed
- [ ] All dimensions scored (FULL mode)
- [ ] Recommendations include line numbers

**Post-execution:**
- [ ] Review file written
- [ ] Path confirmed
- [ ] No overwrites occurred

## Critical Execution Protocol

**DO:**
- ✅ Read complete rule file
- ✅ Run schema validator
- ✅ Score all dimensions per rubrics
- ✅ Generate specific recommendations
- ✅ Write complete review

**DON'T:**
- ❌ Skip dimensions (FULL mode requires all 6)
- ❌ Estimate scores without rubrics
- ❌ Generate generic recommendations
- ❌ Abbreviate review to save tokens
- ❌ Skip schema validation

## Expected Review Size

Typical FULL mode review: 3000-8000 bytes

**Red flags:**
- < 2000 bytes (too abbreviated)
- > 12000 bytes (excessive detail)

## Examples

See `examples/` for complete review samples:
- `full-review.md` - FULL mode walkthrough
- `focused-review.md` - FOCUSED mode example  
- `staleness-review.md` - STALENESS mode example
- `edge-cases.md` - Error scenarios

## Related Skills

- **bulk-rule-reviewer:** Batch review orchestrator (uses this skill)
- **rule-creator:** Rule authoring (validated with this skill)
- **skill-timing:** Execution time measurement (optional integration)

## Quality Checklist

Before considering review complete:

- [ ] Schema validator executed
- [ ] Agent Execution Test performed
- [ ] All required dimensions scored
- [ ] Each score has rationale
- [ ] Critical issues identified
- [ ] Recommendations prioritized
- [ ] Line numbers provided for fixes
- [ ] Review written to reviews/
- [ ] File path confirmed

## Version History

- **v2.0.0:** Removed PROMPT.md, added progressive disclosure with rubrics/
- **v1.4.0:** Added timing integration, schema validation
- **v1.3.0:** Added FOCUSED and STALENESS modes
- **v1.2.0:** Added Agent Execution Test
- **v1.1.0:** Added no-overwrite safety
- **v1.0.0:** Initial release
