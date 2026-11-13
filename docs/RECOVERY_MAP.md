# TL1 Recovery and Porting Map

> This document is the source-of-truth inventory for recovering the earlier TL1 work into this repository. It deliberately separates verified source code from conversation-only notes and newly created scaffolding.

## Repository boundaries

- Target repository: `ichigoadam212/JARVIS-TL1`
- Current integration branch: `work/tl1-dev-environment`
- Android source repository: `ichigoadam212/Jarve-Android-V1`
- Android source snapshot verified during recovery: `2c69843afb44501e72dd454b0f2f629f56c41359`
- The Android repository is a source reference, not a replacement for the Linux TL1 runtime.
- Do not merge the development branch into `main` until recovered components are mapped, ported, and tested.

## Original Linux TL1 layout recovered from project history

```text
TL1/
├── Bridge/
│   ├── API/
│   ├── Android/
│   └── Linux/
├── Config/
├── Core/
├── Friday/
│   ├── Analysis/
│   ├── Memory/
│   └── Study/
├── Guardian/
│   ├── Monitor/
│   └── Recovery/
├── Jarvis/
│   ├── Commands/
│   ├── Engine/
│   └── Voice/
├── Logs/
├── Memory/
├── Security/
├── Tools/
└── Updates/
```

The original Linux environment was Debian 13 (trixie), aarch64, Python 3.13.5, running as the unprivileged `jarvis` user in Andronix/PRoot. The historical working path was `/home/jarvis/TL1`.

## Recovery inventory

| Component | Historical evidence | Git/source status | Integration decision |
|---|---|---|---|
| Core Kernel | `Core/kernel.py`; reported system identity and component status | File name and observed output are in conversation history; original source body is not currently available in this repository | Recover original file before rewriting; then port/adapt with tests |
| Core Logger | `Core/logger.py`; log included `TL1 Core initialized` | Historical behavior observed; exact source body unavailable | Preserve behavior and log format when source is recovered |
| Core Status | `Core/status.py`; JSON status output | Historical behavior observed; exact source body unavailable | Recover output schema before implementing |
| Config | `Config/system.conf` | File name is known; exact contents unavailable | Never invent old settings; create a documented example only after schema is confirmed |
| Logs | `Logs/system.log` | Runtime output was observed; log file itself is not committed here | Treat as generated data, never commit personal/runtime logs |
| Command Engine | Earlier Android V1 has `core/CommandEngine.kt`; Linux TL1 command work also recorded | Android source exists; Linux original implementation is not yet located | Keep platform-neutral command contracts; port only after inspecting both implementations |
| Guardian | Android V1 Guardian files exist; TL1 Linux monitor v0.1 was tested for two cycles but watched itself | Android source exists; Linux monitor behavior is conversation-recorded, not source-verified | Keep Android Guardian and Linux process monitor separate; do not claim process supervision from an in-process health check |
| Recovery | Planned Linux module; Android Guardian V3 work is separately recorded | No verified Linux recovery source in this repository | Implement only after defining safe recovery boundaries and tests |
| Android Bridge | Planned as an authenticated bridge between Linux and Android | No verified bridge source found | Design protocol and trust boundary before implementation |
| Voice | Android V1 speech/wake-word modules exist | Android source exists; no verified Linux voice source | Reuse concepts, not Android APIs |
| FRIDAY | Study, analysis, and memory submodules were planned | No verified source body located | Preserve separate identity and data boundary from general JARVIS |
| Memory | Persistent memory planned | No verified Linux source located | Define storage format, retention, and privacy before coding |
| Security / Owner Protection | Owner-only protected settings planned; Android policies exist | Android policy source can be inspected; Linux authentication not verified | Never trust a user-supplied owner flag; implement authentication before privileged actions |
| Tools | Directory exists in historical tree | No verified module inventory | Add tools only with explicit allowlists and least privilege |
| Updates | Directory exists in historical tree | No verified updater implementation | Require signed/verified update design before enabling updates |
| Dashboard / Control Center | Cyber identity, hybrid navigation, balanced information density were design decisions | Design notes only | Build after stable APIs and state model exist |

## Verified Android source files to inspect before porting

Repository: `ichigoadam212/Jarve-Android-V1`

- `app/src/main/java/com/ichigoadam/jarvis/core/CommandEngine.kt`
- `app/src/main/java/com/ichigoadam/jarvis/core/JarvisController.kt`
- `app/src/main/java/com/ichigoadam/jarvis/guardian/Guardian.kt`
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianState.kt`
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianHealth.kt`
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianService.kt`
- Speech-related changes are present in commits `34d2b6cb5a582632f22f094bbd504be5ce7264fe` and `2c69843afb44501e72dd454b0f2f629f56c41359`.

These files must be read in full and mapped to platform-neutral interfaces before any port is considered complete. Android service lifecycle, permissions, and APIs must not be copied into Linux code.

## Current development-branch scaffold (not recovered original source)

The existing branch contains a newer Python foundation under `src/jarvis/` with an event bus, event types, command engine, policy, logger, and an in-process Guardian health-check monitor, plus tests and CI.

This foundation is not the original `/home/jarvis/TL1` source tree. Keep it isolated while comparing it against recovered behavior. In particular, the current Guardian implementation does not inspect or restart operating-system processes.

## Required recovery sequence

1. Inspect the full Android source files and their history; record exact behavior and tests.
2. Recover the original Linux files from the prior TL1 workspace or original project artifacts. Do not recreate them from names or summaries.
3. Compare original Linux behavior with the current Python scaffold; preserve newer, verified behavior and record every intentional change.
4. Port platform-neutral components first: configuration validation, logger, event model, command contracts, and status reporting.
5. Implement Guardian process supervision, Recovery, Security, Memory, Bridge, Voice, FRIDAY, Tools, Updates, and UI as separately testable modules with explicit trust boundaries.
6. Run unit, integration, and security tests on each module. Do not report a component as complete until its tests pass.
7. Only then open a pull request to `main`.

## Evidence labels

- **Verified source**: a file exists in a Git repository and its full contents have been inspected.
- **Historical behavior**: a previous conversation records a command result or observed behavior, but not necessarily the original source.
- **Planned**: a design or intention was discussed, without evidence of implementation.
- **Ported**: adapted code exists in this repository and passes its tests.
