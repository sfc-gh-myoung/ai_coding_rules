# Overlap Resolution Matrix

## Purpose

This document defines how to assign issues to their PRIMARY dimension when they could legitimately belong to multiple dimensions. Using consistent assignment rules eliminates double-counting and ensures deterministic scoring.

## Common Overlapping Issues

| Issue Type | Could Be | Assign To | Rationale |
|------------|----------|-----------|-----------|
| Undefined threshold ("large") | Actionability OR Completeness | **Actionability** | Agent blocking is primary concern |
| Missing else branch | Actionability OR Cross-Agent | **Actionability** | Execution blocking takes priority |
| Deprecated tool mentioned | Staleness OR Completeness | **Staleness** | Currency is primary concern |
| Repeated content | Token Efficiency OR Completeness | **Token Efficiency** | Efficiency is primary concern |
| Term used inconsistently | Consistency OR Actionability | **Consistency** | Internal alignment is primary |
| Missing error handling | Completeness OR Actionability | **Completeness** | Coverage gap is primary |
| Passive voice | Actionability OR Parsability | **Actionability** | Execution clarity takes priority |
| Schema validation failure | Parsability OR Completeness | **Parsability** | Structure takes priority |
| Broken link | Staleness OR Accuracy | **Staleness** | Currency check catches this |
| Vague guidance | Actionability OR Clarity | **Actionability** | Agent execution is primary |

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

### Rule 5: Token Efficiency

If issue is REDUNDANCY or budget:
- Assign to **Token Efficiency**
- Examples: Repeated definitions, verbose prose, budget exceeded
- Rationale: Efficiency problem

### Rule 6: Staleness

If issue is CURRENCY related:
- Assign to **Staleness**
- Examples: Deprecated tools, broken links, old patterns
- Rationale: Time-based decay

### Rule 7: Cross-Agent Consistency

If issue is AGENT-SPECIFIC assumption:
- Assign to **Cross-Agent Consistency**
- Examples: Tool assumptions, capability assumptions, terminology
- Rationale: Portability concern (lowest priority, only 5 points)

## Conflict Resolution Protocol

When an issue could match multiple rules:

1. **Apply rules in order** (1 → 7)
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

**Issue:** Rule uses "flake8" for linting

- Could be: Staleness (deprecated tool)
- Could be: Actionability (agent might not have access to outdated tool)

**Resolution:**
- Rule 6 applies: Tool currency is the primary concern
- Assign to: **Staleness** (1 deprecated tool)
- Do NOT also count in Actionability

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
| 67 | flake8 deprecated | Staleness | Rule 6 | Actionability |
| 89 | Missing else branch | Actionability | Rule 2 | Cross-Agent, Completeness |

This documentation enables verification and audit of assignment decisions.
