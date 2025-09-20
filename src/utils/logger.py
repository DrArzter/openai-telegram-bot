import logging
import sys
from pathlib import Path

LEVEL_EMOJI: dict[str, str] = {
    "DEBUG": "🐛",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}

LEVEL_COLOR: dict[str, str] = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
}

RESET_COLOR = "\033[0m"


class FixedFormatter(logging.Formatter):
    def format(self, record) -> str:
        """
        Format the log record with emoji, shortened logger name, padded level name,
        and optional color for console output.
        """
        record.emoji = LEVEL_EMOJI.get(record.levelname, "")
        parts = record.name.split(".")
        short = ".".join(parts[-2:])
        record.shortname = (short[:12] + "...") if len(short) > 15 else short.ljust(15)
        record.levelname = f"{record.levelname:<8}"

        color = LEVEL_COLOR.get(record.levelname.strip(), "")
        record.msg = (
            f"{color}{record.getMessage()}{RESET_COLOR}"
            if color
            else record.getMessage()
        )

        return super().format(record)


def get_logger(
    name: str = __name__, level: int = logging.INFO, log_file: Path | str | None = None
) -> logging.Logger:
    """
    Returns a logger with both console and optional file logging.

    :param name: Logger name
    :param level: Logging level
    :param log_file: Optional path to log file
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        FixedFormatter(
            "%(asctime)s | %(emoji)s %(levelname)s | %(shortname)s | %(message)s",
            datefmt="%H:%M",
        )
    )
    logger.addHandler(console_handler)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    return logger
