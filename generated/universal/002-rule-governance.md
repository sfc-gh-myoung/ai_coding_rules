**Keywords:** rule governance, standards, semantic discovery, metadata, keywords, RULES_INDEX, system prompt altitude, right altitude, tool design
**Depends:** 000-global-core

# Rule Governance: Universal Standards for AI Coding Rules

## Purpose
Establish comprehensive governance for creating, maintaining, and organizing AI coding rule files to ensure consistency, discoverability, and effectiveness across different editors and AI models.

## Rule Type and Scope

- **Type:** Auto-attach
- **Scope:** Universal rule file creation, maintenance, and governance standards for all AI models and editors

## Contract
- **Inputs/Prereqs:** Rule creation requirements; project context; technology scope
- **Allowed Tools:** Documentation tools; rule templates; validation tools
- **Forbidden Tools:** Rule duplication tools; context-specific rule generators without universal principles
- **Required Steps:**
  1. Define rule purpose and scope clearly
  2. Include required sections (Purpose, Contract, Validation, etc.)
  3. Specify type (Auto-attach vs Agent Requested)
  4. Include compliance checklist and response template
  5. Add external documentation references
- **Output Format:** Markdown files following required section structure
- **Validation Steps:** Section completeness check; cross-reference validation; size budget compliance

## Key Principles

- **Universal Applicability:** Rules work across different AI models (Claude 4.x, GPT-4, Gemini) and editors (Cursor, Copilot, Cline)
- **Single Responsibility:** Each rule focuses on one specific domain or technology
- **Explicit Contracts:** Clear inputs, outputs, and validation criteria with quantifiable success metrics
- **Composable Design:** Rules reference and build upon each other logically with declared dependencies
- **Professional Standards:** Consistent tone, structure, and formatting using semantic markup
- **LLM-Optimized Format:** Enhanced Markdown with emojis for semantic sections, token budgets declared, explicit behavior specifications
- **Context Awareness:** Support for Claude 4.5+ native token management and multi-session state tracking
- **Investigation-First:** Rules must encourage verification over speculation to minimize hallucinations

## 1. Rule Creation & Naming Constraints
- **Requirement:** Place universal rule files in the canonical `ai_coding_rules/` directory. Optional mirrors may exist in editor-specific folders (e.g., `.cursor/rules/`).
- **Requirement:** Use a snake-case naming convention with a `.md` extension (e.g., `your_rule_name.md`).
- **Requirement:** Include a clear description and, if needed, scope notes at the top of the file. Mandatory metadata `Version`, `LastUpdated`, `Keywords`, `TokenBudget`, and `ContextTier` must be included in plain text. The `Keywords` field is **CRITICAL** for semantic discovery and automatic rule loading (promoted to required in v2.4).

## 2. Semantic Markup with Enhanced Markdown

### LLM Parsing Optimization with Universal Markdown

**Requirement:** Use enhanced Markdown with emojis for semantic markup to enable precise LLM parsing across ALL models (Claude 4.x, GPT-4, Gemini) and editors (Cursor, Copilot, Cline).

**Universal Compatibility:**
- ✅ **Claude 4:** Markdown with emojis fully supported
- ✅ **GPT-4:** Native Markdown interpretation
- ✅ **Gemini:** Full Markdown support
- ✅ **GitHub Copilot:** Markdown-based custom instructions
- ✅ **Cursor IDE:** Markdown rules with all LLM backends
- ✅ **Cline:** Markdown-based rules
- ✅ **All Markdown Viewers:** Clean rendering

**Standard Markdown Patterns for Rules:**

```markdown
> **Section Metadata**  
> Token Budget: ~450 | Context Tier: essential | Priority: high

**🔥 MANDATORY:**
- [Mandatory content here]

**❌ FORBIDDEN:**
- [Forbidden actions here]

**✅ RECOMMENDED:**
- [Best practices here]

> **⚠️ Investigation Required**  
> [Instructions requiring verification before response]

> **🤖 Claude 4 Specific Guidance**  
> [Claude 4 specific optimizations]
```

**Markdown Pattern Guidelines:**
- **Requirement:** Use emoji-prefixed bold headings for directive strength
- **Requirement:** Use blockquotes (`>`) for metadata and special guidance sections
- **Always:** Include Section Metadata blockquote for priority/budget tracking
- **Consider:** Add model-specific guidance blockquotes for model-optimized patterns

**Emoji Standards (Universal):**
- 🔥 **MANDATORY** - Critical requirements
- ❌ **FORBIDDEN** - Prohibited actions
- ✅ **RECOMMENDED** - Best practices
- ⚠️ **Investigation Required** - Verification needed
- 🤖 **Model-Specific** - Model-optimized guidance
- 📊 **Metric** - Measurements and targets

## 3. Required Rule Structure

### Mandatory Sections (In Order)
Every rule file must follow this structure:

