# Running the harness on Codex

> **In plain terms:** The plugin in this repo installs into Claude Code. Codex (OpenAI's coding CLI) is a different runtime with a different config format, so the plugin does not install there. What ports is everything that matters: the principles, the discipline, and the tool loadout. This folder is the Codex-side setup, plus an honest list of what does not carry over.

The harness is two things stacked. Underneath are the **principles and discipline**, which are runtime-agnostic and port to any coding agent. On top is the **packaging**, which is Claude Code specific. Only the packaging fails to port.

Verified on Codex CLI 0.143.0, Windows, 2026-07-27.

---

## What ports, and what does not

| Harness piece | Claude Code | Codex | Notes |
|---|---|---|---|
| Principles and patterns | plugin skills | `AGENTS.md` | Ports fully. Same text, different delivery. |
| MCP tool loadout | `.mcp.json` | `config.toml` | Ports, but the format differs. Conversion below. |
| Memory bank (durable context) | `/harness-init` scaffolds it | copy `templates/` by hand | The files are plain markdown. Only the scaffolder is Claude-specific. |
| Sub-agent fleet | `agents/*.md` | no direct equivalent | Codex has no first-class named sub-agent registry. Express the same decomposition inside the task prompt instead. |
| Skills (auto-triggered) | `skills/*/SKILL.md` | no direct equivalent | Fold the load-bearing ones into `AGENTS.md` so they are always in context rather than triggered. |
| SessionStart hook | `hooks/hooks.json` | no direct equivalent | Run the same script manually, or have the first prompt ask for the state it would have surfaced. |
| Cross-model review gate | calls Codex from Claude | calls Claude from Codex | Ports, and inverts cleanly. The point is a reviewer of different lineage, whichever side you start from. |

The honest summary: **the thinking ports, the automation does not.** On Codex you get the same discipline with more of it carried by the prompt and less by the runtime.

---

## 1. The MCP loadout in Codex format

Claude Code reads `.mcp.json`. Codex reads `~/.codex/config.toml` and uses TOML tables. Same four servers, same purpose, no API keys:

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]

[mcp_servers.sequential-thinking]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-sequential-thinking"]

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "."]

[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
```

Append that to `~/.codex/config.toml`, keeping any blocks already there.

Two differences worth knowing. Claude Code expands `${CLAUDE_PROJECT_DIR}` for the filesystem server's root; Codex has no equivalent variable, so pass `.` and launch from the project directory, or hardcode an absolute path. And if a server is slow to start on your machine, Codex accepts `startup_timeout_sec` inside the server's table, which Claude Code does not need.

All four packages were confirmed live on npm and one was confirmed starting on stdio during verification.

---

## 2. The principles, as `AGENTS.md`

Codex reads `~/.codex/AGENTS.md` globally and an `AGENTS.md` at a project root for project scope. That is the natural home for what the plugin delivers as skills.

Copy [`PRINCIPLES.md`](../PRINCIPLES.md) in, then add the operating rules the plugin would otherwise enforce automatically. At minimum:

```markdown
## Operating discipline

- Verify against canonical source, never model memory. Read the real file, the
  live schema, the installed SDK, before relying on any claim about them.
- Never report a result you did not produce. If a command did not run, say so.
  No invented test counts, no assumed gate verdicts.
- One orchestrator, sequential sub-tasks. Decompose, do each piece, integrate.
  Do not fan out work that will collide.
- Audit before building on anything substantial: find the drift while it is
  still cheap.
- Mechanize safety. If a rule matters, put it in a test or a gate rather than
  relying on it being remembered.
- Measure the output rather than opining about it. See QUALITY-GAUGE.md.
```

Those exist as auto-triggering skills in the Claude plugin. On Codex they are always-on context, which is arguably stronger and definitely more token-hungry.

---

## 3. The memory bank

Identical on both runtimes, because it is just markdown. Copy [`templates/`](../templates/) into your project and keep the three files doing their distinct jobs: `decisions.md` append-only, `active-context.md` replaced not appended, `progress.md` chronological. Point `AGENTS.md` at them so every Codex session reads them first.

The only loss is the `/harness-init` scaffolder and the SessionStart hook that surfaces state automatically. Both are convenience, not substance.

---

## 4. Cross-model review, which is the piece that gets better

The [cross-model review](../plugins/agentic-harness/skills/cross-model-review/SKILL.md) skill has Claude call Codex to review a diff before commit. Running the harness on Codex simply inverts it: Codex writes, Claude reviews.

Do not skip this because both are strong models. The value is **lineage, not capability**. In production use, a same-family reviewer repeatedly missed defects that a different-lineage reviewer caught, including a privilege-escalation path in code that had already passed several rounds of same-family review. Reviewers share blind spots with the models they came from.

---

## Verification status

Checked on 2026-07-27 rather than assumed:

- Codex CLI 0.143.0 present, `~/.codex/config.toml` confirmed using `[mcp_servers.NAME]` TOML tables and `~/.codex/AGENTS.md` confirmed as the instruction file.
- All four MCP packages resolve on npm at current versions.
- One server confirmed starting on stdio.
- The Claude Code SessionStart hook confirmed executing on Windows and reporting correct git state.

What has **not** been verified end to end: a full Codex session running with this loadout on a real task. If you do that, record the result here rather than assuming it works.
