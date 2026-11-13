# Guardian restart-policy port

## Provenance

This is a platform-neutral adaptation of the verified Android Guardian V3
supervisor in `ichigoadam212/adam`, commit
[`76862243a995efd6b307fd0e260632caa4535475`](https://github.com/ichigoadam212/adam/commit/76862243a995efd6b307fd0e260632caa4535475).
The inspected `JarvisSupervisor.kt` at snapshot
`09ba72a13d27ca71144ff859ce60998467b07c78` defines five maximum attempts,
exponential backoff starting at one second and capped at sixty seconds, and
reset after a healthy run.

## Scope

`RestartSupervisor` is policy only. It decides whether a retry is permitted
and reports the remaining delay. It does not spawn, signal, kill, or restart
processes. A future Linux process adapter must be a separate component with
explicit executable paths, argument arrays, ownership checks, bounded
timeouts, and tests.

The historical Linux Guardian v0.1 was reported to monitor itself rather than
an external JARVIS process. This port does not claim to recover or fix that
original implementation; it provides a tested policy primitive for a later,
separately reviewed Linux adapter.

## Behavior

- Default maximum: five restart attempts.
- Backoff: 1, 2, 4, 8, 16 seconds, capped at 60 seconds.
- A healthy run resets attempts and failure timestamp.
- Reaching the attempt limit blocks further retries until a healthy reset.
- Time is injectable in tests; production defaults to a monotonic clock.
