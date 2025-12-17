# AI Agent Bootstrap Protocol

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
> 
> This file defines the mandatory rule loading protocol and MODE/ACT framework
> that ALL agents must follow for EVERY response. 
> 
> **Context Window Management:** If context limits are reached, preserve this
> file completely. Summarize task history, file contents, or other context first.
> This bootstrap protocol must remain fully accessible at all times.

## Mandatory Rule Loading Protocol

> **Note:** All rules referenced in this document are located in the `rules/` directory.
> File paths shown use bare filenames (e.g., `000-global-core.md`) for readability.
> When loading rules with tools, prefix with `rules/` (e.g., `read_file("rules/000-global-core.md")`).

**FIRST ACTION EVERY RESPONSE:**

> **Note:** Steps 1-3 are internal processing (before generating response).
> Steps 4-5 define the response output format.

1. **Load Foundation** - Read `000-global-core.md` (always first, no exceptions)
   - IF not accessible: STOP with "Cannot proceed - 000-global-core.md not accessible"
   - IF empty: STOP with "Rule generation failed - 000-global-core.md is empty"

2. **Load Domain + Language Rules** - Match file extensions to domain rules
   - Scan user request for file extensions and technology keywords
   - See RULES_INDEX.md "Rule Loading Strategy", Section 2 for complete mapping
   - **Do not duplicate mappings here; RULES_INDEX.md is the canonical source**
   - **Load even for "simple" tasks** (linting, formatting, syntax fixes)
   - **Unknown extensions:** If no domain rule exists for a file type, load only 000-global-core.md and note in Rules Loaded: "No domain-specific rules available for [extension]"

3. **Load Activity-Specific Rules** - Search `RULES_INDEX.md` Keywords field
   - Method: `grep -i "KEYWORD" RULES_INDEX.md` (or scan Keywords field manually if shell unavailable)
   - See RULES_INDEX.md, Section 3 for common keyword-to-rule mappings

**Fallback: Browse by Domain Section**

If keyword search yields no matches, browse RULES_INDEX.md Rule Catalog by domain:
- **Core Foundation (000-series):** Workflow, governance, context, tool design
- **Snowflake (100-series):** SQL, Streamlit, Cortex, pipelines, security
- **Python (200-series):** Linting, testing, FastAPI, Typer, Pydantic
- **Shell (300-series):** Bash, Zsh scripting
- **Frontend (400-series):** JavaScript, TypeScript, React
- **Go (600-series):** Go development
- **Project (800-series):** Changelog, README, contributing, Taskfile
- **Analytics (900-series):** Business analytics, demos

**Lazy Loading Strategy (Token Optimization):**

**PLAN Phase (Minimal Load):**
- ALWAYS load: 000-global-core.md
- Load domain core IF files being modified (200-python for .py, 100-snowflake for .sql, etc.)
- DEFER specialized rules until task list is defined

**ACT Phase (Task-Driven Load):**
- Load specialized rules based on task list keywords:
  - Task mentions "tests": load pytest/testing rule
  - Task mentions "performance": load performance tuning rule
  - Task mentions "security": load security patterns rule

**Example:**
```
PLAN: Load 000 + 200-python-core (analyze task)
Task List: "Refactor auth.py, update tests, check types"

ACT: NOW load 206-python-pytest + 207-python-typing (execute with full context)
```

**When to Skip Lazy Loading:**
- Complex tasks requiring upfront comprehensive analysis
- User explicitly requests detailed review
- Previous attempts failed (may need more rules)

4. **Declare MODE** - First line of response: `MODE: [PLAN|ACT]`
   - Default: MODE: PLAN
   - ACT only after user types "ACT"
   - **For MODE transition rules and workflow behavior, see rules/000-global-core.md**
   - **Optional (clarifying questions):** When input is ambiguous, ask clarifying questions using
     **A/B/C/D/E** choices (see `000-global-core.md`, "Clarification Gate (Options-Based
     Questions)").
   - If you present a Task List in MODE: PLAN, end the response with:
     - `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`

