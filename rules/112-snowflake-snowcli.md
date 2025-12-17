# Snowflake SnowCLI (snow) Usage Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** snow CLI, SnowCLI, Snowflake CLI, snowflake-cli, uvx, Taskfile, task automation, deployment automation, snowflake.yml, profiles, CI/CD, JSON output, authentication, stage copy
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide clear, reproducible guidance for installing, invoking, and automating Snowflake CLI (SnowCLI) with a strong preference for hermetic, pinned execution to ensure consistency across local development and CI/CD.

## Rule Scope

Snowflake CLI usage across local development, scripts, Taskfile targets, and CI/CD pipelines

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use uvx for hermetic execution** - `uvx --from=snowflake-cli==3.12 snow` for pinned version
- **Wrap in Taskfile** - Create task targets for developer ergonomics
- **Use profiles or env vars** - Never hardcode credentials
- **Non-interactive flags in automation** - Machine-readable output (JSON)
- **Validate version** - Check `snow --version` matches pinned version
- **Secure secret store** - Use proper credential management
- **Never use global pip installs** - Always pinned via uvx
- **CRITICAL: Stage copy compression** - Use `--no-auto-compress` NOT `--auto-compress false`

**Quick Checklist:**
- [ ] uvx with pinned snowflake-cli version
- [ ] Taskfile wrapper created
- [ ] Profile-based or env var config
- [ ] No hardcoded credentials
- [ ] Non-interactive flags for CI/CD
- [ ] Version validation in workflows
- [ ] Secure secret store integrated
- [ ] Stage copy uses `--no-auto-compress` (not `--auto-compress false`)

## Contract

<contract>
<inputs_prereqs>
Python ≥ 3.10; `uv` installed; Snowflake account and role; connection/auth method (SSO, key-pair, OAuth, or user/password) configured outside of code
</inputs_prereqs>

<mandatory>
`uvx` (preferred), `uv tool install`, Homebrew (Mac dev-only fallback), environment variables and secure secret stores, Taskfile targets
</mandatory>

<forbidden>
Global, system-wide pip installs; unpinned CLI versions in CI; committing credentials or private keys to the repository
</forbidden>

<steps>
1. Prefer hermetic, pinned execution using `uvx --from=snowflake-cli==3.12 snow {{.CLI_ARGS}}` for all scripted and CI usage
2. Provide a Taskfile wrapper for developer ergonomics that shells out to the pinned `uvx` invocation
3. Use profile-based or env var–based configuration; never hardcode secrets; integrate a secure secret store
4. Use non-interactive flags and machine-readable output (e.g., JSON) in automation
5. Validate the pinned version and basic connectivity before running workflows
</steps>

<output_format>
Shell command snippets, Taskfile targets, and brief configuration notes
</output_format>

<validation>
- `snow --version` resolves to the pinned version when invoked through `uvx`
- Core commands run non-interactively in CI with machine-readable output
- No credentials present in code or Taskfile; secrets flow via CI secret manager or OS keychain
</validation>

<design_principles>
- Reproducibility first: use ephemeral, pinned CLI execution with `uvx`
- Non-global installs: avoid polluting developer machines and CI agents
- Security by default: never commit secrets; prefer key-pair/OAuth/SSO or secret managers
- CI-friendly: non-interactive, idempotent, parseable output
- Version hygiene: upgrade with intent; validate before adopting a new CLI minor/major
</design_principles>

</contract>

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
uvx --from=snowflake-cli==3.12 snow --version

# In Taskfile.yaml - single source of truth for version
CLI_VERSION: "3.12"
tasks:
  deploy:
    cmds:
      - uvx --from=snowflake-cli=={{.CLI_VERSION}} snow {{.CLI_ARGS}}
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
# Connection defined in ~/.snowflake/connections.toml with secure credential storage

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
  SNOW_CLI_VERSION: "3.12"  # Single source of truth

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
uvx --from=snowflake-cli==3.13 snow stage copy \
  --connection default \
  streamlit/app.py @DB.SCHEMA.STAGE \
  --overwrite \
  --no-auto-compress
