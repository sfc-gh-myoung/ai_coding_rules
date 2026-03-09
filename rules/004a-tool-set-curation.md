# Tool Set Curation for AI Agents

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** tool set curation, minimal viable tool set, tool splitting, tool merging, tool overlap, tool bloat, tool boundaries
**TokenBudget:** ~1550
**ContextTier:** Medium
**Depends:** 004-tool-design-for-agents.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Curating minimal viable tool sets for AI agents. Covers deciding the right number of tools, when to split complex tools into focused ones, when to merge related tools for efficiency, and maintaining clear tool boundaries.

**When to Load This Rule:**
- Evaluating whether a tool set has too many or too few tools
- Deciding whether to split a complex tool or merge related tools
- Auditing an existing tool set for bloat or gaps
- Designing a new tool set from scratch

## References

### Dependencies

**Must Load First:**
- **004-tool-design-for-agents.md** - Core tool design principles
- **000-global-core.md** - Foundation for all rules

**Related:**
- **004b-tool-output-efficiency.md** - Token-efficient tool outputs

## Contract

### Inputs and Prerequisites

- An existing or planned set of tools for an AI agent
- Understanding of the agent's core use cases
- Access to tool specifications or source code

### Mandatory

- Tool inventory (list of current or planned tools)
- Use case mapping (which tasks the agent must perform)

### Forbidden

- Adding tools without identifying a clear gap in existing capabilities
- Keeping redundant tools that overlap in purpose

### Execution Steps

1. Identify core capabilities the agent needs
2. Design a minimal tool for each capability
3. Check for overlap between tools, then eliminate ambiguity
4. Resist adding "nice to have" tools without proven need
5. Validate coverage with actual agent usage
6. Add tools only when a clear gap is identified through testing

### Output Format

A curated tool set with clear boundaries between each tool and documented rationale for splits or merges.

### Validation

**Pre-Task-Completion Checks:**
- Each tool has a distinct, non-overlapping purpose
- The tool set covers all required agent capabilities
- No "nice to have" tools without proven need

**Success Criteria:**
- Agent can unambiguously select the right tool for any task
- Tool set is minimal while covering all use cases
- No two tools serve the same purpose

### Post-Execution Checklist

- [ ] Each tool has a distinct, non-overlapping purpose
- [ ] Tool set covers all required agent capabilities
- [ ] No redundant tools remain after curation
- [ ] Split/merge decisions documented with rationale
- [ ] Validated with actual agent usage

### Error Recovery

- **Curation removes a needed tool:** Add it back and mark as "required" to prevent future removal
- **Splitting creates >20 total tools:** Re-evaluate whether the split was justified or if split tools should share a namespace
- **Agent can't complete task after curation:** Identify the missing capability, add the minimal tool to cover it, then re-validate

### Negative Tests

After curation, the agent should NOT:
- Hesitate between two tools for the same task
- Call two tools when one would suffice
- Fail a task due to missing capability in the tool set

## Minimal Viable Tool Set

**Principle:** Provide the smallest set of tools that covers all necessary use cases. Follow the Execution Steps above.

**Tool count guidance:** 5-12 tools -- lean and focused. 13-20 tools -- review for overlap. 20+ tools -- audit required, likely bloated.

**Example Minimal Set for Code Repository:**

```python
# Core file operations
read_file(path: str) -> str
write_file(path: str, content: str) -> None

# Code exploration
grep(pattern: str, path: str = ".") -> List[Match]
list_directory(path: str) -> List[str]

# Validation
run_tests(pattern: str = None) -> TestResults
check_lints() -> LintResults

# Git operations
git_status() -> Status
git_diff(file: str = None) -> Diff
```

**Why This Works:**
- 8 focused tools cover most needs
- Each has clear, non-overlapping purpose
- Agent can combine tools for complex tasks
- Easy to understand and document

## When to Split Tools

**Split a tool when:**
- It has multiple distinct use cases
- Parameters become complex or ambiguous
- Error handling diverges
- Output formats differ significantly

**Example:**

```python
# Before: One complex tool
def file_operation(path, operation, content=None, lines=None, append=False):
    if operation == "read":
        if lines:
            return read_lines(path, lines)
        return read_full(path)
    elif operation == "write":
        if append:
            return append_to_file(path, content)
        return write_file(path, content)
    # Gets complex fast...

# After: Clear, focused tools
def read_file(path: str) -> str:
    """Read entire file"""

def read_lines(path: str, start: int, end: int) -> str:
    """Read specific line range"""

def write_file(path: str, content: str) -> None:
    """Write/overwrite file"""

def append_to_file(path: str, content: str) -> None:
    """Append to existing file"""
```

## When to Merge Tools

**Merge tools when:**
- They always get used together
- They operate on same data or resource
- Separate calls waste tokens on redundant context

**Example:**

```python
# Before: Always used together
user = get_user(user_id)  # API call 1
preferences = get_user_preferences(user_id)  # API call 2
settings = get_user_settings(user_id)  # API call 3

# After: One comprehensive call
user_data = get_user_profile(user_id)  # Returns user + prefs + settings
```

**Decision criteria:** Merge when tools share 3+ parameters AND are called together >80% of the time. Split when a tool has >4 distinct use cases OR >6 parameters. Otherwise, keep as-is.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Too Many Similar Tools

**Problem:** Providing multiple tools that do nearly the same thing, confusing the agent.

```python
# WRONG: Overlapping tools
tools = [
    "read_file",
    "get_file_contents",
    "load_file",
    "fetch_file_data"
]
```

**Correct Pattern:**
```python
# CORRECT: Single clear tool per action
tools = [
    "read_file"  # One tool for file reading
]
```

### Anti-Pattern 2: Tools Without Clear Boundaries

**Problem:** Tools with ambiguous or overlapping responsibilities.

```python
# WRONG: Unclear when to use each
def process_data(data): ...
def handle_data(data): ...
def manage_data(data): ...
```

**Correct Pattern:**
```python
# CORRECT: Clear, distinct purposes
def validate_data(data): """Check data format and constraints"""
def transform_data(data): """Convert data to target format"""
def store_data(data): """Persist data to database"""
```
