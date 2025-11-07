# Release Notes: AI Coding Rules v2.1.0

**Release Date:** November 5, 2025  
**Type:** Minor Version Release (BREAKING CHANGES)  
**Focus:** Project Structure Reorganization, Maintainability, Scalability

---

## 🎯 Overview

Version 2.1.0 introduces a **major architectural restructuring** to the AI Coding Rules project. This release reorganizes the project directory structure to follow industry best practices from static site generators and template systems like Hugo, Sphinx, and cookiecutter.

**Key Highlights:**
- 📁 New template-first directory structure (templates → generation → outputs)
- 🔄 Clear separation of source templates and generated outputs
- 🚀 Enhanced generation script with auto-detection and smart paths
- 🔧 Backward compatibility via `--legacy-paths` flag and `task rule:legacy`
- 📚 Professional project organization for better maintainability

---

## 🚨 BREAKING CHANGES

### Project Structure Reorganization

This release introduces a **source-first architecture** with significant directory changes.

#### Old Structure (v2.0.x)
```
ai_coding_rules/
├── 000-global-core.md         # 72 rule files in root
├── 001-memory-bank.md
├── ... (70 more rules)
├── AGENTS.md                   # Discovery files in root
├── RULES_INDEX.md
├── generate_agent_rules.py     # Scripts in root
└── validate_agent_rules.py
```

#### New Structure (v2.1.0)
```
ai_coding_rules/
├── templates/                  # ← Source templates (edit these)
│   ├── 000-global-core.md
│   └── ... (72 rule files)
├── discovery/                  # ← Discovery system
│   ├── AGENTS.md
│   ├── RULES_INDEX.md
│   └── EXAMPLE_PROMPT.md
├── generated/                  # ← Generated outputs
│   ├── universal/              # Universal format
│   ├── cursor/rules/           # Cursor .mdc files
│   ├── copilot/instructions/   # GitHub Copilot
│   └── cline/                  # Cline format
├── scripts/                    # ← Generation tools
│   ├── generate_agent_rules.py
│   ├── validate_agent_rules.py
│   └── deploy_rules.py
├── docs/                       # ← Documentation
└── examples/                   # ← Usage examples
```

### Impact Assessment

**✅ For Rule Consumers (Using the Rules):**
- **No action required** - Clone and use immediately
- Generated files included in repository (no build step needed)
- Configure IDE to use `generated/{format}/` directories
- Or use `task rule:legacy` for traditional paths

**⚠️ For Rule Contributors (Editing Rules):**
- **Action required** - Edit templates in `templates/` directory
- Run `task rule:all` after edits to regenerate outputs
- Commit both template changes AND generated files
- Migration helper available: `scripts/migrate_to_templates.sh`

**✅ For CI/CD Pipelines:**
- **Mostly compatible** - Update paths if hardcoded
- Generation commands remain similar
- Validation commands unchanged

---

## ✨ New Features

### 1. Template-First Directory Structure

**Added:**
- `templates/` - 72 source template files (canonical source of truth)
- `discovery/` - Discovery system files (AGENTS.md, EXAMPLE_PROMPT.md, RULES_INDEX.md)
- `generated/` - All generated outputs organized by format
  - `generated/universal/` - Universal format (stripped metadata)
  - `generated/cursor/rules/` - Cursor-specific .mdc files
  - `generated/copilot/instructions/` - GitHub Copilot format
  - `generated/cline/` - Cline format
- `scripts/` - Generation and validation tools
- `docs/` - Project documentation
- `examples/` - Usage examples and templates

**Benefits:**
- Clear separation of source (templates) vs. generated (outputs)
- Professional, organized project structure
- Easier to understand what to edit vs. what's generated
- Scalable for adding new IDE formats
- Better version control (clear diffs on what changed)

### 2. Enhanced Generation Script

**`scripts/generate_agent_rules.py` Improvements:**

**Auto-Detection of Source Directory:**
```python
# Priority order:
# 1. templates/ (new structure)
# 2. ai_coding_rules/ (legacy)
# 3. . (current directory)
```

**New Flags:**
- `--source` - Manual source directory specification
- `--legacy-paths` - Generate to old output locations for backward compatibility

**Smart Path Detection:**
- Automatically finds templates regardless of where script is run
- Clear user feedback about detected paths
- Fails gracefully with helpful error messages

**Discovery File Handling:**
- Automatically copies AGENTS.md, RULES_INDEX.md, EXAMPLE_PROMPT.md to universal format output
- Ensures discovery files are always available alongside rules

