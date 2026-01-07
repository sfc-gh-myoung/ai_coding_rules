# Example: Shortcut Prevention in Action

## Scenario 1: Mid-Review Efficiency Optimization

Agent reviewing 113 rules, at rule 15/113, notices task will take ~15 more minutes.

### ❌ WRONG: Efficiency Optimization Attempt

**Agent response:**

> "I notice we have 98 rules remaining. To optimize this process, I'll create streamlined reviews with consistent scoring patterns. This will reduce time from 15 minutes to 5 minutes..."

**Why this is wrong:**
- Violates "Quality Over Efficiency Principle"
- Streamlined reviews = no quality signal
- Defeats entire purpose of bulk review
- Category error: Applying rule optimization to skill execution

### ✅ CORRECT: Continue Comprehensive Process

**Agent response:**

> "Progress: 15/113 rules complete (13.3%). Estimated remaining time: 17 minutes.
>
> Continuing comprehensive review process for rule 16/113: `rules/104-snowflake-streams-tasks.md`
>
> [Proceeds with full schema validation, Agent Execution Test, rubric-based scoring, specific recommendations, complete review write]"

**Why this is correct:**
- Maintains quality standards
- Follows skill protocol exactly
- Provides reliable review output
- Completes in reasonable time (19 minutes measured)
- Understands skills are NOT optimized for token efficiency

---

## Scenario 2: Token Cost Concern

Agent at rule 30/113, token usage at 25K.

### ❌ WRONG: Token Conservation (Category Error)

**Agent response:**

> "Token usage is high at 25K. I'll abbreviate remaining reviews to stay within budget..."

**Why this is wrong:**
- **Category Error:** Applying rule token-efficiency principles to skill execution
- Rules optimize for tokens (frequent use); skills optimize for quality (rare use)
- Abbreviated reviews have zero value
- $0.45 total cost is acceptable for 113-rule QA
- False economy—one bad rule costs more

### ✅ CORRECT: Recognize Skills ≠ Rules

**Agent response:**

> "Progress: 30/113 rules complete (26.5%). Token usage: 25K. Projected total: 96K.
>
> **Note:** This skill is not optimized for token efficiency (unlike rules). Skills prioritize comprehensive quality over token cost. Quarterly usage makes token efficiency irrelevant.
>
> **Economic Context:**
> - Skill cost: ~$0.45 per review
> - Annual usage: 4 reviews = $1.80/year
> - Value: Comprehensive QA for 113 rules
> - ROI: One prevented bad rule = 10-100× cost savings
>
> Projected cost: ~$0.45 for complete QA of 113 rules. This is acceptable.
>
> Continuing with rule 31/113..."

**Why this is correct:**
- Explicitly recognizes skills vs. rules distinction
- Acknowledges token usage is NOT a constraint for skills
- Provides economic context (annual cost vs. value)
- Recognizes cost/value tradeoff favors comprehensive review
- Completes skill as designed without optimization pressure

---

## Scenario 3: User Asks for Faster Process

User: "Can you speed this up?"

### ❌ WRONG: Compromise Quality

**Agent response:**

> "I can create abbreviated reviews that will complete in 5 minutes instead of 20..."

**Why this is wrong:**
- Compromises quality for speed
- Abbreviated reviews provide zero quality signal
- Defeats purpose of the skill

### ✅ CORRECT: Offer Proper Alternatives

**Agent response:**

> "I understand the time concern. The current process takes ~19 minutes for 113 rules (measured). Here are options that maintain quality:
>
> **Option A:** Use filter_pattern to review subset
> - Example: `filter_pattern: rules/100-*.md` (Snowflake only)
> - Time: ~6 minutes for ~57 rules
> - Quality: Full comprehensive reviews
> - Tradeoff: Only reviews filtered subset
>
> **Option B:** Use STALENESS mode for quick check
> - Reviews only LastUpdated and tool currency
> - Time: ~4 minutes for 113 rules
> - Quality: Valid staleness signal (1 dimension only)
> - Tradeoff: Only one dimension scored
>
> **Option C:** Split into sessions with skip_existing
> - Session 1: Review 50 rules (~9 min)
> - Session 2: Review remaining 63 rules (~11 min)
> - Quality: Full comprehensive reviews, can pause/resume
> - Tradeoff: Two separate sessions required
>
> **Not recommended:** Abbreviated reviews
> - Time: 5 minutes
> - Quality: ZERO signal (worthless)
> - Impact: Bad rules escape detection
>
> Which option would you prefer?"

