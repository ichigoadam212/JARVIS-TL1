# JARVIS TL1

A modular, local-first assistant core. The repository is being rebuilt as a clean foundation; it is **not** a recovered copy of the earlier phone-based TL1 source tree.

## Current status

Implemented on the development branch:

- Python 3.12+ package layout and editable installation.
- Event model and thread-safe in-process Event Bus.
- Central console Logger.
- Allowlisted Command Engine (`help`, `status`, `exit` only).
- Guardian health checks for registered in-process components.
- A bounded restart-policy primitive ported from verified Guardian V3 history (five attempts, exponential backoff capped at 60 seconds); policy only, not an OS process restarter.
- Automated tests cover core behavior, restart-policy limits, and secret-owner authorization. The latest observed GitHub Actions run failed during test collection because of an incorrect test import; that import has been corrected in a later commit, and a passing rerun is still pending.

Not implemented yet: Android Bridge, external process supervision, AI provider integration, persistent memory, owner authentication, dashboard, or background service.

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
- `.devcontainer/` — Debian development container.

## Security baseline

The command engine never invokes a shell and rejects unregistered commands. Do not commit API keys, passwords, tokens, or populated environment files. Future integrations must use least privilege, explicit allowlists, and tests.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before extending the core.
