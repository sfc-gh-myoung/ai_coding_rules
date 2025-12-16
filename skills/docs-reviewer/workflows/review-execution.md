# Workflow: Review Execution

## Inputs

- `resolved_targets`: list of file paths to review
- `review_date`: validated date string
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `review_scope`: `single` | `collection`
- `model_slug`: normalized model identifier
- `focus_area`: (optional) for FOCUSED mode
- `baseline_rules`: list of available documentation rules

## Steps

### Step 1: Read Review Prompt

Read `PROMPT.md` (colocated in this skill folder).

### Step 2: Read Target Documentation

For each file in `resolved_targets`:
- Read file contents
- Note file path and line count
- Extract existing structure (headings, sections)

### Step 3: Read Baseline Rules (if available)

If baseline rules exist, read them for comparison:
- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards

### Step 4: Perform Cross-Reference Verification

For each target file:
1. Extract code references (file paths, commands, functions)
2. Verify each reference exists in the codebase
3. Build Cross-Reference Verification Table

```python
import re
from pathlib import Path

def verify_references(content: str, doc_path: str) -> list[dict]:
    """Extract and verify code references"""
    results = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # File paths in backticks
        file_refs = re.findall(r'`([^`]+\.(py|md|yml|yaml|json|sh|ts|js|go|toml))`', line)
        for ref, ext in file_refs:
            exists = Path(ref).exists()
            results.append({
                'reference': ref,
                'type': 'file',
                'location': f"{doc_path}:{line_num}",
                'exists': exists
            })
        
        # Directory paths
        dir_refs = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_/]*/)`', line)
        for ref in dir_refs:
            exists = Path(ref).exists()
            results.append({
                'reference': ref,
                'type': 'directory',
                'location': f"{doc_path}:{line_num}",
                'exists': exists
            })
        
        # Task commands
        task_refs = re.findall(r'`(task\s+[a-z:_-]+)`', line)
        for ref in task_refs:
            # Check if task exists in Taskfile.yml
            taskfile = Path('Taskfile.yml')
            task_name = ref.replace('task ', '')
            exists = taskfile.exists()  # Basic check
            results.append({
                'reference': ref,
                'type': 'command',
                'location': f"{doc_path}:{line_num}",
                'exists': exists
            })
    
    return results
```

### Step 5: Perform Link Validation

For each target file:
1. Extract all links (internal, anchor, external)
2. Verify internal links exist
3. Verify anchor links point to valid headings
4. Flag external URLs for manual check
5. Build Link Validation Table

```python
import re
from pathlib import Path

def validate_links(content: str, doc_path: str) -> list[dict]:
    """Extract and validate links"""
    results = []
    lines = content.split('\n')
    
    # Extract headings for anchor validation
    headings = set()
    for line in lines:
        if line.startswith('#'):
            # Convert heading to anchor format
            heading_text = re.sub(r'^#+\s*', '', line)
            anchor = heading_text.lower()
            anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
            anchor = re.sub(r'\s+', '-', anchor)
            headings.add(f"#{anchor}")
    
    for line_num, line in enumerate(lines, 1):
        # Markdown links [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
        for text, url in links:
            if url.startswith('http'):
                link_type = 'external'
                status = 'manual_check'
            elif url.startswith('#'):
                link_type = 'anchor'
                status = 'valid' if url in headings else 'broken'
            else:
                link_type = 'internal'
                # Resolve relative path
                doc_dir = Path(doc_path).parent
                target = doc_dir / url
                status = 'valid' if target.exists() else 'broken'
            
            results.append({
                'url': url,
                'text': text,
                'type': link_type,
                'location': f"{doc_path}:{line_num}",
                'status': status
            })
    
    return results
```

### Step 6: Perform Review

Using the rubric from `PROMPT.md`:
1. Score each dimension (1-5)
2. Identify Critical, Should Fix, and Minor issues
3. Generate specific recommendations with line numbers
4. Complete Documentation Perspective Checklist

**Review mode determines scope:**
- `FULL`: All 6 dimensions, all tables
- `FOCUSED`: Only specified `focus_area` dimension
- `STALENESS`: Dimensions 5-6 (Staleness, Structure) + Link Validation

### Step 7: Generate Review Output

Produce the final review Markdown content:
- Scores table
- Verification tables (Cross-Reference, Link Validation, Baseline Compliance)
- Issues by severity
- Specific recommendations
- Documentation Perspective Checklist

**Scope determines output structure:**
- `single`: One complete review per document
- `collection`: Consolidated review with per-document sections

## Output

- `review_markdown`: full Markdown review content (single file or collection)
- `doc_name`: base name for output filename

