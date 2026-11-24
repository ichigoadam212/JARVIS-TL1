"""Run a minimal local JARVIS command session with python -m jarvis."""
from jarvis.core.command_engine import CommandEngine
from jarvis.core.logger import configure_logging


def main() -> None:
    logger = configure_logging()
    engine = CommandEngine()
    logger.info("JARVIS TL1 local session started")
    while True:
        try:
            raw = input("JARVIS> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        result = engine.execute(raw)
        print(result.message)
        if result.should_exit:
            break
    logger.info("JARVIS TL1 local session ended")


if __name__ == "__main__":
    main()
