# 120 Example: SPCS Service Specification

> **EXAMPLE FILE** - Reference implementation for `120-snowflake-spcs.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 120-snowflake-spcs.md
**Demonstrates:** Complete Snowpark Container Services deployment with production-ready YAML specification including security, logging, and RBAC
**Use When:** Deploying containerized applications to SPCS with proper resource limits, secrets management, and service roles
**Version:** 1.0
**Last Validated:** 2026-01-27

## Prerequisites

- [ ] Snowflake account with SPCS enabled
- [ ] ACCOUNTADMIN or role with CREATE COMPUTE POOL, CREATE SERVICE privileges
- [ ] Docker image built and ready to push
- [ ] Snowflake secret created for sensitive configuration
- [ ] Database and schema for image repository

## Implementation

### Step 1: Create Image Repository

```sql
-- Create image repository in target schema
CREATE IMAGE REPOSITORY my_db.my_schema.my_app_repo;

-- Grant usage to developer role
GRANT USAGE ON IMAGE REPOSITORY my_db.my_schema.my_app_repo 
  TO ROLE app_developer_role;

-- Get repository URL for docker push
SHOW IMAGE REPOSITORIES LIKE 'my_app_repo' IN SCHEMA my_db.my_schema;
-- Copy the repository_url value
```

### Step 2: Build and Push Docker Image

```bash
# Authenticate to Snowflake registry
docker login <account>.registry.snowflakecomputing.com \
  -u <username>

# Tag image with semantic version (NEVER use 'latest')
docker tag my-app:local \
  <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0

# Push to Snowflake registry
docker push \
  <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0
```

### Step 3: Create Compute Pool

```sql
-- Create compute pool with auto-scaling
CREATE COMPUTE POOL my_app_pool
  MIN_NODES = 1
  MAX_NODES = 5
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_SUSPEND_SECS = 300
  COMMENT = 'Compute pool for my-app service';

-- For GPU workloads (ML/AI only)
CREATE COMPUTE POOL ml_training_pool
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = GPU_NV_S
  AUTO_SUSPEND_SECS = 600
  COMMENT = 'GPU pool for ML training jobs';

-- Verify pool status
SHOW COMPUTE POOLS LIKE 'my_app_pool';
DESC COMPUTE POOL my_app_pool;
```

### Step 4: Create Secret for Sensitive Configuration

```sql
-- Create secret for database credentials
CREATE SECRET my_db.my_schema.db_credentials
  TYPE = GENERIC_STRING
  SECRET_STRING = '{"username": "app_user", "password": "secure_password_here"}';

-- Grant usage to service role
GRANT USAGE ON SECRET my_db.my_schema.db_credentials 
  TO ROLE app_service_role;
```

### Step 5: Create Service Specification (YAML)

Save as `service_spec.yaml`:

```yaml
spec:
  containers:
  - name: my-app
    image: /my_db/my_schema/my_app_repo/my-app:v1.0.0
    
    # Resource limits (MANDATORY - prevents runaway resource usage)
    resources:
      requests:
        memory: 1Gi
        cpu: 0.5
      limits:
        memory: 2Gi
        cpu: 1.0
    
    # Environment variables (non-sensitive config)
    env:
      SNOWFLAKE_WAREHOUSE: MY_WAREHOUSE
      SNOWFLAKE_DATABASE: MY_DB
      SNOWFLAKE_SCHEMA: MY_SCHEMA
      LOG_LEVEL: INFO
      APP_ENV: production
    
    # Secrets (NEVER put sensitive values in env directly)
    secrets:
    - snowflakeSecret:
        objectName: db_credentials
      envVarName: DATABASE_CREDENTIALS
      secretKeyRef: password
    
    # Readiness probe (application health check)
    readinessProbe:
      port: 8080
      path: /health
  
  # Structured logging to event table
  logExporters:
    eventTableConfig:
      logLevel: INFO
  
  # Service endpoints
  endpoints:
  - name: web-endpoint
    port: 8080
    public: true
    protocol: HTTP
  
  - name: metrics-endpoint
    port: 9090
    public: false
    protocol: TCP

# Security context (CRITICAL for production)
capabilities:
  securityContext:
    executeAsCaller: false

# Service roles for RBAC (who can access which endpoints)
serviceRoles:
- name: api_user_role
  endpoints:
  - web-endpoint

- name: monitoring_role
  endpoints:
  - web-endpoint
  - metrics-endpoint
```

### Step 6: Create and Start Service

```sql
-- Create service from specification
CREATE SERVICE my_db.my_schema.my_app_service
  IN COMPUTE POOL my_app_pool
  FROM SPECIFICATION $$
spec:
  containers:
  - name: my-app
    image: /my_db/my_schema/my_app_repo/my-app:v1.0.0
    resources:
      requests:
        memory: 1Gi
        cpu: 0.5
      limits:
        memory: 2Gi
        cpu: 1.0
    env:
      SNOWFLAKE_WAREHOUSE: MY_WAREHOUSE
      LOG_LEVEL: INFO
    secrets:
    - snowflakeSecret:
        objectName: db_credentials
      envVarName: DATABASE_CREDENTIALS
      secretKeyRef: password
  logExporters:
    eventTableConfig:
      logLevel: INFO
  endpoints:
  - name: web-endpoint
    port: 8080
    public: true
    protocol: HTTP
capabilities:
  securityContext:
    executeAsCaller: false
serviceRoles:
- name: api_user_role
  endpoints:
  - web-endpoint
$$
  COMMENT = 'Production web application service';

-- Grant service role to users
GRANT SERVICE ROLE my_db.my_schema.my_app_service!api_user_role 
  TO ROLE analyst_role;
```

## Monitoring

```sql
-- Check service status
SHOW SERVICES LIKE 'my_app_service';
DESC SERVICE my_db.my_schema.my_app_service;

-- Get service logs from event table
SELECT *
FROM my_db.my_schema.my_event_table
WHERE RESOURCE_ATTRIBUTES['snow.service.name'] = 'my_app_service'
ORDER BY TIMESTAMP DESC
LIMIT 100;

-- Check container status
SELECT SYSTEM$GET_SERVICE_STATUS('my_db.my_schema.my_app_service');

-- Get service endpoint URL
SHOW ENDPOINTS IN SERVICE my_db.my_schema.my_app_service;
```

## Validation

```sql
-- Verify image was pushed
SHOW IMAGES IN IMAGE REPOSITORY my_db.my_schema.my_app_repo;
-- Expected: my-app:v1.0.0 listed

-- Verify compute pool is active
SHOW COMPUTE POOLS LIKE 'my_app_pool';
-- Expected: state = ACTIVE or IDLE

-- Verify service is running
SELECT SYSTEM$GET_SERVICE_STATUS('my_db.my_schema.my_app_service');
-- Expected: status = READY for all containers

-- Test endpoint accessibility (from allowed role)
-- Use the ingress_url from SHOW ENDPOINTS
SELECT SYSTEM$GET_SERVICE_ENDPOINT('my_db.my_schema.my_app_service', 'web-endpoint');
```

**Expected Results:**
- Image repository contains versioned image (v1.0.0)
- Compute pool shows ACTIVE or IDLE state
- Service status shows READY for all containers
- Endpoint URL accessible from granted roles
- Logs appear in event table with structured format
