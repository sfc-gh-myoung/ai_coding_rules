# Snowflake Cortex Agents Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Cortex Agents patterns. Load for Cortex Agent tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** multi-tool agents, planning instructions, testing, troubleshooting, semantic views, create agent, debug agent, agent not working, tool execution failed, agent error, fix agent
**TokenBudget:** ~3100
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 106-snowflake-semantic-views-core.md
**LoadTrigger:** kw:agent, kw:cortex-agent

## Scope

**What This Rule Covers:**
Core patterns to design, configure, and deploy Cortex Agents including agent archetypes, tool configurations, and essential anti-patterns.

**When to Load This Rule:**
- Creating or configuring Cortex Agents
- Designing agent archetypes (single-tool, multi-tool, hybrid)
- Configuring tools and orchestration patterns

**For planning/response instructions, see `115a-snowflake-cortex-agents-instructions.md`.**
**For testing, RBAC, observability, cost management, see `115b-snowflake-cortex-agents-operations.md`.**

> **Investigation Required**
> Before creating any Cortex Agent, verify ALL prerequisites:
> - [ ] Cortex features enabled: `SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT`
> - [ ] Tools exist and work: Test semantic views, Cortex Search services independently
> - [ ] Role has CORTEX privileges: `SHOW GRANTS TO ROLE role_name`
>
> **STOP if any condition fails. DO NOT create agents using assumptions.**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **106-snowflake-semantic-views-core.md** - Semantic views as agent tools

**Related:**
- **115a-snowflake-cortex-agents-instructions.md** - Planning and response instructions
- **115b-snowflake-cortex-agents-operations.md** - Testing, RBAC, observability
- **116-snowflake-cortex-search.md** - Cortex Search for document retrieval

### Related Examples

- **examples/115-cortex-agent-prerequisites-example.md** - Pre-flight validation workflow
- **examples/115-cortex-agent-hybrid-sql-example.md** - Multi-tool agent (SQL DDL)
- **examples/115-cortex-agent-hybrid-python-example.md** - Multi-tool agent (Python SDK)

### External Documentation
- [Cortex Agents Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Cortex Agent Tools](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-tools)

## Contract

### Inputs and Prerequisites

- Snowflake account with Cortex Agents availability
- Grounding sources (semantic views, Cortex Search indices)
- Tool catalog with least-privilege permissions

### Mandatory

Cortex Agents, semantic views, Cortex Search, Cortex Analyst

### Forbidden

- Unbounded tool execution without guardrails
- Prompts containing secrets/PII
- Business rule flagging in semantic views (belongs in agent instructions)

### Execution Steps

1. Choose agent archetype based on use case
2. Define objectives; select smallest model that meets quality (prefer llama3.1-8b for classification tasks; scale to 70b only for complex multi-step reasoning — see 114-snowflake-cortex-aisql.md model ladder)
3. Ground with governed sources (semantic views, curated indices)
4. Configure tools with clear descriptions
5. Write planning instructions for tool selection
6. Define response instructions with flagging logic
7. Test components independently before integration

### Output Format

Agent configs, planning templates, SQL/Python snippets

### Validation

- Component tests pass (tools work independently)
- Integration tests pass (orchestration works)
- RBAC enforced (least privilege)

### Design Principles

- Choose archetype based on tool combination and use case
- Smallest sufficient model reduces cost and risk
- Ground with curated, governed sources; prefer semantic views
- **CRITICAL:** Flagging logic belongs in agent instructions, NEVER in semantic views
- **Timeout:** Set query timeout to 120s for Cortex Analyst tools; 30s for Cortex Search tools
- **Cost:** Each agent query consumes credits for model inference + tool execution; monitor via QUERY_HISTORY filtering on query type
- Test tools independently before integration

### Post-Execution Checklist

- [ ] Agent created with clear purpose and description
- [ ] Tools defined with comprehensive descriptions
- [ ] Planning instructions guide multi-step reasoning
- [ ] Response instructions format output appropriately
- [ ] Agent tested with in-scope and out-of-scope questions
- [ ] RBAC configured for agent access

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Vague Tool Descriptions

**Problem:** Tool description like "Gets data" - too vague for agent to select correctly.

**Correct Pattern:**
```python
tools = [{
    "name": "sales_revenue_analyst",
    "description": """Query sales revenue data including:
    - Total revenue by time period
    - Revenue by product category, region
    - Top N products by revenue
    Use for quantitative revenue questions."""
}]
```

