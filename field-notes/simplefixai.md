# Field notes: SimpleFixAI

> **In plain terms:** SimpleFixAI is my patent-pending Windows repair app. It ships a new release roughly every day or two, entirely through coding agents, to real users whose PCs it repairs with full undo. That pace with that blast radius is only survivable because of the harness patterns below. This page is the two weeks that hardened them: four public releases, a product-history-old bug found and fixed, and a test gate that got honest the hard way.

The product itself stays private. What follows is how it is built and operated.

## The setup: paired sessions, not one session

SimpleFixAI runs on **two long-lived Claude Code sessions in the same repo, with opposite jobs**:

- **The Worker (orchestrator).** Runs the build sessions: reads the design brief, spawns specialized sub-agents in parallel scopes, implements, gates, commits.
- **The Advisor (verifier and prompt-writer).** Never edits the repo. Its loop: receive the Worker's session summary, **verify every load-bearing claim against ground truth** (git, the live database, the production update feed, the actual code), correct any drift plainly, and only then write the next session's prompt.

The ordering rule that makes this work: **the prompt is the output of verification, not the start of it.** Investigate first, consolidate findings, emit the prompt last. Early on I did it backwards (prompt first, checks after) and the prompt encoded stale assumptions; the sessions built on sand.

Why two sessions instead of one: a session grading its own homework inherits its own blind spots. The Advisor has independently caught, among others: a session's self-reported diff numbers being wrong, a "historically clean" test-gate premise that had silently gone stale, and a marketing claim that shipped features could not support. None of those were lies. They were the normal drift of a model summarizing its own long day, and an independent reader with tool access catches them cheaply.

## Patterns proven here

### Cross-model adversarial review (the gate that keeps earning its keep)

**Failure it answers:** the same model that wrote the code reviews the code, and shares its blind spots.

A second vendor's coding model runs as an independent reviewer at every release gate: read-only sandbox, isolated from user config, structured JSON verdict, scoped to the git diff. Operational rules learned the hard way:

- **Trust the output file, never the exit code.** Reviewer CLIs linger, time out, and exit nonzero after writing a perfectly good verdict. The file is the contract.
- **Kill the whole process tree on timeout.** A shim's child process survives a direct kill and keeps consuming tokens.
- **A severity floor overrides the declared verdict.** A high-severity finding never exits clean, whatever the reviewer's summary line says.
- **Leave the reviewer model unpinned.** It tracks the account's current best model and cannot silently rot the gate the way a deprecated pinned model would.

### The consolidation loop (review the staged bundle, repeatedly)

**Failure it answers:** the initial review examined the old tree; the bugs are in the code the session just wrote.

After implementation, the cross-model reviewer runs again **on the staged diff**, and again after each round of fixes, until it converges or hits a tripwire (about four passes, after which you step back and re-examine the design instead of patching). Four consecutive sessions of evidence: the loop caught roughly 10, then 20, then 30 defects **in the session's own new code**, including two high-severity ones where the fix for a problem would have shipped a worse version of the same problem. This is now mandatory before any commit.

### Design locks with single-owner scopes

**Failure it answers:** parallel sub-agents overwrite each other, or the merge tax eats the parallelism.

Before parallel implementation, one agent produces a design lock: the contract every scope builds against, including a touch-site map where **every shared file has exactly one owner** and cross-scope needs are expressed as named contracts (a key name, a field, a verbatim string). Sub-agents then work the same working tree concurrently without collisions and the orchestrator makes one reviewed commit. Same isolation payoff as giving every agent its own git worktree, without the per-agent disk and merge overhead. Worktrees still get used where they shine: running a long release-verification hook against a pinned commit while implementers keep editing the live tree.

### Watchdog, checkpoints, and takeover

**Failure it answers:** sub-agents die silently at session limits, and their unsaved work dies with them.

Every spawned agent gets a stall watchdog from dispatch and writes its results to disk incrementally as it works. When an agent goes silent past the threshold, the orchestrator **takes the work over directly instead of respawning**; a second respawn has never been faster than a takeover here. The checkpoint files mean a silent death costs minutes, not the phase.

### The order-independence gate

**Failure it answers:** a test suite that passes in one order and fails in another is hiding state leaks that will eventually hide a real bug.

The release gate runs the full suite twice under randomized ordering with two fixed seeds, on a deliberately quiet machine, and both orders must reach zero. Two honest lessons from operating it: a failure mass that reproduces identically across seeds but vanishes in isolation is a test-infrastructure defect, not a product defect, and deserves its own dedicated session rather than a mid-release rush; and when a machine is saturated with concurrent runs, the gate lies. Quiet the machine before believing it.

### Ground truth or it did not happen

**Failure it answers:** confident numbers from memory.

Session reports re-derive every number from the source at reporting time: diffs from git, test counts from the runner output, field claims from the production database, release claims from the live update feed. The Advisor then re-verifies independently. The same rule extends outward: before claiming anything about the world outside the repo (was that directory submission ever sent? did that user get a reply?), **check the actual outbox**. I once assumed a software directory had listed the product organically; my own sent mail showed I had submitted it months earlier and the listing was already converting users.

### The field-truth loop

**Failure it answers:** shipping "improvements" that field data does not confirm, and polluting that field data with your own testing.

Anonymous telemetry (never on the repair path) is the acceptance test: every reliability claim gets a before/after query against production data, written before the fix ships. Two disciplines guard the data itself: every development run sets a dev flag so its rows are marked synthetic and excluded from field views (one unflagged dev session once manufactured a fake day-one crash spike that nearly blocked a release), and error messages are treated as testimony, not truth: when a Windows error blames "insufficient disk space," the diagnosis verifies disk space before acting on the claim. It is frequently wrong.

### Support email as a product organ

**Failure it answers:** feedback rots in the inbox while the roadmap gets invented from theory.

Every substantive support email becomes: a root-cause investigation grounded in primary sources (vendor documentation, not forum vibes), a personal reply that tells the user honestly what the product can and cannot do today, and one or more concrete roadmap items. In one week this loop turned three user emails into a restart-first diagnosis gate, two new repair modules, and a class-level triage heuristic. The reply drafts are verified against the codebase before sending so the product's own support mail never overclaims what the product does.

## Failures worth remembering

- **A verification function existed but was never called, for seven versions.** The feature everyone assumed was running was dead code. The fix took a day; finding it took an adversarial audit. Lesson: "the code exists" and "the code runs" are different claims, and only runtime evidence separates them.
- **The undo feature's registry restore had failed silently since version 1.0.0** while printing success, because an invalid command-line switch was swallowed by suppressed stderr. Found by the cross-model discovery pass, not by any test. Lesson: every external command's exit code is checked, and "restore" claims are verified by reading back what was restored.
- **A generic feedback broadcast landed on a user whose detailed ticket had gone unanswered.** He called the product "a tradesman with amnesia," and he was right about the operation even more than the software. Lesson: the mailing list now excludes anyone with an open support thread, and the harness treats comms with the same verification discipline as code.

## What this project taught the harness

1. The **Advisor/Worker paired-session pattern** deserves to be a first-class harness pattern alongside orchestrator-plus-sub-agents.
2. **Cross-model review plus the consolidation loop** is the single highest-yield quality practice discovered here.
3. **Verification order matters:** investigate, then consolidate, then prompt. Never prompt first.
4. Sub-agent **takeover beats respawn**, and checkpoints are what make takeover cheap.
5. Field telemetry, support email, and the release gate are all the same discipline wearing different clothes: **canonical source over model confidence.**
