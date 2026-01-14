# Anti-Shortcut Checklist

## Purpose

Prevent efficiency-driven shortcuts that compromise review quality.

## Pre-Review Self-Assessment

Before beginning bulk review, confirm:

- [ ] I understand this is a QUALITY process, not an EFFICIENCY process
- [ ] I've read "Why This Process Cannot Be Shortened" section
- [ ] I know the actual time cost: ~19 minutes for 113 rules (not 5-10 hours)
- [ ] I know the actual token cost: ~50K tokens ≈ $0.45 (acceptable for QA)
- [ ] I understand Skills ≠ Rules (different optimization goals)
- [ ] I will NOT suggest optimizations mid-process
- [ ] I will NOT apply rule token-efficiency principles to skill execution
- [ ] I will load and consult rubrics for EVERY dimension
- [ ] I will run schema_validator.py for EVERY rule
- [ ] I will perform Agent Execution Test for EVERY rule
- [ ] I will write COMPLETE reviews (3000-8000 bytes for FULL mode)
- [ ] I will show progress every 10 reviews (not continuously)

## During-Review Monitoring

Every 10 reviews, verify:

- [ ] Reviews are 3000-8000 bytes (FULL mode)
- [ ] Schema validation section present in each review
- [ ] All 6 dimensions scored (FULL mode)
- [ ] Recommendations include specific line numbers
- [ ] No batch processing of multiple rules
- [ ] No template reuse across reviews
- [ ] Rubrics loaded for each dimension scored
- [ ] No token-efficiency concerns mentioned

## Red Flags (Self-Detect)

If you notice yourself:

- Typing "to save time" or "for efficiency"
- Typing "token costs" or "token efficiency"
- Creating reviews <2500 bytes
- Scoring without loading rubrics
- Using previous review as template
- Processing multiple rules in parallel (unless max_parallel set)
- Skipping schema validation
- Providing generic recommendations
- Estimating scores instead of analyzing
- Applying rule optimization principles to skill execution
- **Writing "None required" or "No recommendations" without line-referenced justification**
- **Producing reviews with zero line references (e.g., "line 47", "lines 120-135")**
- **Writing dimension analysis without direct quotes from the rule file**
- **Multiple consecutive perfect scores (100/100) with no recommendations - statistically improbable**
- **Recommendations section under 3 sentences for ANY rule**

**IMMEDIATE ACTION:** STOP. Delete incomplete work. Re-read skill. Resume correctly.

## The "Rubber Stamp" Detection Pattern

**WARNING:** If you find yourself writing reviews that all look like:

```markdown
## Recommendations

None required. [Positive statement about the rule].
```

**YOU ARE RUBBER-STAMPING, NOT REVIEWING.**

Even excellent rules have improvement opportunities. A rigorous reviewer finds:
- Terminology that could be more consistent with related rules
- Examples that could cover one more edge case  
- Cross-references that could be more explicit
- TokenBudget that could be tighter or needs expansion
- Patterns that could benefit from future-proofing notes

**If you cannot find ANY of these after thorough analysis, you must document your search:**

```markdown
## Recommendations

After thorough analysis, no HIGH or MEDIUM severity issues identified.

**LOW severity opportunities considered but deemed unnecessary:**
- Line 45-67: Terminology "refresh schedule" vs "refresh cadence" - consistent with 104-snowflake-streams-tasks.md, no change needed
- Line 120-135: Example coverage - all common scenarios present
- TokenBudget ~6550 (actual ~6400) - within 5% tolerance

No actionable recommendations at this time.
```

**The difference:**
- ❌ "None required" (no evidence of analysis)
- ✅ "No HIGH/MEDIUM issues; LOW severity options evaluated at lines X, Y, Z" (proves thorough review)

## Category Confusion Check

**Critical:** Am I confusing rules with skills?

**RULES (what I'm reviewing):**
- Should be token-efficient (YES)
- TokenBudget metadata matters (YES)
- Loaded frequently → cost multiplier (YES)

**SKILLS (what I'm executing):**
- Should NOT optimize for tokens (NO)
- No TokenBudget metadata (CORRECT)
- Used rarely → token cost irrelevant (YES)

**If I'm thinking about token efficiency during skill execution, I'm making a category error.**

## Post-Review Validation

After all reviews complete, spot-check 5 random reviews:

- [ ] Each is 3000-8000 bytes (FULL mode)
- [ ] Schema validation output present
- [ ] Agent Execution Test results documented
- [ ] All 6 dimension scores with rationales (FULL mode)
- [ ] Recommendations have line numbers
- [ ] No copy-paste template patterns across reviews

## Success Criteria

**PASS:** All checks above satisfied, no shortcuts detected  
**FAIL:** Any shortcut detected → Review compromised → Discard and redo

## If Shortcuts Were Attempted

**Recovery Protocol:**

1. **Acknowledge:** Identify which shortcuts were attempted
2. **Understand:** Was it category confusion (applying rule principles to skills)?
3. **Discard:** Delete all abbreviated/templated reviews
4. **Learn:** Re-read "Why This Process Cannot Be Shortened"
5. **Learn:** Re-read "Skills vs. Rules - Different Optimization Goals"
6. **Reset:** Clear working memory of efficiency biases
7. **Resume:** Start fresh with comprehensive process
8. **Report:** Notify user of restart and reason

**Do NOT proceed with compromised reviews.**

## Key Reminders

**Skills Are Not Rules:**
- Rules: Optimize for tokens (frequent use)
- Skills: Optimize for quality (rare use)
- Do not confuse the two

**Economic Reality:**
- Annual cost: $1.80 for 4 comprehensive reviews
- One bad rule: 10-100× more expensive
- Token efficiency is a false economy for skills

**Time Reality:**
- Measured: 19 minutes for 113 rules
- Not: 5-10 hours (incorrect estimate)
- Already efficient, no optimization needed

**Quality Priority:**
- Every step matters for quality signal
- Shortcuts = zero value
- No tradeoff is acceptable