```markdown
# Rule Title

> **Section Metadata**  
> Token Budget: ~450 | Context Tier: essential | Priority: high

## Purpose
[1-2 sentences clearly explaining what this rule accomplishes and why it exists]

## Rule Type and Scope
- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Description of what the rule covers and applies to]

## Contract

**🔥 MANDATORY:**
- **Inputs/Prereqs:** [Required context, files, env vars]
- **Allowed Tools:** [List tools permitted for this rule]

**❌ FORBIDDEN:**
- **Forbidden Tools:** [List tools not allowed]

**🔥 MANDATORY:**
- **Required Steps:** [Ordered, explicit steps the AI must follow. Be explicit - Claude 4 requires clear instructions]
- **Output Format:** [Exact expected output format]
- **Validation Steps:** [Checks the AI must run to confirm success]

## Key Principles (when applicable)
- [Concise bullet points summarizing core concepts]

## 1. Detailed Section
[Comprehensive implementation details with explicit instructions]

## Anti-Patterns and Common Mistakes (CRITICAL for Claude 4)
**❌ Anti-Pattern 1:** [Description with example]
**✅ Correct Pattern:** [How to do it right with example]

**❌ Anti-Pattern 2:** [Description with example]
**✅ Correct Pattern:** [How to do it right with example]

## Quick Compliance Checklist
- [ ] [5-10 verification items AI can check before acting]

## Validation
- **Success Checks:** [How to verify rule compliance]
- **Negative Tests:** [What should fail and how to detect it]
```

## Response Template
```<LANG>
<Minimal, copy-pasteable template showing expected output format>
```

## References

