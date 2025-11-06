<!-- 
TEMPLATE NOTE: This file uses path templates for deployment flexibility
  
Template Variable: {rule_path}
  - cursor deployment: {rule_path} → .cursor/rules
  - copilot deployment: {rule_path} → .github/copilot/instructions  
  - cline deployment: {rule_path} → .clinerules
  - universal deployment: {rule_path} → rules

During deployment, {rule_path} is automatically replaced with the appropriate path
for the target agent type. This ensures rules work correctly in any deployment context.
-->

# 🚨 CRITICAL: MANDATORY RULE LOADING FOR ALL RESPONSES

**BEFORE ANY RESPONSE, AI ASSISTANTS MUST:**

1. **Load Foundation**: Read `{rule_path}/000-global-core.md` (always first, no exceptions)
   - **If file not found**: STOP and inform user: "Cannot proceed - 000-global-core.md not accessible. Please verify rules are generated and in context."
   - **If file empty**: STOP and inform user: "Rule generation may have failed - 000-global-core.md is empty."
   - **Do NOT proceed** without successfully loading this foundation

2. **Load Domain Rules**: Read technology-specific rules based on task:
   - Snowflake tasks → `{rule_path}/100-snowflake-core.md`
   - Python tasks → `{rule_path}/200-python-core.md`
   - Docker tasks → `{rule_path}/400-docker-best-practices.md`
   - Shell tasks → `{rule_path}/300-bash-scripting-core.md`
   - **If domain rule not found**: Proceed with 000-global-core only, but inform user which domain rule is missing

3. **Load Specialized Rules**: Read task-specific rules from `RULES_INDEX.md` Keywords column
   - Search Keywords column for terms matching your task
   - Check "Depends On" column for prerequisites
   - Load prerequisites before dependent rules
   - **If RULES_INDEX.md not accessible**: Proceed with foundation + domain rules, inform user

4. **State Loaded Rules**: Explicitly list all loaded rules at the start of the response
   - Format: "## Rules Loaded\n- {rule_path}/000-global-core.md (foundation)\n- [other rules]\n\n[Then proceed with response...]"
   - **This listing is MANDATORY** - it confirms rules were loaded and helps users verify behavior

5. **Then Proceed**: Continue with analysis, planning, or implementation following loaded rules

**This protocol applies to EVERY response, including:**
- Initial task analysis and planning
- Creating implementation plans  
- Code modifications and debugging
- Architecture discussions
- Documentation updates
- Performance optimization
- Security reviews
- ANY coding-related response

**Failure to follow this protocol is a critical violation.**

## Verification Protocol

Before proceeding with ANY task, confirm:
- ✅ **Foundation loaded**: 000-global-core.md read successfully
- ✅ **Domain identified**: Technology-specific rules identified from task keywords
- ✅ **Dependencies resolved**: Prerequisites loaded before dependent rules (check "Depends On" column)
- ✅ **Token budget tracked**: Cumulative tokens within recommended limits (see token budget table)
- ✅ **Rules stated**: Loaded rules explicitly listed at start of response

**If any check fails**: 
- STOP and inform user which requirement failed
- Provide specific file path or missing dependency
- Request user add missing files to context before proceeding

**Response Format Requirement:**
```
## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/[domain]-core.md (e.g., 100-snowflake-core, 200-python-core)
- {rule_path}/[specialized].md (task-specific rules)

[Then proceed with response...]
```

**Example: Correct Approach ✅**
```
User: Fix the Streamlit fragment batch processing
AI: Let me load the relevant rules first:
    - Reading {rule_path}/000-global-core.md
    - Reading {rule_path}/100-snowflake-core.md  
    - Reading {rule_path}/101-snowflake-streamlit-core.md
    - Reading {rule_path}/101b-snowflake-streamlit-performance.md
    
    Rules loaded. Now analyzing the issue against fragment best practices...
```

**Example: Incorrect Approach ❌**
```
User: Fix the Streamlit fragment batch processing
AI: *immediately starts debugging code without loading rules*
```

