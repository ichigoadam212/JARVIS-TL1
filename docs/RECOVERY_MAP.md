# TL1 Recovery and Porting Map

> Source-of-truth inventory for recovering earlier TL1 work into this repository. This separates verified source code from conversation-only notes and newly created scaffolding.

## Repository boundaries

- Target repository: `ichigoadam212/JARVIS-TL1`
- Integration branch: `work/tl1-dev-environment`
- Android source repository: `ichigoadam212/Jarve-Android-V1`
- Android source snapshot inspected: `2c69843afb44501e72dd454b0f2f629f56c41359`
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

Original environment: Debian 13 (trixie), aarch64, Python 3.13.5, unprivileged `jarvis` user in Andronix/PRoot. Historical path: `/home/jarvis/TL1`.

## Recovery inventory

| Component | Historical evidence | Source status | Decision |
|---|---|---|---|
| Core Kernel | `Core/kernel.py`; reported Linux identity and component status | Name and observed output are in conversation history; original source body is not in the Git repositories inspected so far | Recover original file before rewriting |
| Core Logger | `Core/logger.py`; log included `TL1 Core initialized` | Historical behavior observed; exact Linux source body unavailable | Preserve behavior and log format when recovered |
| Core Status | `Core/status.py`; JSON status output | Historical behavior observed; exact Linux source body unavailable | Recover output schema before implementing |
| Config | `Config/system.conf` | File name known; exact contents unavailable | Do not invent old settings |
| Logs | `Logs/system.log` | Runtime output observed; log file not committed | Generated data; do not commit runtime logs |
| Linux Command Engine | Linux TL1 work recorded for `status` and `exit` | Exact Linux source body not yet located | Compare with current Python scaffold before porting |
| Android Command Engine | `core/CommandEngine.kt` | Full source inspected at pinned Android snapshot | Keep as Android implementation; port behavior only where appropriate |
| Linux Guardian v0.1 | Two monitor cycles were reported; monitor watched itself, not an external JARVIS process | Conversation evidence only; exact source body unavailable | Rebuild only after original source recovery and process-supervision tests |
| Android Guardian | `Guardian.kt`, `GuardianState.kt`, `GuardianHealth.kt`, `GuardianService.kt` | Full source inspected at pinned Android snapshot | Keep Android lifecycle code in Android repo; do not copy Android APIs into Linux |
| Guardian V3 | `ichigoadam212/adam` commit `76862243a995efd6b307fd0e260632caa4535475`; full Guardian service diff inspected | Verified Android source history; supervisor and Binder gateway files inspected at `09ba72a13d27ca71144ff859ce60998467b07c78` | Port only platform-neutral supervision policy; keep Binder and Android service lifecycle Android-only |
| Linux restart policy port | `src/jarvis/core/restart_supervisor.py`; `docs/GUARDIAN_PORT.md` | New platform-neutral adaptation of verified Android retry policy; isolated unit tests pass locally | Keep policy separate from any future Linux process-control adapter |
| Recovery | Linux module planned; Android Guardian fallback behavior exists | No verified Linux recovery source | Define safe recovery boundaries before implementation |
| Android Bridge | Authenticated bridge planned between Linux and Android | No verified bridge source | Design protocol and trust boundary first |
| Voice | Android V1 speech and wake-word modules exist | Android source available; no verified Linux voice source | Reuse concepts, not Android APIs |
| FRIDAY | Study, analysis, and memory submodules planned | No verified Linux source body | Preserve separate identity and data boundary from general JARVIS |
| Memory | Persistent memory planned | No verified Linux source body | Define storage format, retention, and privacy |
| Security / Owner Protection | Owner-only protected settings planned; Android policy and voice verification code exists | Android source available; Linux authentication unverified | Never trust a user-supplied owner flag |
| Tools | Directory exists in historical tree | No verified module inventory | Add only explicitly allowlisted tools |
| Updates | Directory exists in historical tree | No verified updater implementation | Require verified update design |
| Dashboard / Control Center | Cyber identity, hybrid navigation, balanced information density recorded | Design notes only | Build after stable APIs and state model |

## Verified Android source files inspected

Repository: `ichigoadam212/Jarve-Android-V1`, pinned snapshot above.

- `app/src/main/java/com/ichigoadam/jarvis/core/CommandEngine.kt` — handles `time`, `status`, and `stop` in Arabic/English. Its `stop` response says listening stopped, but the engine itself only returns a result; controller/service lifecycle performs actual stopping.
- `app/src/main/java/com/ichigoadam/jarvis/core/JarvisController.kt` — integrates voice input/output, wake-word handling, owner voice verification, accessibility actions, memory/style helpers, and command routing.
- `app/src/main/java/com/ichigoadam/jarvis/guardian/Guardian.kt` — bounded restart attempts (maximum three).
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianState.kt` — running/restart-count data model.
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianHealth.kt` — reads JARVIS service and accessibility connection state.
- `app/src/main/java/com/ichigoadam/jarvis/guardian/GuardianService.kt` — foreground monitor polls every ten seconds and hands over to Friday fallback after bounded restart attempts.

