# Phase 1: Auto-Generate RULES_INDEX.md - Technical Specification

## Overview

Build `scripts/build_rules_index.py` to automatically generate `RULES_INDEX.md` from template file metadata, eliminating manual maintenance and ensuring accuracy.

---

## Goals

### Primary Goals
1. ✅ Extract metadata from all template files
2. ✅ Generate RULES_INDEX.md table automatically
3. ✅ Integrate into build process (`task rule:all`)
4. ✅ Validate metadata completeness
5. ✅ Reduce maintenance burden

### Non-Goals (Out of Scope)
- ❌ Generate AGENTS.md (stays manual)
- ❌ Generate EXAMPLE_PROMPT.md (stays manual)
- ❌ Modify template files (read-only operation)
- ❌ Validate rule content (only metadata)

---

## Current State Analysis

### Existing RULES_INDEX.md Structure

**File**: `RULES_INDEX.md` (94 lines, manually maintained)

**Structure:**
```markdown
**Keywords:** rules index, rule discovery, semantic search...
**Version:** 2.4
**LastUpdated:** 2025-10-23

# Rules Index

[Introduction text - keep this manual]

## How to Use This Index
[Instructions - keep this manual]

|| File | Type | Purpose (one line) | Scope | Keywords/Hints | Depends On |
||------|------|---------------------|-------|----------------|------------|
|| `000-global-core.md` | Auto-attach | ... | ... | ... | — |
|| `001-memory-bank.md` | Auto-attach | ... | ... | ... | `000-global-core.md` |
[... 70+ more rows]
```

**Key Observations:**
1. Header section (lines 1-18): **Keep manual** (metadata, introduction, instructions)
2. Table section (lines 19-94): **Auto-generate** (rule catalog)
3. Table has 6 columns
4. Each row represents one rule file
5. Dependencies shown in last column

---

### Existing Template Metadata Format

**Example from `000-global-core.md`:**

```markdown
**Description:** The core, universally-applied operating contract for a reliable and safe workflow.
**AutoAttach:** true
**Type:** Auto-attach
**Keywords:** PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, prompt engineering
**Version:** 6.5
**LastUpdated:** 2025-10-29
**Depends:** None

**TokenBudget:** ~300
**ContextTier:** Critical

# Global Core Guidelines

## Purpose
Establish the foundational operating contract...
```

**Metadata Fields Used in RULES_INDEX:**
- **Keywords** → Keywords/Hints column
- **Type** → Type column
- **Description** → Purpose column (first sentence)
- **Depends** → Depends On column

**Metadata Fields NOT Used in RULES_INDEX:**
- AutoAttach (redundant with Type)
- Version (not shown in table)
- LastUpdated (not shown in table)
- TokenBudget (not shown in table, but useful for future)
- ContextTier (not shown in table, but useful for future)

**Scope Column:**
- Not in metadata - must be inferred or kept manual
- Examples: "Universal", "Snowflake SQL & modeling", "Python ecosystem"

---

## Proposed Solution

### Script Architecture

```python
# scripts/build_rules_index.py

"""
Auto-generate RULES_INDEX.md from template file metadata.

Usage:
    python scripts/build_rules_index.py [--check] [--dry-run]
    
    --check: Verify current RULES_INDEX.md is up-to-date (CI mode)
    --dry-run: Print generated content without writing
"""

import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class RuleMetadata:
    """Extracted metadata from a rule template file."""
    filename: str           # e.g., "000-global-core.md"
    filepath: Path          # Full path to template
    description: str        # One-line purpose
    type: str              # "Auto-attach" or "Agent Requested"
    keywords: str          # Comma-separated keywords
    depends: str           # Dependencies or "—" if None
    scope: str             # Manually provided or inferred
    
    # Optional (for future use)
    token_budget: Optional[str] = None
    context_tier: Optional[str] = None

def extract_metadata(filepath: Path) -> RuleMetadata:
    """Extract metadata from a single template file."""
    pass

def scan_templates(templates_dir: Path) -> list[RuleMetadata]:
    """Recursively scan templates/ directory for rule files."""
    pass

def generate_table_row(metadata: RuleMetadata) -> str:
    """Generate markdown table row for one rule."""
    pass

def generate_rules_index(rules: list[RuleMetadata]) -> str:
    """Generate complete RULES_INDEX.md content."""
    pass

def main():
    """Main entry point."""
    pass
```