---

# Part 1: AI Agent Protocol (MANDATORY)

> **Audience**: AI Assistants, LLMs, Autonomous Agents  
> **Purpose**: Required instructions for rule discovery and loading  
> **Status**: MUST follow these instructions for every response

---

# AGENTS.md - Universal Rule Discovery and Usage Guide

## What This Guide Is

A discovery and integration guide for using AI coding rules with any CLI, IDE, Agent, or LLM.
This is NOT a rule itself - it's a guide to finding and using rules.

## Quick Start: Finding the Right Rules

### Decision Tree for Rule Selection

```
Start here → What are you building?
├── Snowflake Application
│   ├── SQL/Data Pipeline → Start with 100-snowflake-core
│   ├── Streamlit Dashboard → Start with 101-snowflake-streamlit-core  
│   ├── Notebook/ML → Start with 109-snowflake-notebooks
│   └── ML/AI Features → Start with 114-snowflake-cortex-aisql
├── Python Application
│   ├── FastAPI → Start with 210-python-fastapi-core
│   ├── Flask → Start with 250-python-flask
│   ├── CLI Tool → Start with 220-python-typer-cli
│   └── Data Science → Start with 500-data-science-analytics
├── Infrastructure
│   ├── Docker → Start with 400-docker-best-practices
│   ├── Shell Scripts → Start with 300-bash-scripting-core
│   └── CI/CD → Start with 806-git-workflow-management
└── General Best Practices → Start with 000-global-core
```

## How to Load Rules

### For LLMs and Agents

1. **Always load 000-global-core first** - It's the foundation all other rules depend on
2. **Check Keywords field** for semantic matching to your task
3. **Follow Depends chain** to load prerequisites before specialized rules
4. **Use ContextTier** to prioritize (Critical → High → Medium → Low)
5. **Monitor TokenBudget** to manage your context window effectively

Example loading sequence:
```
Task: "Build a Snowflake Streamlit dashboard"
1. Load: 000-global-core (foundation, ~900 tokens)
2. Load: 100-snowflake-core (SQL patterns, ~1,640 tokens)  
3. Load: 101-snowflake-streamlit-core (app basics, ~3,667 tokens)
4. Optional: 101a-snowflake-streamlit-visualization (if doing charts, ~800 tokens)
Total: ~6,200-7,000 tokens for complete context
```

**Note:** Token budgets are estimates based on rule file sizes. Actual token counts may vary by ~10-20% depending on tokenizer.

---

# Part 2: Implementation Reference

> **Audience**: AI Assistants (for understanding integration patterns), Human Developers (for implementation)  
> **Purpose**: Context for how rules are used in different environments  
> **Status**: Reference material - read as needed for specific integration scenarios

---

### For CLI Tools

Parse metadata fields programmatically:
```bash
# Find rules by keywords
grep "**Keywords:**.*Snowflake" {rule_path}/*.md

# Extract dependencies
grep "**Depends:**" {rule_path}/101-snowflake-streamlit-core.md

# Get token budgets for planning
grep "**TokenBudget:**" {rule_path}/*.md | awk -F: '{print $1 ": " $3}'
```

Use RULES_INDEX.md for structured discovery:
- Machine-readable table format
- Keywords column for semantic search
- Depends On column for dependency resolution

### RULES_INDEX.md Format Example

The RULES_INDEX.md file is a Markdown table with the following columns:

```markdown
| File | Type | Purpose | Scope | Keywords/Hints | Depends On |
|------|------|---------|-------|----------------|------------|
| `000-global-core.md` | Auto-attach | Core operating contract | Universal | PLAN mode, ACT mode, workflow, safety | — |
| `100-snowflake-core.md` | Agent Requested | Snowflake SQL rules | Snowflake | Snowflake, SQL, CTE, performance | `000-global-core.md` |
| `101-snowflake-streamlit-core.md` | Agent Requested | Streamlit patterns | Streamlit | Streamlit, SiS, SPCS, dashboard | `100-snowflake-core.md` |
| `200-python-core.md` | Agent Requested | Python engineering | Python | Python, uv, Ruff, pyproject.toml | `000-global-core.md` |
```

