# Project Structure Recommendations: Template-Based Rule Generation

## Current State Analysis

### Current Structure (Confusing)
```
ai_coding_rules_gitlab/
├── 000-global-core.md              ← Source templates (70+ files in root)
├── 001-memory-bank.md
├── 100-snowflake-core.md
├── ... (67+ more .md files)
├── AGENTS.md                        ← Discovery guide
├── AGENTS_V2.md                     ← Alternative discovery guide
├── EXAMPLE_PROMPT.md                ← Baseline prompt
├── RULES_INDEX.md                   ← Catalog
├── generate_agent_rules.py          ← Generator script
├── .cursor/rules/*.mdc              ← Generated (45 files, Cursor format)
├── .github/instructions/*.md        ← Generated (Copilot format)
├── .clinerules/*.md                 ← Generated (Cline format)
└── [no rules/ directory]            ← Should be generated universal format
```

**Problems:**
1. **Source templates scattered in root** - Hard to distinguish from other project files
2. **No `rules/` directory by default** - Confusing when AGENTS_V2.md references `rules/`
3. **Multiple discovery files in root** - AGENTS.md, AGENTS_V2.md, EXAMPLE_PROMPT.md unclear relationship
4. **Generated outputs mixed with source** - `.cursor/`, `.github/`, `.clinerules/` alongside templates

---

## Industry Best Practices Analysis

### Pattern 1: Hugo/Jekyll Static Site Generators
```
project/
├── content/              ← Source templates
│   ├── posts/
│   └── pages/
├── public/               ← Generated output (gitignored)
└── config.yml
```
**Pros:** Clear separation, generated output gitignored
**Cons:** Assumes single output format

### Pattern 2: Sphinx Documentation
```
project/
├── source/               ← Source RST/MD files
│   ├── conf.py
│   └── index.rst
├── build/                ← Generated HTML/PDF (gitignored)
└── Makefile
```
**Pros:** Clear source/build separation
**Cons:** Build artifacts gitignored (not suitable if we want generated rules in git)

### Pattern 3: Terraform/Pulumi IaC
```
project/
├── templates/            ← Template files
├── modules/              ← Reusable components
├── generated/            ← Generated configs (sometimes gitignored)
└── terraform.tfstate
```
**Pros:** Templates clearly separated
**Cons:** Complex for our use case

### Pattern 4: Cookiecutter/Yeoman Project Templates
```
cookiecutter-project/
├── {{cookiecutter.project}}/  ← Template directory
│   ├── src/
│   └── README.md
└── cookiecutter.json          ← Template variables
```
**Pros:** Template nature is obvious
**Cons:** Single output directory structure

### Pattern 5: Multi-Target Build Systems (Make, CMake, Bazel)
```
project/
├── src/                  ← Source files
├── build/                ← Build artifacts per target
│   ├── release/
│   └── debug/
└── Makefile
```
**Pros:** Multiple output targets, clear source location
**Cons:** Build directory structure can be complex

---

## Recommended Options for AI Coding Rules

### Option 1: Source-First with Generated Outputs (RECOMMENDED)

```
ai_coding_rules_gitlab/
├── templates/                      ← Source templates (canonical)
│   ├── 000-global-core.md
│   ├── 001-memory-bank.md
│   ├── 100-snowflake-core.md
│   └── ... (70+ template files)
│
├── discovery/                      ← Discovery system templates
│   ├── AGENTS.md                   ← Primary discovery guide
│   ├── AGENTS_V2.md                ← Alternative (staging)
│   ├── EXAMPLE_PROMPT.md           ← Baseline prompt template
│   └── RULES_INDEX.md              ← Catalog template
│
├── generated/                      ← All generated outputs (gitignored OR committed)
│   ├── universal/                  ← Universal format (rules/)
│   │   ├── 000-global-core.md
│   │   ├── AGENTS.md               ← Copied from discovery/
│   │   ├── RULES_INDEX.md          ← Copied from discovery/
│   │   └── ... (70+ files)
│   ├── cursor/                     ← Cursor format (.cursor/rules/)
│   │   └── rules/
│   │       └── *.mdc
│   ├── copilot/                    ← Copilot format (.github/instructions/)
│   │   └── instructions/
│   │       └── *.md
│   └── cline/                      ← Cline format (.clinerules/)
│       └── *.md
│
├── scripts/                        ← Generation tooling
│   ├── generate_agent_rules.py
│   └── validate_agent_rules.py
│
├── tests/                          ← Test suite
├── memory-bank/                    ← Example memory bank
├── pyproject.toml
├── Taskfile.yml
└── README.md
```

