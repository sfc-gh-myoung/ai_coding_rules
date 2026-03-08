# Using the Rule Reviewer Skill

**Last Updated:** 2026-03-07

The Rule Reviewer Skill automates agent-centric rule reviews, scoring rules across 7 dimensions using a 100-point system optimized for AI agent understanding and executability. Reviews are written to `reviews/rule-reviews/` with no-overwrite safety.


## Quick Start

### 1. Load the skill

```text
Load skills/rule-reviewer/SKILL.md
```

### 2. Request a review

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_mode: FULL
```

The skill will prompt for any missing parameters (date, model).

### 3. Check the output

Reviews are written to `reviews/rule-reviews/<rule-name>-<model>-<date>.md`

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/rule-reviews/801-project-readme-claude-sonnet-45-2026-03-08.md
Overall: 85/100
Verdict: EXECUTABLE_WITH_REFINEMENTS
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive 7-dimension review | Standard rule validation |
| **FOCUSED** | Subset of dimensions only | Quick checks on specific areas |
| **STALENESS** | Reference and link validation | Periodic maintenance audits |

### FULL Mode

```text
target_file: rules/801-project-readme.md
review_mode: FULL
```

Reviews all 7 dimensions with complete scoring.

### FOCUSED Mode

```text
target_file: rules/801-project-readme.md
review_mode: FOCUSED
focus_dimensions: actionability, completeness
```

Reviews only specified dimensions. Useful for targeted validation.

### STALENESS Mode

```text
target_file: rules/801-project-readme.md
review_mode: STALENESS
```

Checks references, links, and example currency without full dimension scoring.


## Understanding Your Results

### Verdicts

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | **EXECUTABLE** | Agent can execute as-is |
| 80-89 | **EXECUTABLE_WITH_REFINEMENTS** | Minor refinements recommended |
| 60-79 | **NEEDS_REFINEMENT** | Significant gaps; agent may fail |
| <60 | **NOT_EXECUTABLE** | Major rework required |

### Scoring Dimensions

Rules are scored across 7 dimensions with weighted points:

**Critical Dimensions (50 points)** — Agent must execute without ambiguity:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Actionability | 25 | Can agent execute instructions without ambiguity? |
| Completeness | 25 | Are all required sections present with error handling? |

**Standard Dimensions (50 points)** — Important but recoverable:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Consistency | 15 | Does rule follow schema conventions and project standards? |
| Parsability | 15 | Does structure support automated parsing? |
| Staleness | 10 | Are references current and links valid? |
| Token Efficiency | 5 | Is content dense without redundancy? |
| Cross-Agent Consistency | 5 | Does rule work across all agent types? |

**Scoring Formula:** `Raw (0-10) × (Weight / 2) = Points`

### Priority Compliance Gate

Reviews evaluate rules against the Design Priority Hierarchy from `000-global-core.md`:

1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

**Impact on score:**
- 3-5 Priority 1 violations → Actionability capped at 15/25 (3/5)
- 6+ Priority 1 violations → Overall score capped at 60/100 (NEEDS_REFINEMENT)

### Blocking Issues

The Agent Execution Test counts issues that prevent autonomous execution:
- Ambiguous phrases ("consider", "as appropriate", "if needed")
- Implicit commands (descriptions instead of explicit instructions)
- Missing branches (no else/default/error handling)
- Undefined thresholds ("large", "significant", "appropriate")


## Advanced Usage

### Custom Output Directory

```text
output_root: quarterly-audit/
```

Writes to `quarterly-audit/rule-reviews/` instead of default `reviews/rule-reviews/`. The skill auto-creates directories and normalizes trailing slashes. Relative paths including `../` are supported.

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to output (duration, token usage, cost estimation).

### No-Overwrite Safety

If the output file exists, suffixes are appended: `-01.md`, `-02.md`, etc.


## FAQ

### What should I pass for `model`?

Prefer a slug like `claude-sonnet-45`. Raw model names are normalized automatically.

### Does `target_file` have to be under `rules/`?

The expected use case is reviewing files under `rules/`, but the skill can review any readable `.md` file. The output filename uses the base filename (without extension) of `target_file`.

### Where does the rubric come from?

The skill uses rubric files in `skills/rule-reviewer/rubrics/` (actionability.md, completeness.md, consistency.md, parsability.md, token-efficiency.md, staleness.md, cross-agent-consistency.md) plus `_overlap-resolution.md` for deterministic scoring.

### Can I use rule-reviewer in a deployed project?

Yes, this skill is available in deployed projects. You can also reference the rubric files in `skills/rule-reviewer/rubrics/` directly.


## Reference

### Architecture

```
Coordinator (Main Agent)
│
├── Phase 1: Setup
│   ├── Load rule content
│   ├── Load overlap resolution rules
│   └── Prepare shared context
│
├── Phase 2: Dimension Evaluation
│   ├── Actionability (25pts)
│   ├── Completeness (25pts)
│   ├── Consistency (15pts)
│   ├── Parsability (15pts)
│   ├── Staleness (10pts)
│   ├── Token Efficiency (5pts)
│   └── Cross-Agent Consistency (5pts)
│
├── Phase 3: Priority Compliance Check
│   └── Apply Design Priority Hierarchy caps
│
└── Phase 4: Aggregate & Report
    └── Generate unified review
```

### File Structure

```text
skills/rule-reviewer/
├── SKILL.md               # Main skill (entrypoint)
├── rubrics/               # Dimension scoring criteria
│   ├── actionability.md
│   ├── completeness.md
│   ├── consistency.md
│   ├── parsability.md
│   ├── token-efficiency.md
│   ├── staleness.md
│   ├── cross-agent-consistency.md
│   └── _overlap-resolution.md
└── tests/                 # Test cases
```

### Integration with Other Skills

**With bulk-rule-reviewer:** Run reviews across all rules in `rules/` directory with a single command.

**With skill-timing:** Enable `timing_enabled: true` for execution duration and cost tracking.

### Support

- **Rubric files:** `skills/rule-reviewer/rubrics/*.md`
- **Tests:** `skills/rule-reviewer/tests/*.md`
- **Timing system:** `skills/skill-timing/README.md`
