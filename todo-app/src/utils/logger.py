import json
import logging
import sys
from dataclasses import dataclass
from logging import Handler, Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.settings import Settings, get_settings

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
_MANAGED_HANDLER_ATTR = "_loginapplication_managed_handler"

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)

_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_STANDARD_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


class JsonLogFormatter(logging.Formatter):
    """Format log records as cloud-friendly structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "source": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_LOG_RECORD_FIELDS and not key.startswith("_")
        }
        payload.update(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


@dataclass(slots=True)
class LoggerFactory:
    """Create and configure application loggers."""

    settings: Settings
    log_file: Path = LOG_FILE
    log_format: str = _LOG_FORMAT
    date_format: str = _DATE_FORMAT

    def configure(self) -> None:
        """Bootstrap logging for the whole application."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self._resolve_level(self.settings.LOG_LEVEL))
        self._replace_managed_handlers(root_logger)
        self._configure_third_party_loggers()

    def get_logger(self, name: str) -> Logger:
        """Return a named application logger."""
        return logging.getLogger(name)

    def build_handlers(self) -> list[Handler]:
        handlers: list[Handler] = []

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(self._build_formatter())
        self._mark_managed(console)
        handlers.append(console)

        if self.settings.LOG_TO_FILE:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB per file
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(self._build_formatter())
            self._mark_managed(file_handler)
            handlers.append(file_handler)

        return handlers

    def _build_formatter(self) -> logging.Formatter:
        if self.settings.LOG_FORMAT == "json":
            return JsonLogFormatter(datefmt=self.date_format)

        return logging.Formatter(self.log_format, datefmt=self.date_format)

    def _replace_managed_handlers(self, root_logger: Logger) -> None:
        for handler in list(root_logger.handlers):
            if getattr(handler, _MANAGED_HANDLER_ATTR, False):
                root_logger.removeHandler(handler)
                handler.close()

        for handler in self.build_handlers():
            root_logger.addHandler(handler)

    def _configure_third_party_loggers(self) -> None:
        if self.settings.ENVIRONMENT == "production":
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
            logging.getLogger("httpx").setLevel(logging.WARNING)

    @staticmethod
    def _mark_managed(handler: Handler) -> None:
        setattr(handler, _MANAGED_HANDLER_ATTR, True)

    @staticmethod
    def _resolve_level(level_name: str) -> int:
        return getattr(logging, level_name.upper(), logging.INFO)


_logger_factory: LoggerFactory | None = None


def get_logger_factory(settings: Settings | None = None) -> LoggerFactory:
    """Return the default logger factory, or create one for explicit settings."""
    global _logger_factory

    if settings is not None:
        return LoggerFactory(settings=settings)

    if _logger_factory is None:
        _logger_factory = LoggerFactory(settings=get_settings())

    return _logger_factory


def configure_logging() -> None:
    """Bootstrap logging for the entire application.

    Call this exactly once at startup (in main.py / lifespan).
    """
    get_logger_factory().configure()


def get_logger(name: str) -> Logger:
    """Return a module-level logger.

    Usage::

        from src.utils.logger import get_logger
        logger = get_logger(__name__)
    """
    return get_logger_factory().get_logger(name)
