---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using 6-dimension rubric and write results to reviews/rule-reviews/ with no-overwrite safety. Use when reviewing rule files, auditing rule quality, checking rule staleness, validating rule compliance, or analyzing agent executability.
version: 2.4.0
---

# Rule Reviewer

Execute comprehensive agent-centric reviews evaluating whether autonomous agents can execute rules without judgment calls.

## Quick Start

```
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

Output: `reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-06.md`

(With `output_root: mytest/` → `mytest/rule-reviews/200-python-core-claude-sonnet-45-2026-01-06.md`)

## Scoring System (100 points)

**Raw Score Range:** 0-10 per dimension
**Formula:** Raw (0-10) × (Weight / 2) = Points

**Dimensions:**
- **Actionability** - Weight: 5, Max: 25 points - Can agents execute without judgment?
- **Completeness** - Weight: 5, Max: 25 points - All scenarios covered?
- **Consistency** - Weight: 3, Max: 15 points - Internal alignment correct?
- **Parsability** - Weight: 3, Max: 15 points - Schema valid?
- **Token Efficiency** - Weight: 2, Max: 10 points - Within ±5% budget?
- **Staleness** - Weight: 2, Max: 10 points - Current patterns?
- **Cross-Agent Consistency** - Weight: 1, Max: 5 points - Works across all agents?

**Detailed rubrics:** `rubrics/[dimension].md`

**Example Calculation (Actionability):**
- Raw score: 8/10
- Weight: 5
- Points: 8 × (5/2) = 8 × 2.5 = 20 points

## Review Modes

- **FULL:** All 6 dimensions scored
- **FOCUSED:** Actionability + Completeness only (50 points max)
- **STALENESS:** Staleness dimension only (10 points max)

## Critical: Anti-Optimization Protocol

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency.

**Forbidden Optimization Thoughts:**
- "This will take too long"
- "I can save time by..."
- "Token costs are high"
- "The user won't notice if I..."
- "I should ask about time constraints"
- "Let me create a faster approach"

**Required Mindset:**
- "I will complete the full process for this rule"
- "Quality signals are worth the cost"
- "The user authorized ACT knowing the scope"
- "Previous runs completed successfully at this pace"

**If you find yourself thinking about optimizing the review process itself:**
1. STOP
2. Re-read this section
3. Return to the comprehensive process
4. Do NOT ask the user about time/complexity

**IMPORTANT DISTINCTION:**
- Optimizing the SKILL EXECUTION (forbidden)
  - "I can review faster by skipping rubric consultation"
  - "I'll estimate scores to save time"
  - "Let me create a template"
- Evaluating RULE OPTIMIZATION (required)
  - Scoring Token Efficiency dimension
  - Identifying verbose patterns in rules
  - Recommending rule consolidation

**The user has already considered timing and scope. Proceed with the work.**

## Workflow

**Progress Display:** Show only `Starting: [rule-name]` and `Complete: [rule-name] → score/100`.
All canary checks, dimension scoring, and evidence gathering are INTERNAL (silent).

1. **Validate inputs**
   - Date format: YYYY-MM-DD
   - File exists (rules/*.md, AGENTS.md, or PROJECT.md)
   - Mode: FULL | FOCUSED | STALENESS

1b. **Detect file type**
   ```bash
   target_basename=$(basename "$target_file")
   
   if [[ "$target_basename" =~ ^(AGENTS|PROJECT)\.md$ ]]; then
       FILE_TYPE="project"
       SKIP_SCHEMA=true
       echo "File type: Project configuration (schema validation skipped)"
   elif [[ "$target_file" == rules/*.md ]]; then
       FILE_TYPE="rule"
       SKIP_SCHEMA=false
       echo "File type: Rule (full schema validation)"
   else
       echo "ERROR: Target must be AGENTS.md, PROJECT.md, or rules/*.md"
       exit 1
   fi
   ```

2. **Pre-Review Canary Check (SILENT - do not output)**
   Before reading the rule file, mentally verify:
   - What will I find in this rule? (RIGHT: "I don't know yet")
   - How long will this review take? (RIGHT: "However long it takes")
   - Can I reuse anything from previous work? (RIGHT: "No, different rule")
   
   **Any wrong answer → Re-read Anti-Optimization Protocol before proceeding**

3. **Run schema validation (conditional)**
   
   **IF FILE_TYPE == "rule":**
   ```bash
   uv run python scripts/schema_validator.py [target_file]
   ```
   Parse output for CRITICAL/HIGH/MEDIUM errors
   
   **IF FILE_TYPE == "project":**
   ```bash
   echo "Schema validation skipped for project file"
   echo "Note: Project files use different structure than rule schema"
   ```
   Set schema_validation_result = "SKIPPED (project file)"
   
   **Rationale:** AGENTS.md and PROJECT.md are bootstrap/configuration files with different structure than domain rules. They don't use rule metadata (SchemaVersion, RuleVersion, TokenBudget) or rule sections (Scope, Contract, References).

4. **Agent Execution Test (SILENT - results go to review file)**
   Count blocking issues (cap score at 60 if ≥10):
   - Undefined thresholds ("large", "significant", "appropriate")
   - Missing conditional branches (no explicit else)
   - Ambiguous actions (multiple interpretations)
   - Visual formatting (ASCII art, arrows, diagrams)

5. **Post-Read Canary Check (SILENT - do not output)**
   After reading file, before scoring, verify internally:
   - Can name 3 specific things unique to THIS file
   - Can cite a specific line number with content
   - Know the exact TokenBudget value (rule files) OR file purpose (project files)
   
   **Unable to verify → Did not actually read → Re-read file**

6. **Score dimensions**
   Read rubrics/ as needed for each dimension:
   - `rubrics/actionability.md`
   - `rubrics/completeness.md`
   - `rubrics/consistency.md`
   - `rubrics/parsability.md`
   - `rubrics/token-efficiency.md`
   - `rubrics/staleness.md`
   - `rubrics/cross-agent-consistency.md`
     - Includes documentation currency check via `web_fetch`
     - See `workflows/doc-currency-check.md` for details

7. **Mid-Review Canary (after dimension 3) (SILENT)**
   - Have I loaded the rubric for EACH dimension scored? (If NO → Go back)
   - Do my first 3 dimensions have distinct line references? (If NO → Find new evidence)
   
8. **Generate recommendations**
   - Specific line numbers
   - Quantified fixes
   - Expected score improvements

9. **Verify review authenticity**
   Before writing, verify review contains:
   - ≥15 line references (FULL mode)
   - Direct quotes with line numbers
   - Rule-specific findings (not generic)
   - See `workflows/review-verification.md`
   - **FAILURE → Trigger reset: Re-read SKILL.md completely**

10. **Write review**
   Path: `{output_root}/rule-reviews/[rule-name]-[model]-[date].md`
   Auto-increment: `-01.md`, `-02.md` if exists (when overwrite=false)

**See workflows/** for detailed error handling

## Verdicts

**Score Ranges:**
- **90-100** - EXECUTABLE - Production-ready
- **80-89** - EXECUTABLE_WITH_REFINEMENTS - Good, minor fixes
- **60-79** - NEEDS_REFINEMENT - Needs work
- **<60** - NOT_EXECUTABLE - Major issues

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score

## Supported File Types

**Rule Files (rules/*.md):**
- Domain-specific patterns and guidelines
- Loaded on-demand by agents
- Full schema validation against `schemas/rule-schema.yml`
- All 6 dimensions scored (100 points max)
- TokenBudget variance check applies

**Project Files (AGENTS.md, PROJECT.md):**
- Bootstrap and configuration documents
- Loaded once during project initialization
- Schema validation skipped (different structure than rules)
- All 6 dimensions scored (100 points max)
- TokenBudget variance skipped (no declared budget)
- Still evaluated for actionability, completeness, consistency, markdown quality, and currency

**Key Differences:**

| Aspect | Rule Files | Project Files |
|--------|------------|---------------|
| Schema validation | Full check | Skipped |
| Parsability scoring | Schema + markdown | Markdown only |
| Token efficiency | Budget variance + redundancy | Redundancy + structure only |
| Metadata required | 7 fields (SchemaVersion, etc.) | None |
| Section structure | Scope → Contract → Content | Custom per project |
| Max score | 100 points | 100 points |

**Both file types are agent-executable documents** - they just follow different schemas optimized for their architectural roles.

## Required Sections in Review

1. Executive Summary (scores table)
2. Schema Validation Results
3. Agent Executability Verdict
4. Dimension Analysis (6 sections for FULL mode)
5. Critical Issues (list)
6. Recommendations (prioritized)
7. Post-Review Checklist
8. Conclusion

## Inputs

- **target_file:** Path to file (e.g., `rules/200-python-core.md`, `AGENTS.md`, `PROJECT.md`)
- **review_date:** ISO 8601 format (YYYY-MM-DD)
- **review_mode:** FULL | FOCUSED | STALENESS
- **model:** Lowercase-hyphenated slug (e.g., `claude-sonnet-45`)
- **output_root:** (optional) Root directory for output files (default: `reviews/`). Subdirectory `rule-reviews/` is appended automatically. Supports relative paths including `../`.
- **overwrite:** (optional) true | false (default: false) - If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled:** (optional) true | false (default: false)

## Integration with Other Skills

### With bulk-rule-reviewer

bulk-rule-reviewer invokes this skill once per rule file. **Never** implement review logic yourself when bulk-rule-reviewer calls you.

### With skill-timing

**Execute IF:** `timing_enabled: true`  
**Skip IF:** `timing_enabled: false` (default)

**When enabled, execute ALL steps below (not optional once enabled):**

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `run_timing.sh start --skill rule-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After schema validation | Checkpoint | `run_timing.sh checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | - |
| After scoring complete | Checkpoint | `run_timing.sh checkpoint --run-id {{_timing_run_id}} --name review_complete` | - |
| Before file write | Compute | `run_timing.sh end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill rule-reviewer` | Store `_timing_stdout` |
| After file write (ACT) | Embed | Parse `_timing_stdout`, append timing metadata section to output file | - |

**Working memory contract:** Retain `_timing_run_id` and `_timing_stdout` from start through embed.

**Quick Reference:**
```bash
# 1. Start (store _timing_run_id from output)
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill rule-reviewer --target rules/200-python-core.md --model claude-sonnet-45 --mode FULL
# Output: TIMING_RUN_ID=rule-reviewer-200-python-core-20260108-abc123

# 2. Checkpoint: skill_loaded
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id rule-reviewer-200-python-core-20260108-abc123 --name skill_loaded

# 3. Checkpoint: review_complete
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id rule-reviewer-200-python-core-20260108-abc123 --name review_complete

# 4. End (store _timing_stdout from output)
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id rule-reviewer-200-python-core-20260108-abc123 \
    --output-file reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-08.md \
    --skill rule-reviewer

# 5. Embed: Parse _timing_stdout, append to output file (ACT mode required)
```

**Post-execution validation:** Verify timing metadata exists in output file (see Error Handling).

**See:** `../skill-timing/workflows/` for detailed workflow documentation

## Error Handling

**Schema validator fails:**
- Continue review
- Note validation unavailable in Parsability section
- Recommend manual schema check

**Rule file not found:**
- Report: "File not found: [path]"
- Verify path and try again

**Review write fails:**
- Print: `OUTPUT_FILE: [path]`
- Print full review content
- User must save manually

**Documentation currency check fails:**
- If `web_fetch` unavailable: Skip currency check, note in review
- If >50% links timeout: Skip penalty, note "Currency check incomplete"
- If all links fail: Note "Unable to verify documentation currency - manual review recommended"
- Continue with remaining staleness scoring (LastUpdated, deprecated tools, patterns, link status)

**See:** `workflows/error-handling.md`

## No-Overwrite Safety

**When `overwrite: false` (default):**

If `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` exists:
- Try `-01.md`
- Try `-02.md`
- Increment until available (max: `-99.md`)
- If `-99.md` exists: STOP, report error `Maximum review versions exceeded for [rule-name]`

**When `overwrite: true`:**

The existing file at `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` will be replaced. Use this when intentionally re-running a review to replace a previous version.

## Progressive Disclosure

Don't load all rubrics at once. Read as needed:
- Scoring Actionability → Read `rubrics/actionability.md`
- Scoring Completeness → Read `rubrics/completeness.md`
- Etc.

Only load what you need for current dimension.

## Validation Requirements

**Pre-Execution Commitment Checklist**

Before starting ANY review work, confirm each item:

- [ ] I will NOT calculate projected completion time
- [ ] I will NOT ask about time constraints mid-execution
- [ ] I will NOT create template-based review
- [ ] I will NOT propose "faster" alternatives
- [ ] I will read the rule file completely
- [ ] I will perform actual Agent Execution Test (count blocking issues)
- [ ] I will consult rubrics for each dimension
- [ ] I will write 3000-8000 byte review with specific analysis
- [ ] I will trust the user's ACT authorization

**If you cannot commit to all items above, STOP and report an error.**
**Do NOT proceed with partial commitment.**

**Pre-execution:**
- [ ] target_file exists under rules/
- [ ] review_date matches YYYY-MM-DD format
- [ ] review_mode is valid enum
- [ ] model slug is lowercase-hyphenated

**During execution:**
- [ ] Schema validation attempted
- [ ] Agent Execution Test completed
- [ ] All dimensions scored (FULL mode)
- [ ] Recommendations include line numbers

**Post-execution:**
- [ ] Review file written
- [ ] Path confirmed
- [ ] No overwrites occurred

## Critical Execution Protocol

**Execution Protocol: No Mid-Stream Questions**

**RULE:** Once user types "ACT", do NOT:
- Ask about time constraints
- Propose alternative approaches
- Calculate projected completion times
- Express concern about scope
- Request clarification on depth/quality trade-offs

**The ACT command means:**
- User understands the review scope
- User wants comprehensive review (3000-8000 bytes)
- User prioritizes accuracy over speed

**If you catch yourself about to ask "Should I..." or "Would you prefer...":**
- STOP
- The answer is: Continue with comprehensive review
- Return to the workflow

**DO:**
- Read complete rule file
- Run schema validator
- Score all dimensions per rubrics
- Generate specific recommendations
- Write complete review

**DON'T:**
- Skip dimensions (FULL mode requires all 6)
- Estimate scores without rubrics
- Generate generic recommendations
- Abbreviate review to save tokens
- Skip schema validation
- Ask about time/complexity mid-execution
- Calculate projected completion time
- Propose "streamlined" approaches

## Quality Over Efficiency Principle

**FOUNDATIONAL UNDERSTANDING:**

This skill exists to provide **reliable quality signals** for rule improvements. Token efficiency is explicitly NOT a goal.

**Agent Behavior Pattern Observed:**
Agents frequently attempt to "optimize" by:
- Creating template-based reviews without analysis
- Asking about time constraints mid-execution
- Proposing "streamlined" approaches
- Calculating projected completion times
- Expressing concern about token costs

**ALL OF THESE ARE FORBIDDEN.**

**Why Agents Do This:**
- Pattern matching to "helpful" behavior (offering options)
- Misapplying token-efficiency principles from rules to skills
- Anthropomorphizing user patience/time constraints
- Attempting to be "considerate" of resources

**Why This Is Wrong:**
1. **User has already authorized:** "ACT" means proceed with full scope
2. **Scope is acceptable:** Comprehensive review is expected
3. **Quality cannot be compromised:** One bad rule costs more than comprehensive review
4. **Skills ≠ Rules:** Token efficiency principles don't apply here

**Correct Behavior:**
- Execute the full workflow for the rule
- Do NOT calculate or mention projected completion time
- Do NOT ask about time constraints
- Do NOT propose "faster" alternatives
- Trust that the user understands the scope

**Detection Test:**
If you're thinking "Should I ask the user about..." - the answer is NO.
The user authorized ACT. Proceed with the work.

**Critical Distinction: Skills vs. Rules**

**RULES (100-snowflake-core.md):**
- Usage: Loaded 100s-1000s of times
- Token Efficiency: CRITICAL priority
- Optimization: Minimize tokens, preserve quality
- TokenBudget metadata: REQUIRED

**SKILLS (rule-reviewer):**
- Usage: Occasional (quarterly/annually)
- Token Efficiency: IRRELEVANT
- Optimization: Maximize quality, ignore tokens
- TokenBudget metadata: NOT APPLICABLE

**Why Skills Don't Optimize for Tokens:**

1. **Usage Frequency:** Quarterly use = 4× annual execution
2. **Annual Cost:** 50K tokens × 4 = 200K tokens ≈ $1.80
3. **Value Delivered:** Comprehensive QA for 113 rules
4. **Cost of Failure:** One bad rule = 10-100× the token cost

**Design Philosophy:**
- Quality Signal > Speed
- Reliability > Token Efficiency
- Completeness > Brevity
- Accuracy > Convenience
- Thoroughness > Cost

**If you're thinking about token costs during skill execution, you're in the wrong mindset.**

**Why Each Step Matters:**

1. **Schema Validation (schema_validator.py)**
   - **Purpose:** Catch structural errors before agents load rules
   - **Cannot skip:** Parsability score requires this
   - **Time cost:** 0.5-1 second
   - **Value:** Prevents agent confusion from malformed rules

2. **Agent Execution Test**
   - **Purpose:** Count specific blocking issues (undefined thresholds, ambiguity)
   - **Cannot skip:** Directly impacts Actionability score
   - **Time cost:** 1-2 seconds (manual reading)
   - **Value:** Predicts agent failure modes

3. **Dimension Scoring with Rubrics**
   - **Purpose:** Consistent, reproducible scoring across reviewers
   - **Cannot skip:** Without rubrics, scores drift arbitrarily
   - **Time cost:** 2-3 seconds per dimension
   - **Value:** Enables trend analysis across reviews

4. **Specific Recommendations with Line Numbers**
   - **Purpose:** Actionable improvements (not generic advice)
   - **Cannot skip:** Without line numbers, rule authors can't act
   - **Time cost:** 1-2 seconds per recommendation
   - **Value:** Actual rule improvements happen

5. **Complete Review Write**
   - **Purpose:** Durable record for comparison, trend tracking
   - **Cannot skip:** Summary aggregation depends on complete reviews
   - **Time cost:** 1-2 seconds (file write)
   - **Value:** Historical quality tracking

**Total Time Per Rule:** 8-12 seconds  
**Total Value:** Reliable quality measurement enabling continuous improvement

**Efficiency Tradeoffs (ALL REJECTED):**

- **Skip schema validation** - Time Saved: 1 sec, Value Lost: Parsability score invalid, Decision: REJECT
- **Estimate scores without rubrics** - Time Saved: 6 sec, Value Lost: Score consistency lost, Decision: REJECT
- **Generic recommendations** - Time Saved: 2 sec, Value Lost: No actionable improvements, Decision: REJECT
- **Abbreviated review** - Time Saved: 2 sec, Value Lost: Aggregation impossible, Decision: REJECT
- **Template-based content** - Time Saved: 8 sec, Value Lost: No actual analysis performed, Decision: REJECT

**Conclusion:** No efficiency tradeoff is worth the quality loss. Period.

**Self-Correction Trigger Words:**
If you think or write any of these phrases, you're taking a shortcut:
- "To save time..."
- "For efficiency..."
- "This would take approximately..."
- "Should I continue with..."
- "Would you prefer..."
- "Let me create a streamlined..."

**Immediate Action:**
1. STOP
2. Re-read the Anti-Optimization Protocol
3. Resume comprehensive process
4. Do NOT notify user of the self-correction (just fix it)

## Expected Review Size

Typical FULL mode review: 3000-8000 bytes

**Size validation:**
- If <2000 bytes: STOP, expand analysis with more specific findings
- If 2000-12000 bytes: Acceptable range
- If >12000 bytes: STOP, consolidate redundant content before writing

## Examples

See `examples/` for complete review samples:
- `full-review.md` - FULL mode walkthrough
- `focused-review.md` - FOCUSED mode example  
- `staleness-review.md` - STALENESS mode example
- `edge-cases.md` - Error scenarios

## Related Skills

- **bulk-rule-reviewer:** Batch review orchestrator (uses this skill)
- **rule-creator:** Rule authoring (validated with this skill)
- **skill-timing:** Execution time measurement (optional integration)

## Quality Checklist

Before considering review complete:

- [ ] Schema validator executed
- [ ] Agent Execution Test performed
- [ ] All required dimensions scored
- [ ] Each score has rationale
- [ ] Critical issues identified
- [ ] Recommendations prioritized
- [ ] Line numbers provided for fixes
- [ ] Review written to {output_root}/rule-reviews/
- [ ] File path confirmed
- [ ] **Review file ≥2500 bytes (drift check)**

## Context Preservation (Bulk Reviews)

When invoked by `bulk-rule-reviewer`, this skill may experience context drift after 10-20 rules.

**Structural Safeguards:**

1. **Pre-write verification:** Check review has ≥15 line refs, score table, verdict before writing
2. **Post-write size check:** If <2500 bytes, flag potential drift
3. **Periodic refresh:** Every 10 rules, re-read `bulk-rule-reviewer/CRITICAL_CONTEXT.md`

**See:** `workflows/review-execution.md` Pre-Write Output Verification section

## Version History

- **v2.4.0:** Added documentation currency check to staleness dimension
- **v2.0.0:** Removed PROMPT.md, added progressive disclosure with rubrics/
- **v1.4.0:** Added timing integration, schema validation
- **v1.3.0:** Added FOCUSED and STALENESS modes
- **v1.2.0:** Added Agent Execution Test
- **v1.1.0:** Added no-overwrite safety
- **v1.0.0:** Initial release

## Determinism Requirements

**Purpose:** Reduce score variance from ±5-8 points to <±2 points across runs.

### Mandatory Behaviors (ALWAYS DO)

1. **Batch-load all rubrics BEFORE reading target rule** - See `workflows/review-execution.md` Phase 1
2. **Create ALL 7 inventories BEFORE reading target rule** - Empty templates from each rubric
3. **Read target rule from line 1 to END** - No skipping sections
4. **Fill inventories systematically** - One dimension at a time, in order
5. **Check Non-Issues list for EACH flagged item** - Remove false positives with notes
6. **Apply overlap resolution rules** - Assign each issue to ONE dimension only
7. **Use Score Decision Matrix for EVERY score** - Look up tier from count/percentage
8. **Include completed inventories in review output** - As evidence for scoring

### Prohibited Behaviors (NEVER DO)

1. **NEVER read target rule before loading rubrics** - Anchors interpretation incorrectly
2. **NEVER skip inventory creation** - Leads to inconsistent counting
3. **NEVER estimate scores without counting** - Creates variance
4. **NEVER double-count issues across dimensions** - Use overlap resolution
5. **NEVER flag items without checking Non-Issues list** - Creates false positives
6. **NEVER omit inventories from review output** - Prevents verification
7. **NEVER score on "feel" or "impression"** - Use decision matrices only
8. **NEVER start scoring before completing all inventories** - Order matters

### Expected Variance Tolerance

| Component | Expected Variance |
|-----------|-------------------|
| Issue counts per dimension | ±1 item |
| Dimension scores | ±1 point |
| Overall score | ±2 points |

**If variance exceeds tolerance:** Review inventory counting, check Non-Issues application, verify overlap resolution.

### Self-Verification Checklist

Before submitting ANY review, verify:

- [ ] All 8 rubric files read BEFORE reading target rule?
- [ ] All 7 inventories created (even if empty)?
- [ ] Target rule read line 1 to END (no skipping)?
- [ ] Each inventory filled using only rubric-defined patterns?
- [ ] Non-Issues list checked for EVERY flagged item?
- [ ] Overlap resolution applied to multi-dimension issues?
- [ ] All inventories included in review output?
- [ ] All scores from Score Decision Matrix lookups?

**If ANY checkbox is NO:** Review is INVALID. Regenerate from Phase 1.
