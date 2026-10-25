# PAT-backed unattended evaluation

Use a named PAT-backed connection for long-running live evaluations. PAT
authentication does not need an interactive SSO browser, so locking the screen
does not prevent a browser login that would otherwise be needed. This is not a
guarantee of uninterrupted execution: sleep, loss of VPN/network, expired or
revoked tokens, role changes and authentication/network policies can still fail.

## Select a connection

For a new project identity, follow the complete
[user, role, network policy and PAT setup guide](../setup/README.md). It provides
all lifecycle SQL templates, Make helpers and a manual or custom process. Defaults are
`AI_RULES_EVAL_USER`, `AI_RULES_EVAL_ROLE`, `AI_RULES_EVAL_PAT`, and local connection
`ai_rules_eval`; override them with `EVAL_USER` and the other `EVAL_*` Make variables.
`EVAL_ACCOUNT` and `EVAL_NETWORK_POLICY` have no defaults and are required to generate
setup SQL; see the variable table in the setup guide for accepted account formats.

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
that does not verify its signature, expiry, identity or server policies. With an explicit `PROGRAMMATIC_ACCESS_TOKEN` authenticator, `eval-check` only confirms a credential source exists (it cannot validate an opaque token); `eval-smoke` is the real check. Never
replace an SSO connection's credentials or identity silently.

```bash
make eval-check EVAL_CONNECTION=my-pat-connection
make eval-smoke EVAL_CONNECTION=my-pat-connection
make eval-run EVAL_CONNECTION=my-pat-connection EVAL_MODEL=openai-gpt-6-sol EVAL_RUNS=1
make eval-all-models EVAL_CONNECTION=my-pat-connection EVAL_RUNS=5 EVAL_EFFORT=medium EVAL_MAX_TURNS=25
bash scripts/run-eval.sh --connection my-pat-connection --require-pat --effort medium --max-turns 25
```

`eval-check` is metadata-only; smoke/run/all-models spend AI credits. Replace the connection name with
your authorized connection. `--require-pat` rejects interactive or unverifiable
authentication metadata before CLI calls; it never falls back to SSO. Without
the guard, attended SSO remains supported. Explicit `--connection` wins over
`SNOWFLAKE_CONNECTION_NAME`. Named Make workflows default to `ai_rules_eval`;
explicit `EVAL_CONNECTION` (or `setup/eval.local.mk`) selects a different profile. The shell runner uses
the explicit argument or that environment selection, not a hard-coded default.
The selected name reaches the CLI unchanged. Reports remain offline:
`make eval-report` never authenticates, even if a connection is configured.

## Troubleshoot safely

- Missing connection: check its name and configuration, not another identity.
- Interactive-auth rejection: choose an authorized PAT-backed connection.
- Missing or invalid credential: use the supported secret-management workflow,
  then verify a fresh CLI connection with doctor smoke. Do not paste tokens.
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
Its runners pass account/user/password to child environments. This evaluator now
invokes CoCo CLI stream JSON directly, not SDK 1.0.7. Connections are ordinary
`snow connection` entries; the PAT is supplied via `SNOWFLAKE_CONNECTIONS_<NAME>_PASSWORD`
or an approved provider. Provisioning, login, rotation and revocation were exercised against a
real account. Existing authorized client connections remain supported. No API transport is substituted.

The earlier incident in #10 recorded browser SAML timeouts. The current original
connection now has PAT candidate metadata and passed an awake SDK smoke on
2026-10-21 in about 25 seconds. Fresh-process smoke succeeded without an observed
browser prompt. PAT login needs no browser by design, and this project did not run a
multi-hour locked-machine test. If you want one, do not infer it from an awake smoke or
a brief screen lock; use the procedure below.

## Optional locked-machine test

The failure this guards against is a browser login required after the SSO session
expires (typically a couple of hours) while the machine is locked. Locking for a few
minutes proves nothing, because the session is still valid. Each fixture run starts a
fresh `cortex` process, so what matters is that a run **started after expiry** needs
no browser.

1. Run `make eval-smoke` and note the time (this is the last interactive point).
2. Start a delayed run that outlasts your session lifetime, then lock the machine.
   Keep it on power and awake; `caffeinate -i` stops idle sleep but still lets the
   screen lock. Use a wait longer than your session expiry (for example 3 hours):

   ```bash
   caffeinate -i sh -c 'sleep 10800; make eval-run > .workbench/locked-run.log 2>&1; echo "exit=$?" >> .workbench/locked-run.log'
   ```

3. After the wait, unlock and read `.workbench/locked-run.log`. The test passes if the
   run finished with `exit=0` and a passing fixture, and no browser window or SSO prompt
   appeared. A hang or `exit` other than 0 fails it; keep the log for the report.
4. Confirm from Snowflake that a new login happened. CoCo can reuse a session between
   processes, so a passing run alone does not show the PAT was used. As an administrator:

   ```sql
   SELECT EVENT_TIMESTAMP, IS_SUCCESS, FIRST_AUTHENTICATION_FACTOR, ERROR_MESSAGE
   FROM TABLE(SNOWFLAKE.INFORMATION_SCHEMA.LOGIN_HISTORY_BY_USER(
     USER_NAME => 'AI_RULES_EVAL_USER',
     TIME_RANGE_START => DATEADD('hour', -6, CURRENT_TIMESTAMP())))
   ORDER BY EVENT_TIMESTAMP DESC;
   ```

   Expect a successful `PROGRAMMATIC_ACCESS_TOKEN` login at the time the delayed run began.
5. Optional control: do the same with an `externalbrowser` connection to confirm the
   environment reproduces the original failure.

## Checking rotation and revocation

A running or recently used CoCo session can keep working after its token is rotated or
removed, because Snowflake does not end existing sessions and CoCo may reuse one. Test
the credential itself with a fresh login from the Snowflake CLI, using the same
exported secret:

```bash
snow connection test --connection <name>
```

After revoking, expect `Programmatic access token is invalid`. After rotating with no
overlap, the previous secret fails the same way and the new one succeeds.

References:

- [Snowflake PAT authentication](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens)
- [Python connector named connections](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect)
- [Cortex Code configuration](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
