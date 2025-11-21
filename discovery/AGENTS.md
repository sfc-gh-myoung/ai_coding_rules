<!-- 
TEMPLATE NOTE: This file uses path templates for deployment flexibility
  
Template Variable: {rule_path}
  - cursor deployment: {rule_path} → .cursor/rules (files: *.mdc)
  - copilot deployment: {rule_path} → .github/copilot/instructions (files: *.md)
  - cline deployment: {rule_path} → .clinerules (files: *.md)
  - universal deployment: {rule_path} → rules (files: *.md)

During deployment, {rule_path} is automatically replaced with the appropriate path
for the target agent type, and file extensions are updated to match agent requirements
(.md → .mdc for Cursor). This ensures rules work correctly in any deployment context.
-->

# CRITICAL: MANDATORY RULE LOADING FOR ALL RESPONSES

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

3. **Load Language Rules by File Type** (MANDATORY - Even for "simple" tasks):
   **Analyze file extensions** from the task or workspace to identify required language rules:
   
   | File Extension | Required Core Rule | When to Load |
   |----------------|-------------------|--------------|
   | `.py`, `.pyi` | `{rule_path}/200-python-core.md` | Any Python file editing |
   | `pyproject.toml`, `setup.py` | `{rule_path}/200-python-core.md` | Python project config |
   | `.sql` | `{rule_path}/100-snowflake-core.md` | SQL file editing |
   | `Dockerfile`, `docker-compose.yml` | `{rule_path}/400-docker-best-practices.md` | Docker file editing |
   | `.sh`, `.bash`, `.zsh` | `{rule_path}/300-bash-scripting-core.md` | Shell script editing |
   | `.md` (in `templates/`, `discovery/`) | `{rule_path}/002-rule-governance.md` | Rule file editing |
   | Python + `streamlit run` | `{rule_path}/101-snowflake-streamlit-core.md` | Streamlit app tasks |
   
   **CRITICAL:** Load language rules even for:
   - "Simple" tasks like linting, formatting, syntax fixes
   - Code review, typo fixes, comment updates
   - Adding type hints, docstrings, or imports
   
   **Why:** These tasks require understanding of:
   - Language-specific tooling (Ruff for Python, shellcheck for bash)
   - Best practices and anti-patterns
   - Project structure conventions
   - Dependency management patterns
   
   **Examples:**
   - Task: "Fix linting in scripts/validate.py" → Load 200-python-core (Python file type)
   - Task: "Add comments to queries.sql" → Load 100-snowflake-core (SQL file type)
   - Task: "Optimize Dockerfile" → Load 400-docker-best-practices (Docker file type)

4. **Load Specialized Rules by Activity Keywords**: Read task-specific rules from `RULES_INDEX.md` Keywords column
   - **MANDATORY:** Extract BOTH file type AND activity keywords from the task
   - **Activity Keywords to Search**:
   
   | User Task Contains | Activity Type | Keywords to Search |
   |--------------------|--------------|-------------------|
   | "lint", "format", "code quality", "style" | Code quality | `linting`, `formatting`, `code quality`, `Ruff` |
   | "test", "pytest", "coverage", "fixtures" | Testing | `pytest`, `testing`, `fixtures`, `coverage` |
   | "optimize", "performance", "slow", "cache" | Performance | `optimization`, `performance`, `caching`, `profiling` |
   | "secure", "auth", "validate input", "XSS" | Security | `security`, `authentication`, `validation`, `XSS` |
   | "deploy", "CI/CD", "Docker", "release" | Deployment | `deployment`, `CI/CD`, `Docker`, `automation` |
   | "document", "docstring", "README", "comments" | Documentation | `documentation`, `docstrings`, `README`, `comments` |
   
   - **Search Process**:
     1. Extract file extensions (e.g., `.py` from "scripts/validate.py")
     2. Extract activity keywords (e.g., "linting" from "fix linting errors")
     3. Search RULES_INDEX.md Keywords column for activity matches
     4. Prioritize rules matching BOTH file type AND activity
     5. Check "Depends On" column and load prerequisites first
   
   - **Example - "Fix linting in Python files"**:
     - File type: `.py` → Load `200-python-core.md`
     - Activity: "linting" → Search RULES_INDEX.md for "linting" → Find `201-python-lint-format.md`
     - Result: Load both 200-python-core + 201-python-lint-format
   
   - **Document search results**: In "Rules Loaded" section, state which keywords were searched
   - **If RULES_INDEX.md not accessible**: Proceed with foundation + language rules, inform user

