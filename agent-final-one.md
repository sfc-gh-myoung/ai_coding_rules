# Final Agent Implementation Plan - Comprehensive Analysis and Roadmap

## Document Scoring (100-Point Scale)

### agent-improvements-one.md: **85/100**

**Strengths:**
- ✅ Comprehensive 8-issue analysis directly tied to the 7-step workflow
- ✅ Concrete code examples for every recommendation
- ✅ Addresses critical "continuous evaluation" requirement (Step 7)
- ✅ Detailed keyword extraction training for agents
- ✅ Clear implementation checklist
- ✅ Strong focus on fixing tool-specific syntax issues

**Weaknesses:**
- ❌ Doesn't address redundancy between AGENTS.md and EXAMPLE_PROMPT.md
- ❌ No mention of parallelization for performance
- ❌ Missing governance-as-domain concept
- ❌ Doesn't propose new rules (e.g., code citation)

**Key Contributions:**
1. Continuous Rule Evaluation section (Critical for Step 7)
2. Keyword Extraction training (Essential for agent autonomy)
3. Rule Loading Limits and Prioritization (Prevents token bloat)
4. Bootstrap sequence clarity (Fixes logical contradiction)

---

### agent-improvements-two.md: **78/100**

**Strengths:**
- ✅ Introduces parallelization concept (performance optimization)
- ✅ Governance-as-domain for meta-requests (clever solution)
- ✅ Missing-file fallback strategy (robustness)
- ✅ Proposes new rule: 005-code-citation-format.md
- ✅ Absolute paths preference (workspace alignment)
- ✅ Specific RULES_INDEX.md bug fix (Docker dependency)

**Weaknesses:**
- ❌ Less comprehensive than improvements-one
- ❌ Minimal code examples
- ❌ Doesn't address continuous evaluation explicitly
- ❌ Missing detailed keyword extraction guidance
- ❌ Shorter, less detailed recommendations

**Key Contributions:**
1. Parallelization for efficiency
2. Code citation standardization (005-code-citation-format.md)
3. Governance-as-domain pattern
4. Missing-file fallback handling

---

### agent-improvements-three.md: **68/100**

**Strengths:**
- ✅ Identifies AGENTS.md + EXAMPLE_PROMPT.md redundancy (important architectural issue)
- ✅ Proposes clean merge strategy
- ✅ Clarifies system prompt vs file loading
- ✅ PLAN/ACT override for expert users (flexibility)

**Weaknesses:**
- ❌ Only 3 recommendations (too high-level)
- ❌ Doesn't address continuous evaluation (Step 7)
- ❌ No keyword extraction guidance
- ❌ Missing concrete implementation details
- ❌ No code examples
- ❌ Proposes deleting EXAMPLE_PROMPT.md (risky - loses baseline prompt value)

**Key Contributions:**
1. Identifies file redundancy issue
2. PLAN/ACT override mechanism
3. System prompt architecture clarification

---

## Final Scoring Summary

| Document | Score | Ranking | Best For |
|----------|-------|---------|----------|
| agent-improvements-one.md | 85/100 | 🥇 1st | Comprehensive fixes, Step 7 support, agent training |
| agent-improvements-two.md | 78/100 | 🥈 2nd | Performance optimization, code citation, robustness |
| agent-improvements-three.md | 68/100 | 🥉 3rd | Architectural clarity, file structure |

---

## Selected Sections for Final Implementation

### From agent-improvements-one.md (Primary Source - 85%)

**✅ INCLUDE - Critical Sections:**
1. **Issue 2: Continuous Rule Evaluation** → AGENTS.md
   - Essential for Step 7 of workflow
   - Provides re-evaluation triggers
   - Mid-session acknowledgment pattern

2. **Issue 3: 000-global-core.md "ALWAYS LOAD FIRST"** → rules/000-global-core.md
   - Makes foundation rule unmistakably special
   - Adds LoadPriority metadata
   - Clear visual emphasis

3. **Issue 4: Universal syntax for EXAMPLE_PROMPT.md** → EXAMPLE_PROMPT.md
   - Removes tool-specific `Read(file_path=...)`
   - Aligns with AGENTS_V2.md universal approach

4. **Issue 5: RULES_INDEX.md emphasis on 000** → rules/RULES_INDEX.md
   - Visual distinction in table
   - Prominent header section

5. **Issue 6: Keyword Extraction Training** → AGENTS.md
   - Teaches agents HOW to extract keywords
   - 5-step process with examples
   - Technology + Action + Feature mapping

6. **Issue 7: Rule Loading Limits** → AGENTS.md
   - Clear token budgets (2000-3500 initial, 5000 max)
   - Priority matrix (Critical → Enhancement)
   - When to STOP loading rules

7. **Issue 8: Bootstrap sequence clarity** → EXAMPLE_PROMPT.md
   - Separates bootstrap (3 files) from task-specific loading
   - Fixes logical contradiction

