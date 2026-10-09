# Example: FULL Review

## Invocation

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_date: <current-date>
review_mode: FULL
model: <actual-model-slug>
output_root: reviews/
```

Resolve placeholders through the skill's parameter workflow. This is an illustrative procedure, not a claim that the named rule has the findings below.

## Review workflow

1. Read the entire target and required review guidance. Preserve the input rule unchanged.
2. For an operational rule, run `uv run --locked ai-rules validate <target_file> --json`. Preserve exit status and real diagnostics; do not infer zero errors from missing output.
3. Check the v4 order Scope, Contract, References and four meaningful required Contract subsections. References before Contract is the invalid order, not the reverse.
4. Review semantic requirements independently: task applicability, safety, required dependencies, outputs, failure handling, one completion checklist, and positive examples. Do not invent thresholds or require an unnecessary else branch.
5. Build each issue inventory and apply the current six-dimension rubrics. Use 0-10 raw scores with weights from `references/reviewer-defaults.yml`; respect caps without copying an old sample score.
6. Assemble canonical review JSON, validate it, render Markdown, and verify the pair using the commands in SKILL.md. Apply no-overwrite naming to both artifacts.

## Illustrative structural finding

If the actual validator reports References before Contract, record its HIGH severity and real line number. Recommend moving the complete References section after Contract while preserving source links. Do not remove references to silence the finding.

If a required Contract subsection is empty, recommend its actual task-specific content, not only a new heading. Omitted optional Forbidden or Output Format subsections are not defects by themselves.

## Outputs

The primary artifact is `{output_root}/rule-reviews/<rule>-<model>-<date>.json`; the same-stem `.md` is derived. The report contains executed schema findings, line-supported semantic findings, scores calculated from actual inventories, and explicit validation limitations.

Do not mark a schema-invalid rule as passing because the review itself completed. Do not claim paid model comparisons, runtime example execution, or documentation checks that were not performed.
