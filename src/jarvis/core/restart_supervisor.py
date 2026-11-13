"""Platform-neutral, bounded restart policy derived from verified Guardian V3 behavior.

This module decides whether a restart may be attempted. It does not launch,
kill, or otherwise control operating-system processes.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True, slots=True)
class RestartState:
    attempts: int
    last_failure_at: float | None
    allowed: bool
    retry_after_seconds: float


class RestartSupervisor:
    """Bounded exponential-backoff policy; process control stays elsewhere."""

    def __init__(
        self,
        max_attempts: int = 5,
        base_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 60.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_backoff_seconds <= 0:
            raise ValueError("base_backoff_seconds must be positive")
        if max_backoff_seconds < base_backoff_seconds:
            raise ValueError("max_backoff_seconds must be >= base_backoff_seconds")

        self._max_attempts = max_attempts
        self._base_backoff = base_backoff_seconds
        self._max_backoff = max_backoff_seconds
        self._attempts = 0
        self._last_failure_at: float | None = None

    def can_restart(self, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        if self._attempts >= self._max_attempts:
            return False
        if self._last_failure_at is None:
            return True
        return current - self._last_failure_at >= self._retry_delay()

    def record_failure(self, now: float | None = None) -> RestartState:
        current = monotonic() if now is None else now
        if self._attempts < self._max_attempts:
            self._attempts += 1
        self._last_failure_at = current
        return self.state(current)

    def record_healthy_run(self) -> RestartState:
        self._attempts = 0
        self._last_failure_at = None
        return self.state()

    def state(self, now: float | None = None) -> RestartState:
        current = monotonic() if now is None else now
        delay = self._retry_delay()
        elapsed = 0.0 if self._last_failure_at is None else max(0.0, current - self._last_failure_at)
        remaining = max(0.0, delay - elapsed) if self._last_failure_at is not None else 0.0
        return RestartState(
            attempts=self._attempts,
            last_failure_at=self._last_failure_at,
            allowed=self.can_restart(current),
            retry_after_seconds=remaining,
        )

    def _retry_delay(self) -> float:
        if self._attempts <= 0:
            return 0.0
        delay = self._base_backoff * (2 ** (self._attempts - 1))
        return min(delay, self._max_backoff)
