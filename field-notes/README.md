# Field notes

> **In plain terms:** The rest of this repo is the harness as designed. This folder is the harness as lived. Every real project I run with coding agents earns a page here describing how the harness actually behaves under that project's pressure, what broke, and what pattern came out of it. Patterns only graduate into `PATTERNS.md` and `PRINCIPLES.md` after they have survived in a field note first.

## Why this folder exists

Templates describe the plan. Production describes the truth. I operate many agent sessions across many projects at once, and each project bends the harness differently: a desktop app with a native test gate needs different verification discipline than a Next.js site that deploys on push. The generic docs cannot hold that texture without bloating, so it lives here, one file per project.

## The convention

Each file is `field-notes/<project-slug>.md` and follows the same shape:

1. **The setup.** How sessions are arranged for this project (solo session, paired sessions, orchestrator plus sub-agents), which model tiers, which MCPs actually earn their place.
2. **Patterns proven here.** Practices that emerged or hardened in this project, written so another project can adopt them. Each one states the failure it answers.
3. **Failures worth remembering.** The honest section. What went wrong, what it cost, and the guardrail that now prevents it.
4. **What this project taught the harness.** The short list of things that graduated (or should graduate) into the shared docs.

## Rules for contributions

- **Sanitize.** No product trade secrets, no proprietary algorithms, no customer names or emails, no keys, no internal file paths that reveal secret sauce, no revenue or user-count specifics beyond what is already public. The methodology is open source. The products are not.
- **Earned, not aspirational.** A pattern goes in only after it has actually run in that project. If it is an idea, it is not a field note yet.
- **Name the failure.** Every pattern exists because something broke without it. Say what broke. The failure is the proof the pattern is real.
- **Plain language.** Someone who has never run a coding agent should be able to follow the story.