---

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scan Phase                                               │
│    - Walk templates/ directory recursively                  │
│    - Find all *.md files (exclude README, etc.)            │
│    - Sort by filename (000, 001, 100, 101, etc.)          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Extract Phase                                            │
│    - Read each template file                                │
│    - Parse metadata lines (**Keywords:**, **Type:**, etc.) │
│    - Extract first sentence of Description                  │
│    - Handle special cases (missing metadata, etc.)         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Transform Phase                                          │
│    - Convert "None" to "—" for dependencies                │
│    - Format Type ("Auto-attach" or "Agent Requested")      │
│    - Infer Scope from category (100-199 = Snowflake, etc.) │
│    - Sort rules by filename                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Generate Phase                                           │
│    - Read RULES_INDEX.md header (manual section)           │
│    - Generate table with all rules                          │
│    - Write to RULES_INDEX.md (or stdout if --dry-run)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Implementation

### 1. Metadata Extraction

**Function**: `extract_metadata(filepath: Path) -> RuleMetadata`

**Algorithm:**
```python
def extract_metadata(filepath: Path) -> RuleMetadata:
    """Extract metadata from template file."""
    
    # Read file
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Initialize metadata
    metadata = {
        'filename': filepath.name,
        'filepath': filepath,
        'description': '',
        'type': 'Agent Requested',  # Default
        'keywords': '',
        'depends': '—',
        'scope': '',
    }
    
    # Parse metadata lines (first ~20 lines)
    for line in lines[:20]:
        if line.startswith('**Description:**'):
            # Extract: "**Description:** Text here" -> "Text here"
            metadata['description'] = line.split('**Description:**')[1].strip()
        
        elif line.startswith('**Type:**'):
            # Extract: "**Type:** Auto-attach" -> "Auto-attach"
            type_val = line.split('**Type:**')[1].strip()
            metadata['type'] = type_val
        
        elif line.startswith('**Keywords:**'):
            # Extract: "**Keywords:** key1, key2, key3" -> "key1, key2, key3"
            metadata['keywords'] = line.split('**Keywords:**')[1].strip()
        
        elif line.startswith('**Depends:**'):
            # Extract: "**Depends:** None" -> "—"
            # Extract: "**Depends:** 000-global-core" -> "000-global-core.md"
            depends_val = line.split('**Depends:**')[1].strip()
            if depends_val.lower() in ['none', '—', '']:
                metadata['depends'] = '—'
            else:
                # Ensure .md extension
                deps = [d.strip() for d in depends_val.split(',')]
                deps = [d if d.endswith('.md') else f"{d}.md" for d in deps]
                metadata['depends'] = ', '.join(deps)
        
        elif line.startswith('**TokenBudget:**'):
            metadata['token_budget'] = line.split('**TokenBudget:**')[1].strip()
        
        elif line.startswith('**ContextTier:**'):
            metadata['context_tier'] = line.split('**ContextTier:**')[1].strip()
    
    # Infer scope from filename prefix
    metadata['scope'] = infer_scope(filepath.name)
    
    return RuleMetadata(**metadata)
```

**Scope Inference:**
```python
def infer_scope(filename: str) -> str:
    """Infer scope category from filename prefix."""
    
    prefix = filename.split('-')[0]  # "000" from "000-global-core.md"
    
    scope_map = {
        '000': 'Universal',
        '001': 'Project continuity',
        '002': 'All rules',
        '003': 'Universal context engineering',
        '004': 'Agent tool development',
        '100': 'Snowflake SQL & modeling',
        '101': 'Streamlit apps',
        '102': 'Demo SQL',
        '103': 'Performance',
        '104': 'Pipelines',
        '105': 'Cost governance',
        '106': 'Modeling',
        '107': 'Security',
        '108': 'Ingestion',
        '109': 'Notebooks',
        '110': 'ML registry',
        '111': 'Observability',
        '112': 'Snowflake CLI',
        '113': 'Feature Store',
        '114': 'AISQL',
        '119': 'Warehouse management',
        '120': 'SPCS',
        '121': 'Snowpipe',
        '122': 'Dynamic Tables',
        '123': 'Object tagging',
        '124': 'Data quality',
        '200': 'Python core',
        '201': 'Linting',
        '202': 'Config validation',
        '203': 'Project setup',
        '204': 'Documentation',
        '205': 'Classes',
        '206': 'Testing',
        '210': 'FastAPI',
        '220': 'CLI',
        '230': 'Validation',
        '240': 'Data generation',
        '250': 'Flask',
        '251': 'Datetime',
        '252': 'Pandas',
        '300': 'Bash',
        '310': 'Zsh',
        '400': 'Docker',
        '500': 'Analytics',
        '600': 'Governance',
        '700': 'BI',
        '800': 'Changelog',
        '801': 'README',
        '805': 'Contributing',
        '806': 'Git workflow',
        '820': 'Automation',
        '900': 'Demo',
        '901': 'Data generation',
    }
    
    return scope_map.get(prefix, 'General')
```

