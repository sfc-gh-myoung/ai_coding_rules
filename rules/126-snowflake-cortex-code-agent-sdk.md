---
schema_version: v4.0
rule_version: v3.1.0
description: "Version-grounded Cortex Code SDK sessions, terminal/structured output, bounded costs, tool confinement, hooks and private MCP integration."
last_updated: 2026-10-08
keywords:
  - kw:cortex-code-agent-sdk
  - kw:agent lifecycle hooks
  - kw:canUseTool permission callback
  - kw:streaming partial messages
  - kw:multi-turn session management
  - kw:structured output json schema
token_budget: ~1700
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
  optional:
    - 115-snowflake-cortex-agents-core.md  # Server-side `CREATE CORTEX AGENT` DDL agents
    - 117-snowflake-mcp-server.md  # Snowflake-managed MCP server (different scope)
    - 118-snowflake-cortex-rest-api.md  # REST clients without the SDK
---
# Snowflake Cortex Code Agent SDK Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Essential SDK session and tool-authority contract; preserve while building SDK applications.

## Scope

**What This Rule Covers:**
TypeScript/Python Cortex Code SDK and CLI subprocess lifecycle, prompts, permission/hooks/MCP boundaries, streaming, structured outputs, and reproducible tests.

**When to Load This Rule:**
When using cortex-code-agent-sdk, query/session clients or Cortex CLI subprocesses. Read `115-snowflake-cortex-agents-core.md` for server-side agents, `117-snowflake-mcp-server.md` for managed MCP, or `118-snowflake-cortex-rest-api.md` for REST-only clients; these are different interfaces.

## Contract

### Inputs and Prerequisites

- Existing application/build/config and actual SDK/CLI versions, supported runtime and CLI path, connection/role, working directory and session state.
- Approved model/transmission/budget, exact tool/argument/path/host/SQL scope, profile/settings context and credential mechanism.
- Input pattern, output schema, terminal/failure policy, deadlines/cancellation, cleanup, and existing immutable test evidence.

### Mandatory

- Inspect installed SDK/CLI options and current reference before writing code; Python snake_case and TypeScript camelCase APIs differ. Package installation, configuration creation, account calls and paid probes need approval; do not read credential values merely to test existence.
- Set connection/cwd and desired model explicitly. auto is a selection policy, not a pinned model identity; record requested selector and observed model separately. Record versions/context/settings for repeatable evaluations, without asserting preview/GA status from stale text.
- Use query for one-shot work, persistent createCortexCodeSession/CortexCodeSDKClient for multi-turn context under current signatures. Close/disconnect via supported resource managers/finally; don't leak CLI subprocesses on errors, cancellation or premature iteration exit.
- Prefer preset-plus-append to retain default tool guidance. Replacing prompts requires deliberate acceptance of lost guidance; prompts alone are not enforceable permission controls. Keep secrets and unnecessary confidential content out of model prompts and logs.
- Bound turns, wall time, token/effort settings where supported, cancellation and spend. max_turns/effort isn't a guaranteed dollar ceiling; record reported versus unavailable usage. Timeouts/max-turn errors are real failed/interrupted outcomes, not hidden retries.
- Dispatch typed complete assistant/user/tool/result messages and partial StreamEvents. Partial text/thinking deltas are not tool execution/results or terminal success; do not expose thinking or render complete content twice. Structured output can arrive only in the terminal result.
- Require an actual terminal ResultMessage and inspect is_error/subtype plus required output checks. EOF, clean trace, some text or absence of an exception is not completion. Validate structured_output with the same JSON schema and consumer type parser; empty valid outputs must not be rejected solely by truthiness.
- Use default-deny policy for actual reachable tools, arguments, resolved paths/symlinks, hosts, object/SQL effects and caller authority. A read tool can exfiltrate secrets; read-only SQL can call side-effectful functions. Tool names alone and destructive-command regexes aren't sufficient confinement.
- allowedTools/disallowedTools or permission mode may resolve requests before canUseTool/can_use_tool. The callback governs permission events reaching it, not a guaranteed audit of every call. Avoid broad auto-allow rules when per-call checks are required; PermissionRequest hooks are another documented path, not universal enforcement.
- Do not enable bypassPermissions in production/user-facing paths. Its safety flag only permits selecting bypass; it doesn't create a sandbox. Test fail-closed behavior across direct calls, wrappers/batches, MCP dispatch and subprocess routes.
- PreToolUse/hook denial must be verified before effects, especially nested direct-tool wrappers. Enforce in-process MCP operations again at the actual dispatcher with reconciled request/decision/result audit when confinement requires it; a denied outer wrapper isn't proof nested calls didn't execute.
- Hooks must return current documented output shapes within explicit bounded time. Distinguish observational PostToolUse from preventive authorization and preserve failures. No unknown hook/event/output field, indefinite approval wait or unreviewed post-hook side effect.
- Treat MCP configuration as executable authority: approve command/args/env/remote host and capabilities; do not pass untrusted user strings to shell/extra_args/headers or install on launch. Inject credentials only to approved consumers and keep logs redacted; env availability alone doesn't protect secrets from agent tools.
- Validate effective settings/profile context rather than assuming setting_sources=[] isolates all ambient skills/configuration. Record actual startup/tool manifests and denied calls; inventory availability is not invocation. Do not patch global SDK/CLI or retry frozen benchmark IDs to hide failure.
- For immutable evaluations freeze prompt/rule/adapter/runtime bytes, distinct attempt IDs, requested/observed models and output criteria. Source changes require a new epoch; interrupted/unpaired/denied traces stay failures or gaps, never substitute passes. Clean traces require separate output/safety review.

### Execution Steps

1. Read actual application/runtime and SDK docs; establish session/input/output, model/data authority and reachable tool/settings boundaries.
2. Implement minimal typed session lifecycle, prompt, schema, bounded deadlines and fail-closed permission/dispatch policy.
3. Test local fixture terminal/error/schema/cancellation/hook/nested-route cases before separately approved model/service calls.
4. Run approved bounded canaries with actual trace/model/context receipts; review terminal output and effects independently.
5. Close sessions and reconcile subprocess/tool/usage evidence; report observed compatibility, failures and unverified controls without rewriting old evidence.

### Validation

- Current typed APIs build/typecheck/import with existing dependencies; no guessed runtime or unapproved install/configuration.
- Complete messages/terminal errors and schema output are handled; cleanup works after cancellation and failures.
- Effective allow/deny covers arguments and dispatch paths, including nested/MCP effects, and permissions aren't silently bypassed.
- Context/model identities, resource budgets, secrets/transmission and immutable attempt accounting are explicit.
- Output includes implementation/configuration, fixture versus live evidence and remaining gaps. Clean traces or non-error result alone do not prove task correctness.

## References

- [SDK Python API](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/python-reference)
- [SDK TypeScript API](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/typescript-reference)
- [Permission rules and callbacks](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/user-input)
- [Hooks](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/hooks)
- [Streaming messages](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/streaming-output)
- [Structured output](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/structured-output)
- [MCP integration](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/mcp-custom-tools)
