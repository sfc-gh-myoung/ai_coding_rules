# Workflow 01: Rule Discovery

## Purpose

Find all markdown files in the `rules/` directory for batch review. Supports filtering by glob patterns to review subsets (e.g., only Snowflake rules, only core rules).

## Inputs

- `filter_pattern` (optional): Glob pattern to filter rules
  - Default: `rules/*.md` (all rules)
  - Examples: `rules/100-*.md`, `rules/*-core.md`, `rules/2*.md`

## Outputs

- List of rule file paths (one per line)
- Sorted alphabetically by filename
- Count of matching files

## Implementation

### Step 1: Validate Rules Directory Exists

```bash
if [ ! -d "rules" ]; then
  echo "ERROR: rules/ directory not found"
  exit 1
fi
```

**Error Handling:**
- If `rules/` doesn't exist: Exit with error "rules/ directory not found"
- If permission denied: Exit with error "Cannot read rules/ directory - check permissions"

### Step 2: Find All Matching Files

```bash
# Using find command (works on all Unix-like systems)
find rules -name "*.md" -type f | sort

# Or with filter pattern (if specified)
# Example: filter_pattern = "rules/100-*.md"
find rules -name "100-*.md" -type f | sort
```

**Alternative Using Glob Tool (if available):**
```
Use glob tool with pattern specified in filter_pattern
Sort results alphabetically
```

### Step 3: Validate Results

```bash
file_count=$(find rules -name "*.md" -type f | wc -l)

if [ "$file_count" -eq 0 ]; then
  echo "ERROR: No rule files found matching pattern: $filter_pattern"
  exit 1
fi

echo "Found $file_count rule files"
```

**Error Handling:**
- If no `.md` files found: Exit with error "No rule files found in rules/"
- If filter_pattern matches nothing: Exit with error "No rule files found matching pattern: <pattern>"

## Expected Output Format

```
Found 113 rule files

rules/000-global-core.md
rules/001-memory-bank.md
rules/002-rule-governance.md
rules/002a-rule-creation.md
rules/002b-rule-maintenance.md
...
rules/950-create-dbt-semantic-view.md
```

## Usage Examples

### Example 1: Discover All Rules

**Input:**
```
filter_pattern: rules/*.md (default)
```

**Output:**
```
Found 113 rule files

rules/000-global-core.md
rules/001-memory-bank.md
...
rules/950-create-dbt-semantic-view.md
```

### Example 2: Discover Snowflake Rules Only

**Input:**
```
filter_pattern: rules/100-*.md
```

**Output:**
```
Found 23 rule files

rules/100-snowflake-core.md
rules/101-snowflake-sql-style.md
rules/102-snowflake-warehouse-sizing.md
...
rules/115-snowflake-cortex-agents-core.md
```

### Example 3: Discover Core Rules Only

**Input:**
```
filter_pattern: rules/*-core.md
```

**Output:**
```
Found 8 rule files

rules/000-global-core.md
rules/100-snowflake-core.md
rules/200-python-core.md
rules/300-bash-scripting-core.md
rules/420-javascript-core.md
rules/430-typescript-core.md
rules/600-golang-core.md
rules/115-snowflake-cortex-agents-core.md
```

## Error Scenarios and Recovery

### Scenario 1: Rules Directory Missing

**Error:**
```
ERROR: rules/ directory not found
```

**Recovery:**
- Verify working directory is project root
- Check if `rules/` directory exists
- Abort bulk review execution

### Scenario 2: No Matching Files

**Error:**
```
ERROR: No rule files found matching pattern: rules/999-*.md
```

**Recovery:**
- Verify filter_pattern is correct
- Check if any files match the pattern
- Adjust pattern or abort execution

### Scenario 3: Permission Denied

**Error:**
```
ERROR: Cannot read rules/ directory - check permissions
```

**Recovery:**
- Check file system permissions
- Verify user has read access to `rules/` directory
- Abort bulk review execution

## Integration with Next Workflow

**Output of this workflow** → **Input to review-execution.md**

The list of file paths produced by this workflow is passed to the review execution workflow, which iterates through each file and invokes the rule-reviewer skill.

## Performance Notes

- Discovery is fast (typically <1 second for 113 files)
- Sorting is alphabetical by full path
- No context load required (simple file system operation)
- Safe to run repeatedly (idempotent, read-only)

## Testing Checklist

- [ ] Discovers all 113 rules with default pattern
- [ ] Filters correctly with `rules/100-*.md` pattern
- [ ] Returns empty result gracefully for non-matching pattern
- [ ] Handles missing `rules/` directory with clear error
- [ ] Sorts results alphabetically
- [ ] Counts files correctly
