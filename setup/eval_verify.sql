-- Filename: eval_verify.sql
-- Description: Read-only exact identity, grants, network policy and PAT metadata checks.
-- Prerequisites: Visibility on the selected user/role/network policy.
-- Creates: Nothing; no credential secret is returned by these commands.
-- Parameters: --user/--role/--network-policy; inspect selected token in the final output.
DESCRIBE USER __USER__;
SHOW GRANTS TO USER __USER__;
SHOW GRANTS TO ROLE __ROLE__;
DESCRIBE NETWORK POLICY __NETWORK_POLICY__;
SHOW USER PROGRAMMATIC ACCESS TOKENS FOR USER __USER__;