```
**Benefits:** Reliable uploads; correct Python imports; no TypeError; professional deployments; clear syntax

## Post-Execution Checklist
- [ ] All scripted/CI invocations route through `uvx --from=snowflake-cli==3.12 snow {{.CLI_ARGS}}`
- [ ] Single pin location (Taskfile/CI template) governs the CLI version
- [ ] No global/system pip installs used
- [ ] No secrets in repo; secrets pass via env/secret manager
- [ ] Non-interactive flags and machine-readable output used in CI
- [ ] `snow --version` logged at job start

## Validation
- **Success checks:**
  - `uvx --from=snowflake-cli==3.12 snow --version` prints the expected version
  - Basic `snow sql -q "select 1"` succeeds using non-interactive auth
  - CI logs contain version and structured outputs; no interactive prompts
- **Negative tests:**
  - Unpinned `snow` in CI should be flagged by code review/build checks
  - Global `pip install` usage should be rejected by reviewers/linters

> **Investigation Required**
> When applying this rule:
> 1. **Read existing CLI usage BEFORE adding new commands** - Check Taskfile, scripts for snow patterns
> 2. **Verify snowflake.yml config** - Check profiles, connection settings
> 3. **Never assume CLI version** - Check what version is currently pinned
> 4. **Review credential management** - Understand how auth is configured
> 5. **Test CLI commands** - Validate commands work with current setup
>
> **Anti-Pattern:**
> "Running snow command... (without checking existing patterns)"
> "Using unpinned snow... (inconsistent across environments)"
>
> **Correct Pattern:**
> "Let me check your SnowCLI setup first."
> [reads Taskfile.yml, checks snowflake.yml, reviews version]
> "I see you use snowflake-cli==3.12 via uvx. Following this pattern for the new command..."

## Output Format Examples
```bash
# Minimal smoke test
uvx --from=snowflake-cli==3.12 snow --version
uvx --from=snowflake-cli==3.12 snow sql -q "select 1 as ok"
```

## References

### External Documentation
- Snowflake CLI GitHub repository: `https://github.com/snowflakedb/snowflake-cli`
- Snowflake CLI Documentation: `https://docs.snowflake.com/developer-guide/snowflake-cli/index`
- Snowflake CLI Cheatsheet: `https://github.com/Snowflake-Labs/sf-cheatsheets/blob/main/snowflake-cli.md`
- Snowflake Engineering blog (context for uv/library management and determinism): `https://www.snowflake.com/en/engineering-blog/how-we-built-library-powering-streamlit-apps/`

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **SQL Automation**: `rules/102a-snowflake-sql-automation.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **SPCS Best Practices**: `rules/120-snowflake-spcs.md`

## 1. Installation and Invocation Patterns

### Preferred (ephemeral, pinned, reproducible)
```bash
# Always pin for automation (local and CI)
uvx --from=snowflake-cli==3.12 snow --version
uvx --from=snowflake-cli==3.12 snow sql -q "select 1 as ok"
```

Rationale: `uvx` downloads and executes the requested version in an isolated environment, avoiding global state and ensuring deterministic behavior. See official repo guidance that recommends `uv`/`uvx` and shows `uvx --from snowflake-cli snow --help` for quick use. Reference: `https://github.com/snowflakedb/snowflake-cli`.

### Developer convenience (Taskfile wrapper)
```yaml
# Taskfile.yml
version: '3'
tasks:
  snow:
    desc: Run Snowflake CLI via pinned uvx (pass args with CLI_ARGS)
    cmds:
      - uvx --from=snowflake-cli==3.12 snow {{.CLI_ARGS}}
    vars:
      CLI_ARGS: "--help"
```