### 3. Task Automation Updates

**New Tasks:**
```bash
task rule:all         # Generate all formats to generated/ (new structure)
task rule:legacy      # Generate to legacy paths (.cursor/rules/, etc.)
```

**Updated Tasks:**
- All rule generation tasks now use `scripts/` directory
- `task clean:rules` cleans both new and legacy paths
- Consistent task naming and behavior

**Backward Compatibility:**
- `task rule:legacy` generates to IDE-expected locations
- `--legacy-paths` flag available for custom workflows
- IDEs can be configured to use either `generated/` or legacy paths

### 4. IDE Compatibility Features

**Flexible Output Paths:**
- IDEs can reference `generated/{format}/` directories directly
- `--legacy-paths` generates to traditional IDE locations when needed
- Choose the approach that best fits your workflow

**Migration Support:**
- Migration helper script: `scripts/migrate_to_templates.sh`
- Clear documentation in CONTRIBUTING.md
- Examples in README.md for common scenarios

---

## 🔄 Changes

### File Organization

**Source Templates:**
- Moved from root directory → `templates/` directory
- 72 rule files (.md format)
- Canonical source of truth - **always edit here**

**Discovery Files:**
- Moved from root directory → `discovery/` directory
- AGENTS.md, EXAMPLE_PROMPT.md, RULES_INDEX.md
- Template-based with variable substitution

**Scripts:**
- Moved from root directory → `scripts/` directory
- All generation and validation tools
- Organized and documented

**Generated Outputs:**
- New `generated/` directory with subdirectories by format
- Clear separation from source files
- Committed to git for user convenience

### Generation Workflow

**Default Target Changed:**
- Old: Generate to root or IDE-specific paths
- New: Generate to `generated/` subdirectories by format
- Legacy behavior available via `--legacy-paths` flag

**Auto-Detection:**
- Scripts automatically detect `templates/` directory
- No manual path specification needed in most cases
- Works from any directory within the project

**Discovery File Copying:**
- AGENTS.md, RULES_INDEX.md, EXAMPLE_PROMPT.md automatically copied to universal output
- Ensures complete rule packages for deployment
- Template variable substitution during deployment

### Git Tracking

**Updated `.gitignore`:**
- Ignores symlinks (if any created)
- Commits generated files for user convenience
- No build step required for end users

**Generated Files Committed:**
- Users can clone and use immediately
- Clear git history of format-specific changes
- No Python/uv dependency for consumers

---

## 📚 Migration Guide

### For Users (Consuming Rules)

**Status:** ✅ No action required

**What Works:**
- Clone repository and use immediately
- Generated files included in `generated/` directories
- All 4 formats available: universal, cursor, copilot, cline

**Options:**
```bash
# Option 1: Use new structure (recommended)
# Configure IDE to use generated/{format}/
# Example: Point Cursor to generated/cursor/rules/

# Option 2: Use legacy paths
task rule:legacy
# Generates to .cursor/rules/, .github/instructions/, etc.
```

### For Contributors (Editing Rules)

**Status:** ⚠️ Action required

**New Workflow:**

1. **Edit source templates:**
   ```bash
   vim templates/200-python-core.md
   ```

2. **Regenerate outputs:**
   ```bash
   task rule:all
   ```

3. **Commit both source and generated:**
   ```bash
   git add templates/200-python-core.md generated/
   git commit -m "feat: update Python core rule"
   ```

**Migration Steps:**

If you have local changes in old structure:

1. **Use migration helper:**
   ```bash
   scripts/migrate_to_templates.sh
   ```

2. **Or manually move your edits:**
   ```bash
   # Copy your changes from root to templates/
   cp your-edited-file.md templates/
   
   # Regenerate
   task rule:all
   
   # Verify
   git diff
   ```

3. **Update your workflow:**
   - Always edit `templates/` files
   - Never edit `generated/` files
   - Run `task rule:all` after changes
   - Commit both directories

### For CI/CD Pipelines

**Status:** ✅ Mostly compatible

**Check These:**

1. **Hardcoded Paths:**
   ```yaml
   # Old (if you had this)
   - run: python generate_agent_rules.py --agent cursor
   
   # New
   - run: python scripts/generate_agent_rules.py --agent cursor
   ```

2. **Validation Commands:**
   ```yaml
   # Validation commands unchanged
   - run: uv run scripts/validate_agent_rules.py
   ```

3. **Generation Checks:**
   ```yaml
   # Check mode works the same
   - run: uv run scripts/generate_agent_rules.py --agent all --check
   ```

