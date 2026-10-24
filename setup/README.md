# Evaluation identity and PAT setup

This directory contains reviewed SQL templates, not an automatic provisioning
service. The project renders SQL for administrator review; **it never executes
setup or captures PAT secrets**. This avoids leaking one-time token results into
agent transcripts, terminal logs or project files.

## Defaults and overrides

| Setting | Default | CLI parameter | Environment |
|---|---|---|---|
| User | `AI_RULES_EVAL_USER` | `--user` | `AI_RULES_EVAL_USER` |
| Role | `AI_RULES_EVAL_ROLE` | `--role` | `AI_RULES_EVAL_ROLE` |
| PAT name | `AI_RULES_EVAL_PAT` | `--token` | `AI_RULES_EVAL_PAT` |
| Eval connection name | `ai_rules_eval` (recommended) | `--connection` on doctor/eval | `SNOWFLAKE_CONNECTION_NAME` |
| Existing network policy | None; required | `--network-policy` | `AI_RULES_EVAL_NETWORK_POLICY` |
| Token lifetime | 15 days | `--days-to-expiry` | None |
| Rotation handoff | 24 hours | `--rotation-overlap-hours` | None |

Identity precedence is **CLI parameter > environment > default**. Make also
accepts `EVAL_USER`, `EVAL_ROLE`, and `EVAL_PAT`, exporting them to the renderer.
Identifiers are conservative unquoted names (letters, digits, underscores).
The connection name is a local configuration name, not a Snowflake user name.
Never supply the secret as `--token`: that option names the PAT object only.

## Prerequisites

Ask the account administrator to review the grants and policy first. They need
authority to create the dedicated user/role, grant the Cortex database role, and
modify programmatic authentication methods for this user. Use a separate
administrator connection or private Snowsight worksheet, never the evaluation
PAT to manage its own lifecycle. SQL does not switch administrator roles for you.

The evaluation user is `TYPE=SERVICE`, with role-restricted PAT authentication and
an approved user-scoped network policy. The role receives only
`SNOWFLAKE.CORTEX_AGENT_USER` for CLI/SDK agent inference. No warehouse, database,
ACCOUNT_USAGE, ownership, administrative or benchmark DDL privileges are granted.
The account must allow the models and PAT authentication. Broader SQL workloads
are outside this rule-discovery evaluator and need separate reviewed grants.

## 1. Prepare network access

Prefer an existing administrator-approved network policy that permits the runner.
Do not copy a policy name from another account without checking it. If a new
policy is needed, render the optional file with explicit approved IPv4 CIDRs:

```bash
make eval-setup-preview CLI_ARGS="network-policy --network-policy AI_RULES_EVAL_POLICY --network-rule ADMIN_DB.SECURITY.AI_RULES_EVAL_RULE --allowed-network 192.0.2.10/32 --output .workbench/pat-setup/01-network.sql"
```

The address above is documentation-only; replace it with an approved runner
address. The database/schema must already exist. `/0` is rejected. No existing
policy/rule is replaced; conflicting names fail. The policy is not attached at
account scope. An administrator reviews and executes the rendered SQL separately.

## 2. Provision the identity

```bash
make eval-setup-preview CLI_ARGS="identity --network-policy APPROVED_RUNNER_POLICY --output .workbench/pat-setup/02-identity.sql"
make eval-setup-preview EVAL_USER=MY_RULES_EVAL EVAL_ROLE=MY_RULES_ROLE CLI_ARGS="identity --network-policy APPROVED_RUNNER_POLICY --output .workbench/pat-setup/custom-identity.sql"
```

Direct CLI override:

```bash
uv run ai-rules rule-loader setup-preview identity --user MY_RULES_EVAL --role MY_RULES_ROLE --network-policy APPROVED_RUNNER_POLICY --output .workbench/pat-setup/identity.sql
```

Render previews outside source evidence, review them, then have the administrator
execute the nonsecret identity SQL using their explicitly selected admin context.
Existing unmarked users/roles fail closed; the tool does not adopt them. Marked
identities can be re-granted and their defaults/policy reconciled. Inspect existing
grants first: markers do not prove least privilege or absence of user-added work.
DDL is not transactional; a later failure can leave earlier setup changes present.
Use verification to inspect partial setup before retrying. PAT issuance is separate.

## 3. Verify and issue a role-restricted PAT

```bash
make eval-setup-preview CLI_ARGS="verify --network-policy APPROVED_RUNNER_POLICY --output .workbench/pat-setup/03-verify.sql"
make eval-setup-preview CLI_ARGS="create-pat --days-to-expiry 15 --output .workbench/pat-setup/04-create-pat.sql"
```

Use the **same overrides** for every operation. Verify the exact user type,
ownership markers, assigned/default role, Cortex grants, network policy and PAT
metadata. Review the configured policy and authentication requirements.

Execute PAT issuance only in a private administrator UI where query-result logging,
screen recording and exports are controlled. The result contains `token_secret`
once. Enter it directly into your approved secret manager/connection manager;
do not copy it into this repository, agent chat, terminal arguments or logs.
There is no project-owned automatic secret-store handoff. A duplicate PAT name
fails; setup never removes or rotates a working token automatically.

## 4. Configure and use the evaluation connection

