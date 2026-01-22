# PROJECT.md

**Loading Context:** This file is loaded as part of AGENTS.md Step 2 (Mandatory Rule Loading Protocol).
AI agents MUST read this file after rules/000-global-core.md and before loading domain rules.

**Purpose:** Project-specific tooling requirements, conventions, and overrides that apply to THIS project only.
Rules in rules/ directory provide general guidance; this file specifies ai_coding_rules project specifics.

This file provides project-specific guidance for AI coding assistants working with code in this repository. It is automatically loaded by AI assistants that support project configuration files (e.g., Cursor, Claude Code, GitHub Copilot, VS Code extensions).

## Quick Reference (Most Common Operations)

- **Fix linting/formatting:** `task quality:fix`
- **Run full validation:** `task validate` (REQUIRED before commits)
- **Run tests:** `task test`
- **Create new rule:** `task rule:new FILENAME=XXX-name`
- **Deploy rules:** `task deploy DEST=~/project`
- **Regenerate index:** `task index:generate`

## Critical Validation Requirements

**Validation Gate Protocol (execute before ANY commit):**

Step 1: Execute validation suite
  - EXECUTE: `task validate`
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
task validate             # Runs all checks
```

**Project Structure:**
- `pyproject.toml` with uv configuration
- `uv.lock` for dependency locking
- `Taskfile.yml` for automation

**Why:** This project demonstrates Astral's modern Python toolchain (uv/ruff/ty). Deployed rules respect alternative toolchains (poetry/pip/black/mypy).

**Rules Are Not Mandates:**

The rules in `rules/` directory provide **recommendations** and **preferences** for modern Python development. They allow projects to use alternative toolchains (poetry, pip, black, mypy) when appropriate. Only THIS project (ai_coding_rules) mandates uv/uvx/ruff/ty.

## High-Level Architecture

**System:** Direct rule editing with no generation step. Rules in `rules/` are production-ready and deploy directly.

**Core Components:**
- `rules/` - 122 production-ready Markdown files with embedded metadata (validated against `schemas/rule-schema.yml`)
- `AGENTS.md` - Bootstrap protocol (always loaded with rules/000-global-core.md)
- `rules/RULES_INDEX.md` - Auto-generated catalog for keyword-based discovery
- `scripts/` - Validation/deployment tools (98% test coverage)

**Rule Organization:** 3-digit prefix (000-999) by domain: Core (000-099), Snowflake (100-199), Python (200-299), Shell (300-399), Frontend/Containers (400-499), Go (600-699), Project (800-899), Analytics (900-999)

**Discovery:** AGENTS.md → search RULES_INDEX.md by keywords → load dependencies → apply rules

**Deployment:** `task deploy DEST=~/project` copies rules/, AGENTS.md, RULES_INDEX.md, and skills/ to target

**Skills:** 3 deployed (doc-reviewer, plan-reviewer, skill-timing), 3 internal-only (rule-creator, rule-reviewer, bulk-rule-reviewer)

## Required Permissions

AI assistants must verify they have necessary permissions before performing operations.

### Filesystem Permissions

**Read permissions required:**
- `rules/` directory and all .md files (for validation, deployment)
- `schemas/rule-schema.yml` (for schema validation)
- `rules/RULES_INDEX.md` (for index verification)
- `AGENTS.md` (for deployment)
- `scripts/` directory and all .py files (for running validation)
- `tests/` directory and all test files (for testing)

**Write permissions required:**
- `rules/` directory (for creating/editing rules)
- `rules/RULES_INDEX.md` (for index regeneration)
- `.pytest_cache/`, `__pycache__/` (for test execution)
- `reviews/` directory (for review output, if using review skills)
- `plans/` directory (for plan documents, if using plan-reviewer skill)

**Execute permissions required:**
- Python scripts in `scripts/` directory
- Task binary (for running Taskfile commands)

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
task rule:new FILENAME=XXX-new-rule TIER=High

# 2. Edit the generated file (replace placeholders)
vim rules/XXX-new-rule.md

# 3. Validate your changes
task rules:validate:verbose

# 4. Update index
task index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-new-rule.md rules/RULES_INDEX.md
git commit -m "feat: add XXX rule for [technology]"
```