### External Documentation
- [Official Documentation](https://example.com/) - Description

### Related Rules
- **Rule Name**: `filename.md`

### Section Requirements

**When to include Key Principles:**
- **Required:** Foundational rules (core, language-specific, major frameworks)
- **Consider:** Complex topics with multiple interconnected concepts
- **Optional:** Simple, focused rules with straightforward implementation

**Rule Type and Scope Section Requirements:**
- **Mandatory:** Every rule must include a `## Rule Type and Scope` section immediately after the Purpose section
- **Type:** Must specify either "Auto-attach" (for foundational rules) or "Agent Requested" (for specialized rules)
- **Scope:** Must clearly describe what the rule covers, applies to, and its intended use cases

**References Section Requirements:**
- **Mandatory:** Every rule must include a `## References` section
- **Mandatory:** Include `### External Documentation` with links to official documentation, guides, and authoritative resources
- **Mandatory:** Include `### Related Rules` when logical relationships exist to other rules in the system
- **Format:** Use `- **Rule Name**: \`filename.md\`` format for Related Rules entries
- **Quality:** External documentation links must be current, authoritative, and directly relevant to the rule's purpose

## 4. Rule Types and Scoping

### Auto-attach Rules
- **Criteria:** Universal principles that apply to all interactions
- **Examples:** Core workflow, safety protocols, professional communication
- **Limit:** Keep to essential foundational rules only
- **Scope Control:** Avoid auto-attaching specialized technology rules
- **Requirement:** Only the global core rule should auto-attach universally
- **Requirement:** Limit scope tightly to avoid auto-attaching rules unnecessarily

### Agent Requested Rules
- **Criteria:** Specialized knowledge for specific technologies or domains
- **Examples:** Language-specific practices, framework patterns, tool usage
- **Benefits:** Reduces context overhead; allows targeted expertise
- **Organization:** Group related rules in numbered ranges (e.g., 200-299 for Python)
- **Consider:** Prefer an on-demand (Agent Requested) pattern for specialized topics to control context cost across IDEs and CLI tools

### Semantic Discovery and Keywords

**Purpose:** Enable AI agents to automatically discover and load relevant rules based on conversation context and user queries.

**Keywords Metadata:**
- 🔥 **CRITICAL - MANDATORY:** Include `**Keywords:**` metadata in ALL rule files for semantic matching (required in v2.4)
- **Format:** Comma-separated list of technologies, concepts, patterns, and common use cases
- **Best Practices:**
  - Include primary technology names (e.g., "Snowflake", "Python", "FastAPI")
  - Add specific features and components (e.g., "CTE", "warehouse", "async", "dependency injection")
  - Include common query terms users might use (e.g., "performance", "optimization", "testing", "security")
  - Add related concepts and patterns (e.g., "incremental loading", "REST API", "authentication")
  - List 5-15 keywords for optimal semantic matching
- **Example:** `**Keywords:** Snowflake, SQL, CTE, performance tuning, cost optimization, warehouse sizing, query profile, clustering keys, partitioning`

**RULES_INDEX.md Integration:**
- **Mandatory:** All Agent Requested rules must be listed in `RULES_INDEX.md` with expanded keyword hints
- **Purpose:** RULES_INDEX.md serves as the primary discovery mechanism for rule selection
- **Always:** When creating or updating rules, ensure RULES_INDEX.md entry includes comprehensive keywords
- **Critical:** Agents MUST consult RULES_INDEX.md before starting technical work to identify relevant rules based on keywords

## 5. Content Standards

### Rule Sizing Guidelines

**Line Count Targets:**
- **Target Length:** 150-300 lines per rule
- **Maximum Length:** 500 lines (split larger topics into multiple rules)
- **Focus Principle:** One rule per major concept or technology area
- **Composition:** Reference other rules rather than duplicating content

**Token Budget Declaration (REQUIRED):**
- **Requirement:** Every rule must declare a token budget in metadata
- **Format:** `**TokenBudget:** ~[number]` (e.g., ~450, ~800, ~2000) - MUST be numeric with tilde prefix
- **Forbidden:** Do NOT use text labels like "small", "medium", "large" - use specific numbers only
- **Context Tier:** Must specify `**ContextTier:** [essential|standard|comprehensive]`
- **Calculation:** Approximately 2 tokens per line as rough estimate

**Token Budget Tiers (Use Numeric Values):**
```markdown
**Small (<300 tokens / ~150 lines):**
- **TokenBudget:** ~150, ~200, ~250 (numeric values)
- **ContextTier:** essential
- **Use Case:** Copilot-safe, always-loaded rules
- **Examples:** Core workflow, security constraints

**Medium (300-600 tokens / ~300 lines):**
- **TokenBudget:** ~300, ~400, ~500, ~600 (numeric values)
- **ContextTier:** standard
- **Use Case:** Language/framework-specific rules
- **Examples:** Python core, FastAPI patterns

**Large (600-1200 tokens / ~300-600 lines):**
- **TokenBudget:** ~700, ~800, ~1000, ~1200 (numeric values)
- **ContextTier:** High
- **Use Case:** Comprehensive technical guides
- **Examples:** Advanced optimization patterns

**Very Large (>1200 tokens / >600 lines):**
- **TokenBudget:** ~1500, ~2000, ~2500+ (numeric values)
- **ContextTier:** comprehensive
- **Use Case:** Extensive domain-specific guides
- **Examples:** Full framework documentation, comprehensive analytics guides
```

**Anti-Pattern:**
❌ `**TokenBudget:** small` or `**TokenBudget:** medium` or `**TokenBudget:** large`

**Correct Pattern:**
✅ `**TokenBudget:** ~450` or `**TokenBudget:** ~1200` or `**TokenBudget:** ~2200`

**Claude 4.5 Context Awareness:**
> **🤖 Claude 4.5 Specific Guidance**  
> **For Claude 4.5+ users:** This model features native context awareness and can track its remaining token budget throughout a conversation. When you declare token budgets in rules:
> - Claude will self-manage context consumption
> - Prioritize core directives if approaching budget limit
> - Use progressive disclosure (read TL;DR sections first)
> - Reference external docs instead of copying content
>
> **For other models:** Token budgets serve as sizing guidance and priority indicators.

**Content Requirements:**
- **Requirement:** Keep each rule file concise and focused (target 150–300 lines; max 500 lines)
- **Consider:** Split large topics into multiple composable rules
- **Requirement:** Avoid duplication across rules; reference other rules or `@path/to/file` instead

### Anti-Patterns Library (CRITICAL for Claude 4)

**Priority:** 🔥 CRITICAL - Claude 4 models pay extreme attention to examples as part of their precise instruction following capabilities.

**Requirement:** Every rule with complex behavior MUST include an Anti-Patterns section showing both incorrect and correct approaches.

**Structure:**
```markdown
## Anti-Patterns and Common Mistakes

**❌ Anti-Pattern 1: [Descriptive Name]**
```[language]
// Bad example showing what NOT to do
[Complete, runnable anti-pattern code]
```
**Problem:** [Specific issues this causes]

**✅ Correct Pattern:**
```[language]
// Good example showing the right approach
[Complete, runnable correct code]
```
**Benefits:** [Why this approach is better]

**❌ Anti-Pattern 2: Vague Instructions**
```markdown
"Create a good analytics dashboard"
```
**Problem:** Claude 4 won't automatically add extra features unless explicitly requested.

**✅ Explicit Instructions:**
```markdown
"Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation. Use your entire context budget to deliver a polished, production-ready result."
```
**Benefits:** Explicit behavior specifications ensure Claude understands scope and quality expectations.
```

**Why This Matters for Claude 4:**
- Claude 4 follows examples with high precision
- Anti-patterns teach what to avoid as effectively as positive examples teach what to do
- Explicit behavior specifications are required (Claude 4 doesn't assume "above and beyond" behavior)
- Complete, runnable examples prevent ambiguity

**Requirement:** Include 2-5 anti-pattern/correct-pattern pairs per rule
**Requirement:** Use fenced code blocks with language tags for all code examples
**Requirement:** Explain WHY each anti-pattern is problematic and WHY the correct pattern is better

### Professional Communication Requirements
- **Tone:** Technical, direct, professional
- **Language:** Use directive language (Requirement, Always, Rule, Avoid)
- **Examples:** Include practical, runnable examples with proper syntax highlighting
- **Requirement:** Be explicit with instructions - Claude 4 requires clear, direct specifications without assuming behavior

### Emoji Usage in Rules

**Context:** LLMs (Claude 4, GPT-4, Gemini) can read and interpret emojis as semantic tokens. Each emoji consumes 1-4 tokens but can significantly improve human scan-ability of long rule files.

**Functional Semantic Markers (ALLOWED in rule files):**

Use these standardized emojis as semantic markers to improve visual parsing:

- 🔥 **CRITICAL** - Critical priority items (security, data loss prevention)
- ⚠️ **WARNING** - Important warnings requiring attention
- ✅ **CORRECT** - Correct pattern examples in anti-pattern sections
- ❌ **INCORRECT** - Anti-pattern examples showing what NOT to do
- 📊 **METRIC** - Measurable targets and quantifiable goals
- 🆕 **NEW** - New sections or features added in updates

**Usage Guidelines:**
- **Limit:** Maximum 3-5 standardized markers per rule file
- **Consistency:** Always use the same emoji for the same meaning across all rules
- **Purpose:** Functional semantic markers only, never decorative
- **Placement:** Beginning of priority statements or section headers
- **Token Cost:** ~5 emojis = ~5 tokens in a 600-token rule = <1% overhead

**Rationale:**
- **Human Benefit:** Dramatically improves scan-ability in 500-line rule files
- **LLM Understanding:** All major LLMs correctly interpret semantic emojis as priority indicators
- **Industry Precedent:** GitHub, GitLab, Notion use emojis as functional markers in technical documentation
- **Minimal Cost:** Token overhead is negligible compared to readability gains

**Decorative Emojis (FORBIDDEN in rule files):**

These serve no semantic purpose and reduce professionalism:

- ❌ **Celebratory:** 🎉🥳🎊 ("Great job!", "Let's go!")
- ❌ **Emphasis:** 💯💪👍 (except standard markers above)
- ❌ **Objects:** 🏗️🔨📊💾 (use descriptive words instead)
- ❌ **Faces:** 😀😎😅🤔 (unprofessional in technical documentation)
- ❌ **Redundant:** Multiple emojis expressing same concept (🔥💥⚡ for one priority)

**GIF Images (FORBIDDEN in rule files):**
- **Reasoning:** LLMs cannot interpret GIF animations (only see alt text)
- **Alternative:** Use code examples, ASCII diagrams, or external documentation links
- **Exception:** None - GIFs provide no semantic value to LLMs

**LLM-Generated Content Standards:**

**❌ FORBIDDEN:**
When LLMs generate code, documentation, or responses:
- **Default:** Must NOT generate emojis or GIFs in output
- **Professionalism:** Technical documentation should be emoji-free by default
- **Exception:** Only when user explicitly requests with phrases like:
  - "add emojis to make it friendly"
  - "use emojis for section headers"
  - "make it more engaging with emojis"
</directive_strength>

**Distinction:**
- **Rule files** (human-authored, machine-consumed): Functional semantic emojis ALLOWED
- **LLM outputs** (machine-generated, human-consumed): Emojis FORBIDDEN unless requested

**Example of Correct Usage in Rules:**

```markdown
## Priority Classification

🔥 **CRITICAL: Never commit secrets to version control**
- Immediate security vulnerability
- Can lead to data breach

⚠️ **WARNING: Avoid using SELECT * in production queries**
- Performance implications
- Wastes context window budget

✅ **RECOMMENDED: Use explicit column lists**
- Better performance
- Clear intent
```

**Example of Incorrect Usage:**

```markdown
## Let's Get Started! 🎉🎊

This is so cool! 😎 We're going to build amazing things! 💪🔥💯

Database design 🏗️ requires careful planning 🤔 and execution 🔨!
```

### Cross-Reference Standards
- **Format:** Use `@filename.md` or `**Rule Name**: \`filename.md\`` format
- **Validation:** Verify all cross-references point to existing files
- **Relationships:** Document logical dependencies between rules
- **Maintenance:** Update references when files are renamed or reorganized

## 5a. System Prompt Altitude

### The Goldilocks Zone

**From Anthropic Context Engineering:** System prompts must be written at the "right altitude" - a balance between brittle hardcoded logic and vague high-level guidance.

**Too Low Altitude (Brittle):**
```markdown
❌ Anti-Pattern: Hardcoded If-Else Logic
If user mentions "price", respond "Contact sales"
If user says "bug", create ticket
If query contains "how", search docs
If user says "thanks", say "welcome"
```
**Problems:**
- Fragile, doesn't generalize
- Requires constant maintenance for edge cases
- Breaks with natural language variations
- Creates rigid, robotic behavior

**Too High Altitude (Vague):**
```markdown
❌ Anti-Pattern: Overly General Guidance
Be helpful and provide good responses.
Try to understand user intent.
Do your best work.
```
**Problems:**
- No concrete signals for behavior
- Assumes shared context that doesn't exist
- Claude 4 won't "go beyond" without explicit instruction
- Lacks actionable heuristics

**Right Altitude (Goldilocks Zone):**
```markdown
✅ Correct Pattern: Specific Heuristics, Flexible Application
You are a technical support agent for ProductX.

## Responsibilities
- Answer technical questions using docs in <docs/>
- Escalate billing to sales team
- Create bug reports for reproducible errors

## Guidelines
- Be concise; users value quick answers
- Ask clarifying questions when ambiguous
- Cite specific doc sections
- Use create_ticket tool for confirmed bugs

## Constraints
- Don't promise unplanned features
- Don't provide pricing without sales approval
- Verify bugs before reporting
```
**Benefits:**
- Specific enough to guide behavior
- Flexible enough to handle variations
- Provides clear heuristics without brittleness
- Agent can adapt while following spirit of instructions

### Finding the Right Altitude for Rules

**Self-Test Questions:**
1. Would another engineer understand intended behavior from this guidance?
2. Does it provide clear heuristics without hardcoding every edge case?
3. Can the model adapt to variations while following the spirit?
4. Are success criteria explicit and measurable?

**Principle:** Give strong heuristics, not brittle if-else trees. Trust the model to apply principles to specific situations.

**Application to Rule Writing:**
- **Contract Section:** Be explicit about required steps, but don't enumerate every possible scenario
- **Key Principles:** Provide actionable heuristics that guide behavior
- **Anti-Patterns:** Show examples of wrong altitude with explanations
- **Validation:** Specify measurable success criteria, not vague "good enough"

### Tool Design Altitude

**Tool specifications also need right altitude:**

**Too Low (Over-Specified):**
```python
❌ Bad: Brittle parameter handling
def search(query: str, mode: int):
    """mode: 0=exact, 1=fuzzy, 2=semantic, 3=hybrid"""
    # Agent must memorize arbitrary codes
```

**Too High (Under-Specified):**
```python
❌ Bad: Vague tool purpose
def do_operation(data: str, operation: str):
    """Perform operation on data"""
    # What operations? What format?
```

**Right Altitude (Clear Contract):**
```python
✅ Good: Semantic, self-documenting
def search(
    query: str,
    mode: Literal["exact", "fuzzy", "semantic"] = "semantic"
) -> List[Result]:
    """Search with specified matching strategy.
    
    Args:
        query: Search terms
        mode: Match strategy - exact for literal, fuzzy for typo-tolerant, semantic for meaning-based
    """
```

## 6. Numbering and Organization

### Numbering Scheme
- **000-099:** Core Foundation (global, memory-bank, governance)
- **100-199:** Data Platform (Snowflake, databases)
- **200-299:** Software Engineering - Python
- **300-399:** Software Engineering - Shell Scripts
- **400-499:** [Reserved for future expansion]
- **500-599:** Data Science & Analytics
- **600-699:** Data Governance
- **700-799:** Business Intelligence
- **800-899:** Project Management
- **900-999:** Demo & Synthetic Data

### Subdomain Organization

**Letter Suffix Standard (Preferred for Multi-File Rule Families):**

When creating 3+ related rules covering subtopics of the same technology or framework, use letter suffixes to group them visually and conserve numeric space:

- **Base Rule:** `NNN-technology-core.md` (foundation rule for the technology)
- **Subtopic Rules:** `NNNa-technology-aspect1.md`, `NNNb-technology-aspect2.md`, etc.

**When to Use Letter Suffixes:**
- ✅ **Use letters** when you have 3+ related rules covering aspects/subtopics of ONE technology
- ✅ **Use letters** for framework-specific features (Streamlit, FastAPI modules, Cortex functions)
- ✅ **Use letters** to create visual clustering in file browsers
- ❌ **Don't use letters** for completely different technologies (use separate numbers)

**Examples:**
- **Streamlit Family (Best Practice):**
  - `101-snowflake-streamlit-core.md` (foundation)
  - `101a-snowflake-streamlit-visualization.md` (charts/maps)
  - `101b-snowflake-streamlit-performance.md` (caching/optimization)
  - `101c-snowflake-streamlit-security.md` (input validation/secrets)
  - `101d-snowflake-streamlit-testing.md` (AppTest/debugging)

- **Cortex Family:**
  - `114-snowflake-cortex-aisql.md` (AI SQL functions)
  - `114a-snowflake-cortex-agents.md` (agents)
  - `114b-snowflake-cortex-search.md` (search)
  - `114c-snowflake-cortex-analyst.md` (analyst)
  - `114d-snowflake-cortex-rest-api.md` (REST API)

- **FastAPI Family:**
  - `210-python-fastapi-core.md` (foundation)
  - `210a-python-fastapi-security.md` (auth/CORS)
  - `210b-python-fastapi-testing.md` (TestClient)
  - `210c-python-fastapi-deployment.md` (deployment)
  - `210d-python-fastapi-monitoring.md` (health checks/logging)

**Benefits:**
- **Visual Clustering:** Related rules group together in `ls` output and file browsers
- **Number Conservation:** Cortex uses 1 number (114) vs 5 numbers (114-118)
- **Logical Hierarchy:** Parent-child relationship visible in filename
- **Human UX:** Faster scanning and discovery for manual rule selection
- **Clear Intent:** Filename itself communicates relationship

**Decision Tree:**
```
Do you have 3+ related rules for the same technology?
├─ Yes → Use letter suffixes (NNN, NNNa, NNNb...)
└─ No  → Use sequential numbers

Are these rules subtopics of ONE technology?
├─ Yes → Use letter suffixes
└─ No  → Use separate number ranges
```

**Legacy Note:** Some existing rule families (created before this standard) still use sequential numbering. New rules should follow the letter suffix pattern. When adding new rules to existing families, consider migrating the entire family to letters for consistency.

## 7. Quality Assurance and Validation

### Investigation-First Protocol (REQUIRED - Anti-Hallucination)

**Priority:** 🔥 CRITICAL - Required in all rules to minimize hallucinations and ensure grounded responses.

**From Claude 4 Best Practices:**
> "Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering."

**Requirement:** Every rule must include investigation-first guidance in appropriate sections.

**Standard Investigation Block:**
```xml
> **⚠️ Investigation Required**  
> When applying this rule:
> 1. **Read referenced files BEFORE making recommendations**
> 2. **Verify assumptions against actual code/data**
> 3. **Never speculate about file contents or system state**
> 4. **If uncertain, explicitly state:** "I need to read [file] to provide accurate guidance"
> 5. **Make grounded, hallucination-free recommendations based on investigation**
>
> **Anti-Pattern:**
> ❌ "Based on typical patterns, this file probably contains..."
> ❌ "Usually this would be implemented as..."
>
> **Correct Pattern:**
> ✅ "Let me read the file first to give you accurate guidance."
> [reads file using appropriate tool]
> ✅ "After reviewing [file], I found [specific facts]. Here's my recommendation based on what I observed..."
```

**Application Guidelines:**
- **Always:** Include investigation-first blocks in rules that reference code, files, or system state
- **Mandatory:** Require verification before making claims about codebase structure
- **Critical:** Emphasize grounded responses over speculative answers
- **Claude 4 Specific:** This model excels at discovering state from filesystem - leverage this capability

### Content Validation Requirements
- **Accuracy:** All code examples must be syntactically correct and tested
- **Currency:** External documentation links must be current and authoritative
- **Completeness:** Required sections must be present and properly formatted
- **Uniqueness:** Avoid duplicating information across rules
- **Grounding:** All recommendations must be based on verified information, not speculation

### Review Process
- **Section Check:** Verify all mandatory sections are present
- **Cross-Reference Validation:** Confirm all rule references are accurate
- **External Link Verification:** Test that documentation links work
- **Example Testing:** Validate all code examples and commands

### Maintenance Responsibilities
- **Version Tracking:** Update version number and LastUpdated date for changes
- **Token Budget Review:** Review and update TokenBudget after significant content changes to reflect actual file size
- **Dependency Updates:** Update cross-references when related rules change
- **Content Pruning:** Remove outdated information and broken links
- **Scope Verification:** Ensure rules remain focused and don't overlap

## 8. Advanced LLM Features and Optimization

### Multi-Session State Management

**Purpose:** Enable rules to work effectively across multiple context windows (Claude 4.5 long-horizon reasoning).

**State Tracking Pattern:**
```markdown
## Multi-Session Workflow Support

<multi_session_guidance>
For complex tasks spanning multiple context windows:

**State Tracking Files:**
1. **progress.json** - Structured state (tests, completed tasks, blockers)
```json
{
  "completed_tasks": ["task1", "task2"],
  "current_focus": "task3",
  "tests_status": "passing",
  "context_window": 2
}
```

2. **session_notes.md** - Freeform progress notes
3. **Git commits** - Checkpoint tracking with semantic messages

**Session Continuity Protocol:**
```bash
# At session start (fresh context window):
cat progress.json          # Read structured state
git log --oneline -5       # Review recent work
cat session_notes.md       # Read freeform notes
```

**Session Handoff (before context limit):**
1. Save current state to memory tool (if available)
2. Commit work: `git commit -m "Session N checkpoint: [summary]"`
3. Update progress.json with next steps
4. Write concise notes in session_notes.md
</multi_session_guidance>
```

**Claude 4.5 Specific Guidance:**
- Model has exceptional state tracking capabilities
- Can discover state from filesystem when starting fresh
- Works best with incremental progress (few things at a time vs everything at once)
- Use tests in structured format (`tests.json`) for long-term iteration
- Create quality-of-life tools (`init.sh`) to start servers/tests gracefully

### Parallel Execution Guidance

**Purpose:** Optimize Claude 4's native parallel tool calling capabilities.

**Standard Parallel Execution Block:**
```xml
<parallel_execution_guidance>
When this rule requires multiple independent operations:

**Maximize Parallelization:**
- Read multiple files simultaneously (not sequentially)
- Execute independent validations in parallel
- Run parallel searches during research
- Avoid sequential operations when order doesn't matter

**Example:**
```python
# ❌ Sequential (slow)
file1 = read_file("a.md")
file2 = read_file("b.md")
file3 = read_file("c.md")

# ✅ Parallel (fast)
files = parallel_read(["a.md", "b.md", "c.md"])
```

**Sequential When Required:**
If step 2 depends on step 1 results, execute sequentially.
Do not use placeholders or guess missing parameters - wait for actual results.
</parallel_execution_guidance>
```

**Model Capabilities:**
- **Claude 4:** Excels at parallel execution, fires multiple operations simultaneously
- **GPT-4:** Supports parallel function calling
- **Gemini:** Supports parallel operations

### Model-Specific Guidance Blocks

**Purpose:** Provide optimized instructions for specific LLM models while maintaining universal compatibility.

**Format:**
```xml
> **🤖 Claude 4 Specific Guidance**  
> **Claude 4 Optimizations:**
> - Context awareness: You can track your remaining token budget
> - Be explicit: Request "above and beyond" behavior directly
> - Parallel tool calls: Maximize simultaneous operations
> - State discovery: Leverage filesystem state tracking

> **🤖 GPT-4 Specific Guidance**  
> **GPT-4 Optimizations:**
> - Token budget: Target <400 tokens per rule for GPT-3.5 compatibility
> - JSON mode: Use `response_format: { "type": "json_object" }` for structured output
> - Function calling: Define functions in separate schema

> **🤖 Gemini Specific Guidance**  
> **Gemini 1.5 Pro Optimizations:**
> - Massive context: Can handle comprehensive rules (>1000 tokens)
> - Native code execution: Leverage for validation examples
> - Multimodal: Include visual examples when relevant
```

**Degradation Strategy:**
- Models ignore guidance blocks for other models
- All guidance blocks are optional enhancements
- Core functionality works without model-specific blocks

## 9. Documentation & Validation
- **Always:** Include links to relevant, current product documentation for reference
- **Requirement:** Before finalizing any rule or code, verify syntax, best practices, and API usage against the linked docs
- **Requirement:** Reference official model documentation for model-specific guidance (Claude 4 Best Practices, OpenAI Prompt Engineering, Gemini documentation)

## 10. Change Workflow
- **Always:** When creating a new rule, include a clear `## Purpose` section and, when appropriate, a `## Key Principles` section with 3-7 concise bullet points summarizing core concepts
- **Mandatory:** When creating a new rule, include a `## Rule Type and Scope` section immediately after the Purpose section specifying the rule's type and scope
- **Mandatory:** When creating a new rule, include a complete `## References` section with both `### External Documentation` and `### Related Rules` subsections
- **Mandatory:** When creating a new rule, include `Version: 1.0` and `LastUpdated` with current date in YYYY-MM-DD format
- 🔥 **CRITICAL:** When creating a new rule, include `Keywords` metadata with 5-15 relevant keywords for semantic discovery (required in v2.4)
- **Mandatory:** When creating a new rule, declare `TokenBudget` and `ContextTier` in metadata
- **Mandatory:** When updating any rule file, increment the version number and update `LastUpdated` to the current date in YYYY-MM-DD format
- **Mandatory:** When updating any rule file, review and update `TokenBudget` to reflect current file size and content (use token budget tiers in Section 5 as guidance: ~150-250 for <150 lines, ~300-600 for 150-300 lines, ~700-1200 for 300-600 lines, ~1500+ for >600 lines)
- **Mandatory:** TokenBudget MUST be numeric with tilde prefix (e.g., ~450), never text labels like "small", "medium", or "large"
- **Always:** When refactoring, split oversized rules and remove content duplication
- **Always:** When creating or updating rules, verify compliance with emoji usage guidelines (standardized functional markers only: 🔥⚠️✅❌📊🆕)
- **Forbidden:** Decorative emojis, celebratory emojis, face emojis, or GIF images in rule files
- **Always:** Include guidance that LLM-generated outputs must be emoji-free unless user explicitly requests them
- **Always:** Validate Related Rules cross-references for accuracy and ensure they represent logical relationships
- **Always:** Before finalizing a rule, validate it against current, vendor-agnostic documentation and your primary IDE/tooling documentation for compliance (e.g., Visual Studio Code, Cursor, Claude Code, Gemini CLI, Cline)
- **Always:** For all agent interactions, follow the core rules in `000-global-core.md`

### Date Handling Protocol

**Critical Requirement:** Never hardcode dates when updating LastUpdated fields.

**🔥 MANDATORY:**
**Date Acquisition:**
- **CRITICAL:** Always obtain current date via system call: `date +%Y-%m-%d` (or equivalent)
- **Forbidden:** Never hardcode, guess, or assume today's date
- **Verification:** Before writing any LastUpdated date, verify it matches today's actual date from system
- **Format:** Use ISO 8601 date format: YYYY-MM-DD

**Anti-Pattern:**
```markdown
❌ BAD: Hardcoding or guessing the date
```
**Problem:** Hardcoded dates are frequently wrong, especially after context resets or when agent lacks current date awareness

**Correct Pattern:**
```bash
✅ GOOD: Get date from system
# First, get today's date from system
date +%Y-%m-%d
# Output: 2025-10-22

# Then use that value in the file
```
**Benefits:** Accurate dates; no guessing; verifiable; consistent

**Implementation Checklist:**
- [ ] Run `date +%Y-%m-%d` or equivalent system call
- [ ] Verify output matches expected format (YYYY-MM-DD)
- [ ] Use exact output value in LastUpdated field
- [ ] Never modify or adjust the date manually
- [ ] Cross-check: Does the date make sense for "today"?

**Model-Specific Guidance:**
- **Claude 4+:** Can execute terminal commands to get current date
- **GPT-4:** May need user to provide current date
- **Gemini:** Can access system date information
- **Fallback:** If unable to access system date, explicitly ask user for today's date

## 11. Rule Creation Template

Use this template when creating new rule files. Copy the entire template below and replace all placeholders with appropriate content:

```markdown
**Keywords:** [technology, concept, pattern, use-case] (comma-separated for semantic discovery)
**TokenBudget:** ~[number] (e.g., ~450, ~800, ~2000)
**ContextTier:** [essential | standard | comprehensive]

# Rule Title (Replace with Descriptive Title)

> **Section Metadata**  
> Token Budget: ~450 | Context Tier: standard | Priority: high

## Purpose
[1-2 sentences clearly explaining what this rule accomplishes and why it exists. Be explicit about expected behaviors - Claude 4 requires clear specifications.]

## Rule Type and Scope

- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Description of what the rule covers and applies to]

## Contract

**🔥 MANDATORY:**
- **Inputs/Prereqs:** [Required context, files, env vars]
- **Allowed Tools:** [List tools permitted for this rule]

**❌ FORBIDDEN:**
- **Forbidden Tools:** [List tools not allowed]

**🔥 MANDATORY:**
- **Required Steps:** [Ordered, explicit steps the agent must follow. Be explicit and specific - include "go beyond the basics", "use entire context budget", etc. when appropriate]
- **Output Format:** [Exact expected output format]
- **Validation Steps:** [Checks the agent must run to confirm success]

## Key Principles
- [Concise bullet point summarizing key concept]
- [Another essential principle or practice]
- [Additional core concepts as needed]

## 1. Detailed Section
[Comprehensive implementation details with explicit instructions]

## Anti-Patterns and Common Mistakes

**❌ Anti-Pattern 1: [Descriptive Name]**
```[language]
// Bad example showing what NOT to do
[Complete, runnable anti-pattern code]
```
**Problem:** [Specific issues this causes]

**✅ Correct Pattern:**
```[language]
// Good example showing the right approach
[Complete, runnable correct code]
```
**Benefits:** [Why this approach is better]

**❌ Anti-Pattern 2: [Another Common Mistake]**
[Description with example]

**✅ Correct Pattern:**
[How to do it right with example]

## Quick Compliance Checklist
- [ ] Item 1 (must be true before proceeding)
- [ ] Item 2 (specific verification check)
- [ ] Item 3 (actionable validation item)
- [ ] Item 4 (compliance requirement)
- [ ] Item 5 (final verification step)

## Validation
- **Success Checks:** [How to verify correct implementation]
- **Negative Tests:** [What should fail and how to detect failures]

> **⚠️ Investigation Required**  
> When applying this rule:
> 1. Read referenced files BEFORE making recommendations
> 2. Verify assumptions against actual code/data
> 3. Never speculate about file contents or system state
> 4. Make grounded, hallucination-free recommendations

## Response Template
    ```<LANG>
    [Minimal, copy-pasteable template showing expected output format]
    ```

## References

### External Documentation
- [Official Documentation](https://example.com/) - Description of the resource
- [Additional Resource](https://example.com/) - Another relevant external link
- [Model-Specific Docs](https://docs.claude.com/) - Reference for model-specific optimizations

### Related Rules
- **Core Rule Name**: `000-global-core.md`
- **Governance**: `002-rule-governance.md`

> **🤖 Claude 4 Specific Guidance**  
> **Claude 4 Optimizations:**
> - Context awareness: Model can track token budget
> - Be explicit: Request comprehensive behavior directly
> - Investigation-first: Model excels at filesystem discovery

> **Note:** Follow professional communication standards including:
> - Use standardized functional emoji markers (🔥⚠️✅❌📊🆕) for priority/pattern identification
> - Prohibit decorative emojis and GIF images
> - LLM-generated outputs must be emoji-free unless user explicitly requests them
```

## Quick Compliance Checklist
- [ ] Rule follows mandatory section structure (all 9+ required sections)
- [ ] Purpose clearly states what rule accomplishes and why
- [ ] 🔥 **Keywords metadata present with 5-15 relevant keywords (CRITICAL in v2.4)**
- [ ] TokenBudget declared as numeric value with tilde (e.g., ~450) and reflects current file size (~2 tokens per line)
- [ ] ContextTier declared in metadata and appropriate for file size
- [ ] XML tags used for semantic markup (section_metadata, directive_strength)
- [ ] Contract specifies inputs, tools, steps, output format, and validation with explicit instructions
- [ ] Anti-Patterns section included with 2-5 examples (CRITICAL for Claude 4)
- [ ] Investigation-First Protocol included (when rule references files/code)
- [ ] Compliance checklist has 5-10 actionable items
- [ ] Response template shows expected output format
- [ ] External documentation links are current and authoritative (include model-specific docs)
- [ ] Related rules cross-references are accurate
- [ ] Rule length is within guidelines (≤500 lines, target 150-300)
- [ ] Professional communication standards followed (explicit, no speculation)
- [ ] Emoji usage follows guidelines (only standardized functional markers: 🔥⚠️✅❌📊🆕)
- [ ] No decorative emojis or GIF images included
- [ ] LLM-generated content guidance includes emoji prohibition
- [ ] Version and LastUpdated metadata included
- [ ] Model-specific guidance blocks added (optional but recommended)

## Validation
- **Success Checks:** All required sections present; cross-references work; external links accessible; examples are syntactically correct
- **Negative Tests:** Rules missing required sections fail validation; broken cross-references cause confusion; outdated external links impede learning

## Response Template
```markdown
## Rule Analysis
- **Purpose:** [What the rule accomplishes]
- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Technology/domain coverage]
- **Dependencies:** [Required prerequisite rules]

## Implementation
[Rule content following required structure]

## Validation
- [ ] [Compliance checklist items]
```

## References

### External Documentation

**Anthropic Engineering Articles:**
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Comprehensive guide to context management, attention budgets, right altitude prompts, and optimization strategies
- [Writing Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) - Best practices for token-efficient tool design, clear contracts, and promoting efficient agent behaviors
- [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Progressive disclosure and skill-based agent architectures

**LLM Model Documentation:**
- [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Official prompt engineering guide for Claude 4.x models
- [Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Foundational prompt engineering techniques for all Claude models
- [Prompt Templates and Variables](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables) - Structured prompt patterns and variable usage
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) - Official OpenAI prompt engineering best practices
- [OpenAI API Best Practices](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api) - Best practices for GPT models
- [Gemini CLI Documentation](https://ai.google.dev/gemini-api/docs) - Google Gemini API and prompt engineering

**IDE and Agent Documentation:**
- [Cursor Documentation](https://docs.cursor.com/) - AI-powered code editor features and capabilities
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules) - Project rules and context management
- [Visual Studio Code Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) - Configure custom instructions for GitHub Copilot in VS Code
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/get-started/best-practices) - GitHub Copilot usage guidance and optimization tips
- [GitHub Copilot Personal Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-personal-instructions) - Configure personal custom instructions for GitHub Copilot
- [GitHub Copilot Repository Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) - Add custom instructions at the repository level
- [Cline Documentation](https://docs.cline.bot/) - Cline AI assistant features and rules

**Technical Writing and Standards:**
- [Technical Writing Guide](https://developers.google.com/tech-writing) - Google's comprehensive guide for clear technical documentation
- [Markdown Specification](https://spec.commonmark.org/) - Official CommonMark specification for consistent formatting
- [Documentation Best Practices](https://www.writethedocs.org/guide/) - Community guide for effective technical documentation
- [Professional Technical Writing](https://developers.google.com/tech-writing) - Google's technical writing standards and best practices
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax and formatting reference

### Related Rules
- **Global Core**: `000-global-core.md` - Foundational workflow and safety protocols
- **Memory Bank Universal**: `001-memory-bank.md` - Context continuity and session recovery
- **Context Engineering**: `003-context-engineering.md` - Attention budget and token efficiency strategies
- **Tool Design for Agents**: `004-tool-design-for-agents.md` - Token-efficient tool development patterns