**ACT Authorization:**
- Recognized: "ACT", "act", "Act" (case-insensitive exact match)
- Recognized: "ACT on items 1-3" (partial authorization)
- NOT recognized: "proceed", "go ahead", "yes", "okay"

See 000-global-core.md "ACT Recognition Rules" for full specification

5. **Declare Loaded Rules** - Immediately after MODE as second section
   - Format: `## Rules Loaded` followed by bulleted list
   - Always include: `- rules/000-global-core.md (foundation)`
   - Add domain/specialized rules with brief context (file extension, keyword, or dependency)
   - Example: `- rules/200-python-core.md (file extension: .py)`

**Violation = INVALID Response** - Any gate failure requires immediate correction before proceeding.

**For operational behavior AFTER rules are loaded (MODE transitions, validation commands, task confirmation, persona), see rules/000-global-core.md**

## Loading Semantics

"Loading" a rule means completing all three steps:
1. **Read** - Retrieve file contents (via read_file or equivalent)
2. **Apply** - Follow all guidance from the rule
3. **Declare** - List in `## Rules Loaded` section with context

All three steps are mandatory. Reading without declaration is a protocol violation.

**Apply Semantics:** Loading makes rules *available*; execution *applies* them. Loading pytest rules doesn't run tests; it informs how to write/run them.

**Rule Loading Failures:**

- **000-global-core.md missing:** STOP with error message. Cannot proceed.
- **RULES_INDEX.md missing:** WARN, load 000 + match by file extension. Can proceed (degraded).
- **Domain rule missing:** WARN, proceed with 000-global-core.md only. Can proceed (limited).
- **Dependency missing:** Skip dependent rule, log warning. Can proceed (skip rule).
- **Rule file malformed:** Log error, skip rule. Can proceed (skip rule).

## Rule Discovery Reference

### Rule Organization

**Prefix Scheme:** 000=Core | 100=Snowflake | 200=Python | 300=Shell | 400=Docker/Frontend | 600=Golang | 800=Project Mgmt | 900=Demo/Analytics  
**Full mapping:** See RULES_INDEX.md

### Rule Discovery Methods

**Primary Method: Search RULES_INDEX.md**

Use RULES_INDEX.md as the authoritative source for rule discovery:
1. **Search Keywords field** for terms matching your task
2. **Check Depends field** for prerequisites
3. **Load in dependency order** (prerequisites first)

**Split Rules Pattern**

Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization. This improves token efficiency by allowing focused loading.

### Essential Rule Metadata

When parsing rules, use these metadata fields:
- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical > High > Medium > Low)
- **Depends:** Prerequisites that must be loaded first

### Progressive Loading Strategy

**Order:** Foundation (000), then Domain core (100/200/300), then Specialized (task-based)  
**Monitor:** Track cumulative tokens, prioritize Critical/High tiers  
**See also:** "Lazy Loading Strategy" section above for PLAN vs ACT phase loading

### Multi-Agent Environments

When multiple AI agents (e.g., Cursor + Cline) work on the same project:

- **File awareness:** If another agent may be editing a file, verify current state before modifications
- **Independent authorization:** Each agent maintains its own MODE state; one agent's ACT does not authorize another
- **Rule consistency:** All agents in the same project should use the same RULES_INDEX.md version

## Glossary

- **Foundation Rule:** `000-global-core.md` (always loaded first)
- **Domain Rule:** Technology-specific core (e.g., 200-python-core, 100-snowflake-core)
- **Activity Rule:** Task-specific patterns (e.g., 206-python-pytest for testing)
- **Surgical Edit:** Minimal, targeted change preserving existing patterns (synonyms: "minimal changes", "delta-focused")
- **Load:** Read + Apply + Declare a rule (all three steps mandatory)
- **Token Budget:** Cumulative token count of all loaded rules
