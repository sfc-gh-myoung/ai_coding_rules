---
schema_version: v4.0
rule_version: v3.0.0
description: "Reserved character handling for Snowflake CLI tools including snow sql, snowsql, and dbt/Jinja contexts. Covers &, <%, %>, {{, }} template characters and SQL single-quote escaping."
last_updated: 2026-10-06
keywords:
  - kw:cli compatibility
  - kw:ampersand escaping
  - kw:template expansion
  - kw:enable-templating flag
  - kw:brand name preservation
  - kw:snow sql tool
token_budget: ~900
context_tier: Low
depends:
  required:
    - 102-snowflake-sql-core.md  # SQL file patterns
---
# Snowflake SQL: Reserved Characters and CLI Compatibility

## Scope

**What This Rule Covers:**
Client-side template expansion versus SQL quoting, preserving legitimate ampersands/apostrophes/template-like data in Snowflake CLI, SnowSQL and dbt/Jinja workflows.

**When to Load This Rule:**
When SQL text contains ampersands, template markers or apostrophes, or CLI rendering reports undefined variables.

## Contract

### Inputs and Prerequisites

- Exact input SQL/data, execution client/version and actual renderer settings.
- Knowledge of whether template substitution is intended; approved target and separate execution permission.

### Mandatory

- Preserve data exactly. Never replace `&` with `and`, remove template-like characters or change legitimate brand names to work around rendering.
- Distinguish Snowflake SQL escaping from preprocessing: a SQL literal can still be interpreted by an enabled client renderer before Snowflake receives it.
- For non-templated `snow sql`, use its documented `--enable-templating NONE` mode; this flag is not automatically supported by SnowSQL or dbt.
- Snowflake CLI STANDARD resolves `<% ... %>`, LEGACY resolves SnowSQL-style ampersand variables, and JINJA resolves `{{ ... }}`. Explicitly select only needed modes; inspect current defaults/version.
- When templates are required, use the chosen renderer's documented escaping/raw mechanisms or parameterized values to preserve literal data. Do not forbid legitimate markers in data merely because the renderer is enabled.
- Double apostrophes within SQL single-quoted literals (`Frank''s`) and bind untrusted values where supported. Shell quoting is another layer, not a substitute for SQL binding.
- Do not concatenate user input or secret values into command/SQL strings; keep connection secrets in approved stores.

### Execution Steps

1. Inspect the SQL and error message, identify the actual client/templating mode and whether substitution is intentional.
2. Disable rendering for non-templated Snowflake CLI input, or use documented mode-specific literal escaping when rendering is required.
3. Preserve all original values and apply SQL apostrophe escaping/binding independently of client rendering.
4. Check the locally rendered output for unresolved variables and unintended substitutions without executing cloud mutations.
5. Execute only with separate authorization, then compare actual stored/output values when permitted. If unavailable, report rendering/runtime checks unverified.

### Validation

- Correct client-specific syntax and flags, no universal SnowSQL/dbt flag assumption.
- Input/rendered values preserve ampersands, quotes and literal template markers exactly.
- No undefined-variable errors or accidental interpolation; intended substitutions are documented.
- SQL quoting/binding and shell argument handling are separately correct.
- No data-corrupting substitutions, hard-coded credentials or unauthorized SQL execution.

## References

- [Snowflake CLI SQL templating](https://docs.snowflake.com/en/developer-guide/snowflake-cli/sql/execute-sql)
- [SnowSQL variable substitution](https://docs.snowflake.com/en/user-guide/snowsql-use)
- [Snowflake string literals](https://docs.snowflake.com/en/sql-reference/data-types-text)
- [dbt Jinja functions](https://docs.getdbt.com/reference/dbt-jinja-functions)
- [Jinja escaping](https://jinja.palletsprojects.com/en/stable/templates/#escaping)
