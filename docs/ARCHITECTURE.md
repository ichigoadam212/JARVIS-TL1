# JARVIS TL1 — Core Architecture

## Current implementation

- **Command Engine:** dispatches only explicitly registered commands: `help`, `status`, `time`, and `exit`; the time provider is injectable and must return a timezone-aware value.
- **Command Policy:** supports public and owner-only command levels; privileged commands are denied by default for anonymous callers.
- **Event model and Event Bus:** typed event envelopes and synchronous in-process publish/subscribe.
- **Logger:** one central console logger. Credentials and tokens must never be logged.
- **Guardian Monitor:** runs explicitly registered health checks and emits failure/recovery events on state transitions. It does not inspect, kill, or restart operating-system processes.
- **Restart Supervisor:** platform-neutral retry policy with a five-attempt limit and exponential backoff capped at 60 seconds, based on verified Guardian V3 Android source. It decides whether a retry is permitted; it does not control processes.
- **Android Bridge protocol foundation:** a separate draft PR defines HMAC-signed, read-only `status.read` and `capabilities.read` envelopes with timestamp and bounded replay checks. It is protocol code only; there is no listener, transport, or Kotlin adapter.
- **Entry point:** `python -m jarvis` starts a local interactive session.

## Security and trust boundaries

The core remains local and in-process. The Bridge protocol foundation does not open a network listener or connect to Android. There is no external AI provider, persistent memory, background daemon, or privileged system access.

The command engine never passes input to a shell. Every new command must be registered in code, have a narrow documented purpose, and declare its `AccessLevel` explicitly; there is no implicit PUBLIC default. Owner-only policy checks are a framework, not a login system: a future trusted authentication layer must create the `Principal` object. Never accept an owner flag directly from an untrusted network request or user-controlled configuration.

Any future system integration must use explicit allowlists, argument arrays (never shell strings), least privilege, secret-safe logging, and tests. API keys belong in the hosting platform's secret store, never in source files or commits.

## Planned modules (not implemented yet)

1. Trusted owner authentication and permission policy integration.
2. Configuration validation and structured audit events.
3. Persistent, versioned memory with explicit retention controls.
4. External process supervision (separate from this in-process health monitor and restart-policy primitive).
5. Android Bridge transport and Kotlin adapter; the protocol-only HMAC/read-only foundation exists on the dedicated work branch.
6. Optional AI provider adapter with server-side secrets only.
7. Dashboard and Control Center.

## Development

Install and test:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m jarvis
```

This repository currently contains a newly built foundation. It is not a recovered copy of the earlier phone-based TL1 source tree.
