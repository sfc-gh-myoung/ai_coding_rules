---
name: bulk-rule-reviewer
description: Execute agent-centric reviews on all rules in rules/ directory and generate prioritized improvement report
version: 2.0.0
---

# Bulk Rule Reviewer

## Overview

Execute comprehensive agent-centric reviews on all rule files in `rules/` directory, then generate consolidated priority report. Designed for periodic quality audits, pre-release validation, and technical debt tracking.

### When to Use

- Periodic quality audits (quarterly/monthly)
- Pre-release validation before major version releases
- Technical debt tracking and prioritization
- Baseline quality measurement for improvement initiatives

### Inputs

**Required:**
- **review_date**: `YYYY-MM-DD` (default: today)
- **review_mode**: `FULL` | `FOCUSED` | `STALENESS` (default: FULL)
- **model**: Lowercase-hyphenated slug (default: `claude-sonnet-45`)

**Optional:**
- **filter_pattern**: Glob pattern (default: `rules/*.md`)
  - Examples: `rules/100-*.md` (Snowflake only), `rules/*-core.md` (cores only)
- **skip_existing**: Boolean (default: true) - Resume capability
- **max_parallel**: Integer 1-10 (default: 1) - Concurrent reviews
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Outputs

**Individual reviews:** `reviews/<rule-name>-<model>-<date>.md` (up to 113 files)

