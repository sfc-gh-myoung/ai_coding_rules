-- Filename: eval_network_policy.sql
-- Description: Optional new, user-scoped approved ingress policy; never replaces one.
-- Prerequisites: Existing database/schema and network-rule/policy creation authority.
-- Creates: Explicitly named network rule and policy. Review approved CIDRs first.
-- Parameters: --network-rule DB.SCHEMA.RULE --allowed-network CIDR (repeat).
-- No IF NOT EXISTS: a conflicting object fails rather than silently reusing it.
CREATE NETWORK RULE __NETWORK_RULE__ MODE = INGRESS TYPE = IPV4
  VALUE_LIST = (__ALLOWED_NETWORKS__)
  COMMENT = 'ai-coding-rules:eval-network-rule:v1';
CREATE NETWORK POLICY __NETWORK_POLICY__ ALLOWED_NETWORK_RULE_LIST = ('__NETWORK_RULE__')
  COMMENT = 'ai-coding-rules:eval-network-policy:v1';
-- Attach only to the evaluation user through eval_identity.sql, not ALTER ACCOUNT.
