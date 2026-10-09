# Review Eval Corpus

Eval harness for `rule-review-result/v1` schema compliance and quality metrics.

## Purpose

Verifies that the review validator and renderer behave correctly across a representative
corpus of rule review artifacts. Metrics are **informational** — thresholds below are a
starting baseline and must be promoted to blocking only after a reviewed model baseline exists.

## Corpus Composition

### Discovery corpus (rule-loader trigger precision/recall)

≥3 positive prompts and ≥2 negative prompts per canonical skill:

| Skill | Positive trigger phrases | Negative trigger phrases |
|-------|--------------------------|--------------------------|
| rule-loader | "load rules for python", "which rules apply to .py", "match rules for snowflake sql" | "review my rule", "bulk audit rules" |
| rule-reviewer | "review this rule", "score rule executability", "FULL mode review" | "load rules", "aggregate reviews" |
| bulk-rule-reviewer | "audit all rules", "score every rule", "bulk review" | "single rule review", "load matcher" |

### Reviewer corpus (review quality)

Three rule quality tiers used as inputs:
- **Strong rule** (`rules/000-global-core.md`) — expected: high score, low blocking count
- **Ambiguous rule** (synthesized fixture `tests/reviewer_eval/fixtures/ambiguous-rule.md`) — expected: medium score
- **Weak rule** (synthesized fixture `tests/reviewer_eval/fixtures/weak-rule.md`) — expected: low score

### Pinned model identity

Evals reference the model slug from the `producer.model` field in each review artifact.
Fixtures use `"claude-sonnet-4-6"` as the canonical test identity. No live model calls
are made in the eval harness; inputs are pre-constructed JSON fixtures.

## Metrics (informational)

| Metric | Description | Informational threshold |
|--------|-------------|------------------------|
| schema_compliance | % of review artifacts passing `validate_review_result` | ≥ 95% |
| score_variance | Std dev of scores across repeated runs of same input | ≤ 5 points |
| finding_jaccard | Jaccard similarity of finding IDs across repeated runs | ≥ 0.6 |
| citation_validity | % of source evidence locators matching `path:line` format | ≥ 90% |
| trigger_recall | % of positive prompts matching their expected skill | ≥ 80% |

Thresholds are informational until a reviewed baseline exists with ≥3 runs per corpus item.

## Threshold Policy

Thresholds below 100% are **informational** — a failing metric triggers a warning but does
**not** block CI. Before promoting any threshold to blocking:
1. Collect ≥3 independent runs against the same input corpus.
2. Document the baseline in this README under **Baseline Records**.
3. Get plan-owner sign-off on the specific threshold value.

## Baseline Records

*(Empty — awaiting first eval run.)*
