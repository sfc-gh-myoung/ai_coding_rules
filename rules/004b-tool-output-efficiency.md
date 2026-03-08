# Tool Output Token Efficiency

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-08
**Keywords:** token efficiency, tool outputs, minimal output, structured output, progressive output, context budget, verbose output
**TokenBudget:** ~1600
**ContextTier:** Medium
**Depends:** 004-tool-design-for-agents.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Designing token-efficient tool outputs for AI agents. Covers returning only necessary information, using structured parseable formats, progressive output for large results, and avoiding verbose metadata that wastes agent context.

**When to Load This Rule:**
- Designing tool output formats for AI agents
- Optimizing existing tool outputs to reduce token usage
- Implementing progressive or paginated tool responses
- Diagnosing agent context overflow caused by verbose tool outputs

## References

### Dependencies

**Must Load First:**
- **004-tool-design-for-agents.md** - Core tool design principles
- **000-global-core.md** - Foundation for all rules

**Related:**
- **003-context-engineering.md** - Context management and attention budgets
- **004a-tool-set-curation.md** - Minimal viable tool sets

## Contract

### Inputs and Prerequisites

- A tool or set of tools with defined output formats
- Understanding of the agent's context window constraints
- Knowledge of what information the agent actually needs from tool outputs

### Mandatory

- Token budget awareness for the target agent
- Measurement of actual output token counts

### Forbidden

- Returning metadata the agent did not request (timestamps, request IDs, API versions)
- Echoing input parameters back in the output
- Including redundant counts that can be derived from the data itself

### Execution Steps

1. Identify what information the agent needs from the tool output
2. Remove all metadata not directly needed for the agent's next action
3. Structure output in a consistent, parseable format
4. Implement progressive output mechanisms for potentially large results
5. Measure token counts and compare before/after optimization

### Output Format

Minimal, structured tool responses containing only the information the agent needs for its next action.

### Validation

**Pre-Task-Completion Checks:**
- Output contains no echoed input parameters
- Output contains no unnecessary metadata (timestamps, request IDs)
- Redundant counts are removed (agent can derive from array length)
- Large results use progressive loading

**Success Criteria:**
- Tool output uses fewer tokens than before optimization
- Agent can still complete its tasks with the reduced output
- Output format is consistent across similar tools

### Post-Execution Checklist

- [ ] Output contains no echoed input parameters
- [ ] No unnecessary metadata in responses (timestamps, request IDs, API versions)
- [ ] Success responses are minimal (silent success where possible)
- [ ] Large results use progressive loading with sensible defaults
- [ ] Token count measured before and after optimization

## Return Only Necessary Information

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

## Structured, Parseable Formats

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

## Progressive Output for Large Results

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

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Returning Full Objects When Summary Suffices

**Problem:** Returning complete data structures when only metadata is needed.

```python
# WRONG: Returns everything
def list_files(path):
    return [{"name": f.name, "content": f.read(), "metadata": f.stat()} 
            for f in Path(path).iterdir()]
```

**Correct Pattern:**
```python
# CORRECT: Return summary, fetch details on demand
def list_files(path):
    return [{"name": f.name, "size": f.stat().st_size} 
            for f in Path(path).iterdir()]

def read_file(path):  # Separate tool for content
    return Path(path).read_text()
```

### Anti-Pattern 2: No Pagination for Large Results

**Problem:** Returning unbounded result sets that overflow context.

```python
# WRONG: Returns all matches
def search(query):
    return database.find_all(query)  # Could be 10K+ results
```

**Correct Pattern:**
```python
# CORRECT: Paginated results
def search(query, limit=10, offset=0):
    return database.find(query, limit=limit, offset=offset)
```
