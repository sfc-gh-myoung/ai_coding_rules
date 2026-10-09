---
schema_version: v4.0
rule_version: v5.0.0
description: "Guide creation of parameterized SQL templates using <%VARIABLE%> syntax for automated Snowflake deployments in production environments. NEVER use CREATE OR REPLACE TABLE (data loss risk), instead use"
last_updated: 2026-10-06
keywords:
  - kw:parameterized SQL templates
  - kw:idempotent MERGE operations
  - kw:create table not exists
  - kw:multi-environment deployment
  - kw:cicd pipeline integration
  - kw:production-safe automation
token_budget: ~1300
context_tier: High
depends:
  required:
    - 102-snowflake-sql-core.md  # General SQL file patterns (headers, syntax, qualified names)
  optional:
    - 117-snowflake-mcp-server.md  # MCP server integration patterns
    - 130-snowflake-demo-sql.md  # Demo SQL patterns (this rule extends demo patterns to production)
---
# Snowflake SQL: Production Automation and CI/CD

## Scope

**What This Rule Covers:**
Environment-parameterized, data-preserving SQL deployment with staged loads, deterministic upserts, explicit authorization, validation and recovery.

**When to Load This Rule:**
When authoring reusable production SQL templates, multi-environment deployment or CI/CD migrations. Use demo guidance only for separately authorized disposable targets.

## Contract

### Inputs and Prerequisites

- Authorized target environment/connection, object inventory, dependency/grant scope and least-privilege execution role.
- Existing automation/CLI version and chosen template renderer; environment values and managed credentials supplied through approved secret mechanisms.
- Source/target schemas, business keys, migration acceptance criteria and recovery design.

### Mandatory

- Parameterize environment-specific database/schema/stage/warehouse/role values. Use uppercase names and the renderer's documented syntax; `<%VARIABLE%>` is Snowflake CLI STANDARD templating, not a universal SnowSQL/dbt format.
- Never hard-code credentials or interpolate untrusted values into SQL. Bind data values and use validated identifiers/IDENTIFIER syntax where supported.
- Preserve production tables: use `CREATE TABLE IF NOT EXISTS` for first creation and explicit reviewed ALTER migrations. Do not use `CREATE OR REPLACE TABLE` on persisted production data.
- `IF NOT EXISTS` preserves an existing object but does not reconcile its definition; compare actual columns, constraints, grants and dependencies before loading.
- MERGE is not automatically idempotent. Require stable business keys, one deterministic source row per key, controlled updates and explicit rerun expectations; reject duplicates/NULL keys rather than silently multiplying rows.
- Stage loads in isolated owned temporary/staging objects, validate COPY errors and source integrity, then apply the reviewed upsert. `ON_ERROR = CONTINUE` must not hide partial loads; forced reload requires intentional approval and duplicate handling.
- View/stage replacement needs reviewed names, grants, dependencies, retention and authorization; no blanket safe-to-replace claim.
- Headers document purpose, parameters, renderer/usage, concrete safe example, dependencies and rerun semantics. Order `NN_<schema>_<operation>.sql` by actual dependency, not filename order alone.
- Separate destructive cleanup, privilege changes and production promotion from ordinary validation; each needs explicit authorization.
- Capture what ran, its environment, query/run identity and actual outcome. A row count is not proof of content correctness; do not query stream-only metadata columns on ordinary tables.

### Execution Steps

1. Inspect current automation, objects and renderer; confirm target/authority without changing accounts or roles implicitly.
2. Define parameter contracts, safe identifier handling, dependency order and file headers.
3. Author non-replacing creation/ALTER statements and deterministic staged upserts. Validate source keys and target compatibility before mutation.
4. Render locally using the selected syntax, inspect resolved identifiers and verify no unresolved template markers or altered data literals remain.
5. With separate execution approval, test in dev/test, including reruns, duplicate/NULL inputs, partial load, grants and dependency behavior.
6. Promote only the reviewed artifact/configuration to an authorized production target. Run pre/post checks and record real outcomes.
7. On failure, inspect actual state and transaction boundaries before recovery. Never blindly rename original/staging tables or delete unverified objects after an uncertain swap.

### Validation

- Renderer/version and all parameters documented; resolved target matches approved environment.
- No secrets, unsafe concatenation, unreviewed table replacement or automatic privilege escalation.
- Creation and schema evolution distinct; existing definitions/grants/dependents checked.
- Source uniqueness/NULL checks, COPY completeness, counts and business aggregates pass; view queries tested only after bases exist/load.
- Rerun tests demonstrate actual data/content expectations, not merely zero command exit.
- Dev/test results and production authorization recorded separately; production is not executed just to complete a checklist.
- Recovery is scoped to verified owned objects with known mutation outcomes; rollback capability/retention is documented, not assumed for all DDL.

## References

- [Snowflake CLI: Execute SQL and templating](https://docs.snowflake.com/en/developer-guide/snowflake-cli/sql/execute-sql)
- [Snowflake MERGE and duplicate-source behavior](https://docs.snowflake.com/en/sql-reference/sql/merge)
- [Snowflake CREATE TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-table)
- [Snowflake IDENTIFIER syntax](https://docs.snowflake.com/en/sql-reference/identifier-literal)
- [Snowflake transactions](https://docs.snowflake.com/en/sql-reference/transactions)
- `102d-snowflake-sql-cicd.md` for deployment-pipeline integration.
