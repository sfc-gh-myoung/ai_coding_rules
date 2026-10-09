---
schema_version: v4.0
rule_version: v5.0.0
description: "Safe markup and configuration file practices to prevent parsing errors and maintain consistency across YAML, TOML, environment files, and Markdown documentation. Covers YAML syntax safety, quoting"
last_updated: 2026-10-06
keywords:
  - kw:YAML syntax safety
  - kw:configuration file linting
  - kw:TOML validation
  - kw:Taskfile.yml patterns
  - kw:YAML anchors aliases
  - kw:secrets in version control
token_budget: ~1100
context_tier: Medium
depends:
  optional:
    - 202a-markdown-linting.md  # Markdown linting patterns and pymarkdownlnt configuration (Recommended)
    - 203-python-project-setup.md  # pyproject.toml configuration
    - 820-taskfile-automation.md
---
# Markup and Configuration File Validation

## Scope

**What This Rule Covers:**
Safe YAML/TOML/environment/Markdown syntax, layered command quoting, schema validation, configuration security and truthful tool availability.

**When to Load This Rule:**
When editing configuration/automation markup, diagnosing parser errors or validating Markdown/TOML/YAML and secret handling.

## Contract

### Inputs and Prerequisites

- Existing files, indentation/style, parser/version, schemas and current project automation.
- Actual installed validation tools; no assumed PyYAML or new dependency installation.
- Authorized configuration scope and approved secret mechanism.

### Mandatory

- Read before editing and preserve style. YAML normally uses spaces, not indentation tabs; two spaces is conventional, not a universal specification requirement. TOML has no mandatory four-space indentation.
- Quote ambiguous scalars such as colon-space strings, leading/trailing spaces, wildcard/alias-like values and intended string forms that the active parser may coerce. Valid URLs/Unicode values do not inherently break YAML.
- Structural bullets must be YAML syntax, not decorative Unicode; international text in values is allowed. Diagnose actual parser errors instead of blanket character bans.
- Validate syntax and schema before deployment. YAML uses an available safe parser; PyYAML is a separate dependency, not Python built-in. TOML can use tomllib on Python3.11+ when the configured interpreter supports it.
- Parsing does not prove runtime configuration valid. Check required fields, values, units, duplicates and application startup behavior with clear errors; use existing schemas for meaningful nested contracts, not arbitrary key-count mandates.
- Keep actual secrets out of versioned configs/env files. Ignoring a file does not remove already tracked secrets; report exposure and approved remediation without printing values. Provide secret-free example templates only.
- Separate YAML scalar escaping, Go/Jinja rendering, shell argument quoting and SQL binding; quote each at its own layer. Prefer helper scripts over nested shell fragments.
- Task deps may run concurrently; use ordered commands for dependent steps. Dynamic vars/status/preconditions can execute during discovery, so previews need source review.
- Anchors/aliases use safe bounded patterns supported by the parser; validate merge-key behavior rather than assuming every YAML dialect supports it. No secret-bearing anchors or deep opaque chains.
- If a validator is absent, use an existing safe syntax parser when available and disclose omitted lint/schema checks. Do not add TODO noise or declare full validation skipped/passed silently.

### Execution Steps

1. Inspect current config, active parser/schema, tooling and automation; identify exact changed semantics and authority.
2. Make minimal correctly quoted/indented edits, with comments for non-obvious units, overrides and external-system references.
3. Run syntax parser, applicable schema/lint and Markdown checks using the actual project environment.
4. Test safe configuration loading/required-value errors and automation command expansion without unauthorized deployment.
5. Fix exact findings, revalidate and report syntax/style/schema/runtime outcomes separately.

### Validation

- YAML/TOML parse under actual supported parser and duplicate/required-field/schema checks pass.
- Ambiguous scalars and command/template layers correctly quoted; Unicode data preserved where valid.
- Secrets not tracked/exposed, example values safe and required env/config documented.
- Anchors/aliases resolve as intended and automation sequencing/error propagation correct.
- Markdown checks use current project config; missing lint/runtime tools reported, not fabricated.
- Config changes documented and no unauthorized install/deployment/restart occurred.

## References

- [YAML specification](https://yaml.org/spec/)
- [yamllint](https://yamllint.readthedocs.io/en/stable/)
- [TOML specification](https://toml.io/en/)
- [Python tomllib](https://docs.python.org/3/library/tomllib.html)
- [PyYAML safe loading](https://pyyaml.org/wiki/PyYAMLDocumentation)
- `202a-markdown-linting.md` for Markdown validation.
