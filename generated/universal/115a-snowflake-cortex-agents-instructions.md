**Keywords:** Cortex Agents, planning instructions, response instructions, tool orchestration, flagging logic, agent prompts, multi-tool orchestration, tool selection, agent prompting, instruction patterns, agent planning, tool chaining, orchestration patterns, multi-step agent, agent workflow, instruction design, tool flagging, agent response format
**TokenBudget:** ~2700
**ContextTier:** Standard
**Depends:** 100-snowflake-core, 115-snowflake-cortex-agents-core

# Snowflake Cortex Agents: Planning & Response Instructions

## Purpose
Provide comprehensive patterns for writing planning instructions (tool orchestration logic) and response instructions (output formatting and flagging logic) for Cortex Agents.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Planning instructions, response instructions, tool selection logic, agent orchestration patterns

## Contract
- **Inputs/Prereqs:** Agent architecture defined (from 115-snowflake-cortex-agents-core), tools configured
- **Allowed Tools:** Planning instruction templates, response instruction templates
- **Forbidden Tools:** Putting business logic in semantic views (belongs in agent instructions)
- **Required Steps:** 1) Define planning logic for tool selection 2) Write response instructions with flagging 3) Test orchestration patterns
- **Output Format:** Planning/response instruction templates
- **Validation Steps:** Test tool selection logic; verify flagging works; confirm tone/format appropriate

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Planning instructions define tool selection** - Be explicit about when to use each tool
- **Response instructions define output format** - Include tone, structure, flagging logic
- **Never put flagging in semantic views** - Business rules belong in agent instructions
- **Test orchestration logic** - Verify tools selected appropriately

**Quick Checklist:**
- [ ] Planning instructions written for tool selection
- [ ] Response instructions define tone and format
- [ ] Flagging logic in response instructions (NOT semantic views)
- [ ] Orchestration tested with sample queries

## Key Principles
- Planning instructions guide HOW agents select and orchestrate tools
- Response instructions define output format, tone, and business rule flagging
- **CRITICAL:** Business rule flagging belongs in response instructions, NEVER in semantic views
- Explicit is better than implicit for multi-tool agents
- Test tool selection logic independently before integration

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

## Validation

- Test planning instructions with multi-step questions requiring tool orchestration
- Verify response instructions format outputs consistently across different question types
- Validate tone and formatting guidelines are followed in agent responses
- Test citation requirements work correctly (data sources, document references)
- Confirm flagging rules trigger appropriately (thresholds, severity levels)
- Verify graceful degradation when tools or data unavailable
- Check that domain-specific terminology is used correctly

## Quick Compliance Checklist

- [ ] Planning instructions define agent role and expertise clearly
- [ ] Planning instructions break down reasoning into numbered steps
- [ ] Planning instructions specify when and how to use each tool
- [ ] Response instructions define consistent formatting structure
- [ ] Response instructions specify tone (conversational, formal, technical)
- [ ] Flagging rules defined with specific thresholds and severity levels
- [ ] Citation requirements specified for data sources and documents
- [ ] Graceful degradation messages defined for missing data scenarios
- [ ] Domain-specific terminology and conventions documented
- [ ] Instructions tested with edge cases (empty results, errors, ambiguous questions)
- [ ] Agent responses reviewed for consistency with instructions

> **Investigation Required**  
> When applying this rule:
> 1. Read existing agent definitions and instructions BEFORE making recommendations
> 2. Verify tool definitions match actual available tools (semantic views, functions, documents)
> 3. Never speculate about data availability or tool capabilities without checking
> 4. Test instructions with actual questions to verify agent behavior
> 5. Make grounded recommendations based on investigated agent responses and tool outputs

## Response Template

```sql
-- Complete Cortex Agent with comprehensive planning and response instructions
CREATE OR REPLACE CORTEX AGENT AGENT_PORTFOLIO_ANALYST
  COMMENT = 'Portfolio analysis agent for investment holdings, risk, and compliance'
  AS
    TOOLS = [
      'SEM_PORTFOLIO_HOLDINGS',     -- Semantic view for holdings data
      'SEM_PERFORMANCE_METRICS',    -- Semantic view for returns and risk metrics
      'DOCUMENT_SEARCH_FUNCTION'    -- Custom function for research document search
    ]
    PLANNING_INSTRUCTIONS = $$
    You are an expert Portfolio Analyst for institutional investment management.
    
    **Your Role:**
    - Analyze portfolio holdings, performance, risk, and compliance
    - Provide data-driven insights with specific numbers and citations
    - Flag concentration risks, compliance issues, and performance anomalies
    - Synthesize information across multiple data sources
    
    **When answering questions:**
    
    1. **Identify question type:**
       - Holdings analysis → Use SEM_PORTFOLIO_HOLDINGS
       - Performance/risk metrics → Use SEM_PERFORMANCE_METRICS
       - Research/compliance → Use DOCUMENT_SEARCH_FUNCTION
       - Multi-dimensional → Use multiple tools in sequence
    
    2. **Break down complex questions:**
       - Step 1: Query base data (holdings, returns, documents)
       - Step 2: Calculate derived metrics if needed
       - Step 3: Apply flagging rules (concentration >6.5%, losses >10%)
       - Step 4: Synthesize findings with context and citations
    
    3. **Handle missing data gracefully:**
       - If holdings data missing: "Unable to retrieve holdings for {portfolio}. Verify portfolio ID and access permissions."
       - If no documents found: "No research documents found for {topic}. Suggest expanding search or checking alternative sources."
    
    4. **Use domain terminology correctly:**
       - "Holdings weight" not "percentage"
       - "Concentration risk" not "over-allocation"
       - "Compliance breach" vs "Warning" vs "Notice" based on thresholds
    $$
    RESPONSE_INSTRUCTIONS = $$
    **Format your response as follows:**
    
    **Analysis Summary:** [1-2 sentence answer to the question with key finding]
    
    **Key Findings:**
    - [Finding 1 with specific numbers and data source]
    - [Finding 2 with specific numbers and data source]
    - [Finding 3 with specific numbers and data source]
    
    **Flagged Items:** [If applicable - concentration risks, compliance issues]
    - [SEVERITY]: {Item} at {exact value}. {Specific recommendation}.
    
    **Citations:** [Data sources and document references]
    - Data: {Semantic view or table} as of {date}
    - Research: "{Document title}" ({Type}, {Date})
    
    **Recommendations:** [Actionable next steps if applicable]
    
    **Tone Guidelines:**
    - Professional and data-driven (you are an institutional analyst)
    - Specific numbers with context (not vague statements)
    - Flag risks prominently with severity levels
    - Cite all data sources and documents
    - Provide actionable recommendations when appropriate
    $$;

-- Test agent with various question types
SELECT *
FROM TABLE(AGENT_QUERY(
  'AGENT_PORTFOLIO_ANALYST',
  'What are the top 5 holdings by weight in the Growth portfolio? Flag any concentration risks.'
));
```

## References

### Internal Documentation
- **115-snowflake-cortex-agents-core:** Core agent creation and tool configuration
- **115b-snowflake-cortex-agents-operations:** Testing, observability, RBAC
- **117-snowflake-cortex-analyst:** Using Cortex Analyst as agent tool
- **106-snowflake-semantic-views-core:** Semantic views as agent data sources

### External Documentation
- [Cortex Agent Instructions Guide](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-instructions) - Writing effective planning and response instructions
- [Agent Prompting Best Practices](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-prompting) - Guidelines for instruction design
- [Multi-Tool Orchestration](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-orchestration) - Coordinating multiple tools in agent workflows