5. **Declare MODE and State Loaded Rules**: Declare current mode and list all loaded rules at the start of the response
   - Format: "MODE: [PLAN|ACT]\n\n## Rules Loaded\n- {rule_path}/000-global-core.md (foundation)\n- {rule_path}/200-python-core.md (Python file type: .py detected)\n- {rule_path}/201-python-lint-format.md (activity: linting keyword matched)\n\n[Then proceed with response...]"
   - **MODE must be first line** - Always declare MODE: PLAN (default) or MODE: ACT (after authorization)
   - **This listing is MANDATORY** - it confirms rules were loaded and helps users verify behavior
   - **Document your analysis**: State which file types detected and which keywords matched

6. **Then Proceed**: Continue with analysis, planning, or implementation following loaded rules

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
- **MODE declared**: Current mode (PLAN/ACT) stated at start of response
- **Foundation loaded**: 000-global-core.md read successfully
- **File types analyzed**: Identified all file extensions being edited
- **Language rules loaded**: Loaded core rules for each file type (.py → 200-python-core, etc.)
- **Activity keywords extracted**: Identified task type (linting, testing, deployment, etc.)
- **Specialized rules loaded**: Loaded activity-specific rules from RULES_INDEX.md
- **Dependencies resolved**: Prerequisites loaded before dependent rules (check "Depends On" column)
- **Token budget tracked**: Cumulative tokens within recommended limits (see token budget table)
- **Rules stated**: Loaded rules explicitly listed at start of response with analysis explanation

**If any check fails**: 
- STOP and inform user which requirement failed
- Provide specific file path or missing dependency
- Request user add missing files to context before proceeding

**Common Mistakes to Avoid:**
- ❌ Loading only 000-global-core for Python editing tasks
- ❌ Skipping language rules for "simple" tasks (linting, formatting, syntax fixes)
- ❌ Not analyzing file extensions before selecting rules
- ❌ Not searching RULES_INDEX.md Keywords column for activity matches
- ❌ Loading rules AFTER starting code edits instead of BEFORE

**Response Format Requirement:**
```
MODE: [PLAN|ACT]

## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/[domain]-core.md (e.g., 100-snowflake-core, 200-python-core)
- {rule_path}/[specialized].md (task-specific rules)

[Then proceed with response...]
```

**Example: Correct Approach **
```
User: Fix the Streamlit fragment batch processing
AI: MODE: PLAN

## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/100-snowflake-core.md (Snowflake SQL patterns)
- {rule_path}/101-snowflake-streamlit-core.md (Streamlit core patterns)
- {rule_path}/101b-snowflake-streamlit-performance.md (performance optimization)

Task Analysis:
Analyzing Streamlit fragment batch processing issue against loaded performance patterns...

Task List:
1. [Specific tasks based on analysis]
2. [Validation steps]

[Awaits "ACT" authorization before making changes]
```

**Example: Incorrect Approach ❌**
```
User: Fix the Streamlit fragment batch processing
AI: *immediately starts debugging code without loading rules*
```

**Example: Python Linting Task**
```
User: Fix linting issues in scripts/validate_agent_rules.py

AI: MODE: PLAN

## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/200-python-core.md (file type: .py detected)
- {rule_path}/201-python-lint-format.md (activity: "linting" keyword matched in RULES_INDEX.md)

File type analysis: Detected .py file → Python language rules required
Activity analysis: "linting issues" → Searched RULES_INDEX.md Keywords: "Ruff, linting, code quality" → Matched 201-python-lint-format.md

Task Analysis:
Based on 201-python-lint-format.md, will use Ruff to identify specific violations...
[Proceeds with analysis]
```

**Example: Streamlit Performance Task**
```
User: Optimize this Streamlit app's dashboard loading time

AI: MODE: PLAN

## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/100-snowflake-core.md (Snowflake dependency for Streamlit)
- {rule_path}/101-snowflake-streamlit-core.md (file type: Streamlit app detected)
- {rule_path}/101b-snowflake-streamlit-performance.md (activity: "optimize" keyword matched)
- {rule_path}/103-snowflake-performance-tuning.md (dependency from 101b)

File type analysis: Streamlit app (.py with st. imports) → Load 101-snowflake-streamlit-core.md
Activity analysis: "optimize performance" → Searched RULES_INDEX.md Keywords: "performance, caching, data loading" → Matched 101b-snowflake-streamlit-performance.md
Dependency analysis: 101b depends on 103-snowflake-performance-tuning.md → Load prerequisite

Task Analysis:
Based on 101b-snowflake-streamlit-performance.md, will analyze caching patterns, query optimization...
[Proceeds with analysis]
```