**Pros:**
- ✅ **Crystal clear separation** - Templates vs generated outputs
- ✅ **Discoverable** - `templates/` name makes purpose obvious
- ✅ **Flexible** - Can gitignore `generated/` or commit it
- ✅ **Scalable** - Easy to add new output formats
- ✅ **Clean root** - Project metadata files stay visible
- ✅ **Industry standard** - Matches Hugo, Sphinx, cookiecutter patterns

**Cons:**
- ⚠️ Requires migration of 70+ files from root to `templates/`
- ⚠️ All existing paths in documentation need updating
- ⚠️ Generated outputs in subdirectories (not IDE-expected locations)

**Migration Path:**
```bash
# 1. Create structure
mkdir -p templates discovery generated/universal scripts

# 2. Move templates
mv *.md templates/  # All rule files
mv templates/README.md templates/CHANGELOG.md templates/CONTRIBUTING.md .  # Restore docs

# 3. Move discovery files
mv AGENTS.md AGENTS_V2.md EXAMPLE_PROMPT.md RULES_INDEX.md discovery/

# 4. Move scripts
mv generate_agent_rules.py validate_agent_rules.py scripts/

# 5. Update Taskfile.yml to use new paths
# 6. Update generate_agent_rules.py --source flag default
# 7. Generate outputs: task rule:all
```

---

### Option 2: Templates with Rules/ as Default Output (HYBRID)

```
ai_coding_rules_gitlab/
├── templates/                      ← Source templates
│   ├── 000-global-core.md
│   └── ... (70+ files)
│
├── rules/                          ← Generated universal output (DEFAULT)
│   ├── 000-global-core.md          ← Generated from templates/
│   ├── AGENTS.md
│   ├── RULES_INDEX.md
│   └── ... (70+ files)
│
├── .cursor/rules/*.mdc             ← Generated Cursor format
├── .github/instructions/*.md       ← Generated Copilot format
├── .clinerules/*.md                ← Generated Cline format
│
├── discovery/                      ← Discovery guide templates
│   ├── AGENTS.md
│   ├── EXAMPLE_PROMPT.md
│   └── RULES_INDEX.md
│
├── scripts/
│   └── generate_agent_rules.py
├── README.md
└── Taskfile.yml
```

**Pros:**
- ✅ **`rules/` is default** - Matches AGENTS_V2.md expectations
- ✅ **Clear template location** - `templates/` for source
- ✅ **IDE formats in expected locations** - `.cursor/rules/`, `.github/instructions/`
- ✅ **Simpler migration** - Only templates move, outputs stay where expected

**Cons:**
- ⚠️ Generated outputs in root pollute project structure
- ⚠️ Mix of generated and non-generated files in root
- ⚠️ Still requires moving 70+ files to `templates/`

**Migration Path:**
```bash
# 1. Create structure
mkdir -p templates discovery scripts rules

# 2. Move templates
mv *.md templates/
mv templates/{README,CHANGELOG,CONTRIBUTING}.md .

# 3. Move discovery files
mv AGENTS.md AGENTS_V2.md EXAMPLE_PROMPT.md RULES_INDEX.md discovery/

# 4. Generate universal output as default
task rule:universal  # Creates rules/
```

---

### Option 3: Minimal Change - Templates Subdirectory Only

```
ai_coding_rules_gitlab/
├── templates/                      ← Source templates (NEW)
│   ├── 000-global-core.md
│   └── ... (70+ files)
│
├── rules/                          ← Generated universal (NEW)
│   ├── 000-global-core.md
│   ├── AGENTS.md                   ← Copied from root
│   └── ... (70+ files)
│
├── AGENTS.md                       ← Discovery guide (root)
├── AGENTS_V2.md                    ← Alternative (root)
├── EXAMPLE_PROMPT.md               ← Baseline prompt (root)
├── RULES_INDEX.md                  ← Catalog (root)
│
├── .cursor/rules/*.mdc             ← Generated
├── .github/instructions/*.md       ← Generated
├── .clinerules/*.md                ← Generated
│
├── generate_agent_rules.py         ← Script (root)
└── README.md
```

