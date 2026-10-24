# PAT-backed unattended evaluation

Use a named PAT-backed connection for long-running live evaluations. PAT
authentication does not need an interactive SSO browser, so locking the screen
does not prevent a browser login that would otherwise be needed. This is not a
guarantee of uninterrupted execution: sleep, loss of VPN/network, expired or
revoked tokens, role changes and authentication/network policies can still fail.

## Select a connection

For a new project identity, follow the complete
[user, role, network policy and PAT setup guide](../setup/README.md). It provides
all lifecycle SQL templates and a preview-only command. Defaults are
`AI_RULES_EVAL_USER`, `AI_RULES_EVAL_ROLE`, `AI_RULES_EVAL_PAT`, and local connection
`ai_rules_eval`; override the user with `--user` or `AI_RULES_EVAL_USER`.

Configure an authorized named connection using your supported Snowflake client
and secret-management workflow. Keep credentials outside this repository; do not
put a token in command arguments, shell history, reports or examples. In Cortex
Code, `/secrets` is the supported interface for supplying secrets to agent-run
commands. A stored secret alone does not configure a named CLI connection.

Use an existing named connection that your CLI can authenticate with. Connection
metadata must explicitly identify account and user. PAT credentials are supplied
in the client's password slot, with explicit `PROGRAMMATIC_ACCESS_TOKEN`
authentication where supported, or the default `snowflake` authenticator with a
PAT password. The guard accepts a JWT-shaped password as a local PAT candidate;
that does not verify its signature, expiry, identity or server policies. Never
replace an SSO connection's credentials or identity silently.

```bash
make eval-doctor CONNECTION=my-pat-connection CLI_ARGS="--require-pat --with-smoke"
make eval-live CONNECTION=my-pat-connection CLI_ARGS="--require-pat --fixture simple-python-task --runs 1 --model openai-gpt-6-sol"
make eval-all-models CONNECTION=my-pat-connection CLI_ARGS="--require-pat --runs 5 --effort medium --max-turns 25 --concurrency 3 --retry-infra 2"
bash scripts/run-eval.sh --connection my-pat-connection --require-pat --effort medium --max-turns 25
```

These are live operations and spend AI credits. Replace the connection name with
your authorized connection. `--require-pat` rejects interactive or unverifiable
authentication metadata before SDK calls; it never falls back to SSO. Without
the guard, attended SSO remains supported. Explicit `--connection` wins over
`SNOWFLAKE_CONNECTION_NAME`. Make requires `CONNECTION`; the shell runner uses
the explicit argument or that environment selection, not a hard-coded default.
The selected name reaches the SDK/CLI unchanged. Reports remain offline:
`make eval-report` never authenticates, even if a connection is configured.

## Troubleshoot safely

- Missing connection: check its name and configuration, not another identity.
- Interactive-auth rejection: choose an authorized PAT-backed connection.
- Missing or invalid credential: use the supported secret-management workflow,
  then verify a fresh SDK connection with doctor smoke. Do not paste tokens.
- Expired, revoked or rotated PAT: coordinate renewal with its owner. A token
  can be valid locally yet rejected by server policy or a revoked role.
- Network/authentication policy: ask the administrator to verify requirements;
  do not bypass policies or change grants as an automatic recovery step.
- Sleep or VPN loss: keep the runner awake and connected. PAT authentication
  avoids interactive login, not connectivity or machine lifecycle failures.

Role-restricted PATs use their restricted role; secondary-role assumptions from
an SSO session may not apply. Check required Cortex permissions with the owner.
Token lifetime and rotation are subject to account policy, not this tool.

## Comparison with harness-eval-bench

The harness's `bench_eval` connection uses a dedicated PAT-backed identity.
Its runners pass account/user/password to child environments and resolve an
inference token separately. This evaluator already forwards a named connection
through SDK 1.0.7 to the CLI, so no credential bridge is needed. This project
does not copy the harness's shell `eval` exports, token-file fallback, provisioning
or identity switching. It preserves supported connection configuration.

The earlier incident in #10 recorded browser SAML timeouts. The current original
connection now has PAT candidate metadata and passed an awake SDK smoke on
2026-10-21 in about 25 seconds. Fresh-process smoke succeeded without an observed
browser prompt. Locked-screen execution and long-session token renewal have not
been verified; do not infer either from the awake smoke. Coordinate a locked-screen
test while the machine remains awake/online before claiming that acceptance check.

References:

- [Snowflake PAT authentication](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens)
- [Python connector named connections](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect)
- [Cortex Code configuration](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
