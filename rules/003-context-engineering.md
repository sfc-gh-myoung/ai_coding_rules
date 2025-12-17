# Context Engineering for AI Agents

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** context engineering, attention budget, context rot, token efficiency, compaction, progressive disclosure, sub-agents, agentic search, system prompts, right altitude, long-horizon tasks, memory management, state tracking
**TokenBudget:** ~4750
**ContextTier:** Critical
**Depends:** rules/000-global-core.md

## Purpose
Establish comprehensive context engineering practices that treat context as a finite resource with diminishing returns, enabling AI agents to maintain focus, minimize context rot, and work effectively across long-horizon tasks through strategic context management.

## Rule Scope

Universal context management principles for all AI agents across all models (Claude, GPT, Gemini) and editors

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Treat context as finite resource** - Every token depletes attention budget (n² pairwise relationships)
- **Progressive disclosure** - Load summaries first, details on-demand (not everything at once)
- **Use sub-agents for complex tasks** - Split work into focused agents with minimal context each
- **Compact before context limits** - Summarize completed work, preserve critical details only
- **Agentic search over RAG** - Explore dynamically instead of pre-loading entire knowledge base
- **Right altitude system prompts** - Specific heuristics (not brittle if-else, not vague guidance)
- **Never load entire codebase** - Context rot degrades recall, use targeted file reading

**Quick Checklist:**
- [ ] Assess attention budget before adding context
- [ ] Prioritize high-signal, actionable information
- [ ] Use progressive disclosure (load details only when needed)
- [ ] Compact context when approaching limits
- [ ] Use sub-agents for multi-faceted tasks
- [ ] Maintain structured notes outside context window
- [ ] Validate context stays within attention budget

## Contract

<contract>
<inputs_prereqs>
Understanding of token budgets; awareness of context window limits; ability to prioritize information; access to memory/state management tools
</inputs_prereqs>

<mandatory>
All context-aware tools; memory tools; file reading tools; state tracking tools; compaction tools
</mandatory>

<forbidden>
Tools that blindly load entire codebases without filtering; tools that duplicate information unnecessarily
</forbidden>

<steps>
1. Assess available attention budget before adding context
2. Prioritize high-signal, actionable information over noise
3. Use progressive disclosure - load details only when needed
4. Apply compaction when approaching context limits
5. Employ sub-agents for complex, multi-faceted tasks
6. Maintain structured notes outside context window for long tasks
</steps>

<output_format>
Minimal, high-signal responses; structured state tracking; clear context summaries
</output_format>

<validation>
Context stays within attention budget; information is non-redundant; agent remains focused on task; compaction maintains fidelity
</validation>

<design_principles>
- **Context as Finite Resource:** Treat context like limited working memory - every token depletes attention budget
- **Context Rot:** As context grows, model's ability to recall specific information degrades (n² pairwise attention relationships)
- **Progressive Disclosure:** Load information hierarchically - summaries first, details on-demand
- **Right Altitude:** System prompts must balance between brittle hardcoded logic and vague high-level guidance
- **Token Efficiency:** Minimize context pollution - every token must provide actionable value
- **Agentic Search:** Prefer just-in-time exploration over pre-computed retrieval when information space is dynamic
- **Compaction Strategy:** Summarize and compress context before hitting limits while preserving critical details
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Loading Entire Codebase Upfront**
```python
# BAD: Blindly load everything
for file in all_python_files:
    content = read_file(file)
    context += content  # Now have 100K tokens!
```
**Problem:** Wastes attention budget on irrelevant code; causes context rot; slow and expensive

**Correct Pattern: Agentic Exploration**
```python
# GOOD: Explore targeted
1. grep "function_name" to find relevant files
2. Read only the 3 files found
3. Follow imports if needed
4. Keep context focused (≤10K tokens)
```
**Benefits:** Maintains attention focus; faster; more cost-effective

**Anti-Pattern 2: Never Compacting Context**
```markdown
[Turn 1: User asks question - 500 tokens]
[Turn 2: Assistant explores - 2000 tokens]
[Turn 3: User follows up - 500 tokens]
[Turn 4: Assistant explores more - 2000 tokens]
...
[Turn 50: Context is 50K tokens, model struggling]
```
**Problem:** Context rot sets in; relevant information lost in noise; performance degrades