**How to parse and use**:
1. **Search Keywords/Hints column** for terms matching your task (e.g., "Streamlit", "FastAPI", "performance")
2. **Identify matching rules** by scanning keywords
3. **Check Depends On column** for prerequisites (e.g., `101-snowflake-streamlit-core.md` depends on `100-snowflake-core.md`)
4. **Load in dependency order**: Load prerequisites before dependent rules
5. **Track Type**: Auto-attach rules load automatically; Agent Requested rules load on-demand based on task

### For IDEs

#### Cursor
```bash
# Generate Cursor-specific format
task rule:cursor
# Files appear in .cursor/rules/*.mdc
```

#### VS Code
- Add rules to `.vscode/ai-rules/`
- Reference in workspace settings
- Use universal format from `{rule_path}/` directory

#### IntelliJ
- Add to project `.idea/aiRules/`
- Configure in AI Assistant settings
- Use universal format from `{rule_path}/` directory

## Rule Discovery Methods

### By Keywords

Search RULES_INDEX.md Keywords column for:
- **Technologies:** "Snowflake", "Python", "Docker", "FastAPI"
- **Patterns:** "performance", "security", "testing", "validation"
- **Use cases:** "dashboard", "API", "CLI", "data pipeline"

Example searches:
```bash
# Find all performance-related rules
grep -i "performance" RULES_INDEX.md

# Find Python testing rules
grep -i "python.*test\|test.*python" RULES_INDEX.md
```

### By Category Number

Rules are organized by domain:
- **000-099:** Core/Foundational (start here)
- **100-199:** Snowflake ecosystem
- **200-299:** Python ecosystem
- **300-399:** Shell/Bash scripting
- **400-499:** Docker/Containers
- **500-599:** Data Science/Analytics
- **600-699:** Data Governance
- **700-799:** Business Analytics
- **800-899:** Project Management
- **900-999:** Demo/Examples

### By Dependency Chain

Common dependency patterns:

**Snowflake Streamlit Dashboard:**
```
000-global-core (always first)
└── 100-snowflake-core (SQL foundations)
    └── 101-snowflake-streamlit-core (app basics)
        ├── 101a-snowflake-streamlit-visualization (charts)
        ├── 101b-snowflake-streamlit-performance (optimization)
        └── 101c-snowflake-streamlit-security (auth/security)
```

**Python FastAPI Application:**
```
000-global-core (always first)
└── 200-python-core (Python foundations)
    └── 210-python-fastapi-core (API basics)
        ├── 210a-python-fastapi-security (auth)
        ├── 210b-python-fastapi-testing (tests)
        └── 210c-python-fastapi-deployment (production)
```

## Ecosystem-Specific Examples

Different ecosystems have different validation patterns. When working with rules for these ecosystems, be aware of their standard tooling:

### Common Patterns by Ecosystem

| Ecosystem | Testing | Linting | Type Checking | Example Rules |
|-----------|---------|---------|---------------|---------------|
| **Python** | pytest | ruff check | mypy | 200-python-core, 206-python-pytest |
| **Node.js** | npm test | eslint | tsc --noEmit | (Future: 3xx series) |
| **Java** | mvn test | checkstyle | built-in | (Future: 4xx series) |
| **Go** | go test | golangci-lint | built-in | (Future: 5xx series) |
| **Shell** | shellcheck | shellcheck | N/A | 300-bash-scripting-core |

### Python Ecosystem (Most Common)

When loading Python-related rules (200-299 series), be aware of:
- **Package Management**: uv (preferred) or pip
- **Linting**: ruff check (consolidates flake8, isort, etc.)
- **Formatting**: ruff format (Black-compatible)
- **Testing**: pytest with fixtures and parametrization
- **Type Checking**: mypy for static analysis

