# Rule Creator Skill

## Skill Purpose

Reproducibly create production-ready Cursor rules following v3.0 schema by orchestrating `template_generator.py`, content refinement based on industry research, and `schema_validator.py` validation loops.

This skill automates the complete rule creation workflow from discovery through validation, ensuring all generated rules pass schema validation with 0 CRITICAL errors and are ready for immediate use.

## Prerequisites

**Required Access:**
- `@rules/` directory (read/write)
- `@scripts/template_generator.py` (execute)
- `@scripts/schema_validator.py` (execute)
- `@RULES_INDEX.md` (read/write)
- Python 3.11+ environment with PyYAML

**Required Rule Files:**
- `@rules/000-global-core.md` (foundation)
- `@rules/002-rule-governance.md` (v3.0 schema standards)
- `@rules/002a-rule-creation-guide.md` (creation workflow)
- `@rules/002b-rule-optimization.md` (token budgets)
- `@rules/002d-schema-validator-usage.md` (validation commands)

**Tools Required:**
- `run_terminal_cmd` (for script execution)
- `read_file` (for rule inspection)
- `search_replace` (for content updates)
- `web_search` (for best practices research)
- `grep` (for RULES_INDEX.md searches)

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  RULE CREATION WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│ Phase 1: Discovery & Research                                │
│   ↓ Search RULES_INDEX.md for existing rules               │
│   ↓ Identify domain range and next number                  │
│   ↓ Web search for best practices                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 2: Template Generation                                 │
│   ↓ Execute: template_generator.py NNN-tech-aspect.md      │
│   ↓ Verify all 9 sections created                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 3: Content Population                                  │
│   ↓ Fill metadata (Keywords, TokenBudget, etc.)            │
│   ↓ Write all required sections                             │
│   ↓ Add Anti-Patterns with code examples                    │
├─────────────────────────────────────────────────────────────┤
│ Phase 4: Validation Loop                                     │
│   ↓ Execute: schema_validator.py rules/NNN-tech.md         │
│   ↓ If CRITICAL errors → Fix → Re-validate                  │
│   ↓ Continue until exit code 0                              │
├─────────────────────────────────────────────────────────────┤
│ Phase 5: Indexing                                            │
│   ↓ Add rule to RULES_INDEX.md                             │
│   ✓ Production-ready rule complete                          │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Discovery & Research

### Step 1.1: Parse User Request

Extract technology name and determine appropriate aspect:
- Technology: e.g., "DaisyUI", "pytest-mock", "Snowflake Hybrid Tables"
- Aspect: Usually "core" for foundational rules, or specific like "security", "testing", "performance"

### Step 1.2: Search RULES_INDEX.md

```bash
# Search for existing related rules
grep -i "[technology]" RULES_INDEX.md

# Examples:
grep -i "daisyui" RULES_INDEX.md  # Search for DaisyUI
grep -i "javascript" RULES_INDEX.md  # Broader search
grep -i "tailwind" RULES_INDEX.md  # Related technology
```

**Analyze results:**
- Extract rule numbers from matches
- Identify domain pattern (e.g., 420, 421 → domain is 420-449)
- Determine next available number in sequence

### Step 1.3: Identify Domain Range

| Domain Range | Technology | Example Rules |
|--------------|------------|---------------|
| 000-099 | Core/Foundational | 000-global-core, 002-rule-governance |
| 100-199 | Snowflake | 100-snowflake-core, 115-cortex-agents |
| 200-299 | Python | 200-python-core, 206-python-pytest |
| 300-399 | Shell/Bash | 300-bash-scripting-core, 310-zsh-core |
| 400-499 | Docker/Containers | 350-docker-best-practices |
| 420-449 | JavaScript/Frontend | 420-javascript-core, 421-alpinejs-core |
| 500-599 | Data Science | 920-data-science-analytics |
| 600-699 | Golang/Go | 600-golang-core |
| 800-899 | Project Management | 800-project-changelog, 820-taskfile |
| 900-999 | Demos/Examples | 900-demo-creation |

### Step 1.4: Load Domain Core Rule

Based on identified domain, load the core rule for context:

```bash
# Frontend/JavaScript
@rules/420-javascript-core.md

# Python
@rules/200-python-core.md

# Snowflake
@rules/100-snowflake-core.md

# Shell/Bash
@rules/300-bash-scripting-core.md

# Docker
@rules/350-docker-best-practices.md
```

### Step 1.5: Web Research for Best Practices

Search for current industry standards (2024-2025):

