# <Project>: Codex session bootstrap

This file is loaded by Codex sessions in this workspace. Keep it short. Long-form context lives in the memory-bank files below. Before non-trivial work, read each file that exists so a new session starts from current decisions and state.

## Durable context
- `.memory-bank/decisions.md`: append-only architectural decisions and rationale
- `.memory-bank/active-context.md`: current state and immediate constraints
- `.memory-bank/progress.md`: chronological shipped-work log

---

## Quick reference
- **Workspace:** <path>
- **Stack:** <languages, frameworks, runtime, data layer, deploy>
- **MCPs configured:** <list; see MCP-LOADOUT.md>
- **Skills / sub-agents:** <the codified procedures and sub-agents this project uses>
- **Prospective evidence contract:** <none, or the project-local policy/runbook path>

## Behavioral defaults
- Verify against canonical source before relying on it: read the live schema, the installed SDK types, the real API state. Behavior beats docs.
- Every new tenant table ships its isolation test in the same commit. No exceptions.
- Every consequential decision is banked in `decisions.md`, dated, with rationale, before the code that implements it.
- No invented metrics. Tag self-measured numbers as self-measured.
- If a prospective evidence contract is configured, assess each new version-controlled code task before outcome-bearing exploration. Start eligible units prospectively, retain real verification failures, and finish every unit truthfully. A maturity floor is not a collection ceiling; a controlled experiment keeps its own preregistered sample cap and lifecycle.
- <house-style rules, for example: no em-dashes in user-facing copy>

## Tooling invocation defaults
- Use the code-intelligence MCP to check blast radius before editing a symbol.
- Use the database MCP to read the schema before writing SQL.
- Use the docs MCP for current SDK and framework behavior instead of recalling it.
- Invoke a code-reviewer sub-agent before any merge.

## Anti-patterns to avoid
- Reaching for the model's memory when an MCP can give current truth.
- Writing code before banking the decision it implements.
- A swarm of sub-agents all writing at once. One orchestrator, sequential delegation.
- Treating an observational maturity threshold as a stopping rule, or mixing ordinary longitudinal units into a controlled cohort.
- Closing a phase without running its phase-gate check.