**❌ SKIP - Covered Elsewhere:**
- Issue 1: AGENTS.md vs AGENTS_V2.md → Use improvements-three approach

---

### From agent-improvements-two.md (Secondary Source - 30%)

**✅ INCLUDE - High-Value Additions:**
1. **Parallelization guidance** → AGENTS.md, rules/000-global-core.md
   - "Maximize parallel tool calls for independent operations"
   - Reduces latency, improves efficiency
   - Cross-reference to existing workspace policy

2. **Governance-as-domain pattern** → AGENTS.md
   - When user asks about rules/process, load 002-rule-governance.md
   - Satisfies "domain rule" requirement for meta-requests

3. **Missing-file fallback** → AGENTS.md
   - State failure clearly
   - Proceed with available context
   - Request missing file from user

4. **New rule: 005-code-citation-format.md** → Create new file
   - Standardizes CODE REFERENCES vs MARKDOWN CODE BLOCKS
   - Already exists in workspace policy, needs extraction to rule
   - Add to RULES_INDEX.md

5. **Absolute paths preference** → AGENTS.md, rules/000-global-core.md
   - Align with workspace policy
   - Prevent path ambiguity

6. **RULES_INDEX.md bug fix** → rules/RULES_INDEX.md
   - Fix Docker dependency reference
   - 202-yaml-config-best-practices → 202-markup-config-validation

7. **Response header budget enforcement** → AGENTS.md
   - Reiterate 50-150 token limit
   - "Filename + brief context only"

**❌ SKIP - Not Needed:**
- ContextTier column in RULES_INDEX.md → Already in rule metadata
- Status updates before tool calls → Too verbose

---

### From agent-improvements-three.md (Architectural Source - 15%)

**✅ INCLUDE - Strategic Decisions:**
1. **Merge strategy (modified)** → Architecture decision
   - DON'T delete EXAMPLE_PROMPT.md (it's a valuable baseline)
   - DO consolidate AGENTS_V2.md as primary AGENTS.md
   - Keep EXAMPLE_PROMPT.md as optional quick-start

2. **System prompt vs file loading clarity** → AGENTS.md
   - Clarify AGENTS.md can be system prompt OR loaded file
   - Flexible for different agent platforms

3. **PLAN/ACT override mechanism (optional)** → rules/000-global-core.md
   - Add `--auto-act` or `--proceed-without-asking` flag
   - Safe default, expert override available
   - Document in Contract section

**❌ SKIP - Conflicts or Low Priority:**
- Deleting EXAMPLE_PROMPT.md → Keep as baseline prompt
- YAML/JSON version of RULES_INDEX.md → Future enhancement

---

## Final Implementation Plan

### Phase 1: Critical Foundation (Must Have)

#### 1.1: Replace AGENTS.md with AGENTS_V2.md
**Rationale:** AGENTS_V2.md already has universal syntax, better structure
**Actions:**
- Backup current AGENTS.md → AGENTS_LEGACY.md
- Rename AGENTS_V2.md → AGENTS.md
- Update all documentation references

**Files Modified:** 1
**Estimated Time:** 10 minutes

---

#### 1.2: Add Continuous Rule Evaluation to AGENTS.md
**Rationale:** Critical for Step 7 of workflow (session-long evaluation)
**Source:** agent-improvements-one.md, Issue 2

**Add new section after "COMPLIANCE SCOPE":**
```markdown
## CONTINUOUS RULE EVALUATION (Session-Long Requirement)

### Throughout the Conversation
After the initial rule loading, CONTINUOUSLY monitor each user message for:
- New technologies mentioned
- Task scope expansion into new domains
- Performance/security/testing concerns emerging
- Features not covered by currently loaded rules

### Re-evaluation Triggers

Load additional rules when:

1. **User introduces new technology**: "Now let's add Redis caching"
   - Action: Search RULES_INDEX.md for "Redis", "caching", "performance"
   - Load: Relevant caching/performance rules immediately
   - Acknowledge: "Loading performance rules for Redis caching guidance"

2. **Task scope changes**: "Also add authentication"
   - Action: Search for "authentication", "security", technology-specific
   - Load: Security-related rules (e.g., 210a-python-fastapi-security)
   - Acknowledge: "Loading security rules for authentication implementation"

3. **Quality concerns emerge**: "This seems slow" / "How do I test this?"
   - Action: Search for "performance", "optimization", "testing"
   - Load: Performance tuning or testing rules
   - Acknowledge: "Loading testing best practices"

4. **User explicitly requests**: "Follow testing best practices"
   - Action: Direct keyword match in RULES_INDEX.md
   - Load: Testing rules for current technology stack
   - Acknowledge: What you loaded and why

### Mid-Session Acknowledgment Pattern

When loading additional rules mid-session:
- **Brief**: "Loading rule 210a (FastAPI security)"
- **Why**: "Adds authentication best practices to our implementation"
- **Apply**: Use newly loaded rules immediately in your response

### Delta Reporting
To conserve tokens, report only NEW rules loaded, not all rules:
- ✅ "Also loaded: 210a-fastapi-security, 230-pydantic"
- ❌ "Loaded: 000, 200, 210, 210a, 230" (repeating already-loaded rules)
```

