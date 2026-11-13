"""Allowlisted command dispatcher. Never invokes a system shell."""
from dataclasses import dataclass
from typing import Callable

from jarvis.core.policy import AccessLevel, CommandPolicy, Principal


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool
    message: str
    should_exit: bool = False


@dataclass(frozen=True, slots=True)
class Command:
    name: str
    description: str
    handler: Callable[[], CommandResult]
    access_level: AccessLevel = AccessLevel.PUBLIC


class CommandEngine:
    """Dispatch registered commands after checking their access policy."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self.register(Command("help", "Show available commands", self._help))
        self.register(Command("status", "Show core status", self._status))
        self.register(Command("exit", "Stop the interactive session", self._exit))

    def register(self, command: Command) -> None:
        key = command.name.strip().lower()
        if not key or key in self._commands:
            raise ValueError("command name must be non-empty and unique")
        self._commands[key] = command

    def execute(self, raw_input: str, principal: Principal | None = None) -> CommandResult:
        parts = raw_input.strip().split()
        if not parts:
            return CommandResult(False, "Empty command")
        command = self._commands.get(parts[0].lower())
        if command is None:
            return CommandResult(False, "Unknown command. Use 'help'.")
        if len(parts) > 1:
            return CommandResult(False, "This command does not accept arguments")
        actor = principal or Principal()
        if not CommandPolicy.allows(command.access_level, actor):
            return CommandResult(False, "Permission denied")
        return command.handler()

    def _help(self) -> CommandResult:
        lines = [
            f"{item.name}: {item.description}"
            for item in self._commands.values()
            if item.access_level is AccessLevel.PUBLIC
        ]
        return CommandResult(True, "\n".join(lines))

    @staticmethod
    def _status() -> CommandResult:
        return CommandResult(True, "JARVIS TL1 core: online (local session)")

    @staticmethod
    def _exit() -> CommandResult:
        return CommandResult(True, "Session stopped", should_exit=True)