### Anti-Pattern 2: Missing Planning Instructions for Multi-Tool Agents

**Problem:** No guidance on tool orchestration - agent guesses randomly.

**Correct Pattern:**
```python
agent = cortex.Agent(
    name="business_intelligence_agent",
    tools=[sales_tool, marketing_tool, document_search],
    planning_instructions="""
    1. Identify query type (quantitative, qualitative, mixed)
    2. For quantitative: Use CORTEX_ANALYST for structured data queries against semantic views
    3. For qualitative: Use document_search for context via CORTEX_SEARCH_SERVICE
    4. For mixed: Get data first, then augment with documents
    5. Always cite data sources

    Tool Selection:
    - Structured data query -> CORTEX_ANALYST + semantic view
    - Document search -> CORTEX_SEARCH_SERVICE + search service name
    - Both needed -> Configure both tools in agent definition
    """
)
```

### Anti-Pattern 3: Business Logic in Semantic Views

**Problem:** Embedding flagging thresholds in semantic view instead of agent instructions.

**Correct Pattern:**
```yaml
# BAD: In semantic view
"Flag holdings where weight > 5% as concentrated risk"

# GOOD: In agent response instructions
"When presenting holdings:
1. Calculate weight using portfolio_analyzer
2. Flag any holding >5% as 'concentrated risk'
3. Explain concentration implications"
```

### Anti-Pattern 4: Not Testing Out-of-Scope Questions

**Problem:** Only testing happy-path questions.

**Correct Pattern:**
```python
test_questions = [
    # In-scope
    "What was Q4 revenue?",
    # Out-of-scope (should gracefully decline)
    "What's the weather?",
    "Book me a flight",
    # Edge cases
    "Revenue for year 3000"
]
```

## Agent Archetypes

### Multi-Domain Analytics (Multiple Cortex Analysts)

**Select when:** Queries routinely span 2+ data domains (e.g., sales AND marketing)

**Tool Configuration:** Multiple Cortex Analyst tools, each with domain-specific semantic views

### Single-Domain Analytics (Single Cortex Analyst)

**Select when:** All queries target one analytical domain with a single semantic view

**Tool Configuration:** Single Cortex Analyst tool with domain-specific semantic view

### Research-Focused (Cortex Search Only)

**Select when:** No quantitative calculations needed; purely document-based Q&A

**Tool Configuration:** Multiple Cortex Search tools for different document types

### Hybrid (Multiple Analysts + Search)

**Select when:** >30% of queries mix quantitative data with qualitative document context

**Tool Configuration:** Multiple Cortex Analyst + Cortex Search tools

## Tool Configuration

### Cortex Analyst Tool Pattern

```yaml
Tool Name: portfolio_analyzer
Type: Cortex Analyst
Semantic View: ANALYTICS.AI.PORTFOLIO_VIEW
Warehouse: ANALYTICS_WH    # REQUIRED for cost tracking
Query Timeout: 120
Description: "Use for quantitative portfolio analysis including holdings, exposures, performance. Use for questions about numbers, percentages, rankings."
```

**Key Elements:**
- **Warehouse:** MUST specify explicitly (prevents execution errors)
- **Description:** Three parts: purpose, capabilities, when-to-use

### Cortex Search Tool Pattern

```yaml
Tool Name: search_research_reports
Type: Cortex Search
Service: DOCS.AI.RESEARCH_SERVICE
ID Column: DOCUMENT_ID
Title Column: DOCUMENT_TITLE
Description: "Search research reports for analyst opinions, ratings, commentary. Use for questions about analyst views, recommendations."
```

### Best Practices

**Tool Ordering:** List frequently used tools first
**Description Clarity:** Define WHEN to use each tool (avoid overlaps)

**Anti-Pattern:**
```
Tool A: "Use for portfolio analysis"
Tool B: "Use for investment analysis"  # Too similar!
```

**Correct Pattern:**
```
Tool A: "Use for holdings, weights, exposure analysis"
Tool B: "Use for risk metrics, volatility, correlation"
```

## Prerequisites Validation