**Files Modified:** AGENTS.md
**Estimated Time:** 15 minutes

---

#### 1.3: Update rules/000-global-core.md - "ALWAYS LOAD FIRST"
**Rationale:** Makes foundation rule unmistakably special
**Source:** agent-improvements-one.md, Issue 3

**Replace first 5 lines with:**
```markdown
**Keywords:** PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, prompt engineering, foundational, always load first, foundation
**Depends:** None
**LoadPriority:** CRITICAL - ALWAYS load this rule FIRST before any other rules
**TokenBudget:** ~300
**ContextTier:** Critical

# Global Core Guidelines

## 🚨 CRITICAL: This Rule Must ALWAYS Be Loaded First

**Non-Negotiable Requirement**: 
- Load this rule at the START of EVERY session
- Load BEFORE any other domain or specialized rules
- If you can only load ONE rule, load this one
- All other rules depend on these foundational principles

**Why This Matters**:
- Establishes PLAN/ACT safety workflow
- Defines surgical editing principles
- Sets professional communication standards  
- Provides the operating contract for all agent behavior
- Required for consistent, safe, reliable responses
```

**Files Modified:** rules/000-global-core.md
**Estimated Time:** 5 minutes

---

#### 1.4: Update rules/RULES_INDEX.md - Emphasize 000-global-core
**Rationale:** Visual distinction makes it unmissable
**Source:** agent-improvements-one.md, Issue 5

**Replace header (lines 1-14) with:**
```markdown
**Keywords:** rules index, rule discovery, semantic search, agent requested, auto-attach, rule governance, context engineering, tool design

# Rules Index

This index helps agents select the correct rule quickly through semantic keyword matching.

## 🚨 CRITICAL: 000-global-core.md is MANDATORY

**ALWAYS load `rules/000-global-core.md` FIRST:**
- Load at session start, BEFORE analyzing user request
- This is the foundation for all other rules
- All other rules depend on these principles
- Non-negotiable requirement for every session
- If you can only load ONE rule, load this one

After loading 000-global-core.md, use this index to discover additional rules based on:
- User's technology stack (keywords)
- Task requirements (actions + features)
- Dependency chains (Depends On column)

## How to Use This Index

1. **Always start**: Load 000-global-core.md first
2. **Parse user request**: Extract technology, action, feature keywords
3. **Search Keywords column**: Find matching rules (case-insensitive, partial matches OK)
4. **Check dependencies**: Look at "Depends On" column, load prerequisites first
5. **Load incrementally**: Start with Critical tier, add High tier as needed
6. **Re-evaluate continuously**: After each user message, check if new rules needed

## Continuous Evaluation

Throughout the session, monitor for:
- New technologies mentioned → search and load relevant rules
- Scope expansion (testing, security, performance) → load specialized rules
- User explicit requests ("follow best practices for X") → load X rules

---

## Rule Catalog

| File | Type | Purpose (one line) | Scope | Keywords/Hints | Depends On |
|------|------|---------------------|-------|----------------|------------|
| `000-global-core.md` | **🚨 MANDATORY - LOAD FIRST** | Global operating contract (PLAN/ACT, safety, validation) | Universal | PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, foundational, always load first | — |
```

**Also fix Docker dependency bug (line ~50):**
```markdown
| `400-docker-best-practices.md` | Agent Requested | Docker container best practices | Docker | Docker, containers, Dockerfile, docker-compose, image optimization, layer caching | `000-global-core.md`, `202-markup-config-validation.md` |
```
Change `202-yaml-config-best-practices.md` → `202-markup-config-validation.md`

**Files Modified:** rules/RULES_INDEX.md
**Estimated Time:** 10 minutes

---

#### 1.5: Update EXAMPLE_PROMPT.md - Universal Syntax
**Rationale:** Remove tool-specific syntax, align with AGENTS.md
**Source:** agent-improvements-one.md, Issue 4 + Issue 8

