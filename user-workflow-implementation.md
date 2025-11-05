# User Workflow Implementation Plan

## Overview

This document provides a detailed implementation plan for creating user-facing documentation after migrating to Option 1 structure. This plan covers three critical deliverables:

1. **Quick Start Documentation** (README.md updates)
2. **Onboarding Checklist** (Team member setup guide)
3. **Release Announcement** (Communication to users)

---

## Deliverable #1: Quick Start Documentation

### Objective

Update README.md with crystal-clear, 5-minute setup instructions for end users adopting ai_coding_rules in their projects.

### Target Audience

- Developers adding rules to existing projects
- New project creators wanting AI assistance
- Teams standardizing on AI coding practices

### Success Criteria

- [ ] User can go from "never heard of this" to "rules working" in < 5 minutes
- [ ] Instructions work for Cursor, Claude, VS Code, and CLI tools
- [ ] No Python/build tools required (use pre-generated outputs)
- [ ] Update process is one command
- [ ] Troubleshooting covers 95% of issues

---

### Implementation: Quick Start Section for README.md

#### Location in README.md

Insert after "Quick Start" heading (around line 72), replacing or enhancing existing "Quick Start" section.

#### Content Structure

```markdown
## Quick Start

### For Rule System Users (Adding Rules to Your Project)

> **Goal**: Get AI coding rules working in your project in < 5 minutes

#### Prerequisites

- ✅ Git (for submodule support)
- ✅ An AI assistant (Cursor, Claude, GitHub Copilot, or similar)
- ❌ No Python required
- ❌ No build tools required

---

#### Step 1: Add Rules to Your Project (2 minutes)

**Option A: Git Submodule (Recommended)**

```bash
# Navigate to your project
cd /path/to/your-project

# Add ai_coding_rules as a submodule
git submodule add https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git .ai-rules

# Create convenient symlink (optional but recommended)
ln -s .ai-rules/generated/universal rules

# Commit the submodule
git add .gitmodules .ai-rules rules
git commit -m "chore: add ai coding rules"
```

**What This Does:**
- Downloads pre-generated rules to `.ai-rules/` directory
- Creates symlink `rules/` for easier access
- Pins your project to a specific version of the rules

**Option B: Direct Download (Air-Gapped Environments)**

```bash
# Download latest release
curl -L https://gitlab.com/.../releases/latest/download/ai-coding-rules-universal.tar.gz | tar xz

# Move to your project
mv ai-coding-rules-universal .ai-rules
ln -s .ai-rules/generated/universal rules
```

---

#### Step 2: Configure Your AI Assistant (2 minutes)

Choose your platform:

<details>
<summary><strong>Cursor IDE</strong></summary>

**Method 1: Manual Context (Simplest)**
```
When starting a conversation in Cursor:
1. Type: @rules/AGENTS.md
2. Cursor loads the rule discovery guide
3. AI automatically discovers and loads relevant rules
```

**Method 2: Project-Level Rules (Automatic)**
```bash
# Symlink to Cursor's expected location
ln -s ../rules .cursor/rules

# Cursor automatically includes .cursor/rules in context
```

**Verify Setup:**
```
Ask Cursor: "What rules are available for Python development?"
Expected: AI lists rules from RULES_INDEX.md (200-python-core, 210-fastapi, etc.)
```

</details>

<details>
<summary><strong>Claude Projects / ChatGPT</strong></summary>

**For Claude Projects:**
1. Upload `rules/AGENTS.md` to your project's knowledge base
2. Upload `rules/EXAMPLE_PROMPT.md` (optional baseline prompt)
3. In chat, reference: "Follow the rules from AGENTS.md"

**For ChatGPT:**
1. Start new conversation
2. Upload or paste `rules/AGENTS.md` content
3. Say: "Use AGENTS.md protocol for all responses"

**Verify Setup:**
```
Ask AI: "Load rules for building a FastAPI application"
Expected: AI loads 000-global-core, 200-python-core, 210-python-fastapi-core
```

</details>

<details>
<summary><strong>VS Code with GitHub Copilot</strong></summary>

**Add to Workspace Settings:**

Create or update `.vscode/settings.json`:
```json
{
  "github.copilot.advanced": {
    "instructions": "Follow rules from .ai-rules/generated/universal/ directory. Load AGENTS.md first for rule discovery protocol."
  }
}
```

**Alternative: Repository Instructions (Requires Commit)**
```bash
# Copy rules to GitHub Copilot location
mkdir -p .github/copilot-instructions.md
echo "Follow the rule discovery protocol from @.ai-rules/generated/universal/AGENTS.md" > .github/copilot-instructions.md

# Commit and push
git add .github/copilot-instructions.md
git commit -m "chore: configure Copilot with ai coding rules"
git push

