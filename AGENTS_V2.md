# 🚨 CRITICAL: MANDATORY RULE LOADING FOR ALL RESPONSES

## ⚠️ AI AGENT SELF-CHECK: Execute Before EVERY Response ⚠️

**STOP AND VERIFY BEFORE RESPONDING:**

- [ ] **Foundation Loaded**: Did I load `rules/000-global-core.md`?
- [ ] **Index Accessed**: Did I access `rules/RULES_INDEX.md` for rule discovery?
- [ ] **Domain Rules Loaded**: Did I load appropriate domain-specific rules?
- [ ] **Rules Acknowledged**: Did I acknowledge which rules are guiding my response?

**❌ IF ANY CHECKBOX IS UNCHECKED: DO NOT RESPOND YET**
**✅ Load rules first using whatever file access method you have**

---

## MANDATORY RULE LOADING PROTOCOL (Universal)

**BEFORE ANY CODING RESPONSE, ALL AI AGENTS MUST:**

### Step 1: Load Foundation (CRITICAL)
- **Required File**: `rules/000-global-core.md`
- **Action**: Load this file using whatever method available to you:
  - File reading function/tool
  - Search your context if pre-loaded
  - Request from user if no access
- **Non-Negotiable**: This rule is ALWAYS required
- **Purpose**: Foundational principles (PLAN/ACT mode, surgical edits, safety)

### Step 2: Access Rule Discovery Index (CRITICAL)
- **Required File**: `rules/RULES_INDEX.md`
- **Location**: Inside the `rules/` directory (NOT root)
- **Purpose**: Semantic keyword lookup and dependency mapping
- **Action**: Load and parse this table to find relevant rules

### Step 3: Semantic Rule Discovery (REQUIRED)
Parse the user's request to identify:
- **Technology Stack**: Snowflake, Python, Docker, Shell, etc.
- **Task Type**: Build, optimize, debug, test, deploy, etc.
- **Features Needed**: Authentication, performance, security, visualization, etc.

Search `RULES_INDEX.md` Keywords column for matches:
- Exact technology names (e.g., "FastAPI", "Streamlit")
- Task patterns (e.g., "testing", "security", "performance")
- Feature requirements (e.g., "authentication", "caching", "monitoring")

### Step 4: Load Domain and Specialized Rules (REQUIRED)
**Priority Loading Order**:
1. **Always**: `rules/000-global-core.md` (foundation)
2. **Domain Core**: `rules/[N]00-[domain]-core.md` for primary technology
   - Python → `rules/200-python-core.md`
   - Snowflake → `rules/100-snowflake-core.md`
   - Shell → `rules/300-bash-scripting-core.md`
   - Docker → `rules/400-docker-best-practices.md`
3. **Specialized**: Task-specific rules from RULES_INDEX.md search
4. **Dependencies**: Load prerequisites based on "Depends On" column

### Step 5: Resolve Dependencies (REQUIRED)
For each rule identified in Step 3:
1. Check the **Depends On** column in `rules/RULES_INDEX.md`
2. Load all prerequisite rules BEFORE the dependent rule
3. Build complete dependency chain (e.g., 210 depends on 200, 200 depends on 000)

### Step 6: Acknowledge Loaded Rules (REQUIRED)
**At the start of your response**, acknowledge which rules are guiding you.

**Flexible Format Options**:
- **Option A**: Explicit list at response start
  ```
  Loaded rules: 000-global-core, 200-python-core, 210-python-fastapi-core
  ```
- **Option B**: Inline references as you apply them
  ```
  Following rule 200-python-core, I'll use uv for dependency management...
  ```
- **Option C**: Brief summary statement
  ```
  Applying Python and FastAPI best practices from the rule system...
  ```

**Key Requirement**: User must know which guidance informed your response.

---

## UNIVERSAL FILE ACCESS STRATEGIES

Different agents have different capabilities. Use the appropriate strategy:

