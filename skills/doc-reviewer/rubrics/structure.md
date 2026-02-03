# Structure Rubric (15 points)

## Mandatory Verification Table (REQUIRED)

**CRITICAL:** You MUST create and fill this table BEFORE calculating score.

### Why This Is Required

- **Eliminates order variance:** Same doc → same table → same score
- **Prevents missed issues:** Systematic check catches all
- **Provides evidence:** Table shows exactly what was evaluated
- **Enables audit:** Users can verify scoring decisions

### Verification Table Template

**Section Order Check (for README):**

| Expected Order | Section | Present? | Actual Position | In Order? |
|----------------|---------|----------|-----------------|-----------|
| 1 | Title & badges | Y/N | | Y/N |
| 2 | Brief description | Y/N | | Y/N |
| 3 | Key features | Y/N | | Y/N |
| 4 | Quick start | Y/N | | Y/N |
| 5 | Installation | Y/N | | Y/N |
| 6 | Usage | Y/N | | Y/N |
| 7 | Configuration | Y/N | | Y/N |
| 8 | Documentation links | Y/N | | Y/N |
| 9 | Contributing | Y/N | | Y/N |
| 10 | License | Y/N | | Y/N |

**Heading Hierarchy:**

| Line | Heading | Level | Expected Level | Valid? |
|------|---------|-------|----------------|--------|
| 1 | Project Title | H1 | H1 | Y |
| 10 | Getting Started | H3 | H2 | N (skip) |
| 25 | Installation | H2 | H2 | Y |

**Navigation Check (if >300 lines):**

| Element | Present? |
|---------|----------|
| Table of contents | Y/N |
| Section links work | Y/N |
| Cross-references valid | Y/N |

### Verification Protocol (5 Steps)

**Step 1: Create Empty Tables**
- Copy all templates above
- Do NOT start reading doc yet

**Step 2: Read Doc Systematically**
- Note each section heading with line number
- Check heading levels (H1, H2, H3...)
- Check if sections follow expected order

**Step 3: Verify Navigation**
- If doc >300 lines: Check for TOC
- Test all internal links
- Test all cross-references

**Step 4: Calculate Totals**
- Count sections out of order
- Count heading hierarchy violations
- Note missing navigation elements

**Step 5: Look Up Score**
- Use section order result as base
- Apply deductions for hierarchy/navigation issues
- Record score with table evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 3
**Points:** Raw × (3/2) = Raw × 1.5

## Scoring Criteria

### 10/10 (15 points): Perfect
- Logical information flow
- Clear heading hierarchy
- Easy navigation
- Table of contents (for long docs)
- Sections in appropriate order

### 9/10 (13.5 points): Near-Perfect
- Excellent flow (1 minor issue)
- Perfect heading hierarchy
- Clear navigation
- TOC present if needed

### 8/10 (12 points): Excellent
- Mostly logical flow (1-2 ordering issues)
- Good heading hierarchy
- Navigation mostly clear
- TOC present if needed

### 7/10 (10.5 points): Good
- Good flow (2-3 ordering issues)
- Good heading hierarchy
- Navigation mostly clear

### 6/10 (9 points): Acceptable
- Some flow issues (3-4 ordering problems)
- Heading hierarchy has 1-2 gaps
- Navigation somewhat confusing

### 5/10 (7.5 points): Borderline
- Flow issues (4-5 ordering problems)
- Heading hierarchy has gaps
- Navigation confusing

### 4/10 (6 points): Needs Work
- Poor flow (5-6 ordering problems)
- Heading hierarchy broken
- Hard to navigate

### 3/10 (4.5 points): Poor
- Poor flow (>6 ordering problems)
- Heading hierarchy broken
- Very hard to navigate

### 2/10 (3 points): Very Poor
- Minimal logical structure
- Chaotic organization
- Navigation impossible

### 1/10 (1.5 points): Inadequate
- No logical structure
- Chaotic organization
- Impossible to navigate

### 0/10 (0 points): No Structure
- Completely unorganized
- Cannot find information

## Information Flow

### Expected README Order

Standard structure for README.md:

1. **Title & badges** (project name, build status, version)
2. **Brief description** (1-2 sentences: what it does)
3. **Key features** (bullet list, 3-7 items)
4. **Quick start** (fastest path to working state)
5. **Installation** (detailed setup)
6. **Usage** (basic examples)
7. **Configuration** (options, environment)
8. **Documentation** (links to full docs)
9. **Contributing** (how to contribute)
10. **License** (license type)

**Scoring:**
- Follows standard order: 10/10
- 1-2 out of order: 8/10
- 3-4 out of order: 6/10
- 5-6 out of order: 4/10
- 7+ out of order: 2/10
- No structure: 0/10

