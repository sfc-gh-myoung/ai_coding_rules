# Phase 4: Validation

## Purpose

Validate the populated rule against the active schema and review its execution contract. Zero CRITICAL and HIGH findings are required; semantic review is a separate gate.

## Inputs

- The populated rule and expected dependency/keyword metadata.
- The current project validator and schema.
- A beforeimage for any existing file being updated.

## Outputs

Executed validation results, reviewed warnings, and a rule with no unresolved structural or semantic blockers. An unavailable check remains blocked rather than passed.

## Workflow

1. Replace the path placeholder and run the focused check:

   ```bash
   uv run ai-rules validate rules/<NNN-technology-aspect>.md --verbose
   ```

2. Retain the exit code and diagnostics. Exit zero means no blocking findings under the selected mode, not proof that every instruction is correct. For automation, use `--json` and the handling in `rules/002f-schema-validator-advanced.md`.
3. Read the affected lines and active schema before fixing a diagnostic. Repair the cause without lowering severity, adding exemptions, or filling missing instructions with generic text.
4. Rerun the focused check after every repair. Stop and report the blocker if three repair attempts do not resolve it; this is the skill's retry policy, not a schema limit.
5. Review prerequisites, authorization, meaningful outcomes, failure handling, correct examples, and required dependency ownership. Check the final token estimate with `--dry-run`.
6. Continue to [keyword and discovery verification](indexing.md). Revalidate after that phase if metadata changes.

## Repairs by category

- Missing metadata: populate the required YAML fields. Keyword counts apply to parsed typed entries, not commas in the file. Preserve the schema-derived combined 5-11 bound and relevance.
- Invalid budget or version: use `~NUMBER` and `vMAJOR.MINOR.PATCH` respectively. Derive the budget from the final text.
- Wrong order: move complete sections into Scope, Contract, References order without losing content.
- Missing or empty Contract body: supply the actual prerequisites, constraints, actions, or checks under the four required subsections. A sibling heading does not fill an empty subsection.
- Late Contract: apply the active schema's placement configuration, not a copied historical line limit.
- Broken link or dependency: verify the intended owner and exact path. Do not silently drop a required read.

Do not require retired Purpose, Quick Start, Related Rules, anti-pattern galleries, or Post-Execution Checklist sections. Forbidden and Output Format are optional when they add distinct requirements.

## Completion

- [ ] The real validator ran against the intended file and returned zero.
- [ ] CRITICAL and HIGH findings are resolved. Lesser findings were reviewed and retained warnings are disclosed.
- [ ] Required section bodies contain meaningful instructions, not merely headings or placeholders.
- [ ] Technical and safety requirements were reviewed independently of structural validation.
- [ ] Repairs preserve unrelated changes; tool failures and unexecuted checks are reported accurately.

If the CLI or schema is unavailable, inspect the approved project setup and report what is missing. Do not restore files destructively, install tools without authorization, or substitute a manual inspection for a passing automated check.