---

### 2. Template Scanning

**Function**: `scan_templates(templates_dir: Path) -> list[RuleMetadata]`

**Algorithm:**
```python
def scan_templates(templates_dir: Path) -> list[RuleMetadata]:
    """Recursively scan templates/ for rule files."""
    
    rules = []
    
    # Walk directory tree
    for filepath in sorted(templates_dir.rglob('*.md')):
        # Skip documentation files
        if filepath.name in ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md']:
            continue
        
        # Skip discovery files
        if filepath.name in ['AGENTS.md', 'EXAMPLE_PROMPT.md', 'RULES_INDEX.md']:
            continue
        
        # Extract metadata
        try:
            metadata = extract_metadata(filepath)
            rules.append(metadata)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
            continue
    
    # Sort by filename (000, 001, 100, 101a, etc.)
    rules.sort(key=lambda r: r.filename)
    
    return rules
```

---

### 3. Table Generation

**Function**: `generate_table_row(metadata: RuleMetadata) -> str`

**Algorithm:**
```python
def generate_table_row(metadata: RuleMetadata) -> str:
    """Generate markdown table row."""
    
    # Format: || `file` | Type | Purpose | Scope | Keywords | Depends ||
    
    # Wrap filename in backticks
    filename = f"`{metadata.filename}`"
    
    # Type as-is
    type_str = metadata.type
    
    # Description (first sentence only if multiple)
    purpose = metadata.description.split('.')[0].strip()
    if purpose and not purpose.endswith('.'):
        purpose += '.'  # Ensure period at end
    
    # Scope
    scope = metadata.scope
    
    # Keywords (as-is, already comma-separated)
    keywords = metadata.keywords
    
    # Dependencies (wrap each in backticks)
    if metadata.depends == '—':
        depends = '—'
    else:
        deps = [f"`{d.strip()}`" for d in metadata.depends.split(',')]
        depends = ', '.join(deps)
    
    # Build row
    row = f"|| {filename} | {type_str} | {purpose} | {scope} | {keywords} | {depends} |"
    
    return row
```

---

### 4. Full Generation

**Function**: `generate_rules_index(rules: list[RuleMetadata]) -> str`

**Algorithm:**
```python
def generate_rules_index(rules: list[RuleMetadata]) -> str:
    """Generate complete RULES_INDEX.md content."""
    
    # Read current RULES_INDEX.md to preserve header
    current_index_path = Path('RULES_INDEX.md')
    
    if current_index_path.exists():
        current_content = current_index_path.read_text()
        
        # Find table start (line with "|| File | Type |")
        lines = current_content.split('\n')
        header_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith('|| File | Type |'):
                # Found table header, keep everything before this
                header_lines = lines[:i]
                break
        
        # Reconstruct header
        header = '\n'.join(header_lines) + '\n'
    else:
        # No existing file, create default header
        header = """**Keywords:** rules index, rule discovery, semantic search, agent requested, auto-attach, rule governance, context engineering, tool design

# Rules Index

This index helps agents select the correct rule quickly through semantic keyword matching.

**How to Use This Index:**
- Browse by category (000=Core, 100=Snowflake, 200=Python, 300=Shell, 400=Docker, 500-900=Domain-specific)
- Search Keywords column for semantic discovery (technologies, patterns, use cases)
- Check Depends On column for prerequisite rules
- Auto-attach rules load automatically; Agent Requested rules load on-demand

"""
    
    # Generate table
    table_header = "|| File | Type | Purpose (one line) | Scope | Keywords/Hints | Depends On |"
    table_separator = "||------|------|---------------------|-------|----------------|------------|"
    
    table_rows = [generate_table_row(rule) for rule in rules]
    
    # Combine
    content = header + table_header + '\n' + table_separator + '\n' + '\n'.join(table_rows) + '\n'
    
    return content
```

