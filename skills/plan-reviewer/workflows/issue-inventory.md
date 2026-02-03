# Issue Inventory System

**Purpose:** Track issues across multiple reviews of the same plan to enable consistent scoring and progress tracking.

## Issue ID Format

Each issue gets a unique identifier based on dimension:

| Prefix | Dimension | Example |
|--------|-----------|---------|
| `E###` | Executability | E001, E002, E015 |
| `C###` | Completeness | C001, C002 |
| `S###` | Success Criteria | S001, S002 |
| `SC###` | Scope | SC001, SC002 |
| `D###` | Dependencies | D001, D002 |
| `DC###` | Decomposition | DC001, DC002 |
| `CX###` | Context | CX001, CX002 |
| `R###` | Risk Awareness | R001, R002 |

**Numbering:** Sequential within each dimension, starting at 001.

## Inventory Format

### Master Inventory Table

| Issue ID | Line | Description | Status | Severity | First Found | Last Checked | Resolution |
|----------|------|-------------|--------|----------|-------------|--------------|------------|
| E001 | 186 | Undefined threshold "near" | OPEN | HIGH | 2026-01-15 | 2026-01-21 | |
| E002 | 245 | Missing else branch after check | FIXED | MEDIUM | 2026-01-15 | 2026-01-21 | Added else at L248 |
| E003 | 312 | "as needed" without criteria | OPEN | HIGH | 2026-01-21 | 2026-01-21 | |
| C001 | 89 | No error recovery for API call | WONTFIX | LOW | 2026-01-15 | 2026-01-21 | Out of scope |

### Column Definitions

- **Issue ID:** Unique identifier (prefix + 3-digit number)
- **Line:** Line number where issue occurs (may shift between versions)
- **Description:** Brief description of the issue (max 50 chars)
- **Status:** Current status (see Status Values below)
- **Severity:** HIGH (blocks execution) | MEDIUM (degrades quality) | LOW (minor)
- **First Found:** Date issue was first identified (YYYY-MM-DD)
- **Last Checked:** Date issue was last verified (YYYY-MM-DD)
- **Resolution:** How issue was resolved (if FIXED or WONTFIX)

## Status Values

| Status | Meaning | Score Impact |
|--------|---------|--------------|
| `OPEN` | Issue identified, not yet resolved | Counted as issue |
| `FIXED` | Issue resolved in current version | Not counted |
| `WONTFIX` | Intentionally not addressing (documented reason) | Not counted |
| `REGRESSION` | Previously fixed, now broken again | Counted as issue + flagged |

### Status Transitions

```
OPEN → FIXED (issue resolved)
OPEN → WONTFIX (intentionally deferred)
FIXED → REGRESSION (fix undone or broken)
WONTFIX → OPEN (decision reversed)
REGRESSION → FIXED (re-fixed)
```

## Usage During Scoring

### Step 1: Load Prior Inventory (if exists)

```bash
# Check for existing inventory
INVENTORY_FILE="reviews/plan-reviews/{plan-name}-inventory.md"
if [ -f "$INVENTORY_FILE" ]; then
    echo "Loading prior inventory from: $INVENTORY_FILE"
else
    echo "No prior inventory - creating new"
fi
```

### Step 2: Match Current Issues Against Inventory

For each issue found in current review:

1. **Check by line number:** Does issue exist at same line in inventory?
   - YES → Same issue, update `Last Checked` date
   - NO → Continue to step 2

2. **Check by description:** Does similar issue exist within ±20 lines?
   - YES → Same issue (line shifted), update Line and `Last Checked`
   - NO → NEW issue, assign next available ID

3. **For NEW issues:**
   - Assign next ID in sequence (e.g., E004 if E001-E003 exist)
   - Set `First Found` and `Last Checked` to current date
   - Set Status to OPEN

### Step 3: Check for Fixed Issues

For each OPEN issue in prior inventory:

1. **Search current plan:** Does issue still exist?
   - YES → Keep OPEN, update `Last Checked`
   - NO → Mark FIXED, add `Resolution` note

2. **Verify fix is genuine:**
   - Issue removed entirely → FIXED
   - Issue moved elsewhere → Update Line, keep OPEN
   - Issue replaced with different problem → FIXED + add NEW issue

