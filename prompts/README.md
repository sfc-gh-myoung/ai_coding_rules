# Example User Prompts

This directory contains **tutorial prompts** that demonstrate how to effectively communicate tasks to AI assistants using the AI Coding Rules framework.

> **Note:** Skill-specific prompts (like rule review rubrics or rule creation templates) are colocated within their respective skill folders under `skills/`. This folder contains only standalone tutorial examples for user education.

## Why These Examples Matter

AI assistants work best when you provide:
1. **Clear task description** - What you want to accomplish
2. **File type context** - Which files/languages are involved  
3. **Activity keywords** - Type of work (linting, testing, optimization, etc.)

These examples show how to structure your prompts to automatically trigger the right rules from the 84+ specialized rules in this framework.

## Available Examples

### EXAMPLE_PROMPT_01.md - Clear and Complete
**Use Case:** Fixing linting errors with specific error codes

**Pattern:**
```
Task: Fix all Ruff linting errors in Python validation scripts
Files: scripts/rule_validator.py, scripts/index_generator.py
Errors: 9 total (F841 unused variables, UP037 quoted type annotations, W293 whitespace)
```

**Triggers:** Python core rules + linting/formatting rules + Ruff-specific patterns

---

### EXAMPLE_PROMPT_02.md - Context-Rich
**Use Case:** Performance optimization with measurable goals and constraints

**Pattern:**
```
Task: Optimize the semantic view validation performance in the compliance reporting feature
Files: scripts/rule_validator.py (methods: parse_boilerplate_structure, compare_against_boilerplate)
Current behavior: 84 templates validated in ~25 seconds
Expected: Sub-15 second validation time
Constraints: Maintain singleton caching pattern, must support all 8 compliance criteria
```

**Triggers:** Python core rules + performance optimization rules + architecture preservation patterns

---

### EXAMPLE_PROMPT_03.md - Minimal but Effective
**Use Case:** Simple code quality improvements with minimal specification

**Pattern:**
```
Task: Add type hints to the data processor functions
Files: src/data_processor.py
```

**Triggers:** Python core rules + typing best practices

---

### EXAMPLE_PROMPT_04.md - Snowflake Semantic View
**Use Case:** Creating semantic views for Cortex Analyst natural language queries

**Pattern:**
```
Task: Create a semantic view for sales analytics to use with Cortex Analyst
Tables: PROD.SALES.ORDERS (order_id, customer_id, order_date, amount), PROD.SALES.CUSTOMERS (customer_id, customer_name, region)
```

**Triggers:** Snowflake core rules + semantic view DDL rules + Cortex Analyst/Agent rules

---

### EXAMPLE_PROMPT_05.md - Snowflake Cortex Search Service
**Use Case:** Creating Cortex Search services for document retrieval with Cortex Agents

**Pattern:**
```
Task: Create a Cortex Search service for product documentation to use with Cortex Agents
Table: DOCS.RAW.PRODUCT_DOCS (doc_id, content, category, author, published_date, access_tier)
```

**Triggers:** Snowflake core rules + Cortex Search rules + Cortex Agent rules

---

### EXAMPLE_PROMPT_06.md - Snowflake Cortex Agent (Hybrid)
**Use Case:** Creating hybrid Cortex Agents combining quantitative analysis with document search

**Pattern:**
```
Task: Create a Cortex Agent that combines quantitative analysis with document search
Semantic View: ANALYTICS.SEMANTIC.SEM_SALES_METRICS
Search Service: DOCS.SEARCH.PRODUCT_DOCS_SERVICE
```

**Triggers:** Cortex Agent rules + semantic view rules + Cortex Search rules

---

### EXAMPLE_PROMPT_07.md - Snowflake Cortex AI Stack (End-to-End)
**Use Case:** Creating complete Cortex AI stack with semantic view, search service, and hybrid agent

**Pattern:**
```
Task: Create complete Cortex AI stack with semantic view, search service, and hybrid agent
Source Tables:
  - PROD.SALES.ORDERS (order_id, customer_id, order_date, amount, product_id)
  - PROD.SALES.CUSTOMERS (customer_id, customer_name, region)
  - DOCS.RAW.PRODUCT_DOCS (doc_id, content, category, author, published_date)
Target Schema: ANALYTICS.AI
```

**Triggers:** All Snowflake Cortex rules (semantic views + search + agents)

---

## How to Use These Examples

### 1. Match Your Task to a Pattern
- **Linting/formatting** → Use Example 01 pattern
- **Performance optimization** → Use Example 02 pattern  
- **Simple improvements** → Use Example 03 pattern
- **Snowflake semantic views** → Use Example 04 pattern
- **Snowflake Cortex Search** → Use Example 05 pattern
- **Snowflake Cortex Agents** → Use Example 06 pattern
- **Snowflake Cortex AI stack** → Use Example 07 pattern

