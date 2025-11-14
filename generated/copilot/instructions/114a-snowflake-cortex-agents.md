---
appliesTo:
  - "**/*.sql"
  - "**/*.py"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Cortex Agents, agent design, tool configuration, grounding, RBAC, multi-tool agents, planning instructions, testing, troubleshooting, semantic views
**TokenBudget:** ~6950
**ContextTier:** High
**Depends:** 100-snowflake-core, 105-snowflake-cost-governance, 106-snowflake-semantic-views, 111-snowflake-observability

# Snowflake Cortex Agents Best Practices

## Purpose
Provide comprehensive patterns to design, configure, secure, and operate Cortex Agents including agent archetypes, tool configurations, planning instructions, testing strategies, RBAC, observability, and quality evaluation, optimized for reliability and cost.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cortex Agents creation and operation, agent archetypes, tool design and configuration, planning/response instructions, testing patterns, RBAC/allowlists, evaluation and tracing, cost/latency trade-offs

## Quick Start TL;DR (Read First - 30 Seconds)

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

Planning instructions define HOW the agent selects and orchestrates tools. Be explicit.

### 4.1 Multi-Tool Hybrid Agent (Multiple Analysts + Search)
```
1. Analyze the user's query to identify distinct sub-questions and analytical domains
2. Classify each sub-question by type:
   - QUANTITATIVE: Numbers, calculations, lists, rankings, exposures, weights, metrics, charts
   - QUALITATIVE: Summaries, opinions, context, explanations, "why" questions
3. For quantitative questions, choose appropriate analyst tool based on domain:
   - {Analyst tool 1}: {Specific domain and capabilities}
   - {Analyst tool 2}: {Specific domain and capabilities}
   - {Analyst tool 3}: {Specific domain and capabilities}
4. For qualitative questions, choose appropriate search tool based on information type:
   - {Document type 1}: {When to use this corpus}
   - {Document type 2}: {When to use this corpus}
   - {Document type 3}: {When to use this corpus}
5. For mixed questions: Use appropriate analyst tool first, then search tools with results as context
6. Always synthesize multiple tool outputs into coherent response
7. If user requests charts/visualizations, ensure appropriate analyst tool generates them
8. If no tool can answer, clearly state limitations and suggest alternatives
```

### 4.2 Multiple Cortex Analyst Agent
```
1. Analyze the user's query to identify data requirements and analytical domains
2. Select appropriate analyst tool(s) based on query type:
   - {Analyst tool 1}: {Specific domain and capabilities}
   - {Analyst tool 2}: {Specific domain and capabilities}
   - {Analyst tool 3}: {Specific domain and capabilities}
3. For queries spanning multiple domains, use multiple analyst tools systematically
4. Generate charts and visualizations when requested or when they enhance understanding
5. Provide comprehensive quantitative insights with proper context and business implications
6. If data is unavailable in one domain, try alternative analyst tools or suggest alternatives
```

### 4.3 Single Cortex Analyst Agent
```
1. Analyze the user's query to identify data requirements and analytical approach
2. Use {analyst_tool_name} tool for all data analysis, calculations, and insights
3. For complex queries, break into logical sub-questions and analyze systematically
4. Generate charts and visualizations when requested or when they enhance understanding
5. Provide quantitative insights with proper context and business implications
6. If data is unavailable, clearly state limitations and suggest alternative approaches
```

### 4.4 Cortex Search Only Agent
```
1. Analyze the user's query to identify relevant document types and search terms
2. Choose appropriate search tool(s) based on information type:
   - {Document type 1}: {When to use this corpus}
   - {Document type 2}: {When to use this corpus}
   - {Document type 3}: {When to use this corpus}
3. For multi-faceted queries, search across multiple document types systematically
4. Synthesize findings from different document sources into coherent response
5. Always provide proper citations with document type, title, and date
6. If no relevant documents found, suggest alternative search terms or document types
```

## 5. Response Instructions Templates

Response instructions define HOW the agent formats and presents answers.

### 5.1 CRITICAL: Flagging Logic Placement Principle

**Agent Instructions:** All flagging, thresholds, highlighting, and business rules
**Cortex Analyst:** ONLY data calculations and SQL generation
**Semantic Views:** ONLY data modeling and query logic
**NEVER:** Put business rule flagging in semantic view custom instructions

**Why This Matters:**
- Semantic views should be reusable across different agents with different thresholds
- Business rules change more frequently than data models
- Agent-level flagging allows consistent application across all tools
- Keeps semantic views focused on accurate calculations only

