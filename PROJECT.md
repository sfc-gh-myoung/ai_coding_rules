# PROJECT.md

**Loading Context:** This file is loaded as part of AGENTS.md Step 2 (Mandatory Rule Loading Protocol).
AI agents MUST read this file after rules/000-global-core.md and before loading domain rules.

**Purpose:** Project-specific tooling requirements, conventions, and overrides that apply to THIS project only.
Rules in rules/ directory provide general guidance; this file specifies ai_coding_rules project specifics.

This file provides project-specific guidance for AI coding assistants working with code in this repository. It is automatically loaded by AI assistants that support project configuration files (e.g., Cursor, Claude Code, GitHub Copilot, VS Code extensions).

## Quick Reference (Most Common Operations)

- **Fix linting/formatting:** `./dev quality:fix`
- **Run full validation:** `./dev validate` (REQUIRED before commits)
- **Run tests:** `./dev test`
- **Create new rule:** `./dev rule:new FILENAME=XXX-name`
- **Deploy rules:** `./dev deploy DEST=~/project`
- **Regenerate index:** `./dev index:generate`

## Critical Validation Requirements

**Validation Gate Protocol (execute before ANY commit):**

Step 1: Execute validation suite
  - EXECUTE: `./dev validate`
  - CAPTURE: Exit code

Step 2: Interpret result
  - IF exit_code == 0: ALL checks passed, PROCEED to Step 3
  - ELSE IF exit_code != 0: At least one check failed, STOP

Step 3: Commit authorization
  - IF Step 2 result == PROCEED: Commit is authorized
  - ELSE: DO NOT commit, report failure to user

**CRITICAL VIOLATION:** Committing with exit_code != 0 invalidates all subsequent work.

**Validation checks that MUST pass:**
1. **Linting** - Code passes all lint checks
2. **Formatting** - Code passes format verification
3. **Type Checking** - Code passes type checker (if applicable)
4. **Compilation** - Code compiles without errors (if applicable)
5. **Tests** - All tests pass

## ai_coding_rules Project Requirements

**CRITICAL: This project mandates specific tooling. Other projects using these rules may choose different tools.**

### Mandatory Tooling for ai_coding_rules

**Python Runtime (REQUIRED):**
- ALLOWED: `uv run python`, `uv run pytest`, `uvx ruff`
- FORBIDDEN: `python` (bare), `pip` (bare), `pytest` (bare), `python3`
- DETECTION: IF command starts with "python " OR "pip " OR "pytest ": HALT, rewrite as "uv run [command]"

**Code Quality (REQUIRED):**
- Linting: EXECUTE `uvx ruff check .` (NOT `ruff check .`)
- Formatting: EXECUTE `uvx ruff format .` (NOT `ruff format .`)
- Type checking: EXECUTE `uvx ty check .` (NOT `ty check .` OR `mypy .`)

**Validation Gates (all must succeed):**

Gate 1: Linting
  - EXECUTE: `uvx ruff check .`
  - SUCCESS: Exit code 0, output "All checks passed!" OR no output
  - FAILURE: Exit code != 0 OR output contains "error:" OR "warning:"

Gate 2: Format Verification
  - EXECUTE: `uvx ruff format --check .`
  - SUCCESS: Exit code 0, no files would be reformatted
  - FAILURE: Exit code != 0 OR output lists files that would change

Gate 3: Type Checking
  - EXECUTE: `uvx ty check .`
  - SUCCESS: Exit code 0, output "Success: no issues found" OR similar
  - FAILURE: Exit code != 0 OR output contains "error:" line

Gate 4: Tests
  - EXECUTE: `uv run pytest`
  - SUCCESS: Exit code 0, output ends with "N passed" (0 failed)
  - FAILURE: Exit code != 0 OR output contains "FAILED" OR "ERROR"

**Shortcut command:**
```bash
./dev validate            # Runs all checks
```

**Project Structure:**
- `pyproject.toml` with uv configuration
- `uv.lock` for dependency locking
- `dev` - bash wrapper script for automation

