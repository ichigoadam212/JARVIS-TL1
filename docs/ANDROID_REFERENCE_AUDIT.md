# Android V1 reference audit for Linux TL1

## Scope and provenance

This is a source audit, not a claim that Android V1 code is the original Linux TL1 implementation.

Repository: `ichigoadam212/Jarve-Android-V1`
Inspected immutable snapshot: `2c69843afb44501e72dd454b0f2f629f56c41359`

The following source files were fetched and inspected at that snapshot:

| Component | Source path | Blob SHA |
|---|---|---|
| Controller | `app/src/main/java/com/ichigoadam/jarvis/core/JarvisController.kt` | `46ef33816caeb1d3fe7e26517cb9b7791a05837a` |
| Command router | `app/src/main/java/com/ichigoadam/jarvis/core/CommandRouter.kt` | `12392fb73a8a4f7a020b5dd77bee27669561cf85` |
| Command policy | `app/src/main/java/com/ichigoadam/jarvis/core/CommandPolicy.kt` | `03c0b64954a36e9479e7f02b8f971790e474ea06` |
| Resource policy | `app/src/main/java/com/ichigoadam/jarvis/core/ResourcePolicy.kt` | `36a7440d8af88f36c85e14440ffb1d5f05faf3bd` |
| Voice input | `app/src/main/java/com/ichigoadam/jarvis/voice/VoiceInput.kt` | `61d9e8615310d88be821e7750090a5d721803436` |
| Voice output | `app/src/main/java/com/ichigoadam/jarvis/voice/VoiceOutput.kt` | `b2bff526d04f495b418c117e1545c9b6026f2261` |
| Wake-word detector | `app/src/main/java/com/ichigoadam/jarvis/voice/WakeWordDetector.kt` | `fea008b37c2d00b4002e8233f55adf5c89452e53` |
| Owner voice gate | `app/src/main/java/com/ichigoadam/jarvis/voice/OwnerVoiceGate.kt` | `f15908d927ec3c75e470bd169486db27d29fb74b` |
| Voice profile | `app/src/main/java/com/ichigoadam/jarvis/voice/VoiceProfile.kt` | `79ac4942fb49aa8f399ad8eca4ca6b7164efd3d2` |
| Voice profile manager | `app/src/main/java/com/ichigoadam/jarvis/voice/VoiceProfileManager.kt` | `791b05a43f90a6fac8420ad2d9612dc1913b24dd` |
| Speaker verifier | `app/src/main/java/com/ichigoadam/jarvis/voice/SpeakerVerifier.kt` | `c4b71351b008181edadabca7c44018583356cdc7` |
| Style analyzer | `app/src/main/java/com/ichigoadam/jarvis/memory/StyleAnalyzer.kt` | `febb92de453fec063b848f87c668937783a91a9b` |
| Style profile store | `app/src/main/java/com/ichigoadam/jarvis/memory/ChatStyleProfileStore.kt` | `ee862d363a2654e53d9e00e29fd6e198272b5f55` |
| Reply generator | `app/src/main/java/com/ichigoadam/jarvis/memory/ReplyGenerator.kt` | `60d99128316c55a7522d762e8127f1d10707620d` |
| Accessibility integration | `app/src/main/java/com/ichigoadam/jarvis/integration/JarvisAccessibilityService.kt` | `1cfeba5749fc81e4b1f6792c86888c243ee55e31` |
| FRIDAY fallback | `app/src/main/java/com/ichigoadam/jarvis/friday/FridayFallbackService.kt` | `14a5a8709355c613b8826a2664d473949e8d00f6` |

## Verified behavior and Linux port boundaries

### Core and commands

- The controller coordinates command handling, voice, owner verification, accessibility, memory/style, and service state.
- The router has explicit labels for time/status, message and screen reading, chat/style actions, supported app launching, secret mode, and stop.
- The policy enum has public, owner-only, and secret-owner-only categories.
- Important source-audit finding: `CommandRouter.policyFor` defaults unknown input to `PUBLIC`. Linux TL1 must not inherit this default. Unknown commands should be rejected by default, and each command should declare an explicit policy.
- Android resource policy values are one background worker, queue size eight, and a 30-second idle timeout. Treat these as historical tuning values, not proven Linux device limits.

