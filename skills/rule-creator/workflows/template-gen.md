# Phase 2: Template Generation

## Purpose

Generate a v4 scaffold with `ai-rules new`. A structurally valid scaffold is not a completed rule.

## Inputs

- The domain, unused filename, and intended scope from discovery.
- A ContextTier chosen for importance and applicability, not file size.
- An authorized output directory and access to the project CLI.

## Outputs

A new rule with YAML frontmatter, ordered Scope, Contract, References sections, and four non-empty required Contract subsections ready for task-specific content.

## Workflow

1. Check the current README domain map and existing filenames. Use three digits, an optional single lowercase suffix letter, and hyphenated lowercase words.
2. Choose Critical, High, Medium, or Low according to the rule's role. Do not derive priority from a token range.
3. Replace the placeholders below and run the generator in the repository's configured environment:

   ```bash
   uv run ai-rules new <NNN-technology-aspect> --context-tier Medium --output-dir rules/
   ```

4. Check the exit code and read the created file. Confirm `schema_version: v4.0`, `rule_version: v1.0.0`, the current date, and all required metadata fields.
5. Confirm Scope, Contract, References order. Contract must contain Inputs and Prerequisites, Mandatory, Execution Steps, and Validation with meaningful bodies after population. Use the active schema for placement limits.
6. Carry the path, researched requirements, keyword candidates, dependency decisions, and references to [content population](content-population.md).

Use [the authoring companion](../../../rules/examples/002a-rule-template.md) for the body layout and [the complete synthetic rule](../../../rules/examples/002-rule-governance-structure-example.md) for a full structural example. Keep the CLI template as the scaffold source rather than maintaining another copy here.

## Failure handling

- Existing file: read it and determine whether this is an update or a naming collision. Never retry with `--force` without overwrite authorization, even when the file contains placeholders.
- Invalid filename or tier: correct the supplied value from the actual diagnostic and retry.
- Missing CLI or Python environment: use approved project setup or report the blocker. Do not install tools silently or assume an absolute path from another machine.
- Unexpected scaffold structure: preserve the output and report the mismatch with the active schema. Do not lower validation requirements.

## Completion

- [ ] Generator exited zero and created the intended unused file.
- [ ] YAML contains the required fields and schema_version v4.0.
- [ ] Required H2 sections and four Contract subsections are present in order.
- [ ] No arbitrary step count, anti-pattern gallery, or duplicate checklist was added.
- [ ] The scaffold is handed to content population, not reported as production-ready.
