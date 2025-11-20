---
appliesTo:
  - "**/*.sql"
  - "**/*.py"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Cortex Agents, agent design, tool configuration, grounding, RBAC, multi-tool agents, planning instructions, testing, troubleshooting, semantic views, create agent, debug agent, agent not working, tool execution failed, agent error, fix agent, agent performance, agent tool integration, cortex agent configuration, UnboundedExecution
**TokenBudget:** ~3850
**ContextTier:** High
**Depends:** 100-snowflake-core, 105-snowflake-cost-governance, 106-snowflake-semantic-views, 111-snowflake-observability-core

# Snowflake Cortex Agents Best Practices

## Purpose
Provide comprehensive patterns to design, configure, secure, and operate Cortex Agents including agent archetypes, tool configurations, planning instructions, testing strategies, RBAC, observability, and quality evaluation, optimized for reliability and cost.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cortex Agents creation and operation, agent archetypes, tool design and configuration, planning/response instructions, testing patterns, RBAC/allowlists, evaluation and tracing, cost/latency trade-offs

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Choose agent archetype** - Single-tool, multi-tool, or hybrid based on use case
- **Ground with semantic views** - Use curated, governed data sources
- **Define clear tool descriptions** - Help agent understand when to use each tool
- **Write planning instructions** - Guide agent orchestration and tool selection
- **Enforce RBAC and allowlists** - Least-privilege access to models, tools, data
- **Test systematically** - Component testing → integration → eval framework
- **Never put business logic in semantic views** - Use agent response instructions

**Quick Checklist:**
- [ ] Agent archetype selected (single/multi/hybrid tool)
- [ ] Grounding sources prepared (semantic views/Cortex Search)
- [ ] Tools defined with clear descriptions
- [ ] Planning instructions written
- [ ] Response instructions (flagging logic) configured
- [ ] RBAC and allowlists enforced
- [ ] Evaluation framework in place

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~600 tokens (always load for agent tasks)
- + Agent Archetypes (sections 1-2): ~1500 tokens (load when designing agent)
- + Tooling & Configuration (sections 3-4): ~2500 tokens (load for setup)
- + Complete Reference: ~2500 tokens (full core guide)

**Recommended Loading Strategy:**
- **Understanding agents**: Quick Start only
- **Choosing agent archetype**: + Agent Archetypes
- **Creating agent**: + Tooling & Configuration (full core)
- **Implementation/testing**: + 115a (instructions) + 115b (operations)

## Contract
- **Inputs/Prereqs:**
  - Snowflake account with Cortex Agents availability; role strategy defined
  - Grounding sources (tables, views, Cortex Search indices, semantic views)
  - Tool catalog (SQL procedures, UDFs, Cortex Analyst, Cortex Search) with least-privilege permissions
- **Allowed Tools:** Cortex Agents (Snowsight/SQL/Python), AI Observability, semantic views, Cortex Search, Cortex Analyst
- **Forbidden Tools:**
  - Unbounded tool execution without guardrails or allowlists
  - Prompts containing secrets/PII, or enabling escalation of privileges
  - Putting business rule flagging in semantic views (belongs in agent instructions)
- **Required Steps:**
  1. Choose agent archetype based on use case and tool combination requirements
  2. Define agent objectives and non-goals; select smallest model and temperature that meet quality
  3. Ground with high-signal sources (semantic views, curated indices); avoid raw ungoverned tables
  4. Configure tools with clear descriptions and when-to-use guidance
  5. Write explicit planning instructions for tool selection and orchestration
  6. Define response instructions with flagging logic (NEVER in semantic views)
  7. Enforce RBAC and allowlists for models, tools, and data
  8. Test components independently before integration testing
  9. Add evaluation (gold questions, assertions) and tracing via AI Observability
  10. Monitor costs and latency; introduce caching and retrieval filters
- **Output Format:** Agent configs/patterns, planning templates, SQL/Python snippets
- **Validation Steps:** Component tests pass; integration tests pass; evaluation scores meet thresholds; traces show bounded tool calls; RBAC enforced; cost objectives met

