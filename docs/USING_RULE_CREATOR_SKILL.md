# Using the Rule Creator Skill

**Last Updated:** 2026-09-30

Use rule-creator to research, scaffold, populate, and validate a rule against the v4 contract. The skill lives in the source repository and is not included in the distributable plugin.

## Start a rule

```text
Use the rule-creator skill to create a rule for pytest security testing.
Domain: Python
Aspect: security
Context tier: High
Use supplied documentation only; do not call paid models.
```

The skill checks existing ownership and the current [rule-category map](../README.md#rule-categories) before choosing an unused filename. Specify a filename if needed, but an existing file is not overwritten automatically. ContextTier reflects importance and applicability, not a token-size range.

## Workflow

| Phase | Result |
|---|---|
| Discovery and research | Existing owners, applicable sources, available filename, dependency decisions |
| Template generation | A scaffold from `ai-rules new` |
| Content population | Task-specific instructions and typed YAML metadata |
| Validation | Executed structural checks plus separate semantic review |
| Keyword and discovery verification | Relevant/irrelevant request checks and integrated loader/plugin verification |

Model-assisted keyword generation is optional. The skill can use manually authored keywords; model calls require authorization for content transmission, model identity, and cost. No separate index file is generated.

## V4 authoring requirements

Required H2 order is **Scope, Contract, References**. Contract requires four meaningful subsections: Inputs and Prerequisites, Mandatory, Execution Steps, Validation. Forbidden and Output Format are optional when they add distinct requirements.

Keep one completion checklist under Validation. Show correct executable examples only and describe defects in prose. No fixed number of steps, examples, or anti-patterns is required. Preserve authorization, confidentiality, required reads, and safe recovery in the active rule or its required dependencies.

The seven required YAML fields are `schema_version`, `rule_version`, `last_updated`, `keywords`, `token_budget`, `context_tier`, and `depends`. Keywords have a combined bound of 5-11 typed entries. Token budgets are estimates of final text, not observed runtime usage.

## Verify the result

The skill reports the created path, commands run, exit codes, reviewed warnings, and unavailable checks. It must replace scaffold placeholders with meaningful content before reporting completion.

```bash
uv run --locked ai-rules validate rules/<created-rule>.md --verbose
uv run --locked ai-rules rule-loader validate
uv run --locked ai-rules rule-loader validate-trigger-contract
make plugin-verify
```

Replace the path placeholder with the actual rule. CRITICAL and HIGH findings block normal validation; a documented exception does not convert them to success. After three unsuccessful repair attempts, the skill reports the remaining blocker.

A schema pass proves structure, not technical correctness or agent behavior. Inspect dependency ownership, sources, safety boundaries, and expected outcomes separately. A short file or a fast run is not evidence of incomplete work; a canned transcript or a large file is not evidence of completion.

## Troubleshooting

- Missing or empty Contract subsection: supply task-specific content under the required heading. Do not add a sibling heading as a substitute.
- Wrong section order: move complete sections into the v4 order while preserving their contents.
- Invalid keywords: inspect parsed YAML and choose relevant typed entries within the bound, not filler.
- Existing filename: inspect the owner and choose an authorized update or a new name. Do not force an overwrite.
- Missing tools or external sources: report the missing dependency or unsupported claim. Do not silently install tools or invent evidence.

## Deployment exclusion

The plugin build includes rule-loader and show-rules. Rule-creator requires the repository-local schemas, authoring CLI, and write access, so it remains source-only. Teams can load [SKILL.md](../skills/rule-creator/SKILL.md) from the source repository or follow [the rule creation guide](../rules/002a-rule-creation.md).

## References

- [Workflow files](../skills/rule-creator/workflows/)
- [Maintainer test guide](../skills/rule-creator/tests/TESTING.md)
- [Rule governance](../rules/002-rule-governance.md)
- [Schema reference](../schemas/README.md)
- [Contribution workflow](../CONTRIBUTING.md)
