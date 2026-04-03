# Snowflake SnowCLI (snow) Usage Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-26
**LoadTrigger:** kw:snowcli, file:snowflake.yml
**Keywords:** snow CLI, SnowCLI, Snowflake CLI, snowflake-cli, uvx, automation, deployment automation, snowflake.yml, profiles, CI/CD, JSON output, authentication, stage copy, config.toml, PAT authentication, WIF authentication, project definition, connection management, stage-to-stage copy
**TokenBudget:** ~4900
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Clear, reproducible guidance for installing, invoking, and automating Snowflake CLI (SnowCLI) with hermetic, pinned execution. Covers uvx usage, build automation integration, profile/env var configuration, CI/CD patterns, version pinning, and secure credential management.

**When to Load This Rule:**
- Setting up SnowCLI for local development
- Creating automation targets for Snowflake deployments
- Configuring CI/CD pipelines with SnowCLI
- Managing SnowCLI versions and dependencies
- Securing SnowCLI credentials
- Working with snowflake.yml project definitions
- Managing Snowflake stages (copy, diff, execute)
- Managing Snowflake CLI connections

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns

**Related:**
- **820-taskfile-automation.md** / **821-makefile-automation.md** - Build automation patterns
- **803-project-git-workflow.md** - CI/CD integration patterns

### External Documentation

