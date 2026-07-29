# Patterns

Concrete, repeatable moves for building with coding agents. These are the plays I run; `PRINCIPLES.md` is why.

## Block 0: audit before you build
Before writing code for a substantial task, run a pre-code audit. Fan out parallel sub-agent threads, each owning one concern: security and isolation, database and bundle impact, vendor and runtime compatibility, accessibility, and alignment with the spec or phase doc. Each returns findings, not code. The audit catches architectural drift, a vendor library that does not work in the target runtime, or a wrong assumption, at the cheapest possible moment: before a line is written. On real tasks this has turned what would have been several material review findings into zero.

## One orchestrator, sequential sub-agents
A coding agent's context window is finite; real work overflows it. So one orchestrator holds the plan and the judgment and delegates bounded pieces to sub-agents one at a time. The orchestrator integrates each result, keeps the through-line, and owns the decisions. If a sub-agent is rate-limited or interrupted, the orchestrator completes its remainder directly rather than losing the work. This is deliberately not a free-for-all swarm; swarms collide and hit rate limits.

## A fleet of specialized sub-agents
For a mature project, define named sub-agents with narrow jobs: a build-verifier, a code-reviewer, a tester, a module-auditor, a docs-updater, a session-bootstrapper. Each has a tight contract and a clear invoke-when trigger. Specialization beats one generalist agent trying to hold every concern at once.

## Pre-merge code review against canonical source
Before any change merges, a code-reviewer sub-agent checks it, and it checks against canonical sources (the installed SDK types, the live schema, the actual security policies), not against the pull request's own description. The description says what the author believes; the canonical source says what is true. The reviewer reads the truth, runs the gates, and posts findings.

## The cross-model review gate
Every substantive diff is reviewed by a second coding agent from a different vendor lineage before it ships. Reviewers from the author's own family share the author's blind spots; an independent lineage was trained differently, so it disagrees in useful places. The gate has a hard bar (zero high-severity findings) and three disciplines, each earned the hard way. Run diff-scoped for the routine pass and whole-module rounds for depth: the diff gate is fast but blind to untouched code, and a whole-module review once found twelve real defects in a file the diff gate had just passed clean. Adjudicate every finding instead of auto-applying: in one cycle, two of the reviewer's suggested fixes would themselves have caused harm. And re-gate the fix: a review that converged to zero highs says nothing about the code you wrote in response, and one high-severity fail-open was caught only by a wider re-gate after nine converged rounds had signed off.

## Phase gates
Break a large build into numbered phases, each with explicit exit criteria written down before the phase starts. A phase is not done until its checklist verifiably passes. While a phase is in flight, the next phase's spec stays closed, so scope does not leak backward. Gates make "are we done" an answerable question.

## Evaluation harnesses and claim-proving
For anything with a quality bar (a classifier, a router, a chat agent), build a runnable eval harness that grades real output against a ground truth you compute independently, and run it continuously. One such harness took an answer-quality pass rate from the low sixties to the high nineties (self-measured) by turning "it seems better" into a number that either went up or did not. A claim-prover step re-checks that every promise the product makes is still backed by a passing test, and refuses to ship one that is not.

## PII-safe verification
To verify a live system that holds private data, run redacted scripts that emit only counts, statuses, and structure. The agent confirms the system is wired correctly without ever seeing a name, an amount, or a balance. Verification and privacy are not in tension when the harness is built this way.

## Single-source code generation
When two representations must agree, generate one from the other. A single TypeScript source can emit an automation node and stamp it with a version, so the running automation and the code can never silently diverge. Maintain one, generate the rest.

## Domain skill packs
Distill domain expertise into versioned instruction files the agent loads only when a task touches that domain: the correct ordering of a family of system commands, the safety pattern for a class of destructive operation, the quirks of one vendor integration. A pack is updated at session end when a correction or edge case was earned, so the knowledge compounds instead of being relearned. Two disciplines keep packs trustworthy: they state rules with the evidence that earned them, and they get the same provenance and hygiene scrutiny as code, because an instruction file can teach a defect back into a codebase long after the code was fixed (see `PRINCIPLES.md`, principle 12).

## Verify on the user's hardware, not yours
A dev machine overstates every performance number and hides every resource-pressure bug. Keep a sandbox VM deliberately specced to the product's modal user tier (the RAM and core count most real users actually have), with clean snapshots so a break-and-fix cycle is repeatable in seconds. Two rules earned the hard way: a green status field proves nothing, screenshot the actual screen; and measure on the modal tier before shipping anything performance-sensitive, because the machine that decides whether a feature is good enough is the user's, not yours.

## MCP as canonical truth
Wire the tools that hold the truth (the database, the deploy platform, the code-intelligence index, the docs) as Model Context Protocol servers, and reach for them instead of the model's memory. Check the schema through the database tool before writing SQL. Fetch current SDK behavior through the docs tool instead of recalling it. The model's memory is a starting hypothesis; the MCP server is the fact.

## Self-improving autonomous loop (when it earns its keep)
For a system mature enough to benefit, run a self-improving loop: verify across layers (a routing or intent corpus, multi-turn scripted flows, and live execution against the real target), let each run spawn focused sub-agents that expand the test corpus, correlate failures across layers, fix gaps, and re-prove every claim, then persist the result to the memory bank so the next run starts ahead of this one. Not every project needs this; the ones that touch real machines or real money do. See `templates/AUTONOMOUS_LOOP.md`.
