"""Central logging configuration; secrets must never be logged."""
import logging


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure the JARVIS logger with a console handler only."""
    normalized = level.upper()
    numeric_level = getattr(logging, normalized, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"unsupported log level: {level}")

    logger = logging.getLogger("jarvis")
    logger.setLevel(numeric_level)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    for handler in logger.handlers:
        handler.setLevel(numeric_level)
    return logger
