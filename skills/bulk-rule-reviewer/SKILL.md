---
name: bulk-rule-reviewer
description: Execute agent-centric reviews on all rules in rules/ directory and generate prioritized improvement report
version: 2.2.0
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
- **overwrite**: Boolean (default: false) - If true, overwrite existing review files. If false, use sequential numbering (-01, -02, etc.) for conflicts
- **max_parallel**: Integer 1-10 (default: 5) - Concurrent sub-agent workers. Set to 1 for sequential execution (legacy behavior)
- **output_root**: Root directory for output files (default: `reviews/`). Subdirectories `rule-reviews/` and `summaries/` appended automatically. Supports relative paths including `../`.
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Outputs

**Individual reviews:** `{output_root}/rule-reviews/<rule-name>-<model>-<date>.md` (up to 113 files)

**Master summary:** `{output_root}/summaries/_bulk-review-<model>-<date>.md` with sections:

(Default `output_root: reviews/`. With `output_root: mytest/` → `mytest/rule-reviews/...` and `mytest/summaries/...`)
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <50, NOT_EXECUTABLE)
3. Priority 2: High (score 50-74, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 75-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (execution errors)
7. Top 10 Recommendations (impact × effort prioritization)
8. Next Steps (immediate/short-term/long-term)
9. Appendix: All Rules by Score (sorted table)

## Critical Execution Protocol

### CRITICAL: Anti-Optimization Protocol

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency.

**Forbidden Optimization Thoughts:**
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

**Required Mindset:**
- "I will complete the full process for each rule"
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
  - "I'll batch these reviews to save time"
  - "Let me create a template"
- Evaluating RULE OPTIMIZATION (required)
  - Scoring Token Efficiency dimension
  - Identifying verbose patterns in rules
  - Recommending rule consolidation

**The user has already considered timing and scope. Proceed with the work.**

### MANDATORY: One Rule At A Time

**NEVER batch multiple rules.** Each rule MUST be processed individually:

1. Read ONE rule file completely
2. Run schema validator for THAT rule
3. Apply ALL 6 scored rubrics to THAT rule
4. Write review file for THAT rule
5. THEN move to next rule

**Forbidden patterns:**
- `for f in rules/*.md; do` (batch shell loops for validation)
- Reading multiple rules before writing any reviews
- "Let me process rules 4-8 together"
- Creating templates to speed up reviews
- Parallelizing any review steps
- Combining schema validation for multiple files
- "Efficient batch processing"

**Why batching fails:**
- Context overflow loses rubric details mid-batch
- Template-based reviews miss rule-specific issues
- Shortcut thinking violates rubric requirements
- Evidence requirements (15+ line refs) impossible without focused reading

**Canary Check - Batching Detection:**

Before EACH rule review, verify:
- [ ] I am reviewing exactly ONE rule
- [ ] I have not combined multiple rules in this tool call
- [ ] My previous tool call was for ONE rule only
- [ ] I am NOT creating a "faster approach"

If ANY check fails: STOP, re-read Anti-Optimization Protocol, resume with ONE rule.

### Required Progress Output

After EACH rule review, output exactly:
```
[N/124] Complete: {filename} → {score}/100
```

This output MUST appear after writing EACH review file. If you see yourself planning to output multiple completion messages at once, you are batching - STOP immediately.

### MANDATORY ENFORCEMENT

This skill MUST execute the complete rule-reviewer workflow for each rule file.

### Context Anchor Protocol (CRITICAL)

**These sections MUST remain in active context throughout execution. NEVER summarize or drop them:**

1. **Anti-Optimization Protocol** (this section, lines 52-86)
2. **Skills vs Rules distinction** (lines 188-218)  
3. **Evidence Requirements** (lines 309-345)

**When context pressure occurs:**
- Summarize completed rule file contents FIRST
- Summarize completed review contents SECOND
- NEVER summarize anchor sections

**Structural Enforcement (MANDATORY):** Re-read `TEMPLATE.md` every 5 rules:

```python
if rule_number % 5 == 0:
    read_file("skills/rule-reviewer/examples/TEMPLATE.md")
```

**Drift Detection:** If any review file is <2500 bytes OR format deviates, immediately re-read:
1. `skills/rule-reviewer/examples/TEMPLATE.md` (output format specification)
2. `SKILL.md` (full protocol)

**Format Deviation Check:** After EVERY review, verify the output matches TEMPLATE.md structure:
- Executive Summary table with exact headers: `| Dimension | Raw (0-10) | Weight | Points | Notes |`
- All 7 required sections present in order
- If deviation detected: re-read TEMPLATE.md and regenerate the review

**See:** `workflows/context-anchor.md` and `workflows/inter-rule-gate.md` for full protocol

### How Skills Work Together

**IMPORTANT:** Skills cannot "invoke" other skills programmatically. Skills are documentation that guides agent behavior, not callable subroutines.

**Correct pattern:**
1. Load `skills/rule-reviewer/SKILL.md` to understand the review workflow
2. Load `skills/rule-reviewer/rubrics/*.md` as needed for each dimension
3. Execute the review workflow for each rule file
4. Write review to `reviews/rule-reviews/` following rule-reviewer's output format
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
- **Skipping schema validation** - Not running `ai-rules validate`

### Required Actions

- Load rule-reviewer/SKILL.md to understand complete workflow
- Load rubrics/*.md files as needed for each dimension being scored
- Run `ai-rules validate` for each rule
- Perform Agent Execution Test (count blocking issues)
- Score all dimensions according to review_mode (FULL/FOCUSED/STALENESS)
- Generate specific recommendations with line numbers
- Write complete review to reviews/rule-reviews/ with proper formatting
- Follow workflows sequentially (discovery → review-execution → aggregation → summary-report)
- Show progress every 10 reviews (not more frequently)

### Progress Display Protocol

**CRITICAL: Minimize console output during execution.**

Canary checks, dimension scoring, and evidence gathering are INTERNAL PROCESSING.
Do NOT display intermediate analysis to the user.

**SHOW to user (concise, one line each):**
- `[45/113] Starting: 310-zsh-scripting-core.md`
- `[45/113] Complete: 310-zsh-scripting-core.md → 95.5/100`
- Every 10 rules: brief aggregate summary (e.g., "Progress: 50/113, avg 87.2")

**DO NOT DISPLAY (internal processing only):**
- Pre-Rule Canary check questions/answers
- Post-Read Canary verification details
- Agent Execution Test blocking issue scans
- Dimension score calculations and breakdowns
- Evidence citations during processing
- Rubric consultation notes
- "3 unique things" verification output

**Rationale:** Canary checks ensure quality but are self-verification, not user communication.
The review FILE contains all evidence and analysis. Console output should show only progress.

**If canary check FAILS:** Log failure reason briefly, then proceed with reset protocol.

### Execution Acknowledgment

**Before proceeding, agent must confirm:**
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

**If cannot commit to ALL items: STOP and report error.**

### Why This Process Cannot Be Shortened

**CRITICAL UNDERSTANDING:**

This skill is designed for **quality assurance**, not efficiency. Short-circuiting defeats its purpose.

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
2. **Scope is acceptable:** Comprehensive review of all rules is expected
3. **Quality cannot be compromised:** One bad rule costs more than comprehensive review
4. **Skills ≠ Rules:** Token efficiency principles don't apply here

**Correct Behavior:**
- Execute the full workflow for each rule
- Do NOT calculate or mention projected completion times
- Do NOT ask about time constraints
- Do NOT propose "faster" alternatives
- Trust that the user understands the scope

**Detection Test:**
If you're thinking "Should I ask the user about..." - the answer is NO.
The user authorized ACT. Proceed with the work.

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
- **Value:** Comprehensive quality assurance for 129 rules
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

4. **"This will take too long"**
   - **Reality:** Comprehensive review completes efficiently with measured execution
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

- **Annual skill usage:** 4 bulk reviews
- **Cost per review:** $0.45 (50K tokens)
- **Annual cost:** $1.80
- **One bad rule in production:** Debug time 2-4 hours, token cost 50K-100K ($0.45-$0.90), opportunity cost from delayed features
- **Cost to prevent:** $0.45 per review
- **ROI:** 10-100× return

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

**Time Expectations (Measured - DO NOT RECALCULATE):**

**Actual Performance (2026-01-06 run):**
- 113 rules reviewed comprehensively
- Execution completes efficiently

**DO NOT:**
- Recalculate these numbers during execution
- Project "time remaining"
- Express concern about duration
- Ask if this is acceptable

**These numbers are provided for INFORMATION only.**
**Your job is to execute, not to optimize or question timing.**

**If you find yourself calculating time:**
- STOP
- You're optimizing instead of executing
- Return to the workflow

### Verification

Each review must contain:
- Executive Summary with scores table (all 6 dimensions for FULL mode)
- Schema Validation Results (from `ai-rules validate` output)
- Agent Executability Verdict (based on Agent Execution Test)
- Dimension Analysis sections (detailed scoring rationale)
- Critical Issues list (specific line numbers)
- Recommendations (prioritized with expected score improvements)
- Post-Review Checklist
- Conclusion

**CRITICAL: Evidence-Based Verification (MANDATORY)**

Every review MUST include evidence proving the file was actually read:

| Requirement | Minimum | Example |
|-------------|---------|---------|
| Line references | ≥15 distinct | "line 47", "lines 120-135" |
| Direct quotes | ≥3 with line numbers | `Line 156: "Use pd.to_datetime() with explicit format"` |
| Metadata citation | TokenBudget value | "TokenBudget ~6550 declared at line 12" |
| Pattern names | ≥2 exact names | "Anti-Pattern 2: Using Deprecated datetime.utcnow()" |
| Code references | ≥1 function/class name | "The `ensure_python_datetime()` helper at lines 330-350" |

**Zero-Recommendation Rule:**

Reviews with "No recommendations" or "None required" MUST justify with:
1. At least 3 specific attempts to find issues (with line references)
2. Explicit statement: "Searched for [X, Y, Z] issues at lines [A, B, C] - none found"

**If a review contains zero recommendations AND zero line references = AUTOMATIC REJECTION**

Even excellent rules (95-100 score) should have at least LOW severity suggestions:
- Minor terminology consistency opportunities
- Potential future-proofing considerations
- Cross-reference enhancement possibilities
- Example expansion opportunities

**Violation consequences:**
- Invalid reviews rejected from summary
- Execution halted with protocol violation error
- User notified of shortcut attempt

**Quality gate:**
- Review file size 3000-8000 bytes (typical for FULL mode)
- < 2000 bytes = too abbreviated (VIOLATION)
- All required sections present (VIOLATION if missing)
- ≥15 line references present (VIOLATION if missing)
- ≥3 direct quotes with line numbers (VIOLATION if missing)

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
   - **Action:** HALT. Run `ai-rules validate`. Include output.

6. **Using examples/ as templates**
   - **Detection:** Review text matches example patterns without rule-specific details
   - **Action:** DELETE review. Re-analyze actual rule content.

7. **Time/token concerns mentioned**
   - Example: "Given the large number of rules..."
   - **Action:** STOP. Re-read "Why This Process Cannot Be Shortened" section.

8. **Applying rule optimization to skills**
   - Example: "To improve token efficiency..." (category error)
   - **Action:** STOP. Skills are NOT rules. Different optimization goals.

**HALT IMMEDIATELY if you:**
1. Generate review text without reading the actual rule file
2. Use the same review text for multiple rules
3. Create reviews in a loop without individual analysis
4. Think "I'll create a template and fill in details"
5. Calculate "time remaining" or "rules per minute"
6. Consider asking the user about scope/timing

**Self-Correction Trigger Words:**
If you think or write any of these phrases, you're taking a shortcut:
- "To save time..."
- "For efficiency..."
- "Given the large number..."
- "This would take approximately..."
- "Should I continue with..."
- "Would you prefer..."
- "Let me create a streamlined..."

**Immediate Action:**
1. DELETE any work done with shortcuts
2. Re-read the Anti-Optimization Protocol
3. Resume comprehensive process
4. Do NOT notify user of the self-correction (just fix it)

**Self-Correction Protocol:**

**If shortcut detected:**
1. ACKNOWLEDGE: "I was attempting [shortcut]. This violates skill protocol."
2. DELETE: Remove any abbreviated/templated reviews created
3. RESET: Re-read bulk-rule-reviewer/SKILL.md and rule-reviewer/SKILL.md
4. RESUME: Return to comprehensive process at last valid checkpoint
5. COMMIT: "I will complete comprehensive reviews without shortcuts."

**User Intervention:**

If agent repeatedly attempts shortcuts despite self-correction:
- User should STOP execution
- Report skill design flaw
- Do NOT proceed with compromised reviews


## Workflow

### Parameter Collection

Collect ALL parameters (required AND optional) using `ask_user_question` tool.

**See:** `workflows/parameter-collection.md`

**MANDATORY:** Prompt for ALL parameters in batched questions (max 4 per call):
- Do NOT silently apply defaults for optional parameters
- User must explicitly confirm each setting
- If `ask_user_question` unavailable, fall back to text-based prompting

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

### Stage 2: Review Execution (Parallel or Sequential)

**Execution mode depends on `max_parallel` parameter:**

#### Parallel Execution (default: max_parallel ≥ 2)

When `max_parallel >= 2`, use parallel sub-agents for faster execution:

1. **Partition rules** into N groups (where N = max_parallel)
2. **Launch N sub-agents** in background, each assigned a group
3. **Each sub-agent** loads rule-reviewer skill and processes its rules independently
4. **Monitor progress** via agent_output polling
5. **Aggregate results** when all sub-agents complete

**Benefits:**
- 5× speedup (~50 minutes instead of 4-6 hours)
- Fresh context per sub-agent (eliminates drift)
- Isolated failures (one agent failing doesn't stop others)

**See:** `workflows/parallel-execution.md` for full implementation
**See:** `workflows/subagent-prompt-template.md` for sub-agent prompt

**File writes:** All sub-agents write directly to `{output_root}/rule-reviews/`. No conflicts because each sub-agent reviews different rules (unique filenames).

#### Sequential Execution (max_parallel = 1)

When `max_parallel = 1`, use legacy sequential processing (single agent reviews all rules).

**Use sequential when:**
- Debugging/troubleshooting the skill
- Very small rule sets (< 10 rules)
- Explicit user preference

---

**CRITICAL: This is where shortcut temptation peaks. Resist it.**

**Execution Protocol: No Mid-Stream Questions**

**RULE:** Once user types "ACT", do NOT:
- Ask about time constraints
- Propose alternative approaches
- Calculate projected completion times
- Express concern about scope
- Request clarification on depth/quality trade-offs

**The ACT command means:**
- User understands the scope (113 rules)
- User wants comprehensive reviews (3000-8000 bytes each)
- User prioritizes accuracy over speed

**If you catch yourself about to ask "Should I..." or "Would you prefer...":**
- STOP
- The answer is: Continue with comprehensive reviews
- Return to the workflow

For each rule file:
1. **INTER-RULE GATE (every 5 rules):** If rule_number % 5 == 0, execute `workflows/inter-rule-gate.md`
2. **PRE-RULE CANARY:** Execute 3 canary questions from `workflows/proactive-canary.md`
3. Extract rule name from path
4. Check if review exists (if skip_existing=true)
5. **READ the actual rule file into working memory**
6. **POST-READ CANARY:** Verify you can name 3 specific things unique to THIS rule
7. **LOAD rule-reviewer/SKILL.md if not already loaded**
8. **LOAD relevant rubrics for dimensions being scored**
9. **RUN `ai-rules validate` on the rule file**
10. **PERFORM Agent Execution Test (count blocking issues)**
11. **MID-REVIEW CANARY (after dimension 3):** Check rubric loading and reference reuse
12. **SCORE each dimension according to rubric, citing line numbers and quotes**
13. **GENERATE specific recommendations with line numbers**
14. **VERIFY review authenticity (see workflows/per-rule-verification.md)**
    - Must have ≥15 line references
    - Must cite direct quotes from rule
    - Must include rule-specific findings
    - **FAILURE triggers `workflows/reset-trigger.md`**
15. **WRITE complete review to reviews/rule-reviews/ directory** (respects overwrite parameter)
16. Store (rule_name, score, verdict, review_path)
17. Show progress every 10 reviews

**CRITICAL:** Step 5 (READ the actual rule file) MUST happen BEFORE steps 10-13. Reviews generated without reading the file will fail verification at step 14.

**DRIFT PREVENTION:** Steps 1, 2, 6, 11 are canary/gate checks that detect optimization drift BEFORE it produces compromised output. These are NOT optional.

**Time per rule:** Efficient execution with comprehensive analysis
**Quality:** Comprehensive, reliable, actionable

**ANTI-PATTERN ALERT:**

If you're thinking ANY of these thoughts, STOP and re-read this skill:
- "This will take too long" → Comprehensive review completes efficiently
- "I can optimize this" → NO. Quality > efficiency
- "Templates would be faster" → Templates = zero signal
- "Token costs are high" → $0.45 for 129 rules is cheap QA (Skills ≠ Rules)
- "Users won't notice abbreviated reviews" → They will. Bad rules escape.

**Correct Agent Self-Talk During Execution:**

**WRONG (Optimization-Seeking):**
- "I've done 10 rules in 8 minutes, so 129 will take 90 minutes..."
- "This seems like a lot of work, should I ask the user?"
- "Maybe I can create a template to speed this up..."
- "Let me calculate the token cost..."

**RIGHT (Execution-Focused):**
- "Next rule: 101a-snowflake-streamlit-visualization.md"
- "Reading rule file... Running schema validation... Counting blocking issues..."
- "Scoring dimension 1: Actionability... Evidence: line 52..."
- "Writing review... Next rule: 101b-snowflake-streamlit-performance.md"

**Notice the difference:**
- WRONG: Meta-thinking about the process
- RIGHT: Executing the process

**Your internal monologue should be task steps, not process analysis.**

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
- Write to `reviews/summaries/_bulk-review-<model>-<date>.md`

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

Request user ACT authorization before file modifications.

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
overwrite: true
```

**Note:** Use `overwrite: true` to replace existing reviews. Use `skip_existing: false` combined with `overwrite: false` (default) to create new versions with sequential numbering (-01, -02).

### Re-Review with Sequential Numbering (Preserve History)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: false
overwrite: false
```

This creates `-01`, `-02` versions without overwriting previous reviews.

### Staleness Check Only

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
```

## Success Criteria

- All matching rules reviewed (or filtered subset)
- Individual review files written to `reviews/rule-reviews/`
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
- Environment: rules/ exists and readable, reviews/rule-reviews/ and reviews/summaries/ writable

**Execution:** Validate inputs before Stage 1 (Discovery). Fail fast on errors.

## Examples

- `examples/full-bulk-review.md` - Complete walkthrough with 113 rules

## Related Skills

- **rule-reviewer** - Single rule review (required dependency)
- **rule-creator** - Create new rules (complementary)

## References

### Rules

- `rules/002h-claude-code-skills.md` - Skill authoring best practices
- `rules/002-rule-governance.md` - Rule schema and standards
- `rules/000-global-core.md` - Foundation patterns