### Updating an Existing Rule

```bash
# 1. Edit the rule file
vim rules/XXX-rule.md

# 2. Validate changes
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# 3. Update token budget if content changed by >20% (e.g., declared 5000 tokens, actual 6100 tokens)
#    Check variance: |actual - declared| / declared > 0.20
uv run python scripts/token_validator.py rules/XXX-rule.md

# 4. Regenerate index if metadata changed
task index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-rule.md rules/RULES_INDEX.md
git commit -m "fix: update XXX rule with [improvement]"
```

### Running Validation

Use Quick Reference commands (lines 11-18). Run `task validate` before commits.

### Monitoring Execution Progress

AI assistants should monitor long-running operations and report progress.

**Universal Monitoring Pattern:**
1. Execute command
2. Watch for status indicators (PASSED/FAILED, error:, exit code)
3. Note completion metrics (N passed, M failed)
4. IF any failures: Investigate with -v flag
5. Re-run after fixes

**Command-Specific Status Indicators:**
- `task validate`: "All checks passed" + exit code 0 = success
- `uv run pytest`: "N passed, 0 failed" + exit code 0 = success
- `task deploy`: "Deployment complete: X rules, Y skills" = success
- `task rules:validate`: "RESULT: PASSED" + exit code 0 = success
- `task index:check`: "RULES_INDEX.md is up-to-date" = success

**Success Criteria:** Exit code 0 + expected completion message

### Testing Changes

Use Quick Reference commands (lines 11-18). Run `task test` or `task test:coverage`.

## Error Recovery and Edge Cases

AI assistants must handle these error scenarios and edge cases according to documented procedures.

### Empty/Zero-State Scenarios

**Empty rules/:**
- **Detection:** `ls rules/ | wc -l` returns 0 OR rules/000-global-core.md missing
- **Action:** Run `task rule:new FILENAME=000-global-core TIER=Critical` to create foundation rule
- **Validation:** Verify `rules/000-global-core.md` exists and passes schema validation
- **Minimum requirement:** Must have rules/000-global-core.md before deployment

**Zero test cases:**
- **Detection:** `find tests/ -name "test_*.py" | wc -l` returns 0
- **Action:** Create smoke test: `tests/test_smoke.py` with basic import checks
- **Behavior:** `task test` will pass but warn "no tests collected"
- **Minimum requirement:** At least 1 test required for CI/CD validation
- **Example smoke test:**
  ```python
  def test_imports():
      """Verify critical modules can be imported."""
      import scripts.schema_validator
      import scripts.token_validator
      import scripts.index_generator
      assert True
  ```

**Empty RULES_INDEX.md:**
- **Detection:** File missing OR file <100 bytes
- **Action:** Run `task index:generate` to regenerate from rule metadata
- **Validation:** Verify file >1KB and contains "## Rule Catalog" header

### Concurrent Modifications

**Git Conflict Resolution Protocol:**

Detection:
  - EXECUTE: `git status`
  - IF output contains "both modified:": Conflict detected, EXECUTE resolution

Resolution (automated):
  - IF conflicting file is .json OR .yml OR .lock: STOP, escalate to user (structured files require manual merge)
  - ELSE IF conflicting file is .md: ATTEMPT automated merge (continue below)

Automated Merge Procedure:
  1. EXECUTE: `git diff [filename]`
  2. IF both sides modified same line: STOP, escalate to user
  3. ELSE IF different sections modified: Apply both changes
  4. EXECUTE validation: `uv run python scripts/schema_validator.py [filename]`
  5. IF validation fails: REVERT, escalate to user
  6. ELSE: EXECUTE `git add [filename] && git commit`

