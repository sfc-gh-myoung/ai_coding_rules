# Advanced Rule Patterns: System Prompt Altitude & Complex Workflows

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.2
**LastUpdated:** 2026-01-13
**Keywords:** system prompt altitude, investigation-first, anti-patterns, multi-session workflows, parallel execution, advanced patterns, heuristics, goldilocks zone, context management, state management
**TokenBudget:** ~4300
**ContextTier:** Medium
**Depends:** 002-rule-governance.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Advanced patterns for writing rules that balance specificity with flexibility. Focuses on system prompt altitude (the "Goldilocks Zone"), investigation-first protocols, anti-pattern structures, multi-session workflows, and parallel execution design.

**When to Load This Rule:**
- Writing complex rules requiring advanced patterns
- Designing anti-pattern libraries
- Creating multi-step workflows with state management
- Understanding system prompt engineering for rules
- Avoiding common rule design pitfalls

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Schema requirements and standards
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002a-rule-creation.md** - Step-by-step rule creation workflow
- **002c-rule-optimization.md** - Token budgets and performance

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema
- **[CommonMark Spec](https://spec.commonmark.org/)** - Authoritative Markdown specification (nested code blocks must comply)

## Contract

### Inputs and Prerequisites

- Complex rule design task
- Understanding of system prompt engineering
- Knowledge of LLM limitations
- Familiarity with advanced rule patterns

### Mandatory

- Advanced pattern templates
- Anti-Pattern structure
- Investigation-First template
- Multi-session examples

### Forbidden

- Over-specifying with brittle if-else rules
- Vague general guidance without actionable heuristics
- Omitting investigation requirements for file/code references
- Assuming file contents without reading them first

### Execution Steps

1. Identify rule complexity level (simple vs advanced patterns needed)
2. Choose appropriate altitude for guidance (specific heuristics, flexible application)
3. Add Investigation-First blocks for file/code references
4. Structure Anti-Patterns with Problem/Correct pairs and explanations
5. Design multi-session state management if needed
6. Specify measurable validation criteria

### Output Format

Rule file with:
- System prompt altitude balance ("Goldilocks Zone")
- Investigation-First protocols for file references
- Anti-Patterns library with Problem and Correct examples
- Explicit state management for multi-session workflows

### Validation

**Pre-Task-Completion Checks:**
- Rule complexity level identified
- Altitude level chosen (not too low, not too high)
- Investigation blocks identified for file references
- Anti-Pattern structure planned
- Multi-session state management designed (if applicable)

**Success Criteria:**
- Another engineer can understand intended behavior from rule guidance
- Rules provide actionable heuristics without hardcoding edge cases
- Investigation Required blocks present for all file/code references
- Anti-Patterns show both Problem and Correct with explanations
- Multi-session workflows preserve state explicitly
- Success criteria are measurable (not vague "good enough")

**Negative Tests:**
- Brittle if-else rules fail with variations
- Vague guidance produces inconsistent behavior
- Missing investigation blocks lead to hallucinations
- Anti-Patterns without explanations don't teach principles
- Lost context between sessions causes rework

**Error Recovery:**
- **Tool timeout during investigation:** Retry with longer timeout, then report partial results with caveat
- **File not found during investigation:** Report missing file, suggest alternatives or ask user to provide path
- **State file corrupted:** Report corruption, offer to recreate from last known good state

### Post-Execution Checklist

- [ ] Rules provide clear heuristics without brittle if-else conditions
- [ ] System prompt altitude in "Goldilocks Zone" (not too low, not too high)
- [ ] Investigation Required blocks added for file/code references
- [ ] Anti-Patterns structured with Problem and Correct examples
- [ ] Multi-session workflows have explicit state management (STATE files or checklists)
- [ ] Parallel execution patterns used where applicable
- [ ] Success criteria are explicit and measurable
- [ ] Self-test questions passed (engineer understanding, clear heuristics, adaptability)

## System Prompt Altitude: The Goldilocks Zone

### What is System Prompt Altitude?

**Definition:** The level of specificity in instructions - finding the balance between too rigid (brittle if-else rules) and too vague (no actionable guidance).

**Goal:** Provide strong heuristics that guide behavior without hardcoding every edge case, allowing AI to adapt while following principles.

### Too Low Altitude (Brittle)

**Problem:** Over-specifying with exact conditions creates fragile rules that don't generalize.

[FAIL] **Anti-Pattern:**
```markdown
If user mentions "price", respond "Contact sales"
If user says "bug", create ticket
If query contains "how", search docs
If user says "thanks", say "welcome"
```

**Why It Fails:**
- Fragile, doesn't handle natural language variations
- Requires constant maintenance for edge cases
- Creates rigid, robotic behavior
- Breaks with synonyms or context shifts

### Too High Altitude (Vague)

**Problem:** General guidance without concrete signals for behavior.

[FAIL] **Anti-Pattern:**
```markdown
Be helpful and provide good responses.
Try to understand user intent.
Do your best work.
```

**Why It Fails:**
- No concrete signals for behavior
- Assumes shared context that doesn't exist
- Lacks actionable heuristics
- Agent won't "go beyond" without explicit instruction

### Right Altitude (Goldilocks Zone)

**Solution:** Specific heuristics with flexible application.

[PASS] **Correct Pattern:**
```markdown
You are a technical support agent for ProductX.

### Responsibilities
- Answer technical questions using docs in <docs/>
- Escalate billing to sales team
- Create bug reports for reproducible errors

### Guidelines
- Be concise; users value quick answers
- Ask clarifying questions when ambiguous
- Cite specific doc sections
- Use create_ticket tool for confirmed bugs

### Constraints
- Don't promise unplanned features
- Don't provide pricing without sales approval
- Verify bugs before reporting
```

**Why It Works:**
- Specific enough to guide behavior
- Flexible enough to handle variations
- Provides clear heuristics without brittleness
- Agent can adapt while following spirit of instructions

### Finding the Right Altitude

**Self-Test Questions:**
1. Would another engineer understand intended behavior from this guidance?
2. Does it provide clear heuristics without hardcoding every edge case?
3. Can the model adapt to variations while following the spirit?
4. Are success criteria explicit and measurable?

**Principle:** Give strong heuristics, not brittle if-else trees. Trust the model to apply principles to specific situations.

## Investigation-First Protocol

### When to Use

**MANDATORY for rules that reference:**
- Files, code, or system state
- Database schemas or data structures
- Configuration files or environment variables
- User-specific content or project structure

### Investigation Required Template

```markdown
> **Investigation Required**
> When applying this rule:
> 1. Read referenced files BEFORE making recommendations
> 2. Verify assumptions against actual code/data
> 3. Never speculate about file contents or system state
> 4. If uncertain, explicitly state: "I need to read [file] to provide accurate guidance"
> 5. Make grounded, hallucination-free recommendations based on investigation
>
> **Anti-Pattern:**
> "Based on typical patterns, this file probably contains..."
> "Usually this would be implemented as..."
>
> **Correct Pattern:**
> "Let me read the file first to give you accurate guidance."
> [reads file using appropriate tool]
> "After reviewing [file], I found [specific facts]. Here's my recommendation..."
```

### Example: Snowflake SQL Optimization Rule

```markdown
## Snowflake SQL Query Optimization

> **Investigation Required**
> Before optimizing queries:
> 1. Read the SQL file to understand current query structure
> 2. Check EXPLAIN output to identify actual bottlenecks
> 3. Review table schemas with DESCRIBE TABLE
> 4. Verify warehouse size and configuration
> 5. Never assume query patterns without reading the code

**MANDATORY:**
- **Read SQL file first** using Read tool
- **Check execution plan** with EXPLAIN before recommending changes
- **Verify table structures** exist before suggesting joins
- **Confirm assumptions** against actual schema
```

## Writing Effective Anti-Patterns

### Problem/Correct Pattern Pairs

**Format:** Always show both the Problem and Correct approach with explanations.

**Template:**
```markdown
## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: [Name]

[FAIL] **Problem: [Brief description]**
```markdown
[Example of incorrect code/approach]
```

**Why It Fails:**
- Reason 1
- Reason 2
- Reason 3

[PASS] **Correct Pattern:**
```markdown
[Example of correct code/approach]
```

**Why It Works:**
- Benefit 1
- Benefit 2
- Benefit 3
```

### Example: Contract Placement

````markdown
### Anti-Pattern: Late Contract Placement

[FAIL] **Problem: Contract after 500 lines**
```markdown
# Rule Title

### 1. Detailed Section
[300 lines]

### 2. Advanced Techniques
[200 lines]

### Task Requirements  <!-- Line 750! Too late! -->
- Inputs: ...
- Outputs: ...
```

**Why It Fails:**
- AI doesn't see requirements early
- Doesn't understand constraints before reading content
- Produces wrong outputs
- Misses validation steps

[PASS] **Correct Pattern (v3.2 - Markdown Headers):**
```markdown
# Rule Title

## Contract  <!-- Line 22! Early! -->

### Inputs and Prerequisites
What AI needs before starting

### Mandatory
Required tools and permissions

### Forbidden
Prohibited actions

### Execution Steps
1. Step 1
2. Step 2

### Output Format
Expected output description

### Validation
Success criteria

### Post-Execution Checklist
- [ ] Item 1

### 1. Detailed Section
[300 lines with AI understanding requirements]
```

**Why It Works:**
- AI reads requirements before implementation details
- Understands constraints early
- Produces correct outputs
- Follows validation steps
````

## Multi-Session State Management

### Problem: Lost Context Between Sessions

AI agents often work across multiple sessions (e.g., PR review, then implementation, then testing). Without explicit state management, context is lost.

### Solution: Explicit State Tracking

**Pattern:**
```markdown
## Multi-Session Workflow

**Session 1: Analysis**
- [ ] Read codebase structure
- [ ] Identify files requiring changes
- [ ] Document findings in /tmp/analysis_STATE.md
- **State to preserve:** File paths, current patterns, required changes

**Session 2: Implementation**
- [ ] Load /tmp/analysis_STATE.md from Session 1
- [ ] Apply changes per documented plan
- [ ] Update STATE with completed changes
- **State to preserve:** Modified files, test results

**Session 3: Validation**
- [ ] Load /tmp/analysis_STATE.md
- [ ] Run full test suite
- [ ] Generate report of coverage
```

### State Preservation Techniques

**Technique 1: State Files**
```markdown
**MANDATORY:**
After each major step:
1. Write state to /tmp/[workflow]_STATE.md
2. Include: completed steps, pending steps, key findings, file paths
3. Load state at start of next session
```

**Technique 2: Structured Checklists**
```markdown
**MANDATORY:**
Maintain checklist throughout workflow:
- [x] Step 1: Analysis complete (findings in Section 3)
- [x] Step 2: Implementation done (files: A, B, C)
- [ ] Step 3: Testing pending
- [ ] Step 4: Deployment pending
```

## Parallel Execution Patterns

### When to Use Parallel Execution

**Use parallel tool calls when:**
- Operations are independent (no dependencies)
- Data fetching from multiple sources
- Multiple file reads
- Batch validation checks

**Example:**
```markdown
**MANDATORY:**
When gathering data from multiple sources:
1. Use parallel tool calls for independent operations:
   - Read file A AND Read file B AND Query database C (parallel)
   - NOT: Read A, then Read B, then Query C (sequential)
2. Combine results after all operations complete
```

### Parallel vs Sequential Decision Tree

**Parallel (Recommended):**
- [PASS] Reading multiple unrelated files
- [PASS] Validating multiple independent rules
- [PASS] Fetching data from multiple APIs
- [PASS] Running multiple independent tests

**Sequential (Required):**
- [PASS] Step 2 depends on Step 1 output
- [PASS] File must be created before reading
- [PASS] Analysis results guide next action
- [PASS] Error handling requires sequential checks

## Tool Design Altitude

### Tool Specifications Need Right Altitude

[FAIL] **Too Low (Over-Specified):**
```python
def search(query: str, mode: int):
    """mode: 0=exact, 1=fuzzy, 2=semantic, 3=hybrid"""
    # Agent must memorize arbitrary codes
```

[FAIL] **Too High (Under-Specified):**
```python
def do_operation(data: str, operation: str):
    """Perform operation on data"""
    # What operations? What format?
```

[PASS] **Right Altitude (Clear Contract):**
```python
def search(
    query: str,
    mode: Literal["exact", "fuzzy", "semantic"] = "semantic"
) -> List[Result]:
    """Search with specified matching strategy.

    Args:
        query: Search term or phrase
        mode: Matching strategy
            - exact: Case-sensitive exact match
            - fuzzy: Handles typos, word order
            - semantic: Meaning-based search

    Returns:
        List of results ranked by relevance
    """
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Premature Rule Abstraction

**Problem:** Creating abstract, highly generalized rules before understanding concrete use cases, or extracting patterns from a single example.

**Why It Fails:** Abstract rules lack actionable guidance. Agents can't apply vague principles to specific situations. Rules become "wisdom" that sounds good but doesn't help execution.

**Correct Pattern:**
```markdown
# BAD: Premature abstraction
"Always consider the trade-offs between different approaches"
"Use appropriate error handling for the context"

# GOOD: Concrete then abstract
## Specific Pattern (from real use cases)
When catching database exceptions in FastAPI:
1. Log full traceback with structlog
2. Return HTTPException(500) with correlation_id
3. Never expose internal error details to client

## Generalized Principle (after 3+ concrete examples)
Error handling should: log details internally, return safe messages externally
```

### Anti-Pattern 2: Over-Engineering Multi-Session State

**Problem:** Creating complex state management systems with multiple STATE files, version tracking, and elaborate recovery protocols for simple workflows.

**Why It Fails:** Adds cognitive overhead without benefit. Simple tasks become bureaucratic. State files become stale faster than they're useful, and maintenance burden exceeds value.

**Correct Pattern:**
```markdown
# BAD: Over-engineered state for simple task
STATE_v3_checkpoint_2024-01-15.json
STATE_recovery_log.md
STATE_session_handoff.yml

# GOOD: Minimal state for task complexity
# Simple task (1-2 sessions): Use activeContext.md only
# Medium task (3-5 sessions): Add task-specific checklist
# Complex task (5+ sessions): Consider dedicated STATE.md
```

## Output Format Examples

### Example 1: Investigation-First Pattern in Python Rule

```python
# Example: Adding investigation block to Python refactoring rule

def refactor_with_investigation(file_path: str):
    """
    Refactor Python code following investigation-first protocol.

    Steps:
    1. Read file to understand current structure
    2. Analyze dependencies and imports
    3. Apply refactoring with verified assumptions
    """
    # Step 1: Investigation Required
    with open(file_path, 'r') as f:
        current_code = f.read()

    # Step 2: Verify assumptions
    imports = extract_imports(current_code)
    function_signatures = extract_signatures(current_code)

    # Step 3: Apply refactoring with facts
    refactored = apply_changes(current_code, imports, function_signatures)

    return refactored
```

### Example 2: System Prompt Altitude

```markdown
## Snowflake SQL Optimization

### Guidelines (Right Altitude)
- Prefer CTEs over subqueries for readability
- Use QUALIFY for window function filtering
- Cluster tables by frequently filtered columns
- Partition large tables by date when querying recent data
- Monitor warehouse credit usage with QUERY_HISTORY

### Constraints
- Don't use SELECT * in production queries
- Don't create tables without explicit clustering keys
- Verify query execution plan before deploying changes
```

### Example 2: Investigation-First

```markdown
## Python Code Refactoring

> **Investigation Required**
> Before refactoring:
> 1. Read the Python file to understand current structure
> 2. Check test files to understand expected behavior
> 3. Verify import statements and dependencies
> 4. Never assume function signatures without reading code
> 5. Confirm refactoring won't break existing tests

**MANDATORY:**
- Read file with Read tool first
- Check tests exist: `grep -r "test_" tests/`
- Run tests before and after changes
```

## Multi-File Task Patterns

### Atomic Changes (Single ACT Session)

Use when files are tightly coupled and changes must be consistent:
- Refactoring that renames functions/classes across files
- Updating API contracts (client + server)
- Schema migrations (DDL + application code)

**Task List Format:**
```
1. Update function signature in `auth.py`
2. Update all call sites in `middleware.py`
3. Update route handlers in `routes.py`
4. Run validation suite (all files)
```

**Rollback Strategy:**

If validation fails, you MUST:
- Revert ALL files to original state
- Return to PLAN mode
- Present revised task list with fixes

**Rollback Mechanisms:**
- **Git repo available (preferred):** Use `git checkout -- <file>` or `git stash`
- **No git, few files:** Store original content in-memory before edit, restore via write tool
- **No git, many files:** Read and store each file before editing; revert individually on failure

**Selection:** Check git availability first (`git status`). If unavailable, use in-memory for simple tasks or incremental for multi-file changes.

**Rollback Reporting:**
```markdown
WARNING: Validation failed. Reverting changes:
- Reverted: `auth.py` (original restored)
- Reverted: `middleware.py` (original restored)
- Unchanged: `routes.py` (not yet modified)

MODE: PLAN
[Revised task list with fixes]
```

### Progressive Changes (Multiple ACT Sessions)

Use when files are loosely coupled:
- Adding independent features to different modules
- Updating documentation across multiple files
- Performance optimizations in separate components

**Task List Format:**
```
Session 1: Update `auth.py`
- [specific changes]
- [validation]
- [await "ACT"]

Session 2: Update `middleware.py`
- [specific changes]
- [validation]
- [await "ACT"]
```

## Importance Marker Inheritance

When splitting rules (e.g., 100-snowflake-core.md into 100a, 100b, 100c):

- Parent rule keeps original marker (CORE/FOUNDATION)
- Child rules inherit same marker if they're core dependencies
- Child rules use no marker if they're specialized topics

Example:
- `200-python-core.md` - CORE RULE (parent)
- `201-python-lint-format.md` - CORE RULE (core dependency)
- `206-python-pytest.md` - no marker (specialized testing rule)