```
Search queries:
1. "2024 2025 [TECHNOLOGY] best practices"
2. "[TECHNOLOGY] industry standards community guidelines"
3. "[TECHNOLOGY] performance optimization patterns"
4. "[TECHNOLOGY] common mistakes anti-patterns"
```

**Extract from research:**
- 10-15 semantic keywords for metadata
- 3+ essential patterns for Quick Start
- 2+ anti-patterns with correct alternatives
- Official documentation links
- Community-adopted standards

## Phase 2: Template Generation

### Step 2.1: Determine Context Tier

Based on rule importance:
- **Critical:** Core framework rules, always-loaded (e.g., 000-global-core)
- **High:** Domain foundations, frequently used (e.g., 100-snowflake-core, 200-python-core)
- **Medium:** Specific features, moderate usage (most new rules)
- **Low:** Specialized, rarely loaded

### Step 2.2: Execute template_generator.py

```bash
python scripts/template_generator.py [NUMBER]-[technology]-[aspect] \
  --context-tier [Critical|High|Medium|Low] \
  --output-dir rules/

# Example: DaisyUI rule
python scripts/template_generator.py 422-daisyui-core \
  --context-tier Medium \
  --output-dir rules/

# Example: Snowflake feature
python scripts/template_generator.py 125-snowflake-hybrid-tables \
  --context-tier High \
  --output-dir rules/
```

### Step 2.3: Verify Template Creation

Check that `rules/NNN-technology-aspect.md` was created with:
- ✓ All 9 required sections present
- ✓ Contract section with 6 XML tags
- ✓ Metadata structure (Keywords, TokenBudget, ContextTier, Depends)
- ✓ Placeholder content ready for population

## Phase 3: Content Population

### Step 3.1: Fill Metadata (Lines 1-12)

```markdown
## Metadata

**SchemaVersion:** v3.0
**Keywords:** [10-15 comma-separated terms from research]
**TokenBudget:** ~[estimate: file_lines × 2, round to nearest 50]
**ContextTier:** [Critical|High|Medium|Low]
**Depends:** rules/000-global-core.md, rules/[domain-core].md
```

**Keyword Selection Strategy:**
- Include primary technology name
- Add related technologies (e.g., Tailwind for DaisyUI)
- Include use cases (components, UI, themes)
- Add pattern types (best practices, optimization, security)
- Total: 10-15 terms, comma-separated

**TokenBudget Estimation:**
- Quick formula: `lines × 2` rounded to nearest 50
- Standard rule: ~500-1500 tokens (150-300 lines)
- Comprehensive rule: ~1500-3000 tokens (300-500 lines)
- Format: `~1200` (tilde prefix required)

### Step 3.2: Write Purpose (1-2 Sentences)

Template:
```markdown
## Purpose

[What problem does this rule solve? Why is it important for [TECHNOLOGY] users?]
```

Example:
```markdown
## Purpose

Establishes best practices for DaisyUI component library usage, covering theme customization, accessibility patterns, and semantic HTML integration with Tailwind CSS utilities.
```

### Step 3.3: Write Rule Scope (1 Line)

Template:
```markdown
## Rule Scope

[Define exact applicability: technologies, contexts, use cases]
```

Example:
```markdown
## Rule Scope

All web applications using DaisyUI component library for UI development with Tailwind CSS.
```

### Step 3.4: Write Quick Start TL;DR

```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1]:** [Description - make it actionable]
- **[Pattern 2]:** [Description - make it actionable]
- **[Pattern 3]:** [Description - make it actionable]
[Add more patterns as needed - no maximum]

**Pre-Execution Checklist:**
- [ ] [Prerequisite check 1]
- [ ] [Prerequisite check 2]
- [ ] [Prerequisite check 3]
- [ ] [Prerequisite check 4]
- [ ] [Prerequisite check 5]
[5-7 items recommended]
```

**Essential Patterns should be:**
- Actionable (developers can apply immediately)
- Specific (not vague advice)
- Core to the technology (not edge cases)

**Pre-Execution Checklist should verify:**
- Required dependencies installed
- Configuration files present
- Access permissions available
- Prerequisites understood

### Step 3.5: Fill Contract Section (MUST be before line 160)