**Correct Pattern: Proactive Compaction**
```markdown
[Turns 1-5: Work on feature A - compact to 1K summary]
[Turns 6-10: Work on feature B - compact to 1K summary]
[Turn 11: Both summaries in context - 2K total, model sharp]
```
**Benefits:** Maintains model performance; keeps attention focused

**Anti-Pattern 3: Vague System Prompts**
```xml
<system_prompt>
Be helpful and provide good code.
Try to understand what the user wants.
Do your best work.
</system_prompt>
```
**Problem:** No concrete signals; assumes shared context; Claude 4 won't "go beyond" automatically

**Correct Pattern: Right Altitude Instructions**
```xml
<system_prompt>
You are a Python backend engineer specializing in FastAPI.

## Post-Execution Checklist

- [ ] Context window usage monitored (not exceeding attention budget)
- [ ] High-signal, actionable information prioritized
- [ ] Progressive disclosure used (summaries before details)
- [ ] System prompts at "right altitude" (neither brittle nor vague)
- [ ] Redundant information eliminated
- [ ] Compaction strategy defined for long tasks
- [ ] Structured note-taking for persistent state
- [ ] Sub-agents considered for complex multi-faceted work
- [ ] Tool outputs are token-efficient
- [ ] Forward-focused (what's next vs what's done)
- [ ] Agentic search used when appropriate
- [ ] Context rot actively prevented

## Validation
- Code must pass: ruff check, ruff format, pytest
</system_prompt>
```
**Benefits:** Clear expectations; specific heuristics; concrete validation criteria

**Anti-Pattern 4: Storing Everything in Context**
```python
# BAD: Keep all history in context
conversation_history = []
for turn in session:
    conversation_history.append(turn)  # Growing forever
    send_to_model(conversation_history)
```
**Problem:** Linear growth until context limit; no pruning strategy

**Correct Pattern: Structured External Memory**
```python
# GOOD: Use persistent memory
memory.store("session_state", {
    "completed": ["task1", "task2"],
    "current": "task3",
    "blockers": []
})

# Keep only recent context
recent_turns = conversation_history[-3:]
state = memory.retrieve("session_state")
send_to_model(recent_turns + state)
```
**Benefits:** Bounded context; persistent state; scalable to long sessions

**Anti-Pattern 5: Premature Optimization**
```python
# BAD: Over-engineer before understanding need
build_vector_index()  # Not needed yet
build_graph_database()  # Overkill
implement_caching_layer()  # Premature
```
**Problem:** Complex infrastructure before validating need; maintenance burden

**Correct Pattern: Start Simple, Scale As Needed**
```python
# GOOD: Start with agentic search
# If it works well enough, keep it
# If bottleneck identified, then optimize

# Start: grep + read_file (simple, works)
# If slow: Add targeted caching
# If still slow: Consider indexing
```
**Benefits:** Avoid premature complexity; validate need first; iterative improvement

## Post-Execution Checklist

After applying context engineering principles:

- [ ] Context budget tracked throughout task execution
- [ ] Progressive disclosure used for large information sources
- [ ] System prompts written at appropriate altitude (not too low-level)
- [ ] Memory bank updated with learnings and patterns
- [ ] Token-efficient tools used where applicable
- [ ] Sub-agents or agentic search employed for complex research
- [ ] Context compaction performed when approaching limits
- [ ] High-signal information prioritized in context window

## Validation

**Success Checks:**
- Context usage stays within attention budget (< 80% recommended)
- Information retrieval is efficient (no redundant reads/searches)
- System prompts are maintainable and appropriate altitude
- Memory bank captures essential project context
- Task completed with minimal context overhead

**Negative Tests:**
- Context thrashing prevented (not re-reading same files repeatedly)
- Token budget not exceeded causing truncation
- Low-signal information excluded from context
- Prompt patterns generalized appropriately (not over-fitted to single examples)

**Performance Metrics:**
- Tokens per task completion (lower is better)
- Context window utilization (< 80% target)
- Information retrieval efficiency (cache hit rate)
- Task completion rate with bounded context

## Output Format Examples

