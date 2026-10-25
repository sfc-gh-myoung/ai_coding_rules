-- Filename: eval_identity_check.sql
-- Description: Fail-closed prerequisite check before PAT creation or rotation/revocation.
-- Prerequisites: Visibility on exact user/role; administrator context.
-- Creates: Nothing. The renderer prefixes this check to token lifecycle operations.
-- Parameters: --user/--role; markers must match without auto-adoption.
EXECUTE IMMEDIATE $$
DECLARE
  existing_count INTEGER;
  conflict_count INTEGER;
  conflict EXCEPTION (-20003, 'PAT operation requires a verified project-managed identity.');
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
  RETURN 'Project identity markers verified; inspect grants and policy separately.';
END;
$$;
