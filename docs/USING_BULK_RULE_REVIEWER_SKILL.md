# Using the Bulk Rule Reviewer Skill

**Last Updated:** 2026-03-08

The Bulk Rule Reviewer Skill executes comprehensive agent-centric reviews on all rule files in the `rules/` directory, generating a consolidated priority report showing which rules need attention. It orchestrates the rule-reviewer skill for each rule, maintaining the same quality standards as individual reviews.

**Primary Use Cases:**
- Periodic quality audits (quarterly/monthly)
- Pre-release validation before major versions
- Technical debt tracking and prioritization
- Baseline quality measurement


## Quick Start

### 1. Load the skill

```text
Load skills/bulk-rule-reviewer/SKILL.md
```

### 2. Request a bulk review

```text
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

### 3. Check the output

On success:

```text
✓ Bulk review complete

Individual reviews: reviews/rule-reviews/<rule-name>-claude-sonnet-45-2026-01-06.md (129 files)
Master summary: reviews/summaries/_bulk-review-claude-sonnet-45-2026-01-06.md
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive evaluation (all 7 dimensions) | Quarterly audits, pre-release validation |
| **FOCUSED** | Actionability + Completeness only | Quick quality checks |
| **STALENESS** | Freshness dimension only | Monthly maintenance, link rot detection |

### FULL Mode

```text
review_mode: FULL
```

All 7 dimensions evaluated per rule. Expected duration: ~50 minutes (parallel with 5 workers).

### FOCUSED Mode

```text
review_mode: FOCUSED
```

Faster execution (~1 hour parallel). Evaluates only the two most critical dimensions.

### STALENESS Mode

```text
review_mode: STALENESS
```

Fastest execution (~30 min parallel). Checks for outdated references and deprecated patterns.


## Understanding Your Results

### Master Summary Report

The master summary (`reviews/summaries/_bulk-review-<model>-<date>.md`) includes:

| Section | Contents |
|---------|----------|
| **Executive Summary** | Score distribution, dimension analysis, critical issues |
| **Priority 1: Urgent** | Score <60, NOT_EXECUTABLE — requires immediate attention |
| **Priority 2: High** | Score 60-79, NEEDS_REFINEMENT — significant work needed |
| **Priority 3: Medium** | Score 80-89, EXECUTABLE_WITH_REFINEMENTS — minor fixes |
| **Priority 4: Excellent** | Score 90-100, EXECUTABLE — production-ready |
| **Failed Reviews** | Execution errors requiring manual review |
| **Top 10 Recommendations** | Prioritized by impact × effort ratio |
| **Next Steps** | Immediate/short-term/long-term actions |
| **Appendix** | All rules sorted by score with review links |

### Individual Review Files

Each rule gets a review file at `reviews/rule-reviews/<rule-name>-<model>-<date>.md` containing:
- Overall score (0-100)
- Dimension scores (Actionability, Completeness, etc.)
- Verdict (EXECUTABLE, NEEDS_REFINEMENT, etc.)
- Critical issues list
- Recommendations

### Score Distribution

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | **EXECUTABLE** | Production-ready, quarterly staleness reviews only |
| 80-89 | **EXECUTABLE_WITH_REFINEMENTS** | Minor fixes needed |
| 60-79 | **NEEDS_REFINEMENT** | Significant refinement required |
| <60 | **NOT_EXECUTABLE** | Major revision needed |


## Advanced Usage

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `review_date` | YYYY-MM-DD | Today | Date stamp for review files |
| `review_mode` | Enum | FULL | Review depth: `FULL`, `FOCUSED`, `STALENESS` |
| `model` | String | claude-sonnet-45 | Model identifier for file naming |
| `output_root` | String | `reviews/` | Output directory for reviews |
| `filter_pattern` | Glob | `rules/*.md` | Filter rules by pattern |
| `skip_existing` | Boolean | `true` | Skip files with existing reviews |
| `max_parallel` | Integer | `5` | Concurrent sub-agents (1-10) |
| `timing_enabled` | Boolean | `false` | Enable execution timing |

### Custom Output Directory

```text
output_root: quarterly-audit/
```

Writes to `quarterly-audit/rule-reviews/` and `quarterly-audit/summaries/` instead of default `reviews/`. The skill auto-creates directories. Relative paths including `../` are supported.

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to the master summary:

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

**Checkpoints tracked:** `skill_loaded` → `discovery_complete` → `reviews_complete` → `aggregation_complete` → `summary_complete`

### Execution Modes

| Mode | Setting | Speed | Use Case |
|------|---------|-------|----------|
| **Parallel** (default) | `max_parallel: 5` | ~50 minutes | Production reviews |
| **Sequential** | `max_parallel: 1` | 4-6 hours | Debugging, low-resource |

Parallel execution launches N sub-agents, each with fresh context to prevent drift.

### Resume Capability

The skill supports resuming after interruptions via `skip_existing: true` (default).

**How it works:**
1. Before reviewing each rule, check if review file exists
2. If exists: Load score from existing file, mark as SKIPPED
3. If not exists: Invoke rule-reviewer normally

