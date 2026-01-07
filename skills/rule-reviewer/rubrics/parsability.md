# Parsability Rubric (15 points)

## Scoring Criteria

### 5/5 (15 points): Excellent
- Schema validation passes with 0 errors
- All metadata fields present and correct
- Markdown structure valid
- No visual formatting issues
- Agent-friendly formatting throughout

### 4/5 (12 points): Good
- Schema validation passes OR only LOW severity issues
- Metadata complete with minor issues
- Markdown mostly valid (1-2 minor issues)
- Minimal visual formatting

### 3/5 (9 points): Acceptable
- 1-2 MEDIUM schema errors
- Some metadata missing or incorrect
- Markdown has 3-5 validation issues
- Some problematic formatting

### 2/5 (6 points): Needs Work
- 1-2 HIGH schema errors OR 3-5 MEDIUM errors
- Multiple metadata issues
- Significant markdown problems
- Visual formatting present

### 1/5 (3 points): Poor
- ≥1 CRITICAL schema error
- Metadata severely incomplete
- Malformed markdown
- Extensive visual formatting

## CRITICAL: Schema Validation Gates

Run before scoring:
```bash
uv run python scripts/schema_validator.py [target_file]
```

### Scoring Impact by Error Severity

| Schema Errors | Max Parsability Score | Notes |
|---------------|----------------------|-------|
| 0 errors | 5/5 (15 points) | Full score available |
| MEDIUM only | 4/5 (12 points) | Minor issues |
| 1-2 HIGH | 3/5 (9 points) | Significant issues |
| ≥3 HIGH | 2/5 (6 points) | Major issues |
| ≥1 CRITICAL | 2/5 (6 points) | **CAPPED** - cannot exceed |

**All schema errors must appear in review's "Critical Issues" section.**

## Schema Compliance Checklist

### Required Metadata Fields (v3.2 schema)

Must be present:
- `SchemaVersion` (format: v3.2)
- `RuleVersion` (format: v3.0.0 semantic versioning)
- `LastUpdated` (format: YYYY-MM-DD)
- `Keywords` (comma-separated, 3+ terms)
- `TokenBudget` (format: ~NNNN)
- `ContextTier` (values: Critical | High | Medium | Low)
- `Depends` (list of rule files OR "None" for foundation)

### Section Order (v3.2 schema)

Must follow this sequence:
1. Title and preamble
2. Metadata block (## Metadata)
3. Scope (## Scope)
4. References (## References)
5. Contract (## Contract)
6. Content sections
7. Post-Execution Checklist (if present)

## Markdown Structure Validation

### Heading Hierarchy

Must be properly nested:
```markdown
✅ GOOD:
# Title (H1)
## Section (H2)
### Subsection (H3)
#### Detail (H4)

❌ BAD:
# Title (H1)
### Subsection (H3) ← Skipped H2!
## Section (H2) ← Out of order!
```

### List Formatting

Use consistent list markers:
```markdown
✅ GOOD:
- Item 1
- Item 2
  - Nested item
  - Nested item

❌ BAD:
- Item 1
* Item 2  ← Mixed markers
- Item 3
  * Nested  ← Mixed markers
```

### Code Block Fencing

Must use proper fencing:
````markdown
✅ GOOD:
```python
code here
```

❌ BAD:
```
code here without language tag
```
````

### Table Formatting

Must use proper structure:
```markdown
✅ GOOD:
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

❌ BAD:
| Column 1 | Column 2 |
| Value 1  | Value 2  |  ← Missing separator row
```

## Visual Formatting Issues

### Forbidden Patterns

Agents cannot interpret these:

**ASCII Art / Diagrams:**
```
❌ FORBIDDEN:
    ┌─────────┐
    │  Start  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │   End   │
    └─────────┘
```

**Arrow Characters:**
```
❌ FORBIDDEN:
Input → Process → Output
A ⇒ B ⇒ C
```

**Box Drawing:**
```
❌ FORBIDDEN:
╔═══════════╗
║  Header   ║
╚═══════════╝
```

### Acceptable Alternatives

Use text-based flow:
```markdown
✅ GOOD:
Workflow:
1. Input → 2. Process → 3. Output

Or:
Step 1: Input
Step 2: Process
Step 3: Output
```

## Common Parsability Issues

### Issue 1: Missing Depends Field

**Error:**
```
[CRITICAL] Missing metadata field: Depends
```

**Fix:**
```markdown
**Depends:** 000-global-core.md

or if foundation rule:

**Depends:** None
```

### Issue 2: Invalid Section Order

**Error:**
```
[HIGH] Section order violation: Contract appears before References
```

**Fix:** Move References section before Contract section.

### Issue 3: Malformed YAML Metadata

**Error:**
```
[CRITICAL] Invalid YAML in metadata block
Line 12: Unexpected tab character
```

**Fix:** Use spaces (not tabs) for YAML indentation.

### Issue 4: Broken Code Fences

**Error:**
```
[MEDIUM] Unclosed code fence at line 234
```

**Fix:** Ensure every ` ``` ` opener has matching closer.

## Scoring Formula

```
Base score = 5/5 (15 points)

Schema validation:
  CRITICAL errors: Cap at 2/5 (6 points)
  HIGH errors (1-2): Max 3/5 (9 points)
  HIGH errors (≥3): Max 2/5 (6 points)
  MEDIUM only: Max 4/5 (12 points)

Additional deductions:
  Heading hierarchy issues: -0.5 each (up to -2)
  List formatting issues: -0.3 each (up to -2)
  Visual formatting present: -1 per instance (up to -3)
  Malformed tables: -0.5 each (up to -2)

Minimum score: 1/5 (3 points)
```

## Integration with Critical Issues

All schema errors (CRITICAL, HIGH, MEDIUM) must be listed in review's Critical Issues section with:
- Severity level
- Line number (if available)
- Error message from validator
- Recommended fix

**Example:**
```markdown
## Critical Issues

### 1. Schema Violation (CRITICAL): Missing metadata field: Depends

**Location:** Line 10 (metadata block)
**Error:** Required field "Depends" not found in metadata section
**Fix:** Add `**Depends:** 000-global-core.md` to metadata block (or "None" for foundation rules)
```
