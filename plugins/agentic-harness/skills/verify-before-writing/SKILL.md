---
name: verify-before-writing
description: The anti-hallucination discipline for writing code against a system too big to hold in context. Before writing code that touches a schema, a route, an API, or a convention you have not looked at THIS session, probe the real thing first, a column probe, a route probe, a type read. The failure this kills: writing correct-looking code against an imagined version of the system instead of the real one. Use in any codebase with more surface than one context window.
---

The most expensive class of agent bug is code written against a memory. The table had that column last month; the route moved; the helper was renamed. The code compiles, reads clean, reviews fine, and fails at runtime against the real system. The cure is cheap: probe before you write.

## The rule

Before writing code that references a surface you have not verified **in this session**, spend the thirty seconds to look at the real one:

- **A table or model:** run a column probe (select one row, read the model definition, or describe the table) before referencing fields. Yesterday's schema is a rumor.
- **A route or endpoint:** hit it or read its definition before calling it. And read the response like a diagnostician: **a 401 means the route is alive and wants auth; a 404 means it is not there at all.** Those are opposite problems; do not fix the wrong one.
- **A function or type:** read its current signature at its source, not from the call site you remember.
- **A convention:** find one existing example in the codebase and match it, rather than inventing a plausible one.

The prior session's summary, the docs, and your own memory are all testimony. The running system is the witness.

## Where it bites hardest

1. **Cross-layer changes.** Frontend calling backend calling database is three chances to imagine a surface. Probe each layer's real contract at the boundary you are about to cross.
2. **Renames and migrations.** After any rename lands, every unverified reference you write is a coin flip. Re-probe surfaces that were recently touched even if you knew them.
3. **Environment differences.** The route that exists locally may not be deployed; the deployed schema may trail the migration folder. Probe the environment your code will actually run against.

## The economics

A probe costs seconds. The failure it prevents costs a full loop: run, hit the runtime error, diagnose, discover the surface changed, rewrite. One prevented loop pays for a hundred probes, and unlike the loop, the probe never ships a subtle wrong-column bug that runs without erroring.
