# Example: Project File Review

## Reviewing AGENTS.md or PROJECT.md

```text
Use the rule-reviewer skill.

target_file: PROJECT.md
review_date: 2026-01-15
review_mode: FULL
model: claude-sonnet-45
```

Expected output file:

`reviews/rule-reviews/PROJECT-claude-sonnet-45-2026-01-15.md`

---

## Key Differences from Rule File Reviews

### 1. File Type Detection (Automatic)

```bash
# Agent detects project file automatically
target_basename=$(basename "PROJECT.md")

if [[ "$target_basename" =~ ^(AGENTS|PROJECT)\.md$ ]]; then
    FILE_TYPE="project"
    SKIP_SCHEMA=true
fi
```

### 2. Schema Validation (Skipped)

**Rule Files:**
```bash
uv run ai-rules validate rules/200-python-core.md
# Validates: metadata, section order, required fields
```

**Project Files:**
```bash
echo "Schema validation skipped for project file"
# Rationale: Different structure than rule schema
```

### 3. Scoring Adjustments

> **Scoring Rubric v2.0:** 6 scored dimensions, Token Efficiency and Staleness are informational only.

**All 6 dimensions still scored, max 100 points:**

| Dimension | Rule Files | Project Files |
|-----------|------------|---------------|
| Actionability | Schema-agnostic | Same |
| Rule Size | Line count | Same |
| Parsability | Schema + Markdown | **Markdown only** |
| Completeness | Schema-agnostic | Same |
| Consistency | Schema-agnostic | Same |
| Cross-Agent | Schema-agnostic | Same |

**Informational (not scored):**
- Token Efficiency: Redundancy noted in recommendations
- Staleness: Deprecated tools/patterns flagged in recommendations

### 4. Parsability Scoring (Markdown Only)

**What's evaluated:**
- ✓ Heading hierarchy
- ✓ List formatting
- ✓ Code block fencing
- ✓ Table structure
- ✓ No visual formatting (ASCII art, arrows)
- ✓ External links valid

**What's skipped:**
- ✗ Schema validation
- ✗ Metadata fields (SchemaVersion, RuleVersion, etc.)
- ✗ Section order (Scope, Contract, References)

**Example score:**
```markdown
## Parsability: 10/10 (15 points)

**File Type:** Project configuration (schema validation skipped)

**Schema Validation:** SKIPPED (project file)

**Markdown Structure:** Perfect
- Proper heading hierarchy (no skips)
- Consistent list markers (-)
- All code blocks fenced with language tags
- No visual formatting issues
- No broken external links
```

### 5. Token Efficiency (Informational Only)

> **Scoring Rubric v2.0:** Token Efficiency is no longer scored. Findings appear in recommendations.

**What's tracked (informational):**
- Redundancy instances
- Structured format ratio
- Use of references

**Example output:**
```markdown
## Token Efficiency (Informational)

**Redundancy instances:** 2
- Line 39: Tool installation command
- Line 114: Same command repeated

**Structure ratio:** 87.8% structured

**Actual token count:** ~4800 tokens (reference only)

**Recommendation:** Consolidate repeated commands into a single reference section.
```

---

## Example Review Output

```markdown
# Rule Review: PROJECT.md

**Rule:** PROJECT.md  
**File Type:** Project Configuration  
**Reviewer:** claude-sonnet-45  
**Review Date:** 2026-01-15  
**Review Mode:** FULL  
**Max Score:** 100 points

---

## Executive Summary

| Dimension | Raw Score | Weight | Points | Max Points |
|-----------|-----------|--------|--------|------------|
| **Actionability** | 8/10 | ×3.0 | 24.0 | 30 |
| **Rule Size** | 9/10 | ×2.5 | 22.5 | 25 |
| **Parsability** | 10/10 | ×1.5 | 15.0 | 15 |
| **Completeness** | 7/10 | ×1.5 | 10.5 | 15 |
| **Consistency** | 6/10 | ×1.0 | 6.0 | 10 |
| **Cross-Agent** | 9/10 | ×0.5 | 4.5 | 5 |
| **TOTAL** | - | - | **82.5** | **100** |

**Overall Verdict:** EXECUTABLE_WITH_REFINEMENTS (75-89)

**Note:** PROJECT.md is a project configuration file. Schema validation skipped. Token Efficiency and Staleness tracked as informational only (not scored).

---

## Schema Validation Results

**Status:** SKIPPED (project file)

**Rationale:** PROJECT.md is a bootstrap/configuration document with different structure than domain rules defined in `schemas/rule-schema.yml`.

**What was evaluated:**
- ✓ Markdown structure and formatting
- ✓ Actionability for AI agents
- ✓ Completeness of guidance
- ✓ Internal consistency
- ✓ Currency of tools and patterns

**What was NOT evaluated:**
- Schema metadata (SchemaVersion, RuleVersion, TokenBudget, ContextTier, Depends)
- Rule-specific sections (Scope, Contract, References)
- Section ordering requirements

---

## Agent Executability Verdict

**Verdict:** EXECUTABLE_WITH_REFINEMENTS

**Rationale:** PROJECT.md provides comprehensive, actionable guidance for AI agents with clear commands, validation requirements, and workflows. Minor improvements needed in actionability and consistency.

**Key Strengths:**
- Highly actionable with concrete commands
- Complete workflow documentation
- Current tooling (uv, ruff, ty, Python 3.11+)
- Excellent markdown structure
- Strong validation requirements

**Key Improvements:**
- Clarify ambiguous threshold terms
- Resolve terminology inconsistencies
- Add comprehensive error handling scenarios

---

## Dimension Analysis

### 1. Actionability: 8/10 (20.0 points)

**Blocking Issues:** 3

[... dimension analysis continues ...]
```

---

## Key Takeaways

1. **Project files are fully reviewable** - All 6 scored dimensions apply
2. **Schema validation skipped** - Different structure than rules
3. **Same max score (100 points)** - Equal quality bar
4. **Parsability = markdown only** - No schema checks
5. **Token Efficiency & Staleness = informational** - Not scored, findings in recommendations
6. **Still highly valuable** - Measures agent executability for critical bootstrap files

---

## Comparison: Rule vs Project File Reviews

### What's the Same
- Actionability scoring (blocking issues, quantification)
- Completeness scoring (error scenarios, edge cases)
- Consistency scoring (contradictions, terminology)
- Cross-agent consistency scoring
- Rule Size scoring (line count)
- Max score: 100 points
- Verdict thresholds: 90-100 EXECUTABLE, 75-89 REFINEMENTS, 50-74 NEEDS_REFINEMENT, <50 NOT_EXECUTABLE
- Review file size: 3000-8000 bytes

### What's Different
- **Parsability:** Rule (schema + markdown) vs Project (markdown only)
- **Token Efficiency:** Both informational, but rules check TokenBudget variance
- **Schema Validation:** Rule (required) vs Project (skipped)
- **File Structure:** Rule (standardized) vs Project (custom)

### Why Both Matter
- **Rule files:** Domain-specific patterns for consistent code generation
- **Project files:** Bootstrap guidance for project-specific tooling and workflows
- **Both:** Agent-executable documents requiring high quality standards
