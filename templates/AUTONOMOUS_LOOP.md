# Autonomous Improvement Loop: <Project>

For projects mature enough to benefit, and only those. A self-improving verification loop that re-proves the product's claims every run and leaves the codebase better than it found it. Not every project needs one; the ones that touch real machines, real money, or real data do. If your project does not, delete this file.

## The loop
Each run is a full cycle, persisted to the memory bank so the next run starts ahead of this one.

1. **Read state.** Load the memory bank and the last run's results. Know what is already proven.
2. **Verify across layers.**
   - **L1, breadth:** a routing or intent corpus (many phrases or cases) graded against ground truth.
   - **L2, depth:** multi-turn scripted flows that exercise real conversation or control paths.
   - **L3, reality:** live execution against the real target (a real OS, a real API, a real browser), not a mock.
3. **Spawn focused sub-agents.** Each owns one job: expand the test corpus, expand the scripted flows, correlate failures across layers, fix the gaps, and re-prove every marketing or product claim.
4. **Prove or pull.** Every claim the product makes must be backed by a passing check this run. A claim that cannot be proven is fixed or removed. No claim ships on faith.
5. **Persist.** Write what was learned and proven back to the memory bank, so the loop is a chained improvement across sessions, not a fresh start each time.

## Rules
- No "cure" or success claim without before-and-after evidence captured this run.
- Tag self-measured numbers as self-measured.
- The loop never weakens a test to make it pass.
- Live execution runs against a disposable, restorable substrate (a VM snapshot, a scratch database) so a real run is always safe to repeat.

## Output
A dated run record appended to the memory bank: what was verified, what passed, what failed, what was fixed, and the claims re-proven.
