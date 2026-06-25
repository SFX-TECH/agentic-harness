# Decisions: <Project>

The architectural spine. Append-only. Every architectural, security, monetization, and scope decision is logged here, dated, with its rationale. Decisions are intended to be permanent or quasi-permanent; reversing one is a new dated entry, not an edit. Superseded entries stay in the log, marked superseded, for archaeology.

---

## YYYY-MM-DD: <decision title>

**Decision:** <what was decided, in one or two sentences>

**Why:** <the reasoning, the alternatives considered, the trade-off accepted>

**Implications:** <what this constrains or enables downstream>

---

## Operational observations

Numbered, durable rules earned from real failures and wins during this build. Each is traceable to the moment that taught it. These are the seed of a cross-project principles doc.

1. <observation> : <the failure or win that taught it>
2. ...

---

## Decision log discipline
- Date-prefix every entry.
- One clear rationale per decision.
- Decisions are architectural, monetization, security, or scope. Not implementation details or routine fixes.
- A proposal to reverse a decision goes through a new dated entry, never a silent edit.
- Review this file at every phase gate.