Developers can run: `task snow -- -q "select 1"` or `task snow -- --version`.

### Alternative (Mac dev-only fallback)
```bash
brew tap snowflakedb/snowflake-cli
brew install snowflake-cli
snow --help
```

Notes:
- Prefer Homebrew only for local Macs; do not rely on it in CI/CD (heterogeneous runners, slower, less deterministic)
- For pinned CI/CD, stick to `uvx --from=snowflake-cli==3.12 ...`

## 2. Version Pinning and Upgrade Strategy
- **Rule:** Default to `snowflake-cli==3.12` in all automation until you explicitly validate a newer release in a staging environment
- **Rule:** Surface the CLI version in logs (`snow --version`) at the start of jobs for traceability
- **Consider:** Maintain a single pin in your Taskfile/CI templates to centralize upgrades

## 3. Configuration and Authentication
- **Rule:** Use profiles or environment variables; never hardcode credentials in scripts or rule files
- **Rule:** Prefer secure methods (key-pair/OAuth/SSO) over user/password; centralize secrets in CI secret managers or OS keychains
- **Rule:** Ensure least-privilege roles and rotate keys regularly per security policy
- **Consider:** For local dev, rely on OS keychain integrations where available; for CI, inject secrets as env vars/files at runtime

References for concepts and configuration flows are covered in official docs: `https://docs.snowflake.com/developer-guide/snowflake-cli/index`.

## 4. Automation Patterns (CI/CD)
- **Always:** Use non-interactive flags and provide all required parameters via env/flags
- **Rule:** Prefer machine-readable output for parsing; where available, use `--format json` or similar
- **Rule:** Fail fast and surface errors clearly; add `--verbose`/`--debug` when diagnosing pipeline failures
- **Rule:** Do not cache credentials in CI workspaces; rely on ephemeral tokens/keys

Examples:
```bash
# Version and health checks in CI
uvx --from=snowflake-cli==3.12 snow --version
uvx --from=snowflake-cli==3.12 snow sql -q "select current_role(), current_warehouse()"

# Idempotent object creation (example pattern; adjust to your needs)
uvx --from=snowflake-cli==3.12 snow sql -q "create warehouse if not exists CI_WH warehouse_size = 'XSMALL' auto_suspend = 60"
```

## 5. Output, Logging, and Troubleshooting
- **Rule:** Prefer structured output (JSON) for automation; only use human-friendly tables in interactive sessions
- **Rule:** Include `--verbose`/`--debug` (if available) when capturing logs for incident analysis
- **Consider:** Capture CLI stdout/stderr separately in CI and archive logs on failure

## 6. Stage Copy Command Syntax

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
uvx --from=snowflake-cli==3.13 snow stage copy \
  --connection default \
  streamlit/app.py @DB.SCHEMA.STAGE \
  --overwrite \
  --no-auto-compress
```

**Compression Syntax by Context:**
- **SQL `PUT` command:** `AUTO_COMPRESS=FALSE` (SQL parameter syntax)
- **`snow stage copy`:** `--no-auto-compress` (Boolean CLI flag)
- **WRONG:** `--auto-compress false` - causes error

### Stage Copy Common Flags

```bash
# Required flags for deployment automation
snow stage copy SOURCE DEST \
  --overwrite              # Replace existing files
  --no-auto-compress       # Keep files uncompressed (critical for Python)
  --recursive              # Upload directories (when needed)
```

## 7. Anti-Patterns to Avoid
- **Avoid:** `pip install snowflake-cli` into system/global environments
- **Avoid:** Unpinned SnowCLI versions in automation
- **Avoid:** Committing credentials, JWTs, or private keys into source control
- **Avoid:** Interactive prompts in CI (missing flags/vars)
- **Avoid:** Assuming Homebrew exists on CI runners (use `uvx` instead)
- **Avoid:** Using `--auto-compress false` (incorrect syntax; use `--no-auto-compress`)
