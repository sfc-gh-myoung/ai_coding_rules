---
schema_version: v4.0
rule_version: v3.0.0
description: "Integrate rule validation with automation using preserved exit status, structured diagnostics, bounded repairs, and failure-capable checks."
last_updated: 2026-09-30
keywords:
  - kw:ci/cd pipeline
  - kw:programmatic parsing
  - kw:automated fix iteration
  - kw:pre-commit hooks
  - kw:github actions workflow
  - kw:batch validation
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 002e-schema-validator-usage.md  # Core validation commands and error resolution
    - 002-rule-governance.md  # Schema requirements and active standards
    - 000-global-core.md  # Foundation for all rules
---
# Schema Validator Advanced: Automation and CI Integration

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when implementing validation automation.

## Scope

**What This Rule Covers:**
Run rule validation from hooks, CI, or local scripts without hiding failures or accepting empty validation runs.

**When to Load This Rule:**
- Parse validator output, configure a validation gate, or automate a narrow repair.
- For individual diagnostics and commands, use `002e-schema-validator-usage.md`.

## Contract

### Inputs and Prerequisites

- Read the current validator CLI, schema, project automation, and CI environment configuration.
- Identify the expected file set and the intended blocking severities.
- Obtain authorization for automated writes or external notifications. Validation itself does not authorize repairs or publication.

### Mandatory

- Preserve the validator's nonzero exit status. Never suppress a blocking failure with shell or CI error-ignore options.
- Prefer JSON for automation; parse the actual supported structure. Preserve stdout and stderr separately and treat malformed or missing JSON as an error, not a zero count.
- Verify that the expected files were checked. A zero-file result or a missing report is not a successful corpus gate.
- CRITICAL and HIGH findings block normal validation; apply stricter warning treatment only when the project explicitly selects it.
- Automate only reviewed, deterministic repairs within authorized files. Keyword selection and missing instruction bodies require content judgment, not arbitrary filler or boilerplate.
- Bound repair attempts with an explicit local policy and stop when the same diagnostic repeats without progress. Keep beforeimages and inspect diffs after each attempt.
- Do not modify the validator to accept invalid content. A checker defect needs a reproducer and a focused test that fails before the fix.

### Execution Steps

1. Use the project's existing validation entrypoint and locked dependencies. Confirm the working directory, schema, and target file set.
2. Run validation and capture exit status plus structured diagnostics. Distinguish execution failure from content failure.
3. Present a proposed repair for any change requiring judgment. Apply only authorized deterministic fixes and revalidate the affected files.
4. Prove that the integration fails on an intentionally invalid disposable fixture and passes a valid one. Verify that removing the expected inputs also fails the integration's completeness check.
5. Report results and remaining warnings. Deliver notifications only to an authorized destination and never include secrets or unrelated file content.

### Validation

- [ ] CI and hooks retain nonzero exit codes; no error-suppression path changes a failure to success.
- [ ] JSON parsing handles valid, invalid, missing, and truncated output without inventing a passing result.
- [ ] The expected file set is covered; no-op runs are identified.
- [ ] Repair attempts preserve unrelated edits and stop on unresolved or repeated errors.
- [ ] Negative controls demonstrate that the gate can fail on the intended defects.
- [ ] Logs distinguish executed checks, warnings, and unavailable checks.

If the runner lacks Python, uv, or the schema, fix its approved setup or report the gate blocked. Do not restore a modified schema from Git or install packages outside authorized setup. A text rerun can aid diagnosis but cannot erase the failed structured-output result.

## References

- `schemas/rule-schema.yml`: active severity and structural configuration.
- `src/ai_rules/commands/validate.py`: JSON output and exit-code implementation.
- `.github/workflows/ci.yml` and `Taskfile.yml`: current project integration rather than a copied historical workflow.

## Read-only subprocess example

Run from the repository root in the configured Python environment. This example checks a directory and rejects an empty result while retaining the validator's status.

```python
import json
import subprocess

result = subprocess.run(
    ["uv", "run", "--locked", "ai-rules", "validate", "rules/", "--json"],
    capture_output=True,
    text=True,
    check=False,
)
try:
    report = json.loads(result.stdout)
    total_files = report["summary"]["total_files"]
except (json.JSONDecodeError, KeyError, TypeError) as error:
    raise SystemExit(f"Invalid validation report: {error}") from error
if not isinstance(total_files, int) or total_files <= 0:
    raise SystemExit("No rule files were validated")
print(f"Validated {total_files} files; validator exit={result.returncode}")
raise SystemExit(result.returncode)
```

This is report handling, not a semantic content checker. Integrations that require a particular inventory must also compare the checked file identities with that inventory.