**SnowCLI Documentation:**
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index) - Official SnowCLI documentation
- [UV Tool](https://github.com/astral-sh/uv) - UV tool for Python package management

## Contract

### Inputs and Prerequisites

- Python ≥ 3.10
- `uv` installed
- Snowflake account and role
- Connection/auth method configured outside of code. Supported methods (preferred order): SSO (`externalbrowser`), key-pair, PAT (`PROGRAMMATIC_ACCESS_TOKEN`), WIF (`WORKLOAD_IDENTITY`), OAuth 2.0 Authorization Code, OAuth 2.0 Client Credentials, user/password (least preferred)

### Mandatory

- `uvx` (preferred) or `uv tool install`
- Homebrew (Mac dev-only fallback)
- Environment variables and secure secret stores
- Project automation targets (Makefile, Taskfile, or equivalent)

### Forbidden

- Global, system-wide pip installs
- Unpinned CLI versions in CI
- Committing credentials or private keys to repository

### Execution Steps

1. Use hermetic, pinned execution: `uvx --from=snowflake-cli==3.16.0 snow {{.CLI_ARGS}}`
2. Provide automation wrapper (Makefile target or Taskfile task) for developer ergonomics
3. Use profile-based or env var configuration; never hardcode secrets
4. Use non-interactive flags and machine-readable output (JSON) in automation
5. Validate pinned version and basic connectivity before running workflows

### Output Format

- Shell command snippets
- Project automation targets (Makefile, Taskfile, or equivalent)
- Configuration notes

### Validation

**Pre-Task-Completion Checks:**
- `snow --version` resolves to pinned version when invoked through `uvx`
- Core commands run non-interactively in CI
- No credentials present in code or automation files

**Success Criteria:**
- Commands execute with pinned version
- Machine-readable output (JSON) in automation
- Secrets flow via CI secret manager or OS keychain
- Non-interactive execution in CI/CD

### Design Principles

- Reproducibility first: use ephemeral, pinned CLI execution with `uvx`
- Non-global installs: avoid polluting developer machines and CI agents
- Security by default: never commit secrets; prefer key-pair/OAuth/SSO or secret managers
- CI-friendly: non-interactive, idempotent, parseable output
- Version hygiene: upgrade with intent; validate before adopting new CLI minor/major

### Post-Execution Checklist

- [ ] uvx with pinned snowflake-cli version configured
- [ ] Automation wrapper created for common commands (Makefile target or Taskfile task)
- [ ] Profile-based or env var config (no hardcoded credentials)
- [ ] Non-interactive flags for CI/CD
- [ ] Version validation in workflows
- [ ] Secure secret store integrated
- [ ] Stage copy uses `--no-auto-compress` (not `--auto-compress false`)

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Installing Snow CLI Globally with pip**
```bash
# Bad: Global pip install, version conflicts
pip install snowflake-cli
snow --version
# Version varies across machines, environments, CI runners!
```
**Problem:** Version drift across environments; dependency conflicts; manual upgrades; inconsistent behavior; CI breakage; reproducibility issues

**Correct Pattern:**
```bash
# Good: Use uvx for isolated, pinned execution
uvx --from=snowflake-cli==3.16.0 snow --version

# In project automation (Makefile, Taskfile, or CI config) - single source of truth for version
# Example (Makefile):
CLI_VERSION := 3.16.0
snow:
	uvx --from=snowflake-cli==$(CLI_VERSION) snow $(ARGS)

# Example (Taskfile.yml):
# CLI_VERSION: "3.16.0"
# tasks:
#   snow:
#     cmds: [uvx --from=snowflake-cli=={{.CLI_VERSION}} snow {{.CLI_ARGS}}]
#
# For complete examples, see 820-taskfile-automation.md or 821-makefile-automation.md
```
**Benefits:** Consistent versions; isolated execution; easy version updates; reproducible environments; CI reliability; no conflicts

**Anti-Pattern 2: Hardcoding Credentials in Scripts**
```bash
# Bad: Credentials in scripts or environment files
snow sql -q "SELECT 1" \
  --account myaccount \
  --user myuser \
  --password MyPassword123  # SECURITY VIOLATION!
```
**Problem:** Credentials in source control; security breach risk; credential leakage; audit violations; compliance failures; difficult rotation

**Correct Pattern:**
```bash
# Good: Use environment variables or secret manager
export SNOWFLAKE_CONNECTION_NAME=prod_connection
# Connection defined in ~/.snowflake/config.toml (primary) or ~/.snowflake/connections.toml (alternative)

snow sql -q "SELECT 1"
# Uses connection from secure config file
```
**Benefits:** No credentials in code; secure storage; easy rotation; compliance-ready; audit-friendly; professional security

**Anti-Pattern 3: Using Interactive Prompts in CI/CD**
```bash
# Bad: Missing flags cause interactive prompts in CI
snow sql -q "SELECT 1"
# Prompts for connection name - CI job hangs!
```
**Problem:** CI jobs hang waiting for input; pipeline failures; timeout errors; manual intervention required; unreliable automation; deployment delays

**Correct Pattern:**
```bash
# Good: All parameters explicit for non-interactive execution
snow sql \
  --connection prod_connection \
  -q "SELECT 1" \
  --format json \  # Machine-readable output
  --no-input       # Fail fast if input needed
```
**Benefits:** Non-interactive execution; reliable CI; fast failures; machine-readable output; automated workflows; professional deployment

**Anti-Pattern 4: Not Pinning Snow CLI Version in CI**
```yaml
# Bad: Use latest version, breaks when CLI updates
# .github/workflows/deploy.yml
steps:
  - name: Deploy
    run: |
      pip install snowflake-cli  # Gets latest version!
      snow object deploy
# Breaks when 3.13 releases with breaking changes!
```
**Problem:** Unexpected breaking changes; CI breakage on updates; unstable pipelines; emergency fixes required; deployment failures; production risk

**Correct Pattern:**
```yaml
# Good: Pin exact version for stability
# .github/workflows/deploy.yml
env:
  SNOW_CLI_VERSION: "3.16.0"  # Single source of truth

steps:
  - name: Deploy
    run: |
      uvx --from=snowflake-cli==${{ env.SNOW_CLI_VERSION }} \
        snow object deploy

  - name: Log version
    run: |
      uvx --from=snowflake-cli==${{ env.SNOW_CLI_VERSION }} \
        snow --version
```
**Benefits:** Stable CI; predictable behavior; controlled upgrades; no surprise breaks; reliable deployments; professional CI/CD

**Anti-Pattern 5: Using Wrong Compression Flag Syntax**
```bash
# Bad: Using SQL syntax for CLI flag
snow stage copy streamlit/app.py @STAGE --auto-compress false
# Error: Got unexpected extra argument (false)
```
**Problem:** Deployment failures; confusion between SQL PUT and CLI syntax; wasted debugging time; production delays; team frustration

**Correct Pattern:**
```bash
# Good: Use proper CLI boolean flag syntax
snow stage copy streamlit/app.py @STAGE --no-auto-compress --overwrite

# For Streamlit/Python files (compression breaks imports):
uvx --from=snowflake-cli==3.16.0 snow stage copy \
  --connection default \
  streamlit/app.py @DB.SCHEMA.STAGE \
  --overwrite \
  --no-auto-compress
```
**Benefits:** Reliable uploads; correct Python imports; no TypeError; professional deployments; clear syntax

**Anti-Pattern 6: Inverted Flag Logic in Python Wrappers**
```python
# Bad: Only adds --auto-compress when True (which is already the default)
def stage_copy(path, stage, auto_compress=True):
    flags = ["--overwrite"]
    if auto_compress:
        flags.append("--auto-compress")  # Redundant: CLI default is compress
    # When caller passes auto_compress=False: nothing happens!
    # CLI still auto-compresses → .py becomes .py.gz → SiS TypeError
```
**Problem:** The `snow stage copy` CLI auto-compresses by default. Omitting `--no-auto-compress` does NOT disable compression — it enables it. This bug is especially insidious because deployment succeeds (`[PASS]`) while the app fails at runtime.

**Correct Pattern:**
```python
# Good: Default to no compression; pass --no-auto-compress explicitly
def stage_copy(path, stage, auto_compress=False):
    flags = ["--overwrite"]
    if not auto_compress:
        flags.append("--no-auto-compress")  # Explicitly disable
    # Default auto_compress=False → safe for SiS deployments
```
**Key Rule:** For application deployment wrappers, **default `auto_compress` to `False`** and pass `--no-auto-compress` when disabled. Always verify with `LIST @stage` that uploaded files show `.py` extensions, not `.py.gz`.

**Benefits:** Safe defaults; correct SiS deployments; no silent compression; verifiable uploads

## Output Format Examples
```bash
# Minimal smoke test
uvx --from=snowflake-cli==3.16.0 snow --version
uvx --from=snowflake-cli==3.16.0 snow sql -q "select 1 as ok"
```

## Installation and Invocation Patterns

### Preferred (ephemeral, pinned, reproducible)
```bash
# Always pin for automation (local and CI)
uvx --from=snowflake-cli==3.16.0 snow --version
uvx --from=snowflake-cli==3.16.0 snow sql -q "select 1 as ok"
```

Rationale: `uvx` downloads and executes the requested version in an isolated environment, avoiding global state and ensuring deterministic behavior. See official repo guidance that recommends `uv`/`uvx` and shows `uvx --from snowflake-cli snow --help` for quick use. Reference: `https://github.com/snowflakedb/snowflake-cli`.

### Developer convenience (automation wrapper)

Wrap the pinned `uvx` invocation in the project's automation tool for ergonomic use:

```bash
# Makefile example:
CLI_VERSION := 3.16.0
.PHONY: snow
snow: ## Run Snowflake CLI via pinned uvx
	uvx --from=snowflake-cli==$(CLI_VERSION) snow $(ARGS)
# Usage: make snow ARGS="sql -q 'select 1'"
```

For Taskfile.yml wrapper patterns, see `820-taskfile-automation.md`.

Developers can run: `make snow ARGS="-q 'select 1'"` or equivalent.

### Alternative (Mac dev-only fallback)
```bash
brew tap snowflakedb/snowflake-cli
brew install snowflake-cli
snow --help
```

Notes:
- Prefer Homebrew only for local Macs; do not rely on it in CI/CD (heterogeneous runners, slower, less deterministic)
- For pinned CI/CD, stick to `uvx --from=snowflake-cli==3.16.0 ...`

### Other Installation Methods

Binary installers (deb, rpm, macOS pkg, Windows MSI) and FIPS-compliant Docker images are available. See [Installation docs](https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation). `pipx install snowflake-cli==3.16.0` is also supported. For automation, `uvx` with pinned version remains preferred.

## Version Pinning and Upgrade Strategy

> **Investigation Required:** Run `snow connection list` and `snow connection test --connection <name>` before modifying any connection configuration.

- **Rule:** Default to `snowflake-cli==3.16.0` in all automation until you run the full test suite with the new version in a staging environment and confirm 0 failures
- **Rule:** Surface the CLI version in logs (`snow --version`) at the start of jobs for traceability
- **Rule:** Maintain a single pin in your automation files (Makefile, Taskfile, or CI templates) to centralize upgrades

## Configuration and Authentication

- **Rule:** Primary configuration file is `~/.snowflake/config.toml`. Alternative: `~/.snowflake/connections.toml` (still supported)
- **Rule:** Use profiles or environment variables; never hardcode credentials in scripts or rule files
- **Rule:** Prefer secure methods (key-pair/OAuth/SSO) over user/password; centralize secrets in CI secret managers or OS keychains
- **Rule:** Ensure least-privilege roles and rotate keys every 90 days or per your organization's security policy
- **Rule:** For local dev, rely on OS keychain integrations where available; for CI, inject secrets as env vars/files at runtime

### Key Environment Variables (CI/CD)

- `SNOWFLAKE_DEFAULT_CONNECTION_NAME` - Connection name to use
- `SNOWFLAKE_CONNECTIONS_<CONN>_ACCOUNT` - Account identifier
- `SNOWFLAKE_CONNECTIONS_<CONN>_USER` - Username
- `SNOWFLAKE_CONNECTIONS_<CONN>_AUTHENTICATOR` - Auth method
- `SNOWFLAKE_CONNECTIONS_<CONN>_PRIVATE_KEY_RAW` - Private key content
- `SNOWFLAKE_CONNECTIONS_<CONN>_TOKEN_FILE_PATH` - Token file path (WIF)

References for concepts and configuration flows are covered in official docs: [Snowflake CLI Documentation](https://docs.snowflake.com/developer-guide/snowflake-cli/index).

## Project Definition (snowflake.yml)

The `snowflake.yml` file (`definition_version: 2`) defines entities for CLI-managed objects. Place at project root. Entity types: `streamlit`, `notebook`, `function`, `procedure`, `application`, `application package`.

See [Project definitions](https://docs.snowflake.com/en/developer-guide/snowflake-cli/project-definitions/about).

## Automation Patterns (CI/CD)
- **Always:** Use non-interactive flags and provide all required parameters via env/flags
- **Rule:** Prefer machine-readable output for parsing; where available, use `--format json` or similar
- **Rule:** Fail fast and surface errors clearly; add `--verbose`/`--debug` when diagnosing pipeline failures
- **Rule:** Do not cache credentials in CI workspaces; rely on ephemeral tokens/keys

Examples:
```bash
# Version and health checks in CI
uvx --from=snowflake-cli==3.16.0 snow --version
uvx --from=snowflake-cli==3.16.0 snow sql -q "select current_role(), current_warehouse()"

# Idempotent object creation (example pattern; adjust to your needs)
uvx --from=snowflake-cli==3.16.0 snow sql -q "create warehouse if not exists CI_WH warehouse_size = 'XSMALL' auto_suspend = 60"
```

## Output, Logging, and Troubleshooting
- **Rule:** Prefer structured output (JSON) for automation; only use human-friendly tables in interactive sessions
- **Rule:** Include `--verbose`/`--debug` (if available) when capturing logs for incident analysis
- **Consider:** Capture CLI stdout/stderr separately in CI. Archive logs on failure.

## Stage Copy Command Syntax

### CRITICAL: Compression Flag Syntax

**Problem:** The `snow stage copy` command uses different syntax than SQL `PUT` command for compression control.

**WRONG (causes "unexpected extra argument" error):**
```bash
# Bad: This syntax DOES NOT WORK in snowflake-cli
snow stage copy file.py @stage --auto-compress false
# Error: Got unexpected extra argument (false)
```

**CORRECT:**
```bash
# Good: Use boolean flag without value
snow stage copy file.py @stage --no-auto-compress
```

**Why This Matters:**
- Python imports fail if files are compressed (.py becomes .py.gz)
- Streamlit apps get "TypeError: bad argument type for built-in operation"
- **This is NOT version-specific** - applies to all snowflake-cli versions (3.11, 3.12, 3.13+)

**Complete Example:**
```bash
# Upload Python files without compression
uvx --from=snowflake-cli==3.16.0 snow stage copy \
  --connection default \
  streamlit/app.py @DB.SCHEMA.STAGE \
  --overwrite \
  --no-auto-compress
```

### Recursive Directory Upload (Streamlit / Multi-File Apps)

For Streamlit apps and other multi-file deployments, use `--recursive` to upload
an entire directory tree while preserving structure:

```bash
# Upload entire Streamlit app directory (recommended for multi-file apps)
uvx --from=snowflake-cli==3.16.0 snow stage copy \
  --connection default \
  streamlit/ @DB.SCHEMA.STREAMLIT_STAGE \
  --recursive \
  --no-auto-compress \
  --overwrite
```

**Why `--recursive`:**
- Uploads all files and subdirectories (pages/, utils/, assets/) in one command
- Preserves directory structure on stage automatically
- Eliminates need for multiple PUT statements or glob patterns
- Simpler to maintain as the app grows

**Stage Copy Common Flags**

```bash
# Required flags for deployment automation
snow stage copy SOURCE DEST \
  --overwrite              # Replace existing files
  --no-auto-compress       # Keep files uncompressed (critical for Python)
  --recursive              # Upload directories (when needed)
```

### Stage-to-Stage Copy

```bash
snow stage copy @SOURCE_STAGE/path/ @DEST_STAGE/path/ --recursive
```

## Additional Anti-Patterns
- **Avoid:** `pip install snowflake-cli` into system/global environments
- **Avoid:** Unpinned SnowCLI versions in automation
- **Avoid:** Committing credentials, JWTs, or private keys into source control
- **Avoid:** Interactive prompts in CI (missing flags/vars)
- **Avoid:** Assuming Homebrew exists on CI runners (use `uvx` instead)
- **Avoid:** Using `--auto-compress false` (incorrect syntax; use `--no-auto-compress`)
- **Avoid:** Inverted flag logic in Python wrappers that omits `--no-auto-compress` when compression should be disabled (default `auto_compress` parameter to `False` for app deployment functions)

## Command Lifecycle Patterns

### Command Groups

- `snow sql` - Execute SQL queries
- `snow stage` - Manage stages (copy, diff, list, remove, execute)
- `snow connection` - Manage connections (list, test, add, remove, set-default)
- `snow app` - Native App development and deployment
- `snow cortex` - Cortex AI operations
- `snow notebook` - Notebook management
- `snow dbt` - dbt project deploy and execute
- `snow git` - Git repository operations
- `snow spcs` - Snowpark Container Services (service, image-repository, compute-pool)
- `snow object` - Generic object operations (list, describe, drop)
- `snow validate-image` - Validate container images for SPCS

### App Teardown
```bash
# Clean up deployed Snowflake Native App
uvx --from=snowflake-cli==3.16.0 snow app teardown --connection prod_connection --force
```

### Stage Diff
```bash
# Compare local files with stage contents before deploying
uvx --from=snowflake-cli==3.16.0 snow stage diff @DB.SCHEMA.STAGE ./local_dir/
```

### Connection Profile Management
```bash
# List configured connections
uvx --from=snowflake-cli==3.16.0 snow connection list

# Test a specific connection
uvx --from=snowflake-cli==3.16.0 snow connection test --connection prod_connection

# Add a new connection (interactive - local dev only)
uvx --from=snowflake-cli==3.16.0 snow connection add

# Remove a connection
uvx --from=snowflake-cli==3.16.0 snow connection remove old_connection

# Set default connection
uvx --from=snowflake-cli==3.16.0 snow connection set-default prod_connection

# Use temporary inline connection (no config file needed)
uvx --from=snowflake-cli==3.16.0 snow sql -q "SELECT 1" -x "account=myaccount user=myuser authenticator=externalbrowser"
```

## Common CLI Errors and Resolutions

- **"Authentication failed":** Expired token or invalid credentials. Fix: Refresh OAuth token, rotate PAT, or verify key-pair path.
- **"Connection refused" / timeout:** Incorrect account URL or network restrictions. Fix: Verify account identifier format (`orgname-acctname`) and firewall rules.
- **"Insufficient privileges":** Role lacks required grants. Fix: Verify `current_role()` has the needed privileges; switch with `--role`.
- **"Got unexpected extra argument":** Wrong flag syntax (e.g., `--auto-compress false`). Fix: Use boolean flags (`--no-auto-compress`).
- **"Object does not exist":** Wrong database/schema context. Fix: Fully qualify object names or set `--database`/`--schema` flags.
- **"Error with --recursive and FQN stages":** Bug in versions before 3.16.0 where `snow stage copy --recursive` failed with fully-qualified stage names. Fix: Upgrade to v3.16.0+.