**Example - CORRECT:**
```yaml
# In Agent Response Instructions:
"When portfolio positions exceed 6.5%, flag with ' CONCENTRATION WARNING' and recommend action."

# In Cortex Analyst Tool:
- Just returns position_weight calculations

# In Semantic View:
- Just calculates position_weight accurately
```

**Example - INCORRECT:**
```yaml
# In Semantic View custom instructions:
"Flag positions >6.5% as concentrations"  # WRONG - belongs in agent instructions

# In Cortex Analyst Tool description:
"Flag concentrations above threshold"  # WRONG - belongs in agent instructions
```

### 5.2 General Response Template
```
1. You are {Agent Role}, an expert assistant for {target_users}
2. Tone: {Professional style appropriate for persona}
3. Format numerical data clearly using tables for lists/comparisons
4. FLAGGING AND THRESHOLDS: {Specific flagging requirements with exact thresholds}
   - Include exact values and recommend specific actions
   - Apply flagging consistently across all tool outputs
5. Always cite document sources with type and date (e.g., "According to {source} from {date}...")
6. For charts: Include clear titles describing what is shown
7. If information unavailable: State clearly and suggest alternatives
8. Focus on actionable insights and {domain-specific} implications
```

### 5.3 Portfolio/Investment Agent Response Template
```
1. You are a Portfolio Management Assistant providing data-driven investment insights
2. Tone: Professional, analytical, action-oriented
3. Format holdings and exposures as tables with clear headers
4. FLAGGING: Flag positions >6.5% with " CONCENTRATION WARNING: {security} at {exact %}. Consider rebalancing."
5. Cite research sources: "According to {broker} Research Report dated {date}..."
6. Charts should have clear titles: "Top 10 Holdings by Weight (%)" not just "Holdings"
7. If data unavailable: "Unable to retrieve {data type}. Suggest checking {alternative source}."
8. Emphasize risk implications and regulatory considerations
```

### 5.4 Research/Compliance Agent Response Template
```
1. You are a Research and Compliance Assistant providing document-based insights
2. Tone: Thorough, detail-oriented, citation-focused
3. Organize findings by document type and date (most recent first)
4. FLAGGING: Flag compliance issues with severity: "BREACH" (>7%), "WARNING" (6-7%), "NOTICE" (<6%)
5. Citations required: Always include document title, type, and date for every claim
6. Synthesize across sources: "Multiple research reports (3 sources) indicate..."
7. If no documents found: "No {document type} found for {topic}. Suggest expanding search to {alternatives}."
8. Highlight contradictory information and explain differences
```

## 6. Testing & Validation Patterns

### 6.1 Component Testing (Test Tools Independently)

Before integration, verify each tool works correctly:

**Testing Cortex Analyst Tools:**
```python
def test_analyst_tool(session: Session, semantic_view: str):
    """Verify Cortex Analyst tool responds correctly"""
    
    # Test with simple query
    result = session.sql(f"""
        SELECT * FROM TABLE(
            {semantic_view}(
                METRICS total_value,
                DIMENSIONS category
            )
        ) LIMIT 5
    """).collect()
    
    print(f"Analyst tool returned {len(result)} results")
    return len(result) > 0
```

**Testing Cortex Search Tools:**
```python
def test_search_tool(session: Session, service_name: str):
    """Verify Cortex Search tool responds correctly"""
    
    # Test with simple search
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{service_name}',
            '{{"query": "test", "limit": 1}}'
        )
    """).collect()
    
    print(f"Search tool returned results")
    return len(result) > 0
```

### 6.2 Integration Testing (Test Tool Combinations)

After component tests pass, test realistic workflows:

**Multi-Tool Agent Testing:**
- Test quantitative query (should use Cortex Analyst)
- Test qualitative query (should use Cortex Search)
- Test mixed query (should use both tool types)
- Verify tool selection logic works correctly

**Example Test Queries:**
```python
# Quantitative (Analyst)
"What are the top 10 holdings by weight?"
"Calculate sector allocation breakdown"

# Qualitative (Search)
"What is the latest research on {company}?"
"Find compliance policies for {topic}"

# Mixed (Both)
"Show top holdings and their latest research ratings"
"Analyze sector exposure with supporting market commentary"
```

### 6.3 Business Scenario Testing

Test with realistic end-user queries:

**Portfolio Management Scenarios:**
```
"What are my largest positions in the Global Growth fund?"
"Show me technology sector exposure across all portfolios"
"Are there any concentration warnings I should be aware of?"
"What does recent research say about my top holdings?"
```

