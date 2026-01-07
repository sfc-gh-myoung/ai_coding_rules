# Consistency Rubric (5 points)

## Scoring Criteria

### 5/5 (5 points): Excellent
- Consistent formatting throughout
- Terminology used uniformly
- Follows project conventions (if rules exist)
- Code style consistent
- Naming patterns consistent

### 4/5 (4 points): Good
- Mostly consistent (1-2 minor inconsistencies)
- Terminology mostly uniform
- Mostly follows conventions

### 3/5 (3 points): Acceptable
- Some inconsistencies (3-4 issues)
- Some terminology variations
- Partially follows conventions

### 2/5 (2 points): Needs Work
- Many inconsistencies (5-7 issues)
- Terminology inconsistent
- Rarely follows conventions

### 1/5 (1 point): Poor
- Highly inconsistent (>7 issues)
- Chaotic terminology
- Ignores conventions

## Formatting Consistency

### Code Block Formatting

Check consistency:

**Inconsistent:**
````markdown
```python
code here
```

    code here (indented)

```
code here (no language)
```
````

**Consistent:**
````markdown
```python
code here
```

```python
more code here
```
````

### List Formatting

Check marker consistency:

**Inconsistent:**
```markdown
- Item 1
* Item 2  ← Different marker
- Item 3
```

**Consistent:**
```markdown
- Item 1
- Item 2
- Item 3
```

### Heading Capitalization

Check heading style consistency:

**Inconsistent:**
```markdown
## Getting started
## Configuration
## usage examples
```

**Consistent (title case):**
```markdown
## Getting Started
## Configuration
## Usage Examples
```

Or consistent (sentence case):
```markdown
## Getting started
## Configuration
## Usage examples
```

## Terminology Consistency

### Name Variations

Track how project/product is referenced:

| Variation | Occurrences | Should Be |
|-----------|-------------|-----------|
| MyApp | 15 | ✅ Standard |
| my-app | 8 | ❌ Inconsistent |
| myapp | 3 | ❌ Inconsistent |
| My App | 2 | ❌ Inconsistent |

**Fix:** Use one consistent name (usually the official one)

### Technical Term Consistency

Track terminology:

| Term 1 | Term 2 | Usage | Preferred |
|--------|--------|-------|-----------|
| "API endpoint" | "API route" | Both used | Choose one |
| "function" | "method" | Both used | Context-dependent (OK) |
| "config" | "configuration" | Both used | Choose one |

**Penalty:** -0.3 points per inconsistent term pair (up to -2)

## Convention Compliance

### Check for Project Rules

If project has documentation rules:
- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards

**Verify compliance:**

| Rule | Requirement | Compliant? | Fix |
|------|-------------|------------|-----|
| 801 | Badges at top | ✅ Yes | - |
| 801 | Installation section | ✅ Yes | - |
| 801 | MIT license badge | ❌ No | Add badge |

**Non-compliance penalty:** -0.5 points per violation (up to -2)

### Style Guide Adherence

If project has style guide, check adherence:

**Example violations:**
- Using tabs when spaces required
- Wrong quote style ('' vs "")
- Inconsistent indentation (2 vs 4 spaces)

## Code Style Consistency

### Language Consistency

In code examples, use consistent style:

**Inconsistent Python:**
```python
# Example 1: snake_case
def process_data():
    pass

# Example 2: camelCase
def processData():  ← Inconsistent!
    pass
```

**Consistent:**
```python
# All examples: snake_case
def process_data():
    pass

def format_output():
    pass
```

### Import Style

**Inconsistent:**
```python
# Example 1
import os
import sys

# Example 2
from pathlib import Path  ← Different style
from typing import List
```

**Consistent:** Choose one style and stick to it

## Scoring Formula

```
Base score = 5/5 (5 points)

Formatting inconsistencies: -0.3 each (up to -2)
Terminology variations: -0.3 each (up to -2)
Convention violations: -0.5 each (up to -2)
Code style inconsistencies: -0.3 each (up to -1)

Minimum score: 1/5 (1 point)
```

## Common Consistency Issues

### Issue 1: Mixed List Markers

**Problem:**
```markdown
- Item 1
* Item 2
- Item 3
```

**Fix:** Use `-` throughout (or `*` throughout)

### Issue 2: Inconsistent Product Names

**Problem:**
```markdown
Welcome to MyApp...
Configure my-app...
Run myapp...
```

**Fix:** Use "MyApp" consistently (official name)

### Issue 3: Mixed Code Block Formats

**Problem:**
````markdown
```python
code here
```

    indented code here

```
code without language
```
````

**Fix:** Use fenced blocks with language tags consistently

### Issue 4: Capitalization Variations

**Problem:**
```markdown
## Installation
## configuration
## Usage Examples
```

**Fix:** Use consistent capitalization (title case or sentence case)

## Consistency Checklist

During review, verify:

- [ ] Code blocks use same format (fenced with language)
- [ ] Lists use same marker (- or *)
- [ ] Headings use consistent capitalization
- [ ] Product/project name consistent
- [ ] Technical terms used consistently
- [ ] Code style consistent across examples
- [ ] If project rules exist, documentation complies
- [ ] Quote style consistent
- [ ] Indentation consistent
- [ ] Link format consistent

## Consistency Tracking Table

Use during review:

| Category | Variations Found | Occurrences | Recommendation |
|----------|------------------|-------------|----------------|
| Product name | MyApp, my-app, myapp | 15, 8, 3 | Standardize on "MyApp" |
| Code blocks | Fenced, indented | 45, 3 | Convert 3 indented to fenced |
| List markers | -, * | 32, 5 | Convert 5 * to - |
| Heading caps | Title, sentence, mixed | 15, 12, 3 | Standardize on title case |

**Total inconsistencies:** 4 issues → Score: 3/5 (3 points)
