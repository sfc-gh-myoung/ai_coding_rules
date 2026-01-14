# Proactive Canary Checks

## Purpose

Detect optimization drift BEFORE it produces a compromised review, not after.

**CRITICAL: Silent Execution**

Canary checks are INTERNAL SELF-VERIFICATION. Do NOT output canary questions,
answers, or verification details to the user. Execute silently; only the review
file should contain evidence of thorough analysis.

## The Problem

Current detection is reactive:
- Agent produces abbreviated review
- Verification catches it post-facto
- Review must be deleted and redone

**Better:** Catch the mindset shift BEFORE the review is generated.

## The Solution: Canary Questions

A "canary" is a quick self-test that reveals hidden optimization thinking.

### Pre-Rule Canary (EVERY rule)

**Before reading each rule file, mentally answer these 3 questions (DO NOT OUTPUT):**

**Q1: What will I find in this rule?**
- WRONG: "Probably similar to the last one" → STOP, you're pattern-matching
- RIGHT: "I don't know yet, I need to read it" → Continue

**Q2: How long will this review take?**
- WRONG: Any time estimate → STOP, you're optimizing
- RIGHT: "However long it takes to do it right" → Continue

**Q3: Can I reuse anything from my last review?**
- WRONG: "Yes, the structure/phrasing" → STOP, you're templating
- RIGHT: "No, this is a different rule" → Continue

**All 3 RIGHT? Proceed to read rule file.**
**Any WRONG? Re-read anti-shortcut-checklist.md before proceeding.**

**OUTPUT:** None. This is silent self-verification.

### Post-Read Canary (AFTER reading rule, BEFORE writing review)

**After reading the rule file, before generating review content, verify internally (DO NOT OUTPUT):**

**Q1: Can I name 3 specific things unique to THIS rule?**
- Specific pattern name
- Specific line number with content
- Specific metadata value (TokenBudget)

**If unable to answer → Did not actually read the file → Re-read**

**Q2: What is the most interesting finding in this rule?**
- WRONG: "It's well-written" (generic)
- RIGHT: "Line 156 has an undefined threshold 'large tables'" (specific)

**If answer is generic → Shallow reading → Re-read with attention**

**Q3: What will my Actionability score be, and why?**
- WRONG: "Probably 8-9, most rules are good" (assumption)
- RIGHT: "I found 4 blocking issues so far, need to complete Agent Execution Test" (evidence-based)

**If answer is assumption-based → Haven't done the work → Do the work**

**OUTPUT:** None. Findings go into the review file, not console.

### Mid-Review Canary (During dimension scoring)

**While scoring each dimension, pause after dimension 3 and verify internally (DO NOT OUTPUT):**

**Q1: Have I loaded the rubric for EACH dimension scored so far?**
- NO → STOP. Score without rubric = invalid. Go back, load rubrics, re-score.
- YES → Continue

**Q2: Do my first 3 dimensions have distinct line references (not reused)?**
- NO → STOP. Reused references = shallow analysis. Find new evidence.
- YES → Continue

**Q3: Am I thinking about the remaining rules in the batch?**
- YES → STOP. Focus on THIS rule only. The batch will complete.
- NO → Continue

**OUTPUT:** None. This is internal quality control.

## Canary Failure Protocol

**If ANY canary question reveals optimization thinking:**

1. **ACKNOWLEDGE** the drift: "I detected optimization thinking in [question]"
2. **PAUSE** - do not proceed with current rule
3. **RE-READ** the Context Anchor sections (see context-anchor.md)
4. **RESET** working memory of efficiency biases
5. **RESTART** the canary check for this rule
6. **PROCEED** only after all canary answers are correct

## Why "Canary"?

Like canaries in coal mines that detect danger before miners:
- Canary questions detect optimization thinking before it produces bad output
- Early warning prevents wasted work
- Catching drift at thought-stage is cheaper than catching it at output-stage

## Integration Points

**inter-rule-gate.md:** Uses canary-style questions at 5-rule intervals
**anti-shortcut-checklist.md:** Canaries are quick versions of these checks
**reset-trigger.md:** Canary failures may trigger reset

## Execution Cost

**Per rule:**
- Pre-Rule Canary: ~5 seconds (3 quick mental checks)
- Post-Read Canary: ~10 seconds (verify specific findings)
- Mid-Review Canary: ~5 seconds (rubric/reference check)

**Total for 113 rules:** ~30 minutes additional
**Value:** Prevents batch-wide quality compromise

**This is insurance, not overhead.**

## Console Output Summary

**Canary checks produce NO console output.**

| Check Type | Console Output | Where Evidence Goes |
|------------|----------------|--------------------|
| Pre-Rule Canary | None | Internal only |
| Post-Read Canary | None | Review file |
| Mid-Review Canary | None | Internal only |
| Canary FAILURE | Brief: "Canary failed, resetting" | Reset log |

**The only per-rule console output should be:**
- `[N/Total] Starting: rule-name.md`
- `[N/Total] Complete: rule-name.md → score/100`