### 2. Adapt the Template
Replace the specifics with your own:
- File paths
- Task description
- Error messages or constraints
- Expected behavior

### 3. Include Key Elements
Every effective prompt should have:
- **Task:** Clear description of what needs to be done
- **Files:** Specific file paths or patterns (e.g., `*.py`, `Dockerfile`)
- **Context:** Error messages, constraints, or expected behavior (when relevant)

## Quick Reference: Keywords that Trigger Rules

| Keyword in Task | Triggers Loading |
|----------------|------------------|
| "lint", "format", "code quality" | Linting/formatting rules (e.g., 201-python-lint-format) |
| "test", "pytest", "coverage" | Testing rules (e.g., 206-python-pytest) |
| "optimize", "performance", "slow" | Performance rules (e.g., 103-snowflake-performance-tuning) |
| "security", "authentication", "validate input" | Security rules (e.g., 101c-snowflake-streamlit-security) |
| "deploy", "Docker", "CI/CD" | Deployment rules (e.g., 400-docker-best-practices) |
| "Streamlit", "dashboard", "st." | Streamlit rules (e.g., 101-snowflake-streamlit-core) |
| "FastAPI", "REST API", "endpoint" | FastAPI rules (e.g., 210-python-fastapi-core) |
| "pandas", "DataFrame" | Pandas rules (e.g., 252-pandas-best-practices) |
| "SQL", "query", "Snowflake" | Snowflake SQL rules (e.g., 100-snowflake-core) |
| "semantic view", "Cortex Analyst" | Semantic view rules (e.g., 106-snowflake-semantic-views-core) |
| "Cortex Agent", "agent tools" | Cortex Agent rules (e.g., 115-snowflake-cortex-agents-core) |
| "Cortex Search", "search service", "RAG" | Cortex Search rules (e.g., 116-snowflake-cortex-search) |
| "type hints", "typing", "annotations" | Python typing rules (type checking patterns) |

## Tips for Better Results

### Give Specific Rules

While the ai_coding_rules system is designed to automatically load appropriate rules based on keywords and context, it's not a perfect system. As your conversation length and iterations increase, the overall utilization of your token count in the context window will increase. This does increase the likelihood that some of AGENTS.md is potentially lost from the context during compaction.

It is considered a best practice to include specific rule names in your prompt, particularly if you know they are relevant. If the agent does not show the list of rules you expect under RULES_LOADED, stop the agent and tell it to load additional rules or reevaluate which rules are loaded.

### MODE PLAN|ACT

Most of the LLMs and agentic tools will generally do a good job of following the MODE workflow established in AGENTS.md and rules/000-global-core.md. However, some LLMs have a tendency to stay in MODE: ACT even when they should fall back to MODE: PLAN. In such cases, stop the agent and tell it to resume MODE:PLAN. You can also explicitly add MODE:PLAN or MODE:ACT to any prompt to force the agent and LLM into the correct mode.

### Be Specific About File Types
✅ **Good:** "Fix linting in scripts/rule_validator.py"  
❌ **Vague:** "Fix the validation script"

### Include Activity Keywords
✅ **Good:** "Optimize query performance in the Streamlit dashboard"  
❌ **Vague:** "Make the app faster"

### Mention Frameworks/Libraries
✅ **Good:** "Add pytest fixtures for FastAPI endpoint testing"  
❌ **Vague:** "Add tests"

### Provide Error Messages When Available
✅ **Good:** "Fix F841 error: Local variable 'table_end_idx' is assigned but never used"  
❌ **Vague:** "Fix the linting error"

## Expected AI Response Format

When you use these prompt patterns, AI assistants should respond with:

```
MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (Python file type: .py detected)
- rules/201-python-lint-format.md (activity: linting keyword matched)

Task List:
1. [Step 1]
2. [Step 2]
...

[awaits "ACT" authorization before making changes]
```

## Need Help?

If the AI isn't loading the right rules, you can:
1. **Be more explicit:** "Please load 200-python-core and 201-python-lint-format rules"
2. **Reference the index:** "Check RULES_INDEX.md for pytest-related rules"  
3. **Ask first:** "What rules should be loaded for this task?"

## Contributing

To add new example prompts:
1. Create a new file `EXAMPLE_PROMPT_XX.md` (use next sequential number)
2. Follow the existing format: The Prompt → What This Helps → Why It's Good
3. Update this README.md with the new example in the "Available Examples" section
4. Ensure the example demonstrates a distinct use case not covered by existing examples