# Wait 5-10 minutes for GitHub to index
```

</details>

<details>
<summary><strong>CLI Tools (aider, mentat, etc.)</strong></summary>

**For aider:**

Create `.aider.conf.yml`:
```yaml
# AI Coding Rules Configuration
context_files:
  - .ai-rules/generated/universal/AGENTS.md
  - .ai-rules/generated/universal/RULES_INDEX.md
  - .ai-rules/generated/universal/000-global-core.md

read_dirs:
  - .ai-rules/generated/universal/

# aider will include these files in every conversation
```

**For other CLI tools:** Check tool documentation for:
- Context file configuration
- System prompt customization
- Read directory permissions

</details>

---

#### Step 3: Verify Setup (1 minute)

**Test 1: Rule Discovery**
```
Ask your AI: "What rules are available for [your technology]?"
Expected: AI lists relevant rules from RULES_INDEX.md
```

**Test 2: Rule Loading**
```
Ask your AI: "Build a simple [Python/Snowflake/etc.] example following project rules"
Expected: AI mentions loading rules 000, domain-core, and specific rules
```

**Test 3: Rule Application**
```
Review generated code
Expected: Code follows patterns from loaded rules (e.g., using uv for Python, CTEs for SQL)
```

✅ **Success**: Your AI assistant now follows project-standard best practices!

---

#### Step 4: Update Rules (Monthly Maintenance)

```bash
# Check for updates
cd your-project
git submodule update --remote .ai-rules

# Review changes
cd .ai-rules
git log --oneline -10
# Shows recent rule updates

# Commit update to your project
cd ..
git add .ai-rules
git commit -m "chore: update ai coding rules to v2.1.0"
git push
```

**Update Frequency:**
- **Monthly**: Routine maintenance
- **Major releases**: When new technologies added
- **Bug fixes**: When rule corrections released

---

### Troubleshooting

<details>
<summary><strong>Issue: Submodule is empty after cloning</strong></summary>

**Problem**: You cloned a project with ai_coding_rules, but `.ai-rules/` directory is empty.

**Solution**:
```bash
# Initialize and update submodules
git submodule update --init --recursive

# Verify rules exist
ls .ai-rules/generated/universal/
# Should show: 000-global-core.md, 100-snowflake-core.md, AGENTS.md, etc.
```

**Prevention**: When cloning, use:
```bash
git clone --recursive https://your-project-url.git
```

</details>

<details>
<summary><strong>Issue: AI says "I don't have access to rules"</strong></summary>

**Diagnosis**:
```bash
# Check if rules directory exists
ls .ai-rules/generated/universal/

# Check if symlink is correct
ls -la rules
# Should show: rules -> .ai-rules/generated/universal
```

**Solutions**:

1. **If directory is empty**: Initialize submodule
   ```bash
   git submodule update --init --recursive
   ```

2. **If symlink is broken**: Recreate it
   ```bash
   rm rules
   ln -s .ai-rules/generated/universal rules
   ```

3. **If path is different**: Tell AI the correct path
   ```
   "Use rules from .ai-rules/generated/universal/ directory"
   ```

</details>

<details>
<summary><strong>Issue: Rules seem outdated</strong></summary>

**Check current version**:
```bash
cd .ai-rules
git log -1 --oneline
# Shows: abc1234 feat: update Python packaging (2 months ago)
```

**Update to latest**:
```bash
cd ..
git submodule update --remote .ai-rules
git add .ai-rules
git commit -m "chore: update to latest ai coding rules"
```

**Force specific version**:
```bash
cd .ai-rules
git checkout v2.1.0  # or specific tag
cd ..
git add .ai-rules
git commit -m "chore: pin ai coding rules to v2.1.0"
```

</details>

<details>
<summary><strong>Issue: AI loads wrong rules</strong></summary>

**Problem**: AI loads Snowflake rules for Python project (or vice versa)

**Cause**: Keyword mismatch in request

**Solution**: Be explicit in your request
```
❌ Bad: "Build this for me"
✅ Good: "Build a Python FastAPI application"
✅ Good: "Create a Snowflake stored procedure"
```

**Verification**: Check which rules AI loaded
```
AI should say: "Loaded rules 000, 200, 210 for Python FastAPI"
```

</details>

<details>
<summary><strong>Issue: Too many rules loaded (context bloat)</strong></summary>

**Problem**: AI loads 10+ rules, response is slow

**Cause**: Request is too broad or vague

**Solution**: Be more specific
```
❌ Bad: "Help me with everything in this project"
✅ Good: "Add authentication to the FastAPI endpoints"
```

**AI should load**: 4-5 rules maximum for most tasks
- 000-global-core (always)
- Domain core (100/200)
- 2-3 specialized rules
```

</details>

---

### Advanced: Customizing Rules for Your Project

**When to Customize:**
- ✅ Adding project-specific conventions
- ✅ Enforcing company-specific practices
- ✅ Subsetting rules (only Python for Python-only project)

**How to Customize:**