### Step 4: Detect Regressions

For each FIXED issue in prior inventory:

1. **Search current plan:** Has issue returned?
   - YES → Mark REGRESSION, update `Last Checked`
   - NO → Keep FIXED

2. **Flag regressions in review output:**
   - REGRESSION issues get special attention
   - Include in "Critical Issues" section

## Integration with Review Workflow

### During Review (Phase 2: Fill Worksheets)

When filling dimension worksheets:

1. Record issue in worksheet as normal
2. Check inventory for matching issue
3. If match found: Use existing Issue ID
4. If no match: Assign new Issue ID
5. Note inventory status in worksheet

**Worksheet Enhancement:**

| Pass | Line | Quote | Category | Issue ID | Inventory Status |
|------|------|-------|----------|----------|------------------|
| 1 | 186 | "near threshold" | Threshold | E001 | OPEN (prior) |
| 1 | 312 | "as needed" | Conditional | E003 | NEW |

### After Review (Before File Write)

1. Update inventory with current findings
2. Calculate status changes
3. Include inventory summary in review output

### Inventory Summary in Review Output

```markdown
## Issue Inventory Summary

**Prior Review:** {baseline_date}
**Current Review:** {current_date}

| Status | Count | Change |
|--------|-------|--------|
| OPEN | 5 | -2 |
| FIXED | 3 | +3 |
| WONTFIX | 1 | 0 |
| REGRESSION | 0 | 0 |
| NEW | 2 | +2 |

**Net Progress:** 3 fixed, 2 new = +1 improvement
```

## Inventory File Management

### File Location

```
reviews/plan-reviews/{plan-name}-inventory.md
```

### File Format

```markdown
# Issue Inventory: {Plan Name}

**Created:** {first_review_date}
**Last Updated:** {current_date}
**Plan File:** {plan_path}

## Active Issues (OPEN)

| Issue ID | Line | Description | Severity | First Found |
|----------|------|-------------|----------|-------------|
| E001 | 186 | Undefined threshold | HIGH | 2026-01-15 |
| E003 | 312 | Vague conditional | HIGH | 2026-01-21 |

## Resolved Issues (FIXED)

| Issue ID | Line | Description | First Found | Fixed Date | Resolution |
|----------|------|-------------|-------------|------------|------------|
| E002 | 245 | Missing else branch | 2026-01-15 | 2026-01-21 | Added else at L248 |

## Deferred Issues (WONTFIX)

| Issue ID | Line | Description | Reason |
|----------|------|-------------|--------|
| C001 | 89 | No API error recovery | Out of scope for this plan |

## Regression History

| Issue ID | Original Fix | Regression Date | Current Status |
|----------|--------------|-----------------|----------------|
| (none) | | | |
```

### Update Protocol

1. Read existing inventory file
2. Apply changes from current review
3. Write updated inventory file
4. Include inventory reference in review output

## Consistency Benefits

### Why Track Issues?

1. **Same issue → same ID:** Prevents counting same issue differently across reviews
2. **Progress tracking:** Clear view of what's fixed vs. remaining
3. **Regression detection:** Catch fixes that get undone
4. **Score stability:** Same issues → same base score across models

### Score Impact

- OPEN issues: Counted toward dimension score
- FIXED issues: Not counted (improvement)
- WONTFIX issues: Not counted (intentional)
- REGRESSION issues: Counted + flagged as critical

## Example Workflow

### First Review (No Prior Inventory)

1. Review finds 5 executability issues
2. Create inventory: E001-E005, all OPEN
3. Score reflects 5 blocking issues
4. Save inventory file

### Second Review (After Fixes)

1. Load prior inventory (E001-E005)
2. Review current plan
3. Match: E001 still at L186 → OPEN
4. Match: E002 not found → FIXED
5. Match: E003 at L310 (was L312) → OPEN (line shifted)
6. New: L400 has new issue → E006 NEW
7. Update inventory
8. Score reflects 4 issues (E001, E003, E005, E006)

### DELTA Review

1. Use inventory for precise issue tracking
2. Comparison table shows FIXED/NEW/OPEN
3. Score delta explained by issue changes
