# Long-Horizon Task Strategies for AI Agents

> **CORE RULE**
>
> Strategies for managing context across long-running, multi-session agent tasks.
> Load when working on tasks that span multiple turns or sessions.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** long-horizon tasks, compaction, checkpointing, sub-agents, structured notes, multi-session, context compression, persistent memory, agent coordination
**TokenBudget:** ~2400
**ContextTier:** Medium
**Depends:** 003-context-engineering.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Strategies for managing context in long-horizon agent tasks: compaction protocols, structured note-taking for persistent memory, and sub-agent architectures for delegating and parallelizing work.

**When to Load This Rule:**
- Working on tasks spanning multiple sessions or many turns
- Context window approaching capacity limits
- Needing to delegate sub-tasks to specialized agents
- Maintaining persistent state across context resets
- Compacting context to preserve attention budget

## References

### Dependencies

**Must Load First:**
- `003-context-engineering.md` - Core context engineering principles (attention budget, progressive disclosure)
- `000-global-core.md` - Foundation for all rules

### Related Rules

- `001-memory-bank.md` - Structured documentation and context preservation
- `004-tool-design-for-agents.md` - Token-efficient tool development patterns

## Contract

### Inputs and Prerequisites

- Understanding of context engineering fundamentals (see `003-context-engineering.md`)
- Access to persistent storage (files, memory tools) for note-taking
- Sub-agent infrastructure available (if using Strategy 3)

### Mandatory

- Read tool, Write tool (for structured notes)
- Grep tool, Glob tool (for context exploration)
- memory.store / memory.retrieve (for persistent state)
- Sub-agent orchestration tools (for delegation patterns)

### Forbidden

- Letting context grow unbounded without compaction
- Losing critical state during context resets
- Running sub-agents without clear task boundaries

### Execution Steps

1. Identify task as long-horizon (multi-turn or multi-session)
2. Select appropriate strategy: compaction, structured notes, sub-agents, or a combination
3. Apply chosen strategy following patterns below
4. Monitor context usage and compact at 75% capacity
5. Persist critical state externally before context resets

### Output Format

- Session summary with objective, completed work, current state, and next steps
- Persistent notes in structured markdown (NOTES.md or memory.store)
- Sub-agent results as concise summaries with actionable deliverables

### Validation

**Pre-Task-Completion Checks:**
- Long-horizon strategy selected and documented
- Compaction triggers defined (75% capacity threshold)
- Persistent state storage identified

**Success Criteria:**
- Context stays within attention budget across all sessions
- No critical state lost during compaction or resets
- Sub-agent results are concise and actionable

### Error Recovery

- **Compaction loses critical detail:** Restore from persistent notes, re-read key files
- **Sub-agent returns irrelevant results:** Refine task description with tighter scope and explicit deliverables
- **Context reset without saving state:** Use file-based recovery, re-read recent outputs, reconstruct from version control

### Negative Tests

- Agent continues adding context beyond 75% without compacting - FAIL
- Sub-agent task has no clear deliverable or boundary - FAIL
- Session ends without updating persistent notes - FAIL
- Compaction summary omits active blockers or next steps - FAIL

### Post-Execution Checklist

- [ ] Long-horizon strategy selected and applied
- [ ] Context compacted at 75% capacity threshold
- [ ] Persistent state updated (notes or memory.store)
- [ ] Sub-agent tasks had clear boundaries and deliverables
- [ ] No critical state lost during session transitions
- [ ] Forward-focused summaries (next steps emphasized over history)

## Strategy Selection

Choose the strategy based on task characteristics:

- **Single session approaching limits** -- Strategy 1 (Compaction)
- **Multi-session, persistent state needed** -- Strategy 2 (Structured Notes)
- **Parallelizable decomposition possible** -- Strategy 3 (Sub-Agents)
- **Complex multi-session with parallelization** -- Combine all three

## Strategy 1: Compaction

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
- Recent files accessed (<=5)
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

## Strategy 2: Structured Note-Taking

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

**NOTES.md Recovery:** If persistent notes become corrupted or truncated: (1) re-read recent tool outputs to reconstruct state, (2) check git history for last-known-good version (`git log -1 NOTES.md`), (3) fall back to compaction of current context as emergency recovery.

## Strategy 3: Sub-Agent Architectures

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

**Sub-Agent Failure Handling:**
- **Timeout:** Retry with narrower scope (e.g., reduce from 3 files to 1)
- **Empty results:** Verify task description specificity, add concrete example of expected output
- **Crash:** Escalate to user with partial results and error context

## Combining Strategies

For complex multi-session tasks, combine all three strategies. Example — refactoring a 50-file codebase: use sub-agents for parallel file analysis, structured notes (NOTES.md) for cross-session state tracking, and compaction within each sub-agent session to keep individual contexts focused.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Accumulating Full Context

**Problem:** Keeping all intermediate results in context instead of summarizing.

```python
# WRONG: Context grows unbounded
context = []
for step in task_steps:
    result = execute(step)
    context.append(result)  # Full result, 10K+ tokens each
```

**Correct Pattern:**
```python
# CORRECT: Summarize and compress
context = []
for step in task_steps:
    result = execute(step)
    summary = summarize(result, max_tokens=500)
    context.append(summary)
```

### Anti-Pattern 2: No Checkpointing for Long Tasks

**Problem:** Losing all progress when a long task fails midway.

```python
# WRONG: No checkpoints
for i, item in enumerate(large_dataset):
    process(item)  # If fails at item 999, restart from 0
```

**Correct Pattern:**
```python
# CORRECT: Checkpoint progress
checkpoint = load_checkpoint() or {"last_index": 0}
for i, item in enumerate(large_dataset[checkpoint["last_index"]:]):
    process(item)
    save_checkpoint({"last_index": i + 1})
```