**Why:** This project demonstrates Astral's modern Python toolchain (uv/ruff/ty). Deployed rules respect alternative toolchains (poetry/pip/black/mypy).

**Rules Are Not Mandates:**

The rules in `rules/` directory provide **recommendations** and **preferences** for modern Python development. They allow projects to use alternative toolchains (poetry, pip, black, mypy) when appropriate. Only THIS project (ai_coding_rules) mandates uv/uvx/ruff/ty.

## High-Level Architecture

**System:** Direct rule editing with no generation step. Rules in `rules/` are production-ready and deploy directly.

**Core Components:**
- `rules/` - 122 production-ready Markdown files with embedded metadata (validated against `schemas/rule-schema.yml`)
- `AGENTS.md` - Bootstrap protocol (always loaded with rules/000-global-core.md)
- `rules/RULES_INDEX.md` - Auto-generated catalog for keyword-based discovery
- `src/ai_rules/` - CLI commands for validation/deployment (98% test coverage)

**Rule Organization:** 3-digit prefix (000-999) by domain: Core (000-099), Snowflake (100-199), Python (200-299), Shell (300-399), Frontend/Containers (400-499), Go (600-699), Project (800-899), Analytics (900-999)

**Discovery:** AGENTS.md → search RULES_INDEX.md by keywords → load dependencies → apply rules

**Deployment:** `./dev deploy DEST=~/project` copies rules/, AGENTS.md, RULES_INDEX.md, and skills/ to target

**Skills:** 3 deployed (doc-reviewer, plan-reviewer, skill-timing), 3 internal-only (rule-creator, rule-reviewer, bulk-rule-reviewer)

### Component Relationships

```
AGENTS.md (Bootstrap Protocol)
    │
    ├─ loads ─────────────────► rules/000-global-core.md (Foundation)
    │                                    │
    │                                    ├─ searches ──► rules/RULES_INDEX.md (Catalog)
    │                                    │                       │
    │                                    │                       └─ loads ──► rules/XXX-domain.md
    │                                    │
    │                                    └─ references ► PROJECT.md (This File)
    │
    └─ deploys via ───────────► ai-rules deploy (CLI)
                                        │
                                        ├─► TARGET/rules/
                                        ├─► TARGET/skills/ (deployed only)
                                        └─► TARGET/AGENTS.md

Validation Flow:
    ai-rules validate    ◄── validates ──► schemas/rule-schema.yml
    ai-rules index       ─── generates ──► rules/RULES_INDEX.md
    ai-rules rule new    ── creates ───► rules/XXX-new-rule.md

Skill Output:
    skills/rule-reviewer/    ─── writes to ───► reviews/rule-reviews/
    skills/doc-reviewer/     ─── writes to ───► reviews/doc-reviews/
    skills/plan-reviewer/    ─── writes to ───► reviews/plan-reviews/
```

### Rules Domain Mapping

| Range | Domain | Count | Key Rules |
|-------|--------|-------|-----------|
| 000-099 | Core/Foundation | 12 | `000-global-core`, `002-rule-governance`, `003-context-engineering` |
| 100-199 | Snowflake | 58 | SQL (`102`), Streamlit (`101`), Cortex AI (`115-117`), Security (`130-133`) |
| 200-299 | Python | 27 | Core (`200`), FastAPI (`210`), Pytest (`206`), Pydantic (`207`), HTMX (`221`) |
| 300-349 | Shell | 7 | Bash (`300`), Zsh (`301`) |
| 350-399 | Containers | 2 | Docker (`350`), Podman (`351`) |
| 400-499 | Frontend/JS | 5 | JavaScript (`420`), TypeScript (`430`), React (`440`), Alpine.js (`450`) |
| 500-599 | Frontend | 2 | HTMX frontend (`500`), Browser globals (`510`) |
| 600-699 | Go | 1 | `600-golang-core` |
| 800-899 | Project Mgmt | 5 | Changelog (`800`), README (`801`), Git (`803`), Taskfile (`820`) |
| 900-999 | Analytics | 4 | Data science (`900`), Governance (`910`), Business analytics (`920`) |