**Compliance Scenarios:**
```
"Check if any positions violate our 7% concentration policy"
"Find engagement notes for companies with ESG controversies"
"What does our policy say about environmental violations?"
```

### 6.4 Validation Checklist

Component Testing:
- [ ] All required AI components exist (semantic views, search services)
- [ ] Each Cortex Analyst tool returns data independently
- [ ] Each Cortex Search tool returns documents independently
- [ ] Tool descriptions are clear and non-overlapping

Integration Testing:
- [ ] Tool selection logic works for quantitative queries
- [ ] Tool selection logic works for qualitative queries
- [ ] Tool selection logic works for mixed queries
- [ ] Multi-tool synthesis produces coherent responses

Business Scenario Testing:
- [ ] Realistic queries return expected results
- [ ] Flagging logic applies correctly
- [ ] Citations are properly formatted
- [ ] Charts/visualizations generate appropriately

Performance & Cost:
- [ ] Query response times are acceptable
- [ ] Token usage is within budget
- [ ] Tool invocation counts are reasonable

## 7. RBAC and Permissions

### 7.1 Required Grants for Cortex Agents

**Database and Schema Access:**
```sql
-- Grant database and schema usage to agent role
GRANT USAGE ON DATABASE {DATABASE} TO ROLE agent_runner;
GRANT USAGE ON SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON DATABASE ANALYTICS TO ROLE agent_runner;
GRANT USAGE ON SCHEMA ANALYTICS.SEMANTIC TO ROLE agent_runner;
```

**Semantic View Access (for Cortex Analyst tools):**
```sql
-- Grant SELECT on specific semantic views
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- Or grant on all views in schema
GRANT SELECT ON ALL VIEWS IN SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;

-- Example:
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW TO ROLE agent_runner;
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.RISK_VIEW TO ROLE agent_runner;
```

**Cortex Search Service Access:**
```sql
-- Grant USAGE on Cortex Search services
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.policy_documents_service TO ROLE agent_runner;
```

**Cortex Function Access:**
```sql
-- Grant USAGE on Cortex AI functions
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE agent_runner;

-- For Cortex Analyst (if using direct function access)
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;
```

**Warehouse Access:**
```sql
-- Grant warehouse usage for query execution
GRANT USAGE ON WAREHOUSE {WAREHOUSE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE agent_runner;
```

### 7.2 Verification Queries

**Verify All Grants:**
```sql
-- Check all grants for agent role
SHOW GRANTS TO ROLE agent_runner;

-- Verify specific grant exists
SELECT *
FROM TABLE(INFORMATION_SCHEMA.APPLICABLE_ROLES())
WHERE grantee = 'AGENT_RUNNER';
```

**Test Access:**
```sql
-- Switch to agent role and test access
USE ROLE agent_runner;

-- Test semantic view access
SELECT COUNT(*) FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- Test Cortex Search service
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);

-- Test Cortex function
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### 7.3 Principle of Least Privilege

Apply these security patterns:
- **Agents:** Only access tools needed for specific use case
- **Tools:** Only access data appropriate for their domain  
- **Roles:** Grant minimum permissions required for functionality
- **Warehouses:** Use dedicated warehouses with auto-suspend for cost control

## 8. Observability and Evaluation

- Use AI Observability to capture traces of agent reasoning, tool invocations, and outcomes
- Employ golden questions and assertions; compare model/tool variants and track regression
- Monitor tool selection accuracy (is agent picking right tool?)
- Track flagging accuracy (are thresholds applied correctly?)

## 9. Cost and Latency

- Prefer cached retrieval; restrict tool invocations per turn
- Control token budgets and cap output tokens; fail fast on oversized requests
- Monitor costs by agent and by tool type
- Optimize expensive tools (multiple Cortex Analyst calls) vs cheaper alternatives

## 10. Common Errors and Solutions

### Error: "Semantic view not found" or "Object does not exist"

**Cause:** Agent role lacks SELECT permission on semantic view, or view doesn't exist

**Solutions:**
```sql
-- 1. Verify view exists
SHOW VIEWS LIKE '{VIEW_NAME}' IN SCHEMA {DATABASE}.{SCHEMA};

-- Example:
SHOW VIEWS LIKE 'PORTFOLIO_VIEW' IN SCHEMA ANALYTICS.SEMANTIC;

-- 2. Grant SELECT access to agent role
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- Example:
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW TO ROLE agent_runner;