**Replace Step 1 (lines 19-40) with:**
```markdown
### Step 1: Bootstrap Loading (BEFORE User Request Analysis)

At the START of a new session, load these THREE files in order:

1. **Load AGENTS.md**
   - Purpose: Understand rule discovery system and loading protocol
   - How: Use whatever file access method you have (read tool, pre-loaded context, etc.)
   - Verification: Confirm you understand the protocol before proceeding
   - Note: This file may be your system prompt; if so, you already have it

2. **Load rules/RULES_INDEX.md**
   - Purpose: Enable semantic search for specialized rules
   - How: Access this file in the rules/ directory
   - Verification: Confirm you can search the Keywords column
   - Required: Must have this catalog for rule discovery

3. **Load rules/000-global-core.md** 🚨 CRITICAL - ALWAYS REQUIRED
   - Purpose: Load foundational principles (PLAN/ACT workflow, surgical edits, safety)
   - How: This is in the rules/ directory
   - Verification: Foundation loaded before any domain rules
   - **NON-NEGOTIABLE**: This is ALWAYS required, no exceptions
   - **Priority**: If you can only load ONE rule, load this one

**Important**: These three files are loaded BEFORE parsing the user's request.
They provide the framework for understanding HOW to discover additional rules.

**Self-Check After Step 1:**
- [ ] Do I have AGENTS.md protocol guidance?
- [ ] Can I search rules/RULES_INDEX.md Keywords column?
- [ ] Is rules/000-global-core.md loaded and active?
- [ ] If NO to any: Load missing files before Step 2
```

**Replace Step 2 (lines 41-47) with:**
```markdown
### Step 2: Parse User Request (AFTER Bootstrap)

NOW that you have the framework loaded:
1. Read the user's request carefully
2. Extract keywords:
   - **Technologies**: Python, FastAPI, Snowflake, Streamlit, Docker, etc.
   - **Actions**: build, optimize, debug, test, deploy, secure, etc.
   - **Features**: authentication, caching, visualization, monitoring, etc.
3. Search rules/RULES_INDEX.md Keywords column for matches
4. Identify 3-5 most relevant rules for this specific request
```

**Files Modified:** EXAMPLE_PROMPT.md
**Estimated Time:** 10 minutes

---

### Phase 2: Agent Training and Optimization (Should Have)

#### 2.1: Add Keyword Extraction Training to AGENTS.md
**Rationale:** Teaches agents HOW to extract keywords systematically
**Source:** agent-improvements-one.md, Issue 6

**Add new section after "SEMANTIC DISCOVERY GUIDE":**
```markdown
## KEYWORD EXTRACTION TRAINING (Agent Instructions)

### How to Parse User Requests for Keywords

Systematic 5-step process for extracting relevant keywords from user prompts:

#### Step 1: Identify Technology Terms
Extract explicit technologies mentioned:
- "Python" → search RULES_INDEX.md for "Python"
- "FastAPI" → search for "FastAPI"
- "Snowflake" → search for "Snowflake"
- "Streamlit" → search for "Streamlit"
- "Docker" → search for "Docker"
- "PostgreSQL", "Redis", "React", etc.

#### Step 2: Identify Action Verbs
Map action verbs to rule categories:
- "build", "create", "implement", "develop" → core implementation rules
- "optimize", "improve", "speed up", "enhance" → performance rules
- "secure", "protect", "authenticate", "authorize" → security rules
- "test", "validate", "debug", "verify" → testing rules
- "deploy", "release", "publish", "containerize" → deployment rules
- "fix", "troubleshoot", "resolve" → debugging rules

#### Step 3: Identify Feature Requirements
Look for feature-specific keywords:
- "authentication", "login", "auth", "SSO" → security rules
- "caching", "cache", "Redis", "memcached" → performance/caching rules
- "dashboard", "visualization", "charts", "graphs" → UI/visualization rules
- "API", "endpoint", "REST", "GraphQL" → API framework rules
- "database", "ORM", "SQL", "queries" → database rules
- "monitoring", "logging", "observability" → monitoring rules

#### Step 4: Combine for Multi-dimensional Search
Example: "Build a FastAPI API with authentication and caching"

Extracted keywords:
- **Technology**: Python, FastAPI
- **Actions**: build, implement
- **Features**: authentication, API, caching

Required rules:
- 000-global-core (always)
- 200-python-core (Python foundation)
- 210-python-fastapi-core (FastAPI framework)
- 210a-python-fastapi-security (authentication)
- Performance rules for caching (search RULES_INDEX.md for "caching")

#### Step 5: Search RULES_INDEX.md Keywords Column
Execute search with extracted keywords:
- Use **case-insensitive** matching
- **Partial matches** are acceptable ("auth" matches "authentication")
- **Prioritize exact matches** over partial
- **Consider synonyms**:
  - "auth" = "authentication" = "security"
  - "optimize" = "performance" = "speed"
  - "test" = "testing" = "validation"
  - "deploy" = "deployment" = "release"

#### Common Keyword Patterns

| User Request Pattern | Extracted Keywords | Typical Rules |
|---------------------|-------------------|---------------|
| "Build a Python CLI tool" | Python, CLI, build | 000, 200, 220 |
| "Add auth to FastAPI" | Python, FastAPI, authentication, security | 000, 200, 210, 210a |
| "Optimize slow Snowflake query" | Snowflake, optimize, performance, query | 000, 100, 103 |
| "Create Streamlit dashboard with charts" | Snowflake, Streamlit, dashboard, visualization, charts | 000, 100, 101, 101a |
| "Write unit tests for my API" | Python, testing, unit tests, API | 000, 200, 206, 210b |
| "Dockerize this application" | Docker, deploy, containerize | 000, 400 |
| "Debug performance issue" | optimize, performance, debug, troubleshoot | 000, domain-core, 103 or perf rules |

### Practice: Self-Test
For the request "Help me secure my Streamlit dashboard with proper authentication":
- Technologies: Snowflake, Streamlit
- Actions: secure, implement
- Features: authentication, security, dashboard
- Rules: 000, 100, 101, 101c (Streamlit security)
```

