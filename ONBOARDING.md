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

#### Option A: Deploy to Existing Project (Recommended)

```bash
# Clone the rules repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules

# Deploy rules to your project (choose one)
task deploy:universal DEST=~/my-project    # For any IDE/LLM
task deploy:cursor DEST=~/my-project       # For Cursor IDE
task deploy:copilot DEST=~/my-project      # For GitHub Copilot
task deploy:cline DEST=~/my-project        # For Cline

# Verify deployment
ls ~/my-project/rules/*.md | wc -l   # Universal: Should show 72+
# OR
ls ~/my-project/.cursor/rules/*.mdc | wc -l  # Cursor: Should show 72+
```

✅ **Success!** Rules deployed with correct paths. Skip to Step 1.2.

#### Option B: Add as Git Submodule

```bash
# From your project root
git submodule add https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git .ai-rules
cd .ai-rules

# Deploy rules to parent project
task deploy:universal DEST=..   # For any IDE/LLM
# OR
task deploy:cursor DEST=..      # For Cursor IDE

# Verify deployment
cd .. && ls rules/*.md | wc -l  # Should show 72+
```

#### Option C: Deployment Without Task

If you don't have Task installed, use the Python deployment script directly:

```bash
# Clone repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules

# Install dependencies
/opt/homebrew/bin/uv sync

# Deploy using Python script (handles everything automatically)
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project

# Verify
ls ~/my-project/rules/*.md | wc -l  # Should show 72+
ls ~/my-project/AGENTS.md ~/my-project/RULES_INDEX.md  # Both should exist
```

**For other formats:**
```bash
# Cursor
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent cursor --destination ~/my-project

# Copilot
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent copilot --destination ~/my-project

# Cline
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent cline --destination ~/my-project
```

**What happens automatically:**
- ✅ Generates rules for your agent type
- ✅ Copies to correct directory (`.cursor/rules/`, `rules/`, etc.)
- ✅ Updates `AGENTS.md` with proper paths
- ✅ Copies `RULES_INDEX.md` to project root
- ✅ No manual editing needed!

---

### Step 1.2: Choose Your AI Tool

Which tool(s) do you use? Check all that apply:

- [ ] **Cursor IDE** → Go to Step 2.1
- [ ] **Claude Projects** → Go to Step 2.2
- [ ] **VS Code + GitHub Copilot** → Go to Step 2.3
- [ ] **Cline AI Assistant** → Go to Step 2.4
- [ ] **Other (ChatGPT, etc.)** → Go to Step 2.5

---

### Step 1.3: Verify Setup

```bash
# For universal deployment
ls rules/*.md | wc -l           # Expected: 72+
ls AGENTS.md RULES_INDEX.md     # Both files should exist

# For Cursor deployment
ls .cursor/rules/*.mdc | wc -l  # Expected: 72+
ls AGENTS.md RULES_INDEX.md     # Both files should exist

# For Copilot deployment
ls .github/copilot/instructions/*.md | wc -l  # Expected: 72+
```

