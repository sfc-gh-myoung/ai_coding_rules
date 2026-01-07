# Bulk Rule Reviewer - Usage Guide

## Overview

The **bulk-rule-reviewer** skill executes comprehensive agent-centric reviews on all rule files in the `rules/` directory, generating a consolidated priority report showing which rules need attention.

**How it works:** This skill loads and follows the rule-reviewer workflow for each rule file. It's an orchestrator skill that maintains the same quality standards as individual rule reviews by following the documented review process.

**Primary Use Cases:**
- Periodic quality audits (quarterly/monthly)
- Pre-release validation before major versions
- Technical debt tracking and prioritization
- Baseline quality measurement

**Expected Execution Time:** 5-10 hours for 113 rules (sequential, 3-5 min per rule)

---

## ⚠️ Execution Integrity Warning

**CRITICAL:** This skill takes 5-10 hours to complete for 113 rules. This is EXPECTED and REQUIRED.

### Common Agent Shortcuts (ALL FORBIDDEN)

Agents executing this skill may attempt to optimize by:
- Batch-processing multiple rules at once (FORBIDDEN)
- Running abbreviated reviews to save time (FORBIDDEN)
- Parallel execution without explicit permission (FORBIDDEN)
- Skipping rubric consultation to save tokens (FORBIDDEN)

**These shortcuts WILL compromise review quality.**

### How to Verify Faithful Execution

**During Execution:**
- Each rule should take 3-5 minutes to review
- Progress updates every 10 reviews (not more frequent)
- Schema validator executed for each rule
- Rubrics loaded and applied for dimension scoring

**After Execution:**
- Check review file sizes (should be 3000-8000 bytes each)
- Verify execution time (5+ hours for 100+ rules)
- Spot-check reviews for complete sections

**Red Flags:**
- ⚠️ Execution completes in < 2 hours for 100+ rules
- ⚠️ Review files < 2000 bytes
- ⚠️ Missing sections in review files
- ⚠️ Schema validation not executed
- ⚠️ Rubrics not consulted for scoring

### Resume Capability

**Expected usage pattern:**
```
Session 1: Review rules 1-30 (3 hours) → Context limit reached
Session 2: Review rules 31-60 (3 hours) → Resume with skip_existing=true
Session 3: Review rules 61-90 (3 hours)
Session 4: Review rules 91-113 (2 hours) + Generate summary
```

**This is NORMAL and EXPECTED for large rule sets.**

---

## Quick Start

### Step 1: Load the Skill

**Load the skill file to enable the agent/model to use it:**

```
skills/bulk-rule-reviewer/SKILL.md
```

**How to load:**
- **Claude Code / Cortex Code:** Open or reference `skills/bulk-rule-reviewer/SKILL.md` in your conversation
- **Cursor / Other agents:** Load `skills/bulk-rule-reviewer/SKILL.md` file which allows the agent to use the skill without "installing" it
- **Manual load:** Use your agent's file reading capability to load the SKILL.md content

**Why this works:** The SKILL.md file contains the complete skill definition. Opening or referencing it makes the skill available to the agent for the current session.

### Step 2: Basic Usage (Review All Rules)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

**Expected Output:**
- 113 individual review files in `reviews/` directory
- 1 master summary report: `reviews/_bulk-review-claude-sonnet-45-2026-01-06.md`
- Console progress: "Reviewing 45/113: rules/200-python-core.md"

---

## Execution Timing

Enable execution timing to measure bulk review duration and track performance:

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

When enabled, the output includes:
- **Timing Metadata section** in the master summary report
- **STDOUT summary** with total duration, checkpoints (discovery, reviews, aggregation, summary), tokens, baseline comparison
- **Real-time anomaly alerts** if duration is suspicious

**Example timing metadata:**

```markdown
## Timing Metadata

| Metric | Value |
|--------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Duration | 342m 15s (20535.5s) |
| Model | claude-sonnet-45 |
| Tokens | 1,840,300 (1,250,000 in / 590,300 out) |
| Cost | ~$12.60 |
```