**Files Modified:** AGENTS.md
**Estimated Time:** 20 minutes

---

#### 2.2: Add Rule Loading Limits to AGENTS.md
**Rationale:** Prevents token bloat, provides clear boundaries
**Source:** agent-improvements-one.md, Issue 7

**Add new section after "TOKEN BUDGET MANAGEMENT":**
```markdown
## RULE LOADING LIMITS AND PRIORITIZATION

### Maximum Recommended Rules Per Session

#### Initial Load (at session start):
- **Minimum**: 1 rule (000-global-core.md only)
- **Typical**: 3-5 rules (foundation + domain + 2-3 specialized)
- **Maximum**: 8-10 rules for complex cross-domain tasks
- **Token budget target**: 2000-3500 tokens total for initial context

#### Throughout Session (as scope expands):
- Add rules **incrementally** as new requirements emerge
- Drop **Low/Medium** tier rules if approaching context limits
- Keep **Critical and High** tier rules loaded
- Re-prioritize based on **current task focus**

### When to STOP Loading Rules

Stop adding rules when:
1. **Token budget exceeds 5000 tokens** of rule content
2. **You have clear guidance** for current task
3. **Diminishing returns**: Adding more rules doesn't improve response quality
4. **User hasn't mentioned** new domains/features requiring additional rules
5. **Context window pressure**: Approaching platform limits

### Rule Loading Priority Matrix

| Priority Level | When to Load | Example Rules | Token Budget |
|----------------|-------------|---------------|--------------|
| 1 - Critical | Always at session start | 000-global-core | ~300 tokens |
| 2 - Domain Core | User mentions technology | 100, 200, 300, 400 | ~400-500 tokens |
| 3 - Primary Feature | User's main request | 210-fastapi, 101-streamlit | ~400-800 tokens |
| 4 - Secondary Feature | Specific requirements mentioned | 210a-security, 101a-visualization | ~300-500 tokens |
| 5 - Enhancement | Nice-to-have improvements | 201-lint-format, 204-docs | ~300-400 tokens |

### Token Budget Tracking Example

Session start - User: "Build a FastAPI app with authentication"
```
Loaded:
- 000-global-core         (~300 tokens)  [Critical]
- 200-python-core         (~450 tokens)  [Domain Core]
- 210-python-fastapi-core (~400 tokens)  [Primary Feature]
- 210a-fastapi-security   (~350 tokens)  [Secondary Feature]
Total: ~1500 tokens ✅ Within target

Mid-session - User: "Also add caching and monitoring"
Additional load:
- Performance/caching rule (~400 tokens)
- Monitoring rule        (~350 tokens)
Total: ~2250 tokens ✅ Still good

Later - User: "Now add comprehensive testing"
Additional load:
- 206-python-pytest     (~400 tokens)
- 210b-fastapi-testing  (~350 tokens)
Total: ~3000 tokens ✅ Approaching limit

If user adds: "And Docker deployment"
Decision: Would reach ~3800 tokens
Action: Load 400-docker, but consider dropping Enhancement tier rules
```

### Prioritization Strategy

When approaching token limits:
1. **Keep**: 000-global-core (always)
2. **Keep**: Domain core rules (100/200/300/400)
3. **Keep**: Rules directly relevant to current task
4. **Drop**: Enhancement rules (documentation, formatting)
5. **Drop**: Medium/Low tier rules not actively being applied
6. **Summarize**: If a rule was loaded but no longer needed, drop it
```

**Files Modified:** AGENTS.md
**Estimated Time:** 15 minutes

---

#### 2.3: Add Parallelization Guidance
**Rationale:** Improves performance, reduces latency
**Source:** agent-improvements-two.md

**Add to AGENTS.md in "UNIVERSAL FILE ACCESS STRATEGIES" section:**
```markdown
### Performance Optimization: Parallel Loading

When loading multiple independent files, use parallel tool calls:
- ✅ Load rules/000-global-core.md, rules/RULES_INDEX.md, rules/200-python-core.md in parallel
- ✅ Read multiple specialized rules simultaneously
- ❌ Don't wait for sequential completion if files are independent

Example parallel loading:
```
# Instead of sequential:
load(000-global-core.md)
load(RULES_INDEX.md)
load(200-python-core.md)

# Use parallel (if your platform supports):
load_parallel([
  000-global-core.md,
  RULES_INDEX.md,
  200-python-core.md
])
```

This reduces latency and improves user experience.
```

