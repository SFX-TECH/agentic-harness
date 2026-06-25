# <Project>: session bootstrap

This file is auto-loaded by every coding-agent session in this workspace. It inlines the memory bank so every session starts with current decisions and state, no matter how long since the last one. Keep it short. Long-form context lives in the files this points at.

## Locked decisions (the spine)
@.memory-bank/decisions.md

## Current state
@.memory-bank/active-context.md

## Progress log
@.memory-bank/progress.md

---

## Quick reference
- **Workspace:** <path>
- **Stack:** <languages, frameworks, runtime, data layer, deploy>
- **MCPs configured:** <list; see MCP-LOADOUT.md>
- **Skills / sub-agents:** <the codified procedures and sub-agents this project uses>

## Behavioral defaults
- Verify against canonical source before relying on it: read the live schema, the installed SDK types, the real API state. Behavior beats docs.
- Every new tenant table ships its isolation test in the same commit. No exceptions.
- Every consequential decision is banked in decisions.md, dated, with rationale, before the code that implements it.
- No invented metrics. Tag self-measured numbers as self-measured.
- <house-style rules, for example: no em-dashes in user-facing copy>

## Tooling invocation defaults
- Use the code-intelligence MCP to check blast radius before editing a symbol.
- Use the database MCP to read the schema before writing SQL.
- Use the docs MCP for current SDK and framework behavior instead of recalling it.
- Invoke the code-reviewer sub-agent before any merge.

## Anti-patterns to avoid
- Reaching for the model's memory when an MCP can give current truth.
- Writing code before banking the decision it implements.
- A swarm of sub-agents all writing at once. One orchestrator, sequential delegation.
- Closing a phase without running its phase-gate check.
