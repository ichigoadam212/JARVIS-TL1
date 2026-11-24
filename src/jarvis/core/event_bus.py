"""Synchronous, thread-safe in-process event dispatch."""
from collections import defaultdict
from threading import RLock
from typing import Callable

from jarvis.core.events import Event

Handler = Callable[[Event], None]


class EventBus:
    """Publish events to subscribers without executing arbitrary commands."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_name: str, handler: Handler) -> Callable[[], None]:
        if not event_name or not event_name.strip():
            raise ValueError("event_name must not be empty")
        with self._lock:
            self._handlers[event_name].append(handler)

        def unsubscribe() -> None:
            with self._lock:
                handlers = self._handlers.get(event_name, [])
                if handler in handlers:
                    handlers.remove(handler)
                if not handlers:
                    self._handlers.pop(event_name, None)

        return unsubscribe

    def publish(self, event: Event) -> int:
        """Dispatch to a stable subscriber snapshot; return handler count.

        Handler exceptions intentionally propagate to the caller so failures
        are visible and can be handled at the application boundary.
        """
        with self._lock:
            handlers = tuple(self._handlers.get(event.name, ()))
            handlers += tuple(self._handlers.get("*", ()))
        for handler in handlers:
            handler(event)
        return len(handlers)

    def subscriber_count(self, event_name: str) -> int:
        with self._lock:
            return len(self._handlers.get(event_name, ()))