-- 3. Verify grant was applied
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access
USE ROLE agent_runner;
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 1;
```

### Error: "Tool returned no results" or "Empty response"

**Cause:** Tool configured but underlying data empty, filters too restrictive, or query logic incorrect

**Solutions:**
```sql
-- 1. Test tool independently (component testing)
-- For Cortex Analyst tool:
SELECT * FROM {SEMANTIC_VIEW} LIMIT 10;

-- For Cortex Search tool:
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    '{SERVICE_NAME}',
    '{"query": "test", "limit": 10}'
);

-- 2. Verify data exists in underlying tables
SELECT COUNT(*) FROM {SEMANTIC_VIEW};

-- 3. Check for overly restrictive filters
-- Review metadata filters in search queries
-- Review WHERE clauses in semantic views

-- 4. Test with broader query
-- Start with simple query, then add filters incrementally
```

### Error: "Agent selected wrong tool" or "Incorrect tool invocation"

**Cause:** Overlapping tool descriptions, vague when-to-use guidance, or unclear planning instructions

**Solutions:**
1. **Review Tool Descriptions** (see Section 2.4 - Avoiding Overlapping Tools)
   - Ensure each tool has distinct use case
   - Add explicit trigger words to descriptions
   - Example: "Use for quantitative analysis (numbers, percentages)" vs "Use for qualitative research (opinions, commentary)"

2. **Update Planning Instructions** (see Section 4)
   - Add clearer tool selection classification logic
   - Include explicit examples of which queries map to which tools
   - Test with example queries before deployment

3. **Validation Script:**
```python
# Test tool selection logic
test_queries = [
    ("What are my top 10 holdings?", "expected_tool: portfolio_analyzer"),
    ("What does research say about AAPL?", "expected_tool: search_research_reports"),
    ("Show sector allocation", "expected_tool: portfolio_analyzer")
]

for query, expected in test_queries:
    result = agent.query(query)
    print(f"Query: {query}")
    print(f"Tool used: {result.tool_used}")
    print(f"Expected: {expected}")
    assert result.tool_used == expected.split(": ")[1]
```

### Error: "Permission denied" on Cortex function

**Cause:** Missing USAGE grants on Cortex functions (COMPLETE, SEARCH_PREVIEW, ANALYST, etc.)

**Solutions:**
```sql
-- Grant USAGE on all required Cortex functions
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;

-- Verify grants
SHOW GRANTS TO ROLE agent_runner;

-- Test function access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### Error: "Search service not found" or "Service inaccessible"

**Cause:** Missing USAGE grant on Cortex Search service

**Solutions:**
```sql
-- 1. Verify service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DATABASE}.{SCHEMA};

-- Example:
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- 2. Grant USAGE on service
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;

-- 3. Verify grant
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);
```

### Error: "Flagging logic not working" or "Thresholds not applied"

**Cause:** Flagging logic placed in semantic view instead of agent response instructions

**Solution:**
- **Review:** Ensure flagging logic is in Agent Response Instructions (see Section 5)
- **NEVER:** Put flagging/threshold logic in semantic view custom instructions
- **Correct Pattern:**
  - Semantic View: Calculate accurate position_weight
  - Agent Response Instructions: "When position_weight > 6.5%, flag with WARNING"

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Flagging Logic in Semantic Views**
```yaml
# In Semantic View custom instructions:
"Flag positions exceeding 6.5% as concentration risks"
```
**Problem:** Semantic views should be reusable across agents with different thresholds. Business rules belong in agent instructions.

**Correct Pattern:**
```yaml
# In Agent Response Instructions:
"When position weights exceed 6.5%, flag with ' CONCENTRATION WARNING'"

# In Semantic View:
Just calculate position_weight accurately (no flagging logic)
```

**Anti-Pattern 2: Overlapping Tool Use Cases**
```yaml
Tool A: "Use for portfolio analysis"
Tool B: "Use for investment analysis"  # Too similar!
```
**Problem:** Agent won't know which tool to pick, leading to inconsistent behavior.

**Correct Pattern:**
```yaml
Tool A: "Use for portfolio holdings, weights, and sector breakdowns"
Tool B: "Use for risk metrics, volatility calculations, and correlations"
```

**Anti-Pattern 3: Missing When-to-Use Guidance**
```yaml
Tool Description: "Analyzes portfolio data"
```
**Problem:** Too vague. Agent doesn't know WHEN this tool is appropriate vs other tools.

