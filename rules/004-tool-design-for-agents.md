# Tool Design for AI Agents

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** tool design, agent tools, token efficiency, tool parameters, function calling, tool overlap, tool contracts, error handling, minimal tool set, self-contained tools, LLM-friendly parameters, single responsibility
**TokenBudget:** ~5000
**ContextTier:** High
**Depends:** rules/000-global-core.md, rules/003-context-engineering.md

## Purpose
Establish comprehensive tool design practices that maximize agent effectiveness through token-efficient outputs, minimal tool overlap, clear contracts, and patterns that promote efficient agent behaviors while maintaining robustness and clarity.

## Rule Scope

Tool development for AI agents across all platforms (Claude, GPT, Gemini) and frameworks

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Single responsibility per tool** - One clear purpose, do it extremely well
- **Token-efficient outputs** - Return only necessary info (not full dumps)
- **LLM-friendly parameters** - Use semantic names like "query" not mode codes like 0/1/2
- **Clear contracts** - Explicitly specify inputs, outputs, errors
- **Minimal overlap** - No ambiguity about which tool to use for a task
- **Self-contained** - No hidden dependencies or required setup
- **Never return verbose outputs** - Agents pay token cost for every character returned

**Quick Checklist:**
- [ ] Tool has single clear purpose (one thing well)
- [ ] Parameters are unambiguous (semantic names)
- [ ] Outputs are minimal and actionable
- [ ] No overlap with existing tools
- [ ] Clear contract (inputs, outputs, errors specified)
- [ ] Robust error handling (actionable messages)
- [ ] Token-efficient (no verbose dumps)

## Contract

<contract>
<inputs_prereqs>
Understanding of agent capabilities; knowledge of token budgets; awareness of LLM strengths/weaknesses; access to tool development framework
</inputs_prereqs>

<mandatory>
All development tools; testing frameworks; agent evaluation tools
</mandatory>

<forbidden>
Tools that create bloated, redundant tool sets without clear boundaries
</forbidden>

<steps>
1. Design tool with clear, single responsibility
2. Define unambiguous parameters that play to LLM strengths
3. Implement token-efficient outputs (return only necessary information)
4. Create clear contracts (inputs, outputs, errors)
5. Ensure no overlap with existing tools
6. Test with actual agent to validate usability
7. Document tool purpose and usage patterns
</steps>

<output_format>
Self-contained tools with clear specifications; token-efficient responses; structured error messages
</output_format>

<validation>
Tool has single clear purpose; parameters are unambiguous; outputs are minimal and actionable; no overlap with other tools; agent can use tool effectively
</validation>

<design_principles>
- **Self-Contained:** Each tool does one thing well, with no hidden dependencies
- **Minimal Overlap:** Clear boundaries between tools; no ambiguity about which tool to use
- **Token Efficient:** Return only necessary information; avoid verbose outputs
- **Clear Contracts:** Inputs, outputs, and errors explicitly specified
- **LLM-Friendly Parameters:** Descriptive parameters that play to semantic understanding
- **Promote Good Patterns:** Tool design guides agents toward efficient behaviors
- **Robust Error Handling:** Clear, actionable error messages
- **Minimal Viable Set:** Curate smallest set of tools that covers use cases
</design_principles>

</contract>

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

## Post-Execution Checklist

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

## Validation

- **Success Checks:** Agent can discover which tool to use; parameters are unambiguous; outputs are token-efficient; no tool overlap causes confusion; error messages enable self-correction; tool set covers needs without bloat; agent follows efficient patterns; tools are self-contained and stateless
- **Negative Tests:** Ambiguous tool boundaries cause agent confusion; verbose outputs waste attention budget; opaque parameter names require memorization; vague error messages prevent correction; bloated tool sets overwhelm agent; stateful tools break after context reset

