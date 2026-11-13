"""Allowlisted command dispatcher. Never invokes a system shell."""
from dataclasses import dataclass
from typing import Callable


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


class CommandEngine:
    """Dispatch only commands explicitly registered by the application."""

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

    def execute(self, raw_input: str) -> CommandResult:
        parts = raw_input.strip().split()
        if not parts:
            return CommandResult(False, "Empty command")
        command = self._commands.get(parts[0].lower())
        if command is None:
            return CommandResult(False, "Unknown command. Use 'help'.")
        if len(parts) > 1:
            return CommandResult(False, "This command does not accept arguments")
        return command.handler()

    def _help(self) -> CommandResult:
        lines = [f"{item.name}: {item.description}" for item in self._commands.values()]
        return CommandResult(True, "\n".join(lines))

    @staticmethod
    def _status() -> CommandResult:
        return CommandResult(True, "JARVIS TL1 core: online (local session)")

    @staticmethod
    def _exit() -> CommandResult:
        return CommandResult(True, "Session stopped", should_exit=True)