**Add to rules/000-global-core.md in "Required Steps" section (after step 5):**
```markdown
6. **Maximize parallel execution**: For independent operations (multiple file reads, searches), execute tool calls in parallel rather than sequentially to reduce latency
```

**Files Modified:** AGENTS.md, rules/000-global-core.md
**Estimated Time:** 10 minutes

---

#### 2.4: Add Missing-File Fallback Strategy
**Rationale:** Robustness when rules are missing
**Source:** agent-improvements-two.md

**Add to AGENTS.md after "ADAPTIVE STRATEGIES BY AGENT CAPABILITY":**
```markdown
## MISSING FILE FALLBACK STRATEGY

### When a Required Rule File is Missing or Unreadable

If you attempt to load a rule and it fails:

1. **State the failure clearly**:
   ```
   ⚠️ Warning: Unable to load rules/210-python-fastapi-core.md
   Error: File not found or unreadable
   ```

2. **Proceed with available context**:
   - Use rules you successfully loaded (especially 000-global-core)
   - Apply general best practices from your training
   - Be explicit about limitations: "Without FastAPI-specific rules, I'm providing general Python API guidance"

3. **Request missing file from user**:
   ```
   To provide FastAPI-specific guidance, please:
   - Verify rules/210-python-fastapi-core.md exists in your workspace
   - Include the file in my context if it's available elsewhere
   - Or proceed with general Python guidance
   ```

4. **Document deviations**:
   - Note which rules you couldn't load
   - Explain how this affects your response
   - Suggest which additional context would improve guidance

### Graceful Degradation Priority

If files are missing, prioritize loading in this order:
1. **Critical**: 000-global-core.md (if this fails, inform user immediately)
2. **High**: RULES_INDEX.md (needed for discovery)
3. **Medium**: Domain core rules (100/200/300/400 series)
4. **Lower**: Specialized rules (can work without, but guidance less specific)
```

**Files Modified:** AGENTS.md
**Estimated Time:** 10 minutes

---

#### 2.5: Add Governance-as-Domain Pattern
**Rationale:** Handles meta-requests about rules/process
**Source:** agent-improvements-two.md

**Add to AGENTS.md in "SEMANTIC DISCOVERY GUIDE" section:**
```markdown
### Special Case: Meta-Requests (Governance-as-Domain)

When the user asks about the rule system itself, treat governance as the domain:

**Meta-request patterns:**
- "How do I create a new rule?"
- "What's the rule governance process?"
- "Show me the rule template"
- "How are rules structured?"
- "What metadata fields do rules have?"

**Response:**
1. Load rules/000-global-core.md (always)
2. Load rules/002-rule-governance.md (governance-as-domain)
3. Load rules/RULES_INDEX.md if they need rule discovery help

This satisfies the "domain rule" requirement for meta-requests.
```

**Files Modified:** AGENTS.md
**Estimated Time:** 5 minutes

---

### Phase 3: New Rules and Enhancements (Nice to Have)

#### 3.1: Create rules/005-code-citation-format.md
**Rationale:** Standardizes code display format, already in workspace policy
**Source:** agent-improvements-two.md

**Create new file:**
```markdown
**Keywords:** code citation, code references, snippets, formatting, documentation, existing code, proposed code, markdown code blocks
**Depends:** 000-global-core
**TokenBudget:** ~250
**ContextTier:** High

# Code Citation Format Standards

## Purpose
Standardize how AI assistants display code to distinguish between citing existing code and proposing new code.

## Contract
- **Inputs/Prereqs**: Code to display; file paths for existing code
- **Required**: Use correct format for existing vs new code
- **Forbidden**: Mixing formats; indenting triple backticks; empty code blocks
- **Output Format**: Either CODE REFERENCES or MARKDOWN CODE BLOCKS
- **Validation**: Format renders correctly in IDEs

## Key Principles

### METHOD 1: CODE REFERENCES - Citing Existing Code

Use for code that already exists in the codebase:

**Format:**
```
```startLine:endLine:filepath
// code content here
```
```

**Required Components:**
1. **startLine**: Starting line number (required)
2. **endLine**: Ending line number (required)
3. **filepath**: Full path to file (required)
4. **NO language tag**: Don't add typescript/python/etc.

**Example:**
```
```12:14:app/components/Todo.tsx
export const Todo = () => {
  return <div>Todo</div>;
};
```
```

**Rules:**
- Include at least 1 line of actual code (no empty blocks)
- You may truncate with comments: `// ... more code ...`
- You may add clarifying comments for readability
- You may show edited versions of the code
- NEVER indent the triple backticks
- Use absolute paths when possible

### METHOD 2: MARKDOWN CODE BLOCKS - Proposing New Code

Use for code that doesn't exist yet or general examples:

**Format:**
```
```python
for i in range(10):
    print(i)
```
```

**Required Components:**
1. **Language tag only**: python, javascript, bash, etc.
2. **No line numbers or file paths**

