# AI Agent Bootstrap Protocol

## Mandatory Rule Loading Protocol

**FIRST ACTION EVERY RESPONSE:**

> **Note:** Steps 1-3 are internal processing (before generating response).
> Steps 4-5 define the response output format.

1. **Load Foundation** - Read `rules/000-global-core.md` (always first, no exceptions)
   - IF not accessible → STOP: "Cannot proceed - 000-global-core.md not accessible"
   - IF empty → STOP: "Rule generation failed - 000-global-core.md is empty"

2. **Load Domain + Language Rules** - Match file extensions to domain rules
   - Scan user request for file extensions and technology keywords
   - See RULES_INDEX.md "Rule Loading Strategy" → Section 2 for complete mapping
   - **Do not duplicate mappings here; RULES_INDEX.md is the canonical source**
   - **Load even for "simple" tasks** (linting, formatting, syntax fixes)
   - **Unknown extensions:** If no domain rule exists for a file type, load only 000-global-core.md and note in Rules Loaded: "No domain-specific rules available for [extension]"

3. **Load Activity-Specific Rules** - Search `RULES_INDEX.md` Keywords column
   - Method: `grep -i "KEYWORD" RULES_INDEX.md` (or scan Keywords column manually if shell unavailable)
   - See RULES_INDEX.md → Section 3 for common keyword-to-rule mappings

4. **Declare MODE** - First line of response: `MODE: [PLAN|ACT]`
   - Default: MODE: PLAN
   - ACT only after user types "ACT"
   - **For MODE transition rules and workflow behavior, see rules/000-global-core.md**
   - **Optional (clarifying questions):** When input is ambiguous, ask clarifying questions using
     **A/B/C/D/E** choices (see `rules/000-global-core.md` → "Clarification Gate (Options-Based
     Questions)").
   - If you present a Task List in MODE: PLAN, end the response with:
     - `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`

**ACT Authorization Examples:**
- "ACT" → Recognized (executes full task list)
- "act" or "Act" → Recognized (case-insensitive)
- "ACT on items 1-3" → Partial authorization (execute specified items only)
- "ACT please" or "go ahead" → NOT recognized (requires exact "ACT")
- See rules/000-global-core.md "ACT Recognition Rules" for complete specification

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

**Apply Semantics:**
- Rules are *applied* during task execution, not during loading
- Loading makes rules *available*; execution *applies* them
- Example: Loading 206-python-pytest.md doesn't run tests; it informs how to write/run tests when the task requires it

**Rule Loading Failures:**

| Failure Type | Response | Can Proceed? |
|--------------|----------|--------------|
| 000-global-core.md missing | STOP with error message | No |
| RULES_INDEX.md missing | WARN, load 000 + match by file extension | Yes (degraded) |
| Domain rule missing | WARN, proceed with 000-global-core.md only | Yes (limited) |
| Dependency missing | Skip dependent rule, log warning | Yes (skip rule) |
| Rule file malformed | Log error, skip rule | Yes (skip rule) |

## Rule Discovery Reference

### Rule Organization

Rules are organized by numeric domain prefixes:
- **000-099:** Core/Foundational (always start here)
- **100-199:** Snowflake ecosystem
- **200-299:** Python ecosystem
- **300-399:** Shell/Bash scripting
- **400-499:** Docker/Containers/Frontend
- **500-599:** Reserved (currently unused)
- **600-699:** Golang
- **700-799:** Reserved (currently unused)
- **800-899:** Project Management
- **900-999:** Demo/Examples/Data Science/Business Analytics

### Rule Discovery Methods

**Primary Method: Search RULES_INDEX.md**

Use RULES_INDEX.md as the authoritative source for rule discovery:
1. **Search Keywords/Hints column** for terms matching your task
2. **Check Depends On column** for prerequisites
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

Load rules incrementally to manage token budget:
1. **Foundation:** 000-global-core.md (always first)
2. **Domain:** Technology-specific core (e.g., 100-snowflake-core, 200-python-core)
3. **Specialized:** Task-specific rules based on Keywords match
4. **Monitor:** Track cumulative tokens, prioritize Critical/High tiers

### Multi-Agent Environments

When multiple AI agents (e.g., Cursor + Cline) work on the same project:

- **File awareness:** If another agent may be editing a file, verify current state before modifications
- **Independent authorization:** Each agent maintains its own MODE state; one agent's ACT does not authorize another
- **Rule consistency:** All agents in the same project should use the same RULES_INDEX.md version

## Glossary

- **Foundation Rule:** `rules/000-global-core.md` (always loaded first)
- **Domain Rule:** Technology-specific core (e.g., 200-python-core, 100-snowflake-core)
- **Activity Rule:** Task-specific patterns (e.g., 206-python-pytest for testing)
- **Surgical Edit:** Minimal, targeted change preserving existing patterns (synonyms: "minimal changes", "delta-focused")
- **Load:** Read + Apply + Declare a rule (all three steps mandatory)
- **Token Budget:** Cumulative token count of all loaded rules
