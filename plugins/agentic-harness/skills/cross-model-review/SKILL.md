---
name: cross-model-review
description: Run a second vendor's coding model as an independent, read-only reviewer over the staged diff before any release-bound commit, and keep re-running it on the updated bundle until it converges or hits the tripwire. The model that wrote the code shares its own blind spots; a different model at a release gate is the cheapest independent auditor available. Use at release gates, after substantial feature work, and whenever a change touches safety-critical paths.
---

The same model reviewing its own code inherits its own blind spots. This skill wires a second vendor's coding model (for example, the codex CLI when Claude wrote the code) into the release gate as an adversarial reviewer, and defines the loop that makes it actually catch things.

## The gate contract

Invoke the reviewer CLI non-interactively over the scoped git diff with these non-negotiable properties:

1. **Read-only sandbox.** The reviewer must never be able to write the tree. It reviews; it does not fix.
2. **Isolated from user config.** Run with the CLI's ignore-user-config flag so a developer's local settings cannot hang or skew the gate.
3. **Structured verdict.** Force a JSON output schema: overall verdict (pass / warn / block), findings with severity, file, line, rationale, and suggested action.
4. **Trust the output file, never the exit code.** Reviewer CLIs linger, time out, and exit nonzero after writing a perfectly good verdict. Read the result from the output file regardless of how the process ended.
5. **Kill the whole process tree on timeout.** CLI shims spawn children that survive a direct kill and keep consuming tokens.
6. **Severity floor over declared verdict.** A high or critical finding never exits clean, whatever the reviewer's own summary says. The floor only escalates; a reviewer's block always stands for human adjudication.
7. **Leave the reviewer model unpinned.** It tracks the account's current best model; a pinned model id rots silently when deprecated, and a dead gate is worse than no gate because it looks green.
8. **Scope the diff.** Exclude lockfiles, generated mirrors, and vendored noise so the reviewer's context is spent on real code.

## The consolidation loop (where the value is)

The first review examines the code as it stood; the bugs are usually in the code the session just wrote, including in the fixes for the reviewer's own findings. So:

1. Stage the bundle. Run the reviewer on the **staged diff**.
2. Adjudicate every finding honestly: fix what is real, dismiss with a recorded rationale what is not, seed to a future session what is real but out of scope. Never dismiss silently.
3. Re-stage and run the reviewer **again** on the updated bundle. Repeat.
4. **Tripwire at roughly four passes.** If new findings keep appearing past that, stop patching and re-examine the design; the loop is telling you the approach is wrong, not the details.
5. Convergence is passes narrowing toward zero new actionable findings, with only previously-adjudicated items recurring. Close the loop there; do not run a victory lap pass that only re-surfaces the permanently-dismissed class.

In production use this loop has repeatedly caught high-severity defects in freshly-written code that the authoring model's own review missed, including fixes that would have shipped a worse version of the problem they fixed. It earns its cost.

## Adjudication discipline

- Every finding gets one of three dispositions, written down: FIXED (with the fix verified by a test or a re-run), DISMISSED (with the rationale recorded, so the same finding recurring later costs nothing), or SEEDED (a real issue, deliberately deferred, tracked where the next session will find it).
- The human owns policy dismissals (an accepted risk, a deliberate design trade). The session owns factual ones (the reviewer misread the code) and must prove them by citation.
- If the same finding is dismissed more than twice across sessions, promote it: either fix it properly or record it as a standing accepted-risk decision in the project's decision log.
