# Context Anchor Protocol

## Purpose

Define skill sections that MUST remain in active context throughout execution and CANNOT be summarized or dropped.

## The Problem

During long executions, agents perform context management by:
- Summarizing older content to save tokens
- Dropping "less relevant" material
- Prioritizing recent conversation over loaded guidance

**This causes skill guidance to fade, enabling optimization drift.**

## The Solution: Context Anchors

### Definition

A **Context Anchor** is a section of skill documentation that:
1. MUST remain word-for-word in context
2. CANNOT be summarized or paraphrased
3. MUST be re-loaded if accidentally dropped
4. Takes precedence over other context during compression

### Designated Anchors for bulk-rule-reviewer

**ANCHOR 1: Anti-Optimization Protocol (SKILL.md lines 52-86)**

```markdown
### CRITICAL: Anti-Optimization Protocol

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency.

**Forbidden Optimization Thoughts:**
- "This will take too long"
- "I can save time by..."
- "Token costs are high"
- "The user won't notice if I..."
- "I should ask about time constraints"
- "Let me create a faster approach"

**Required Mindset:**
- "I will complete the full process for each rule"
- "Quality signals are worth the cost"
- "The user authorized ACT knowing the scope"
- "Previous runs completed successfully at this pace"
```

**ANCHOR 2: Skills vs Rules Distinction (SKILL.md lines 188-218)**

```markdown
**Skills vs. Rules - Different Optimization Goals:**

**Rules:** Usage Frequency: Loaded repeatedly (100s-1000s of times)
**Skills:** Usage Frequency: Used occasionally (quarterly/monthly)

**Rules:** Token Efficiency: CRITICAL
**Skills:** Token Efficiency: IRRELEVANT

**DO NOT apply rule token-efficiency principles to skill execution.**
```

**ANCHOR 3: Evidence Requirements (SKILL.md lines 309-345)**

```markdown
**CRITICAL: Evidence-Based Verification (MANDATORY)**

| Requirement | Minimum |
|-------------|---------|
| Line references | ≥15 distinct |
| Direct quotes | ≥3 with line numbers |
| Metadata citation | TokenBudget value |
| Pattern names | ≥2 exact names |
| Code references | ≥1 function/class name |
```

### Context Management Rules

**When context pressure occurs:**

1. **NEVER summarize** anchor sections
2. **Summarize these FIRST:**
   - Previous rule file contents (after review written)
   - Completed review contents
   - Conversation history
   - Error messages from resolved issues
3. **Preserve in order:**
   - Anchor sections (highest priority)
   - Current rule being reviewed
   - Relevant rubric being scored
   - Review in progress

### Structural Enforcement (PRIMARY MECHANISM)

**Behavioral guidance alone is insufficient.** LLMs summarize "older" context regardless of instructions.

**Solution: Periodic file re-reads inject fresh context that cannot be summarized:**

```python
# Every 10 rules - mandatory
if rule_number % 10 == 0:
    read_file("skills/bulk-rule-reviewer/CRITICAL_CONTEXT.md")

# On drift detection - immediate
if previous_review_size < 2500:
    read_file("skills/bulk-rule-reviewer/CRITICAL_CONTEXT.md")
    read_file("skills/bulk-rule-reviewer/SKILL.md")
```

**CRITICAL_CONTEXT.md contains (~150 tokens):**
- Evidence requirements table
- Review output format template
- Quality gate thresholds
- Score table format

**Why this works:** File reads are "new" content that gets full attention weight, unlike "old" content from conversation start that gets summarized.

### Detection of Anchor Loss

**Symptoms indicating anchors have faded:**

1. Agent starts calculating time remaining
2. Agent suggests "streamlined" approach
3. Agent asks about scope/timing
4. Reviews start getting shorter
5. Line references decrease
6. "Template" patterns appear across reviews

**If ANY symptom detected:**

1. STOP current work
2. Re-read SKILL.md completely
3. Verify anchor sections are in active context
4. Resume only after anchors confirmed active

### Self-Verification Protocol

**Every 10 rules, verify anchor presence:**

```markdown
## Anchor Verification (Rule #[N])

Can I recite from memory (without re-reading):

1. What are the 6 Forbidden Optimization Thoughts?
   - [List them]

2. Why are Skills different from Rules regarding token efficiency?
   - [Explain the distinction]

3. What are the 5 evidence requirements for a valid review?
   - [List minimum thresholds]

**If unable to answer accurately → Anchors have faded → Re-read SKILL.md**
```

### Implementation Guidance

**For agents supporting persistent context:**
- Mark anchor sections as "pinned" or "do not summarize"
- Refresh anchors every 25% of batch completion

**For agents without persistent context:**
- Re-read anchor sections explicitly every 10 rules
- Include anchor re-read in inter-rule-gate protocol

## Relationship to 000-global-core.md

The Context Window Management Protocol in 000-global-core.md defines preservation for RULES. This protocol extends that concept to SKILLS during execution.

**Priority alignment:**
1. AGENTS.md (bootstrap)
2. 000-global-core.md (foundation)
3. **Active skill anchor sections** (during skill execution)
4. Domain rules relevant to task
5. Everything else (summarizable)
