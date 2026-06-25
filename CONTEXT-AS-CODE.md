# Context as Code

The single biggest failure mode of building with a coding agent is amnesia. Every session starts cold. A decision made on Tuesday gets re-litigated on Friday, the opposite way, because nothing carried it forward. The fix is to treat context as a first-class, version-controlled artifact: a memory bank that is the project's durable brain, loaded at the start of every session.

## The memory bank

Three files, three distinct jobs. The discipline is in keeping the jobs separate.

### `decisions.md`: the architectural spine (append-only)
Every architectural, security, monetization, and scope decision, dated, with its rationale. Append-only: superseded entries stay in the log for archaeology and are marked superseded, never silently overwritten. This is where "why did we do it this way" lives, so it is never re-argued from zero. On a real seven-phase production build this file grew past 7,000 lines and was reviewed at every phase gate. It is the most valuable file in the repo. Reversing a decision is itself a new dated entry, not an edit.

### `active-context.md`: this week only (replace, do not append)
What is true right now: current phase, what just shipped, what is blocked, what is next. Replaced when work shifts, not appended to. If `decisions.md` is the history book, this is the sticky note on the monitor. Keeping it short and current is the whole point; a stale active-context is worse than none.

### `progress.md`: the ship log (append-only, chronological)
What actually shipped, in order, with dates. Append-only. This is the narrative of the build and the receipts. It answers "what got done and when" without polluting the decision log.

## Inline it into the bootstrap

The memory bank is only useful if the agent reads it. The project's `CLAUDE.md` (the file every session loads first) inlines or imports the memory bank, so a fresh session, no matter how long since the last one, starts with current decisions, current state, and the locked constraints already in context. Cold starts are the enemy; the bootstrap is the cure.

## Bank operational observations

Beyond decisions, the most reusable output of a long build is the set of principles you earn from real failures and real wins. Bank them as numbered operational observations inside `decisions.md`: short, durable rules, each traceable to the moment that taught it. They compound. By the end of a real build there were dozens, and they are the seed of `PRINCIPLES.md` in this repo.

## Why this beats a summary file

A summary you write once and forget rots immediately. The memory bank works because each file has one job, the bootstrap forces it into context every session, and updating it is part of the work, not an afterthought. Context as code: the project's brain lives in the repo, in plain markdown, under version control, where the agent and the human both read and write it.

See `templates/` for drop-in `CLAUDE.md`, `decisions.md`, `active-context.md`, and `progress.md` starters.