Relevant Android speech-history commits include `34d2b6cb5a582632f22f094bbd504be5ce7264fe` and `2c69843afb44501e72dd454b0f2f629f56c41359`.

Android service lifecycle, permissions, accessibility, and APIs must not be copied into Linux code.

## Android V1 reference audit

A source-level audit of the immutable Android V1 snapshot `2c69843afb44501e72dd454b0f2f629f56c41359` is recorded in [`docs/ANDROID_REFERENCE_AUDIT.md`](ANDROID_REFERENCE_AUDIT.md). It covers the controller, command router/policies, resource policy, voice input/output, wake-word text detector, owner gate/profile, speaker verifier, style sample store/analyzer/reply generator, Accessibility integration, and FRIDAY fallback.

Key port constraints established by source inspection:
- Reject unknown commands by default; Android's current router defaults unknown input to PUBLIC.
- Voice similarity is explicitly not biometric-grade authentication.
- Keep Accessibility and app automation in the permissioned Android Bridge; default message sending to draft-and-confirm.
- Separate FRIDAY's study/assistant role from Guardian process recovery.
- The Android style store is not a general persistent memory implementation.

## Additional verified Guardian V3 source (separate Android repository)

Repository: `ichigoadam212/adam`.

- Guardian integration commit: [`76862243a995efd6b307fd0e260632caa4535475`](https://github.com/ichigoadam212/adam/commit/76862243a995efd6b307fd0e260632caa4535475).
- Full source files inspected at snapshot `09ba72a13d27ca71144ff859ce60998467b07c78`:
  - `android/app/src/main/java/com/jarvis/system/JarvisGuardianService.kt`
  - `android/app/src/main/java/com/jarvis/system/JarvisSupervisor.kt`
  - `android/app/src/main/java/com/jarvis/system/JarvisService.kt`
  - `android/app/src/main/aidl/com/jarvis/system/IJarvisGateway.aidl`
- Verified behavior: Guardian polls the JARVIS runtime through a narrow Binder health interface every 5 seconds; a missing connection or non-`ready` state requests recovery.
- The supervisor allows at most five attempts, uses exponential backoff starting at 1 second and capped at 60 seconds, and resets its failure counter after a healthy run.
- The Binder gateway exposes runtime status and tool-name discovery only; it does not expose unrestricted tool execution.
- These are Android-specific sources. Linux TL1 should implement equivalent process-health contracts with Linux-native IPC/process supervision, not copy Android classes or APIs.
- This source history does not establish that the original Linux `/home/jarvis/TL1` files are present in GitHub.

## Current development-branch scaffold (not recovered original source)

The existing branch contains a newer Python foundation under `src/jarvis/`: event bus, event types, command engine, policy, logger, in-process Guardian health-check monitor, tests, and CI.

This foundation is not the original `/home/jarvis/TL1` source tree. Keep it isolated while comparing behavior. The current Guardian implementation does not inspect or restart operating-system processes.

## Required implementation sequence

1. Guardian V3 source inspection is complete for the Android reference above; inspect remaining Android modules only when they map to a specific Linux feature.
2. Recover the original Linux files from the previous TL1 workspace or original project artifacts. Do not recreate them from names or summaries.
3. Compare original Linux behavior with the current Python scaffold; preserve verified behavior and record intentional changes.
4. Port platform-neutral components first: configuration validation, logger, event model, command contracts, and status reporting.
5. Implement Guardian process supervision, Recovery, Security, Memory, Bridge, Voice, FRIDAY, Tools, Updates, and UI as separately testable modules with explicit trust boundaries.
6. Run unit, integration, and security tests on each module. Do not report a component complete until tests pass.
7. Only then open a pull request to `main`.

## Evidence labels

- **Verified source**: a file exists in a Git repository and its full contents have been inspected.
- **Historical behavior**: a previous conversation records a command result or observed behavior, but not necessarily the original source.
- **Planned**: a design or intention was discussed without evidence of implementation.
- **Ported**: adapted code exists in this repository and passes its tests.

## Current verification note

- Linux authorization now distinguishes PUBLIC, OWNER_ONLY, and SECRET_OWNER_ONLY. Secret mode requires a non-anonymous owner principal plus explicit secret-mode authorization.
- GitHub Actions run 42 failed during test collection because the restart-policy test imported the class from the wrong module. The import was corrected in commit `244eecec9990d4a3b830548a991594099ff9c557`; a subsequent passing CI result has not yet been observed. Do not treat the failed run as a code-test failure beyond that collection error, and do not report CI as green.
