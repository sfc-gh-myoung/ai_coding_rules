# Snowflake App Deployment Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.1
**LastUpdated:** 2026-03-26
**LoadTrigger:** kw:multi-env-deploy, kw:deployment-rollback
**Keywords:** multi-environment deployment, deployment rollback, deployment recovery, deployment validation, environment-specific deployment, dev qa prod deployment, rollback strategy
**TokenBudget:** ~2700
**ContextTier:** Low
**Depends:** 109b-snowflake-app-deployment-core.md, 109h-snowflake-app-deployment-taskfile.md

## Scope

**What This Rule Covers:**
Advanced deployment patterns for Snowflake applications including multi-environment deployment (dev/qa/prod), deployment with validation gates, and rollback/recovery procedures.

**When to Load This Rule:**
- Deploying to multiple environments (dev, qa, prod)
- Implementing deployment validation gates
- Setting up rollback and recovery procedures
- Handling failed deployments

## References

### Related Rules
**Closely Related** (consider loading together):
- **109b-snowflake-app-deployment-core.md** - Parent rule with core deployment patterns
- **109h-snowflake-app-deployment-taskfile.md** - Taskfile implementation patterns (Makefile alternative: see 821)
- **109c-snowflake-app-deployment-troubleshooting.md** - Deployment debugging

## Contract

### Inputs and Prerequisites

- Core deployment workflow functional (109b)
- Automation structure in place (Taskfile per 109h, or Makefile per 821)
- Multiple target environments configured

### Mandatory

- Environment variable controls target database/schema
- Validation gates between upload and create steps
- Rollback procedure documented and tested

### Forbidden

- Deploying directly to production without dev/qa validation
- Missing rollback procedures for production deployments

### Execution Steps

1. Configure environment-specific variables
2. Add validation tasks between deployment steps
3. Implement rollback procedure
4. Test full workflow per environment

### Output Format

Environment-aware automation configuration and rollback scripts.

### Validation

Deploy succeeds in all environments. Rollback recovers to previous state. Validation gates catch deployment issues.

### Design Principles

- Always deploy to dev first, then qa, then prod.
- Validation gates prevent bad deployments from reaching production.
- Rollback should be as simple as a single command.

### Post-Execution Checklist

- [ ] Environment variable controls target database
- [ ] Validation gates verify stage contents before CREATE
- [ ] Rollback procedure tested in dev environment
- [ ] Git tags mark known-good deployment states

## Implementation Details

## Advanced Patterns

### Multi-Environment Deployment

```yaml
vars:
  ENV: "{{.ENV | default \"dev\"}}"
  DB_NAME:
    sh: |
      case "{{.ENV}}" in
        prod) echo "PROD_DB" ;;
        qa)   echo "QA_DB" ;;
        *)    echo "DEV_DB" ;;
      esac

tasks:
  deploy:app:
    cmds:
      - echo "Deploying to {{.ENV}} environment ({{.DB_NAME}})..."
      - task: drop:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: remove:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: upload:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: create:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
```

**Usage:**
```bash
task notebook:deploy:app ENV=dev
task notebook:deploy:app ENV=qa
task notebook:deploy:app ENV=prod
```

### Deployment with Validation

```yaml
tasks:
  deploy:app:
    cmds:
      - task: drop:app
      - task: remove:app
      - task: upload:app
      - task: validate:stage
      - task: create:app
      - task: validate:object

  validate:stage:
    desc: Verify files in stage
    silent: true
    cmds:
      - |
        echo "Validating stage contents..."
        uvx snow sql -q "LIST @{{.SNOWFLAKE_STAGE}};" | grep -q "app.ipynb"
        echo "[PASS] Stage validation passed"

  validate:object:
    desc: Verify object exists
    silent: true
    cmds:
      - |
        echo "Validating notebook object..."
        uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA {{.SNOWFLAKE_DB}}.SCHEMA;" \
          | grep -q "APP_NOTEBOOK"
        echo "[PASS] Object validation passed"
```

## Rollback and Recovery

### Failed Deployment Recovery

If a deployment fails mid-workflow:

```bash
# 1. Check current state
uvx snow sql -q "LIST @DB.SCHEMA.STAGE;"
uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA DB.SCHEMA;"

# 2. Clean up partial deployment
task notebook:drop:app     # Remove broken object
task notebook:remove:app   # Clean stage

# 3. Redeploy from clean state
task notebook:deploy:app
```

### Rollback to Previous Version

```bash
# Option 1: Redeploy from git (quick fix)
git checkout HEAD~1 -- notebooks/app.ipynb
task notebook:deploy:app
git checkout HEAD -- notebooks/app.ipynb  # Restore current version in working tree

# Option 2: Backup stage with COPY FILES (recommended for production)
uvx snow sql -q "COPY FILES INTO @DB.SCHEMA.BACKUP_STAGE FROM @DB.SCHEMA.NOTEBOOK_STAGE;"
# To restore: reverse the COPY FILES direction
```

**Prevention:** Always deploy to dev/qa first. Use git tags to mark known-good deployment states.

### Deployment Locking

Use a Snowflake table to track active deployments and prevent concurrent deploys:

```sql
-- Check for active deployment lock before deploying
SELECT * FROM deployment_locks WHERE env = 'prod' AND status = 'active';

-- Acquire lock
INSERT INTO deployment_locks (env, status, locked_by, locked_at)
VALUES ('prod', 'active', CURRENT_USER(), CURRENT_TIMESTAMP());

-- Release lock after deployment completes
UPDATE deployment_locks SET status = 'released', released_at = CURRENT_TIMESTAMP()
WHERE env = 'prod' AND status = 'active';
```