Create the local connection named `ai_rules_eval` (or your chosen name) using the
supported Snowflake client/connection manager. These **nonsecret** fields must
match the provisioned identity:

```toml
[ai_rules_eval]
account = "your-org-your-account"
user = "AI_RULES_EVAL_USER"
role = "AI_RULES_EVAL_ROLE"
authenticator = "PROGRAMMATIC_ACCESS_TOKEN"
```

Supply the PAT in the client's password credential slot through its approved
secure credential mechanism. Do not save this illustrative fragment in the repo
as a credential file. Default `snowflake` authentication with a PAT password is
also supported by Snowflake clients. The preflight checks the existing selected
configuration; it does not automatically inject a `/secrets` entry into it.
Never switch to an unrelated configured user just because a connection succeeds.

```bash
make eval-doctor CONNECTION=ai_rules_eval CLI_ARGS="--require-pat --with-smoke"
make eval-live CONNECTION=ai_rules_eval CLI_ARGS="--require-pat --fixture simple-python-task --runs 1 --model openai-gpt-6-sol"
make eval-all-models CONNECTION=ai_rules_eval CLI_ARGS="--require-pat --runs 5 --effort medium --max-turns 25 --concurrency 3 --retry-infra 2"
```

Live calls cost credits. A successful smoke proves an awake fresh SDK process,
not a locked-screen run or long-session renewal. See
[PAT evaluation](../docs/PAT_EVALUATION.md) for those limits.

## 5. Rotate, revoke or tear down explicitly

```bash
make eval-setup-preview CLI_ARGS="rotate-pat --rotation-overlap-hours 24 --output .workbench/pat-setup/rotate.sql"
make eval-setup-preview CLI_ARGS="revoke-pat --confirm-destructive --output .workbench/pat-setup/revoke.sql"
make eval-setup-preview CLI_ARGS="teardown --confirm-destructive --output .workbench/pat-setup/teardown.sql"
```

Rotation returns a new secret only in the private administrator UI. Update the
secure connection credential during the overlap window and test a fresh login.
Expiry and role restriction are inherited from the old token and account policy;
rotation does not grant more access. Revocation is irreversible. Do not run token
lifecycle statements from that same user's PAT-authenticated session.

Teardown checks project markers, drops only the selected user/role and leaves
shared policies/rules/warehouses/databases alone. Inspect owned objects, other
users granted the role, and all dependencies before administrator execution.
Dropping a user also invalidates its PATs; marker checks are not proof there are
no dependencies. No operation executes merely because a preview was generated.

## SQL inventory and verification limits

| File | Purpose |
|---|---|
| `eval_identity.sql` | Guarded dedicated service user and minimal role grants |
| `eval_network_policy.sql` | Optional new explicit approved ingress policy |
| `eval_identity_check.sql` | Guard prepended to token lifecycle previews |
| `eval_pat_create.sql` | Separate initial role-restricted issuance |
| `eval_verify.sql` | Read-only identity/grants/policy/PAT metadata |
| `eval_pat_rotate.sql` | Explicit bounded-overlap rotation |
| `eval_pat_revoke.sql` | Explicit exact-token revocation |
| `eval_teardown.sql` | Guarded project identity teardown |

Templates are exercised by rendering/security tests. Compile-only validation was
performed on `myoung_iuc17074_all` on 2026-10-22. With separate explicit approval,
isolated identity setup, marker checks and teardown were also executed.

| Statement | Compile-only result |
|---|---|
| `CREATE ROLE`, `CREATE USER` | Passed with project defaults |
| `CREATE NETWORK POLICY` | Passed with explicit project policy/rule names |
| PAT creation, rotation, revocation | Syntax passed using existing `MYOUNG` as the user; no token was issued, rotated or revoked |
| `ALTER USER` defaults/policy | Syntax passed using existing `MYOUNG`; no settings changed |
| PAT metadata `SHOW` | Passed using existing `MYOUNG` |
| Network rule in illustrative `ADMIN_DB.SECURITY` | Blocked because the prerequisite database does not exist |
| `ALTER USER`, PAT lifecycle and teardown with new project identity | Blocked because project user/role do not exist |
| Anonymous blocks, `EXECUTE IMMEDIATE` and `GRANT` | Compile-only validator rejects these statement classes; identity setup/grants, marker guard and teardown passed a separately approved isolated execution test |

Read-only `SHOW USERS` and `SHOW ROLES` confirmed the `name`, `comment`, and user
`type` output columns used by ownership guards. The isolated execution used
`AI_RULES_EVAL_VALIDATE_31`, `AI_RULES_EVAL_VALIDATE_ROLE_31`, and a temporary
user-scoped policy allowing only documentation address `192.0.2.10/32`.
Identity setup, the Cortex Agent grant, policy binding, marker guard and guarded
teardown succeeded. The temporary policy was removed afterward; `SHOW` verified
all three objects absent. No existing identity or shared policy was changed.

No PAT was issued, rotated or revoked. Optional network-rule creation, identity
setup rerun/idempotence, unmarked-object rejection by execution, login using the
new identity, locked-screen runs and session renewal remain unverified. Syntax
compilation against an existing user does not establish PAT lifecycle behavior.