**Pros:**
- ✅ **Minimal disruption** - Only templates move
- ✅ **Quick migration** - Small change to implement
- ✅ **Backward compatible** - Discovery files stay in root

**Cons:**
- ❌ **Still cluttered root** - Many files in root
- ❌ **Discovery files not clearly marked as templates** - Ambiguous purpose
- ⚠️ **Doesn't fully solve the problem** - Root still confusing

---

### Option 4: Source-in-Place (Keep Current + Add rules/)

```
ai_coding_rules_gitlab/
├── 000-global-core.md              ← Source templates (root)
├── 001-memory-bank.md
├── ... (70+ files)
│
├── rules/                          ← Generated universal output
│   ├── 000-global-core.md          ← Clean version
│   ├── AGENTS.md
│   └── ...
│
├── AGENTS.md                       ← Discovery (root)
├── EXAMPLE_PROMPT.md
├── RULES_INDEX.md
│
├── .cursor/rules/*.mdc             ← Generated
├── .github/instructions/*.md       ← Generated
├── .clinerules/*.md                ← Generated
└── README.md
```

**Pros:**
- ✅ **Zero migration** - No files move
- ✅ **Works immediately** - Just add `rules/` generation
- ✅ **No breaking changes** - All existing paths valid

**Cons:**
- ❌ **Confusing duplication** - Source `000-global-core.md` vs `rules/000-global-core.md`
- ❌ **Root clutter** - 70+ template files + generated `rules/` + discovery files
- ❌ **Not industry standard** - No clear template separation
- ❌ **High collision risk** - Easy to edit wrong file

**Not Recommended** - Doesn't solve the core problem

---

## Detailed Comparison Matrix

| Aspect | Option 1: Source-First | Option 2: Hybrid | Option 3: Minimal | Option 4: In-Place |
|--------|------------------------|------------------|-------------------|---------------------|
| **Clarity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Industry Standard** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Migration Effort** | ⚠️ High | ⚠️ Medium | ✅ Low | ✅ None |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Root Cleanliness** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Discoverability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Breaking Changes** | ⚠️ Yes | ⚠️ Yes | ⚠️ Yes | ✅ No |
| **Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## Recommendation: Option 1 (Source-First) with Phased Migration

### Why Option 1 is Best

1. **Industry Alignment**: Matches proven patterns from Hugo, Sphinx, cookiecutter
2. **Future-Proof**: Easy to add new formats without cluttering root
3. **Clarity**: Anyone cloning repo immediately understands structure
4. **Professional**: Looks like a mature, well-organized project
5. **Maintainable**: Clear separation reduces errors (editing wrong file)
6. **Discoverable**: New contributors find templates easily

### Phased Migration Plan (Minimize Disruption)

#### Phase 1: Create Structure (No Breaking Changes)
```bash
# Create new directories
mkdir -p templates discovery generated/universal scripts

# Copy (don't move) templates to new location
cp *.md templates/
rm templates/{README,CHANGELOG,CONTRIBUTING}.md

# Copy discovery files
cp AGENTS.md AGENTS_V2.md EXAMPLE_PROMPT.md RULES_INDEX.md discovery/

# Move scripts
mv generate_agent_rules.py validate_agent_rules.py scripts/
```

**Result**: Both old and new structures exist (transition period)

#### Phase 2: Update Tooling (Backward Compatible)
```bash
# Update Taskfile.yml to support both locations
# Add --source flag to use templates/ or root
# Default to templates/ if it exists, fall back to root

# Update generate_agent_rules.py
# Auto-detect source location:
#   1. Try templates/ first
#   2. Fall back to root if templates/ empty
```

**Result**: Tools work with both structures

#### Phase 3: Update Documentation
- Update README.md to explain new structure
- Update CONTRIBUTING.md with new file locations
- Add migration guide for external users
- Update all cross-references

**Result**: Documentation reflects new structure