### Deployment Audit Trail

After each deployment, log a record for traceability:

```sql
INSERT INTO deployment_log (env, app, version, deployed_by, deployed_at, status)
VALUES ('prod', 'MY_NOTEBOOK', 'v1.2.0', CURRENT_USER(), CURRENT_TIMESTAMP(), 'success');
```

> Query `deployment_log` to identify when issues were introduced or to verify rollback history.

### Deployment Notifications

Add an automation target that sends a notification on deployment completion or failure:

```yaml
  notify:deploy:
    desc: Send deployment notification via webhook
    cmds:
      - |
        curl -s -X POST "{{.WEBHOOK_URL}}" \
          -H "Content-Type: application/json" \
          -d '{"text": "Deployed {{.APP_NAME}} to {{.ENV}} — status: {{.STATUS}}"}'
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Deploying Directly to Production Without Environment Promotion**

**Problem:** Developers skip the dev/qa environments and deploy directly to production using `task deploy:app ENV=prod` because "the change is small" or "it worked locally." Without validation in lower environments, issues like missing dependencies, incorrect stage paths, or incompatible Snowflake versions only surface in production. Rolling back is stressful and error-prone when the previous working state wasn't preserved.

**Correct Pattern:** Always promote through environments in order: dev -> qa -> prod. Each environment deployment should pass validation gates (stage contents verified, object created successfully, basic smoke test) before promoting to the next. Never skip environments regardless of change size.

```bash
# Wrong: Deploying directly to prod — skipping dev/qa validation
task deploy:app ENV=prod  # "It's a small change, it'll be fine"
# Result: Missing dependency surfaces only in prod, app is broken

# Correct: Promote through environments in order
task deploy:app ENV=dev    # Deploy and validate in dev first
task validate:app ENV=dev  # Run validation gates
task deploy:app ENV=qa     # Promote to qa after dev passes
task validate:app ENV=qa   # Run validation gates
task deploy:app ENV=prod   # Only after qa passes
```

**Anti-Pattern 2: Rollback Strategy That Requires Rebuilding from Source**

**Problem:** The only rollback option is to check out a previous git commit and redeploy from scratch. This is slow (minutes to rebuild), requires git access from the deployment environment, and fails if the deployment infrastructure itself changed between versions. During an outage, this delay extends downtime unnecessarily.

**Correct Pattern:** Maintain a backup stage or use Snowflake's `COPY FILES` to snapshot the current stage contents before each deployment. Rollback becomes a single operation: copy files from backup stage back to the app stage and recreate the object. Test the rollback procedure in dev before relying on it in production.

```sql
-- Wrong: Rollback requires git checkout and full redeploy (slow, error-prone)
-- git checkout HEAD~1 -- notebooks/app.ipynb
-- task deploy:app ENV=prod
-- (Takes 5+ minutes during an outage)

-- Correct: Snapshot stage before deploy, rollback with COPY FILES
-- Before deploying: backup current stage
COPY FILES INTO @DB.SCHEMA.BACKUP_STAGE FROM @DB.SCHEMA.NOTEBOOK_STAGE;

-- If deployment fails: restore from backup in seconds
REMOVE @DB.SCHEMA.NOTEBOOK_STAGE;
COPY FILES INTO @DB.SCHEMA.NOTEBOOK_STAGE FROM @DB.SCHEMA.BACKUP_STAGE;
DROP NOTEBOOK IF EXISTS DB.SCHEMA.MY_NOTEBOOK;
CREATE NOTEBOOK DB.SCHEMA.MY_NOTEBOOK
    FROM '@DB.SCHEMA.NOTEBOOK_STAGE'
    QUERY_WAREHOUSE = MY_WH
    MAIN_FILE = 'app.ipynb';
```

**Anti-Pattern 3: Validation Gates That Only Check Object Existence**

**Problem:** The `validate:object` task only checks that the notebook or Streamlit object exists in the schema (e.g., `SHOW NOTEBOOKS | grep APP_NAME`). This passes even when the object was created with wrong parameters, missing files, or an incorrect ROOT_LOCATION. The deployment is marked as successful, but the app fails when users try to open it.

**Correct Pattern:** Validation gates should verify both object existence and object health. Check that `LIST @STAGE` returns the expected number of files, verify file extensions are correct (`.py` not `.py.gz`), confirm ROOT_LOCATION matches stage paths via `DESCRIBE STREAMLIT`, and if possible, perform a basic health check by accessing the app endpoint.

```bash
# Wrong: Only checking if object exists — passes even with broken deployments
validate:object:
  cmds:
    - uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA {{.DB}}.{{.SCHEMA}};" | grep -q "APP"
    - echo "[PASS] Object exists"
# Result: Object exists but has wrong ROOT_LOCATION — app fails at runtime

# Correct: Validate existence, file health, and path alignment
validate:object:
  cmds:
    - |
      echo "Checking object exists..."
      uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA {{.DB}}.{{.SCHEMA}};" | grep -q "APP"
      echo "[PASS] Object exists"
    - |
      echo "Checking stage file count..."
      COUNT=$(uvx snow sql -q "LIST @{{.STAGE}};" | grep -cE '\.py$|\.ipynb$|\.yml$')
      [ "$COUNT" -ge 2 ] || { echo "[FAIL] Expected >=2 files, found $COUNT"; exit 1; }
      echo "[PASS] Stage has $COUNT application files"
    - |
      echo "Checking no compressed files..."
      uvx snow sql -q "LIST @{{.STAGE}};" | grep -qE '\.py\.gz|\.yml\.gz' \
        && { echo "[FAIL] Compressed files found"; exit 1; } || true
      echo "[PASS] No compressed files detected"
```
