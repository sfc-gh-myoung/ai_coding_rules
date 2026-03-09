# Tool Design for AI Agents

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** tool design, agent tools, token efficiency, tool parameters, function calling, tool overlap, tool contracts, error handling, minimal tool set, self-contained tools, LLM-friendly parameters, single responsibility
**TokenBudget:** ~4200
**ContextTier:** High
**Depends:** 000-global-core.md, 003-context-engineering.md

## Scope

**What This Rule Covers:**
Comprehensive tool design practices that maximize agent effectiveness. Covers single responsibility, token-efficient outputs, LLM-friendly parameters, clear contracts, minimal tool overlap, self-contained design, robust error handling, and patterns that promote efficient agent behaviors.

**When to Load This Rule:**
- Designing new tools for AI agents
- Evaluating existing tool effectiveness
- Understanding token-efficient tool outputs
- Creating clear tool contracts
- Minimizing tool overlap in tool sets
- Implementing LLM-friendly parameters

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **003-context-engineering.md** - Context management and attention budgets

**Related:**
- **002g-agent-optimization.md** - Agent-first design principles
- **002c-rule-optimization.md** - Token budgets and optimization
- **004a-tool-set-curation.md** - Minimal viable tool sets, when to split/merge tools
- **004b-tool-output-efficiency.md** - Token-efficient tool output design

### External Documentation

- **Claude Tool Use:** Anthropic documentation on function calling
- **OpenAI Function Calling:** GPT function calling best practices
- **Schema Definition:** `schemas/rule-schema.yml` - v3.2 schema with tool design principles

## Contract

### Inputs and Prerequisites

- Inventory of existing tools available to the agent
- Target agent's context window size (e.g., 128k tokens) and typical usage patterns
- Tool development framework or SDK (e.g., OpenAI function calling, Anthropic tool use)
- 003-context-engineering.md loaded for token budget principles

### Mandatory

- Python or equivalent language for tool implementation
- Agent testing harness (e.g., pytest with agent fixtures, eval framework)
- Token counter (e.g., tiktoken) for measuring output efficiency

### Forbidden

- Tools that create bloated, redundant tool sets without clear boundaries
- Verbose tool outputs that waste tokens
- Ambiguous parameter names
- Stateful tools that assume context memory

### Execution Steps

1. Design tool with clear, single responsibility
2. Define unambiguous parameters that play to LLM strengths
3. Implement token-efficient outputs (return only necessary information)
4. Create clear contracts (inputs, outputs, errors)
5. Ensure no overlap with existing tools
6. Test with actual agent to validate usability
7. Document tool purpose and usage patterns

### Output Format

Self-contained tools with:
- Clear specifications
- Token-efficient responses
- Structured error messages
- No hidden dependencies

### Validation

**Pre-Task-Completion Checks:**
- Tool purpose clearly defined (single responsibility)
- Parameters designed (semantic, unambiguous)
- Output format planned (token-efficient)
- Existing tools reviewed for overlap
- Contract documented (inputs, outputs, errors)

**Success Criteria:**
- Tool has single clear purpose
- Parameters are unambiguous
- Outputs are minimal and actionable
- No overlap with other tools
- Agent can use tool effectively
- Tool is self-contained and stateless

**Investigation Required:**
1. **Review existing tool set BEFORE adding new tools** - Check for overlap, identify gaps
2. **Test tool outputs for token efficiency** - Measure actual token counts
3. **Never assume tool behavior** - Run tools with test inputs to verify outputs
4. **Verify tool contracts match implementation** - Check parameter types, return values, error handling
5. **Make grounded recommendations based on investigated tool behavior** - Don't suggest tools without understanding their actual outputs

**Anti-Pattern:** "Based on typical tool design, this probably returns a JSON object..."

**Correct Pattern:** "Let me check the existing tools first to see if any handle this use case." [reviews tool specifications and tests relevant tools]

### Post-Execution Checklist

- [ ] Each tool has single, clear responsibility
- [ ] Tool names are descriptive (verb-noun pairs)
- [ ] No ambiguous overlap between tools
- [ ] Parameters are semantic and self-documenting
- [ ] Tool outputs are token-efficient (minimal necessary info)
- [ ] Clear contracts: inputs, outputs, errors documented
- [ ] Error messages are actionable and specific
- [ ] Tools promote efficient agent behaviors
- [ ] Minimal viable tool set (resist tool bloat)
- [ ] Tested with actual agent to validate usability
- [ ] No stateful tools that assume context memory
- [ ] Validation provides clear feedback for correction

