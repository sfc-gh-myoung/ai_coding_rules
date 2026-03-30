# Workflow: Review Verification

## Purpose

Prevent shortcut-based reviews by enforcing evidence requirements that can only be satisfied by actually reading the rule file.

## Evidence Requirements

Every review MUST include:

### 1. Rule Content Quotes (MANDATORY)

Each dimension score MUST cite at least one direct quote from the rule file with line number.

**Format:**
```
**Evidence:** Line 47 states: "ALWAYS use pd.to_datetime() with explicit format parameter"
```

**Verification:** The quoted text MUST appear verbatim at the cited line number. Fabricated quotes = INVALID review.

### 2. Line Reference Density

**Minimum Requirements:**
- FULL mode: ≥15 distinct line references across all dimensions
- FOCUSED mode: ≥5 distinct line references per dimension
- STALENESS mode: ≥3 distinct line references

**Why:** Template-based reviews cannot produce valid line references because the agent didn't read the file.

### 3. Rule-Specific Findings

Each review MUST identify at least 2 findings unique to that rule:
- Specific anti-pattern names
- Specific function/class names from code examples
- Specific keyword from metadata
- Specific section headings

**Generic findings that apply to any rule are INSUFFICIENT.**

## Verification Checklist

Before writing review to file, verify:

- [ ] ≥15 line references present (FULL mode)
- [ ] Each dimension cites direct quote with line number
- [ ] Findings reference rule-specific content (not generic advice)
- [ ] Agent Execution Test counts specific blocking issues from THIS rule
- [ ] Recommendations reference specific sections by line number

## Detection of Shortcut Attempts

**Red Flags (Automatic INVALID):**

1. **No line references** - Review contains zero "line X" or "(lines X-Y)" references
2. **Round line numbers only** - All references are to lines 10, 20, 30, etc. (fabricated)
3. **Generic content** - Findings could apply to any rule without modification
4. **Template patterns** - Multiple reviews share identical phrasing for different rules
5. **Missing quotes** - No direct quotes from rule content

## Enforcement

If verification fails:
1. DELETE the invalid review
2. READ the actual rule file
3. Generate review with proper evidence
4. Re-verify before writing

**Do NOT write reviews that fail verification.**

## Why This Cannot Be Shortcut

To produce a valid review under these requirements, the agent MUST:
1. Read the rule file (to find actual line numbers)
2. Extract actual quotes (to cite as evidence)
3. Identify rule-specific content (to demonstrate comprehension)

**There is no way to satisfy these requirements without reading the file.**

### 4. Template Compliance

- [ ] Executive Summary table uses exact column headers from REVIEW-OUTPUT-TEMPLATE.md
- [ ] All 9 required H2 sections present in correct order
- [ ] Post-Review Checklist has exactly 11 items
- [ ] Informational sections (Token Efficiency, Staleness) are inline, not separate H2

## Integration Point

Call this verification before `file-write.md` workflow:
1. Generate review content
2. **Run review-verification.md checklist**
3. If PASS: proceed to file-write.md
4. If FAIL: return to review generation with actual file reading
