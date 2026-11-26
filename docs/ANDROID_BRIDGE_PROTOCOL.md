# Android Bridge protocol foundation

## Status

This branch adds a **protocol-only foundation** for the future Android Bridge. It is not a working Android-to-Linux connection yet: there is no socket listener, IPC transport, Android Kotlin adapter, background service, or device-side integration.

The module is intentionally narrow:
- HMAC-SHA256 signed request envelopes.
- Protocol version 1 and a short timestamp acceptance window.
- A bounded process-local replay registry: at most 16 distinct key IDs and 4,096 nonces per key. A 17th distinct key or a larger per-key nonce limit is rejected fail-closed; entries are not evicted because that could reopen replay acceptance.
- A nondecreasing wall-clock high-water check shared by those instances; a backward clock adjustment makes verification fail closed until the clock catches up, so expired nonces cannot become fresh again after cache cleanup.
- Only two read-only actions: `status.read` and `capabilities.read`.
- Empty payloads only. No command text, process controls, message sending, or arbitrary tool execution.

## Trust boundary

The HMAC secret must contain at least 32 bytes and must be provisioned outside GitHub. The module accepts it in memory; it does not read, create, or persist secrets. Never put the secret in source, a committed config file, logs, or frontend assets.

A valid HMAC proves only that the sender possesses the shared secret. It does **not** prove that the sender is the device owner, create a trusted `Principal`, or authorize OWNER_ONLY / SECRET_OWNER_ONLY commands. Owner authentication remains a separate future component.

The replay registry is bounded to 16 key IDs × 4,096 nonces per key and is process-local. It is cleared when the process restarts; it deliberately rejects additional keys rather than evicting live replay history. This is not a key-rotation lifecycle or a durable replay store. Before a real transport is enabled, add a fresh per-session challenge or a persistent replay strategy and test it across restarts. Do not expose this protocol to a network until that work is complete.

## Required next steps

1. Implement the Android-side Kotlin encoder/verifier against the same canonical JSON and HMAC test vectors.
2. Define a local-only transport that binds to loopback and has explicit request/response size and timeout limits.
3. Add a fresh session handshake and secure secret provisioning; do not hardcode a shared secret.
4. Connect only the two read-only actions first and test on the actual Redmi/Android + Debian/PRoot environment.
5. Keep all privileged operations disabled until a separate trusted owner-authentication and confirmation design is implemented.

## Explicit non-goals

This protocol does not control Linux services, start or stop Android services, invoke shell commands, access Android Accessibility, send messages, or bypass Android permissions. Android remains the primary device environment; Linux is a complementary unprivileged environment.
