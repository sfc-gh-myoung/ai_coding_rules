# 117-snowflake-mcp-server: Snowflake-Managed MCP Server (Tool-Agnostic)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** MCP, Model Context Protocol, Snowflake-managed MCP server, CREATE MCP SERVER, SYSTEM_EXECUTE_SQL, CORTEX_ANALYST_MESSAGE, CORTEX_SEARCH_SERVICE_QUERY, CORTEX_AGENT_RUN, tools/list, tools/call, initialize, OAuth, SECURITY INTEGRATION, RBAC, PAT
**TokenBudget:** ~2600
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 107-snowflake-security-governance.md, 112-snowflake-snowcli.md

## Scope

**What This Rule Covers:**
Authoritative, tool-agnostic guidance for using Snowflake's Snowflake-managed MCP server to expose governed Snowflake capabilities (Cortex Analyst/Search/Agents, SQL execution, and custom tools) to MCP-compatible clients.

**When to Load This Rule:**
- Creating Snowflake-managed MCP servers
- Securing and configuring MCP server access with RBAC
- Integrating MCP clients (Cursor, Claude Desktop, custom clients)
- Exposing Cortex Analyst, Search, or Agents through MCP
- Troubleshooting MCP server authentication or tool invocation issues

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake fundamentals (DDL, RBAC basics)
- **107-snowflake-security-governance.md** - Security governance and least privilege
- **112-snowflake-snowcli.md** - SnowCLI usage patterns

**Related:**
- **106-snowflake-semantic-views-core.md** - Semantic views for Cortex Analyst tools
- **115-snowflake-cortex-agents-core.md** - Cortex Agents configuration
- **116-snowflake-cortex-search.md** - Cortex Search services

### External Documentation

- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp) - Overview, client flow, security guidance
- [CREATE MCP SERVER](https://docs.snowflake.com/en/sql-reference/sql/create-mcp-server) - DDL syntax and specification schema
- [DESCRIBE MCP SERVER](https://docs.snowflake.com/en/sql-reference/sql/describe-mcp-server) - Inspect server spec metadata
- [SHOW MCP SERVERS](https://docs.snowflake.com/en/sql-reference/sql/show-mcp-servers) - List MCP servers in scope
- [Cortex Analyst REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst#rest-api) - semantic_view and semantic_models request fields

## Contract

### Inputs and Prerequisites

- Target DATABASE.SCHEMA for the MCP server
- Inventory of Snowflake objects to expose as tools (semantic views, search services, agents, UDFs/SPs)
- Authentication approach for clients (OAuth recommended; PAT only with least privilege)
- Clear RBAC plan (roles that can discover vs invoke tools)
- Understanding of MCP JSON-RPC protocol

### Mandatory

- Snowflake CLI (snow) for executing SQL
- Privileges to create/configure MCP servers in the target schema
- Explicit grants for tool invocation:
  - Semantic view: SELECT privilege
  - Search service: USAGE privilege
  - Agent: USAGE privilege
  - UDF/SP: USAGE privilege
  - Warehouse: USAGE privilege (if required)

### Forbidden

- Embedding secrets (tokens, client secrets) in repos, MCP specs, or prompts
- Granting overly broad roles (e.g., ACCOUNTADMIN) to MCP clients "just to make it work"
- Assuming USAGE on MCP server implies access to tools (it does not)
- Storing sensitive/regulated data in MCP server spec metadata

### Execution Steps

1. **Identify Tools:** Choose target DATABASE and SCHEMA; identify tools to expose (semantic views, search services, agents, UDFs/SPs)
2. **Validate Objects:** Create/verify underlying objects and validate they work directly in Snowflake
3. **Create Server:** Execute `CREATE OR REPLACE MCP SERVER ... FROM SPECIFICATION $$ ... $$`
4. **Grant Privileges:** Grant USAGE (discovery) and per-tool privileges (invocation) to intended roles
5. **Validate Spec:** Check with `DESCRIBE MCP SERVER` and test client flow (initialize, tools/list, tools/call)
6. **Harden Security:** Configure OAuth, verify hostname hygiene, validate third-party tools, enforce least privilege, document operational runbooks

### Output Format

```sql
-- MCP server creation with multiple tool types
CREATE OR REPLACE MCP SERVER {DATABASE}.{SCHEMA}.{SERVER_NAME}
  FROM SPECIFICATION $$
    tools:
      - name: "analyst_tool"
        type: "CORTEX_ANALYST_MESSAGE"
        identifier: "{DATABASE}.{SCHEMA}.{SEMANTIC_VIEW}"
        title: "Analyst Tool"
        description: "Cortex Analyst tool backed by semantic view."
      
      - name: "sql_exec"
        type: "SYSTEM_EXECUTE_SQL"
        title: "SQL Execution"
        description: "Execute SQL queries."
  $$;

-- Grant discovery + invocation privileges
GRANT USAGE ON MCP SERVER {DATABASE}.{SCHEMA}.{SERVER_NAME} TO ROLE {ROLE};
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{SEMANTIC_VIEW} TO ROLE {ROLE};
```

```json
// MCP client JSON-RPC flow
// 1. Initialize
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}

// 2. List tools
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

// 3. Call tool
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "analyst_tool", "arguments": {"message": "Query text"}}}
```

### Validation

**Pre-Task-Completion Checks:**
- MCP server created successfully
- Underlying objects (semantic views, search services, agents) exist and work
- RBAC plan documented (discovery vs invocation roles)
- OAuth configured or PAT is least-privilege
- No secrets or sensitive data in MCP spec metadata
- Client flow tested (initialize, tools/list, tools/call)

**Success Criteria:**
- `SHOW MCP SERVERS` lists the server in target scope
- `DESCRIBE MCP SERVER` returns server_spec with expected tools
- "Discover-only" role can list tools but cannot call them (expected)
- "Invoke" role can call tools and gets successful results
- No privilege errors for properly granted clients

**Negative Tests:**
- Calling tool without underlying object privileges yields authorization error
- Using hostnames with underscores causes connectivity issues (avoid)
- USAGE grant alone does not enable tool invocation

### Design Principles

- **Least Privilege Per-Tool:** USAGE on MCP server enables discovery; per-tool grants enable invocation
- **OAuth Over Tokens:** Prefer OAuth 2.0 for authentication; avoid hardcoded tokens
- **SQL-First Semantic Views:** CORTEX_ANALYST_MESSAGE tools reference semantic views (not YAML files)
- **Metadata Hygiene:** Don't store sensitive/regulated data in MCP server spec metadata
- **Standard MCP JSON-RPC:** Client flow follows initialize -> tools/list -> tools/call pattern

### Post-Execution Checklist

- [ ] DESCRIBE MCP SERVER matches intended tools and identifiers
- [ ] RBAC is least-privilege: discovery (USAGE) separated from invocation (per-tool grants)
- [ ] OAuth configured (or PAT is least-privilege with rotation plan)
- [ ] No secrets or regulated data in MCP server spec metadata
- [ ] Client smoke test works: initialize, tools/list, tools/call
- [ ] Hostname hygiene verified (hyphens preferred; underscores avoided)

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Treating USAGE on the MCP server as "access to everything"

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

**Benefits:** Predictable authorization, least-privilege enforcement, fewer "it lists tools but can't call them" incidents.

### Anti-Pattern 2: Putting secrets or sensitive data into MCP spec metadata

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