## Key Principles
- Choose agent archetype based on tool combination and use case requirements
- Smallest sufficient model and minimal tool surface reduce cost and risk
- Ground with curated, up-to-date, governed sources; prefer semantic views
- **CRITICAL:** Business rule flagging belongs in agent instructions, NEVER in semantic views
- Deterministic tools with strict validation; idempotent, bounded side-effects
- Explicit planning instructions required for multi-tool agents
- Test tools independently (component testing) before integration
- Add allowlists/deny lists for models, tools, and tables/views
- Log/trace agent steps and evaluate quality regularly

> **Investigation Required**  
> When implementing Cortex Agents:
> 1. Verify Cortex features enabled: `SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;`
> 2. Test semantic views are queryable: `SELECT * FROM TABLE(SEMANTIC_VIEW('<view_name>')) LIMIT 1;`
> 3. Check Cortex Search services exist: `SHOW CORTEX SEARCH SERVICES IN SCHEMA <db>.<schema>;`
> 4. Verify role permissions: `SHOW GRANTS TO ROLE <agent_role>;`
> 5. Never assume tool availability - test each tool independently before agent integration
> 6. Test Cortex function access: `SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');`
>
> **Anti-Pattern:**
> "Let me create an agent with these tools - they should work."
>
> **Correct Pattern:**
> "Let me verify prerequisites first before creating the agent."
> [runs SHOW PARAMETERS, tests semantic view, checks permissions]
> "All prerequisites verified. Here's the agent configuration based on tested components..."

## 0. Prerequisites Validation

Before implementing Cortex Agents, verify your environment meets requirements:

### 0.1 Prerequisites Checklist

- [ ] Snowflake account has Cortex features enabled
- [ ] Required permissions granted (USAGE, SELECT, EXECUTE)
- [ ] Semantic views exist and are queryable (for Cortex Analyst tools)
- [ ] Cortex Search services created and accessible (for Search tools)
- [ ] Test queries return expected results before agent integration
- [ ] RBAC roles properly configured for agent execution

### 0.2 Verification Commands

**Check Cortex Availability:**
```sql
-- Verify Cortex features are available in your account
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Expected: Parameters showing Cortex feature configuration
```

**Verify Semantic View Access (for Cortex Analyst tools):**
```sql
-- Test semantic view is accessible and has data
SELECT * FROM {DATABASE}.{SCHEMA}.{SEMANTIC_VIEW} LIMIT 5;

-- Example:
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 5;
```

**Verify Cortex Search Service (for Search tools):**
```sql
-- Check search service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DATABASE}.{SCHEMA};

-- Test search service responds
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    '{DATABASE}.{SCHEMA}.{SERVICE_NAME}',
    '{"query": "test", "limit": 1}'
);

-- Example:
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);
```

**Verify Role Permissions:**
```sql
-- Check current role's grants
SHOW GRANTS TO ROLE {AGENT_ROLE};

-- Example:
SHOW GRANTS TO ROLE agent_runner;

-- Required grants should include:
-- - USAGE on databases and schemas
-- - SELECT on semantic views
-- - USAGE on Cortex Search services
-- - USAGE on Cortex functions (COMPLETE, SEARCH_PREVIEW, etc.)
```

**Test Cortex Function Access:**
```sql
-- Verify Cortex functions are accessible
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-8b',
    'What is 2+2?'
) AS test_response;

-- Expected: Returns JSON response from model
```

### 0.3 Pre-Implementation Validation

Run this comprehensive check before creating agents:

```sql
-- 1. Check Cortex availability
SELECT 'Cortex Features' AS check_type, 
       COUNT(*) AS parameter_count
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "name" LIKE 'CORTEX%';

-- 2. Verify semantic views (if using Cortex Analyst)
-- Replace with your actual views
SELECT 'Semantic View: PORTFOLIO' AS check_type,
       COUNT(*) AS row_count
FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- 3. Verify search services (if using Cortex Search)
SHOW CORTEX SEARCH SERVICES;

-- 4. Check permissions
SELECT 'Role Permissions' AS check_type,
       COUNT(*) AS grant_count  
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
```

**All checks should return non-zero counts.** If any return 0 or error, address prerequisites before proceeding.

## 1. Agent Archetypes

Choose the appropriate agent pattern based on your use case and tool requirements:

### 1.1 Multi-Domain Analytics Agents (Multiple Cortex Analysts)
**Use Cases:** Comprehensive analysis across different data domains (portfolio + risk + performance + compliance)

**Tool Configuration:**
- Multiple Cortex Analyst tools, each with domain-specific semantic views
- Each tool focuses on one analytical domain with distinct metrics/dimensions

