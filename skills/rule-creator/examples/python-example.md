# Example: Python Library Rule Creation

This walkthrough illustrates authoring a pytest-mock rule. It does not record an executed run or prescribe mocking over the project's existing test strategy.

## Request

```text
Create a focused rule for pytest-mock where our tests need controlled external dependencies. Preserve the existing testing policy.
```

## Workflow

1. Discover existing Python/testing owners and read them. Check whether extending an existing rule is sufficient before choosing an unused Python-domain filename.
2. Read the project's dependency versions, test patterns, and current library documentation. Distinguish repository preferences from library requirements.
3. Generate a scaffold with `uv run ai-rules new <NNN-python-aspect> --context-tier Medium`, replacing the filename placeholder.
4. Populate YAML frontmatter and Scope, Contract, References. Include the four meaningful required Contract subsections and one completion checklist. Keep Python/testing owners required when the procedure relies on them.
5. Add only correct examples that demonstrate a distinct ambiguity, with imports, setup, and expected assertions. Explain avoided failures in prose instead of embedding broken code.
6. Validate the populated rule, preview its token estimate with `--dry-run`, and verify representative discovery and plugin fidelity through the creator workflows.

## Expected result

Return the rule path and actual validation evidence, including zero CRITICAL and HIGH findings. Review keyword relevance and dependency ownership separately from schema success. Manual keyword selection must remain available when paid generation is not authorized.

Do not create a separate index, copy a historical filename over an existing rule, or claim runtime library verification from a Markdown check. Report any unverified technical assumptions.
