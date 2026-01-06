# Example Prompt: Rule Creation with Script Orchestration

## Purpose

This example demonstrates how to request creation of a new Cursor rule following v3.2 schema standards by orchestrating existing automation scripts (`template_generator.py` and `schema_validator.py`).

## Prompt Template

```markdown
Create a new Cursor rule documenting [TECHNOLOGY] best practices following v3.2 schema.

MANDATORY PRE-FLIGHT CHECKS:
1. Search RULES_INDEX.md Keywords column for existing [TECHNOLOGY] rules
2. Identify domain range (e.g., 420-449 for JavaScript frameworks)
3. Determine next available rule number
4. Load domain core rule (e.g., rules/420-javascript-core.md for frontend)
5. Load rules/002-rule-governance.md, rules/002a-rule-creation-guide.md, rules/002b-rule-optimization.md, rules/002d-schema-validator-usage.md

PHASE 1: DISCOVERY & RESEARCH
1. Search RULES_INDEX.md for related rules:
   - grep -i "[technology]" RULES_INDEX.md
   - Identify domain pattern from existing numbers
   - Determine next available number in range

2. Load domain-specific rules:
   - Frontend (420-449): rules/420-javascript-core.md
   - Python (200-299): rules/200-python-core.md
   - Snowflake (100-199): rules/100-snowflake-core.md
   - Shell (300-399): rules/300-bash-scripting-core.md
   - Docker (400-499): rules/350-docker-best-practices.md

3. Web research for current best practices:
   - Search: "2024 2025 [TECHNOLOGY] best practices"
   - Search: "[TECHNOLOGY] industry standards community guidelines"
   - Focus on: Official docs, widely-adopted patterns, performance optimization
   - Identify: 10-15 semantic keywords for metadata

PHASE 2: TEMPLATE GENERATION
1. Execute template_generator.py:
   ```bash
   python scripts/template_generator.py [NUMBER]-[technology]-[aspect] \
     --context-tier [Critical|High|Medium|Low] \
     --output-dir rules/
   ```

2. Verify template created successfully:
   - File exists at rules/NNN-technology-aspect.md
   - Contains all 9 required sections
   - Contract section has 6 XML tags
   - Metadata structure present

PHASE 3: CONTENT POPULATION
1. Fill Metadata (lines 1-12):
   - **Keywords:** [10-15 comma-separated semantic terms from research]
   - **TokenBudget:** ~[estimate: lines × 2, round to nearest 50]
   - **ContextTier:** [Critical|High|Medium|Low based on importance]
   - **Depends:** rules/000-global-core.md, rules/[domain-core].md

2. Write Purpose (1-2 sentences):
   - What problem does this rule solve?
   - Why is it important for [TECHNOLOGY] users?

3. Write Rule Scope (1 line):
   - Define exact applicability: technologies, contexts, use cases

4. Write Quick Start TL;DR:
   - **MANDATORY:** header (required)
   - **Essential Patterns:** Minimum 3, no maximum
     - **[Pattern name]:** Brief description
   - **Pre-Execution Checklist:** 5-7 items
     - [ ] Specific prerequisite checks

5. Fill Contract Section (MUST be before line 160):
   - <inputs_prereqs>: What agent needs before starting
   - <mandatory>: Required tools, libraries, access
   - <forbidden>: Prohibited actions, anti-patterns
   - <steps>: 5-10 sequential steps
   - <output_format>: Expected output description
   - <validation>: How to verify success

6. Write Anti-Patterns and Common Mistakes:
   - Minimum 2 anti-patterns with:
     - **Problem:** Description of wrong approach
     - Code example showing incorrect pattern
     - **Why It Fails:** Explanation of consequences
     - **Correct Pattern:** Right approach
     - Code example showing correct pattern
     - **Benefits:** Why correct pattern is better

7. Write Post-Execution Checklist (5+ items):
   - Different from Pre-Execution checklist
   - Verification items after task completion

8. Write Validation Section:
   - **Success Checks:** How to verify compliance
   - **Negative Tests:** What should fail and how

9. Write Output Format Examples:
   - Minimum 1 code block with examples
   - Show command execution and expected output
   - Demonstrate correct patterns from research

10. Write References Section:
    - **Related Rules:** Links to rules/ files (use rules/ prefix)
    - **External Documentation:** Official docs, community resources

PHASE 4: VALIDATION & ITERATION
1. Run schema validator:
   ```bash
   python scripts/schema_validator.py rules/[NNN]-[technology]-[aspect].md
   ```

2. Check exit code and parse output:
   - Exit code 0: PASS (proceed to Phase 5)
   - Exit code 1: FAIL (continue to step 3)

3. If CRITICAL errors present:
   - Read error messages with line numbers
   - Common fixes:
     - Missing metadata field → Add **Field:** value
     - Keywords count wrong → Adjust to 10-15 terms
     - TokenBudget format → Change to ~NUMBER format
     - Missing Contract XML tag → Add tag in Contract section
     - Section order wrong → Reorder per v3.2 schema
   - Apply fixes to rule file
   - Go to step 1 (re-validate)

4. If HIGH errors present:
   - Review and fix if possible
   - Document if intentionally deviating from standard

5. If MEDIUM warnings only:
   - Consider addressing for quality
   - Acceptable to proceed with warnings

6. Continue validation loop until 0 CRITICAL errors

PHASE 5: INDEXING
1. Add entry to RULES_INDEX.md:
   - Format: | NNN-technology-aspect | [Scope description] | [Keywords] | [Dependencies] |
   - Place in correct numeric order
   - Match keywords from metadata

2. Verify index entry:
   - Rule number matches filename
   - Keywords aid semantic discovery
   - Dependencies listed accurately

VALIDATION GATES (All must pass):
- [ ] RULES_INDEX.md searched for existing rules
- [ ] Domain range identified and number available
- [ ] template_generator.py executed successfully
- [ ] All 4 metadata fields present with correct format
- [ ] Keywords: 10-15 comma-separated terms
- [ ] TokenBudget: ~NUMBER format (e.g., ~1200)
- [ ] All 9 required sections present in order
- [ ] Contract has 6 XML tags before line 160
- [ ] schema_validator.py returns 0 CRITICAL errors (exit code 0)
- [ ] Rule added to RULES_INDEX.md

OUTPUT:
Production-ready rule file at rules/NNN-[technology]-[aspect].md ready for immediate use.
```