### Error Recovery

- **Tool returns unexpected format:** Log the raw output, retry once, then surface error to user with the raw output attached
- **Tool timeout:** Retry with exponential backoff (max 3 attempts), then fail with actionable message including timeout duration
- **Tool not found at runtime:** Fall back to manual equivalent (e.g., bash command), warn user that tool is unavailable
- **Parameter validation failure:** Return specific field-level errors so agent can correct and retry without guessing

### Negative Tests

- Agent provides wrong parameter types -- tool returns clear type error, not stack trace
- Agent calls tool in wrong context -- tool explains why it cannot proceed and suggests correct tool
- Tool receives empty/null input -- tool returns descriptive validation error, not silent failure

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Bloated Tool Sets**
```python
# 50+ tools covering every edge case
get_user(), get_user_by_email(), get_user_by_name(), get_user_by_id()
search_users(), find_users(), lookup_users(), query_users()
create_user(), add_user(), register_user(), new_user()
# ... 40 more tools
```
**Problem:** Overwhelming; unclear which tool to use; lots of overlap

**Correct Pattern: Focused Minimal Set**
```python
# Small, clear tool set
get_user(identifier: str) -> User  # Works with ID, email, or username
search_users(query: str, limit: int = 10) -> List[User]
create_user(data: UserData) -> User
update_user(user_id: str, data: Partial[UserData]) -> User
delete_user(user_id: str) -> None
```
**Benefits:** Clear which tool to use; each has distinct purpose; easy to learn

**Anti-Pattern 2: Verbose Tool Outputs**
```python
def search(query: str) -> dict:
    return {
        "metadata": {
            "query": query,
            "timestamp": "2025-01-22T10:30:00",
            "duration_ms": 145,
            "api_version": "v2",
            "request_id": "req_12345"
        },
        "results": {
            "total_count": 42,
            "returned_count": 10,
            "has_more": true,
            "items": [...]  # Actual results buried
        }
    }
```
**Problem:** Wastes ~50 tokens on metadata; actual results obscured

**Correct Pattern: Minimal Output**
```python
def search(query: str, limit: int = 10) -> List[Result]:
    """Returns up to 'limit' results directly as list"""
    return results  # Just the results
```
**Benefits:** Token efficient; clear and direct; agent gets what it needs

**Anti-Pattern 3: Ambiguous Parameters**
```python
def process_data(data: str, mode: int, flags: str = ""):
    """Process data with mode and flags

    mode: 0=normal, 1=fast, 2=accurate, 3=balanced
    flags: Comma-separated options
    """
```
**Problem:** Agent must memorize arbitrary codes; unclear what flags are available

**Correct Pattern: Semantic Parameters**
```python
def process_data(
    data: str,
    priority: Literal["speed", "accuracy", "balanced"] = "balanced",
    preserve_formatting: bool = True,
    validate_output: bool = True
):
    """Process data with clear options"""
```
**Benefits:** Self-documenting; agent understands options; no memorization needed

**Anti-Pattern 4: Missing Error Context**
```python
def api_call(endpoint: str) -> dict:
    response = requests.get(endpoint)
    if not response.ok:
        raise Exception("API call failed")  # What failed? Why?
    return response.json()
```
**Problem:** Agent doesn't know what went wrong or how to fix it

**Correct Pattern: Actionable Errors**
```python
def api_call(endpoint: str) -> dict:
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise TimeoutError(
            f"API request to {endpoint} timed out after 30s. "
            f"The service may be slow or unavailable. Retry with longer timeout?"
        )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Endpoint {endpoint} not found. Check API documentation for correct path.")
        elif e.response.status_code == 401:
            raise AuthenticationError(f"API key invalid or missing. Set API_KEY environment variable.")
        else:
            raise APIError(f"API returned {e.response.status_code}: {e.response.text}")
```
**Benefits:** Agent knows exactly what happened; can take corrective action