**Usage:** When creating a new rule, select the appropriate range based on domain. Use `./dev rule:new FILENAME=1XX-snowflake-feature` for Snowflake rules, `2XX-python-feature` for Python, etc.

### Scripts Reference

| Script | Purpose | Dev Command |
|--------|---------|-------------|
| `schema_validator.py` | Validate rules against v3.2 schema | `./dev rules:validate` |
| `index_generator.py` | Generate RULES_INDEX.md from metadata | `./dev index:generate` |
| `template_generator.py` | Create new v3.2-compliant rule templates | `./dev rule:new` |
| `rule_deployer.py` | Deploy rules + skills to target projects | `./dev deploy` |
| `token_validator.py` | Check TokenBudget accuracy (±10%) | `./dev tokens:check` |
| `keyword_generator.py` | TF-IDF keyword suggestions | `./dev keywords:suggest` |
| `badge_updater.py` | Update README badges (version, coverage) | `./dev badges:update` |
| `validate_index_references.py` | Verify RULES_INDEX.md references | (used by CI) |

### Skills Deployment Matrix

| Skill | Deployed | Purpose | Output Directory |
|-------|----------|---------|------------------|
| `doc-reviewer/` | Yes | Review documentation quality | `reviews/doc-reviews/` |
| `plan-reviewer/` | Yes | Review LLM plans for executability | `reviews/plan-reviews/` |
| `skill-timing/` | Yes | Measure skill execution time | N/A |
| `rule-reviewer/` | No | Review rule quality (internal) | `reviews/rule-reviews/` |
| `rule-creator/` | No | Create new rules (internal) | N/A |
| `bulk-rule-reviewer/` | No | Bulk rule reviews (internal) | `reviews/rule-reviews/` |

**Configuration:** Exclusions defined in `pyproject.toml [tool.rule_deployer].exclude_skills`

### Rules Examples

The `rules/examples/` directory contains validated implementation examples for complex Snowflake configurations:

| Example File | Purpose |
|--------------|---------|
| `115-cortex-agent-*-example.md` | Cortex Agent setup patterns (prerequisites, hybrid SQL/Python) |
| `116-cortex-search-service-example.md` | Cortex Search Service configuration |
| `106-semantic-view-*-example.md` | Semantic View YAML, DDL, and workarounds |
| `120-spcs-service-spec-example.md` | SPCS container service specifications |
| `121-snowpipe-auto-ingest-example.md` | Snowpipe auto-ingest configuration |
| `001-memory-bank-templates-example.md` | Memory Bank template patterns |

**Usage:** Load parent rule + example when working on complex Snowflake features.
**Validation:** `./dev examples:validate`

## Required Permissions

AI assistants must verify they have necessary permissions before performing operations.

### Filesystem Permissions

**Read permissions required:**
- `rules/` directory and all .md files (for validation, deployment)
- `schemas/rule-schema.yml` (for schema validation)
- `rules/RULES_INDEX.md` (for index verification)
- `AGENTS.md` (for deployment)
- `src/ai_rules/` directory and all .py files (for CLI commands)
- `tests/` directory and all test files (for testing)

**Write permissions required:**
- `rules/` directory (for creating/editing rules)
- `rules/RULES_INDEX.md` (for index regeneration)
- `.pytest_cache/`, `__pycache__/` (for test execution)
- `reviews/` directory (for review output, if using review skills)
- `plans/` directory (for plan documents, if using plan-reviewer skill)

**Execute permissions required:**
- `./dev` wrapper script (bash)

**Permission Verification Protocol (execute before file operations):**

Before ANY file write operation:
  1. EXECUTE: `test -w [target_directory] && echo "WRITABLE" || echo "NOT_WRITABLE"`
  2. IF output != "WRITABLE": STOP, report permission error to user
  3. ELSE: Proceed with write operation

Before ANY git commit:
  1. EXECUTE: `git config user.name && git config user.email`
  2. IF either command returns empty: STOP, report "Git not configured"
  3. ELSE: Proceed with commit