### If You Have File System Access (Read Functions/Tools)
```
1. Load: rules/RULES_INDEX.md
2. Load: rules/000-global-core.md  
3. Search RULES_INDEX.md for relevant rules
4. Load: rules/[identified-rules].md
5. Apply rules to your response
```

### If Files Are Pre-loaded in Your Context
```
1. Search context for "RULES_INDEX.md"
2. Parse the table for relevant rules
3. Search context for identified rule names
4. Apply rules you find in your context
```

### If You Have Limited/No File Access
```
1. Inform user: "I need access to the rules/ directory"
2. Request specific rules based on task analysis:
   - "Please include rules/200-python-core.md for Python work"
   - "Please include rules/100-snowflake-core.md for Snowflake tasks"
3. Work with whatever rules are provided
4. Note any missing rules that would improve guidance
```

---

## COMPLIANCE SCOPE

**This protocol applies to EVERY coding-related response, including:**
- Initial task analysis and planning
- Creating implementation plans
- Code modifications and debugging  
- Architecture discussions
- Documentation updates
- Performance optimization
- Security reviews
- Testing strategies
- ANY technical implementation task

**This protocol does NOT apply to:**
- Purely conversational or clarifying questions
- Non-technical discussions
- Requests for general information

---

## CONSEQUENCES OF NON-COMPLIANCE

**Strict Enforcement:**

1. **Response is Invalid**: Does not meet project quality standards
2. **User Should Reject**: Point out the violation and request proper rule loading
3. **Pattern Recognition**: Repeated violations indicate agent is not suitable for this workflow

**Zero-Tolerance Items:**
- Missing `rules/000-global-core.md` from guidance
- No acknowledgment of which rules are being applied
- Ignoring available rule system when context is provided
- Making up guidance instead of loading actual rules

**For AI Agents - Self-Assessment**:
- After responding, verify you acknowledged rule sources
- If missing, immediately provide correction
- Do not wait for user to point out the violation

---

## EXAMPLE WORKFLOWS (Agent Learning)

### Example 1: User Request "Build a Python FastAPI application"

**Agent Process**:
```
1. Load rules/000-global-core.md (foundation)
2. Load rules/RULES_INDEX.md (discovery)
3. Parse request: Technology="Python,FastAPI", Task="build", Type="API"
4. Search RULES_INDEX.md Keywords for "Python" → finds 200-python-core
5. Search RULES_INDEX.md Keywords for "FastAPI" → finds 210-python-fastapi-core
6. Check dependencies: 210 depends on 200, 200 depends on 000
7. Load rules/200-python-core.md
8. Load rules/210-python-fastapi-core.md
```

**Agent Response**:
```
Applying rules 000 (foundation), 200 (Python core), and 210 (FastAPI) 
to guide this implementation.

Based on rule 200-python-core, I'll use uv for dependency management.
Following rule 210-python-fastapi-core, here's the recommended structure...

[Implementation follows]
```

### Example 2: User Request "Optimize my Snowflake query performance"

**Agent Process**:
```
1. Load rules/000-global-core.md
2. Load rules/RULES_INDEX.md
3. Parse request: Technology="Snowflake", Task="optimize", Focus="performance"
4. Search Keywords for "Snowflake" → finds 100-snowflake-core
5. Search Keywords for "performance" → finds 103-snowflake-performance-tuning
6. Check dependencies: 103 depends on 100, 100 depends on 000
7. Load rules/100-snowflake-core.md
8. Load rules/103-snowflake-performance-tuning.md
```

**Agent Response**:
```
Using Snowflake optimization guidance from rules 100 and 103.

Following rule 103-snowflake-performance-tuning, I'll analyze:
1. Query profile for bottlenecks
2. Clustering key effectiveness
3. Warehouse sizing appropriateness
...
```

### Example 3: User Request "Create a Streamlit dashboard with charts"