> **Investigation Required**
> When applying this rule:
> 1. **Review existing tool set BEFORE adding new tools** - Check for overlap, identify gaps
> 2. **Test tool outputs for token efficiency** - Measure actual token counts, not theoretical
> 3. **Never assume tool behavior** - Run tools with test inputs to verify outputs
> 4. **Verify tool contracts match implementation** - Check parameter types, return values, error handling
> 5. **Make grounded recommendations based on investigated tool behavior** - Don't suggest tools without understanding their actual outputs
>
> **Anti-Pattern:**
> "Based on typical tool design, this probably returns a JSON object..."
> "Let me add a new tool for this - it shouldn't overlap with existing ones..."
>
> **Correct Pattern:**
> "Let me check the existing tools first to see if any handle this use case."
> [reviews tool specifications and tests relevant tools]
> "I see tool X already handles part of this, but returns 500+ token outputs. Here's a new token-efficient tool that complements it without overlap..."

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

## References

### External Documentation

**Anthropic Engineering Articles:**
- [Writing Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) - Comprehensive guide to token-efficient tool design, clear contracts, and promoting efficient agent behaviors
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Context management strategies that inform tool output design

**Claude Documentation:**
- [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Model-specific tool usage patterns
- [Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Tool specification best practices

**Additional Resources:**
- [API Design Best Practices](https://developers.google.com/tech-writing) - Principles for clear, usable interfaces
- [Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling) - OpenAI's function calling patterns

### Related Rules
- **Global Core**: `rules/000-global-core.md` - Foundational workflow and safety protocols
- **Context Engineering**: `rules/003-context-engineering.md` - Token efficiency and attention budget management
- **Rule Governance**: `rules/002-rule-governance.md` - Standards for rule and tool documentation
- **AGENTS Workflow**: `AGENTS.md` - Rule discovery and operational protocols

## 1. Tool Design Fundamentals

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

## 2. Token Efficiency in Tool Outputs

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

## 3. Parameter Design

### Play to LLM Strengths

**LLMs are good at:**
- Semantic understanding
- Natural language descriptions
- Contextual reasoning
- Pattern matching

**LLMs are bad at:**
- Precise numerical values without context
- Complex nested structures from memory
- Remembering exact syntax
- Arbitrary identifiers

**Design Parameters Accordingly:**

**Good: Semantic, Descriptive Parameters**
```python
def create_task(
    title: str,
    priority: Literal["low", "medium", "high", "critical"],
    category: Literal["bug", "feature", "docs", "test"],
    description: str
):
    """Create a task with clear categorical parameters"""
```

**Bad: Arbitrary Codes**
```python
def create_task(
    title: str,
    priority: int,  # What does 1 vs 2 mean?
    category_code: str,  # "BG" vs "FT" vs "DC"?
    description: str
):
    """Create a task with opaque codes"""
```

### Descriptive Parameter Names

**Parameters should be self-documenting:**

```python
# Good: Clear what each parameter means
def send_notification(
    recipient_email: str,
    subject: str,
    message_body: str,
    include_timestamp: bool = True
)

# Bad: Unclear parameter meanings
def send_notification(
    to: str,  # Email? User ID? Name?
    s: str,  # Subject?
    msg: str,  # Message?
    ts: bool = True  # Timestamp? TLS? ???
)
```

### Parameter Validation

**Validate inputs and provide clear errors:**

```python
def search_date_range(
    start_date: str,
    end_date: str,
    resource_type: str
) -> List[Result]:
    """Search resources within date range.

    Args:
        start_date: ISO format (YYYY-MM-DD)
        end_date: ISO format (YYYY-MM-DD)
        resource_type: One of: "users", "posts", "comments"

    Raises:
        ValueError: If dates not in ISO format or end < start
        ValueError: If resource_type not recognized
    """
    # Validate date format
    if not validate_iso_date(start_date):
        raise ValueError(f"start_date must be ISO format (YYYY-MM-DD), got: {start_date}")

    # Validate logical constraints
    if end_date < start_date:
        raise ValueError(f"end_date ({end_date}) must be after start_date ({start_date})")

    # Validate enumerated options
    valid_types = ["users", "posts", "comments"]
    if resource_type not in valid_types:
        raise ValueError(f"resource_type must be one of {valid_types}, got: {resource_type}")
```

**Benefits:**
- Agent receives actionable error messages
- Can self-correct based on validation feedback
- Prevents silent failures

## 4. Explicit Tool Specifications

### Tool Specification Standards

**Every tool must clearly specify:**
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
    """Create a pull request in the repository.

    Purpose:
        Opens a new pull request from source_branch to target_branch
        with specified title, description, and optional reviewers.

    Args:
        title: PR title (max 200 characters)
        description: PR description (markdown supported)
        source_branch: Branch containing changes
        target_branch: Branch to merge into (default: "main")
        reviewers: List of GitHub usernames to request review from

    Returns:
        {
            "pr_number": int,
            "url": str,
            "status": "open" | "draft"
        }

    Raises:
        ValueError: If title exceeds 200 chars
        BranchNotFoundError: If source_branch doesn't exist
        PermissionError: If user lacks permission to create PR
        GitHubAPIError: If GitHub API request fails

    Side Effects:
        - Creates PR in GitHub repository
        - Sends notifications to reviewers
        - Triggers CI/CD pipeline if configured

    Example:
        pr = create_pull_request(
            title="Add authentication feature",
            description="Implements OAuth2 login flow",
            source_branch="feature/auth",
            reviewers=["alice", "bob"]
        )
        print(f"Created PR #{pr['pr_number']}")
    """
```

### Error Handling Patterns

**Provide Clear, Actionable Errors:**

**Bad Error Messages:**
```python
raise Exception("Error")  # What error?
raise ValueError("Invalid input")  # What's invalid?
raise RuntimeError("Something went wrong")  # What went wrong?
```

**Good Error Messages:**
```python
# Specific problem and remediation
raise ValueError(
    f"source_branch '{source_branch}' does not exist. "
    f"Available branches: {', '.join(available_branches)}"
)

# Clear constraint violation
raise ValueError(
    f"title exceeds maximum length of 200 characters "
    f"(current: {len(title)}). Please shorten the title."
)

# Actionable permission error
raise PermissionError(
    f"User '{username}' lacks permission to create pull requests. "
    f"Required permission: 'repo:write'. "
    f"Contact repository administrator to request access."
)
```

**Benefits:**
- Agent understands exactly what went wrong
- Error message suggests how to fix the issue
- Can retry with corrected parameters

## 5. Promoting Efficient Agent Behaviors

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

## 6. Tool Set Curation

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

## 7. Testing Tool Usability

### Agent-Centric Testing

**Don't just test if tool works - test if agent can use it effectively:**

```python
# Test scenarios
1. Can agent discover when to use this tool?
2. Can agent provide correct parameters?
3. Does agent understand the output?
4. Can agent handle errors gracefully?
5. Does tool guide agent toward efficient patterns?
```

**Testing Approach:**

```python
# Evaluation prompt
"""
You have these tools: [list tools]

Task: Implement user authentication

[Observe which tools agent chooses and how it uses them]
"""

# Look for:
- Does agent pick right tool for each step?
- Does it struggle with parameter formats?
- Does it waste tokens loading unnecessary data?
- Does it handle errors and retry correctly?
```

### Iterate Based on Usage

**Monitor how agents actually use tools:**

```python
# Common agent mistakes might indicate tool design issues

Agent repeatedly provides wrong parameter format
- Cause: Parameter naming/documentation unclear

Agent uses tool A when tool B is more appropriate
- Cause: Tool boundaries need clarification

Agent loads too much data
- Cause: Tool should have better filtering/limiting

Agent gets confused by error messages
- Cause: Error messages need improvement
```

## Tool Design Analysis
- **Purpose:** [What this tool accomplishes in one sentence]
- **Parameters:** [Each parameter with type and meaning]
- **Returns:** [Return type and structure]
- **Errors:** [Exceptions and when raised]

## Token Efficiency
- **Output Size:** [Estimated tokens in typical response]
- **Optimization:** [How output is minimized]

## Agent Usability
- **Clear Use Case:** [When agent should use this tool]
- **Parameter Guidance:** [How agent should provide parameters]
- **Error Handling:** [How agent should respond to errors]

## Implementation
[Tool code or specification]
```
