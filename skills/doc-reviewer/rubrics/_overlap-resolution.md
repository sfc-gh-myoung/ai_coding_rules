# Overlap Resolution Matrix

## Purpose

This document defines how to assign issues to their PRIMARY dimension when they could legitimately belong to multiple dimensions. Using consistent assignment rules eliminates double-counting and ensures deterministic scoring.

## Common Overlapping Issues

| Issue Type | Could Be | Assign To | Rationale |
|------------|----------|-----------|-----------|
| Wrong file path | Accuracy OR Completeness | **Accuracy** | Reference validation is primary |
| Broken external link | Staleness OR Accuracy | **Staleness** | Link currency is primary concern |
| Outdated code example | Accuracy OR Staleness | **Accuracy** | Code correctness takes priority |
| Missing feature docs | Completeness OR Structure | **Completeness** | Coverage gap is primary |
| Unexplained jargon | Clarity OR Completeness | **Clarity** | Accessibility is primary concern |
| Wrong heading level | Structure OR Consistency | **Structure** | Organization takes priority |
| Mixed list markers | Consistency OR Structure | **Consistency** | Formatting consistency is primary |
| Deprecated command | Staleness OR Accuracy | **Staleness** | Currency is primary concern |
| No troubleshooting | Completeness OR Structure | **Completeness** | Coverage gap is primary |
| Long complex sentence | Clarity OR Consistency | **Clarity** | Accessibility takes priority |

## Decision Rules

**Apply in order (Rule 1 has highest priority):**

### Rule 1: Accuracy

If issue is a FACTUAL ERROR in references:
- Assign to **Accuracy**
- Examples: Wrong file path, incorrect function name, broken code example
- Rationale: Factual correctness is highest priority

### Rule 2: Completeness

If issue is a MISSING section or feature:
- Assign to **Completeness**
- Examples: Undocumented feature, missing setup steps, no troubleshooting
- Rationale: Coverage gap prevents user success

### Rule 3: Clarity

If issue is ACCESSIBILITY for new users:
- Assign to **Clarity**
- Examples: Unexplained jargon, complex sentences, no examples
- Rationale: User understanding is critical

### Rule 4: Structure

If issue is ORGANIZATION or navigation:
- Assign to **Structure**
- Examples: Wrong section order, broken heading hierarchy, missing TOC
- Rationale: Information flow problem

### Rule 5: Staleness

If issue is CURRENCY or outdatedness:
- Assign to **Staleness**
- Examples: Broken links, deprecated tools, old versions
- Rationale: Time-based decay

### Rule 6: Consistency

If issue is FORMATTING variation:
- Assign to **Consistency**
- Examples: Mixed markers, terminology variation, code style differences
- Rationale: Lowest impact, cosmetic concern

## Conflict Resolution Protocol

When an issue could match multiple rules:

1. **Apply rules in order** (1 → 6)
2. **First match wins** - assign to that dimension
3. **Document the rule applied** in verification table
4. **Never double-count** - each issue appears in ONE table only

### Example Resolutions

**Issue:** File path `src/utils.py` doesn't exist (should be `src/helpers.py`)

- Could be: Accuracy (wrong reference)
- Could be: Completeness (missing documentation for actual file)

**Resolution:**
- Rule 1 applies: Wrong file path is factual error
- Assign to: **Accuracy** (1 invalid reference)
- Do NOT also count in Completeness

---

**Issue:** External link https://old-docs.example.com returns 404

- Could be: Staleness (broken link)
- Could be: Accuracy (invalid reference)

**Resolution:**
- Rule 5 applies: Link validity is currency check
- Assign to: **Staleness** (1 broken link)
- Do NOT also count in Accuracy

---

**Issue:** Code example uses `df.append()` (deprecated in pandas 2.0)

- Could be: Accuracy (code doesn't work)
- Could be: Staleness (deprecated pattern)

**Resolution:**
- Rule 1 applies: Code correctness is primary
- Assign to: **Accuracy** (1 outdated code example)
- Do NOT also count in Staleness

---

**Issue:** "idempotent" used without explanation

- Could be: Clarity (unexplained jargon)
- Could be: Completeness (missing glossary)

**Resolution:**
- Rule 3 applies: Accessibility is primary concern
- Assign to: **Clarity** (1 unexplained term)
- Do NOT also count in Completeness

---

**Issue:** Configuration section appears before Installation

- Could be: Structure (wrong order)
- Could be: Completeness (missing clear path to working state)

**Resolution:**
- Rule 4 applies: Organization problem
- Assign to: **Structure** (1 ordering issue)
- Do NOT also count in Completeness

---

**Issue:** Some code blocks use ``` and others use indentation

- Could be: Consistency (mixed formatting)
- Could be: Structure (inconsistent presentation)

**Resolution:**
- Rule 6 applies: Formatting variation
- Assign to: **Consistency** (1 formatting inconsistency)
- Do NOT also count in Structure

## Verification Table Documentation

When assigning an issue, document in the verification table:

| Line | Issue | Assigned To | Rule Applied | Excluded From |
|------|-------|-------------|--------------|---------------|
| 45 | Wrong file path | Accuracy | Rule 1 | Completeness |
| 67 | Broken link | Staleness | Rule 5 | Accuracy |
| 89 | Unexplained jargon | Clarity | Rule 3 | Completeness |
| 112 | Mixed markers | Consistency | Rule 6 | Structure |

This documentation enables verification and audit of assignment decisions.