**Agent Process**:
```
1. Load rules/000-global-core.md
2. Load rules/RULES_INDEX.md  
3. Parse: Technology="Snowflake,Streamlit", Task="create", Feature="dashboard,charts"
4. Search for "Streamlit" → finds 101-snowflake-streamlit-core
5. Search for "visualization,charts" → finds 101a-snowflake-streamlit-visualization
6. Check dependencies: 101a depends on 101, 101 depends on 100, 100 depends on 000
7. Load complete chain: 000 → 100 → 101 → 101a
```

**Agent Response**:
```
Loaded Streamlit best practices (rules 100, 101, 101a) for dashboard development.

Per rule 101-snowflake-streamlit-core, I'll use st.connection for Snowflake access.
Per rule 101a, I'll use Plotly for interactive visualizations.
...
```

---

## FILE STRUCTURE REFERENCE (Agent Critical Information)

### All Rules Are in the `rules/` Directory

**Critical Files to Load First**:
```
rules/RULES_INDEX.md          ← Lookup table (load second)
rules/000-global-core.md      ← Foundation (load first)
```

**Domain Core Rules** (load based on technology):
```
rules/100-snowflake-core.md        ← Snowflake foundation
rules/200-python-core.md           ← Python foundation  
rules/300-bash-scripting-core.md   ← Shell foundation
rules/400-docker-best-practices.md ← Docker foundation
```

**Specialized Rules** (70+ rules in rules/ directory):
```
rules/101-snowflake-streamlit-core.md
rules/210-python-fastapi-core.md
rules/206-python-pytest.md
... (see RULES_INDEX.md for complete catalog)
```

### Path Reference Rules
- **From project root**: `rules/[filename]`
- **RULES_INDEX.md location**: `rules/RULES_INDEX.md` (NOT in root directory)
- **All rule files**: Inside `rules/` directory
- **Never assume**: Rules are in root or other locations

---

## SEMANTIC DISCOVERY GUIDE (Agent Instructions)

### How to Use RULES_INDEX.md for Discovery

The `rules/RULES_INDEX.md` file contains a table with these columns:
- **File**: Rule filename
- **Type**: Auto-attach or Agent Requested
- **Purpose**: One-line description
- **Scope**: Applicability context
- **Keywords/Hints**: Comma-separated search terms
- **Depends On**: Prerequisite rules

### Discovery Process

**Step 1: Parse User Request**
Extract key terms:
- Technologies: Snowflake, Python, FastAPI, Docker, Streamlit, etc.
- Actions: build, optimize, test, deploy, debug, secure, etc.
- Features: authentication, caching, performance, monitoring, etc.

**Step 2: Search Keywords Column**
Look for matches in the Keywords/Hints column:
- **Exact matches**: "FastAPI" → rule 210
- **Pattern matches**: "testing" → rules 206, 101d, etc.
- **Domain matches**: "Snowflake" → rules 100-124 range

**Step 3: Build Dependency Chain**
For each matched rule:
1. Check "Depends On" column
2. Add prerequisites to loading list
3. Ensure 000-global-core is always included
4. Load in dependency order (prerequisites first)

**Step 4: Consider ContextTier**
Each rule has metadata indicating priority:
- **Critical**: Must load for basic functionality (~1000-1500 tokens)
- **High**: Important for common tasks (~1000 tokens additional)
- **Medium**: Useful for specific scenarios (~500-1000 tokens)
- **Low**: Optional enhancements (load only if specifically needed)

Start with Critical tier, add High tier as needed.

### Pattern Recognition Examples

| User Request | Technologies | Actions | Relevant Rules |
|-------------|--------------|---------|---------------|
| "Build a Python CLI tool" | Python, CLI | build | 000, 200, 220 |
| "Add auth to FastAPI" | Python, FastAPI, security | implement | 000, 200, 210, 210a |
| "Fix slow Snowflake query" | Snowflake | optimize | 000, 100, 103 |
| "Create Streamlit dashboard" | Snowflake, Streamlit, UI | create | 000, 100, 101, 101a |
| "Write unit tests" | Python | test | 000, 200, 206 |
| "Dockerize application" | Docker | deploy | 000, 400 |

