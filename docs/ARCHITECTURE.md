# JARVIS TL1 — Core Architecture

## Current implementation

- **Command Engine:** dispatches only explicitly registered commands: `help`, `status`, and `exit`.
- **Event model and Event Bus:** typed event envelopes and synchronous in-process publish/subscribe.
- **Logger:** one central console logger. Credentials and tokens must never be logged.
- **Guardian Monitor:** runs explicitly registered health checks and emits failure/recovery events. It does not inspect, kill, or restart operating-system processes.
- **Entry point:** `python -m jarvis` starts a local interactive session.

## Boundaries

The current core is local and in-process. It has no network listener, Android integration, external AI provider, persistent memory, background daemon, or privileged system access.

The command engine never passes input to a shell. New commands must be registered in code and must have a narrow, documented purpose. Any future system integration must use explicit allowlists, argument arrays (never shell strings), least privilege, and tests.

## Planned modules (not implemented yet)

1. Configuration validation and structured audit events.
2. Owner authentication and permission policy.
3. Persistent, versioned memory with explicit retention controls.
4. External process supervision (separate from this in-process health monitor).
5. Android Bridge with an authenticated, least-privilege protocol.
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