**Example: Testing Task Without pytest Rule ❌ Common Mistake**
```
User: Add unit tests for the data validation functions

AI: MODE: PLAN

## Rules Loaded
- {rule_path}/000-global-core.md (foundation)
- {rule_path}/200-python-core.md (Python file type)

❌ MISSING: 206-python-pytest.md - Task involves "tests" keyword but pytest rule not loaded!

CORRECT approach should be:
- Search RULES_INDEX.md for "testing", "pytest", "fixtures"
- Load 206-python-pytest.md for testing patterns
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

Use this navigation tree to quickly identify starting rules based on your task domain:

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

After identifying your starting rule, use RULES_INDEX.md to search for additional specialized rules. Search the Keywords column for technology terms (Snowflake, Python, Docker, FastAPI) and activity terms (testing, performance, security, deployment).

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

### Task Keyword Extraction Guide (CRITICAL FOR RULE LOADING)

Before loading rules, extract keywords from the user's task description to ensure you load ALL relevant rules:

**Technology Keywords** (trigger domain rules):
- Python, pytest, FastAPI, Flask, Typer, Pydantic, pandas → 200-python-core.md + specialized rules
- Snowflake, SQL, Streamlit, Cortex, SPCS → 100-snowflake-core.md + specialized rules
- Docker, containers, multi-stage builds → 400-docker-best-practices.md
- Bash, shell, zsh → 300-bash-scripting-core.md or 310-zsh-scripting-core.md

**Activity Keywords** (trigger specialized rules):
- **testing, test coverage, unit tests, integration tests, fixtures, mocking** → 206-python-pytest.md
- deployment, CI/CD, automation, workflow → 820-taskfile-automation.md, 806-git-workflow-management.md
- validation, linting, formatting, code quality → 201-python-lint-format.md
- documentation, docs, docstrings, README, CHANGELOG → 204-python-docs-comments.md, 800-project-changelog-rules.md
- security, authentication, authorization, XSS, SQL injection → *-security.md rules
- performance, optimization, caching, slow queries → *-performance*.md rules

**Process for Every Task:**
1. **Extract keywords**: Identify ALL technology and activity terms in user's request
2. **Search RULES_INDEX.md**: Look for matches in Keywords column
3. **Load matching rules**: In dependency order (check "Depends On" column)
4. **State loaded rules AND searched keywords**: In "Rules Loaded" section of response

**Example:**
```
User: "Create pytest fixtures for database testing"

Keywords extracted:
- Technology: pytest (Python testing framework)
- Activity: testing, fixtures, database

Rules to load:
1. 000-global-core.md (foundation - always load)
2. 200-python-core.md (Python domain rule)
3. 206-python-pytest.md (MATCH on "pytest, testing, fixtures" keywords)
4. Check RULES_INDEX for database-specific rules → no exact match, use general patterns