---

## TOKEN BUDGET MANAGEMENT (Agent Optimization)

### Context Window Guidelines

**Minimal Context** (~500-1000 tokens):
- 000-global-core + one domain core
- Use for: Quick fixes, simple tasks

**Standard Context** (~1500-2500 tokens):
- Foundation + domain core + 2-3 specialized rules
- Use for: Most development tasks

**Full Context** (~3000-5000 tokens):
- Complete dependency chain for complex workflows
- Use for: Major implementations, architectural decisions

### Dynamic Management Strategy

1. **Start Minimal**: Load only Critical tier rules
2. **Add as Needed**: Include High tier for common features
3. **Monitor Usage**: Track cumulative token consumption
4. **Drop if Needed**: Remove Medium/Low tier if approaching limits
5. **Focus**: Prioritize task-specific rules over general ones

### Token Budget Metadata

Each rule includes **TokenBudget** in its metadata:
```
**TokenBudget:** ~400
```

Track total as you load:
- 000-global-core: ~300 tokens
- Domain core (100/200/300/400): ~400-500 tokens
- Specialized rules: ~300-800 tokens each
- Target total: Keep under 3500 tokens for optimal performance

---

## ADAPTIVE STRATEGIES BY AGENT CAPABILITY

### For Agents with Full File System Access

**Optimal Workflow**:
1. Read `rules/RULES_INDEX.md` for discovery
2. Read `rules/000-global-core.md` for foundation
3. Parse user request for semantic matching
4. Read identified rules from `rules/` directory
5. Build dependency chain and load prerequisites
6. Apply rules consistently in response
7. Acknowledge which rules guided your work

### For Agents with Pre-loaded Context

**Adapted Workflow**:
1. Search context for "RULES_INDEX.md" content
2. Search context for "000-global-core.md" content
3. Parse table to identify relevant rules
4. Search context for identified rule names
5. Apply whatever rules are available in context
6. Note if key rules are missing from context

### For Agents with Limited/No File Access

**Fallback Workflow**:
1. Inform user: "I need access to the rules/ directory for this project"
2. Analyze task and recommend specific rules:
   - "I recommend including rules/200-python-core.md for Python work"
   - "I recommend including rules/210-python-fastapi-core.md for FastAPI"
3. Explain why each rule is relevant
4. Work with whatever rules user provides
5. Apply general best practices if no rules available
6. Document deviations from project standards

---

## RULE CATEGORIES (Quick Reference)

### By Number Range

- **000-099**: Core/Foundational (start here - always load 000)
- **100-199**: Snowflake ecosystem (SQL, Streamlit, Cortex, etc.)
- **200-299**: Python ecosystem (FastAPI, testing, utilities)
- **300-399**: Shell/Bash scripting
- **400-499**: Docker/Containers
- **500-599**: Data Science/Analytics
- **600-699**: Data Governance
- **700-799**: Business Analytics
- **800-899**: Project Management
- **900-999**: Demo/Examples

### Common Dependency Patterns

**Snowflake Streamlit Dashboard**:
```
000-global-core (always first)
└── 100-snowflake-core (SQL foundations)
    └── 101-snowflake-streamlit-core (app basics)
        ├── 101a-snowflake-streamlit-visualization (charts)
        ├── 101b-snowflake-streamlit-performance (optimization)
        └── 101c-snowflake-streamlit-security (auth/security)
```

**Python FastAPI Application**:
```
000-global-core (always first)
└── 200-python-core (Python foundations)
    └── 210-python-fastapi-core (API basics)
        ├── 210a-python-fastapi-security (auth)
        ├── 210b-python-fastapi-testing (tests)
        └── 210c-python-fastapi-deployment (production)
```

