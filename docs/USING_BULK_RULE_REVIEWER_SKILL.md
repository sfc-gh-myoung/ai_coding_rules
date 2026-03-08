# Using the Bulk Rule Reviewer Skill

**Last Updated:** 2026-03-07

## Background

The bulk-rule-reviewer skill automates comprehensive agent-centric reviews of all rule files in the `rules/` directory, generating a consolidated priority report showing which rules need attention.

Key behaviors:

- Reviews all rules in `rules/` directory (or filtered subset)
- Launches parallel sub-agents by default (5 workers), each with fresh context
- Invokes rule-reviewer skill for each rule individually
- Generates individual review files in `{output_root}rule-reviews/` directory
- Creates master summary report in `{output_root}summaries/`
- Default `output_root`: `reviews/`
- Supports resume capability for long-running batches
- Expected execution time: 1-2 hours (parallel), 5-10 hours (sequential)

## Quick Start

### 1. Load the skill

```text
Load skills/bulk-rule-reviewer/SKILL.md
```

### 2. Request a bulk review

**Basic usage (all rules):**

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

**With custom output directory:**

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
output_root: quarterly-audit/
```

**Filtered review (Snowflake rules only):**

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
filter_pattern: rules/100-*.md
```

**With execution timing:**

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

### 3. Output locations

**Individual reviews:** `{output_root}rule-reviews/<rule-name>-<model>-<date>.md` (one per rule)

**Master summary:** `{output_root}summaries/_bulk-review-<model>-<date>.md`

**Default output_root:** `reviews/`

**Examples:**
- Default: `reviews/rule-reviews/...` and `reviews/summaries/_bulk-review-...`
- With `output_root: quarterly-audit/`: `quarterly-audit/rule-reviews/...` and `quarterly-audit/summaries/...`

The master summary includes:
- Executive Summary (score distribution, dimension analysis)
- Priority 1: Urgent (score <60, NOT_EXECUTABLE)
- Priority 2: High (score 60-79, NEEDS_REFINEMENT)
- Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
- Priority 4: Excellent (score 90-100, EXECUTABLE)
- Failed Reviews (execution errors)
- Top 10 Recommendations (impact × effort prioritization)
- Next Steps (immediate/short-term/long-term)
- Appendix: All Rules by Score

## Review Modes

**FULL Mode (Comprehensive):**
- All 7 dimensions evaluated per rule
- Expected duration: 1-2 hours (parallel with 5 workers), 5-10 hours (sequential)
- Use for: Quarterly audits, pre-release validation

**FOCUSED Mode (Targeted):**
- Actionability + Completeness only
- Faster execution (~1 hour parallel)
- Use for: Quick quality checks

**STALENESS Mode (Periodic Maintenance):**
- Staleness dimension only
- Fastest execution (~30 min parallel)
- Use for: Monthly maintenance, link rot detection

## Resume Capability

The skill supports resuming after interruptions:

**Problem:** Bulk reviews take hours; interruptions waste work

**Solution:** `skip_existing` parameter (default: `true`)

**How it works:**
1. Before reviewing each rule, check if review file exists
2. If exists AND `skip_existing=true`: Load score from existing file, mark as SKIPPED
3. If not exists OR `skip_existing=false`: Invoke rule-reviewer normally

**Example usage:**

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: true
```

**Benefits:**
- Resume after interruption without re-work
- Idempotent execution (safe to run multiple times without side effects)
- Save 3-4 hours when resuming mid-batch

## Execution Timing

When `timing_enabled: true`:
- STDOUT summary with total duration
- Checkpoints tracked: skill_loaded, discovery_complete, reviews_complete, aggregation_complete, summary_complete
- Timing metadata section in master summary report
- Baseline comparison against historical runs
- Real-time anomaly alerts if duration is suspicious

**See:** `skills/skill-timing/README.md` for full timing documentation.

## Filtering Options

**By Domain:**
```text
filter_pattern: rules/100-*.md  # Snowflake only
filter_pattern: rules/200-*.md  # Python only
filter_pattern: rules/300-*.md  # Shell only
```

**By Type:**
```text
filter_pattern: rules/*-core.md      # Core rules only
filter_pattern: rules/002*.md        # Governance rules only
```

## FAQ

### Q: What happens if the process is interrupted?

**A:** Use the resume capability. Set `skip_existing: true` and re-run. The skill will skip already-reviewed files and continue from where it left off.

### Q: Can I customize the output directory?

**A:** Yes, use the `output_root` parameter:
```text
output_root: quarterly-audit/
```
This writes reviews to `quarterly-audit/rule-reviews/` and summary to `quarterly-audit/summaries/` instead of `reviews/`. The skill auto-creates directories and normalizes trailing slashes. Relative paths including `../` are supported.

### Q: Can I force a re-review of all rules?

**A:** Yes. Set `skip_existing: false` to overwrite existing reviews with fresh evaluations.

### Q: How long does a full review take?

**A:** For 124 rules in FULL mode: 1-2 hours with parallel execution (default, 5 workers), or 5-10 hours sequential (3-5 minutes per rule).

### Q: Why is it so slow?

**A:** Each rule gets a complete agent-centric review using the full rubric. Shortcuts compromise review quality. The skill uses parallel sub-agents by default to balance speed with quality—each sub-agent has fresh context to prevent drift.

### Q: Where does the rubric come from?

**A:** The skill invokes the rule-reviewer skill for each rule, which uses rubric files in `skills/rule-reviewer/rubrics/` (actionability.md, completeness.md, consistency.md, parsability.md, token-efficiency.md, staleness.md, cross-agent-consistency.md) plus `_overlap-resolution.md` as the rubric.

### Q: Can I run reviews in parallel?

**A:** Yes! Parallel execution is now the default (`max_parallel: 5`). Each sub-agent gets fresh context, eliminating drift that occurs in long sequential sessions. Set `max_parallel: 1` for sequential execution if needed.

## Error Handling

**Review failure:** Continues with next file, logs error, marks FAILED in summary

**Context overflow:** Switches to minimal output mode, continues execution

**File write failure:** Prints OUTPUT_FILE directive for manual save, continues

**Empty rules directory:** Reports error, exits gracefully

## Success Criteria

✅ All matching rules reviewed (or filtered subset)  
✅ Individual review files written to `reviews/`  
✅ Master summary report generated with valid path  
✅ Prioritized improvement list included  
✅ No context overflow during execution  
✅ Resume capability functional (existing reviews skipped)  
✅ Error handling graceful (failed reviews don't stop batch)

## Support

For detailed documentation:
- **Skill README:** `skills/bulk-rule-reviewer/README.md`
- **Workflow guides:** `skills/bulk-rule-reviewer/workflows/*.md`
- **Examples:** `skills/bulk-rule-reviewer/examples/full-bulk-review.md`
- **Tests:** `skills/bulk-rule-reviewer/tests/validation-tests.md`

## Related Skills

- **rule-reviewer** - Single rule review