**Example:**
```
```python
def calculate_total(items):
    return sum(item.price for item in items)
```
```

## Critical Rules

### Never Mix Formats
- ❌ Don't use line numbers with language tags: ````1:3:python`
- ❌ Don't use language tags with file paths: ````typescript:app/file.ts`
- ✅ Either CODE REFERENCE or MARKDOWN CODE BLOCK, never hybrid

### Never Indent Triple Backticks
Even in lists or nested contexts:
```
❌ Bad:
- Here's code:
  ```python
  code here
  ```

✅ Good:
- Here's code:
```python
code here
```
```

### Never Include Line Numbers in Content
```
❌ Bad:
```python
1  for i in range(10):
2      print(i)
```

✅ Good:
```python
for i in range(10):
    print(i)
```
```

### Always Include Code Content
```
❌ Bad (empty block):
```12:14:app/components/Todo.tsx
```

✅ Good (at least 1 line):
```12:14:app/components/Todo.tsx
export const Todo = () => {
  return <div>Todo</div>;
};
```
```

## Inline References

For inline mentions (mid-sentence), use single backticks:
- ✅ "The TODO element (`app/components/Todo.tsx`) contains the bug"
- ❌ "The TODO element (```12:14:app/components/Todo.tsx```) contains..."

## Validation
- CODE REFERENCES render correctly in IDE
- MARKDOWN CODE BLOCKS syntax highlight properly
- No format mixing errors
- Absolute paths resolve correctly

## References
- **Related Rules**: 000-global-core (surgical editing), 204-python-docs-comments
- **Workspace Policy**: See <citing_code> section in system prompt
```

**Add to rules/RULES_INDEX.md:**
```markdown
| `005-code-citation-format.md` | Auto-attach | Code citation and snippet formatting standards | Universal code display | code citation, code references, snippets, formatting, documentation, existing code, proposed code, markdown code blocks | `000-global-core.md` |
```

**Files Modified:** New file created, RULES_INDEX.md updated
**Estimated Time:** 20 minutes

---

#### 3.2: Add PLAN/ACT Override to rules/000-global-core.md
**Rationale:** Flexibility for expert users and automated workflows
**Source:** agent-improvements-three.md

**Add to "Mode-Based Workflow" section in rules/000-global-core.md:**
```markdown
### Expert User Override

For experienced users or automated workflows, an override mechanism is available:

**Override Flags:**
- `--auto-act`: Agent proceeds with modifications without waiting for "ACT"
- `--proceed-without-asking`: Bypass PLAN mode for simple tasks
- User statement: "Proceed without asking for approval"

**When Override is Active:**
- Agent still operates safely (surgical edits, validation)
- Agent still discloses planned changes
- Agent proceeds immediately to implementation
- PLAN mode can be re-enabled mid-session: "Switch to PLAN mode"