```markdown
MODE: [PLAN|ACT]

Rules Loaded:
- rules/000-global-core.md (foundation)
- [additional rules based on task]

Analysis:
[Brief analysis of the requirement]

Task List:
1. [Specific task with clear deliverable]
2. [Another task with validation criteria]
3. [Final task with success metrics]

Implementation:
[Code/configuration changes following established patterns]

Validation:
- [x] Changes validated against requirements
- [x] Tests passing / linting clean
- [x] Documentation updated
```

## Rule Loading and Discovery

**Canonical Source:** See `RULES_INDEX.md` for the authoritative mapping of 
file extensions, keywords, and technologies to rule files. Always consult
RULES_INDEX.md rather than hardcoding rule discovery logic.

## Context Preservation Mechanism

**Primary Preservation Mechanism:**

Natural language markers (CRITICAL, CORE RULE, FOUNDATION RULE) are the primary
mechanism for context preservation. ContextTier metadata is secondary.

See `000-global-core.md`, section "Context Window Management Protocol" for full hierarchy.

## References

### External Documentation

**Anthropic Engineering Articles:**
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Comprehensive guide to context management, attention budgets, and optimization strategies
- [Writing Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) - Best practices for token-efficient tool design
- [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Progressive disclosure and skill-based agent architectures

**Claude Documentation:**
- [Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Foundational prompt engineering techniques
- [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Model-specific optimization guidance
- [Prompt Templates and Variables](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables) - Structured prompt patterns

**Additional Resources:**
- [Technical Writing Best Practices](https://developers.google.com/tech-writing) - Clear, efficient documentation
- [Documentation Systems](https://documentation.divio.com/) - Information architecture principles

### Related Rules
- **Global Core**: `000-global-core.md` - Foundational workflow and safety protocols
- **Memory Bank System**: `001-memory-bank.md` - Structured documentation for context continuity
- **Rule Governance**: `002-rule-governance.md` - Token budgets and rule sizing standards
- **Tool Design**: `004-tool-design-for-agents.md` - Token-efficient tool development patterns
- **AGENTS Workflow**: `AGENTS.md` - Rule discovery and operational protocols

## 1. Context vs Prompt Engineering

### The Evolution from Prompts to Context

**Prompt Engineering (Traditional):**
- Focus: Writing effective one-shot prompts
- Scope: System instructions, few examples
- Use Case: Single-turn classification, text generation
- Challenge: Static instructions for all scenarios

**Context Engineering (Modern):**
- Focus: Managing entire context state across multiple turns
- Scope: System instructions + tools + memory + message history + external data
- Use Case: Multi-turn agents, long-horizon tasks
- Challenge: Curating what enters limited context window at each inference step

**Key Difference:**
Context engineering is iterative - the curation phase happens **each time** we decide what to pass to the model, not just once when writing the system prompt.

## 2. Context as Finite Resource

### Attention Budget and Architectural Constraints

**The n² Problem:**
```
For n tokens in context:
- Pairwise relationships = n²
- Each new token creates relationships with all existing tokens
- Attention gets stretched thin across growing context
```

**Example:**
- 1,000 tokens = 1,000,000 pairwise relationships
- 10,000 tokens = 100,000,000 pairwise relationships
- 100,000 tokens = 10,000,000,000 pairwise relationships

**Context Rot:**
As context length increases, models experience:
- Reduced recall accuracy ("needle in haystack" degradation)
- Weakened attention to specific details
- Increased latency and cost
- Diminishing marginal returns per token

**Implication:**
Even with 200K+ context windows, thoughtful curation remains essential for optimal performance.

### Training Distribution Effects

Models have:
- More training examples with shorter sequences
- Fewer specialized parameters for long-range dependencies
- Position encoding adapted to handle extended contexts (with some degradation)

**Result:** Performance gradient rather than hard cliff - models remain capable at long contexts but show reduced precision.

## 3. System Prompts at "Right Altitude"

### The Goldilocks Zone

**Too Low (Brittle Hardcoded Logic):**
```xml
Anti-Pattern:
<system_prompt>
If user asks about pricing, say "Contact sales"
If user mentions bug, create JIRA ticket
If query contains "how to", search docs
If user says "thanks", respond "You're welcome"
</system_prompt>
```
**Problem:** Fragile, doesn't generalize, requires constant maintenance

**Too High (Vague High-Level Guidance):**
```xml
Anti-Pattern:
<system_prompt>
Be a helpful assistant. Provide good answers.
Do your best to help the user.
</system_prompt>
```
**Problem:** No concrete signals, assumes shared context, lacks specificity

**Right Altitude (Goldilocks Zone):**
```xml
Correct Pattern:
<system_prompt>
You are a customer support agent for SaaS product X.

## Core Responsibilities
- Answer technical questions using documentation in <docs/>
- Escalate billing issues to sales team
- Create bug reports when users describe reproducible errors

## Guidelines
- Be concise; users value quick answers
- Ask clarifying questions if request is ambiguous
- Cite specific doc sections when providing technical guidance
- Use <tool>create_ticket</tool> for confirmed bugs

## Constraints
- Do not promise features not in roadmap
- Do not provide pricing without sales approval
- Do not speculate about bugs - verify first
</system_prompt>
```
**Benefits:** Specific enough to guide behavior; flexible enough to handle variations; provides clear heuristics

### Finding the Right Altitude

**Ask yourself:**
1. Would another engineer understand the intended behavior from this prompt?
2. Does it provide clear heuristics without hardcoding every edge case?
3. Can the model adapt to variations while following the spirit of the instructions?

**Principle:** Give the model strong heuristics, not brittle if-else trees.

## 4. Context Curation Strategies

### What to Include

**MANDATORY:**
**High-Signal Information:**
- Current task objective and success criteria
- Essential domain knowledge for task
- Relevant code/data directly referenced in task
- Recent conversation context (2-3 turns)
- Active decisions blocking progress
- Tool specifications for available actions

### What to Exclude

**FORBIDDEN:**
**Low-Signal Noise:**
- Redundant information already stated
- Historical context no longer relevant
- Entire codebases (use targeted file reading)
- Verbose tool outputs after decisions made
- Completed tasks with no future dependencies
- Speculative information not yet needed

### Curation Guidelines

```markdown

## Context Prioritization Framework

**Critical (Always Include):**
- Active task objective
- Blocking issues/decisions
- Tool specifications
- Recent conversation (≤3 turns)

**Important (Include When Relevant):**
- Domain-specific knowledge
- Referenced files/data
- Active state/progress tracking
- Error messages requiring action

**Optional (Load On-Demand):**
- Historical context
- Detailed documentation
- Large code files
- Archived decisions

**Exclude (Remove/Don't Load):**
- Redundant information
- Completed work details
- Irrelevant tool outputs
- Stale context
```

## 5. Progressive Disclosure

### Hierarchical Information Loading

**Principle:** Don't load everything upfront - provide summaries first, details on-demand.

**Three-Tier Strategy:**

**Tier 1: Quick Start (Lines 1-30)**
- Primary objective
- Immediate next steps
- Critical constraints
- Validation criteria

**Tier 2: Context Overview (Lines 31-100)**
- Recent session summary
- Active decisions
- Current blockers
- Available resources

**Tier 3: Deep Details (On-Demand)**
- Full file contents
- Detailed documentation
- Historical context
- Comprehensive data

### Implementation Pattern

```markdown

## activeContext.md Structure

### Quick Start (Read First)
**Objective:** Implement user authentication with OAuth2
**Next Step:** Create login endpoint in auth.py
**Validation:** Test with curl command below

### Current Session
- Completed: Database schema migration
- In Progress: OAuth2 integration
- Blocked: Need client credentials from user

### Resources (Load As Needed)
- Main files: auth.py, models.py, config.py
- Documentation: @docs/oauth2-setup.md
- Tests: @tests/test_auth.py
```

**Agent Behavior:**
1. Read Quick Start to understand objective immediately
2. Check Current Session to know what's done and what's next
3. Load Resources only when needed for specific task

## 6. Agentic Search vs Pre-computed Retrieval

### When to Use Each Strategy

**Agentic Search (Just-In-Time Exploration):**

**Use When:**
- Information space is dynamic (changing codebase)
- Indices might be stale
- Exploration path depends on findings
- Query requires reasoning over results

**Example Pattern:**
```python
# Agent explores filesystem dynamically
1. grep "AuthService" to find references
2. Read files containing AuthService
3. Follow imports to find dependencies
4. Explore related files based on findings
```

**Benefits:**
- Always up-to-date information
- Adapts to discovered context
- No stale indices to maintain

**Trade-offs:**
- Slower than pre-computed retrieval
- Requires good tool design
- Needs clear heuristics for exploration

**Pre-computed Retrieval:**

**Use When:**
- Information space is static (documentation)
- Query patterns are predictable
- Speed is critical
- Content has clear semantic boundaries

**Example Pattern:**
```python
# Pre-indexed vector search
query = "how to implement OAuth2"
results = vector_db.search(query, limit=5)
context = "\n".join([r.content for r in results])
```

**Benefits:**
- Fast retrieval
- Handles large corpora efficiently
- Good for FAQ/documentation

**Trade-offs:**
- Can be stale if content changes
- May retrieve irrelevant context
- Less adaptive to discoveries

### Hybrid Strategy

**Recommended Pattern:**
1. Start with pre-computed retrieval for baseline context
2. Use agentic search for dynamic exploration
3. Let agent decide when to dig deeper

**Example:**
```markdown
1. Load CLAUDE.md (pre-computed: always relevant)
2. Use grep to find specific functions (agentic)
3. Read discovered files (agentic)
4. Follow imports as needed (agentic)
```

## 7. Long-Horizon Task Strategies

### Strategy 1: Compaction

**Purpose:** Summarize and compress context when approaching limits while preserving critical details.

**Compaction Pattern:**
```markdown

## When to Compact
- Context approaching 75% of window limit
- Repetitive tool outputs accumulating
- Historical conversation no longer relevant
- State can be summarized without loss

## What to Compact
1. Tool call history - Keep only recent/unique calls
2. Conversation history - Summarize older turns
3. Code exploration - Keep architectural decisions, discard raw outputs
4. Decisions made - Document outcome, remove deliberation

## What to Preserve
- Active task objectives
- Unresolved blockers
- Recent files accessed (≤5)
- Critical architectural decisions
```

**Implementation:**
```python
# Compaction prompt
"""
Summarize the conversation history, preserving:
1. Current objective and success criteria
2. Decisions made and their rationale
3. Active blockers or open questions
4. Files modified and key changes
5. Next steps

Discard:
- Redundant tool outputs
- Resolved issues
- Exploratory dead-ends
- Verbose explanations already understood
"""
```

**Example Compaction:**

**Before (1500 tokens):**
```
User: I need to add authentication
Assistant: I'll help you add authentication. Let me explore...
[reads auth.py - 200 lines]
[reads config.py - 150 lines]
[reads models.py - 300 lines]
Assistant: I found the auth module. It uses JWT...
User: Great, can you add OAuth2?
Assistant: Yes, let me check the dependencies...
[reads requirements.txt]
[searches for OAuth2 examples]
...
```

**After Compaction (300 tokens):**
```

## Session Summary
**Objective:** Add OAuth2 authentication to existing app
**Completed:**
- Explored auth system (JWT-based in auth.py)
- Verified dependencies (requirements.txt has oauth2 support)
**Current State:** Ready to implement OAuth2 endpoints
**Next Steps:** Create OAuth2 login endpoint in auth.py
**Key Files:** auth.py (main auth logic), config.py (settings), models.py (User model)
```

### Strategy 2: Structured Note-Taking

**Purpose:** Maintain persistent memory outside context window for long-running tasks.

**Pattern:**
```markdown

## NOTES.md (Persistent State)

### Session 1 (Jan 20)
- Implemented User model with email/password fields
- Added bcrypt hashing for passwords
- Created database migration

### Session 2 (Jan 21)
- Added JWT token generation in auth.py
- Created /login endpoint
- **TODO:** Add OAuth2 support (blocked on client creds)

### Session 3 (Jan 22)
- Received OAuth2 credentials
- **IN PROGRESS:** Implementing /oauth/login endpoint
- Challenge: Need to handle callback URL registration
```

**Agent Behavior:**
1. Read NOTES.md at session start
2. Understand project state from notes
3. Update NOTES.md with progress
4. Use notes to bridge context resets

**Tool Support:**
```python
# Memory tool (Anthropic Platform)
memory.store("oauth_progress", {
    "completed_tasks": ["user_model", "jwt_auth"],
    "current_focus": "oauth2_integration",
    "blockers": [],
    "next_steps": ["create_callback_handler", "test_oauth_flow"]
})

# Retrieve later
state = memory.retrieve("oauth_progress")
```

### Strategy 3: Sub-Agent Architectures

**Purpose:** Specialized agents handle focused tasks, return condensed summaries to coordinator.

**Pattern:**

Main Agent (Coordinator) delegates to:
1. **Sub-Agent 1:** Research OAuth2 patterns
   - Returns: 2K token summary
2. **Sub-Agent 2:** Implement authentication endpoints
   - Returns: 1K token summary + code
3. **Sub-Agent 3:** Write integration tests
   - Returns: 1K token summary + test results

**Benefits:**
- Each sub-agent has clean context window
- Detailed work stays isolated
- Main agent receives condensed results
- Parallelizable for complex tasks

**Implementation:**
```python
# Main agent delegates
research_summary = sub_agent_research(
    "Find OAuth2 best practices for FastAPI"
)
# Sub-agent uses 20K tokens exploring, returns 2K summary

implementation = sub_agent_implement(
    context=research_summary,
    task="Create OAuth2 endpoints following best practices"
)
# Sub-agent uses 30K tokens coding, returns 1K summary + code

# Main agent context: ~3K tokens (summaries only)
```

**When to Use:**
- Complex research requiring extensive exploration
- Multi-faceted tasks with clear boundaries
- Tasks benefiting from parallel execution
- When detailed work can be summarized concisely

## 8. Token Efficiency Guidelines

### Minimize Context Pollution

**MANDATORY:**
**Rules:**
1. **No Redundancy:** Each piece of information exists once
2. **Actionable Only:** Every token must enable progress
3. **Structured Over Prose:** Use lists, tables, bullets instead of paragraphs
4. **Reference Over Duplication:** Link to docs instead of copying
5. **Temporal Boundaries:** Separate current/recent/historical clearly
6. **Forward Focus:** Emphasize what's next, not what's done

### Tool Output Efficiency

**Tools should return:**
- Minimal necessary information
- Structured, parseable formats
- Clear success/failure signals
- Actionable error messages

**Tools should NOT return:**
- Verbose debug output
- Entire file contents when excerpt suffices
- Redundant confirmation messages
- Decorative formatting

### Context Budgets in Practice

**Memory Bank System (from 001-memory-bank.md):**
- Total context: ≤600 lines across all files
- Active context: ≤100 lines (most critical)
- Each file has specific size limit
- Aggressive pruning of outdated content

**Rule System (from 002-rule-governance.md):**
- Target: 150-300 lines per rule
- Maximum: 500 lines per rule
- Token budgets declared in metadata
- Composition over duplication

## 9. Context Engineering Workflow

### Standard Operating Procedure

```mermaid
flowchart TD
    Start[New Task] --> Assess[Assess Attention Budget]
    Assess --> Priority[Prioritize Information]
    Priority --> Load[Load High-Signal Context]
    Load --> Work[Perform Task]
    Work --> Check{Approaching Limit?}
    Check -->|No| Work
    Check -->|Yes| Compact[Apply Compaction]
    Compact --> Work
    Work --> Complete[Task Complete]
    Complete --> Document[Update Persistent State]
```

**Steps:**
1. **Assess Budget:** How much context window is available?
2. **Prioritize:** What information is essential for this task?
3. **Load:** Bring in high-signal context progressively
4. **Work:** Execute task with focused context
5. **Monitor:** Watch for context limits approaching
6. **Compact:** Summarize and compress when needed
7. **Document:** Update persistent memory for future sessions

## Your Approach
- Write production-ready code with error handling
- Include type hints and docstrings
- Follow project style in pyproject.toml
- Use async/await for I/O operations
- Add comprehensive test coverage

## Available Tools
- read_file: Read source files
- grep: Search codebase
- run_tests: Execute pytest

## Context Assessment
- **Attention Budget:** [Available context window]
- **Current Usage:** [Token count / percentage]
- **Priority Information:** [What must be in context]
- **Compaction Status:** [Needed / Not needed]

## Task Context
- **Objective:** [Clear goal]
- **Approach:** [Progressive disclosure / Agentic search / Sub-agents]
- **Key Files:** [Minimal set of relevant files]

## Next Steps
- [Actionable step 1]
- [Actionable step 2]
