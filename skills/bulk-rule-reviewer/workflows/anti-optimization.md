# Anti-Optimization Protocol

## Purpose

Prevent agents from applying rule-style token-efficiency optimizations to skill
execution. This skill prioritizes ACCURACY over efficiency.

## Foundational Principle

Skills are used occasionally (quarterly/monthly) for quality assurance. Token
efficiency is NOT a design goal for skills. Do NOT apply rule optimization
principles here.

| Dimension | Rules | Skills |
|-----------|-------|--------|
| Usage frequency | 100s–1000s/month | 4–12/year |
| Token efficiency | Critical | Irrelevant |
| Optimization goal | Minimize tokens | Maximize quality |
| Acceptable size | 5K–8K tokens | Whatever it takes |

## Forbidden Optimization Thoughts

- "This will take too long"
- "I can save time by..."
- "Token costs are high"
- "The user won't notice if I..."
- "I should ask about time constraints"
- "Let me create a faster approach"
- "Let me batch these rules together"
- "I can validate multiple rules at once"
- "Let me process rules 4-8 efficiently"
- "I'll read several rules before reviewing"

## Required Mindset

- "I will complete the full process for each rule"
- "Quality signals are worth the cost"
- "The user authorized ACT knowing the scope"
- "Previous runs completed successfully at this pace"

## Important Distinction

- **Optimizing the SKILL EXECUTION (forbidden)** — "I can review faster by
  skipping rubric consultation", "I'll batch these reviews to save time",
  "Let me create a template"
- **Evaluating RULE OPTIMIZATION (required)** — Scoring Token Efficiency
  dimension, identifying verbose patterns in rules, recommending rule
  consolidation

The user has already considered timing and scope. Proceed with the work.

## One Rule At A Time (MANDATORY)

NEVER batch multiple rules. Each rule MUST be processed individually:

1. Read ONE rule file completely
2. Run schema validator for THAT rule
3. Apply ALL 6 scored rubrics to THAT rule
4. Write review file for THAT rule
5. THEN move to next rule

### Forbidden patterns

- `for f in rules/*.md; do` (batch shell loops for validation)
- Reading multiple rules before writing any reviews
- "Let me process rules 4-8 together"
- Creating templates to speed up reviews
- Parallelizing any review steps
- Combining schema validation for multiple files
- "Efficient batch processing"

### Why batching fails

- Context overflow loses rubric details mid-batch
- Template-based reviews miss rule-specific issues
- Shortcut thinking violates rubric requirements
- Evidence requirements (15+ line refs) impossible without focused reading

### Canary Check - Batching Detection

Before EACH rule review, verify:

- [ ] I am reviewing exactly ONE rule
- [ ] I have not combined multiple rules in this tool call
- [ ] My previous tool call was for ONE rule only
- [ ] I am NOT creating a "faster approach"

If ANY check fails: STOP, re-read this file, resume with ONE rule.

## Required Progress Output

After EACH rule review, output exactly:

```
[N/<total_rules>] Complete: {filename} → {score}/100
```

This output MUST appear after writing EACH review file. If you see yourself
planning to output multiple completion messages at once, you are batching —
STOP immediately.

## Why This Process Cannot Be Shortened

This skill is designed for **quality assurance**, not efficiency.
Short-circuiting defeats its purpose.

Agents frequently attempt to "optimize" by creating template-based reviews
without analysis, asking about time constraints mid-execution, proposing
"streamlined" approaches, calculating projected completion times, or
expressing concern about token costs. **ALL OF THESE ARE FORBIDDEN.**

Correct behavior:

- Execute the full workflow for each rule
- Do NOT calculate or mention projected completion times
- Do NOT ask about time constraints
- Do NOT propose "faster" alternatives
- Trust that the user understands the scope

Detection test: If you're thinking "Should I ask the user about..." the
answer is NO. The user authorized ACT. Proceed with the work.

### Common Efficiency Instincts (ALL WRONG)

1. **"I can create streamlined reviews to save time"** — Streamlined reviews
   miss critical issues, produce false confidence, lead to undetected
   blocking issues.
2. **"Template-based reviews are consistent"** — Templates skip actual
   analysis, miss rule-specific issues, cause score drift.
3. **"Batch processing multiple rules is efficient"** — Aggregation loses
   per-rule detail, makes actionable recommendations impossible.
4. **"This will take too long"** — Comprehensive review completes
   efficiently with measured execution.
5. **"Token costs are too high"** — ~$0.45 for a repository-wide quality
   audit is cheap. One bad rule costs more.

### When Shortcuts Are Acceptable

**NEVER.** If time/tokens are constraints, use these instead:

- Set `filter_pattern` to review subset (e.g., `rules/100-*.md`)
- Set `review_mode: STALENESS` for quick check (1 dimension)
- Split into multiple sessions with `skip_existing: true`

DO NOT create a "fast mode" that compromises quality.

## Shortcut Detection and Prevention

During execution, HALT immediately if agent exhibits:

### Red Flags (Stop and Self-Correct)

1. **Suggesting efficiency improvements mid-review** → STOP. Re-read this
   file. Return to comprehensive process.
