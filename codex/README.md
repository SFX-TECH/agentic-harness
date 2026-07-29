# Running the harness on Codex

This adapter was reproduced on Codex CLI 0.143.0, repaired, then exercised end
to end on Windows with Codex CLI 0.146.0 and the configured GPT-5.6 Sol default
on 2026-07-28. All four MCP servers started and handled real tool calls. The
verification also found two adapter assumptions and one CLI-version problem
that can make the setup look broken.

## What actually failed

At reproduction time, the live `C:\Users\jesse\.codex\config.toml` already
contained the four target servers, along with ten other stdio servers. Its
target entries used `cmd /c npx`; the filesystem entry allowed two absolute
SimpleFix paths; no target entry set a startup timeout. The file also set:

```toml
model = "gpt-5.6-sol"
approval_policy = "on-request"
approvals_reviewer = "auto_review"
```

Three different failures appeared during reproduction:

1. **The default model prevented a CLI task from starting.** Codex CLI 0.143.0
   returned:

   ```text
   The 'gpt-5.6-sol' model requires a newer version of Codex. Please upgrade
   to the latest app or CLI and try again.
   ```

   A temporary `gpt-5.4` pin proved that the MCP configuration was independent
   of the model failure. The CLI was then updated from 0.143.0 to 0.146.0.
   An explicit GPT-5.6 Sol task returned `GPT-5.6-SOL-OK`, the live default was
   restored to `gpt-5.6-sol`, and the final four-server proof passed without
   any `-m` model override. The blocker was the old CLI, not model entitlement
   and not the adapter's MCP tables.

   The first `codex update` attempt failed before installation because the
   managed shell did not pass the Windows `OS` environment value to OpenAI's
   installer:

   ```text
   install.ps1 supports Windows only. Use install.sh on macOS or Linux.
   ```

   Running the same official installer with `OS=Windows_NT` scoped to that
   installer process resolved version 0.146.0, verified its checksums, and
   installed it successfully.

2. **The filesystem example allowed only the working directory.** With `.` as
   its only allowed root, the requested outside-workdir read returned:

   ```text
   Access denied - path outside allowed directories:
   C:\Users\jesse\.codex\AGENTS.md not in D:\agentic-harness
   ```

   Adding the exact outside directory as a second server argument made the
   same tool call succeed.

3. **Noninteractive Playwright needed an MCP approval decision.** In an
   isolated `codex exec` run, `browser_navigate` returned
   `user cancelled MCP tool call`, including with `-a never`. A narrow
   `mcp_servers.playwright.tools.browser_navigate.approval_mode = "approve"`
   override made the call succeed without disabling the sandbox. The actual
   user config also succeeded because its existing automatic approval reviewer
   approved the call.

The following suspected causes were ruled out by direct runs:

- `[mcp_servers.NAME]` is the correct table shape in 0.143.0 and 0.146.0.
- `command = "npx"` works directly on this Windows installation. A full path
  and `cmd /c` are not required here.
- stdio transport is inferred for command-based servers.
- the default startup timeout was sufficient. No `startup_timeout_sec` change
  was needed.

One environment trap is worth separating from the adapter. A CLI process
started inside a restricted Codex desktop command sandbox used
`C:\Users\CodexSandboxOffline\.codex` as `CODEX_HOME`, so `codex mcp list`
reported `No MCP servers configured yet.` The same command from the normal
user environment loaded `C:\Users\jesse\.codex\config.toml` and reported 14
enabled stdio servers. Run configuration diagnostics from a normal terminal,
or inspect `codex doctor` and confirm the `config.toml` path it reports.

## Working MCP configuration

Append the four tables from
[`config.toml.example`](config.toml.example) to `~/.codex/config.toml`, keeping
unrelated existing tables. Restart Codex after editing, then run the checks
below.

The base filesystem entry is deliberately project-scoped:

```toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "."]
```

The server denies every path outside the roots in `args`. To allow a second
root, add the exact absolute directory after reviewing its contents:

```toml
args = [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    ".",
    'C:\path\you\intend\to\allow',
]
```

Do not grant a home directory or credential directory merely to make a test
pass. Every child of an allowed root becomes readable through that MCP server.

The isolated `codex exec` proof needed an approval route for browser
navigation. The example approves only the tool used by that proof:

```toml
[mcp_servers.playwright.tools.browser_navigate]
approval_mode = "approve"
```

That setting permits browser navigation without a prompt. Remove it if every
navigation should remain interactive. Do not replace it with
`--dangerously-bypass-approvals-and-sandbox` on a normal workstation.

Check which config Codex loaded and which servers it sees:

```powershell
codex doctor --summary
codex mcp list
```

