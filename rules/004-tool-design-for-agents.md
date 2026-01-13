# Tool Design for AI Agents

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** tool design, agent tools, token efficiency, tool parameters, function calling, tool overlap, tool contracts, error handling, minimal tool set, self-contained tools, LLM-friendly parameters, single responsibility
**TokenBudget:** ~5800
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

### External Documentation

- **Claude Tool Use:** Anthropic documentation on function calling
- **OpenAI Function Calling:** GPT function calling best practices
- **Schema Definition:** `schemas/rule-schema.yml` - v3.2 schema with tool design principles

## Contract

### Inputs and Prerequisites

- Understanding of agent capabilities
- Knowledge of token budgets
- Awareness of LLM strengths/weaknesses
- Access to tool development framework

### Mandatory

- All development tools
- Testing frameworks
- Agent evaluation tools

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

### Design Principles

- **Self-Contained:** Each tool does one thing well, with no hidden dependencies
- **Minimal Overlap:** Clear boundaries between tools; no ambiguity about which tool to use
- **Token Efficient:** Return only necessary information; avoid verbose outputs
- **Clear Contracts:** Inputs, outputs, and errors explicitly specified
- **LLM-Friendly Parameters:** Descriptive parameters that play to semantic understanding
- **Promote Good Patterns:** Tool design guides agents toward efficient behaviors
- **Robust Error Handling:** Clear, actionable error messages
- **Minimal Viable Set:** Curate smallest set of tools that covers use cases

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

**Critical Rule:** If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better.

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

### Return Only Necessary Information

**Principle:** Every token in a tool response depletes the agent's attention budget. Return the minimal set of information needed to make progress.

**Anti-Pattern: Verbose Outputs**
```python
def read_file(path: str) -> dict:
    return {
        "success": True,
        "message": "File read successfully",
        "file_path": path,
        "file_size": 1024,
        "last_modified": "2025-01-22T10:30:00",
        "encoding": "utf-8",
        "line_count": 50,
        "content": "..."  # Actual content buried in metadata
    }
```
**Problem:** Wastes ~100 tokens on metadata; actual content is obscured

**Correct Pattern: Minimal Necessary Output**
```python
def read_file(path: str) -> str:
    """Read file and return contents directly.

    Returns: File contents as string
    Raises: FileNotFoundError if file doesn't exist
    """
    return file_contents  # Just the content, nothing else
```
**Benefits:** Agent gets what it needs; no token waste; clear and direct

### Structured, Parseable Formats

**When returning data, use formats that are:**
- Easy for LLMs to parse
- Consistent across similar tools
- Minimal while complete

**Examples:**

**For Search Results:**
```python
# Good: Structured, minimal
{
    "matches": [
        {"file": "auth.py", "line": 42, "text": "def login(user):"},
        {"file": "views.py", "line": 15, "text": "def login_view(request):"}
    ]
}

# Bad: Verbose, redundant
{
    "search_results": {
        "query": "login",  # Agent already knows this
        "timestamp": "2025-01-22T10:30:00",  # Unnecessary
        "total_matches": 2,  # Can count matches array
        "execution_time_ms": 145,  # Usually irrelevant
        "matches": [...]
    }
}
```

**For File Operations:**
```python
# Good: Success is silent
def write_file(path: str, content: str) -> None:
    # No return value if successful
    # Raises exception if error

# Bad: Verbose confirmation
def write_file(path: str, content: str) -> dict:
    return {
        "status": "success",
        "message": "File written successfully",
        "bytes_written": len(content),
        "file_path": path
    }
```

### Progressive Output for Large Results

**For potentially large outputs, provide mechanisms to limit results:**

```python
def search_documents(
    query: str,
    limit: int = 10,  # Default to reasonable limit
    fields: List[str] = ["title", "summary"]  # Not full content
) -> List[Dict]:
    """Search documents with result limiting.

    Args:
        query: Search terms
        limit: Max results to return (default 10)
        fields: Which fields to include in results

    Returns: List of matching documents with specified fields
    """
```