**Master summary:** `reviews/_bulk-review-<model>-<date>.md` with sections:
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <60, NOT_EXECUTABLE)
3. Priority 2: High (score 60-79, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (execution errors)
7. Top 10 Recommendations (impact × effort prioritization)
8. Next Steps (immediate/short-term/long-term)
9. Appendix: All Rules by Score (sorted table)

## Critical Execution Protocol

### MANDATORY ENFORCEMENT

This skill MUST execute the complete rule-reviewer workflow for each rule file.

### How Skills Work Together

**IMPORTANT:** Skills cannot "invoke" other skills programmatically. Skills are documentation that guides agent behavior, not callable subroutines.

**Correct pattern:**
1. Load `skills/rule-reviewer/SKILL.md` to understand the review workflow
2. Load `skills/rule-reviewer/rubrics/*.md` as needed for each dimension
3. Execute the review workflow for each rule file
4. Write review to `reviews/` following rule-reviewer's output format
5. Continue to next rule

**Why this matters:**
- The rule-reviewer skill documents a proven, high-quality review process
- Following its workflow ensures consistency and completeness
- Progressive disclosure (loading rubrics as needed) manages context efficiently
- Each rule deserves full evaluation per the documented process

### Protocol Violations (FORBIDDEN)

Agents commonly attempt these shortcuts. **ALL ARE FORBIDDEN:**

- **Skipping rubric consultation** - Scoring without reading dimension rubrics
- **Batch optimization** - Aggregating multiple rules into single review
- **Parallel shortcuts** - Running concurrently unless max_parallel set
- **Token-saving shortcuts** - Generating abbreviated reviews
- **Time-saving shortcuts** - Estimating scores without proper analysis
- **Template-based reviews** - Using examples/ as templates without actual analysis
- **Skipping schema validation** - Not running schema_validator.py

### Required Actions

- Load rule-reviewer/SKILL.md to understand complete workflow
- Load rubrics/*.md files as needed for each dimension being scored
- Run schema_validator.py for each rule
- Perform Agent Execution Test (count blocking issues)
- Score all dimensions according to review_mode (FULL/FOCUSED/STALENESS)
- Generate specific recommendations with line numbers
- Write complete review to reviews/ with proper formatting
- Follow workflows sequentially (discovery → review-execution → aggregation → summary-report)
- Show progress every 10 reviews (not more frequently)

### Execution Acknowledgment

**Before proceeding, agent must confirm:**
- [ ] Will follow rule-reviewer workflow for each rule (complete process)
- [ ] Will load and consult rubrics for dimension scoring
- [ ] Will run schema validation for each rule
- [ ] Will perform Agent Execution Test for each rule
- [ ] Will NOT optimize for time/tokens at expense of quality
- [ ] Understands process takes 5-10 hours for 113 rules
- [ ] Will use resume capability (skip_existing) if interrupted

**If cannot commit: STOP and report error.**

### Why This Process Cannot Be Shortened

**CRITICAL UNDERSTANDING:**

This skill is designed for **quality assurance**, not efficiency. Short-circuiting defeats its purpose.

**Skills vs. Rules - Different Optimization Goals:**

**Rules (e.g., 100-snowflake-core.md):**
- **Usage Frequency:** Loaded repeatedly (100s-1000s of times)
- **Token Efficiency:** CRITICAL (repeated cost multiplier)
- **Optimization Goal:** Minimize tokens while preserving quality
- **Acceptable Size:** Minimize (5K-8K tokens ideal)
- **Design Priority:** Token budget discipline

**Skills (e.g., bulk-rule-reviewer):**
- **Usage Frequency:** Used occasionally (quarterly/monthly)
- **Token Efficiency:** IRRELEVANT (one-time QA cost)
- **Optimization Goal:** Maximize quality regardless of tokens
- **Acceptable Size:** Whatever it takes (50K-100K acceptable)
- **Design Priority:** Comprehensive coverage

**Why This Matters:**

You may have noticed rule files emphasize token efficiency (TokenBudget metadata, optimization guidelines). That's correct for rules because they're loaded frequently by many agents.

**Skills are different.** They're used for specialized tasks a few times per year. Token efficiency is NOT a design goal for skills.

**Example:**
- **Rule (100-snowflake-core.md):** Loaded 100+ times per month → 5K tokens × 100 = 500K monthly cost → Token efficiency matters
- **Skill (bulk-rule-reviewer):** Used 4 times per year → 50K tokens × 4 = 200K annual cost → Token efficiency irrelevant

**For this skill specifically:**
- **Cost:** ~50K tokens × 4 reviews/year = 200K tokens/year ≈ $1.80 annually
- **Value:** Comprehensive quality assurance for 113 rules
- **ROI:** One prevented bad rule saves 10-100× the token cost

**DO NOT apply rule token-efficiency principles to skill execution.**

**Common Efficiency Instincts (ALL WRONG):**

1. **"I can create streamlined reviews to save time"**
   - **Reality:** Streamlined reviews miss critical issues
   - **Impact:** False confidence in rule quality, undetected blocking issues
   - **Consequence:** Agents fail in production with "streamlined" rules

2. **"Template-based reviews are consistent"**
   - **Reality:** Templates skip actual analysis
   - **Impact:** Miss rule-specific issues, score drift, no improvement signal
   - **Consequence:** Repository degrades over time with passing scores

3. **"Batch processing multiple rules is efficient"**
   - **Reality:** Aggregation loses per-rule detail
   - **Impact:** Cannot track individual rule improvements
   - **Consequence:** Actionable recommendations impossible

4. **"This will take too long (5-10 hours)"**
   - **Reality:** 113 rules × 10 sec = 19 minutes (actual measured time)
   - **Impact:** Premature optimization based on incorrect estimate
   - **Consequence:** Unnecessary shortcuts for non-existent problem

5. **"Token costs are too high"**
   - **Reality:** 50K tokens ≈ $0.45 for repository-wide quality audit (quarterly = $1.80/year)
   - **Impact:** False economy—one bad rule costs more in debugging
   - **Consequence:** Penny-wise, pound-foolish optimization
   - **Category Error:** Applying rule token-efficiency principles to skill execution (wrong context)

**The Real Cost:**
- Short-circuited review: 5 minutes, $0.05, ZERO quality signal
- Comprehensive review: 19 minutes, $0.45, ACTIONABLE improvements for 113 rules
- Debugging one bad rule in production: 2+ hours, frustrated users

**Annual Economic Reality:**
```
Annual skill usage: 4 bulk reviews
Cost per review: $0.45 (50K tokens)
Annual cost: $1.80

One bad rule in production:
- Debug time: 2-4 hours
- Token cost: 50K-100K tokens ($0.45-$0.90)
- Opportunity cost: Delayed features

Cost to prevent: $0.45 per review
ROI: 10-100× return
```

**Token Efficiency Category Error:**

Skills are NOT rules. Do not apply rule optimization principles here:
- "Skills should be token-efficient like rules" → WRONG context
- "Skills should be comprehensive regardless of tokens" → CORRECT context

**When Shortcuts Are Acceptable:**
**NEVER.** If time/tokens are constraints, use these instead:
- Set `filter_pattern` to review subset (e.g., `rules/100-*.md`)
- Set `review_mode: STALENESS` for quick check (1 dimension)
- Split into multiple sessions with `skip_existing: true`

**DO NOT create a "fast mode" that compromises quality.**

**Time Expectations (Measured):**

**Actual Performance (2026-01-06 run):**
- 113 rules reviewed in 19 minutes 32 seconds
- Average: 10.4 seconds per rule
- NOT 5-10 hours (original estimate was 30-60× off)

**Checkpoint Breakdown:**
- Discovery: 10 seconds
- Review execution: 409 seconds (6.8 min) - main work
- Aggregation: 520 seconds (8.7 min)
- Summary generation: 68 seconds (1.1 min)
- Overhead: 174 seconds (2.9 min)

**Lesson:** The process is already efficient. Further optimization harms quality.

### Verification

Each review must contain:
- Executive Summary with scores table (all 6 dimensions for FULL mode)
- Schema Validation Results (from schema_validator.py output)
- Agent Executability Verdict (based on Agent Execution Test)
- Dimension Analysis sections (detailed scoring rationale)
- Critical Issues list (specific line numbers)
- Recommendations (prioritized with expected score improvements)
- Post-Review Checklist
- Conclusion

**Violation consequences:**
- Invalid reviews rejected from summary
- Execution halted with protocol violation error
- User notified of shortcut attempt

**Quality gate:**
- Review file size 3000-8000 bytes (typical for FULL mode)
- < 2000 bytes = too abbreviated (VIOLATION)
- All required sections present (VIOLATION if missing)

### Shortcut Detection and Prevention

**During execution, HALT immediately if agent exhibits:**

**RED FLAGS (Stop and Self-Correct):**

1. **Suggesting efficiency improvements mid-review**
   - Example: "To save time, I'll create streamlined reviews..."
   - **Action:** STOP. Re-read this skill. Return to comprehensive process.

2. **Creating reviews <2500 bytes (FULL mode)**
   - **Detection:** `wc -c review_file` shows <2500
   - **Action:** DELETE abbreviated review. Re-do with full analysis.

3. **Not loading rubrics before scoring**
   - **Detection:** Dimension score provided without `read_file(rubrics/[dimension].md)`
   - **Action:** HALT. Load rubric. Re-score with rubric guidance.

4. **Batch processing mentions**
   - Example: "I'll process rules 1-10 together..."
   - **Action:** STOP. Review one rule at a time. No exceptions.

5. **Skipping schema validation**
   - **Detection:** Review lacks "Schema Validation Results" section with actual output
   - **Action:** HALT. Run schema_validator.py. Include output.

6. **Using examples/ as templates**
   - **Detection:** Review text matches example patterns without rule-specific details
   - **Action:** DELETE review. Re-analyze actual rule content.

7. **Time/token concerns mentioned**
   - Example: "Given the large number of rules..."
   - **Action:** STOP. Re-read "Why This Process Cannot Be Shortened" section.

8. **Applying rule optimization to skills**
   - Example: "To improve token efficiency..." (category error)
   - **Action:** STOP. Skills are NOT rules. Different optimization goals.

**Self-Correction Protocol:**

```
IF shortcut_detected:
  1. ACKNOWLEDGE: "I was attempting [shortcut]. This violates skill protocol."
  2. DELETE: Remove any abbreviated/templated reviews created
  3. RESET: Re-read bulk-rule-reviewer/SKILL.md and rule-reviewer/SKILL.md
  4. RESUME: Return to comprehensive process at last valid checkpoint
  5. COMMIT: "I will complete comprehensive reviews without shortcuts."
```

**User Intervention:**

If agent repeatedly attempts shortcuts despite self-correction:
- User should STOP execution
- Report skill design flaw
- Do NOT proceed with compromised reviews


## Workflow

### [OPTIONAL] Timing Start

**When:** Only if `timing_enabled: true` in inputs  
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md`

**Action:** Capture `run_id` in working memory for later use.

**Note:** Timing tracks the entire bulk review process (all stages), not individual rule-reviewer calls.

### [OPTIONAL] Checkpoint: skill_loaded

**When:** Only if timing was started  
**Checkpoint name:** `skill_loaded`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 1: Discovery

Find all `.md` files in `rules/` directory, apply filter_pattern, sort alphabetically.

**See:** `workflows/discovery.md`

### [OPTIONAL] Checkpoint: discovery_complete

**When:** Only if timing was started  
**Checkpoint name:** `discovery_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 2: Review Execution

**CRITICAL: This is where shortcut temptation peaks. Resist it.**

For each rule file:
1. Extract rule name from path
2. Check if review exists (if skip_existing=true)
3. **LOAD rule-reviewer/SKILL.md if not already loaded**
4. **LOAD relevant rubrics for dimensions being scored**
5. **RUN schema_validator.py on the rule file**
6. **PERFORM Agent Execution Test (count blocking issues)**
7. **SCORE each dimension according to rubric**
8. **GENERATE specific recommendations with line numbers**
9. **WRITE complete review to reviews/ directory**
10. Store (rule_name, score, verdict, review_path)
11. Show progress every 10 reviews

**Time per rule:** 8-15 seconds (measured average: 10.4 seconds)  
**Quality:** Comprehensive, reliable, actionable

**ANTI-PATTERN ALERT:**

If you're thinking ANY of these thoughts, STOP and re-read this skill:
- "This will take too long" → Measured: 19 minutes for 113 rules
- "I can optimize this" → NO. Quality > efficiency
- "Templates would be faster" → Templates = zero signal
- "Token costs are high" → $0.45 for 113 rules is cheap QA (Skills ≠ Rules)
- "Users won't notice abbreviated reviews" → They will. Bad rules escape.

**Reminder:** 
- ONE bad rule in production costs 100× more than comprehensive review
- Skills are NOT rules → Token efficiency is irrelevant (different optimization goals)

**See:** `workflows/review-execution.md` for orchestration details, resume capability, error handling.

### [OPTIONAL] Checkpoint: reviews_complete

**When:** Only if timing was started  
**Checkpoint name:** `reviews_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 3: Aggregation

For each review file:
1. Read first 150 lines only (context management)
2. Extract: overall score, verdict, critical issues, dimension scores
3. Build lightweight data structure (no full content)
4. Calculate statistics: average, median, distribution

**See:** `workflows/aggregation.md` for parsing strategy and statistics calculations.

### [OPTIONAL] Checkpoint: aggregation_complete

**When:** Only if timing was started  
**Checkpoint name:** `aggregation_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 4: Summary Report

Generate master summary with:
- Prioritized sections (Priority 1-4)
- Rules sorted by score within tiers
- Impact × effort ratios for recommendations
- Write to `reviews/_bulk-review-<model>-<date>.md`

**See:** `workflows/summary-report.md` for report format and section generation.

### [OPTIONAL] Checkpoint: summary_complete

**When:** Only if timing was started  
**Checkpoint name:** `summary_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### [OPTIONAL] Timing End (Compute)

**When:** Only if timing was started  
**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1)

**Action:** Capture STDOUT output for metadata embedding.

### [MODE TRANSITION: PLAN → ACT]

Authorization required for file modifications.

### [OPTIONAL] Timing End (Embed)

**When:** Only if timing was started  
**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2)

**Action:** Parse STDOUT, append timing metadata section to summary report file.

## Critical Design Decisions

**Context Management:** Parse only first 150 lines of each review (scores/verdicts only). Full details remain in individual files.

**Stateless Execution:** Review failures don't stop batch. Resume via skip_existing parameter.

**See:** `workflows/aggregation.md` for complete strategy.

## Error Handling

**Review failure:** Continue with next file, log error, mark FAILED in summary.

**Context overflow:** Switch to minimal output mode, report warning, continue.

**File write failure:** Print OUTPUT_FILE directive for manual save, continue.

**Empty rules directory:** Report error, exit gracefully without empty summary.

**Partial completion:** Resume capability allows continuation using existing reviews.

## Usage Examples

### Basic Invocation (All Rules, Full Review)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

### Filtered Review (Snowflake Rules Only)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
filter_pattern: rules/100-*.md
```

### Force Re-Review (Overwrite Existing)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: false
```

### Staleness Check Only

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
```

## Success Criteria

- All matching rules reviewed (or filtered subset)
- Individual review files written to `reviews/`
- Master summary report generated with valid path
- Prioritized improvement list included
- No context overflow during execution
- Resume capability functional (existing reviews skipped)
- Error handling graceful (failed reviews don't stop batch)

## Expected Outcomes

**Score distribution:** Average, median, distribution by priority tier.

**Dimension analysis:** Average scores for all 6 dimensions.

**Critical issues summary:** Count of rules with 0, 1-2, 3+ critical issues.

**Prioritized recommendations:** Top 10 rules to improve (impact × effort), estimated effort, expected score improvement.

**Next steps:** Immediate actions, short-term goals, long-term strategy.

## Installation Requirements

**Dependency:** rule-reviewer skill (required)

**Skill location resolution supports two patterns:**

1. **Installed Skill (Recommended):** Install `rule-reviewer` via agent tool's skill management
2. **Local Skill (Fallback):** Ensure `skills/rule-reviewer/` exists in project

**Auto-detection:** Automatically detects which pattern is available.

**Error handling:** If neither found, execution stops with installation guidance.

## Validation

**See:** `workflows/input-validation.md` for validation workflow and code patterns.

**Key Requirements:**
- `review_date`: YYYY-MM-DD format (valid calendar date)
- `review_mode`: FULL | FOCUSED | STALENESS (uppercase)
- `model`: lowercase-hyphenated (e.g., claude-sonnet-45)
- `filter_pattern`: rules/*.md glob (optional, must match ≥1 file)
- `skip_existing`: boolean true/false (optional, default: true)
- `max_parallel`: integer 1-10 (optional, default: 1)
- Environment: rules/ exists and readable, reviews/ writable

**Execution:** Validate inputs before Stage 1 (Discovery). Fail fast on errors.

## Examples

- `examples/full-bulk-review.md` - Complete walkthrough with 113 rules

## Related Skills

- **rule-reviewer** - Single rule review (required dependency)
- **rule-creator** - Create new rules (complementary)

## References

### Rules

- `rules/002f-claude-code-skills.md` - Skill authoring best practices
- `rules/002-rule-governance.md` - Rule schema and standards
- `rules/000-global-core.md` - Foundation patterns
