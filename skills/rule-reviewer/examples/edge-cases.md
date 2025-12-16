# Edge Cases: Rule Reviewer

This document captures ambiguous scenarios, unusual inputs, and their resolutions for the rule review workflow.

## Edge Case 1: Rule File Has Invalid Structure

**Scenario:** Target rule fails to parse (invalid YAML, missing sections)

**Example:**
```
target_file: rules/broken-rule.md
Error: Could not parse metadata - invalid YAML frontmatter
```

**Resolution Pattern:**
```
Pre-review validation failed: Rule structure invalid

Issue: YAML frontmatter parsing error at line 5

Options:
A. Run schema_validator.py first to identify structural issues
B. Perform partial review (content only, skip metadata scoring)
C. Decline review until structure is fixed

Recommendation: Option A

Command: python scripts/schema_validator.py rules/broken-rule.md

This will identify:
- Missing required sections
- Invalid metadata format
- Structural violations

Fix structural issues first, then re-run review.
```

---

## Edge Case 2: Review Mode Doesn't Match Rule Type

**Scenario:** STALENESS review requested for brand-new rule

**Example:**
```
target_file: rules/999-new-technology.md (created today)
review_mode: STALENESS
```

**Resolution Pattern:**
```
Review mode mismatch detected:

Rule: rules/999-new-technology.md
Created: 2025-12-15 (today)
Requested mode: STALENESS

STALENESS reviews check for:
- Outdated patterns (6+ months old)
- Deprecated APIs/tools
- Version drift from current releases

For new rules, STALENESS review will return:
- All "current" scores (trivially passes)
- No meaningful staleness findings

Recommendation: Use FULL review for new rules

Proceed with STALENESS anyway? (yes/no/switch to FULL)
```

---

## Edge Case 3: FOCUSED Review Without Focus Area

**Scenario:** User selects FOCUSED mode but doesn't specify what to focus on

**Example:**
```
target_file: rules/200-python-core.md
review_mode: FOCUSED
focus_area: (not provided)
```

**Resolution Pattern:**
```
FOCUSED review requires a focus_area parameter.

Available focus areas for rule reviews:
A. metadata - Keywords, TokenBudget, ContextTier, Depends
B. contract - XML tags, placement, completeness
C. examples - Code examples, anti-patterns quality
D. references - External links, related rules accuracy
E. clarity - Readability, structure, progressive disclosure

Please specify: focus_area: [A|B|C|D|E]

Or switch to FULL review for comprehensive evaluation.
```

---

## Edge Case 4: Rule References Non-Existent Dependencies

**Scenario:** Rule's `Depends:` field references rules that don't exist

**Example:**
```
# In rules/422-daisyui-core.md
**Depends:** rules/420-javascript-core.md, rules/421-tailwind-core.md

# But rules/421-tailwind-core.md doesn't exist
```

**Resolution Pattern:**
```
Dependency validation warning:

Rule: rules/422-daisyui-core.md
Declared dependencies:
  ✓ rules/420-javascript-core.md (exists)
  ✗ rules/421-tailwind-core.md (NOT FOUND)

Impact on review:
- Cannot verify dependency chain completeness
- May affect "Related Rules" scoring

Options:
A. Proceed with review, flag missing dependency as issue
B. Pause review, create missing dependency first
C. Update rule to remove invalid dependency, then review

Recommendation: Option A
The review will note this as a HIGH severity issue in the 
"References" dimension.
```

---

## Edge Case 5: Very Large Rule File

**Scenario:** Rule exceeds typical size (>500 lines, >5000 tokens)

**Example:**
```
target_file: rules/000-global-core.md
Size: 622 lines, ~6500 tokens
```

**Resolution Pattern:**
```
Large rule file detected:

File: rules/000-global-core.md
Lines: 622
Estimated tokens: ~6500

Considerations:
- Full review may timeout
- TokenBudget may be intentionally high (Critical tier)
- May need chunked analysis

Options:
A. Proceed with FULL review (may be slow)
B. Use FOCUSED review on specific sections
C. Split into multiple FOCUSED reviews

Recommendation: 
- For Critical tier rules: Option A (comprehensive review justified)
- For Medium/Low tier rules: Option B (investigate why so large)

Proceeding with FULL review...
(Timeout extended to 180s for large file)
```

---

## Edge Case 6: Rule Has No Anti-Patterns Section

**Scenario:** Rule missing optional Anti-Patterns section

**Example:**
```
target_file: rules/820-taskfile.md
# No "## Anti-Patterns" section found
```

**Resolution Pattern:**
```
Optional section missing: Anti-Patterns

Rule: rules/820-taskfile.md
Missing: ## Anti-Patterns and Common Mistakes

Impact on scoring:
- Not a structural violation (section is optional)
- May reduce "Completeness" score
- Consider domain: Some technologies have fewer anti-patterns

Review handling:
- Score as "acceptable" if rule is otherwise comprehensive
- Note as "improvement opportunity" in recommendations
- Check if similar rules in domain have anti-patterns

Recommendation in review:
"Consider adding Anti-Patterns section with common Taskfile 
mistakes (e.g., circular dependencies, missing error handling)
to improve rule completeness."
```

---

## Edge Case 7: Model Slug Not Recognized