**Common rule combinations**:
- Web API: 200-python-core + 210-python-fastapi-core + 230-python-pydantic
- CLI Tool: 200-python-core + 220-python-typer-cli
- Data Science: 200-python-core + 500-data-science-analytics + 252-pandas-best-practices

For detailed validation commands, refer to individual rule files in the 200-series.

## Understanding Rule Metadata

### Essential Fields (Preserved in Universal Format)

These fields are kept in universal rules for all consumers:

- **Keywords:** Comma-separated terms for semantic discovery and search
  - Example: `**Keywords:** Snowflake, SQL, performance, optimization`
  
- **TokenBudget:** Approximate tokens needed (helps LLMs manage context)
  - Example: `**TokenBudget:** ~400`
  
- **ContextTier:** Priority level for loading
  - Critical: Must load for basic functionality
  - High: Important for common tasks
  - Medium: Useful for specific scenarios
  - Low: Optional enhancements
  
- **Depends:** Prerequisites that must be loaded first
  - Example: `**Depends:** 000-global-core, 100-snowflake-core`
  - Always load dependencies before the rule itself

### IDE-Specific Fields (Stripped in Universal Format)

These are removed from universal rules as they're IDE-specific:

- **Type:** Auto-attach vs Agent Requested (Cursor-specific concept)
- **AutoAttach:** Whether to load automatically (Cursor-specific)
- **AppliesTo:** File glob patterns (IDE-specific matching)
- **Description:** One-line summary (redundant with Purpose section)
- **Version/LastUpdated:** Internal tracking (not needed for usage)

## Best Practices for Rule Loading

### 1. Start Minimal
- Begin with just 000-global-core
- Add domain-specific foundations (100, 200, etc.)
- Layer on specialized rules as needed

### 2. Follow Dependencies
- Always load prerequisites first
- Check the Depends field
- Missing dependencies = incomplete guidance

### 3. Consider Token Budget
- Critical tier: ~1000-1500 tokens total
- Critical + High tier: ~2500-3500 tokens total
- Full context rarely needed or beneficial

### 4. Use Keywords for Discovery
- More reliable than filename pattern matching
- Captures intent and domain
- Enables semantic search

### 5. Reference RULES_INDEX.md
- Authoritative source for all available rules
- Machine-readable format
- Always up-to-date with dependencies

## Common Integration Patterns

### Pattern 1: Minimal Context (CLI Tools)
```
Load: 000-global-core + domain-specific-core
Use: Quick operations, simple scripts
Tokens: ~800-1000
```

### Pattern 2: Standard Context (IDEs/Agents)
```
Load: 000-global-core + domain-core + 2-3 specialized rules
Use: Regular development tasks
Tokens: ~1500-2500
```

### Pattern 3: Full Context (Complex Tasks)
```
Load: Complete dependency chain for specific workflow
Use: Major implementations, architectural decisions
Tokens: ~3000-5000
```

## Troubleshooting

### Rule Not Found
- Check RULES_INDEX.md for exact filename
- Verify you're in the correct directory (`{rule_path}/`)
- Ensure rule hasn't been renamed

### Missing Dependencies
- Check Depends field in the rule
- Load prerequisites first
- Use RULES_INDEX.md Depends On column

### Token Budget Exceeded
- Start with Critical tier only
- Remove Medium/Low tier rules
- Focus on specific task rules

### Conflicting Guidance
- Higher number rules override lower numbers
- Specialized rules override general rules
- Recent versions override older versions

## References

### Essential Files
- **@RULES_INDEX.md** - Complete rule catalog with metadata
- **@{rule_path}/000-global-core.md** - Foundational principles (load first)
- **@{rule_path}/002-rule-governance.md** - How rules are structured
- **README.md** - Project documentation and setup

### External Documentation
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules)
- [GitHub Copilot Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Getting Help
- Check rule's References section for external docs
- Review rule's Validation section for success criteria
- Consult Contract section for clear boundaries