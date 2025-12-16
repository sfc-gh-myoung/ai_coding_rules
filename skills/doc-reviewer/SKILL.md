---
name: doc-reviewer
description: Review project documentation (README, CONTRIBUTING, docs/*.md) for accuracy, completeness, clarity, consistency, staleness, and structure. Supports configurable file targets, single/collection review modes, cross-reference verification, and link validation. Triggers on keywords like "review docs", "audit documentation", "check README", "documentation quality", "docs staleness".
version: 1.0.0
author: AI Coding Rules Project
tags: [documentation-review, quality-audit, accuracy-check, link-validation, cross-reference, staleness-check, deployable]
dependencies: []
---

# Documentation Reviewer

## Purpose

Review project documentation using `PROMPT.md` (colocated in this skill folder) and write the full review output to `reviews/`. Evaluates documentation against 6 dimensions: Accuracy, Completeness, Clarity, Consistency, Staleness, and Structure.

## Use this skill when

- The user asks to **review documentation** (README, CONTRIBUTING, docs/*.md)
- The user asks for a **FULL / FOCUSED / STALENESS** documentation review
- The user wants to verify documentation is **current with the codebase**
- The user wants to check for **broken links** or **outdated references**

## Inputs

### Required

- `review_date`: `YYYY-MM-DD`
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `model`: preferred slug (e.g., `claude-sonnet45`)

### Optional

- `target_files`: list of file paths to review (defaults to project docs if not specified)
- `review_scope`: `single` | `collection` (default: `single`)
- `focus_area`: required if `review_mode` is `FOCUSED`

## Default Target Files

When `target_files` is not specified, the skill reviews:

- `./README.md` - Project overview and setup
- `./CONTRIBUTING.md` - Contribution guidelines  
- `./docs/*.md` - All documentation files in docs/ folder

## Output (required)

Write the full review to:

**Single scope (per-file reviews):**
`reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`

**Collection scope (consolidated review):**
`reviews/docs-collection-<model>-<YYYY-MM-DD>.md`

**No overwrites:** if that file already exists, write to:
`reviews/<name>-<model>-<YYYY-MM-DD>-01.md`, then `-02.md`, etc.

## Procedure (progressive disclosure)

Follow these workflows in order:

1. Input validation → `workflows/input-validation.md`
2. Model slugging → `workflows/model-slugging.md`
3. Review execution → `workflows/review-execution.md`
4. File write (no-overwrite) → `workflows/file-write.md`
5. Error handling → `workflows/error-handling.md`

## Hard requirements

- Do not ask the user to manually copy/paste the review into a file.
- Do not print the entire review in chat if file writing succeeds.
- If file writing fails unexpectedly, print:
  - `OUTPUT_FILE: <path>`
  - then the full Markdown review content.
- Cross-reference verification: List all code references and verify existence.
- Link validation: Verify internal links, flag external URLs for manual check.

## Review Dimensions

| Dimension | Score | Focus |
|-----------|-------|-------|
| **Accuracy** | X/5 | Is documentation current with the codebase? |
| **Completeness** | X/5 | Are all features, APIs, and workflows documented? |
| **Clarity** | X/5 | Is it user-friendly, intuitive, and accessible? |
| **Consistency** | X/5 | Does it follow project style and conventions? |
| **Staleness** | X/5 | Are tool versions, links, and examples current? |
| **Structure** | X/5 | Is organization logical and navigable? |

## Baseline Comparison

The skill checks for and uses as standards:

1. **Project rules** (e.g., `rules/801-project-readme.md`, `rules/802-project-contributing.md`)
2. **Standard documentation templates** when available
3. **General best practices** as fallback

## Examples

- `examples/full-review.md` - FULL review mode walkthrough
- `examples/focused-review.md` - FOCUSED review mode walkthrough
- `examples/staleness-review.md` - STALENESS review mode walkthrough
- `examples/edge-cases.md` - Ambiguous scenarios and resolutions

## Quick Validation Snippets

These inline checks can be run without external dependencies for input validation:

```python
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default documentation files
DEFAULT_DOC_FILES = ['README.md', 'CONTRIBUTING.md']
DEFAULT_DOC_DIRS = ['docs/']

def get_default_targets(project_root: str = '.') -> list[str]:
    """Returns list of default documentation files to review"""
    targets = []
    root = Path(project_root)
    
    # Check root-level docs
    for doc in DEFAULT_DOC_FILES:
        path = root / doc
        if path.exists():
            targets.append(str(path))
    
    # Check docs/ directory
    docs_dir = root / 'docs'
    if docs_dir.exists():
        targets.extend(str(f) for f in docs_dir.glob('*.md'))
    
    return targets

# Validate target_files exist and are markdown
def check_target_files(paths: list[str]) -> tuple[bool, list[str]]:
    """Returns (all_valid, list of error messages)"""
    errors = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            errors.append(f"File not found: {path}")
        elif not path.endswith('.md'):
            errors.append(f"Not a markdown file: {path}")
    return (len(errors) == 0, errors)

# Validate review_date format
def check_date(date_str: str) -> bool:
    """Must be YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate review_mode
VALID_MODES = {'FULL', 'FOCUSED', 'STALENESS'}
def check_mode(mode: str) -> bool:
    return mode.upper() in VALID_MODES

# Validate review_scope
VALID_SCOPES = {'single', 'collection'}
def check_scope(scope: str) -> bool:
    return scope.lower() in VALID_SCOPES

# Generate output filename (no-overwrite)
def get_output_path(doc_name: str, model: str, date: str, 
                    scope: str = 'single') -> str:
    """Returns next available filename"""
    if scope == 'collection':
        base = f"reviews/docs-collection-{model}-{date}"
    else:
        base = f"reviews/{doc_name}-{model}-{date}"
    
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    i = 1
    while Path(f"{base}-{i:02d}.md").exists():
        i += 1
    return f"{base}-{i:02d}.md"

# Extract code references from markdown
def extract_code_references(content: str) -> list[dict]:
    """Extract file paths, commands, and function references from markdown"""
    refs = []
    
    # File paths (backticked)
    file_patterns = re.findall(r'`([^`]+\.(py|md|yml|yaml|json|sh|ts|js|go))`', content)
    for match in file_patterns:
        refs.append({'type': 'file', 'reference': match[0]})
    
    # Directory paths
    dir_patterns = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_/]*/)(?:`|$)', content)
    for match in dir_patterns:
        refs.append({'type': 'directory', 'reference': match})
    
    # Task commands
    task_patterns = re.findall(r'`(task\s+[a-z:_-]+)`', content)
    for match in task_patterns:
        refs.append({'type': 'command', 'reference': match})
    
    return refs

# Extract links from markdown
def extract_links(content: str) -> list[dict]:
    """Extract all links from markdown content"""
    links = []
    
    # Markdown links [text](url)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, url in md_links:
        link_type = 'external' if url.startswith('http') else 'internal'
        if url.startswith('#'):
            link_type = 'anchor'
        links.append({'text': text, 'url': url, 'type': link_type})
    
    return links
```

## Version History

- **v1.0.0** (2025-12-16): Initial release
  - 6-dimension documentation review rubric
  - Configurable target files with sensible defaults
  - Single and collection review scopes
  - Cross-reference verification (code refs in docs)
  - Link validation (internal verified, external flagged)
  - Rule-aware baselines (801, 802 rules when present)
  - FULL/FOCUSED/STALENESS review modes
  - No-overwrite file safety
  - Deployable to other projects