**Multiple agents editing same rule:**
- **Detection:** Awareness of concurrent sessions
- **Action:** Coordinate via git branches
- **Procedure:**
  1. Each agent creates branch: `git checkout -b agent-<name>-<task>`
  2. Make changes in separate branches
  3. Merge sequentially (one at a time) to avoid conflicts
  4. First merge: Direct to main
  5. Subsequent merges: Rebase on main first (`git rebase main`)

**RULES_INDEX.md out of sync:**
- **Detection:** `task index:check` fails with "Index out of sync" error
- **Action:** Regenerate index: `task index:generate`
- **Cause:** Rule metadata changed but index not updated
- **Prevention:** Always run `task index:generate` after changing rule metadata

### Dependency Resolution Conflicts

**uv dependency resolution fails:**
- **Detection:** `uv pip install` fails with "Could not find a version that satisfies"
- **Action:**
  1. Check Python version: `python --version` (require 3.11+)
  2. Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  3. Clear cache: `uv cache clean`
  4. Try again: `uv pip install -r requirements.txt`
  5. If still fails: Check pyproject.toml for incompatible constraints

**Missing rule dependencies:**
- **Detection:** Schema validator reports "Dependency not found: rules/XXX-rule.md"
- **Action:**
  1. Verify file exists: `ls -la rules/XXX-rule.md`
  2. If missing: Create rule OR update Depends field to remove reference
  3. If filename wrong: Correct Depends field to match actual filename
- **Validation:** Run `task rules:validate` after fix

**Circular dependencies:**
- **Detection:** Schema validator reports "Circular dependency detected"
- **Action:**
  1. Review dependency chain in error message
  2. Identify cycle: A → B → C → A
  3. Break cycle: Remove one dependency (usually the "upward" reference)
  4. Document relationship in rule content instead of Depends field
- **Best practice:** Dependencies should form a DAG (directed acyclic graph)

### Large File/Bulk Operations

**Bulk rule validation (>50 rules):**
- **Command:** `uv run python scripts/schema_validator.py rules/`
- **Progress:** Shows "Validating N files..." with progress counter
- **Timeout:** Allow 5 seconds per rule (50 rules = ~250 seconds = 4 minutes)
- **If timeout:** Process in batches: `rules/0*.md`, `rules/1*.md`, etc.

**Deployment with >100 rules:**
- **Command:** `task deploy DEST=/path`
- **Expected duration:** ~30 seconds for 122 rules + 6 skills
- **Progress monitoring:** Watch output for "Copying rules/" and "Copying skills/"
- **Verification:** Check destination has correct count: `ls /path/rules/*.md | wc -l`

**Index generation with >100 rules:**
- **Command:** `task index:generate`
- **Expected duration:** ~15 seconds for 122 rules
- **Progress:** Shows "Processing rules..." with count
- **Output:** RULES_INDEX.md regenerated (~50KB for 122 rules)

## Important File Locations

