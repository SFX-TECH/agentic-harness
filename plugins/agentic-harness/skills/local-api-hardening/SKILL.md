---
name: local-api-hardening
description: The threat-model checklist for a localhost API, the loopback server behind a desktop app (Tauri, Electron, a Python or Node sidecar), a local dashboard, or a dev tool. "It only listens on localhost" is not a security model; any process or browser tab on the machine can reach loopback. Use when building or reviewing anything that serves HTTP on 127.0.0.1.
---

Loopback is a neighborhood, not a vault. Every browser tab, every other process, and every piece of malware on the machine shares localhost with your API. Harden it like it is public, because on its own machine, it is.

## The one rule that does most of the work

**Any endpoint that mutates state MUST be protected. Read-only status endpoints may stay open.** Draw that line explicitly in the route table: a health check or a status read can be unauthenticated; anything that writes, executes, deletes, or reconfigures requires a credential. If you cannot say which side of the line a route is on, it is on the protected side.

## The checklist

1. **Bind to 127.0.0.1 explicitly**, never 0.0.0.0, and normalize what "loopback" means in your checks (127.0.0.1, ::1, and localhost are three spellings; match them all or an origin check can be bypassed by the spelling you forgot).
2. **Authenticate mutations with a token the app hands to its own UI at startup**, not a password a user types. Short TTL, regenerate per session, and build the re-bootstrap path: on a 401, the UI silently fetches a fresh token and retries once, so expiry never becomes user pain.
3. **Compare secrets timing-safe.** HMAC or token comparison uses the constant-time primitive your language provides (for example `hmac.compare_digest`), never `==`.
4. **Keep tokens out of persistent storage and out of logs.** Session-scoped storage that clears on close beats localStorage; the token never appears in a URL, an error message, or a log line.
5. **CORS is deny-by-default.** The UI's own origin only. A wildcard on a localhost API means any website the user visits can drive your app through the browser.
6. **Validate input at the boundary like the caller is hostile**, because on shared loopback, it might be: schema-validate bodies, reject unknown fields, cap sizes, and never pass a request string into a shell or a query without parameterization.
7. **Rate-limit and log mutations.** A local API that executes actions deserves the same audit line per mutation you would demand from a cloud one: who (token id), what, when, result.
8. **CSRF-check anything a browser can reach.** If the UI is a webview or a browser tab, a mutation endpoint needs the token in a header (not a cookie), which makes cross-site form posts inert.

## Review shorthand

Walk the route table and ask three questions per route: does it mutate (then where is its auth), what does it do with what the caller sent (then where is the validation), and what would a hostile tab on this machine do with it. An unprotected mutation route is a finding every time, no matter how local the API feels.
