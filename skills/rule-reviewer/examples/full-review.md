# Example: FULL Review

## Custom Output Directory

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45
output_root: mytest/
```

Expected output file:

`mytest/rule-reviews/801-project-readme-claude-sonnet45-2025-12-12.md`

---

## Default Output Directory

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45
```

Expected output file:

`reviews/rule-reviews/801-project-readme-claude-sonnet45-2025-12-12.md` (or `...-01.md`, `...-02.md`, etc. if the base filename already exists)

## Review Workflow

### Step 1: Read Target Rule

```bash
# Agent reads complete rule file
cat rules/801-project-readme.md
```

### Step 2: Run Schema Validation (MANDATORY)

```bash
uv run ai-rules validate rules/801-project-readme.md
```

**Example Output:**
```
[CRITICAL] Missing metadata field: Depends
[HIGH] Section order violation: Contract appears before References
[MEDIUM] TokenBudget ±18% off actual (stated ~2000, actual ~2360)

SUMMARY:
   CRITICAL: 1
    HIGH: 1
  ℹ️  MEDIUM: 1

Result: FAILED
```

**Parsability Impact:** 1 CRITICAL + 1 HIGH error = Score capped at 2/5 (6/15)

### Step 3: Execute Agent Execution Test

**Blocking Issues Found:**
- 3 undefined thresholds ("significant", "appropriate", "clear")
- 2 conditionals without explicit branches
- 1 visual formatting issue (ASCII arrow character)

**Total:** 6 blocking issues (under threshold of 10, scoring proceeds normally)

### Step 4: Score All 7 Dimensions

Using weighted formula from SKILL.md:
- Actionability: 3/5 × 5 = 15/25
- Completeness: 4/5 × 5 = 20/25
- Consistency: 5/5 × 3 = 15/15
- Parsability: 2/5 × 3 = 6/15 (capped by schema CRITICAL errors)
- Token Efficiency: 4/5 × 2 = 8/10
- Rule Size: 8/10 × 2 = 8/10 (480 lines, within target)
- Staleness: 5/5 × 2 = 10/10

**Overall Score:** 82/105

### Step 5: Generate Review Output

**Schema Validation Section (included in Parsability):**

```markdown
#### 4. Parsability Score: 2/5 (6/15)

**Schema Validation Results:**
- CRITICAL: 1 errors
- HIGH: 1 errors
- MEDIUM: 1 errors

**Rationale:** Schema validation detected CRITICAL errors, capping this score at 2/5 per rubric. The missing "Depends" field prevents agents from loading prerequisite rules via dependency chain, breaking the rule loading protocol defined in AGENTS.md.

**Critical Schema Violations:**
1. [CRITICAL] Missing metadata field: Depends (line 10) - Required field per schemas/rule-schema.yml
2. [HIGH] Section order violation: Contract appears before References (line 45) - References must appear before Contract per v3.2 schema
```

**Critical Issues Section:**
1. **Schema Violation (CRITICAL):** Missing metadata field: Depends (line 10)
2. **Schema Violation (HIGH):** Section order violation: Contract appears before References (line 45)
3. **Undefined Threshold:** "significant changes" in line 67 requires quantification
4. **Missing Branch:** Conditional "If repository is public..." has no else clause (line 134)

**Recommendations:**
1. Add missing "Depends" field to metadata section (line 10): `**Depends:** 000-global-core.md`
2. Reorder sections: Move References section (lines 145-160) before Contract section (line 45)
3. Quantify "significant changes" threshold (line 67): Define as ">10 modified files" or ">500 lines changed"
4. Add explicit else branch to public/private conditional (line 134)

### Step 6: Write Review to File

```bash
# Agent writes complete review to:
reviews/rule-reviews/801-project-readme-claude-sonnet45-2025-12-12.md
```

**File Size Validation:** 5,234 bytes (within expected range of 3000-8000 for typical rules)

## Key Takeaways

1. **Schema validation is mandatory** - Run before dimension scoring
2. **Line count is 100% deterministic** - `wc -l` for Rule Size dimension
3. **CRITICAL errors cap Parsability** - 1+ CRITICAL = max 2/5 score
4. **HIGH errors also cap** - 3+ HIGH = max 3/5 score
5. **Rule Size flags trigger actions** - >600 lines = SPLITTING_REQUIRED
6. **Schema errors go to Critical Issues** - All CRITICAL/HIGH violations listed
7. **Specific recommendations required** - Include line numbers and fix suggestions from validator
