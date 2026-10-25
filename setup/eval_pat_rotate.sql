-- Filename: eval_pat_rotate.sql
-- Description: Explicit rotation; retains a bounded handoff period for the old secret.
-- Prerequisites: Verify exact user/token metadata first; administrator rotation authority.
-- Creates: New token secret. Existing PAT lifetime/role restriction remain unchanged.
-- Parameters: --user/--token and --rotation-overlap-hours (0-24).
-- SECURITY: Private terminal or administrator UI only; result contains a one-time token_secret.
-- Never run through captured agent tools or store the result in generated SQL/logs.
ALTER USER __USER__ ROTATE PROGRAMMATIC ACCESS TOKEN __TOKEN__
  EXPIRE_ROTATED_TOKEN_AFTER_HOURS = __OVERLAP__;