**Checkpoints tracked:**
- `skill_loaded` - After loading SKILL.md
- `discovery_complete` - After discovering all rule files
- `reviews_complete` - After all individual rule reviews
- `aggregation_complete` - After aggregating review data
- `summary_complete` - After generating summary report

**Note:** For bulk reviews with 100+ rules, timing duration can be 3-6 hours. Anomaly detection thresholds are configured separately for bulk-rule-reviewer.

**See:** `skills/skill-timing/README.md` for full documentation on timing features, baseline comparison, and analysis tools.

---

## Input Parameters

### Required Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `review_date` | YYYY-MM-DD | Today | Date stamp for review files | `2026-01-06` |
| `review_mode` | Enum | FULL | Review depth | `FULL`, `FOCUSED`, `STALENESS` |
| `model` | String | claude-sonnet-45 | Model identifier | `claude-sonnet-45`, `gpt-4` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `filter_pattern` | Glob | `rules/*.md` | Filter rules by pattern | `rules/100-*.md` |
| `skip_existing` | Boolean | `true` | Skip files with existing reviews | `true`, `false` |
| `max_parallel` | Integer | `1` | Max concurrent reviews | `1` (sequential) |
| `timing_enabled` | Boolean | `false` | Enable execution timing | `true`, `false` |

---

## Usage Examples

### Example 1: Full Review of All Rules

**Scenario:** Quarterly quality audit of entire rule repository

**Invocation:**
```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

**Output:**
- 113 individual reviews: `reviews/000-global-core-claude-sonnet-45-2026-01-06.md`, etc.
- Master summary: `reviews/_bulk-review-claude-sonnet-45-2026-01-06.md`

**Expected Duration:** 5.6-9.4 hours (sequential)

---

### Example 2: Review Snowflake Rules Only

**Scenario:** Pre-release validation for Snowflake-specific features

**Invocation:**
```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
filter_pattern: rules/100-*.md
```

**Output:**
- ~23 individual reviews for Snowflake rules (100-series)
- Master summary: `reviews/_bulk-review-claude-sonnet-45-2026-01-06.md`

**Expected Duration:** ~1-2 hours

---

### Example 3: Staleness Check (Quick Audit)

**Scenario:** Check if rules need updates due to outdated references

**Invocation:**
```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
```

**Output:**
- 113 staleness reviews (focused on freshness dimension only)
- Master summary with staleness scores

**Expected Duration:** 2-3 hours (faster than FULL mode)

---

### Example 4: Force Re-Review (Overwrite Existing)

**Scenario:** Re-review rules after major improvements, replacing old reviews

**Invocation:**
```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: false
```

**Output:**
- All existing reviews overwritten with fresh evaluations
- New master summary

**Note:** Use with caution - overwrites existing reviews for the same date

---

### Example 5: Resume After Interruption

**Scenario:** Previous bulk review stopped at rule 67/113 due to context overflow

**Invocation:**
```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: true
```

**Output:**
- Skips rules 1-67 (existing reviews found)
- Reviews rules 68-113
- Master summary includes all 113 rules

**Benefit:** Resume capability saves 3-4 hours of re-work

---

## Output Structure

### Individual Review Files

**Location:** `reviews/<rule-name>-<model>-<date>.md`

**Format:** Standard rule-reviewer output with:
- Overall score (0-100)
- Dimension scores (Actionability, Completeness, etc.)
- Verdict (EXECUTABLE, NEEDS_REFINEMENT, etc.)
- Critical issues list
- Recommendations

**Example:** `reviews/100-snowflake-core-claude-sonnet-45-2026-01-06.md`

---

### Master Summary Report

**Location:** `reviews/_bulk-review-<model>-<date>.md`

**Sections:**

1. **Executive Summary**
   - Score distribution (Excellent 90-100, Good 80-89, Needs Work 60-79, Poor <60)
   - Dimension analysis (average scores for all 6 dimensions)
   - Critical issues summary

2. **Priority 1: Urgent (Score <60)**
   - NOT_EXECUTABLE rules requiring immediate attention
   - Detailed breakdown with estimated effort

3. **Priority 2: High (Score 60-79)**
   - NEEDS_REFINEMENT rules
   - Top 5-10 with quick wins highlighted

4. **Priority 3: Medium (Score 80-89)**
   - EXECUTABLE_WITH_REFINEMENTS rules
   - Aggregate issues summary

5. **Priority 4: Excellent (Score 90-100)**
   - EXECUTABLE rules (production-ready)
   - Maintenance: quarterly staleness reviews only

6. **Failed Reviews**
   - Rules that couldn't be reviewed (errors)
   - Action required for manual review

7. **Top 10 Improvement Recommendations**
   - Prioritized by impact × effort ratio
   - High impact, low effort first

8. **Next Steps**
   - Immediate (this week)
   - Short-term (this month)
   - Long-term (quarterly)

9. **Appendix: All Rules by Score**
   - Sortable table with links to individual reviews

**Example:** `reviews/_bulk-review-claude-sonnet-45-2026-01-06.md`

---

## Workflow Stages

The skill executes in 4 sequential stages:

### Stage 1: Discovery (workflows/discovery.md)
- Find all `.md` files in `rules/` directory
- Apply filter_pattern if specified
- Sort alphabetically
- **Duration:** <1 second

### Stage 2: Review Execution (workflows/review-execution.md)
- Load rule-reviewer/SKILL.md to understand workflow
- For each rule: follow the documented review process
- Load rubrics/ progressively for dimension scoring
- Handle errors gracefully (continue on failure)
- Track progress with console output
- **Duration:** 3-5 min per rule × 113 rules = 5.6-9.4 hours

### Stage 3: Aggregation (workflows/aggregation.md)
- Extract scores/verdicts from review files
- Calculate statistics (averages, distributions)
- Group by priority tiers
- **Duration:** <5 seconds

### Stage 4: Summary Report (workflows/summary-report.md)
- Generate master markdown report
- Prioritize recommendations
- Write to file
- **Duration:** <2 seconds

---

## Resume Capability

**Problem:** Bulk reviews take hours; interruptions waste work

**Solution:** `skip_existing` parameter (default: `true`)

**How It Works:**

1. Before reviewing each rule, check if review file exists
2. If exists AND `skip_existing=true`: Load score from existing file, mark as SKIPPED
3. If not exists OR `skip_existing=false`: Invoke rule-reviewer normally

**Example:**

```
Starting bulk review: 113 rules

