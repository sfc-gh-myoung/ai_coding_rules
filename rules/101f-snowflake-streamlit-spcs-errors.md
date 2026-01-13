# Streamlit SPCS Deployment Errors

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** SPCS error, Docker build failure, container networking, image registry, service startup timeout, port binding, deployment error, container error, SPCS troubleshooting
**TokenBudget:** ~1600
**ContextTier:** Low
**Depends:** 101-snowflake-streamlit-core.md

## Scope

**What This Rule Covers:**
SPCS-specific deployment error scenarios and resolution steps for Streamlit applications running on Snowpark Container Services.

**When to Load This Rule:**
- Debugging SPCS deployment failures
- Troubleshooting Docker build errors for Snowflake
- Resolving container networking issues
- Fixing image registry authentication problems
- Diagnosing service startup timeouts

## References

### Dependencies

**Must Load First:**
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns and SPCS overview

**Related:**
- **120-snowflake-spcs.md** - Snowpark Container Services fundamentals

### External Documentation

- [SPCS Documentation](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview) - Official SPCS guide
- [SPCS Troubleshooting](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/troubleshooting) - Error resolution

## Contract

### Inputs and Prerequisites

- SPCS service deployment attempted
- Error message from deployment or service logs
- Access to Snowflake account with SPCS permissions

### Mandatory

- Identify error type from error message
- Follow resolution steps in order
- Verify fix before redeploying

### Forbidden

- Deploying without testing Docker build locally first
- Ignoring service logs when debugging
- Hardcoding credentials in Dockerfiles

### Execution Steps

1. Match error message to error scenario below
2. Follow resolution steps for that scenario
3. Verify fix locally if possible
4. Redeploy and monitor logs

### Output Format

Resolved SPCS deployment with service status READY.

### Validation

- Service logs show successful startup
- Health check endpoint responds
- Application accessible via endpoint URL

### Post-Execution Checklist

- [ ] Error identified and matched to scenario
- [ ] Resolution steps followed in order
- [ ] Fix verified locally before redeploying
- [ ] Service status shows READY after deployment

## Error Scenarios

### Error 1: Docker Build Failure - Dependency Resolution

```
Error: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
exit code: 1
```

**Cause:** Package dependency resolution failed or package not available on PyPI

**Resolution:**
1. Verify all packages in requirements.txt are available: `pip install --dry-run -r requirements.txt`
2. Test Docker build locally before pushing: `docker build -t test-image .`
3. Check for conflicting package versions: Review pip resolver output
4. Pin working versions: Use `pip freeze > requirements.txt` from tested environment
5. Consider using multi-stage builds to separate dependency installation

### Error 2: Container Networking Timeout

```
Error: dial tcp 10.0.0.5:443: i/o timeout
```

**Cause:** SPCS container cannot reach external API, Snowflake service, or internet resource

**Resolution:**
1. Verify external access enabled in service specification: `EXTERNAL_ACCESS_INTEGRATIONS`
2. Check network policy allows outbound connections: `SHOW NETWORK POLICIES`
3. Confirm API endpoint is reachable from SPCS: Test with `curl` in container
4. Review egress firewall rules and allowed endpoints list
5. Validate external access integration configuration: `DESCRIBE INTEGRATION <name>`

### Error 3: Image Registry Authentication Failure

```
Error: failed to pull image <org>-<account>.registry.snowflakecomputing.com/mydb/myschema/myrepo/myapp:latest
Error: unauthorized: authentication required
```

**Cause:** Missing or invalid authentication to Snowflake image repository

**Resolution:**
1. Authenticate to repository: `docker login <org>-<account>.registry.snowflakecomputing.com`
2. Verify repository exists: `SHOW IMAGE REPOSITORIES IN SCHEMA`
3. Check repository grants: `SHOW GRANTS ON IMAGE REPOSITORY <name>`
4. Confirm image was pushed successfully: `SHOW IMAGES IN IMAGE REPOSITORY <name>`
5. Validate image tag matches service specification exactly (case-sensitive)

### Error 4: Service Startup Timeout

```
Error: Service failed to start within timeout period (300s)
Container health check failed
```

**Cause:** Application takes too long to start or health check endpoint not responding

**Resolution:**
1. Optimize container startup time: Reduce image size, pre-compile dependencies
2. Increase service timeout: Adjust `MAX_STARTUP_TIME` in service specification (max 600s)
3. Verify health check endpoint: Ensure `/healthz` or configured path responds quickly
4. Review container logs: `CALL SYSTEM$GET_SERVICE_LOGS('<service_name>', 0, 'main')`
5. Check resource allocation: Increase CPU/memory if application is resource-constrained

### Error 5: Port Binding Conflict

```
Error: failed to create endpoint: port 8501 already in use
```

**Cause:** Multiple containers trying to bind to same port or incorrect port mapping

**Resolution:**
1. Verify service specification port mapping matches Dockerfile `EXPOSE` directive
2. Check only one process binds to application port in container
3. Review service specification: Ensure unique port assignments per endpoint
4. Validate Streamlit runs on expected port: Check `config.toml` or `--server.port` flag
5. Restart service to clear stale port bindings: `ALTER SERVICE <name> SUSPEND; ALTER SERVICE <name> RESUME;`

## Validation Checklist

**Before Deployment:**
- [ ] Docker image builds successfully locally
- [ ] All required external access integrations configured
- [ ] Image pushed to Snowflake registry and accessible
- [ ] Health check endpoint responds within timeout
- [ ] Port mappings consistent between Dockerfile and service spec

**After Deployment:**
- [ ] Service logs reviewed for startup errors
- [ ] Resource allocation sufficient for application requirements
- [ ] Service status shows READY

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Skipping Local Docker Build

**Problem:**
```bash
snow spcs image-repository push myimage:latest
```

**Why It Fails:** Pushing directly without local build verification leads to runtime failures that are harder to debug in SPCS.

**Correct Pattern:**
```bash
docker build -t myimage:latest .
docker run -p 8501:8501 myimage:latest
snow spcs image-repository push myimage:latest
```

### Anti-Pattern 2: Missing Health Check Endpoint

**Problem:**
```yaml
spec:
  containers:
    - name: main
      image: myimage:latest
```

**Why It Fails:** SPCS cannot verify container health, causing timeout failures and service instability.

**Correct Pattern:**
```yaml
spec:
  containers:
    - name: main
      image: myimage:latest
      readinessProbe:
        path: /healthz
        port: 8501
```