```markdown
## Contract

<inputs_prereqs>
[What the agent needs to have/know before starting]
Example: Project using [TECHNOLOGY]; access to configuration files; understanding of [concepts]
</inputs_prereqs>

<mandatory>
[Required tools, libraries, permissions, access]
Example: [TECHNOLOGY] v[VERSION]+; [related tools]; text editor; terminal access
</mandatory>

<forbidden>
[Prohibited actions, tools, or approaches]
Example: Don't use deprecated features; don't skip validation; don't hardcode credentials
</forbidden>

<steps>
1. [First required step - be specific]
2. [Second required step]
3. [Third required step]
4. [Fourth required step]
5. [Fifth required step]
[5-10 steps total, sequential and actionable]
</steps>

<output_format>
[Description of expected output format (file type, structure, content)]
Example: [Type of file/artifact] with [specific structure]; validated by [tool]
</output_format>

<validation>
[How to verify success - specific checks agent should run]
Example: Run [command]; verify [output]; check [file] contains [content]
</validation>
```

**Contract Placement Rule:** Must appear before line 160 to ensure agents read requirements early.

### Step 3.6: Write Anti-Patterns Section

Minimum 2 anti-patterns required:

```markdown
## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: [Descriptive Name]

**Problem:** [What developers do wrong]

```[language]
// Wrong approach code example
[show incorrect pattern]
```

**Why It Fails:**
- [Reason 1: technical consequence]
- [Reason 2: maintenance issue]
- [Reason 3: performance/security concern]

**Correct Pattern:**

```[language]
// Right approach code example
[show correct pattern]
```

**Benefits:**
- [Benefit 1: solves the technical issue]
- [Benefit 2: improves maintainability]
- [Benefit 3: enhances performance/security]

### Anti-Pattern 2: [Another Descriptive Name]
[Repeat structure above]
```

### Step 3.7: Write Post-Execution Checklist (5+ Items)

```markdown
## Post-Execution Checklist

- [ ] [Verification item 1 - different from pre-execution]
- [ ] [Verification item 2]
- [ ] [Verification item 3]
- [ ] [Verification item 4]
- [ ] [Verification item 5]
[5-7 items, focused on verifying completion]
```

**Should verify:**
- Implementation completed correctly
- Tests passing
- Documentation updated
- No regressions introduced
- Performance acceptable

### Step 3.8: Write Validation Section

```markdown
## Validation

**Success Checks:**
- [How to verify rule compliance - specific commands]
- [Expected outcomes - measurable]
- [Tools to run - with examples]

**Negative Tests:**
- [What should fail and how to detect it]
- [Edge cases to verify]
- [Common error scenarios]
```

### Step 3.9: Write Output Format Examples

Minimum 1 code block required:

```markdown
## Output Format Examples

```bash
# Example command
[command here]

# Expected output:
[output here]
```

```[language]
# Example code output
[code example here with proper syntax]
```

### Step 3.10: Write References Section

```markdown
## References

### Related Rules
- `rules/000-global-core.md` - Global standards and conventions
- `rules/[domain-core].md` - Domain foundation
- `rules/[related-rule].md` - Related patterns

