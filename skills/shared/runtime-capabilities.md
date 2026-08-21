# Runtime Capabilities

This contract defines the runtime vocabulary used by skill producer contracts.
It distinguishes a runtime's capabilities from its installation target.
`TargetPlatform` remains the plugin installation vocabulary: `cortex` or
`claude`.

## Runtime IDs

| Runtime ID | Status | Capability IDs | Required fallback |
|---|---|---|---|
| `cortex-code` | supported | `subagents`, `tools`, `mode-switching`, `user-questions` | None |
| `claude-code` | supported | `subagents`, `tools`, `user-questions` | Run directly when mode switching is unavailable. |
| `unsupported` | unsupported | None | Stop with a terminal runtime-unsupported error. |

## Capability IDs

- `subagents`: The runtime can delegate bounded work to a named worker and receive its result.
- `tools`: The runtime can invoke the tools named by a skill contract.
- `mode-switching`: The runtime can change between planning and execution modes.
- `user-questions`: The runtime can collect structured user answers before execution.

## Producer Rules

1. A producer may request only the capability IDs declared for its runtime ID.
2. A producer requiring a missing capability must take the runtime's documented fallback.
3. An `unsupported` runtime is terminal. It must not fabricate a tool, agent, mode, or question capability.
4. Runtime attestation belongs only to the final loader coordinator. Matcher and semantic artifacts must not contain it.

## Fixture Contract

The runtime fixtures in `tests/fixtures/runtime_capabilities/` use this shape:

```json
{
  "runtime_id": "cortex-code",
  "status": "supported",
  "capability_ids": ["subagents", "tools", "mode-switching", "user-questions"],
  "fallback": null
}
```

Fixture files are test inputs, not generated project artifacts. Generated
execution evidence remains under `.snowflake/cortex/`.
