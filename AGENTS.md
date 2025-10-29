# AGENTS.md - Universal Rule Discovery and Usage Guide

## What This Guide Is

A discovery and integration guide for using AI coding rules with any CLI, IDE, Agent, or LLM.
This is NOT a rule itself - it's a guide to finding and using rules.

## ⚠️ MANDATORY RULE LOADING PROTOCOL (For AI Assistants)

**CRITICAL**: Before beginning ANY coding task, you MUST follow this protocol:

### Step 1: Analyze the Task (Required)

Identify:
- Primary technology domain (Snowflake, Python, Docker, etc.)
- Specific framework/tool (Streamlit, FastAPI, etc.)
- Task type (debugging, new feature, performance, security)

### Step 2: Load Foundation Rules (Always Required)

Execute in order:
1. Read `rules/000-global-core.md` (ALWAYS first)
2. Read relevant domain core rule based on technology:
   - Snowflake → `rules/100-snowflake-core.md`
   - Python → `rules/200-python-core.md`
   - Docker → `rules/400-docker-best-practices.md`
   - Bash → `rules/300-bash-scripting-core.md`

### Step 3: Load Specialized Rules (Based on Task)

Search `RULES_INDEX.md` Keywords column and load:
- Technology-specific rules (e.g., `101-snowflake-streamlit-core.md`)
- Pattern-specific rules (e.g., `101b-snowflake-streamlit-performance.md`)
- Feature-specific rules (e.g., `210a-python-fastapi-security.md`)

### Step 4: Verify Rule Loading

Before proceeding with implementation:
- State which rules were loaded
- Confirm rules match the task requirements
- If uncertain, load additional rules rather than guessing

### Enforcement

**Failure to load rules before coding is a protocol violation.**

If you realize mid-task that rules weren't loaded:
1. STOP implementation immediately
2. Load relevant rules
3. Review implementation against rule guidelines
4. Make corrections if needed

### Example: Correct Approach ✅

```
User: Fix the Streamlit fragment batch processing
AI: Let me load the relevant rules first:
    - Reading rules/000-global-core.md
    - Reading rules/100-snowflake-core.md  
    - Reading rules/101-snowflake-streamlit-core.md
    - Reading rules/101b-snowflake-streamlit-performance.md
    
    Rules loaded. Now analyzing the issue against fragment best practices...
```

### Example: Incorrect Approach ❌

```
User: Fix the Streamlit fragment batch processing
AI: *immediately starts debugging code without loading rules*
```

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
1. Load: 000-global-core (foundation, ~450 tokens)
2. Load: 100-snowflake-core (SQL patterns, ~400 tokens)  
3. Load: 101-snowflake-streamlit-core (app basics, ~350 tokens)
4. Optional: 101a-snowflake-streamlit-visualization (if doing charts)
Total: ~1200-1600 tokens for complete context
```

### For CLI Tools

Parse metadata fields programmatically:
```bash
# Find rules by keywords
grep "**Keywords:**.*Snowflake" rules/*.md

# Extract dependencies
grep "**Depends:**" rules/101-snowflake-streamlit-core.md

# Get token budgets for planning
grep "**TokenBudget:**" rules/*.md | awk -F: '{print $1 ": " $3}'
```

Use RULES_INDEX.md for structured discovery:
- Machine-readable table format
- Keywords column for semantic search
- Depends On column for dependency resolution

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
- Use universal format from `rules/` directory

#### IntelliJ
- Add to project `.idea/aiRules/`
- Configure in AI Assistant settings
- Use universal format from `rules/` directory

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

### Python Projects

Typical validation commands:
```bash
# Testing
<test-runner> <test-directory>      # e.g., pytest tests/
<test-runner> --cov=<module>        # e.g., pytest --cov=myapp

# Linting and Formatting
<linter> check <directory>           # e.g., ruff check src/
<formatter> --check <directory>      # e.g., black --check .

# Type Checking
<type-checker> <directory>           # e.g., mypy src/
```

Common Python rule combinations:
- Web API: 200 + 210 (FastAPI) or 250 (Flask)
- CLI Tool: 200 + 220 (Typer) + 230 (Pydantic)
- Data Science: 200 + 500 + 251 (datetime) + 252 (pandas)

### Node.js Projects

Typical validation commands:
```bash
# Testing
npm test                             # or yarn test
npm run test:coverage                # with coverage

# Linting and Formatting
npm run lint                         # ESLint
npm run format:check                 # Prettier check

# Type Checking (TypeScript)
npm run type-check                   # tsc --noEmit
```

### Java Projects

Typical validation commands:
```bash
# Maven projects
mvn test                             # Run tests
mvn checkstyle:check                 # Code style
mvn spotless:check                   # Formatting

# Gradle projects
gradle test                          # Run tests
gradle checkstyleMain                # Code style
gradle spotlessCheck                 # Formatting
```

### Go Projects

Typical validation commands:
```bash
# Testing
go test ./...                        # Run all tests
go test -cover ./...                 # With coverage

# Linting and Formatting
golangci-lint run                    # Comprehensive linting
go fmt ./...                         # Format code
go vet ./...                         # Static analysis
```

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
- Verify you're in the correct directory
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
- **RULES_INDEX.md** - Complete rule catalog with metadata
- **000-global-core.md** - Foundational principles (load first)
- **002-rule-governance.md** - How rules are structured
- **README.md** - Project documentation and setup

### External Documentation
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules)
- [GitHub Copilot Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Getting Help
- Check rule's References section for external docs
- Review rule's Validation section for success criteria
- Consult Contract section for clear boundaries