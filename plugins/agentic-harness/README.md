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

**Skills:**

- `/harness-init`: scaffold a `CLAUDE.md` bootstrap and a memory bank (decisions, active context, progress) into your current project.
- `harness-principles`: the operational principles, available to your agent when it plans non-trivial work.

## Use it

1. In a project, run **`/harness-init`** to scaffold the harness, then fill in `CLAUDE.md` with your real stack, locked decisions, and current state.
2. Keep the memory bank current. It is the project's durable brain across sessions.
3. Run **`block-0-auditor`** before non-trivial work and **`code-reviewer`** before merging.
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
