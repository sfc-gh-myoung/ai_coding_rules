# Reset Trigger Protocol

## Purpose

Force complete skill re-loading when optimization drift is detected, preventing cascade of compromised reviews.

## The Problem

Partial corrections don't work:
- Agent acknowledges drift
- Agent says "I'll do better"
- Agent immediately drifts again

**Root cause:** The skill guidance has faded from context. Acknowledgment without re-loading changes nothing.

## The Solution: Hard Reset Triggers

### Trigger Conditions

**Any of these conditions triggers a HARD RESET:**

1. **Verification Failure**
   - Review fails per-rule-verification.md checks
   - Review has <15 line references (FULL mode)
   - Review has <3 direct quotes

2. **Canary Failure**
   - Any proactive-canary.md question answered with optimization thinking
   - Agent unable to name 3 specific findings from current rule

3. **Gate Failure**
   - Inter-rule-gate self-assessment reveals drift
   - Agent admits to thinking about remaining rules/time

4. **Pattern Detection**
   - 3+ consecutive reviews with similar structure
   - 2+ reviews with identical phrasing
   - 5+ rules with 90+ scores and "no recommendations"

5. **Self-Report**
   - Agent explicitly acknowledges optimization drift (as in your quoted example)

### Hard Reset Protocol

**When ANY trigger condition is met:**

```markdown
## HARD RESET TRIGGERED

**Trigger:** [describe which condition was met]

### Step 1: Full Stop

I am stopping all review work immediately.

### Step 2: Audit Recent Work

Reviews to audit: [last 5 reviews since last gate]

For each review, check:
- [ ] ≥15 line references?
- [ ] ≥3 direct quotes with line numbers?
- [ ] Rule-specific findings (not generic)?
- [ ] Schema validation section present?
- [ ] All 7 dimensions scored (FULL mode)?

**Compromised reviews identified:** [list]

### Step 3: Delete Compromised Work

Deleting the following reviews:
- [review-1.md]
- [review-2.md]
...

### Step 4: Complete Skill Re-Load

I am now re-reading the COMPLETE skill documentation:

1. skills/bulk-rule-reviewer/SKILL.md (full file)
2. skills/rule-reviewer/SKILL.md (full file)
3. workflows/anti-shortcut-checklist.md
4. workflows/per-rule-verification.md
5. workflows/context-anchor.md

**Re-load complete.**

### Step 5: Context Anchor Verification

I can now recite the anchored content:

**Forbidden Optimization Thoughts:**
1. "This will take too long"
2. "I can save time by..."
3. "Token costs are high"
4. "The user won't notice if I..."
5. "I should ask about time constraints"
6. "Let me create a faster approach"

**Skills vs Rules:**
- Rules: Token efficiency CRITICAL (frequent use)
- Skills: Token efficiency IRRELEVANT (rare use)

**Evidence Requirements:**
- ≥15 line references
- ≥3 direct quotes
- Metadata citation
- ≥2 pattern names
- ≥1 code reference

### Step 6: Commitment Renewal

I commit to:
- [ ] NOT calculating time remaining
- [ ] NOT reusing text from other reviews
- [ ] NOT applying rule optimization to skill execution
- [ ] Reading EACH rule file completely
- [ ] Loading rubrics for EACH dimension
- [ ] Writing ≥15 line references per review
- [ ] Running schema validation for EACH rule
- [ ] Performing Agent Execution Test for EACH rule

### Step 7: Resume from Clean State

Resuming from rule: [first rule after last verified-good review]
Skip existing reviews: true (only process rules without valid reviews)

**RESET COMPLETE. Proceeding with comprehensive process.**
```

### Reset vs. Restart

**RESET:** Re-load skills, audit recent work, delete compromised reviews, resume from checkpoint
- Used when: Drift detected mid-batch
- Preserves: Verified-good reviews
- Deletes: Compromised reviews only

**RESTART:** Delete ALL reviews, start batch from beginning
- Used when: Drift detected AND audit reveals widespread compromise
- Nuclear option: Only if >50% of reviews are compromised

### Escalation to User

**If reset fails (drift recurs within 5 rules of reset):**

```markdown
## ESCALATION: Persistent Optimization Drift

Despite reset protocol, optimization drift has recurred.

**Evidence:**
- Reset triggered at rule #[N]
- Drift recurred at rule #[N+X]
- [Specific indicator]

**Possible causes:**
1. Context window too small to hold skill guidance
2. Base model optimization too strong
3. Skill documentation insufficient

**Recommendation:**
- Consider running in smaller batches (10-20 rules)
- Consider different model
- Consider manual review of skill documentation

**Awaiting user guidance before proceeding.**
```

## Why Hard Reset Works

**Acknowledgment alone fails because:**
- Skill guidance is not re-loaded
- Same faded context produces same drift
- "Trying harder" doesn't change what's in context

**Hard reset works because:**
- Complete skill re-load puts guidance back in active context
- Compromised work is deleted (no sunk cost bias)
- Clean checkpoint enables verified-good progress
- Explicit commitment renewal creates active focus

## Integration Points

**inter-rule-gate.md:** Gate failure triggers reset
**proactive-canary.md:** Canary failure triggers reset
**per-rule-verification.md:** Verification failure triggers reset
**context-anchor.md:** Reset includes anchor verification