```sql
-- Check Cortex availability
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Verify semantic view access
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 5;

-- Verify Cortex Search service
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- Verify role permissions
SHOW GRANTS TO ROLE agent_runner;

-- Test Cortex function
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

## Tool Error Handling

### Common Tool Failures and Recovery

**Semantic view returns no results:**
- Verify semantic view exists: `SHOW SEMANTIC VIEWS IN SCHEMA <schema>;`
- Test semantic view independently: `SELECT * FROM <semantic_view> LIMIT 5;`
- Check warehouse is specified and running

**Cortex Search returns irrelevant results:**
- Verify search service is active: `SHOW CORTEX SEARCH SERVICES IN SCHEMA <schema>;`
- Check index freshness and document count
- Refine tool description to clarify when to use

**Agent returns "tool execution failed":**
1. Test the failing tool independently (outside agent context)
2. Check role permissions: `SHOW GRANTS TO ROLE <agent_role>;`
3. Verify warehouse exists and is not suspended
4. Check Cortex availability: `SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;`

## Agent Lifecycle Management

```sql
-- Create agent (COMMENT is mandatory for discoverability)
CREATE OR REPLACE CORTEX AGENT my_agent
  COMMENT = 'Purpose description'  -- REQUIRED: describe the agent's purpose
  AS TOOLS = ['TOOL1'] PLANNING_INSTRUCTIONS = $$ ... $$;

-- Modify agent (e.g., update instructions)
CREATE OR REPLACE CORTEX AGENT my_agent
  COMMENT = 'Updated purpose'
  AS TOOLS = ['TOOL1', 'TOOL2'] PLANNING_INSTRUCTIONS = $$ Updated ... $$;

-- Remove agent
DROP CORTEX AGENT IF EXISTS my_agent;

-- List agents
SHOW CORTEX AGENTS;

-- Describe agent configuration
DESCRIBE CORTEX AGENT my_agent;
```

## YAML Agent Spec Format (Programmatic API)

When creating agents via the REST API or Python SDK (rather than SQL DDL), the agent
is defined with a YAML specification. Key formatting requirements:

### sample_questions: Use Object Format (NOT Plain Strings)

```yaml
# CORRECT -- objects with question/answer keys
instructions:
  sample_questions:
    - question: "What is the total spend by location this week?"
      answer: "I'll query the purchasing data to calculate total spend broken down by location for the current week."
    - question: "Which items have the worst ML forecast accuracy?"
      answer: "I'll analyze forecast accuracy metrics to identify items with the largest deviation."

# INCORRECT -- plain strings cause 399510 (22023) spec validation error
instructions:
  sample_questions:
    - "What is the total spend by location this week?"
    - "Which items have the worst ML forecast accuracy?"
```

### String Quoting

The Snowflake agent spec parser is stricter than standard YAML. Always quote string values explicitly:

```yaml
tools:
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "my_analyst"
      description: "Converts natural language to SQL queries"

tool_resources:
  my_analyst:
    semantic_view: "DB.SCHEMA.MY_SEMANTIC_VIEW"
```

### Instruction Strings: Prefer Inline Over Block Scalars

```yaml
# PREFERRED -- inline quoted strings (matches Snowflake documentation examples)
instructions:
  orchestration: "You are an assistant. Route questions through the analyst tool."
  response: "Always include context. Format dollar amounts with $ and 2 decimal places."

# AVOID -- block scalars (valid YAML but not in Snowflake examples, may cause issues)
instructions:
  orchestration: >
    You are an assistant.
    Route questions through the analyst tool.
```

## Output Format Examples

```sql
CREATE OR REPLACE CORTEX AGENT AGENT_ASSET_ANALYST
  COMMENT = 'Agent for analyzing asset performance using semantic views'
  AS
    TOOLS = ['SEM_ASSET_PERFORMANCE']
    PLANNING_INSTRUCTIONS = $$
    You are an expert asset performance analyst.
    
    When answering questions:
    1. Use SEM_ASSET_PERFORMANCE for asset data
    2. Break complex questions into multiple queries
    3. Calculate derived metrics when needed
    4. Cite specific data points
    $$
    RESPONSE_INSTRUCTIONS = $$
    **Analysis Summary:** [1-2 sentence answer]
    
    **Key Findings:**
    - [Finding with numbers]
    - [Finding with numbers]
    
    **Data Source:** [Semantic view queried]
    $$;

-- Test the agent
SELECT * FROM TABLE(AGENT_QUERY(
  'AGENT_ASSET_ANALYST',
  'Which asset type has highest failure rate?'
));
```
