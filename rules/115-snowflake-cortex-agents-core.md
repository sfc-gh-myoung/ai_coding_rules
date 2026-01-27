# Snowflake Cortex Agents Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Cortex Agents patterns. Load for Cortex Agent tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**Keywords:** multi-tool agents, planning instructions, testing, troubleshooting, semantic views, create agent, debug agent, agent not working, tool execution failed, agent error, fix agent
**TokenBudget:** ~2150
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
2. Define objectives; select smallest model that meets quality
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
    2. For quantitative: Use appropriate analyst tool first
    3. For qualitative: Use document_search for context
    4. For mixed: Get data first, then augment with documents
    5. Always cite data sources
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

**Use Cases:** Comprehensive analysis across different data domains

**Tool Configuration:** Multiple Cortex Analyst tools, each with domain-specific semantic views

**When to Use:** Queries span multiple analytical domains regularly

### Single-Domain Analytics (Single Cortex Analyst)

**Use Cases:** Focused analysis within specific domain

**Tool Configuration:** Single Cortex Analyst tool with domain-specific semantic view

**When to Use:** Deep analysis needed within one area

### Research-Focused (Cortex Search Only)

**Use Cases:** Document synthesis, policy research, compliance checking

**Tool Configuration:** Multiple Cortex Search tools for different document types

**When to Use:** No quantitative calculations required

### Hybrid (Multiple Analysts + Search)

**Use Cases:** Investment decisions, comprehensive analysis

**Tool Configuration:** Multiple Cortex Analyst + Cortex Search tools

**When to Use:** Queries mix quantitative and qualitative needs frequently

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
