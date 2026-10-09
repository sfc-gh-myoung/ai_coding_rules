# Testing rule-creator

This guide is for maintainers. Use disposable outputs under the ignored `.workbench/` directory; preserve existing rules and do not run model generation without separate approval.

## Automated checks

Run from the configured repository environment:

```bash
uv run --locked pytest tests/cli/test_new.py tests/cli/test_validate.py tests/cli/test_tokens.py
uv run --locked ai-rules validate-skills skills/rule-creator
uv run --locked ai-rules rule-loader validate-trigger-contract
```

The CLI tests exercise scaffold generation and the active validator. They do not prove that a live agent followed the skill. The trigger-contract check verifies the schema-derived keyword bound across registered authoring surfaces.

## Workflow checks

Use the cases in [test-workflows.md](test-workflows.md) for a manual or approved live evaluation. Record source hashes, the model/runtime when applicable, actual commands, and outcomes.

- Discovery: inspect current frontmatter and the README category map, not a nonexistent index file. Confirm required owners were read and the selected name is unused.
- Generation: require v4 YAML, Scope, Contract, References order, and four non-empty required Contract subsections. Run the real validator; a heading count alone is insufficient.
- Population: inspect meaningful task instructions, safety boundaries, required dependencies, and correct examples. One completion checklist is enough; byte size or elapsed time does not establish completeness.
- Validation: require zero CRITICAL and HIGH findings and report lesser warnings. Missing tooling, missing reports, or no files checked remain validation gaps.
- Discovery verification: test representative and irrelevant requests against the actual matcher. No separate index or numeric table insertion is required.

## Negative controls

In disposable copies, reverse Contract and References and verify rejection. Empty each required Contract body separately and verify rejection. Confirm that code-fenced headings cannot satisfy real subsection requirements. Keep these cases in the permanent validator tests rather than inventing a second schema checker here.

Test filename collisions without `--force`; assert that original bytes are unchanged. Test missing inputs and unavailable tooling before writes. A live workflow must not call optional paid keyword generation when authorization is absent.

## Regression and reporting

- [ ] The skill's frontmatter and changelog version agree.
- [ ] All workflow/example links resolve and the entrypoint satisfies its own skill schema.
- [ ] Scaffold, validator, and token-tool checks pass with the active rule schema.
- [ ] Required safety and dependency instructions survive content population.
- [ ] Invalid controls fail for the intended reason rather than an unrelated setup error.
- [ ] Reports distinguish automated checks, manual review, live evaluation, skips, and blocked work.

After a skill or schema edit, rerun affected checks and inspect examples. Use the locked Python requirements from `pyproject.toml`. Do not fabricate runtime results or delete an incomplete rule as an automatic repair; preserve its evidence and change only authorized content.
