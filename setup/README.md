# Evaluation identity setup

Long-running rule-loader evaluations should not depend on a browser login. This
directory provides **time-saving helpers**, not a security boundary: the Make targets
generate SQL for a dedicated, least-privilege service identity and can run it for you.
Your Snowflake administrators decide what is allowed in your account, and you or they
verify the result. Everything here can be done by hand; see
[Manual or custom process](#manual-or-custom-process).

Credentials never belong in SQL bundles, config files, command arguments or logs.

## Quick start

```bash
# 1. Generate reviewed SQL (nothing runs yet). Prints the bundle path.
make eval-setup EVAL_ACCOUNT=myorg-myaccount EVAL_NETWORK_POLICY=USER_NW_POLICY

# 2. Review the three files, then run them as an administrator.
make eval-setup-apply BUNDLE=<bundle path> ADMIN_CONNECTION=my_admin ADMIN_ROLE=ACCOUNTADMIN

# 3. Register a credential-free connection, then supply the PAT (see below).
make eval-connection-add EVAL_ACCOUNT=myorg-myaccount

# 4. Check and evaluate.
make eval-check
make eval-smoke
make eval-run
```

Step 2 asks for confirmation (`CONFIRM=1` skips it). It runs each bundle file in order
with `snow sql --filename` and stops at the first failing statement. DDL is not
transactional; inspect partial setup before retrying.

**Issuing the PAT.** `03-create-pat.sql` returns the token secret once, in the
terminal. Run step 2 yourself in a private terminal, or use `PHASE=identity` to run only
the identity and verification files and issue the PAT separately in a private
administrator UI (Snowsight worksheet). Never run the PAT file through a captured or
logged agent session. The secret is not stored anywhere by this project.

**Supplying the PAT.** Export it for the shell session without echoing it (zsh):

```zsh
read -rs "PAT?Paste PAT: "; echo
export SNOWFLAKE_CONNECTIONS_<CONNECTION_NAME_UPPERCASE>_PASSWORD="$PAT"; unset PAT
```

Or use any approved credential provider your organization supports for `snow`/`cortex`
connections. `eval-check` only confirms a credential source exists; `eval-smoke` is the
real login check and costs AI credits.

## Defaults and overrides

The `Makefile` defines every default with `?=`. Precedence, highest first:

1. Command line: `make eval-run EVAL_MODEL=openai-gpt-6-sol`
2. Environment: `EVAL_MODEL=openai-gpt-6-sol make eval-run`
3. Optional ignored `setup/eval.local.mk` for stable nonsecret values (path overridable
   with `EVAL_LOCAL=`), for example `EVAL_NETWORK_POLICY ?= USER_NW_POLICY`
4. Makefile defaults

| Variable | Default |
|---|---|
| `EVAL_USER` | `AI_RULES_EVAL_USER` |
| `EVAL_ROLE` | `AI_RULES_EVAL_ROLE` |
| `EVAL_PAT` | `AI_RULES_EVAL_PAT` (PAT object name) |
| `EVAL_CONNECTION` | `ai_rules_eval` |
| `EVAL_AUTHENTICATOR` | `PROGRAMMATIC_ACCESS_TOKEN` (or `snowflake`) |
| `EVAL_ACCOUNT` | none; `ORGANIZATION-ACCOUNT` form, required to generate SQL and register a connection |
| `EVAL_CONNECTION_ACCOUNT` | `EVAL_ACCOUNT`; the account string `eval-connection-add` writes to the connection. Set it when your environment uses another form, such as a locator (`iuc17074.us-east-1`), while the generated SQL guard keeps `EVAL_ACCOUNT` |
| `EVAL_NETWORK_POLICY` | none; required to generate identity and PAT bundles |
| `EVAL_NETWORK_RULE`, `EVAL_ALLOWED_NETWORKS` | none; only for `eval-network-policy` |
| `EVAL_OUTPUT_DIR` | `setup/sql` (contents are Git-ignored) |
| `EVAL_DAYS`, `EVAL_OVERLAP_HOURS` | `15`, `24` |
| `EVAL_MODEL`, `EVAL_FIXTURE` | `auto`, `simple-python-task` |
| `EVAL_RUNS`, `EVAL_MAX_TURNS`, `EVAL_EFFORT` | `1`, `5`, `low` |

Per-invocation inputs with no default: `BUNDLE`, `ADMIN_CONNECTION`, `ADMIN_ROLE`,
`PHASE` (`all` or `identity`) and `CONFIRM=1`. Isolated test namespaces are ordinary
overrides, for example `EVAL_USER=TEST_USER EVAL_OUTPUT_DIR=.workbench/sql`.

Make is quiet by default. Add `V=1` or `VERBOSE=1` (for example `make V=1 eval-check`)
to show the exact commands.

`EVAL_AUTHENTICATOR=snowflake` places the PAT in the password slot of a standard
connection. Use it only when your organization's CoCo policy allows it; nothing
switches authenticators after a policy rejection.

## What runs what

| Target | Runs |
|---|---|
| `eval-setup`, `eval-identity`, `eval-verify`, `eval-pat-create`, `eval-pat-rotate`, `eval-pat-revoke`, `eval-teardown`, `eval-network-policy` | `ai-rules rule-loader workflow <action>`: renders SQL into a new bundle directory with a hash manifest |
| `eval-setup-apply` | `workflow check-bundle`, then `snow sql --filename` for each bundle file |
| `eval-connection-add` | `snow connection add --no-interactive` (no secret in arguments) |
| `eval-check`, `eval-smoke` | `ai-rules rule-loader doctor --require-pat` (`--with-smoke` for smoke) |
| `eval-run`, `eval-all-models` | `ai-rules rule-loader eval --require-pat` |

Generated files each start with an account guard that stops the run before any change
if the connected `ORGANIZATION-ACCOUNT` differs from `EVAL_ACCOUNT`. `check-bundle`
refuses a bundle whose SQL was edited after generation; if you want to edit the SQL,
run the files with `snow sql` or Snowsight directly instead.

## Lifecycle targets

| Target | Generates |
|---|---|
| `make eval-identity` | Service user and role only |
| `make eval-network-policy EVAL_NETWORK_RULE=DB.SCHEMA.RULE EVAL_ALLOWED_NETWORKS=192.0.2.1/32` | Optional ingress rule and policy |
| `make eval-verify` | Read-only `DESCRIBE`/`SHOW` of the user, grants, policy and token metadata |
| `make eval-pat-create` | Initial PAT (`EVAL_DAYS`) |
| `make eval-pat-rotate` | Rotation with `EVAL_OVERLAP_HOURS` of old-secret overlap |
| `make eval-pat-revoke CONFIRM=1` | Removes the named PAT |
| `make eval-teardown CONFIRM=1` | Drops the user and role; shared policies, rules, databases and warehouses are left alone |

Each is applied with `make eval-setup-apply BUNDLE=... ADMIN_CONNECTION=... ADMIN_ROLE=...`.
Rotation and PAT creation return a secret; handle them as described above.
After rotation, update the credential in your provider and rerun `make eval-check`.

## Manual or custom process

Use this if you run SQL through your own change process or automation. Nothing in the
Makefile is required.

**What the SQL creates (all names configurable):**

| File | Effect |
|---|---|
| `eval_identity.sql` | A `TYPE = SERVICE` user and a role holding only `SNOWFLAKE.CORTEX_AGENT_USER`; sets the user's default role and user-level network policy. Both objects carry `ai-coding-rules:*` comments, and the script refuses to adopt an existing user or role without them. No warehouse, database or administrator grant is included. |
| `eval_network_policy.sql` | Optional. An ingress network rule and policy for approved IPv4 ranges (`/0` is rejected). |
| `eval_pat_create.sql` | `ALTER USER ... ADD PROGRAMMATIC ACCESS TOKEN` with `ROLE_RESTRICTION` and `DAYS_TO_EXPIRY`. |
| `eval_pat_rotate.sql` / `eval_pat_revoke.sql` | Rotate or remove the named token. |
| `eval_verify.sql` | Read-only checks. |
| `eval_teardown.sql` | Drops the project user and role. |

**Requirements:**
- A role that can create users and roles and grant a database role, for example
  `ACCOUNTADMIN` or a delegated administrator role.
- An existing approved network policy, or one created from `eval_network_policy.sql`.
  Snowflake requires a network policy for PAT use unless your account configures a bypass.
- The ability to issue a PAT for the service user (`MODIFY PROGRAMMATIC AUTHENTICATION
  METHODS` when acting for another user) and account policies that allow the requested
  lifetime.
- The user and role must be able to use Cortex Agents in your account.

**Manual steps:**
1. Run `make eval-setup EVAL_ACCOUNT=... EVAL_NETWORK_POLICY=...` to render the SQL, or copy
   the templates in this directory and replace the `__PLACEHOLDERS__`.
2. Review the files. Run them as an administrator with
   `snow sql --connection <admin> --role <role> --filename <file>` or in Snowsight.
3. Verify what matters to you. This project does **not** enforce these; typical checks are
   the user's default role and network policy, the role's grants, and token ownership,
   role restriction and expiry (`SHOW USER PROGRAMMATIC ACCESS TOKENS FOR USER <user>`).
   Do the same before rotating, revoking or tearing down.
4. Register the connection and supply the PAT as in the quick start. For the native
   form: `snow connection add --connection-name <n> --account <org-acct> --user <user>
   --role <role> --authenticator PROGRAMMATIC_ACCESS_TOKEN`.
5. Run `cortex --connection <n>` directly, or `make eval-smoke EVAL_CONNECTION=<n>`.

A separate administrator can run steps 1 to 3 and hand over only the user, role, account
and PAT through your normal secret channel; the evaluating user then performs steps 4 and 5.

## Evaluation notes

The runner uses CoCo CLI stream JSON, not the Agent SDK. Smoke and evaluation cost AI
credits. The default run is one `simple-python-task` pass at low effort and five turns.
`make eval-all-models` is deliberately separate and makes many model calls.
CoCo managed-policy rejections (for example a disallowed authentication method) are
enforced by the CLI before login and must be resolved with the policy owner.

CLI tool-use events supply read evidence; scoring is unchanged. Bash and file mutation
tools are denied. Manifests identify `coco-cli-stream/v1`; reports reject comparisons
mixed with legacy SDK protocols.

## Verification limits

The identity, PAT create, login, rotate, revoke and teardown steps were exercised against
a real account. A multi-hour locked-machine run after SSO session expiry was not
performed; PAT login needs no browser by design. CoCo can reuse a session between
processes, so verify a rotation or revocation with `snow connection test` rather than a
passing CoCo run. See [PAT evaluation](../docs/PAT_EVALUATION.md) for the optional
locked-machine procedure.
