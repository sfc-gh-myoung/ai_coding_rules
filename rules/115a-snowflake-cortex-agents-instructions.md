# Snowflake Cortex Agents: Planning & Response Instructions

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Cortex Agents, planning instructions, response instructions, tool orchestration, flagging logic, agent prompts, multi-tool orchestration, tool selection, agent prompting, instruction patterns, agent planning
**TokenBudget:** ~4900
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 115-snowflake-cortex-agents-core.md

## Scope

**What This Rule Covers:**
Comprehensive patterns for writing planning instructions (tool orchestration logic) and response instructions (output formatting and flagging logic) for Cortex Agents.

**When to Load This Rule:**
- Writing planning instructions for agent tool orchestration
- Defining response instructions with formatting and flagging logic
- Implementing tool selection patterns
- Creating multi-tool orchestration workflows
- **CRITICAL:** Implementing business rule flagging (belongs in agent instructions, NOT semantic views)

> **Investigation Required**
> When applying this rule:
> 1. Read existing agent definitions and instructions BEFORE making recommendations
> 2. Verify tool definitions match actual available tools (semantic views, functions, documents)
> 3. Never speculate about data availability or tool capabilities without checking
> 4. Test instructions with actual questions to verify agent behavior
> 5. Make grounded recommendations based on investigated agent responses and tool outputs

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **115-snowflake-cortex-agents-core.md** - Core agent creation and tool configuration

**Related:**
- **115b-snowflake-cortex-agents-operations.md** - Testing, observability, RBAC
- **106c-snowflake-semantic-views-integration.md** - Using Cortex Analyst as agent tool
- **106-snowflake-semantic-views-core.md** - Semantic views as agent data sources

### External Documentation

- [Cortex Agent Instructions Guide](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-instructions) - Writing effective planning and response instructions
- [Agent Prompting Best Practices](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-prompting) - Guidelines for instruction design
- [Multi-Tool Orchestration](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-orchestration) - Coordinating multiple tools in agent workflows

## Contract

### Inputs and Prerequisites

Agent architecture defined (from 115-snowflake-cortex-agents-core), tools configured

### Mandatory

Planning instruction templates, response instruction templates

### Forbidden

Putting business logic in semantic views (belongs in agent instructions)

### Execution Steps

1. Define planning logic for tool selection
2. Write response instructions with flagging
3. Test orchestration patterns

### Output Format

Planning/response instruction templates

### Validation

**Pre-Task-Completion Checks:**
- Planning instructions written for tool selection
- Response instructions define tone and format
- Flagging logic in response instructions (NOT semantic views)
- Orchestration logic ready for testing

**Success Criteria:**
- Test tool selection logic works correctly
- Verify flagging triggers appropriately
- Confirm tone/format meet requirements
- Multi-tool orchestration tested successfully

**Negative Tests:**
- Wrong tool selected should trigger review
- Missing flagging logic should be caught
- Vague instructions should be refined

### Design Principles

- Planning instructions guide HOW agents select and orchestrate tools
- Response instructions define output format, tone, and business rule flagging
- **CRITICAL:** Business rule flagging belongs in response instructions, NEVER in semantic views
- Explicit is better than implicit for multi-tool agents
- Test tool selection logic independently before integration

### Post-Execution Checklist

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

**Anti-Pattern 1: Putting Business Logic in Semantic Views Instead of Agent Instructions**
```yaml
# Bad: Flagging logic embedded in semantic view
views:
  - name: revenue_view
    semantic_type: measure
    expr: |
      CASE
        WHEN revenue > 1000000 THEN 'HIGH_ALERT'
        WHEN revenue < 100000 THEN 'LOW_WARNING'
        ELSE revenue
      END
```
**Problem:** Semantic views should describe data, not implement flagging; business rules hard to update; requires semantic model redeployment; agent can't customize flagging; violates separation of concerns

**Correct Pattern:**
```markdown
# Good: Flagging logic in agent response instructions
**Response Instructions:**
When presenting revenue data:
1. Calculate total revenue from revenue_view
2. Apply flagging rules:
   - If revenue > $1M: Flag as "WARNING: HIGH - Exceeds target"
   - If revenue < $100K: Flag as "WARNING: LOW - Below threshold"
3. Explain flagging rationale in response
```
**Benefits:** Business rules in agent layer; easy to update without model changes; flexible per-agent customization; clear separation of concerns; version control friendly

**Anti-Pattern 2: Vague Planning Instructions Without Tool Selection Criteria**
```markdown
# Bad: Unclear when to use which tool
**Planning Instructions:**
1. Analyze the user's question
2. Use the appropriate tool
3. Return results
```
**Problem:** Agent doesn't know which tool to select; random tool choice; inconsistent behavior; poor user experience; tool usage inefficiencies

**Correct Pattern:**
```markdown
# Good: Explicit tool selection criteria
**Planning Instructions:**
1. Classify query type:
   - QUANTITATIVE (numbers, calculations, rankings): Use sales_analyst tool
   - QUALITATIVE (summaries, explanations, context): Use document_search tool
2. For quantitative queries:
   - Sales metrics: Use sales_analyst
   - Marketing metrics: Use marketing_analyst
3. For qualitative queries:
   - Product docs: Use product_search
   - Policy docs: Use policy_search
4. For mixed queries: Use analyst first, then augment with search
```
**Benefits:** Predictable tool selection; consistent agent behavior; clear decision criteria; optimized tool usage; better user experience; debuggable logic

**Anti-Pattern 3: No Graceful Degradation for Missing Data**
```markdown
# Bad: Agent fails silently or errors when data unavailable
**Planning Instructions:**
1. Query the sales_analyst tool
2. Return results
[No handling for empty results or tool failures]
```
**Problem:** Poor user experience on empty results; confusing error messages; agent appears broken; no fallback guidance; user abandonment; trust erosion

