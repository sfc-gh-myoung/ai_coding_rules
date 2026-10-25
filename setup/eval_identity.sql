-- Filename: eval_identity.sql
-- Description: Provision only the project-managed rule-discovery identity.
-- Prerequisites: Administrator role with CREATE USER, CREATE ROLE and grant authority;
-- an existing approved network policy.
-- Creates: Configurable service user and Cortex Agent evaluation role.
-- Parameters: Rendered by make eval-setup / eval-identity (see setup/README.md).
EXECUTE IMMEDIATE $$
DECLARE
  existing_count INTEGER;
  conflict_count INTEGER;
  conflict EXCEPTION (-20001, 'Existing identity is not project-managed; no adoption or replacement permitted.');
BEGIN
  SHOW USERS LIKE '__USER__';
  SELECT COUNT(*), COUNT_IF(COALESCE("comment", '') != 'ai-coding-rules:eval-identity:v1'
    OR COALESCE("type", '') != 'SERVICE') INTO :existing_count, :conflict_count
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) WHERE "name" = '__USER__';
  IF (existing_count > 0 AND conflict_count > 0) THEN
    RAISE conflict;
  END IF;
  SHOW ROLES LIKE '__ROLE__';
  SELECT COUNT(*), COUNT_IF(COALESCE("comment", '') != 'ai-coding-rules:eval-role:v1')
    INTO :existing_count, :conflict_count
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) WHERE "name" = '__ROLE__';
  IF (existing_count > 0 AND conflict_count > 0) THEN
    RAISE conflict;
  END IF;
  CREATE ROLE IF NOT EXISTS __ROLE__ COMMENT = 'ai-coding-rules:eval-role:v1';
  GRANT DATABASE ROLE SNOWFLAKE.CORTEX_AGENT_USER TO ROLE __ROLE__;
  CREATE USER IF NOT EXISTS __USER__ TYPE = SERVICE DEFAULT_ROLE = __ROLE__
    COMMENT = 'ai-coding-rules:eval-identity:v1';
  GRANT ROLE __ROLE__ TO USER __USER__;
  ALTER USER __USER__ SET DEFAULT_ROLE = __ROLE__ NETWORK_POLICY = __NETWORK_POLICY__;
  RETURN 'Project-managed identity configured. No PAT issued or rotated.';
END;
$$;