**Scenario:** User provides non-standard model identifier

**Example:**
```
model: gpt-4-turbo
# But this is a Claude skill, not OpenAI
```

**Resolution Pattern:**
```
Model slug validation:

Provided: gpt-4-turbo
Expected: Claude model slug

Valid Claude slugs:
- claude-opus-4
- claude-sonnet-4
- claude-sonnet-45
- claude-haiku

For output filename, will normalize to provided slug:
reviews/810-project-readme-gpt-4-turbo-2025-12-15.md

Note: The review will be performed by the current Claude model,
regardless of the slug provided. The slug is for filename 
identification only.

Proceed with slug "gpt-4-turbo"? (yes/no/use claude-sonnet-45)
```

---

## Edge Case 8: Review Output File Already Exists (All Suffixes)

**Scenario:** Base filename and all numbered suffixes exist

**Example:**
```
Existing files:
- reviews/810-project-readme-claude-sonnet45-2025-12-15.md
- reviews/810-project-readme-claude-sonnet45-2025-12-15-01.md
- reviews/810-project-readme-claude-sonnet45-2025-12-15-02.md
... through -99.md
```

**Resolution Pattern:**
```
Output filename exhausted:

All suffix slots (01-99) are occupied for:
reviews/810-project-readme-claude-sonnet45-2025-12-15-XX.md

Options:
A. Use different date (tomorrow's date)
B. Use different model slug
C. Archive old reviews and reuse base filename
D. Use 3-digit suffix (-100.md)

Recommendation: Option A or B

Alternative filename:
reviews/810-project-readme-claude-sonnet45-2025-12-16.md

Or with different slug:
reviews/810-project-readme-claude-opus4-2025-12-15.md
```

---

## Edge Case 9: Rule Content is Mostly Placeholder

**Scenario:** Rule exists but contains placeholder text

**Example:**
```
## Key Principles

### 1. [Pattern Name]
[Description of pattern]

### 2. [Another Pattern]
[TODO: Add content]
```

**Resolution Pattern:**
```
Placeholder content detected:

File: rules/999-incomplete-rule.md
Placeholders found:
- Line 45: "[Pattern Name]"
- Line 46: "[Description of pattern]"
- Line 52: "[TODO: Add content]"

Review handling options:
A. Decline review - rule is incomplete
B. Review structure only, note content gaps
C. Provide completion recommendations instead of scores

Recommendation: Option A

Response:
"Rule contains placeholder content and is not ready for review.
Please complete content population (Phase 3 of rule-creator) 
before requesting review.

Placeholders to resolve:
- Line 45-46: Key Principles section
- Line 52: TODO marker

After completion, run schema_validator.py, then request review."
```

---

## Edge Case 10: Cross-Skill Validation Request

**Scenario:** User wants to validate rule-creator output with rule-reviewer

**Example:**
```
"I just created rules/425-nextjs-core.md using rule-creator.
Can you review it to verify quality?"
```

**Resolution Pattern:**
```
Cross-skill validation request detected.

Workflow:
1. Verify rule-creator completion:
   - Check schema_validator.py passed (exit code 0)
   - Check RULES_INDEX.md entry exists

2. Run rule-reviewer FULL review:
   - target_file: rules/425-nextjs-core.md
   - review_mode: FULL
   - review_date: [today]
   - model: [current]

3. Compare against creation quality gates:
   - Keywords: 10-15 ✓
   - TokenBudget: ~NUMBER format ✓
   - Contract before line 160 ✓
   - All 6 XML tags present ✓

4. Additional review dimensions:
   - Content accuracy (web research quality)
   - Example code correctness
   - Anti-pattern relevance

This provides end-to-end quality assurance for newly created rules.
```

---

## Quick Reference: Edge Case Decision Tree

```
Does rule file parse correctly?
├─ YES → Proceed to review
└─ NO → Run schema_validator first (Edge Case 1)

Is review mode appropriate for rule age?
├─ YES → Proceed
└─ NO → Suggest alternative mode (Edge Case 2)

Is FOCUSED mode with focus_area?
├─ YES → Proceed
└─ NO → Request focus_area (Edge Case 3)

Do declared dependencies exist?
├─ YES → Proceed
└─ NO → Flag in review (Edge Case 4)

Is rule unusually large?
├─ YES → Extend timeout, consider FOCUSED (Edge Case 5)
└─ NO → Proceed with standard review

Is output filename available?
├─ YES → Write file
└─ NO → Use suffix or alternative (Edge Case 8)

Does rule contain placeholders?
├─ YES → Decline review (Edge Case 9)
└─ NO → Proceed with full review
```

## Integration with rule-creator

When reviewing rules created by rule-creator skill:

1. **Verify creation completion:**
   ```bash
   python scripts/schema_validator.py rules/<file>.md
   # Must return exit code 0
   ```

2. **Check indexing:**
   ```bash
   grep "<rule-name>" RULES_INDEX.md
   # Must find entry
   ```

3. **Run comprehensive review:**
   ```
   target_file: rules/<file>.md
   review_mode: FULL
   review_date: <today>
   model: <current>
   ```

4. **Quality threshold for new rules:**
   - Overall score: ≥ 75/100
   - No CRITICAL issues
   - No HIGH issues in Actionability or Completeness dimensions

