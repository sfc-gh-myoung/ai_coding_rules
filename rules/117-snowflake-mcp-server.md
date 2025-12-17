# 117-snowflake-mcp-server: Snowflake-Managed MCP Server (Tool-Agnostic)

## Metadata

**SchemaVersion:** v3.0
**RuleVersion:** v1.0.0
**Keywords:** MCP, Model Context Protocol, Snowflake-managed MCP server, CREATE MCP SERVER, SYSTEM_EXECUTE_SQL, CORTEX_ANALYST_MESSAGE, CORTEX_SEARCH_SERVICE_QUERY, CORTEX_AGENT_RUN, tools/list, tools/call, initialize, OAuth, SECURITY INTEGRATION, RBAC, PAT
**TokenBudget:** ~1650
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/107-snowflake-security-governance.md, rules/112-snowflake-snowcli.md

## Purpose

Provide authoritative, tool-agnostic guidance for using Snowflake’s **Snowflake-managed MCP server** to expose governed Snowflake capabilities (Cortex Analyst/Search/Agents, SQL execution, and custom tools) to MCP-compatible clients.

## Rule Scope

Applies whenever you create, secure, or use **Snowflake-managed MCP servers** from any MCP client (Cursor, Claude Desktop, custom clients, etc.).

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use SQL-first semantic views for Analyst**: In Snowflake-managed MCP, `CORTEX_ANALYST_MESSAGE` tools reference **semantic views** (not YAML semantic model files).
- **Least privilege is per-tool**: `USAGE` on the MCP server enables discovery, but you must grant privileges on **each referenced tool object** (semantic view, search service, agent, UDF/SP).
- **OAuth over tokens**: Prefer OAuth 2.0; avoid hardcoded tokens; if using a PAT, ensure it is scoped to the least-privileged role.
- **Client flow is standard MCP JSON-RPC**: `initialize` (protocol `2025-06-18`), then `tools/list`, then `tools/call`.
- **Treat MCP specs as metadata**: Don’t put sensitive/regulated data in MCP server metadata (tool titles/descriptions/spec).

**Pre-Execution Checklist:**
- [ ] You know the target `DATABASE` and `SCHEMA` where the MCP server will live
- [ ] You have (or can create) a **semantic view** for Analyst and/or a Cortex Search Service / Cortex Agent / UDF or stored proc as tools
- [ ] You have a clear RBAC plan (roles that can **discover** vs **invoke** tools)
- [ ] You have an OAuth plan (Snowflake OAuth integration) or an approved PAT with least-privilege role
- [ ] You will avoid putting any sensitive content into MCP server spec metadata

## Contract

<inputs_prereqs>
- Target `DATABASE.SCHEMA` for the MCP server
- Inventory of the Snowflake objects you want to expose as tools (semantic views, search services, agents, UDFs/SPs)
- Authentication approach for clients (OAuth recommended; PAT only with least privilege)
</inputs_prereqs>

<mandatory>
- Snowflake CLI (`snow`) for executing SQL (per project conventions)
- Privileges to create/configure MCP servers in the target schema
- Explicit grants for tool invocation (semantic view SELECT, search service USAGE, agent USAGE, UDF/SP USAGE, warehouse USAGE if required)
</mandatory>

<forbidden>
- Embedding secrets (tokens, client secrets) in repos, MCP specs, or prompts
- Granting overly broad roles (e.g., `ACCOUNTADMIN`) to MCP clients “just to make it work”
- Assuming `USAGE` on MCP server implies access to tools (it does not)
</forbidden>

<steps>
1. Choose a target `DATABASE` and `SCHEMA` and identify the tools you want to expose
2. Create/verify underlying objects (semantic view, search service, agent, UDF/SP) and validate they work directly in Snowflake
3. Create the MCP server with `CREATE OR REPLACE MCP SERVER ... FROM SPECIFICATION $$ ... $$`
4. Grant `USAGE` (discovery) and per-tool privileges (invocation) to the intended roles
5. Validate the MCP server spec with `DESCRIBE MCP SERVER` and test the client flow (`initialize`, then `tools/list`, then `tools/call`)
6. Harden security posture (OAuth, hostname hygiene, third-party tool verification, least privilege) and document operational runbooks
</steps>

<output_format>
- SQL snippets to create MCP servers and grants (rerunnable/idempotent where reasonable)
- A short client-side flow description (JSON-RPC methods and endpoints)
</output_format>

<validation>
- `SHOW MCP SERVERS` lists the server in the target scope
- `DESCRIBE MCP SERVER <name>` shows the expected tools in `server_spec`
- A client with only `USAGE` on the server can `tools/list` but cannot successfully call tools without per-tool grants
- A properly granted client can invoke `tools/call` and gets results without privilege errors
</validation>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Treating `USAGE` on the MCP server as “access to everything”**

```sql
-- Bad: Only granting USAGE on the MCP server, then expecting tools to work
GRANT USAGE ON MCP SERVER MY_DB.MY_SCHEMA.MY_MCP TO ROLE MCP_CLIENT_ROLE;
```

**Problem:** Tool discovery may work, but tool invocation will fail because privileges must be granted on the underlying objects (semantic views, search services, agents, UDF/SPs).

