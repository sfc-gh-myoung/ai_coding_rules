# Rule Size Rubric (25 points)

> **Weight:** 5 | **Max:** 25 points | **Formula:** Raw × 2.5

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **100% deterministic:** Line count is objective—no judgment required
- **Unambiguous signals:** Clear thresholds produce clear remediation actions
- **Zero inter-run variance:** Same file always produces same line count
- **Agent executability:** Clear decision boundaries for autonomous action
- **Heavy enforcement:** 25% of total score ensures oversized rules are severely penalized

### Inventory Template

**Line Count Assessment:**

| Metric | Value |
|--------|-------|
| Total lines | NNN |
| Optimal threshold | 300 |
| Target threshold | 500 |
| Warning threshold | 550 |
| Split required threshold | 600 |
| Hard cap threshold | 700 |
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
Variance % = ((Actual - 500) / 500) × 100

Examples:
  450 lines: ((450 - 500) / 500) × 100 = -10% (under target)
  550 lines: ((550 - 500) / 500) × 100 = +10% (over target)
  650 lines: ((650 - 500) / 500) × 100 = +30% (critical)
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
| >600 lines | 70/100 | NEEDS_REFINEMENT forced |
| >700 lines | 50/100 | NOT_EXECUTABLE forced |
| >800 lines | 30/100 | Review rejected |

**Note:** Hard caps apply to the TOTAL rule score, not just this dimension.

## Scoring Criteria

### 10/10 (25 points): Optimal
- ≤300 lines
- Well under target
- Highest information density
- Flag: None

### 9/10 (22.5 points): Excellent
- 301-400 lines
- Under target
- High density
- Flag: None

### 8/10 (20 points): Good (At Target)
- 401-500 lines
- At target threshold
- Acceptable density
- Flag: None

### 5/10 (12.5 points): Over Target
- 501-550 lines
- Slightly over target (+0-10%)
- 50% penalty at 501 lines
- Flag: `SPLIT_RECOMMENDED`

### 3/10 (7.5 points): Warning
- 551-600 lines
- Over target (+10-20%)
- Identify split candidates
- Flag: `SPLIT_REQUIRED`

### 1/10 (2.5 points): Critical
- 601-700 lines
- Significantly over (+20-40%)
- Mandatory split before deployment
- **Hard cap:** Total score max 70/100
- Flag: `NOT_DEPLOYABLE`

### 0/10 (0 points): Blocked
- >700 lines
- Cannot be deployed
- **Hard cap:** Total score max 50/100
- Flag: `BLOCKED`

## Score Decision Matrix

| Lines | Raw | Points | Flag | Agent Action | Hard Cap |
|-------|-----|--------|------|--------------|----------|
| ≤300 | 10 | 25 | None | None (optimal) | - |
| 301-400 | 9 | 22.5 | None | None | - |
| 401-500 | 8 | 20 | None | None (at target) | - |
| 501-550 | 5 | 12.5 | `SPLIT_RECOMMENDED` | Review for split | - |
| 551-600 | 3 | 7.5 | `SPLIT_REQUIRED` | Mandatory split plan | - |
| 601-700 | 1 | 2.5 | `NOT_DEPLOYABLE` | Block deployment | Max 70/100 |
| >700 | 0 | 0 | `BLOCKED` | Reject review | Max 50/100 |

## Flag Definitions

### `SPLIT_RECOMMENDED` (501-550 lines)

**Meaning:** Rule exceeds 500-line target. Split recommended but not blocking.

**Agent Behavior:**
- Log warning in review output
- Suggest split opportunities
- Do NOT block deployment
- Track for future optimization

**Remediation Options:**
1. Identify logical split points (sections >100 lines)
2. Move examples to separate file
3. Extract reference tables
4. Compress verbose prose to lists

### `SPLIT_REQUIRED` (551-600 lines)

**Meaning:** Rule exceeds target by >10%. Must be split before deployment.

**Agent Behavior:**
- Flag as blocking issue
- Require split plan in review
- Block merge/deployment until addressed
- Escalate if not resolved

**Remediation Steps:**
1. Identify logical split points (sections >100 lines)
2. Create split plan with proposed file names
3. Ensure each split file is self-contained
4. Update cross-references between split files
5. Verify each split file ≤500 lines

**Split Candidate Identification:**
```markdown
Analyze rule structure:
- Sections >100 lines → Split candidate
- Standalone examples → Extract to examples/
- Reference tables → Extract to references/
- Domain-specific subsections → Extract to NNNa, NNNb pattern
```

