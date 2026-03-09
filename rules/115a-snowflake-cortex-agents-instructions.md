# Snowflake Cortex Agents: Planning & Response Instructions

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:agent-instructions
**Keywords:** Cortex Agents, planning instructions, response instructions, tool orchestration, flagging logic, agent prompts, multi-tool orchestration, tool selection, agent prompting, instruction patterns, agent planning
**TokenBudget:** ~4650
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

> **Investigation Required:** Run `DESCRIBE CORTEX AGENT <name>` to review current instruction content before modifying.

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
- Keep instruction text under 4000 characters per field. For longer instructions, reference a document in a Cortex Search service.

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

### 5.1 Flagging Logic Placement

**Key rule:** All flagging, thresholds, and business rules belong in agent response instructions - NEVER in semantic views or Cortex Analyst tools. See Anti-Pattern 1 above for detailed examples.

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

### Anti-Pattern 4: Putting Business Logic in Semantic Views Instead of Agent Instructions

**Problem:** Embedding flagging logic, conditional formatting, or business rules in semantic view expressions instead of agent response instructions.

**Why It Fails:** Semantic views should describe data structure, not implement business rules. Flagging logic in views is hard to update, violates separation of concerns, and prevents per-agent customization.

**Correct Pattern:**
```yaml
# BAD: Flagging logic in semantic view
views:
  - name: revenue_view
    expr: "CASE WHEN revenue > 1000000 THEN 'HIGH_ALERT' ELSE revenue END"

# GOOD: Flagging logic in agent response instructions
Response Instructions: |
  When presenting revenue data:
  1. Get revenue from revenue_view
  2. If revenue > $1M: Flag as "WARNING: HIGH - Exceeds target"
  3. If revenue < $100K: Flag as "WARNING: LOW - Below threshold"
```

### Anti-Pattern 5: Vague Planning Instructions Without Tool Selection Criteria

**Problem:** Planning instructions that say "analyze the question" and "use the appropriate tool" without specifying which tool for which query type.

**Why It Fails:** Agent selects tools randomly; inconsistent behavior across identical queries; no debuggable decision logic.

**Correct Pattern:**
```markdown
# BAD: "Analyze the question and use the appropriate tool"

# GOOD: Explicit tool selection criteria
Planning Instructions:
1. Classify query type:
   - QUANTITATIVE (numbers, rankings): Use sales_analyst tool
   - QUALITATIVE (summaries, context): Use document_search tool
2. For mixed queries: Use analyst first, then augment with search
```

### Anti-Pattern 6: No Graceful Degradation for Missing Data

**Problem:** Agent fails silently or returns cryptic errors when data is unavailable or tool calls return empty results.

**Why It Fails:** Poor user experience; confusing error messages; no fallback guidance; users lose trust in the agent.

**Correct Pattern:**
```markdown
# GOOD: Graceful degradation with helpful guidance
Planning Instructions:
1. Query the sales_analyst tool
2. If results empty or tool unavailable:
   - Explain what data was attempted
   - Specify why unavailable
   - Suggest alternatives
3. If partial data available:
   - Present what is available
   - Note limitations clearly
```

### Anti-Pattern 7: Missing Tone and Formatting Guidance in Response Instructions

**Problem:** Response instructions that say "return the data to the user" without specifying tone, structure, or formatting requirements.

**Why It Fails:** Inconsistent tone across responses; unprofessional formatting; poor readability; no structured insights.

**Correct Pattern:**
```markdown
# BAD: "Return the data to the user."

# GOOD: Explicit tone and formatting
Response Instructions:
Tone: Professional, conversational, helpful
Structure:
1. Brief summary sentence (1-2 lines)
2. Key insights as bulleted list (3-5 bullets)
3. Data table if >5 rows
4. Closing context or recommendation
```
