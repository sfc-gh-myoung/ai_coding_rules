# Using the Rule Review Prompt

This file explains how to use the Agent-Centric Rule Review prompt template in
`skills/rule-reviewer/PROMPT.md`.

## What this is for

Use this prompt to get consistent, actionable assessments from any AI model when
reviewing rule files.
The target user is an **AI agent** following instructions, not a human reading
documentation.

**Tested Models:**

- GPT-4o
- GPT-5.1
- GPT-5.2
- Claude Sonnet 4.5
- Claude Opus 4.5
- Gemini 2.5 Pro
- Gemini 3 Pro

## How to run a review

1. Copy the full prompt template from `skills/rule-reviewer/PROMPT.md` into your model
   session.
2. Fill in:
   - **Target File** (the rule file to review)
   - **Review Date** (YYYY-MM-DD)
   - **Review Mode** (FULL | FOCUSED | STALENESS)
3. Submit the prompt.
4. Save the output to `reviews/` using the filename format required by the template:
   - `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

## Review Modes

### FULL Mode (Comprehensive)

Use for new rules or major revisions. Evaluates all 6 criteria with detailed recommendations.

### FOCUSED Mode (Targeted)

Use when you know specific areas need attention. Specify which criteria to evaluate.

### STALENESS Mode (Periodic Maintenance)

Use for quarterly/annual rule audits. Focuses on criteria 5-6 (Token Efficiency,
Staleness) plus dependency drift.

**For FOCUSED/STALENESS modes:**
Skip the mandatory verification tables unless you are explicitly reviewing:

- **Actionability** (Threshold Audit)
- **Consistency** (Example-Mandate Alignment)
- **Token Efficiency** (Token Budget Verification)

## Usage Examples

### Example 1: Full Review

```text
Review rules/002b-rule-optimization.md using the Agent-Centric Rule Review criteria.
Review Date: 2025-12-12
Review Mode: FULL
```

### Example 2: Focused Review

```text
Review rules/200-python-core.md using Agent-Centric Rule Review.
Review Date: 2025-12-12
Review Mode: FOCUSED
Focus Areas: Actionability, Completeness
```

### Example 3: Staleness Check (Periodic Maintenance)

```text
Review rules/206-python-pytest.md using Agent-Centric Rule Review.
Review Date: 2025-12-12
Review Mode: STALENESS
Context: Quarterly rule audit - check for outdated pytest patterns, deprecated fixtures,
or version-specific guidance that may need updating.
```

### Example 4: Batch Staleness Audit

```text
Perform a STALENESS mode review on these rules:
- rules/200-python-core.md
- rules/201-python-lint-format.md
- rules/206-python-pytest.md

Review Date: 2025-12-12
Focus: Identify any Python ecosystem changes since last review (tool versions,
deprecated patterns, new best practices).
```

### Example 5: Comparative Review

```text
Compare rules/101-snowflake-streamlit-core.md against the Agent-Centric Rule Review
criteria.
How does it compare to rules/200-python-core.md?
Review Date: 2025-12-12
Review Mode: FULL
```

## Periodic Review Schedule

### Recommended Cadence

| Rule Type | Review Frequency | Mode |
|----------|------------------|------|
| Foundation (000-*) | Quarterly | FULL |
| Domain Cores (1XX, 2XX, etc.) | Quarterly | STALENESS |
| Specialized/Activity Rules | Semi-annually | STALENESS |
| Reference Rules (>5000 tokens) | Annually | STALENESS |

### Staleness Triggers (Review Immediately)

- **Major tool release:** New Python version, Ruff major update, pytest breaking
  changes
- **Framework deprecation:** Library sunset, API retirement
- **Industry shift:** New security standards, compliance requirements
- **Agent feedback:** Repeated failures or confusion on specific rules

### Review Tracking

Maintain a review log with:

```markdown
| Rule | Last Review | Reviewer Model | Score | Next Review |
|------|-------------|----------------|-------|-------------|
| 000-global-core.md | 2025-12-12 | Claude Opus 4.5 | 28/30 | 2026-03-12 |
| 200-python-core.md | 2025-12-12 | GPT-5.1 | 25/30 | 2026-03-12 |
```

## Cross-Model Validation (Recommended for Critical Rules)

For critical rules (000-*, domain cores), run reviews on **multiple models** (2-3
recommended) and compare.

### Recommended Workflow

1. Run 2-3 models on critical rules (000-*, domain cores)
2. Merge findings, prioritizing consensus issues
3. Investigate model-specific findings as potential ambiguity indicators
4. Use single-model review for specialized rules (lower stakes)

### Model Selection Guidance

Based on observed patterns across multiple reviews:

- **GPT-4o/5.x**: strict consistency checks; good at finding subtle logic issues
- **Claude Sonnet 4.5**: comprehensive coverage; strong at actionable recommendations
- **Claude Opus 4.5**: balanced perspective; good at synthesizing findings
- **Gemini 2.5/3 Pro**: strong structural analysis; good at technical validation

**Merge strategy:**
1. Start with most comprehensive review (usually Sonnet)
2. Add unique findings from other models
3. Prioritize consensus issues highest
4. Flag model-specific findings as "potential ambiguity - verify"

## Related Resources

- **Rule Governance:** `rules/002-rule-governance.md` - Schema and format requirements
- **Rule Optimization:** `rules/002b-rule-optimization.md` - Token budget and sizing
  guidelines
- **Schema Validator:** `scripts/schema_validator.py` - Automated format validation
- **Token Validator:** `scripts/token_validator.py` - Budget accuracy verification