**Correct Pattern:**
```markdown
# Good: Graceful degradation with helpful guidance
**Planning Instructions:**
1. Query the sales_analyst tool
2. If results empty or tool unavailable:
   - Explain what data was attempted (e.g., "I searched for Q4 2024 sales data")
   - Specify why unavailable (e.g., "Data not yet loaded for this quarter")
   - Suggest alternatives (e.g., "Try Q3 2024 data or check back next week")
3. If partial data available:
   - Present what's available
   - Clearly note limitations
   - Suggest complementary searches
```
**Benefits:** Clear failure communication; helpful user guidance; maintains trust; actionable alternatives; professional experience; reduces support burden

**Anti-Pattern 4: Missing Tone and Formatting Guidance in Response Instructions**
```markdown
# Bad: No guidance on response style
**Response Instructions:**
Return the data to the user.
```
**Problem:** Inconsistent tone across responses; unprofessional formatting; unclear structure; doesn't match brand voice; poor readability; user confusion

**Correct Pattern:**
```markdown
# Good: Explicit tone and formatting requirements
**Response Instructions:**
Tone: Professional, conversational, helpful
Structure:
1. Brief summary sentence (1-2 lines)
2. Key insights as bulleted list (3-5 bullets)
3. Data table if >5 rows
4. Closing context or recommendation

Example:
"Q4 revenue reached $1.2M, up 15% from Q3.

Key insights:
• Enterprise segment drove 60% of growth
• APAC region outperformed at +25% QoQ
• SaaS recurring revenue now 80% of total

[Revenue breakdown table]

Consider focusing Q1 investment on APAC enterprise expansion given strong momentum."
```
**Benefits:** Consistent professional tone; readable formatting; structured insights; brand-aligned voice; clear communication; better user satisfaction

## Output Format Examples

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
       - Holdings analysis: Use SEM_PORTFOLIO_HOLDINGS
       - Performance/risk metrics: Use SEM_PERFORMANCE_METRICS
       - Research/compliance: Use DOCUMENT_SEARCH_FUNCTION
       - Multi-dimensional: Use multiple tools in sequence

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

## Planning Instructions Patterns

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

## Response Instructions Templates

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

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Mixing Data Calculation and Presentation Logic

**Problem:** Combining SQL calculation instructions and response formatting rules in the same instruction block, making it unclear whether instructions are for Cortex Analyst (data layer) or the agent (presentation layer).

**Why It Fails:** Cortex Analyst processes semantic view instructions differently than agent response instructions. Mixing them causes calculation errors, formatting failures, and unpredictable behavior. The agent can't distinguish between "how to calculate" vs "how to present."

**Correct Pattern:**
```yaml
# BAD: Mixed instructions
Agent Instructions: |
  Calculate portfolio concentration as sum of top 5 holdings divided by total AUM.
  Flag any concentration >25% in red with warning icon.
  Format as percentage with 2 decimals.

# GOOD: Separated by layer
Semantic View Custom Instructions: |
  Calculate top5_concentration as:
  SUM(CASE WHEN holding_rank <= 5 THEN holding_value ELSE 0 END) / total_aum

Agent Response Instructions: |
  When presenting concentration metrics:
  1. Use portfolio_analyzer tool to get top5_concentration
  2. Flag concentration >25% with [⚠️ HIGH CONCENTRATION] prefix
  3. Format as percentage with 2 decimals (e.g., "28.50%")
  4. Explain concentration risk implications
```

### Anti-Pattern 2: Vague Flagging Criteria Without Exact Thresholds

**Problem:** Using subjective terms like "high," "concerning," or "significant" for flagging without defining exact numeric thresholds and formatting rules.

**Why It Fails:** Agent interprets thresholds inconsistently across queries, produces different flags for identical values, and confuses users with unpredictable warnings. Vague criteria prevent reproducible behavior and audit trails.

**Correct Pattern:**
```yaml
# BAD: Vague flagging
Response Instructions: |
  Flag high concentration positions with appropriate warnings.
  Highlight concerning risk levels.

# GOOD: Explicit thresholds and formatting
Response Instructions: |
  Flagging Logic (apply to all holdings):
  - Concentration >10%: Prefix with [⚠️ CONCENTRATION]
  - Volatility >25%: Prefix with [📊 HIGH VOLATILITY]
  - Liquidity <$1M daily: Prefix with [💧 LOW LIQUIDITY]
  
  Format: "{flag} {security_name}: {metric_value} ({threshold} threshold)"
  Example: "[⚠️ CONCENTRATION] AAPL: 12.5% (10% threshold)"
```

### Anti-Pattern 3: Overloading Planning Instructions with Response Formatting

**Problem:** Including detailed response formatting, tone guidelines, and output structure in Planning Instructions instead of Response Instructions.

**Why It Fails:** Planning Instructions should focus on tool selection logic only. Overloading them with formatting details makes tool selection logic hard to find, confuses the agent's decision-making process, and violates separation of concerns.

**Correct Pattern:**
```yaml
# BAD: Formatting in Planning Instructions
Planning Instructions: |
  For portfolio questions, use portfolio_analyzer and format results as tables
  with clear headers, include charts, use professional tone, and flag risks.

# GOOD: Separated concerns
Planning Instructions: |
  Tool Selection:
  - Portfolio metrics (allocation, holdings, weights): portfolio_analyzer
  - Risk metrics (volatility, VaR, correlation): risk_analyzer
  - Document questions (research, policies): search_research_docs

Response Instructions: |
  Formatting Standards:
  - Present tabular data with clear headers
  - Include visualizations for trends and distributions
  - Use professional, analytical tone
  - Apply flagging logic per thresholds defined above
```