```bash
# 1. Copy rules to your project (no longer using submodule)
cp -r .ai-rules/generated/universal/* rules/
git rm .ai-rules  # Remove submodule

# 2. Edit rules to add project specifics
vim rules/200-python-core.md
# Add: "Project-Specific: Use our internal auth library"

# 3. Commit customized rules
git add rules/
git commit -m "chore: customize ai coding rules for project"
```

**Tradeoffs:**
- ✅ Full control over rules
- ✅ Project-specific customizations
- ❌ No automatic updates from upstream
- ❌ Must manually merge updates

**Recommendation**: Only customize if you have strong project-specific requirements. Otherwise, use submodule for easy updates.

---

### Next Steps

**For Teams:**
1. Add rules to shared project template
2. Create onboarding checklist (see ONBOARDING.md)
3. Schedule monthly rule update reviews
4. Monitor rule effectiveness (better code quality?)

**For Individuals:**
1. Try rules on next project
2. Provide feedback via GitLab issues
3. Suggest new rules for your tech stack
4. Share success stories with team

---

### Support

- **Documentation**: [Full guide](link-to-docs)
- **Issues**: [GitLab Issues](https://snow.gitlab-dedicated.com/.../issues)
- **Discussions**: [GitLab Discussions](https://snow.gitlab-dedicated.com/.../discussions)
- **Internal Support**: #ai-coding-rules Slack channel

---
```

---

## Deliverable #4: Onboarding Checklist

### Objective

Create a comprehensive checklist for new team members to get up and running with ai_coding_rules in < 10 minutes.

### Target Audience

- New hires joining teams using ai_coding_rules
- Existing team members switching projects
- Contractors/consultants onboarding

### Success Criteria

- [ ] Checklist covers 100% of setup steps
- [ ] Includes verification steps (how to know it's working)
- [ ] Links to detailed docs for each step
- [ ] Completion time < 10 minutes
- [ ] Self-service (no senior dev assistance needed)

---

### Implementation: ONBOARDING.md File

**File Location**: `ONBOARDING.md` in repository root

**Content**:

```markdown
# AI Coding Rules: Team Member Onboarding Checklist

> **Goal**: Get new team members productive with AI coding rules in < 10 minutes

## Prerequisites Check

Before starting, verify you have:

- [ ] Git installed (`git --version`)
- [ ] Access to project repository
- [ ] AI assistant installed (Cursor, Claude, GitHub Copilot, etc.)
- [ ] 10 minutes of focused time

---

## Phase 1: Environment Setup (3 minutes)

### Step 1.1: Clone Project with Submodules

If cloning project for the first time:

```bash
# Clone with --recursive to include submodules
git clone --recursive https://[project-url].git
cd [project-name]

# Verify rules exist
ls .ai-rules/generated/universal/
# Expected output: 000-global-core.md, 100-snowflake-core.md, AGENTS.md, etc.
```

**Verification**:
- [ ] `.ai-rules/` directory exists
- [ ] `.ai-rules/generated/universal/` contains 70+ `.md` files
- [ ] `AGENTS.md` exists in universal directory

**If submodule is empty** (directory exists but no files):
```bash
git submodule update --init --recursive
```

---

### Step 1.2: Verify Symlink (if project uses one)

```bash
# Check if rules/ symlink exists
ls -la rules
# Expected: rules -> .ai-rules/generated/universal
```

**If symlink doesn't exist but should**:
```bash
ln -s .ai-rules/generated/universal rules
```

**Verification**:
- [ ] `rules/` directory or symlink exists
- [ ] `ls rules/` shows rule files

---

## Phase 2: AI Assistant Configuration (4 minutes)

### Step 2.1: Choose Your AI Tool

Select the tool your team uses:

- [ ] **Cursor IDE** → Follow 2.2
- [ ] **Claude Projects** → Follow 2.3
- [ ] **VS Code + Copilot** → Follow 2.4
- [ ] **CLI Tool (aider/mentat)** → Follow 2.5

---

### Step 2.2: Configure Cursor

**Method A: Manual Context (Recommended)**

1. Open Cursor IDE
2. Open your project
3. Start a new conversation
4. Type: `@rules/AGENTS.md`
5. Cursor loads rule discovery guide

**Verification**:
```
Ask Cursor: "What rules are available for Python?"
Expected: Lists rules from RULES_INDEX.md (200-python-core, 210-fastapi, etc.)
```

**Method B: Automatic Context**

If your project has `.cursor/rules/` directory:

1. Verify directory exists: `ls .cursor/rules/`
2. Cursor automatically includes these rules
3. No manual loading needed

**Verification**:
- [ ] Cursor shows rules in context panel
- [ ] Rules appear in autocomplete suggestions

---

### Step 2.3: Configure Claude Projects

1. Open Claude.ai
2. Navigate to your project (or create new one)
3. Go to "Project Knowledge"
4. Upload files:
   - [ ] `rules/AGENTS.md`
   - [ ] `rules/EXAMPLE_PROMPT.md` (optional)
   - [ ] `rules/RULES_INDEX.md`
5. Start conversation

**Verification**:
```
Ask Claude: "Load rules for FastAPI development"
Expected: Claude loads 000-global-core, 200-python-core, 210-python-fastapi-core
```

---

### Step 2.4: Configure VS Code + GitHub Copilot

**Check if project has workspace settings:**

```bash
cat .vscode/settings.json
```

**If settings exist**: You're done! Copilot uses them automatically.

**If settings DON'T exist**: Add them manually

1. Create `.vscode/settings.json` (if doesn't exist)
2. Add:
```json
{
  "github.copilot.advanced": {
    "instructions": "Follow rules from .ai-rules/generated/universal/. Load AGENTS.md for rule discovery protocol."
  }
}
```
3. Reload VS Code window

**Verification**:
- [ ] Settings file exists and has copilot configuration
- [ ] Copilot suggestions follow project patterns

---

### Step 2.5: Configure CLI Tools (aider, etc.)

**Check if project has config file:**

```bash
ls .aider.conf.yml
# OR
ls .aiconfig
```

**If config exists**: You're done! Tool uses it automatically.

**If config DON'T exist**: Create one

For aider, create `.aider.conf.yml`:
```yaml
context_files:
  - .ai-rules/generated/universal/AGENTS.md
  - .ai-rules/generated/universal/RULES_INDEX.md
  - .ai-rules/generated/universal/000-global-core.md

read_dirs:
  - .ai-rules/generated/universal/
```

**Verification**:
```bash
aider --help
# Should show context files loaded
```

---

## Phase 3: Testing and Verification (3 minutes)

### Step 3.1: Test Rule Discovery

**Test Command**:
```
Ask AI: "What rules are available for [your-tech-stack]?"
Example: "What rules are available for Python development?"
```

**Expected Response**:
```
AI should list rules like:
- 000-global-core (foundation)
- 200-python-core (Python basics)
- 210-python-fastapi-core (FastAPI framework)
- 220-python-typer-cli (CLI tools)
- etc.
```

**Verification**:
- [ ] AI lists at least 5 relevant rules
- [ ] AI mentions RULES_INDEX.md or rule discovery
- [ ] Rules match your project's technology stack

---

### Step 3.2: Test Rule Loading

**Test Command**:
```
Ask AI: "Create a simple [language] example following project rules"
Example: "Create a simple Python FastAPI endpoint following project rules"
```

**Expected Response**:
```
AI should:
1. State which rules it's loading (000, 200, 210)
2. Generate code following those rules
3. Reference specific rules in explanation
```

**Verification**:
- [ ] AI explicitly states which rules loaded
- [ ] Code uses modern practices (e.g., uv for Python, not pip)
- [ ] Code structure matches rule recommendations

---

### Step 3.3: Test Rule Application

**Test Command**:
```
Ask AI: "Review this code for compliance with project rules: [paste code]"
```

**Expected Response**:
```
AI should:
1. Reference specific rules (e.g., "Per rule 200-python-core...")
2. Point out any violations
3. Suggest improvements based on loaded rules
```

**Verification**:
- [ ] AI references specific rule numbers
- [ ] AI catches anti-patterns defined in rules
- [ ] AI suggests rule-compliant alternatives

---

## Phase 4: Team Integration (Ongoing)

### Step 4.1: Read Team-Specific Documentation

Check if your project has custom documentation:

- [ ] Read `PROJECT_RULES.md` (if exists)
- [ ] Review project-specific conventions in Confluence/Wiki
- [ ] Join #ai-coding-rules Slack channel (if exists)

---

### Step 4.2: Bookmark Key Resources

Add these to your browser bookmarks:

- [ ] [AI Coding Rules Repository](https://snow.gitlab-dedicated.com/...)
- [ ] [Rule Index](https://snow.gitlab-dedicated.com/.../RULES_INDEX.md)
- [ ] [GitLab Issues](https://snow.gitlab-dedicated.com/.../issues) (for questions)
- [ ] [Internal Wiki](link) (team-specific docs)

---

### Step 4.3: Schedule Rule Update Reviews

Add to calendar:

- [ ] Monthly: Check for rule updates (`git submodule update --remote .ai-rules`)
- [ ] Quarterly: Review which rules your team uses most
- [ ] Yearly: Suggest new rules for your domain

---

## Common Issues and Solutions

### Issue: "Can't find .ai-rules directory"

**Solution**:
```bash
# Initialize submodule
git submodule update --init --recursive

# Verify
ls .ai-rules/generated/universal/
```

---

### Issue: "Rules seem outdated"

**Solution**:
```bash
# Check current version
cd .ai-rules
git log -1 --oneline

# Update to latest
cd ..
git submodule update --remote .ai-rules

# Commit update
git add .ai-rules
git commit -m "chore: update ai coding rules"
```

---

### Issue: "AI not following rules"

**Diagnosis**:
1. Verify rules are loaded (ask AI: "Which rules did you load?")
2. Check if request was specific enough
3. Verify correct rules for your task

**Solution**:
- Be explicit: "Build Python FastAPI app" (not just "build app")
- Reference rules directly: "Following rule 210, create..."
- Check AI's loaded rules list

---

## Success Checklist

Before marking onboarding complete, verify:

- [ ] **Environment**: `.ai-rules/` exists with 70+ rule files
- [ ] **Symlink**: `rules/` points to universal directory (if applicable)
- [ ] **AI Tool**: Configured and tested (Cursor/Claude/Copilot)
- [ ] **Discovery**: AI can list available rules
- [ ] **Loading**: AI loads correct rules for tasks
- [ ] **Application**: AI generates code following rules
- [ ] **Documentation**: Reviewed team-specific docs
- [ ] **Resources**: Bookmarked key links
- [ ] **Support**: Know where to ask questions

**Estimated Completion Time**: 10 minutes ✅

---

## Getting Help

### Self-Service Resources

1. **README.md**: Quick start and troubleshooting
2. **RULES_INDEX.md**: Complete rule catalog
3. **AGENTS.md**: Rule discovery protocol details
4. **GitLab Issues**: Search existing questions

### Escalation Path

1. **Level 1**: Team members (Slack #ai-coding-rules)
2. **Level 2**: Project maintainers (GitLab issues)
3. **Level 3**: Internal support (SE-support@snowflake.com)

---

## Contributing Back

Found an issue or have a suggestion?

- [ ] **Bug**: Open GitLab issue with "bug" label
- [ ] **Improvement**: Open issue with "enhancement" label
- [ ] **New Rule**: See CONTRIBUTING.md for rule creation guide
- [ ] **Documentation**: PR to improve onboarding docs

---

**Welcome to the team! 🎉**

*Your AI assistant is now configured to help you write better code, faster.*
```

---

## Deliverable #5: Release Announcement

### Objective

Communicate the Option 1 migration to existing users, explaining benefits, migration path, and timeline.

### Target Audience

- Current ai_coding_rules users
- Internal Snowflake teams
- External users (if open-sourced)

### Success Criteria

- [ ] Clearly explains what's changing
- [ ] Highlights benefits (why it matters)
- [ ] Provides migration timeline
- [ ] Includes migration steps
- [ ] Addresses breaking changes
- [ ] Links to detailed guides

---

### Implementation: Release Announcement Document

**File Location**: `RELEASE_ANNOUNCEMENT_V2.md` in repository root

**Distribution Channels**:
- GitLab release notes
- Internal Slack announcement
- Email to known users
- Snowflake internal wiki
- README.md banner (temporary)

**Content**:

```markdown
# 🚀 AI Coding Rules v2.0.0: Major Restructure for Better User Experience

**Release Date**: [DATE]
**Status**: Pre-release (migration in progress)
**Migration Deadline**: [DATE + 2 weeks]

---

## TL;DR (60-Second Summary)

**What's Changing:**
- ✅ **Source templates** moved to `templates/` directory
- ✅ **Generated outputs** in `generated/universal/` (or exposed as `rules/`)
- ✅ **Clearer structure** - obvious which files are source vs output
- ✅ **Easier setup** - users reference pre-generated outputs, no local build needed

**What You Need to Do:**
- ✅ Update submodule reference (1 command)
- ✅ Update AI assistant path (if hardcoded)
- ✅ Read migration guide (5 minutes)

**Timeline:**
- **Now - [DATE]**: Transition period (both structures supported)
- **[DATE]**: Old structure deprecated
- **[DATE + 2 weeks]**: Old structure removed

---

## Why We're Making This Change

### Problem: Current Structure is Confusing

**Before (v1.x):**
```
ai_coding_rules/
├── 000-global-core.md          ← Source template? Or final version?
├── 100-snowflake-core.md       ← Unclear which file to use
├── ... (70+ files in root)     ← Hard to find project files
├── .cursor/rules/*.mdc         ← Generated? Or source?
└── [no rules/ directory]       ← AGENTS_V2.md references rules/ but it doesn't exist
```

**Issues Users Reported:**
- ❌ "Which file should I edit - root or .cursor/rules/?"
- ❌ "AGENTS_V2.md references rules/ directory that doesn't exist"
- ❌ "Do I need to run Python to generate rules?"
- ❌ "70+ template files in root - where's README.md?"
- ❌ "How do I know if I'm using the right version?"

---

### Solution: Clear Template/Output Separation

**After (v2.0):**
```
ai_coding_rules/
├── templates/                  ← 🎯 Source templates (edit these)
│   ├── 000-global-core.md
│   └── ... (70+ template files)
│
├── generated/                  ← 🎯 Generated outputs (use these)
│   ├── universal/              → Exposed as rules/
│   │   ├── 000-global-core.md
│   │   ├── AGENTS.md
│   │   └── ... (70+ clean files)
│   ├── cursor/rules/*.mdc
│   ├── copilot/instructions/*.md
│   └── cline/*.md
│
├── scripts/                    ← Generation tools
│   └── generate_agent_rules.py
│
├── README.md                   ← Easy to find!
└── docs/                       ← Clear documentation
```

**Benefits:**
- ✅ **Crystal clear**: `templates/` = source, `generated/` = output
- ✅ **User-friendly**: Users reference `generated/universal/` (no local build)
- ✅ **Professional**: Matches industry standards (Hugo, Sphinx, etc.)
- ✅ **Scalable**: Easy to add new output formats
- ✅ **Discoverable**: `rules/` directory now exists as expected

---

## What's New in v2.0.0

### Feature 1: Clear Directory Structure

**templates/** directory contains all source templates
- Edit these to modify rules
- Follows rule governance standards
- Organized by domain (optional subdirectories)

**generated/** directory contains all outputs
- `generated/universal/` - Clean markdown for any IDE/agent
- `generated/cursor/` - Cursor-specific `.mdc` files
- `generated/copilot/` - GitHub Copilot instructions
- `generated/cline/` - Cline-specific format

**New:** `rules/` directory (symlink to `generated/universal/`)
- AGENTS_V2.md references finally work!
- Standard location expected by documentation
- Easy to remember

---

### Feature 2: Pre-Generated Outputs (No Build Required)

**Before**: Users had to run generator locally
```bash
# Old workflow - confusing!
git clone ai_coding_rules
cd ai_coding_rules
task deps:dev           # Install Python/uv
task rule:universal     # Generate rules
```

**After**: Use pre-generated outputs directly
```bash
# New workflow - simple!
git submodule add https://.../ai_coding_rules.git .ai-rules
ln -s .ai-rules/generated/universal rules
# Done! No Python needed.
```

---

### Feature 3: Improved Documentation

- ✅ **Quick Start**: 5-minute setup guide
- ✅ **Onboarding Checklist**: Team member setup
- ✅ **Troubleshooting**: Common issues + solutions
- ✅ **Migration Guide**: Step-by-step transition
- ✅ **Workflow Examples**: Real project setups

---

## Breaking Changes

### 1. File Paths Changed

**Old Paths (v1.x):**
```
000-global-core.md              (root)
AGENTS.md                       (root)
.cursor/rules/000-global-core.mdc
```

**New Paths (v2.0):**
```
templates/000-global-core.md    (source)
generated/universal/000-global-core.md (output)
generated/cursor/rules/000-global-core.mdc
```

**Impact**: If you hardcoded paths, update them.

**Migration**: See "How to Migrate" below.

---

### 2. Generator Script Moved

**Old Location**: `generate_agent_rules.py` (root)

**New Location**: `scripts/generate_agent_rules.py`

**Impact**: If you run generator manually, update command.

**Migration**:
```bash
# Old
python generate_agent_rules.py --agent universal

# New
python scripts/generate_agent_rules.py --agent universal
```

---

### 3. rules/ Directory Now Exists

**Old**: No `rules/` directory (AGENTS_V2.md references didn't work)

**New**: `rules/` symlink to `generated/universal/`

**Impact**: Positive! AGENTS_V2.md now works correctly.

**Migration**: None needed - this fixes existing issues.

---

## Migration Guide

### Step 1: Update Your Submodule Reference (1 minute)

```bash
cd your-project

# Update to latest version
git submodule update --remote .ai-rules

# Verify new structure
ls .ai-rules/templates/         # Should show rule template files
ls .ai-rules/generated/universal/  # Should show generated clean files

# Update your symlink (if you had one)
rm rules  # Remove old symlink
ln -s .ai-rules/generated/universal rules  # Create new symlink

# Commit changes
git add .ai-rules rules
git commit -m "chore: update ai_coding_rules to v2.0.0"
```

---

### Step 2: Update AI Assistant Configuration (2 minutes)

**If you hardcoded paths**, update them:

**Cursor:**
```
Old: @.ai-rules/000-global-core.md
New: @.ai-rules/generated/universal/000-global-core.md
# OR use symlink:
New: @rules/000-global-core.md
```

**Claude Projects:**
- Re-upload `rules/AGENTS.md` (path changed)
- Re-upload `rules/EXAMPLE_PROMPT.md` (if used)

**VS Code:**
```json
// .vscode/settings.json
{
  "github.copilot.advanced": {
    "instructions": "Follow rules from .ai-rules/generated/universal/"
  }
}
```

**CLI Tools:**
```yaml
# .aider.conf.yml
context_files:
  - .ai-rules/generated/universal/AGENTS.md
  - .ai-rules/generated/universal/RULES_INDEX.md
```

---

### Step 3: Test Setup (1 minute)

```
Ask AI: "What rules are available for Python?"
Expected: AI lists rules from RULES_INDEX.md
```

✅ **Success**: Migration complete!

---

## Timeline

### Phase 1: Pre-Release (Now - [DATE])

**Status**: Both structures available (transition period)

**Actions**:
- ✅ Review migration guide
- ✅ Test in non-production projects
- ✅ Report issues via GitLab
- ⚠️ Old structure still works (deprecated)

---

### Phase 2: Release (DATE)

**Status**: v2.0.0 officially released

**Actions**:
- ✅ Migrate production projects
- ✅ Update team documentation
- ✅ Train team members
- ⚠️ Old structure deprecated (works but triggers warnings)

---

### Phase 3: Old Structure Removal (DATE + 2 weeks)

**Status**: v2.1.0 removes old structure support

**Actions**:
- ❌ Old structure no longer works
- ✅ All projects must use new structure
- ✅ Clean, simple repository structure

---

## Support During Migration

### Self-Service Resources

1. **Migration Guide**: [MIGRATION_V2.md](link)
2. **Quick Start**: [README.md#quick-start](link)
3. **Troubleshooting**: [README.md#troubleshooting](link)
4. **Onboarding**: [ONBOARDING.md](link)

### Getting Help

**Internal Snowflake:**
- Slack: #ai-coding-rules
- Email: SE-support@snowflake.com
- Office Hours: Tuesdays 2-3pm PT

**External/Open Source:**
- GitLab Issues: [https://gitlab.com/.../issues](link)
- GitLab Discussions: [https://gitlab.com/.../discussions](link)

### Reporting Issues

Found a problem? Report it:
- **Bug**: [Open GitLab issue](link) with "bug" label
- **Documentation**: [Open GitLab issue](link) with "documentation" label
- **Question**: [Start discussion](link)

---

## FAQ

### Q: Do I have to migrate immediately?

**A**: Not immediately, but we recommend migrating before [DATE + 2 weeks] when old structure is removed.

**Transition Period**: Both structures work until [DATE + 2 weeks]

---

### Q: Will my existing setup break?

**A**: Your existing setup continues working during transition period. After [DATE + 2 weeks], you must migrate.

---

### Q: What if I've customized rules?

**A**: 
1. **Option A**: Copy your customizations to new structure
2. **Option B**: Continue using customized copy (no submodule)
3. **Option C**: Submit customizations as project-specific rules

See [CUSTOMIZATION_GUIDE.md](link) for details.

---

### Q: Do I need Python to use v2.0?

**A**: No! That's one of the benefits. Use pre-generated outputs in `generated/universal/` directory.

---

### Q: Can I preview the new structure before migrating?

**A**: Yes!

```bash
# Clone a test copy
git clone https://.../ai_coding_rules.git ai_coding_rules_test
cd ai_coding_rules_test
git checkout v2.0.0-rc1  # Release candidate

# Explore new structure
ls templates/
ls generated/universal/
```

---

### Q: What if I find an issue during migration?

**A**: Report it immediately! We want to fix issues before final release.

1. Open GitLab issue with "migration-issue" label
2. Include steps to reproduce
3. We'll prioritize migration-blocking issues

---

## Benefits Summary

### For End Users

- ✅ **Simpler setup**: No Python required, use pre-generated outputs
- ✅ **Clearer structure**: Obvious which files to use
- ✅ **Faster onboarding**: 5-minute setup vs 15-minute setup
- ✅ **Better documentation**: Quick start, troubleshooting, examples
- ✅ **Easier updates**: Single git command

### For Rule Contributors

- ✅ **Clear editing workflow**: Edit `templates/`, run generator, commit
- ✅ **No confusion**: One source of truth (`templates/`)
- ✅ **Better tooling**: Improved generator with validation
- ✅ **Scalable structure**: Easy to add new formats

### For Teams

- ✅ **Standardization**: Everyone uses same structure
- ✅ **Reduced support**: Clearer docs = fewer questions
- ✅ **Professional appearance**: Mature project structure
- ✅ **Future-proof**: Easy to evolve and extend

---

## Acknowledgments

Thank you to everyone who provided feedback on the v1.x structure:
- User feedback via GitLab issues
- Internal Snowflake SE team
- Early adopters who tested pre-releases

Your input made v2.0.0 possible! 🙏

---

## Next Steps

### For Existing Users

1. ⏰ **Now**: Read this announcement
2. 📖 **This Week**: Review migration guide
3. 🧪 **Next Week**: Test in non-production project
4. 🚀 **Before [DATE]**: Migrate production projects

### For New Users

Just follow the Quick Start guide - you get the v2.0 experience automatically!

---

## Questions?

- **Slack**: #ai-coding-rules (internal Snowflake)
- **GitLab**: [Open discussion](link)
- **Email**: SE-support@snowflake.com

---

**We're excited about this improvement and can't wait for you to try v2.0!**

The AI Coding Rules Team
[DATE]
```

---

## Implementation Checklist

### Pre-Release Tasks (Before Migration)

- [ ] **Create documentation files**:
  - [ ] Update README.md with Quick Start section
  - [ ] Create ONBOARDING.md
  - [ ] Create RELEASE_ANNOUNCEMENT_V2.md
  - [ ] Create MIGRATION_V2.md (detailed migration steps)
  - [ ] Update CONTRIBUTING.md with new structure

- [ ] **Update generation tools**:
  - [ ] Add `--source` flag to generator script
  - [ ] Update Taskfile.yml with new paths
  - [ ] Test all output formats with new structure
  - [ ] Verify backward compatibility (transition period)

- [ ] **Create example projects**:
  - [ ] `examples/fastapi-starter/` - Python FastAPI using rules
  - [ ] `examples/streamlit-dashboard/` - Snowflake Streamlit using rules
  - [ ] Each with `.ai-rules` submodule configured

- [ ] **Internal testing**:
  - [ ] Test with 3-5 internal projects
  - [ ] Gather feedback on migration process
  - [ ] Identify pain points
  - [ ] Adjust documentation based on feedback

---

### Release Tasks (During Release)

- [ ] **Tag release**:
  - [ ] Create v2.0.0-rc1 release candidate
  - [ ] Test for 1 week
  - [ ] Create v2.0.0 final release

- [ ] **Update documentation**:
  - [ ] Add banner to README.md announcing v2.0
  - [ ] Update CHANGELOG.md with v2.0 changes
  - [ ] Link to migration guide prominently

- [ ] **Communicate release**:
  - [ ] Post in #ai-coding-rules Slack
  - [ ] Email announcement to known users
  - [ ] Update internal wiki
  - [ ] Add to Snowflake SE newsletter

- [ ] **Monitor for issues**:
  - [ ] Watch GitLab issues for migration problems
  - [ ] Host office hours (first 2 weeks)
  - [ ] Create FAQ based on questions
  - [ ] Update docs with discovered issues

---

### Post-Release Tasks (After Successful Migration)

- [ ] **Gather metrics**:
  - [ ] Track adoption rate (submodule usage)
  - [ ] Measure setup time (before/after)
  - [ ] Count support tickets (should decrease)
  - [ ] Survey user satisfaction

- [ ] **Iterate on documentation**:
  - [ ] Update based on user feedback
  - [ ] Add more examples
  - [ ] Expand troubleshooting section
  - [ ] Create video walkthrough

- [ ] **Remove old structure** (after 2 weeks):
  - [ ] Create v2.1.0 removing old paths
  - [ ] Announce deprecation completed
  - [ ] Celebrate clean structure! 🎉

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Setup Time** | < 5 min | Time new user to "rules working" |
| **Migration Time** | < 10 min | Time to update existing project |
| **Support Tickets** | < 5/month | GitLab issues labeled "setup-help" |
| **Adoption Rate** | > 80% in 1 month | Projects using v2.0+ |
| **Documentation Clarity** | > 90% | User survey: "Docs were clear" |

### Qualitative Metrics

| Metric | How to Assess |
|--------|---------------|
| **User Satisfaction** | Survey after 1 month |
| **Reduced Confusion** | Fewer "which file?" questions |
| **Professional Perception** | Feedback on project structure |
| **Contributor Experience** | Easier to add new rules? |

---

## Rollback Plan

If major issues discovered:

### Week 1-2: Immediate Rollback Available

```bash
# Users can pin to v1.x
cd .ai-rules
git checkout v1.9.0
cd ..
git add .ai-rules
git commit -m "chore: rollback to v1.9.0 due to [issue]"
```

### Week 3+: Address Issues, Push Forward

Focus on fixing issues rather than rolling back:
1. Identify root cause
2. Fix in v2.0.1
3. Update documentation
4. Communicate fix

---

## Timeline Summary

| Date | Milestone | Action |
|------|-----------|--------|
| **[DATE]** | Pre-release | Release v2.0.0-rc1, start testing |
| **[DATE + 1 week]** | Feedback period | Gather feedback, fix issues |
| **[DATE + 2 weeks]** | Official release | Release v2.0.0 |
| **[DATE + 4 weeks]** | Deprecation warning | Add deprecation warnings to old structure |
| **[DATE + 6 weeks]** | Old structure removed | Release v2.1.0 with clean structure |

---

**Total Estimated Effort**:

- **Documentation creation**: 4-6 hours
- **Example projects**: 2-3 hours
- **Testing**: 3-4 hours
- **Communication**: 2 hours
- **Support during migration**: 5-8 hours (first 2 weeks)

**Total**: ~16-23 hours spread over 6 weeks

---

*This implementation plan provides a comprehensive roadmap for delivering exceptional user experience with the v2.0 migration.*