**Planning Focus:**
- Domain-specific tool selection based on query type
- Cross-domain synthesis when queries span multiple areas
- Visualization generation across different data domains

**When to Use:**
- Queries span multiple analytical domains regularly
- Need comprehensive insights from different data perspectives
- Have multiple semantic views modeling different domains

**Examples:** Chief investment officer agent, comprehensive portfolio manager, multi-domain analyst

### 1.2 Single-Domain Analytics Agents (Single Cortex Analyst)
**Use Cases:** Focused analysis within specific domain (portfolio analysis only, risk monitoring only)

**Tool Configuration:**
- Single Cortex Analyst tool with domain-specific semantic view
- Deep analytical capabilities within one domain

**Planning Focus:**
- Breaking complex queries into logical sub-questions within domain
- Visualization generation for domain-specific metrics
- Clear limitations when data unavailable

**When to Use:**
- Queries focus on single analytical domain
- Deep analysis needed within one area
- Simpler tool selection logic preferred

**Examples:** Portfolio analyzer, risk monitor, performance tracker, ESG scorer

### 1.3 Research-Focused Agents (Cortex Search Only)
**Use Cases:** Document synthesis, policy research, literature review, compliance checking

**Tool Configuration:**
- Multiple Cortex Search tools for different document types
- No Cortex Analyst tools (pure document research)

**Planning Focus:**
- Document type selection based on information needs
- Content synthesis across multiple document sources
- Citation management and source attribution

**When to Use:**
- Queries focus on qualitative information from documents
- Need synthesis of multiple document types
- No quantitative calculations required

**Examples:** Policy researcher, document librarian, compliance checker, ESG researcher

### 1.4 Hybrid Agents (Multiple Analysts + Search)
**Use Cases:** Investment decisions, comprehensive analysis, client advisory, multi-faceted insights

**Tool Configuration:**
- Multiple Cortex Analyst tools for quantitative analysis
- Multiple Cortex Search tools for document research
- Complex orchestration across tool types

**Planning Focus:**
- Query classification (quantitative vs qualitative vs mixed)
- Tool selection logic across both Analyst and Search tools
- Data-to-document workflows (quantitative results inform document search)
- Multi-source synthesis

**When to Use:**
- Queries frequently mix quantitative and qualitative needs
- Investment/advisory scenarios requiring data + research
- Maximum flexibility needed for complex workflows

**Examples:** Portfolio copilot, investment advisor, ESG guardian, chief risk officer agent

## 2. Tooling Strategy

### 2.1 Core Tool Principles
Tools should be:
- Deterministic, side-effect aware, and idempotent
- Validating inputs (types/ranges) and returning structured outputs
- Bounded by RBAC and schema-level allowlists

### 2.2 Cortex Analyst Tool Configuration Pattern
```yaml
Tool Name: {analyst_tool_name}              # e.g., portfolio_analyzer, risk_analyzer
Type: Cortex Analyst
Semantic View: {DATABASE}.{SCHEMA}.{VIEW}   # e.g., ANALYTICS.AI.PORTFOLIO_VIEW
Description: "Use this tool for {specific_analysis_type}. It can {capabilities_list}. Use for questions about {when_to_use_guidance}."

# Example: Portfolio Analytics
Tool Name: portfolio_analyzer
Type: Cortex Analyst
Semantic View: ANALYTICS.AI.PORTFOLIO_VIEW
Description: "Use this tool for quantitative portfolio analysis including holdings, exposures, sector breakdowns, performance metrics, and concentration calculations. It can calculate weights, generate lists of securities, perform aggregations, and create charts. Use for questions about numbers, percentages, rankings, comparisons, visualizations, and portfolio analytics."
```

**Key Elements:**
- **Tool Name:** Clear, descriptive, domain-focused
- **Semantic View:** Fully qualified name with appropriate governance
- **Description:** Three parts: purpose, capabilities, when-to-use

