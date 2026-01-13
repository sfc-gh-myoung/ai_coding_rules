# Per-Rule Verification Protocol

## Purpose

Ensure each rule receives genuine individual analysis by requiring evidence that can ONLY be obtained by reading the actual rule file.

## The Problem

Agents may attempt to generate reviews without reading files by:
- Using bash heredocs with templated content
- Copying patterns from previous reviews
- Generating generic findings that could apply to any rule
- Fabricating line numbers without verification

## The Solution: Unforgeable Evidence Requirements

### Evidence That Proves File Was Read

Each review MUST contain ALL of the following:

#### 1. Exact Quote Verification

**Requirement:** At least 3 direct quotes from the rule file with line numbers.

**Format:**
```markdown
Line 156: "Use `datetime.now(UTC)` not deprecated `datetime.utcnow()`"
```

**Why Unforgeable:** Agent must have read line 156 to know what it says.

#### 2. Metadata Extraction

**Requirement:** Review must cite actual metadata values:
- Exact `TokenBudget` value (e.g., "~6200")
- Exact `LastUpdated` date (e.g., "2026-01-12")
- At least 3 Keywords from the actual file

**Why Unforgeable:** Each rule has unique metadata values.

#### 3. Rule-Specific Pattern Names

**Requirement:** Cite at least 2 specific patterns/anti-patterns by their exact names as they appear in the rule.

**Example:** "Anti-Pattern 2: Using Deprecated `datetime.utcnow()`"

**Why Unforgeable:** Pattern names are unique to each rule.

#### 4. Code Example Verification

**Requirement:** Reference at least one specific code example from the rule, citing the function/class names used.

**Example:** "The `ensure_python_datetime()` helper function at lines 330-350..."

**Why Unforgeable:** Function names are rule-specific.

## Verification Algorithm

```python
def verify_review_authenticity(review_text: str, rule_path: str) -> bool:
    """Verify review was generated from actual rule reading."""
    rule_content = read_file(rule_path)
    
    # Extract line references from review
    line_refs = extract_line_references(review_text)  # "(line 42)", "lines 50-55"
    
    # Verify at least 15 references exist (FULL mode)
    if len(line_refs) < 15:
        return False, "Insufficient line references"
    
    # Verify quoted content matches actual lines
    quotes = extract_quotes_with_lines(review_text)
    for line_num, quoted_text in quotes:
        actual_line = get_line(rule_content, line_num)
        if quoted_text not in actual_line:
            return False, f"Quote mismatch at line {line_num}"
    
    # Verify metadata values match
    rule_token_budget = extract_token_budget(rule_content)
    if rule_token_budget not in review_text:
        return False, "TokenBudget not cited"
    
    return True, "Verification passed"
```

## Detection Heuristics

### Shortcut Indicators (Any = REJECT)

1. **Zero line references** - Impossible if file was read
2. **All round numbers** - Lines 10, 20, 50, 100 (statistically improbable)
3. **Identical phrasing across reviews** - Template reuse
4. **Generic findings** - "Code examples are clear" (no specifics)
5. **Missing metadata citation** - TokenBudget, LastUpdated not mentioned
6. **No function/class names** - Every rule has code examples

### Authentic Review Indicators

1. **Varied line numbers** - 47, 156, 234, 512 (actual positions)
2. **Direct quotes match** - Quoted text exists at cited line
3. **Rule-specific terminology** - Uses exact pattern names from rule
4. **Metadata matches** - TokenBudget value is correct
5. **Code references** - Cites actual function/class names

## Enforcement in Workflow

### For rule-reviewer

After generating review content, before file write:

1. Run verification checklist
2. If ANY check fails: **DO NOT WRITE FILE**
3. Return to rule file, read properly
4. Regenerate review with actual evidence
5. Re-verify

### For bulk-rule-reviewer

For each rule:

1. READ the rule file (store in working memory)
2. Generate review with evidence from working memory
3. Verify evidence before writing
4. Only after verification passes: write to file
5. Clear working memory, load next rule

**CRITICAL:** Working memory must contain rule content BEFORE review generation.

## Why This Works

An agent attempting shortcuts cannot:
- Guess the exact text at line 156
- Know the TokenBudget is "~6200" vs "~5500"
- Know the anti-pattern is named "Using Deprecated datetime.utcnow()"
- Know the helper function is called "ensure_python_datetime"

**This evidence can ONLY come from reading the actual file.**
