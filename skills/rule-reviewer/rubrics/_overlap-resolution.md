# Overlap Resolution Matrix

## Purpose

This document defines how to assign issues to their PRIMARY dimension when they could legitimately belong to multiple dimensions. Using consistent assignment rules eliminates double-counting and ensures deterministic scoring.

> **Scoring Rubric v2.0:** Only 6 dimensions are scored. Token Efficiency and Staleness are informational only.

## Scored Dimensions (100 points total)

| Dimension | Weight | Max Points |
|-----------|--------|------------|
| Actionability | 6 | 30 |
| Rule Size | 5 | 25 |
| Parsability | 3 | 15 |
| Completeness | 3 | 15 |
| Consistency | 2 | 10 |
| Cross-Agent Consistency | 1 | 5 |

## Common Overlapping Issues

| Issue Type | Could Be | Assign To | Rationale |
|------------|----------|-----------|-----------|
| Undefined threshold ("large") | Actionability OR Completeness | **Actionability** | Agent blocking is primary concern |
| Missing else branch | Actionability OR Cross-Agent | **Actionability** | Execution blocking takes priority |
| Term used inconsistently | Consistency OR Actionability | **Consistency** | Internal alignment is primary |
| Missing error handling | Completeness OR Actionability | **Completeness** | Coverage gap is primary |
| Passive voice | Actionability OR Parsability | **Actionability** | Execution clarity takes priority |
| Schema validation failure | Parsability OR Completeness | **Parsability** | Structure takes priority |
| Vague guidance | Actionability OR Clarity | **Actionability** | Agent execution is primary |
| File exceeds line limit | Rule Size (exclusive) | **Rule Size** | No overlap - line count is unique metric |

## Decision Rules

**Apply in order (Rule 1 has highest priority):**

### Rule 1: Parsability

If issue prevents PARSING the rule:
- Assign to **Parsability**
- Examples: Invalid schema, malformed YAML, broken markdown structure
- Rationale: Can't evaluate content that can't be parsed

### Rule 2: Actionability

If issue prevents EXECUTION by agent:
- Assign to **Actionability**
- Examples: Undefined thresholds, missing branches, ambiguous actions
- Rationale: Execution blocking is highest-impact concern

### Rule 3: Completeness

If issue is a MISSING coverage area:
- Assign to **Completeness**
- Examples: No error handling section, missing prerequisites, no validation steps
- Rationale: Gap in what should be documented

### Rule 4: Consistency

If issue is INTERNAL contradiction or variation:
- Assign to **Consistency**
- Examples: Different terms for same concept, conflicting instructions
- Rationale: Internal alignment problem

### Rule 5: Rule Size

If issue is LINE COUNT related:
- Assign to **Rule Size**
- Examples: File exceeds 500 lines, needs splitting
- Rationale: Physical size constraint (100% deterministic)
- **Note:** Rule Size has NO overlaps with other dimensions - line count is a unique metric

### Rule 6: Cross-Agent Consistency

If issue is AGENT-SPECIFIC assumption:
- Assign to **Cross-Agent Consistency**
- Examples: Tool assumptions, capability assumptions, terminology
- Rationale: Portability concern (lowest priority, only 5 points)

## Informational Dimensions (Not Scored)

The following dimensions are tracked for informational purposes but do not contribute to the score:

- **Token Efficiency:** Redundancy issues are noted in recommendations
- **Staleness:** Deprecated tools and broken links are flagged for remediation

## Conflict Resolution Protocol

When an issue could match multiple rules:

1. **Apply rules in order** (1 → 6)
2. **First match wins** - assign to that dimension
3. **Document the rule applied** in inventory
4. **Never double-count** - each issue appears in ONE inventory only

### Example Resolutions

**Issue:** "Use appropriate timeout for large tables"

- Could be: Actionability ("appropriate" undefined, "large" undefined)
- Could be: Cross-Agent (different agents may interpret differently)

**Resolution:**
- Rule 2 applies: "appropriate" and "large" prevent agent execution
- Assign to: **Actionability** (2 blocking issues)
- Do NOT also count in Cross-Agent

---

**Issue:** "If file not found, handle gracefully" (no else branch)

- Could be: Actionability (missing else branch)
- Could be: Completeness (error handling incomplete)
- Could be: Cross-Agent (different agents handle missing branches differently)

**Resolution:**
- Rule 2 applies: Missing branch blocks execution
- Assign to: **Actionability** (1 blocking issue)
- Do NOT also count in Completeness or Cross-Agent

---

**Issue:** "The configuration should be validated" (passive voice)

- Could be: Actionability (unclear who validates, how)
- Could be: Parsability (passive construction)

**Resolution:**
- Rule 2 applies: Passive voice makes action unclear for agent
- Assign to: **Actionability** (0.5 passive voice issue)
- Do NOT also count in Parsability

---

**Issue:** Large table defined as ">10M rows" at line 36 and ">5M rows" at line 150

- Could be: Consistency (conflicting thresholds)
- Could be: Actionability (agent doesn't know which to use)

**Resolution:**
- Rule 4 applies: Internal contradiction
- Assign to: **Consistency** (1 internal contradiction)
- Do NOT also count in Actionability

## Inventory Documentation

When assigning an issue, document in the inventory:

| Line | Issue | Assigned To | Rule Applied | Excluded From |
|------|-------|-------------|--------------|---------------|
| 45 | "appropriate" undefined | Actionability | Rule 2 | Cross-Agent |
| 89 | Missing else branch | Actionability | Rule 2 | Cross-Agent, Completeness |

This documentation enables verification and audit of assignment decisions.