### 2.3 Cortex Search Tool Configuration Pattern
```yaml
Tool Name: search_{document_type}          # e.g., search_research_reports, search_policies
Type: Cortex Search
Service: {DATABASE}.{SCHEMA}.{SERVICE}     # e.g., DOCS.AI.RESEARCH_REPORTS_SERVICE
ID Column: DOCUMENT_ID
Title Column: DOCUMENT_TITLE
Description: "Search {document_type} for {specific_use_case}. Use for questions about {when_to_use_guidance}."

# Example: Document Search
Tool Name: search_research_reports
Type: Cortex Search
Service: DOCS.AI.RESEARCH_REPORTS_SERVICE
ID Column: DOCUMENT_ID
Title Column: DOCUMENT_TITLE
Description: "Search investment research reports for analyst opinions, ratings, price targets, and market commentary. Use for questions about analyst views, investment recommendations, and qualitative research insights."
```

**Key Elements:**
- **Tool Name:** Prefix with `search_` for clarity
- **Service:** Fully qualified Cortex Search service name
- **ID/Title Columns:** Must match service configuration exactly
- **Description:** Document type, use cases, when-to-use guidance

### 2.4 Tool Configuration Best Practices

**Tool Ordering:**
- List most frequently used tools first
- Group similar tools together (all Cortex Analyst tools, then all Search tools)
- Consider tool execution time in ordering (faster tools first)

**Description Clarity:**
- Clearly define WHEN to use each tool (avoid overlaps)
- Include specific examples of appropriate queries
- Specify tool capabilities explicitly
- Avoid ambiguous use cases that could match multiple tools

**Avoiding Overlapping Use Cases:**
**Anti-Pattern:**
```
Tool A: "Use for portfolio analysis"
Tool B: "Use for investment analysis"  # Too similar to Tool A
```

**Correct Pattern:**
```
Tool A: "Use for portfolio holdings, weights, and exposure analysis"
Tool B: "Use for risk metrics, volatility, and correlation analysis"  # Distinct domain
```

## 3. Agent Configuration Templates

### 3.1 Multi-Tool Hybrid Agent Template
```yaml
Agent Name: {agent_name}
Display Name: {Agent Display Name}
Description: {Business context and capabilities}
Response Instructions: {Tone, format, and output guidelines with flagging logic}

Tools:
  - {analyst_tool_1} (Cortex Analyst)              # Primary quantitative tool
  - {analyst_tool_2} (Cortex Analyst)              # Secondary domain (optional)
  - search_{document_type_1} (Cortex Search)       # Primary document search
  - search_{document_type_2} (Cortex Search)       # Secondary document search

Orchestration Model: Claude 4 (or claude-3-opus-20240229)
Planning Instructions: {Tool selection logic for multiple analysts and document search}
```

### 3.2 Multiple Cortex Analyst Agent Template
```yaml
Agent Name: {agent_name}
Display Name: {Agent Display Name}
Description: {Comprehensive quantitative analysis across multiple domains}
Response Instructions: {Data-focused tone and formatting guidelines}

Tools:
  - {analyst_tool_1} (Cortex Analyst)              # e.g., portfolio_analyzer
  - {analyst_tool_2} (Cortex Analyst)              # e.g., risk_analyzer
  - {analyst_tool_3} (Cortex Analyst)              # e.g., performance_analyzer

Orchestration Model: Claude 4
Planning Instructions: {Logic for selecting appropriate analyst tool based on domain}
```

### 3.3 Single Cortex Analyst Agent Template
```yaml
Agent Name: {agent_name}
Display Name: {Agent Display Name}
Description: {Specific analytical domain focus}
Response Instructions: {Domain-focused tone and formatting guidelines}

Tools:
  - {analyst_tool_name} (Cortex Analyst)           # Single domain-specific tool

Orchestration Model: Claude 4
Planning Instructions: {Logic for single-domain quantitative analysis}
```

### 3.4 Cortex Search Only Agent Template
```yaml
Agent Name: {agent_name}
Display Name: {Agent Display Name}
Description: {Document search and qualitative research capabilities}
Response Instructions: {Research-focused tone with proper citations}

Tools:
  - search_{document_type_1} (Cortex Search)       # Primary document corpus
  - search_{document_type_2} (Cortex Search)       # Secondary document corpus

Orchestration Model: Claude 4
Planning Instructions: {Logic for document search and content synthesis}
```

## 4. Planning Instructions Patterns

## Related Rules

**Closely Related** (consider loading together):
- `115a-snowflake-cortex-agents-instructions` - Planning and response instruction patterns for tool orchestration
- `115b-snowflake-cortex-agents-operations` - Testing, RBAC, observability, cost management, troubleshooting
- `117-snowflake-cortex-analyst` - When using Cortex Analyst as an agent tool (semantic view integration)
- `116-snowflake-cortex-search` - When using Cortex Search as an agent tool (document retrieval)