---

### 5. Main Entry Point

**Function**: `main()`

**Algorithm:**
```python
def main():
    """Main entry point."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Auto-generate RULES_INDEX.md from template metadata'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if RULES_INDEX.md is up-to-date (exit 1 if not)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print generated content without writing to file'
    )
    parser.add_argument(
        '--templates-dir',
        type=Path,
        default=Path('templates'),
        help='Path to templates directory (default: templates)'
    )
    
    args = parser.parse_args()
    
    # Scan templates
    print(f"Scanning {args.templates_dir}...")
    rules = scan_templates(args.templates_dir)
    print(f"Found {len(rules)} rule files")
    
    # Generate content
    content = generate_rules_index(rules)
    
    # Handle modes
    if args.dry_run:
        # Print to stdout
        print("\n--- Generated RULES_INDEX.md ---\n")
        print(content)
        return 0
    
    if args.check:
        # Compare with existing
        current_path = Path('RULES_INDEX.md')
        if not current_path.exists():
            print("ERROR: RULES_INDEX.md does not exist")
            return 1
        
        current_content = current_path.read_text()
        if current_content.strip() == content.strip():
            print("✓ RULES_INDEX.md is up-to-date")
            return 0
        else:
            print("✗ RULES_INDEX.md is out of date")
            print("Run: python scripts/build_rules_index.py")
            return 1
    
    # Write to file
    output_path = Path('RULES_INDEX.md')
    output_path.write_text(content)
    print(f"✓ Generated {output_path}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
```

---

## Integration Points

### 1. Taskfile.yml Integration

**Add new task:**
```yaml
tasks:
  # ... existing tasks ...
  
  rules:index:
    desc: "Generate RULES_INDEX.md from template metadata"
    cmds:
      - uv run scripts/build_rules_index.py
  
  rules:index:check:
    desc: "Check if RULES_INDEX.md is up-to-date"
    cmds:
      - uv run scripts/build_rules_index.py --check
  
  rule:all:
    desc: "Generate all rule formats (universal, cursor, copilot, cline)"
    cmds:
      - task: rules:index              # NEW: Generate index first
      - task: rule:universal
      - task: rule:cursor
      - task: rule:copilot
      - task: rule:cline
```

---

### 2. CI/CD Integration

**Add to `.github/workflows/validate-rules.yml`:**
```yaml
- name: Check RULES_INDEX.md is up-to-date
  run: |
    uv run scripts/build_rules_index.py --check
    # Exits 1 if out of date
```

---

### 3. Pre-commit Hook (Optional)

**Create `.git/hooks/pre-commit`:**
```bash
#!/bin/bash
# Auto-generate RULES_INDEX.md before commit

python scripts/build_rules_index.py

# Add to commit if changed
git add RULES_INDEX.md
```

---

## Validation & Testing

### Test Cases

#### Test 1: Basic Extraction
**Input**: `templates/core/000-global-core.md`
**Expected Output**:
```
|| `000-global-core.md` | Auto-attach | The core, universally-applied operating contract for a reliable and safe workflow. | Universal | PLAN mode, ACT mode, workflow, safety... | — |
```

#### Test 2: Dependencies
**Input**: `templates/python/210-python-fastapi-core.md`
**Expected Output**:
```
|| `210-python-fastapi-core.md` | Agent Requested | FastAPI core patterns... | FastAPI | FastAPI, API, REST... | `000-global-core.md`, `200-python-core.md` |
```

#### Test 3: Missing Metadata
**Input**: File with incomplete metadata
**Expected**: Warning message, use defaults

#### Test 4: Subdirectories
**Input**: Files in `templates/snowflake/`, `templates/python/`
**Expected**: All files found and processed

#### Test 5: Sorting
**Input**: Files: 101a, 100, 001, 210, 000
**Expected**: Sorted: 000, 001, 100, 101a, 210

---

### Validation Checks

