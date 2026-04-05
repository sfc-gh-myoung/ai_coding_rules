# Snowflake SQL: CI/CD Pipeline Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-03-26
**Keywords:** CI/CD, GitHub Actions, Makefile, deployment automation, environment variables, multi-environment, pipeline, secrets management
**TokenBudget:** ~1300
**ContextTier:** Low
**Depends:** 102a-snowflake-sql-automation.md

## Scope

**What This Rule Covers:**
CI/CD pipeline patterns for automated Snowflake SQL deployments: Makefile integration, GitHub Actions workflows, and environment-specific variable management across dev/test/prod.

**When to Load This Rule:**
- Setting up CI/CD pipelines for Snowflake SQL deployments
- Configuring GitHub Actions for SQL automation
- Using Makefile for SQL template execution
- Managing environment-specific secrets and variables

## References

### Dependencies

**Must Load First:**
- **102a-snowflake-sql-automation.md** - SQL automation patterns and templates

## Contract

### Inputs and Prerequisites

- CI/CD platform (GitHub Actions, GitLab CI, or equivalent)
- Snowflake CLI installed in pipeline
- Environment-specific secrets configured per platform

### Mandatory

- Secrets stored in CI/CD platform secret store (never in code)
- Environment-specific variables for dev/test/prod
- SQL templates use `<%VARIABLE%>` parameterization from 102a

### Forbidden

- Hardcoded credentials in workflow files
- Direct production deployment without dev/test validation

### Execution Steps

1. Configure Makefile with centralized variables
2. Set up GitHub Actions workflow triggered on SQL file changes
3. Configure environment-specific secrets in CI/CD platform
4. Test pipeline in dev before enabling for prod

### Output Format

Makefile, GitHub Actions workflow YAML, environment variable configurations.

### Validation

- Pipeline executes successfully in dev environment
- Secrets are not exposed in logs
- SQL templates deploy correctly with variable substitution

### Post-Execution Checklist

- [ ] Makefile centralizes all environment variables
- [ ] GitHub Actions workflow triggers on correct file paths
- [ ] Secrets configured per environment (DEV, TEST, PROD)
- [ ] Pipeline tested in dev before prod deployment

## Makefile Integration

**Pattern:**
```makefile
DATABASE ?= UTILITY_DEMO_V2
SCHEMA ?= GRID_DATA
STAGE ?= @$(DATABASE).$(SCHEMA).DATA_FILES
SNOW ?= uvx --from=snowflake-cli-labs snow

.PHONY: sql-exec operations-create-schema operations-load-assets operations-merge-assets

sql-exec: ## Execute SQL template with variables (internal)
	$(SNOW) sql \
		-D DATABASE=$(DATABASE) \
		-D SCHEMA=$(SCHEMA) \
		-D STAGE=$(STAGE) \
		-f $(SQL_FILE)

operations-create-schema: ## Create GRID_DATA schema
	$(MAKE) sql-exec SQL_FILE=sql/operations/grid/01_grid_create_schema.sql

operations-load-assets: ## Load grid assets from stage
	$(MAKE) sql-exec SQL_FILE=sql/operations/grid/03_grid_copy_assets.sql

operations-merge-assets: ## Upsert grid assets (production-safe)
	$(MAKE) sql-exec SQL_FILE=sql/operations/grid/04_grid_merge_assets.sql
```

**Benefits:**
- Environment variables centralized
- Reusable target patterns
- Easy to test locally
- CI/CD can call same commands

> **Note:** If your project uses Taskfile.yml instead of Makefile, see `820-taskfile-automation.md` for equivalent Taskfile patterns.

## GitHub Actions Integration

**Pattern:**
```yaml
name: Deploy SQL Changes

on:
  push:
    branches: [main]
    paths:
      - 'sql/operations/**/*.sql'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Snowflake CLI
        run: pip install snowflake-cli-labs

      - name: Configure Snowflake Connection
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
        run: |
          snow connection add prod \
            --account $SNOWFLAKE_ACCOUNT \
            --user $SNOWFLAKE_USER \
            --password $SNOWFLAKE_PASSWORD

      - name: Deploy Schema Changes
        run: |
          snow sql \
            -D DATABASE=PROD \
            -D SCHEMA=GRID_DATA \
            -f sql/operations/grid/01_grid_create_schema.sql

      - name: Deploy Table Changes
        run: |
          snow sql \
            -D DATABASE=PROD \
            -D SCHEMA=GRID_DATA \
            -f sql/operations/grid/02_grid_create_tables.sql
```

## Environment-Specific Variables

**Pattern:**
```bash
# Development
snow sql -D DATABASE=DEV -D SCHEMA=GRID -f template.sql

# Test
snow sql -D DATABASE=TEST -D SCHEMA=GRID -f template.sql

# Production
snow sql -D DATABASE=PROD -D SCHEMA=GRID -f template.sql
```

**Store in CI/CD secrets:**
- `SNOWFLAKE_ACCOUNT_DEV`
- `SNOWFLAKE_ACCOUNT_TEST`
- `SNOWFLAKE_ACCOUNT_PROD`

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hardcoded Credentials in Workflow Files

**Problem:** Storing Snowflake credentials directly in YAML files exposes them in version control.

```yaml
# WRONG: credentials in plain text
env:
  SNOWFLAKE_PASSWORD: my_secret_password
```

**Correct Pattern:** Use CI/CD platform secret stores:
```yaml
# CORRECT: reference secrets
env:
  SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
```

### Anti-Pattern 2: Single-Environment Pipeline

**Problem:** Pipeline only deploys to production without dev/test validation.

**Correct Pattern:** Deploy to dev first, run validation, then promote to test, then prod. Use environment-specific variable files or CI/CD environment gates.