#### Phase 4: Announce Transition
- Create MIGRATION.md guide
- Update CHANGELOG.md with breaking change notice
- Tag current version as "pre-migration"
- Give users 1-2 weeks notice

**Result**: Users prepared for change

#### Phase 5: Remove Old Structure
```bash
# Remove template files from root
rm 0*.md 1*.md 2*.md 3*.md 4*.md 5*.md 6*.md 7*.md 8*.md 9*.md

# Remove old discovery files
rm AGENTS.md EXAMPLE_PROMPT.md RULES_INDEX.md
# Keep AGENTS_V2.md if still needed, or move to discovery/

# Update .gitignore
echo "# Keep generated outputs out of git (optional)" >> .gitignore
echo "generated/" >> .gitignore
```

**Result**: Clean structure, only source templates remain

---

## Recommended Structure Details (Option 1 Enhanced)

### Complete Directory Layout

```
ai_coding_rules_gitlab/
│
├── templates/                           ← SOURCE TEMPLATES (canonical)
│   ├── core/                            ← Core foundation rules
│   │   ├── 000-global-core.md
│   │   ├── 001-memory-bank.md
│   │   ├── 002-rule-governance.md
│   │   ├── 003-context-engineering.md
│   │   └── 004-tool-design-for-agents.md
│   │
│   ├── snowflake/                       ← Snowflake domain (100-series)
│   │   ├── 100-snowflake-core.md
│   │   ├── 101-snowflake-streamlit-core.md
│   │   ├── 101a-snowflake-streamlit-visualization.md
│   │   └── ... (20+ files)
│   │
│   ├── python/                          ← Python domain (200-series)
│   │   ├── 200-python-core.md
│   │   ├── 201-python-lint-format.md
│   │   ├── 210-python-fastapi-core.md
│   │   └── ... (15+ files)
│   │
│   ├── shell/                           ← Shell scripting (300-series)
│   │   ├── 300-bash-scripting-core.md
│   │   ├── 310-zsh-scripting-core.md
│   │   └── ...
│   │
│   ├── infrastructure/                  ← Infrastructure (400-series)
│   │   └── 400-docker-best-practices.md
│   │
│   ├── analytics/                       ← Analytics & BI (500-700-series)
│   │   ├── 500-data-science-analytics.md
│   │   ├── 600-data-governance-quality.md
│   │   └── 700-business-analytics.md
│   │
│   ├── project-mgmt/                    ← Project management (800-series)
│   │   ├── 800-project-changelog-rules.md
│   │   ├── 801-project-readme-rules.md
│   │   └── ...
│   │
│   └── demos/                           ← Demo patterns (900-series)
│       ├── 900-demo-creation.md
│       └── 901-data-generation-modeling.md
│
├── discovery/                           ← DISCOVERY SYSTEM TEMPLATES
│   ├── AGENTS.md                        ← Primary discovery guide
│   ├── EXAMPLE_PROMPT.md                ← Baseline prompt
│   ├── RULES_INDEX.md                   ← Rule catalog (maybe generated?)
│   └── templates/                       ← Discovery file templates
│       └── AGENTS.template.md           ← If AGENTS.md is also generated
│
├── generated/                           ← GENERATED OUTPUTS (gitignored or committed)
│   ├── universal/                       ← Universal format (rules/)
│   │   ├── 000-global-core.md
│   │   ├── AGENTS.md                    ← Copied from discovery/
│   │   ├── RULES_INDEX.md
│   │   └── ... (70+ clean markdown files)
│   │
│   ├── cursor/                          ← Cursor-specific
│   │   └── rules/
│   │       ├── 000-global-core.mdc
│   │       └── ... (*.mdc files)
│   │
│   ├── copilot/                         ← GitHub Copilot
│   │   └── instructions/
│   │       ├── 000-global-core.md
│   │       └── ... (with YAML frontmatter)
│   │
│   └── cline/                           ← Cline format
│       ├── 000-global-core.md
│       └── ... (plain markdown)
│
├── scripts/                             ← BUILD TOOLS
│   ├── generate_agent_rules.py          ← Main generator
│   ├── validate_agent_rules.py          ← Validator
│   ├── build_rules_index.py             ← Generate RULES_INDEX.md (if automated)
│   └── migrate_to_templates.sh          ← Migration helper script
│
├── tests/                               ← TEST SUITE
│   ├── test_generate_agent_rules.py
│   ├── test_rule_validation.py
│   └── fixtures/
│
├── examples/                            ← USAGE EXAMPLES
│   ├── memory-bank/                     ← Example memory bank
│   │   ├── projectbrief.md
│   │   ├── activeContext.md
│   │   └── ...
│   └── integration/
│       ├── cursor-setup.md
│       ├── copilot-setup.md
│       └── cli-setup.md
│
├── docs/                                ← PROJECT DOCUMENTATION
│   ├── architecture.md                  ← System architecture
│   ├── migration-guide.md               ← Migration from old structure
│   ├── adding-rules.md                  ← How to add new rules
│   └── rule-format-spec.md              ← Rule file specification
│
├── .cursor/                             ← PROJECT-LEVEL IDE CONFIGS
│   └── (empty or project-specific)
│
├── .github/                             ← GITHUB WORKFLOWS
│   └── workflows/
│       ├── validate-rules.yml
│       └── generate-rules.yml
│
├── pyproject.toml                       ← Python project config
├── Taskfile.yml                         ← Task automation
├── .gitignore                           ← Git ignore (optionally ignore generated/)
├── README.md                            ← Main documentation
├── CHANGELOG.md                         ← Version history
├── CONTRIBUTING.md                      ← Contribution guide
└── LICENSE                              ← License file
```

