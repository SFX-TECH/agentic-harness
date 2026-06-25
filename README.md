# Agentic Harness

> The operating system I wrap around coding agents to ship and maintain production software. Durable context, decision discipline, orchestrated sub-agents, and verification gates. This is the harness, open source. The products I build with it stay private; the way I build them is here.

![License](https://img.shields.io/badge/license-MIT-2ea44f)
![Built with](https://img.shields.io/badge/built%20with-Claude%20Code-7a5cff)
![Approach](https://img.shields.io/badge/approach-context%20as%20code-0a66c2)
![Orchestration](https://img.shields.io/badge/orchestration-one%20orchestrator%20%2B%20sub%20agents-3b5bdb)
![Runs](https://img.shields.io/badge/works-local%20%2B%20offline%20capable-2ea44f)

I am [Jesse Jolly](https://linkedin.com/in/jessegjolly), solo founder and CTO of [SFX Tech Innovation](https://sfxtechinnovation.com). I ship production AI systems on my own: a patent-pending offline Windows-repair app, a live client-memory SaaS, local-AI desktop tools, and AI automations that run real businesses. This repo is the harness I built to do that with coding agents and keep doing it as the systems grow.

Anyone can vibe-code a demo in an afternoon. The hard part is shipping something real and then *operating* it for months without it rotting: keeping context durable across sessions, making decisions you can trace and trust, coordinating more work than one agent can hold in its head, and verifying every change against the truth instead of the model's confidence. That gap is the harness. This is mine, generalized and stripped of anything proprietary.

---

## Why a harness

A coding agent is a powerful but forgetful contractor. Point it at a real codebase with no harness and you get three failures, every time:

1. **Context evaporates.** Every session starts cold. Decisions made on Tuesday are re-litigated on Friday, the opposite way.
2. **Work outgrows one context window.** A real change touches more files, more systems, and more verification than a single agent can reason about at once.
3. **Confidence replaces correctness.** The model says it is done. Whether it is done is a separate question that nothing answered.

The harness answers each one with a discipline, not a vibe:

| Failure | Discipline |
|---|---|
| Context evaporates | **Context as code:** a memory bank that is the project's durable brain (decisions, current state, progress) |
| Work outgrows one window | **One orchestrator, sequential sub-agents:** decompose, delegate, integrate, never a free-for-all swarm |
| Confidence replaces correctness | **Verify against canonical source:** build, tests, evals, and phase gates are the source of truth, not the model |

---

## How it works

```mermaid
flowchart TD
    CTX["Durable context<br/>memory bank: decisions, active context, progress"] --> PLAN["Plan the work<br/>phase gates, Block 0 vendor and capability audit"]
    PLAN --> ORCH["Orchestrate<br/>one orchestrator, sequential sub-agents"]
    ORCH --> VERIFY["Verify against canonical source<br/>build, tests, evals, gates"]
    VERIFY --> BANK["Bank the decision<br/>append-only log, numbered operational observations"]
    BANK --> CTX
    HUB[("Local workspace hub<br/>semantic search + knowledge graph<br/>fully local, offline")] -. feeds context .-> CTX
    HUB -. feeds planning .-> PLAN
    subgraph LOOP ["The harness: the control system around the agent"]
      CTX
      PLAN
      ORCH
      VERIFY
      BANK
    end
```

The agent does the work. The harness decides what context it gets, how the work is split, how it is checked, and what is remembered. That control system is the difference between a clever demo and software you can run a business on.

---

## What is in here

Real, usable scaffolding plus the principles behind it. Copy the templates, keep the conventions, and you have the same backbone I run across every project.

- **[`templates/CLAUDE.md`](templates/CLAUDE.md)**: the project bootstrap every session loads first: locked decisions, current state, behavioral defaults, tooling-invocation defaults, and the anti-patterns to avoid. The single file that makes a fresh agent session start informed instead of cold.
- **[`CONTEXT-AS-CODE.md`](CONTEXT-AS-CODE.md)**: the memory bank: `decisions.md` (append-only architectural log), `active-context.md` (this week only, replaced not appended), `progress.md` (chronological shipped log). Why each exists and how they keep their distinct jobs.
- **[`templates/decisions.md`](templates/decisions.md)**, **[`templates/active-context.md`](templates/active-context.md)**, **[`templates/progress.md`](templates/progress.md)**: drop-in memory-bank templates.
- **[`templates/AUTONOMOUS_LOOP.md`](templates/AUTONOMOUS_LOOP.md)**: the sub-agent orchestration contract: when to spawn, how to spec a sub-agent, the invoke-when matrix, and why sequential beats a swarm under real-world rate limits.
- **[`PRINCIPLES.md`](PRINCIPLES.md)**: the operational principles I bank as I work, each earned from a real failure or a real win. Verify against canonical source. Mechanized safety over remembered safety. Architectural pre-work pays back in iteration count. Discipline is the pace enabler, not its enemy.
- **[`PATTERNS.md`](PATTERNS.md)**: the orchestration patterns: the Block 0 audit, one-orchestrator-plus-sequential-sub-agents, completing a rate-limited sub-agent's remainder, phase-gate discipline.
- **[`WORKSPACE-HUB.md`](WORKSPACE-HUB.md)**: the design of my local workspace hub: a fully offline semantic index and knowledge graph over an entire multi-project workspace, exposed to agents over MCP, so any session can retrieve the right context from any project without anything leaving the machine.
- **[`MCP-LOADOUT.md`](MCP-LOADOUT.md)**: the Model Context Protocol servers I run, what each is for, and the rule that governs all of them: prefer the canonical source over the model's memory.

---

## The principles, in one breath

The full list lives in [`PRINCIPLES.md`](PRINCIPLES.md). The load-bearing ones:

- **Verify against canonical source.** Documentation states intent. Source code, the live schema, and the API state describe behavior. When they disagree, behavior wins. Read the real thing before you rely on it.
- **Mechanized safety over remembered safety.** A rule a human has to remember fails at 11pm. Move it into a test, a gate, a guard, or a type so it cannot be forgotten.
- **Architectural pre-work pays back in iteration count.** Surfacing a decision before writing the code costs minutes. Surfacing it mid-build costs iterations. Decide first.
- **One orchestrator, sequential sub-agents.** Decompose the work, delegate bounded pieces, integrate the results, own the judgment calls yourself. A swarm that all writes at once is a merge conflict and a rate-limit wall waiting to happen.
- **Discipline is the pace enabler.** The intuition that process slows shipping is wrong at real complexity. The audits and gates catch problems at the cheapest possible moment, which is what lets the work move fast.

---

## Proven in production

This is not a thought experiment. The harness is how I build and operate, solo:

- **SimpleFix AI**: a shipping, fully offline, patent-pending Windows repair app. Thousands of automated tests, a multi-tier repair engine, snapshot-and-undo on every change. [Showcase »](https://github.com/SFX-TECH/simplefixai-showcase)
- **CoachFile**: a live private client-memory SaaS, with AI extraction that cites its sources and never invents. [Showcase »](https://github.com/SFX-TECH/coachfile-showcase)
- **SFX Lead Intelligence Command Center**: a fully local LLM hub and dashboard; answer quality lifted from 61 percent to 99 percent (self-measured) by a ground-truth evaluation harness. [Showcase »](https://github.com/SFX-TECH/sfx-lead-intelligence)
- **CullPilot** and **Local Transcriber**: local-first, on-device AI desktop tools. [CullPilot »](https://github.com/SFX-TECH/cullpilot) · [Local Transcriber »](https://github.com/SFX-TECH/local-transcriber)
- **Production automations for live clients**: operations command centers, growth stacks, and lead-generation pipelines that systematize whole workflows, not just write code.

The products are private and proprietary. The harness that builds them is this repo.

---

## Use it

The harness is intentionally small and copy-paste friendly:

1. Drop `templates/CLAUDE.md` at your project root and fill in the real decisions and current state.
2. Add the `memory-bank` (decisions, active-context, progress) and make updating it a habit, not an afterthought.
3. Adopt `AUTONOMOUS_LOOP.md` when a task is bigger than one context window.
4. Read `PRINCIPLES.md` and `PATTERNS.md`, then start banking your own. The principles that matter most are the ones you earn.

MIT licensed. Take what is useful, make it yours.

---

Built by **Jesse Jolly** · [SFX Tech Innovation](https://sfxtechinnovation.com) · [LinkedIn](https://linkedin.com/in/jessegjolly) · jessejolly.com coming soon

*The harness is open source under MIT. The products built with it are private and proprietary. Nothing in this repo includes client data, application source, or patent-method internals.*
