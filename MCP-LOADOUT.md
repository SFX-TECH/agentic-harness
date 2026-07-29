# MCP Loadout

The Model Context Protocol servers I run, and the one rule that governs all of them: prefer the canonical source over the model's memory. Each server is the authoritative source for one kind of truth, loaded on demand so context stays lean.

## The rule
The model's training data lags reality, especially across the seams between vendors. So the harness reaches for the live source: the schema before writing SQL, the installed SDK's types before calling it, the current docs before relying on an API shape. An MCP server turns "I think the API looks like this" into "here is what it actually is."

## The loadout
- **Code intelligence.** A knowledge-graph index of the codebase: who calls what, blast radius before editing a symbol, change scope before a commit. The harness consults it before touching code, so an edit is made with its dependents in view.
- **The workspace hub.** My own local semantic hub over every project (see `WORKSPACE-HUB.md`). Cross-project retrieval, fully local.
- **The knowledge vault.** A personal markdown vault (Obsidian-compatible) served over MCP, distinct from the workspace hub: the hub indexes what the projects are, the vault holds what I have decided and learned in prose. Agents read and write it like any other canonical source.
- **Database.** Schema introspection, migrations, security policies, generated types. The schema is read here before any SQL is written.
- **Deploy and hosting.** Workers, builds, environment, preview deploys, domains. Deploys and their state, driven from the agent.
- **Docs.** Current, version-correct documentation for frameworks and SDKs, fetched on demand instead of recalled.
- **Browser automation.** Drive the real UI in a real browser to verify a deploy end to end, asserting zero console errors against production.
- **Version control and CI.** Repos, pull requests, checks, and a watcher that diagnoses CI failures.
- **Payments, email, and observability.** The billing platform, the transactional email service, and error and product analytics, each wired as the source of truth for its own domain.
- **Automation.** A workflow automation platform for the background jobs that run real operations, authored and validated through its server.
- **Reasoning and filesystem.** A structured-thinking server for multi-step planning, and filesystem access scoped to the work.

## How it is used
Load on demand, not all at once: a server's tools enter context when the task needs them, so the window stays focused. The discipline is the same every time. When the model's memory and the MCP server disagree, the server is right.

## One loadout, two runtimes
The same servers run under both Claude Code and Codex from their respective configs, proven with real tool calls on each side rather than assumed portable (see `codex/` for the translation and the proof transcript). The loadout is a property of the workflow, not of any one vendor's agent.
