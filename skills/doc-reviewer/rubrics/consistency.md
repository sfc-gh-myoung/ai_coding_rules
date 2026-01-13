# Consistency Rubric (5 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Scoring Criteria

### 10/10 (5 points): Perfect
- Consistent formatting throughout
- Terminology used uniformly
- Follows project conventions (if rules exist)
- Code style consistent
- Naming patterns consistent

### 9/10 (4.5 points): Near-Perfect
- 1 minor inconsistency
- Terminology uniform
- Follows conventions

### 8/10 (4 points): Excellent
- Mostly consistent (1-2 minor inconsistencies)
- Terminology mostly uniform
- Mostly follows conventions

### 7/10 (3.5 points): Good
- 2-3 minor inconsistencies
- Terminology mostly uniform
- Mostly follows conventions

### 6/10 (3 points): Acceptable
- 3-4 inconsistencies
- Some terminology variations
- Partially follows conventions

### 5/10 (2.5 points): Borderline
- 4-5 inconsistencies
- Some terminology variations
- Partially follows conventions

### 4/10 (2 points): Needs Work
- 5-6 inconsistencies
- Terminology inconsistent
- Rarely follows conventions

### 3/10 (1.5 points): Poor
- 6-7 inconsistencies
- Terminology inconsistent
- Rarely follows conventions

### 2/10 (1 point): Very Poor
- 7-9 inconsistencies
- Terminology chaotic
- Ignores conventions

### 1/10 (0.5 points): Inadequate
- 9-12 inconsistencies
- Chaotic terminology
- Ignores conventions

### 0/10 (0 points): Not Consistent
- >12 inconsistencies
- Pervasive chaos
- Unreadable

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

- **MyApp** - Occurrences: 15, Should Be: Standard
- **my-app** - Occurrences: 8, Should Be: Inconsistent
- **myapp** - Occurrences: 3, Should Be: Inconsistent
- **My App** - Occurrences: 2, Should Be: Inconsistent

**Fix:** Use one consistent name (usually the official one)

### Technical Term Consistency

Track terminology:

- **"API endpoint"** - Term 2: "API route", Usage: Both used, Preferred: Choose one
- **"function"** - Term 2: "method", Usage: Both used, Preferred: Context-dependent (OK)
- **"config"** - Term 2: "configuration", Usage: Both used, Preferred: Choose one

**Penalty:** -0.15 points per inconsistent term pair (up to -1)

## Convention Compliance

### Check for Project Rules

If project has documentation rules:
- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards

**Verify compliance:**

- **801** - Requirement: Badges at top, Compliant?: Yes, Fix: -
- **801** - Requirement: Installation section, Compliant?: Yes, Fix: -
- **801** - Requirement: MIT license badge, Compliant?: No, Fix: Add badge

**Non-compliance penalty:** -0.25 points per violation (up to -1)

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
Base score = 10/10 (5 points)

Formatting inconsistencies: -0.15 each (up to -1)
Terminology variations: -0.15 each (up to -1)
Convention violations: -0.25 each (up to -1)
Code style inconsistencies: -0.15 each (up to -0.5)

Minimum score: 0/10 (0 points)
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

- **Product name** - Variations Found: MyApp, my-app, myapp, Occurrences: 15, 8, 3, Recommendation: Standardize on "MyApp"
- **Code blocks** - Variations Found: Fenced, indented, Occurrences: 45, 3, Recommendation: Convert 3 indented to fenced
- **List markers** - Variations Found: -, *, Occurrences: 32, 5, Recommendation: Convert 5 * to -
- **Heading caps** - Variations Found: Title, sentence, mixed, Occurrences: 15, 12, 3, Recommendation: Standardize on title case

**Total inconsistencies:** 4 issues → Score: 6/10 (3 points)