**Correct Pattern:**
```sql
-- Good: Grant USAGE on server for discovery + per-tool privileges for invocation
GRANT USAGE ON MCP SERVER MY_DB.MY_SCHEMA.MY_MCP TO ROLE MCP_CLIENT_ROLE;

-- Analyst tool -> SELECT on semantic view
GRANT SELECT ON VIEW MY_DB.MY_SCHEMA.SEM_REVENUE TO ROLE MCP_CLIENT_ROLE;

-- Search tool -> USAGE on search service
GRANT USAGE ON CORTEX SEARCH SERVICE MY_DB.MY_SCHEMA.PRODUCT_SEARCH TO ROLE MCP_CLIENT_ROLE;
```

**Benefits:** Predictable authorization, least-privilege enforcement, fewer “it lists tools but can’t call them” incidents.

**Anti-Pattern 2: Putting secrets or sensitive data into MCP spec metadata**

```yaml
# Bad: secret-ish / sensitive info in title/description/metadata (stored in Snowflake metadata)
tools:
  - name: "sql_exec"
    type: "SYSTEM_EXECUTE_SQL"
    title: "SQL Exec (token=abc123...)"
    description: "Run SQL; contact me at ...; customer SSNs are in table ..."
```

**Problem:** MCP server specifications are stored as metadata and can be surfaced via `DESCRIBE MCP SERVER`. Don’t store regulated/sensitive data there.

**Correct Pattern:**
```yaml
# Good: descriptive but non-sensitive metadata
tools:
  - name: "sql_exec"
    type: "SYSTEM_EXECUTE_SQL"
    title: "SQL Execution"
    description: "Execute SQL statements using the connected Snowflake session."
```

**Benefits:** Lower leakage risk; aligns with Snowflake metadata guidance; easier to audit.

## Post-Execution Checklist

- [ ] `DESCRIBE MCP SERVER` matches the intended tools and identifiers
- [ ] RBAC is least-privilege: discovery (`USAGE` on MCP server) is separated from invocation (per-tool grants)
- [ ] OAuth is configured (or PAT is least-privilege with a clear rotation story)
- [ ] No secrets or regulated data appear in MCP server spec metadata
- [ ] Client-side smoke test works: `initialize`, then `tools/list`, then `tools/call`
- [ ] Hostname hygiene checked (hyphens preferred; avoid underscores)

## Validation

**Success Checks:**
- `SHOW MCP SERVERS IN SCHEMA <schema_name>;` shows the server
- `DESCRIBE MCP SERVER <server_name>;` returns `server_spec` with the expected tools
- A “discover-only” role can list tools but cannot call them successfully (expected)
- An “invoke” role can call tools and gets successful results

**Negative Tests:**
- Calling a tool without underlying object privileges yields an authorization error
- Using hostnames containing underscores causes connectivity issues in some MCP client configurations (avoid)

## Output Format Examples

```bash
# Snowflake CLI (preferred) – always set db/schema explicitly in interactive commands
snow sql -q "USE DATABASE MY_DB; USE SCHEMA MY_SCHEMA; SHOW MCP SERVERS;"

# Expect: server listed (plus any others you have access to)
```

```sql
-- Create an MCP server with Analyst + SQL execution tools
CREATE OR REPLACE MCP SERVER MY_MCP
  FROM SPECIFICATION $$
    tools:
      - name: "revenue_analyst"
        type: "CORTEX_ANALYST_MESSAGE"
        identifier: "MY_DB.MY_SCHEMA.SEM_REVENUE"
        title: "Revenue Semantic View"
        description: "Cortex Analyst tool backed by the SEM_REVENUE semantic view."

      - name: "sql_exec"
        type: "SYSTEM_EXECUTE_SQL"
        title: "SQL Execution"
        description: "Execute SQL queries against the connected Snowflake session."
  $$;
```

```json
// Tool-agnostic MCP client flow (Snowflake-managed MCP server)
// POST /api/v2/databases/{database}/schemas/{schema}/mcp-servers/{name}
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": { "protocolVersion": "2025-06-18" }
}
```

```json
// tools/list
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

```json
// tools/call (Analyst tool takes a "message" argument)
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "revenue_analyst",
    "arguments": { "message": "Which company had the most revenue?" }
  }
}
```

## References

### Related Rules
- `rules/100-snowflake-core.md` - Snowflake fundamentals (DDL, RBAC basics)
- `rules/107-snowflake-security-governance.md` - Security governance and least privilege
- `rules/112-snowflake-snowcli.md` - SnowCLI usage patterns

### External Documentation
- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp) - Overview, client flow, security guidance
- [CREATE MCP SERVER](https://docs.snowflake.com/en/sql-reference/sql/create-mcp-server) - DDL syntax and specification schema
- [DESCRIBE MCP SERVER](https://docs.snowflake.com/en/sql-reference/sql/describe-mcp-server) - Inspect server spec metadata
- [SHOW MCP SERVERS](https://docs.snowflake.com/en/sql-reference/sql/show-mcp-servers) - List MCP servers in scope
- [Cortex Analyst REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst#rest-api) - `semantic_view` and `semantic_models` request fields
