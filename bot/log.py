import logging
import logging.handlers
from pathlib import Path

from bot.constants import Client


def setup() -> None:
    """Set up loggers."""
    # Configure the "TRACE" logging level (e.g. "log.trace(message)")
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")
    logging.Logger.trace = _monkeypatch_trace

    # Set up file logging
    log_file = Path("logs/sir-lancebot.log")
    log_file.parent.mkdir(exist_ok=True)

    # File handler rotates logs every 5 MB
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * (2 ** 20), backupCount=10, encoding="utf-8",
    )
    file_handler.setLevel(logging.TRACE if Client.debug else logging.DEBUG)

    # Console handler prints to terminal
    console_handler = logging.StreamHandler()
    level = logging.TRACE if Client.debug else logging.INFO
    console_handler.setLevel(level)

    # Remove old loggers, if any
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    # Silence irrelevant loggers
    logging.getLogger("discord").setLevel(logging.ERROR)
    logging.getLogger("websockets").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logging.getLogger("async_rediscache").setLevel(logging.WARNING)

    # Setup new logging configuration
    logging.basicConfig(
        format="%(asctime)s - %(name)s %(levelname)s: %(message)s",
        datefmt="%D %H:%M:%S",
        level=logging.TRACE if Client.debug else logging.DEBUG,
        handlers=[console_handler, file_handler],
    )
    logging.getLogger().info("Logging initialization complete")


def _monkeypatch_trace(self: logging.Logger, msg: str, *args, **kwargs) -> None:
    """
    Log 'msg % args' with severity 'TRACE'.

    To pass exception information, use the keyword argument exc_info with a true value, e.g.
    logger.trace("Houston, we have an %s", "interesting problem", exc_info=1)
    """
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, msg, args, **kwargs)