**The script should validate:**
1. ✅ All template files have **Keywords** field
2. ✅ All template files have **Type** field
3. ✅ All template files have **Description** field
4. ⚠️ Warning if **Depends** is missing (default to "—")
5. ⚠️ Warning if **TokenBudget** or **ContextTier** missing (optional)

**Error Handling:**
- Missing critical fields → Print warning, use defaults
- Malformed metadata → Print error, skip file
- Empty templates directory → Error and exit

---

## Dependencies

### Python Requirements

**Add to `pyproject.toml`:**
```toml
[project]
dependencies = [
    # ... existing ...
]

[project.optional-dependencies]
dev = [
    # ... existing ...
]
```

**No new dependencies needed!** Uses only Python standard library:
- `pathlib` (file operations)
- `argparse` (CLI arguments)
- `dataclasses` (data structures)

---

## Success Criteria

### Functional Requirements
- [ ] Script extracts metadata from all template files
- [ ] Generated RULES_INDEX.md matches manual format
- [ ] Preserves manual header section
- [ ] Handles subdirectories correctly
- [ ] Sorts rules by filename
- [ ] Validates metadata completeness

### Non-Functional Requirements
- [ ] Runs in < 5 seconds (for 70+ files)
- [ ] Clear error messages for missing metadata
- [ ] Works on macOS, Linux, Windows
- [ ] Integrated into `task rule:all`
- [ ] CI check fails if index is stale

---

## Timeline Estimate

**Implementation:**
- Metadata extraction: 1 hour
- Template scanning: 30 minutes
- Table generation: 1 hour
- Testing & debugging: 1.5 hours
- Integration (Taskfile, CI): 30 minutes
- Documentation: 30 minutes

**Total: ~5 hours**

---

## Deliverables

### Phase 1 Deliverables
1. ✅ `scripts/build_rules_index.py` (fully functional)
2. ✅ Updated `Taskfile.yml` with `rules:index` task
3. ✅ Updated `.github/workflows/validate-rules.yml` with check
4. ✅ Generated `RULES_INDEX.md` (auto-generated)
5. ✅ Test suite validating all functionality
6. ✅ Documentation in script docstrings

---

## Rollback Plan

If auto-generation causes issues:

1. **Immediate**: Use current manual RULES_INDEX.md
2. **Short-term**: Fix bugs in script, regenerate
3. **Long-term**: If unfixable, return to manual maintenance

**Risk**: Low - script is read-only (doesn't modify templates)

---

## Questions Before Implementation

### Q1: Scope Field Strategy

The "Scope" column is currently manual (not in metadata). Should we:

**Option A**: Infer from filename prefix (as shown in spec)
- Pro: Automatic, no manual work
- Con: Less flexible, might be inaccurate

**Option B**: Add **Scope:** metadata field to templates
- Pro: Explicit, accurate
- Con: Requires updating 70+ template files

**Option C**: Keep manual in RULES_INDEX.md header
- Pro: No changes needed
- Con: Defeats purpose of auto-generation

**Recommendation**: Option A (infer from prefix) - can always add metadata later

---

### Q2: Validation Strictness

Should missing metadata be:

**Option A**: Error (fail generation)
- Pro: Ensures quality
- Con: Blocks generation until fixed

**Option B**: Warning (use defaults, continue)
- Pro: Permissive, always generates
- Con: May hide issues

**Option C**: Configurable (`--strict` flag)
- Pro: Flexibility
- Con: More complexity

**Recommendation**: Option B (warnings) for now, add strictness later

---

### Q3: Header Preservation Strategy

Current plan: Preserve everything before table header line.

**Is this acceptable?** Or should we:
- Parse header section more carefully?
- Use a marker comment like `<!-- AUTO-GENERATED TABLE BELOW -->`?
- Split into header.md + generated table?

**Current approach seems safest** - agree?

---

## Approval Checkpoint

**Before I implement, please confirm:**

1. ✅ Overall approach is acceptable
2. ✅ Metadata extraction algorithm looks correct
3. ✅ Table generation format matches expectations
4. ✅ Integration points (Taskfile, CI) are appropriate
5. ✅ Timeline estimate (~5 hours) is reasonable

**Any concerns or changes before I start coding?**

---

*This specification provides a complete blueprint for Phase 1 implementation. Upon approval, I'll proceed with building the script.*