2. **Creating reviews <2500 bytes (FULL mode)** → DELETE abbreviated review.
   Re-do with full analysis.
3. **Not loading rubrics before scoring** → HALT. Load rubric. Re-score.
4. **Batch processing mentions** → STOP. Review one rule at a time.
5. **Skipping schema validation** → HALT. Run `ai-rules validate`.
6. **Using examples/ as templates** → DELETE review. Re-analyze actual rule.
7. **Time/token concerns mentioned** → STOP. Re-read this file.
8. **Applying rule optimization to skills** → STOP. Category error.

### Halt Immediately If You

1. Generate review text without reading the actual rule file
2. Use the same review text for multiple rules
3. Create reviews in a loop without individual analysis
4. Think "I'll create a template and fill in details"
5. Calculate "time remaining" or "rules per minute"
6. Consider asking the user about scope/timing

### Self-Correction Trigger Words

If you think or write any of these, you're taking a shortcut:

- "To save time..."
- "For efficiency..."
- "Given the large number..."
- "This would take approximately..."
- "Should I continue with..."
- "Would you prefer..."
- "Let me create a streamlined..."

### Immediate Action

1. DELETE any work done with shortcuts
2. Re-read this file
3. Resume comprehensive process
4. Do NOT notify user of the self-correction (just fix it)

### Self-Correction Protocol

If shortcut detected:

1. ACKNOWLEDGE: "I was attempting [shortcut]. This violates skill protocol."
2. DELETE: Remove any abbreviated/templated reviews created
3. RESET: Re-read bulk-rule-reviewer/SKILL.md and rule-reviewer/SKILL.md
4. RESUME: Return to comprehensive process at last valid checkpoint
5. COMMIT: "I will complete comprehensive reviews without shortcuts."

## Execution Acknowledgment

Before proceeding, agent must confirm:

- [ ] Will follow rule-reviewer workflow for each rule (complete process)
- [ ] Will load and consult rubrics for dimension scoring
- [ ] Will run schema validation for each rule
- [ ] Will perform Agent Execution Test for each rule
- [ ] Will NOT optimize for time/tokens at expense of quality
- [ ] Will NOT calculate projected completion times
- [ ] Will NOT ask about time constraints mid-execution
- [ ] Will NOT create template-based reviews
- [ ] Will NOT propose "faster" alternatives
- [ ] Will use resume capability (skip_existing) if interrupted

If cannot commit to ALL items: STOP and report error.

## Progress Display Protocol

CRITICAL: Minimize console output during execution. Canary checks, dimension
scoring, and evidence gathering are INTERNAL PROCESSING. Do NOT display
intermediate analysis to the user.

Starting/Complete examples:

- `[45/<total_rules>] Starting: 310-zsh-scripting-core.md`
- `[45/<total_rules>] Complete: 310-zsh-scripting-core.md → 95.5/100`
- Every 10 rules: brief aggregate summary
  (e.g., "Progress: 50/<total_rules>, avg 87.2")

DO NOT DISPLAY (internal processing only):

- Pre-Rule Canary check questions/answers
- Post-Read Canary verification details
- Agent Execution Test blocking issue scans
- Dimension score calculations and breakdowns
- Evidence citations during processing
- Rubric consultation notes
- "3 unique things" verification output

The review FILE contains all evidence and analysis. Console output should
show only progress.

## Verification Requirements

Each review must contain:

- Executive Summary with scores table (all 6 dimensions for FULL mode)
- Schema Validation Results (from `ai-rules validate` output)
- Agent Executability Verdict (based on Agent Execution Test)
- Dimension Analysis sections (detailed scoring rationale)
- Critical Issues list (specific line numbers)
- Recommendations (prioritized with expected score improvements)
- Post-Review Checklist
- Conclusion

### Evidence-Based Verification (MANDATORY)

Every review MUST include evidence proving the file was actually read:

| Requirement | Minimum | Example |
|-------------|---------|---------|
| Line references | ≥15 distinct | "line 47", "lines 120-135" |
| Direct quotes | ≥3 with line numbers | `Line 156: "..."` |
| Metadata citation | TokenBudget value | "TokenBudget ~6550 declared at line 12" |
| Pattern names | ≥2 exact names | "Anti-Pattern 2: ..." |
| Code references | ≥1 function/class name | "The `helper()` at lines 330-350" |

### Zero-Recommendation Rule

Reviews with "No recommendations" or "None required" MUST justify with:

1. At least 3 specific attempts to find issues (with line references)
2. Explicit statement: "Searched for [X, Y, Z] issues at lines [A, B, C] -
   none found"

If a review contains zero recommendations AND zero line references =
AUTOMATIC REJECTION.

### Quality Gate

- Review file size 3000–8000 bytes (typical for FULL mode)
- < 2000 bytes = too abbreviated (VIOLATION)
- All required sections present (VIOLATION if missing)
- ≥15 line references present (VIOLATION if missing)
- ≥3 direct quotes with line numbers (VIOLATION if missing)

Violation consequences: invalid reviews rejected from summary; execution
halted with protocol violation error; user notified of shortcut attempt.
