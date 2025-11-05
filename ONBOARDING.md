# Team Onboarding: AI Coding Rules

**Welcome!** This guide will help you set up and use AI Coding Rules in your project in under 15 minutes.

---

## 📋 Quick Overview

**What You're Setting Up:**
- 72 specialized coding rules for AI assistants
- Automatic rule discovery and loading
- IDE-specific configurations (Cursor, VS Code, etc.)
- Consistent AI-assisted development across your team

**Time Required:** 10-15 minutes  
**Prerequisites:** Git, your preferred IDE/AI assistant

---

## ✅ Onboarding Checklist

### Phase 1: Initial Setup (5 minutes)

- [ ] **Clone or verify submodule** (Step 1.1)
- [ ] **Choose your AI tool** (Step 1.2)
- [ ] **Verify files exist** (Step 1.3)

### Phase 2: Tool Configuration (5 minutes)

- [ ] **Configure IDE/AI assistant** (Step 2.x - choose your tool)
- [ ] **Verify configuration** (Step 2.x verification)

### Phase 3: Testing (3 minutes)

- [ ] **Test rule discovery** (Step 3.1)
- [ ] **Test rule loading** (Step 3.2)
- [ ] **Test rule application** (Step 3.3)

### Phase 4: Integration (Ongoing)

- [ ] **Bookmark resources** (Step 4.1)
- [ ] **Join team channels** (Step 4.2)
- [ ] **Schedule updates** (Step 4.3)

---

## Phase 1: Initial Setup

### Step 1.1: Get the Rules

#### If Your Project Already Has Rules (Git Submodule)

```bash
# From your project root
git submodule update --init --recursive

# Verify submodule loaded
ls .ai-rules/
```

**Expected output:**
```
discovery/
generated/
templates/
scripts/
README.md
... (more files)
```

✅ **Success!** Skip to Step 1.2.

#### If Your Project Doesn't Have Rules Yet

```bash
# From your project root
git submodule add https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git .ai-rules
cd .ai-rules

# Generate rules (requires Python 3.11+ and uv)
task rule:all

# Verify generation
ls generated/universal/ | head -5
```

**Expected output:**
```
000-global-core.md
001-memory-bank.md
002-rule-governance.md
003-context-engineering.md
004-tool-design-for-agents.md
```

---

### Step 1.2: Choose Your AI Tool

Which tool(s) do you use? Check all that apply:

- [ ] **Cursor IDE** → Go to Step 2.1
- [ ] **Claude Projects** → Go to Step 2.2
- [ ] **VS Code + GitHub Copilot** → Go to Step 2.3
- [ ] **Cline AI Assistant** → Go to Step 2.4
- [ ] **Other (aider, ChatGPT, etc.)** → Go to Step 2.5

---

### Step 1.3: Verify Files Exist

```bash
# Check generated rules
ls .ai-rules/generated/universal/*.md | wc -l
# Expected: 72+

# Check discovery files
ls .ai-rules/discovery/
# Expected: AGENTS.md, RULES_INDEX.md, EXAMPLE_PROMPT.md
```