**Python CLI Tool**:
```
000-global-core (always first)
└── 200-python-core (Python foundations)
    └── 220-python-typer-cli (CLI framework)
```

---

## FOR HUMAN USERS: Enforcing Agent Compliance

### How to Verify Your Agent is Following Protocol

**✅ Valid Response Checklist**:
- [ ] Agent acknowledged which rules were loaded
- [ ] Response follows patterns from loaded rules
- [ ] At minimum, foundation rule (000-global-core) is mentioned
- [ ] Agent loaded domain-specific rules for your technology
- [ ] Technical decisions align with rule guidance

**❌ Invalid Response Indicators**:
- Agent responds without mentioning any rules
- Agent says "following best practices" without specifying which
- Response contradicts known rule guidance
- Agent makes up guidance not in the rule system

### What to Do When Protocol is Violated

**Copy-Paste Correction Template**:
```
STOP. You violated the AGENTS_V2.md rule loading protocol.

Required actions:
1. Load rules/000-global-core.md (foundation)
2. Load rules/RULES_INDEX.md (discovery)  
3. Load domain-specific rules for this task
4. Acknowledge which rules are guiding your response
5. Respond again following the loaded rules

Please reload rules and respond properly.
```

### Why This Protocol Matters

**Consistency**: Rules ensure consistent coding standards across all responses

**Traceability**: You can verify which rules informed each decision

**Quality**: Rules contain battle-tested patterns and project-specific standards

**Accountability**: Agent must explicitly acknowledge guidance sources

**Debugging**: When issues arise, check if correct rules were loaded

---

## PLATFORM INTEGRATION EXAMPLES

### Cursor IDE
```
1. Add AGENTS_V2.md to context: @AGENTS_V2.md
2. Add EXAMPLE_PROMPT.md if available: @EXAMPLE_PROMPT.md
3. Reference rules directory: @rules/
4. Ask your question: "Build a FastAPI application"

Agent will automatically discover and load relevant rules.
```

### VS Code with GitHub Copilot
```
Option A: Add to .github/copilot-instructions.md
- Include content from AGENTS_V2.md
- Reference rules/ directory in workspace

Option B: Use workspace instructions
- Add AGENTS_V2.md to workspace docs
- Copilot will use it for context
```

### Claude/ChatGPT Web Interface
```
1. Upload or paste AGENTS_V2.md content
2. Upload or paste rules/RULES_INDEX.md content
3. Upload specific rule files or paste content
4. Ask: "Following AGENTS_V2.md protocol, help me build..."

Agent will work with provided rules.
```

### CLI Tools (aider, mentat, cursor-cli, etc.)
```
Add to tool's configuration file:

context_files:
  - AGENTS_V2.md
  - rules/RULES_INDEX.md
  - rules/000-global-core.md
  
read_dirs:
  - rules/

Agent will have access to rule system.
```

### Gemini via API
```
Include in system prompt:
- AGENTS_V2.md instructions
- File access to rules/ directory
- Request rule loading before responses

Agent will follow protocol programmatically.
```

---

## UNDERSTANDING RULE METADATA

### Universal Fields (All Rules Have These)

**Keywords**: Comma-separated terms for semantic discovery
```
**Keywords:** Python, FastAPI, API, REST, web framework
```

**Depends**: Prerequisites that must be loaded first  
```
**Depends:** 000-global-core, 200-python-core
```

**TokenBudget**: Approximate tokens needed
```
**TokenBudget:** ~450
```

**ContextTier**: Priority level for loading
```
**ContextTier:** High
```
- Critical: Must load for basic functionality
- High: Important for common tasks
- Medium: Useful for specific scenarios
- Low: Optional enhancements

### How to Use Metadata

1. **Keywords**: Search RULES_INDEX.md Keywords column for task matches
2. **Depends**: Load prerequisites before dependent rules
3. **TokenBudget**: Track cumulative tokens to manage context
4. **ContextTier**: Prioritize Critical/High, defer Medium/Low