**Sometimes Related** (load if specific scenario):
- `106-snowflake-semantic-views-core` - When grounding agents with semantic views (data source setup)
- `111-snowflake-observability-core` - When implementing agent observability and tracing
- `105-snowflake-cost-governance` - When monitoring agent costs and setting budgets

**Complementary** (different aspects of same domain):
- `114-snowflake-cortex-aisql` - For SQL-based AI function usage (different from agent orchestration)
- `107-snowflake-security-governance` - For RBAC and security policies affecting agent permissions

## Validation

- Create Cortex Agent with at least one tool (SQL function, Python UDF, or semantic view) and verify it responds
- Test agent with multi-step questions requiring tool orchestration
- Verify planning instructions guide agent behavior correctly
- Confirm response instructions format outputs as expected
- Validate tool definitions include clear descriptions and parameter specs
- Test agent with questions outside tool scope to verify graceful degradation
- Check agent observability logs for tool execution traces

## Quick Compliance Checklist

- [ ] Agent created with clear purpose and description in CREATE statement
- [ ] At least one tool defined with comprehensive description
- [ ] Tool parameters include type specifications and constraints
- [ ] Planning instructions guide multi-step reasoning
- [ ] Response instructions format output appropriately
- [ ] Agent tested with questions requiring multiple tool calls
- [ ] Agent tested with out-of-scope questions (graceful degradation)
- [ ] Tool execution logs verified in observability interface
- [ ] RBAC configured for agent access (users, roles, permissions)
- [ ] Cost monitoring configured for agent usage tracking
- [ ] Agent naming follows conventions (SEM_ prefix for semantic-grounded)

## Response Template

```sql
-- Create Cortex Agent with semantic view tool and planning instructions
CREATE OR REPLACE CORTEX AGENT AGENT_ASSET_PERFORMANCE_ANALYST
  COMMENT = 'Agent for analyzing asset performance, failures, and maintenance costs using semantic views'
  AS
    TOOLS = [
      'SEM_ASSET_PERFORMANCE'  -- Semantic view as tool
    ]
    PLANNING_INSTRUCTIONS = $$
    You are an expert asset performance analyst for energy grid operations.
    
    When answering questions:
    1. Use the SEM_ASSET_PERFORMANCE semantic view to query asset data
    2. Break complex questions into multiple queries if needed
    3. Calculate derived metrics when simple aggregations don't suffice
    4. Provide context about asset types, failure patterns, and cost trends
    5. Cite specific data points to support your analysis
    
    Example reasoning:
    - User asks: "Which asset type has highest failure rate?"
    - Steps:
      1. Query failure_count and asset_count by asset_type
      2. Calculate rate = failure_count / asset_count
      3. Rank by rate descending
      4. Return top asset type with supporting numbers
    $$
    RESPONSE_INSTRUCTIONS = $$
    Format your response as follows:
    
    **Analysis Summary:** [1-2 sentence answer to the question]
    
    **Key Findings:**
    - [Finding 1 with specific numbers]
    - [Finding 2 with specific numbers]
    - [Finding 3 with specific numbers]
    
    **Data Source:** [Semantic view or tables queried]
    **Time Period:** [Date range of analysis]
    $$;

-- Test the agent
SELECT *
FROM TABLE(AGENT_QUERY(
  'AGENT_ASSET_PERFORMANCE_ANALYST',
  'Which asset type has the highest failure rate in the last year?'
));
```

## References

### Internal Documentation
- **115a-snowflake-cortex-agents-instructions:** Planning and response instruction patterns
- **115b-snowflake-cortex-agents-operations:** Testing, RBAC, observability, cost management
- **117-snowflake-cortex-analyst:** Using Cortex Analyst as an agent tool
- **116-snowflake-cortex-search:** Using Cortex Search for document retrieval in agents
- **106-snowflake-semantic-views-core:** Semantic views as agent tools

### External Documentation
- [Snowflake Cortex Agents Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Official agent creation and management
- [Cortex Agent Tools](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-tools) - Supported tool types and configurations
- [Agent Planning Instructions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-instructions) - Writing effective planning and response instructions