### Git Permissions

**Required for commits:**
- Write access to repository
- Configured git user.name and user.email
- SSH key (if using SSH) or personal access token (if using HTTPS)

**Required for branches:**
- Create branch permission
- Push to remote permission (if pushing branches)

**Required for deployment:**
- Read access to source repository
- Write access to destination directory

### AI Commit Attribution

**Project Default:** `ai_attribution_footer: false`

This project does NOT include AI attribution footers in commit messages by default.
Users may override per-session by responding to the prompt defined in `803-project-git-workflow.md`.

**Valid values:**
- `true` - Always include AI attribution footer
- `false` - Never include AI attribution footer (default for this project)
- `ask` - Prompt user on first commit each session

## Key Workflows

### Creating a New Rule

```bash
# 1. Generate template with validation
./dev rule:new FILENAME=XXX-new-rule TIER=High

# 2. Edit the generated file (replace placeholders)
vim rules/XXX-new-rule.md

# 3. Validate your changes
./dev rules:validate:verbose

# 4. Update index
./dev index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-new-rule.md rules/RULES_INDEX.md
git commit -m "feat: add XXX rule for [technology]"
```

### Updating an Existing Rule

```bash
# 1. Edit the rule file
vim rules/XXX-rule.md

# 2. Validate changes
uv run ai-rules validate rules/XXX-rule.md --verbose

# 3. Update token budget if content changed by >20% (e.g., declared 5000 tokens, actual 6100 tokens)
#    Check variance: |actual - declared| / declared > 0.20
uv run ai-rules tokens check rules/XXX-rule.md

# 4. Regenerate index if metadata changed
./dev index:generate
git add RULES_INDEX.md
   ```

4. **Follow Conventional Commits:**
   ```bash
   git commit -m "feat(domain): add new feature"
   git commit -m "fix(rules): correct validation issue"
   git commit -m "docs(readme): improve installation guide"
   ```

5. **Run full validation before PR:**
   ```bash
   ./dev validate  # Runs all CI/CD checks
   ```

## Schema Version vs Project Version

- **SchemaVersion** (v3.2): Rule metadata format version
  - Appears in rule files: `**SchemaVersion:** v3.2`
  - Changes when rule structure evolves
  - All rules must use same schema version

- **Project Version** (v3.5.1): Release version
  - Appears in pyproject.toml and README badges
  - Follows semantic versioning
  - Independent of schema version

## Common Patterns

### Investigation-First Protocol

Always investigate before making changes:

```bash
# Read files before editing
uv run ai-rules validate rules/XXX-rule.md --verbose

# Check dependencies
grep "**Depends:**" rules/XXX-rule.md

# Verify rule exists in index
grep "XXX-rule" RULES_INDEX.md
```

### Token Budget Management

Token budgets track context window usage:

```bash
# Check single file
uv run ai-rules tokens check rules/XXX-rule.md --dry-run --detailed

# Update all budgets
./dev tokens:update

# Check all budgets
./dev tokens:check
```

### Keyword Generation

Keywords enable semantic rule discovery:

```bash
# Suggest keywords for a rule
./dev keywords:suggest FILE=rules/XXX-rule.md

# Show diff of current vs suggested
./dev keywords:diff FILE=rules/XXX-rule.md

# Update keywords in-place
./dev keywords:update FILE=rules/XXX-rule.md
```

## Testing Philosophy

The project maintains 98% test coverage with comprehensive test suites:

- **Unit tests:** All validation scripts (schema_validator, token_validator, etc.)
- **Integration tests:** Rule deployment, index generation
- **Validation tests:** Schema compliance, metadata accuracy

Run tests frequently during development:

```bash
./dev test                  # Quick test run
./dev test:coverage         # Full coverage report
uv run pytest tests/test_schema_validator.py -v  # Specific test
```

## Documentation Structure

