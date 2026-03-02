# Rule Size Rubric (10 points)

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **100% deterministic:** Line count is objective—no judgment required
- **Unambiguous signals:** Clear thresholds produce clear remediation actions
- **Zero inter-run variance:** Same file always produces same line count
- **Agent executability:** Clear decision boundaries for autonomous action

### Inventory Template

**Line Count Assessment:**

| Metric | Value |
|--------|-------|
| Total lines | NNN |
| Target threshold | 500 |
| Warning threshold | 600 |
| Critical threshold | 700 |
| Variance from target | +NN% or -NN% |
| Score tier | X/10 |
| Flag | [None/OPTIMIZATION_RECOMMENDED/SPLITTING_REQUIRED/NOT_DEPLOYABLE] |

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
**Weight:** 2
**Points:** Raw × (2/2) = Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Optimal
- ≤400 lines
- Well under target
- High information density
- Flag: None

### 9/10 (9 points): Excellent
- 401-450 lines
- Under target
- Good density
- Flag: None

### 8/10 (8 points): Good
- 451-500 lines
- At target threshold
- Acceptable density
- Flag: None

### 7/10 (7 points): Acceptable
- 501-550 lines
- Slightly over target (+0-10%)
- Review for consolidation opportunities
- Flag: `OPTIMIZATION_RECOMMENDED`

### 6/10 (6 points): Warning
- 551-600 lines
- Over target (+10-20%)
- Identify verbose sections
- Flag: `OPTIMIZATION_RECOMMENDED`

### 5/10 (5 points): Over Limit
- 601-650 lines
- Exceeds 20% threshold (+20-30%)
- Identify split candidates
- Flag: `SPLITTING_REQUIRED`

### 4/10 (4 points): Critical
- 651-700 lines
- Significantly over (+30-40%)
- Mandatory split before deployment
- Flag: `SPLITTING_REQUIRED`

### 3/10 (3 points): Severe
- 701-750 lines
- Severely over (+40-50%)
- Block deployment until addressed
- Flag: `SPLITTING_REQUIRED`

### 2/10 (2 points): Unacceptable
- 751-800 lines
- Unacceptably large (+50-60%)
- Immediate remediation required
- Flag: `NOT_DEPLOYABLE`

### 1/10 (1 point): Critical Failure
- 801-900 lines
- Major restructure required (+60-80%)
- Cannot be deployed
- Flag: `NOT_DEPLOYABLE`

### 0/10 (0 points): Invalid
- >900 lines
- Complete rewrite required (>80% over)
- Rule is not viable in current form
- Flag: `NOT_DEPLOYABLE`

## Score Decision Matrix

| Lines | Score | Points | Flag | Agent Action |
|-------|-------|--------|------|--------------|
| ≤400 | 10/10 | 10 | None | None required |
| 401-450 | 9/10 | 9 | None | None required |
| 451-500 | 8/10 | 8 | None | None required |
| 501-550 | 7/10 | 7 | `OPTIMIZATION_RECOMMENDED` | Review for consolidation |
| 551-600 | 6/10 | 6 | `OPTIMIZATION_RECOMMENDED` | Identify verbose sections |
| 601-650 | 5/10 | 5 | `SPLITTING_REQUIRED` | Identify split candidates |
| 651-700 | 4/10 | 4 | `SPLITTING_REQUIRED` | Mandatory split plan |
| 701-750 | 3/10 | 3 | `SPLITTING_REQUIRED` | Block deployment |
| 751-800 | 2/10 | 2 | `NOT_DEPLOYABLE` | Immediate remediation |
| 801-900 | 1/10 | 1 | `NOT_DEPLOYABLE` | Major restructure |
| >900 | 0/10 | 0 | `NOT_DEPLOYABLE` | Complete rewrite |

## Flag Definitions

### `OPTIMIZATION_RECOMMENDED` (501-600 lines)

**Meaning:** Rule exceeds target but is within acceptable tolerance.

**Agent Behavior:**
- Log warning in review output
- Suggest consolidation opportunities
- Do NOT block deployment
- Track for future optimization

**Remediation Options:**
1. Consolidate redundant sections
2. Move examples to separate file
3. Extract reference tables
4. Compress verbose prose to lists

### `SPLITTING_REQUIRED` (601-800 lines)

**Meaning:** Rule exceeds 20% threshold. Must be split before deployment.

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

### `NOT_DEPLOYABLE` (>800 lines)

**Meaning:** Rule is too large for agent context windows. Cannot be deployed.

**Agent Behavior:**
- Fail the review
- Require immediate remediation
- Do NOT allow any deployment path
- Escalate to human maintainer

**Remediation:**
- Major restructure required
- Split into 2-4 focused rules
- May require architectural review

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
- 651-700 lines = 4/10 (4 points)
- Flag: `SPLITTING_REQUIRED`

### Step 4: Document in Review

```markdown
## Rule Size: 4/10 (4 points)

**Line count:** 650 lines
**Target:** 500 lines
**Variance:** +30% (exceeds 20% threshold)

**Flag:** `SPLITTING_REQUIRED`

**Split candidates identified:**
- Lines 140-280: Anti-Patterns section (140 lines) → Extract to 350a-docker-anti-patterns.md
- Lines 300-420: Security Checklist (120 lines) → Extract to 350b-docker-security.md

**Remediation plan:**
1. Extract Anti-Patterns to 350a-docker-anti-patterns.md (~150 lines)
2. Extract Security to 350b-docker-security.md (~130 lines)
3. Core 350-docker-core.md reduced to ~370 lines
4. Update cross-references

**Expected post-split:**
- 350-docker-core.md: ~370 lines (8/10)
- 350a-docker-anti-patterns.md: ~150 lines (10/10)
- 350b-docker-security.md: ~130 lines (10/10)
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

### No Overlap with Token Efficiency

Rule Size and Token Efficiency measure different concerns:

| Dimension | Measures | Can Coexist? |
|-----------|----------|--------------|
| **Rule Size** | Physical line count | Yes |
| **Token Efficiency** | Budget accuracy, redundancy, structure | Yes |

**Example:** A 480-line rule (Rule Size: 8/10) can still have redundancy issues (Token Efficiency: 6/10). These are independent assessments.

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

- **v1.0.0:** Initial release (2026-02-04)
