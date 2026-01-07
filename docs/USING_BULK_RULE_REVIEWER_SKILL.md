# Using the Bulk Rule Reviewer Skill (Internal Only)

**Note:** The Bulk Rule Reviewer Skill is **not deployed** to team projects. It remains in the ai_coding_rules source repository for internal use only.

**Last Updated:** 2026-01-07

## Background

The bulk-rule-reviewer skill automates comprehensive agent-centric reviews of all rule files in the `rules/` directory, generating a consolidated priority report showing which rules need attention.

Key behaviors:

- Reviews all rules in `rules/` directory (or filtered subset)
- Invokes rule-reviewer skill for each rule individually
- Generates individual review files in `reviews/` directory
- Creates master summary report with prioritized improvement recommendations
- Supports resume capability for long-running batches
- Expected execution time: 5-10 hours for 113 rules (sequential)

## Why Not Deployed?

The bulk-rule-reviewer skill is designed for **rule maintainers** working in the source ai_coding_rules repository. It:

1. **Requires rule-reviewer skill** - Must invoke rule-reviewer for each file
2. **Writes to reviews/** - Directory structure specific to rule maintenance
3. **Targets rule repository** - Most useful for bulk rule quality audits
4. **Long-running process** - Takes 5-10 hours for full repository review

For deployed projects, teams should use the rule-reviewer skill directly for individual rule validation.

## Configuration

The skill is excluded from deployment in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",
    "rule-reviewer/",
    "bulk-rule-reviewer/",
]
```

## For ai_coding_rules Contributors

If you're working in the ai_coding_rules repository and want to run bulk rule reviews:

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

**Individual reviews:** `reviews/<rule-name>-<model>-<date>.md` (one per rule)

**Master summary:** `reviews/_bulk-review-<model>-<date>.md`

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
- All 6 dimensions evaluated per rule
- Expected duration: 5-10 hours for 113 rules
- Use for: Quarterly audits, pre-release validation

**FOCUSED Mode (Targeted):**
- Actionability + Completeness only
- Faster execution (2-3 hours)
- Use for: Quick quality checks

**STALENESS Mode (Periodic Maintenance):**
- Staleness dimension only
- Fastest execution (1-2 hours)
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

### Q: Can I force a re-review of all rules?

**A:** Yes. Set `skip_existing: false` to overwrite existing reviews with fresh evaluations.

### Q: How long does a full review take?

**A:** For 113 rules in FULL mode: 5-10 hours (3-5 minutes per rule). This is EXPECTED and REQUIRED for quality reviews.

### Q: Why is it so slow?

**A:** Each rule gets a complete agent-centric review using the full rubric. Shortcuts compromise review quality. The skill includes execution integrity warnings to prevent agents from optimizing for speed at the expense of accuracy.

### Q: Where does the rubric come from?

**A:** The skill invokes the rule-reviewer skill for each rule, which uses rubric files in `skills/rule-reviewer/rubrics/` (actionability.md, completeness.md, consistency.md, parsability.md, token-efficiency.md, staleness.md) as the rubric.

### Q: Can I run reviews in parallel?

**A:** Sequential execution (default: `max_parallel=1`) is recommended. Parallel execution is possible but may cause context management issues.

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

- **rule-reviewer** - Single rule review (required dependency)
- **rule-creator** - Create new rules (complementary)
- **skill-timing** - Execution timing instrumentation