**All checks passed?** ✅ Continue to Phase 2.  
**Issues?** See [Troubleshooting](#troubleshooting) below.

---

## Phase 2: Tool Configuration

### Step 2.1: Configure Cursor IDE

#### If You Deployed Cursor Rules

If you used `task deploy:cursor`, Cursor automatically loads rules from `.cursor/rules/`!

**Verify:**
```
Ask Cursor: "What rules are available for Python?"
```

**Expected:** Cursor lists relevant rules from your `.cursor/rules/` directory

#### If You Have Rules Elsewhere

1. Open Cursor IDE
2. Open your project
3. Start a new conversation
4. Type: `@AGENTS.md` (loads rule discovery guide)

**Verification Checklist:**
- [ ] Cursor shows rules in context panel
- [ ] AI references specific rule numbers (e.g., "Per rule 200...")
- [ ] Code follows project conventions

---

### Step 2.2: Configure Claude Projects

1. **Open Claude.ai** → Navigate to your project (or create new)
2. **Go to "Project Knowledge"**
3. **Upload files from your project:**
   - [ ] `AGENTS.md` (rule loading protocol)
   - [ ] `RULES_INDEX.md` (rule catalog)
   - [ ] `rules/*.md` (upload all or just the rules you need)

4. **Test:**
```
Ask Claude: "What rules are available for Python?"
```

**Expected:** Claude lists relevant Python rules from RULES_INDEX.md

**Verification Checklist:**
- [ ] Files uploaded successfully
- [ ] Claude references specific rules (e.g., "Per rule 200...")
- [ ] Claude applies rules to generated code

---

### Step 2.3: Configure VS Code + GitHub Copilot

#### If You Deployed Copilot Rules

If you used `task deploy:copilot`, GitHub Copilot automatically reads from `.github/copilot/instructions/`!

**Important:** Commit and push the files:
```bash
git add .github/copilot/instructions/ AGENTS.md RULES_INDEX.md
git commit -m "chore: add AI coding rules"
git push
```

GitHub Copilot reads from your repository (takes 5-10 minutes to sync).

**Verification:**
```
Ask Copilot: "What Python coding standards should I follow?"
```

**Expected:** Copilot references your project's Python rules

**Verification Checklist:**
- [ ] Files committed and pushed to repository
- [ ] Copilot suggestions follow project conventions
- [ ] Copilot references specific rules

---

### Step 2.4: Configure Cline AI Assistant

#### If You Deployed Cline Rules

If you used `task deploy:cline`, Cline automatically processes all `.md` files in `.clinerules/`!

**Verify:**
```
Ask Cline: "What rules govern Python development here?"
```

**Expected:** Cline references rules from `.clinerules/` directory

**Verification Checklist:**
- [ ] Cline shows awareness of rules
- [ ] Cline references specific rules in responses
- [ ] Generated code follows project conventions

---

### Step 2.5: Other Tools (ChatGPT, etc.)

#### For ChatGPT

1. Open ChatGPT
2. Start new conversation
3. Upload files from your project:
   - `AGENTS.md` (rule loading protocol)
   - `RULES_INDEX.md` (rule catalog)
   - Relevant rule files (e.g., `rules/200-python-core.md`)

**Test:**
```
Ask ChatGPT: "What rules are available for Python?"
```

#### For Universal Deployment

If you deployed with `task deploy:universal`, you have:
- `rules/*.md` — 72+ rule files
- `AGENTS.md` — Rule loading protocol
- `RULES_INDEX.md` — Rule catalog

Upload these files to your AI tool's context/knowledge base.

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
  # With Task:
  cd /tmp/ai-rules && git pull
  task deploy:universal DEST=~/my-project
  
  # Without Task (Python script):
  cd /tmp/ai-rules && git pull
  /opt/homebrew/bin/uv sync
  /opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
  ```

- [ ] **Quarterly:** Review which rules your team uses most
- [ ] **Yearly:** Suggest new rules for your domain

---

## Troubleshooting

### Issue: "Rules not found in my project"

**Solution:**
```bash
# Check if rules were deployed
ls rules/*.md | wc -l                     # Universal deployment
ls .cursor/rules/*.mdc | wc -l            # Cursor deployment
ls .github/copilot/instructions/*.md | wc -l  # Copilot deployment

# If no files found, deploy rules
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules
/opt/homebrew/bin/uv sync

# With Task:
task deploy:universal DEST=~/my-project

# Without Task:
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

---

### Issue: "AI not loading rules automatically"

**Diagnosis:**
```bash
# Check if discovery files exist in your project root
ls AGENTS.md RULES_INDEX.md

# Check if rules exist
ls rules/*.md | wc -l  # Should be 72+
```

**Solution:**
1. **If files missing:** Re-deploy:
   ```bash
   # With Task:
   task deploy:universal DEST=~/my-project
   
   # Without Task:
   /opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
   ```
2. **If files exist:** Manually reference `@AGENTS.md` in your AI tool
3. **Still not working:** Upload files directly to AI tool's knowledge base

---

### Issue: "Rules seem outdated"

**Solution:**
```bash
# Pull latest rules and re-deploy
cd /tmp/ai-rules
git pull
/opt/homebrew/bin/uv sync

# With Task:
task deploy:universal DEST=~/my-project

# Without Task:
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

---

### Issue: "AI suggests different approach than rules"

**Solution:**
1. **Explicitly reference rule:** "Follow rule 200-python-core for this task"
2. **Verify AI has access:** Ask "Which rules are you following?"
3. **Check rule content:** Read the rule file to verify it says what you expect
4. **Report conflict:** File an issue if rule seems incorrect

---

### Issue: "Permission denied accessing rules"

**Internal Snowflake Only:**
Contact your manager or team lead to request access to the internal GitLab repository.

---

### Issue: "Task command not found"

**Problem:** Don't have Task installed or can't install it

**Solution:** Use Python deployment script directly (Option C)

See [Option C: Deployment Without Task](#option-c-deployment-without-task) for complete instructions.

Quick commands for universal rules:
```bash
cd /tmp/ai-rules
/opt/homebrew/bin/uv sync
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

---

## Quick Reference Card

Print or bookmark this for easy access:

### Common Commands

**With Task:**
```bash
# Deploy/update rules
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules
task deploy:universal DEST=~/my-project
```

**Without Task (Python script):**
```bash
# Deploy/update rules using Python script
cd /tmp/ai-rules
/opt/homebrew/bin/uv sync
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

**General:**
```bash
# Check rule count
ls rules/*.md | wc -l  # Should show 72+

# Search rules
grep -i "keyword" RULES_INDEX.md

# Find specific rule
find rules -name "*python*"
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

| File | Purpose | Location (after deployment) |
|------|---------|----------|
| `AGENTS.md` | Rule discovery guide | Project root |
| `RULES_INDEX.md` | Searchable catalog | Project root |
| `000-global-core.md` | Foundation rules | `rules/` or `.cursor/rules/` |
| All rule files | 72+ specialized rules | `rules/` or IDE-specific directory |

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