**Correct Pattern:**
```yaml
Tool Description: "Use this tool for quantitative portfolio analysis including holdings lists, weight calculations, and sector allocations. Use for questions about 'how much', 'what percentage', 'top N', and data visualizations."
```

**Anti-Pattern 4: Testing Only End-to-End**
```python
# Only test complete agent workflows
test_full_agent_query("Show me everything about my portfolio")
```
**Problem:** When tests fail, you don't know which tool or component is broken.

**Correct Pattern:**
```python
# Test components first
test_analyst_tool_works()
test_search_tool_works()
# Then test integration
test_multi_tool_workflow()
```

**Anti-Pattern 5: Vague Planning Instructions**
```
"Use the best tool for each query"
```
**Problem:** Too ambiguous. Agent needs explicit tool selection logic.

**Correct Pattern:**
```
"For numerical questions (how much, what percentage, top N), use portfolio_analyzer. For opinions and research (what do analysts say, latest commentary), use search_research_reports."
```

## Quick Compliance Checklist
- [ ] Agent archetype chosen based on use case and tool requirements
- [ ] Agent objectives defined; smallest sufficient model chosen
- [ ] Grounding uses governed sources (semantic views or indices)
- [ ] Tools have clear descriptions with when-to-use guidance
- [ ] Tool use cases are distinct (no overlaps)
- [ ] Planning instructions are explicit about tool selection logic
- [ ] Flagging logic is in AGENT instructions (NOT semantic views)
- [ ] Tools are deterministic, validated, and least-privilege
- [ ] Component testing completed before integration testing
- [ ] Model/tool/table allowlists configured; secrets/PII excluded from prompts
- [ ] Tracing and evaluation enabled; thresholds monitored
- [ ] Token/output caps set; cost/latency tracked

## Validation
- **Success checks:** Component tests pass; integration tests pass; evaluation meets targets; tool selection logic works correctly; flagging applies consistently; traces show bounded tool use; costs stable
- **Negative tests:** Prompt injections fail; unauthorized tool/data access blocked; oversized prompts rejected; overlapping tools don't confuse agent; flagging in semantic views flagged in code review

> **Investigation Required**  
> When applying this rule:
> 1. **Read existing agent configurations BEFORE making changes** - Check current grounding sources, tools, instructions
> 2. **Verify available Cortex features** - Check if Cortex Analyst, Search, semantic views are available
> 3. **Never assume agent architecture** - Read existing agents to understand patterns
> 4. **Check RBAC and permissions** - Verify what roles and objects are accessible
> 5. **Test after changes** - Run component and integration tests to verify behavior
>
> **Anti-Pattern:**
> "Creating a Cortex Agent with these tools... (without checking available features)"
> "Adding semantic view grounding... (without verifying semantic views exist)"
>
> **Correct Pattern:**
> "Let me check your Cortex setup first."
> [reads existing agents, checks Cortex Search indices, verifies semantic views]
> "I see you have semantic views for sales data and Cortex Search for docs. Creating agent with these grounding sources..."

## Response Template

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT 
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## Cortex Agent Plan
- Archetype: <Multi-Domain Analytics / Single-Domain / Research / Hybrid>
- Objective: <clear objective>
- Model: <smallest sufficient model>
- Grounding: <semantic views / indices>
- Tools (allowlist):
  - Cortex Analyst: [analyst_tool_1, analyst_tool_2]
  - Cortex Search: [search_tool_1, search_tool_2]
- Planning Logic: <tool selection strategy>
- Response Instructions: <flagging thresholds, tone, format>
- RBAC: <roles/allowed objects>
- Cost/Latency: <budgets, caps>
- Testing: <component + integration approach>
- Evaluation: <gold Qs, assertions>

## Agent Configuration
- System prompt: <summary>
- Tool descriptions: <when-to-use guidance>
- Planning instructions: <explicit tool selection logic>
- Response instructions: <flagging logic, formatting>
- Observability: <traces/metrics enabled>

## Validation
- Component tests: <pass/fail>
- Integration tests: <pass/fail>
- Eval score >= <threshold>
- Tool calls bounded; costs within budget
```

## References

### External Documentation
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts, tools, and setup
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Tracing, evaluations, comparisons
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Natural language to SQL
- [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search) - Semantic search service

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Cortex Analyst**: `114c-snowflake-cortex-analyst.md` - Semantic view design and Analyst tool configuration
- **Cortex Search**: `114b-snowflake-cortex-search.md` - Search service setup and tool integration
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Observability**: `111-snowflake-observability.md`
