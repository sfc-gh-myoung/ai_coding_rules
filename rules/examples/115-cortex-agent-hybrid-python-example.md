# 115 Example: Cortex Agent Hybrid (Python SDK)

> **EXAMPLE FILE** - Reference implementation for `115-snowflake-cortex-agents-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 115-snowflake-cortex-agents-core.md
**Demonstrates:** Hybrid agent creation using Python SDK with Semantic View + Cortex Search
**Use When:** Building Cortex Agents programmatically in Python applications or notebooks
**Version:** 1.0
**Last Validated:** 2026-01-23

## Prerequisites

- [ ] Python 3.8+ with snowflake-snowpark-python>=1.15.0
- [ ] Valid Snowflake connection with CORTEX privileges
- [ ] Existing semantic view and Cortex Search service
- [ ] Environment: Snowflake notebook, Streamlit in Snowflake, or local Python

## Implementation

```python
from snowflake.snowpark import Session
from snowflake.cortex import Agent, AgentConfig, Tool

# Step 1: Establish session
session = Session.builder.config("connection_name", "my_connection").create()

# Step 2: Verify prerequisites (MANDATORY)
prereq_check = session.sql("""
    SELECT 
        (SELECT VALUE FROM TABLE(FLATTEN(PARSE_JSON(
            SYSTEM$SHOW_PARAMETERS_AS_JSON('CORTEX_ENABLED_CROSS_REGION', 'ACCOUNT')
        ))) WHERE VALUE:name = 'CORTEX_ENABLED_CROSS_REGION'):value::STRING AS cortex_enabled
""").collect()
assert prereq_check[0]['CORTEX_ENABLED'] == 'true', "Cortex not enabled"

# Step 3: Test tools independently before agent creation
# Test semantic view
sv_test = session.sql("""
    SELECT * FROM TABLE(SEMANTIC_VIEW('my_db.my_schema.sales_semantic_view')) LIMIT 1
""").collect()
assert len(sv_test) > 0, "Semantic view not accessible"

# Test Cortex Search
search_test = session.sql("""
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'my_db.my_schema.docs_search_service',
        '{"query": "test", "columns": ["chunk"], "limit": 1}'
    )
""").collect()
assert search_test is not None, "Cortex Search not accessible"

# Step 4: Define planning instructions
PLANNING_INSTRUCTIONS = """
## Tool Selection Guidelines

**When to use sales_semantic_view:**
- Questions about sales metrics, revenue, customer counts
- Aggregations and comparisons of business data
- Any question requiring numerical analysis

**When to use docs_search_service:**
- Questions about policies, procedures, or guidelines
- Searching for specific document content
- Reference materials and definitions

**Orchestration Rules:**
1. Start with the most specific tool for the question
2. Sequential execution only - never call both tools simultaneously
3. For compound questions, break into sub-questions and route appropriately
"""

RESPONSE_INSTRUCTIONS = """
## Response Format

**For numerical answers:**
- Lead with the key metric
- Include time period and scope

**Flagging Rules:**
- Flag as APPROXIMATE if based on partial data
- Flag as POLICY_REFERENCE if citing documents
"""

# Step 5: Create agent configuration
agent_config = AgentConfig(
    model="claude-3-5-sonnet",
    tools=[
        Tool(
            name="sales_semantic_view",
            type="semantic_view",
            reference="my_db.my_schema.sales_semantic_view",
            description="Query structured sales and revenue data"
        ),
        Tool(
            name="docs_search_service", 
            type="cortex_search",
            reference="my_db.my_schema.docs_search_service",
            description="Search company policies and documentation"
        )
    ],
    planning_instructions=PLANNING_INSTRUCTIONS,
    response_instructions=RESPONSE_INSTRUCTIONS
)

# Step 6: Create agent
agent = Agent.create(
    session=session,
    name="my_hybrid_agent",
    config=agent_config,
    comment="Sales analytics with document search"
)

# Step 7: Test agent execution
def test_agent(question: str) -> str:
    """Test agent with a question and return response."""
    result = agent.run(question)
    return result.response

# Component tests
print("Testing structured data query...")
response1 = test_agent("What was total revenue in Q4 2025?")
print(f"Response: {response1}")

print("Testing document search...")
response2 = test_agent("What is our return policy?")
print(f"Response: {response2}")

# Step 8: Grant access (if needed)
session.sql("""
    GRANT USAGE ON CORTEX AGENT my_hybrid_agent TO ROLE analyst_role
""").collect()
```

## Validation

```python
# Verify agent exists
agents = session.sql("SHOW CORTEX AGENTS LIKE 'my_hybrid_agent'").collect()
assert len(agents) == 1, "Agent not created"

# Test tool routing
test_cases = [
    ("What was revenue last month?", "semantic_view"),  # Should use SV
    ("What is our refund policy?", "cortex_search"),    # Should use CS
    ("Tell me a joke", "decline"),                       # Should decline
]

for question, expected_tool in test_cases:
    response = agent.run(question, return_metadata=True)
    print(f"Q: {question}")
    print(f"Tool used: {response.tools_used}")
    print(f"Response: {response.response[:100]}...")
    print("---")

# Verify RBAC
grants = session.sql("SHOW GRANTS ON CORTEX AGENT my_hybrid_agent").collect()
print(f"Grants: {grants}")
```

**Expected Result:**
- Agent creation succeeds with both tools configured
- Structured data questions route to semantic view
- Policy questions route to Cortex Search
- Out-of-scope questions are declined gracefully
- Only authorized roles have access