**Anti-Pattern 5: Tools That Assume Context**
```python
# Bad: Assumes agent remembers previous results
def get_next_page() -> List[Result]:
    """Get next page of previous search"""
    # Which search? Agent might not remember
```
**Problem:** Stateful tools break when context resets; agent gets confused

**Correct Pattern: Stateless Tools**
```python
def search(query: str, page: int = 1, limit: int = 10) -> SearchResponse:
    """Search with explicit pagination.

    Returns:
        {
            "results": [...],
            "page": 1,
            "total_pages": 5,
            "has_next": true
        }
    """
```
**Benefits:** Explicit state; agent can resume after context reset; clear API

## Tool Design Fundamentals

### Single Responsibility Principle

**Each tool should:**
- Have one clear, focused purpose
- Do that one thing extremely well
- Not try to handle multiple disparate use cases

**Example:**

**Bad: Ambiguous Multi-Purpose Tool**
```python
def file_operation(path: str, operation: str, content: str = None):
    """Perform various file operations"""
    if operation == "read":
        return read_file(path)
    elif operation == "write":
        return write_file(path, content)
    elif operation == "delete":
        return delete_file(path)
    elif operation == "search":
        return search_in_file(path, content)
    # ... more operations
```
**Problem:** Unclear which operations exist; parameter meanings change; hard to document

**Good: Focused Single-Purpose Tools**
```python
def read_file(path: str) -> str:
    """Read and return the complete contents of a file."""

def write_file(path: str, content: str) -> None:
    """Write content to a file, overwriting if it exists."""

def search_file(path: str, pattern: str) -> List[Match]:
    """Search for pattern in file, return matching lines."""
```
**Benefits:** Clear purpose; unambiguous parameters; easy to understand and use

### Tool Naming Conventions

**Guidelines:**
- Use descriptive verb-noun pairs: `read_file`, `create_ticket`, `search_documents`
- Avoid vague names: `do_operation`, `handle_request`, `process_data`
- Be specific about scope: `search_github_issues` not just `search`
- Use consistent naming across related tools

**Examples:**
```python
# Good names
get_user_profile(user_id)
list_active_sessions()
create_database_backup(db_name)
send_email_notification(to, subject, body)

# Bad names
do_user_thing(id, action)  # Vague
data_ops(params)  # Unclear
handle(request)  # Too general
process()  # What does it process?
```

### Tool Boundaries and Overlap

**Critical Rule:** If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better. Boundary test: if 2 out of 3 engineers independently choose different tools for the same task, the tools have overlapping boundaries that must be resolved.

**Quantitative threshold:** If an agent selects the wrong tool >20% of the time for a given task category, the tool boundaries need redesign. Track selection accuracy during testing.

**Decision Framework:**
```
Is there exactly ONE obvious tool for this task?
- If Yes: Good tool boundaries
- If No: Refactor to eliminate ambiguity
```

**Example of Poor Boundaries:**

```python
# Overlapping tools - which to use?
def search_codebase(query: str):
    """Search for code matching query"""

def find_function(name: str):
    """Find function by name"""

def grep_files(pattern: str):
    """Grep for pattern in files"""
```
**Problem:** Three tools do similar things; unclear which to use when

**Example of Clear Boundaries:**

```python
# Clear, non-overlapping tools
def grep(pattern: str, path: str = ".") -> List[Match]:
    """Search for exact text pattern in files using ripgrep.
    Use for: Finding specific strings, class names, function calls"""

def codebase_search(semantic_query: str) -> List[Result]:
    """Semantic search for code by meaning, not exact text.
    Use for: Finding functionality when you don't know exact names"""
```
**Benefits:** Clear use cases; no overlap; agent knows which to use when

## Token Efficiency in Tool Outputs

Key principles for tool output design:

1. **Return only what the agent needs for its next decision** -- omit metadata, timestamps, and internal IDs unless requested
2. **Use structured formats (JSON/tables) over prose** -- agents parse structured data more reliably and with fewer tokens
3. **Implement progressive output for large results** -- return summary first, let agent request details on specific items

See **004b-tool-output-efficiency.md** for detailed guidance on minimal outputs, structured formats, and progressive output for large results.

## Parameter Design

### Play to LLM Strengths

**LLMs excel at:** Semantic understanding, natural language, contextual reasoning
**LLMs struggle with:** Arbitrary codes, complex nested structures, precise numerical values without context

