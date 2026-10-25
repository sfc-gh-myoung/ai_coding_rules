-- Filename: eval_teardown.sql
-- Description: Explicit guarded teardown of only the project-managed user and role.
-- Prerequisites: Stop all runs, inspect ownership/dependencies/grants, administrator authority.
-- Creates: Nothing. Never drops shared warehouses, databases, network policies or rules.
-- Parameters: --user/--role; generate with CONFIRM=1.
-- Ownership markers are safeguards, not proof there are no user-added dependencies.
EXECUTE IMMEDIATE $$
DECLARE
  existing_count INTEGER;
  conflict_count INTEGER;
  conflict EXCEPTION (-20002, 'Refusing teardown of an absent or unmarked project identity.');
BEGIN
  SHOW USERS LIKE '__USER__';
  SELECT COUNT(*), COUNT_IF(COALESCE("comment", '') != 'ai-coding-rules:eval-identity:v1'
    OR COALESCE("type", '') != 'SERVICE') INTO :existing_count, :conflict_count
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) WHERE "name" = '__USER__';
  IF (existing_count != 1 OR conflict_count > 0) THEN
    RAISE conflict;
  END IF;
  SHOW ROLES LIKE '__ROLE__';
  SELECT COUNT(*), COUNT_IF(COALESCE("comment", '') != 'ai-coding-rules:eval-role:v1')
    INTO :existing_count, :conflict_count
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) WHERE "name" = '__ROLE__';
  IF (existing_count != 1 OR conflict_count > 0) THEN
    RAISE conflict;
  END IF;
  DROP USER __USER__;
  DROP ROLE __ROLE__;
  RETURN 'Project user and role removed; shared resources preserved.';
END;
$$;
