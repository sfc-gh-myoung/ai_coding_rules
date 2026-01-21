# Overlap Resolution Matrix

**Purpose:** Eliminate double-counting by defining primary ownership for issues that could belong to multiple dimensions.

**Rule:** An issue is counted in ONE dimension only. Use primary dimension from this matrix.

## Common Overlapping Issues

| Issue Type | Primary Dimension | NOT Counted In | Rationale |
|------------|-------------------|----------------|-----------|
| Missing else branch | Executability | Completeness, Risk | Blocking execution - agent cannot proceed |
| Undefined threshold | Executability | Success Criteria | Can't execute without concrete value |
| Missing error recovery | Completeness | Risk Awareness | Error handling is flow completeness |
| No rollback plan | Risk Awareness | Completeness | Risk mitigation is risk-specific |
| Vague success criteria | Success Criteria | Executability | Verification issue, not execution blocker |
| Missing prerequisite check | Dependencies | Executability | Dependency ordering, not blocking issue |
| Unbounded iteration | Scope | Executability | Scope boundary issue, not blocking if default exists |
| Missing task decomposition | Decomposition | Completeness | Structural issue, not content missing |
| Missing rationale for choice | Context | Completeness | Understanding issue, not flow gap |
| Concurrent modification risk | Risk Awareness | Data, Completeness | Risk identification specific |

## Decision Rules (IF-THEN)

### Rule 1: Execution Blocking
**IF** issue prevents autonomous agent from taking next action  
**THEN** → Executability (primary)

### Rule 2: Missing Content/Flow
**IF** issue is about missing steps, error handling, or flow branches (but agent CAN proceed)  
**THEN** → Completeness (primary)

### Rule 3: Verification Missing
**IF** issue is about how to verify success (not about executing the action)  
**THEN** → Success Criteria (primary)

### Rule 4: Boundary Missing
**IF** issue is about unclear scope, unbounded work, or missing termination  
**THEN** → Scope (primary)

### Rule 5: Ordering/Prerequisites
**IF** issue is about what must come before/after (not about blocking execution)  
**THEN** → Dependencies (primary)

### Rule 6: Structure/Granularity
**IF** issue is about task size, parallelization, or grouping  
**THEN** → Decomposition (primary)

### Rule 7: Understanding/Rationale
**IF** issue is about WHY a choice was made (not about execution)  
**THEN** → Context (primary)

### Rule 8: Risk/Mitigation
**IF** issue is about potential failures and their prevention  
**THEN** → Risk Awareness (primary)

## Conflict Resolution Protocol

When an issue could match multiple rules:

1. **Apply rules in order** (Rule 1 has highest priority, Rule 8 lowest)
2. **First matching rule wins**
3. **Document the rule applied** in worksheet

### Example Resolution

**Issue:** "Missing else branch after git status check"

- **Check Rule 1:** Does it block execution? YES (agent doesn't know what to do if status fails)
- **Result:** Executability is primary
- **Action:** Count in Executability worksheet only
- **Note in Completeness:** "See Executability for missing branch (Rule 1)"

**Issue:** "No rollback strategy if migration fails"

- **Check Rule 1:** Does it block execution? NO (agent can proceed with migration)
- **Check Rule 2:** Missing flow? Partial (recovery flow missing)
- **Check Rule 8:** Risk/mitigation? YES (failure scenario handling)
- **Result:** Risk Awareness is primary (Rule 8 more specific than Rule 2)
- **Action:** Count in Risk Awareness worksheet only

## Cross-Reference Table

Use this table when uncertain about primary ownership:

| If you're reviewing... | And you find... | Check first... | Then check... |
|------------------------|-----------------|----------------|---------------|
| Executability | Missing branch | Rule 1 (Exec) | N/A - keep here |
| Executability | Vague threshold | Rule 3 (SC) | Rule 1 (Exec) |
| Completeness | Missing error handling | Rule 2 (Comp) | Rule 8 (Risk) |
| Success Criteria | Can't verify | Rule 3 (SC) | Rule 1 (Exec) |
| Scope | Unbounded | Rule 4 (Scope) | Rule 1 (Exec) |
| Dependencies | Wrong order | Rule 5 (Deps) | Rule 1 (Exec) |
| Decomposition | Task too big | Rule 6 (Decomp) | Rule 2 (Comp) |
| Context | No rationale | Rule 7 (Context) | Rule 3 (SC) |
| Risk Awareness | No mitigation | Rule 8 (Risk) | Rule 2 (Comp) |

## Worksheet Notation

When an issue is resolved to a different dimension, note it in the original worksheet:

```markdown
| Line | Quote | Category | Status |
|------|-------|----------|--------|
| 145 | "Check if success" | Vague | → SC (Rule 3) |
| 156 | "Handle errors" | Missing | Counted here |
```

**Legend:**
- `→ XX (Rule N)` = Moved to dimension XX per Rule N
- `Counted here` = This is the primary dimension