**All checks passed?** ✅ Continue to Phase 2.  
**Issues?** See [Troubleshooting](#troubleshooting) below.

---

## Phase 2: Tool Configuration

### Step 2.1: Configure Cursor IDE

#### Quick Method (Recommended)

1. Open Cursor IDE
2. Open your project
3. Start a new conversation
4. Type: `@.ai-rules/discovery/AGENTS.md`
5. Cursor loads rule discovery guide automatically

**Verify:**
```
Ask Cursor: "What rules are available for [your-tech-stack]?"
Example: "What rules are available for Python?"
```

**Expected:** Cursor lists relevant rules from RULES_INDEX.md

#### Alternative: Use Generated Cursor Rules

```bash
# Copy generated Cursor format to IDE location
cp -r .ai-rules/generated/cursor/rules/* .cursor/rules/

# Cursor automatically loads these
```

**Verification Checklist:**
- [ ] Cursor shows rules in context panel
- [ ] Rules appear in autocomplete
- [ ] AI references specific rule numbers

---

### Step 2.2: Configure Claude Projects

1. **Open Claude.ai** → Navigate to your project (or create new)
2. **Go to "Project Knowledge"**
3. **Upload files:**
   - [ ] `.ai-rules/discovery/AGENTS.md`
   - [ ] `.ai-rules/discovery/RULES_INDEX.md`
   - [ ] `.ai-rules/discovery/EXAMPLE_PROMPT.md` (optional)

4. **Add key rules for your stack:**
   - Python: Upload `.ai-rules/generated/universal/200-python-core.md`
   - Snowflake: Upload `.ai-rules/generated/universal/100-snowflake-core.md`
   - Docker: Upload `.ai-rules/generated/universal/400-docker-best-practices.md`

5. **Test:**
```
Ask Claude: "Load rules for [your-tech-stack] development"
Example: "Load rules for FastAPI development"
```

**Expected:** Claude loads 000-global-core, 200-python-core, 210-python-fastapi-core

**Verification Checklist:**
- [ ] Files uploaded successfully
- [ ] Claude references RULES_INDEX.md
- [ ] Claude loads appropriate rules for tasks

---

### Step 2.3: Configure VS Code + GitHub Copilot

#### Option A: Project Already Configured

```bash
# Check if config exists
cat .vscode/settings.json
```

**If settings mention `.ai-rules` or rules:** ✅ You're done!

#### Option B: Manual Configuration

1. **Create/edit `.vscode/settings.json`:**

```json
{
  "github.copilot.advanced": {
    "instructions": "Follow rules from .ai-rules/generated/universal/. Load discovery/AGENTS.md for rule discovery protocol."
  }
}
```

2. **Reload VS Code:**
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Reload Window"
   - Press Enter

3. **Test:**
```
Ask Copilot: "What Python coding standards should I follow?"
```

**Verification Checklist:**
- [ ] `.vscode/settings.json` exists with copilot config
- [ ] Copilot suggestions follow project patterns
- [ ] Copilot chat references rules

---

### Step 2.4: Configure Cline AI Assistant

#### Option A: Use Generated Cline Format

```bash
# Copy generated Cline format to IDE location
cp -r .ai-rules/generated/cline/* .clinerules/

# Cline automatically processes all .md files in .clinerules/
```

#### Option B: Reference Universal Format

Add to Cline settings:
```json
{
  "cline.customInstructions": "Load rules from .ai-rules/generated/universal/. Follow discovery/AGENTS.md for rule discovery."
}
```

**Verification:**
```
Ask Cline: "What rules govern Python development here?"
```

**Expected:** Cline lists 000-global-core, 200-python-core, and related rules

---

### Step 2.5: Other Tools (aider, ChatGPT, etc.)

#### For aider CLI Tool

Create `.aider.conf.yml`:
```yaml
context_files:
  - .ai-rules/discovery/AGENTS.md
  - .ai-rules/discovery/RULES_INDEX.md
  - .ai-rules/generated/universal/000-global-core.md

read_dirs:
  - .ai-rules/generated/universal/
```

**Test:**
```bash
aider --help
# Should show context files loaded
```

#### For ChatGPT

1. Open ChatGPT
2. Start new conversation
3. Upload files:
   - `.ai-rules/discovery/AGENTS.md`
   - `.ai-rules/discovery/RULES_INDEX.md`
   - Relevant rule files for your task

#### For Custom Integrations

Read the [Programmatic Rule Loading](#programmatic-rule-loading) section in README.md for API integration examples.

---

## Phase 3: Testing and Verification

### Step 3.1: Test Rule Discovery

**Command:**
```
Ask AI: "What rules are available for [your-tech-stack]?"
```

**Expected Response:**
- AI lists at least 5 relevant rules
- AI mentions RULES_INDEX.md or rule discovery
- Rules match your project's technology stack

**Verification:**
- [ ] AI discovered rules automatically
- [ ] Rules listed are relevant to your project
- [ ] AI can explain what each rule covers

---

### Step 3.2: Test Rule Loading

**Command:**
```
Ask AI: "Create a simple [language] example following project rules"
Example: "Create a simple Python FastAPI endpoint following project rules"
```

**Expected Response:**
- AI states which rules it's loading (e.g., 000, 200, 210)
- Generated code follows those rules
- AI references specific rules in explanation

**Verification:**
- [ ] AI explicitly states which rules loaded
- [ ] Code uses modern practices (e.g., uv for Python, not pip)
- [ ] Code structure matches rule recommendations
- [ ] AI explains rationale with rule references

---

### Step 3.3: Test Rule Application

**Command:**
```
Ask AI: "Review this code for compliance with project rules"
[Paste some existing project code]
```

**Expected Response:**
- AI references specific rules (e.g., "Per rule 200-python-core...")
- AI points out any violations
- AI suggests improvements based on loaded rules

**Verification:**
- [ ] AI references specific rule numbers
- [ ] AI catches anti-patterns defined in rules
- [ ] AI suggests rule-compliant alternatives
- [ ] Suggestions align with team conventions

---

## Phase 4: Team Integration

### Step 4.1: Bookmark Key Resources

Add these to your browser:

- [ ] [AI Coding Rules Repository](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules)
- [ ] [RULES_INDEX.md](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/blob/main/discovery/RULES_INDEX.md)
- [ ] [Project Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/issues) (for questions/feedback)

---

### Step 4.2: Join Team Channels

- [ ] **Slack:** #ai-coding-rules (ask your team lead for invite)
- [ ] **Teams:** AI Coding Rules Channel
- [ ] **Email List:** Subscribe to rule update notifications

---

### Step 4.3: Schedule Rule Updates

Add to your calendar:

- [ ] **Monthly:** Check for rule updates
  ```bash
  cd .ai-rules && git pull && cd ..
  git submodule update --remote .ai-rules
  ```

- [ ] **Quarterly:** Review which rules your team uses most
- [ ] **Yearly:** Suggest new rules for your domain

---

## Troubleshooting

### Issue: "Can't find .ai-rules directory"

**Solution:**
```bash
# Initialize submodule
git submodule update --init --recursive

# Verify
ls .ai-rules/
```

If still not working, check with your project lead if the submodule has been added to the project yet.

---

### Issue: "AI not loading rules automatically"

**Diagnosis:**
```bash
# Check if discovery files exist
ls .ai-rules/discovery/AGENTS.md
ls .ai-rules/discovery/RULES_INDEX.md

# Check if rules generated
ls .ai-rules/generated/universal/*.md | wc -l
# Should be 72+
```

**Solution:**
1. **If files missing:** Run `cd .ai-rules && task rule:all`
2. **If files exist:** Manually load `AGENTS.md` in your AI tool
3. **Still not working:** Try explicitly: "Load rules from .ai-rules/discovery/AGENTS.md"

---

### Issue: "Rules seem outdated"

**Solution:**
```bash
# Check current version
cd .ai-rules
git log -1 --oneline

# Update to latest
cd ..
git submodule update --remote .ai-rules
cd .ai-rules
task rule:all  # Regenerate

# Commit update
cd ..
git add .ai-rules
git commit -m "chore: update ai coding rules"
```

---

### Issue: "AI suggests different approach than rules"

**Diagnosis:**
- Check if AI actually loaded the rules
- Ask: "Which rules are you following?"

**Solution:**
1. **Explicitly reference rule:** "Follow rule 200-python-core for this task"
2. **Check rule version:** Rules may have been updated
3. **Report conflict:** If rule seems wrong, file an issue

---

### Issue: "Generated files missing"

**Solution:**
```bash
cd .ai-rules

# Install dependencies
task deps:dev

# Generate all formats
task rule:all

# Verify
ls generated/universal/*.md | wc -l
# Should be 72+
```

---

### Issue: "Permission denied accessing rules"

**Internal Snowflake Only:**
Contact your manager or team lead to request access to the internal GitLab repository.

---

## Quick Reference Card

Print or bookmark this for easy access:

### Common Commands

```bash
# Update rules
git submodule update --remote .ai-rules

# Regenerate rules
cd .ai-rules && task rule:all && cd ..

# Check rule count
ls .ai-rules/generated/universal/*.md | wc -l

# Search rules
grep -i "keyword" .ai-rules/discovery/RULES_INDEX.md

# Find specific rule
find .ai-rules/generated/universal -name "*python*"
```

### Common Prompts

```
"What rules are available for [technology]?"
"Load rules for [task] development"
"Review this code for rule compliance"
"Which rule covers [specific topic]?"
"Follow rule [number] for this implementation"
```

### Key Files

| File | Purpose | Location |
|------|---------|----------|
| `AGENTS.md` | Rule discovery guide | `.ai-rules/discovery/` |
| `RULES_INDEX.md` | Searchable catalog | `.ai-rules/discovery/` |
| `EXAMPLE_PROMPT.md` | Baseline prompt | `.ai-rules/discovery/` |
| `000-global-core.md` | Foundation rules | `.ai-rules/generated/universal/` |
| `README.md` | Full documentation | `.ai-rules/` |

---

## Getting Help

### Self-Service Resources

1. **README.md:** Comprehensive documentation
   - Architecture details
   - Advanced configuration
   - Troubleshooting guide

2. **RULES_INDEX.md:** Find rules by keyword
   - Search by technology
   - Browse by category (000-900)
   - Check dependencies

3. **AGENTS.md:** Rule loading protocol
   - Decision trees
   - Integration patterns
   - Best practices

### Team Support

1. **Slack:** #ai-coding-rules
   - Quick questions
   - Tips and tricks
   - Community support

2. **GitLab Issues:** [File an issue](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/issues)
   - Bug reports
   - Feature requests
   - Rule suggestions

3. **Team Lead:** Contact your manager
   - Access issues
   - Strategic questions
   - Process clarifications

---

## Next Steps

✅ **Onboarding Complete!** You're ready to use AI Coding Rules.

### Recommended Actions

1. **Try it out:** Create something with your AI assistant using the rules
2. **Share feedback:** What worked? What didn't?
3. **Help others:** Assist teammates with their onboarding
4. **Contribute:** Suggest improvements or new rules

### Advanced Topics (Optional)

- **Custom Rules:** Create project-specific rules
- **Rule Development:** Contribute to the rule repository
- **CI Integration:** Add rule validation to your pipeline
- **Team Templates:** Create starter templates with rules pre-configured

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

**Questions?** Reach out in #ai-coding-rules or file an issue.  
**Welcome to the team! 🚀**

