"""Health-check monitor for registered in-process checks."""
from dataclasses import dataclass
from typing import Callable

from jarvis.core.event_bus import EventBus
from jarvis.core.events import Event


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    healthy: bool
    consecutive_failures: int


class GuardianMonitor:
    """Runs supplied checks; it does not inspect or restart OS processes."""

    def __init__(self, event_bus: EventBus, failure_threshold: int = 2) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        self._bus = event_bus
        self._threshold = failure_threshold
        self._checks: dict[str, Callable[[], bool]] = {}
        self._failures: dict[str, int] = {}
        self._alerted: set[str] = set()

    def register_check(self, name: str, check: Callable[[], bool]) -> None:
        if not name or name in self._checks:
            raise ValueError("check name must be non-empty and unique")
        self._checks[name] = check
        self._failures[name] = 0

    def run_once(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for name, check in self._checks.items():
            healthy = bool(check())
            previous_failures = self._failures[name]
            self._failures[name] = 0 if healthy else previous_failures + 1
            result = CheckResult(name, healthy, self._failures[name])
            results.append(result)

            if not healthy and result.consecutive_failures == self._threshold:
                self._alerted.add(name)
                self._bus.publish(Event(
                    "guardian.check_failed",
                    {"name": name, "consecutive_failures": result.consecutive_failures},
                ))
            elif healthy and name in self._alerted:
                self._alerted.remove(name)
                self._bus.publish(Event("guardian.check_recovered", {"name": name}))
        return results
