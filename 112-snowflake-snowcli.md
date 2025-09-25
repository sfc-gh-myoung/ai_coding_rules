**Description:** Guidelines and best practices for Snowflake CLI (SnowCLI) usage with reproducible, pinned execution.
**AppliesTo:** `**/Taskfile.yml`, `**/*.sh`, `**/*.zsh`, `**/*.md`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-25

# Snowflake SnowCLI (snow) Usage Best Practices

## Purpose
Provide clear, reproducible guidance for installing, invoking, and automating Snowflake CLI (SnowCLI) with a strong preference for hermetic, pinned execution to ensure consistency across local development and CI/CD.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake CLI usage across local development, scripts, Taskfile targets, and CI/CD pipelines

## Contract
- **Inputs/Prereqs:** Python ≥ 3.10; `uv` installed; Snowflake account and role; connection/auth method (SSO, key-pair, OAuth, or user/password) configured outside of code
- **Allowed Tools:** `uvx` (preferred), `uv tool install`, Homebrew (Mac dev-only fallback), environment variables and secure secret stores, Taskfile targets
- **Forbidden Tools:** Global, system-wide pip installs; unpinned CLI versions in CI; committing credentials or private keys to the repository
- **Required Steps:**
  1. Prefer hermetic, pinned execution using `uvx --from=snowflake-cli==3.12 snow {{.CLI_ARGS}}` for all scripted and CI usage
  2. Provide a Taskfile wrapper for developer ergonomics that shells out to the pinned `uvx` invocation
  3. Use profile-based or env var–based configuration; never hardcode secrets; integrate a secure secret store
  4. Use non-interactive flags and machine-readable output (e.g., JSON) in automation
  5. Validate the pinned version and basic connectivity before running workflows
- **Output Format:** Shell command snippets, Taskfile targets, and brief configuration notes
- **Validation Steps:**
  - `snow --version` resolves to the pinned version when invoked through `uvx`
  - Core commands run non-interactively in CI with machine-readable output
  - No credentials present in code or Taskfile; secrets flow via CI secret manager or OS keychain

## Key Principles
- Reproducibility first: use ephemeral, pinned CLI execution with `uvx`
- Non-global installs: avoid polluting developer machines and CI agents
- Security by default: never commit secrets; prefer key-pair/OAuth/SSO or secret managers
- CI-friendly: non-interactive, idempotent, parseable output
- Version hygiene: upgrade with intent; validate before adopting a new CLI minor/major

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

## 6. Anti-Patterns to Avoid
- **Avoid:** `pip install snowflake-cli` into system/global environments
- **Avoid:** Unpinned SnowCLI versions in automation
- **Avoid:** Committing credentials, JWTs, or private keys into source control
- **Avoid:** Interactive prompts in CI (missing flags/vars)
- **Avoid:** Assuming Homebrew exists on CI runners (use `uvx` instead)

## Quick Compliance Checklist
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

## Response Template
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
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Security Governance**: `107-snowflake-security-governance.md`
- **SPCS Best Practices**: `120-snowflake-spcs.md`


