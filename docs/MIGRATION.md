# Migration Guides

## Overview

This directory contains migration guides for different aspects of the AI Coding Rules project:

- **[Project Architecture Migration (v2.x → v3.0)](#project-architecture-migration-v2x--v30)** - Template system removal, production-ready rules
- **[Schema Migration (v3.1 → v3.2)](MIGRATION_SCHEMA_v3.1_to_v3.2.md)** - Rule format changes, section restructuring

---

## Project Architecture Migration: v2.x → v3.0

Version 3.0 represents a major architectural shift from a template-based generation system to a **production-ready rule system**. This guide helps you migrate from the old workflow to the new simplified approach.

## TL;DR - What Changed

**Before (v2.x):**
```bash
# Edit templates
vim templates/100-snowflake-core.md

# Generate rules for all agents
task rule:all

# Deploy generated rules
python scripts/rule_deployer.py --agent cursor --destination /path
```

**After (v3.0):**
```bash
# Edit production-ready rules directly
vim rules/100-snowflake-core.md

# Validate rules (optional)
python scripts/schema_validator.py rules/

# Deploy directly (no generation step)
python scripts/rule_deployer.py --dest /path
```

## Key Changes

### 1. No More Templates or Generation

**Old System:**
- Rules authored in `templates/` with placeholders
- `scripts/generate_agent_rules.py` processed templates
- Generated outputs in `generated/` (cursor, copilot, cline, universal)
- `discovery/AGENTS.md` and `discovery/RULES_INDEX.md` were generated

**New System:**
- **All rules in `rules/` directory** - production-ready, no placeholders
- **No generation step** - rules are ready to deploy
- **AGENTS.md and RULES_INDEX.md in project root** - manually maintained
- **Removed old template structure** (templates/, generated/, discovery/ directories)

### 2. Simplified Deployment

**Old Command:**
```bash
python scripts/rule_deployer.py --agent cursor --destination ~/my-project
```

**New Command:**
```bash
python scripts/rule_deployer.py --dest ~/my-project
```

**Changes:**
- `--dest` is now **required** (no default)
- No `--agent` flag - deployment is agent-agnostic
- Rules copied to `DEST/rules/` (not agent-specific paths)
- AGENTS.md and RULES_INDEX.md copied to DEST root

### 3. Validation Updates

**Old Command:**
```bash
python scripts/rule_validator.py --directory templates
```

**New Command:**
```bash
python scripts/schema_validator.py rules/
```

**Changes:**
- Use `schema_validator.py` (replaces `rule_validator.py`)
- Pass directory as positional argument (not `--directory` flag)
- Default target is `rules/` directory (v3.0 architecture)

### 4. Directory Structure Changes

**Before:**
```
ai_coding_rules/
├── templates/          # Source templates (91 files)
├── generated/          # Generated outputs
│   ├── cursor/
│   ├── copilot/
│   ├── cline/
│   └── universal/
├── discovery/          # Generated AGENTS.md, RULES_INDEX.md
└── rules/              # Some production rules (91 files)
```

**After:**
```
ai_coding_rules/
├── rules/              # Production-ready rules (91 files)
├── AGENTS.md           # Rule loading guide (root)
├── RULES_INDEX.md      # Rule catalog (root)
└── scripts/
    ├── rule_deployer.py       # Simplified deployment
    ├── schema_validator.py    # Schema-based validation (v3.0)
    ├── token_validator.py     # Token budget analysis
    ├── index_generator.py     # RULES_INDEX.md generation
    └── template_generator.py  # Create new rule templates
```

## Migration Steps

### For Rule Authors

**1. Switch from templates/ to rules/**

```bash
# Old workflow
vim templates/215-python-django-core.md
task rule:all  # Generate all formats
git add templates/215-python-django-core.md generated/

# New workflow
vim rules/215-python-django-core.md
git add rules/215-python-django-core.md
```

**2. Update references in your rules**

If your rules reference file paths:
- ❌ Old: `templates/002a-rule-boilerplate.md`
- ✅ New: `rules/002a-rule-creation-guide.md` (renamed and refactored for v3.0)

**3. No more generation step**

The `task rule:all` command is no longer needed. Rules in `rules/` are production-ready.

### For Deployment Users

**1. Update deployment commands**

```bash
# Old
python scripts/rule_deployer.py --agent cursor --destination ~/my-cursor-project

# New
python scripts/rule_deployer.py --dest ~/my-cursor-project
```

**2. Update deployed rule paths**

Rules are now deployed to `DEST/rules/` instead of agent-specific paths:
- ❌ Old: `.cursor/rules/`, `.clinerules/`, `.github/copilot/instructions/`
- ✅ New: `rules/` (agent-agnostic)

**3. Use dry-run for testing**

```bash
python scripts/rule_deployer.py --dest ~/project --dry-run
```

### For CI/CD Pipelines

**Update validation commands:**

```bash
# Old
python scripts/rule_validator.py --directory templates

# New
python scripts/schema_validator.py rules/
```

**Remove generation steps:**

```bash
# Old pipeline
- task rule:all  # Generate rules ❌ Remove this
- python scripts/rule_deployer.py --agent universal --destination $DEST

# New pipeline
- python scripts/schema_validator.py rules/
- python scripts/rule_deployer.py --dest $DEST
```

### For Taskfile Users

**Update task commands in Taskfile.yml:**

Old tasks to remove or update:
- `task rule:all` - No longer needed
- `task generate:rules:*` - Remove generation tasks
- `task deploy:cursor` - Update to use new deployment

For the complete list of current task commands, see the [Development Commands](README.md#development-commands) section in README.md.

**Key task changes:**
```yaml
# Old (deprecated)
task rule:all               # Remove

# New (v3.0)
task rules:validate         # Validate rules against schema
task deploy DEST=<path>     # Deploy to any project
task index:generate         # Update RULES_INDEX.md
```

## Breaking Changes

### 1. Generation Scripts Removed

**Removed files:**
- `scripts/generate_agent_rules.py` - Multi-agent template generation no longer needed
- `templates/` directory - Production rules in `rules/` replace templates
- `generated/` directory - No longer needed (rules are production-ready)
- `discovery/` directory - AGENTS.md and RULES_INDEX.md moved to project root

**Retained and Updated:**
- `scripts/index_generator.py` - Generates RULES_INDEX.md from `rules/` directory
- `scripts/template_generator.py` - Creates new rule templates for development

**Replacement:** Edit `rules/` directly; use `scripts/index_generator.py` to update RULES_INDEX.md automatically.

### 2. Deployment Flag Changes

- `--agent` flag **removed** (deployment is agent-agnostic)
- `--destination` renamed to `--dest` and is **required**
- Agent-specific paths (`.cursor/rules/`, etc.) no longer used
- New optional flags: `--dry-run`, `--verbose`, `--quiet`

### 3. File Locations

- `discovery/AGENTS.md` → project root `AGENTS.md`
- `discovery/RULES_INDEX.md` → project root `RULES_INDEX.md`
- `templates/*.md` → `rules/*.md`

## Benefits of v3.0

**Simpler Workflow:**
- ✅ No template processing step
- ✅ Faster iteration (edit rules directly)
- ✅ Clearer source of truth (`rules/` is canonical)

**Easier Contributions:**
- ✅ Contributors edit final rules, not templates
- ✅ No need to regenerate formats
- ✅ WYSIWYG - what you edit is what gets deployed

**Reduced Complexity:**
- ✅ Fewer scripts to maintain
- ✅ No placeholder substitution logic
- ✅ Agent-agnostic deployment

## Frequently Asked Questions

### Q: Can I still use the old template system?

**A:** The old template-based generation system has been removed in v3.0. All rules are now production-ready in the `rules/` directory.

### Q: How do I update RULES_INDEX.md now?

**A:** Use the automated script: `python scripts/index_generator.py` or `task index:generate`. The script extracts metadata from all rules in the `rules/` directory and generates an up-to-date index. You can also manually edit `RULES_INDEX.md` if needed.

### Q: What happened to agent-specific formats (.mdc for Cursor)?

**A:** Agent-specific file extensions are no longer needed. All agents can work with standard `.md` files. Deployment is now agent-agnostic.

### Q: Can I deploy to agent-specific paths?

**A:** The new deployment script deploys to `DEST/rules/` by default. If you need agent-specific paths, you can manually move files after deployment or modify the script.

### Q: How do I validate rules now?

**A:** Use `python scripts/schema_validator.py rules/` to validate all rules in the `rules/` directory.

### Q: Where can I find the old templates?

**A:** The old templates have been replaced with production-ready rules in the `rules/` directory. If you need historical reference, check the v2.x git tags.

## Support

If you encounter issues during migration:

1. **Review CHANGELOG.md** for detailed change log
2. **Check README.md** for v3.0 architecture overview
3. **Open an issue** in the project repository

## Version Compatibility

- **v3.0+**: Production-ready rules, no generation
- **v2.x**: Template-based generation (removed in v3.0, use git tags for historical reference)
- **v1.x**: Early versions (not compatible)

## Next Steps

After migrating:

1. **Validate rules:** Run `python scripts/schema_validator.py rules/` or `task rules:validate`
2. **Test deployment:** Run `python scripts/rule_deployer.py --dest /tmp/test --dry-run` or `task deploy:dry DEST=/tmp/test`
3. **Update RULES_INDEX.md:** Run `python scripts/index_generator.py` or `task index:generate`
4. **Update documentation:** If you have custom documentation, update references to templates/ → rules/
5. **Update CI/CD:** Remove generation steps, update validation commands

---

**Ready to deploy?** See [README.md](README.md#quick-start) for deployment instructions.