---

## MIGRATION FROM AGENTS.md (Original)

### Breaking Changes

1. **File paths**: Now explicitly `rules/RULES_INDEX.md` (not root)
2. **Examples**: No more XML-style syntax, universal language only
3. **Tool references**: No more "Read tool" assumptions
4. **Response format**: More flexible acknowledgment options
5. **Enforcement**: Streamlined user correction templates

### What Stayed the Same

1. **Core requirement**: Always load 000-global-core.md first
2. **Semantic discovery**: Still use RULES_INDEX.md for finding rules
3. **Dependency resolution**: Still load prerequisites before dependents
4. **Strict compliance**: Still zero-tolerance for skipping rule loading
5. **Rule structure**: Rules themselves unchanged

### Why This Version is Better

1. **Universal compatibility**: Works with any agent platform
2. **Clearer paths**: Explicit file locations prevent confusion
3. **Adaptive strategies**: Supports agents with different capabilities
4. **Better examples**: Real-world patterns instead of abstract syntax
5. **Agent-focused**: Instructions written for AI agents, not humans

### Transition Guidance

**For Users**: Replace references to AGENTS.md with AGENTS_V2.md in your contexts

**For Agents**: Follow new protocol, adapt to your file access capabilities

**For Tools**: Update configuration to point to AGENTS_V2.md

---

## QUICK REFERENCE CARD (Agent Cheat Sheet)

### Critical Path (Minimum Required)

```
1. Load rules/000-global-core.md (always)
2. Load rules/RULES_INDEX.md (discovery)
3. Parse user request for keywords
4. Search RULES_INDEX.md for matches
5. Load domain core + specialized rules
6. Resolve dependencies
7. Acknowledge rules in response
8. Apply rules consistently
```

### Common Task → Rule Mapping

| Task | Rules to Load |
|------|---------------|
| Python API | 000, 200, 210 |
| Python CLI | 000, 200, 220 |
| Python tests | 000, 200, 206 |
| Snowflake SQL | 000, 100 |
| Streamlit dashboard | 000, 100, 101, 101a |
| Docker container | 000, 400 |
| Shell script | 000, 300 |
| FastAPI + auth | 000, 200, 210, 210a |
| Performance tuning | 000, 100/200, 103 |

### File Location Quick Reference

```
Project Root/
├── AGENTS_V2.md (this file)
├── EXAMPLE_PROMPT.md (optional baseline)
└── rules/
    ├── RULES_INDEX.md ← LOOKUP TABLE
    ├── 000-global-core.md ← ALWAYS LOAD FIRST
    ├── 100-snowflake-core.md
    ├── 200-python-core.md
    └── ... (70+ specialized rules)
```

### Self-Check Before Responding

- [ ] Did I load 000-global-core.md?
- [ ] Did I search RULES_INDEX.md?
- [ ] Did I load domain-specific rules?
- [ ] Did I resolve dependencies?
- [ ] Will I acknowledge rules in my response?

If all yes → Proceed with response
If any no → Load missing rules first

---

## SUMMARY: Core Contract

### User Provides
1. AGENTS_V2.md in agent context
2. Access to rules/ directory (or specific rules)
3. EXAMPLE_PROMPT.md (optional but recommended)

### Agent Commits To
1. Always load rules/000-global-core.md first
2. Use rules/RULES_INDEX.md for semantic discovery
3. Load relevant domain and specialized rules
4. Resolve and load all dependencies
5. Acknowledge which rules are being applied
6. Follow rule guidance consistently

### Result
- Consistent, high-quality technical responses
- Traceable decision-making process
- Standards-aligned implementations
- Predictable, reliable agent behavior

---

*This is AGENTS_V2.md - A universal instruction file for autonomous rule discovery and application across all AI agent platforms.*

