**Description:** Comprehensive best practices for Snowflake Snowpark Container Services (SPCS), covering containerized application deployment, management, and optimization.
**AppliesTo:** `**/*.yaml`, `**/*.yml`, `**/*.sql`, `**/*.py`, `**/Dockerfile*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~650
**ContextTier:** Medium

# Snowflake Snowpark Container Services (SPCS) Best Practices

## Purpose
Provide comprehensive guidance for deploying, managing, and optimizing containerized applications using Snowflake Snowpark Container Services, covering architecture patterns, security, performance optimization, and operational best practices.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Snowpark Container Services, containerized applications, microservices

## Key Principles
- Use OCI-compliant images; leverage Snowflake's managed image registry for secure storage.
- Design services for high availability with proper health checks and resource limits.
- Optimize compute pools for workload patterns; use GPUs for ML/AI workloads.
- Implement proper service-to-service communication and external endpoint security.
- Follow cost optimization patterns; monitor usage and scale appropriately.

## 1. Architecture, Images, and Service Types

### Container and Image Management
- **Rule:** Build OCI-compliant images optimized for Snowflake; use multi-stage builds to minimize size.
- **Always:** Use Snowflake's managed image registry with semantic versioning (e.g., `v1.2.3`, not `latest`).
- **Rule:** Include health check endpoints in applications; implement vulnerability scanning and automated builds.
- **Always:** Design stateless services with graceful shutdown handling and explicit resource limits.

```sql
-- Create and configure image repository
CREATE IMAGE REPOSITORY my_app_repo;
GRANT USAGE ON IMAGE REPOSITORY my_app_repo TO ROLE app_developer_role;
```

```bash
# Upload image with proper tagging
docker tag my-app:v1.0.0 <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0
docker push <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0
```

### Service Types and Patterns
- **Rule:** Use long-running services for web applications, APIs, and persistent workloads.
- **Rule:** Use job services for batch processing, ML training, and finite-duration tasks.
- **Always:** Choose service type based on workload characteristics and implement proper lifecycle management.

## 2. Compute Pools and Resource Management

### Pool Configuration and Scaling
- **Rule:** Right-size compute pools based on workload requirements; set appropriate min/max nodes for auto-scaling.
- **Rule:** Use GPU-enabled machine types only for ML/AI workloads requiring GPU acceleration.
- **Always:** Configure auto-suspend for variable workloads; use dedicated pools for production guarantees.
- **Always:** Monitor utilization, costs, and implement account-level quotas and limits.

```sql
-- Compute pool examples
CREATE COMPUTE POOL my_app_pool MIN_NODES = 1 MAX_NODES = 5 INSTANCE_FAMILY = CPU_X64_XS;
CREATE COMPUTE POOL ml_training_pool MIN_NODES = 1 MAX_NODES = 3 INSTANCE_FAMILY = GPU_NV_S;
```

## 3. Service Specifications and Security

### YAML Configuration and Security Standards
- **Rule:** Use explicit resource requests/limits; implement structured logging with `logExporters`.
- **Always:** Build health endpoints into applications; use environment variables for configuration.
- **Rule:** Never include secrets in specifications; use Snowflake's secret management instead.
- **Always:** Follow official SPCS specification syntax; implement least-privilege access controls.

```yaml
# Complete service specification with security
spec:
  containers:
  - name: my-app
    image: /my_db/my_schema/my_app_repo/my-app:v1.0.0
    resources:
      requests: { memory: 1Gi, cpu: 0.5 }
      limits: { memory: 2Gi, cpu: 1.0 }
    env:
      SNOWFLAKE_WAREHOUSE: MY_WAREHOUSE
      LOG_LEVEL: INFO
    secrets:
    - snowflakeSecret: { objectName: db-credentials }
      envVarName: DATABASE_PASSWORD
      secretKeyRef: password
  logExporters:
    eventTableConfig: { logLevel: INFO }
  endpoints:
  - name: web-endpoint
    port: 8080
    public: true
    protocol: HTTP
capabilities:
  securityContext: { executeAsCaller: false }
serviceRoles:
- name: api_user_role
  endpoints: [web-endpoint]
```

## 4. Networking and Data Integration

### Service Communication and Endpoints
- **Rule:** Use service DNS names for internal communication; configure public endpoints only when required.
- **Always:** Implement connection pooling, circuit breakers, and proper authentication for external endpoints.
- **Rule:** Use HTTPS/TLS for external communications; monitor and log endpoint access.
- **Always:** Use Snowflake connectors with connection pooling for optimal data access performance.

### Data Access and Stage Integration
- **Rule:** Leverage Snowflake stages for file-based data exchange; use appropriate warehouse sizes.
- **Always:** Clean up temporary stage files; implement proper error handling and use efficient formats (Parquet, JSON).

```python
# Snowflake connectivity with connection pooling
import snowflake.connector
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'), warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'), schema=os.getenv('SNOWFLAKE_SCHEMA'),
        authenticator='snowflake_jwt', private_key=get_private_key()
    )
```

```yaml
# Service with stage volumes and endpoints
spec:
  containers:
  - name: data-processor
    image: /my_db/my_schema/my_app_repo/processor:v1.0.0
    volumeMounts:
    - { name: data-stage, mountPath: /data }
    - { name: temp-storage, mountPath: /tmp }
  volumes:
  - { name: data-stage, source: "@my_data_stage", uid: 1000, gid: 1000 }
  - { name: temp-storage, source: local }
  endpoints:
  - { name: api, port: 8080, public: true, protocol: HTTP }
