# Structure Rubric (15 points)

## Scoring Criteria

### 5/5 (15 points): Excellent
- Logical information flow
- Clear heading hierarchy
- Easy navigation
- Table of contents (for long docs)
- Sections in appropriate order

### 4/5 (12 points): Good
- Mostly logical flow (1-2 ordering issues)
- Good heading hierarchy
- Navigation mostly clear

### 3/5 (9 points): Acceptable
- Some flow issues (3-4 ordering problems)
- Heading hierarchy has gaps
- Navigation somewhat confusing

### 2/5 (6 points): Needs Work
- Poor flow (>4 ordering problems)
- Heading hierarchy broken
- Hard to navigate

### 1/5 (3 points): Poor
- No logical structure
- Chaotic organization
- Impossible to navigate

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
- Follows standard order: 5/5
- 1-2 out of order: 4/5
- 3-4 out of order: 3/5
- 5+ out of order: 2/5
- No structure: 1/5

### Information Dependencies

Check that information is introduced in dependency order:

**Bad example:**
```markdown
## Configuration
Set DATABASE_URL in your .env file

## Installation
Create .env file from template
```
→ ❌ Configuration before installation

**Good example:**
```markdown
## Installation
Create .env file from template

## Configuration
Set DATABASE_URL in your .env file
```
→ ✅ Installation before configuration

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
Base score = 5/5 (15 points)

Information flow:
  Follows standard: 5/5
  1-2 out of order: 4/5 (-1 point)
  3-4 out of order: 3/5 (-2 points)
  5+ out of order: 2/5 (-3 points)
  No structure: 1/5 (-4 points)

Deductions:
  Broken heading hierarchy: -1 point per issue (up to -3)
  Missing TOC (>300 lines): -1 point
  Broken cross-references: -0.5 per link (up to -2)
  Poor section order: -0.5 per issue (up to -2)

Minimum score: 1/5 (3 points)
```

## Critical Gate

If documentation has no logical structure:
- Cap score at 1/5 (3 points) maximum
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
