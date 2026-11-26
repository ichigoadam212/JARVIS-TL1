# JARVIS TL1

A modular, local-first assistant core. The repository is being rebuilt as a clean foundation; it is **not** a recovered copy of the earlier phone-based TL1 source tree.

## Current status

Implemented on the development branch:

- Python 3.12+ package layout and editable installation.
- Event model and thread-safe in-process Event Bus.
- Central console Logger.
- Allowlisted Command Engine (`help`, `status`, `time`, `exit` only); the `time` command reports local time through an injectable timezone-aware clock.
- Guardian health checks for registered in-process components.
- A bounded restart-policy primitive ported from verified Guardian V3 history (five attempts, exponential backoff capped at 60 seconds); policy only, not an OS process restarter.
- Android Bridge protocol foundation on the dedicated work branch: HMAC-SHA256 signed, read-only `status.read` and `capabilities.read` envelopes with timestamp checks and bounded process-local replay protection. No socket listener or Android adapter is included.
- Automated tests cover core behavior, restart-policy limits, secret-owner authorization, and bridge protocol validation. Core CI run #71 passed 23 tests; Bridge protocol CI run #58 passed on its original head. A fresh run is required for this synchronized branch.

Not implemented yet: Android-side Kotlin adapter/transport, session handshake and secure secret provisioning, external process supervision, AI provider integration, persistent memory, trusted owner authentication, dashboard, or background service.

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m jarvis
```

## Repository map

- `src/jarvis/core/` — core runtime components.
- `tests/` — automated tests.
- `config/settings.example.toml` — non-secret example settings.
- `docs/ARCHITECTURE.md` — architecture and planned modules.
- `docs/ANDROID_BRIDGE_PROTOCOL.md` — protocol v1 scope and trust boundary.
- `.devcontainer/` — Debian development container.

## Security baseline

The command engine never invokes a shell and rejects unregistered commands. Do not commit API keys, passwords, tokens, or populated environment files. Future integrations must use least privilege, explicit allowlists, and tests.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before extending the core.
