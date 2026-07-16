---
name: safe-mutation-loop
description: The discipline for an agent whose actions mutate real state (a user's machine, a production database, live configuration, files that matter). Every mutation runs the same loop, gate, snapshot, execute, verify with evidence, and carries an honest undo answer and an autonomy tier. Use when building or reviewing any agent, automation, or fixer that changes state someone would miss.
---

Reading is free; mutating is a promise. An agent that changes real state owes the user four things for every change: a reason it was allowed, a way back, proof of what happened, and honesty about which of those it cannot provide. This skill is that contract as a loop. It was earned operating an agent product that repairs real machines, where a silent failure in any step became a user's bad day.

## The loop

Every mutation, no exceptions:

1. **Gate.** The action must pass a policy check before execution, and the policy is data, not vibes: an allowlist of known actions with declared risk, never a freeform command a model composed. If a model chooses the action, it chooses FROM the list; model output never reaches execution unvalidated. Anything not on the list is a proposal for a human, not an action.

2. **Snapshot.** Capture before you mutate: the file copied, the config exported, the row values saved, the previous state recorded somewhere restore can reach. If the snapshot fails, the mutation does not run without an explicit human override. Prefer rename over delete and additive over destructive, because those come with their undo built in.

3. **Execute with its exit code.** Run the change and actually check the result of every external command. Suppressed stderr plus an assumed success is how a restore that never worked reports "restored" for years.

4. **Verify with evidence, and scale confidence by evidence.** "It ran" is not "it worked." Re-measure the thing the mutation was supposed to change and report the before/after delta. If the outcome cannot be measured yet (a restart is pending, the effect is delayed), the honest status is "not yet verified," never "done." Confidence is not a constant 1.0; it is a function of what you actually observed.

5. **Answer the undo question honestly.** Every action declares its undo coverage: fully undoable (the snapshot restores everything), partially undoable (name what does not come back), or `undoable: false` with the reason stated up front, before the user says yes. An honest "this cannot be undone" beats a false "reversible" every time. Skipping the field is not an option; unknown coverage is `false`.

## The autonomy tiers

Not every gated action deserves the same leash. Classify each allowed action into one of three tiers, and let the tier, not the moment's convenience, decide what runs hands-free:

| Tier | Meaning | Contract |
|---|---|---|
| `autonomous_safe` | Executes silently | Reversible, verified cheap, blast radius near zero. The tier for actions you would not bother telling anyone about. |
| `autonomous_verify` | Executes, then auto-reverts if verification fails | Reversible with a reliable snapshot AND a reliable verification. The revert path must be tested, not assumed. |
| `manual_only` | Queues for human approval | Irreversible, destructive, high blast radius, or verification is weak. When in doubt, this tier. |

Tier assignments are reviewed like code: adding an action to a hands-free tier is a policy change with a rationale, not an edit.

## Review checklist

When reviewing an agent or automation against this skill: every mutation path hits all five loop steps; no model-composed string reaches an executor; snapshot failure blocks execution; every external command's exit code is checked; verification measures the outcome rather than the attempt; undo coverage is declared per action with no silent gaps; and the hands-free tiers contain nothing you would not let run at 2 AM on a machine you cannot see.
