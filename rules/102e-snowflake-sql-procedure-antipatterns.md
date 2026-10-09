---
schema_version: v4.0
rule_version: v3.0.0
description: "Common anti-patterns in Snowflake SQL stored procedures and UDFs: incorrect delimiter usage, missing EXECUTE AS, SQL injection via string concatenation, literal $$ in bodies, and unqualified object"
last_updated: 2026-10-06
keywords:
  - kw:stored procedure anti-patterns
  - kw:dollar quoting
  - kw:EXECUTE AS
  - kw:SQL injection bind variables
  - kw:fully qualified object names
  - kw:procedure delimiter escaping
  - kw:udf
token_budget: ~900
context_tier: Low
depends:
  optional:
    - 102b-snowflake-sql-procedures.md  # Procedure creation patterns and templates
---
# Snowflake SQL: Procedure Safety Review

## Scope

**What This Rule Covers:**
Reviewing procedure/function quoting, rights, bindings, identifier scope, exceptions and destructive lifecycle assumptions. Defects are described in prose only.

**When to Load This Rule:**
When debugging/reviewing SQL handlers or checking dynamic SQL security and execution context.

## Contract

### Inputs and Prerequisites

- Existing handler source, object kind/signature, actual grants/callers and user edit/execution scope.
- Current primary rights/binding documentation; load procedure-authoring companion when implementing.

### Mandatory

- Prefer dollar-quoted bodies while preserving real string escaping. Literal closing delimiter inside a body terminates it even in comments/strings; construct necessary dollar pairs from parts.
- Procedures explicitly choose OWNER/CALLER/RESTRICTED CALLER by approved privilege boundary. Restricted caller uses caller privileges constrained by caller grants, not owner privileges. Functions do not take procedure EXECUTE AS.
- Use colon-prefixed variables/parameters in SQL statements, bound values with placeholders/USING, and authorized IDENTIFIER syntax for dynamic object names where supported.
- Never concatenate arbitrary input into dynamic SQL; shell escaping is not SQL binding. Identifier syntax validation alone is not object authorization.
- Persistent references fully qualified and tested against actual owner/caller resolution; no claim every unqualified object resolves identically across rights modes.
- Replacements/truncate/reloads need explicit target/ownership/data-loss/dependent/grant review; no destructive example presented as automatically correct.
- Exceptions/status must truthfully propagate failure and multi-statement transactions reflect real scope/DDL commits. Do not turn failed operations into successful error-string returns.
- Binding/quoting improvements do not guarantee performance gains; measure actual behavior before claims.

### Execution Steps

1. Read complete source/callers and classify procedure versus UDF/UDTF, rights and resource scope.
2. Identify quoted-body/SQL-binding/identifier/exception/lifecycle defects with exact evidence.
3. Apply scoped correct patterns and preserve approved behavior, not copied negative implementations.
4. Run safe static checks; create/CALL/query tests only when authorized and in a controlled target.
5. Report authored/compiled/executed status and residual security/runtime gaps separately.

### Validation

- Correct delimiters/strings, explicit applicable rights, variable bindings and fully qualified targets.
- Dynamic values/identifiers safe and approved; no arbitrary input concatenation or unowned resource mutation.
- Error/status/transaction behavior correct, replacement/destructive scope separately authorized.
- Review findings grounded and actual tests distinguish static inspection from runtime verification.

## References

- [Snowflake SQL Scripting procedures](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-snowflake-scripting)
- [Snowflake execution rights](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-rights)
- [Restricted caller rights](https://docs.snowflake.com/en/developer-guide/restricted-callers-rights)
- [IDENTIFIER](https://docs.snowflake.com/en/sql-reference/identifier-literal)
- [EXECUTE IMMEDIATE](https://docs.snowflake.com/en/sql-reference/sql/execute-immediate)
- `102b-snowflake-sql-procedures.md` for implementation detail.