**Recommended Updates:**
```yaml
# Use new paths
- name: Generate rules
  run: |
    cd scripts
    uv run generate_agent_rules.py --agent all

# Or use Task
- name: Generate rules
  run: task rule:all
```

---

## 🏗️ Technical Details

### Architecture Alignment

**Industry Standards:**
- Follows patterns from Hugo, Jekyll, Sphinx (static site generators)
- Similar to cookiecutter, Yeoman (template systems)
- Common in Make, CMake, Bazel (build systems)

**Core Principles:**
1. **Templates → Generation → Outputs** (unidirectional flow)
2. **Single Source of Truth** (templates/ directory)
3. **Clear Separation of Concerns** (source vs. generated)
4. **Scalability** (easy to add new formats)

### Benefits

**For Maintainers:**
- Clear what to edit (templates/) vs. what's generated (generated/)
- Reduced cognitive load
- Easier code reviews (source changes are clear)
- Professional project organization

**For Contributors:**
- Obvious where to make changes
- Can't accidentally edit generated files
- Better onboarding experience
- Clear contribution workflow

**For Users:**
- No build step required (generated files committed)
- Multiple format options available
- Flexible IDE configuration
- Backward compatibility maintained

**For the Project:**
- Scalable architecture for future IDE formats
- Better version control (clear diffs)
- Reduced root directory clutter
- Future-proof structure

### Performance

**Generation Speed:**
- Unchanged (~1-2 seconds for 72 rules)
- Auto-detection adds <50ms overhead
- Linear scaling with rule count

**Repository Size:**
- Slight increase due to organized structure
- Generated files already committed (no change there)
- Better organization outweighs size concerns

---

## 🔧 Backward Compatibility

### Legacy Path Support

**`--legacy-paths` Flag:**
```bash
# Generate to old paths
python scripts/generate_agent_rules.py --agent cursor --legacy-paths

# Output: .cursor/rules/*.mdc (traditional location)
```

**`task rule:legacy` Command:**
```bash
# Generate all formats to legacy paths
task rule:legacy

# Creates:
# - .cursor/rules/
# - .github/instructions/
# - .clinerules/
# - rules/ (universal)
```

**When to Use:**
- IDE expects specific paths
- Can't/won't reconfigure IDE
- Testing compatibility
- Gradual migration

### IDE Configuration

**Option 1: Use New Structure (Recommended)**
```
Cursor: Point to generated/cursor/rules/
Copilot: Use generated/copilot/instructions/
Universal: Use generated/universal/
```

**Option 2: Use Legacy Paths**
```bash
task rule:legacy

Cursor: Uses .cursor/rules/
Copilot: Uses .github/instructions/
Universal: Uses rules/
```

**Both options fully supported!**

---

## 📊 Statistics

### Project Reorganization

