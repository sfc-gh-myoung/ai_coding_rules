# Context Engineering for AI Agents

> **CRITICAL RULE**
>
> Treat context as a finite resource with diminishing returns.
> Load when managing context windows, preventing context rot, or working with long-horizon tasks.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** context engineering, attention budget, context rot, token efficiency, compaction, progressive disclosure, sub-agents, agentic search, system prompts, right altitude, long-horizon tasks, memory management, state tracking
**TokenBudget:** ~4550
**ContextTier:** Critical
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Comprehensive context engineering practices that treat context as a finite resource with diminishing returns. Covers attention budgets (n² pairwise relationships), context rot, progressive disclosure, sub-agent patterns, agentic search vs RAG, compaction strategies, and long-horizon task management.

**When to Load This Rule:**
- Managing context window efficiently
- Preventing context rot in long tasks
- Understanding attention budget trade-offs
- Implementing progressive disclosure patterns
- Working with long-horizon multi-session tasks
- Designing sub-agent workflows
- Compacting context before limits

## References

### Dependencies

**Must Load First:**
- `000-global-core.md` - Foundation for all rules, Context Window Management Protocol

### Related Rules

- `001-memory-bank.md` - Structured documentation and context preservation
- `002d-advanced-rule-patterns.md` - System prompt altitude and investigation-first
- `002c-rule-optimization.md` - Token budgets and optimization
- `003a-long-horizon-tasks.md` - Compaction, structured notes, sub-agent architectures
- `004-tool-design-for-agents.md` - Token-efficient tool development patterns

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
- Schema Definition: `schemas/rule-schema.yml` - v3.2 schema with context-optimized structures

## Contract

### Inputs and Prerequisites

- Understanding of token budgets
- Awareness of context window limits
- Ability to prioritize information
- Access to memory/state management tools

### Mandatory

- Read tool, Write tool (file access and modification)
- Grep tool, Glob tool (targeted code search and file discovery)
- memory.store / memory.retrieve (persistent state across sessions)
- Context window monitoring (attention budget tracking)
- Compaction prompts (context summarization when approaching limits)

### Forbidden

- Tools that blindly load entire codebases without filtering
- Tools that duplicate information unnecessarily
- Pre-loading entire knowledge bases (use agentic search)
- Never compacting context in long tasks

### Execution Steps

1. Assess available attention budget before adding context
2. Prioritize high-signal, actionable information over noise
3. Use progressive disclosure - load details only when needed
4. Apply compaction when approaching context limits
5. Employ sub-agents for complex, multi-faceted tasks
6. Maintain structured notes outside context window for long tasks

### Output Format

- Minimal, high-signal responses
- Structured state tracking
- Clear context summaries
- Token-efficient tool outputs

### Validation

**Pre-Task-Completion Checks:**
- Attention budget assessed
- High-signal information identified
- Progressive disclosure plan ready
- Compaction strategy defined (if long task)
- Sub-agent needs assessed

**Success Criteria:**
- Context stays within attention budget
- Information is non-redundant
- Agent remains focused on task
- Compaction maintains fidelity
- Forward-focused (what's next vs what's done)

### Error Recovery

- **Context window overflow:** Immediately compact by summarizing completed work, preserving only active objectives and blockers
- **Context rot detected (degraded recall):** Remove oldest conversation turns, re-state critical constraints at end of context
- **Lost state after compaction:** Restore from persistent notes (NOTES.md or memory.store), re-read key files identified in session summary
- **Sub-agent returns off-topic results:** Narrow task scope, add explicit deliverable format, provide example output

### Negative Tests

- Agent loads entire codebase without filtering - FAIL (violates attention budget)
- Context exceeds 75% capacity with no compaction plan - FAIL
- Redundant information appears in multiple places in context - FAIL (violates No Redundancy rule)
- System prompt is either fully hardcoded if-else logic or vague platitudes - FAIL (wrong altitude)
- Historical context kept when no longer relevant to active task - FAIL
- Long-horizon task proceeds without persistent state tracking - FAIL

### Post-Execution Checklist

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

## Design Principles

- **Context as Finite Resource:** Treat context like limited working memory - every token depletes attention budget
- **Context Rot:** As context grows, model's ability to recall specific information degrades (n² pairwise attention relationships)
- **Progressive Disclosure:** Load information hierarchically - summaries first, details on-demand
- **Right Altitude:** System prompts must balance between brittle hardcoded logic and vague high-level guidance
- **Token Efficiency:** Minimize context pollution - every token must provide actionable value
- **Agentic Search:** Prefer just-in-time exploration over pre-computed retrieval when information space is dynamic
- **Compaction Strategy:** Summarize and compress context before hitting limits while preserving critical details

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

## Core Responsibilities
- Write production-ready async endpoints
- Follow project style in pyproject.toml
- Include type hints and comprehensive error handling

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

## Context vs Prompt Engineering

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

## Context as Finite Resource

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

## System Prompts at Right Altitude

See `002d-advanced-rule-patterns.md` for System Prompt Altitude and Goldilocks Zone guidance (lines 127-209).

## Context Curation Strategies

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

## Progressive Disclosure

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

## Agentic Search vs Pre-computed Retrieval

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
1. Load PROJECT.md (pre-computed: always relevant)
2. Use grep to find specific functions (agentic)
3. Read discovered files (agentic)
4. Follow imports as needed (agentic)
```

## Long-Horizon Task Strategies

See `003a-long-horizon-tasks.md` for compaction protocols, structured note-taking, and sub-agent architecture patterns.

## Token Efficiency Guidelines

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
- Target: 200-400 lines per rule
- Maximum: 500 lines per rule
- Token budgets declared in metadata
- Composition over duplication

## Context Engineering Workflow

### Standard Operating Procedure

**Context Engineering Workflow:**
1. Assess attention budget for current context window
2. Prioritize high-signal information (rules, active code)
3. Load context progressively (foundation, then domain, then specialized)
4. Perform task with loaded context
5. If approaching 75% limit: Apply compaction protocol
   - Summarize completed work
   - Preserve active rules and current file
   - Return to step 4
6. Complete task with validation
7. Update persistent state (memory-bank if applicable)

**Detailed Steps:**
1. **Assess Budget:** How much context window is available?
2. **Prioritize:** What information is essential for this task?
3. **Load:** Bring in high-signal context progressively
4. **Work:** Execute task with focused context
5. **Monitor:** Watch for context limits approaching
6. **Compact:** Summarize and compress when needed
7. **Document:** Update persistent memory for future sessions