## Example Usage

### Example 1: DaisyUI Component Library Rule

```markdown
Create a new Cursor rule documenting DaisyUI best practices following v3.2 schema.

[Agent follows 5-phase workflow above]

Expected output:
- rules/422-daisyui-core.md created
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
- Ready for use in Cursor
```

### Example 2: Python Testing Library Rule

```markdown
Create a new Cursor rule documenting pytest-mock best practices following v3.2 schema.

[Agent follows 5-phase workflow above]

Expected output:
- rules/209-python-pytest-mock.md created (if 208 is next available in 200-299 range)
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
- Ready for use in Cursor
```

### Example 3: Snowflake Feature Rule

```markdown
Create a new Cursor rule documenting Snowflake Hybrid Tables best practices following v3.2 schema.

[Agent follows 5-phase workflow above]

Expected output:
- rules/125-snowflake-hybrid-tables.md created (if 125 is next available in 100-199 range)
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
- Ready for use in Cursor
```

## Key Differences from Manual Rule Creation

| Aspect | Manual Approach | Script Orchestration Approach |
|--------|----------------|-------------------------------|
| Template creation | Copy existing rule, modify | Run `template_generator.py` |
| Structure validation | Manual review | Automatic via `schema_validator.py` |
| Error detection | Visual inspection | Automated with exit codes |
| Fix iteration | Manual trial-and-error | Structured validation loop |
| Consistency | Varies by author | Guaranteed by scripts |
| Time to production | 30-60 minutes | 10-20 minutes |

## Anti-Patterns to Avoid

### Anti-Pattern 1: Skipping Template Generator

**Problem:** Manually creating rule file structure instead of using `template_generator.py`.

**Why It Fails:** High risk of missing required sections, incorrect metadata format, wrong section order. Manual files often have CRITICAL validation errors.

**Correct Pattern:** Always use `template_generator.py` to create initial structure, then populate content.

### Anti-Pattern 2: Single-Pass Validation

**Problem:** Running `schema_validator.py` once, seeing errors, and manually fixing without re-validating.

**Why It Fails:** Fixes may introduce new errors. No confirmation that all CRITICAL errors resolved.

**Correct Pattern:** Implement validation loop: validate → fix → validate → repeat until exit code 0.

### Anti-Pattern 3: Proceeding with CRITICAL Errors

**Problem:** Adding rule to RULES_INDEX.md and considering it "done" despite CRITICAL validation errors.

**Why It Fails:** Rule won't load correctly in Cursor, breaks semantic discovery, violates v3.2 schema.

**Correct Pattern:** Block progression to Phase 5 (indexing) until `schema_validator.py` returns exit code 0.

## References

- **Rule Governance:** `rules/002-rule-governance.md` - v3.2 schema requirements
- **Creation Guide:** `rules/002a-rule-creation-guide.md` - Detailed rule creation workflow
- **Optimization Guide:** `rules/002b-rule-optimization.md` - Token budget guidance
- **Validator Usage:** `rules/002d-schema-validator-usage.md` - Validation commands and error resolution
- **Template Generator:** `scripts/template_generator.py` - Rule template creation script
- **Schema Validator:** `scripts/schema_validator.py` - v3.2 schema validation script
- **Rules Index:** `RULES_INDEX.md` - Master index for semantic discovery