```text
✓ Skipping 000-global-core (review exists)
✓ Skipping 001-memory-bank (review exists)
[67/129] Reviewing: rules/067-new-rule.md
```

**Benefits:** Resume after interruption without re-work. Save 3-4 hours when resuming mid-batch.

### Filtering Options

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


## Execution Integrity

**CRITICAL:** Bulk reviews take ~50 minutes (parallel) or 4-6 hours (sequential). This is expected and required.

### Verification During Execution

- Each rule should take 90-120 seconds to review
- Progress updates every 10 reviews
- Schema validator executed for each rule
- Rubrics loaded and applied for dimension scoring

### Verification After Execution

- Review file sizes: 3000-8000 bytes each
- Execution time: ~50 minutes for 100+ rules (parallel)
- Spot-check reviews for complete sections

### Red Flags

| Indicator | Problem |
|-----------|---------|
| Completes in <30 min for 100+ rules | Possible shortcuts |
| Review files <2000 bytes | Incomplete reviews |
| Missing sections in review files | Abbreviated execution |
| Schema validation not executed | Skipped quality checks |


## FAQ

### What happens if the process is interrupted?

Use the resume capability. Set `skip_existing: true` (default) and re-run. The skill skips already-reviewed files and continues from where it left off.

### Can I force a re-review of all rules?

Yes. Set `skip_existing: false` to overwrite existing reviews with fresh evaluations.

### How long does a full review take?

For ~129 rules in FULL mode: ~50 minutes with parallel execution (5 workers), or 4-6 hours sequential (90-120 seconds per rule).

### Why is it slow?

Each rule gets a complete agent-centric review using the full rubric. Shortcuts compromise review quality. The parallel execution provides 5× speedup while maintaining quality through fresh context per sub-agent.

### Where does the rubric come from?

The skill invokes rule-reviewer for each rule, which uses rubric files in `skills/rule-reviewer/rubrics/` plus `_overlap-resolution.md` to prevent double-counting.

### Reviews taking too long?

Use `FOCUSED` mode for faster execution (Actionability and Completeness only), or filter to a subset with `filter_pattern`.

### Context overflow mid-batch?

Use resume capability (`skip_existing: true`) and reduce scope with `filter_pattern` (e.g., review 100-series, then 200-series separately).

### Master summary not generated?

Check if all reviews failed. Fix rule files with malformed markdown and re-run.


## Reference

### Architecture

```text
Bulk Review Orchestrator
│
├── Stage 1: Discovery (<1 second)
│   ├── Find all .md files in rules/
│   ├── Apply filter_pattern
│   └── Sort alphabetically
│
├── Stage 2: Review Execution (1-2 hours parallel)
│   ├── Partition rules into N groups (N = max_parallel)
│   ├── Launch N sub-agents with fresh context
│   ├── Each sub-agent: load rule-reviewer, process rules
│   └── Monitor progress, aggregate results
│
├── Stage 3: Aggregation (<5 seconds)
│   ├── Extract scores/verdicts from review files
│   ├── Calculate statistics (averages, distributions)
│   └── Group by priority tiers
│
└── Stage 4: Summary Report (<2 seconds)
    ├── Generate master markdown report
    ├── Prioritize recommendations
    └── Write to file
```

### File Structure

```text
skills/bulk-rule-reviewer/
├── SKILL.md                       # Main skill (entrypoint)
├── CRITICAL_CONTEXT.md            # Execution integrity rules
├── examples/
│   ├── full-bulk-review.md        # Complete 113-rule walkthrough
│   └── shortcut-prevention.md     # Anti-shortcut patterns
├── tests/
│   └── validation-tests.md        # Validation test cases
└── workflows/
    ├── discovery.md               # Stage 1: File discovery
    ├── review-execution.md        # Stage 2: Rule-reviewer orchestration
    ├── parallel-execution.md      # Parallel sub-agent strategy
    ├── subagent-prompt-template.md # Sub-agent prompt template
    ├── aggregation.md             # Stage 3: Score extraction
    ├── summary-report.md          # Stage 4: Report generation
    └── input-validation.md        # Input validation workflow
```

### Error Handling

| Error | Behavior |
|-------|----------|
| Review failure | Log error, mark FAILED, continue with next rule |
| Empty rules directory | Exit with error, no summary generated |
| Context overflow | Switch to minimal output mode, continue |
| File write failure | Print OUTPUT_FILE directive for manual save |

### Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| **rule-reviewer** | Invoked for each individual rule review |
| **skill-timing** | Provides execution timing when enabled |

### Deployment

This skill is **internal-only** and is not deployed to team projects. It remains in the ai_coding_rules source repository for bulk rule maintenance and quality audits.

### Support

- **Skill entrypoint:** `skills/bulk-rule-reviewer/SKILL.md`
- **Workflow guides:** `skills/bulk-rule-reviewer/workflows/*.md`
- **Examples:** `skills/bulk-rule-reviewer/examples/full-bulk-review.md`
- **Tests:** `skills/bulk-rule-reviewer/tests/validation-tests.md`
- **Timing system:** `skills/skill-timing/README.md` 
