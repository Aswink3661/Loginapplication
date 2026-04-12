import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.settings import get_settings

settings = get_settings()

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)

_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _build_handlers() -> list:
    handlers: list = []

    # Console handler — always present
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    handlers.append(console)

    # Rotating file handler — only when LOG_TO_FILE is enabled
    if settings.LOG_TO_FILE:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        handlers.append(file_handler)

    return handlers


def configure_logging() -> None:
    """Bootstrap logging for the entire application.

    Call this exactly once at startup (in main.py / lifespan).
    """
    numeric_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        handlers=_build_handlers(),
    )

    # Silence overly chatty third-party libraries in production
    if settings.ENVIRONMENT == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger.

    Usage::

        from src.utils.logger import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