**Good: Semantic, Self-Documenting Parameters**
```python
def create_task(
    title: str,
    priority: Literal["low", "medium", "high", "critical"],
    category: Literal["bug", "feature", "docs", "test"],
    description: str
):
    """Clear categorical parameters - agent understands options immediately"""

def send_notification(
    recipient_email: str,  # Clear what this is
    subject: str,
    message_body: str,
    include_timestamp: bool = True
)
```

**Bad: Opaque Parameters**
```python
def create_task(title: str, priority: int, category_code: str):  # What does 1 vs 2 mean? "BG" vs "FT"?
def send_notification(to: str, s: str, msg: str, ts: bool):  # Unclear abbreviations
```

### Parameter Validation

Validate inputs and provide clear, actionable errors:

```python
def search_date_range(start_date: str, end_date: str, resource_type: str):
    """Search resources within date range.
    
    Args:
        start_date: ISO format (YYYY-MM-DD)
        end_date: ISO format (YYYY-MM-DD)  
        resource_type: One of: "users", "posts", "comments"
    """
    if not validate_iso_date(start_date):
        raise ValueError(f"start_date must be ISO format (YYYY-MM-DD), got: {start_date}")
    if end_date < start_date:
        raise ValueError(f"end_date ({end_date}) must be after start_date ({start_date})")
    valid_types = ["users", "posts", "comments"]
    if resource_type not in valid_types:
        raise ValueError(f"resource_type must be one of {valid_types}, got: {resource_type}")
```

## Explicit Tool Specifications

Every tool must clearly specify:
1. **Purpose:** What it does (one sentence)
2. **Parameters:** Each parameter's type, meaning, constraints
3. **Returns:** What it returns (type and structure)
4. **Errors:** What exceptions it raises and when
5. **Side Effects:** Any state changes it causes

**Example Complete Specification:**

```python
def create_pull_request(
    title: str,
    description: str,
    source_branch: str,
    target_branch: str = "main",
    reviewers: List[str] = None
) -> Dict[str, Any]:
    """Create a pull request from source_branch to target_branch.

    Args:
        title: PR title (max 200 characters)
        description: PR description (markdown supported)
        source_branch: Branch containing changes
        target_branch: Branch to merge into (default: "main")
        reviewers: GitHub usernames to request review from

    Returns: {"pr_number": int, "url": str, "status": "open" | "draft"}

    Raises:
        ValueError: If title exceeds 200 chars
        BranchNotFoundError: If source_branch doesn't exist
        PermissionError: If user lacks permission

    Side Effects: Creates PR, notifies reviewers, triggers CI/CD
    """
```

### Error Handling Patterns

**Bad:** `raise Exception("Error")` or `raise ValueError("Invalid input")`

**Good:** Specific problem with remediation guidance:
```python
raise ValueError(
    f"source_branch '{source_branch}' does not exist. "
    f"Available branches: {', '.join(available_branches)}"
)
raise PermissionError(
    f"User '{username}' lacks 'repo:write' permission. "
    f"Contact repository administrator."
)
```

## Promoting Efficient Agent Behaviors

Tool design can encourage or discourage behaviors. Key principles:

- **Encourage targeted exploration over bulk loading** -- provide search/filter tools rather than "get all" tools
- **Support incremental work** -- allow running subsets (e.g., specific tests) rather than forcing all-or-nothing operations
- **Eliminate ambiguous decision points** -- either provide ONE tool per task or multiple tools with explicit "Use for:" distinctions in docstrings

See Anti-Patterns 1 and 5 above for detailed before/after examples.

## Testing Tool Usability

### Agent-Centric Testing

Test if agent can use the tool effectively:

1. Can agent discover when to use this tool?
2. Can agent provide correct parameters without documentation lookup?
3. Does agent understand the output?
4. Can agent handle errors gracefully?
5. Does tool guide agent toward efficient patterns?

### Iterate Based on Usage

Monitor agent mistakes to identify design issues:
- **Wrong parameter format repeatedly:** Parameter naming/docs unclear
- **Uses tool A when B is more appropriate:** Tool boundaries need clarification
- **Loads too much data:** Tool should have better filtering
- **Confused by error messages:** Error messages need improvement
