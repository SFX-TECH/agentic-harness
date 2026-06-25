# Principles

The principles I bank as I build. Each one was earned from a real failure or a real win, then generalized so it applies anywhere. The list grows; these are the load-bearing ones.

## 1. Verify against canonical source
Documentation states intent. Source code, the installed SDK's type definitions, the live database schema, and the actual API state describe behavior. When intent and behavior disagree, and across vendor seams they often do, behavior wins. Read the real thing before you rely on it. The cost of verifying is minutes; the cost of trusting a doc that lags reality is hours of debugging. This is the most-applied principle in my work, by a wide margin.

## 2. Truthful by design
Never claim a number you did not measure. Tag every self-measured figure as self-measured. For anything that touches a person's machine, money, or data, make no claim you cannot prove: no cure-rate without before-and-after evidence, no test count you did not run. When verifying a system, build the evidence ledger first and let it classify each result as proven, failed, or inconclusive. Trustworthiness is the product, not the marketing around it.

## 3. Mechanized safety over remembered safety
A rule a human has to remember fails at 11pm, under fatigue, or when a new contributor never heard it. Move the rule into a test, a CI gate, a guard clause, a type, or a database constraint, so it cannot be forgotten. Discipline that depends on vigilance does not scale; discipline that is mechanized does.

## 4. Architectural pre-work pays back in iteration count
Surfacing a consequential decision before writing the code costs minutes. Surfacing it mid-build costs iterations, each one a full cycle of write, fail, diagnose, redo. Decide first. The pre-work feels like overhead and is actually the cheapest iteration you will ever run.

## 5. One orchestrator, sequential sub-agents
Decompose the work, delegate bounded pieces to sub-agents, integrate the results yourself, and own every judgment call. Resist the swarm: many agents writing at once is a merge conflict and a rate-limit wall waiting to happen. Sequential orchestration is slower on paper and faster in practice, because it does not spend half its time colliding with itself. When a sub-agent is interrupted, the orchestrator finishes its remainder rather than restarting it.

## 6. Discipline is the pace enabler
The intuition that process slows shipping is wrong at real complexity. Audits, gates, and verification catch problems at the cheapest possible moment, before code is written or before it merges, instead of in production. The discipline is what lets the work move fast and stay shipped.

## 7. Security invariants are tested, not trusted
In a multi-tenant system, isolation is the one thing that can never regress. So it is mechanized: every tenant table gets a row-level-security policy with ownership checks on every referenced row, and every new table ships its isolation test in the same commit. A security guarantee that is not tested on every change is a hope, not a guarantee.

## 8. Idempotency by sequence for at-least-once work
Queues and webhooks deliver at least once, so handlers must be safe to run twice. Achieve it by sequence, not by wishful thinking: a unique constraint with on-conflict handling, or a claim-before-side-effect step, so a retry collapses to a no-op. External side effects that cost money or send mail are guarded so a redelivery cannot double them.

## 9. Keep private data out of the agent's context
You can let an agent verify a live financial or medical system without ever pulling personal data into its context. Write redacted verification scripts that report only counts, statuses, and structure, never names, amounts, or balances. The agent confirms the wiring is correct, not what flows through it.

## 10. One source of truth, generated outward
When the same logic has to exist in two places (a TypeScript module and an automation node, a schema and its types), do not maintain both by hand. Generate one from the other and stamp it with a version, so the two cannot drift. Drift between two hand-maintained copies is a bug that ships silently.

---

These are abstracted from real production work and contain no client data or application internals. The principle is the asset; the project that taught it stays private.