### Information Dependencies

Check that information is introduced in dependency order:

**Bad example:**
```markdown
## Configuration
Set DATABASE_URL in your .env file

## Installation
Create .env file from template
```
→  Configuration before installation

**Good example:**
```markdown
## Installation
Create .env file from template

## Configuration
Set DATABASE_URL in your .env file
```
→  Installation before configuration

## Heading Hierarchy

### Proper Nesting

Headings must nest properly:

**Bad:**
```markdown
# Title
### Subsection  ← Skipped H2!
## Section      ← Out of order!
```

**Good:**
```markdown
# Title
## Section
### Subsection
#### Detail
```

### Heading Consistency

Check heading format consistency:

**Inconsistent:**
```markdown
## installation
## Configuration
## USAGE
```

**Consistent:**
```markdown
## Installation
## Configuration
## Usage
```

## Navigation

### Internal Links

For long documents (>300 lines), require:

- [ ] Table of contents at top
- [ ] Section links in TOC
- [ ] "Back to top" links for long sections

**Example TOC:**
```markdown
## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
```

### Cross-References

Check that cross-references work:

**Broken:**
```markdown
See the setup guide (link broken/missing)
```

**Working:**
```markdown
See the [setup guide](docs/setup.md)
```

## Page Length

**Optimal lengths:**
- README.md: 100-400 lines
- Tutorial: 50-200 lines per page
- Reference: As needed, but paginated

**Issues:**
- Single-page >1000 lines → Consider splitting
- Many pages <50 lines → Consider combining

## Scoring Formula

```
Base score = 10/10 (15 points)

Information flow:
  Follows standard: 10/10
  1-2 out of order: 8/10 (-0.75 points)
  3-4 out of order: 6/10 (-1.5 points)
  5-6 out of order: 4/10 (-2.25 points)
  7+ out of order: 2/10 (-3 points)
  No structure: 0/10 (-3.75 points)

Deductions:
  Broken heading hierarchy: -0.5 point per issue (up to -1.5)
  Missing TOC (>300 lines): -0.5 point
  Broken cross-references: -0.25 per link (up to -1)
  Poor section order: -0.25 per issue (up to -1)

Minimum score: 0/10 (0 points)
```

## Critical Gate

If documentation has no logical structure:
- Cap score at 2/10 (3 points) maximum
- Mark as CRITICAL issue
- Users cannot find information

## Common Structure Issues

### Issue 1: Configuration Before Installation

**Problem:**
```markdown
## Configuration
Set these environment variables...

## Installation
Run npm install...
```

**Fix:** Move Installation before Configuration

### Issue 2: Missing Table of Contents

**Problem:** 800-line README with no navigation

**Fix:**
```markdown
## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
...
```

### Issue 3: Broken Heading Hierarchy

**Problem:**
```markdown
# Project Title
### Getting Started  ← Skipped H2
## Installation       ← Wrong level
```

**Fix:**
```markdown
# Project Title
## Getting Started
### Prerequisites
### Installation
```

### Issue 4: Poor Logical Flow

**Problem:**
```markdown
## Advanced Usage
(complex patterns)

## Basic Usage
(simple patterns)
```

**Fix:** Basic before Advanced

## Structure Checklist

During review, verify:

- [ ] README follows standard order
- [ ] Information introduced in logical sequence
- [ ] Prerequisites before installation
- [ ] Installation before configuration
- [ ] Basic usage before advanced
- [ ] Headings nested properly (no skipped levels)
- [ ] Heading capitalization consistent
- [ ] TOC present if >300 lines
- [ ] All cross-references work
- [ ] Sections are right-sized (not too long/short)

## Non-Issues (Do NOT Count as Structure Problems)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Intentional Order Variation
**Pattern:** Non-standard order that makes sense for context
**Example:** "Quick Start" before "Installation" for experienced users
**Why NOT an issue:** Order variation is justified by purpose
**Action:** Remove from table with note "Intentional order"

### Pattern 2: Short Documents
**Pattern:** Document <100 lines without TOC
**Example:** Simple README without table of contents
**Why NOT an issue:** TOC not needed for short docs
**Action:** Remove from table with note "Short doc, TOC not required"

### Pattern 3: Alternative Structures
**Pattern:** Non-README documentation with different structure
**Example:** API reference that starts with endpoints, not overview
**Why NOT an issue:** Different doc types have different structures
**Action:** Remove from table with note "Alternative doc type"

### Pattern 4: Flat Hierarchy by Design
**Pattern:** Document intentionally using only H2 headings
**Example:** FAQ with all questions at same level
**Why NOT an issue:** Flat structure is appropriate for content
**Action:** Remove from table with note "Flat hierarchy by design"
