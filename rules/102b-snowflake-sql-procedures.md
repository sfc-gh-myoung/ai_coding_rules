---
schema_version: v4.0
rule_version: v3.0.0
description: Best practices for authoring Snowflake SQL Scripting stored procedures
  and user-defined functions (UDFs). Covers body delimiter selection ($$ vs single
  quotes), nested quoting strategies, the EXECUTE
last_updated: 2026-10-06
keywords:
- kw:SQL scripting
- kw:dollar quoting
- kw:EXECUTE AS
- kw:EXECUTE IMMEDIATE
- kw:bind variables
- kw:procedure body quoting
- ext:.sql
token_budget: ~1400
context_tier: High
depends:
  required:
  - 102-snowflake-sql-core.md
  optional:
  - 102a-snowflake-sql-automation.md
  - 100-snowflake-core.md
---
# Snowflake SQL: Stored Procedures and UDFs

## Scope

**What This Rule Covers:**
LANGUAGE SQL procedures, scalar/table functions, body quoting, explicit execution rights, bindings, dynamic identifiers, exception handling and scoped transactions.

**When to Load This Rule:**
When creating or reviewing SQL Scripting procedures, SQL UDF/UDTF handlers or dynamic SQL and rights-related failures.

## Contract

### Inputs and Prerequisites

- Authorized schema/object change, parameter/return types, calling contexts and least-privilege grants.
- Purpose classified as procedure (operations/side effects) or function (query computation); existing definitions/dependents reviewed before replacement.
- Current primary documentation for execution rights, supported SQL handler features and transaction behavior.

### Mandatory

- Prefer `$$` body delimiters to avoid outer quote-escaping noise. Do not include a literal closing `$$` inside that body; build it from separate dollar strings if needed. SQL strings still escape apostrophes by doubling them.
- Fully qualify persistent objects, use double quotes only for intentionally case-sensitive/special identifiers, and document purpose/parameters with COMMENT.
- Every procedure must explicitly choose execution rights. CALLER uses caller privileges/context; OWNER uses the owner's privileges and has documented caller-session restrictions. Use OWNER only for an intentionally approved privilege boundary.
- RESTRICTED CALLER uses the caller's existing privileges limited by administrator caller grants; it is not owner's rights limited to caller-visible objects. Confirm feature availability and required caller grants before adopting it.
- Functions do not take a procedure EXECUTE AS clause. Do not apply procedure transaction/side-effect templates to SQL UDF/UDTF bodies.
- Prefix parameters/variables with `:` inside SQL statements, including SELECT INTO, DML and dynamic execution. In procedural assignments/conditions/RETURN use the scripting variable form documented for that context.
- Bind user values with placeholders/USING rather than concatenating them into SQL strings. For dynamic object names prefer `IDENTIFIER(:object_name)` where supported, with an authorized object allowlist; ordinary value binding alone does not authorize arbitrary identifiers.
- Capture SQLROWCOUNT immediately after the DML whose count is needed. Avoid intervening statements changing status before reporting results.
- Preserve errors: use statement/expression/other handlers as appropriate, log safe SQLCODE/SQLERRM context and re-raise when the operation failed. Do not return an error string as if deployment succeeded.
- For atomic multi-statement DML, establish and finish the transaction in the same documented scope, roll back on exception and propagate failure. DDL/implicit commit behavior must be reviewed; transaction syntax does not make every procedure atomic.

### Execution Steps

1. Review purpose, inputs, existing object, grants and dependencies; choose procedure versus scalar/table function.
2. Select explicit rights and least-privilege access. Do not grant roles/caller grants without separate approval.
3. Write a readable dollar-quoted body with typed parameters, fully qualified names, colon-prefixed SQL bindings and explicit return schema.
4. Bind dynamic values; validate/allowlist any dynamic identifier independently of syntax escaping.
5. Define exceptions, status capture and transaction ownership/recovery for the actual operations.
6. Only when authorized, create/replace and test under intended roles, hostile values, NULLs, quoting, alternate calling context and failure paths. CALL can mutate data; never use it as a harmless compile probe.
7. Report authored, compiled and executed status separately; no tool access means tests remain unverified.

### Validation

- Handler syntax, delimiters, parameter/return types and COMMENT agree with the intended object kind.
- Explicit procedure rights are correct; restricted caller grants never supply privileges the caller lacks.
- SQL bindings/IDENTIFIER use prevent injection and enforce approved object scope.
- Persistent references resolve in different caller database/schema contexts.
- Exceptions do not hide failure; DML status is captured correctly and transaction boundaries are tested when execution authorized.
- Safe diagnostics use current query/event evidence; GET_DDL formatting is not assumed to reproduce original source delimiters. Keep reviewed source definitions authoritative.

## References

- [CREATE PROCEDURE](https://docs.snowflake.com/en/sql-reference/sql/create-procedure)
- [CREATE FUNCTION](https://docs.snowflake.com/en/sql-reference/sql/create-function)
- [SQL Scripting procedures](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-snowflake-scripting)
- [Caller and owner rights](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-rights)
- [Restricted caller rights](https://docs.snowflake.com/en/developer-guide/restricted-callers-rights)
- [EXECUTE IMMEDIATE](https://docs.snowflake.com/en/sql-reference/sql/execute-immediate)
- [IDENTIFIER binding](https://docs.snowflake.com/en/sql-reference/identifier-literal)
- [Transactions](https://docs.snowflake.com/en/sql-reference/transactions)
- `102e-snowflake-sql-procedure-antipatterns.md` for focused quoting/security guidance.
