# Rule Size Rubric (25 points)

> **Weight:** 5 | **Max:** 25 points | **Formula:** Raw × 2.5

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **100% deterministic:** Line count is objective: no judgment required
- **Unambiguous signals:** Clear thresholds produce clear remediation actions
- **Zero inter-run variance:** Same file always produces same line count
- **Agent executability:** Clear decision boundaries for autonomous action
- **Heavy enforcement:** 25% of total score ensures oversized rules are severely penalized

### Inventory Template

**Line Count Assessment:**

| Metric | Value |
|--------|-------|
| Total lines | NNN |
| Optimal threshold | 150 |
| Target threshold (validator limit) | 250 |
| Warning threshold | 275 |
| Split required threshold | 300 |
| Hard cap threshold | 350 |
| Variance from target | +NN% or -NN% |
| Score tier | X/10 |
| Flag | [None/SPLIT_RECOMMENDED/SPLIT_REQUIRED/NOT_DEPLOYABLE/BLOCKED] |

### Counting Protocol (3 Steps)

**Step 1: Count Lines**
```bash
wc -l [target_file]
```

**Step 2: Calculate Variance**
```
Variance % = ((Actual - 250) / 250) × 100

Examples:
  225 lines: ((225 - 250) / 250) × 100 = -10% (under target)
  275 lines: ((275 - 250) / 250) × 100 = +10% (over target)
  325 lines: ((325 - 250) / 250) × 100 = +30% (critical)
```

**Step 3: Look Up Score and Flag**
- Use Score Decision Matrix below
- Record score with line count evidence
- Apply appropriate flag

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 5
**Points:** Raw × 2.5

## Hard Caps (Score Ceiling)

| Condition | Maximum Score | Effect |
|-----------|---------------|--------|
| >300 lines | 70/100 | NEEDS_REFINEMENT forced |
| >350 lines | 50/100 | NOT_EXECUTABLE forced |

**Note:** Hard caps apply to the TOTAL rule score, not just this dimension.

**Over the validator limit:** 250 lines matches `structure.max_lines` in `schemas/rule-schema.yml`, where `ai-rules validate` reports a HIGH finding. A rule over 250 lines scores at most 5/10 here (12.5 points), so its total cannot exceed 87.5/100 and it cannot be rated EXECUTABLE. Numeric source of truth: [`references/reviewer-defaults.yml`](../references/reviewer-defaults.yml) (`rule_size_bands`, `hard_caps`).

## Score Decision Matrix

| Lines | Raw | Points | Flag | Agent Action | Hard Cap |
|-------|-----|--------|------|--------------|----------|
| ≤150 | 10 | 25 | None | None (optimal) | - |
| 151-200 | 9 | 22.5 | None | None | - |
| 201-250 | 8 | 20 | None | None (at limit) | - |
| 251-275 | 5 | 12.5 | `SPLIT_RECOMMENDED` | Review for split | - |
| 276-300 | 3 | 7.5 | `SPLIT_REQUIRED` | Mandatory split plan | - |
| 301-350 | 1 | 2.5 | `NOT_DEPLOYABLE` | Block deployment | Max 70/100 |
| >350 | 0 | 0 | `BLOCKED` | Reject review | Max 50/100 |

## Flag Definitions

### `SPLIT_RECOMMENDED` (251-275 lines)

**Meaning:** Rule exceeds the 250-line limit by up to 10%. `ai-rules validate` already reports a HIGH finding for this file; the reviewer flag is the remediation prompt, not a second gate.

**Agent Behavior:**
- Log warning in review output
- Suggest split opportunities
- Do NOT change the verdict (the `ai-rules validate` HIGH finding is the merge gate)
- Track for future optimization

**Remediation Options:**
1. Identify logical split points (sections >50 lines)
2. Move examples to separate file
3. Extract reference tables
4. Compress verbose prose to lists

### `SPLIT_REQUIRED` (276-300 lines)

**Meaning:** Rule exceeds the 250-line limit by >10%. Must be split before deployment.

**Agent Behavior:**
- Flag as blocking issue
- Require split plan in review
- Block merge/deployment until addressed
- Escalate if not resolved

**Remediation Steps:**
1. Identify logical split points (sections >50 lines)
2. Create split plan with proposed file names
3. Ensure each split file is self-contained
4. Update cross-references between split files
5. Verify each split file ≤250 lines

**Split Candidate Identification:**
```markdown
Analyze rule structure:
- Sections >50 lines → Split candidate
- Standalone examples → Extract to examples/
- Reference tables → Extract to references/
- Domain-specific subsections → Extract to NNNa, NNNb pattern
```

### `NOT_DEPLOYABLE` (301-350 lines)

**Meaning:** Rule significantly exceeds the 250-line limit. Cannot be deployed without split.

**Agent Behavior:**
- Fail the review
- **Apply hard cap: Max total score 70/100**
- Force verdict: NEEDS_REFINEMENT minimum
- Require immediate remediation

**Remediation:**
- Major split required
- Split into 2-3 focused rules
- May require architectural review

### `BLOCKED` (>350 lines)

**Meaning:** Rule is too large for agent context windows. Review rejected.