On the verified machine, `codex doctor --summary` reported
`14 server (14 stdio)`, and `codex mcp list` showed `context7`,
`filesystem`, `playwright`, and `sequential-thinking` as enabled.

## End-to-end proof

The final proof used Codex CLI 0.146.0, the configured `gpt-5.6-sol` default,
no `-m` model override, and JSONL output. Temporary MCP overrides supplied the
public filesystem test root and the narrow Playwright navigation approval. The
tool-call events, not only the final model summary, were checked. All four
operations completed with no MCP failures.

### Context7

Tools called:

```text
context7.resolve-library-id
context7.query-docs
```

Result: React resolved to `/reactjs/react.dev`. The current official
documentation said that an Effect may return a cleanup function, that React
runs cleanup before rerunning an Effect whose dependencies changed, and that
it runs cleanup once more on unmount. Context7 also returned the official
disconnect and stale-async-response examples.

### Filesystem

Tool called:

```text
filesystem.read_text_file
```

The first call, with only `D:\agentic-harness` allowed, produced the exact
access-denied error shown above. The final proof allowed
`C:\Users\Public\Documents` as a second root. Codex then read
`C:\Users\Public\Documents\desktop.ini` from outside the working directory and
returned its first nonempty line:

```text
[.ShellClassInfo]
```

### Sequential thinking

Tool called three times:

```text
sequential-thinking.sequentialthinking
```

Result: the server recorded thoughts 1 through 3 and returned
`nextThoughtNeeded: false` on the third call. The resulting plan was to verify
each server through its own tool surface, include positive and negative
permission cases, capture exact failures, and finish with live browser
navigation.

### Playwright

Tool called:

```text
playwright.browser_navigate
```

Without an approval route, the exact result was:

```text
user cancelled MCP tool call
```

With the per-tool `approval_mode = "approve"` override, the MCP result was:

```text
Page URL: https://example.com/
Page Title: Example Domain
```

The same navigation also succeeded against the actual loaded user config,
where `approvals_reviewer = "auto_review"` was already enabled.

## What ports, and what needs adaptation

| Harness piece | Verified Codex 0.143.0 and 0.146.0 status | Evidence and limit |
|---|---|---|
| Principles and patterns | Ports | A global `AGENTS.md` instruction caused the proof session to read the required prompt architecture file before delegating. Plain instruction text is portable. |
| MCP tool loadout | Ports | All four servers handled real calls. Codex uses `config.toml`, explicit filesystem roots, and MCP tool approval policy. |
| Memory bank files | Ports as data | The Markdown files need no runtime conversion. Automatic creation and startup surfacing are separate capabilities. |
| Sub-agent execution | Ports | `codex features list` reported `multi_agent` stable and enabled. A real `spawn_agent` call read `PRINCIPLES.md` and returned `Verify against canonical source`. The Claude-specific named files in `agents/*.md` were not imported or tested. |
| Skills | Ports with path and content review | Codex attempted to load a user `SKILL.md` during every proof session, and the current manual documents `.agents/skills`. The existing `harness-principles` content is portable. `harness-init` is not drop-in because it uses `CLAUDE_SKILL_DIR`, `CLAUDE_PROJECT_DIR`, `$ARGUMENTS`, `CLAUDE.md`, and `.claude/memory-bank`. |
| Hooks | Codex has an equivalent, but this hook is not ported | `codex features list` reported hooks stable, and the CLI exposes hook trust handling. The repository's Bash `SessionStart` hook uses Claude-specific variables and was not executed by Codex in this verification. |
| Plugin packaging | Codex has a plugin system, but this package is not verified | `codex plugin list` and `codex plugin --help` ran successfully. The Claude plugin in this repository was not installed as a Codex plugin, so this adapter does not claim package-level compatibility. |
| Cross-model review | Method only, not verified here | The review discipline is runtime-independent, but a Codex-to-Claude review invocation was not part of this MCP proof. |

The earlier summary that "the thinking ports, the automation does not" is no
longer accurate for this Codex version. MCP, sub-agent execution, skills,
hooks, and plugins all have runtime surfaces. What does not automatically port
is Claude-specific packaging, paths, variables, named-agent definitions, and
hook scripts. Those pieces require a deliberate Codex package rather than an
instruction to pretend the runtime has no equivalent.

## Other diagnostics observed

Codex 0.143.0 also emitted these unrelated errors while the MCP calls still
completed:

```text
failed to load models cache: missing field `supports_reasoning_summaries`
failed to load skill C:\Users\jesse\.agents\skills\sfx-audit\SKILL.md:
invalid YAML
```

The 0.146.0 update eliminated the model-cache schema error. The invalid
`sfx-audit` skill YAML error still appeared and that skill was skipped. The
0.146.0 run also reported missing authorization for unrelated Figma and Vercel
plugin MCPs; neither affected the four key-free servers verified here.