Rules Loaded section:
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (Python domain)
- rules/206-python-pytest.md (keywords: testing, fixtures - matched "pytest fixtures")
```

### Self-Check Protocol: Did I Load the Right Rules?

**Before responding, verify you completed ALL steps:**

**Foundation Check:**
- [ ] Loaded 000-global-core.md? (MANDATORY for all tasks)
- [ ] Confirmed file loaded successfully (not empty)?

**Domain Check:**
- [ ] Identified primary technology? (Python, Snowflake, Docker, Bash, etc.)
- [ ] Loaded domain core rule? (200-python-core, 100-snowflake-core, etc.)

**Specialized Check:**
- [ ] Extracted task keywords? (List them: e.g., "testing, pytest, fixtures")
- [ ] Searched RULES_INDEX.md Keywords column for matches?
- [ ] Found and loaded specialized rules matching keywords?
- [ ] **If testing task**: Loaded 206-python-pytest.md?
- [ ] **If deployment task**: Loaded relevant deployment/automation rules?
- [ ] **If documentation task**: Loaded relevant docs rules?

**Dependency Check:**
- [ ] Checked "Depends On" column for all loaded rules?
- [ ] Loaded prerequisites first (in dependency order)?

**Documentation Check:**
- [ ] Stated loaded rules in "Rules Loaded" section?
- [ ] Listed searched keywords?

**If ANY check failed:** STOP and search RULES_INDEX.md again before responding.

### Common Rule Loading Pitfalls (Learn from These!)

**Pitfall 1: Testing Tasks Without pytest Rule** ⚠️
- **Trigger words**: testing, test coverage, unit tests, integration tests, fixtures, parametrization
- **Required rule**: 206-python-pytest.md
- **Why critical**: Contains AAA pattern, fixture patterns, marker usage, parametrization, Pre-Task-Completion Test Execution Gate
- **Keywords to search**: "pytest", "testing", "test coverage", "fixtures"

**Pitfall 2: Python Tasks Without Linting Rule** ⚠️
- **Trigger words**: Python, code quality, formatting, style, lint errors
- **Required rules**: 200-python-core.md + 201-python-lint-format.md
- **Why critical**: Contains `uvx ruff` usage, validation gates, linting standards
- **Keywords to search**: "Python", "linting", "formatting", "ruff"

**Pitfall 3: Deployment Tasks Without Taskfile/Git Rules** ⚠️
- **Trigger words**: deploy, CI/CD, automation, workflow, release
- **Required rules**: 820-taskfile-automation.md, 806-git-workflow-management.md
- **Why critical**: Contains deployment patterns, git workflow management, task automation
- **Keywords to search**: "deployment", "CI/CD", "automation", "git workflow"

**Pitfall 4: Documentation Tasks Without Docs Rules** ⚠️
- **Trigger words**: documentation, docs, README, CHANGELOG, docstrings
- **Required rules**: 800-project-changelog-rules.md, 801-project-readme-rules.md, 204-python-docs-comments.md
- **Why critical**: Contains structured documentation standards, changelog format, docstring conventions
- **Keywords to search**: "documentation", "CHANGELOG", "README", "docstrings"

**Pitfall 5: Streamlit Tasks Without Streamlit Rules** ⚠️
- **Trigger words**: Streamlit, dashboard, st.cache, fragments, SiS
- **Required rules**: 101-snowflake-streamlit-core.md + specialized 101*-streamlit-*.md
- **Why critical**: Contains state management, caching, performance patterns
- **Keywords to search**: "Streamlit", "dashboard", "caching", "fragments"

---

# Part 2: Rule Discovery Reference

> **Audience**: AI Assistants  
> **Purpose**: Quick reference for rule discovery and loading strategies  
> **Status**: Use for rule selection and dependency resolution

---

## Rule Organization

Rules are organized by numeric domain prefixes:
- **000-099:** Core/Foundational (always start here)
- **100-199:** Snowflake ecosystem
- **200-299:** Python ecosystem
- **300-399:** Shell/Bash scripting
- **400-499:** Docker/Containers
- **500-599:** Data Science/Analytics
- **600-699:** Data Governance
- **700-799:** Business Analytics
- **800-899:** Project Management
- **900-999:** Demo/Examples

## Rule Discovery Methods

### Primary Method: Search RULES_INDEX.md

Use RULES_INDEX.md as the authoritative source for rule discovery:
1. **Search Keywords/Hints column** for terms matching your task
2. **Check Depends On column** for prerequisites
3. **Load in dependency order** (prerequisites first)

Example: For Streamlit performance task, search Keywords for "Streamlit, performance, caching" → find relevant 101b rule → check dependencies → load chain.

### Split Rules Pattern

Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization. This improves token efficiency by allowing focused loading. Search RULES_INDEX.md Keywords column and check "Related Rules" sections to discover related split rules.

## Essential Rule Metadata

When parsing rules, use these metadata fields:

- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical > High > Medium > Low)
- **Depends:** Prerequisites that must be loaded first

## Progressive Loading Strategy

Load rules incrementally to manage token budget:

1. **Foundation:** 000-global-core.md (always first, ~900 tokens)
2. **Domain:** Technology-specific core (e.g., 100-snowflake-core, 200-python-core)
3. **Specialized:** Task-specific rules based on Keywords match
4. **Monitor:** Track cumulative tokens, prioritize Critical/High tiers

Example loading sequence for Snowflake Streamlit dashboard:
```
000-global-core (~900 tokens)
└── 100-snowflake-core (~1,640 tokens)
    └── 101-snowflake-streamlit-core (~3,667 tokens)
        └── 101b-snowflake-streamlit-performance (~2,500 tokens, if optimizing)
Total: ~6,000-9,000 tokens depending on specialization needs
```

## Common Mistake Patterns

**Testing tasks without pytest rule:**
- Keywords: testing, pytest, fixtures, parametrization
- Required: 206-python-pytest.md
- Critical: Contains AAA pattern, fixture patterns, Pre-Task-Completion Test Execution Gate

**Python tasks without linting rule:**
- Keywords: Python, linting, formatting, code quality
- Required: 201-python-lint-format.md
- Critical: Contains uvx ruff usage, validation gates

**Deployment tasks without automation rules:**
- Keywords: deploy, CI/CD, automation, release
- Required: 820-taskfile-automation.md, 806-git-workflow-management.md

**Documentation tasks without docs rules:**
- Keywords: documentation, CHANGELOG, README, docstrings
- Required: 800-project-changelog-rules.md, 801-project-readme-rules.md, 204-python-docs-comments.md

**Streamlit tasks without Streamlit rules:**
- Keywords: Streamlit, dashboard, caching, fragments, st.cache
- Required: 101-snowflake-streamlit-core.md + specialized 101* rules

## Ecosystem Tooling Reference

| Ecosystem | Testing | Linting | Type Checking | Core Rule |
|-----------|---------|---------|---------------|-----------|
| Python | pytest | ruff check | mypy | 200-python-core |
| Shell | shellcheck | shellcheck | N/A | 300-bash-scripting-core |
| Docker | docker build | hadolint | N/A | 400-docker-best-practices |