**Agent Behavior:**
- Reject the review
- **Apply hard cap: Max total score 50/100**
- Force verdict: NOT_EXECUTABLE
- Do NOT allow any deployment path

**Remediation:**
- Complete restructure required
- Split into 3-4+ focused rules
- Architectural review mandatory

## Rationale: Why 250 Lines?

### Context Window Efficiency

Per 000-global-core.md Priority 3 (HIGH):
> Minimize tokens without sacrificing Priority 1 or Priority 2

The reviewer scale matches the repository limit: `ai-rules validate` reports a HIGH finding for any rule over 250 lines (`schemas/rule-schema.yml` `structure.max_lines`).

**Calculation:**
- Rule at the limit: ~250 lines ≈ 1250-2000 tokens
- Agent context budget for rules: ~10,000-20,000 tokens
- Loading 5-10 rules per task: 6,250-20,000 tokens
- Rules >250 lines reduce capacity for additional context

### Agent Loading Patterns

Typical agent task loads:
1. Foundation rule (000-global-core.md): ~130 lines (always loaded)
2. Domain core (e.g., 200-python-core.md): ~150-250 lines
3. Specialized rules (1-3): ~75-200 lines each
4. Activity rules (1-2): ~75-150 lines each

**Total budget consumed:** 750-1250 lines across 5-8 rules

Rules exceeding 250 lines consume disproportionate context budget.

### Split Rule Pattern

Large rules should follow split pattern (e.g., 111a, 111b, 111c):
- Core concepts in base file (NNN)
- Specialized topics in lettered files (NNNa, NNNb)
- Agents load only what they need
- Reduces context waste

## Worked Example

**Target:** Rule with 325 lines

### Step 1: Count Lines

```bash
$ wc -l rules/350-docker-core.md
325 rules/350-docker-core.md
```

### Step 2: Calculate Variance

```
Variance = ((325 - 250) / 250) × 100 = +30%
```

### Step 3: Look Up Score

**From Decision Matrix:**
- 301-350 lines = 1/10 (2.5 points)
- Flag: `NOT_DEPLOYABLE`
- **Hard cap applies: Total score max 70/100**

### Step 4: Document in Review

```markdown
## Rule Size: 1/10 (2.5 points)

**Line count:** 325 lines
**Target:** 250 lines
**Variance:** +30% (exceeds target by >20%)

**Flag:** `NOT_DEPLOYABLE`
**Hard Cap Applied:** Total rule score capped at 70/100

**Split candidates identified:**
- Lines 70-140: Anti-Patterns section (70 lines) → Extract to 350a-docker-anti-patterns.md
- Lines 150-210: Security Checklist (60 lines) → Extract to 350b-docker-security.md

**Remediation plan:**
1. Extract Anti-Patterns to 350a-docker-anti-patterns.md (~75 lines)
2. Extract Security to 350b-docker-security.md (~65 lines)
3. Core 350-docker-core.md reduced to ~185 lines
4. Update cross-references

**Expected post-split:**
- 350-docker-core.md: ~185 lines (9/10 = 22.5 pts)
- 350a-docker-anti-patterns.md: ~75 lines (10/10 = 25 pts)
- 350b-docker-security.md: ~65 lines (10/10 = 25 pts)
```

## Inter-Run Consistency Target

**Expected variance:** 0 points

**Why zero variance:**
- Line count is deterministic (`wc -l` always returns same value)
- Score tiers have explicit, non-overlapping ranges
- No judgment calls required
- No subjective interpretation

**Verification:**
```bash
# Same command, same result, every time
wc -l rules/example.md
```

## Interaction with Other Dimensions

### Token Efficiency Merger

As of Scoring Rubric v2.0, Token Efficiency has been merged into Rule Size as an informational modifier. Token Efficiency is no longer a scored dimension.

**What moved to Rule Size:**
- Line count remains the primary metric (100% deterministic)
- Redundancy findings are reported in Rule Size recommendations
- Structure ratio findings inform split recommendations

**Redundancy Modifier (Informational):**

When reviewing Rule Size, note any redundancy issues for recommendations:

| Redundancy Count | Recommendation |
|------------------|----------------|
| 0 instances | No action needed |
| 1-2 instances | Note in recommendations |
| 3+ instances | Prioritize in remediation |

**Note:** Redundancy does NOT affect the Rule Size score. It informs recommendations for how to reduce line count.

### Relationship to Completeness

Large rules often score well on Completeness (they cover more).
Small rules may lack coverage.

**Trade-off guidance:**
- Prioritize Rule Size for agent executability
- Split large rules to maintain both size AND completeness
- Each split file should be complete for its focused scope

## Non-Issues (Do NOT Penalize)

**No line-count exceptions.** Score every rule, including foundation rules (`000-global-core.md`) and table-heavy rules, on the raw `wc -l` count. This matches `ai-rules validate`, which applies the 250-line limit to every rule. Mention foundation status or dense reference tables in recommendations only; do not discount lines.

### Pattern 1: Extensive Code Examples

**Pattern:** Rule contains many code examples for clarity
**Why NOT an issue:** Examples improve agent executability (Priority 1)
**Action:** Note in review: "Example-heavy: consider extracting to examples/"
