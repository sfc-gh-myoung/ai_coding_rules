# Project Documentation Organization

## Metadata

**SchemaVersion:** v3.3
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-04-22
**Keywords:** kw:documentation, kw:docs folder, file:docs/, file:ARCHITECTURE.md, kw:project structure, kw:architecture.md, kw:deployment.md, kw:adr, kw:github pages, kw:community health files, kw:cross-references, kw:link maintenance, kw:documentation organization
**TokenBudget:** ~3200
**ContextTier:** Medium
**Depends:** required:000-global-core.md

## Scope

**What This Rule Covers:**
Universal best practices for organizing project documentation files, including file placement conventions, extended documentation types, cross-reference management, and GitHub community health file standards.

**When to Load This Rule:**
- Organizing documentation for new or existing projects
- Creating extended documentation (ARCHITECTURE.md, DEPLOYMENT.md, ADRs)
- Setting up docs/ folder structure
- Managing cross-references between documentation files
- Implementing GitHub Pages or documentation site

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **800-project-changelog.md** - Changelog management standards
- **801-project-readme.md** - README best practices
- **802-project-contributing.md** - Contributing guidelines
- **803-project-git-workflow.md** - Git workflow management

### External Documentation
- [GitHub Community Health Files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) - Standard community health file conventions
- [GitHub Pages](https://docs.github.com/en/pages) - Documentation hosting from docs/ folder
- [CommonMark Spec](https://spec.commonmark.org/) - Authoritative Markdown specification
- [Architectural Decision Records](https://adr.github.io/) - ADR format and conventions
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure framework

## Contract

### Inputs and Prerequisites
- Project repository with existing or planned documentation
- Understanding of project complexity and documentation needs
- Knowledge of target audience (users vs contributors vs operators)

### Mandatory
- MUST keep community health files (README.md, CONTRIBUTING.md, LICENSE, CODE_OF_CONDUCT.md, SECURITY.md) in repository root
- MUST place extended documentation (ARCHITECTURE.md, DEPLOYMENT.md, ADRs) in docs/ folder
- MUST validate all cross-references when moving or renaming documentation files
- MUST use relative paths for internal documentation links

### Forbidden
- Placing ARCHITECTURE.md or DEPLOYMENT.md in repository root (use docs/)
- Creating documentation files without clear purpose or audience
- Using absolute URLs for internal documentation links
- Duplicating content across multiple documentation files
- Creating empty placeholder documentation files

### Execution Steps
1. Identify documentation type: community health file vs extended documentation
2. Place file in correct location (root vs docs/)
3. Add or update cross-references in related documentation
4. Validate all links point to correct relative paths
5. Run link validation before committing

### Output Format
Well-organized documentation structure:
```
/
├── README.md              # Project overview (root - GitHub UI)
├── CONTRIBUTING.md        # Contribution guide (root - GitHub UI)
├── LICENSE                # License file (root - GitHub UI)
├── CODE_OF_CONDUCT.md     # Community standards (root - GitHub UI)
├── SECURITY.md            # Security policy (root - GitHub UI)
├── docs/
│   ├── ARCHITECTURE.md    # Technical architecture
│   ├── DEPLOYMENT.md      # Deployment guide
│   ├── adr/               # Architectural Decision Records
│   │   ├── 0001-use-typescript.md
│   │   └── ...
│   └── guides/            # How-to guides (optional)
└── ...
```

### Validation
**Pre-Task-Completion Checks:**
- [ ] File placed in correct location per file type
- [ ] All internal links use relative paths
- [ ] Cross-references updated in affected files
- [ ] No duplicate content across files

**Success Criteria:**
- Documentation structure follows conventions
- All links resolve correctly
- Clear separation between user and contributor documentation
- No orphaned documentation files

### Design Principles
- **GitHub UI Integration** - Community health files in root for GitHub feature support
- **Progressive Disclosure** - Users find what they need without contributor noise
- **Single Source of Truth** - No content duplication across files
- **Maintainable Links** - Relative paths survive repository moves
- **Discoverability** - Clear index and navigation structure

### Post-Execution Checklist
- [ ] Community health files in repository root
- [ ] Extended documentation in docs/ folder
- [ ] All cross-references validated
- [ ] Link validation passes
- [ ] No duplicate content

## File Placement Standards

### Root Directory Files (GitHub UI Integration)

These files receive special treatment from GitHub's UI and MUST remain in the repository root:

- **README.md** - Project overview; rendered on repository home page
- **LICENSE** or **LICENSE.md** - License terms; enables license badge and detection
- **CONTRIBUTING.md** - Contribution guide; linked in PR creation UI
- **CODE_OF_CONDUCT.md** - Community standards; linked in issue/PR templates
- **SECURITY.md** - Security policy; Security tab integration
- **FUNDING.yml** - Sponsor information; enables Sponsor button (place in .github/)

**Why Root Placement Matters:**
- GitHub automatically links these files in relevant UI contexts
- Contributors expect to find them at repository root
- Search engines and tools index root-level files preferentially
- Forking preserves visibility of these community files

### docs/ Folder Files (Extended Documentation)

Extended documentation belongs in docs/ for these reasons:
- Keeps repository root clean and scannable
- Supports GitHub Pages deployment from docs/ folder
- Groups related documentation for easier navigation
- Separates user documentation from project metadata

**Standard docs/ Contents:**

- **ARCHITECTURE.md** - System design and technical decisions (Audience: Contributors)
- **DEPLOYMENT.md** - Deployment and operations guide (Audience: Operators)
- **TROUBLESHOOTING.md** - Common issues and solutions (Audience: Operators)
- **adr/** - Architectural Decision Records (Audience: Contributors)
- **api/** - API documentation (Audience: Developers)
- **guides/** - How-to guides and tutorials (Audience: Users)

## Cross-Reference Management

### Relative Path Conventions

**From root to docs/:**
```markdown
See [Architecture](docs/ARCHITECTURE.md) for technical details.
```

**From docs/ to root:**
```markdown
See [Quick Start](../README.md#quick-start) for installation.
```

**Within docs/:**
```markdown
See [Deployment](DEPLOYMENT.md) for production setup.
```

### Link Validation

Before committing documentation changes, validate links:

```bash
# Check for broken markdown links (if tool available)
find . -name "*.md" -exec grep -l '\[.*\](.*\.md' {} \; | \
  xargs -I{} sh -c 'echo "Checking: {}"; grep -oP "\[.*?\]\(\K[^)]+\.md[^)]*" {} | while read link; do
    if [[ "$link" != http* ]]; then
      dir=$(dirname {})
      target="$dir/$link"
      target="${target%%#*}"  # Remove anchors
      if [ ! -f "$target" ]; then echo "  BROKEN: $link"; fi
    fi
  done'
```

### Updating Cross-References When Moving Files

When moving a documentation file:

1. **Find all references to the file:**
   ```bash
   grep -rn "filename.md" --include="*.md" .
   ```

2. **Update each reference with new relative path**

3. **Verify no broken links remain:**
   ```bash
   grep -rn "old-path/filename.md" --include="*.md" .
   ```

## Extended Documentation Types

### ARCHITECTURE.md

**Location:** `docs/ARCHITECTURE.md`
**Audience:** Contributors, technical reviewers
**Purpose:** Document system design, patterns, and technical decisions

**Recommended Sections:**
- Overview / System Context
- Component Architecture
- Data Flow
- Key Design Decisions (or link to ADRs)
- Technology Stack
- Directory Structure

### DEPLOYMENT.md

**Location:** `docs/DEPLOYMENT.md`
**Audience:** Operators, DevOps engineers
**Purpose:** Document deployment procedures and operational concerns

**Recommended Sections:**
- Prerequisites
- Environment Setup
- Deployment Steps
- Configuration Reference
- Monitoring and Logging
- Troubleshooting

### Architectural Decision Records (ADRs)

**Location:** `docs/adr/`
**Audience:** Contributors, future maintainers
**Purpose:** Document significant technical decisions and their rationale

**Naming Convention:** `NNNN-title-with-hyphens.md` (e.g., `0001-use-typescript.md`)

**Standard ADR Template:**
```markdown
# N. Title

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded by [ADR-N](NNNN-title.md)

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this change?
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: ARCHITECTURE.md in Root

**Problem:**
```
/
├── README.md
├── ARCHITECTURE.md    # Wrong location
├── CONTRIBUTING.md
└── ...
```

**Why It Fails:**
- Clutters repository root with non-essential files
- Breaks GitHub Pages compatibility
- Inconsistent with industry conventions (Kubernetes, React, etc.)

**Correct Pattern:**
```
/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   └── ARCHITECTURE.md    # Correct location
└── ...
```

### Anti-Pattern 2: Absolute URLs for Internal Links

**Problem:**
```markdown
See [Architecture](https://github.com/org/repo/blob/main/docs/ARCHITECTURE.md)
```

**Why It Fails:**
- Breaks when repository is forked
- Breaks when branch names change
- Harder to maintain and update
- Fails in local documentation preview

**Correct Pattern:**
```markdown
See [Architecture](docs/ARCHITECTURE.md)
```

### Anti-Pattern 3: Duplicating Content Across Files

**Problem:**
Installation instructions appear in both README.md and CONTRIBUTING.md.

**Why It Fails:**
- Creates maintenance burden (update in multiple places)
- Content drifts out of sync over time
- Confuses readers about authoritative source

**Correct Pattern:**
- Define content in ONE location (usually README.md for user content)
- Link to that section from other files:
  ```markdown
  For installation, see [Quick Start](../README.md#quick-start).
  ```

## When NOT to Create Documentation

**Avoid creating documentation files when:**

- Project is simple enough that README.md covers everything
- Content would duplicate what's already documented elsewhere
- Documentation would immediately become stale
- Target audience doesn't need the information
- Code is self-documenting and well-commented

**Rule of Thumb:**
- Projects with <1000 LOC: README.md may be sufficient
- Projects with 1000-10000 LOC: Consider CONTRIBUTING.md and docs/ARCHITECTURE.md
- Projects with >10000 LOC: Full documentation structure recommended

## GitHub Pages Compatibility

To enable GitHub Pages from docs/ folder:

1. **Repository Settings** > **Pages** > **Source**: Select "Deploy from a branch"
2. **Branch**: Select main (or master) and `/docs` folder
3. **Add index.html or use Jekyll** to render markdown

**For static site generators:**
- **MkDocs**: Configure `docs_dir: docs` in mkdocs.yml
- **Docusaurus**: Place content in `docs/` by default
- **Jekyll**: Add `_config.yml` to docs/ folder

## Investigation Required

Before reorganizing documentation:

1. **Check existing structure:** `find . -name "*.md" -type f | head -20`
2. **Identify community health files:** `ls README.md CONTRIBUTING.md LICENSE* CODE_OF_CONDUCT.md SECURITY.md 2>/dev/null`
3. **Check for docs/ folder:** `ls -la docs/ 2>/dev/null || echo "No docs/ folder"`
4. **Find cross-references:** `grep -rn "\.md)" --include="*.md" . | head -20`
5. **Check GitHub Pages config:** Look in repository Settings > Pages
