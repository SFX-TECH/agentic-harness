---
name: phase-gate-check
description: Run before declaring a phase, milestone, or release complete. Walks the phase's written exit criteria, runs the project's build, tests, lint, and deploy as the source of truth, and returns READY-TO-CLOSE or BLOCKED with the failing criteria. A phase is not done because the work feels done; it is done when its checklist verifiably passes.
---

A phase closes on evidence, not on feeling finished. This is the gate. Run it before any "this phase is complete" claim.

## Steps

1. **Find the exit criteria.** Read the phase's written acceptance criteria or exit checklist (in the phase doc, the spec, or CLAUDE.md). If none are written down, that is the first finding: a phase with no defined "done" cannot be gated. Surface the implied criteria and confirm them rather than guessing.

2. **Run the source of truth, do not trust claims.** Execute the project's real verification commands from CLAUDE.md: typecheck, lint, the test suite, the build, and a deploy or smoke check where one exists. The running system describes reality; a prior session's "done" describes intent. When they disagree, reality wins.

3. **Verify each criterion against actual state**, not against the diff's comments or memory. For a data surface, confirm its isolation test ran and passed. For a behavior, confirm it was exercised, not just written.

4. **Return a verdict table.** One row per criterion: the criterion, the command or check that proves it, PASS or FAIL, and the evidence. End with READY-TO-CLOSE, or BLOCKED (N) with the N failing criteria named.

5. **Refuse to close on red.** If anything fails, the phase stays open. Report what to fix. Do not soften a red into a pass.

A clean pass that names what it verified is the goal. An honest BLOCKED is a successful gate, not a failure.