**Default Behavior:**
- PLAN/ACT workflow is the DEFAULT
- Override must be explicitly requested
- Override is session-specific (doesn't persist)

**Example:**
```
User: "Fix the login bug --auto-act"
Agent: [Identifies bug, makes surgical fix, validates, reports completion]

vs.

User: "Fix the login bug"
Agent: [Enters PLAN mode, analyzes, proposes fix, waits for "ACT"]
```

**Safety Note:** Override is intended for:
- Expert users who understand the codebase
- Automated workflows with proper review processes
- Simple, low-risk modifications
- NOT recommended for complex refactoring or destructive operations
```

**Files Modified:** rules/000-global-core.md
**Estimated Time:** 10 minutes

---

#### 3.3: Add Absolute Paths Preference
**Rationale:** Aligns with workspace policy, prevents ambiguity
**Source:** agent-improvements-two.md

**Add to rules/000-global-core.md "Surgical Editing Principle" section:**
```markdown
### 6. Path References
- **Prefer absolute paths** over relative paths for tool calls
- Example: `/Users/myoung/Development/project/file.py` vs `file.py`
- Prevents path resolution ambiguity
- Aligns with workspace policy
```

**Add to AGENTS.md "FILE STRUCTURE REFERENCE" section:**
```markdown
### Path Conventions
- **Prefer absolute paths** when possible: `/full/path/to/rules/000-global-core.md`
- **Use relative from project root** when absolute not available: `rules/000-global-core.md`
- **Never use**: Ambiguous relative paths like `../rules/file.md`
```

**Files Modified:** rules/000-global-core.md, AGENTS.md
**Estimated Time:** 5 minutes

---

## Implementation Checklist

### Phase 1: Critical Foundation (Must Have)
- [ ] **1.1**: Replace AGENTS.md with AGENTS_V2.md (backup old as AGENTS_LEGACY.md)
- [ ] **1.2**: Add "Continuous Rule Evaluation" section to AGENTS.md
- [ ] **1.3**: Update rules/000-global-core.md with "ALWAYS LOAD FIRST" header
- [ ] **1.4**: Update rules/RULES_INDEX.md header and fix Docker dependency bug
- [ ] **1.5**: Update EXAMPLE_PROMPT.md Step 1 with universal syntax

**Estimated Time: 50 minutes**
**Files Modified: 4** (AGENTS.md, rules/000-global-core.md, EXAMPLE_PROMPT.md, rules/RULES_INDEX.md)

---

### Phase 2: Agent Training and Optimization (Should Have)
- [ ] **2.1**: Add "Keyword Extraction Training" to AGENTS.md
- [ ] **2.2**: Add "Rule Loading Limits" to AGENTS.md
- [ ] **2.3**: Add parallelization guidance to AGENTS.md and rules/000-global-core.md
- [ ] **2.4**: Add "Missing File Fallback" to AGENTS.md
- [ ] **2.5**: Add "Governance-as-Domain" pattern to AGENTS.md

**Estimated Time: 60 minutes**
**Files Modified: 2** (AGENTS.md, rules/000-global-core.md)

---

### Phase 3: New Rules and Enhancements (Nice to Have)
- [ ] **3.1**: Create rules/005-code-citation-format.md and update RULES_INDEX.md
- [ ] **3.2**: Add PLAN/ACT override to rules/000-global-core.md
- [ ] **3.3**: Add absolute paths preference to rules/000-global-core.md and AGENTS.md

**Estimated Time: 35 minutes**
**Files Modified: 4** (New: rules/005-code-citation-format.md, Updated: rules/000-global-core.md, AGENTS.md, rules/RULES_INDEX.md)

---

## Total Implementation

- **Total Files Modified**: 5 (AGENTS.md, rules/000-global-core.md, EXAMPLE_PROMPT.md, rules/RULES_INDEX.md, new: rules/005-code-citation-format.md)
- **Total Estimated Time**: ~2.5 hours
- **Critical Path**: Phase 1 (50 minutes) - blocks workflow if not done
- **High Value**: Phase 2 (60 minutes) - significantly improves agent performance
- **Optional**: Phase 3 (35 minutes) - nice enhancements, not blocking

---

## Testing Plan

### Test Cases After Implementation

#### Test 1: Bootstrap Loading
**User**: Start new session with "Build a Python API"
**Expected**: Agent loads 000, RULES_INDEX, then 200, 210
**Verify**: Agent acknowledges loaded rules

#### Test 2: Continuous Evaluation
**User**: "Build Python API" then "Add authentication"
**Expected**: Agent loads security rules mid-session
**Verify**: Agent says "Loading 210a-fastapi-security for authentication"

#### Test 3: Keyword Extraction
**User**: "Optimize my Snowflake query performance"
**Expected**: Agent extracts "Snowflake", "optimize", "performance"
**Verify**: Agent loads 100, 103 (performance tuning)

#### Test 4: Token Limits
**User**: Request covering 8+ domains
**Expected**: Agent stops at ~5000 tokens, prioritizes Critical/High tier
**Verify**: Agent explains which rules not loaded due to limits

#### Test 5: Missing File
**User**: Task requiring missing rule
**Expected**: Agent states failure, proceeds with available rules, requests file
**Verify**: Graceful degradation, clear communication

#### Test 6: Meta-Request
**User**: "How do I create a new rule?"
**Expected**: Agent loads 000 + 002-rule-governance
**Verify**: Uses governance-as-domain pattern

---

## Success Metrics

### Quantitative
- ✅ Agent loads 000-global-core in 100% of sessions
- ✅ Agent re-evaluates rules mid-session when scope expands
- ✅ Token budget stays under 3500 tokens for initial load
- ✅ Agent uses correct keyword extraction in 90%+ of cases

### Qualitative
- ✅ Agent responses consistently reference loaded rules
- ✅ User can trace which rules informed each decision
- ✅ Agent gracefully handles missing files
- ✅ Multiple agent platforms (Claude, GPT-4, Gemini) follow protocol

---

## Rollback Plan

If implementation causes issues:

1. **Immediate rollback**: Restore AGENTS_LEGACY.md → AGENTS.md
2. **Partial rollback**: Keep Phase 1, remove Phase 2/3 changes
3. **Rule-specific rollback**: Revert individual rule changes using git
4. **Testing**: Have original AGENTS.md and AGENTS_V2.md available for comparison

---

## Post-Implementation

### Documentation Updates Needed
- [ ] Update README.md to reference new AGENTS.md structure
- [ ] Update CONTRIBUTING.md with continuous evaluation workflow
- [ ] Add "Getting Started" guide for new users
- [ ] Document keyword extraction process for humans

### Future Enhancements (Out of Scope)
- [ ] YAML/JSON version of RULES_INDEX.md for programmatic parsing
- [ ] Automated rule validation tool
- [ ] Rule usage analytics (which rules are loaded most frequently)
- [ ] Interactive rule discovery tool

---

*This implementation plan synthesizes the best recommendations from all three improvement documents, prioritized by impact on the 7-step workflow.*