- **rules/** - Edit rule content here (production-ready)
- **AGENTS.md** - Bootstrap protocol (project root)
- **PROJECT.md** - Project-specific configuration (this file)
- **rules/000-global-core.md** - Execution protocols and MODE framework
- **RULES_INDEX.md** - Generated catalog (don't edit directly)
- **schemas/rule-schema.yml** - Schema definition for validation
- **scripts/** - Validation and deployment tools
- **tests/** - Comprehensive test suite (98% coverage)
- **skills/** - AI Agent Skills (6 total)
- **docs/** - Architecture and usage documentation

## Critical Development Rules

1. **CRITICAL: Validate before committing:**
   ```bash
   task validate  # MUST pass (exit code 0) before any commit
   # All checks must succeed: linting, formatting, type checking, tests, schema validation
   # If any check fails (exit code != 0), DO NOT commit
   ```

   **Enforcement mechanisms:**

   **Manual enforcement (current):**
   - AI assistants must run `task validate` before committing
   - Check exit code: 0 = success, non-zero = failure
   - Block commit if validation fails
   - Re-run validation after fixing issues

   **Automated enforcement (optional, recommended for teams):**

   *Pre-commit hook (local enforcement):*
   ```bash
   # Install pre-commit hook (one-time setup)
   # Note: This project uses Entro Secret Scan pre-commit hook already
   # To add validation enforcement, create .git/hooks/pre-commit:

   cat > .git/hooks/pre-commit << 'EOF'
   #!/bin/bash
   set -e
   echo "Running validation before commit..."
   task validate
   if [ $? -ne 0 ]; then
       echo "❌ Validation failed. Commit blocked."
       echo "Fix errors and try again."
       exit 1
   fi
   echo "✓ Validation passed. Proceeding with commit."
   EOF

   chmod +x .git/hooks/pre-commit
   ```

   *CI/CD enforcement (remote enforcement):*
   ```yaml
   # Example GitHub Actions workflow (.github/workflows/validate.yml)
   name: Validate
   on: [push, pull_request]
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install Task
           run: sh -c "$(curl -sSfL https://taskfile.dev/install.sh)"
         - name: Install uv
           run: curl -LsSf https://astral.sh/uv/install.sh | sh
         - name: Run validation
           run: task validate
         - name: Block merge if validation fails
           if: failure()
           run: exit 1
   ```

   **Validation enforcement benefits:**
   - Pre-commit: Prevents committing invalid code locally
   - CI/CD: Prevents merging invalid code to main branch
   - Consistent: All contributors follow same quality standards
   - Fast feedback: Errors caught immediately, not in code review

   **Note:** Current project uses manual enforcement for flexibility. Add automated enforcement when working in teams or when strict quality gates are required.

2. **Use template generator for new rules:**
   ```bash
   task rule:new FILENAME=XXX-name
   # Don't create rules manually - schema compliance is critical
   ```

3. **Update index after metadata changes:**
   ```bash
   task index:generate
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
   task validate  # Runs all CI/CD checks
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
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# Check dependencies
grep "**Depends:**" rules/XXX-rule.md

# Verify rule exists in index
grep "XXX-rule" RULES_INDEX.md
```

### Token Budget Management

Token budgets track context window usage:

```bash
# Check single file
uv run python scripts/token_validator.py rules/XXX-rule.md --dry-run --detailed

# Update all budgets
task tokens:update

# Check all budgets
task tokens:check
```

### Keyword Generation

Keywords enable semantic rule discovery:

```bash
# Suggest keywords for a rule
task keywords:suggest FILE=rules/XXX-rule.md

# Show diff of current vs suggested
task keywords:diff FILE=rules/XXX-rule.md

# Update keywords in-place
task keywords:update FILE=rules/XXX-rule.md
```

## Testing Philosophy

The project maintains 98% test coverage with comprehensive test suites:

- **Unit tests:** All validation scripts (schema_validator, token_validator, etc.)
- **Integration tests:** Rule deployment, index generation
- **Validation tests:** Schema compliance, metadata accuracy

Run tests frequently during development:

```bash
task test                  # Quick test run
task test:coverage         # Full coverage report
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
**task not found:** macOS: `brew install go-task`, Linux: `sh -c "$(curl -sSfL https://taskfile.dev/install.sh)"`

### Resource Exhaustion

**Disk space:** Clean caches: `rm -rf .pytest_cache __pycache__` + `uv cache clean` (require 2GB minimum)
**Memory:** Close applications, process in batches <1000 rules (require 4GB RAM minimum)
**Open files:** Increase limit: `ulimit -n 4096`

### Validation Failures

**task validate fails:** Run individual checks (`task quality:lint`, `task test`, etc.), fix in order, re-run after each
**Schema validation fails:** Run `uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose`, fix CRITICAL → HIGH → MEDIUM → LOW

---

## Appendix: Direct Script Usage (Advanced)

**Recommendation:** Use Task commands (Quick Reference section). Direct script usage is only for custom CI/CD pipelines or non-Task automation. All scripts are in `scripts/` directory. Run with: `uv run python scripts/[script_name].py [args]`. Refer to scripts/README.md for complete documentation.
