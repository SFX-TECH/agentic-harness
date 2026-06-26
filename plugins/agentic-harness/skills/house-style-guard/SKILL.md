---
name: house-style-guard
description: Run to mechanize a project's house-style or content rules into a guard that cannot be forgotten, the harness's own Principle #3 (mechanized safety over remembered safety) applied to your own copy and code. Reads the project's stated rules (banned phrases, required placeholders instead of real names or secrets, no invented metrics, naming) and generates a test or check that fails when a rule is violated.
---

Principle #3 of this harness is mechanized safety over remembered safety, yet most house-style rules live as a line in CLAUDE.md that a tired human has to remember. This skill closes that gap: turn a project's stated rules into a guard the pipeline enforces.

Use it when a project has house-style or content rules worth enforcing: a banned punctuation mark, required placeholders instead of real client names or secrets, no fabricated metrics, naming conventions, a tone rule.

## Steps

1. **Collect the rules.** Read the project's CLAUDE.md and any style or brand doc for stated rules. Restate them as concrete, testable assertions (for example: "user-facing strings contain no em-dash character", "production-facing copy contains none of these real names: <list>", "no metric is stated without a source").

2. **Pick the cheapest mechanization for this stack:**
   - A unit test that scans the relevant source or strings and fails on a violation. Prefer this: it runs in the existing suite and CI, and it is portable.
   - A PreToolUse hook on Edit and Write, only when the rule must catch a violation before it is written and the owner wants it project-local. Keep it opt-in. Never impose one project's style on a different project or globally.

3. **Generate the guard** in the project's own test or hook location, matching the existing test conventions and naming. The failure message must name the rule and the offending location.

4. **Verify it has teeth.** Inject a known violation, confirm the guard fails, then revert. A guard that never fails is not a guard. Confirm it is wired into the suite or the CI that actually runs.

5. **Record it** as a one-line entry in decisions.md: the rule is now mechanized, and where the guard lives.

A rule a human must remember fails at 11pm under a deadline. A rule the suite enforces does not.
