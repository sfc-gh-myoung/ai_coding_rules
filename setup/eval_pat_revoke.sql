-- Filename: eval_pat_revoke.sql
-- Description: Explicit revocation of only the selected PAT; cannot be undone.
-- Prerequisites: Verify user/token metadata and stop runs first; administrator authority.
-- Creates: Nothing. Does not drop the user or role or alter shared policies.
-- Parameters: --user/--token; generate with CONFIRM=1.
ALTER USER __USER__ REMOVE PROGRAMMATIC ACCESS TOKEN __TOKEN__;
