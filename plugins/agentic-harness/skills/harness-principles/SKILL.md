---
name: harness-principles
description: The operational principles of the agentic harness, for deciding how to approach a non-trivial change. Verifying against canonical source, mechanized over remembered safety, architectural pre-work, one-orchestrator sub-agent discipline, and discipline as the pace enabler.
---

These are the load-bearing principles of the harness. Apply them when planning or executing a non-trivial change.

1. **Verify against canonical source.** Documentation states intent; source code, the live schema, and the API state describe behavior. When they disagree, behavior wins. Read the real thing before relying on it: the installed SDK's types, the live schema before SQL, the current docs before an API shape, the actual file before trusting a description of it.

2. **Mechanized safety over remembered safety.** A rule a human has to remember fails under fatigue and at scale. Move it into a test, a gate, a guard, or a type so it cannot be forgotten. A required check is worth more than a careful habit.

3. **Architectural pre-work pays back in iteration count.** Surfacing a consequential decision before writing the code costs minutes; surfacing it mid-build costs iterations. Decide first. Run the pre-work audit before the code, not after the rework.

4. **One orchestrator, sequential sub-agents.** Decompose the work, delegate bounded pieces with tight specs, integrate the results, and own the judgment calls yourself. A swarm that all writes at once is a merge conflict and a rate-limit wall waiting to happen. When a sub-agent is interrupted, verify its work against the real file state and complete the remainder; never trust its report alone.

5. **Discipline is the pace enabler, not its enemy.** The intuition that process slows shipping is wrong at real complexity. The audits and gates catch problems at the cheapest moment, which is exactly what lets the work move fast. Bank every consequential decision, dated, with its rationale, before the code that implements it.

When the work outgrows a single context window, treat the memory bank as the project's durable brain: decisions.md (append-only, the architectural spine), active-context.md (this week only, replaced not appended), progress.md (chronological shipped log).