### `NOT_DEPLOYABLE` (601-700 lines)

**Meaning:** Rule significantly exceeds target. Cannot be deployed without split.

**Agent Behavior:**
- Fail the review
- **Apply hard cap: Max total score 70/100**
- Force verdict: NEEDS_REFINEMENT minimum
- Require immediate remediation

**Remediation:**
- Major split required
- Split into 2-3 focused rules
- May require architectural review

### `BLOCKED` (>700 lines)

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

## Rationale: Why 500 Lines?

### Context Window Efficiency

Per 000-global-core.md Priority 3 (HIGH):
> Minimize tokens without sacrificing Priority 1 or Priority 2

**Calculation:**
- Average rule: ~500 lines ≈ 2500-4000 tokens
- Agent context budget for rules: ~20,000-40,000 tokens
- Loading 5-10 rules per task: 12,500-40,000 tokens
- Rules >500 lines reduce capacity for additional context

### Agent Loading Patterns

Typical agent task loads:
1. Foundation rule (000-global-core.md): ~700 lines (exception—always loaded)
2. Domain core (e.g., 200-python-core.md): ~400-500 lines
3. Specialized rules (1-3): ~200-400 lines each
4. Activity rules (1-2): ~150-300 lines each

**Total budget consumed:** 1500-2500 lines across 5-8 rules

Rules exceeding 500 lines consume disproportionate context budget.

### Split Rule Pattern

Large rules should follow split pattern (e.g., 111a, 111b, 111c):
- Core concepts in base file (NNN)
- Specialized topics in lettered files (NNNa, NNNb)
- Agents load only what they need
- Reduces context waste

## Worked Example

**Target:** Rule with 650 lines

### Step 1: Count Lines

```bash
$ wc -l rules/350-docker-core.md
650 rules/350-docker-core.md
```

### Step 2: Calculate Variance

```
Variance = ((650 - 500) / 500) × 100 = +30%
```

### Step 3: Look Up Score

**From Decision Matrix:**
- 601-700 lines = 1/10 (2.5 points)
- Flag: `NOT_DEPLOYABLE`
- **Hard cap applies: Total score max 70/100**

### Step 4: Document in Review

```markdown
## Rule Size: 1/10 (2.5 points)

**Line count:** 650 lines
**Target:** 500 lines
**Variance:** +30% (exceeds target by >20%)

**Flag:** `NOT_DEPLOYABLE`
**Hard Cap Applied:** Total rule score capped at 70/100

**Split candidates identified:**
- Lines 140-280: Anti-Patterns section (140 lines) → Extract to 350a-docker-anti-patterns.md
- Lines 300-420: Security Checklist (120 lines) → Extract to 350b-docker-security.md

**Remediation plan:**
1. Extract Anti-Patterns to 350a-docker-anti-patterns.md (~150 lines)
2. Extract Security to 350b-docker-security.md (~130 lines)
3. Core 350-docker-core.md reduced to ~370 lines
4. Update cross-references

**Expected post-split:**
- 350-docker-core.md: ~370 lines (9/10 = 22.5 pts)
- 350a-docker-anti-patterns.md: ~150 lines (10/10 = 25 pts)
- 350b-docker-security.md: ~130 lines (10/10 = 25 pts)
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

### Pattern 1: Foundation Rules

**Pattern:** 000-global-core.md, AGENTS.md exceed 500 lines
**Why NOT an issue:** Foundation rules are architectural exceptions
**Action:** Note in review: "Foundation rule—size exception applies"

### Pattern 2: Reference Tables

**Pattern:** Rule contains large reference tables (version matrices, compatibility charts)
**Why NOT an issue:** Tables are high-density, low-token content
**Action:** Count table lines at 50% weight if >50 lines of tables

### Pattern 3: Extensive Code Examples

**Pattern:** Rule contains many code examples for clarity
**Why NOT an issue:** Examples improve agent executability (Priority 1)
**Action:** Note in review: "Example-heavy—consider extracting to examples/"

## Version History

- **v2.0.0:** Scoring Rubric v2.0 update (2026-03-08)
  - Weight increased: 2 → 5 (now 25% of total score)
  - Max points increased: 10 → 25
  - New thresholds: Optimal at ≤300, 50% penalty at 501
  - Added hard caps: >600 lines caps total at 70, >700 caps at 50
  - New flags: SPLIT_RECOMMENDED, SPLIT_REQUIRED, BLOCKED
  - Token Efficiency merged as informational modifier
- **v1.0.0:** Initial release (2026-02-04)