**Benefits:**
- Agent can start with summaries
- Load full content only if needed
- Prevents context overflow

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

### Guide Agents Toward Good Patterns

**Tool design can encourage or discourage certain behaviors:**

**Example: Discouraging Blind Loading**

```python
# Bad: Encourages loading everything
def get_all_files() -> List[str]:
    """Return contents of all files in repository"""
    # Agents will use this and waste context

# Good: Encourages targeted exploration
def search_files(pattern: str, file_type: str = None) -> List[Match]:
    """Search for pattern in specific files.

    Encourages agent to search first, then read matches.
    """

def read_file(path: str) -> str:
    """Read a specific file by path.

    Requires agent to know which file to read.
    """
```

**Example: Encouraging Incremental Work**

```python
# Good: Supports incremental progress
def run_tests(test_pattern: str = None) -> TestResults:
    """Run specific tests or all tests.

    Args:
        test_pattern: Optional pattern to run subset (e.g., "test_auth*")

    Allows agent to run relevant tests without full suite.
    """

# Bad: Forces all-or-nothing
def run_all_tests() -> TestResults:
    """Run entire test suite (may take 10 minutes)"""
    # Agent hesitates to validate changes
```

### Avoid Ambiguous Decision Points

**If there are multiple ways to accomplish something, either:**
1. Provide ONE clear tool for the task
2. Provide multiple tools with CLEAR use case distinctions

**Bad: Ambiguous Tools**
```python
def search_api(query: str, mode: str = "auto"):
    """Search using best mode automatically"""
    # What does "auto" mean? When does it pick what?

def search_api_fast(query: str):
    """Fast search (less accurate)"""
    # When should agent use this vs regular search?
```

**Good: Clear Distinctions**
```python
def search_documents(query: str, limit: int = 10) -> List[Result]:
    """Semantic search across all documents.
    Use for: General queries, exploratory search, when you don't know exact location"""

def get_document_by_id(doc_id: str) -> Document:
    """Retrieve specific document by ID.
    Use for: When you have the exact document ID from previous search"""
```

## Tool Set Curation

### Minimal Viable Tool Set

**Principle:** Provide the smallest set of tools that covers all necessary use cases.

**Process:**
1. Identify core capabilities needed
2. Design minimal tool for each capability
3. Resist urge to add "nice to have" tools
4. Validate with actual agent usage
5. Add tools only when clear gap identified

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

### When to Split Tools

**Split a tool when:**
- It has multiple distinct use cases
- Parameters become complex/ambiguous
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

### When to Merge Tools

**Merge tools when:**
- They always get used together
- They operate on same data/resource
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

**Trade-off:** Balance between tool focus and efficiency.

## Testing Tool Usability

### Agent-Centric Testing

Don't just test if tool works - test if agent can use it effectively:

1. Can agent discover when to use this tool?
2. Can agent provide correct parameters?
3. Does agent understand the output?
4. Can agent handle errors gracefully?
5. Does tool guide agent toward efficient patterns?

### Iterate Based on Usage

Monitor agent mistakes to identify design issues:
- **Wrong parameter format repeatedly:** Parameter naming/docs unclear
- **Uses tool A when B is more appropriate:** Tool boundaries need clarification
- **Loads too much data:** Tool should have better filtering
- **Confused by error messages:** Error messages need improvement

## Template: Tool Design Analysis

```markdown
## Tool: [name]
- **Purpose:** [One sentence]
- **Parameters:** [Type and meaning]
- **Returns:** [Structure]
- **Errors:** [Exceptions]

## Token Efficiency
- **Output Size:** [Estimated tokens]
- **Optimization:** [How minimized]

## Agent Usability
- **Use Case:** [When to use]
- **Error Handling:** [How agent should respond]
```
