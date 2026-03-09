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

**Total:** 6 blocking issues (triggers hard cap: total score capped at 80/100)

### Step 4: Score All 6 Dimensions

Using weighted formula from SKILL.md (Scoring Rubric v2.0):

| Dimension | Raw | Weight | Points |
|-----------|-----|--------|--------|
| Actionability | 6/10 | ×3.0 | 18/30 |
| Rule Size | 9/10 | ×2.5 | 22.5/25 |
| Parsability | 4/10 | ×1.5 | 6/15 |
| Completeness | 8/10 | ×1.5 | 12/15 |
| Consistency | 8/10 | ×1.0 | 8/10 |
| Cross-Agent | 9/10 | ×0.5 | 4.5/5 |

**Raw Total:** 71/100

**Hard Cap Applied:** 6 blocking issues → capped at 80/100

**Final Score:** 71/100 (under cap, no adjustment needed)

**Informational Dimensions (not scored):**
- Token Efficiency: 3 redundancy issues noted → See recommendations
- Staleness: LastUpdated current, no deprecated patterns → No action needed

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
3. **6 scored dimensions** - Token Efficiency and Staleness are informational only
4. **Hard caps apply** - >600 lines caps at 70/100, ≥6 blocking issues caps at 80/100
5. **Rule Size flags trigger actions** - >600 lines = SPLIT_REQUIRED, >700 = BLOCKED
6. **Schema errors go to Critical Issues** - All CRITICAL/HIGH violations listed
7. **New verdict thresholds** - 90-100 EXECUTABLE, 75-89 REFINEMENTS, 50-74 NEEDS_REFINEMENT, <50 NOT_EXECUTABLE
