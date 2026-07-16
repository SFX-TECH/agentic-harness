# Agentic Harness (Claude Code plugin)

The installable form of [Jesse Jolly's](https://jessejolly.com) agentic engineering harness: the control system around coding agents that ships and operates production software. Durable context, one orchestrator plus sequential sub-agents, and verify-against-canonical-source gates, dropped straight into your Claude Code.

Built by **Jesse Jolly** of [SFX Tech Innovation](https://sfxtechinnovation.com). The products built with this harness are private; the harness is open source under MIT.

## Install

```
/plugin marketplace add SFX-TECH/agentic-harness
/plugin install agentic-harness@sfx-harness
```

Then `/reload-plugins` (or restart Claude Code).

## What you get

**MCP loadout** (auto-starts on install, all key-free, launched via npx):

- `context7`: current, version-correct framework and SDK docs, on demand
- `sequential-thinking`: structured multi-step planning
- `filesystem`: scoped to your project
- `playwright`: drive a real browser to verify a deploy end to end

Claude Code's built-in WebFetch and WebSearch cover web access. GitHub and project-specific servers (your database, deploy platform, payments, email) are easy adds: `claude mcp add ...` or a project `.mcp.json`.

**Sub-agents** (`/agents`):

- `code-reviewer`: the verification gate. Run before any merge.
- `block-0-auditor`: the pre-work audit. Run before writing code for a non-trivial change.
- `memory-bank-curator`: the maintenance partner. Run at the end of a meaningful session to propose memory-bank updates.
- `ci-watcher`: watch an open PR's CI, diagnose a failure from the real logs, and propose a fix. Uses the gh CLI, no GitHub MCP token needed.
- `advisor`: the independent verifier and prompt-writer that pairs with a worker session. Never edits; verifies every load-bearing claim against ground truth (git, live artifacts, real data), then writes the next session's brief. The prompt is the output of verification, never the start of it.

**Skills:**

- `/harness-init`: scaffold a `CLAUDE.md` bootstrap and a memory bank (decisions, active context, progress) into your current project.
- `harness-principles`: the operational principles, available to your agent when it plans non-trivial work.
- `/closure-synthesis`: at the end of a meaningful change, close the loop on the memory bank (append progress, replace active context, bank decisions, surface observations). The ritual that keeps the bank alive.
- `/phase-gate-check`: before declaring a phase or release complete, run the exit criteria against the build, tests, and deploy. Refuses to close on red.
- `/bank-observation`: record a reusable lesson with the second-instance promotion gate (a candidate on first sight, a numbered observation on recurrence).
- `/house-style-guard`: mechanize a project's house-style or content rules into a guard that fails on violation, Principle #3 applied to your own copy.
- `cross-model-review`: run a second vendor's coding model as a read-only adversarial reviewer over the staged diff, and keep re-reviewing the updated bundle until it converges or hits the tripwire. The model that wrote the code shares its own blind spots; this gate does not.
- `no-api-spend`: a hard cost guardrail. No code the agent writes may call a paid API without stating volume, estimated cost, and getting explicit approval first. Covers scripts, subagents, batches, and packages that phone home on your key.
- `safe-mutation-loop`: the contract for an agent that mutates real state: gate against a policy allowlist, snapshot before, execute with exit codes checked, verify with evidence, declare honest undo coverage, and classify every action into three autonomy tiers (silent / auto-revert / human-gate).
- `local-api-hardening`: the threat-model checklist for a localhost API behind a desktop app or dev tool. Loopback is a neighborhood, not a vault: every mutation route authenticated, timing-safe comparisons, deny-by-default CORS, tokens never persisted or logged.
- `verify-before-writing`: the anti-hallucination probe. Before writing code against a schema, route, or signature not verified this session, look at the real one (a column probe, a route probe; a 401 means alive-wants-auth, a 404 means not-there).

**Hooks:**

- `SessionStart`: surfaces the project's memory-bank presence and git freshness at the start of every session, so work never begins on stale state. Read-only, never blocks.

## Use it

1. In a project, run **`/harness-init`** to scaffold the harness, then fill in `CLAUDE.md` with your real stack, locked decisions, and current state.
2. Keep the memory bank current. It is the project's durable brain across sessions.
3. Run **`block-0-auditor`** before non-trivial work and **`code-reviewer`** before merging. Close meaningful work with **`/closure-synthesis`**, and gate a phase or release with **`/phase-gate-check`**.
4. Make it yours.

## Customize

Everything is overridable; this is a starting point, not a cage.

- **Edit an agent or skill:** drop a file of the same name in your project's `.claude/agents/`, `.claude/skills/`, or `.claude/commands/` (or the `~/.claude/` equivalents). Your version wins over the plugin's.
- **Add or remove MCP servers:** add your own with `claude mcp add ...` or a project `.mcp.json`. The bundled set is just the universally-useful baseline.
- **Disable or remove the plugin:** `/plugin disable agentic-harness@sfx-harness` or `/plugin uninstall agentic-harness@sfx-harness`.
- **Fork locally:** clone the repo and run Claude Code with `--plugin-dir ./plugins/agentic-harness` to customize before re-publishing.

## The methodology behind it

The full principles, patterns, and templates live in the [repo root](https://github.com/SFX-TECH/agentic-harness): `PRINCIPLES.md`, `PATTERNS.md`, `CONTEXT-AS-CODE.md`, `MCP-LOADOUT.md`, and `templates/`. This plugin is that harness, made installable.

MIT licensed. Take what is useful, make it yours.