### Benefits of Subdirectory Organization

**templates/** subdirectories:
- ✅ **Logical grouping** - Rules organized by domain
- ✅ **Easier navigation** - Find rules by category
- ✅ **Reduced clutter** - Each dir has ~10-20 files instead of 70+
- ✅ **Scalable** - Easy to add new domains without root pollution
- ⚠️ **Requires generator updates** - Must recursively scan subdirectories

**Alternative: Flat templates/**
- ✅ **Simpler generator** - Just read `templates/*.md`
- ✅ **Easier migration** - Direct move, no reorganization
- ⚠️ **70+ files in one directory** - Still cluttered

**Recommendation**: Start flat, add subdirectories later if needed

---

## Generator Script Updates Required

### Update generate_agent_rules.py

```python
# Current (line 42-52)
python ai_coding_rules/generate_agent_rules.py --agent cursor [--dry-run]

# Proposed
python scripts/generate_agent_rules.py --agent cursor [--source templates] [--dry-run]
```

**Key Changes:**
1. Add `--source` flag (default: `templates/` if exists, else `.`)
2. Update default output paths:
   - `universal` → `generated/universal/` or `rules/`
   - `cursor` → `generated/cursor/rules/` or `.cursor/rules/`
   - `copilot` → `generated/copilot/instructions/` or `.github/instructions/`
   - `cline` → `generated/cline/` or `.clinerules/`
3. Add migration mode: `--legacy-paths` for backward compatibility

### Update Taskfile.yml

```yaml
# Current
tasks:
  rule:universal:
    cmds:
      - uv run generate_agent_rules.py --agent universal --source . --destination {{.DEST | default "."}}

# Proposed
tasks:
  rule:universal:
    cmds:
      - uv run scripts/generate_agent_rules.py --agent universal --source templates --destination {{.DEST | default "generated/universal"}}
```

---

## .gitignore Strategy

### Option A: Commit Generated Files (Current Approach)
```gitignore
# Don't ignore generated/ - commit to git for convenience
# Users can directly use generated outputs without running generator
```

**Pros:**
- ✅ Users can clone and immediately use rules
- ✅ No build step required
- ✅ Git tracks changes to generated outputs

**Cons:**
- ⚠️ Git diffs show template changes + generated changes
- ⚠️ Risk of template/generated divergence
- ⚠️ Larger repository size

### Option B: Gitignore Generated Files (Build-Time Generation)
```gitignore
# Generated outputs - run `task rule:all` to build
generated/
.cursor/rules/
.github/instructions/
.clinerules/
rules/
```

**Pros:**
- ✅ Cleaner git history (only template changes)
- ✅ Guaranteed consistency (always freshly generated)
- ✅ Smaller repository

**Cons:**
- ⚠️ Requires build step after clone
- ⚠️ CI/CD must generate before use
- ⚠️ External users need Python + uv

**Recommendation**: **Option A (Commit)** for user convenience, but add CI check to ensure generated files are up-to-date

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-rules.yml
name: Validate Rules

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      
      - name: Install dependencies
        run: uv sync
      
      - name: Validate rule structure
        run: uv run scripts/validate_agent_rules.py
      
      - name: Check generated files are up-to-date
        run: |
          uv run scripts/generate_agent_rules.py --agent all --check
          # Exits non-zero if generated files are stale
```

---

## Migration Checklist

### Phase 1: Preparation (1-2 hours)
- [ ] Create new directory structure
- [ ] Copy templates to `templates/`
- [ ] Copy discovery files to `discovery/`
- [ ] Move scripts to `scripts/`
- [ ] Update `generate_agent_rules.py` with `--source` flag
- [ ] Update `Taskfile.yml` with new paths
- [ ] Test generation works with new structure

### Phase 2: Documentation (2-3 hours)
- [ ] Update README.md architecture diagram
- [ ] Update README.md file paths
- [ ] Create `docs/migration-guide.md`
- [ ] Update `CONTRIBUTING.md` with new paths
- [ ] Update `agent-final-one.md` with Phase 0
- [ ] Update `agent-final-one-corrections.md`

### Phase 3: Testing (1 hour)
- [ ] Test `task rule:universal` with new structure
- [ ] Test `task rule:cursor` with new structure
- [ ] Test `task rule:copilot` with new structure
- [ ] Test `task rule:cline` with new structure
- [ ] Verify AGENTS_V2.md references work

### Phase 4: Transition (1 week)
- [ ] Commit new structure alongside old
- [ ] Tag version as `v1.0.0-pre-migration`
- [ ] Announce migration in CHANGELOG.md
- [ ] Update GitHub README
- [ ] Monitor for issues

### Phase 5: Cleanup (30 minutes)
- [ ] Remove old template files from root
- [ ] Remove old discovery files from root
- [ ] Update .gitignore
- [ ] Tag version as `v2.0.0`
- [ ] Celebrate! 🎉

**Total Estimated Time**: ~8 hours for complete migration

---

## Alternative: Simpler Structure (If Migration Too Costly)

If full migration to Option 1 is too disruptive, consider this hybrid:

```
ai_coding_rules_gitlab/
├── templates/                    ← All source templates (flat)
│   ├── 000-global-core.md
│   └── ... (70+ files)
│
├── rules/                        ← Universal output (default)
│   ├── 000-global-core.md
│   ├── AGENTS.md
│   └── ...
│
├── AGENTS.md                     ← Discovery (root)
├── EXAMPLE_PROMPT.md
├── RULES_INDEX.md
├── generate_agent_rules.py
├── .cursor/rules/*.mdc           ← Generated
├── .github/instructions/*.md     ← Generated
└── .clinerules/*.md              ← Generated
```

**Why This Works:**
- ✅ Clear template location
- ✅ `rules/` exists by default
- ✅ Only 1 directory move required
- ✅ Minimal breaking changes
- ⚠️ Root still has some clutter

---

## Final Recommendation

**Best Choice**: **Option 1 (Source-First) with Phased Migration**

**Rationale**:
1. Aligns with industry standards (Hugo, Sphinx, cookiecutter)
2. Future-proof and scalable
3. Professional appearance
4. Clear separation of concerns
5. Phased migration minimizes disruption

**If Time/Resources Limited**: **Option 2 (Hybrid)** as interim solution

**Next Steps**:
1. Review this document with team
2. Decide on Option 1 vs Option 2
3. Execute Phase 1 (preparation) in feature branch
4. Test thoroughly
5. Merge and announce transition

---

**Questions to Consider:**

1. **Commit generated files?** Recommend YES for user convenience
2. **Subdirectories in templates/?** Recommend NO initially (start flat)
3. **Migration timeline?** Recommend 1-2 week transition period
4. **Breaking change acceptable?** Version 2.0.0 warrants it

---

*Analysis completed following industry best practices for template-based generation systems*

