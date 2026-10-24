-- Filename: eval_pat_create.sql
-- Description: Explicit initial issuance; never replaces an existing named PAT.
-- Prerequisites: Verified project-managed service user/role and approved network policy;
-- MODIFY PROGRAMMATIC AUTHENTICATION METHODS on this user when issuing for another user.
-- Creates: Role-restricted PAT with configured lifetime (account policy may reject it).
-- Parameters: Same --user/--role/--token as identity setup; --days-to-expiry.
-- SECURITY: Run only in a private administrator UI with logging/export disabled.
-- The result contains a one-time token_secret. Do not run through captured agent tools.
ALTER USER __USER__ ADD PROGRAMMATIC ACCESS TOKEN __TOKEN__
  ROLE_RESTRICTION = '__ROLE__' DAYS_TO_EXPIRY = __DAYS__
  COMMENT = 'ai-coding-rules:eval-pat:v1';