- **Files Moved:** 72 rule templates → `templates/`
- **Scripts Moved:** 5 scripts → `scripts/`
- **Discovery Files Moved:** 3 files → `discovery/`
- **New Directories Created:** 8 (templates, discovery, generated/*, scripts, docs, examples)
- **Git History Preserved:** All files moved with `git mv`

### Format Coverage

- **Universal Format:** 72 rules in `generated/universal/`
- **Cursor Format:** 72 .mdc files in `generated/cursor/rules/`
- **Copilot Format:** 72 .md files in `generated/copilot/instructions/`
- **Cline Format:** 72 .md files in `generated/cline/`
- **Total Generated Files:** 288 (72 rules × 4 formats)

---

## 🚀 Upgrade Instructions

### Step 1: Update Repository

```bash
# Pull latest changes
cd ai_coding_rules
git pull origin main

# Verify new structure
ls templates/        # Should show 72 .md files
ls discovery/        # Should show AGENTS.md, etc.
ls generated/        # Should show universal/, cursor/, etc.
```

### Step 2: Update Your Workflow

**If you're a rule consumer:**
```bash
# Option A: Configure IDE to use generated/{format}/
# No code changes needed

# Option B: Use legacy paths
task rule:legacy
# Configure IDE to use traditional paths
```

**If you're a rule contributor:**
```bash
# 1. Move any in-progress edits to templates/
mv your-draft-rule.md templates/

# 2. Always edit templates/ going forward
vim templates/your-rule.md

# 3. Regenerate after changes
task rule:all

# 4. Commit both
git add templates/ generated/
git commit -m "feat: your changes"
```

### Step 3: Update IDE Configuration (Optional)

**Cursor:**
```
Settings → Rules → Point to:
generated/cursor/rules/
```

**VS Code + Copilot:**
```
# Repository instructions auto-detected from:
.github/copilot/instructions/
# Or use: generated/copilot/instructions/
```

**Claude Projects:**
```
# Upload files from:
generated/universal/
```

### Step 4: Update CI/CD (If Needed)

```yaml
# Update script paths
- run: uv run scripts/generate_agent_rules.py --agent all

# Or use Task
- run: task rule:all
```

---

## 🎓 Learning Resources

### Documentation

- **README.md** - Updated with new structure
- **CONTRIBUTING.md** - New contributor workflow
- **docs/ARCHITECTURE.md** - Technical architecture details
- **CHANGELOG.md** - Complete change history

### Key Files to Understand

```
templates/                    # Edit these (source)
├── 000-global-core.md       # Always load first
├── 100-snowflake-core.md    # Domain foundations
└── 200-python-core.md       # Language-specific rules

discovery/                    # Rule discovery system
├── AGENTS.md                # How agents should load rules
├── RULES_INDEX.md           # Machine-readable catalog
└── EXAMPLE_PROMPT.md        # Baseline prompt template

generated/                    # Generated outputs (don't edit)
├── universal/               # Clean markdown
├── cursor/rules/            # Cursor .mdc files
├── copilot/instructions/    # Copilot format
└── cline/                   # Cline format

scripts/                      # Generation tools
├── generate_agent_rules.py  # Main generator
├── validate_agent_rules.py  # Validation
└── deploy_rules.py          # Deployment helper
```

### Task Reference

```bash
# View all tasks
task -l

# Generation
task rule:all              # Generate all formats (new structure)
task rule:legacy           # Generate to legacy paths
task rule:universal        # Generate universal format only
task rule:cursor           # Generate Cursor format only

# Validation
task validate              # Full validation
task rules:validate        # Rule structure validation

# Deployment (for users)
task deploy:universal DEST=~/project
task deploy:cursor DEST=~/project
```

---

## 🙏 Acknowledgments

This restructuring represents a significant improvement in project organization and maintainability. The new template-first architecture provides a solid foundation for future growth and makes the project more accessible to contributors.

Special thanks to the community for feedback on project structure and best practices.

---

## 📞 Support

- **Issues:** [GitLab Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/issues)
- **Discussions:** [GitLab Discussions](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/discussions)
- **Documentation:** [README.md](README.md)
- **Migration Help:** File an issue with "migration" label

---

## 🔮 What's Next?

**Looking ahead to v2.2.0:**
- Enhanced validation features
- Token budget accuracy improvements
- Additional workflow automation
- Performance optimizations

---

## ⚠️ Important Notes

### For Existing Users

1. **Your existing rules still work** - No breaking changes for rule consumers
2. **Generated files are committed** - No build step required
3. **Backward compatibility maintained** - Legacy paths available via `--legacy-paths`
4. **IDE configuration optional** - Can continue using current setup

### For Contributors

1. **Always edit `templates/`** - Never edit `generated/` files
2. **Always run `task rule:all`** - After editing templates
3. **Always commit both** - Templates and generated files together
4. **Use migration helper** - If you have pending changes

### For CI/CD

1. **Update script paths** - If hardcoded
2. **Test generation** - Verify new structure works
3. **Consider using Task** - Simpler than direct script calls

---

**Full Changelog:** See [CHANGELOG.md](CHANGELOG.md) for complete details.

**Download:** [v2.1.0 Release](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/releases/v2.1.0)

---

## 📝 Quick Migration Checklist

### For Rule Consumers
- [ ] Pull latest changes (`git pull`)
- [ ] Choose structure option (new generated/ or legacy paths)
- [ ] Update IDE configuration (if using new structure)
- [ ] Verify rules load correctly
- [ ] Test with AI assistant

### For Rule Contributors
- [ ] Pull latest changes (`git pull`)
- [ ] Move in-progress edits to `templates/`
- [ ] Update local workflow (always edit templates/)
- [ ] Test generation (`task rule:all`)
- [ ] Verify output in `generated/`
- [ ] Update documentation/notes with new paths
- [ ] Commit template + generated changes together

### For CI/CD Maintainers
- [ ] Update script paths in pipelines
- [ ] Test generation in CI environment
- [ ] Verify output paths
- [ ] Update deployment scripts (if any)
- [ ] Test validation commands
- [ ] Update documentation

---

**Questions?** File an issue or start a discussion in the project repository.