```

## 5. Monitoring, Logging, and Troubleshooting

### Service Monitoring and Health Checks
- **Always:** Build health endpoints into applications; use structured JSON logging with correlation IDs.
- **Rule:** Monitor metrics using `platformMonitor`; set up alerting based on logs and external monitoring.
- **Always:** Since SPCS has no built-in health probes, implement application-level health checks.

### Logging and Observability
- **Rule:** Use Snowflake's logging functions for analysis; implement appropriate log retention policies.
- **Always:** Include request IDs and user context; log health status for monitoring via log analysis.

```yaml
# Monitoring configuration
spec:
  containers:
  - name: my-app
    env: { HEALTH_CHECK_PORT: "8080", HEALTH_CHECK_PATH: "/health" }
  logExporters: { eventTableConfig: { logLevel: INFO } }
  platformMonitor: { metricConfig: { groups: [basic] } }
```

```python
# Health check implementation
from flask import Flask, jsonify
import logging
app = Flask(__name__)
@app.route('/health')
def health_check():
    try:
        health_status = {"status": "healthy", "checks": {"database": "ok", "memory": "ok"}}
        logging.info(f"Health check passed: {health_status}")
        return jsonify(health_status), 200
    except Exception as e:
        error_status = {"status": "unhealthy", "error": str(e)}
        logging.error(f"Health check failed: {error_status}")
        return jsonify(error_status), 503
```

### Troubleshooting and Debugging
- **Always:** Check service logs first; verify compute pool capacity and network connectivity.
- **Rule:** Validate YAML syntax; use Snowflake's built-in monitoring functions for operational visibility.

```sql
-- Essential troubleshooting queries
SELECT * FROM TABLE(SYSTEM$GET_SERVICE_LOGS('my_service', 'web-app', 100));
SELECT * FROM TABLE(SPCS_GET_EVENTS('my_service'));
SELECT SYSTEM$GET_SERVICE_STATUS('my_service');
SHOW SERVICES; SHOW COMPUTE POOLS; DESCRIBE SERVICE my_service;
```

## 6. Performance Optimization and Cost Management

### Container and Resource Optimization
- **Rule:** Use optimized base images (Alpine, distroless); minimize startup time through image optimization.
- **Always:** Profile applications for optimal resource allocations; implement proper caching and connection pooling.
- **Rule:** Use multi-stage builds; implement horizontal scaling for variable workloads.

### Cost Optimization and Efficiency
- **Rule:** Use auto-suspend for dev/test; share compute pools across similar workloads for better utilization.
- **Always:** Monitor costs and right-size pools; implement cost budgets and alerts for SPCS usage.
- **Rule:** Clean up unused services regularly; use appropriate instance families for workload characteristics.

```sql
-- Cost monitoring and optimization
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.COMPUTE_POOL_HISTORY 
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```


## 7. Development, Testing, and Deployment

### CI/CD and Testing Strategies
- **Rule:** Implement automated testing for images and specifications; use infrastructure as code.
- **Always:** Test services in isolated compute pools; implement integration and synthetic monitoring tests.
- **Rule:** Use proper environment promotion workflows (dev then test then prod) with approval gates.
- **Always:** Test disaster recovery scenarios; maintain deployment runbooks.

## 8. ML/AI Workloads and Advanced Patterns

### Machine Learning and GPU Workloads
- **Rule:** Use GPU-enabled compute pools for ML training; integrate with Snowflake ML features.
- **Always:** Use job services for model training/inference; implement proper model versioning.
- **Rule:** Integrate with Streams and Tasks for event-driven processing; leverage data sharing capabilities.

```yaml
# GPU-enabled ML training specification
spec:
  containers:
  - name: ml-trainer
    image: /my_db/my_schema/ml_repo/trainer:v2.0.0
    resources:
      requests: { memory: 8Gi, cpu: 2.0, nvidia.com/gpu: 1 }
      limits: { memory: 16Gi, cpu: 4.0, nvidia.com/gpu: 1 }
    env: { CUDA_VISIBLE_DEVICES: "0", MODEL_OUTPUT_PATH: "/models" }
    volumeMounts: [{ name: model-storage, mountPath: /models }]
  volumes: [{ name: model-storage, source: "@model_artifacts_stage" }]
```

### Compliance and Governance
- **Always:** Maintain audit logs; implement data lineage tracking and use Snowflake's governance features.
- **Rule:** Implement data masking/encryption; follow data residency requirements and retention policies.

## 9. Anti-Patterns and Common Pitfalls

### Critical Anti-Patterns to Avoid
- **Avoid:** Using `latest` tags in production; hardcoding secrets in images; running unnecessary root containers.
- **Avoid:** Creating oversized pools for simple workloads; exposing internal services publicly.
- **Avoid:** New connections per request (use pooling); processing large datasets in memory without streaming.
- **Avoid:** Ignoring resource limits; using synchronous processing for long-running operations.

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Snowpark Container Services Overview](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview) - Architecture, concepts, and getting started guide                                        
- [SPCS Tutorials](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials) - Step-by-step implementation examples                                                                          
- [Service Specification Reference](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference) - YAML service definition schema and options                                     
- [SPCS SQL Commands](https://docs.snowflake.com/en/sql-reference/sql/create-service) - CREATE SERVICE and related SQL command reference                                                                                
- [SPCS Cost Management](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/costs) - Pricing model and cost optimization strategies

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Security Governance**: `107-snowflake-security-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
