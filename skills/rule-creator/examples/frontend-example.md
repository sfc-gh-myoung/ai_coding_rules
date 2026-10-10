# Example: Frontend Rule Creation

This is an illustrative workflow, not a recorded successful run or a source of current frontend-library specifications.

## Request

```text
Create a rule for DaisyUI theme customization. Check existing coverage first and use documentation matching the project's installed version.
```

## Discovery

Use the current loader and rule frontmatter to find existing coverage. Read the applicable frontend owner and its required dependencies. Check the README category map and actual filename availability rather than assuming a historical number remains free.

Inspect the project's dependency versions and current primary documentation before stating configuration requirements. Record source links and unresolved claims. Select relevant typed keywords within the active schema's combined bound; a keyword self-match alone is not a sufficient discovery test.

## Generate and populate

Substitute the selected unused name:

```bash
uv run ai-rules new <NNN-technology-aspect> --context-tier Medium --output-dir rules/
```

Read the result and populate v4 YAML metadata. Write Scope once, then Contract with meaningful Inputs and Prerequisites, Mandatory, Execution Steps, and Validation. Place References after Contract.

Keep the applicable domain core required when the procedure depends on it. Include version-specific configuration examples only after verifying them. Describe defects in prose and show correct code. Keep one completion checklist with actual build, accessibility, and behavior checks appropriate to the project; do not invent performance thresholds or require a fixed number of examples.

## Validate and verify discovery

```bash
uv run ai-rules validate rules/<NNN-technology-aspect>.md --verbose
uv run ai-rules tokens rules/<NNN-technology-aspect>.md --dry-run
uv run ai-rules rule-loader validate
uv run ai-rules rule-loader validate-trigger-contract
make plugin-verify
```

Record actual results. Resolve CRITICAL and HIGH findings without weakening checks. Test a representative relevant request and an irrelevant request against the matcher. Model-assisted keyword generation remains optional and requires authorization.

## Expected handoff

Return the populated rule path, reviewed dependency/keyword metadata, executed validation results, and any unverified runtime behavior. No separate index entry, canned success transcript, runtime duration, or claimed percentage saving is part of this example.