- **README.md** - User-facing documentation, setup, usage
- **CONTRIBUTING.md** - Development guidelines, PR process
- **AGENTS.md** - Bootstrap protocol for AI agents
- **PROJECT.md** - Project-specific configuration (this file)
- **CHANGELOG.md** - Version history (single source of truth)
- **docs/ARCHITECTURE.md** - System design, technical decisions
- **docs/MEMORY_BANK.md** - Context continuity system (optional)
- **docs/USING_*_SKILL.md** - Individual skill usage guides

## Common Task Patterns

### Adding a New Snowflake Rule

```bash
# 1. Create rule in appropriate range (100-199)
./dev rule:new FILENAME=1XX-snowflake-feature TIER=High

# 2. Edit rule content
vim rules/1XX-snowflake-feature.md

# 3. If complex feature, add example
vim rules/examples/1XX-snowflake-feature-example.md

# 4. Validate and update index
./dev validate && ./dev index:generate

# 5. Commit (only after validation passes)
git add rules/ && git commit -m "feat(snowflake): add 1XX rule for feature"
```

### Fixing Validation Failures

```bash
# Step 1: Auto-fix lint and format issues
./dev quality:fix

# Step 2: Fix type errors manually (ty shows locations)
uvx ty check .

# Step 3: Review and fix test failures
uv run pytest -v --tb=short

# Step 4: Fix schema validation errors
./dev rules:validate:verbose
# Fix errors in order: CRITICAL → HIGH → MEDIUM → LOW

# Step 5: Re-run full validation
./dev validate
```

### Deploying to Another Project

```bash
# Preview what will be deployed
./dev deploy:dry DEST=~/other-project

# Execute deployment
./dev deploy DEST=~/other-project

# Verify deployment
ls ~/other-project/rules/ | wc -l      # Should be ~125
ls ~/other-project/skills/ | wc -l     # Should be 3 (deployed skills)
cat ~/other-project/AGENTS.md | head   # Verify bootstrap protocol
```

### Updating Multiple Rules (Bulk Operations)

```bash
# Update token budgets for all rules
./dev tokens:update

# Regenerate keywords using TF-IDF
./dev keywords:all

# Validate all rules
./dev rules:validate

# Regenerate index after bulk changes
./dev index:generate

# Run full validation
./dev validate
```

## Troubleshooting

### Network Timeout Recovery (max 2 attempts)

Attempt 1: `ping github.com -c 1` → IF success: Retry git operation → ELSE: Attempt 2
Attempt 2: `ssh -T git@github.com` → IF authenticated: Retry → ELSE: STOP, report "Network unavailable. Work offline: commit locally, push when restored."

### Permission Denied

**Filesystem write fails:** Check `ls -la [path]`, verify ownership `stat [path]`, check parent permissions. Request access if needed.
**Git commit fails:** Check `git config --list | grep user`, verify SSH key `ls -la ~/.ssh/id_*`, fix permissions `chmod 600 ~/.ssh/id_rsa`.

### Tool Availability

**uv not found:** Install via `curl -LsSf https://astral.sh/uv/install.sh | sh`, reload shell
**ruff/ty not found:** Run `uvx ruff --version` or `uvx ty --version` (auto-installs)

### Resource Exhaustion

**Disk space:** Clean caches: `rm -rf .pytest_cache __pycache__` + `uv cache clean` (require 2GB minimum)
**Memory:** Close applications, process in batches <1000 rules (require 4GB RAM minimum)
**Open files:** Increase limit: `ulimit -n 4096`

### Validation Failures

**./dev validate fails:** Run individual checks (`./dev quality:lint`, `./dev test`, etc.), fix in order, re-run after each
**Schema validation fails:** Run `uv run ai-rules validate rules/XXX-rule.md --verbose`, fix CRITICAL → HIGH → MEDIUM → LOW

---

## Appendix: CLI Command Usage (Advanced)

**Recommendation:** Use ./dev commands (Quick Reference section). Direct CLI usage is only for custom CI/CD pipelines or non-./dev automation. All commands are available via `uv run ai-rules [command]`. Run `uv run ai-rules --help` for complete documentation.