✓ Skipping 000-global-core (review exists)
✓ Skipping 001-memory-bank (review exists)
...
✓ Skipping 066-example-rule (review exists)

[67/113] Reviewing: rules/067-new-rule.md
  ✓ Complete: 85/100 (EXECUTABLE_WITH_REFINEMENTS)
```

**Benefits:**
- Resume after interruption without re-work
- Idempotent execution (safe to run multiple times)
- Save 3-4 hours when resuming mid-batch

---

## Error Handling

### Review Failure

**Cause:** Malformed rule, context overflow, missing metadata

**Behavior:**
- Log error to console
- Mark as FAILED in results
- Continue with next rule (don't stop batch)
- Include in "Failed Reviews" section of master summary

**Example:**
```
[45/113] Reviewing: rules/broken-syntax.md
  ✗ Failed: Malformed markdown syntax
```

### Empty Rules Directory

**Cause:** No `.md` files found in `rules/`

**Behavior:**
- Exit with error: "No rule files found in rules/"
- No summary generated

### Context Overflow

**Cause:** Too many reviews in memory

**Behavior:**
- Switch to minimal output mode
- Continue execution
- If overflow persists, abort and report progress

### File Write Failure

**Cause:** Cannot write to `reviews/` directory (permissions, disk full)

**Behavior:**
- Print OUTPUT_FILE directive for manual save
- Continue execution

---

## Filtering Options

### By Rule Prefix (Domain-Specific)

**Snowflake Rules Only:**
```
filter_pattern: rules/100-*.md
```

**Python Rules Only:**
```
filter_pattern: rules/200-*.md
```

**Shell Rules Only:**
```
filter_pattern: rules/300-*.md
```

### By Rule Type

**Core Rules Only:**
```
filter_pattern: rules/*-core.md
```

**Governance Rules Only:**
```
filter_pattern: rules/002*.md
```

### By Numbering Range

**All 100-series and 200-series:**
```
filter_pattern: rules/[12]*.md
```

---

## Performance Notes

- **Sequential execution:** 1 review at a time (default: `max_parallel=1`)
- **Average review time:** 3-5 minutes per rule
- **Total time (113 rules):** 5.6-9.4 hours
- **Context efficiency:** Only first 150 lines of each review file loaded
- **Resume capability:** Critical for long-running batches

---

## Success Criteria

✅ All matching rules reviewed (or filtered subset)  
✅ Individual review files written to `reviews/`  
✅ Master summary report generated with valid path  
✅ Prioritized improvement list included  
✅ No context overflow during execution  
✅ Resume capability functional (existing reviews skipped)  
✅ Error handling graceful (failed reviews don't stop batch)

---

## Troubleshooting

### Issue: "No rule files found"

**Cause:** Working directory is not project root

**Solution:** Verify `rules/` directory exists in current working directory

---

### Issue: Reviews taking too long

**Cause:** FULL mode reviews entire rule (all 6 dimensions)

**Solution:** Use `FOCUSED` mode for faster execution (Actionability and Completeness only)

---

### Issue: Context overflow mid-batch

**Cause:** Too many reviews loaded into context

**Solution:** 
1. Use resume capability (`skip_existing=true`)
2. Reduce `filter_pattern` scope (review 100-series, then 200-series separately)

---

### Issue: Master summary not generated

**Cause:** All reviews failed, no successful data

**Solution:**
1. Check individual review errors
2. Fix rule files with malformed markdown
3. Re-run bulk review

---

### Issue: Existing reviews not skipped

**Cause:** `skip_existing=false` or review file name mismatch

**Solution:**
1. Verify `skip_existing: true` in invocation
2. Check review file naming: `<rule-name>-<model>-<date>.md`

---

## Deployment

This skill is **internal-only** and is not deployed to team projects. It remains in the ai_coding_rules source repository for bulk rule maintenance and quality audits.

**Rationale:** Bulk reviews are infrastructure operations for rule repository maintenance, not typical project workflows.

---

## Related Documentation

- **Skill Definition:** `SKILL.md`
- **Workflows:** `workflows/discovery.md`, `review-execution.md`, `aggregation.md`, `summary-report.md`, `input-validation.md`
- **Examples:** `examples/full-bulk-review.md`
- **Tests:** `tests/validation-tests.md`

---

## Version History

- **v1.0.0 (2026-01-06):** Initial implementation

---

## Next Steps After Bulk Review

### Immediate (This Week)
1. Review Priority 1 rules (score <60)
2. Address failed reviews manually
3. Implement quick wins from Top 10 list (items with <30 min effort)

### Short-Term (This Month)
1. Address Priority 2 rules with <75 score
2. Fix undefined thresholds across Priority 3 rules
3. Update outdated references (Python versions, deprecated APIs)

### Long-Term (Quarterly)
1. Re-run bulk review to track improvement trends
2. Compare current vs. baseline scores (score deltas)
3. Consider automated quality gates for CI/CD
4. Maintain target: 90% of rules ≥80/100

---

## File Structure

```
skills/bulk-rule-reviewer/
├── SKILL.md               # Main skill instructions (Claude Code entrypoint)
├── README.md              # This file - usage documentation
├── examples/              # Complete workflow examples
│   └── full-bulk-review.md    # Complete 113-rule walkthrough
├── tests/                 # Skill test cases
│   └── validation-tests.md    # Validation test cases
└── workflows/             # Stage-specific detailed guides
    ├── discovery.md           # Stage 1: File discovery
    ├── review-execution.md    # Stage 2: Rule-reviewer orchestration
    ├── aggregation.md         # Stage 3: Score extraction and statistics
    ├── summary-report.md      # Stage 4: Master report generation
    └── input-validation.md    # Input validation workflow
```

---

**For detailed implementation guidance, see workflow files in `workflows/` directory.**
