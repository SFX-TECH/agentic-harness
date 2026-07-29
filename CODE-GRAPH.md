# The Code Graph

> How the agent knows who calls what before it edits anything.

> **In plain terms:** By default a coding agent navigates a codebase the way a stranger does: text search. It finds the function it wants to change, but not the twelve places that depend on it. A code graph is a pre-built map of every symbol and every relationship in the repo, so the agent can ask "what breaks if I change this?" and get an answer from the map instead of a guess.

The graph I run is [GitNexus](https://github.com/abhigyanpatwari/GitNexus): a local index of every function, class, and call relationship, exposed to the agent over MCP. On my main product it currently holds 21,282 symbols, 36,122 relationships, and 295 traced execution flows. Indexing is one command, and the index never leaves the machine.

## The two rules that make it a discipline

A graph nobody consults is furniture. Two rules in the project's context file make it load-bearing:

1. **Impact analysis before editing any symbol.** Before the agent modifies a function it runs the blast-radius query: direct callers, execution flows it participates in, risk level. High risk gets surfaced to me before the edit, not after.
2. **Change detection before committing.** The agent diffs the graph, not just the files, to verify the change touched only the symbols it intended to touch.

Renames go through the graph too, never find-and-replace. The graph knows the call sites; a regex only knows the spelling.

## Freshness is the whole game

A stale graph is worse than no graph, because it answers confidently from the past. A post-commit hook checks index freshness and tells the agent to reindex when it drifts. The rule generalizes past graphs: any derived artifact an agent trusts needs an automatic staleness signal, or it becomes a well-organized lie.

## What it buys, honestly

Navigability, not quality. The graph collapses the understanding-debt problem: the agent stops re-deriving the architecture every session and starts from the map. Whether the code is any good is a separate question, and that is what [QUALITY-GAUGE.md](QUALITY-GAUGE.md) measures. I keep those two claims apart on purpose, because the published evidence supports the first and only the gauge can support the second.

One optional layer earns its keep for security-sensitive code: the program-dependence build adds source-to-sink taint flows, which turns "review this for injection" from a reading exercise into a query.