Linux port: preserve the separation between command parsing, routing, authorization, execution, and resource budgets. Implement Linux-native interfaces and tests.

### Voice

- Voice input prefers Android on-device speech recognition when available, otherwise uses the platform recognizer; it requests offline preference and defaults to `ar-EG`.
- Voice output uses Android TextToSpeech.
- Wake-word detection is a simple text-token detector for `jarvis`; it is not a continuously running acoustic wake-word model.
- OwnerVoiceGate requires both enrollment and a separate positive speaker-verification result.
- VoiceProfileManager stores a boolean enrollment flag in Android SharedPreferences.
- SpeakerVerifier stores a normalized 16-feature acoustic vector and uses cosine similarity threshold 0.90. Its own source comment explicitly says this is not biometric-grade authentication.

Linux port: use provider interfaces for speech-to-text and text-to-speech; treat voice match as a convenience signal only, never the sole authorization factor for sensitive operations. Keep an explicit owner-authentication mechanism and safe fallback when audio or models are unavailable.

### Memory and reply style

- ChatStyleProfileStore retains up to 12 samples per package/chat key in Android SharedPreferences, truncating each sample to 12,000 characters.
- StyleAnalyzer derives average length, punctuation tendencies, Egyptian Arabic signal, and common openers/closers.
- ReplyGenerator is a small rule-based response generator, not an LLM.
- The inspected implementation is a style/sample store, not a general persistent conversational memory system.

Linux port: separate user-approved style samples from operational logs and assistant memory; define retention, deletion, encryption, and export behavior before storing personal conversation content. Do not silently ingest chats.

### Android integration and automatic actions

- Accessibility integration is explicitly limited to WhatsApp, Instagram, and Facebook package names in this snapshot.
- It can read visible UI text, derive a chat key, scroll visible history, fill a focused editable field, click a send control, and launch supported apps.
- It debounces content-change events before checking the auto-reply coordinator.
- These are Android Accessibility APIs and must not be copied into Linux TL1.
- The ability to populate and send a message is a consequential external action. Linux/Android bridge design should default to draft-and-confirm, with a separate explicit permission for any automatic sending. Log the action and provide a clear disable switch.

Linux port: keep Android UI automation behind a separately permissioned Android Bridge. The Linux core must not gain unrestricted access to device messages or app actions merely because the bridge exists.

### FRIDAY fallback

- FridayFallbackService runs as a separate Android service, uses a foreground notification, listens for a small set of restart phrases, and starts JarvisService before stopping itself.
- This is an Android recovery/fallback implementation, not evidence of the planned Linux FRIDAY Study/Analysis/Memory modules.

Linux port: keep FRIDAY's school/study assistant role distinct from process recovery. Define a small health/recovery protocol between components; do not conflate FRIDAY's conversational role with Guardian's process supervision.

## Actionable Linux TL1 design decisions

1. Reject unknown commands by default.
2. Separate authorization from speech recognition; voice similarity alone is not owner proof.
3. Keep Guardian restart policy separate from the Linux process adapter.
4. Keep Android Accessibility and app automation inside a permissioned bridge.
5. Make sending messages draft-and-confirm by default.
6. Keep study memory, style samples, logs, and operational state as distinct stores with explicit retention controls.
7. Treat speech and voice providers as optional capabilities; command/status core must work without microphone, cloud, or network.

## What this audit does not prove

- It does not recover the original Linux files from `/home/jarvis/TL1`.
- It does not prove production-ready voice authentication, continuous wake-word detection, or full offline AI.
- It does not prove the Android accessibility actions work across every app version or device.
- It does not prove GitHub Actions or the current branch CI passed.