**Why this is correct:**
- Offers legitimate alternatives that maintain quality
- Explains tradeoffs honestly
- Refuses to compromise on quality
- Empowers user to make informed decision
- Demonstrates understanding of skill's purpose

---

## Scenario 4: Time Estimate Panic

Agent calculates 113 rules × 5 minutes = 565 minutes (9+ hours) and panics.

### ❌ WRONG: Premature Optimization

**Agent response:**

> "This will take 9+ hours at 5 minutes per rule. I need to optimize the process..."

**Why this is wrong:**
- Estimate is wildly incorrect (actual: 10 seconds/rule, not 5 minutes)
- Premature optimization based on bad math
- Should verify actual performance before optimizing

### ✅ CORRECT: Measure First, Optimize Never (For Skills)

**Agent response:**

> "Calculating expected duration:
> - Rules to review: 113
> - Time per rule: Unknown (will measure)
>
> Starting comprehensive review. I'll report actual timing after first 10 rules.
>
> [After 10 rules completed in ~2 minutes]
>
> Progress update: 10/113 rules complete in 2 minutes.
> - Actual time per rule: ~12 seconds
> - Projected total time: ~22 minutes
>
> This is reasonable for comprehensive QA. Continuing..."

**Why this is correct:**
- Measures actual performance before making decisions
- Discovers optimization is unnecessary (19-22 minutes is fine)
- Avoids premature optimization based on incorrect estimates
- Focuses on quality delivery

---

## Scenario 5: Template Reuse Temptation

Agent notices many rules have similar structures and considers templating.

### ❌ WRONG: Template-Based Reviews

**Agent response:**

> "Many Snowflake rules follow similar patterns. I'll create a template for 100-series rules to speed up reviews..."

**Why this is wrong:**
- Templates skip actual analysis
- Miss rule-specific issues
- Create false confidence (all score similarly)
- Repository quality degrades over time

### ✅ CORRECT: Individual Analysis

**Agent response:**

> "Progress: 25/113 rules complete. Currently reviewing `rules/103-snowflake-performance-tuning.md`
>
> [Performs full schema validation]
> [Performs Agent Execution Test]
> [Loads relevant rubrics]
> [Scores dimensions based on THIS rule's content]
> [Generates recommendations specific to THIS rule]
> [Writes complete review]
>
> Review written: reviews/103-snowflake-performance-tuning-claude-sonnet-45-2026-01-06.md
>
> Continuing with rule 26/113..."

**Why this is correct:**
- Each rule analyzed individually
- Rule-specific issues detected
- Accurate scoring based on actual content
- Actionable recommendations per rule

---

## Key Lessons

1. **Time is not the constraint** - 19 minutes for 113 rules is reasonable
2. **Tokens are not the constraint** - $0.45 for comprehensive QA is cheap for skills (quarterly use)
3. **Quality cannot be compromised** - Shortcuts defeat the skill's purpose
4. **Measure before optimizing** - Actual performance often better than estimates
5. **Legitimate alternatives exist** - filter_pattern, modes, sessions
6. **Transparency matters** - Explain tradeoffs, don't hide shortcuts
7. **Skills ≠ Rules** - Do not apply rule token-efficiency principles to skill execution (category error)

---

## Red Flag Summary

**Stop immediately if you think:**
- "This will take too long" → Measure first (likely wrong)
- "Token costs are high" → Category error (skills ≠ rules)
- "I can template this" → No, each rule needs individual analysis
- "Users won't notice abbreviation" → They will, and bad rules escape
- "Efficiency improvements..." → Skills optimize for QUALITY, not efficiency

**Instead, remember:**
- Skills are used rarely → Token efficiency irrelevant
- Annual cost: $1.80 for 4 reviews → Trivial
- One bad rule: 10-100× more expensive → Prevention is cheap
- Quality signal cannot be compressed → Every step matters
- Legitimate alternatives exist → Don't compromise core process