### External Documentation
- [Official Docs](https://example.com/docs) - Official documentation
- [Community Guide](https://example.com/guide) - Community best practices
- [Tutorial](https://example.com/tutorial) - Getting started guide
```

**Important:** Related Rules must use `rules/` prefix (e.g., `rules/420-javascript-core.md`, not just `420-javascript-core.md`).

## Phase 4: Validation Loop

### Step 4.1: Run Schema Validator

```bash
python scripts/schema_validator.py rules/[NNN]-[technology]-[aspect].md
```

### Step 4.2: Check Exit Code

```bash
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✓ Validation PASSED - 0 CRITICAL errors"
  # Proceed to Phase 5
else
  echo "✗ Validation FAILED - fixing errors..."
  # Continue to Step 4.3
fi
```

### Step 4.3: Parse Validation Output

Read the validation report for error details:

```
================================================================================
VALIDATION REPORT: rules/NNN-technology-aspect.md
================================================================================

SUMMARY:
  ❌ CRITICAL: 2
  ⚠️  HIGH: 1
  ℹ️  MEDIUM: 0
  ✓ Passed: 445 checks

❌ CRITICAL ISSUES (2):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Keywords count: 8 (expected 10-15)
  Line: 5
  Fix: Add 2 more keywords to reach minimum of 10

[Contract] Missing XML tag: <validation>
  Line: 78
  Fix: Add <validation> tag in Contract section
```

### Step 4.4: Common Error Fixes

| Error Pattern | Fix |
|---------------|-----|
| Keywords count: 8 (expected 10-15) | Add 2-7 more keywords to metadata |
| TokenBudget format invalid | Change to `~1200` format (with tilde) |
| Missing XML tag: `<tag>` | Add missing tag to Contract section |
| Contract after line 160 | Move Contract section earlier in file |
| Section order wrong | Reorder sections per v3.0 schema |
| Missing required section | Add section with proper structure |

### Step 4.5: Apply Fixes and Re-validate

1. Update file with fixes
2. Re-run: `python scripts/schema_validator.py rules/NNN-tech.md`
3. Check exit code again
4. Repeat until exit code 0

**Maximum iterations:** 3 attempts
- If still failing after 3 iterations → Report unresolved errors to user
- Most rules pass within 1-2 iterations

### Step 4.6: Handle Different Severity Levels

**CRITICAL (Must fix):**
- Missing required metadata fields
- Missing required sections
- Missing Contract XML tags
- Keywords count outside 10-15 range
- → Block progression until resolved

**HIGH (Strongly recommended to fix):**
- Section order violations
- TokenBudget format issues
- → Fix if possible, document if intentional

**MEDIUM (Optional):**
- Missing Anti-Patterns section (recommended but optional)
- Missing some code examples
- → Consider fixing for quality, OK to proceed

## Phase 5: Indexing

### Step 5.1: Add Entry to RULES_INDEX.md

Format:
```markdown
| NNN-technology-aspect | [Scope description] | [Keywords] | [Dependencies] |
```

Example entries:
```markdown
| 422-daisyui-core | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility | rules/420-javascript-core.md |
| 125-snowflake-hybrid-tables | Snowflake Hybrid Tables for OLTP workloads | snowflake, hybrid tables, OLTP, row-level locking, unistore | rules/100-snowflake-core.md |
```

### Step 5.2: Insert in Correct Numeric Order

Rules should be ordered numerically in RULES_INDEX.md:
- Find correct position (after NNN-1, before NNN+1)
- Insert new row maintaining sorted order
- Verify table formatting remains intact

### Step 5.3: Verify Indexing Complete

Check:
- ✓ Rule number matches filename
- ✓ Scope description is clear and concise
- ✓ Keywords match metadata (exactly or subset)
- ✓ Dependencies listed correctly

## Complete Workflow Example: DaisyUI Rule

```markdown
USER: Create a new Cursor rule documenting DaisyUI best practices

AGENT EXECUTION:

═══════════════════════════════════════════════════════════
PHASE 1: DISCOVERY & RESEARCH
═══════════════════════════════════════════════════════════

Step 1: Search RULES_INDEX.md
$ grep -i "daisyui\|javascript\|tailwind" RULES_INDEX.md

Results:
- 420-javascript-core.md (JavaScript foundation)
- 421-javascript-alpinejs-core.md (Alpine.js patterns)

Analysis:
- Domain: 420-449 (JavaScript/Frontend)
- Next available: 422

Step 2: Load domain core
Loading @rules/420-javascript-core.md for context...

Step 3: Web research
Searching: "2024 2025 DaisyUI best practices"
Searching: "DaisyUI component library guidelines"

Key findings:
- Semantic HTML with utility classes
- Theme customization via CSS variables
- Accessibility-first approach
- Zero runtime JavaScript overhead
- Component composition patterns

Keywords identified: daisyui, tailwind, components, ui library, themes, 
accessibility, semantic html, css variables, responsive design, customization,
utility-first, design system, best practices, patterns, optimization

═══════════════════════════════════════════════════════════
PHASE 2: TEMPLATE GENERATION
═══════════════════════════════════════════════════════════

$ python scripts/template_generator.py 422-daisyui-core \
    --context-tier Medium \
    --output-dir rules/

✓ Created rule template: rules/422-daisyui-core.md

Verification:
✓ All 9 required sections present
✓ Contract section with 6 XML tags
✓ Metadata structure ready

═══════════════════════════════════════════════════════════
PHASE 3: CONTENT POPULATION
═══════════════════════════════════════════════════════════

Updating rules/422-daisyui-core.md:

✓ Metadata filled:
  - Keywords: 15 semantic terms
  - TokenBudget: ~1200 (estimated)
  - ContextTier: Medium
  - Depends: rules/000-global-core.md, rules/420-javascript-core.md

✓ Purpose: "Establishes best practices for DaisyUI component library..."
✓ Rule Scope: "All web applications using DaisyUI..."
✓ Quick Start TL;DR: 4 Essential Patterns, 6 Pre-Execution items
✓ Contract: All 6 XML tags filled (before line 160)
✓ Anti-Patterns: 3 patterns with code examples
✓ Post-Execution Checklist: 7 verification items
✓ Validation: Success checks and negative tests defined
✓ Output Format Examples: 3 code blocks with examples
✓ References: 3 related rules + 4 external docs

═══════════════════════════════════════════════════════════
PHASE 4: VALIDATION LOOP
═══════════════════════════════════════════════════════════

Iteration 1:
$ python scripts/schema_validator.py rules/422-daisyui-core.md

Result: FAILED (exit code 1)
Errors:
  ❌ CRITICAL: 1 (Keywords count: 9, expected 10-15)

Fix applied: Added "component-design" keyword
  
Iteration 2:
$ python scripts/schema_validator.py rules/422-daisyui-core.md

Result: PASSED (exit code 0)
✓ 0 CRITICAL errors
✓ 0 HIGH errors  
ℹ️  1 MEDIUM warning (acceptable)

═══════════════════════════════════════════════════════════
PHASE 5: INDEXING
═══════════════════════════════════════════════════════════

Adding to RULES_INDEX.md:
| 422-daisyui-core | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |

✓ Entry added in correct numeric position (after 421, before 440)
✓ Formatting verified

═══════════════════════════════════════════════════════════
COMPLETE
═══════════════════════════════════════════════════════════

✅ Production-ready rule created: rules/422-daisyui-core.md
✅ Validates with 0 CRITICAL errors
✅ Added to RULES_INDEX.md
✅ Ready for immediate use in Cursor
```

## Validation Gates Summary

All gates must pass before considering rule complete:

1. ✓ RULES_INDEX.md searched for existing rules
2. ✓ Domain range identified (e.g., 420-449)
3. ✓ Next available number determined (e.g., 422)
4. ✓ template_generator.py executed successfully
5. ✓ Template verified (9 sections + Contract with 6 XML tags)
6. ✓ All metadata fields filled correctly
7. ✓ Keywords: 10-15 comma-separated terms
8. ✓ TokenBudget: ~NUMBER format
9. ✓ ContextTier: valid value (Critical|High|Medium|Low)
10. ✓ Contract before line 160
11. ✓ schema_validator.py returns exit code 0
12. ✓ Rule added to RULES_INDEX.md

## Error Recovery Patterns

### Recovery Pattern 1: Template Generation Fails

```bash
Error: Invalid filename format

Fix: Verify filename pattern: NNN-technology-aspect
  - NNN must be 3 digits (e.g., 422, not 42)
  - Use hyphens (not underscores)
  - Use lowercase (e.g., daisyui, not DaisyUI)

Retry with corrected filename
```

### Recovery Pattern 2: Validation Fails After Multiple Iterations

```bash
After 3 iterations, still have CRITICAL errors

Action:
1. Review error messages carefully
2. Check @rules/002d-schema-validator-usage.md for error resolution
3. For persistent issues:
   - Read similar rules for structure examples
   - Verify section order matches v3.0 schema exactly
   - Confirm all XML tags spelled correctly
4. Request user assistance if needed
```

### Recovery Pattern 3: Domain Detection Ambiguous

```bash
Technology could fit multiple domains

Example: "React Testing Library"
  - Could be 200-299 (Python testing)
  - Could be 440-449 (React frontend)

Action: Ask user to clarify:
  "React Testing Library is primarily used for frontend React testing.
   Recommended domain: 440-449 (React).
   Suggested number: 442-react-testing-library.
   Proceed? (yes/no/suggest alternative)"
```

## Success Criteria

Rule creation is successful when:
- ✅ File exists at `rules/NNN-technology-aspect.md`
- ✅ `schema_validator.py` returns exit code 0 (0 CRITICAL errors)
- ✅ Rule added to `RULES_INDEX.md` in correct position
- ✅ Rule loads successfully in Cursor with `@rules/` prefix
- ✅ Metadata enables semantic discovery via RULES_INDEX
- ✅ Content reflects current (2024-2025) best practices

## References

- **Rule Governance:** `@rules/002-rule-governance.md` - v3.0 schema standards
- **Creation Guide:** `@rules/002a-rule-creation-guide.md` - Detailed workflow
- **Optimization Guide:** `@rules/002b-rule-optimization.md` - Token budgets
- **Validator Usage:** `@rules/002d-schema-validator-usage.md` - Validation commands
- **Template Generator:** `@scripts/template_generator.py` - Rule template script
- **Schema Validator:** `@scripts/schema_validator.py` - v3.0 validation script
- **Rules Index:** `@RULES_INDEX.md` - Master index for discovery
- **Example Prompt:** `@prompts/EXAMPLE_PROMPT_04_RULE_CREATION.md` - Usage examples

